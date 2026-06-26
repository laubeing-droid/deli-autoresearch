---
name: spec-report
description: Generate a status report for all or specific specifications
---

# /spec-report

Generate a structured progress report.

## Usage

```
/spec-report
/spec-report <spec-id>
```

## Actions

1. Scan all spec directories
2. For each spec: count tasks by status (TODO, IN_PROGRESS, COMPLETE, BLOCKED)
3. For each spec: check CI status
4. For each spec: count open human decisions
5. Generate markdown report with:
   - Overall progress summary
   - Per-spec breakdown
   - Blocked items and reasons
   - Pending human decisions
   - Sorry ledger status

## Output

Markdown report suitable for inclusion in progress tracking.

## Constraints

- Read-only. No modifications.
