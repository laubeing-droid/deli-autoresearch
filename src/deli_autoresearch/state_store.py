"""Filesystem-backed state and log store with cross-process file locks and atomic writes."""

from __future__ import annotations

import json
import os
import tempfile
import time
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
    MONITOR_DIRNAME,
    ORCHESTRATOR_LOG_FILENAME,
    ORCHESTRATOR_LOCK_FILENAME,
    PROGRESS_FILENAME,
    REGISTRY_FILENAME,
    RUNTIME_DIRNAME,
    STATE_DIRNAME,
    TASKS_DIRNAME,
    TASK_LOCK_FILENAME,
    TASK_SPEC_FILENAME,
    VERIFICATION_LOG_FILENAME,
    WORK_LOG_FILENAME,
)
from .file_lock import ProcessFileLock, LockHeldError
from .jsonl_store import JsonlStore
from .models import ClaimRecord, Direction, Progress, Registry, utc_now_iso
from .utils import ensure_parent, json_dumps


def _atomic_write(path: Path, content: str) -> None:
    ensure_parent(path)
    fd = -1
    try:
        fd, tmp_name = tempfile.mkstemp(
            suffix=".tmp", prefix=path.name, dir=str(path.parent)
        )
        os.write(fd, content.encode("utf-8"))
        os.fsync(fd)
        os.close(fd)
        fd = -1
        os.replace(tmp_name, str(path))
    finally:
        if fd >= 0:
            os.close(fd)
            try:
                os.unlink(tmp_name)
            except OSError:
                pass


class StateStore:
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.runtime_root = workspace_root / RUNTIME_DIRNAME
        self.tasks_root = self.runtime_root / TASKS_DIRNAME
        self.monitor_root = self.runtime_root / MONITOR_DIRNAME
        self.registry_path = self.runtime_root / REGISTRY_FILENAME
        self._jsonl_stores: dict[str, JsonlStore] = {}
        self._owner_id: str = f"store_{os.getpid()}_{int(time.time())}"

    def acquire_workspace_lock(self, owner_instance_id: str) -> ProcessFileLock:
        lock = ProcessFileLock.workspace_lock(self.workspace_root, owner_instance_id, timeout_seconds=0)
        lock.acquire()
        return lock

    def acquire_task_lock(self, task_id: str, owner_instance_id: str) -> ProcessFileLock:
        lock = ProcessFileLock.task_lock(self.monitor_root, task_id, owner_instance_id, timeout_seconds=0)
        lock.acquire()
        return lock

    def ensure_runtime(self) -> None:
        self.runtime_root.mkdir(parents=True, exist_ok=True)
        self.tasks_root.mkdir(parents=True, exist_ok=True)
        self.monitor_root.mkdir(parents=True, exist_ok=True)
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

    def monitor_lease_path(self, task_id: str) -> Path:
        self.monitor_root.mkdir(parents=True, exist_ok=True)
        return self.monitor_root / f"{task_id}_monitor.json"

    def _get_jsonl(self, path: Path, *, require_fsync: bool | None = None) -> JsonlStore:
        key = str(path)
        if key not in self._jsonl_stores:
            task_id = ""
            parts = path.parts
            if "tasks" in parts:
                idx = parts.index("tasks")
                if idx + 1 < len(parts):
                    task_id = parts[idx + 1]
            self._jsonl_stores[key] = JsonlStore(
                path, writer_instance_id=self._owner_id,
                task_id=task_id, require_fsync=require_fsync,
            )
        return self._jsonl_stores[key]

    def append_jsonl(self, path: Path, payload: dict[str, Any], *, event_id: str = "") -> str:
        store = self._get_jsonl(path)
        return store.append(payload, event_id=event_id)

    def log_event(self, path: Path, source: str, level: str, event: str, detail: dict[str, Any]) -> None:
        self.append_jsonl(path, {"ts": utc_now_iso(), "source": source, "level": level, "event": event, "detail": detail})

    def read_registry(self) -> Registry:
        self.ensure_runtime()
        if not self.registry_path.exists():
            return Registry()
        return Registry.from_dict(json.loads(self.registry_path.read_text(encoding="utf-8")))

    def write_registry(self, registry: Registry) -> None:
        ensure_parent(self.registry_path)
        _atomic_write(self.registry_path, json_dumps(registry.to_dict()))

    def read_progress(self, task_id: str) -> Progress:
        return Progress.from_dict(json.loads(self.progress_path(task_id).read_text(encoding="utf-8")))

    def write_progress(self, progress: Progress) -> None:
        progress.state_version += 1
        progress.updated_at = utc_now_iso()
        _atomic_write(self.progress_path(progress.task_id), json_dumps(progress.to_dict()))

    def write_progress_cas(self, progress: Progress, expected_version: int | None = None) -> bool:
        if expected_version is not None:
            current = self.read_progress(progress.task_id)
            if current.state_version != expected_version:
                return False
        progress.state_version += 1
        progress.updated_at = utc_now_iso()
        _atomic_write(self.progress_path(progress.task_id), json_dumps(progress.to_dict()))
        return True

    def read_directions(self, task_id: str) -> list[Direction]:
        path = self.directions_path(task_id)
        if not path.exists():
            return []
        payload = json.loads(path.read_text(encoding="utf-8"))
        return [Direction.from_dict(item) for item in payload]

    def write_directions(self, task_id: str, directions: list[Direction]) -> None:
        _atomic_write(self.directions_path(task_id), json_dumps([d.to_dict() for d in directions]))

    def read_claims(self, task_id: str) -> dict[str, ClaimRecord]:
        path = self.claims_path(task_id)
        if not path.exists():
            return {}
        payload = json.loads(path.read_text(encoding="utf-8"))
        return {cid: ClaimRecord.from_dict(item) for cid, item in payload.items()}

    def write_claims(self, task_id: str, claims: dict[str, ClaimRecord]) -> None:
        payload = {cid: record.to_dict() for cid, record in claims.items()}
        _atomic_write(self.claims_path(task_id), json_dumps(payload))

    def initialize_task(self, task_id, template_type, task_spec, directions, *, target_validated_findings=1, max_iterations=12, tail_pass_required=True):
        self.ensure_runtime()
        self.task_state_dir(task_id).mkdir(parents=True, exist_ok=True)
        self.task_logs_dir(task_id).mkdir(parents=True, exist_ok=True)
        self.task_spec_path(task_id).write_text(task_spec, encoding="utf-8")
        progress = Progress(task_id=task_id, template_type=template_type, target_validated_findings=target_validated_findings, max_iterations=max_iterations, tail_pass_required=tail_pass_required)
        if directions:
            progress.current_direction = directions[0].to_dict()
            self.write_directions(task_id, directions)
        else:
            self.write_directions(task_id, [])
        self.write_progress(progress)
        self.write_claims(task_id, {})
        for log_path in (self.hypotheses_path(task_id), self.findings_path(task_id), self.iteration_log_path(task_id), self.work_log_path(task_id), self.verification_log_path(task_id), self.orchestrator_log_path(task_id), self.heartbeat_log_path(task_id)):
            ensure_parent(log_path)
            if not log_path.exists():
                log_path.write_text("", encoding="utf-8")
        return progress

    def write_monitor_lease(self, task_id: str, data: dict[str, Any]) -> None:
        _atomic_write(self.monitor_lease_path(task_id), json_dumps(data))

    def read_monitor_lease(self, task_id: str) -> dict[str, Any] | None:
        path = self.monitor_lease_path(task_id)
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

