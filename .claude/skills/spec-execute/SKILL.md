---
name: spec-execute
description: Execute a single task within a worktree
---

# /spec-execute

Execute one task in isolation.

## Usage

```
/spec-execute <spec-id> <task-id>
```

## Actions

1. Verify task dependencies are satisfied (all COMPLETE)
2. Create a worktree for the task
3. Record target hash before modification
4. Spawn implementation agent (lean-prover, runtime-engineer, etc.)
5. Agent modifies only allowed files
6. Record changed files and evidence
7. Push to `spec/<spec-id>` branch
8. CI triggers automatically
9. Update task status in `tasks.md`

## Constraints

- One task at a time.
- Worker cannot self-mark complete.
- All changes in worktree only.
- Record all commands in `evidence/commands.jsonl`.
