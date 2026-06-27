# THEOREM_OBLIGATIONS.md — Unified Asset Ledger

**Generated**: 2026-06-27 (P0-G02)
**Baseline**: CROSS_REPO_LOCK.json frozen 2026-06-27T16:00:00Z
**Purpose**: Single source of truth for every theorem, test, script, and evidence artifact across the three repos.

---

## 0. Trust Boundary Legend

| Symbol | Meaning | Trust Level |
|--------|---------|-------------|
| `F` | **Formal** — Lean machine proof (`lake build`) | Kernel-verified (highest) |
| `S` | **Empirical Spec** — pytest under `tests/spec/` | Spec-aligned test (high) |
| `E` | **Empirical** — pytest outside `tests/spec/` | Experience-based (medium) |
| `G` | **Gate** — CI script / automated check | Mechanical (medium) |
| `D` | **Domain Axiom** — `sorry` in non-blocking path | Assumed (low, tracked) |
| `R` | **Release Evidence** — audit/report artifact | Human/LLM review (low) |

**Rule**: An asset's trust boundary is the **lowest** trust level in its dependency chain.

---

## 1. Lean Formal Theorems (F)

### 1.1 Blocking-Path Theorems (19)

These MUST build with `lake build`, MUST have ZERO sorry, ZERO custom axiom.

| # | Theorem | File | SPEC | Scope | Verified By |
|---|---------|------|------|-------|-------------|
| 1 | `horn_result_fixed_point` | HornFixedPoint.lean | 210 | Horn closure is a fixed point | `lake build JurisLean.HornFixedPoint` |
| 2 | `horn_result_is_minimal_model` | HornFixedPoint.lean | 210 | Horn closure is the least fixed point | same |
| 3 | `horn_completeness` | HornFixedPoint.lean | 210 | Derivation-complete for Horn systems | same |
| 4 | `hornStep_monotone` | HornCanonical.lean | 210 | Single Horn step monotone | `lake build JurisLean.HornCanonical` |
| 5 | `hornClosure_extensive` | HornCanonical.lean | 210 | Closure includes input | same |
| 6 | `hornClosure_closed` | HornCanonical.lean | 210 | Closure is closed under rules | same |
| 7 | `hornClosure_idempotent` | HornCanonical.lean | 210 | Closure of closure = closure | same |
| 8 | `horn_semantic_equivalence` | HornCanonical.lean | 210 | Canonical = operational Horn | same |
| 9 | `compileArguments_sound` | ArgumentCompiler.lean | 230 | Compiler only produces valid arguments | `lake build JurisLean.ArgumentCompiler` |
| 10 | `compileArguments_complete` | ArgumentCompiler.lean | 230 | Compiler produces all valid arguments | same |
| 11 | `compileAttacks_sound` | AttackDecision.lean | 240 | Attack compiler sound | `lake build JurisLean.AttackDecision` |
| 12 | `compileAttacks_complete` | AttackDecision.lean | 240 | Attack compiler complete | same |
| 13 | `compileAttacks_exact` | AttackDecision.lean | 240 | Attack compiler exact characterization | same |
| 14 | `decision_status_mutually_exclusive` | AttackDecision.lean | 240 | No argument is both PROVED and REFUTED | same |
| 15 | `decision_status_coverage` | AttackDecision.lean | 240 | Every argument gets a status | same |
| 16 | `tainted_fail_closed` | AttackDecision.lean | 240 | TAINTED status unreachable for args in framework | same |
| 17 | `check_sound` | CertificateChecker.lean | 250 | Checker acceptance implies correctness | `lake build JurisLean.CertificateChecker` |
| 18 | `certificate_verifies` | CertificateChecker.lean | 250 | Checker produces verified certificate | same |
| 19 | `certified_end_to_end_refinement` | EndToEnd.lean | 280 | Full pipeline: check → decision + safety conjuncts | `lake build JurisLean.EndToEnd` |

