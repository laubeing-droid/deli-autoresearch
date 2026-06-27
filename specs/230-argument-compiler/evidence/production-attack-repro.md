# P0-G04: Production Attack Compiler Failure — Reproduction

**Date**: 2026-06-27
**Playbook**: Playbook E, Section 3.3, P0-G04
**Baseline**: CROSS_REPO_LOCK.json (frozen 2026-06-27T16:00:00Z)
**Question**: Does the production attack compiler close through the canonical contract, or only through the shadow/spec path?

---

## Conclusion

**Production path is broken.** `StratifiedEvaluator.evaluate()` crashes with `TypeError` at Stage 2 because it calls `build_attack_graph_from_evaluator()` with 5 arguments, but the function only accepts 2. The canonical adapter (`canonical_adapter.py`) is completely disconnected from the production pipeline — it is never imported by `stratified_evaluator.py` or `evaluator.py`.

---

## 1. Failure Reproduction

### 1.1 Minimal Reproduction

```python
# Run from juris-calculus/
from compiler_core.stratified_evaluator import StratifiedEvaluator
from compiler_core.types import IRState, LegalFact
import tempfile, os

yaml_content = """rules:
  - id: R1
    premise_atoms: [fact_a]
    head_claim: claim_a
    concepts: [contract]
    exception_chain: []
    head_type: HORN
    mechanical_exception: true
    norm_modality: OBLIGATION
"""
with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
    f.write(yaml_content)
    path = f.name

evaluator = StratifiedEvaluator(path)
state = IRState()
state.facts["fact_a"] = LegalFact(id="fact_a", description="fact a")
result = evaluator.evaluate(state)  # TypeError here
os.unlink(path)
```

**Output**:
```
TypeError: build_attack_graph_from_evaluator() takes 2 positional arguments but 5 were given
```

### 1.2 Failing Tests

```
FAILED tests/unit/test_stratified_evaluator.py::TestStratifiedEvaluator::test_returns_list_not_irdstate
FAILED tests/unit/test_stratified_evaluator.py::TestStratifiedEvaluator::test_returns_claims_when_facts_match
FAILED tests/unit/test_stratified_evaluator.py::TestStratifiedEvaluator::test_accepted_claims_have_epistemic_status
3 failed, 1 passed in 2.37s
```

The 1 passing test (`test_returns_empty_when_no_facts`) passes because it hits the early return at line 63 (`if not raw_claims: return []`), before reaching the broken Stage 2 call.

---

## 2. Root Cause Analysis

### 2.1 Signature Mismatch

**Caller** (`stratified_evaluator.py:67-71`):
```python
attacks = build_attack_graph_from_evaluator(
    horn_state.claims,          # arg1: Dict[str, LegalClaim]
    self.rules,                 # arg2: List[LegalRule]
    self.evaluator.constraint_validator,  # arg3: ConstraintValidator
    horn_state,                 # arg4: IRState
    horn_state.blocked_claims   # arg5: Set[str]
)
```

**Definition** (`argumentation.py:356-362`):
```python
def build_attack_graph_from_evaluator(
    rules: list[dict[str, Any]],          # arg1
    evaluator_result: dict[str, Any],      # arg2
) -> list[tuple[str, str]]:
```

The function was written for the spec test interface (dict-based), but the production caller passes runtime objects.

### 2.2 Field Name Mismatch

**Production types** (`types.py:97`):
```python
exception_chain: List[str] = field(default_factory=list)
```

**argumentation.py:383**:
```python
exceptions = rule.get("exception_to", []) if isinstance(rule, dict) else getattr(rule, "exception_to", [])
```

`LegalRule` has `exception_chain`, not `exception_to`. This means exception-based attacks are silently missed even if the signature mismatch were fixed.

### 2.3 Canonical Adapter Disconnection

| Module | Imports canonical_adapter? | Imports canonical_schema? |
|--------|---------------------------|--------------------------|
| `evaluator.py` | **NO** | **NO** |
| `stratified_evaluator.py` | **NO** | **NO** |
| `argumentation.py` | **NO** | **NO** |
| `certificate_checker.py` | **NO** | **NO** |

The canonical adapter is a standalone module. The production pipeline (`StratifiedEvaluator`) bypasses it entirely.

### 2.4 Spec Test Path vs Production Path

