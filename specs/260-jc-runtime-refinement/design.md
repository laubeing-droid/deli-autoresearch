# SPEC-260 Design

## Architecture

SPEC-260 is runtime-only. The 8-stage pipeline already exists in `automated_pipeline.py` and is aligned with the formal model from SPEC-200 through SPEC-250. No new Lean theorems are needed.

## Pipeline Stages (verified)

| Stage | Function | Aligned With |
|-------|----------|-------------|
| 0 | validate model/time/jurisdiction | — |
| 1 | positive Horn closure (`evaluate_horn`) | SPEC-210 Horn semantics |
| 2 | DDL norm and violation records | SPEC-220 DDL |
| 3 | canonical Argument and Attack compilation | SPEC-240 AttackCompiler |
| 4 | grounded extension | SPEC-230 DungAAF |
| 5 | generic Decision projection | SPEC-240 DecisionProjection |
| 6 | certificate emission | SPEC-250 Certificate |
| 7 | independent certificate verification | SPEC-250 CertificateChecker |

## Key Design Decisions

1. **No SyntheticClaim in production.** Only `spec_shadow_harness.py` (test-only) uses it. Verified by source inspection.
2. **Certificate checker independence.** `certificate_checker.py` has zero imports from `evaluator.py`. Verified by grep.
3. **Fail-closed.** If `cert.verify(aaf)` returns False, the pipeline must raise/abort. Verified by mutation tests.
4. **Positive Horn closure.** `evaluate_horn` uses forward chaining on positive premises only. Monotonicity verified by test.

## Test Design

- `test_jc_runtime_refinement.py`: 12 tests across 6 classes covering all 8 stages
- Uses existing infrastructure: `FixpointEvaluator`, `grounded_extension`, `GroundedINCertificate`, `OUTCertificate`, `UNDECCertificate`
- Fail-closed tests construct invalid certificates and verify rejection
