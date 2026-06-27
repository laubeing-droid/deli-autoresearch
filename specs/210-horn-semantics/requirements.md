# SPEC-210 Requirements: Positive Horn Semantics

## FREQ-210-001: Positive Horn Rule
Formal model SHALL define positive Horn rule.

## FREQ-210-002: Monotone One-Step Operator
Model SHALL define monotone one-step operator (TH).

## FREQ-210-003: Inductive Derives
Model SHALL define inductive `Derives`.

## FREQ-210-004: Derives ≠ Closure Membership
`Derives` SHALL NOT be defined as closure membership.

## FREQ-210-005: Derivation Soundness
Model SHALL prove derivation soundness: `Derives → closure membership`.

## FREQ-210-006: Derivation Completeness
Model SHALL prove derivation completeness: `closure membership → Derives`.

## FREQ-210-007: Least-Closure Minimality
Model SHALL prove least-closure minimality.

## FREQ-210-008: Semantic Equivalence
Model SHALL prove finite positive Horn model-theoretic equivalence.

## RREQ-210-001: JC Monotonicity
JC Horn evaluation SHALL be monotone when adding facts.

## RREQ-210-002: No Exception/Rebuttal/Priority in Horn
JC Horn evaluation SHALL NOT execute exception defeat, rebuttal, or priority effect.

## RREQ-210-003: Single-Step Differential
JC SHALL provide single-step differential evidence.
