---
name: spec-red-team
description: Run automated three-layer red team review on a completed task
---

# /spec-red-team

Execute the three-layer red team defense.

## Usage

```
/spec-red-team <spec-id> <task-id>
```

## Actions

### Layer 1: CI Mechanical Checks
- Verify `lake build` exit 0
- Verify sorry=0 in blocking path
- Verify admit=0
- Verify custom_axiom=0
- Verify theorem hash unchanged
- Verify runtime tests pass

### Layer 2: Claude Agent Semantic Checks (RT-001 to RT-008)
- RT-001: Theorem statement matches requirement target
- RT-002: All premises used in proof
- RT-003: Checker independence from production evaluator
- RT-004: No fixture-only proof
- RT-005: No production bypass
- RT-006: No ID conflation (RuleId, ClaimId, ArgumentId)
- RT-007: Theorem name matches strength
- RT-008: No unregistered sorry in blocking path

### Layer 3: Adversarial Verification
- Spawn 3 independent agents:
  - Agent 1: Construct counterexample
  - Agent 2: Check if theorem weakened
  - Agent 3: Validate proof technique
- Scoring: 3/3=PASS, 2/3=PASS_WITH_LIMITS, <=1=REJECT

## Output

JSON verdict with:
- verdict: PASS | PASS_WITH_LIMITS | REJECT | HUMAN_DECISION_REQUIRED
- checks_passed / checks_failed
- findings list
- adversarial_votes

## Constraints

- Read-only. Do not modify source code.
- All checks are automated, no human intervention required.
