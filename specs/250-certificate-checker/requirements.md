# SPEC-250 Requirements: Certificate Checker

## Goal

Prove the boundary of independent certificate checking.

## Functional Requirements

| ID | Requirement |
|----|-------------|
| FREQ-250-001 | Certificate SHALL contain model and input hashes |
| FREQ-250-002 | Certificate SHALL contain Horn derivation witnesses |
| FREQ-250-003 | Certificate SHALL contain Argument records |
| FREQ-250-004 | Certificate SHALL contain Attack records and witnesses |
| FREQ-250-005 | Certificate SHALL contain grounded evidence |
| FREQ-250-006 | Certificate SHALL contain decision evidence |
| FREQ-250-007 | Formal model SHALL prove checker soundness |

## Security Requirements

| ID | Requirement |
|----|-------------|
| SREQ-250-001 | Checker SHALL NOT call the JC production evaluator |
| SREQ-250-002 | Checker SHALL reject missing required fields |
| SREQ-250-003 | Checker SHALL reject tampered witnesses |

## Blocking Theorems

| Lean Name | Status |
|-----------|--------|
| `check_sound` | PROVEN |
| `certificate_verifies` | PROVEN |

## Formal Verification

- 0 sorry, 0 admit, 0 custom axiom in CertificateChecker.lean
- `lake build +JurisLean.CertificateChecker` passes
- Axiom audit: only standard Lean axioms

## Runtime Alignment

- `test_certificate_checker.py`: 17 tests (Horn, IN, OUT, UNDEC, independence)
- `test_certificate_mutations.py`: 11 tests (removed premise, forged rule/attack/label, hash)
- 380 passed, 38 skipped, 0 failed
