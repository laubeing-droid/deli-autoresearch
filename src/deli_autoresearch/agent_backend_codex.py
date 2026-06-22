"""Agent backend abstraction for mock and file-bridge execution."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
import time
from typing import Any

from .constants import BRIDGE_DIRNAME, REQUESTS_DIRNAME, RESPONSES_DIRNAME
from .prompting import build_verification_instruction, build_work_instruction


@dataclass
class BackendEnvelope:
    agent_id: str
    payload: dict[str, Any]


@dataclass
class MockAgentBackend:
    """Deterministic backend used by tests and local dry runs."""

    work_queue: list[dict[str, Any]] = field(default_factory=list)
    verification_queue: list[dict[str, Any]] = field(default_factory=list)
    _counter: int = 0

    def _next_agent_id(self, prefix: str) -> str:
        self._counter += 1
        return f"{prefix}_{self._counter}"

    def run_work(self, task_id: str, prompt: dict[str, Any]) -> BackendEnvelope:
        if not self.work_queue:
            raise RuntimeError(f"No queued work response for task {task_id}")
        return BackendEnvelope(agent_id=self._next_agent_id("work"), payload=self.work_queue.pop(0))

    def run_verification(self, task_id: str, prompt: dict[str, Any]) -> BackendEnvelope:
        if not self.verification_queue:
            raise RuntimeError(f"No queued verification response for task {task_id}")
        return BackendEnvelope(agent_id=self._next_agent_id("verify"), payload=self.verification_queue.pop(0))


class CodexAgentBackend:
    """File bridge for real Codex-driven execution.

    The local Python runtime cannot call host-side chat tools directly.
    Instead it emits request files and waits for a compatible responder
    to write JSON result files back into the bridge response directory.
    """

    def __init__(self, runtime_root: Path, *, timeout_seconds: int = 300, poll_interval_seconds: float = 1.0) -> None:
        self.runtime_root = runtime_root
        self.timeout_seconds = timeout_seconds
        self.poll_interval_seconds = poll_interval_seconds
        self.bridge_root = runtime_root / BRIDGE_DIRNAME
        self.requests_dir = self.bridge_root / REQUESTS_DIRNAME
        self.responses_dir = self.bridge_root / RESPONSES_DIRNAME
        self.requests_dir.mkdir(parents=True, exist_ok=True)
        self.responses_dir.mkdir(parents=True, exist_ok=True)
        self._counter = 0

    def _next_agent_id(self, prefix: str) -> str:
        self._counter += 1
        return f"{prefix}_{self._counter}"

    def run_work(self, task_id: str, prompt: dict[str, Any]) -> BackendEnvelope:
        return self._roundtrip(
            kind="work",
            task_id=task_id,
            prompt=prompt,
            instruction=build_work_instruction(prompt),
        )

    def run_verification(self, task_id: str, prompt: dict[str, Any]) -> BackendEnvelope:
        return self._roundtrip(
            kind="verification",
            task_id=task_id,
            prompt=prompt,
            instruction=build_verification_instruction(prompt),
        )

    def _roundtrip(self, *, kind: str, task_id: str, prompt: dict[str, Any], instruction: str) -> BackendEnvelope:
        agent_id = self._next_agent_id(kind)
        request_path = self.requests_dir / f"{agent_id}.json"
        response_path = self.responses_dir / f"{agent_id}.json"
        request_path.write_text(
            json.dumps(
                {
                    "agent_id": agent_id,
                    "kind": kind,
                    "task_id": task_id,
                    "instruction": instruction,
                    "prompt": prompt,
                },
                ensure_ascii=True,
                indent=2,
                sort_keys=True,
            ),
            encoding="utf-8",
        )
        deadline = time.time() + self.timeout_seconds
        while time.time() < deadline:
            if response_path.exists():
                payload = json.loads(response_path.read_text(encoding="utf-8-sig"))
                return BackendEnvelope(agent_id=agent_id, payload=payload)
            time.sleep(self.poll_interval_seconds)
        raise TimeoutError(
            f"Timed out waiting for {kind} response for task {task_id}. "
            f"Expected response file at {response_path}"
        )