**Build command (all blocking)**:
```bash
cd legal-math-modeling/proofs/lean/juris_lean
lake build JurisLean.HornFixedPoint JurisLean.HornCanonical \
           JurisLean.ArgumentCompiler JurisLean.AttackDecision \
           JurisLean.CertificateChecker JurisLean.SafetyTheorems \
           JurisLean.EndToEnd JurisLean.DDLDefinitions
```

**Forbidden claims**: These theorems do NOT prove runtime correctness, do NOT verify safety predicates (they are caller hypotheses in theorem 19), do NOT eliminate all `sorry` from the repo.

### 1.2 Supporting Theorems (5)

Non-blocking, fully proven, 0 sorry.

| # | Theorem | File | SPEC | Scope |
|---|---------|------|------|-------|
| 20 | `provenance_sound` | SafetyTheorems.lean | 270 | Accepted args have non-empty provenance |
| 21 | `temporal_safe` | SafetyTheorems.lean | 270 | Temporal records have start ≤ end |
| 22 | `jurisdiction_safe` | SafetyTheorems.lean | 270 | Jurisdiction records map to target |
| 23 | `accepted_in_grounded` | EndToEnd.lean | 280 | Check-proved args are in grounded extension |
| 24 | `burden_unsatisfied_blocks_defense` | DDLDefinitions.lean | 220 | Unsatisfied burden blocks defense |

### 1.3 Deferred (Domain Axioms) — 3 sorry

| # | Theorem | File | SPEC | Sorry Reason | Plan |
|---|---------|------|------|-------------|------|
| 25 | `violation_implies_norm_active` | DDLDefinitions.lean | 220 | Rule→Norm mapping not in model | Domain axiom |
| 26 | `permission_no_direct_violation` | DDLDefinitions.lean | 220 | RuleId≠NormId structural gap | Domain axiom |
| 27 | `constitutive_no_direct_violation` | DDLDefinitions.lean | 220 | Same structural gap | Domain axiom |

### 1.4 Additional Theorems (64)

These exist in the codebase, are fully proven (0 sorry), but are not on the blocking chain. Grouped by subsystem.

**HornFixedPoint.lean** (7 additional):
`horn_operator_subset_univ`, `horn_operator_monotone`, `horn_iteration_monotone`, `horn_finite_termination`, `horn_iteration_bound`, `horn_result_least_fixed_point`, `horn_soundness`

**HornCanonical.lean** (3 additional):
`derives_sound`, `derives_complete`, `hornClosure_least`

**HornDefinitions.lean** (2):
`TH_monotone`, `TH_subset_univ`

**DungFixedPoint.lean** (16):
`F_monotone`, `iteration_monotone`, `finite_termination`, `iteration_bound`, `groundedSpec_is_fixed_point`, `grounded_is_fixed_point`, `groundedSpec_is_least_fixed_point`, `grounded_is_least_fixed_point`, `grounded_is_least_complete`, `groundedSpec_unique_least_fixed_point`, `labelling_partition`, `in_soundness`, `out_soundness`, `undecided_characterization`, `self_attack_precise_theorem`, `self_attack_not_in_grounded`

**EndToEnd.lean** (5 additional):
`check_proved_accepted_in_grounded`, `check_proved_accepted_in_args`, `cert_provenance_from_check`, `cert_temporal_from_record`, `cert_jurisdiction_from_record`

**DDLDefinitions.lean** (3 additional):
`ordered_next_requires_prior_failure`, `alternative_imposes_no_order`, `court_selected_not_auto_chosen`

**FiniteMonotoneIteration.lean** (9):
`iter_succ`, `iter_subset_univ`, `iter_mono`, `iter_stable`, `iter_ssubset_of_ne`, `iter_card_lt_of_ne`, `iter_card_le_univ`, `exists_fixpoint_le_card`, `fixed_at_card`

**FiniteRosetta.lean** (9):
`cnOnly_eq_30`, `collision_eq_4`, `asymmetry_eq_3`, `obstruction_eq_37`, `cnOnly_exceeds_half`, `obstruction_exceeds_half`, `no_total_functor`, `obstruction_density_gt_two_thirds`, `pure_obstruction_majority`

