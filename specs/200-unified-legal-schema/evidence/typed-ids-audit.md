# P1-G01: Typed IDs Audit — Lean LegalIds.lean

**Date**: 2026-06-27
**Playbook**: Playbook E, Section 4.3, P1-G01
**Baseline**: CROSS_REPO_LOCK.json (frozen 2026-06-27T16:00:00Z)
**Question**: Are all typed IDs defined in LegalIds.lean? Does LegalSyntax.lean use them everywhere (no bare String/Nat for ID fields)?

---

## Conclusion

**Gap found and fixed.** LegalIds.lean had 8 of 13 required ID types. 5 missing types (`DefenseId`, `PriorityId`, `ViolationId`, `ReparationId`, `DecisionId`) caused LegalSyntax.lean to use bare `String` for 5 structures and 2 cross-reference fields. All 5 types added; all bare `String` ID fields replaced; full build verified (2954 jobs, 0 new errors).

---

## 1. Before State

### 1.1 LegalIds.lean (before fix)

8 typed ID structures defined:

| # | Type | Derives | Status |
|---|------|---------|--------|
| 1 | `FactId` | DecidableEq, BEq, Repr, Inhabited | OK |
| 2 | `RuleId` | DecidableEq, BEq, Repr, Inhabited | OK |
| 3 | `NormId` | DecidableEq, BEq, Repr, Inhabited | OK |
| 4 | `ClaimId` | DecidableEq, BEq, Repr, Inhabited | OK |
| 5 | `ArgumentId` | DecidableEq, BEq, Repr, Inhabited | OK |
| 6 | `AttackId` | DecidableEq, BEq, Repr, Inhabited | OK |
| 7 | `SourceId` | DecidableEq, BEq, Repr, Inhabited | OK |
| 8 | `JurisdictionId` | DecidableEq, BEq, Repr, Inhabited | OK |

### 1.2 LegalSyntax.lean bare String usage (before fix)

| Line | Structure | Field | Type Used | Should Be |
|------|-----------|-------|-----------|-----------|
| 97 | `Defense` | `id` | `String` | `DefenseId` |
| 106 | `Priority` | `id` | `String` | `PriorityId` |
| 113 | `Violation` | `id` | `String` | `ViolationId` |
| 122 | `Reparation` | `id` | `String` | `ReparationId` |
| 124 | `Reparation` | `target_violation` | `String` | `ViolationId` |
| 125 | `Reparation` | `ordered_successors` | `List String` | `List ReparationId` |
| 148 | `Decision` | `id` | `String` | `DecisionId` |

Total bare `String` ID fields: **7** (across 5 structures)

---

## 2. Fix Applied

### 2.1 LegalIds.lean — 5 new types added

```lean
structure DefenseId   where val : String deriving DecidableEq, BEq, Repr, Inhabited
structure PriorityId  where val : String deriving DecidableEq, BEq, Repr, Inhabited
structure ViolationId where val : String deriving DecidableEq, BEq, Repr, Inhabited
structure ReparationId where val : String deriving DecidableEq, BEq, Repr, Inhabited
structure DecisionId  where val : String deriving DecidableEq, BEq, Repr, Inhabited
```

Total ID types: 8 → **13**

### 2.2 LegalSyntax.lean — 7 field type replacements

| Structure | Field | Old Type | New Type |
|-----------|-------|----------|----------|
| `Defense` | `id` | `String` | `DefenseId` |
| `Priority` | `id` | `String` | `PriorityId` |
| `Violation` | `id` | `String` | `ViolationId` |
| `Reparation` | `id` | `String` | `ReparationId` |
| `Reparation` | `target_violation` | `String` | `ViolationId` |
| `Reparation` | `ordered_successors` | `List String` | `List ReparationId` |
| `Decision` | `id` | `String` | `DecisionId` |

---

## 3. Build Verification

### 3.1 Core chain

