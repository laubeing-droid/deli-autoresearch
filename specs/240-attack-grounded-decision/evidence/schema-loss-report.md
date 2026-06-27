# P0-G05: Schema Loss Report — Production vs Canonical

**Date**: 2026-06-27
**Playbook**: Playbook E, Section 3.3, P0-G05
**Baseline**: CROSS_REPO_LOCK.json (frozen 2026-06-27T16:00:00Z)
**Question**: What fields, semantics, and evidence chains does the production path lose relative to the canonical schema?

---

## Conclusion

**The production path retains 2 of 14 canonical types (LegalFact, LegalClaim). It produces zero downstream types (Argument, Attack, Decision, Certificate).** 12 of 14 canonical types are entirely absent from the production output. The canonical adapter exists but is never imported by the production pipeline.

---

## 1. Type Presence Comparison

### 1.1 Core Model Types (LegalModel, 12 component types)

| Canonical Type | In Production `types.py`? | Produced by Pipeline? | In Canonical Adapter? |
|----------------|--------------------------|----------------------|----------------------|
| `LegalFact` | YES (dataclass) | YES (Stage 1) | YES (`adapt_jc_rule`) |
| `LegalClaim` | YES (dataclass) | YES (Stage 1) | **NO** (no adapter) |
| `LegalRule` | YES (dataclass) | INPUT (not output) | YES (`adapt_jc_rule`) |
| `LegalNorm` | **NO** | **NO** | **NO** |
| `Defense` | **NO** | **NO** | **NO** |
| `Priority` | **NO** | **NO** | **NO** |
| `Violation` | **NO** | **NO** | **NO** |
| `Reparation` | **NO** | **NO** | **NO** |
| `Argument` | **NO** | **NO** | **NO** |
| `Attack` | **NO** | **NO** | **NO** |
| `Decision` | **NO** | **NO** | **NO** |
| `Certificate` | **NO** | **NO** | **NO** |

### 1.2 Supporting Types

| Canonical Type | Production Equivalent | Notes |
|----------------|----------------------|-------|
| `Modality` (enum) | `NormModality` (str, Enum) | Canonical: 4 values. Production: 5 values (adds `UNKNOWN`). |
| `AttackKind` (enum) | **NONE** | No attack type classification in production |
| `DefenseKind` (enum) | **NONE** | Defense not modeled in production |
| `ReparationMode` (enum) | **NONE** | Reparation not modeled in production |
| `DecisionStatus` (enum) | **NONE** | Decision not modeled in production |
| `TimeInterval` | `valid_from: str` + `valid_to: str` | Canonical: int start/end. Production: ISO date strings. Type mismatch. |
| `SourceRef` | **NONE** | Provenance not tracked |
| `TemporalEntry` | **NONE** | Temporal record not tracked |
| `JurisdictionEntry` | **NONE** | Jurisdiction record not tracked |
| `SCHEMA_VERSION` | **NONE** | No schema version in production types |

---

## 2. Field-by-Field Loss per Type

### 2.1 LegalFact

| Canonical Field | Canonical Type | Production Field | Production Type | Match? |
|-----------------|---------------|-----------------|----------------|--------|
| `id` | `str` | `id` | `str` | YES |
| `content` | `str` | `description` | `str` | **NAME MISMATCH** |
| `source` | `str` | `source` | `str` | YES |
| `time` | `int` (≥0) | **NONE** | — | **LOST** |

**Production-only fields** (no canonical equivalent):
- `formalizable: float` — formalizability score
- `taint_status: str` — contamination tracking
- `extraction_confidence: float`
- `carrier_level: str` — evidence carrier grading
- `raw_text: str` — source anchoring
- `source_anchor: str`

**Loss**: `time` (temporal fact timestamp) is absent. `content` is renamed to `description` — semantic mismatch if cross-system consumption assumes canonical naming.

### 2.2 LegalClaim

| Canonical Field | Canonical Type | Production Field | Production Type | Match? |
|-----------------|---------------|-----------------|----------------|--------|
| `id` | `str` | `id` | `str` | YES |
| `content` | `str` | `description` | `str` | **NAME MISMATCH** |
| `claimant` | `str` | **NONE** | — | **LOST** |

