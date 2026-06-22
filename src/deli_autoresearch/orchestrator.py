"""Single-pass orchestrator implementation."""

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
    STRONG_SOURCE_KINDS,
    VERDICT_NEEDS_MORE_EVIDENCE,
    VERDICT_REJECTED,
    VERDICT_VALIDATED,
)
from .models import ClaimRecord, Progress, VerificationResult, WorkResult, utc_now_iso
from .registry_manager import RegistryManager
from .state_store import StateStore
from .template_runtime import TemplateRuntime
from .utils import claim_id_for, normalize_claim_text


class Orchestrator:
    def __init__(self, store: StateStore, registry: RegistryManager, templates: TemplateRuntime, backend) -> None:
        self.store = store
        self.registry = registry
        self.templates = templates
        self.backend = backend

    def run_once(self) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for task in self.registry.list_enabled_tasks():
            results.append(self.run_task_once(task.task_id))
            self.registry.touch_orchestrator_run(task)
        return results

    def run_task_once(self, task_id: str) -> dict[str, Any]:
        progress = self.store.read_progress(task_id)
        if progress.status != STATUS_ACTIVE:
            self.store.log_event(
                self.store.orchestrator_log_path(task_id),
                "orchestrator",
                "info",
                "skip_inactive",
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
        work_prompt = self._build_work_prompt(task_id, progress)
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
                if evidence.get("source_kind") not in BASE_SOURCE_KINDS:
                    raise ValueError("evidence contains unknown source kind")
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

        verification_results: list[VerificationResult] = []
        verification_agent_ids: list[str] = []
        for claim_id, claim_record, candidate in prepared:
            verify_prompt = self._build_verification_prompt(task_id, progress, claim_id, claim_record, candidate)
            verify_envelope = self.backend.run_verification(task_id, verify_prompt)
            verification_agent_ids.append(verify_envelope.agent_id)
            verdict = VerificationResult.from_dict(verify_envelope.payload)
            if verdict.claim_id != claim_id:
                raise ValueError("verification returned mismatched claim_id")
            verification_results.append(verdict)
            self._apply_verification(task_id, progress, claims, candidate, verdict)

        progress.last_verification_agent_ids = verification_agent_ids
        if verification_results and all(result.verdict != VERDICT_VALIDATED for result in verification_results):
            progress.last_seen = utc_now_iso()
        self._maybe_pivot(task_id, progress, template, verification_results)
        self._maybe_complete(task_id, progress, work_result, verification_results)
        self.store.write_claims(task_id, claims)
        self.store.write_progress(progress)
        self.store.append_jsonl(
            self.store.iteration_log_path(task_id),
            {
                "iteration": progress.iteration,
                "work_summary": work_result.summary,
                "verification": [result.to_dict() for result in verification_results],
                "validated_findings_count": progress.validated_findings_count,
                "stall_pressure": progress.stall_pressure,
                "status": progress.status,
                "completion_stage": progress.completion_stage,
                "completion_reason": progress.completion_reason,
            },
        )
        self.store.log_event(
            self.store.orchestrator_log_path(task_id),
            "orchestrator",
            "info",
            "iteration_complete",
            {
                "task_id": task_id,
                "iteration": progress.iteration,
                "validated_findings_count": progress.validated_findings_count,
                "stall_pressure": progress.stall_pressure,
                "status": progress.status,
                "completion_stage": progress.completion_stage,
            },
        )
        return {
            "task_id": task_id,
            "iteration": progress.iteration,
            "status": progress.status,
            "validated_findings_count": progress.validated_findings_count,
            "stall_pressure": progress.stall_pressure,
            "completion_stage": progress.completion_stage,
        }

    def resume_task_with_direction(self, task_id: str, strategy_type: str, summary: str, rationale: str) -> Progress:
        progress = self.store.read_progress(task_id)
        progress.status = STATUS_ACTIVE
        progress.completion_stage = "main"
        progress.completion_reason = None
        progress.current_direction = {
            "strategy_type": strategy_type,
            "summary": summary,
            "rationale": rationale,
            "origin_iteration": progress.iteration,
            "template_extension": {},
        }
        progress.last_seen = utc_now_iso()
        directions = self.store.read_directions(task_id)
        directions.append(self.templates.get(progress.template_type).generate_next_direction(
            tried_directions=directions,
            progress=replace(progress, current_direction=progress.current_direction),
            trigger="human_resume",
        ))
        directions[-1] = self.templates.get(progress.template_type).generate_next_direction(
            tried_directions=directions[:-1],
            progress=replace(progress, current_direction=progress.current_direction),
            trigger="human_resume",
        )
        directions[-1].strategy_type = strategy_type
        directions[-1].summary = summary
        directions[-1].rationale = rationale
        self.store.write_directions(task_id, directions)
        self.store.write_progress(progress)
        return progress

    def _accept_claim(self, task_id: str, claims: dict[str, ClaimRecord], candidate) -> tuple[str, ClaimRecord]:
        normalized = normalize_claim_text(candidate.claim_text)
        claim_id = claim_id_for(normalized)
        claim = claims.get(claim_id)
        if claim is None:
            claim = ClaimRecord(claim_id=claim_id, claim_text=candidate.claim_text, normalized_claim_text=normalized)
            claims[claim_id] = claim
        elif claim.status == "rejected" and not self._can_reopen(candidate):
            raise ValueError(f"claim {claim_id} cannot reopen without strong evidence or new direction basis")
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
        return self._has_strong_evidence(candidate.evidence)

    def _has_strong_evidence(self, evidence_items: list[dict[str, Any]]) -> bool:
        return any(item.get("source_kind") in STRONG_SOURCE_KINDS for item in evidence_items)

    def _apply_verification(
        self,
        task_id: str,
        progress: Progress,
        claims: dict[str, ClaimRecord],
        candidate,
        verdict: VerificationResult,
    ) -> None:
        claim = claims[verdict.claim_id]
        self.store.append_jsonl(self.store.verification_log_path(task_id), verdict.to_dict())
        if verdict.verdict == VERDICT_VALIDATED:
            if not self._has_strong_evidence(candidate.evidence):
                raise ValueError("validated findings require strong evidence")
            progress.validated_findings_count += 1
            progress.stall_pressure = 0.0
            progress.consecutive_needs_more_evidence = 0
            progress.last_progress_at = utc_now_iso()
            claim.status = "validated"
            self.store.append_jsonl(
                self.store.findings_path(task_id),
                {
                    "ts": utc_now_iso(),
                    "claim_id": verdict.claim_id,
                    "claim": claim.claim_text,
                    "evidence": candidate.evidence,
                    "verifiable": candidate.verifiable,
                    "source_kind": candidate.source_kind,
                    "verification_summary": verdict.summary,
                    "evidence_strength": verdict.evidence_strength,
                },
            )
            return
        if verdict.verdict == VERDICT_NEEDS_MORE_EVIDENCE:
            progress.stall_pressure += 0.5
            progress.consecutive_needs_more_evidence += 1
            claim.status = "needs_more_evidence"
            if progress.consecutive_needs_more_evidence >= SAME_DIRECTION_RETRY_LIMIT:
                claim.history.append({"ts": utc_now_iso(), "event": "same_direction_retry_limit_hit"})
            return
        if verdict.verdict == VERDICT_REJECTED:
            progress.stall_pressure += 1.0
            progress.consecutive_needs_more_evidence = 0
            claim.status = "rejected"
            claim.history.append({"ts": utc_now_iso(), "event": "rejected"})
            return
        raise ValueError(f"unknown verdict: {verdict.verdict}")

    def _maybe_pivot(self, task_id: str, progress: Progress, template, verification_results: list[VerificationResult]) -> None:
        rules = template.template_stall_rules(
            progress=progress,
            verification_results=[result.to_dict() for result in verification_results],
        )
        directions = self.store.read_directions(task_id)
        trigger = None
        if progress.stall_pressure >= 4:
            progress.status = STATUS_PAUSED_FOR_HUMAN
            trigger = "needs_human_attention"
        elif progress.stall_pressure >= 2:
            trigger = "stall_pressure"
        elif progress.consecutive_needs_more_evidence >= SAME_DIRECTION_RETRY_LIMIT:
            trigger = "same_direction_retry"
        if trigger is None and not rules:
            return
        if trigger == "needs_human_attention":
            self.store.log_event(
                self.store.orchestrator_log_path(task_id),
                "orchestrator",
                "warn",
                "paused_for_human",
                {"task_id": task_id, "stall_pressure": progress.stall_pressure},
            )
            return
        direction = template.generate_next_direction(
            tried_directions=directions,
            progress=progress,
            trigger=trigger or "template_rule",
        )
        current_type = (progress.current_direction or {}).get("strategy_type")
        if current_type == direction.strategy_type:
            raise ValueError("pivot must change direction strategy type")
        directions.append(direction)
        progress.current_direction = direction.to_dict()
        progress.consecutive_needs_more_evidence = 0
        self.store.write_directions(task_id, directions)
        self.store.log_event(
            self.store.orchestrator_log_path(task_id),
            "orchestrator",
            "info",
            "pivot",
            {"task_id": task_id, "direction": direction.to_dict(), "trigger": trigger, "template_rules": rules},
        )

    def _maybe_complete(
        self,
        task_id: str,
        progress: Progress,
        work_result: WorkResult,
        verification_results: list[VerificationResult],
    ) -> None:
        if progress.status != STATUS_ACTIVE:
            return
        if progress.validated_findings_count < progress.target_validated_findings:
            return
        if progress.tail_pass_required and not progress.tail_pass_completed:
            if progress.completion_stage == "main":
                progress.completion_stage = "tail_pass_pending"
                self.store.log_event(
                    self.store.orchestrator_log_path(task_id),
                    "orchestrator",
                    "info",
                    "tail_pass_scheduled",
                    {"task_id": task_id, "iteration": progress.iteration},
                )
                return
            if progress.completion_stage in {"tail_pass_pending", "tail_pass"}:
                progress.tail_pass_completed = True
                progress.completion_stage = "done"
                progress.status = STATUS_COMPLETED
                progress.completion_reason = "tail_pass_complete"
                return
        progress.completion_stage = "done"
        progress.status = STATUS_COMPLETED
        progress.completion_reason = "target_validated_findings_reached"

    def _build_work_prompt(self, task_id: str, progress: Progress) -> dict[str, Any]:
        task_spec = self.store.task_spec_path(task_id).read_text(encoding="utf-8")
        directions = [direction.to_dict() for direction in self.store.read_directions(task_id)]
        is_tail_pass = progress.completion_stage == "tail_pass_pending"
        if is_tail_pass:
            progress.completion_stage = "tail_pass"
        return {
            "task_spec": task_spec,
            "progress": progress.to_dict(),
            "directions_tried": directions,
            "max_claims": 1 if is_tail_pass else MAX_CLAIMS_PER_ITERATION,
            "tail_pass": is_tail_pass,
            "strict_json": True,
        }

    def _build_verification_prompt(self, task_id: str, progress: Progress, claim_id: str, claim: ClaimRecord, candidate) -> dict[str, Any]:
        return {
            "task_id": task_id,
            "iteration": progress.iteration,
            "claim_id": claim_id,
            "claim": claim.claim_text,
            "candidate": candidate.to_dict(),
            "strict_json": True,
            "allowed_verdicts": [VERDICT_VALIDATED, VERDICT_REJECTED, VERDICT_NEEDS_MORE_EVIDENCE],
        }
