"""Lock-protected JSONL append with tail recovery and event_id uniqueness.

Every append_jsonl call acquires a per-file OS lock, writes a complete
single-line JSON record, flushes, and optionally fsyncs for business-critical
logs (findings, hypotheses).

Tail recovery: on first open, inspects the last line. If incomplete JSON,
quarantines the tail, truncates to the last complete record, and logs an
audit event.
"""

from __future__ import annotations

import hashlib
import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .file_lock import ProcessFileLock, _IS_WINDOWS
from .utils import ensure_parent

# Files that require fsync after every write
FSYNC_LOG_FILES = {"findings.jsonl", "hypotheses.jsonl"}

# Recovery quarantine subdirectory
QUARANTINE_DIRNAME = "quarantine"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _payload_checksum(data: dict[str, Any]) -> str:
    """SHA-256 hex of canonically-serialised payload."""
    canonical = json.dumps(data, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:12]


def _new_event_id() -> str:
    return str(uuid.uuid4())


class JsonlStore:
    """Lock-protected, crash-recoverable JSONL file store.

    Each JsonlStore instance manages ONE JSONL file. Appending acquires an
    OS lock on that file, writes a complete single-line record, then releases.

    On first access, tail recovery inspects the last line and quarantines
    any incomplete JSON.
    """

    def __init__(
        self,
        path: Path,
        *,
        writer_instance_id: str = "",
        task_id: str = "",
        require_fsync: bool | None = None,
    ) -> None:
        self.path = path
        self.writer_instance_id = writer_instance_id or f"jsonl_writer_{os.getpid()}"
        self.task_id = task_id
        self.require_fsync = (
            require_fsync
            if require_fsync is not None
            else path.name in FSYNC_LOG_FILES
        )
        self._sequence: int = 0
        self._seen_event_ids: set[str] = set()
        self._tail_recovered: bool = False

    # ---- lifecycle ----

    def open(self) -> None:
        """Ensure directory, recover tail, and load existing event_ids."""
        ensure_parent(self.path)
        if not self.path.exists():
            self.path.write_text("", encoding="utf-8")
        if not self._tail_recovered:
            self._recover_tail()
            self._load_existing_event_ids()
            self._tail_recovered = True

    def _recover_tail(self) -> None:
        """Inspect last line. If incomplete, quarantine and truncate."""
        if not self.path.exists():
            return
        content = self.path.read_bytes()
        if not content:
            return

        # Find last newline
        last_nl = content.rfind(b"\n")
        if last_nl == -1:
            # No newline at all — entire file is one partial line
            tail = content
            self._quarantine(tail, "entire_file_no_newline")
            self.path.write_text("", encoding="utf-8")
            return

        # Check if there's content after the last newline
        if last_nl < len(content) - 1:
            tail = content[last_nl + 1:]
            if tail.strip():
                # Try to parse as JSON
                try:
                    json.loads(tail.decode("utf-8"))
                    # Valid JSON but no newline — add the newline
                    self.path.write_bytes(content + b"\n")
                except (json.JSONDecodeError, UnicodeDecodeError):
                    self._quarantine(tail, "incomplete_last_line")
                    self.path.write_bytes(content[: last_nl + 1])
            else:
                # Trailing whitespace after newline — trim
                self.path.write_bytes(content[: last_nl + 1])
        # else: file ends with newline — clean

    def _quarantine(self, data: bytes, reason: str) -> None:
        """Save corrupted tail to quarantine directory."""
        q_dir = self.path.parent / QUARANTINE_DIRNAME
        q_dir.mkdir(parents=True, exist_ok=True)
        ts = _utc_now_iso().replace(":", "-")
        q_path = q_dir / f"{self.path.name}.tail.{ts}.bin"
        q_path.write_bytes(data)

        # Write audit event
        audit_path = q_dir / f"{self.path.name}.recovery.jsonl"
        audit_record = {
            "ts": _utc_now_iso(),
            "event": "jsonl_tail_recovery",
            "file": str(self.path),
            "reason": reason,
            "quarantine_path": str(q_path),
            "tail_size": len(data),
        }
        ensure_parent(audit_path)
        # Direct write — quarantine audit must not depend on JsonlStore itself
        with audit_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(audit_record, ensure_ascii=True, sort_keys=True) + "\n")

    def _load_existing_event_ids(self) -> None:
        """Load all existing event_ids for idempotency check."""
        if not self.path.exists():
            return
        self._seen_event_ids.clear()
        for line in self.path.read_text(encoding="utf-8").strip().split("\n"):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
                eid = record.get("event_id", "")
                if eid:
                    self._seen_event_ids.add(eid)
            except json.JSONDecodeError:
                pass  # skip corrupted lines (should have been recovered)
        self._sequence = len(self._seen_event_ids)

    # ---- append (core) ----

    def append(self, payload: dict[str, Any], *, event_id: str = "") -> str:
        """Append one complete JSONL record with lock, flush, optional fsync.

        Returns the event_id used (auto-generated if not provided).
        """
        self.open()

        if not event_id:
            event_id = _new_event_id()

        # Idempotency: reject duplicate event_id
        if event_id in self._seen_event_ids:
            return event_id  # already written — no-op

        self._sequence += 1

        # Enrich payload
        record: dict[str, Any] = {
            **payload,
            "event_id": event_id,
            "task_id": self.task_id,
            "writer_instance_id": self.writer_instance_id,
            "sequence_number": self._sequence,
            "payload_checksum": _payload_checksum(payload),
        }

        # Serialize — must be single line, no embedded newlines
        line = json.dumps(record, ensure_ascii=True, sort_keys=True) + "\n"
        if "\n" in line[:-1]:
            raise ValueError("JSONL record contains embedded newline — rejected")

        line_bytes = line.encode("utf-8")

        # Acquire OS lock on the JSONL file
        lock_dir = self.path.parent / "locks"
        lock_dir.mkdir(parents=True, exist_ok=True)
        lock = ProcessFileLock(
            lock_path=self.path.with_suffix(".lock"),
            meta_path=self.path.with_suffix(".lock.meta"),
            scope="jsonl",
            target=str(self.path),
            owner_instance_id=self.writer_instance_id,
            timeout_seconds=5,
        )

        with lock:
            fd = -1
            try:
                fd = os.open(str(self.path), os.O_WRONLY | os.O_APPEND)
                os.write(fd, line_bytes)
                os.fsync(fd) if self.require_fsync else None
                # flush is implicit in os.write on Windows; explicit fsync ensures durability
            finally:
                if fd >= 0:
                    os.close(fd)

        self._seen_event_ids.add(event_id)
        return event_id

    def append_many(
        self, records: list[dict[str, Any]], *, base_event_id: str = ""
    ) -> list[str]:
        """Append multiple records under one lock acquisition.

        Returns list of event_ids.
        """
        ids: list[str] = []
        for i, record in enumerate(records):
            eid = self.append(record, event_id=f"{base_event_id}_{i}" if base_event_id else "")
            ids.append(eid)
        return ids

    # ---- read ----

    def read_all(self) -> list[dict[str, Any]]:
        """Read all valid lines from the JSONL file."""
        self.open()
        if not self.path.exists():
            return []
        results: list[dict[str, Any]] = []
        for line in self.path.read_text(encoding="utf-8").strip().split("\n"):
            line = line.strip()
            if not line:
                continue
            try:
                results.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return results

    @property
    def event_count(self) -> int:
        return len(self._seen_event_ids)


# ---------------------------------------------------------------------------
# Richer append helpers matching StateStore's old API
# ---------------------------------------------------------------------------

def atomic_jsonl_append(
    path: Path,
    payload: dict[str, Any],
    *,
    writer_instance_id: str = "",
    task_id: str = "",
    event_id: str = "",
    require_fsync: bool | None = None,
) -> str:
    """Convenience function: one-shot append to a JSONL file."""
    store = JsonlStore(
        path,
        writer_instance_id=writer_instance_id,
        task_id=task_id,
        require_fsync=require_fsync,
    )
    return store.append(payload, event_id=event_id)


def recover_jsonl_tail(path: Path) -> None:
    """Run tail recovery on a JSONL file without appending."""
    store = JsonlStore(path)
    store.open()
