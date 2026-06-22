"""G10 Banach multi-dimensional contraction verification backend.

Wraps the juris-calculus BanachVerifier for deterministic contraction checking.
Used when verification prompts carry run_banach_verification: true.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

# Add juris-calculus to path to import banach_verifier
_juris_root = Path(r"D:\Codex\juris-calculus")
if str(_juris_root) not in sys.path:
    sys.path.insert(0, str(_juris_root))

from compiler_core.banach_verifier import BanachVerifier  # noqa: E402

from .agent_backend_codex import BackendEnvelope, CodexAgentBackend, MockAgentBackend


class BanachBackend:
    """Hybrid backend: work -> agent, verification -> BanachVerifier + agent fallback.

    When verification prompt sets run_banach_verification: true, the BanachVerifier
    runs the full contraction regression and returns a structured verdict.
    Otherwise verification is delegated to the inner backend.
    """

    def __init__(self, inner_backend: CodexAgentBackend | MockAgentBackend) -> None:
        self.inner = inner_backend
        self.verifier = BanachVerifier()

    def run_work(self, task_id: str, prompt: dict[str, Any]) -> BackendEnvelope:
        return self.inner.run_work(task_id, prompt)

    def run_verification(self, task_id: str, prompt: dict[str, Any]) -> BackendEnvelope:
        if prompt.get("run_banach_verification"):
            return self._run_banach_verification(task_id, prompt)
        return self.inner.run_verification(task_id, prompt)

    def _run_banach_verification(self, task_id: str, prompt: dict[str, Any]) -> BackendEnvelope:
        claim_id = prompt.get("claim_id", "")
        report = self.verifier.run_full_regression()

        if report["failed"] == 0:
            verdict = "validated"
            summary = (
                f"Banach contraction regression passed ({report['passed']}/{report['total']} tests). "
                f"All matrices satisfy contraction properties."
            )
            evidence_strength = "strong"
        else:
            verdict = "rejected"
            failed_names = [r["name"] for r in report["results"] if not r["passed"]]
            summary = (
                f"Banach contraction regression failed {report['failed']}/{report['total']} tests. "
                f"Failed: {failed_names}"
            )
            evidence_strength = "strong"

        payload = {
            "claim_id": claim_id,
            "verdict": verdict,
            "evidence_strength": evidence_strength,
            "summary": summary,
            "supporting_evidence": [
                {
                    "source_kind": "banach_norm_test",
                    "test_name": r["name"],
                    "passed": r["passed"],
                }
                for r in report["results"]
            ],
        }
        agent_id = f"banach_engine_{claim_id}"
        return BackendEnvelope(agent_id=agent_id, payload=payload)
