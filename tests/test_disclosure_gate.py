import pytest

from deli_autoresearch.disclosure_gate import (
    BLOCKED,
    PRIVATE_LAYER,
    PUBLIC_KERNEL,
    ReportRow,
    build_report_row,
)


def test_report_row_requires_block_reason_when_disclosure_denied():
    with pytest.raises(ValueError, match="blocked_reason"):
        ReportRow(
            claim_id="c1",
            claim_text="claim",
            source_id="s1",
            evidence_path="artifact.json",
            verifier="source_span_backend",
            verifier_status="validated",
            public_private_classification=BLOCKED,
            allowed_disclosure=False,
        )


def test_public_kernel_report_row_requires_source_evidence():
    row = build_report_row(
        {
            "claim_id": "c1",
            "claim": "source-backed claim",
            "source_id": "formal_theorem_manifest",
            "evidence_path": "runtime/report.json",
            "backend_name": "lean_manifest_backend",
            "verification_status": "validated",
        }
    )

    assert row.public_private_classification == PUBLIC_KERNEL
    assert row.allowed_disclosure is True


def test_private_marker_blocks_release_evidence():
    row = build_report_row(
        {
            "claim_id": "c1",
            "claim": "client litigation_strategy output",
            "source_id": "private",
            "evidence_path": "private.json",
            "backend_name": "human_review_backend",
            "verification_status": "validated",
        }
    )

    assert row.public_private_classification == PRIVATE_LAYER
    assert row.allowed_disclosure is False
    assert "private marker" in row.blocked_reason


def test_missing_source_evidence_is_blocked():
    row = build_report_row(
        {
            "claim_id": "c1",
            "claim": "unsupported claim",
            "backend_name": "source_span_backend",
            "verification_status": "validated",
        }
    )

    assert row.public_private_classification == BLOCKED
    assert row.allowed_disclosure is False
