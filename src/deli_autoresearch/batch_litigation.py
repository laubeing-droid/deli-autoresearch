"""P2 Batch litigation runner — deterministic multi-claim Horn+AAF evaluation.

Takes a batch of claims, facts, and Horn rules, runs them through
juris-calculus (Horn fixpoint -> AAF -> grounded extension),
collects certificates, proof traces, and SCC witnesses, then feeds
results back to the Deli runtime as structured findings.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .juris_calculus_bridge import JurisCalculusBridge

JURIS_ROOT = r"D:\Codex\juris-calculus"


@dataclass
class BatchLitigationCase:
    case_id: str
    facts: set[str]
    horn_rules: list[dict[str, Any]]
    target_claims: list[str]


@dataclass
class BatchLitigationResult:
    case_id: str
    horn_derived: set[str]
    horn_saturated: bool
    horn_witnesses: int
    grounded_accepted: list[str]
    grounded_rejected: list[str]
    grounded_undecided: list[str]
    certificates: list[dict[str, Any]]
    scc_witnesses: list[list[str]]
    rule_impacts: list[dict[str, Any]]
    missing_evidence: list[dict[str, Any]]
    total_findings: int


@dataclass
class BatchReport:
    cases: list[BatchLitigationResult] = field(default_factory=list)
    total_cases: int = 0
    pass_count: int = 0
    fail_count: int = 0

    @property
    def all_passed(self) -> bool:
        return self.fail_count == 0


def _horn_fixpoint(
    bridge: JurisCalculusBridge,
    initial: dict[str, Any],
    rules: list[dict[str, Any]],
) -> tuple[set[str], Any]:
    import importlib, sys
    if str(bridge.juris_root) not in sys.path:
        sys.path.insert(0, str(bridge.juris_root))
    mod = importlib.import_module("compiler_core.horn_completeness")
    derived, comp = mod.horn_fixpoint_with_completeness(initial, rules)
    return derived, comp


def _run_one_case(
    bridge: JurisCalculusBridge,
    case: BatchLitigationCase,
) -> BatchLitigationResult:
    initial = {f: True for f in case.facts}
    derived, completeness = _horn_fixpoint(bridge, initial, case.horn_rules)

    # Compile derived Horn conclusions to AAF claims/attacks
    aaf_claims = [{"id": c} for c in sorted(derived)]
    aaf_attacks: list[tuple[str, str]] = []
    for rule in case.horn_rules:
        head = rule.get("head", "")
        for atom in rule.get("body", []):
            aaf_attacks.append((head, atom))
    aaf_attacks = [(s, t) for s, t in aaf_attacks if s in derived and t in derived]

    grounded = bridge.run_grounded_extension(aaf_claims, aaf_attacks)

    certificates: list[dict[str, Any]] = []
    for cid in case.target_claims:
        cert = bridge.generate_litigation_certificate(cid, aaf_claims, aaf_attacks, result=grounded)
        certificates.append(cert)

    # SCC witnesses
    try:
        import importlib, sys
        if str(bridge.juris_root) not in sys.path:
            sys.path.insert(0, str(bridge.juris_root))
        mod = importlib.import_module("compiler_core.argumentation")
        sccs = mod.scc_decomposition(aaf_claims, aaf_attacks)
    except Exception:
        sccs = []

    impacts: list[dict[str, Any]] = []
    for rule in case.horn_rules:
        rid = rule.get("id", rule.get("head", ""))
        if rid:
            impact = bridge.analyze_horn_rule_impact(rid, case.horn_rules, case.facts)
            impacts.append(impact)

    missing: list[dict[str, Any]] = []
    for cid in case.target_claims:
        me = bridge.compute_horn_missing_evidence(cid, case.facts, case.horn_rules)
        missing.append(me)

    total = len(certificates) + len(impacts) + len(missing)

    return BatchLitigationResult(
        case_id=case.case_id,
        horn_derived=derived,
        horn_saturated=bool(getattr(completeness, "saturated", True)),
        horn_witnesses=len(getattr(completeness, "proof_witnesses", [])),
        grounded_accepted=grounded.get("accepted", []),
        grounded_rejected=grounded.get("rejected", []),
        grounded_undecided=grounded.get("undecided", []),
        certificates=certificates,
        scc_witnesses=sccs,
        rule_impacts=impacts,
        missing_evidence=missing,
        total_findings=total,
    )


def run_batch_litigation(
    cases: list[BatchLitigationCase],
    *,
    juris_root: str = JURIS_ROOT,
) -> BatchReport:
    bridge = JurisCalculusBridge(juris_root)
    report = BatchReport()
    for case in cases:
        result = _run_one_case(bridge, case)
        report.cases.append(result)
        report.total_cases += 1
        if result.total_findings > 0:
            report.pass_count += 1
        else:
            report.fail_count += 1
    return report
