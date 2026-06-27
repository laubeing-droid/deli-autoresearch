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

### 1.1 Core Blocking-Path Theorems (43)

These MUST build with `lake build JurisLean`, MUST have ZERO sorry, ZERO custom axiom.

All 43 theorems exist as actual `theorem`/`lemma` declarations in the Lean source files.

**FiniteMonotoneIteration.lean** (9 core):
`iter_succ`, `iter_subset_univ`, `iter_mono`, `iter_stable`, `iter_ssubset_of_ne`, `iter_card_lt_of_ne`, `iter_card_le_univ`, `exists_fixpoint_le_card`, `fixed_at_card`

**DungFixedPoint.lean** (17 core):
`F_monotone`, `iteration_monotone`, `grounded_eq_groundedSpec`, `finite_termination`, `iteration_bound`, `groundedSpec_is_fixed_point`, `grounded_is_fixed_point`, `groundedSpec_is_least_fixed_point`, `grounded_is_least_fixed_point`, `grounded_is_least_complete`, `groundedSpec_unique_least_fixed_point`, `labelling_partition`, `in_soundness`, `out_soundness`, `undecided_characterization`, `self_attack_precise_theorem`, `self_attack_not_in_grounded`

**HornFixedPoint.lean** (10 core):
`horn_operator_subset_univ`, `horn_operator_monotone`, `horn_iteration_monotone`, `horn_finite_termination`, `horn_iteration_bound`, `horn_result_fixed_point`, `horn_result_least_fixed_point`, `horn_soundness`, `horn_completeness`, `horn_result_is_minimal_model`

**WeightedSupNorm.lean** (4 core):
`weightedSupDist_nonneg`, `weightedSupDist_triangle`, `weightedSupDist_symm`, `weightedSupDist_complete`

**HornDefinitions.lean** (2 core):
`TH_monotone`, `TH_subset_univ`

**ContractionCondition.lean** (1 core):
`lipschitz_coupling_implies_weighted_contraction`

**Build command (umbrella)**:
```bash
cd legal-math-modeling/proofs/lean/juris_lean
lake build JurisLean
# 2954 jobs, 0 errors, 0 sorry
```

**Forbidden claims**: These theorems do NOT prove runtime correctness, do NOT verify safety predicates, do NOT eliminate all `sorry` from the repo.

### 1.2 Supporting Theorems (51)

Non-blocking, fully proven, 0 sorry. Includes: BanachEffectiveNodes (8), FiniteRosetta (9), FiniteGaloisAdjunction (2), TemporalKripke (6), UnifiedModel (16), JC_Formalization (6), BanachContraction (2), BanachFixedPoint (1), SupZeroLemma (1).

### 1.3 Deferred (Domain Axioms) — 3 sorry

Registered in `legal-math-modeling/SORRY_LEDGER.md`. Not yet formalized in any Lean file.

| # | Axiom | Status | Sorry Reason |
|---|-------|--------|-------------|
| 1 | `violation_implies_norm_active` | Deferred | Rule→Norm mapping not in model |
| 2 | `permission_no_direct_violation` | Deferred | RuleId≠NormId structural gap |
| 3 | `constitutive_no_direct_violation` | Deferred | Same structural gap |

### 1.4 Additional Theorems (0 beyond core+supporting)

All theorems in the codebase are already listed in 1.1 (core) and 1.2 (supporting).
The 94 unique theorems across 15 Lean files constitute the complete formal surface.

### 1.5 Lean Summary

| Category | Count | Sorry | Custom Axiom |
|----------|-------|-------|--------------|
| Core blocking | 43 | 0 | 0 |
| Supporting | 51 | 0 | 0 |
| Deferred (axioms) | 3 | 3 | 0 |
| **Total (unique)** | **94** | **0** | **0** |

### 1.6 Axiom Audit

**Command**: `lake build +JurisLean.AxiomAudit`
**Result**: Only `propext`, `Classical.choice`, `Quot.sound` — standard Lean 4 / Mathlib. Zero custom axioms.

---

## 2. Python Executable Spec Tests (S)

### 2.1 juris-calculus / tests/spec/ (132 tests, 11 files)

These mirror the Lean core theorems as executable Python specs.

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

| Entry | Status | Type |
|-------|--------|------|
| `violation_implies_norm_active` | Deferred (not yet formalized) | D |
| `permission_no_direct_violation` | Deferred (not yet formalized) | D |
| `constitutive_no_direct_violation` | Deferred (not yet formalized) | D |

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

1. **11 phantom Lean files** — designed in SPEC-200~290 but never created. Their theorems were absorbed into existing files or remain PLANNED. See theorem-manifest.md "Phantom File Clarification" for mapping.
2. **3 DDL sorry** — domain axioms registered in SORRY_LEDGER.md. Not yet formalized in any Lean file.
3. **38 skipped tests** in juris-calculus — pre-existing condition-dependent tests (spacy/heavy deps).
4. **Red Team is Claude self-review** — not independent audit. Layers 2+3 depend on LLM judgment.
5. **Branch mismatch** (corrected by P0-G01): legal-math-modeling uses `master`, not `main`.

---

## 8. Reproducibility Commands

```bash
# Lean: umbrella build (all modules, 2954 jobs, 0 errors)
cd legal-math-modeling/proofs/lean/juris_lean
lake build JurisLean

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
