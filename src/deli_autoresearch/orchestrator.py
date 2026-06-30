"""Deterministic orchestrator with cross-process file locks, multi-tier stall pressure,
claim-bound verification, CAS progress writes, and fail-closed semantics."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Any

from .constants import (
    BASE_SOURCE_KINDS,
    MAX_CLAIMS_PER_ITERATION,
    MAX_EVIDENCE_PER_CLAIM,
    SAME_DIRECTION_RETRY_LIMIT,
    STATUS_ACTIVE,
    STATUS_COMPLETED,
    STATUS_PAUSED_FOR_HUMAN,
    VERIFICATION_STATUS_PROVED,
    VERIFICATION_STATUS_REFUTED,
    VERIFICATION_STATUS_NEEDS_MORE_EVIDENCE,
)
from .file_lock import LockHeldError, ReentrantLockError
from .models import (
    ClaimRecord,
    Progress,
    VerificationResult,
    WorkResult,
    hash_digest,
    new_uuid,
    utc_now_iso,
)
from .disclosure_gate import build_report_row
from .memory_router import MemoryRouter
from .registry_manager import RegistryManager
from .retrieval_policy import RetrievalPolicy
from .source_registry import SourceRegistry
from .state_store import StateStore
from .template_runtime import TemplateRuntime
from .utils import claim_id_for, normalize_claim_text


class Orchestrator:
    def __init__(
        self,
        store: StateStore,
        registry: RegistryManager,
        templates: TemplateRuntime,
        backend,
        *,
        source_registry: SourceRegistry | None = None,
    ) -> None:
        self.store = store
        self.registry = registry
        self.templates = templates
        self.backend = backend
        self.source_registry = source_registry
        self.retrieval_policy = RetrievalPolicy(source_registry) if source_registry else None
        self._instance_id = f"orchestrator_{new_uuid()}"

    # ------------------------------------------------------------------
    # Main scheduling loop — protected by workspace lock
    # ------------------------------------------------------------------

    def run_once(self) -> list[dict[str, Any]]:
        """Run one pass over all enabled tasks under workspace lock.

        Acquires workspace lock first. If another process holds it, returns
        LOCK_HELD status immediately (fail-fast).
        """
        try:
            ws_lock = self.store.acquire_workspace_lock(self._instance_id)
        except LockHeldError as exc:
            return [{
                "status": "LOCK_HELD",
                "scope": exc.scope,
                "existing_meta": exc.existing_meta,
            }]

        with ws_lock:
            results: list[dict[str, Any]] = []
            tasks = sorted(
                self.registry.list_enabled_tasks(),
                key=lambda t: t.priority,
                reverse=True,
            )
            for task in tasks:
                results.append(self.run_task_once(task.task_id))
                self.registry.touch_orchestrator_run(task)
            return results

    # ------------------------------------------------------------------
    # Per-task execution — protected by task lock
    # ------------------------------------------------------------------

    def run_task_once(self, task_id: str) -> dict[str, Any]:
        """Execute one iteration for a task under task lock.

        Acquires task lock (fail-fast). Covers the full transaction:
        read progress → work → verification → state transition → commit.
        """
        try:
            task_lock = self.store.acquire_task_lock(task_id, self._instance_id)
        except LockHeldError as exc:
            return {
                "task_id": task_id,
                "status": "LOCK_HELD",
                "scope": exc.scope,
                "skipped": True,
            }
        except ReentrantLockError:
            return {
                "task_id": task_id,
                "status": "REENTRANT_REJECTED",
                "skipped": True,
            }

        with task_lock:
            progress = self.store.read_progress(task_id)
            if progress.status != STATUS_ACTIVE:
                self.store.log_event(
                    self.store.orchestrator_log_path(task_id),
                    "orchestrator", "info", "skip_inactive",
                    {"task_id": task_id, "status": progress.status},
                )
                return {"task_id": task_id, "status": progress.status, "skipped": True}

            if progress.iteration >= progress.max_iterations:
                progress.status = STATUS_COMPLETED
                progress.completion_reason = "max_iterations_reached"
                self.store.write_progress(progress)
                return {"task_id": task_id, "status": progress.status, "skipped": True}

            progress.iteration += 1
            progress.last_seen = utc_now_iso()
            template = self.templates.get(progress.template_type)
            work_prompt = self._build_work_prompt(task_id, progress, template)
            work_envelope = self.backend.run_work(task_id, work_prompt)
            progress.last_work_agent_id = work_envelope.agent_id
            work_result = WorkResult.from_dict(work_envelope.payload)
            claims = self.store.read_claims(task_id)

            if len(work_result.claims) > MAX_CLAIMS_PER_ITERATION:
                raise ValueError("work result exceeds max claim count")

            prepared = []
            for candidate in work_result.claims:
                if len(candidate.evidence) > MAX_EVIDENCE_PER_CLAIM:
                    raise ValueError("candidate exceeds max evidence count")
                if candidate.source_kind not in BASE_SOURCE_KINDS:
                    raise ValueError(f"unknown candidate source kind: {candidate.source_kind}")
                for evidence in candidate.evidence:
                    if not isinstance(evidence, dict):
                        raise ValueError("evidence must be structured objects")
                self._validate_work_candidate(template, candidate)
                claim_id, claim_record = self._accept_claim(task_id, claims, candidate)
                prepared.append((claim_id, claim_record, candidate))

            self.store.write_claims(task_id, claims)
            self.store.append_jsonl(
                self.store.work_log_path(task_id),
                {
                    "iteration": progress.iteration,
                    "agent_id": work_envelope.agent_id,
                    "summary": work_result.summary,
                    "claims": [candidate.to_dict() for candidate in work_result.claims],
                },
            )

            # Verification phase — aggregate verdicts before state transition
            verification_results: list[VerificationResult] = []
            verification_agent_ids: list[str] = []
            pending_transitions: list[dict[str, Any]] = []

            for claim_id, claim_record, candidate in prepared:
                verify_prompt = self._build_verification_prompt(
                    task_id, progress, claim_id, claim_record, candidate, template
                )
                verify_envelope = self.backend.run_verification(task_id, verify_prompt)
                verification_agent_ids.append(verify_envelope.agent_id)
                verdict = VerificationResult.from_dict(verify_envelope.payload)

                if verdict.claim_id != claim_id:
                    raise ValueError(
                        f"verification returned mismatched claim_id: {verdict.claim_id} vs {claim_id}"
                    )

                # Validate digest echo
                if (verdict.claim_digest
                        and verdict.claim_digest != verify_prompt.get("claim_digest", "")):
                    raise ValueError(f"claim_digest mismatch for {claim_id}")
                if (verdict.payload_digest
                        and verdict.payload_digest != verify_prompt.get("payload_digest", "")):
                    raise ValueError(f"payload_digest mismatch for {claim_id}")
                if (verdict.request_id
                        and verdict.request_id != verify_prompt.get("request_id", "")):
                    raise ValueError(f"request_id mismatch for {claim_id}")

                verification_results.append(verdict)
                pending_transitions.append({
                    "claim_id": claim_id,
                    "claim_record": claim_record,
                    "candidate": candidate,
                    "verdict": verdict,
                })

            progress.last_verification_agent_ids = verification_agent_ids

            # Aggregate and apply all verdicts
            for entry in pending_transitions:
                self._apply_verification(
                    task_id, progress, claims,
                    entry["candidate"], entry["verdict"],
                )

            self._maybe_pivot(task_id, progress, template, verification_results)
            self._maybe_complete(task_id, progress, work_result, verification_results)

            self.store.write_claims(task_id, claims)
            self.store.write_progress(progress)

            self.store.append_jsonl(
                self.store.iteration_log_path(task_id),
                {
                    "iteration": progress.iteration,
                    "work_summary": work_result.summary,
                    "verification": [r.to_dict() for r in verification_results],
                    "validated_findings_count": progress.validated_findings_count,
                    "claim_stall_pressure": progress.claim_stall_pressure,
                    "direction_stall_pressure": progress.direction_stall_pressure,
                    "task_stall_pressure": progress.task_stall_pressure,
                    "status": progress.status,
                    "completion_stage": progress.completion_stage,
                    "completion_reason": progress.completion_reason,
                },
            )
            self.store.log_event(
                self.store.orchestrator_log_path(task_id),
                "orchestrator", "info", "iteration_complete",
                {
                    "task_id": task_id,
                    "iteration": progress.iteration,
                    "validated_findings_count": progress.validated_findings_count,
                    "claim_stall_pressure": progress.claim_stall_pressure,
                    "direction_stall_pressure": progress.direction_stall_pressure,
                    "task_stall_pressure": progress.task_stall_pressure,
                    "status": progress.status,
                },
            )
            return {
                "task_id": task_id,
                "iteration": progress.iteration,
                "status": progress.status,
                "validated_findings_count": progress.validated_findings_count,
                "claim_stall_pressure": progress.claim_stall_pressure,
                "direction_stall_pressure": progress.direction_stall_pressure,
                "task_stall_pressure": progress.task_stall_pressure,
            }

    # ------------------------------------------------------------------
    # Resume
    # ------------------------------------------------------------------

    def resume_task_with_direction(
        self, task_id: str, strategy_type: str, summary: str, rationale: str
    ) -> Progress:
        progress = self.store.read_progress(task_id)
        progress.status = STATUS_ACTIVE
        progress.completion_stage = "main"
        progress.completion_reason = None
        progress.claim_stall_pressure = 0.0
        progress.direction_stall_pressure = 0.0
        progress.task_stall_pressure = 0.0
        progress.current_direction = {
            "strategy_type": strategy_type,
            "summary": summary,
            "rationale": rationale,
            "origin_iteration": progress.iteration,
            "template_extension": {},
        }
        progress.last_seen = utc_now_iso()
        directions = self.store.read_directions(task_id)
        direction = self.templates.get(progress.template_type).generate_next_direction(
            tried_directions=directions,
            progress=replace(progress, current_direction=progress.current_direction),
            trigger="human_resume",
        )
        direction.strategy_type = strategy_type
        direction.summary = summary
        direction.rationale = rationale
        directions.append(direction)
        self.store.write_directions(task_id, directions)
        self.store.write_progress(progress)
        return progress

    # ------------------------------------------------------------------
    # Claim lifecycle
    # ------------------------------------------------------------------

    def _accept_claim(
        self, task_id: str, claims: dict[str, ClaimRecord], candidate
    ) -> tuple[str, ClaimRecord]:
        normalized = normalize_claim_text(candidate.claim_text)
        claim_id = claim_id_for(normalized)
        claim = claims.get(claim_id)
        if claim is None:
            claim = ClaimRecord(
                claim_id=claim_id,
                claim_text=candidate.claim_text,
                normalized_claim_text=normalized,
            )
            claims[claim_id] = claim
        elif claim.status == "rejected" and not self._can_reopen(candidate):
            raise ValueError(
                f"claim {claim_id} cannot reopen without strong evidence or new direction basis"
            )
        elif claim.status == "rejected":
            claim.status = "reopened"
            claim.reopen_count += 1
            claim.history.append({"ts": utc_now_iso(), "event": "reopened"})
        self.store.append_jsonl(
            self.store.hypotheses_path(task_id),
            {
                "ts": utc_now_iso(),
                "claim_id": claim_id,
                "claim": candidate.claim_text,
                "support_kind": candidate.support_kind,
                "source_kind": candidate.source_kind,
                "evidence": candidate.evidence,
            },
        )
        return claim_id, claim

    def _can_reopen(self, candidate) -> bool:
        if candidate.support_kind == "new_direction_basis":
            return True
        strong_items = [
            e for e in candidate.evidence
            if isinstance(e, dict)
            and e.get("source_kind") in {"code", "experiment", "local_file", "source_span", "human_review"}
        ]
        return len(strong_items) > 0

    # ------------------------------------------------------------------
    # Verification application
    # ------------------------------------------------------------------

    def _apply_verification(
        self,
        task_id: str,
        progress: Progress,
        claims: dict[str, ClaimRecord],
        candidate,
        verdict: VerificationResult,
    ) -> None:
        claim = claims[verdict.claim_id]
        self.store.append_jsonl(
            self.store.verification_log_path(task_id), verdict.to_dict()
        )
        verif_status = verdict.verification_status

        if verif_status == VERIFICATION_STATUS_PROVED:
            finding_payload = self._build_finding_payload(
                task_id, progress, claim, candidate, verdict, verif_status
            )
            report_row = build_report_row(finding_payload)
            finding_payload.update(report_row.to_dict())
            if not report_row.allowed_disclosure:
                failure = dict(finding_payload)
                failure["event_type"] = "failure"
                failure["failure_reason"] = report_row.blocked_reason
                MemoryRouter(self.store.task_logs_dir(task_id)).route(failure)
                verdict.verification_status = VERIFICATION_STATUS_NEEDS_MORE_EVIDENCE
                verdict.verdict = "needs_more_evidence"
                progress.claim_stall_pressure += 0.5
                progress.direction_stall_pressure += 0.5
                progress.task_stall_pressure += 0.5
                progress.consecutive_needs_more_evidence += 1
                claim.status = "needs_more_evidence"
                claim.history.append({
                    "ts": utc_now_iso(),
                    "event": "finding_blocked",
                    "reason": report_row.blocked_reason,
                })
                return

            routing = MemoryRouter(self.store.task_logs_dir(task_id)).route(finding_payload)
            if not routing.accepted:
                verdict.verification_status = VERIFICATION_STATUS_NEEDS_MORE_EVIDENCE
                verdict.verdict = "needs_more_evidence"
                progress.claim_stall_pressure += 0.5
                progress.direction_stall_pressure += 0.5
                progress.task_stall_pressure += 0.5
                progress.consecutive_needs_more_evidence += 1
                claim.status = "needs_more_evidence"
                claim.history.append({
                    "ts": utc_now_iso(),
                    "event": "finding_rejected_by_memory_router",
                    "reason": routing.reason,
                })
                return

            progress.validated_findings_count += 1
            progress.claim_stall_pressure = 0.0
            progress.direction_stall_pressure = 0.0
            progress.task_stall_pressure = 0.0
            progress.consecutive_needs_more_evidence = 0
            progress.last_progress_at = utc_now_iso()
            claim.status = "validated"
            return

        if verif_status == VERIFICATION_STATUS_REFUTED:
            progress.claim_stall_pressure += 1.0
            progress.direction_stall_pressure += 1.0
            progress.task_stall_pressure += 1.0
            progress.consecutive_needs_more_evidence = 0
            claim.status = "rejected"
            claim.history.append({
                "ts": utc_now_iso(), "event": "rejected", "reason": verdict.summary,
            })
            return

        if verif_status == VERIFICATION_STATUS_NEEDS_MORE_EVIDENCE:
            progress.claim_stall_pressure += 0.5
            progress.direction_stall_pressure += 0.5
            progress.task_stall_pressure += 0.5
            progress.consecutive_needs_more_evidence += 1
            claim.status = "needs_more_evidence"
            if progress.consecutive_needs_more_evidence >= SAME_DIRECTION_RETRY_LIMIT:
                template = self.templates.get(progress.template_type)
                action = template.handle_same_direction_retry(
                    progress=progress, claim_id=verdict.claim_id,
                )
                claim.history.append({
                    "ts": utc_now_iso(),
                    "event": "same_direction_retry_limit_hit",
                    "action": {"action": action.action, "reason": action.reason},
                })
            return

        if verdict.wont_validate:
            progress.claim_stall_pressure += 0.5
            progress.task_stall_pressure += 0.5
            claim.status = "needs_more_evidence"
            self.store.log_event(
                self.store.orchestrator_log_path(task_id),
                "orchestrator", "warn", f"verification_{verif_status.lower()}",
                {"claim_id": verdict.claim_id, "status": verif_status, "summary": verdict.summary},
            )
            return

        raise ValueError(f"unknown verification status: {verif_status}")

    # ------------------------------------------------------------------
    # Pivot
    # ------------------------------------------------------------------

    def _maybe_pivot(
        self, task_id: str, progress: Progress, template,
        verification_results: list[VerificationResult],
    ) -> None:
        rules = template.template_stall_rules(
            progress=progress,
            verification_results=[r.to_dict() for r in verification_results],
        )
        directions = self.store.read_directions(task_id)
        trigger = None

        if progress.task_stall_pressure >= 4:
            progress.status = STATUS_PAUSED_FOR_HUMAN
            trigger = "needs_human_attention"
        elif progress.direction_stall_pressure >= 2:
            trigger = "direction_stall_pressure"
        elif progress.consecutive_needs_more_evidence >= SAME_DIRECTION_RETRY_LIMIT:
            trigger = "same_direction_retry"

        if trigger is None and not rules:
            return

        if trigger == "needs_human_attention":
            self.store.log_event(
                self.store.orchestrator_log_path(task_id),
                "orchestrator", "warn", "paused_for_human",
                {
                    "task_id": task_id,
                    "claim_stall_pressure": progress.claim_stall_pressure,
                    "direction_stall_pressure": progress.direction_stall_pressure,
                    "task_stall_pressure": progress.task_stall_pressure,
                },
            )
            return

        direction = template.generate_next_direction(
            tried_directions=directions,
            progress=progress,
            trigger=trigger or "template_rule",
        )
        current_type = (progress.current_direction or {}).get("strategy_type", "")
        if current_type == direction.strategy_type:
            raise ValueError("pivot must change direction strategy type")

        directions.append(direction)
        progress.current_direction = direction.to_dict()
        progress.consecutive_needs_more_evidence = 0
        progress.direction_stall_pressure = 0.0
        self.store.write_directions(task_id, directions)
        self.store.log_event(
            self.store.orchestrator_log_path(task_id),
            "orchestrator", "info", "pivot",
            {"task_id": task_id, "direction": direction.to_dict(), "trigger": trigger, "template_rules": rules},
        )

    # ------------------------------------------------------------------
    # Completion
    # ------------------------------------------------------------------

    def _maybe_complete(
        self, task_id: str, progress: Progress,
        work_result: WorkResult, verification_results: list[VerificationResult],
    ) -> None:
        if progress.status != STATUS_ACTIVE:
            return
        if progress.validated_findings_count < progress.target_validated_findings:
            return

        if progress.tail_pass_required and not progress.tail_pass_completed:
            if progress.completion_stage == "main":
                progress.completion_stage = "tail_pass_pending"
                return
            if progress.completion_stage in {"tail_pass_pending", "tail_pass"}:
                tail_proved = [r for r in verification_results if r.verification_status == VERIFICATION_STATUS_PROVED]
                tail_refuted = [r for r in verification_results if r.verification_status == VERIFICATION_STATUS_REFUTED]
                tail_wont = [r for r in verification_results if r.wont_validate]
                if tail_wont:
                    progress.completion_stage = "tail_pass_pending"
                    return
                if not tail_proved and tail_refuted:
                    progress.completion_stage = "done"
                    progress.status = STATUS_COMPLETED
                    progress.completion_reason = "tail_pass_refuted_all"
                    return
                if tail_proved:
                    progress.tail_pass_completed = True
                    progress.completion_stage = "done"
                    progress.status = STATUS_COMPLETED
                    progress.completion_reason = "tail_pass_complete"
                return

        progress.completion_stage = "done"
        progress.status = STATUS_COMPLETED
        progress.completion_reason = "target_validated_findings_reached"

    # ------------------------------------------------------------------
    # Prompt builders
    # ------------------------------------------------------------------

    def _build_work_prompt(self, task_id: str, progress: Progress, template) -> dict[str, Any]:
        task_spec = self.store.task_spec_path(task_id).read_text(encoding="utf-8")
        directions = [d.to_dict() for d in self.store.read_directions(task_id)]
        is_tail_pass = progress.completion_stage == "tail_pass_pending"
        if is_tail_pass:
            progress.completion_stage = "tail_pass"
        work_prompt_contract = self._work_prompt_contract(template)
        return {
            "task_spec": task_spec,
            "progress": progress.to_dict(),
            "directions_tried": directions,
            "max_claims": 1 if is_tail_pass else MAX_CLAIMS_PER_ITERATION,
            "tail_pass": is_tail_pass,
            "strict_json": True,
            "work_prompt_contract": work_prompt_contract,
            "iteration": progress.iteration,
            "request_id": new_uuid(),
        }

    def _build_verification_prompt(
        self, task_id: str, progress: Progress, claim_id: str,
        claim: ClaimRecord, candidate, template,
    ) -> dict[str, Any]:
        claim_digest = hash_digest({"claim_text": candidate.claim_text})
        payload = candidate.formal_payload if isinstance(candidate.formal_payload, dict) else {}
        payload_digest = hash_digest(payload)
        request_id = new_uuid()
        return {
            "task_id": task_id,
            "iteration": progress.iteration,
            "claim_id": claim_id,
            "claim": claim.claim_text,
            "candidate": candidate.to_dict(),
            "strict_json": True,
            "claim_digest": claim_digest,
            "payload_digest": payload_digest,
            "request_id": request_id,
            "request_digest": hash_digest({
                "task_id": task_id,
                "iteration": str(progress.iteration),
                "claim_id": claim_id,
            }),
            "verification_type": self._infer_verification_type(candidate),
            "claim_bound_contract": getattr(template, "name", "") == "legal_proof",
            "formal_payload": payload,
        }

    def _infer_verification_type(self, candidate) -> str:
        fp = candidate.formal_payload or {}
        vt = fp.get("verification_type", "")
        if vt:
            return vt
        sk = candidate.source_kind
        if sk in ("juris_test_pass",):
            return "grounded_extension"
        if sk in ("z3_counterexample", "lean_proof"):
            return "smt_logic"
        if sk in ("banach_norm_test",):
            return "banach_contraction"
        return "grounded_extension"

    def _work_prompt_contract(self, template) -> dict[str, Any]:
        contract_fn = getattr(template, "work_prompt_contract", None)
        contract = contract_fn() if callable(contract_fn) else {}
        if contract:
            return contract
        if getattr(template, "name", "") == "legal_proof":
            return {
                "template_name": "legal_proof",
                "verification_type": "grounded_extension",
                "required_candidate_fields": [
                    "claim_text",
                    "evidence",
                    "source_kind",
                    "verifiable",
                    "formal_payload",
                ],
                "formal_payload_required_fields": [
                    "claims",
                    "attacks",
                    "verification_type",
                ],
                "formal_payload_constraints": {
                    "claims_non_empty": True,
                    "attacks_non_empty": True,
                    "verification_type": "grounded_extension",
                },
            }
        return {}

    def _validate_work_candidate(self, template, candidate) -> None:
        payload = candidate.to_dict()
        errors: list[str] = []

        validator = getattr(template, "validate_work_candidate", None)
        if callable(validator):
            errors.extend(validator(payload))

        if payload.get("source_kind") == "web":
            errors.append("web source_kind must route as source_candidate, not a claim finding")

        for index, evidence in enumerate(payload.get("evidence") or []):
            if not isinstance(evidence, dict):
                continue
            if evidence.get("source_kind") == "web":
                errors.append(f"evidence[{index}] web source must route as source_candidate")
            source_id = evidence.get("source_id")
            if source_id and self.retrieval_policy and not self.retrieval_policy.decide(str(source_id)).allowed:
                errors.append(f"evidence[{index}] source_id is not approved: {source_id}")

        if getattr(template, "name", "") == "legal_proof":
            formal_payload = payload.get("formal_payload")
            if not isinstance(formal_payload, dict) or not formal_payload:
                errors.append("legal_proof candidate requires a non-empty formal_payload dict")
            else:
                claims = formal_payload.get("claims")
                attacks = formal_payload.get("attacks")
                verification_type = formal_payload.get("verification_type")
                if not isinstance(claims, list) or not claims:
                    errors.append("formal_payload.claims must be a non-empty list")
                if not isinstance(attacks, list) or not attacks:
                    errors.append("formal_payload.attacks must be a non-empty list")
                if verification_type != "grounded_extension":
                    errors.append("formal_payload.verification_type must be grounded_extension")

        if errors:
            raise ValueError(
                "work candidate failed template contract: " + "; ".join(errors)
            )

    def _build_finding_payload(
        self,
        task_id: str,
        progress: Progress,
        claim: ClaimRecord,
        candidate,
        verdict: VerificationResult,
        verif_status: str,
    ) -> dict[str, Any]:
        metadata = self._first_evidence_metadata(candidate.evidence)
        return {
            "event_type": "verified_finding",
            "ts": utc_now_iso(),
            "task_id": task_id,
            "iteration": progress.iteration,
            "claim_id": verdict.claim_id,
            "claim": claim.claim_text,
            "claim_text": claim.claim_text,
            "evidence": candidate.evidence,
            "verifiable": candidate.verifiable,
            "source_kind": candidate.source_kind,
            "source_id": metadata["source_id"],
            "source_span": metadata["source_span"],
            "evidence_path": metadata["evidence_path"],
            "verifier": verdict.backend_name or "verification_agent",
            "verifier_status": verif_status,
            "verification_summary": verdict.summary,
            "evidence_strength": verdict.evidence_strength,
            "verification_status": verif_status,
            "backend_name": verdict.backend_name,
            "backend_version": verdict.backend_version,
            "backend_input_digest": verdict.payload_digest,
            "backend_output_digest": verdict.request_digest,
            "artifact_refs": verdict.artifact_refs,
        }

    @staticmethod
    def _first_evidence_metadata(evidence: list[dict[str, Any]]) -> dict[str, str]:
        fallback = {"source_id": "", "source_span": "", "evidence_path": ""}
        for item in evidence:
            if not isinstance(item, dict):
                continue
            source_id = str(
                item.get("source_id")
                or item.get("source")
                or item.get("source_kind")
                or ""
            )
            evidence_path = str(
                item.get("evidence_path")
                or item.get("locator")
                or item.get("path")
                or item.get("url")
                or item.get("test_name")
                or item.get("manifest_path")
                or ""
            )
            source_span = str(item.get("source_span") or item.get("span") or "")
            metadata = {
                "source_id": source_id,
                "source_span": source_span,
                "evidence_path": evidence_path,
            }
            if evidence_path or source_span:
                return metadata
            if not fallback["source_id"]:
                fallback = metadata
        return fallback
