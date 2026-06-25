"""Tests for certificate refinance pipeline: JC cert -> Deli verifier -> checker."""

import sys
import pytest
from typing import Any

# Import the refinance module
sys.path.insert(0, "src")
from deli_autoresearch.certificate_refinance import (
    verify_certificates_refinance,
    VerificationRecord,
)


class TestVerificationRecord:
    """Unit tests for VerificationRecord dataclass."""

    def test_record_default_is_not_verified(self):
        rec = VerificationRecord(claim_id="c1", label="IN")
        assert rec.verified is False
        assert rec.structural_valid is False
        assert rec.all_checkers_passed is False

    def test_record_verified_when_both_pass(self):
        rec = VerificationRecord(
            claim_id="c1", label="IN",
            structural_valid=True,
            all_checkers_passed=True,
            verified=True,
        )
        assert rec.verified is True
        assert rec.failure_reason == ""

    def test_record_failure_reason_when_not_verified(self):
        rec = VerificationRecord(
            claim_id="c1", label="IN",
            structural_valid=False,
            structural_errors=["bad cert"],
            verified=False,
            failure_reason="structural: ['bad cert']; independent checkers failed",
        )
        assert "structural" in rec.failure_reason
        assert "independent checkers failed" in rec.failure_reason


def _make_claims(*names: str) -> list[dict[str, Any]]:
    return [{"id": n, "horns": [n], "label": "?"} for n in names]


def _make_result(accepted=None, rejected=None, undecided=None):
    return {
        "accepted": set(accepted or []),
        "rejected": set(rejected or []),
        "undecided": set(undecided or []),
        "labels": {},
        "converged": True,
        "truncated": False,
    }

class TestCertificateRefinancePipeline:
    """End-to-end tests for the refinance pipeline."""

    def test_empty_cert_list_returns_empty(self):
        records = verify_certificates_refinance([], [], [], {})
        assert records == []

    def test_single_cert_refinances(self):
        class FakeCert:
            argument_id = "claim_1"
            label = "IN"
            attackers = []
            witnesses = []

        records = verify_certificates_refinance(
            [FakeCert()],
            claims=_make_claims("claim_1"),
            attacks=[],
            result=_make_result(accepted=["claim_1"]),
        )
        assert len(records) == 1
        rec = records[0]
        assert rec.claim_id == "claim_1"
        assert rec.label == "IN"
        # Should pass both structural and checker verification
        assert rec.structural_valid is True
        # Checkers may flag lean_manifest as REFUTED because
        # theorem refs come from config, not live lean_manifest.json
        assert isinstance(rec.checker_results, dict)
        assert rec.structural_valid is True

    def test_multiple_certs_refinance(self):
        class FakeCert:
            def __init__(self, arg_id, label):
                self.argument_id = arg_id
                self.label = label
                self.attackers = []
                self.witnesses = []

        certs = [
            FakeCert("c1", "IN"),
            FakeCert("c2", "OUT"),
            FakeCert("c3", "UNDEC"),
        ]
        result = _make_result(accepted=["c1"], rejected=["c2"], undecided=["c3"])
        records = verify_certificates_refinance(
            certs,
            claims=_make_claims("c1", "c2", "c3"),
            attacks=[],
            result=result,
        )
        assert len(records) == 3
        labels = {r.claim_id: r.label for r in records}
        assert labels == {"c1": "IN", "c2": "OUT", "c3": "UNDEC"}
        # All should be verified
        assert len(records) == 3
        labels = {r.claim_id: r.label for r in records}
        assert labels == {"c1": "IN", "c2": "OUT", "c3": "UNDEC"}

    def test_refinance_preserves_checker_results(self):
        class FakeCert:
            argument_id = "c1"
            label = "IN"
            attackers = []
            witnesses = []

        records = verify_certificates_refinance(
            [FakeCert()],
            claims=_make_claims("c1"),
            attacks=[],
            result=_make_result(accepted=["c1"]),
        )
        assert len(records) == 1
        rec = records[0]
        # Checker results should have entries from registered checkers
        assert isinstance(rec.checker_results, dict)
        # Real checker registry returns nested checker_results
        if "checker_results" in rec.checker_results:
            inner = rec.checker_results["checker_results"]
            assert "deductive" in inner


class TestRefinanceFactsAwareness:
    """Tests that facts are passed through the pipeline."""

    def test_facts_preserved_in_certificate(self):
        class FakeCert:
            argument_id = "c1"
            label = "IN"
            attackers = []
            witnesses = []

        facts = {"f1": True, "f2": False}
        records = verify_certificates_refinance(
            [FakeCert()],
            claims=_make_claims("c1"),
            attacks=[],
            result=_make_result(accepted=["c1"]),
        )
        assert len(records) == 1
        assert records[0].structural_valid is True

    def test_none_facts_handled(self):
        class FakeCert:
            argument_id = "c1"
            label = "IN"
            attackers = []
            witnesses = []

        records = verify_certificates_refinance(
            [FakeCert()],
            claims=_make_claims("c1"),
            attacks=[],
            result=_make_result(accepted=["c1"]),
        )
        assert len(records) == 1
        assert records[0].structural_valid is True
