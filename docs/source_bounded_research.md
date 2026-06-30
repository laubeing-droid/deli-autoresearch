# Source-Bounded Research Mode

This document is the operational boundary for Deli research tasks that touch
legal formalization, juris-calculus runtime evidence, or future local-history
projects such as `D:\Codex\闽南文史ALLinAI`.

## Core Rule

Deli is a source-bounded autonomous research harness, not an open-web autonomous
researcher. A model or web search may propose candidates, but only approved
sources and objective verification backends can promote a claim into findings.

## Required Flow

1. Register every source in `config/source_registry.example.yml` or a task-local
   registry with the same schema.
2. Use `SourceRegistry` and `RetrievalPolicy` before reading material.
3. Route open-web results as `source_candidate`; never route them as
   `verified_finding`.
4. Record every positive and negative trial through `TrialHarness`.
5. Use `SearchFrontier` to keep multiple bounded directions with lineage,
   promotion reasons, and discard reasons.
6. Route memory through `MemoryRouter`; a `verified_finding` without strong
   evidence must become a failure record.
7. Report the claim, source, verifier, and disclosure status before publishing
   any research output.

## Implementation Map

| Mechanism | File |
| --- | --- |
| Source registry | `src/deli_autoresearch/source_registry.py` |
| Retrieval admission | `src/deli_autoresearch/retrieval_policy.py` |
| Trial feedback | `src/deli_autoresearch/trial_harness.py` |
| Memory routing | `src/deli_autoresearch/memory_router.py` |
| Population frontier | `src/deli_autoresearch/search_frontier.py` |
| Registry schema | `schemas/source_registry.schema.json` |
| Registry example | `config/source_registry.example.yml` |

## Fail-Closed Conditions

- Unregistered source requested for retrieval.
- Proposed or rejected source requested for retrieval.
- Open-web material requested as a finding.
- `verified_finding` lacks strong source or formal backend evidence.
- Two consecutive trials add no strong evidence.
- Three repeated failures hit the same claim.

## Local-History Boundary

For `D:\Codex\闽南文史ALLinAI`, web search defaults to off. Allowed work is
OCR alignment, source indexing, conflict detection, candidate extraction, and
human-review question generation over approved material. A local-history fact
requires an approved source span before it can be written as a finding.
