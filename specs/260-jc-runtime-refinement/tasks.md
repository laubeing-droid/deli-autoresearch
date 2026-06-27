# SPEC-260 Tasks

## T1 — Pipeline Integration Tests
- [x] Create `test_jc_runtime_refinement.py` with tests for all 8 pipeline stages
- [x] Horn closure monotonicity and positivity
- [x] Grounded extension correctness (IN/OUT, cycles)
- [x] Certificate emission for all three types (IN, OUT, UNDEC)
- [x] End-to-end: grounded extension → certificate → independent verification

## T2 — Fail-Closed Tests
- [x] Tampered certificate rejected
- [x] Wrong iteration rejected
- [x] Forged attack rejected

## T3 — Production Purity
- [x] Verify no SyntheticClaim in automated_pipeline.py
- [x] Verify certificate_checker.py independent of evaluator.py

## T4 — Lifecycle Files
- [x] spec.yaml, requirements.md, tasks.md, acceptance.md, design.md, status.json
- [x] evidence/red-team-verdict.json
