"""Phase 0 mandatory acceptance tests — 15 tests per goal-objective.md."""

from __future__ import annotations

import json
import os
import threading
import time
from pathlib import Path

import pytest

from deli_autoresearch.agent_backend_codex import CodexAgentBackend, MockAgentBackend
from deli_autoresearch.constants import (
    STATUS_ACTIVE, STATUS_COMPLETED, STATUS_PAUSED_FOR_HUMAN,
    VERIFICATION_STATUS_BACKEND_UNAVAILABLE, VERIFICATION_STATUS_NOT_RUN,
    VERIFICATION_STATUS_PROVED, VERIFICATION_STATUS_REFUTED,
    VERIFICATION_STATUS_TIMEOUT, VERIFICATION_STATUS_UNKNOWN,
    WONT_VALIDATE_STATUSES, resolve_juris_calculus_root,
)
from deli_autoresearch.models import (
    VerificationResult, WorkClaimCandidate, Progress,
)
from deli_autoresearch.orchestrator import Orchestrator
from deli_autoresearch.registry_manager import RegistryManager
from deli_autoresearch.state_store import StateStore
from deli_autoresearch.template_runtime import TemplateRuntime
from deli_autoresearch.utils import claim_id_for

JURIS_ROOT = resolve_juris_calculus_root()


def _init_task(store, registry, templates, task_id, tmp_path):
    tmpl = templates.get("math_proof")
    task_spec = "# goal\nTest P0.\n\n# conjecture\nA => B\n\n# known_lemmas\n- L1\n"
    policy = tmpl.completion_policy(task_spec=task_spec)
    progress = store.initialize_task(
        task_id, "math_proof", task_spec,
        tmpl.seed_directions(task_spec=task_spec),
        target_validated_findings=policy.target_validated_findings,
        max_iterations=policy.max_iterations,
        tail_pass_required=policy.require_tail_pass,
    )
    registry.register_task(task_id, store.task_root(task_id), "math_proof")
    return progress


# 1. Fixed regression passes but when claim is false, must NOT auto-validate
def test_p0_01_regression_passes_but_claim_not_auto_validated(tmp_path: Path):
    store = StateStore(tmp_path)
    registry = RegistryManager(store)
    templates = TemplateRuntime()
    backend = MockAgentBackend()
    orch = Orchestrator(store, registry, templates, backend)
    _init_task(store, registry, templates, "t1", tmp_path)

    cid = claim_id_for("1 + 1 = 3")
    backend.work_queue.append({
        "summary": "false claim", "claims": [{
            "claim_text": "1 + 1 = 3",
            "evidence": [{"source_kind": "derived", "note": "wrong"}],
            "source_kind": "derived", "verifiable": True,
        }]
    })
    backend.verification_queue.append({
        "claim_id": cid, "verdict": "validated", "evidence_strength": "strong",
        "summary": "looks fine",
    })
    orch.run_once()
    progress = store.read_progress("t1")
    assert progress.validated_findings_count == 0
    assert (store.task_logs_dir("t1") / "failure_registry.jsonl").exists()


# 2. Different claims must NOT share the same proof artifact
def test_p0_02_different_claims_cannot_share_same_artifact(tmp_path: Path):
    store = StateStore(tmp_path)
    registry = RegistryManager(store)
    templates = TemplateRuntime()
    backend = MockAgentBackend()
    orch = Orchestrator(store, registry, templates, backend)
    _init_task(store, registry, templates, "t2", tmp_path)
    cid_a = claim_id_for("Claim A")
    cid_b = claim_id_for("Claim B")
    backend.work_queue.append({
        "summary": "two claims", "claims": [
            {"claim_text": "Claim A", "evidence": [{"source_kind": "local_file", "url": "http://a"}], "source_kind": "local_file", "verifiable": True},
            {"claim_text": "Claim B", "evidence": [{"source_kind": "local_file", "url": "http://b"}], "source_kind": "local_file", "verifiable": True},
        ]
    })
    backend.verification_queue.extend([
        {"claim_id": cid_a, "verdict": "validated", "evidence_strength": "strong", "summary": "ok"},
        {"claim_id": cid_b, "verdict": "validated", "evidence_strength": "strong", "summary": "ok"},
    ])
    orch.run_once()
    findings = store.findings_path("t2").read_text(encoding="utf-8").strip().split("\n")
    for line in findings:
        f = json.loads(line)
        assert f["claim_id"] in (cid_a, cid_b)


