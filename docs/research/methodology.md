# Deli AutoResearch: Methodology

## What Makes Deli a Research Method

Deli governs long-horizon autonomous research through a state machine with
non-negotiable protocols: single-writer model, fresh session per round,
three-state verification verdict, stall/pivot pressure accounting.

## The Stall/Pivot State Machine

| Verification Result | Stall Pressure | Action |
|---------------------|---------------|--------|
| validated | reset to 0 | Finding recorded |
| needs_more_evidence | +0.5 | Retry; >=2 consecutive -> exit claim |
| rejected | +1 | Move to next claim or pivot |

Pressure >= 2 forces structural pivot (strategy_type must change).
Pressure >= 4 marks needs_human_attention (paused_for_human).

## Claim Lifecycle

claim (proposed) -> hypothesis (under investigation, hypotheses.jsonl)
-> finding (verified, findings.jsonl) — only if source is strong
(web, local_file, code, experiment), not derived/model_generated alone.

## Orchestrator Principle

The orchestrator does process arbitration only. It asks:
- What was the verdict?
- What is the stall pressure?
- Has a structural pivot been triggered?

It never evaluates claim content quality.

## Template System

Templates adapt Deli to domains via: build_task_spec_schema, seed_directions,
generate_next_direction, template_stall_rules, validate_work_candidate,
validate_finding_rules, completion_policy.

## Key Design Constraints

Single writer, fresh session per round, no database, file system as truth,
fail-closed semantics, human intervention limited to injecting new directions.