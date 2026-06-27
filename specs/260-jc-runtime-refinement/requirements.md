# SPEC-260 Requirements

## Goal

Refine the JC runtime to guarantee alignment with the formal model:
positive Horn closure, Dung grounded extension, and independent certificate verification.

## Requirements

1. **R1 — Horn closure is positive and monotone.** Adding facts can only increase the closure. No negative premises.
2. **R2 — Grounded extension matches Dung semantics.** Single attackers → IN/OUT. Mutual attacks → UNDECIDED.
3. **R3 — Certificates are independent of production evaluator.** Checker does not import evaluator.
4. **R4 — Tampered certificates are rejected.** Wrong targets, wrong iterations, forged attacks all fail.
5. **R5 — Fail-closed on checker rejection.** If `verify` returns False, runtime must not proceed.
6. **R6 — No SyntheticClaim in production path.** Only allowed in test harnesses.

## Non-goals

- New Lean blocking theorems (none needed for SPEC-260).
- Changes to DDL norm processing (Stage 2).
- Cross-certificate chaining (deferred to SPEC-280).
