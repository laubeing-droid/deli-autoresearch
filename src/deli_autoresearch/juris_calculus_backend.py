"""Hybrid backend: work via agent, verification via local juris-calculus engine.

This backend pairs a creative work agent (CodexAgentBackend or MockAgentBackend)
with a deterministic local verification engine that calls juris-calculus's
grounded_extension directly.  Verification prompts that include a
'run_local_engine' flag trigger local execution; otherwise the inner
backend handles verification as usual.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .agent_backend_codex import BackendEnvelope, CodexAgentBackend, MockAgentBackend
from .juris_calculus_bridge import JurisCalculusBridge


class JurisCalculusBackend:
    """Hybrid backend: work -> agent, verification -> local engine + agent fallback.

    When the verification prompt sets `run_local_engine: true`, the
    bridge runs the full regression suite and returns a structured
    verdict.  Otherwise verification is delegated to the inner backend.
    """

    def __init__(
        self,
        inner_backend: CodexAgentBackend | MockAgentBackend,
        juris_root: str | Path,
    ) -> None:
        self.inner = inner_backend
        self.bridge = JurisCalculusBridge(juris_root)

    # -- work: always delegate to inner agent --
    def run_work(self, task_id: str, prompt: dict[str, Any]) -> BackendEnvelope:
        return self.inner.run_work(task_id, prompt)

    # -- verification: local engine first, fallback to inner --
    def run_verification(self, task_id: str, prompt: dict[str, Any]) -> BackendEnvelope:
        claim_id = prompt.get("claim_id", "")
        claim_text = prompt.get("claim", "")

        if prompt.get("run_local_engine"):
            return self._run_local_verification(task_id, claim_id, claim_text, prompt)

        # Fallback: delegate to inner backend
        return self.inner.run_verification(task_id, prompt)

    def _run_local_verification(
        self,
        task_id: str,
        claim_id: str,
        claim_text: str,
        prompt: dict[str, Any],
    ) -> BackendEnvelope:
        """Run the juris-calculus bridge and map results to a verification verdict."""
        report = self.bridge.run_full_regression()

        if report.all_passed:
            verdict = "validated"
            summary = (
                f"Local engine regression passed ({report.passed}/{report.total} tests). "
                f"All DAG + cycle cases produce expected grounded extensions."
            )
            evidence_strength = "strong"
        else:
            verdict = "rejected"
            failed_names = [r.test_name for r in report.results if not r.passed]
            summary = (
                f"Local engine regression failed {report.failed}/{report.total} tests. "
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
                    "source_kind": "juris_test_pass",
                    "test_name": r.test_name,
                    "passed": r.passed,
                    "accepted": r.accepted,
                    "rejected": r.rejected,
                    "undecided": r.undecided,
                    "iterations": r.iterations,
                    "error": r.error,
                }
                for r in report.results
            ],
        }
        # Use a synthetic agent_id since no external agent was involved.
        agent_id = f"juris_engine_{claim_id}"
        return BackendEnvelope(agent_id=agent_id, payload=payload)
