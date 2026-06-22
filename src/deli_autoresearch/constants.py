"""Shared constants for the local framework."""

from __future__ import annotations

RUNTIME_DIRNAME = "runtime"
TASKS_DIRNAME = "tasks"
STATE_DIRNAME = "state"
LOGS_DIRNAME = "logs"
BRIDGE_DIRNAME = "bridge"
REQUESTS_DIRNAME = "requests"
RESPONSES_DIRNAME = "responses"

REGISTRY_FILENAME = "registry.json"
TASK_SPEC_FILENAME = "task_spec.md"
PROGRESS_FILENAME = "progress.json"
DIRECTIONS_FILENAME = "directions_tried.json"
CLAIMS_FILENAME = "claims.json"
HYPOTHESES_FILENAME = "hypotheses.jsonl"
FINDINGS_FILENAME = "findings.jsonl"
ITERATION_LOG_FILENAME = "iteration_log.jsonl"
WORK_LOG_FILENAME = "work.jsonl"
VERIFICATION_LOG_FILENAME = "verification.jsonl"
ORCHESTRATOR_LOG_FILENAME = "orchestrator.jsonl"
HEARTBEAT_LOG_FILENAME = "heartbeat.jsonl"

STATUS_ACTIVE = "active"
STATUS_PAUSED_FOR_HUMAN = "paused_for_human"
STATUS_COMPLETED = "completed"
STATUS_FAILED = "failed"

VERDICT_VALIDATED = "validated"
VERDICT_REJECTED = "rejected"
VERDICT_NEEDS_MORE_EVIDENCE = "needs_more_evidence"

STRONG_SOURCE_KINDS = {"web", "local_file", "code", "experiment"}
BASE_SOURCE_KINDS = {
    "web",
    "local_file",
    "code",
    "derived",
    "experiment",
    "model_generated",
}

BASE_DIRECTION_TYPES = {
    "opposite_hypothesis",
    "new_evidence_path",
    "reframe_decomposition",
    "cross_domain_analogy",
    "constraint_shift",
}

DEFAULT_ORCHESTRATOR_INTERVAL_SECONDS = 3600
DEFAULT_TIMEOUT_MULTIPLIER = 3
MAX_CLAIMS_PER_ITERATION = 3
MAX_EVIDENCE_PER_CLAIM = 3
SAME_DIRECTION_RETRY_LIMIT = 2
