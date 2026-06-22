"""Dataclasses used by the framework."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

from .constants import STATUS_ACTIVE


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Direction:
    strategy_type: str
    summary: str
    rationale: str
    origin_iteration: int
    template_extension: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "Direction":
        return cls(**payload)


@dataclass
class ClaimRecord:
    claim_id: str
    claim_text: str
    normalized_claim_text: str
    status: str = "open"
    created_at: str = field(default_factory=utc_now_iso)
    reopen_count: int = 0
    history: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ClaimRecord":
        return cls(**payload)


@dataclass
class Progress:
    task_id: str
    template_type: str
    status: str = STATUS_ACTIVE
    iteration: int = 0
    validated_findings_count: int = 0
    stall_pressure: float = 0.0
    consecutive_needs_more_evidence: int = 0
    current_direction: dict[str, Any] | None = None
    completion_stage: str = "main"
    tail_pass_required: bool = False
    tail_pass_completed: bool = False
    completion_reason: str | None = None
    target_validated_findings: int = 1
    max_iterations: int = 12
    last_seen: str = field(default_factory=utc_now_iso)
    last_progress_at: str = field(default_factory=utc_now_iso)
    last_work_agent_id: str | None = None
    last_verification_agent_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "Progress":
        return cls(**payload)


@dataclass
class RegistryTask:
    task_id: str
    task_path: str
    enabled: bool
    priority: int
    template_type: str
    last_seen: str | None = None
    next_check_at: str | None = None
    last_orchestrator_run_at: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "RegistryTask":
        return cls(**payload)


@dataclass
class Registry:
    tasks: list[RegistryTask] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {"tasks": [task.to_dict() for task in self.tasks]}

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "Registry":
        return cls(tasks=[RegistryTask.from_dict(item) for item in payload.get("tasks", [])])


@dataclass
class WorkClaimCandidate:
    claim_text: str
    evidence: list[dict[str, Any]]
    source_kind: str
    verifiable: bool
    support_kind: str = "new"
    reopen_of: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class WorkResult:
    summary: str
    claims: list[WorkClaimCandidate]

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "WorkResult":
        claims = [WorkClaimCandidate(**claim) for claim in payload["claims"]]
        return cls(summary=payload["summary"], claims=claims)


@dataclass
class VerificationResult:
    claim_id: str
    verdict: str
    evidence_strength: str
    summary: str
    supporting_evidence: list[dict[str, Any]] = field(default_factory=list)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "VerificationResult":
        return cls(**payload)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
