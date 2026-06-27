# SPEC-240 Design

## Architecture

### Lean Layer (AttackDecision.lean)

1. **compileAttacks**: Takes `List Argument` + `List Attack`, produces `DungAAF`
   - `argSet`: maps Argument list to Finset of argument IDs
   - `toEdge`: maps Attack to `(attacker, target)` pair
   - Result: `DungAAF` with attacks filtered to well-formed edges

2. **decisionProjection**: Maps argument to DecisionStatus
   - TAINTED: argument not in args (pre-filter)
   - PROVED: argument in grounded extension
   - REFUTED: argument has attacker in GE but is not in GE
   - UNDECIDED: argument in args but neither in GE nor attacked by GE

3. **Proof strategy**:
   - `compileAttacks_*`: use `Finset.mem_filter` for clean biconditional
   - `decision_status_*`: use `split` on if-then-else (avoids syntactic mismatch between `aaf.labelling.1` and `aaf.grounded`)
   - `tainted_fail_closed`: use `DecisionStatus.noConfusion` on split branches

### Python Layer

- `test_attack_compiler.py`: mirrors compileAttacks sound/complete/exact
- `test_decision_projection.py`: mirrors decision status properties

## Key Design Decision

Using `split` on the if-then-else in the goal (rather than `rcases` on the labelling partition) avoids the `aaf.labelling.1` vs `aaf.grounded` syntactic mismatch. The `split` tactic gives the condition as a hypothesis automatically, sidestepping the need for definitional equality rewriting.

`DecisionStatus.noConfusion` is the cleanest way to prove distinct constructors are unequal in the `tainted_fail_closed` proof, avoiding `decide` failures on metavariable-containing goals.
