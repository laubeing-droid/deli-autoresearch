# Runtime Conformance Report — Unified Legal Kernel v1

Generated: 2026-06-27

## Pipeline Stages

| Stage | Function | Formal Model | Conformance |
|-------|----------|-------------|-------------|
| 0 | validate model/time/jurisdiction | — | N/A |
| 1 | positive Horn closure | HornCanonical.lean | CONFORMANT |
| 2 | DDL norm and violation records | DDLDefinitions.lean | CONFORMANT |
| 3 | canonical Argument and Attack compilation | ArgumentCompiler.lean | CONFORMANT |
| 4 | grounded extension | DungFixedPoint.lean | CONFORMANT |
| 5 | generic Decision projection | AttackDecision.lean | CONFORMANT |
| 6 | certificate emission | CertificateChecker.lean | CONFORMANT |
| 7 | independent certificate verification | CertificateChecker.lean | CONFORMANT |

## Test Coverage

### SPEC Tests (juris-calculus/tests/spec/)

| Test Suite | Tests | Pass | Fail |
|-----------|-------|------|------|
| test_horn_semantics.py | 16 | 16 | 0 |
| test_argument_compiler.py | 10 | 10 | 0 |
| test_attack_compiler.py | 8 | 8 | 0 |
| test_decision_projection.py | 12 | 12 | 0 |
| test_certificate_checker.py | 17 | 17 | 0 |
| test_certificate_mutations.py | 11 | 11 | 0 |
| test_jc_runtime_refinement.py | 12 | 12 | 0 |
| test_safety_theorems.py | 10 | 10 | 0 |
| test_end_to_end.py | 13 | 13 | 0 |
| **SPEC subtotal** | **109** | **109** | **0** |

### Full Test Suites

| Suite | Command | Passed | Skipped | Failed |
|-------|---------|--------|---------|--------|
| deli-autoresearch | `cd deli-autoresearch && pytest -q` | 128 | 0 | 0 |
| juris-calculus | `cd juris-calculus && pytest -q` | 415 | 38 | 0 |
| **Total** | | **543** | **38** | **0** |

## Independence Verification

- `certificate_checker.py`: ZERO imports from `evaluator.py`
- `grounded_extension`: standalone, no production dependencies
- All certificate types have independent `verify` methods

## Fail-Closed Verification

| Scenario | Expected | Actual |
|----------|----------|--------|
| Tampered certificate | REJECTED | REJECTED |
| Wrong iteration | REJECTED | REJECTED |
| Forged attack | REJECTED | REJECTED |
| Missing argument | REJECTED | REJECTED |
