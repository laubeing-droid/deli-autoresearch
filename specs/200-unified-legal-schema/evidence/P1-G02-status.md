# P1-G02 Status — Define Canonical Legal Syntax

**Date**: 2026-06-27
**Playbook**: Playbook E, Section 4.3, P1-G02
**Baseline**: CROSS_REPO_LOCK.json (frozen 2026-06-27T16:00:00Z)

---

## Goal

Verify that `LegalSyntax.lean` defines `DecisionStatus` and all rule / norm / claim / provenance / certificate structures matching the canonical schema.

## Products

| Product | Path | Status |
|---------|------|--------|
| Syntax alignment audit | `specs/200-unified-legal-schema/evidence/syntax-alignment-audit.md` | CREATED |
| This status report | `specs/200-unified-legal-schema/evidence/P1-G02-status.md` | CREATED |

---

## Verdict

**No changes needed.** Lean `LegalSyntax.lean` and Python `canonical_schema.py` are fully aligned. 5 enums and 12 model types match across 66 fields.

---

## Audit Summary

| Category | Count | All Match? |
|----------|-------|-----------|
| Enums (Modality, AttackKind, ReparationMode, DefenseKind, DecisionStatus) | 5 | YES |
| Core types (LegalFact, LegalClaim, LegalRule, LegalNorm) | 4 | YES |
| Support types (Defense, Priority, Violation, Reparation) | 4 | YES |
| Argumentation types (Argument, Attack, Decision) | 3 | YES |
| Certificate (with provenance, temporal, jurisdiction records) | 1 | YES |
| **Total fields checked** | **66** | **66/66** |

---

## DecisionStatus (Playbook Checklist Item)

```
Lean:   PROVED | REFUTED | UNDECIDED | TAINTED
Python: PROVED | REFUTED | UNDECIDED | TAINTED
```

4/4 values match. Used by `AttackDecision.lean` (decisionProjection) and `CertificateChecker.lean` (check).

---

## Design Differences (Not Gaps)

| Aspect | Lean | Python |
|--------|------|--------|
| ID types | Opaque structures (FactId, RuleId, ...) | Bare str |
| Provenance entries | Anonymous tuples | Named types (SourceRef, TemporalEntry, JurisdictionEntry) |
| TimeInterval validation | Nat (≥0 by construction) | Pydantic `Field(ge=0)` |

These are language-level differences, not schema misalignment. P1-G05 (JC adapters) will bridge the Python side.

---

## Acceptance Criteria

| Criterion | Status |
|-----------|--------|
| DecisionStatus defined | PASS |
| rule/norm/claim/provenance/certificate structures match | PASS |
| No fields missing in Lean | PASS |
| No fields missing in Python | PASS |
| No P1-G03 work started | PASS |

---

## Allowed Modifications

| File | Operation |
|------|-----------|
| `deli-autoresearch/specs/200-unified-legal-schema/evidence/syntax-alignment-audit.md` | New |
| `deli-autoresearch/specs/200-unified-legal-schema/evidence/P1-G02-status.md` | New |

No Lean files modified. No Python files modified. No P1-G03 work started.
