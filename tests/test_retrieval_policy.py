from deli_autoresearch.retrieval_policy import RetrievalPolicy
from deli_autoresearch.source_registry import SourceRecord, SourceRegistry


def test_retrieval_policy_allows_only_approved_sources():
    registry = SourceRegistry(
        [
            SourceRecord("approved_source", "approved"),
            SourceRecord("proposed_source", "proposed"),
            SourceRecord("rejected_source", "rejected"),
        ]
    )
    policy = RetrievalPolicy(registry)

    assert policy.decide("approved_source").allowed is True
    assert policy.decide("proposed_source").allowed is False
    assert policy.decide("rejected_source").allowed is False
    assert policy.decide("missing_source").allowed is False
    assert policy.filter_retrievable(
        ["approved_source", "proposed_source", "missing_source"]
    ) == ["approved_source"]


def test_open_web_can_only_create_source_candidate():
    policy = RetrievalPolicy(SourceRegistry([]))

    decision = policy.decide("https://example.invalid/paper", channel="open_web")

    assert decision.allowed is False
    assert decision.action == "source_candidate"
    assert decision.source_status == "unverified"
