---
name: spec-decide
description: Record a human decision in the decisions log
---

# /spec-decide

Record a human decision without making the decision itself.

## Usage

```
/spec-decide <spec-id> <decision-topic> "<decision-text>"
```

## Actions

1. Validate that the spec is in HUMAN_DECISION_REQUIRED status
2. Record decision in `specs/<spec-id>/decisions.md`:
   - Topic
   - Decision text
   - Timestamp
   - Human (not AI) made the decision
3. Clear HUMAN_DECISION_REQUIRED if all decisions resolved
4. Update `status.json`

## Constraints

- Only records decisions, never makes them.
- User must provide the decision text.
- Cannot be used to bypass HUMAN_DECISION_REQUIRED.