| Module | Jobs | Result |
|--------|------|--------|
| `JurisLean.LegalIds` | 584 | OK |
| `JurisLean.LegalSyntax` | 585 | OK |
| `JurisLean.LegalModel` | 586 | OK |
| `JurisLean.LegalWellFormed` | 587 | OK |

### 3.2 Downstream proof chain

| Module | Jobs | Result | Notes |
|--------|------|--------|-------|
| `JurisLean.DDLDefinitions` | 2954 | OK | Pre-existing sorry (line 144, registered) |
| `JurisLean.ArgumentCompiler` | 2954 | OK | — |
| `JurisLean.AttackDecision` | 2954 | OK | — |
| `JurisLean.CertificateChecker` | 2954 | OK | — |
| `JurisLean.SafetyTheorems` | 2954 | OK | — |
| `JurisLean.EndToEnd` | 2954 | OK | Pre-existing unused variable warning |

**0 new errors. 0 new warnings. All pre-existing sorry/warnings unchanged.**

### 3.3 Downstream impact analysis

| File | Affected? | Reason |
|------|-----------|--------|
| `DDLDefinitions.lean` | NO | Reads `Defense`, `Violation`, `Reparation` fields; no construction |
| `ArgumentCompiler.lean` | NO | Uses `FactId`, `RuleId`, `ClaimId` (unchanged) |
| `AttackDecision.lean` | NO | Uses `Argument`, `Attack`, `DecisionStatus` (unchanged) |
| `CertificateChecker.lean` | NO | Reads `Certificate.decision.status` (unchanged) |
| `SafetyTheorems.lean` | NO | Reads `Certificate` fields (unchanged) |
| `EndToEnd.lean` | NO | Composes above modules |
| `LegalWellFormed.lean:114` | OK | `v.id = r.target_violation` — both now `ViolationId` |
| `LegalWellFormed.lean:116` | OK | `r.ordered_successors.length` — `List.length` works on any `List α` |

No downstream proof files construct `Defense`, `Priority`, `Violation`, `Reparation`, or `Decision` directly. All access is via `LegalModel` field reads, which are type-safe.

---

## 4. Remaining Issues (Out of P1-G01 Scope)

### 4.1 Category 2: Standalone formalizations with bare Nat

`UnifiedModel.lean` and `TemporalKripke.lean` use bare `Nat` for all identifiers and do not import `LegalIds` or `LegalSyntax`. These are standalone formal exercises, not part of the canonical pipeline.

**Tracked under**: P1-G03 (WellFormed model scope) or future work.

### 4.2 Category 3: DungDefinitions.lean bare String

`DungDefinitions.lean` defines `abbrev Arg : Type := String` and builds the entire Dung AAF framework on bare `String`. `AttackDecision.lean` and `CertificateChecker.lean` bridge via `.val` extraction.

**Tracked under**: Future refactoring (Dung AAF is independently proven, bridge is deliberate).

### 4.3 Python canonical_schema.py alignment

The Python canonical schema (`canonical_schema.py`) also uses bare `str` for all ID fields. Python does not have the same type-safety concern, but naming alignment with Lean should be verified in P1-G04.

---

## 5. Verdict

| Criterion | Result |
|-----------|--------|
| Playbook required IDs present (FactId/RuleId/NormId/ClaimId/ArgumentId/AttackId) | **PASS** — all 6 present |
| No bare `String` in LegalSyntax.lean ID fields | **PASS** — 7 fields fixed |
| No bare `String` cross-references in LegalSyntax.lean | **PASS** — `Reparation.target_violation` and `ordered_successors` fixed |
| LegalIds.lean builds independently | **PASS** — 584 jobs |
| LegalSyntax.lean builds with new IDs | **PASS** — 585 jobs |
| Full downstream proof chain builds | **PASS** — 2954 jobs, 0 new errors |
| No new sorry/admit introduced | **PASS** |
| P1-G02 not started | **PASS** |
