"""Canonical cross-repo fixtures for refinement and checker tests."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .aaf_canonical import STANDARD_TEST_CASES
from .juris_calculus_bridge import JurisCalculusBridge


@dataclass(frozen=True)
class CanonicalCase:
    name: str
    claims: list[dict[str, Any]]
    attacks: list[tuple[str, str]]
    expected_accepted: list[str]
    expected_undecided: list[str]


class CanonicalTestSuite:
    """Single source of truth for cross-repo grounded fixtures."""

    @classmethod
    def grounded_extension_cases(cls) -> list[CanonicalCase]:
        cases: dict[str, CanonicalCase] = {}

        def add_case(name: str, claims: list[dict[str, Any]], attacks, exp_in, exp_undec) -> None:
            normalized_attacks = [tuple(pair) for pair in attacks]
            cases[name] = CanonicalCase(
                name=name,
                claims=claims,
                attacks=normalized_attacks,
                expected_accepted=sorted(exp_in),
                expected_undecided=sorted(exp_undec),
            )

        for item in STANDARD_TEST_CASES:
            args = item["aaf"].get("arguments", [])
            add_case(
                item["name"],
                [{"id": arg} for arg in args],
                item["aaf"].get("attacks", []),
                item.get("expected_in", []),
                item.get("expected_undec", []),
            )

        bridge_case_groups = (
            JurisCalculusBridge.dag_linear_cases(),
            JurisCalculusBridge.bidirectional_cycle_cases(),
            JurisCalculusBridge.triangle_cycle_cases(),
            JurisCalculusBridge.even_cycle_cases(),
            JurisCalculusBridge.mixed_cases(),
            JurisCalculusBridge.self_loop_cases(),
            JurisCalculusBridge.long_chain_cases(),
            JurisCalculusBridge.branched_dag_cases(),
            JurisCalculusBridge.single_node_cases(),
            JurisCalculusBridge.disconnected_cases(),
            JurisCalculusBridge.cycle_attacking_dag_cases(),
            JurisCalculusBridge.dag_attacking_cycle_cases(),
            JurisCalculusBridge.multiple_attackers_cases(),
            JurisCalculusBridge.nested_scc_cases(),
        )
        for group in bridge_case_groups:
            for item in group:
                add_case(
                    item["name"],
                    item["claims"],
                    item["attacks"],
                    item.get("expected_accepted", set()),
                    item.get("expected_undecided", set()),
                )

        return [cases[name] for name in sorted(cases)]
