"""G10 Banach multi-dimensional contraction verification backend (claim-bound).

Verifies actual matrices/operators from formal payload, not fixed regression suites.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

_juris_root = Path(r"D:\Codex\juris-calculus")
if str(_juris_root) not in sys.path:
    sys.path.insert(0, str(_juris_root))

from compiler_core.banach_verifier import BanachVerifier  # noqa: E402

from .agent_backend_codex import BackendEnvelope, CodexAgentBackend, MockAgentBackend
from .models import (
    VERIFICATION_STATUS_BACKEND_UNAVAILABLE,
    VERIFICATION_STATUS_PROVED,
    VERIFICATION_STATUS_REFUTED,
    hash_digest,
    new_uuid,
)


class BanachBackend:
    """Hybrid backend: work -> agent, verification -> BanachVerifier + agent fallback.

    Verification is claim-bound: verifies the actual matrix/operator from the
    work agent candidate formal_payload, not the fixed regression suite.
    """

    def __init__(self, inner_backend: CodexAgentBackend | MockAgentBackend) -> None:
        self.inner = inner_backend
        self.verifier = BanachVerifier()

    def run_work(self, task_id: str, prompt: dict[str, Any]) -> BackendEnvelope:
        return self.inner.run_work(task_id, prompt)

    def run_verification(self, task_id: str, prompt: dict[str, Any]) -> BackendEnvelope:
        verification_type = prompt.get("verification_type", "")
        if verification_type == "banach_contraction":
            return self._run_claim_bound_verification(task_id, prompt)
        return self.inner.run_verification(task_id, prompt)

    def _run_claim_bound_verification(
        self, task_id: str, prompt: dict[str, Any]
    ) -> BackendEnvelope:
        claim_id = prompt.get("claim_id", "")
        formal_payload = prompt.get("formal_payload", {})
        payload_digest = hash_digest(formal_payload)
        request_id = prompt.get("request_id", new_uuid())
        matrix = formal_payload.get("matrix", [])
        norm_type = formal_payload.get("norm_type", "max")
        threshold = formal_payload.get("threshold", 1.0)

        if not matrix:
            return BackendEnvelope(
                agent_id=f"banach_engine_{claim_id}",
                payload={
                    "claim_id": claim_id,
                    "verdict": "rejected",
                    "evidence_strength": "weak",
                    "summary": "No matrix provided in formal_payload",
                    "verification_status": VERIFICATION_STATUS_BACKEND_UNAVAILABLE,
                    "claim_digest": prompt.get("claim_digest", ""),
                    "payload_digest": payload_digest,
                    "request_id": request_id,
                    "backend_name": "banach",
                    "backend_version": "compiler_core.banach_verifier.BanachVerifier",
                    "supporting_evidence": [],
                },
            )

        try:
            if norm_type == "max":
                norm_value = self.verifier.max_norm(matrix)
            elif norm_type == "l1":
                norm_value = self.verifier.l1_norm(matrix)
            elif norm_type == "frobenius":
                norm_value = self.verifier.frobenius_norm(matrix)
            else:
                norm_value = self.verifier.max_norm(matrix)

            is_contraction = norm_value < threshold
        except Exception as exc:
            return BackendEnvelope(
                agent_id=f"banach_engine_{claim_id}",
                payload={
                    "claim_id": claim_id,
                    "verdict": "rejected",
                    "evidence_strength": "weak",
                    "summary": f"Banach verification error: {exc}",
                    "verification_status": VERIFICATION_STATUS_BACKEND_UNAVAILABLE,
                    "claim_digest": prompt.get("claim_digest", ""),
                    "payload_digest": payload_digest,
                    "request_id": request_id,
                    "backend_name": "banach",
                    "backend_version": "compiler_core.banach_verifier.BanachVerifier",
                    "supporting_evidence": [],
                },
            )

        if is_contraction:
            status = VERIFICATION_STATUS_PROVED
            verdict = "validated"
            evidence_strength = "strong"
            summary = f"Banach contraction verified: {norm_type}-norm = {norm_value:.6f} < {threshold}"
        else:
            status = VERIFICATION_STATUS_REFUTED
            verdict = "rejected"
            evidence_strength = "strong"
            summary = f"Banach contraction refuted: {norm_type}-norm = {norm_value:.6f} >= {threshold}"

        return BackendEnvelope(
            agent_id=f"banach_engine_{claim_id}",
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
                "backend_name": "banach",
                "backend_version": "compiler_core.banach_verifier.BanachVerifier",
                "artifact_refs": [
                    {
                        "artifact_kind": "banach_norm_test",
                        "locator": f"BanachVerifier.{norm_type}_norm(matrix={len(matrix)}x{len(matrix[0]) if matrix else 0})",
                        "digest": payload_digest,
                    }
                ],
                "supporting_evidence": [
                    {
                        "source_kind": "banach_norm_test",
                        "norm_type": norm_type,
                        "norm_value": norm_value,
                        "threshold": threshold,
                        "is_contraction": is_contraction,
                    }
                ],
            },
        )

    def run_health_check(self) -> dict[str, Any]:
        """Run fixed regression — only BACKEND_HEALTHY or BACKEND_UNHEALTHY."""
        report = self.verifier.run_full_regression()
        return {
            "backend_name": "banach",
            "healthy": report.get("failed", 0) == 0,
            "passed": report.get("passed", 0),
            "failed": report.get("failed", 0),
            "total": report.get("total", 0),
            "status": "BACKEND_HEALTHY" if report.get("failed", 0) == 0 else "BACKEND_UNHEALTHY",
        }
