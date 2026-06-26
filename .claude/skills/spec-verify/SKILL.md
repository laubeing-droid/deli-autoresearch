---
name: spec-verify
description: Verify task completion with CI and local acceptance checks
---

# /spec-verify

Verify a completed task meets all acceptance criteria.

## Usage

```
/spec-verify <spec-id> <task-id>
```

## Actions

1. Confirm CI green light for the task branch
2. Re-run local acceptance checks as double verification
3. Verify file scope compliance (no changes outside allowed paths)
4. Verify target hash (theorem statements not weakened)
5. Verify sorry ledger compliance
6. Verify evidence files exist and are valid
7. Output verdict: `PASS_CANDIDATE` | `REWORK` | `BLOCKED` | `HUMAN_DECISION_REQUIRED`

## Constraints

- Read-only. Do not modify source code.
- CI status is the primary signal.
- Local acceptance is secondary confirmation.
