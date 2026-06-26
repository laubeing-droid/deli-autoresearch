---
name: spec-status
description: Display current status of all specifications
---

# /spec-status

Show the lifecycle status of every specification.

## Usage

```
/spec-status
/spec-status <spec-id>
```

## Actions

1. Scan `specs/*/spec.yaml` and `specs/*/status.json`
2. Display table: spec-id, title, status, last updated, task progress (completed/total)
3. For a specific spec: show full status including pending tasks and blockers

## Output

Markdown table with columns: SPEC ID | Title | Status | Tasks Done | Last Updated

## Constraints

- Read-only. No modifications.
