---
name: spec-design
description: Generate design.md for a specification
---

# /spec-design

Produce the technical design document.

## Usage

```
/spec-design <spec-id>
```

## Actions

1. Read `requirements.md` and existing code
2. Write `design.md` with:
   - Architecture decisions
   - Interface definitions
   - Data models
   - Error semantics
   - Migration strategy
   - Module boundaries
3. Update `status.json` to `DESIGN_APPROVED`

## Constraints

- Do not modify source code.
- Design must address every requirement.
- Design must not contradict requirements.
