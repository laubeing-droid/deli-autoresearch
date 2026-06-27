# SPEC-240 Acceptance Criteria

## Lean Formal Proofs

| Criterion | Verification |
|-----------|-------------|
| 0 sorry in AttackDecision.lean | `grep sorry → empty` |
| 0 admit in AttackDecision.lean | `grep admit → empty` |
| 0 custom axiom | AxiomAudit: only standard Lean axioms |
| `lake build +JurisLean.AttackDecision` passes | Build log |
| All 6 theorems proven | Build output shows no errors |

## Python Runtime Tests

| Criterion | Verification |
|-----------|-------------|
| `test_attack_compiler.py` passes | 8/8 passed |
| `test_decision_projection.py` passes | 12/12 passed |
| Full test suite passes | 352 passed, 0 failed |

## Semantic Alignment

| Criterion | Verification |
|-----------|-------------|
| compileAttacks mirrors Lean definition | Both filter edges to arg_set endpoints |
| decisionProjection mirrors Lean definition | TAINTED/PROVED/REFUTED/UNDECIDED mapping |
| No argument in args gets TAINTED | Both Lean and Python prove/verify |
