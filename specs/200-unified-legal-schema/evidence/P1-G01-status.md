# P1-G01 Status — Introduce Typed IDs in Lean

**Date**: 2026-06-27
**Playbook**: Playbook E, Section 4.3, P1-G01
**Baseline**: CROSS_REPO_LOCK.json (frozen 2026-06-27T16:00:00Z)

---

## Goal

Verify that `LegalIds.lean` defines all required typed IDs and that `LegalSyntax.lean` uses them everywhere (no bare `String`/`Nat` mixing).

## Products

| Product | Path | Status |
|---------|------|--------|
| Typed IDs audit report | `specs/200-unified-legal-schema/evidence/typed-ids-audit.md` | CREATED |
| This status report | `specs/200-unified-legal-schema/evidence/P1-G01-status.md` | CREATED |

---

## Verdict

**Gap found and fixed.** 5 missing ID types added to `LegalIds.lean`; 7 bare `String` fields in `LegalSyntax.lean` replaced with typed IDs. Full downstream proof chain builds successfully (2954 jobs, 0 new errors).

---

## Changes Made

### Files Modified

| File | Repo | Change |
|------|------|--------|
| `proofs/lean/juris_lean/JurisLean/LegalIds.lean` | legal-math-modeling | Added 5 ID types: DefenseId, PriorityId, ViolationId, ReparationId, DecisionId |
| `proofs/lean/juris_lean/JurisLean/LegalSyntax.lean` | legal-math-modeling | Replaced 7 bare `String` fields with typed IDs |

### Summary

| Metric | Before | After |
|--------|--------|-------|
| ID types in LegalIds.lean | 8 | 13 |
| Bare String ID fields in LegalSyntax.lean | 7 | 0 |
| Bare String cross-references | 2 (Reparation) | 0 |
| Build errors (new) | — | 0 |
| Build warnings (new) | — | 0 |

---

## Build Evidence

```
$ lake build JurisLean.LegalIds JurisLean.LegalSyntax JurisLean.LegalModel JurisLean.LegalWellFormed
Build completed successfully (587 jobs).

$ lake build JurisLean.DDLDefinitions JurisLean.ArgumentCompiler JurisLean.AttackDecision JurisLean.CertificateChecker JurisLean.SafetyTheorems JurisLean.EndToEnd
Build completed successfully (2954 jobs).
```

All 10 modules build. Pre-existing warnings only (sorry in DDLDefinitions, deprecated push_neg, unused variable in EndToEnd).

---

## Acceptance Criteria

| Criterion | Status |
|-----------|--------|
| `FactId` / `RuleId` / `NormId` / `ClaimId` / `ArgumentId` / `AttackId` present | PASS |
| No bare `String` / `Nat` mixing in LegalSyntax.lean ID fields | PASS |
| `LegalIds.lean` builds independently | PASS |
| Full downstream proof chain builds | PASS |
| No new sorry/admit introduced | PASS |
| No P1-G02 work started | PASS |

---

## Remaining Issues (Out of Scope)

| Issue | Severity | Tracked Under |
|-------|----------|---------------|
| `UnifiedModel.lean` / `TemporalKripke.lean` use bare Nat | Low | Standalone formalization, not canonical pipeline |
| `DungDefinitions.lean` uses bare String (`Arg`) | Low | Independent AAF framework, bridge is deliberate |
| Python `canonical_schema.py` uses bare str for IDs | Low | P1-G04 (Python schema alignment) |

---

## Allowed Modifications

| File | Operation |
|------|-----------|
| `legal-math-modeling/proofs/lean/juris_lean/JurisLean/LegalIds.lean` | Modified |
| `legal-math-modeling/proofs/lean/juris_lean/JurisLean/LegalSyntax.lean` | Modified |
| `deli-autoresearch/specs/200-unified-legal-schema/evidence/typed-ids-audit.md` | New |
| `deli-autoresearch/specs/200-unified-legal-schema/evidence/P1-G01-status.md` | New |

No other files modified. No P1-G02 work started.
