# SPEC-270 Requirements

## Goal

Prove provenance, temporal, and jurisdiction safety properties for the legal reasoning pipeline.

## Requirements

1. **R1 — ProvenanceSound**: Every accepted argument in a certificate has a provenance entry with non-empty sources.
2. **R2 — TemporalSafe**: Every entry in the temporal record has a valid (non-degenerate) interval.
3. **R3 — JurisdictionSafe**: Every entry in the jurisdiction record maps to the target jurisdiction.
4. **R4 — AllSafe**: Combined predicate: ProvenanceSound ∧ TemporalSafe ∧ JurisdictionSafe.

## Blocking status

All three theorems are **non-blocking**. Sorry is allowed if registered in SORRY_LEDGER.md.

## Non-goals

- End-to-end composition (deferred to SPEC-280).
- Cross-jurisdiction mapping spec (requires human decision).
