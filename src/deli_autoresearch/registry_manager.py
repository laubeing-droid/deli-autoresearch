"""Registry operations."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from .models import Registry, RegistryTask, utc_now_iso
from .state_store import StateStore


class RegistryManager:
    def __init__(self, store: StateStore):
        self.store = store

    def register_task(self, task_id: str, task_path: Path, template_type: str, priority: int = 100) -> RegistryTask:
        registry = self.store.read_registry()
        for existing in registry.tasks:
            if existing.task_id == task_id:
                return existing
        task = RegistryTask(
            task_id=task_id,
            task_path=str(task_path),
            enabled=True,
            priority=priority,
            template_type=template_type,
            last_seen=utc_now_iso(),
        )
        registry.tasks.append(task)
        registry.tasks.sort(key=lambda item: item.priority)
        self.store.write_registry(registry)
        return task

    def list_enabled_tasks(self) -> list[RegistryTask]:
        registry = self.store.read_registry()
        return [task for task in registry.tasks if task.enabled]

    def update_task(self, updated: RegistryTask) -> None:
        registry = self.store.read_registry()
        registry.tasks = [updated if task.task_id == updated.task_id else task for task in registry.tasks]
        self.store.write_registry(registry)

    def touch_orchestrator_run(self, task: RegistryTask) -> RegistryTask:
        updated = replace(task, last_orchestrator_run_at=utc_now_iso(), last_seen=utc_now_iso())
        self.update_task(updated)
        return updated
