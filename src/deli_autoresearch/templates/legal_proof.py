"""Legal-proof template for G9 grounded-semantics exploration."""

from __future__ import annotations

from ..constants import LEGAL_DIRECTION_TYPES, ALL_DIRECTION_TYPES
from ..models import Direction
from .general_research import GeneralResearchTemplate
from .base import CompletionPolicy


class LegalProofTemplate(GeneralResearchTemplate):
    """Template specialised for juris-calculus G9 cyclic grounded extension.

    Inherits general stall-pressure / pivot machinery from
    GeneralResearchTemplate but overrides direction strategies,
    completion policy and stall rules to match the G9 MVM target:

    MVM = prove convergence for odd-cycle-free or bidirectional-only
    cyclic attack graphs under Dung grounded semantics.
    """

    name = "legal_proof"

    def build_task_spec_schema(self) -> dict:
        schema = super().build_task_spec_schema()
        schema["required_sections"].extend([
            "target_semantics",
            "attack_graph_class",
            "verification_engine",
            "known_lemmas",
            "mvm_breakthrough",
        ])
        return schema

    def work_prompt_contract(self) -> dict:
        contract = super().work_prompt_contract()
        contract.update({
            "required_fields": [
                "claim_text",
                "evidence",
                "source_kind",
                "verifiable",
                "formal_payload",
            ],
            "formal_payload": {
                "required": True,
                "type": "object",
                "required_keys": ["claims", "attacks", "verification_type"],
                "verification_type": "grounded_extension",
                "claims": {
                    "required": True,
                    "non_empty": True,
                    "entry_required_fields": ["id"],
                },
                "attacks": {
                    "required": True,
                    "non_empty": True,
                    "entry_shape": ["source_id", "target_id"],
                },
            },
        })
        return contract

    def initial_direction(self) -> Direction:
        return Direction(
            strategy_type="scc_decomposition",
            summary="Decompose cyclic attack graph into SCCs, apply grounded semantics per-component.",
            rationale=(
                "SCC decomposition is the most direct structural approach to taming cycles "
                "in Dung frameworks. It preserves DAG behaviour trivially (each node is its own SCC)."
            ),
            origin_iteration=0,
        )

    def seed_directions(self, *, task_spec: str) -> list[Direction]:
        return [
            self.initial_direction(),
            Direction(
                strategy_type="characteristic_function_relaxation",
                summary="Relax the characteristic function (F) to a non-monotone operator that converges on cycles.",
                rationale=(
                    "Standard F is monotone on DAGs. Relaxing to a weaker contraction "
                    "may allow fixed-point convergence even with odd cycles."
                ),
                origin_iteration=0,
            ),
            Direction(
                strategy_type="stage_extension",
                summary="Extend stage-based evaluation to handle cycles via iterative labelling refinement.",
                rationale=(
                    "Stage semantics (Caminada 2006) already handles some cycle structures. "
                    "Extending it with a convergence guarantee is a well-trodden research path."
                ),
                origin_iteration=0,
            ),
            Direction(
                strategy_type="preferred_extension_subset",
                summary="Restrict to preferred-extension subsets that are cycle-resolvable.",
                rationale=(
                    "Preferred extensions can coexist with cycles. "
                    "Finding the maximal cycle-safe subset may yield a tractable MVM."
                ),
                origin_iteration=0,
            ),
            Direction(
                strategy_type="cf2_semantics",
                summary="Apply CF2 (cycle-free) semantics: cut cycles at SCC boundaries and recombine.",
                rationale=(
                    "CF2 semantics (Baroni et al.) is designed exactly for cyclic graphs. "
                    "Proving equivalence with grounded on odd-cycle-free graphs is the MVM target."
                ),
                origin_iteration=0,
            ),
        ]

    def completion_policy(self, *, task_spec: str) -> CompletionPolicy:
        return CompletionPolicy(
            target_validated_findings=3,
            max_iterations=20,
            require_tail_pass=True,
        )

    def validate_work_candidate(self, candidate: dict) -> list[str]:
        errors = super().validate_work_candidate(candidate)
        if not isinstance(candidate, dict):
            return errors

        formal_payload = candidate.get("formal_payload")
        if not isinstance(formal_payload, dict):
            errors.append("formal_payload must be a structured object")
            return errors

        if formal_payload.get("verification_type") != "grounded_extension":
            errors.append("formal_payload.verification_type must be grounded_extension")

        claims = formal_payload.get("claims")
        if not isinstance(claims, list) or not claims:
            errors.append("formal_payload.claims must be a non-empty list")
        else:
            for index, claim in enumerate(claims):
                if not isinstance(claim, dict):
                    errors.append(f"formal_payload.claims[{index}] must be a structured object")
                elif not claim.get("id"):
                    errors.append(f"formal_payload.claims[{index}].id is required")

        attacks = formal_payload.get("attacks")
        if not isinstance(attacks, list) or not attacks:
            errors.append("formal_payload.attacks must be a non-empty list")
        else:
            for index, attack in enumerate(attacks):
                if not isinstance(attack, (list, tuple)):
                    errors.append(f"formal_payload.attacks[{index}] must be a pair")
                elif len(attack) != 2:
                    errors.append(f"formal_payload.attacks[{index}] must contain exactly two endpoints")

        return errors

    def generate_next_direction(self, *, tried_directions: list[Direction], progress, trigger: str) -> Direction:
        used = {d.strategy_type for d in tried_directions}
        current = (progress.current_direction or {}).get("strategy_type")

        for strategy in ALL_DIRECTION_TYPES:
            if strategy != current and strategy not in used:
                return Direction(
                    strategy_type=strategy,
                    summary=f"Pivot to {strategy} after {trigger}.",
                    rationale=f"Triggered by {trigger}; previous strategies exhausted: {sorted(used)}.",
                    origin_iteration=progress.iteration,
                )

        # All strategies tried; cycle back to a legal-specific one that is not current.
        for strategy in LEGAL_DIRECTION_TYPES:
            if strategy != current:
                return Direction(
                    strategy_type=strategy,
                    summary=f"Re-explore {strategy} with accumulated evidence.",
                    rationale=f"All direction types exhausted; cycling back because of {trigger}.",
                    origin_iteration=progress.iteration,
                )

        fallback = next(iter(LEGAL_DIRECTION_TYPES - {current}), "scc_decomposition")
        return Direction(
            strategy_type=fallback,
            summary=f"Final fallback: {fallback}.",
            rationale=f"No untried strategy remaining; {trigger}.",
            origin_iteration=progress.iteration,
        )

    def template_stall_rules(self, *, progress, verification_results: list[dict]) -> list[str]:
        warnings: list[str] = []
        if not verification_results and progress.iteration > 0:
            warnings.append("no verification output for legal-proof task")
        # Detect semantic collapse: all verifications returned needs_more_evidence
        # with model_generated evidence only — signals trivial/meaningless claims.
        if verification_results:
            all_nme = all(v.get("verdict") == "needs_more_evidence" for v in verification_results)
            all_model = all(
                all(e.get("source_kind") == "model_generated" for e in v.get("supporting_evidence", []))
                for v in verification_results
            )
            if all_nme and all_model:
                warnings.append(
                    "semantic_collapse_risk: all claims supported only by model_generated evidence"
                )
        return warnings

    def validate_finding_rules(self, candidate: dict) -> list[str]:
        errors: list[str] = []
        if not candidate.get("claim"):
            errors.append("missing claim text")
        # Legal-proof findings must have structured evidence with source_kind
        evidence = candidate.get("evidence", [])
        if not evidence:
            errors.append("legal-proof findings require at least one evidence item")
        for i, e in enumerate(evidence):
            if not isinstance(e, dict):
                errors.append(f"evidence[{i}] must be a structured object")
            elif not e.get("source_kind"):
                errors.append(f"evidence[{i}] missing source_kind")
        return errors
