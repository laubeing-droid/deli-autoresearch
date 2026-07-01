# Template Authoring Guide

Templates adapt Deli's research loop to a domain. A template should narrow the contract, not bypass the global runtime rules.

## Required Interfaces

### `build_task_spec_schema()`

Return the Markdown sections that a task spec must contain. The base research template requires broad task context; domain templates add domain-specific sections.

Example: a legal proof template can require target semantics, attack graph class, verification engine, known lemmas, and breakthrough objective.

### `seed_directions()`

Return the initial strategy pool as `Direction` objects.

Each direction needs:

- `strategy_type`;
- `summary`;
- `rationale`;
- `origin_iteration`.

`initial_direction()` should return the strongest starting point. `seed_directions()` should return that direction plus meaningful alternatives.

### `generate_next_direction(tried_directions, progress, trigger)`

Return a new direction when stall pressure forces a structural pivot.

The new direction must use a `strategy_type` that has not already been tried for the current pivot set. Otherwise the orchestrator can loop without changing the search shape.

### `template_stall_rules(progress, verification_results)`

Return domain-specific warnings. Global pressure thresholds remain in the runtime; the template adds domain knowledge.

Example: if repeated candidates are only model-generated and never add source-backed or backend-backed evidence, flag semantic collapse risk.

### `completion_policy(task_spec)`

Return:

- `target_validated_findings`;
- `max_iterations`;
- `require_tail_pass`.

Use conservative defaults. A tail pass is useful when the domain needs evidence that the loop has stopped finding new validated claims.

## Structural Validators

### `validate_work_candidate(candidate)`

Reject candidates that cannot be verified. A domain template should require the payload fields that its backend actually checks.

For claim-bound legal proof work, this usually means a structured `formal_payload` with claims, attacks, and verification type.

### `validate_finding_rules(finding)`

Reject findings that lack required source or backend evidence. This validator is the template's last chance to prevent a domain-specific weak result from entering the finding stream.

## Design Rules

1. Start from the general template and override only domain-specific behavior.
2. Make `strategy_type` names meaningful; pivot quality depends on them.
3. Treat formal payload design as the core contract with verification.
4. Prefer deterministic checks over natural-language reviewer judgment.
5. Let missing external engines fail closed.
6. Never make model output a verified finding by template policy.

## Testing A Template

Add tests for:

- task-spec schema requirements;
- seed direction shape;
- pivot direction uniqueness;
- invalid candidate rejection;
- weak evidence rejection;
- completion policy;
- at least one successful end-to-end mock run.

Run:

```powershell
python -m pytest -q
```
