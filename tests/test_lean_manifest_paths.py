import json

from deli_autoresearch.lean_manifest import (
    MANIFEST_RELATIVE_PATH,
    LeanManifest,
    discover_cross_repo_status,
    resolve_lean_manifest_path,
)


def _write_manifest(root):
    path = root / MANIFEST_RELATIVE_PATH
    path.parent.mkdir(parents=True)
    path.write_text(
        json.dumps(
            {
                "build_status": "PASS",
                "total": 1,
                "theorems": [{"name": "env_theorem"}],
            }
        ),
        encoding="utf-8",
    )
    return path


def test_manifest_resolver_prefers_legal_math_modeling_root_env(tmp_path, monkeypatch):
    legal_root = tmp_path / "legal-math-modeling"
    expected = _write_manifest(legal_root)
    monkeypatch.setenv("LEGAL_MATH_MODELING_ROOT", str(legal_root))

    resolution = resolve_lean_manifest_path()
    manifest = LeanManifest()

    assert resolution.source == "LEGAL_MATH_MODELING_ROOT"
    assert resolution.path == expected
    assert manifest.is_strong_evidence("env_theorem")


def test_manifest_resolver_fails_closed_for_missing_env_manifest(tmp_path, monkeypatch):
    legal_root = tmp_path / "legal-math-modeling"
    monkeypatch.setenv("LEGAL_MATH_MODELING_ROOT", str(legal_root))

    resolution = resolve_lean_manifest_path()

    assert resolution.exists is False
    assert resolution.source == "LEGAL_MATH_MODELING_ROOT"
    assert "manifest not found" in resolution.error


def test_doctor_exposes_cross_repo_and_manifest_status():
    report = discover_cross_repo_status()

    assert "deli_autoresearch_root" in report
    assert "juris_calculus_root" in report
    assert "theorem_manifest" in report
    assert ("D:" + "\\Claude") not in report["theorem_manifest"]["path"]
