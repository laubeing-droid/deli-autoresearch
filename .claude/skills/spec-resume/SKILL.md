---
name: spec-resume
description: Resume work from disk state without conversation history
---

# /spec-resume

Recover state from disk and continue execution.

## Usage

```
/spec-resume
/spec-resume <spec-id>
```

## Actions

1. Scan all `specs/*/status.json`
2. Identify the spec furthest along that is not COMPLETE or BLOCKED
3. Read its `tasks.md` to find next TODO task
4. Verify dependencies are satisfied
5. Resume from the appropriate lifecycle phase
6. Do not rely on any conversation memory

## Constraints

- Disk state is the sole authority.
- No conversation history dependency.
- Resume exactly where the spec left off.
