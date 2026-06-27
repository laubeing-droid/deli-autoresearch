# SPEC-240 Tasks

## TASK-240-001: Define compileAttacks in Lean
- Status: DONE
- Files: `AttackDecision.lean` (argSet, toEdge, compileAttacks definitions)

## TASK-240-002: Prove compileAttacks_sound
- Status: DONE
- Lean proof: `Finset.mem_filter.mp`

## TASK-240-003: Prove compileAttacks_complete
- Status: DONE
- Lean proof: `Finset.mem_filter.mpr`

## TASK-240-004: Prove compileAttacks_exact
- Status: DONE
- Lean proof: constructor + sound/complete

## TASK-240-005: Define decisionProjection in Lean
- Status: DONE
- Files: `AttackDecision.lean` (decisionProjection definition)

## TASK-240-006: Prove decision_status_mutually_exclusive
- Status: DONE
- Lean proof: split + concrete DecisionStatus constructors

## TASK-240-007: Prove decision_status_coverage
- Status: DONE
- Lean proof: split on if-then-else branches

## TASK-240-008: Define attacksWellFormed + Prove tainted_fail_closed
- Status: DONE
- Lean proof: DecisionStatus.noConfusion

## TASK-240-009: Create Python tests
- Status: DONE
- Files: `test_attack_compiler.py`, `test_decision_projection.py`

## TASK-240-010: Red-team + finalize
- Status: DONE
- Evidence: build logs, test logs, axiom audit
