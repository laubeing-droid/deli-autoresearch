# SPEC-270 Acceptance Criteria

## Lean Formal Proofs

| Criterion | Verification |
|-----------|-------------|
| SafetyTheorems.lean builds | `lake build +JurisLean.SafetyTheorems` passes |
| 1 sorry (provenance_sound) | Registered in SORRY_LEDGER.md as SORRY-002 |
| temporal_safe fully proven | No sorry |
| jurisdiction_safe fully proven | No sorry |
| 0 admit | grep admit → empty |
| 0 custom axiom | Only standard Lean axioms |

## Python Runtime Tests

| Criterion | Verification |
|-----------|-------------|
| test_safety_theorems.py | 10/10 passed |
| Provenance safety tests | 3/3 passed |
| Temporal safety tests | 2/2 passed |
| Jurisdiction safety tests | 2/2 passed |
| Fail-closed tests | 3/3 passed |

## Sorry Audit

| ID | Theorem | Sorry Location | Plan Close |
|----|---------|---------------|------------|
| SORRY-002 | provenance_sound | sources ≠ [] | SPEC-280 closing pass |
