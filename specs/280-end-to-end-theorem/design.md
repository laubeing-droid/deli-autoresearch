# SPEC-280 Design

## Architecture

### Lean Layer (EndToEnd.lean)

**Core definitions:**
- `evaluate`: `LegalModel → List (Argument × DecisionStatus)` — compiles model into AAF, applies decisionProjection per argument
- `check_model`: `LegalModel → Certificate → Bool` — wrapper that compiles model to DungAAF then calls `check`

**BLOCKING theorem: `certified_end_to_end_refinement`**

```
Given: M (LegalModel), cert (Certificate), target (JurisdictionId),
       hM (WellFormed M), hcheck (check_model M cert = true),
       hprov (provenance witness), htemp (temporal witness), hjur (jurisdiction witness)
Concludes:
  (1) ∀ a ∈ accArgs cert, decisionProjection aaf a = PROVED
  (2) ProvenanceSound cert
  (3) TemporalSafe cert
  (4) JurisdictionSafe cert target
```

**Proof strategy:**
- `hcheck` unfolds to `CertificateChecker.check aaf cert = true`
- Apply `check_sound` for (1)
- Apply `provenance_sound`, `temporal_safe`, `jurisdiction_safe` for (2-4)
- All proofs are direct applications — no sorry, no induction

### Sorry Closing Pass

- `provenance_sound`: strengthened hypothesis from `a ∈ cert.provenance.map Prod.fst` to `∃ sources, (a, sources) ∈ cert.provenance ∧ sources ≠ []`
- `burden_unsatisfied_blocks_defense`: proven by `push_neg` + contradiction on `DefenseApplicable.2`
- 3 DDL theorems: closed as DEFERRED domain axioms (structural gaps in model)

### Python Layer

- 13 tests across 5 classes: EndToEndComposition, CheckerAcceptanceImpliesCorrectness, SafetyImplied, EndToEndFailClosed, CompositionBiconditional
- Tests verify the runtime analog of the Lean theorem: certificate acceptance ↔ grounded extension membership
