# State Authority

- Disk state is authoritative.
- `status.json` is updated only after mechanical validation.
- COMPLETE requires CI green + red-team approval.
- HUMAN_DECISION_REQUIRED cannot be cleared automatically.
- A failed command must be recorded in `commands.jsonl`.
- Never mark a task complete because the worker reports success.
