"""Cross-process file locking via atomic O_EXCL file creation (Windows + POSIX).

Uses os.O_CREAT | os.O_EXCL to atomically create a lock file.
On Windows, file creation is truly atomic and works across processes.
On POSIX, O_EXCL guarantees exclusive creation.
The lock file's existence IS the lock.

Stale lock detection: if the lock holder's PID is no longer running,
the lock is broken and re-acquired.

Requirement: ProcessFileLock does NOT depend on msvcrt.locking.
"""

from __future__ import annotations

import json
import os
import platform
import socket
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .models import utc_now_iso
from .utils import ensure_parent, json_dumps

_IS_WINDOWS = platform.system() == "Windows"


# ---------------------------------------------------------------------------
# Lock metadata (diagnostic only)
# ---------------------------------------------------------------------------

@dataclass
class LockMeta:
    lock_scope: str
    target: str
    owner_instance_id: str
    pid: int = field(default_factory=os.getpid)
    hostname: str = field(default_factory=socket.gethostname)
    acquired_at: str = field(default_factory=utc_now_iso)
    command: str = field(default_factory=lambda: " ".join(sys.argv))
    protocol_version: str = "1.0"

    def to_dict(self) -> dict[str, Any]:
        from dataclasses import asdict
        return asdict(self)


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class LockHeldError(RuntimeError):
    def __init__(self, scope: str, target: str, existing_meta: dict | None = None):
        self.scope = scope
        self.target = target
        self.existing_meta = existing_meta or {}
        super().__init__(
            f"LOCK_HELD: {scope} lock for {target} is held by another process "
            f"(pid={self.existing_meta.get('pid', '?')}, "
            f"owner={self.existing_meta.get('owner_instance_id', '?')})"
        )


class ReentrantLockError(RuntimeError):
    pass


# ---------------------------------------------------------------------------
# ProcessFileLock — O_EXCL-based
# ---------------------------------------------------------------------------

class ProcessFileLock:
    """Cross-process file lock via atomic O_EXCL file creation.

    Usage:
        lock = ProcessFileLock.workspace_lock(workspace_root, owner_id)
        with lock:
            ...

        task_lock = ProcessFileLock.task_lock(task_lock_dir, task_id, owner_id)
        with task_lock:
            ...
    """

    def __init__(
        self,
        lock_path: Path,
        meta_path: Path,
        scope: str,
        target: str,
        owner_instance_id: str,
        *,
        timeout_seconds: float = 0,
    ) -> None:
        self.lock_path = lock_path
        self.meta_path = meta_path
        self.scope = scope
        self.target = target
        self.owner_instance_id = owner_instance_id
        self.timeout_seconds = timeout_seconds
        self._acquired: bool = False
        self._meta: LockMeta | None = None
        self._reentrancy_registry: dict[str, set[str]] = _reentrancy_guard

    # ---- factory methods ----

    @classmethod
    def workspace_lock(
        cls, workspace_root: Path, owner_instance_id: str, *, timeout_seconds: float = 0
    ) -> "ProcessFileLock":
        lock_dir = workspace_root / "runtime" / "monitor"
        lock_dir.mkdir(parents=True, exist_ok=True)
        return cls(
            lock_path=lock_dir / "orchestrator.lock",
            meta_path=lock_dir / "orchestrator.lock.meta",
            scope="workspace",
            target=str(workspace_root.resolve()),
            owner_instance_id=owner_instance_id,
            timeout_seconds=timeout_seconds,
        )

    @classmethod
    def task_lock(
        cls, task_lock_dir: Path, task_id: str, owner_instance_id: str,
        *, timeout_seconds: float = 0,
    ) -> "ProcessFileLock":
        task_lock_dir.mkdir(parents=True, exist_ok=True)
        return cls(
            lock_path=task_lock_dir / f"{task_id}.task.lock",
            meta_path=task_lock_dir / f"{task_id}.task.lock.meta",
            scope="task",
            target=task_id,
            owner_instance_id=owner_instance_id,
            timeout_seconds=timeout_seconds,
        )

    # ---- context manager ----

    def __enter__(self) -> "ProcessFileLock":
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.release()
        return False

    # ---- acquire / release ----

    def acquire(self) -> None:
        if self._acquired:
            return

        # Reentrancy check
        if self.target in self._reentrancy_registry.get(self.owner_instance_id, set()):
            raise ReentrantLockError(
                f"Same owner {self.owner_instance_id} already holds lock for {self.target}"
            )

        ensure_parent(self.lock_path)
        ensure_parent(self.meta_path)

        deadline = time.time() + self.timeout_seconds
        while True:
            try:
                fd = os.open(str(self.lock_path), os.O_CREAT | os.O_EXCL | os.O_RDWR)
                os.close(fd)
                break  # acquired — lock file created
            except FileExistsError:
                # Lock file exists — check if it's stale
                if self._is_stale():
                    # Break the stale lock
                    try:
                        os.unlink(self.lock_path)
                    except OSError:
                        pass
                    continue  # retry
                if time.time() >= deadline:
                    existing_meta = self._read_existing_meta()
                    raise LockHeldError(self.scope, self.target, existing_meta)
                time.sleep(0.1)

        # Write diagnostic metadata
        self._meta = LockMeta(
            lock_scope=self.scope,
            target=self.target,
            owner_instance_id=self.owner_instance_id,
        )
        self._write_meta()

        # Track reentrancy
        self._reentrancy_registry.setdefault(self.owner_instance_id, set()).add(self.target)
        self._acquired = True

    def release(self) -> None:
        if not self._acquired:
            return
        try:
            if self.lock_path.exists():
                os.unlink(self.lock_path)
        except OSError:
            pass
        try:
            if self.meta_path.exists():
                os.unlink(self.meta_path)
        except OSError:
            pass
        guard = self._reentrancy_registry.get(self.owner_instance_id)
        if guard:
            guard.discard(self.target)
        self._acquired = False

    def is_held(self) -> bool:
        return self._acquired

    # ---- stale lock detection ----

    def _is_stale(self) -> bool:
        """Check if existing lock holder PID is still running."""
        existing_meta = self._read_existing_meta()
        if not existing_meta:
            # No meta file — stale lock file (never finished writing meta)
            return True
        pid = existing_meta.get("pid", 0)
        if pid == 0:
            return True
        try:
            if _IS_WINDOWS:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                handle = kernel32.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
                if handle:
                    kernel32.CloseHandle(handle)
                    return False  # process still running
                return True  # process gone
            else:
                os.kill(pid, 0)
                return False
        except (OSError, Exception):
            return True

    # ---- helpers ----

    def _write_meta(self) -> None:
        if self._meta is None:
            return
        self.meta_path.write_text(json_dumps(self._meta.to_dict()), encoding="utf-8")

    def _read_existing_meta(self) -> dict[str, Any] | None:
        if not self.meta_path.exists():
            return None
        try:
            return json.loads(self.meta_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None


_reentrancy_guard: dict[str, set[str]] = {}