**Production-only fields** (no canonical equivalent):
- `confidence: float` — formalizability-based score
- `epistemic_status: Optional[EpistemicStatus]` — trust label wrapper
- `taint_chain: List[TaintNode]` — contamination provenance
- `requires_human_review: bool`
- `claim_type: str` — HORN_CLAIM / DISCRETIONARY / REQUIRES_REVIEW
- `execution_trace_id: str`
- `proof_trace: List[Dict]` — execution trace (not canonical proof trace)
- `source_anchor: str`
- `domain_origin: str`
- `L0_primitive_source: str`
- `allowed_claim: bool`
- `forbidden_claim: bool`
- `agent_instruction: str`

**Loss**: `claimant` (who asserts this claim) is absent. `content` renamed to `description`.

### 2.3 LegalRule

| Canonical Field | Canonical Type | Production Field | Production Type | Match? |
|-----------------|---------------|-----------------|----------------|--------|
| `id` | `str` | `id` | `str` | YES |
| `modality` | `Modality` (enum) | `norm_modality: str` | `str` | **TYPE MISMATCH** |
| `premises` | `List[str]` | `premise_atoms: List[str]` | `List[str]` | **NAME MISMATCH** |
| `conclusion` | `str` | `head_claim: str` | `str` | **NAME MISMATCH** |
| `source` | `str` | **NONE** | — | **LOST** |
| `jurisdiction` | `str` | `jurisdiction: str` | `str` | YES |
| `valid_interval` | `TimeInterval` | `valid_from + valid_to` | `str + str` | **TYPE MISMATCH** |

**Production-only fields** (no canonical equivalent):
- `exception_chain: List[str]` — defeasible exception list
- `concepts: List[str]` — domain concept tags
- `mechanical_exception: bool`
- `head_type: str` — HORN / other
- `attacks: List[str]` — direct attack targets
- `priority_over: List[str]` — priority relations
- `modality_confidence: float`
- `modality_source: str`
- `reparation_chain_pool: list`
- `source_anchor: str`
- `authority_rank: str`
- `trust_label: str`
- `data_quality: str`

**Loss**: `source` (legal source citation) absent. `modality` uses `str` instead of `Modality` enum — no validation. `valid_interval` is split into two strings instead of validated `TimeInterval(int, int)`.

### 2.4 Missing Types — Semantic Loss

| Missing Type | Semantic Purpose | What Is Lost |
|--------------|-----------------|-------------|
| `LegalNorm` | Deontic norms distinct from Horn rules | Production folds norms into `LegalRule` with `norm_modality: str`. Loses `enabled` flag, separate `condition`/`consequence` structure. |
| `Defense` | Defeater/justification/excuse targeting rules | `DefenseKind` classification, `burden_of_proof`, `facts_required` — entire defense modeling absent |
| `Priority` | Rule priority ordering | Production has `priority_over: List[str]` on LegalRule, but no standalone `Priority` type — no `higher`/`lower` structural validation |
| `Violation` | Triggered violations with support facts | `trigger_fact`, `support_facts` — violation tracking absent from production |
| `Reparation` | Reparation chains for violations | `ReparationMode` (ALTERNATIVE/ORDERED_CHAIN/CONCURRENT/COURT_SELECTED) — reparation modeling absent |
| `Argument` | Structured argument with derivation witness | `claim`, `rule`, `support_facts`, `sources`, `derivation_witness` — argument structure absent |
| `Attack` | Typed attack between arguments | `AttackKind` (REBUTTAL/EXCEPTION_DEFEAT/PRIORITY_DEFEAT) — attack typing absent |
| `Decision` | Accepted/rejected argument sets | `DecisionStatus` (PROVED/REFUTED/UNDECIDED/TAINTED) — decision semantics absent |
| `Certificate` | Auditable certificate with provenance | `model_hash`, `input_hash`, `grounded_label`, `provenance`, `temporal_record`, `jurisdiction_record` — entire audit trail absent |

