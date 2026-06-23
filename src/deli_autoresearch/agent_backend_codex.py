"""Agent backend abstraction for mock and file-bridge execution.

Bridge protocol v1.0: atomic request/response with UUID-bound request_id,
response validation, and consumed-response archive.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
import os
import time
from pathlib import Path
from typing import Any

from .constants import (
    ARCHIVE_DIRNAME,
    BRIDGE_DIRNAME,
    BRIDGE_PROTOCOL_VERSION,
    REQUESTS_DIRNAME,
    RESPONSES_DIRNAME,
)
from .models import (
    BridgeRequest,
    BridgeResponse,
    hash_digest,
    new_uuid,
)
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

    def run_work(self, task_id: str, prompt: dict[str, Any]) -> BackendEnvelope:
        if not self.work_queue:
            raise RuntimeError(f"No queued work response for task {task_id}")
        payload = self.work_queue.pop(0)
        agent_id = payload.get("request_id", new_uuid())
        return BackendEnvelope(agent_id=agent_id, payload=payload)

    def run_verification(self, task_id: str, prompt: dict[str, Any]) -> BackendEnvelope:
        if not self.verification_queue:
            raise RuntimeError(f"No queued verification response for task {task_id}")
        payload = self.verification_queue.pop(0)
        agent_id = payload.get("request_id", new_uuid())
        return BackendEnvelope(agent_id=agent_id, payload=payload)


class CodexAgentBackend:
    """File bridge for real Codex-driven execution (v1.0 atomic protocol).

    Request files are written atomically. Responses are validated against
    request fields (request_id, task_id, iteration, claim_id, request_digest).
    Consumed responses are archived immediately.
    """

    def __init__(
        self,
        runtime_root: Path,
        *,
        timeout_seconds: int = 300,
        poll_interval_seconds: float = 1.0,
    ) -> None:
        self.runtime_root = runtime_root
        self.timeout_seconds = timeout_seconds
        self.poll_interval_seconds = poll_interval_seconds
        self.bridge_root = runtime_root / BRIDGE_DIRNAME
        self.requests_dir = self.bridge_root / REQUESTS_DIRNAME
        self.responses_dir = self.bridge_root / RESPONSES_DIRNAME
        self.archive_dir = self.bridge_root / ARCHIVE_DIRNAME
        self.requests_dir.mkdir(parents=True, exist_ok=True)
        self.responses_dir.mkdir(parents=True, exist_ok=True)
        self.archive_dir.mkdir(parents=True, exist_ok=True)

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

    def _roundtrip(
        self, *, kind: str, task_id: str, prompt: dict[str, Any], instruction: str
    ) -> BackendEnvelope:
        """Atomic request/response roundtrip with validation and archive."""
        iteration = prompt.get("iteration", 0)
        claim_id = prompt.get("claim_id", str(self._fallback_claim_id(task_id)))
        request_id = prompt.get("request_id", new_uuid())

        request = BridgeRequest(
            request_id=request_id,
            task_id=task_id,
            iteration=iteration,
            kind=kind,
            claim_id=claim_id,
            prompt=prompt,
            instruction=instruction,
            protocol_version=BRIDGE_PROTOCOL_VERSION,
        )

        # Atomic write of request file
        request_path = self.requests_dir / f"{request_id}.json"
        tmp_path = request_path.with_suffix(".tmp")
        try:
            tmp_path.write_text(
                json.dumps(request.to_dict(), ensure_ascii=True, indent=2, sort_keys=True),
                encoding="utf-8",
            )
            os.replace(str(tmp_path), str(request_path))
        except Exception:
            if tmp_path.exists():
                tmp_path.unlink()
            raise

        # Wait for response
        response_path = self.responses_dir / f"{request_id}.json"
        deadline = time.time() + self.timeout_seconds
        while time.time() < deadline:
            if response_path.exists():
                # Read and validate response
                try:
                    raw = json.loads(response_path.read_text(encoding="utf-8-sig"))
                    response = BridgeResponse.from_dict(raw)
                    errors = response.validate(request)
                    if errors:
                        raise ValueError(f"Response validation failed: {errors}")
                    # Archive consumed response
                    self._archive_response(response_path, request_id)
                    return BackendEnvelope(agent_id=request_id, payload=response.payload)
                except (json.JSONDecodeError, ValueError) as exc:
                    # Half-written or invalid response — archive and continue waiting
                    try:
                        self._archive_response(response_path, request_id)
                    except OSError:
                        pass
                    if deadline - time.time() < 5:
                        raise TimeoutError(f"Invalid response for {request_id}: {exc}")
            time.sleep(self.poll_interval_seconds)

        raise TimeoutError(
            f"Timed out waiting for {kind} response for request {request_id} "
            f"(task {task_id}, iteration {iteration}). "
            f"Expected response file at {response_path}"
        )

    def _archive_response(self, response_path: Path, request_id: str) -> None:
        """Atomically move consumed response to archive."""
        if not response_path.exists():
            return
        archive_path = self.archive_dir / f"{request_id}.json"
        if archive_path.exists():
            # Append timestamp to avoid collision
            archive_path = self.archive_dir / f"{request_id}_{int(time.time())}.json"
        os.replace(str(response_path), str(archive_path))

    def _fallback_claim_id(self, task_id: str) -> str:
        return f"{task_id}_unknown"
