"""Trial harness that records objective evidence outcomes and pivot pressure."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from .constants import STRONG_SOURCE_KINDS
from .models import utc_now_iso


@dataclass(frozen=True)
class TrialDecision:
    """State-machine output derived from trial history, not fact judgment."""

    status: str
    repeated_failures: int
    consecutive_without_strong_evidence: int
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "repeated_failures": self.repeated_failures,
            "consecutive_without_strong_evidence": self.consecutive_without_strong_evidence,
            "reason": self.reason,
        }


class TrialHarness:
    """Append trial results and trigger pivot/review on repeated weak outcomes."""

    def __init__(self, ledger_path: str | Path, *, strong_source_kinds: set[str] | None = None) -> None:
        self.ledger_path = Path(ledger_path)
        self.strong_source_kinds = strong_source_kinds or set(STRONG_SOURCE_KINDS)

    def record_trial(
        self,
        *,
        trial_id: str,
        claim_id: str,
        outcome: str,
        evidence: list[dict[str, Any]] | None = None,
        parent_id: str = "",
        mutation_type: str = "",
        objective: str = "",
        metrics: dict[str, float] | None = None,
        promotion_reason: str = "",
        discard_reason: str = "",
    ) -> TrialDecision:
        evidence = evidence or []
        has_strong_evidence = self._has_strong_evidence(evidence)
        record = {
            "ts": utc_now_iso(),
            "trial_id": trial_id,
            "claim_id": claim_id,
            "outcome": outcome,
            "evidence": evidence,
            "has_strong_evidence": has_strong_evidence,
            "parent_id": parent_id,
            "mutation_type": mutation_type,
            "objective": objective,
            "metrics": dict(metrics or {}),
            "promotion_reason": promotion_reason,
            "discard_reason": discard_reason,
        }
        self._append(record)
        history = self._read_history()
        repeated_failures = sum(
            1
            for item in history
            if item.get("claim_id") == claim_id and item.get("outcome") == "failure"
        )
        consecutive_without_strong = self._consecutive_without_strong(history)

        if repeated_failures >= 3:
            return TrialDecision(
                status="needs_human_review",
                repeated_failures=repeated_failures,
                consecutive_without_strong_evidence=consecutive_without_strong,
                reason="three repeated failures for the same claim",
            )
        if repeated_failures >= 2:
            return TrialDecision(
                status="pivot",
                repeated_failures=repeated_failures,
                consecutive_without_strong_evidence=consecutive_without_strong,
                reason="two repeated failures for the same claim",
            )
        if consecutive_without_strong >= 2:
            return TrialDecision(
                status="pivot",
                repeated_failures=repeated_failures,
                consecutive_without_strong_evidence=consecutive_without_strong,
                reason="two consecutive trials without strong evidence",
            )
        return TrialDecision(
            status="continue",
            repeated_failures=repeated_failures,
            consecutive_without_strong_evidence=consecutive_without_strong,
            reason="trial recorded",
        )

    def _has_strong_evidence(self, evidence: list[dict[str, Any]]) -> bool:
        return any(
            isinstance(item, dict) and item.get("source_kind") in self.strong_source_kinds
            for item in evidence
        )

    def _append(self, record: dict[str, Any]) -> None:
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        with self.ledger_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=True, sort_keys=True) + "\n")

    def _read_history(self) -> list[dict[str, Any]]:
        if not self.ledger_path.exists():
            return []
        return [
            json.loads(line)
            for line in self.ledger_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    @staticmethod
    def _consecutive_without_strong(history: list[dict[str, Any]]) -> int:
        count = 0
        for item in reversed(history):
            if item.get("has_strong_evidence"):
                break
            count += 1
        return count
