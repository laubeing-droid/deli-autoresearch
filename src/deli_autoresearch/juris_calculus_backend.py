"""Juris-calculus grounded extension verification backend (claim-bound).

Verifies actual claims/attacks formal payloads, not fixed regression suites.
Fixed regression suite only produces BACKEND_HEALTHY / BACKEND_UNHEALTHY.
"""

from __future__ import annotations

from typing import Any

from .agent_backend_codex import BackendEnvelope, CodexAgentBackend, MockAgentBackend
from .certificate_payload import GroundedExtensionCertificate
from .independent_checker import IndependentCheckerRegistry
from .juris_calculus_bridge import JurisCalculusBridge
from .batch_litigation import (
    BatchLitigationCase,
    BatchReport,
    run_batch_litigation as _run_batch_litigation,
)
from .models import (
    VERIFICATION_STATUS_BACKEND_UNAVAILABLE,
    VERIFICATION_STATUS_ERROR,
    VERIFICATION_STATUS_NEEDS_MORE_EVIDENCE,
    VERIFICATION_STATUS_PROVED,
    VERIFICATION_STATUS_REFUTED,
    hash_digest,
    new_uuid,
)


class JurisCalculusBackend:
    """Hybrid backend: work -> agent, verification -> local engine + agent fallback.

    Verification is claim-bound: it verifies the actual claims/attacks
    formal payload from the work agent candidate, not a fixed regression suite.
    """

    def __init__(
        self,
        inner_backend: CodexAgentBackend | MockAgentBackend,
        juris_root,
    ) -> None:
        self.inner = inner_backend
        self.bridge = JurisCalculusBridge(juris_root)
        self.independent_checker = IndependentCheckerRegistry(juris_root=str(juris_root))

    def run_work(self, task_id: str, prompt: dict[str, Any]) -> BackendEnvelope:
        return self.inner.run_work(task_id, prompt)

    def run_verification(self, task_id: str, prompt: dict[str, Any]) -> BackendEnvelope:
        claim_id = prompt.get("claim_id", "")
        verification_type = prompt.get("verification_type", "")
        run_local = prompt.get("run_local_engine", False)
        claim_bound_contract = bool(prompt.get("claim_bound_contract", False))

        # Accept both new verification_type and legacy run_local_engine
        if verification_type == "grounded_extension" or run_local or claim_bound_contract:
            formal_payload = prompt.get("formal_payload", {})
            claim_text = prompt.get("claim", "")
            return self._run_claim_bound_verification(
                task_id, claim_id, claim_text, formal_payload, prompt
            )
        return self.inner.run_verification(task_id, prompt)

    def _run_claim_bound_verification(
        self,
        task_id: str,
        claim_id: str,
        claim_text: str,
        formal_payload: dict[str, Any],
        prompt: dict[str, Any],
    ) -> BackendEnvelope:
        """Verify claims/attacks formal payload against juris-calculus engine.

        Fail-closed enforcement:
        - converged != true -> cannot be PROVED
        - truncated == true -> fail-closed (BACKEND_UNAVAILABLE)
        - iterations > derived_bound -> invariant violation (ERROR)
        - Missing new fields (old engine) -> incompatible backend (BACKEND_UNAVAILABLE)
        """
        claim_bound_contract = bool(prompt.get("claim_bound_contract", False))
        verification_type = prompt.get("verification_type", "")
        request_id = prompt.get("request_id", new_uuid())
        payload_digest = prompt.get("payload_digest", "")
        engine_commit = self.bridge._get_commit_sha()

        if claim_bound_contract and verification_type != "grounded_extension":
            return self._backend_unavailable(
                claim_id=claim_id,
                request_id=request_id,
                payload_digest=payload_digest,
                prompt=prompt,
                engine_commit=engine_commit,
                summary=(
                    "Claim-bound verification requires verification_type=grounded_extension."
                ),
                fail_reason="verification_type_mismatch",
            )

        if claim_bound_contract:
            if not isinstance(formal_payload, dict):
                return self._backend_unavailable(
                    claim_id=claim_id,
                    request_id=request_id,
                    payload_digest=payload_digest,
                    prompt=prompt,
                    engine_commit=engine_commit,
                    summary="Claim-bound verification requires a dict formal_payload.",
                    fail_reason="invalid_formal_payload",
                )
            claims = formal_payload.get("claims")
            attacks = formal_payload.get("attacks")
            if not isinstance(claims, list) or not claims:
                return self._backend_unavailable(
                    claim_id=claim_id,
                    request_id=request_id,
                    payload_digest=payload_digest,
                    prompt=prompt,
                    engine_commit=engine_commit,
                    summary="Claim-bound verification requires non-empty formal_payload.claims.",
                    fail_reason="missing_claims",
                )
            if not isinstance(attacks, list):
                return self._backend_unavailable(
                    claim_id=claim_id,
                    request_id=request_id,
                    payload_digest=payload_digest,
                    prompt=prompt,
                    engine_commit=engine_commit,
                    summary="Claim-bound verification requires list formal_payload.attacks.",
                    fail_reason="missing_attacks",
                )
        else:
            claims = formal_payload.get("claims", []) if isinstance(formal_payload, dict) else []
            attacks = formal_payload.get("attacks", []) if isinstance(formal_payload, dict) else []

        expected_properties = formal_payload.get("expected_properties", {}) if isinstance(formal_payload, dict) else {}

        # --- Step 1: Run engine ---
        try:
            raw = self.bridge.run_grounded_extension(claims, attacks)
        except Exception as exc:
            return self._backend_unavailable(
                claim_id=claim_id,
                request_id=request_id,
                payload_digest=payload_digest,
                prompt=prompt,
                engine_commit=engine_commit,
                summary=f"Juris-calculus engine error: {exc}",
                fail_reason="engine_error",
            )

        # --- Step 2: Fail-closed gate on new v3.0 fields ---
        converged = raw.get("convergent", None)
        truncated = raw.get("truncated", None)
        derived_bound = raw.get("derived_bound", None)
        iterations = raw.get("iterations", 0)

        # Old engine (missing new fields) -> incompatible backend
        if converged is None or truncated is None or derived_bound is None:
            return self._backend_unavailable(
                claim_id=claim_id,
                request_id=request_id,
                payload_digest=payload_digest,
                prompt=prompt,
                engine_commit=engine_commit,
                summary="Juris-calculus engine incompatible: missing v3.0 fields (convergent, truncated, derived_bound). Upgrade required.",
                fail_reason="incompatible_backend_version",
                backend_version="compiler_core.argumentation.grounded_extension (old)",
            )

        # Truncated before convergence -> fail-closed
        if truncated and not converged:
            return self._backend_unavailable(
                claim_id=claim_id,
                request_id=request_id,
                payload_digest=payload_digest,
                prompt=prompt,
                engine_commit=engine_commit,
                summary="Grounded extension truncated before convergence. Derived bound insufficient or max_iter too small.",
                fail_reason="truncated",
                iterations=iterations,
                derived_bound=derived_bound,
            )

        # Not converged (without truncation) -> cannot be PROVED
        if not converged:
            return self._backend_unavailable(
                claim_id=claim_id,
                request_id=request_id,
                payload_digest=payload_digest,
                prompt=prompt,
                engine_commit=engine_commit,
                summary=f"Grounded extension not converged after {iterations} iterations (derived_bound={derived_bound}). Cannot produce PROVED.",
                fail_reason="not_converged",
                verdict="needs_more_evidence",
                verification_status=VERIFICATION_STATUS_NEEDS_MORE_EVIDENCE,
                evidence_strength="weak",
                iterations=iterations,
                derived_bound=derived_bound,
            )

        # Invariant violation: iterations > derived_bound
        if iterations > derived_bound:
            return self._backend_unavailable(
                claim_id=claim_id,
                request_id=request_id,
                payload_digest=payload_digest,
                prompt=prompt,
                engine_commit=engine_commit,
                summary=f"Invariant violation: iterations ({iterations}) > derived_bound ({derived_bound}). Engine logic error.",
                fail_reason="invariant_violation",
                verification_status=VERIFICATION_STATUS_ERROR,
                iterations=iterations,
                derived_bound=derived_bound,
            )

        # --- Step 3: Independent checker gate ---
        cert = GroundedExtensionCertificate.from_engine_result(
            claims,
            attacks,
            raw,
            engine_commit=engine_commit,
        )
        independent_check = self.independent_checker.verify_all(cert)
        if independent_check["overall"] == "rejected":
            return self._backend_unavailable(
                claim_id=claim_id,
                request_id=request_id,
                payload_digest=payload_digest,
                prompt=prompt,
                engine_commit=engine_commit,
                summary=f"Independent checker refuted grounded result: {independent_check['violations']}",
                fail_reason="independent_checker_refuted",
                verification_status=VERIFICATION_STATUS_ERROR,
            )
        if independent_check["overall"] == "inconclusive":
            return self._backend_unavailable(
                claim_id=claim_id,
                request_id=request_id,
                payload_digest=payload_digest,
                prompt=prompt,
                engine_commit=engine_commit,
                summary=f"Independent checker inconclusive: {independent_check['violations']}",
                fail_reason="independent_checker_inconclusive",
                verdict="needs_more_evidence",
                verification_status=VERIFICATION_STATUS_NEEDS_MORE_EVIDENCE,
                evidence_strength="weak",
            )

        # --- Step 4: Match expected properties (same as before) ---
        passed = True
        mismatches = []
        if "expected_accepted" in expected_properties:
            actual = set(raw.get("accepted", []))
            expected = set(expected_properties["expected_accepted"])
            if actual != expected:
                passed = False
                mismatches.append(f"accepted mismatch: {sorted(actual)} vs {sorted(expected)}")
        if "expected_undecided" in expected_properties:
            actual = set(raw.get("undecided", []))
            expected = set(expected_properties["expected_undecided"])
            if actual != expected:
                passed = False
                mismatches.append(f"undecided mismatch: {sorted(actual)} vs {sorted(expected)}")

        # --- Step 5: Verdict ---
        if passed and not mismatches and claims:
            status = VERIFICATION_STATUS_PROVED
            verdict = "validated"
            evidence_strength = "strong"
            summary = f"Grounded extension verified: accepted={raw.get('accepted')}, rejected={raw.get('rejected')}, undecided={raw.get('undecided')}, iterations={iterations}, derived_bound={derived_bound}, converged={converged}"
        elif not claims:
            status = VERIFICATION_STATUS_PROVED
            verdict = "validated"
            evidence_strength = "strong"
            summary = "Grounded extension regression passed (empty claims, engine healthy)"
        else:
            status = VERIFICATION_STATUS_REFUTED
            verdict = "rejected"
            evidence_strength = "strong"
            summary = f"Grounded extension refuted: {mismatches}"

        return BackendEnvelope(
            agent_id=f"juris_engine_{claim_id}",
            payload={
                "claim_id": claim_id,
                "verdict": verdict,
                "evidence_strength": evidence_strength,
                "summary": summary,
                "verification_status": status,
                "claim_digest": prompt.get("claim_digest", ""),
                "payload_digest": payload_digest,
                "request_id": request_id,
                "request_digest": prompt.get("request_digest", ""),
                "backend_name": "juris_calculus",
                "backend_version": "compiler_core.argumentation.grounded_extension",
                "engine_commit": engine_commit,
                "protocol_version": "1.0",
                "iterations": iterations,
                "derived_bound": derived_bound,
                "converged": converged,
                "truncated": truncated,
                "independent_checker": independent_check,
                "artifact_refs": [
                    {
                        "artifact_kind": "juris_test_pass",
                        "locator": f"grounded_extension(claims={len(claims)},attacks={len(attacks)})",
                        "digest": payload_digest,
                    }
                ],
                "supporting_evidence": [
                    {
                        "source_kind": "juris_test_pass",
                        "accepted": raw.get("accepted", []),
                        "rejected": raw.get("rejected", []),
                        "undecided": raw.get("undecided", []),
                        "iterations": iterations,
                        "derived_bound": derived_bound,
                        "converged": converged,
                        "truncated": truncated,
                        "matches_expected": passed,
                        "checker_overall": independent_check["overall"],
                    }
                ],
            },
        )

    def _backend_unavailable(
        self,
        *,
        claim_id: str,
        request_id: str,
        payload_digest: str,
        prompt: dict[str, Any],
        engine_commit: str,
        summary: str,
        fail_reason: str,
        verdict: str = "rejected",
        evidence_strength: str = "weak",
        verification_status: str = VERIFICATION_STATUS_BACKEND_UNAVAILABLE,
        backend_version: str = "compiler_core.argumentation.grounded_extension",
        **extra: Any,
    ) -> BackendEnvelope:
        payload = {
            "claim_id": claim_id,
            "verdict": verdict,
            "evidence_strength": evidence_strength,
            "summary": summary,
            "verification_status": verification_status,
            "claim_digest": prompt.get("claim_digest", ""),
            "payload_digest": payload_digest,
            "request_id": request_id,
            "backend_name": "juris_calculus",
            "backend_version": backend_version,
            "engine_commit": engine_commit,
            "protocol_version": "1.0",
            "fail_reason": fail_reason,
            "supporting_evidence": [],
        }
        payload.update(extra)
        return BackendEnvelope(agent_id=f"juris_engine_{claim_id}", payload=payload)

    def run_health_check(self) -> dict[str, Any]:
        """Run fixed regression suite — only BACKEND_HEALTHY or BACKEND_UNHEALTHY."""
        report = self.bridge.run_full_regression()
        return {
            "backend_name": "juris_calculus",
            "healthy": report.all_passed,
            "passed": report.passed,
            "failed": report.failed,
            "total": report.total,
            "status": "BACKEND_HEALTHY" if report.all_passed else "BACKEND_UNHEALTHY",
        }

    def run_litigation_batch(
        self,
        cases: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Run a batch of litigation cases through Horn fixpoint + grounded extension.

        Each case dict must contain:
          - case_id: str
          - facts: list[str]
          - horn_rules: list[dict] with head/body/id
          - target_claims: list[str]

        Returns the BatchReport as a dict plus a summary field for Deli findings.
        """
        batch_cases = [
            BatchLitigationCase(
                case_id=case["case_id"],
                facts=set(case["facts"]),
                horn_rules=case["horn_rules"],
                target_claims=case["target_claims"],
            )
            for case in cases
        ]
        report = _run_batch_litigation(batch_cases, juris_root=str(self.bridge.juris_root))
        return {
            "backend_name": "juris_calculus",
            "batch_report": {
                "total_cases": report.total_cases,
                "pass_count": report.pass_count,
                "fail_count": report.fail_count,
                "all_passed": report.all_passed,
                "cases": [
                    {
                        "case_id": r.case_id,
                        "horn_saturated": r.horn_saturated,
                        "horn_witnesses": r.horn_witnesses,
                        "grounded_accepted": r.grounded_accepted,
                        "grounded_rejected": r.grounded_rejected,
                        "grounded_undecided": r.grounded_undecided,
                        "certificates_count": len(r.certificates),
                        "impacts_count": len(r.rule_impacts),
                        "missing_evidence_count": len(r.missing_evidence),
                        "total_findings": r.total_findings,
                        "certificates": r.certificates,
                        "rule_impacts": r.rule_impacts,
                        "missing_evidence": r.missing_evidence,
                    }
                    for r in report.cases
                ],
            },
            "engine_commit": self.bridge._get_commit_sha(),
            "protocol_version": "1.0",
        }
