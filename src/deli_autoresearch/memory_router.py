"""Fail-closed routing for findings, rejected claims, candidates, and failures."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from .constants import VERIFIED_EVIDENCE_SOURCE_KINDS
from .models import utc_now_iso


LEDGER_FILES = {
    "verified_finding": "findings.jsonl",
    "rejected_claim": "rejected_claims.jsonl",
    "source_candidate": "source_candidates.jsonl",
    "failure": "failure_registry.jsonl",
    "skill_improvement": "skill_changes.jsonl",
}


@dataclass(frozen=True)
class RoutingResult:
    """Destination decision for one memory event."""

    destination: str
    accepted: bool
    reason: str


class MemoryRouter:
    """Route research memory without allowing weak model output into findings."""

    def __init__(self, ledger_root: str | Path, *, strong_source_kinds: set[str] | None = None) -> None:
        self.ledger_root = Path(ledger_root)
        self.strong_source_kinds = strong_source_kinds or set(VERIFIED_EVIDENCE_SOURCE_KINDS)

    def route(self, payload: dict[str, Any]) -> RoutingResult:
        event_type = str(payload.get("event_type", "")).strip()
        if event_type == "verified_finding":
            if not self._has_strong_evidence(payload):
                failure = dict(payload)
                failure["event_type"] = "failure"
                failure["failure_reason"] = "verified_finding lacks strong evidence"
                self._append("failure", failure)
                return RoutingResult(LEDGER_FILES["failure"], False, failure["failure_reason"])
            self._append("verified_finding", payload)
            return RoutingResult(LEDGER_FILES["verified_finding"], True, "routed verified finding")

        if event_type in {"rejected_claim", "source_candidate", "failure", "skill_improvement"}:
            self._append(event_type, payload)
            return RoutingResult(LEDGER_FILES[event_type], True, f"routed {event_type}")

        failure = dict(payload)
        failure["event_type"] = "failure"
        failure["failure_reason"] = f"unknown memory event type: {event_type}"
        self._append("failure", failure)
        return RoutingResult(LEDGER_FILES["failure"], False, failure["failure_reason"])

    def _has_strong_evidence(self, payload: dict[str, Any]) -> bool:
        evidence = payload.get("evidence") or payload.get("supporting_evidence") or []
        if not isinstance(evidence, list):
            return False
        return any(
            isinstance(item, dict) and item.get("source_kind") in self.strong_source_kinds
            for item in evidence
        )

    def _append(self, event_type: str, payload: dict[str, Any]) -> None:
        self.ledger_root.mkdir(parents=True, exist_ok=True)
        record = dict(payload)
        record.setdefault("ts", utc_now_iso())
        path = self.ledger_root / LEDGER_FILES[event_type]
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=True, sort_keys=True) + "\n")
