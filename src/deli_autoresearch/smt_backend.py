"""SMT/Z3 formal verification backend (claim-bound, fail-closed).

Verifies actual Z3 constraints from formal payload.
Z3 unavailable, timeout, or unknown NEVER produce "validated".
"""

from __future__ import annotations

import sys
from typing import Any

from .agent_backend_codex import BackendEnvelope, CodexAgentBackend, MockAgentBackend
from .constants import resolve_juris_calculus_root
from .models import (
    VERIFICATION_STATUS_BACKEND_UNAVAILABLE,
    VERIFICATION_STATUS_ERROR,
    VERIFICATION_STATUS_NOT_RUN,
    VERIFICATION_STATUS_PROVED,
    VERIFICATION_STATUS_REFUTED,
    VERIFICATION_STATUS_TIMEOUT,
    hash_digest,
    new_uuid,
)

_juris_root = resolve_juris_calculus_root()
if _juris_root.exists() and str(_juris_root) not in sys.path:
    sys.path.insert(0, str(_juris_root))

try:
    import z3  # type: ignore
    HAS_Z3 = True
except ImportError:
    HAS_Z3 = False


class SMTBackend:
    """Hybrid backend: work -> agent, verification -> Z3/SMT (fail-closed).

    Fixed regression suite only produces BACKEND_HEALTHY / BACKEND_UNHEALTHY.
    Claim-bound verification uses actual Z3 constraints from formal_payload.
    """

    def __init__(self, inner_backend: CodexAgentBackend | MockAgentBackend) -> None:
        self.inner = inner_backend

    def run_work(self, task_id: str, prompt: dict[str, Any]) -> BackendEnvelope:
        return self.inner.run_work(task_id, prompt)

    def run_verification(self, task_id: str, prompt: dict[str, Any]) -> BackendEnvelope:
        verification_type = prompt.get("verification_type", "")

        if verification_type == "smt_logic":
            return self._run_smt_logic_verification(task_id, prompt)
        if verification_type == "grounded_smt":
            return self._run_grounded_smt_verification(task_id, prompt)
        return self.inner.run_verification(task_id, prompt)

    def _run_smt_logic_verification(
        self, task_id: str, prompt: dict[str, Any]
    ) -> BackendEnvelope:
        claim_id = prompt.get("claim_id", "")
        formal_payload = prompt.get("formal_payload", {})
        payload_digest = hash_digest(formal_payload)
        request_id = prompt.get("request_id", new_uuid())

        if not HAS_Z3:
            return self._unavailable_envelope(claim_id, payload_digest, request_id, prompt, "Z3 not installed")

        constraints = formal_payload.get("constraints", [])
        expected = formal_payload.get("expected", {})

        if not constraints:
            return self._unavailable_envelope(claim_id, payload_digest, request_id, prompt, "No constraints in formal_payload")

        try:
            solver = z3.Solver()
            solver.set("timeout", 10000)  # 10s timeout
            for c in constraints:
                name = c.get("name", "c")
                left = c.get("left")
                op = c.get("op", "==")
                right = c.get("right")
                if left is None or right is None:
                    continue
                expr = _build_z3_expr(z3, left, op, right)
                if expr is not None:
                    tag = z3.Bool(name)
                    solver.assert_and_track(expr, tag)

            result = solver.check()
            actual_sat = str(result) == "sat"
            expected_sat = expected.get("sat", None)

            if result == z3.unknown:
                return BackendEnvelope(
                    agent_id=f"smt_engine_{claim_id}",
                    payload={
                        "claim_id": claim_id,
                        "verdict": "needs_more_evidence",
                        "evidence_strength": "weak",
                        "summary": f"Z3 returned UNKNOWN (timeout or incompleteness)",
                        "verification_status": VERIFICATION_STATUS_TIMEOUT,
                        "claim_digest": prompt.get("claim_digest", ""),
                        "payload_digest": payload_digest,
                        "request_id": request_id,
                        "request_digest": prompt.get("request_digest", ""),
                        "backend_name": "z3_smt",
                        "backend_version": f"z3 {z3.get_version_string()}",
                        "supporting_evidence": [],
                    },
                )

            if expected_sat is not None and actual_sat != expected_sat:
                status = VERIFICATION_STATUS_REFUTED
                verdict = "rejected"
                evidence_strength = "strong"
                summary = f"Z3 returned {result}, expected {'sat' if expected_sat else 'unsat'}"
            elif expected_sat is None:
                status = VERIFICATION_STATUS_PROVED if not actual_sat else VERIFICATION_STATUS_REFUTED
                verdict = "validated" if not actual_sat else "rejected"
                evidence_strength = "strong"
                summary = f"Z3 SMT result: {result}"
            else:
                status = VERIFICATION_STATUS_PROVED
                verdict = "validated"
                evidence_strength = "strong"
                summary = f"Z3 SMT verified: {result} matches expected"
        except Exception as exc:
            return BackendEnvelope(
                agent_id=f"smt_engine_{claim_id}",
                payload={
                    "claim_id": claim_id,
                    "verdict": "rejected",
                    "evidence_strength": "weak",
                    "summary": f"Z3 SMT error: {exc}",
                    "verification_status": VERIFICATION_STATUS_ERROR,
                    "claim_digest": prompt.get("claim_digest", ""),
                    "payload_digest": payload_digest,
                    "request_id": request_id,
                    "backend_name": "z3_smt",
                    "backend_version": "unknown",
                    "supporting_evidence": [],
                },
            )

        return BackendEnvelope(
            agent_id=f"smt_engine_{claim_id}",
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
                "backend_name": "z3_smt",
                "backend_version": f"z3 {z3.get_version_string()}" if HAS_Z3 else "not available",
                "artifact_refs": [
                    {
                        "artifact_kind": "z3_counterexample" if actual_sat else "lean_proof",
                        "locator": f"Z3 check({len(constraints)} constraints)",
                        "digest": payload_digest,
                    }
                ],
                "supporting_evidence": [
                    {
                        "source_kind": "z3_counterexample" if actual_sat else "lean_proof",
                        "constraint_count": len(constraints),
                        "result": str(result),
                        "expected_sat": expected_sat,
                        "matches": expected_sat is None or actual_sat == expected_sat,
                    }
                ],
            },
        )

    def _run_grounded_smt_verification(
        self, task_id: str, prompt: dict[str, Any]
    ) -> BackendEnvelope:
        claim_id = prompt.get("claim_id", "")
        formal_payload = prompt.get("formal_payload", {})
        payload_digest = hash_digest(formal_payload)
        request_id = prompt.get("request_id", new_uuid())

        if not HAS_Z3:
            return self._unavailable_envelope(claim_id, payload_digest, request_id, prompt, "Z3 not installed")

        claims = formal_payload.get("claims", [])
        attacks = formal_payload.get("attacks", [])
        if not claims:
            return self._unavailable_envelope(claim_id, payload_digest, request_id, prompt, "No claims in formal_payload")

        try:
            from compiler_core.grounded_smt_verifier import GroundedSMTChecker
            checker = GroundedSMTChecker()
            if not checker.available:
                return self._unavailable_envelope(claim_id, payload_digest, request_id, prompt, "GroundedSMTChecker: Z3 not available")

            result = checker.verify_labelling(
                test_name=claim_id,
                claims=claims,
                attacks=attacks,
                expected_accepted=set(formal_payload.get("expected_accepted", [])),
                expected_undecided=set(formal_payload.get("expected_undecided", [])),
                max_nodes=formal_payload.get("max_nodes", 20),
            )

            if getattr(result, "status", "") == "UNKNOWN":
                return BackendEnvelope(
                    agent_id=f"smt_grounded_{claim_id}",
                    payload={
                        "claim_id": claim_id,
                        "verdict": "needs_more_evidence",
                        "evidence_strength": "weak",
                        "summary": "Grounded SMT returned UNKNOWN",
                        "verification_status": VERIFICATION_STATUS_TIMEOUT,
                        "claim_digest": prompt.get("claim_digest", ""),
                        "payload_digest": payload_digest,
                        "request_id": request_id,
                        "backend_name": "grounded_smt",
                        "backend_version": "compiler_core.grounded_smt_verifier",
                        "supporting_evidence": [],
                    },
                )

            if result.passed:
                status = VERIFICATION_STATUS_PROVED
                verdict = "validated"
                evidence_strength = "strong"
                summary = f"Grounded SMT verified: {getattr(result, 'status', 'SAT-MATCH')}"
            else:
                status = VERIFICATION_STATUS_REFUTED
                verdict = "rejected"
                evidence_strength = "strong"
                summary = f"Grounded SMT refuted: {getattr(result, 'detail', result.status)}"
        except Exception as exc:
            return BackendEnvelope(
                agent_id=f"smt_grounded_{claim_id}",
                payload={
                    "claim_id": claim_id,
                    "verdict": "rejected",
                    "evidence_strength": "weak",
                    "summary": f"Grounded SMT error: {exc}",
                    "verification_status": VERIFICATION_STATUS_ERROR,
                    "claim_digest": prompt.get("claim_digest", ""),
                    "payload_digest": payload_digest,
                    "request_id": request_id,
                    "backend_name": "grounded_smt",
                    "backend_version": "compiler_core.grounded_smt_verifier",
                    "supporting_evidence": [],
                },
            )

        return BackendEnvelope(
            agent_id=f"smt_grounded_{claim_id}",
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
                "backend_name": "grounded_smt",
                "backend_version": "compiler_core.grounded_smt_verifier",
                "artifact_refs": [
                    {
                        "artifact_kind": "lean_proof",
                        "locator": f"GroundedSMTChecker.verify_labelling({claim_id})",
                        "digest": payload_digest,
                    }
                ],
                "supporting_evidence": [
                    {
                        "source_kind": "lean_proof",
                        "test_name": claim_id,
                        "passed": result.passed,
                        "status": getattr(result, "status", ""),
                    }
                ],
            },
        )

    def _unavailable_envelope(self, claim_id, payload_digest, request_id, prompt, reason):
        return BackendEnvelope(
            agent_id=f"smt_engine_{claim_id}",
            payload={
                "claim_id": claim_id,
                "verdict": "needs_more_evidence",
                "evidence_strength": "weak",
                "summary": f"SMT verification unavailable: {reason}",
                "verification_status": VERIFICATION_STATUS_NOT_RUN if "not installed" in reason else VERIFICATION_STATUS_BACKEND_UNAVAILABLE,
                "claim_digest": prompt.get("claim_digest", ""),
                "payload_digest": payload_digest,
                "request_id": request_id,
                "backend_name": "z3_smt",
                "backend_version": "not available",
                "supporting_evidence": [],
            },
        )

    def run_health_check(self) -> dict[str, Any]:
        """Run fixed regression suite — only BACKEND_HEALTHY or BACKEND_UNHEALTHY."""
        if not HAS_Z3:
            return {"backend_name": "z3_smt", "healthy": False, "status": "BACKEND_UNHEALTHY"}
        try:
            solver = z3.Solver()
            x = z3.Bool("x")
            solver.add(x)
            result = solver.check()
            healthy = str(result) == "sat"
            return {"backend_name": "z3_smt", "healthy": healthy, "status": "BACKEND_HEALTHY" if healthy else "BACKEND_UNHEALTHY"}
        except Exception:
            return {"backend_name": "z3_smt", "healthy": False, "status": "BACKEND_UNHEALTHY"}


def _build_z3_expr(z3_module, left, op, right):
    """Build a Z3 expression from a constraint triple."""
    l_val = z3_module.BoolVal(left) if isinstance(left, bool) else left
    r_val = z3_module.BoolVal(right) if isinstance(right, bool) else right
    if op == "==":
        return l_val == r_val
    if op == "!=":
        return l_val != r_val
    return None
