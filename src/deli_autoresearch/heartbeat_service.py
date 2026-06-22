"""Heartbeat and timeout checks."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from .constants import DEFAULT_ORCHESTRATOR_INTERVAL_SECONDS, DEFAULT_TIMEOUT_MULTIPLIER, STATUS_PAUSED_FOR_HUMAN
from .models import utc_now_iso
from .registry_manager import RegistryManager
from .state_store import StateStore


def parse_iso(timestamp: str | None) -> datetime | None:
    if not timestamp:
        return None
    return datetime.fromisoformat(timestamp)


class HeartbeatService:
    def __init__(self, store: StateStore, registry: RegistryManager):
        self.store = store
        self.registry = registry

    def run_once(
        self,
        *,
        interval_seconds: int = DEFAULT_ORCHESTRATOR_INTERVAL_SECONDS,
        timeout_multiplier: int = DEFAULT_TIMEOUT_MULTIPLIER,
    ) -> list[dict]:
        now = datetime.now(timezone.utc)
        timeout = timedelta(seconds=interval_seconds * timeout_multiplier)
        results: list[dict] = []
        for task in self.registry.list_enabled_tasks():
            progress = self.store.read_progress(task.task_id)
            last_seen = parse_iso(progress.last_seen) or now
            timed_out = now - last_seen > timeout
            stalled = progress.status == STATUS_PAUSED_FOR_HUMAN
            result = {
                "task_id": task.task_id,
                "timed_out": timed_out,
                "status": progress.status,
                "stalled": stalled,
                "last_seen": progress.last_seen,
            }
            self.store.log_event(
                self.store.heartbeat_log_path(task.task_id),
                "heartbeat",
                "warn" if timed_out else "info",
                "heartbeat_check",
                result,
            )
            progress.last_seen = utc_now_iso()
            self.store.write_progress(progress)
            results.append(result)
        return results