**JC_Formalization.lean** (6):
`proved_theorems_card`, `empirical_proxy_card`, `refuted_theorems_card`, `pending_theorems_card`, `advance_preserves_domain_bound`, `advance_cannot_revive_refuted`

**Banach Track** (7):
`weightedMetricSpace_dist`, `weighted_contraction_bound`, `weighted_contraction_bound_nnreal`, `pricingFn_contraction`, `pricingFn_fixed_point`, `pricingFn_unique_fixed_point`, `weightedContractionData_of_coupling`

**Other** (5):
`lipschitz_coupling_implies_weighted_contraction` (ContractionCondition.lean), `galois_connection_of_residuated` (FiniteGaloisAdjunction.lean), `temporal_guard_always`, `litigation_always_guard` (TemporalKripke.lean), `weightedSupDist_complete` (WeightedSupNorm.lean)

**UnifiedModel.lean** (11) — **NOT on main proof chain** (import conflict with LegalSyntax):
`horn_step_mono`, `unattacked_in_ge`, `unattacked_in_lfp`, `banach_bounded`, `soundness_aaf`, `soundness_banach`, `gc2_completeness`, `unified_composition_v2`, `full_chain`, `horn_monotone`, `banach_bound_uniform`

**WeightedSupNorm.lean** (3 additional):
`weightedSupDist_nonneg`, `weightedSupDist_triangle`, `weightedSupDist_symm`

### 1.5 Lean Summary

| Category | Count | Sorry | Custom Axiom |
|----------|-------|-------|--------------|
| Blocking | 19 | 0 | 0 |
| Supporting | 5 | 0 | 0 |
| Deferred | 3 | 3 | 0 |
| Additional | 83 | 0 | 0 |
| **Total** | **110** | **3** | **0** |

### 1.6 Axiom Audit

**Command**: `lake build +JurisLean.AxiomAudit`
**Result**: Only `propext`, `Classical.choice`, `Quot.sound` — standard Lean 4 / Mathlib. Zero custom axioms.

---

## 2. Python Executable Spec Tests (S)

### 2.1 juris-calculus / tests/spec/ (132 tests, 11 files)

These mirror the Lean blocking-path theorems as executable Python specs.

| File | Tests | Mirrors Lean Theorem(s) | Trust |
|------|-------|------------------------|-------|
| `test_horn_differential.py` | 8 | horn_result_fixed_point, hornClosure_*, horn_semantic_equivalence | S |
| `test_argument_compiler.py` | 5 | compileArguments_sound, compileArguments_complete | S |
| `test_attack_compiler.py` | 8 | compileAttacks_sound, compileAttacks_complete, compileAttacks_exact | S |
| `test_decision_projection.py` | 12 | decision_status_mutually_exclusive, decision_status_coverage, tainted_fail_closed | S |
| `test_certificate_checker.py` | 21 | check_sound, certificate_verifies | S |
| `test_certificate_mutations.py` | 14 | Fail-closed behavior on cert corruption | S |
| `test_safety_theorems.py` | 12 | provenance_sound, temporal_safe, jurisdiction_safe | S |
| `test_end_to_end.py` | 15 | certified_end_to_end_refinement | S |
| `test_jc_runtime_refinement.py` | 14 | Full runtime pipeline | S |
| `test_canonical_schema.py` | 14 | Schema round-trip (SPEC-200) | S |
| `test_ddl_evaluator.py` | 9 | DDL evaluation (SPEC-220) | S |

**Critical distinction**: These are **empirical tests**, not formal proofs. They verify behavior on specific inputs, not universal quantification. A test passing ≠ a theorem proven.

### 2.2 juris-calculus / tests/ top-level (85 tests)

