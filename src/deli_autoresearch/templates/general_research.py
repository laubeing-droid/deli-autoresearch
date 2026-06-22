"""General research template."""

from __future__ import annotations

from ..constants import BASE_DIRECTION_TYPES
from ..models import Direction
from .base import CompletionPolicy, RetryAction


class GeneralResearchTemplate:
    name = "general_research"

    def build_task_spec_schema(self) -> dict:
        return {
            "required_sections": ["goal", "milestones", "success_criteria", "constraints"],
            "max_claims_per_iteration": 3,
        }

    def initial_direction(self) -> Direction:
        return Direction(
            strategy_type="new_evidence_path",
            summary="Start from direct evidence collection.",
            rationale="Default general-research starting direction.",
            origin_iteration=0,
        )

    def seed_directions(self, *, task_spec: str) -> list[Direction]:
        return [self.initial_direction()]

    def completion_policy(self, *, task_spec: str) -> CompletionPolicy:
        return CompletionPolicy(target_validated_findings=1, max_iterations=12, require_tail_pass=True)

    def generate_next_direction(self, *, tried_directions: list[Direction], progress, trigger: str) -> Direction:
        used = {direction.strategy_type for direction in tried_directions}
        for strategy in BASE_DIRECTION_TYPES:
            if strategy != (progress.current_direction or {}).get("strategy_type") and strategy not in used:
                return Direction(
                    strategy_type=strategy,
                    summary=f"Pivot via {strategy}.",
                    rationale=f"Triggered by {trigger}.",
                    origin_iteration=progress.iteration,
                )
        fallback = next(iter(BASE_DIRECTION_TYPES - {(progress.current_direction or {}).get('strategy_type')}), "constraint_shift")
        return Direction(
            strategy_type=fallback,
            summary=f"Repeat pivot via {fallback}.",
            rationale=f"All strategies used; cycling because of {trigger}.",
            origin_iteration=progress.iteration,
        )

    def template_stall_rules(self, *, progress, verification_results: list[dict]) -> list[str]:
        return []

    def validate_finding_rules(self, candidate: dict) -> list[str]:
        errors: list[str] = []
        if not candidate.get("claim"):
            errors.append("missing claim text")
        return errors

    def handle_same_direction_retry(self, *, progress, claim_id: str) -> RetryAction:
        return RetryAction(action="new_claim_same_direction", reason=f"Claim {claim_id} exceeded retry limit.")
