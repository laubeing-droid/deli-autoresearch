"""Tests for legal_proof template and juris-calculus bridge."""

from __future__ import annotations

import json
from pathlib import Path

from deli_autoresearch.agent_backend_codex import MockAgentBackend
from deli_autoresearch.constants import (
    LEGAL_DIRECTION_TYPES,
    ALL_DIRECTION_TYPES,
    LEGAL_STRONG_SOURCE_KINDS,
    STATUS_PAUSED_FOR_HUMAN,
)
from deli_autoresearch.juris_calculus_bridge import JurisCalculusBridge, RegressionReport
from deli_autoresearch.juris_calculus_backend import JurisCalculusBackend
from deli_autoresearch.orchestrator import Orchestrator
from deli_autoresearch.registry_manager import RegistryManager
from deli_autoresearch.state_store import StateStore
from deli_autoresearch.template_runtime import TemplateRuntime
from deli_autoresearch.utils import claim_id_for


JURIS_ROOT = Path(r"D:\Codex\juris-calculus")


# ---- helpers ----

def build_legal_runtime(tmp_path: Path):
    store = StateStore(tmp_path)
    registry = RegistryManager(store)
    templates = TemplateRuntime()
    backend = MockAgentBackend()
    orchestrator = Orchestrator(store, registry, templates, backend)
    return store, registry, templates, backend, orchestrator


def init_legal_task(tmp_path: Path, task_id: str = "g9-test"):
    store, registry, templates, backend, orchestrator = build_legal_runtime(tmp_path)
    task_spec = (
        "# Goal\nExtend grounded semantics for cycles.\n\n"
        "# Target Semantics\nDung grounded.\n\n"
        "# Attack Graph Class\nBidirectional and triangle cycles.\n\n"
        "# Verification Engine\njuris-calculus.\n\n"
        "# Known Lemmas\n- Dung 1995.\n\n"
        "# MVM Breakthrough\nOdd-cycle-free convergence.\n"
    )
    template = templates.get("legal_proof")
    policy = template.completion_policy(task_spec=task_spec)
    progress = store.initialize_task(
        task_id,
        "legal_proof",
        task_spec,
        template.seed_directions(task_spec=task_spec),
        target_validated_findings=policy.target_validated_findings,
        max_iterations=policy.max_iterations,
        tail_pass_required=policy.require_tail_pass,
    )
    registry.register_task(task_id, store.task_root(task_id), "legal_proof")
    return store, registry, templates, backend, orchestrator, progress


# ---- constants ----

def test_legal_direction_types_exist():
    assert "scc_decomposition" in LEGAL_DIRECTION_TYPES
    assert "cf2_semantics" in LEGAL_DIRECTION_TYPES
    assert "semiring_substitution" in LEGAL_DIRECTION_TYPES
    assert len(LEGAL_DIRECTION_TYPES) >= 5


def test_all_direction_types_merges_base_and_legal():
    assert LEGAL_DIRECTION_TYPES.issubset(ALL_DIRECTION_TYPES)
    assert "opposite_hypothesis" in ALL_DIRECTION_TYPES  # from base


def test_legal_strong_source_kinds_include_engine_types():
    assert "z3_counterexample" in LEGAL_STRONG_SOURCE_KINDS
    assert "lean_proof" in LEGAL_STRONG_SOURCE_KINDS
    assert "juris_test_pass" in LEGAL_STRONG_SOURCE_KINDS
    assert "web" in LEGAL_STRONG_SOURCE_KINDS  # from base


# ---- template ----

def test_legal_proof_template_registered():
    runtime = TemplateRuntime()
    template = runtime.get("legal_proof")
    assert template.name == "legal_proof"


def test_legal_proof_schema_requires_legal_sections():
    runtime = TemplateRuntime()
    schema = runtime.get("legal_proof").build_task_spec_schema()
    required = schema["required_sections"]
    assert "target_semantics" in required
    assert "attack_graph_class" in required
    assert "verification_engine" in required
    assert "known_lemmas" in required
    assert "mvm_breakthrough" in required


def test_legal_proof_seed_directions_include_scc():
    runtime = TemplateRuntime()
    directions = runtime.get("legal_proof").seed_directions(task_spec="dummy")
    types = {d.strategy_type for d in directions}
    assert "scc_decomposition" in types
    assert "cf2_semantics" in types
    assert len(directions) >= 5


def test_legal_proof_initial_direction_is_scc():
    runtime = TemplateRuntime()
    d = runtime.get("legal_proof").initial_direction()
    assert d.strategy_type == "scc_decomposition"


def test_legal_proof_completion_policy_target_3():
    runtime = TemplateRuntime()
    policy = runtime.get("legal_proof").completion_policy(task_spec="dummy")
    assert policy.target_validated_findings == 3
    assert policy.max_iterations == 20
    assert policy.require_tail_pass is True


