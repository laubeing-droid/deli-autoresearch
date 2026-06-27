# P0-G02 Status — Build Theorem/Evidence Ledger

**Date**: 2026-06-27
**Playbook**: Playbook E, Section 3.3, P0-G02
**Baseline**: CROSS_REPO_LOCK.json (frozen 2026-06-27T16:00:00Z)

---

## Goal

Build a unified asset ledger of every theorem, script, test, certificate, and audit artifact across the three repos. Classify each by trust boundary (Formal / Empirical Spec / Empirical / Gate / Domain Axiom / Release Evidence).

## Products

| Product | Path | Status |
|---------|------|--------|
| Unified asset ledger | `docs/execution/THEOREM_OBLIGATIONS.md` | CREATED |
| This status report | `specs/100-jc-public-baseline/evidence/P0-G02-status.md` | CREATED |

## Input Scan Summary

### Lean Formal Theorems

| Metric | Value |
|--------|-------|
| Total .lean files in JurisLean/ | 36 |
| Files with theorems | 22 |
| Total theorem declarations | 110 |
| Blocking-path (0 sorry, 0 axiom) | 19 |
| Supporting (0 sorry) | 5 |
| Deferred (3 sorry, domain axioms) | 3 |
| Additional (0 sorry) | 83 |
| Custom axioms | 0 |
| Standard axioms only | propext, Classical.choice, Quot.sound |

### Python Tests

| Suite | Files | Tests | Passing | Skipped | Failed |
|-------|-------|-------|---------|---------|--------|
| juris-calculus/spec | 11 | 132 | 132 | 0 | 0 |
| juris-calculus/top-level | 10 | 85 | 85 | 0 | 0 |
| juris-calculus/unit | 40 | 234 | 234 | 38 | 0 |
| deli-autoresearch | 10 | 127 | 127 | 0 | 0 |
| **Total** | **71** | **578** | **578** | **38** | **0** |

Note: 38 skipped tests are in juris-calculus unit tests (require spacy/heavy deps), not in spec tests.

### Evidence Files

| SPEC | Evidence Files | Notes |
|------|---------------|-------|
| 100 | 22 (incl. baselines, inventories, classifications, reports) | Richest evidence |
| 200 | 2 (acceptance.json, red-team-verdict.json) | |
| 210 | 2 | |
| 220 | 2 | |
| 230 | 2 | |
| 240 | 1 (red-team only) | **Missing acceptance.json** |
| 250 | 1 | **Missing acceptance.json** |
| 260 | 1 | **Missing acceptance.json** |
| 270 | 1 | **Missing acceptance.json** |
| 280 | 1 | **Missing acceptance.json** |
| 290 | 7 (release boundary, axiom audit, manifest, claims, audit) | |

### SORRY_LEDGER

| Metric | Value |
|--------|-------|
| OPEN entries | 0 |
| CLOSED entries | 5 (3 deferred domain axioms + 2 proven-and-closed) |
| Blocking-path sorry | 0 |
| Gate status | PASS |

### Checker Independence

| Check | Result |
|-------|--------|
| `certificate_checker.py` imports `evaluator.py`? | **NO** (only comment found) |

---

## Gaps Found

### G1: Missing acceptance.json (SPEC-240 through SPEC-280)

**Severity**: Low
**Impact**: Status=COMPLETE without formal acceptance evidence in evidence/ dir.
**Cause**: Playbook C closed these specs via Red Team verdict only; acceptance.json not generated.
**Recommendation**: P1-P8 audit should either generate acceptance.json or document why it's unnecessary.

### G2: Full lake build fails

**Severity**: Medium
**Impact**: Cannot do single-command verification of all modules.
**Cause**: UnifiedModel.lean and LegalSyntax.lean have conflicting `decEq` instances.
**Workaround**: Per-module `lake build` works.
**Recommendation**: P9-G05 should archive UnifiedModel.lean to resolve conflict.

### G3: UnifiedModel.lean orphaned (11 theorems)

**Severity**: Low
**Impact**: 11 theorems exist but cannot be built alongside the main chain.
**Cause**: Pre-existing import conflict.
**Recommendation**: These should be explicitly excluded from blocking path.

### G4: Red Team is Claude self-review

**Severity**: Medium (structural)
**Impact**: Layers 2+3 of Red Team depend on LLM judgment, not independent audit.
**Mitigation**: Layer 1 (mechanical) is fully reproducible. GPT cross-review has been performed.
**Recommendation**: Any third-party audit should re-run Layer 1 mechanically.

### G5: SORRY_LEDGER 2 CLOSED entries are stale

**Severity**: Low
**Impact**: `burden_unsatisfied_blocks_defense` and `provenance_sound` are marked CLOSED but were subsequently proven (no sorry remains). The CLOSED status is accurate but the "sorry" framing is misleading.
**Recommendation**: Update SORRY_LEDGER to distinguish "CLOSED (was sorry, now proven)" from "CLOSED (deferred domain axiom)".

### G6: Test count discrepancies across evidence files

**Severity**: Low
**Impact**: Various evidence files report different counts (109 SPEC vs 543 full vs 578 actual).
**Cause**: Different scopes were used (SPEC-only vs full suite).
**Resolution**: THEOREM_OBLIGATIONS.md now reports all 4 tiers separately.

---

## Acceptance Criteria (from Playbook E)

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Theorem/script/test/cert/audit unified in one file | PASS | THEOREM_OBLIGATIONS.md sections 1-5 |
| Each asset classified by trust boundary | PASS | F/S/E/G/D/R legend + per-asset tags |
| Lean theorems list statement scope | PASS | Section 1, "Scope" column |
| Python tests classified separately from Lean proofs | PASS | Section 2, with explicit "test ≠ proof" note |
| SORRY_LEDGER cross-referenced | PASS | Section 5 |
| SPEC → asset map exists | PASS | Section 6 |
| Known gaps documented | PASS | Section 7 |

## What P0-G02 Does NOT Do

- Does not change any code or proof files
- Does not modify status.json for any SPEC
- Does not start P0-G03
- Does not re-run any builds or tests (data sourced from prior runs)

## Allowed Modifications

| File | Operation |
|------|-----------|
| `deli-autoresearch/docs/execution/THEOREM_OBLIGATIONS.md` | New |
| `deli-autoresearch/specs/100-jc-public-baseline/evidence/P0-G02-status.md` | New |

No P1-P9 code modified.
