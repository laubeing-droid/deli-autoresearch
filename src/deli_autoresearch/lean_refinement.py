"""Lean-to-Python refinement helpers for grounded extension."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .canonical_fixture import CanonicalCase, CanonicalTestSuite
from .certificate_payload import GroundedExtensionCertificate
from .independent_checker import IndependentCheckerRegistry
from .juris_calculus_bridge import JurisCalculusBridge
from .lean_manifest import DEFAULT_LEAN_MANIFEST_PATH


@dataclass
class RefinementReport:
    total: int
    passed: int
    failed: int
    results: list[dict[str, Any]]

    @property
    def all_passed(self) -> bool:
        return self.failed == 0


class LeanRefinementBridge:
    def __init__(self, *, manifest_path: str = DEFAULT_LEAN_MANIFEST_PATH, juris_root: str) -> None:
        self.bridge = JurisCalculusBridge(juris_root)
        self.checkers = IndependentCheckerRegistry(
            juris_root=juris_root,
            manifest_path=manifest_path,
        )

    def differential_test(self, case: CanonicalCase) -> dict[str, Any]:
        raw = self.bridge.run_grounded_extension(case.claims, case.attacks)
        cert = GroundedExtensionCertificate.from_engine_result(
            case.claims,
            case.attacks,
            raw,
            engine_commit=self.bridge._get_commit_sha(),
        )
        check = self.checkers.verify_all(cert)
        expected_match = (
            sorted(raw.get("accepted", [])) == case.expected_accepted
            and sorted(raw.get("undecided", [])) == case.expected_undecided
        )
        passed = expected_match and check["overall"] == "verified"
        return {
            "name": case.name,
            "passed": passed,
            "expected_match": expected_match,
            "checker_overall": check["overall"],
            "violations": check["violations"],
        }

    def run_cross_repo_regression(self) -> RefinementReport:
        results = [self.differential_test(case) for case in CanonicalTestSuite.grounded_extension_cases()]
        passed = sum(1 for item in results if item["passed"])
        failed = len(results) - passed
        return RefinementReport(total=len(results), passed=passed, failed=failed, results=results)
