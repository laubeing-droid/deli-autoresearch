"""Dataclasses used by the framework."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import hashlib
import json
import uuid
from typing import Any

from .constants import STATUS_ACTIVE, VERDICT_VALIDATED


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def hash_digest(data: dict[str, Any]) -> str:
    """Deterministic SHA-256 hex digest for a JSON-serialisable dict."""
    canonical = json.dumps(data, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


def new_uuid() -> str:
    return str(uuid.uuid4())


# ---------------------------------------------------------------------------
# Unified verification status (fail-closed)
# ---------------------------------------------------------------------------

VERIFICATION_STATUS_PROVED = "PROVED"
VERIFICATION_STATUS_REFUTED = "REFUTED"
VERIFICATION_STATUS_NEEDS_MORE_EVIDENCE = "NEEDS_MORE_EVIDENCE"
VERIFICATION_STATUS_UNKNOWN = "UNKNOWN"
VERIFICATION_STATUS_TIMEOUT = "TIMEOUT"
VERIFICATION_STATUS_NOT_RUN = "NOT_RUN"
VERIFICATION_STATUS_BACKEND_UNAVAILABLE = "BACKEND_UNAVAILABLE"
VERIFICATION_STATUS_ERROR = "ERROR"

TERMINAL_VERIFICATION_STATUSES = {
    VERIFICATION_STATUS_PROVED,
    VERIFICATION_STATUS_REFUTED,
}

WONT_VALIDATE_STATUSES = {
    VERIFICATION_STATUS_UNKNOWN,
    VERIFICATION_STATUS_TIMEOUT,
    VERIFICATION_STATUS_NOT_RUN,
    VERIFICATION_STATUS_BACKEND_UNAVAILABLE,
    VERIFICATION_STATUS_ERROR,
}


# ---------------------------------------------------------------------------
# Claim-bound verification structures
# ---------------------------------------------------------------------------

@dataclass
class FormalPayload:
    verification_type: str
    payload: dict[str, Any]
    digest: str = ""

    def __post_init__(self) -> None:
        if not self.digest:
            self.digest = hash_digest(self.payload)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ArtifactRef:
    artifact_kind: str
    locator: str
    digest: str
    timestamp: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


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
    state_version: int = 0
    updated_by: str = ""
    updated_at: str = ""
    claim_stall_pressure: float = 0.0
    direction_stall_pressure: float = 0.0
    task_stall_pressure: float = 0.0
    last_seen: str = field(default_factory=utc_now_iso)
    last_progress_at: str = field(default_factory=utc_now_iso)
    last_work_agent_id: str | None = None
    last_verification_agent_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "Progress":
        known = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in payload.items() if k in known}
        return cls(**filtered)


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
    formal_payload: dict[str, Any] = field(default_factory=dict)
    claim_digest: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "WorkClaimCandidate":
        known = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in payload.items() if k in known}
        return cls(**filtered)


@dataclass
class WorkResult:
    summary: str
    claims: list[WorkClaimCandidate]
    request_id: str = ""
    request_digest: str = ""

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "WorkResult":
        claims = [WorkClaimCandidate.from_dict(c) for c in payload.get("claims", [])]
        return cls(
            summary=payload.get("summary", ""),
            claims=claims,
            request_id=payload.get("request_id", ""),
            request_digest=payload.get("request_digest", ""),
        )


@dataclass
class VerificationResult:
    claim_id: str
    verdict: str
    evidence_strength: str
    summary: str
    verification_status: str = VERIFICATION_STATUS_UNKNOWN
    claim_digest: str = ""
    payload_digest: str = ""
    request_id: str = ""
    request_digest: str = ""
    backend_name: str = ""
    backend_version: str = ""
    artifact_refs: list[dict[str, Any]] = field(default_factory=list)
    supporting_evidence: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.verification_status == VERIFICATION_STATUS_UNKNOWN and self.verdict:
            self.verification_status = _old_verdict_to_status(self.verdict)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "VerificationResult":
        known = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in payload.items() if k in known}
        return cls(**filtered)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @property
    def is_terminal(self) -> bool:
        return self.verification_status in TERMINAL_VERIFICATION_STATUSES

    @property
    def wont_validate(self) -> bool:
        return self.verification_status in WONT_VALIDATE_STATUSES


# ---------------------------------------------------------------------------
# Bridge protocol structures
# ---------------------------------------------------------------------------

@dataclass
class BridgeRequest:
    request_id: str
    task_id: str
    iteration: int
    kind: str
    claim_id: str
    prompt: dict[str, Any]
    instruction: str
    protocol_version: str = "1.0"
    request_digest: str = ""
    agent_id: str = ""

    def __post_init__(self) -> None:
        if not self.request_digest:
            self.request_digest = hash_digest({
                "task_id": self.task_id,
                "iteration": str(self.iteration),
                "kind": self.kind,
                "claim_id": self.claim_id,
                "instruction": self.instruction,
            })
        if not self.agent_id:
            self.agent_id = self.request_id

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class BridgeResponse:
    request_id: str
    task_id: str
    iteration: int
    claim_id: str
    payload: dict[str, Any]
    protocol_version: str = "1.0"
    request_digest: str = ""

    def validate(self, request: BridgeRequest) -> list[str]:
        errors: list[str] = []
        if self.request_id != request.request_id:
            errors.append(f"request_id mismatch: {self.request_id} vs {request.request_id}")
        if self.task_id != request.task_id:
            errors.append(f"task_id mismatch: {self.task_id} vs {request.task_id}")
        if self.iteration != request.iteration:
            errors.append(f"iteration mismatch: {self.iteration} vs {request.iteration}")
        if self.claim_id != request.claim_id:
            errors.append(f"claim_id mismatch: {self.claim_id} vs {request.claim_id}")
        if self.request_digest != request.request_digest:
            errors.append(f"request_digest mismatch")
        if self.protocol_version != request.protocol_version:
            errors.append(f"protocol_version mismatch")
        return errors

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "BridgeResponse":
        return cls(**{k: v for k, v in payload.items() if k in cls.__dataclass_fields__})


def _old_verdict_to_status(verdict: str) -> str:
    _map = {
        VERDICT_VALIDATED: VERIFICATION_STATUS_PROVED,
        "rejected": VERIFICATION_STATUS_REFUTED,
        "needs_more_evidence": VERIFICATION_STATUS_NEEDS_MORE_EVIDENCE,
    }
    return _map.get(verdict, VERIFICATION_STATUS_UNKNOWN)
