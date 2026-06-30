import json

from deli_autoresearch.trial_harness import TrialHarness


def test_two_trials_without_strong_evidence_trigger_pivot(tmp_path):
    harness = TrialHarness(tmp_path / "trials.jsonl")

    first = harness.record_trial(
        trial_id="t1",
        claim_id="c1",
        outcome="needs_more_evidence",
        evidence=[{"source_kind": "model_generated"}],
    )
    second = harness.record_trial(
        trial_id="t2",
        claim_id="c2",
        outcome="needs_more_evidence",
        evidence=[{"source_kind": "derived"}],
    )

    assert first.status == "continue"
    assert second.status == "pivot"
    assert second.consecutive_without_strong_evidence == 2


def test_repeated_failures_trigger_pivot_then_review(tmp_path):
    harness = TrialHarness(tmp_path / "trials.jsonl")

    harness.record_trial(trial_id="t1", claim_id="c1", outcome="failure")
    second = harness.record_trial(trial_id="t2", claim_id="c1", outcome="failure")
    third = harness.record_trial(trial_id="t3", claim_id="c1", outcome="failure")

    assert second.status == "pivot"
    assert third.status == "needs_human_review"
    assert third.repeated_failures == 3


def test_trial_harness_records_without_fact_judgment(tmp_path):
    ledger = tmp_path / "trials.jsonl"
    harness = TrialHarness(ledger)

    harness.record_trial(
        trial_id="t1",
        claim_id="c1",
        outcome="observed",
        evidence=[{"source_kind": "local_file", "locator": "artifact.json"}],
    )

    record = json.loads(ledger.read_text(encoding="utf-8").strip())
    assert record["has_strong_evidence"] is True
    assert "truth" not in record
