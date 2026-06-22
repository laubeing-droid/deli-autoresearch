# Formal Trust Boundary

## Lean Proof Coverage
- **Status**: NOT YET DEPLOYED
- **Location**: D:\Claude\数学证明\legal-math-modeling\proofs\lean\juris_lean
- **Covered**: 0 of 13 G9A theorems formally verified in Lean
- **Planned**: characteristic_function_monotone, grounded_iteration_monotone, finite_grounded_termination, grounded_iteration_bound, grounded_is_fixed_point, grounded_is_least_fixed_point, grounded_is_least_complete_extension, grounded_unique, grounded_labelling_partition, in_soundness, out_soundness, undecided_characterization, self_attack_supported

## SMT Bounded Coverage
- **File**: compiler_core/grounded_smt_verifier.py
- **Role**: Consistency checker — verifies that a proposed labelling satisfies Dung semantics for a specific test case
- **Scope**: Bounded per-case checking, N=2..13 for universal DAG/cycle proofs
- **NOT**: Proof of least-fixed-point semantics for arbitrary graphs
- **NOT**: Inductive proof for arbitrary N

## Python Test Coverage
- **G9A**: 18 graph types, 20 tests — all pass
- **B6**: 8 engineering capability tests — all pass
- **Deli AutoResearch**: 56 tests (34 original + 15 P0 + 7 multiprocess) — all pass

## Unformalized Parts
1. Horn evaluator: uses state.max_iterations and config.k_max as hardcoded cutoffs
2. Trust label projection: UNDEC → forbidden mapping not formally prevented
3. Four-stage composition: each stage individually correct, composition unverified
4. Cross-jurisdiction mapping: MATCH/COLLISION/ASYMMETRY not formally specified

## Forbidden Declarations
1. Do not claim arbitrary-N proofs from bounded SMT enumeration (N=2..13)
2. Do not claim spectral_radius exact value from max-norm upper bound
3. Do not claim block-triangular contraction from diagonal-block-only analysis
4. Do not claim four-stage pipeline correctness from individual stage tests
5. Do not claim Lean-formalized without actual Lean proof artifacts
