# P8-G03 — Safety Conjuncts Are Explicit Hypotheses

**Date**: 2026-06-27 | **Verdict**: PASS

Verified at EndToEnd.lean:130-143:
- `hprov : ProvenanceSafe cert.decision.accepted_arguments` — caller-provided
- `htemp : TemporalSafe cert.temporal_record` — caller-provided
- `hjur : JurisdictionSafe cert.jurisdiction_record target` — caller-provided

The theorem does NOT derive safety from the checker. This is a deliberate design choice
matching the checker's limited scope (structure validation only).