---

## 3. Evidence Chain Loss

### 3.1 Proof Trace

| Aspect | Canonical | Production |
|--------|-----------|------------|
| Derivation witness | `Argument.derivation_witness: str` | `LegalClaim.proof_trace: List[Dict]` (different structure) |
| Attack witness | `Certificate.attack_witnesses: List[str]` | **NONE** |
| Grounded label | `Certificate.grounded_label: str` | `LegalClaim.get_trust_label()` (different semantics) |

**Loss**: Production's `proof_trace` is a flat list of execution dictionaries. Canonical's `derivation_witness` is a string identifier linking to a specific derivation step. These serve different purposes and are not interchangeable.

### 3.2 Provenance

| Aspect | Canonical | Production |
|--------|-----------|------------|
| Source reference | `SourceRef(argument_id, source_ids)` in `Certificate.provenance` | `LegalFact.source_anchor: str` (different granularity) |
| Temporal record | `TemporalEntry(rule_id, valid_interval)` in `Certificate.temporal_record` | `LegalRule.valid_from/valid_to` (per-rule, not aggregated) |
| Jurisdiction record | `JurisdictionEntry(rule_id, jurisdiction_id)` in `Certificate.jurisdiction_record` | `LegalRule.jurisdiction` (per-rule, not aggregated) |

**Loss**: No aggregated provenance. Each rule stores its own jurisdiction/validity, but there is no certificate-level record that collects all relevant temporal and jurisdictional constraints for a decision.

### 3.3 Audit Certificate

| Certificate Field | Present in Production? | Notes |
|-------------------|----------------------|-------|
| `model_hash` | **NO** | Would require hashing the LegalModel |
| `input_hash` | **NO** | Would require hashing the input facts |
| `decision` | **NO** | Decision type not produced |
| `derivation_witnesses` | **PARTIAL** | `LegalClaim.execution_trace_id` exists but not aggregated |
| `attack_witnesses` | **NO** | Attack type not produced |
| `grounded_label` | **PARTIAL** | `LegalClaim.get_trust_label()` exists but per-claim, not per-decision |
| `provenance` | **NO** | SourceRef type not produced |
| `temporal_record` | **NO** | TemporalEntry type not produced |
| `jurisdiction_record` | **NO** | JurisdictionEntry type not produced |

**Loss**: The entire audit certificate is absent. No decision can be independently verified without re-running the pipeline.

---

## 4. Adapter Disconnection

`canonical_adapter.py` provides:
- `adapt_jc_rule(jc_rule) → canonical.LegalRule` — maps production → canonical
- `adapt_ir_rule(ir_rule) → canonical.LegalRule` — maps IR → canonical
- `load_canonical_from_yaml(path) → canonical.LegalModel` — loads canonical from YAML
- `canonical_to_json(model) → str` — deterministic JSON serialization
- `canonical_from_json(json_str) → canonical.LegalModel` — deserialization
- `roundtrip(model) → bool` — round-trip test helper

**Import graph** (verified by grep):
```
canonical_adapter.py   →  imported by: NOTHING in production pipeline
canonical_schema.py    →  imported by: canonical_adapter.py, tests/spec/
evaluator.py           →  imports neither canonical_adapter nor canonical_schema
stratified_evaluator.py → imports neither
argumentation.py       →  imports neither
```

The adapter exists as dead code. The production pipeline has no bridge to the canonical contract.

---

## 5. Modality Enum Divergence

| Value | Canonical `Modality` | Production `NormModality` |
|-------|---------------------|--------------------------|
| `UNKNOWN` | **NO** | YES |
| `OBLIGATION` | YES | YES |
| `PROHIBITION` | YES | YES |
| `PERMISSION` | YES | YES |
| `CONSTITUTIVE` | YES | YES |

Production defaults to `UNKNOWN` when modality is not detected. Canonical does not have this value — any production rule with `UNKNOWN` modality cannot be represented in the canonical schema without data loss or validation failure.

---

## 6. Field Name Mapping Summary