| Aspect | Spec Tests (test_attack_compiler.py) | Production (stratified_evaluator.py) |
|--------|--------------------------------------|--------------------------------------|
| Attack compilation | `_compile_attacks` (standalone helper) | `build_attack_graph_from_evaluator` (broken call) |
| Data format | Dict-based (`{"id": "A"}`) | Runtime objects (`LegalRule`, `IRState`) |
| Uses canonical_adapter | **NO** | **NO** |
| Tests pass? | **YES** (8/8) | **NO** (3/4 fail) |
| Canonical contract | N/A (standalone) | Not used |

The spec tests verify the Lean theorem mirrors in isolation. They do not exercise the production pipeline.

---

## 3. Impact Assessment

### 3.1 What Works

| Component | Status | Evidence |
|-----------|--------|----------|
| `evaluate_horn()` (Stage 1) | **OK** | 415 tests pass, P0-G03 confirmed monotone |
| `grounded_extension()` (Stage 3) | **OK** | Standalone, signature compatible |
| `argumentation.py` standalone functions | **OK** | `grounded_extension`, `scc_decomposition`, etc. |
| Spec tests (`tests/spec/`) | **OK** | 132/132 pass |
| Canonical adapter + schema | **OK** | Round-trip tests pass |

### 3.2 What Is Broken

| Component | Status | Evidence |
|-----------|--------|----------|
| `StratifiedEvaluator.evaluate()` | **CRASH** | TypeError at Stage 2 |
| `build_attack_graph_from_evaluator()` call | **CRASH** | 5 args vs 2 params |
| Exception-based attack edges | **SILENT MISS** | `exception_to` vs `exception_chain` |
| Production → canonical contract bridge | **MISSING** | No import of canonical_adapter |
| `test_stratified_evaluator.py` | **3/4 FAIL** | Confirmed by pytest |

### 3.3 What Is NOT Broken

This failure does NOT affect:
- The Lean proofs (they are about `DecisionStatus` projection, not the Python runtime)
- The spec tests (they use standalone helpers)
- The Horn closure stage (Stage 1 works correctly)
- The grounded extension algorithm (Stage 3 works standalone)
- The certificate checker (independent module)

---

## 4. Spec Test vs Production Divergence

The spec tests (`test_attack_compiler.py`) define their own `_compile_attacks` helper that mirrors the Lean `compileAttacks` logic. This helper:
1. Takes `(arg_ids, raw_attacks)` — both as simple data
2. Filters attacks where both endpoints are in `arg_set`
3. Returns filtered list

The production `build_attack_graph_from_evaluator`:
1. Takes `(rules, evaluator_result)` — as dicts
2. Builds attacks from `priority_over` and `exception_to` fields
3. Also adds rebuttal-based attacks from conflicting heads

These are **two different algorithms** with **different inputs**. The spec test verifies the Lean mirror, not the production logic.

---

## 5. Gap Classification

| Gap | Severity | Type |
|-----|----------|------|
| `StratifiedEvaluator` crashes at Stage 2 | **Critical** | Bug — signature mismatch |
| `exception_to` vs `exception_chain` | **High** | Bug — silent data loss |
| Canonical adapter not in production path | **Medium** | Design gap — P7 work item |
| Spec tests don't exercise production path | **Medium** | Coverage gap |

---

## 6. Recommended Fix (not implemented — P0-G04 is audit-only)

The fix requires P4-G08 and P7 work. Minimum viable fix:

1. Align `build_attack_graph_from_evaluator` signature to accept `(claims, rules, constraint_validator, state, blocked_claims)` — or refactor the caller.
2. Fix `exception_to` → `exception_chain` in `argumentation.py:383`.
3. Add a production-path test that exercises the full 4-stage pipeline with attacks.

These are tracked under P4-G08 (Repair JC production attack compiler) and P7-G01 (Rebuild production stratified pipeline).

---

## 7. Verdict

| Criterion | Result |
|-----------|--------|
| Production attack compiler failure reproduced? | **YES** — TypeError at Stage 2 |
| Failure is in production path, not spec path? | **YES** — spec tests pass, production crashes |
| Canonical contract used by production? | **NO** — canonical_adapter not imported |
| Failure affects Lean proofs? | **NO** — Lean is independently verified |
| Failure affects spec tests? | **NO** — spec tests use standalone helpers |
| P0-G04 can be closed? | **YES** — failure reproduced and documented |