def test_general_research_work_prompt_contract_is_loose():
    runtime = TemplateRuntime()
    template = runtime.get("general_research")
    contract = template.work_prompt_contract()
    assert contract["strict_json"] is True
    assert contract["formal_payload"]["required"] is False
    assert "claim_text" in contract["required_fields"]
    assert template.validate_work_candidate({"claim_text": "bare minimum"}) == []
    assert template.validate_work_candidate({
        "claim_text": "with optional structure",
        "evidence": [{"note": "any list shape is fine here"}],
        "formal_payload": {"anything": "json"},
    }) == []
    assert any(
        "evidence must be a list when provided" in error
        for error in template.validate_work_candidate({
            "claim_text": "bad evidence",
            "evidence": "not-a-list",
        })
    )
    assert any(
        "formal_payload must be a structured object when provided" in error
        for error in template.validate_work_candidate({
            "claim_text": "bad payload",
            "formal_payload": "not-a-dict",
        })
    )


def test_legal_proof_work_prompt_contract_requires_claim_bound_payload():
    runtime = TemplateRuntime()
    contract = runtime.get("legal_proof").work_prompt_contract()
    assert contract["strict_json"] is True
    assert contract["required_fields"] == [
        "claim_text",
        "evidence",
        "source_kind",
        "verifiable",
        "formal_payload",
    ]
    assert contract["formal_payload"]["required"] is True
    assert contract["formal_payload"]["type"] == "object"
    assert contract["formal_payload"]["required_keys"] == [
        "claims",
        "attacks",
        "verification_type",
    ]
    assert contract["formal_payload"]["verification_type"] == "grounded_extension"
    assert contract["formal_payload"]["claims"]["required"] is True
    assert contract["formal_payload"]["claims"]["non_empty"] is True
    assert contract["formal_payload"]["claims"]["entry_required_fields"] == ["id"]
    assert contract["formal_payload"]["attacks"]["required"] is True
    assert contract["formal_payload"]["attacks"]["non_empty"] is True


def test_legal_proof_validate_work_candidate_rejects_missing_contract_payload():
    runtime = TemplateRuntime()
    template = runtime.get("legal_proof")

    valid_candidate = {
        "claim_text": "A and B form a grounded-extension cycle case.",
        "evidence": [
            {"source_kind": "code", "locator": "argumentation.py:42"},
        ],
        "source_kind": "code",
        "verifiable": True,
        "formal_payload": {
            "claims": [{"id": "A"}, {"id": "B"}],
            "attacks": [["A", "B"]],
            "verification_type": "grounded_extension",
        },
    }
    assert template.validate_work_candidate(valid_candidate) == []

    missing_formal_payload = {
        "claim_text": "A and B form a grounded-extension cycle case.",
        "evidence": [
            {"source_kind": "code", "locator": "argumentation.py:42"},
        ],
        "source_kind": "code",
        "verifiable": True,
    }
    errors = template.validate_work_candidate(missing_formal_payload)
    assert any("formal_payload must be a structured object" in e for e in errors)

    missing_claims = {
        "claim_text": "A and B form a grounded-extension cycle case.",
        "evidence": [
            {"source_kind": "code", "locator": "argumentation.py:42"},
        ],
        "source_kind": "code",
        "verifiable": True,
        "formal_payload": {
            "attacks": [["A", "B"]],
            "verification_type": "grounded_extension",
        },
    }
    errors = template.validate_work_candidate(missing_claims)
    assert any("formal_payload.claims must be a non-empty list" in e for e in errors)

    missing_attacks = {
        "claim_text": "A and B form a grounded-extension cycle case.",
        "evidence": [
            {"source_kind": "code", "locator": "argumentation.py:42"},
        ],
        "source_kind": "code",
        "verifiable": True,
        "formal_payload": {
            "claims": [{"id": "A"}, {"id": "B"}],
            "verification_type": "grounded_extension",
        },
    }
    errors = template.validate_work_candidate(missing_attacks)
    assert any("formal_payload.attacks must be a non-empty list" in e for e in errors)

    empty_claims = {
        "claim_text": "A and B form a grounded-extension cycle case.",
        "evidence": [
            {"source_kind": "code", "locator": "argumentation.py:42"},
        ],
        "source_kind": "code",
        "verifiable": True,
        "formal_payload": {
            "claims": [],
            "attacks": [["A", "B"]],
            "verification_type": "grounded_extension",
        },
    }
    errors = template.validate_work_candidate(empty_claims)
    assert any("formal_payload.claims must be a non-empty list" in e for e in errors)

    empty_attacks = {
        "claim_text": "A and B form a grounded-extension cycle case.",
        "evidence": [
            {"source_kind": "code", "locator": "argumentation.py:42"},
        ],
        "source_kind": "code",
        "verifiable": True,
        "formal_payload": {
            "claims": [{"id": "A"}, {"id": "B"}],
            "attacks": [],
            "verification_type": "grounded_extension",
        },
    }
    errors = template.validate_work_candidate(empty_attacks)
    assert any("formal_payload.attacks must be a non-empty list" in e for e in errors)


