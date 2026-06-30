import pytest

from deli_autoresearch.verification_backends import (
    BACKEND_CONTRACTS,
    HUMAN_REVIEW_BACKEND,
    LEAN_MANIFEST_BACKEND,
    BackendResult,
    fail_closed_backend_result,
)


def test_required_backend_contracts_are_registered():
    expected = {
        "lean_manifest_backend",
        "jc_runtime_backend",
        "spec_shadow_backend",
        "source_span_backend",
        "ocr_alignment_backend",
        "citation_upgrade_backend",
        "human_review_backend",
    }

    assert expected.issubset(BACKEND_CONTRACTS)


def test_backend_result_requires_known_backend_and_valid_status():
    result = BackendResult(
        backend_name=LEAN_MANIFEST_BACKEND,
        backend_version="v1",
        status="validated",
        input_digest="input",
        output_digest="output",
    )

    assert result.to_dict()["backend_name"] == LEAN_MANIFEST_BACKEND
    with pytest.raises(ValueError, match="unknown verification backend"):
        BackendResult("unknown", "v1", "validated", "input", "output")
    with pytest.raises(ValueError, match="invalid verification backend status"):
        BackendResult(HUMAN_REVIEW_BACKEND, "v1", "passed", "input", "output")


def test_fail_closed_backend_result_uses_needs_more_evidence():
    result = fail_closed_backend_result(
        LEAN_MANIFEST_BACKEND,
        input_payload={"manifest": "missing"},
        reason="manifest not found",
    )

    assert result.status == "needs_more_evidence"
    assert result.input_digest
    assert result.output_digest
