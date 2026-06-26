---
name: spec-tasks
description: Compile requirements and design into atomic tasks
---

# /spec-tasks

Break design into atomic, independently verifiable tasks.

## Usage

```
/spec-tasks <spec-id>
```

## Actions

1. Read `requirements.md` and `design.md`
2. Write `tasks.md` with:
   - Numbered tasks (TASK-<spec>-NNN)
   - Each task: Status, Dependencies, Allowed files, Actions, Acceptance (AC-<spec>-NNN), Evidence
   - Acyclic dependency graph
3. Update `status.json` to `READY`

## Constraints

- Each task must have at least one acceptance criterion.
- Dependencies must form a DAG (no cycles).
- Each task must declare allowed file paths.
- One task = one atomic change.
