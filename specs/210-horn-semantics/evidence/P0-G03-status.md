# P0-G03 Status — Reproduce Horn Non-Monotonicity

**Date**: 2026-06-27
**Playbook**: Playbook E, Section 3.3, P0-G03
**Baseline**: CROSS_REPO_LOCK.json (frozen 2026-06-27T16:00:00Z)

---

## Goal

Confirm whether `evaluate_horn()` in `juris-calculus/compiler_core/evaluator.py` still mixes exception/priority/negative effects into the Horn stage. Produce a minimal counterexample if yes, or evidence that the risk is eliminated if no.

## Products

| Product | Path | Status |
|---------|------|--------|
| Non-monotonicity reproduction report | `specs/210-horn-semantics/evidence/non-monotonicity-repro.md` | CREATED |
| This status report | `specs/210-horn-semantics/evidence/P0-G03-status.md` | CREATED |

---

## Verdict

**Risk eliminated.** No counterexample found. The Horn stage is strictly monotone.

---

## Evidence Summary

### Code Analysis

| Check | Result | Evidence |
|-------|--------|----------|
| `evaluate_horn` uses `fact_to_rules_horn` (no exception atoms) | YES | evaluator.py:601 vs :395 |
| `_apply_rule_horn` has no exception chain penetration | YES | evaluator.py:511-558 — no `_check_exceptions` call |
| `_apply_rule_horn` has no PROHIBITION blocking | YES | No `blocked_claims` reference |
| `_apply_rule_horn` has no rebuttal | YES | No `constraint_validator.check_rebuttal` call |
| `evaluate_horn` has no constraint rules | YES | No `check_constraint_rules` call |
| `evaluate_horn` has no CriticalClarityFailure | YES | No `critical_score_threshold` check |
| Claims only added, never removed | YES | evaluator.py:609-612 — only `claim.id not in state.claims` guard |
| `compute_formalizable` does not affect claim presence | YES | Only sets `confidence`, not claim existence |

### Counterexample Attempt

Constructed rule set with exception chain that would defeat a claim if exceptions were applied:

```
R1: p → h    (exception_chain: [R_exc])
R_exc: q → ¬h

Facts A: {p}        → claims = {h}
Facts B: {p, q}     → claims = {h}   (exception NOT triggered)
```

`claims(A) ⊆ claims(B)` — monotonicity holds.

### Test Coverage

| Category | Tests | Files | Status |
|----------|-------|-------|--------|
| Direct monotonicity (F⊆G) | 5 | test_horn_differential.py, test_nonmonotone_regression.py, test_jc_runtime_refinement.py, test_safety_theorems.py | All PASS |
| Exception defeat prevention | 2 | test_horn_differential.py | All PASS |
| Additional Horn properties | 6 | test_horn_differential.py, test_jc_runtime_refinement.py, test_end_to_end.py | All PASS |
| **Total Horn tests** | **13** | **6 files** | **All PASS** |

---

## Remaining Risks

| Risk | Severity | Notes |
|------|----------|-------|
| `k_max` depth guard edge case | Negligible | k_max set once at construction, never mutated |
| `state.rules_applied` dedup | None | By-design deduplication, not non-monotonicity |
| `fact_to_rules_horn` construction | None | Built once at __init__, never mutated |

---

## Acceptance Criteria (from Playbook E)

| Criterion | Status |
|-----------|--------|
| Given a minimal counterexample OR evidence of elimination | PASS — evidence of elimination |
| Non-monotonicity-repro.md exists | PASS |
| No P0-G04 work started | PASS |

---

## Allowed Modifications

| File | Operation |
|------|-----------|
| `deli-autoresearch/specs/210-horn-semantics/evidence/non-monotonicity-repro.md` | New |
| `deli-autoresearch/specs/210-horn-semantics/evidence/P0-G03-status.md` | New |

No code files modified. No P0-G04 work started.
