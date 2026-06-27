# SPEC-260 Acceptance Criteria

## Pipeline Integration

| Criterion | Verification |
|-----------|-------------|
| Horn closure monotone | test_monotone PASSED |
| Horn closure positive-only | test_positive_only PASSED |
| Grounded extension IN/OUT | test_simple_aaf PASSED |
| Grounded extension cycles | test_cycle PASSED |
| IN certificate valid | test_in_certificate PASSED |
| OUT certificate valid | test_out_certificate PASSED |
| UNDEC certificate valid | test_undec_certificate PASSED |
| End-to-end verification | test_end_to_end PASSED |

## Fail-Closed

| Criterion | Verification |
|-----------|-------------|
| Tampered cert rejected | test_tampered_cert_rejected PASSED |
| Wrong iteration rejected | test_wrong_iteration_rejected PASSED |
| Forged attack rejected | test_forged_attack_rejected PASSED |

## Production Purity

| Criterion | Verification |
|-----------|-------------|
| No SyntheticClaim in production | test_no_synthetic_in_production PASSED |
| Checker independent of evaluator | source inspection: no evaluator imports in certificate_checker.py |

## Overall

| Metric | Value |
|--------|-------|
| SPEC-260 tests | 12/12 passed |
| Lean blocking theorems | 0 (runtime-only SPEC) |
| Full test suite | 392+ passed, 0 failed |
