# Deli AutoResearch Methodology

Deli is a research-control method implemented as a Python runtime. Its main job is to keep long-running research stateful, auditable, and bounded by verification.

## Research Loop

Each round follows the same shape:

1. Select an active task and direction.
2. Ask the work agent for strict JSON candidates.
3. Validate candidate structure and source class.
4. Run independent verification.
5. Route the result through memory and disclosure gates.
6. Update stall pressure and decide whether to continue, pivot, complete, or pause for human attention.

## Verdict Semantics

| Verdict | Meaning | Runtime effect |
| --- | --- | --- |
| `validated` | Candidate passed the required evidence or backend gate | Finding may be recorded if disclosure also passes |
| `rejected` | Candidate conflicts with evidence, backend, or contract | Claim is rejected and stall pressure increases |
| `needs_more_evidence` | Candidate is not refuted, but support is insufficient | Candidate remains bounded; repeated weak evidence forces exit |

No other verdict is part of the control plane.

## Stall And Pivot Rules

| Verification result | Stall pressure | Action |
| --- | --- | --- |
| `validated` | reset | record finding and continue or enter tail pass |
| `needs_more_evidence` | `+0.5` | continue briefly; repeated weak evidence exits the claim |
| `rejected` | `+1` | move to another claim or direction |

Pressure at or above `2` forces a structural pivot. The next direction must use a different `strategy_type`.

Pressure at or above `4` marks the task as needing human attention and pauses it.

## Claim Lifecycle

```text
candidate -> claim -> verification request -> verdict -> routed memory record
```

A claim becomes a finding only when:

- the verifier produces an admissible result;
- the source class is strong enough;
- memory routing accepts it as a verified finding;
- disclosure policy does not block it.

Weak candidates are not silently discarded. They go to candidate, rejection, or failure records so the research trail remains inspectable.

## Orchestrator Boundary

The orchestrator arbitrates process. It does not judge content quality. It asks:

- Is the candidate structurally valid?
- Is the source class admissible?
- What verdict did verification return?
- Did the task hit a stall or pivot threshold?
- Is a tail pass required?

Domain content belongs in templates, verification backends, source registries, and human decisions.

## Template Boundary

Templates provide domain-specific structure through:

- task-spec schema;
- seed directions;
- next-direction generation;
- domain stall rules;
- work-candidate validation;
- finding validation;
- completion policy.

Templates may make a domain stricter. They must not weaken global fail-closed rules.

## Evidence Boundary

Deli supports empirical tests, formal manifests, source spans, human review, and deterministic backend artifacts. It does not convert experience, LLM output, or web snippets into formal proof.
