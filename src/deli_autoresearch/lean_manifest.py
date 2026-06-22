 """Lean manifest reader — machine-readable theorem proof status.

 Reads the legal-math-modeling Lean manifest and provides
 fail-closed filtering: theorems with `contains_sorry=true` or
 `contains_axiom=true` are never treated as strong evidence.
 """

 from __future__ import annotations

 import json
 from pathlib import Path
 from typing import Any


 class LeanManifest:
     """Machine-readable snapshot of Lean theorem proof status."""

     def __init__(self, manifest_path: str | Path) -> None:
         self.path = Path(manifest_path)
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
         return self.data.get("total_theorems", 0)

     def complete_theorems(self) -> list[dict[str, Any]]:
         """Theorems with complete proofs: no sorry, no axiom, no admit, not evasion."""
         self._ensure_loaded()
         result = []
         for t in self.data.get("theorems", []):
             if (
                 not t.get("contains_sorry", True)
                 and not t.get("contains_axiom", True)
                 and not t.get("contains_admit", True)
                 and t.get("proof_status") not in ("EVASION", "INCOMPLETE", "UNKNOWN")
             ):
                 result.append(t)
         return result

     def incomplete_theorems(self) -> list[dict[str, Any]]:
         """Theorems with sorry, axiom, admit, evasion, or unknown status."""
         self._ensure_loaded()
         result = []
         for t in self.data.get("theorems", []):
             if (
                 t.get("contains_sorry", False)
                 or t.get("contains_axiom", False)
                 or t.get("contains_admit", False)
                 or t.get("proof_status") in ("EVASION", "INCOMPLETE", "UNKNOWN")
             ):
                 result.append(t)
         return result

     def is_strong_evidence(self, theorem_name: str) -> bool:
         """A theorem counts as strong evidence only if it has a complete proof."""
         for t in self.complete_theorems():
             if t["theorem_name"] == theorem_name:
                 return True
         return False

     def can_provide_strong_evidence(self) -> bool:
         """At least one theorem has a complete proof."""
         return len(self.complete_theorems()) > 0


 # Path to the canonical manifest in legal-math-modeling
 DEFAULT_LEAN_MANIFEST_PATH = (
     r"D:\Claude\数学证明\legal-math-modeling\docs\remediation\lean_manifest.json"
 )
