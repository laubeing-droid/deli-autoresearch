# Template Authoring Guide

## The Five Required Interfaces

Every template must implement five interfaces. These are the contract
between the orchestrator and the domain.

### 1. build_task_spec_schema()

Returns a dict with required_sections: the Markdown headings a task spec
must contain. The general_research base requires goal, scope, and
constraints. Domain templates extend with domain-specific headings.

Example (legal_proof): adds target_semantics, attack_graph_class,
verification_engine, known_lemmas, mvm_breakthrough.

### 2. seed_directions()

Returns a list of Direction objects that seed the initial strategy pool.
These are the first directions the orchestrator will try. Each Direction
has: strategy_type (must be in the template's registered types), summary
(human-readable), rationale, origin_iteration (always 0).

Rule: the initial_direction() method should return the single most
promising starting point. seed_directions() returns the full pool
(initial + alternatives).

### 3. generate_next_direction(tried_directions, progress, trigger)

Called when a structural pivot is required (stall pressure >= 2).
Receives all previously attempted directions and the current progress
state. Must return a Direction with a strategy_type NOT in
tried_directions.

The trigger parameter indicates what caused the pivot: stall_pressure_2,
stall_pressure_3, stalled_at_max_iterations, etc.

### 4. template_stall_rules(progress, verification_results)

Returns a list of warning strings. This is where domain-specific stall
detection lives. The base kernel handles universal rules (pressure
thresholds). Templates add domain-specific ones.

Example (legal_proof): if all verification results are
needs_more_evidence with only model_generated evidence, flag
semantic_collapse_risk — the work agent is producing trivial claims.

### 5. completion_policy(task_spec)

Returns a CompletionPolicy with:
- target_validated_findings: how many validated findings before the
  task is considered complete
- max_iterations: hard stop after this many iterations regardless
- require_tail_pass: if True, the final iteration must produce no
  new validated findings (convergence check)

### Also: validate_work_candidate() and validate_finding_rules()

These are the structural validators. validate_work_candidate ensures
the work agent's output conforms to the claim-bound contract (e.g.,
legal_proof requires formal_payload with claims, attacks,
verification_type). validate_finding_rules enforces domain-specific
evidence standards.

## Design Principles

1. Start from general_research. Inherit its stall/pivot machinery.
   Only override what your domain genuinely requires.

2. Direction types are the vocabulary of your domain. Invest in
   naming them well — the orchestrator enforces that a structural
   pivot MUST change strategy_type, so having meaningful
   categories is the difference between productive pivots and
   random walk.

3. Completion policies should be conservative. Four iterations
   with target_validated_findings=3 is a reasonable default for
   domains with deterministic verification. Increase max_iterations
   only when verification latency is high.

4. The claim-bound contract (formal_payload) is the single most
   important design decision. It determines what the verification
   agent can actually check. Make it as structured as possible.