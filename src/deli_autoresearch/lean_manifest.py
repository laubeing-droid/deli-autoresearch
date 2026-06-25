"""Lean manifest reader — machine-readable theorem proof status."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class LeanManifest:
    """Machine-readable snapshot of Lean theorem proof status."""

    def __init__(self, manifest_path: str | Path = "") -> None:
        self.path = Path(manifest_path or DEFAULT_LEAN_MANIFEST_PATH)
        self.data: dict[str, Any] = {}
        self._loaded = False

    def _ensure_loaded(self) -> None:
        if self._loaded:
            return
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


DEFAULT_LEAN_MANIFEST_PATH = (
    r"D:\Claude\数学证明\legal-math-modeling\docs\formal-release\theorem_manifest.json"
)
