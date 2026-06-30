import json

from deli_autoresearch.memory_router import MemoryRouter


def _read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_verified_finding_requires_strong_evidence(tmp_path):
    router = MemoryRouter(tmp_path)

    result = router.route(
        {
            "event_type": "verified_finding",
            "claim": "model-only",
            "evidence": [{"source_kind": "model_generated"}],
        }
    )

    assert result.accepted is False
    assert result.destination == "failures.jsonl"
    assert not (tmp_path / "findings.jsonl").exists()
    failures = _read_jsonl(tmp_path / "failures.jsonl")
    assert failures[0]["failure_reason"] == "verified_finding lacks strong evidence"


def test_verified_finding_routes_with_strong_evidence(tmp_path):
    router = MemoryRouter(tmp_path)

    result = router.route(
        {
            "event_type": "verified_finding",
            "claim": "source-backed",
            "evidence": [{"source_kind": "local_file", "locator": "manifest.json"}],
        }
    )

    assert result.accepted is True
    findings = _read_jsonl(tmp_path / "findings.jsonl")
    assert findings[0]["claim"] == "source-backed"


def test_rejected_candidate_and_failure_have_distinct_ledgers(tmp_path):
    router = MemoryRouter(tmp_path)

    router.route({"event_type": "rejected_claim", "claim": "bad"})
    router.route({"event_type": "source_candidate", "url": "https://example.invalid"})
    router.route({"event_type": "failure", "failure_reason": "timeout"})

    assert (tmp_path / "rejected_claims.jsonl").exists()
    assert (tmp_path / "source_candidates.jsonl").exists()
    assert (tmp_path / "failures.jsonl").exists()
