"""P3 Research automation — breakthrough scoring, batch benchmark replay, capability maps.

Wraps juris-calculus breakthrough_candidates scoring, provides batch
benchmark replay against current engine state, and auto-generates
capability maps and blocking reports.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .juris_calculus_bridge import JurisCalculusBridge
from .batch_litigation import (
    BatchLitigationCase,
    BatchLitigationResult,
    run_batch_litigation,
)

JURIS_ROOT = r"D:\Codex\juris-calculus"


@dataclass
class BreakthroughRanking:
    theorem_id: str
    proposition: str
    priority_raw: float
    engineering_unlock: float
    complexity: int
    depends_on: list[str]
    risk: str


@dataclass
class CapabilityMap:
    theorem_id: str
    status: str  # PROVED | PARTIAL | UNPROVEN | DATA_BLOCKED
    module: str
    capability: str
    gap: str


@dataclass
class ResearchAutomationReport:
    breakthroughs: list[BreakthroughRanking] = field(default_factory=list)
    capability_map: list[CapabilityMap] = field(default_factory=list)
    benchmark_results: dict[str, Any] = field(default_factory=dict)
    top_priority: str = ""
    blocking_items: list[str] = field(default_factory=list)


def rank_breakthroughs(
    *,
    juris_root: str = JURIS_ROOT,
) -> list[BreakthroughRanking]:
    import importlib, sys
    if juris_root not in sys.path:
        sys.path.insert(0, juris_root)
    mod = importlib.import_module("compiler_core.breakthrough_candidates")
    ranked = mod.ranked_candidates()
    return [
        BreakthroughRanking(
            theorem_id=c["theorem_id"],
            proposition=c.get("proposition", ""),
            priority_raw=c.get("priority_raw", 0.0),
            engineering_unlock=c.get("engineering_unlock_score", 0.0),
            complexity=c.get("estimated_complexity", 0),
            depends_on=c.get("depends_on", []),
            risk=c.get("risk_if_wrong", ""),
        )
        for c in ranked
    ]


def build_capability_map(
    *,
    juris_root: str = JURIS_ROOT,
) -> list[CapabilityMap]:
    import importlib, sys
    if juris_root not in sys.path:
        sys.path.insert(0, juris_root)
    mod = importlib.import_module("compiler_core.breakthrough_candidates")
    candidates = mod.CANDIDATES
    return [
        CapabilityMap(
            theorem_id=c["theorem_id"],
            status="UNPROVEN",
            module=c.get("production_module", ""),
            capability=c.get("capability_unlocked", ""),
            gap=c.get("current_gap", ""),
        )
        for c in candidates
    ]


STANDARD_BENCHMARK_CASES = [
    BatchLitigationCase(
        case_id="bench_dag_linear",
        facts={"a", "b"},
        horn_rules=[
            {"head": "C", "body": ["a", "b"]},
            {"head": "D", "body": ["C"]},
        ],
        target_claims=["C", "D"],
    ),
    BatchLitigationCase(
        case_id="bench_cycle",
        facts={"x", "y"},
        horn_rules=[
            {"head": "A", "body": ["x"]},
            {"head": "B", "body": ["y"]},
        ],
        target_claims=["A", "B"],
    ),
    BatchLitigationCase(
        case_id="bench_single",
        facts={"p"},
        horn_rules=[{"head": "Q", "body": ["p"]}],
        target_claims=["Q"],
    ),
]


def run_benchmark_replay(
    *,
    juris_root: str = JURIS_ROOT,
    cases: list[BatchLitigationCase] | None = None,
) -> dict[str, Any]:
    if cases is None:
        cases = list(STANDARD_BENCHMARK_CASES)
    report = run_batch_litigation(cases, juris_root=juris_root)
    return {
        "total_cases": report.total_cases,
        "pass_count": report.pass_count,
        "fail_count": report.fail_count,
        "all_passed": report.all_passed,
        "details": [
            {
                "case_id": r.case_id,
                "horn_saturated": r.horn_saturated,
                "horn_witnesses": r.horn_witnesses,
                "grounded_accepted": r.grounded_accepted,
                "certificates": len(r.certificates),
                "impacts": len(r.rule_impacts),
                "missing": len(r.missing_evidence),
            }
            for r in report.cases
        ],
    }


def run_research_automation(
    *,
    juris_root: str = JURIS_ROOT,
) -> ResearchAutomationReport:
    breakthroughs = rank_breakthroughs(juris_root=juris_root)
    capability_map = build_capability_map(juris_root=juris_root)
    benchmark = run_benchmark_replay(juris_root=juris_root)

    top = breakthroughs[0].theorem_id if breakthroughs else "none"
    blocking = [
        c.theorem_id
        for c in breakthroughs
        if c.complexity >= 5 and not c.depends_on
    ]

    return ResearchAutomationReport(
        breakthroughs=breakthroughs,
        capability_map=capability_map,
        benchmark_results=benchmark,
        top_priority=top,
        blocking_items=blocking,
    )
