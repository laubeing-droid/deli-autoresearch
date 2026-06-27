# Theorem Manifest — Unified Legal Kernel v1

Generated: 2026-06-27 (full regeneration against working tree)

## Blocking-Path Theorems (ZERO sorry, ZERO custom axiom)

Verified by: `lake build JurisLean.HornFixedPoint JurisLean.HornCanonical JurisLean.ArgumentCompiler JurisLean.AttackDecision JurisLean.CertificateChecker JurisLean.SafetyTheorems JurisLean.EndToEnd JurisLean.DDLDefinitions`

| # | Theorem | File | SPEC | Status |
|---|---------|------|------|--------|
| 1 | horn_result_fixed_point | HornFixedPoint.lean | 210 | PROVEN |
| 2 | horn_result_is_minimal_model | HornFixedPoint.lean | 210 | PROVEN |
| 3 | horn_completeness | HornFixedPoint.lean | 210 | PROVEN |
| 4 | hornStep_monotone | HornCanonical.lean | 210 | PROVEN |
| 5 | hornClosure_extensive | HornCanonical.lean | 210 | PROVEN |
| 6 | hornClosure_closed | HornCanonical.lean | 210 | PROVEN |
| 7 | hornClosure_idempotent | HornCanonical.lean | 210 | PROVEN |
| 8 | horn_semantic_equivalence | HornCanonical.lean | 210 | PROVEN |
| 9 | compileArguments_sound | ArgumentCompiler.lean | 230 | PROVEN |
| 10 | compileArguments_complete | ArgumentCompiler.lean | 230 | PROVEN |
| 11 | compileAttacks_sound | AttackDecision.lean | 240 | PROVEN |
| 12 | compileAttacks_complete | AttackDecision.lean | 240 | PROVEN |
| 13 | compileAttacks_exact | AttackDecision.lean | 240 | PROVEN |
| 14 | decision_status_mutually_exclusive | AttackDecision.lean | 240 | PROVEN |
| 15 | decision_status_coverage | AttackDecision.lean | 240 | PROVEN |
| 16 | tainted_fail_closed | AttackDecision.lean | 240 | PROVEN |
| 17 | check_sound | CertificateChecker.lean | 250 | PROVEN |
| 18 | certificate_verifies | CertificateChecker.lean | 250 | PROVEN |
| 19 | certified_end_to_end_refinement | EndToEnd.lean | 280 | PROVEN |

**Total blocking**: 19 theorems, 0 sorry, 0 custom axiom.

## Supporting Theorems (non-blocking, fully proven, 0 sorry)

| # | Theorem | File | SPEC | Status |
|---|---------|------|------|--------|
| 20 | provenance_sound | SafetyTheorems.lean | 270 | PROVEN |
| 21 | temporal_safe | SafetyTheorems.lean | 270 | PROVEN |
| 22 | jurisdiction_safe | SafetyTheorems.lean | 270 | PROVEN |
| 23 | accepted_in_grounded | EndToEnd.lean | 280 | PROVEN |
| 24 | burden_unsatisfied_blocks_defense | DDLDefinitions.lean | 220 | PROVEN |

**Total supporting**: 5 theorems, 0 sorry.

## Deferred (Domain Axioms — sorry, 3 total)

| # | Theorem | File | SPEC | Reason |
|---|---------|------|------|--------|
| 25 | violation_implies_norm_active | DDLDefinitions.lean | 220 | Rule→Norm mapping not in model |
| 26 | permission_no_direct_violation | DDLDefinitions.lean | 220 | RuleId≠NormId structural gap |
| 27 | constitutive_no_direct_violation | DDLDefinitions.lean | 220 | Same structural gap |

**Total deferred**: 3 theorems with `sorry`. These are domain axioms, not on the blocking path.

## Additional Theorems (not on blocking path, all proven)

These exist in the codebase but are not part of the core blocking chain. Included for completeness.

| Theorem | File | SPEC |
|---------|------|------|
| horn_operator_subset_univ | HornFixedPoint.lean | 210 |
| horn_operator_monotone | HornFixedPoint.lean | 210 |
| horn_iteration_monotone | HornFixedPoint.lean | 210 |
| horn_finite_termination | HornFixedPoint.lean | 210 |
| horn_iteration_bound | HornFixedPoint.lean | 210 |
| horn_result_least_fixed_point | HornFixedPoint.lean | 210 |
| horn_soundness | HornFixedPoint.lean | 210 |
| derives_sound | HornCanonical.lean | 210 |
| derives_complete | HornCanonical.lean | 210 |
| hornClosure_least | HornCanonical.lean | 210 |
| check_proved_accepted_in_grounded | EndToEnd.lean | 280 |
| check_proved_accepted_in_args | EndToEnd.lean | 280 |
| cert_provenance_from_check | EndToEnd.lean | 280 |
| cert_temporal_from_record | EndToEnd.lean | 280 |
| cert_jurisdiction_from_record | EndToEnd.lean | 280 |
| ordered_next_requires_prior_failure | DDLDefinitions.lean | 220 |
| alternative_imposes_no_order | DDLDefinitions.lean | 220 |
| concurrent_imposes_no_order | DDLDefinitions.lean | 220 |
| court_selected_not_auto_chosen | DDLDefinitions.lean | 220 |

**Additional**: 19 theorems, 0 sorry.

## Grand Total

| Category | Count | Sorry | Custom Axiom |
|----------|-------|-------|-------------|
| Blocking | 19 | 0 | 0 |
| Supporting | 5 | 0 | 0 |
| Deferred | 3 | 3 | 0 |
| Additional | 19 | 0 | 0 |
| **Total** | **46** | **3** | **0** |

## Changelog

- 2026-06-27: Full regeneration. Corrected all theorem names to match actual Lean identifiers.
  - `compiler_correctness` → `compileArguments_sound` + `compileArguments_complete`
  - `hornClosure_converges` → `horn_result_fixed_point` + related
  - `checker_sound` → `check_sound`
  - Removed `attacksWellFormed` (dead code, not a theorem)
  - Added 18 additional theorems from codebase scan
