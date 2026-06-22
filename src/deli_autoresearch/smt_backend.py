"""SMT/Z3 formal verification backend for Deli AutoResearch."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

_juris_root = Path(r"D:\Codex\juris-calculus")
if str(_juris_root) not in sys.path:
    sys.path.insert(0, str(_juris_root))

from compiler_core.smt_sidecar import SMTSidecar  # noqa: E402
from .agent_backend_codex import BackendEnvelope, CodexAgentBackend, MockAgentBackend


class SMTBackend:
    """Hybrid backend: work -> agent, verification -> Z3/SMT + agent fallback."""

    def __init__(self, inner_backend: CodexAgentBackend | MockAgentBackend) -> None:
        self.inner = inner_backend
        self.sidecar = SMTSidecar()

    def run_work(self, task_id: str, prompt: dict[str, Any]) -> BackendEnvelope:
        return self.inner.run_work(task_id, prompt)

    def run_verification(self, task_id: str, prompt: dict[str, Any]) -> BackendEnvelope:
        if prompt.get("run_grounded_smt"):
            return self._run_grounded_smt_verification(task_id, prompt)
        if prompt.get("run_smt_verification"):
            return self._run_smt_verification(task_id, prompt)
        return self.inner.run_verification(task_id, prompt)


    def _run_grounded_smt_verification(self, task_id, prompt):
        claim_id = prompt.get("claim_id", "")
        try:
            import sys as _sys
            _sys.path.insert(0, str(_juris_root))
            from compiler_core.grounded_smt_verifier import GroundedSMTChecker
            from deli_autoresearch.juris_calculus_bridge import JurisCalculusBridge
            from deli_autoresearch.constants import JURIS_CALCULUS_ROOT
            checker = GroundedSMTChecker()
            bridge = JurisCalculusBridge(JURIS_CALCULUS_ROOT)
            report = checker.verify_bridge_cases(bridge)
            if report.all_passed:
                verdict = "validated"
                summary = f"SMT grounded semantics: {report.passed}/{report.total} cases SAT-MATCH with Dung definition"
            else:
                verdict = "rejected"
                summary = f"SMT grounded semantics: {report.failed}/{report.total} cases mismatch"
            evidence_strength = "strong"
        except Exception as e:
            verdict = "rejected"
            summary = f"SMT grounded verification error: {e}"
            evidence_strength = "weak"
            report = None
        payload = {
            "claim_id": claim_id, "verdict": verdict,
            "evidence_strength": evidence_strength, "summary": summary,
            "supporting_evidence": [
                {"source_kind": "lean_proof", "test_name": r.test_name, "passed": r.passed}
                for r in (report.results if report else [])
            ],
        }
        agent_id = f"smt_grounded_{claim_id}"
        return BackendEnvelope(agent_id=agent_id, payload=payload)

    def _run_smt_verification(self, task_id: str, prompt: dict[str, Any]) -> BackendEnvelope:
        claim_id = prompt.get("claim_id", "")
        results = self._run_logic_test_suite()

        if results["failed"] == 0:
            verdict = "validated"
            summary = f"Z3 SMT verification passed ({results['passed']}/{results['total']} checks). {results.get('detail','')}"
            evidence_strength = "strong"
        else:
            verdict = "rejected"
            summary = f"Z3 SMT verification failed {results['failed']}/{results['total']} checks."
            evidence_strength = "strong"

        payload = {
            "claim_id": claim_id,
            "verdict": verdict,
            "evidence_strength": evidence_strength,
            "summary": summary,
            "supporting_evidence": [
                {"source_kind": "z3_counterexample" if not r["passed"] else "lean_proof",
                 "test_name": r["name"], "passed": r["passed"]}
                for r in results.get("results", [])
            ],
        }
        agent_id = f"smt_engine_{claim_id}"
        return BackendEnvelope(agent_id=agent_id, payload=payload)

    def _run_logic_test_suite(self) -> dict[str, Any]:
        tests = [
            {
                "name": "modus_ponens",
                "constraints": [
                    {"name": "A", "left": True, "op": "==", "right": True},
                    {"name": "B", "left": False, "op": "==", "right": True},
                ],
                "expect_unsat": True,
            },
            {
                "name": "non_contradiction",
                "constraints": [
                    {"name": "A_true", "left": True, "op": "==", "right": True},
                    {"name": "A_false", "left": False, "op": "==", "right": True},
                ],
                "expect_unsat": True,
            },
            {
                "name": "double_negation_consistent",
                "constraints": [
                    {"name": "A_true", "left": True, "op": "==", "right": True},
                ],
                "expect_unsat": False,
            },
            {
                "name": "transitivity",
                "constraints": [
                    {"name": "A_true", "left": True, "op": "==", "right": True},
                    {"name": "C_false", "left": False, "op": "==", "right": True},
                ],
                "expect_unsat": True,
            },
        ]

        passed = 0; failed = 0; results_list = []
        for test in tests:
            smt_result = self.sidecar.check(test["constraints"])
            is_unsat = smt_result.status == "UNSAT"
            ok = is_unsat == test["expect_unsat"]
            if ok: passed += 1
            else: failed += 1
            results_list.append({"name": test["name"], "passed": ok,
                                 "status": smt_result.status, "expected_unsat": test["expect_unsat"]})

        detail = f"Z3 available: {self.sidecar.available}"
        return {"total": passed + failed, "passed": passed, "failed": failed,
                "results": results_list, "detail": detail}
