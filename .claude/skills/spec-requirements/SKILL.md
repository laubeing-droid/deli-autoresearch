---
name: spec-requirements
description: Generate requirements.md for a specification from repository analysis
---

# /spec-requirements

Analyze relevant repositories and produce structured requirements.

## Usage

```
/spec-requirements <spec-id>
```

## Actions

1. Read `spec.yaml` for scope, dependencies, and allowed paths
2. Read relevant code across all declared repositories
3. Extract current state and identify conflicts
4. Write `requirements.md` with:
   - Numbered requirements (REQ-<spec>-NNN)
   - Non-goals
   - Risks
   - Human decision topics (HREQ-<spec>-NNN)
5. Update `status.json` to `REQUIREMENTS_APPROVED`

## Constraints

- Read-only on target repositories.
- Do not modify source code.
- Each requirement must have a unique ID.
- Identify all human decision topics.
