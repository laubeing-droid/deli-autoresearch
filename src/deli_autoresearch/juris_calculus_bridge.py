"""Bridge to juris-calculus grounded_extension engine.

Provides a thin wrapper that imports juris-calculus's compiler_core
and runs grounded_extension on arbitrary claim/attack graphs.
Used by JurisCalculusBackend for deterministic local verification.
"""

from __future__ import annotations

import importlib
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class BridgeResult:
    """Result of running grounded_extension on a test case."""
    accepted: list[str]
    rejected: list[str]
    undecided: list[str]
    iterations: int
    test_name: str = ""
    passed: bool = True
    error: str | None = None


@dataclass
class RegressionReport:
    """Aggregated report from running multiple test cases."""
    total: int = 0
    passed: int = 0
    failed: int = 0
    results: list[BridgeResult] = field(default_factory=list)

    @property
    def all_passed(self) -> bool:
        return self.failed == 0


class JurisCalculusBridge:
    """Direct Python bridge to juris-calculus grounded_extension.

    Adds the juris-calculus source root to sys.path and imports
    compiler_core.argumentation.grounded_extension for local execution.
    """

    def __init__(self, juris_root: str | Path) -> None:
        self.juris_root = Path(juris_root).resolve()
        self._grounded_fn = None

    def _ensure_import(self) -> Any:
        if self._grounded_fn is not None:
            return self._grounded_fn
        root_str = str(self.juris_root)
        if root_str not in sys.path:
            sys.path.insert(0, root_str)
        mod = importlib.import_module("compiler_core.argumentation")
        self._grounded_fn = mod.grounded_extension
        return self._grounded_fn

    def run_grounded_extension(
        self,
        claims: list[dict[str, Any]],
        attacks: list[tuple[str, str]],
        *,
        max_iter: int = 100,
    ) -> dict[str, Any]:
        """Run grounded_extension and return the raw result dict."""
        fn = self._ensure_import()
        return fn(claims, attacks, max_iter=max_iter)

    def run_test_case(
        self,
        name: str,
        claims: list[dict[str, Any]],
        attacks: list[tuple[str, str]],
        *,
        expected_accepted: set[str] | None = None,
        expected_undecided: set[str] | None = None,
        max_iter: int = 100,
    ) -> BridgeResult:
        """Run one test case and optionally assert expected outcome."""
        try:
            raw = self.run_grounded_extension(claims, attacks, max_iter=max_iter)
            accepted = set(raw.get("accepted", []))
            undecided = set(raw.get("undecided", []))
            passed = True
            if expected_accepted is not None and accepted != expected_accepted:
                passed = False
            if expected_undecided is not None and undecided != expected_undecided:
                passed = False
            return BridgeResult(
                accepted=sorted(accepted),
                rejected=sorted(raw.get("rejected", [])),
                undecided=sorted(undecided),
                iterations=raw.get("iterations", 0),
                test_name=name,
                passed=passed,
            )
        except Exception as exc:
            return BridgeResult(
                accepted=[], rejected=[], undecided=[], iterations=0,
                test_name=name, passed=False, error=str(exc),
            )

    # ------------------------------------------------------------------
    # Built-in G9 test corpus
    # ------------------------------------------------------------------

    @staticmethod
    def dag_linear_cases() -> list[dict[str, Any]]:
        """A -> B -> C: A accepted, B rejected, C accepted."""
        return [
            {
                "name": "dag_linear_A_B_C",
                "claims": [{"id": "A"}, {"id": "B"}, {"id": "C"}],
                "attacks": [("A", "B"), ("B", "C")],
                "expected_accepted": {"A", "C"},
                "expected_undecided": set(),
            },
            {
                "name": "dag_single_attack",
                "claims": [{"id": "X"}, {"id": "Y"}],
                "attacks": [("X", "Y")],
                "expected_accepted": {"X"},
                "expected_undecided": set(),
            },
        ]

    @staticmethod
    def bidirectional_cycle_cases() -> list[dict[str, Any]]:
        """A <-> B: both undecided under grounded semantics."""
        return [
            {
                "name": "bidirectional_A_B",
                "claims": [{"id": "A"}, {"id": "B"}],
                "attacks": [("A", "B"), ("B", "A")],
                "expected_accepted": set(),
                "expected_undecided": {"A", "B"},
            },
        ]

    @staticmethod
    def triangle_cycle_cases() -> list[dict[str, Any]]:
        """A -> B -> C -> A (odd cycle): all undecided."""
        return [
            {
                "name": "triangle_A_B_C",
                "claims": [{"id": "A"}, {"id": "B"}, {"id": "C"}],
                "attacks": [("A", "B"), ("B", "C"), ("C", "A")],
                "expected_accepted": set(),
                "expected_undecided": {"A", "B", "C"},
            },
        ]

    @staticmethod
    def even_cycle_cases() -> list[dict[str, Any]]:
        """A -> B -> C -> D -> A (even cycle): all undecided."""
        return [
            {
                "name": "even_cycle_A_B_C_D",
                "claims": [{"id": "A"}, {"id": "B"}, {"id": "C"}, {"id": "D"}],
                "attacks": [("A", "B"), ("B", "C"), ("C", "D"), ("D", "A")],
                "expected_accepted": set(),
                "expected_undecided": {"A", "B", "C", "D"},
            },
        ]

    @staticmethod
    def mixed_cases() -> list[dict[str, Any]]:
        """DAG nodes alongside a cycle: cycle undecided, DAG nodes resolved."""
        return [
            {
                "name": "mixed_dag_plus_cycle",
                "claims": [
                    {"id": "P"}, {"id": "Q"},
                    {"id": "A"}, {"id": "B"},
                ],
                "attacks": [
                    ("P", "Q"),
                    ("A", "B"), ("B", "A"),
                ],
                "expected_accepted": {"P"},
                "expected_undecided": {"A", "B"},
            },
        ]

    def run_full_regression(self) -> RegressionReport:
        """Run all built-in test cases and produce a report."""
        all_cases = (
            self.dag_linear_cases()
            + self.bidirectional_cycle_cases()
            + self.triangle_cycle_cases()
            + self.even_cycle_cases()
            + self.mixed_cases()
        )
        report = RegressionReport()
        for case in all_cases:
            result = self.run_test_case(
                case["name"],
                case["claims"],
                case["attacks"],
                expected_accepted=case.get("expected_accepted"),
                expected_undecided=case.get("expected_undecided"),
            )
            report.total += 1
            if result.passed:
                report.passed += 1
            else:
                report.failed += 1
            report.results.append(result)
        return report
