# SPEC-270 Design

## Architecture

### Lean Layer (SafetyTheorems.lean)

Defines three safety predicates as Props over `Certificate`:

1. **ProvenanceSound**: `∀ aid ∈ cert.decision.accepted_arguments, ∃ sources, (aid, sources) ∈ cert.provenance ∧ sources ≠ []`
2. **TemporalSafe**: `∀ entry ∈ cert.temporal_record, entry.2.start ≤ entry.2.end_`
3. **JurisdictionSafe**: `∀ entry ∈ cert.jurisdiction_record, entry.2 = target`
4. **AllSafe**: Conjunction of all three

### Proof Strategy

- `provenance_sound`: rw + rcases on List.mem_map, 1 sorry for `sources ≠ []` (requires model-level source validation)
- `temporal_safe`: Direct from hypothesis (interval well-formedness is decidable)
- `jurisdiction_safe`: Direct from hypothesis (jurisdiction equality is decidable)

### Python Layer

- 10 tests across 4 classes: ProvenanceSafety, TemporalSafety, JurisdictionSafety, FailClosedSafety
- Uses existing certificate types: HornCertificate, GroundedINCertificate, OUTCertificate, UNDECCertificate
- Fail-closed tests verify tampered/wrong certificates are rejected

## Key Design Decision

Safety predicates are defined on the `Certificate` type which already contains `provenance`, `temporal_record`, and `jurisdiction_record` fields. This avoids needing to pass the `LegalModel` into the safety predicates — the certificate is the witness of safety.
