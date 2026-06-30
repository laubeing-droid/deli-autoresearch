"""Population frontier for bounded research directions and trial lineage."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
from pathlib import Path
from typing import Any

from .models import utc_now_iso


ACTIVE = "active"
PROMOTED = "promoted"
DISCARDED = "discarded"
VALID_STATUSES = {ACTIVE, PROMOTED, DISCARDED}


@dataclass(frozen=True)
class FrontierNode:
    """One bounded research direction with immutable lineage metadata."""

    node_id: str
    objective: str
    parent_id: str = ""
    mutation_type: str = "seed"
    metrics: dict[str, float] = field(default_factory=dict)
    status: str = ACTIVE
    reason: str = ""
    verifier: str = ""
    source_approval: str = ""
    created_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["created_at"] = self.created_at or utc_now_iso()
        return payload


class SearchFrontier:
    """Append-only frontier that prevents single-path hill climbing."""

    def __init__(self, ledger_path: str | Path) -> None:
        self.ledger_path = Path(ledger_path)

    def add(
        self,
        *,
        node_id: str,
        objective: str,
        parent_id: str = "",
        mutation_type: str = "seed",
        metrics: dict[str, float] | None = None,
    ) -> FrontierNode:
        """Add a candidate direction without judging it as a finding."""

        if not node_id.strip():
            raise ValueError("frontier node_id is required")
        if not objective.strip():
            raise ValueError("frontier objective is required")
        node = FrontierNode(
            node_id=node_id,
            objective=objective,
            parent_id=parent_id,
            mutation_type=mutation_type,
            metrics=dict(metrics or {}),
            status=ACTIVE,
        )
        self._append({"event_type": "add", **node.to_dict()})
        return node

    def promote(
        self,
        node_id: str,
        *,
        reason: str,
        verifier: str = "",
        source_approval: str = "",
    ) -> FrontierNode:
        """Mark a direction as promoted after objective verification."""

        if not verifier.strip() and not source_approval.strip():
            raise ValueError("frontier promotion requires verifier or source approval")
        return self._set_status(
            node_id,
            PROMOTED,
            reason,
            verifier=verifier,
            source_approval=source_approval,
        )

    def discard(self, node_id: str, *, reason: str) -> FrontierNode:
        """Mark a direction as discarded while keeping the negative result."""

        return self._set_status(node_id, DISCARDED, reason)

    def active(self) -> list[FrontierNode]:
        """Return active directions ordered by score descending."""

        return self.ranked(status=ACTIVE)

    def ranked(self, *, metric: str = "score", status: str | None = None) -> list[FrontierNode]:
        """Rank frontier nodes by one metric without mutating the ledger."""

        nodes = list(self._state().values())
        if status is not None:
            if status not in VALID_STATUSES:
                raise ValueError(f"invalid frontier status: {status}")
            nodes = [node for node in nodes if node.status == status]
        return sorted(nodes, key=lambda node: (node.metrics.get(metric, 0.0), node.node_id), reverse=True)

    def lineage(self, node_id: str) -> list[FrontierNode]:
        """Return the parent chain from root to the requested node."""

        state = self._state()
        if node_id not in state:
            raise KeyError(node_id)
        chain: list[FrontierNode] = []
        current = state[node_id]
        while True:
            chain.append(current)
            if not current.parent_id:
                break
            if current.parent_id not in state:
                raise KeyError(f"missing parent frontier node: {current.parent_id}")
            current = state[current.parent_id]
        return list(reversed(chain))

    def _set_status(
        self,
        node_id: str,
        status: str,
        reason: str,
        *,
        verifier: str = "",
        source_approval: str = "",
    ) -> FrontierNode:
        if status not in VALID_STATUSES:
            raise ValueError(f"invalid frontier status: {status}")
        if not reason.strip():
            raise ValueError("frontier status change requires a reason")
        state = self._state()
        if node_id not in state:
            raise KeyError(node_id)
        old = state[node_id]
        node = FrontierNode(
            node_id=old.node_id,
            objective=old.objective,
            parent_id=old.parent_id,
            mutation_type=old.mutation_type,
            metrics=old.metrics,
            status=status,
            reason=reason,
            verifier=verifier,
            source_approval=source_approval,
            created_at=old.created_at,
        )
        self._append({"event_type": status, **node.to_dict()})
        return node

    def _state(self) -> dict[str, FrontierNode]:
        state: dict[str, FrontierNode] = {}
        if not self.ledger_path.exists():
            return state
        for raw_line in self.ledger_path.read_text(encoding="utf-8").splitlines():
            if not raw_line.strip():
                continue
            payload = json.loads(raw_line)
            status = str(payload.get("status", ACTIVE))
            if status not in VALID_STATUSES:
                raise ValueError(f"invalid frontier status in ledger: {status}")
            node = FrontierNode(
                node_id=str(payload["node_id"]),
                objective=str(payload["objective"]),
                parent_id=str(payload.get("parent_id", "")),
                mutation_type=str(payload.get("mutation_type", "seed")),
                metrics={str(k): float(v) for k, v in dict(payload.get("metrics", {})).items()},
                status=status,
                reason=str(payload.get("reason", "")),
                verifier=str(payload.get("verifier", "")),
                source_approval=str(payload.get("source_approval", "")),
                created_at=str(payload.get("created_at", "")),
            )
            state[node.node_id] = node
        return state

    def _append(self, payload: dict[str, Any]) -> None:
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        record = dict(payload)
        record.setdefault("created_at", utc_now_iso())
        with self.ledger_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=True, sort_keys=True) + "\n")