def test_legal_proof_stall_rules_detect_semantic_collapse():
    runtime = TemplateRuntime()
    template = runtime.get("legal_proof")

    class P:
        iteration = 1

    vrs = [
        {"verdict": "needs_more_evidence", "supporting_evidence": [{"source_kind": "model_generated"}]},
        {"verdict": "needs_more_evidence", "supporting_evidence": [{"source_kind": "model_generated"}]},
    ]
    warnings = template.template_stall_rules(progress=P(), verification_results=vrs)
    assert any("semantic_collapse" in w for w in warnings)


def test_legal_proof_validate_finding_rules_requires_evidence():
    runtime = TemplateRuntime()
    template = runtime.get("legal_proof")
    errors = template.validate_finding_rules({"claim": "test", "evidence": []})
    assert any("require at least one" in e for e in errors)


def test_legal_proof_validate_finding_rules_requires_source_kind():
    runtime = TemplateRuntime()
    template = runtime.get("legal_proof")
    errors = template.validate_finding_rules({
        "claim": "test",
        "evidence": [{"note": "no source_kind"}],
    })
    assert any("source_kind" in e for e in errors)


# ---- bridge ----

def test_bridge_dag_regression():
    if not JURIS_ROOT.exists():
        return
    bridge = JurisCalculusBridge(JURIS_ROOT)
    cases = bridge.dag_linear_cases()
    for case in cases:
        result = bridge.run_test_case(
            case["name"], case["claims"], case["attacks"],
            expected_accepted=case.get("expected_accepted"),
            expected_undecided=case.get("expected_undecided"),
        )
        assert result.passed, f"{case['name']} failed: {result.error}"


def test_bridge_bidirectional_cycle():
    if not JURIS_ROOT.exists():
        return
    bridge = JurisCalculusBridge(JURIS_ROOT)
    cases = bridge.bidirectional_cycle_cases()
    for case in cases:
        result = bridge.run_test_case(
            case["name"], case["claims"], case["attacks"],
            expected_accepted=case.get("expected_accepted"),
            expected_undecided=case.get("expected_undecided"),
        )
        assert result.passed, f"{case['name']} failed: accepted={result.accepted}, undecided={result.undecided}"


def test_bridge_triangle_cycle():
    if not JURIS_ROOT.exists():
        return
    bridge = JurisCalculusBridge(JURIS_ROOT)
    cases = bridge.triangle_cycle_cases()
    for case in cases:
        result = bridge.run_test_case(
            case["name"], case["claims"], case["attacks"],
            expected_accepted=case.get("expected_accepted"),
            expected_undecided=case.get("expected_undecided"),
        )
        assert result.passed, f"{case['name']} failed: accepted={result.accepted}, undecided={result.undecided}"


def test_bridge_full_regression():
    if not JURIS_ROOT.exists():
        return
    bridge = JurisCalculusBridge(JURIS_ROOT)
    report = bridge.run_full_regression()
    assert report.all_passed, f"Regression failed: {[r.test_name for r in report.results if not r.passed]}"
    assert report.total >= 5


# ---- backend ----

def test_hybrid_backend_delegates_work_to_inner():
    if not JURIS_ROOT.exists():
        return
    inner = MockAgentBackend()
    inner.work_queue.append({"summary": "test", "claims": []})
    hybrid = JurisCalculusBackend(inner, JURIS_ROOT)
    envelope = hybrid.run_work("t1", {"task": "test"})
    assert envelope.payload["summary"] == "test"


def test_hybrid_backend_runs_local_engine_for_verification():
    if not JURIS_ROOT.exists():
        return
    inner = MockAgentBackend()
    hybrid = JurisCalculusBackend(inner, JURIS_ROOT)
    prompt = {
        "claim_id": "claim_abc",
        "claim": "test claim",
        "verification_type": "grounded_extension",
        "formal_payload": {
            "claims": [{"id": "A"}],
            "attacks": [],
            "expected_properties": {"expected_accepted": ["A"]},
        },
        "claim_digest": "abc",
        "payload_digest": "",
        "request_id": "req-001",
        "request_digest": "rd-001",
    }
    envelope = hybrid.run_verification("t1", prompt)
    assert envelope.payload["verdict"] in ("validated", "rejected")
    assert "verification_status" in envelope.payload


