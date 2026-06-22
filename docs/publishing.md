# Publishing Notes

## Local State Before Publishing

- `runtime/` should not be committed.
- `.benchmark_runtime/` should not be committed.
- Request/response bridge files should not be committed.

## GitHub Setup

1. Create an empty GitHub repository named `delichen-proofweaver`.
2. Add the remote:

```bash
git remote add origin https://github.com/<user>/delichen-proofweaver.git
```

3. Push the current branch:

```bash
git push -u origin main
```

## Suggested Repo Metadata

- Name: `delichen-proofweaver`
- Description: `Long-horizon proof research orchestration framework by DeliChen`
- Topics:
  - `mathematical-proofs`
  - `research-automation`
  - `agent-orchestration`
  - `llm`
  - `python`
