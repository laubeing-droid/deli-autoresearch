# SPEC-270 Tasks

## T1 — Lean Safety Predicates
- [x] Define ProvenanceSound (accepted arguments have provenance entries)
- [x] Define TemporalSafe (valid intervals in temporal record)
- [x] Define JurisdictionSafe (jurisdiction record maps to target)
- [x] Define AllSafe (combined predicate)

## T2 — Lean Safety Theorems
- [x] provenance_sound (1 sorry: sources ≠ [] requires model-level check)
- [x] temporal_safe (fully proven)
- [x] jurisdiction_safe (fully proven)

## T3 — Python Safety Tests
- [x] test_safety_theorems.py: 10 tests covering provenance, temporal, jurisdiction, fail-closed

## T4 — Lifecycle Files
- [x] spec.yaml, requirements.md, tasks.md, acceptance.md, design.md, status.json
- [x] evidence/red-team-verdict.json

## T5 — SORRY_LEDGER.md
- [x] Register SORRY-002 for provenance_sound sorry
