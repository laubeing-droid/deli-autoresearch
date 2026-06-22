"""Math proof specific template."""

from __future__ import annotations

from ..models import Direction
from .general_research import GeneralResearchTemplate


class MathProofTemplate(GeneralResearchTemplate):
    name = "math_proof"

    def build_task_spec_schema(self) -> dict:
        schema = super().build_task_spec_schema()
        schema["required_sections"].extend(["conjecture", "known_lemmas"])
        return schema

    def initial_direction(self) -> Direction:
        return Direction(
            strategy_type="reframe_decomposition",
            summary="Break the conjecture into candidate lemmas.",
            rationale="Math proof tasks benefit from explicit decomposition.",
            origin_iteration=0,
        )

    def seed_directions(self, *, task_spec: str) -> list[Direction]:
        return [
            self.initial_direction(),
            Direction(
                strategy_type="opposite_hypothesis",
                summary="Try to refute the conjecture via a counterexample search.",
                rationale="A proof task should keep a disproof path available early.",
                origin_iteration=0,
            ),
            Direction(
                strategy_type="new_evidence_path",
                summary="Collect algebraic identities or canonical proof moves relevant to the conjecture.",
                rationale="Math proof tasks benefit from a direct identity-driven route alongside decomposition.",
                origin_iteration=0,
            ),
        ]

    def template_stall_rules(self, *, progress, verification_results: list[dict]) -> list[str]:
        warnings: list[str] = []
        if not verification_results and progress.iteration > 0:
            warnings.append("no verification output for proof task")
        return warnings