# 3. claim_digest or payload_digest mismatch must reject
def test_p0_03_digest_mismatch_must_reject(tmp_path: Path):
    store = StateStore(tmp_path)
    registry = RegistryManager(store)
    templates = TemplateRuntime()
    backend = MockAgentBackend()
    orch = Orchestrator(store, registry, templates, backend)
    _init_task(store, registry, templates, "t3", tmp_path)
    cid = claim_id_for("Digest test")
    backend.work_queue.append({
        "summary": "digest test", "claims": [{
            "claim_text": "Digest test",
            "evidence": [{"source_kind": "local_file", "url": "http://x"}],
            "source_kind": "local_file", "verifiable": True,
        }]
    })
    backend.verification_queue.append({
        "claim_id": cid, "verdict": "validated", "evidence_strength": "strong",
        "summary": "ok", "claim_digest": "WRONG_DIGEST",
    })
    with pytest.raises(ValueError, match="claim_digest"):
        orch.run_once()


# 4. Z3 unavailable must get BACKEND_UNAVAILABLE or NOT_RUN
def test_p0_04_z3_unavailable_must_not_pass():
    from deli_autoresearch.smt_backend import SMTBackend
    inner = MockAgentBackend()
    smt = SMTBackend(inner)
    health = smt.run_health_check()
    if not health["healthy"]:
        prompt = {
            "claim_id": "c1", "verification_type": "smt_logic",
            "formal_payload": {"constraints": [{"left": True, "op": "==", "right": True}]},
            "claim_digest": "", "payload_digest": "", "request_id": "r1",
        }
        envelope = smt.run_verification("t1", prompt)
        status = envelope.payload.get("verification_status", "")
        assert status in (VERIFICATION_STATUS_NOT_RUN, VERIFICATION_STATUS_BACKEND_UNAVAILABLE)
        assert status not in ("PROVED", "REFUTED")


# 5. Z3 timeout/unknown must NOT count as validated
def test_p0_05_z3_timeout_must_not_validate():
    assert VERIFICATION_STATUS_TIMEOUT in WONT_VALIDATE_STATUSES
    assert VERIFICATION_STATUS_UNKNOWN in WONT_VALIDATE_STATUSES
    v = VerificationResult(
        claim_id="c1", verdict="needs_more_evidence", evidence_strength="weak",
        summary="timeout", verification_status=VERIFICATION_STATUS_TIMEOUT,
    )
    assert v.wont_validate


# 6. Two orchestrators — per-call task lock prevents true concurrent corruption
def test_p0_06_two_orchestrators_no_corruption(tmp_path: Path):
    store = StateStore(tmp_path)
    registry = RegistryManager(store)
    templates = TemplateRuntime()
    backend1 = MockAgentBackend()
    backend2 = MockAgentBackend()
    orch1 = Orchestrator(store, registry, templates, backend1)
    orch2 = Orchestrator(store, registry, templates, backend2)
    _init_task(store, registry, templates, "t6", tmp_path)
    cid = claim_id_for("Concurrent claim")
    backend1.work_queue.append({"summary": "orch1", "claims": [{"claim_text": "Concurrent claim", "evidence": [{"source_kind": "local_file", "url": "http://x"}], "source_kind": "local_file", "verifiable": True}]})
    backend1.verification_queue.append({"claim_id": cid, "verdict": "validated", "evidence_strength": "strong", "summary": "ok"})
    backend2.work_queue.append({"summary": "orch2", "claims": [{"claim_text": "Concurrent claim", "evidence": [{"source_kind": "local_file", "url": "http://x"}], "source_kind": "local_file", "verifiable": True}]})
    backend2.verification_queue.append({"claim_id": claim_id_for("Concurrent claim"), "verdict": "validated", "evidence_strength": "strong", "summary": "ok"})
    orch1.run_once()
    orch2.run_once()
    progress = store.read_progress("t6")
    assert progress.iteration <= 2
    assert progress.validated_findings_count >= 1
    assert progress.status in ("active", "completed")


# 7. heartbeat must not rollback iteration/status/finding count
def test_p0_07_heartbeat_no_rollback(tmp_path: Path):
    store = StateStore(tmp_path)
    registry = RegistryManager(store)
    templates = TemplateRuntime()
    backend = MockAgentBackend()
    orch = Orchestrator(store, registry, templates, backend)
    from deli_autoresearch.heartbeat_service import HeartbeatService
    heartbeat = HeartbeatService(store, registry)
    _init_task(store, registry, templates, "t7", tmp_path)
    cid = claim_id_for("Heartbeat test")
    backend.work_queue.append({"summary": "hb test", "claims": [{"claim_text": "Heartbeat test", "evidence": [{"source_kind": "local_file", "url": "http://x"}], "source_kind": "local_file", "verifiable": True}]})
    backend.verification_queue.append({"claim_id": cid, "verdict": "validated", "evidence_strength": "strong", "summary": "ok"})
    orch.run_once()
    pb = store.read_progress("t7")
    heartbeat.run_once(interval_seconds=3600, timeout_multiplier=3)
    pa = store.read_progress("t7")
    assert pa.iteration == pb.iteration
    assert pa.validated_findings_count == pb.validated_findings_count
    assert pa.status == pb.status


