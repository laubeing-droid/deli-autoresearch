# P5-G01~G06 Status — Grounded & Decision Projection

**Date**: 2026-06-27
**Playbook**: Playbook E, Section 8.3, P5-G01 through P5-G06
**Baseline**: CROSS_REPO_LOCK.json (frozen 2026-06-27T16:00:00Z)

---

## P5-G01: Generic Decision Projection

**PASS.** `AttackDecision.lean:52-56`: `decisionProjection` maps `DungAAF × Arg → DecisionStatus` with 4-way logic:
1. `a ∉ args` → TAINTED (fail-closed)
2. `a ∈ grounded` → PROVED
3. attacker in grounded exists → REFUTED
4. otherwise → UNDECIDED

## P5-G02: Status Mutual Exclusion

**PASS.** `decision_status_mutually_exclusive` (line 63): proven, 0 sorry. For any `a ∈ args`, exactly one of PROVED/REFUTED/UNDECIDED holds, and TAINTED is impossible.

## P5-G03: Status Coverage

**PASS.** `decision_status_coverage` (line 87): proven, 0 sorry. `∃! s ≠ TAINTED, decisionProjection aaf a = s`.

## P5-G04: Fail-Closed Behavior

**PASS.** `tainted_fail_closed` (line 107): proven, 0 sorry. `∀ a ∈ args, projection ≠ TAINTED`. Arguments not in args get TAINTED; arguments in args never get TAINTED.

## P5-G05: No Scenario-Specific Evaluators

**PASS.** JC `evaluator.py` has no domain-specific status projection branches. The `DecisionStatus` enum is defined once in `types.py` with 4 values matching the Lean definition.

## P5-G06: JC Status Projection Aligned

**PASS.** `test_decision_projection.py`: 12/12 tests pass, covering PROVED/REFUTED/UNDECIDED/TAINTED scenarios.

---

## Test Verification

```
$ python -m pytest tests/spec/test_decision_projection.py -v
12 passed
```

## Acceptance Criteria

| Criterion | Status |
|-----------|--------|
| 4 Lean blocking theorems proven (0 sorry) | PASS |
| JC DecisionStatus matches Lean | PASS |
| No domain-specific status hardcoding | PASS |
| Fail-closed not bypassed | PASS |
