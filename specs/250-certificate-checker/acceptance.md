# SPEC-250 Acceptance Criteria

## Lean Formal Proofs

| Criterion | Verification |
|-----------|-------------|
| 0 sorry in CertificateChecker.lean | grep sorry → empty |
| 0 admit in CertificateChecker.lean | grep admit → empty |
| 0 custom axiom | AxiomAudit: only standard Lean axioms |
| `lake build +JurisLean.CertificateChecker` passes | Build log |
| check_sound proven | Build output shows no errors |
| certificate_verifies proven | Build output shows no errors |

## Python Runtime Tests

| Criterion | Verification |
|-----------|-------------|
| test_certificate_checker.py passes | 17/17 passed |
| test_certificate_mutations.py passes | 11/11 passed |
| Full test suite passes | 380 passed, 0 failed |

## Security Requirements

| Criterion | Verification |
|-----------|-------------|
| Checker independent of evaluator | Source inspection: no evaluator imports |
| Tampered witnesses rejected | Mutation tests: all 11 pass |
