"""Template protocol."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from ..models import Direction


@dataclass
class RetryAction:
    action: str
    reason: str


@dataclass
class CompletionPolicy:
    target_validated_findings: int
    max_iterations: int
    require_tail_pass: bool = True


class TaskTemplate(Protocol):
    name: str

    def build_task_spec_schema(self) -> dict:
        ...

    def initial_direction(self) -> Direction:
        ...

    def seed_directions(self, *, task_spec: str) -> list[Direction]:
        ...

    def completion_policy(self, *, task_spec: str) -> CompletionPolicy:
        ...

    def generate_next_direction(self, *, tried_directions: list[Direction], progress, trigger: str) -> Direction:
        ...

    def template_stall_rules(self, *, progress, verification_results: list[dict]) -> list[str]:
        ...

    def validate_finding_rules(self, candidate: dict) -> list[str]:
        ...

    def handle_same_direction_retry(self, *, progress, claim_id: str) -> RetryAction:
        ...
