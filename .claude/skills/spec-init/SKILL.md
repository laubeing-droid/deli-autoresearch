---
name: spec-init
description: Initialize a new specification directory with empty spec files and DRAFT status
---

# /spec-init

Create a new specification directory under `specs/`.

## Usage

```
/spec-init <spec-id> <title>
```

## Actions

1. Create directory `specs/<spec-id>/`
2. Create subdirectories: `evidence/`, `evidence/test-results/`, `evidence/diffs/`, `evidence/reports/`, `evidence/hashes/`, `iterations/`
3. Create `spec.yaml` with:
   - `schema_version: "1.0"`
   - `spec_id: <spec-id>`
   - `title: <title>`
   - `status: DRAFT`
4. Create empty: `requirements.md`, `design.md`, `tasks.md`, `acceptance.md`, `decisions.md`, `risks.md`
5. Create `status.json` with `{"status": "DRAFT", "updated": "<timestamp>"}`
6. Create `evidence/commands.jsonl` (empty)

## Constraints

- Do NOT modify any target repository code.
- Do NOT create spec if it already exists.
- State is set to DRAFT only.