| File | Tests | Category | Trust |
|------|-------|----------|-------|
| `test_argumentation_b6.py` | 8 | AAF edge cases | E |
| `test_canonical_serialization.py` | 8 | Serialization round-trip | E |
| `test_composition_safety.py` | 9 | Safety composition | E |
| `test_conflict_case.py` | 1 | Conflict resolution | E |
| `test_grounded_g9a.py` | 20 | Grounded extension validation | E |
| `test_horn_completeness.py` | 9 | Horn completeness empirical | E |
| `test_incremental_grounded.py` | 5 | Incremental grounded | E |
| `test_independent_checker.py` | 11 | Checker independence | E |
| `test_litigation_engineering.py` | 10 | Litigation scenarios | E |
| `test_mcp_smoke.py` | 4 | MCP interface smoke | E |

### 2.3 juris-calculus / tests/unit/ (234 tests)

Pre-existing unit tests for production runtime. Not aligned to SPEC chain. Trust: E.

### 2.4 deli-autoresearch / tests/ (127 tests)

| File | Tests | Category | Trust |
|------|-------|----------|-------|
| `test_cross_repo.py` | 25 | Cross-repo integration | E |
| `test_legal_proof.py` | 25 | Legal proof scenarios | E |
| `test_p0_acceptance.py` | 15 | P0 acceptance gates | E |
| `test_scoring.py` | 12 | Breakthrough scoring | E |
| `test_framework.py` | 13 | Framework validation | E |
| `test_priority_queue.py` | 11 | Priority queue | E |
| `test_certificate_refinance.py` | 8 | Certificate refinance | E |
| `test_p0_1_multiprocess.py` | 7 | Multiprocess | E |
| `test_batch_litigation.py` | 2 | Batch litigation | E |
| `tests/demo/test_classifier.py` | 9 | Classifier demo | E |

### 2.5 Test Summary

| Suite | Files | Tests | Trust |
|-------|-------|-------|-------|
| juris-calculus/spec | 11 | 132 | S |
| juris-calculus/top-level | 10 | 85 | E |
| juris-calculus/unit | 40 | 234 | E |
| deli-autoresearch | 10 | 127 | E |
| **Total** | **71** | **578** | mixed |

---

## 3. Gate Scripts (G)

| Script | Location | Purpose | Trust |
|--------|----------|---------|-------|
| `sorry-gate.py` | deli-autoresearch/scripts/ | Enforces SORRY_LEDGER: blocking=0 sorry, non-blocking registered | G |
| `lake build` | Lean toolchain | Type-checks all theorems | G |
| `lake build +JurisLean.AxiomAudit` | Lean toolchain | Checks for custom axioms | G |
| `pytest` | Python | Runs test suites | G |

### Checker Independence

`juris-calculus/compiler_core/certificate_checker.py` does NOT import from `evaluator.py`. Verified: `grep evaluator` returns only a comment line. This enforces the rule: "Do not let certificate checkers call the production evaluator."

---

## 4. Release Evidence (R)

### SPEC-290 Evidence Files

| File | Purpose | Trust |
|------|---------|-------|
| `theorem-manifest.md` | Full theorem listing with names, files, status | R |
| `axiom-report.md` | Actual `lake build +JurisLean.AxiomAudit` output | R |
| `release-boundary-report.md` | Formal release boundary: what's proven, what's not | R |
| `runtime-conformance-report.md` | Python test results, SPEC coverage | R |
| `red-team-verdict.json` | Structured Red Team output | R |
| `audit-report.md` | Full audit report with GPT review response | R |
| `allowed-claims.md` | What can be claimed about this release | R |
| `forbidden-claims.md` | What must NOT be claimed | R |

### SPEC-100 Evidence Files

| File | Purpose |
|------|---------|
| `baselines.json` | Cross-repo HEAD baselines (updated by P0-G01) |
| `formal-inventory.json` | Lean file inventory |
| `jc-inventory.json` | JC runtime file inventory |
| `license-scan.json` | License compliance scan |
| `coverage-validation.json` | Coverage validation |
| `red-team-verdict.json` | SPEC-100 Red Team |

### Per-SPEC Evidence (SPEC-200 through SPEC-280)

