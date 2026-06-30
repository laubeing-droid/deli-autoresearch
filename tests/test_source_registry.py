import json

import pytest

from deli_autoresearch.source_registry import SourceRegistry


def test_source_registry_reads_all_statuses(tmp_path):
    path = tmp_path / "sources.json"
    path.write_text(
        json.dumps(
            {
                "sources": [
                    {
                        "id": "formal",
                        "review_status": "approved",
                        "kind": "local_file",
                        "location": "manifest.json",
                        "trust_tier": "official",
                        "allowed_tasks": ["lean_manifest_backend"],
                        "forbidden_tasks": ["open_web_fact_memory"],
                    },
                    {
                        "id": "candidate",
                        "review_status": "proposed",
                        "kind": "web",
                        "location": "https://example.invalid",
                        "trust_tier": "untrusted_candidate",
                    },
                    {
                        "id": "bad",
                        "review_status": "rejected",
                        "kind": "model_generated",
                        "location": "model",
                        "trust_tier": "untrusted_candidate",
                    },
                ]
            }
        ),
        encoding="utf-8",
    )

    registry = SourceRegistry.from_file(path)

    assert registry.is_approved("formal")
    assert registry.status("candidate") == "proposed"
    assert registry.status("bad") == "rejected"
    assert registry.status("missing") == "unregistered"
    assert registry.get("formal").trust_tier == "official"
    assert registry.get("formal").allowed_tasks == ("lean_manifest_backend",)


def test_source_registry_fails_closed_on_invalid_status(tmp_path):
    path = tmp_path / "sources.json"
    path.write_text(
        json.dumps({"sources": [{"id": "x", "status": "unknown"}]}),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="invalid status"):
        SourceRegistry.from_file(path)


def test_source_registry_reads_example_yaml():
    registry = SourceRegistry.from_file("config/source_registry.example.yml")

    assert registry.is_approved("formal_theorem_manifest")
    assert registry.status("open_web_candidate") == "proposed"
    assert registry.status("model_only_claims") == "rejected"
    assert registry.get("formal_theorem_manifest").trust_tier == "official"
    assert "verified_finding" in registry.get("open_web_candidate").forbidden_tasks
