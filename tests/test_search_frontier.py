import json

import pytest

from deli_autoresearch.search_frontier import SearchFrontier


def test_search_frontier_ranks_active_candidates(tmp_path):
    frontier = SearchFrontier(tmp_path / "frontier.jsonl")

    frontier.add(node_id="low", objective="Weak direction", metrics={"score": 0.1})
    frontier.add(node_id="high", objective="Strong direction", metrics={"score": 0.9})

    assert [node.node_id for node in frontier.active()] == ["high", "low"]


def test_search_frontier_preserves_lineage_and_status(tmp_path):
    frontier = SearchFrontier(tmp_path / "frontier.jsonl")

    frontier.add(node_id="root", objective="Initial source-bounded plan")
    frontier.add(
        node_id="child",
        objective="Refined plan",
        parent_id="root",
        mutation_type="refine",
        metrics={"score": 0.7},
    )
    promoted = frontier.promote(
        "child",
        reason="passed source-span verification",
        verifier="source_span_backend",
    )

    assert promoted.status == "promoted"
    assert [node.node_id for node in frontier.lineage("child")] == ["root", "child"]
    assert frontier.active()[0].node_id == "root"


def test_search_frontier_keeps_discarded_negative_results(tmp_path):
    ledger = tmp_path / "frontier.jsonl"
    frontier = SearchFrontier(ledger)

    frontier.add(node_id="bad", objective="Open-web fact import", metrics={"score": 0.2})
    discarded = frontier.discard("bad", reason="open-web source cannot become verified finding")

    assert discarded.status == "discarded"
    records = [json.loads(line) for line in ledger.read_text(encoding="utf-8").splitlines()]
    assert records[-1]["reason"] == "open-web source cannot become verified finding"


def test_search_frontier_fails_closed_on_unknown_node(tmp_path):
    frontier = SearchFrontier(tmp_path / "frontier.jsonl")

    with pytest.raises(KeyError):
        frontier.promote("missing", reason="not present", verifier="source_span_backend")


def test_search_frontier_promotion_requires_verifier_or_source_approval(tmp_path):
    frontier = SearchFrontier(tmp_path / "frontier.jsonl")
    frontier.add(node_id="candidate", objective="Candidate source review")

    with pytest.raises(ValueError, match="verifier or source approval"):
        frontier.promote("candidate", reason="reason alone is not enough")
