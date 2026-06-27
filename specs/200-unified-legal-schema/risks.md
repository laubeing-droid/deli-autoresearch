# SPEC-200 Risks

## RISK-200-001: ID Type Explosion
8 distinct ID types may create adapter complexity.
**Mitigation**: All IDs are opaque String wrappers; adapters use a common pattern.

## RISK-200-002: LegalRule/LegalNorm Conflation
Downstream specs may accidentally use one for the other.
**Mitigation**: Distinct types prevent unification; WellFormed enforces valid references.

## RISK-200-003: WellFormed Completeness
Missing a sub-condition could allow malformed models into proof chain.
**Mitigation**: Explicit checklist in requirements; reference-existence lemmas prove each condition.

## RISK-200-004: Round-Trip Field Loss
JSON serialization may silently drop fields not in the Pydantic model.
**Mitigation**: Negative tests verify unknown fields are rejected, not ignored.
