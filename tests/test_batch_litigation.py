"""Tests for P2 batch litigation runner."""

from deli_autoresearch.batch_litigation import (
    run_batch_litigation,
    BatchLitigationCase,
)


def test_single_case_horn_to_grounded_certificates():
    cases = [
        BatchLitigationCase(
            case_id="simple_chain",
            facts={"a", "b"},
            horn_rules=[
                {"head": "C", "body": ["a", "b"]},
                {"head": "D", "body": ["C"]},
            ],
            target_claims=["C", "D"],
        )
    ]
    report = run_batch_litigation(cases)
    assert report.all_passed
    assert report.total_cases == 1
    result = report.cases[0]
    assert len(result.certificates) == 2
    assert len(result.rule_impacts) == 2
    assert len(result.missing_evidence) == 2


def test_batch_report_aggregates_multiple_cases():
    cases = [
        BatchLitigationCase(
            case_id="case1",
            facts={"a"},
            horn_rules=[{"head": "C", "body": ["a"]}],
            target_claims=["C"],
        ),
        BatchLitigationCase(
            case_id="case2",
            facts={"x", "y"},
            horn_rules=[{"head": "Z", "body": ["x", "y"]}],
            target_claims=["Z"],
        ),
    ]
    report = run_batch_litigation(cases)
    assert report.total_cases == 2
    assert report.pass_count == 2
    assert report.fail_count == 0
    assert report.all_passed
    assert len(report.cases) == 2
