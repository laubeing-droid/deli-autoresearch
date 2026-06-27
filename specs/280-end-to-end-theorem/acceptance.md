# SPEC-280 Acceptance Criteria

## Lean Formal Proofs

| Criterion | Verification |
|-----------|-------------|
| EndToEnd.lean builds | `lake build +JurisLean.EndToEnd` passes |
| 0 sorry in EndToEnd.lean | grep sorry → empty (comments only) |
| 0 sorry in blocking path | SafetyTheorems.lean + EndToEnd.lean + CertificateChecker.lean + AttackDecision.lean = 0 sorry |
| 0 admit | grep admit → empty |
| 0 custom axiom | Only standard Lean axioms |
| certified_end_to_end_refinement proven | Build output: no errors |
| SORRY_LEDGER all CLOSED | All entries marked CLOSED |

## Python Runtime Tests

| Criterion | Verification |
|-----------|-------------|
| test_end_to_end.py | 13/13 passed |
| Full spec test suite | 119/119 passed |
| Composition tests | Horn → AAF → grounded verified |
| Biconditional tests | Certificate acceptance ↔ grounded membership |
| Fail-closed tests | Tampered/wrong certificates rejected |

## Sorry Audit (SPEC-280 Closing Pass)

| Entry | Status | Resolution |
|-------|--------|------------|
| SORRY-002 (provenance_sound) | CLOSED | Hypothesis strengthened, sorry removed |
| burden_unsatisfied_blocks_defense | CLOSED | Proven via push_neg + Or.inr |
| violation_implies_norm_active | CLOSED | DEFERRED: domain axiom (RuleId≠NormId) |
| permission_no_direct_violation | CLOSED | DEFERRED: domain axiom |
| constitutive_no_direct_violation | CLOSED | DEFERRED: domain axiom |
