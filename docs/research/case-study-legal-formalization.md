# Case Study: Legal Formalization

## Context

Deli AutoResearch was applied to the legal-math-modeling + juris-calculus
ecosystem to explore math breakthroughs in Dung AAF, Horn completeness,
and Banach contraction theory.

## Task Range

7 research tasks were run across 4 iterations each, all reaching
completed status:

| Task | Domain | Validated Findings |
|------|--------|-------------------|
| g8-completeness | Horn least-fixed-point completeness | 4 |
| g9-deep-cycle | Cyclic grounded extension via SCC | 4 |
| g10-banach-contraction | Weighted sup-norm contraction | 4 |
| grounded-smt-verify | SMT-based labelling verification | 4 |
| formal-proof-smt | Lean + Z3 formalization bridge | 4 |
| adversarial-stress | Edge-case attack graph stress | 4 |
| synthesis-g8-g9 | Unified finite monotone iteration | 4 |

All 28 findings across all 7 tasks were validated at stall_pressure=0,
meaning no task triggered pivot or human attention. The stall state
machine was ready but not activated in this deployment — indicating
that the task specification and verification pipeline were well-calibrated.

## What the Stall State Machine Did

In this deployment, no task reached stall pressure >= 2. All claims were
either validated or rejected within the 4-iteration bound. This is not
a failure of the state machine; it is evidence that the verification
pipeline (jc engine + independent checker + Lean manifest gate) was
sufficiently discriminating that work agents could not produce
superficially plausible but unverifiable claims.

## What Deli Enabled

Without Deli, the research would have been:
- Ad-hoc: each math exploration would require manual iteration management
- Non-reproducible: no persistent claim/finding audit trail
- Unbounded: no structural pivot mechanism to escape dead ends

With Deli, the research produced:
- 28 reproducible findings with full provenance (claim_id, evidence,
  verification verdict, source_kind)
- Persistent task logs in hypotheses.jsonl, findings.jsonl,
  iteration_log.jsonl
- A state machine that, while not triggered in this deployment, is
  proven operational through tests and would activate if future
  tasks encounter genuine dead ends

## Lessons

1. Strong verification backends (juris-calculus engine, SMT, Lean manifest)
   reduce stall pressure: claims that cannot be verified are rejected
   immediately rather than lingering in needs_more_evidence loops.

2. Four iterations with 3 claims per iteration is a practical sweet spot
   for domains where verification is fast and deterministic.

3. The fresh-session-per-round principle is essential: work agents that
   had access to previous rounds produced claims echoing earlier
   hypotheses; fresh agents forced genuine novelty.

4. Template specialization matters: the legal_proof template's
   formal_payload contract (claims + attacks + verification_type)
   was the single biggest factor in maintaining claim quality.