# Theorem Manifest — Unified Legal Kernel v1

Generated: 2026-06-27 (full regeneration from actual Lean source files)

Source of truth: `legal-math-modeling/docs/formal-release/theorem_manifest.json`

## Core Blocking-Path Theorems (ZERO sorry, ZERO custom axiom)

Verified by: `lake build JurisLean` (umbrella, 2954 jobs, 0 errors)

All theorems below exist as actual `theorem` or `lemma` declarations in the Lean source files
under `proofs/lean/juris_lean/JurisLean/`.

### FiniteMonotoneIteration.lean (9 core theorems)

Generic finite monotone iteration kernel. Shared by AAF and Horn tracks.

| # | Theorem | Line | Description |
|---|---------|------|-------------|
| 1 | `iter_succ` | L30 | Iteration successor definition |
| 2 | `iter_subset_univ` | L32 | Iteration stays within universe |
| 3 | `iter_mono` | L39 | Iteration is monotone |
| 4 | `iter_stable` | L46 | Stable iteration characterization |
| 5 | `iter_ssubset_of_ne` | L62 | Strict subset when not equal |
| 6 | `iter_card_lt_of_ne` | L71 | Cardinality strictly decreases |
| 7 | `iter_card_le_univ` | L75 | Cardinality bounded by universe |
| 8 | `exists_fixpoint_le_card` | L80 | Fixpoint exists within card steps |
| 9 | `fixed_at_card` | L103 | Fixed point reached at card bound |

### DungFixedPoint.lean (17 core theorems)

Dung grounded extension fixed-point layer.

| # | Theorem | Line | Description |
|---|---------|------|-------------|
| 10 | `F_monotone` | L44 | Characteristic function is monotone |
| 11 | `iteration_monotone` | L48 | Iteration is monotone |
| 12 | `grounded_eq_groundedSpec` | L53 | Grounded equals groundedSpec |
| 13 | `finite_termination` | L56 | Iteration terminates finitely |
| 14 | `iteration_bound` | L60 | Iteration bounded by card |
| 15 | `groundedSpec_is_fixed_point` | L64 | groundedSpec is a fixed point |
| 16 | `grounded_is_fixed_point` | L70 | grounded is a fixed point |
| 17 | `groundedSpec_is_least_fixed_point` | L74 | groundedSpec is least fixed point |
| 18 | `grounded_is_least_fixed_point` | L90 | grounded is least fixed point |
| 19 | `grounded_is_least_complete` | L94 | grounded is least complete extension |
| 20 | `groundedSpec_unique_least_fixed_point` | L98 | groundedSpec is unique least fixed point |
| 21 | `labelling_partition` | L104 | IN/OUT/UNDECIDED partition |
| 22 | `in_soundness` | L154 | IN label soundness |
| 23 | `out_soundness` | L163 | OUT label soundness |
| 24 | `undecided_characterization` | L169 | UNDECIDED characterization |
| 25 | `self_attack_precise_theorem` | L199 | Self-attack precise theorem |
| 26 | `self_attack_not_in_grounded` | L222 | Self-attacking args not in grounded |

### HornFixedPoint.lean (10 core theorems)

Finite Horn closure layer.

| # | Theorem | Line | Description |
|---|---------|------|-------------|
| 27 | `horn_operator_subset_univ` | L17 | Horn operator within universe |
| 28 | `horn_operator_monotone` | L21 | Horn operator is monotone |
| 29 | `horn_iteration_monotone` | L25 | Horn iteration is monotone |
| 30 | `horn_finite_termination` | L31 | Horn iteration terminates |
| 31 | `horn_iteration_bound` | L37 | Horn iteration bounded |
| 32 | `horn_result_fixed_point` | L43 | Horn result is fixed point |
| 33 | `horn_result_least_fixed_point` | L60 | Horn result is least fixed point |
| 34 | `horn_soundness` | L74 | Horn derivation soundness |
| 35 | `horn_completeness` | L79 | Horn derivation completeness |
| 36 | `horn_result_is_minimal_model` | L85 | Horn result is minimal model |

### WeightedSupNorm.lean (4 core theorems)

Weighted sup metric.

| # | Theorem | Line | Description |
|---|---------|------|-------------|
| 37 | `weightedSupDist_nonneg` | L36 | Non-negativity |
| 38 | `weightedSupDist_triangle` | L47 | Triangle inequality |
| 39 | `weightedSupDist_symm` | L69 | Symmetry |
| 40 | `weightedSupDist_complete` | L76 | Completeness |

### HornDefinitions.lean (2 core theorems)

| # | Theorem | Line | Description |
|---|---------|------|-------------|
| 41 | `TH_monotone` | L41 | Horn closure operator monotone |
| 42 | `TH_subset_univ` | L55 | Closure within universe |

### ContractionCondition.lean (1 core theorem)

| # | Theorem | Line | Description |
|---|---------|------|-------------|
| 43 | `lipschitz_coupling_implies_weighted_contraction` | L33 | Lipschitz coupling implies weighted contraction |

**Total core blocking**: 43 theorems, 0 sorry, 0 custom axiom.

---

## Supporting Theorems (non-blocking, all PROVEN, 0 sorry)

### BanachEffectiveNodes.lean (8 supporting)

