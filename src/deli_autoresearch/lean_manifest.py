"""Lean manifest reader with fail-closed cross-repo path discovery."""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
from typing import Any


MANIFEST_RELATIVE_PATH = Path("docs") / "formal-release" / "theorem_manifest.json"
LEGAL_MATH_MODELING_ENV = "LEGAL_MATH_MODELING_ROOT"


@dataclass(frozen=True)
class ManifestResolution:
    """Resolved manifest path plus probe metadata for doctor output."""

    path: Path | None
    source: str
    exists: bool
    candidates: list[str]
    error: str = ""


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _is_legacy_claude_path(path: Path) -> bool:
    """Reject old auto-probe candidates without blocking explicit env input."""

    text = str(path.resolve()).lower()
    return text.startswith(r"d:\claude".lower())


def _candidate_roots(workspace: Path | None = None) -> list[Path]:
    """Return workspace anchors used to probe adjacent legal-math-modeling roots."""

    roots: list[Path] = []
    for root in [workspace, Path.cwd(), _repo_root()]:
        if root is None:
            continue
        resolved = root.resolve()
        roots.append(resolved)
        roots.extend(resolved.parents)
    deduped: list[Path] = []
    seen: set[str] = set()
    for root in roots:
        key = str(root).lower()
        if key not in seen:
            seen.add(key)
            deduped.append(root)
    return deduped


def _probe_candidates(workspace: Path | None = None) -> list[Path]:
    """Build deterministic manifest candidates from adjacent and parent workspaces."""

    candidates: list[Path] = []
    for root in _candidate_roots(workspace):
        candidates.extend(
            [
                root / MANIFEST_RELATIVE_PATH,
                root / "legal-math-modeling" / MANIFEST_RELATIVE_PATH,
                root / "数学证明" / "legal-math-modeling" / MANIFEST_RELATIVE_PATH,
            ]
        )
    deduped: list[Path] = []
    seen: set[str] = set()
    for candidate in candidates:
        resolved = candidate.resolve()
        key = str(resolved).lower()
        if key in seen or _is_legacy_claude_path(resolved):
            continue
        seen.add(key)
        deduped.append(resolved)
    return deduped


def resolve_lean_manifest_path(
    manifest_path: str | Path | None = None,
    *,
    workspace: str | Path | None = None,
) -> ManifestResolution:
    """Resolve theorem_manifest.json using explicit path, env root, then probes.

    The resolver never falls back to the legacy D:\\Claude hard-coded path. A
    missing result is reported as fail-closed so callers do not silently verify
    against stale formal evidence.
    """

    candidates: list[Path] = []
    if manifest_path:
        path = Path(manifest_path).resolve()
        return ManifestResolution(
            path=path,
            source="explicit",
            exists=path.exists(),
            candidates=[str(path)],
            error="" if path.exists() else f"manifest not found: {path}",
        )

    env_root = os.environ.get(LEGAL_MATH_MODELING_ENV, "").strip()
    if env_root:
        path = (Path(env_root).resolve() / MANIFEST_RELATIVE_PATH)
        return ManifestResolution(
            path=path,
            source=LEGAL_MATH_MODELING_ENV,
            exists=path.exists(),
            candidates=[str(path)],
            error="" if path.exists() else f"manifest not found from {LEGAL_MATH_MODELING_ENV}: {path}",
        )

    workspace_path = Path(workspace).resolve() if workspace else None
    candidates = _probe_candidates(workspace_path)
    for candidate in candidates:
        if candidate.exists():
            return ManifestResolution(
                path=candidate,
                source="workspace_probe",
                exists=True,
                candidates=[str(p) for p in candidates],
            )

    return ManifestResolution(
        path=None,
        source="fail_closed",
        exists=False,
        candidates=[str(p) for p in candidates],
        error="theorem_manifest.json not found by env or workspace probe",
    )


def discover_cross_repo_status(workspace: str | Path | None = None) -> dict[str, Any]:
    """Expose Deli, legal-math-modeling, juris-calculus and manifest status."""

    from .constants import JURIS_CALCULUS_ROOT

    deli_root = _repo_root()
    resolution = resolve_lean_manifest_path(workspace=workspace)
    legal_root = resolution.path.parents[2] if resolution.path else None
    juris_root = Path(JURIS_CALCULUS_ROOT)
    return {
        "deli_autoresearch_root": str(deli_root),
        "legal_math_modeling_root": str(legal_root) if legal_root else "",
        "legal_math_modeling_env": os.environ.get(LEGAL_MATH_MODELING_ENV, ""),
        "juris_calculus_root": str(juris_root),
        "juris_calculus_exists": juris_root.exists(),
        "theorem_manifest": {
            "path": str(resolution.path) if resolution.path else "",
            "source": resolution.source,
            "exists": resolution.exists,
            "error": resolution.error,
            "candidates": resolution.candidates,
        },
    }


class LeanManifest:
    """Machine-readable snapshot of Lean theorem proof status."""

    def __init__(self, manifest_path: str | Path | None = None) -> None:
        self.resolution = resolve_lean_manifest_path(manifest_path)
        if self.resolution.path is None:
            raise FileNotFoundError(self.resolution.error)
        self.path = self.resolution.path
        self.data: dict[str, Any] = {}
        self._loaded = False

    def _ensure_loaded(self) -> None:
        if self._loaded:
            return
        if not self.resolution.exists:
            raise FileNotFoundError(self.resolution.error)
        self.data = json.loads(self.path.read_text(encoding="utf-8"))
        self._loaded = True

    @property
    def commit_sha(self) -> str:
        self._ensure_loaded()
        return self.data.get("commit_sha", "unknown")

    @property
    def lean_version(self) -> str:
        self._ensure_loaded()
        return self.data.get("lean_version", "unknown")

    @property
    def build_status(self) -> str:
        self._ensure_loaded()
        return self.data.get("build_status", "unknown")

    @property
    def total_theorems(self) -> int:
        self._ensure_loaded()
        if "total_theorems" in self.data:
            return self.data.get("total_theorems", 0)
        return self.data.get("total_kernel_checked_results", self.data.get("total", 0))

    def _iter_theorems(self) -> list[dict[str, Any]]:
        self._ensure_loaded()
        return self.data.get("theorems", [])

    def complete_theorems(self) -> list[dict[str, Any]]:
        result = []
        for theorem in self._iter_theorems():
            if "proof_status" in theorem:
                if (
                    not theorem.get("contains_sorry", True)
                    and not theorem.get("contains_axiom", True)
                    and not theorem.get("contains_admit", True)
                    and theorem.get("proof_status") not in ("EVASION", "INCOMPLETE", "UNKNOWN")
                ):
                    result.append(theorem)
            else:
                result.append(theorem)
        return result

    def incomplete_theorems(self) -> list[dict[str, Any]]:
        result = []
        for theorem in self._iter_theorems():
            if "proof_status" in theorem and (
                theorem.get("contains_sorry", False)
                or theorem.get("contains_axiom", False)
                or theorem.get("contains_admit", False)
                or theorem.get("proof_status") in ("EVASION", "INCOMPLETE", "UNKNOWN")
            ):
                result.append(theorem)
        return result

    def is_strong_evidence(self, theorem_name: str) -> bool:
        for theorem in self.complete_theorems():
            if theorem.get("theorem_name") == theorem_name or theorem.get("name") == theorem_name:
                return True
        return False

    def can_provide_strong_evidence(self) -> bool:
        return len(self.complete_theorems()) > 0


DEFAULT_LEAN_MANIFEST_PATH = ""
