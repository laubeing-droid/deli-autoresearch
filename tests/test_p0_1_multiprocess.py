"""Phase 0.1 real multi-process acceptance tests.

Uses multiprocessing (spawn) on Windows for true cross-process isolation.
"""
from __future__ import annotations
import json, multiprocessing, os, sys, tempfile, time
from pathlib import Path
import subprocess
import pytest

_SRC = str(Path(__file__).resolve().parent.parent / "src")
_PROJ = str(Path(__file__).resolve().parent.parent)


def _worker_hold_lock(workspace_str, hold_seconds, result_queue):
    """Acquire workspace lock, hold for hold_seconds, report LOCK_HELD if unavailable."""
    sys.path.insert(0, _SRC)
    from deli_autoresearch.state_store import StateStore
    from deli_autoresearch.file_lock import ProcessFileLock, LockHeldError
    workspace = Path(workspace_str)
    store = StateStore(workspace)
    try:
        ws_lock = store.acquire_workspace_lock("worker-" + str(os.getpid()))
        with ws_lock:
            result_queue.put({"status": "LOCK_ACQUIRED", "pid": os.getpid()})
            time.sleep(hold_seconds)
    except LockHeldError as e:
        result_queue.put({"status": "LOCK_HELD", "existing_pid": e.existing_meta.get("pid")})
    except Exception as e:
        result_queue.put({"status": "ERROR", "error": str(e)})
    """Hold workspace lock for 2s so the second worker can observe LOCK_HELD."""
    """Module-level worker for multiprocessing spawn."""
    sys.path.insert(0, _SRC)
    from deli_autoresearch.state_store import StateStore
    from deli_autoresearch.registry_manager import RegistryManager
    from deli_autoresearch.template_runtime import TemplateRuntime
    from deli_autoresearch.orchestrator import Orchestrator
    from deli_autoresearch.agent_backend_codex import MockAgentBackend
    from deli_autoresearch.utils import claim_id_for

    workspace = Path(workspace_str)
    store = StateStore(workspace)
    registry = RegistryManager(store)
    templates = TemplateRuntime()
    backend = MockAgentBackend()
    orch = Orchestrator(store, registry, templates, backend)

    claim_id = claim_id_for("mp-claim")
    backend.work_queue.append({"summary": "mp", "claims": [{"claim_text": "mp-claim", "evidence": [{"source_kind": "web", "url": "http://x"}], "source_kind": "web", "verifiable": True}]})
    backend.verification_queue.append({"claim_id": claim_id, "verdict": "validated", "evidence_strength": "strong", "summary": "ok"})

    # Hold lock for 2s so another worker can observe LOCK_HELD
    import time
    time.sleep(2.0)
    try:
        result = orch.run_once()
        result_queue.put({"success": True, "result": result})
    except Exception as e:
        result_queue.put({"success": False, "error": str(e)})


# ------------------------------------------------------------------
# Test 1: Two multiprocessing workers 鈥?one gets workspace LOCK_HELD
# ------------------------------------------------------------------

