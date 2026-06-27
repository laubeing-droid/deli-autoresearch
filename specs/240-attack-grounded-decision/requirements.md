# SPEC-240 Requirements: Attack, Grounded, and Decision

## Goal

Formalize attack compilation, grounded extension projection, and decision status assignment.

## Functional Requirements

| ID | Requirement |
|----|-------------|
| FREQ-240-001 | `compileAttacks`: compile attack list into `DungAAF` filtering to well-formed edges |
| FREQ-240-002 | `compileAttacks_sound`: every compiled attack has both endpoints in the arg set |
| FREQ-240-003 | `compileAttacks_complete`: all valid attack edges are in the compiled AAF |
| FREQ-240-004 | `compileAttacks_exact`: biconditional soundness + completeness |
| FREQ-240-005 | `decisionProjection`: map argument to DecisionStatus based on grounded extension |
| FREQ-240-006 | `decision_status_mutually_exclusive`: no argument gets two statuses |
| FREQ-240-007 | `decision_status_coverage`: every argument in args gets exactly one non-TAINTED status |
| FREQ-240-008 | `attacksWellFormed`: all attack edges have both endpoints in args |
| FREQ-240-009 | `tainted_fail_closed`: no argument in args is assigned TAINTED |

## Blocking Theorems

| Lean Name | Status |
|-----------|--------|
| `compileAttacks_sound` | PROVEN |
| `compileAttacks_complete` | PROVEN |
| `compileAttacks_exact` | PROVEN |
| `decision_status_mutually_exclusive` | PROVEN |
| `decision_status_coverage` | PROVEN |
| `tainted_fail_closed` | PROVEN |

## Formal Verification

- 0 sorry, 0 admit, 0 custom axiom in `AttackDecision.lean`
- `lake build +JurisLean.AttackDecision` passes
- Axiom audit: only standard Lean axioms (propext, Classical.choice, Quot.sound)

## Runtime Alignment

- `test_attack_compiler.py`: 8 tests (sound, complete, exact)
- `test_decision_projection.py`: 12 tests (mutual exclusion, coverage, tainted closed)
- 352 passed, 38 skipped, 0 failed
