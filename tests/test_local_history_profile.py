from deli_autoresearch.local_history_profile import default_minnan_profile


def test_minnan_profile_defaults_to_source_bounded_paths():
    profile = default_minnan_profile()
    paths = profile.planned_paths()

    assert profile.open_web_fact_ingestion is False
    assert any(path.endswith("config") for path in paths)
    assert any(path.endswith("runtime\\findings") for path in paths)
    assert any(path.endswith("runtime\\rejected_claims") for path in paths)


def test_minnan_profile_enforces_claim_evidence_requirements():
    profile = default_minnan_profile()

    errors = profile.validate_claim("historical_fact", {"source_span": "p1"})
    assert errors == ["missing required evidence: primary_or_official_source"]
    assert profile.validate_claim(
        "historical_fact",
        {"source_span": "p1", "primary_or_official_source": "gazetteer"},
    ) == []
    assert "unknown local-history claim type" in profile.validate_claim("rumor", {})[0]
