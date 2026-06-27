# SPEC-210 Tasks

## Formal (Lean)

- [x] TASK-210-001: Audit current Horn definitions in FiniteMonotoneIteration / HornDefinitions / HornFixedPoint
- [x] TASK-210-002: Record theorem-strength gaps (8 blocking theorems identified)
- [x] TASK-210-003: Define or reuse HornRule (reuse existing)
- [x] TASK-210-004: Define hornStep (TH reuse, hornStep_monotone canonical name)
- [x] TASK-210-005: Prove hornStep monotone (BLOCKING)
- [x] TASK-210-006: Define finite hornClosure (reuse iter + card univ)
- [x] TASK-210-007: Prove closure extensive (BLOCKING)
- [x] TASK-210-008: Prove closure closed (BLOCKING)
- [x] TASK-210-009: Prove closure idempotent (BLOCKING)
- [x] TASK-210-010: Define inductive Derives (BLOCKING, NOT closure membership)
- [x] TASK-210-011: Prove initial derivations sound
- [x] TASK-210-012: Prove rule application sound
- [x] TASK-210-013: Compose derives_sound (BLOCKING)
- [x] TASK-210-014: Prove step membership has derivation
- [x] TASK-210-015: Prove iteration membership has derivation
- [x] TASK-210-016: Prove derives_complete (BLOCKING)
- [x] TASK-210-017: Define ClosedUnder (via hornClosure_least)
- [x] TASK-210-018: Prove hornClosure_least (BLOCKING)
- [x] TASK-210-019: Define Horn model satisfaction (via horn_semantic_equivalence)
- [x] TASK-210-020: Prove model-theoretic equivalence (BLOCKING, horn_semantic_equivalence)

## Runtime (JC)

- [x] TASK-210-021: Add JC monotonicity counterexample test
- [x] TASK-210-022: Remove exception effect from Horn stage
- [x] TASK-210-023: Remove rebuttal effect from Horn stage
- [x] TASK-210-024: Remove priority effect from Horn stage
- [x] TASK-210-025: Add single-step differential
- [x] TASK-210-026: Add closure differential

## Red-Team

- [x] TASK-210-027: Red-team theorem strength (CI sorry=0, axiom=0)
- [x] TASK-210-028: Red-team runtime monotonicity
