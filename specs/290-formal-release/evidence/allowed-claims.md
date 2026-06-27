# Allowed Claims — Unified Legal Kernel v1

Generated: 2026-06-27

## Formal Theorems (PROVEN, 0 sorry in blocking path)

1. **Horn closure is positive and monotone.** (hornStep_monotone, hornClosure_extensive, hornClosure_closed, hornClosure_idempotent)
2. **Argument compilation is sound and complete.** (compiler_correctness)
3. **Attack compilation is sound, complete, and exact.** (compileAttacks_sound, compileAttacks_complete, compileAttacks_exact)
4. **Decision status is mutually exclusive and covers all cases.** (decision_status_mutually_exclusive, decision_status_coverage)
5. **TAINTED status is impossible for well-formed arguments.** (tainted_fail_closed)
6. **Checker acceptance implies accepted arguments have PROVED status.** (check_sound)
7. **Checker acceptance implies accepted arguments are in the grounded extension.** (certificate_verifies)
8. **End-to-end: checker acceptance implies formal output equality, provenance safety, temporal safety, and jurisdiction safety.** (certified_end_to_end_refinement)

## Runtime Properties (TESTED, 109 tests)

1. **Horn closure is positive and monotone at runtime.** (test_monotone, test_positive_only)
2. **Grounded extension matches Dung semantics.** (test_simple_aaf, test_cycle)
3. **Certificates are independent of the production evaluator.** (independence verification)
4. **Tampered certificates are rejected.** (mutation tests)
5. **Pipeline stages align with the formal model.** (test_jc_runtime_refinement)

## Boundary Conditions

- **Finite models only.** The formal proofs assume finite argument sets (Finset).
- **Positive Horn rules only.** No negation in rule premises.
- **Dung grounded semantics only.** No preferred, stable, or other semantics.
- **Single-jurisdiction.** Cross-jurisdiction mapping is DEFERRED.
