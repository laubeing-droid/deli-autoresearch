# SPEC-100 Design

## Overview

SPEC-100 performs a read-only audit of three repositories, classifying all tracked files into one of 7 categories. No source code is modified.

## Architecture

```
TASK-100-001 (baselines)
    ├─► TASK-100-002 (formal inventory)
    ├─► TASK-100-003 (JC inventory)
    ├─► TASK-100-004 (license scan) ─► TASK-100-005 (file markers)
    ├─► TASK-100-006 (third-party scan)
    └─► TASK-100-007 (public paths) requires 002+003+005
           ├─► TASK-100-008~014 (7 classifications, parallel)
           └─► TASK-100-015 (coverage validation) requires 008~014
                  ├─► TASK-100-016 (manifest)
                  ├─► TASK-100-017 (disclosure freeze)
                  ├─► TASK-100-018 (classification JSON)
                  ├─► TASK-100-019 (classification MD)
                  ├─► TASK-100-020 (license status)
                  └─► TASK-100-021 (human review list)
                           └─► TASK-100-022 (red team)
                                    └─► TASK-100-023 (local commit)
```

## Data Model

Each classified path entry:
```json
{
  "path": "relative/path/to/file",
  "category": "PUBLIC_STANDARD|PUBLIC_FORMAL|PUBLIC_CORE|PUBLIC_REFERENCE|COMMERCIAL_PRIVATE_FUTURE|PATENT_REVIEW|THIRD_PARTY_REVIEW",
  "confidence": "HIGH|MEDIUM|LOW",
  "reason": "string",
  "source_repo": "formal|runtime|control"
}
```

## Constraints

- Read-only audit: no business code modification
- No license changes
- No repository visibility changes
- No history rewriting
- PATENT_REVIEW items trigger HUMAN_DECISION_REQUIRED
