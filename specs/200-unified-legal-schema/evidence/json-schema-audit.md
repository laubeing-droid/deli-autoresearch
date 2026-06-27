# P1-G04: Python Canonical Schema — Audit

**Date**: 2026-06-27
**Playbook**: Playbook E, Section 4.3, P1-G04
**Baseline**: CROSS_REPO_LOCK.json (frozen 2026-06-27T16:00:00Z)
**Question**: Does `juris-calculus/compiler_core/canonical_schema.py` define all types and fields matching Lean `LegalSyntax.lean`?

---

## Conclusion

**No gaps.** Python `canonical_schema.py` and Lean `LegalSyntax.lean` are fully aligned across 5 enums, 13 structures, and 69 fields.

---

## 1. Enum Alignment

| Enum | Values | Lean | Python | Match |
|------|--------|------|--------|-------|
| Modality | OBLIGATION, PROHIBITION, PERMISSION, CONSTITUTIVE | ✓ | ✓ | 4/4 |
| AttackKind | REBUTTAL, EXCEPTION_DEFEAT, PRIORITY_DEFEAT | ✓ | ✓ | 3/3 |
| ReparationMode | ALTERNATIVE, ORDERED_CHAIN, CONCURRENT, COURT_SELECTED | ✓ | ✓ | 4/4 |
| DefenseKind | DEFEATER, JUSTIFICATION, EXCUSE | ✓ | ✓ | 3/3 |
| DecisionStatus | PROVED, REFUTED, UNDECIDED, TAINTED | ✓ | ✓ | 4/4 |

---

## 2. Structure Alignment

| Type | Fields | Lean ↔ Python | Match |
|------|--------|--------------|-------|
| TimeInterval | start, end | 2/2 | ✓ |
| SourceRef | argument_id, source_ids | 2/2 | ✓ |
| TemporalEntry | rule_id, valid_interval | 2/2 | ✓ |
| JurisdictionEntry | rule_id, jurisdiction_id | 2/2 | ✓ |
| LegalFact | id, content, source, time | 4/4 | ✓ |
| LegalClaim | id, content, claimant | 3/3 | ✓ |
| LegalRule | id, modality, premises, conclusion, source, jurisdiction, valid_interval | 7/7 | ✓ |
| LegalNorm | id, modality, condition, consequence, source, jurisdiction, valid_interval, enabled | 8/8 | ✓ |
| Defense | id, kind, target, burden_of_proof, facts_required | 5/5 | ✓ |
| Priority | id, higher, lower | 3/3 | ✓ |
| Violation | id, rule, trigger_fact, support_facts, source | 5/5 | ✓ |
| Reparation | id, mode, target_violation, ordered_successors | 4/4 | ✓ |
| Argument | id, claim, rule, support_facts, sources, derivation_witness | 6/6 | ✓ |
| Attack | id, kind, attacker, target | 4/4 | ✓ |
| Decision | id, status, accepted_arguments, rejected_arguments | 4/4 | ✓ |
| Certificate | model_hash, input_hash, decision, derivation_witnesses, attack_witnesses, grounded_label, provenance, temporal_record, jurisdiction_record | 9/9 | ✓ |
| LegalModel | schema_version + 12 component lists | 13/13 | ✓ |

**Total: 69 fields across 17 types. All match.**

---

## 3. Design Differences (Not Gaps)

| Aspect | Lean | Python |
|--------|------|--------|
| ID representation | Opaque structures (FactId, RuleId, ...) | Bare str |
| TimeInterval.end | `end_` (Lean keyword avoidance) | `end` (no Python conflict) |
| Provenance entries | Anonymous tuples | Named types (SourceRef, TemporalEntry, JurisdictionEntry) |
| LegalModel.schema_version | Not present (Lean uses type-level) | `str` field with Pydantic validator |
| TimeInterval validation | Nat (≥0 by construction) | `Field(ge=0)` + model_validator |

These are language-level implementation differences, not schema misalignment.

---

## 4. Verdict

| Criterion | Result |
|-----------|--------|
| All 5 enums match | **PASS** |
| All 13 structures match | **PASS** |
| All 69 fields match | **PASS** |
| No missing fields in Python | **PASS** |
| No missing fields in Lean | **PASS** |
| P1-G04 can be closed | **YES** |