def test_hybrid_backend_fallback_to_inner_when_no_flag():
    if not JURIS_ROOT.exists():
        return
    inner = MockAgentBackend()
    inner.verification_queue.append({
        "claim_id": "c1",
        "verdict": "validated",
        "evidence_strength": "strong",
        "summary": "inner handled it",
    })
    hybrid = JurisCalculusBackend(inner, JURIS_ROOT)
    prompt = {"claim_id": "c1", "claim": "test"}
    envelope = hybrid.run_verification("t1", prompt)
    assert envelope.payload["summary"] == "inner handled it"


# ---- orchestrator integration ----

def test_legal_proof_task_init_creates_state(tmp_path: Path):
    store, registry, templates, backend, orchestrator, progress = init_legal_task(tmp_path)
    assert store.progress_path(progress.task_id).exists()
    assert progress.template_type == "legal_proof"
    assert progress.target_validated_findings == 3


def test_legal_proof_orchestrator_runs_with_mock(tmp_path: Path):
    store, registry, templates, backend, orchestrator, progress = init_legal_task(tmp_path)
    claim_id = claim_id_for("bidirectional cycle A<->B undecided")
    backend.work_queue.append({
        "summary": "Verify bidirectional cycle handling.",
        "claims": [{
            "claim_text": "bidirectional cycle A<->B undecided",
            "evidence": [
                {"source_kind": "code", "locator": "argumentation.py:42"},
                {"source_kind": "juris_test_pass", "test_name": "bidirectional_A_B"},
            ],
            "source_kind": "code",
            "verifiable": True,
            "support_kind": "new",
            "formal_payload": {
                "claims": [{"id": "A"}, {"id": "B"}],
                "attacks": [["A", "B"]],
                "verification_type": "grounded_extension",
            },
        }],
    })
    backend.verification_queue.append({
        "claim_id": claim_id,
        "verdict": "validated",
        "evidence_strength": "strong",
        "summary": "Regression confirms UNDECIDED for A<->B.",
    })
    results = orchestrator.run_once()
    assert len(results) == 1
    p = store.read_progress(progress.task_id)
    assert p.validated_findings_count >= 1


def test_legal_proof_full_flow_with_engine(tmp_path: Path):
    """Full integration: legal_proof template + JurisCalculusBackend + orchestrator."""
    if not JURIS_ROOT.exists():
        return

    store = StateStore(tmp_path)
    registry = RegistryManager(store)
    templates = TemplateRuntime()
    store.ensure_runtime()

    task_id = "g9-integration"
    task_spec = (
        "# Goal\nVerify G9 fix.\n\n# Target Semantics\nDung.\n\n"
        "# Attack Graph Class\nBidirectional.\n\n# Verification Engine\njuris.\n\n"
        "# Known Lemmas\n- Dung 1995.\n\n# MVM Breakthrough\nOdd-cycle-free.\n"
    )
    template = templates.get("legal_proof")
    policy = template.completion_policy(task_spec=task_spec)
    progress = store.initialize_task(
        task_id, "legal_proof", task_spec,
        template.seed_directions(task_spec=task_spec),
        target_validated_findings=policy.target_validated_findings,
        max_iterations=policy.max_iterations,
        tail_pass_required=policy.require_tail_pass,
    )
    registry.register_task(task_id, store.task_root(task_id), "legal_proof")

    inner = MockAgentBackend()
    inner.work_queue.append({
        "summary": "Verify G9 grounded extension on cycles.",
        "claims": [{
            "claim_text": "grounded_extension correctly returns UNDECIDED for all cycle types",
            "evidence": [
                {"source_kind": "code", "locator": "argumentation.py"},
                {"source_kind": "juris_test_pass", "test_name": "full_regression"},
            ],
            "source_kind": "code",
            "verifiable": True,
            "support_kind": "new",
            "formal_payload": {
                "claims": [{"id": "A"}, {"id": "B"}],
                "attacks": [["A", "B"]],
                "verification_type": "grounded_extension",
            },
        }],
    })

    hybrid = JurisCalculusBackend(inner, JURIS_ROOT)
    orch = Orchestrator(store, registry, templates, hybrid)

    # Patch to use grounded_extension verification type
    original_build = orch._build_verification_prompt
    def patched(task_id, progress, claim_id, claim, candidate, template):
        prompt = original_build(task_id, progress, claim_id, claim, candidate, template)
        prompt["verification_type"] = "grounded_extension"
        return prompt
    orch._build_verification_prompt = patched

    results = orch.run_once()
    assert len(results) == 1

    final = store.read_progress(task_id)
    assert final.validated_findings_count >= 1, f"Expected findings, got {final.validated_findings_count}"

    findings_text = store.findings_path(task_id).read_text(encoding="utf-8").strip()
    assert findings_text, "Expected findings in log"
    finding = json.loads(findings_text.split("\n")[0])
    assert finding["source_kind"] == "code"