| Canonical Name | Production Name | Semantic? | Cross-system Impact |
|----------------|----------------|-----------|-------------------|
| `LegalFact.content` | `LegalFact.description` | YES | Adapter must rename |
| `LegalClaim.content` | `LegalClaim.description` | YES | Adapter must rename |
| `LegalClaim.claimant` | — | — | **LOST** — cannot reconstruct |
| `LegalRule.premises` | `LegalRule.premise_atoms` | YES | Adapter must rename |
| `LegalRule.conclusion` | `LegalRule.head_claim` | YES | Adapter must rename |
| `LegalRule.source` | — | — | **LOST** — cannot reconstruct |
| `LegalRule.modality` (Modality) | `LegalRule.norm_modality` (str) | TYPE+NAME | Adapter must convert |
| `LegalRule.valid_interval` (TimeInterval) | `valid_from + valid_to` (str+str) | TYPE+SPLIT | Adapter must merge+convert |

---

## 7. Pipeline Output vs Canonical Output

### What the production pipeline actually emits (when not crashing):

```
StratifiedEvaluator.evaluate(state: IRState) → List[Dict]
  Stage 1: evaluate_horn()     → LegalClaim objects (in horn_state.claims)
  Stage 2: build_attack_graph  → CRASHES (P0-G04)
  Stage 3: grounded_extension  → NOT REACHED
  Stage 4: trust_label update  → NOT REACHED
```

### What it would emit if Stage 2 were fixed:

```
  Stage 1: LegalClaim objects with proof_trace, confidence, epistemic_status
  Stage 2: Attack edges (list of tuples) — but NOT canonical Attack objects
  Stage 3: Accepted/rejected claim IDs — but NOT canonical Decision objects
  Stage 4: Trust labels on LegalClaim — but NOT canonical Certificate
```

**Even with all 4 stages working, the pipeline does not produce:**
- `Argument` objects (structured arguments with derivation witnesses)
- `Attack` objects (typed attacks with AttackKind)
- `Decision` objects (with accepted/rejected argument lists)
- `Certificate` objects (with provenance, temporal record, jurisdiction record)
- `LegalNorm`, `Defense`, `Priority`, `Violation`, `Reparation` objects

---

## 8. Gap Classification

| Gap | Severity | Type | Fix Phase |
|-----|----------|------|-----------|
| 10/12 canonical types absent from production types.py | **Critical** | Missing types | P7-G01/P7-G02 |
| No Argument/Attack/Decision/Certificate production | **Critical** | Missing pipeline output | P7-G01 |
| Canonical adapter not imported | **High** | Dead code | P7-G02 |
| LegalFact: `content` → `description` rename | **High** | Field mismatch | P7-G02 |
| LegalClaim: `content` → `description` rename | **High** | Field mismatch | P7-G02 |
| LegalRule: `premises` → `premise_atoms` rename | **High** | Field mismatch | P7-G02 |
| LegalRule: `conclusion` → `head_claim` rename | **High** | Field mismatch | P7-G02 |
| LegalRule: `source` absent | **High** | Lost field | P7-G02 |
| LegalRule: `modality` enum vs str | **Medium** | Type mismatch | P7-G02 |
| LegalRule: `valid_interval` vs split strings | **Medium** | Type mismatch | P7-G02 |
| Modality `UNKNOWN` not in canonical | **Medium** | Enum divergence | P7-G02 |
| No audit certificate | **High** | Missing evidence chain | P7-G03 |
| No aggregated provenance | **Medium** | Missing evidence chain | P7-G03 |

---

## 9. Verdict

| Criterion | Result |
|-----------|--------|
| Production path retains all canonical types? | **NO** — 2/14 types present |
| Production pipeline produces canonical outputs? | **NO** — 0 downstream types produced |
| Field names match canonical? | **NO** — 5 name mismatches, 1 absence |
| Evidence chain complete? | **NO** — no Certificate, no aggregated provenance |
| Canonical adapter bridges the gap? | **NO** — never imported |
| Schema loss report written? | **YES** |