Each has: `status.json`, `red-team-verdict.json`, and most have `acceptance.json`.
SPEC-240 through SPEC-280 are missing `acceptance.json` in evidence/ (gap noted).

---

## 5. SORRY Ledger (D + G)

**File**: `legal-math-modeling/SORRY_LEDGER.md`
**Gate**: `python sorry-gate.py --ledger SORRY_LEDGER.md --strict-for blocking`

| Entry | File | Status | Type |
|-------|------|--------|------|
| `violation_implies_norm_active` | DDLDefinitions.lean | CLOSED (deferred) | D |
| `permission_no_direct_violation` | DDLDefinitions.lean | CLOSED (deferred) | D |
| `constitutive_no_direct_violation` | DDLDefinitions.lean | CLOSED (deferred) | D |
| `burden_unsatisfied_blocks_defense` | DDLDefinitions.lean | CLOSED (proven) | F |
| `provenance_sound` | SafetyTheorems.lean | CLOSED (proven) | F |

**Net**: 0 OPEN. 3 sorry remain as domain axioms (deferred). 2 were proven and closed.

---

## 6. Cross-Reference: SPEC → Asset Map

| SPEC | Lean Theorems (blocking) | Lean Theorems (other) | Spec Tests | Evidence |
|------|--------------------------|----------------------|------------|----------|
| 200 | 0 | 0 (types only) | 14 | acceptance.json, red-team |
| 210 | 8 | 18 | 8 | acceptance.json, red-team |
| 220 | 0 | 10 (3 sorry) | 9 | acceptance.json, red-team |
| 230 | 2 | 0 | 5 | acceptance.json, red-team |
| 240 | 6 | 0 | 20 | red-team |
| 250 | 2 | 0 | 35 | red-team |
| 260 | 0 | 0 | 14 | red-team |
| 270 | 0 | 3 | 12 | red-team |
| 280 | 1 | 6 | 15 | red-team |
| 290 | 0 | 0 | 0 | 7 files |
| **Total** | **19** | **37+** | **132** | — |

---

## 7. Known Gaps

1. **SPEC-240 through SPEC-280 missing `acceptance.json`** in evidence/. Status = COMPLETE but acceptance evidence absent.
2. **Full `lake build JurisLean` fails** — import conflict UnifiedModel/LegalSyntax. Must use per-module builds.
3. **UnifiedModel.lean** (11 theorems) cannot be built alongside LegalSyntax.lean. These are orphaned from the main chain.
4. **3 DDL sorry** — domain axioms, not proven. Require Rule→Norm mapping not in current model.
5. **Safety conjuncts** in `certified_end_to_end_refinement` are caller hypotheses, not checker-derived conclusions.
6. **38 skipped tests** in juris-calculus — pre-existing condition-dependent tests (spacy/heavy deps).
7. **Red Team is Claude self-review** — not independent audit. Layers 2+3 depend on LLM judgment.
8. **SORRY_LEDGER `CLOSED`** entries for `burden_unsatisfied_blocks_defense` and `provenance_sound` were proven after initial tracking — these no longer have sorry in code.
9. **Branch mismatch** (corrected by P0-G01): legal-math-modeling uses `master`, not `main`.

---

## 8. Reproducibility Commands

```bash
# Lean: all blocking modules
cd legal-math-modeling/proofs/lean/juris_lean
lake build JurisLean.HornFixedPoint JurisLean.HornCanonical \
           JurisLean.ArgumentCompiler JurisLean.AttackDecision \
           JurisLean.CertificateChecker JurisLean.SafetyTheorems \
           JurisLean.EndToEnd JurisLean.DDLDefinitions

# Axiom audit
lake build +JurisLean.AxiomAudit

# Sorry gate
cd D:\Claude\deli_autoresearch_codex_implementation_playbook
python deli-autoresearch/scripts/sorry-gate.py \
  --ledger legal-math-modeling/SORRY_LEDGER.md --strict-for blocking

# Python tests
cd deli-autoresearch && pytest -q
cd juris-calculus && pytest -q
```