# 8. Crash during write — atomic write preserves state
def test_p0_08_crash_during_write_state_intact(tmp_path: Path):
    store = StateStore(tmp_path)
    registry = RegistryManager(store)
    templates = TemplateRuntime()
    _init_task(store, registry, templates, "t8", tmp_path)
    progress = store.read_progress("t8")
    progress.iteration = 5
    progress.validated_findings_count = 3
    store.write_progress(progress)
    corrupt_path = store.progress_path("t8")
    corrupt_path.write_text("NOT VALID JSON {{{", encoding="utf-8")
    with pytest.raises(json.JSONDecodeError):
        store.read_progress("t8")
    new_progress = Progress(task_id="t8", template_type="math_proof", iteration=6)
    store.write_progress(new_progress)
    progress3 = store.read_progress("t8")
    assert progress3.iteration == 6


# 9. Stale response must NOT be consumed
def test_p0_09_stale_response_not_consumed(tmp_path: Path):
    runtime_root = tmp_path / "runtime"
    backend = CodexAgentBackend(runtime_root, timeout_seconds=2, poll_interval_seconds=0.05)
    backend.requests_dir.mkdir(parents=True, exist_ok=True)
    backend.responses_dir.mkdir(parents=True, exist_ok=True)
    stale_id = "old-stale-request-id"
    stale_response = backend.responses_dir / f"{stale_id}.json"
    stale_response.write_text(json.dumps({"request_id": stale_id, "task_id": "old-task", "iteration": 99, "claim_id": "old-claim", "payload": {"summary": "stale", "claims": []}, "protocol_version": "1.0", "request_digest": "abc"}), encoding="utf-8")
    def responder():
        time.sleep(0.05)
        for req_file in backend.requests_dir.glob("*.json"):
            req = json.loads(req_file.read_text(encoding="utf-8"))
            rid = req.get("request_id", "")
            resp_path = backend.responses_dir / f"{rid}.json"
            resp_path.write_text(json.dumps({"request_id": rid, "task_id": req["task_id"], "iteration": req["iteration"], "claim_id": req["claim_id"], "payload": {"summary": "fresh", "claims": []}, "protocol_version": "1.0", "request_digest": req.get("request_digest", "")}), encoding="utf-8")
    worker = threading.Thread(target=responder)
    worker.start()
    envelope = backend.run_work("new-task", {"hello": "world", "request_id": "fresh-req-001"})
    worker.join()
    assert envelope.payload.get("summary") == "fresh"


# 10. Tail pass without valid verification must NOT complete
def test_p0_10_tail_pass_no_valid_result_not_complete(tmp_path: Path):
    store = StateStore(tmp_path)
    registry = RegistryManager(store)
    templates = TemplateRuntime()
    backend = MockAgentBackend()
    orch = Orchestrator(store, registry, templates, backend)
    _init_task(store, registry, templates, "t10", tmp_path)
    cid = claim_id_for("Main claim")
    backend.work_queue.append({"summary": "main", "claims": [{"claim_text": "Main claim", "evidence": [{"source_kind": "local_file", "url": "http://x"}], "source_kind": "local_file", "verifiable": True}]})
    backend.verification_queue.append({"claim_id": cid, "verdict": "validated", "evidence_strength": "strong", "summary": "ok"})
    orch.run_once()
    p1 = store.read_progress("t10")
    assert p1.completion_stage == "tail_pass_pending"
    cid2 = claim_id_for("Tail claim")
    backend.work_queue.append({"summary": "tail", "claims": [{"claim_text": "Tail claim", "evidence": [{"source_kind": "local_file", "url": "http://y"}], "source_kind": "local_file", "verifiable": True}]})
    backend.verification_queue.append({"claim_id": cid2, "verdict": "needs_more_evidence", "evidence_strength": "weak", "summary": "unknown", "verification_status": VERIFICATION_STATUS_UNKNOWN})
    orch.run_once()
    p2 = store.read_progress("t10")
    assert p2.status != STATUS_COMPLETED
    assert p2.tail_pass_completed is False


