# P0-G05 Status — Produce Schema Loss Report

**Date**: 2026-06-27
**Playbook**: Playbook E, Section 3.3, P0-G05
**Baseline**: CROSS_REPO_LOCK.json (frozen 2026-06-27T16:00:00Z)

---

## Goal

Analyze what the production path loses relative to the canonical schema — fields, semantics, and evidence chains.

## Products

| Product | Path | Status |
|---------|------|--------|
| Schema loss report | `specs/240-attack-grounded-decision/evidence/schema-loss-report.md` | CREATED |
| This status report | `specs/240-attack-grounded-decision/evidence/P0-G05-status.md` | CREATED |

---

## Verdict

**Severe loss.** Production retains 2 of 14 canonical types. Zero downstream types (Argument, Attack, Decision, Certificate) are produced. The canonical adapter exists but is never imported by the production pipeline.

---

## Evidence Summary

### Type Presence

| Category | Count | Detail |
|----------|-------|--------|
| Canonical types defined | 14 | LegalModel + 12 component types + 1 aggregate |
| In production types.py | 3 | LegalFact, LegalClaim, LegalRule (input only) |
| Produced by pipeline | 2 | LegalFact, LegalClaim (LegalRule is input) |
| Absent from production | 11 | LegalNorm, Defense, Priority, Violation, Reparation, Argument, Attack, Decision, Certificate, LegalModel, Supporting types |

### Field Loss

| Type | Lost Fields | Renamed Fields | Type-Mismatched Fields |
|------|------------|----------------|----------------------|
| LegalFact | `time` | `content`→`description` | — |
| LegalClaim | `claimant` | `content`→`description` | — |
| LegalRule | `source` | `premises`→`premise_atoms`, `conclusion`→`head_claim` | `modality` (enum→str), `valid_interval` (TimeInterval→2 strings) |

### Evidence Chain Loss

| Chain Component | Canonical | Production |
|----------------|-----------|------------|
| Audit Certificate | `Certificate` (9 fields) | **NONE** |
| Provenance | `SourceRef` list in Certificate | Per-fact `source_anchor` only |
| Temporal record | `TemporalEntry` list in Certificate | Per-rule `valid_from/valid_to` only |
| Jurisdiction record | `JurisdictionEntry` list in Certificate | Per-rule `jurisdiction` only |
| Attack witnesses | `Certificate.attack_witnesses` | **NONE** |
| Model/input hash | `Certificate.model_hash/input_hash` | **NONE** |

### Adapter Disconnection

| Check | Result |
|-------|--------|
| `canonical_adapter.py` exists? | YES (191 lines) |
| Imported by `evaluator.py`? | **NO** |
| Imported by `stratified_evaluator.py`? | **NO** |
| Imported by `argumentation.py`? | **NO** |
| Imported by any production file? | **NO** |

### Enum Divergence

| Enum | Canonical | Production | Divergence |
|------|-----------|------------|------------|
| Modality | 4 values | 5 values | Production adds `UNKNOWN` (not in canonical) |

---

## Acceptance Criteria

| Criterion | Status |
|-----------|--------|
| Schema loss report written | PASS |
| Field-by-field comparison complete | PASS |
| Evidence chain loss documented | PASS |
| No P0-G06 work started | PASS |

---

## Downstream Tracking

| Gap | Fix Location | Status |
|-----|-------------|--------|
| Missing 10 canonical types in production | P7-G01 (Rebuild production pipeline) | Not started |
| Canonical adapter disconnection | P7-G02 (Connect canonical adapter) | Not started |
| No audit certificate | P7-G03 (Certificate production) | Not started |
| Field name mismatches | P7-G02 (Adapter mapping) | Not started |
| Enum divergence (UNKNOWN) | P7-G02 (Modality validation) | Not started |

---

## Allowed Modifications

| File | Operation |
|------|-----------|
| `deli-autoresearch/specs/240-attack-grounded-decision/evidence/schema-loss-report.md` | New |
| `deli-autoresearch/specs/240-attack-grounded-decision/evidence/P0-G05-status.md` | New |

No code files modified. No P0-G06 work started.
