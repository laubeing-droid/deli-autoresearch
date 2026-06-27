# SPEC-210 Design: Positive Horn Semantics

## Overview

SPEC-210 formalizes the positive Horn layer and aligns the JC runtime Stage 1
with the formal specification. The Lean module `HornCanonical.lean` proves 8
blocking theorems; the JC evaluator's `evaluate_horn()` / `_apply_rule_horn()`
are purged of exception, rebuttal, and priority effects.

## Lean Side

- Reuses `HornDefinitions`, `HornFixedPoint`, `FiniteMonotoneIteration`.
- Defines `inductive Derives` (NOT closure membership, per FREQ-210-004).
- Proves `derives_sound` and `derives_complete` using classical logic
  filter + `horn_result_least_fixed_point`.
- 0 sorry, 0 admit, 0 custom axiom.

## Runtime Side

- `_apply_rule_horn()`: exception chain penetration REMOVED.
  When an exception triggers, the original rule simply fails (returns None).
  No recursive exception-rule application.
- Monotonicity counterexample test added:
  `F ⊆ G → closure(F) ⊆ closure(G)` — adding a fact must never remove a claim.
- Single-step differential: `evaluate_horn()` returns per-step new claims.
- Closure differential: `evaluate()` returns differential between
  Horn closure and final accepted set.

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Exception handling in Horn | Remove entirely | RREQ-210-002: Horn is pure positive |
| Derives definition | Inductive type | FREQ-210-004: not closure membership |
| Classical logic | `open Classical` | Decidability of `Derives` in filter |