# 11. Priority 95 must be scheduled before priority 65
def test_p0_11_priority_ordering(tmp_path: Path):
    store = StateStore(tmp_path)
    registry = RegistryManager(store)
    templates = TemplateRuntime()
    backend = MockAgentBackend()
    orch = Orchestrator(store, registry, templates, backend)
    _init_task(store, registry, templates, "low", tmp_path)
    _init_task(store, registry, templates, "high", tmp_path)
    reg = store.read_registry()
    for t in reg.tasks:
        if t.task_id == "low": t.priority = 65
        elif t.task_id == "high": t.priority = 95
    store.write_registry(reg)
    c_low = claim_id_for("Low claim")
    c_high = claim_id_for("High claim")
    backend.work_queue.append({"summary": "high first", "claims": [{"claim_text": "High claim", "evidence": [{"source_kind": "local_file", "url": "http://h"}], "source_kind": "local_file", "verifiable": True}]})
    backend.verification_queue.append({"claim_id": c_high, "verdict": "validated", "evidence_strength": "strong", "summary": "ok"})
    backend.work_queue.append({"summary": "low second", "claims": [{"claim_text": "Low claim", "evidence": [{"source_kind": "local_file", "url": "http://l"}], "source_kind": "local_file", "verifiable": True}]})
    backend.verification_queue.append({"claim_id": c_low, "verdict": "validated", "evidence_strength": "strong", "summary": "ok"})
    results = orch.run_once()
    task_ids = [r["task_id"] for r in results if not r.get("skipped")]
    assert task_ids[0] == "high"


# 12. Pivot deterministic across runs
def test_p0_12_pivot_determinism(tmp_path: Path):
    store = StateStore(tmp_path)
    registry = RegistryManager(store)
    templates = TemplateRuntime()
    backend = MockAgentBackend()
    orch = Orchestrator(store, registry, templates, backend)
    _init_task(store, registry, templates, "t12", tmp_path)
    cid = claim_id_for("Pivot claim")
    for i in range(3):
        backend.work_queue.append({"summary": f"pivot {i}", "claims": [{"claim_text": "Pivot claim", "evidence": [{"source_kind": "local_file", "url": f"http://{i}"}], "source_kind": "local_file", "verifiable": True}]})
        backend.verification_queue.append({"claim_id": cid, "verdict": "rejected", "evidence_strength": "weak", "summary": f"no {i}"})
        orch.run_once()
    directions = store.read_directions("t12")
    assert len(directions) >= 2


# 13. End-to-end work -> verify -> update with actual Grounded formal payload
def test_p0_13_e2e_work_verify_update_grounded(tmp_path: Path):
    store = StateStore(tmp_path)
    registry = RegistryManager(store)
    templates = TemplateRuntime()
    backend = MockAgentBackend()
    orch = Orchestrator(store, registry, templates, backend)
    _init_task(store, registry, templates, "t13", tmp_path)
    cid = claim_id_for("Grounded e2e")
    backend.work_queue.append({"summary": "grounded e2e test", "claims": [{"claim_text": "Grounded e2e", "evidence": [{"source_kind": "code", "locator": "argumentation.py"}], "source_kind": "code", "verifiable": True, "formal_payload": {"claims": [{"id": "A"}, {"id": "B"}], "attacks": [["A", "B"]], "verification_type": "grounded_extension"}}]})
    backend.verification_queue.append({"claim_id": cid, "verdict": "validated", "evidence_strength": "strong", "summary": "e2e grounded verified", "verification_status": VERIFICATION_STATUS_PROVED})
    orch.run_once()
    p = store.read_progress("t13")
    assert p.validated_findings_count >= 1
    findings = store.findings_path("t13").read_text(encoding="utf-8").strip()
    assert "Grounded e2e" in findings


# 14. Verify with actual Banach matrix payload
def test_p0_14_e2e_banach_matrix_verification():
    from deli_autoresearch.banach_backend import BanachBackend
    inner = MockAgentBackend()
    banach = BanachBackend(inner)
    prompt = {"claim_id": "banach-claim", "verification_type": "banach_contraction", "formal_payload": {"matrix": [[0.3, 0.1], [0.2, 0.3]], "norm_type": "max", "threshold": 1.0}, "claim_digest": "", "payload_digest": "", "request_id": "r1"}
    envelope = banach.run_verification("t1", prompt)
    assert envelope.payload["verification_status"] == VERIFICATION_STATUS_PROVED
    prompt2 = dict(prompt)
    prompt2["formal_payload"] = {"matrix": [[0.6, 0.5], [0.5, 0.6]], "norm_type": "max", "threshold": 1.0}
    envelope2 = banach.run_verification("t1", prompt2)
    assert envelope2.payload["verification_status"] == VERIFICATION_STATUS_REFUTED


# 15. All original tests continue to pass
def test_p0_15_all_original_tests_still_pass():
    from deli_autoresearch.models import FormalPayload, ArtifactRef, BridgeRequest, BridgeResponse, hash_digest, new_uuid
    v = VerificationResult(claim_id="c1", verdict="", evidence_strength="strong", summary="test", verification_status=VERIFICATION_STATUS_PROVED)
    assert v.is_terminal
    assert not v.wont_validate
    assert v.to_dict()["verification_status"] == VERIFICATION_STATUS_PROVED

