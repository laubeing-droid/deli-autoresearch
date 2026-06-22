"""Filesystem-backed state and log store."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .constants import (
    CLAIMS_FILENAME,
    DIRECTIONS_FILENAME,
    FINDINGS_FILENAME,
    HEARTBEAT_LOG_FILENAME,
    HYPOTHESES_FILENAME,
    ITERATION_LOG_FILENAME,
    LOGS_DIRNAME,
    ORCHESTRATOR_LOG_FILENAME,
    PROGRESS_FILENAME,
    REGISTRY_FILENAME,
    RUNTIME_DIRNAME,
    STATE_DIRNAME,
    TASKS_DIRNAME,
    TASK_SPEC_FILENAME,
    VERIFICATION_LOG_FILENAME,
    WORK_LOG_FILENAME,
)
from .models import ClaimRecord, Direction, Progress, Registry, utc_now_iso
from .utils import ensure_parent, json_dumps


class StateStore:
    """Single-writer access to runtime state files."""

    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.runtime_root = workspace_root / RUNTIME_DIRNAME
        self.tasks_root = self.runtime_root / TASKS_DIRNAME
        self.registry_path = self.runtime_root / REGISTRY_FILENAME

    def ensure_runtime(self) -> None:
        self.runtime_root.mkdir(parents=True, exist_ok=True)
        self.tasks_root.mkdir(parents=True, exist_ok=True)
        if not self.registry_path.exists():
            self.write_registry(Registry())

    def task_root(self, task_id: str) -> Path:
        return self.tasks_root / task_id

    def task_state_dir(self, task_id: str) -> Path:
        return self.task_root(task_id) / STATE_DIRNAME

    def task_logs_dir(self, task_id: str) -> Path:
        return self.task_root(task_id) / LOGS_DIRNAME

    def progress_path(self, task_id: str) -> Path:
        return self.task_state_dir(task_id) / PROGRESS_FILENAME

    def directions_path(self, task_id: str) -> Path:
        return self.task_state_dir(task_id) / DIRECTIONS_FILENAME

    def claims_path(self, task_id: str) -> Path:
        return self.task_state_dir(task_id) / CLAIMS_FILENAME

    def task_spec_path(self, task_id: str) -> Path:
        return self.task_state_dir(task_id) / TASK_SPEC_FILENAME

    def hypotheses_path(self, task_id: str) -> Path:
        return self.task_logs_dir(task_id) / HYPOTHESES_FILENAME

    def findings_path(self, task_id: str) -> Path:
        return self.task_logs_dir(task_id) / FINDINGS_FILENAME

    def iteration_log_path(self, task_id: str) -> Path:
        return self.task_logs_dir(task_id) / ITERATION_LOG_FILENAME

    def work_log_path(self, task_id: str) -> Path:
        return self.task_logs_dir(task_id) / WORK_LOG_FILENAME

    def verification_log_path(self, task_id: str) -> Path:
        return self.task_logs_dir(task_id) / VERIFICATION_LOG_FILENAME

    def orchestrator_log_path(self, task_id: str) -> Path:
        return self.task_logs_dir(task_id) / ORCHESTRATOR_LOG_FILENAME

    def heartbeat_log_path(self, task_id: str) -> Path:
        return self.task_logs_dir(task_id) / HEARTBEAT_LOG_FILENAME

    def initialize_task(
        self,
        task_id: str,
        template_type: str,
        task_spec: str,
        directions: list[Direction],
        *,
        target_validated_findings: int = 1,
        max_iterations: int = 12,
        tail_pass_required: bool = True,
    ) -> Progress:
        self.ensure_runtime()
        self.task_state_dir(task_id).mkdir(parents=True, exist_ok=True)
        self.task_logs_dir(task_id).mkdir(parents=True, exist_ok=True)
        self.task_spec_path(task_id).write_text(task_spec, encoding="utf-8")
        progress = Progress(
            task_id=task_id,
            template_type=template_type,
            target_validated_findings=target_validated_findings,
            max_iterations=max_iterations,
            tail_pass_required=tail_pass_required,
        )
        if directions:
            progress.current_direction = directions[0].to_dict()
            self.write_directions(task_id, directions)
        else:
            self.write_directions(task_id, [])
        self.write_progress(progress)
        self.write_claims(task_id, {})
        for log_path in (
            self.hypotheses_path(task_id),
            self.findings_path(task_id),
            self.iteration_log_path(task_id),
            self.work_log_path(task_id),
            self.verification_log_path(task_id),
            self.orchestrator_log_path(task_id),
            self.heartbeat_log_path(task_id),
        ):
            ensure_parent(log_path)
            if not log_path.exists():
                log_path.write_text("", encoding="utf-8")
        return progress

    def read_registry(self) -> Registry:
        self.ensure_runtime()
        if not self.registry_path.exists():
            return Registry()
        return Registry.from_dict(json.loads(self.registry_path.read_text(encoding="utf-8")))

    def write_registry(self, registry: Registry) -> None:
        ensure_parent(self.registry_path)
        self.registry_path.write_text(json_dumps(registry.to_dict()), encoding="utf-8")

    def read_progress(self, task_id: str) -> Progress:
        return Progress.from_dict(json.loads(self.progress_path(task_id).read_text(encoding="utf-8")))

    def write_progress(self, progress: Progress) -> None:
        self.progress_path(progress.task_id).write_text(json_dumps(progress.to_dict()), encoding="utf-8")

    def read_directions(self, task_id: str) -> list[Direction]:
        path = self.directions_path(task_id)
        if not path.exists():
            return []
        payload = json.loads(path.read_text(encoding="utf-8"))
        return [Direction.from_dict(item) for item in payload]

    def write_directions(self, task_id: str, directions: list[Direction]) -> None:
        self.directions_path(task_id).write_text(
            json_dumps([direction.to_dict() for direction in directions]),
            encoding="utf-8",
        )

    def read_claims(self, task_id: str) -> dict[str, ClaimRecord]:
        path = self.claims_path(task_id)
        if not path.exists():
            return {}
        payload = json.loads(path.read_text(encoding="utf-8"))
        return {claim_id: ClaimRecord.from_dict(item) for claim_id, item in payload.items()}

    def write_claims(self, task_id: str, claims: dict[str, ClaimRecord]) -> None:
        payload = {claim_id: record.to_dict() for claim_id, record in claims.items()}
        self.claims_path(task_id).write_text(json_dumps(payload), encoding="utf-8")

    def append_jsonl(self, path: Path, payload: dict[str, Any]) -> None:
        ensure_parent(path)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=True, sort_keys=True) + "\n")

    def log_event(self, path: Path, source: str, level: str, event: str, detail: dict[str, Any]) -> None:
        self.append_jsonl(
            path,
            {
                "ts": utc_now_iso(),
                "source": source,
                "level": level,
                "event": event,
                "detail": detail,
            },
        )