def test_p0_1_01_two_workers_workspace_lock(tmp_path: Path):
    workspace = tmp_path / 'ws'
    workspace.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, _SRC)
    from deli_autoresearch.state_store import StateStore
    from deli_autoresearch.registry_manager import RegistryManager
    from deli_autoresearch.template_runtime import TemplateRuntime
    store = StateStore(workspace)
    registry = RegistryManager(store)
    templates = TemplateRuntime()
    task_id = 'mp-ws'
    task_spec = '# goal\nTest.\n\n# conjecture\nA => B\n\n# known_lemmas\n- L1\n'
    tmpl = templates.get('math_proof')
    policy = tmpl.completion_policy(task_spec=task_spec)
    store.initialize_task(task_id, 'math_proof', task_spec, tmpl.seed_directions(task_spec=task_spec),
                          target_validated_findings=policy.target_validated_findings,
                          max_iterations=policy.max_iterations,
                          tail_pass_required=policy.require_tail_pass)
    registry.register_task(task_id, store.task_root(task_id), 'math_proof')

    worker_path = Path(_PROJ) / 'scripts' / '_lock_worker.py'
    env = os.environ.copy()
    env['PYTHONPATH'] = _SRC
    p1 = subprocess.Popen([sys.executable, str(worker_path), str(workspace), 'worker-A', '2.0'],
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
    time.sleep(0.3)
    p2 = subprocess.Popen([sys.executable, str(worker_path), str(workspace), 'worker-B', '0'],
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)

    out1, err1 = p1.communicate(timeout=30)
    out2, err2 = p2.communicate(timeout=30)

    lines1 = [l for l in out1.strip().split(chr(10)) if l.strip()]
    lines2 = [l for l in out2.strip().split(chr(10)) if l.strip()]
    r1 = json.loads(lines1[-1]) if lines1 else {'status': 'NO_OUTPUT', 'stderr': err1}
    r2 = json.loads(lines2[-1]) if lines2 else {'status': 'NO_OUTPUT', 'stderr': err2}

    assert r1['status'] == 'LOCK_ACQUIRED', f"Worker 1 failed: {r1}"
    assert r2['status'] == 'LOCK_HELD', f"Expected LOCK_HELD, got {r2}"

def test_p0_1_02_concurrent_jsonl_no_interleaving(tmp_path: Path):
    log_dir = tmp_path / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "test.jsonl"

    def jsonl_worker(log_path_str, records_json):
        sys.path.insert(0, _SRC)
        from deli_autoresearch.jsonl_store import JsonlStore
        log_path = Path(log_path_str)
        records = json.loads(records_json)
        store = JsonlStore(log_path, writer_instance_id=f"w_{os.getpid()}")
        for rec in records:
            store.append(rec)

    import subprocess as sp
    worker_script = str(tmp_path / "_jlw.py")
    with open(worker_script, "w", encoding="utf-8") as wf:
        wf.write(
            "import json, os, sys\n"
            f"sys.path.insert(0, {_SRC!r})\n"
            "from pathlib import Path\n"
            "from deli_autoresearch.jsonl_store import JsonlStore\n"
            "lp, rj = sys.argv[1], sys.argv[2]\n"
            "store = JsonlStore(Path(lp), writer_instance_id=f'w_{os.getpid()}')\n"
            "for rec in json.loads(rj):\n"
            "    store.append(rec)\n"
        )

    recs_a = [{"from": "A", "i": i} for i in range(20)]
    recs_b = [{"from": "B", "i": i} for i in range(20)]

    env = os.environ.copy()
    env["PYTHONPATH"] = _SRC

    pa = sp.Popen([sys.executable, worker_script, str(log_path), json.dumps(recs_a)],
                  stdout=sp.PIPE, stderr=sp.PIPE, text=True, env=env)
    pb = sp.Popen([sys.executable, worker_script, str(log_path), json.dumps(recs_b)],
                  stdout=sp.PIPE, stderr=sp.PIPE, text=True, env=env)
    pa.communicate(timeout=30)
    pb.communicate(timeout=30)

    lines = log_path.read_text(encoding="utf-8").strip().split("\n")
    valid = 0
    eids = set()
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
            valid += 1
            eid = rec.get("event_id", "")
            assert eid not in eids, f"Duplicate event_id: {eid}"
            eids.add(eid)
        except json.JSONDecodeError:
            pytest.fail(f"Invalid JSON line: {line[:100]}")
    assert valid >= 30


# ------------------------------------------------------------------
# Test 3: JSONL tail recovery
# ------------------------------------------------------------------

def test_p0_1_03_jsonl_tail_recovery(tmp_path: Path):
    log_dir = tmp_path / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "recovery.jsonl"

    sys.path.insert(0, _SRC)
    from deli_autoresearch.jsonl_store import JsonlStore

    store1 = JsonlStore(log_path)
    store1.append({"msg": "r1"})
    store1.append({"msg": "r2"})
    store1.append({"msg": "r3"})

    with log_path.open("ab") as f:
        f.write(b'{"msg": "broken')

    store2 = JsonlStore(log_path)
    store2.open()
    records = store2.read_all()
    assert len(records) == 3
    assert records[0]["msg"] == "r1"

    q_dir = log_dir / "quarantine"
    assert q_dir.exists()
    recovery_files = list(q_dir.glob("recovery.jsonl.tail.*.bin"))
    assert len(recovery_files) >= 1


# ------------------------------------------------------------------
# Test 4: Finding event_id idempotent
# ------------------------------------------------------------------

def test_p0_1_04_finding_event_id_idempotent(tmp_path: Path):
    log_dir = tmp_path / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "findings_idem.jsonl"

    sys.path.insert(0, _SRC)
    from deli_autoresearch.jsonl_store import JsonlStore

    store = JsonlStore(log_path)
    eid = "finding_test_123"
    store.append({"claim": "test"}, event_id=eid)
    store.append({"claim": "test AGAIN"}, event_id=eid)
    records = store.read_all()
    assert len(records) == 1
    assert records[0]["claim"] == "test"


# ------------------------------------------------------------------
# Test 5: Lock released on exception
# ------------------------------------------------------------------

def test_p0_1_05_lock_released_on_exception(tmp_path: Path):
    sys.path.insert(0, _SRC)
    from deli_autoresearch.file_lock import ProcessFileLock

    lock_dir = tmp_path / "locks"
    lock_dir.mkdir(parents=True, exist_ok=True)
    lp = lock_dir / "test.lock"
    mp = lock_dir / "test.lock.meta"

    lock = ProcessFileLock(lp, mp, "task", "test-exc", "owner-1")
    try:
        lock.acquire()
        assert lock.is_held()
        raise RuntimeError("simulated")
    except RuntimeError:
        lock.release()
    finally:
        if lock.is_held():
            lock.release()
    assert not lock.is_held()

    lock2 = ProcessFileLock(lp, mp, "task", "test-exc", "owner-2")
    lock2.acquire()
    assert lock2.is_held()
    lock2.release()


# ------------------------------------------------------------------
# Test 6: Phase 0 tests pass
# ------------------------------------------------------------------

def test_p0_1_06_phase_0_tests_still_pass():
    result = subprocess.run(
        [sys.executable, "-m", "pytest", str(Path(__file__).parent / "test_p0_acceptance.py"), "-q", "--tb=line"],
        capture_output=True, text=True, timeout=60,
        cwd=_PROJ,
    )
    assert result.returncode == 0, f"Phase 0 tests failed:\n{result.stdout}\n{result.stderr}"


# ------------------------------------------------------------------
# Test 7: Full test suite passes
# ------------------------------------------------------------------

def test_p0_1_07_full_test_suite_passes():
    result = subprocess.run(
        [sys.executable, "-m", "pytest", str(Path(__file__).parent), "-q", "--tb=line",
         "--ignore=" + str(Path(__file__).resolve())],
        capture_output=True, text=True, timeout=120,
        cwd=_PROJ,
    )
    assert result.returncode == 0, f"Test suite failed:\n{result.stdout}\n{result.stderr}"








