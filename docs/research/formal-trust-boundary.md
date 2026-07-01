# Formal Trust Boundary

This document states what Deli may claim about formal trust. It is intentionally conservative.

## Trust Layers

| Layer | Evidence class | Allowed claim |
| --- | --- | --- |
| Source span | Approved source registry entry plus locator | The claim is grounded in a specific source segment |
| Runtime test | Deterministic test or backend artifact | The implementation behaved as tested for that case |
| Cross-repo runtime backend | juris-calculus result plus independent checker where applicable | The external runtime produced and checked a result for the supplied payload |
| Lean manifest | legal-math-modeling theorem manifest | A named theorem is available as formal evidence if the manifest marks it complete |
| Human review | Explicit reviewed anchor | A human accepted the cited source or interpretation |

## What Deli Must Not Claim

- Do not claim arbitrary formal proof from bounded tests.
- Do not claim Lean-formalized evidence unless a theorem manifest entry supports it.
- Do not claim external-engine health when the engine is missing or incompatible.
- Do not claim a candidate is verified when evidence is only `derived`, `model_generated`, or open-web.
- Do not claim four-stage runtime correctness from isolated stage tests.
- Do not claim legal conclusion correctness from a formatting or serialization pass.

## Fail-Closed Cross-Repo Behavior

External roots are resolved by environment variable or sibling discovery. If a required repository, manifest, module, or backend is missing, Deli reports backend unavailability or needs-more-evidence. It must not replace missing formal evidence with a model explanation.

## Release Language

Allowed:

- "The local pytest suite passed."
- "The source-bounded gate rejected unregistered or weak evidence."
- "The bridge returned a checked result for this payload."
- "The theorem manifest contains a complete entry for this theorem."

Forbidden:

- "The system proved the legal outcome" when only runtime tests ran.
- "The LLM verified the fact."
- "The release is vulnerability-clean" when the advisory query timed out.
- "The public repository contains the full legal product" when private workflows, rule libraries, or benchmarks are intentionally excluded.
