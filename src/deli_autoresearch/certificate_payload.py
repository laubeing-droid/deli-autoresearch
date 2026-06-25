"""Unified certificate payloads for grounded extension verification."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class GroundedExtensionCertificate:
    arguments: list[str]
    attacks: list[tuple[str, str]]
    claimed_in: list[str]
    claimed_out: list[str]
    claimed_undec: list[str]
    engine_commit: str
    lean_theorem_refs: list[str] = field(default_factory=list)
    derived_bound: int = 0
    converged: bool = False
    truncated: bool = False
    iterations: int = 0

    @classmethod
    def from_engine_result(
        cls,
        claims: list[dict[str, Any]],
        attacks: list[tuple[str, str]],
        raw: dict[str, Any],
        *,
        theorem_refs: list[str] | None = None,
        engine_commit: str = "",
    ) -> "GroundedExtensionCertificate":
        return cls(
            arguments=[c["id"] for c in claims],
            attacks=[tuple(pair) for pair in attacks],
            claimed_in=sorted(raw.get("accepted", [])),
            claimed_out=sorted(raw.get("rejected", [])),
            claimed_undec=sorted(raw.get("undecided", [])),
            engine_commit=engine_commit,
            lean_theorem_refs=theorem_refs or [
                "grounded_is_least_fixed_point",
                "fixed_at_card",
                "exists_fixpoint_le_card",
            ],
            derived_bound=int(raw.get("derived_bound", 0)),
            converged=bool(raw.get("convergent", False)),
            truncated=bool(raw.get("truncated", False)),
            iterations=int(raw.get("iterations", 0)),
        )

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["attacks"] = [list(pair) for pair in self.attacks]
        return payload