| # | Theorem | Line |
|---|---------|------|
| 44 | `pricingFn_sub` | L42 |
| 45 | `abs_pricingFn_sub` | L53 |
| 46 | `abs_one_sub_beta_of_pos_lt_one` | L62 |
| 47 | `one_sub_beta_lt_one` | L69 |
| 48 | `one_sub_beta_nonneg` | L73 |
| 49 | `pricingFn_contraction` | L81 |
| 50 | `pricingFn_fixed_point` | L107 |
| 51 | `pricingFn_unique_fixed_point` | L120 |

### FiniteRosetta.lean (9 supporting)

| # | Theorem | Line |
|---|---------|------|
| 52 | `cnOnly_eq_30` | L71 |
| 53 | `collision_eq_4` | L74 |
| 54 | `asymmetry_eq_3` | L77 |
| 55 | `obstruction_eq_37` | L80 |
| 56 | `cnOnly_exceeds_half` | L83 |
| 57 | `obstruction_exceeds_half` | L86 |
| 58 | `no_total_functor` | L91 |
| 59 | `obstruction_density_gt_two_thirds` | L98 |
| 60 | `pure_obstruction_majority` | L103 |

### FiniteGaloisAdjunction.lean (2 supporting)

| # | Theorem | Line |
|---|---------|------|
| 61 | `fn_sup_preserves` | L36 |
| 62 | `galois_connection_of_residuated` | L49 |

### TemporalKripke.lean (6 supporting)

| # | Theorem | Line |
|---|---------|------|
| 63 | `temporal_guard_always` | L55 |
| 64 | `w0_guard` | L87 |
| 65 | `w1_guard` | L90 |
| 66 | `w2_guard` | L93 |
| 67 | `all_worlds_guard` | L96 |
| 68 | `litigation_always_guard` | L105 |

### UnifiedModel.lean (16 supporting)

| # | Theorem | Line |
|---|---------|------|
| 69 | `is_fireable_mono` | L72 |
| 70 | `horn_step_mono` | L78 |
| 71 | `unattacked_in_ge` | L124 |
| 72 | `unattacked_defended_any` | L166 |
| 73 | `unattacked_in_char_fn` | L173 |
| 74 | `mem_lfp_iterate` | L183 |
| 75 | `unattacked_in_lfp` | L200 |
| 76 | `avg_le_max` | L223 |
| 77 | `banach_bounded` | L238 |
| 78 | `soundness_aaf` | L271 |
| 79 | `soundness_banach` | L278 |
| 80 | `gc2_completeness` | L293 |
| 81 | `unified_composition_v2` | L309 |
| 82 | `full_chain` | L335 |
| 83 | `horn_monotone` | L355 |
| 84 | `banach_bound_uniform` | L368 |

### JC_Formalization.lean (6 supporting)

| # | Theorem | Line | Note |
|---|---------|------|------|
| 85 | `proved_theorems_card` | L139 | definitional |
| 86 | `empirical_proxy_card` | L147 | definitional |
| 87 | `refuted_theorems_card` | L155 | definitional |
| 88 | `pending_theorems_card` | L163 | definitional |
| 89 | `advance_preserves_domain_bound` | L176 | |
| 90 | `advance_cannot_revive_refuted` | L182 | |

### BanachContraction.lean (2 supporting)

| # | Theorem | Line |
|---|---------|------|
| 91 | `weighted_contraction_bound` | L21 |
| 92 | `weighted_contraction_bound_nnreal` | L34 |

### BanachFixedPoint.lean (1 supporting)

| # | Theorem | Line |
|---|---------|------|
| 93 | `weightedContractionData_of_coupling` | L34 |

### SupZeroLemma.lean (1 supporting)

| # | Theorem | Line |
|---|---------|------|
| 94 | `sup_zero_eq_zero` | L11 |

**Total supporting**: 51 theorems, 0 sorry.

---

## Grand Total

| Category | Count | Sorry | Custom Axiom |
|----------|-------|-------|-------------|
| Core blocking | 43 | 0 | 0 |
| Supporting | 51 | 0 | 0 |
| **Total** | **94** | **0** | **0** |

Note: The manifest in `legal-math-modeling/docs/formal-release/theorem_manifest.json` lists 100 entries
because some definitional entries are counted twice (as both theorem and definitional). The unique
theorem count is 94.

## Phantom File Clarification

The following Lean files were designed in SPEC-200 through SPEC-290 but were **never created** in
the repository. Their intended theorems were absorbed into the actual files listed above:

| Phantom File | Intended Content | Actual Location |
|---|---|---|
| `LegalSyntax.lean` | Legal syntax types | `HornDefinitions.lean`, `DungDefinitions.lean` |
| `DDLDefinitions.lean` | DDL modality system | PLANNED (not yet formalized) |
| `HornCanonical.lean` | Horn canonical form | `HornFixedPoint.lean` |
| `ArgumentCompiler.lean` | Argument compilation | Python implementation only |
| `AttackDecision.lean` | Attack/decision logic | `DungFixedPoint.lean`, `UnifiedModel.lean` |
| `CertificateChecker.lean` | Certificate checking | PLANNED (not yet formalized) |
| `EndToEnd.lean` | End-to-end theorem | `UnifiedModel.lean` (partial) |
| `SafetyTheorems.lean` | Safety properties | `UnifiedModel.lean`, `TemporalKripke.lean` |

## Changelog

- 2026-06-27: Full regeneration from actual Lean source files. Replaced phantom-file-based manifest
  with ground-truth theorems from `proofs/lean/juris_lean/JurisLean/`.
- Previous version referenced 46 theorems from 8 phantom Lean files; none of those files exist.
