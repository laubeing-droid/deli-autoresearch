# Source-Bounded Research Mode

Deli is a source-bounded autonomous research harness. A model, search tool, or external agent may propose a candidate. Only approved sources and objective verification backends can promote that candidate into a finding.

## Admission Rule

A publishable finding needs at least one of:

- an approved source span from the source registry;
- a formal or deterministic backend result;
- a human-reviewed anchor recorded as evidence.

Open-web material, `derived` content, and `model_generated` content are never sufficient by themselves.

## Required Flow

1. Register sources in `config/source_registry.example.yml` or a task-local registry with the same schema.
2. Ask `SourceRegistry` and `RetrievalPolicy` before reading material.
3. Route open-web output as `source_candidate`.
4. Record positive and negative trials through `TrialHarness`.
5. Use `SearchFrontier` to track bounded directions, lineage, promotion reasons, and discard reasons.
6. Route accepted, rejected, candidate, and failure records through `MemoryRouter`.
7. Pass disclosure checks before any research output is treated as publishable.

## Implementation Map

| Mechanism | File |
| --- | --- |
| Source registry | `src/deli_autoresearch/source_registry.py` |
| Retrieval admission | `src/deli_autoresearch/retrieval_policy.py` |
| Trial feedback | `src/deli_autoresearch/trial_harness.py` |
| Frontier management | `src/deli_autoresearch/search_frontier.py` |
| Memory routing | `src/deli_autoresearch/memory_router.py` |
| Disclosure gate | `src/deli_autoresearch/disclosure_gate.py` |
| Verification backend contracts | `src/deli_autoresearch/verification_backends.py` |
| Local-history profile | `src/deli_autoresearch/local_history_profile.py` |
| Registry schema | `schemas/source_registry.schema.json` |

## Fail-Closed Conditions

Deli must not write a verified finding when:

- the source is unregistered;
- the source is only proposed or rejected;
- the source is open-web material without an approved anchor;
- evidence lacks `source_id` plus `source_span` or `evidence_path`;
- the backend returns unknown, timeout, unavailable, truncated, or not run;
- a candidate relies only on `derived` or `model_generated` content;
- repeated trials produce no strong evidence.

## Local-History Boundary

For local-history projects, web search defaults to off. Allowed work includes OCR alignment, source indexing, conflict detection, candidate extraction, and human-review question generation over approved material. A local-history fact requires an approved source span before it can become a finding.

The profile root is resolved from `MINNAN_PROFILE_ROOT` or sibling-repository discovery. The root itself must not be committed as a machine-specific default path.
