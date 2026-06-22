#!/usr/bin/env python3
"""Run G9 grounded-semantics exploration via Deli AutoResearch.

Usage (from workspace root):
    python scripts/run_g9_exploration.py [--juris-root PATH]

This script:
1. Runs the juris-calculus bridge regression suite directly.
2. Initialises a legal_proof task in the local runtime.
3. Runs one orchestrator iteration with the JurisCalculusBackend.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="G9 exploration runner")
    parser.add_argument(
        "--juris-root",
        default=r"D:\Codex\juris-calculus",
        help="Path to juris-calculus source root",
    )
    parser.add_argument("--workspace", default=".", help="AutoResearch workspace root")
    args = parser.parse_args()

    workspace = Path(args.workspace).resolve()
    juris_root = Path(args.juris_root).resolve()

    # --- Step 1: Direct bridge regression ---
    print("=== Step 1: juris-calculus bridge regression ===")
    # Add auto-research src to path
    src_dir = workspace / "src"
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

    from deli_autoresearch.juris_calculus_bridge import JurisCalculusBridge

    bridge = JurisCalculusBridge(juris_root)
    report = bridge.run_full_regression()
    print(f"  Total: {report.total}, Passed: {report.passed}, Failed: {report.failed}")
    for r in report.results:
        status = "PASS" if r.passed else "FAIL"
        print(f"  [{status}] {r.test_name}: accepted={r.accepted}, undecided={r.undecided}")
        if r.error:
            print(f"         error: {r.error}")

    if not report.all_passed:
        print("\nWARNING: Some bridge tests failed. Check juris-calculus engine.")
        # Continue anyway to show the full flow

    # --- Step 2: Initialize legal_proof task ---
    print("\n=== Step 2: Initialize legal_proof task ===")
    from deli_autoresearch.cli import make_services

    store, registry, templates, orchestrator, heartbeat, backend = make_services(
        workspace, backend_name="mock"
    )
    store.ensure_runtime()

    task_id = "g9-grounded-extension"
    task_spec_file = workspace / "examples" / "legal_proof" / "g9_cyclic_grounded_extension.md"
    if not task_spec_file.exists():
        print(f"ERROR: task spec not found at {task_spec_file}")
        return 1

    template = templates.get("legal_proof")
    task_spec = task_spec_file.read_text(encoding="utf-8")
    policy = template.completion_policy(task_spec=task_spec)

    from deli_autoresearch.task_assets import load_seed_directions

    # Check if already initialized
    if store.progress_path(task_id).exists():
        print(f"  Task {task_id} already initialized, reading existing state.")
        progress = store.read_progress(task_id)
    else:
        progress = store.initialize_task(
            task_id,
            "legal_proof",
            task_spec,
            load_seed_directions(task_spec_file, template),
            target_validated_findings=policy.target_validated_findings,
            max_iterations=policy.max_iterations,
            tail_pass_required=policy.require_tail_pass,
        )
        registry.register_task(task_id, store.task_root(task_id), "legal_proof", priority=100)
    print(f"  Task: {task_id}")
    print(f"  Status: {progress.status}")
    print(f"  Iteration: {progress.iteration}")
    print(f"  Target findings: {progress.target_validated_findings}")

    # --- Step 3: Run orchestrator with JurisCalculusBackend ---
    print("\n=== Step 3: Run orchestrator with local engine ===")
    from deli_autoresearch.agent_backend_codex import MockAgentBackend
    from deli_autoresearch.juris_calculus_backend import JurisCalculusBackend
    from deli_autoresearch.orchestrator import Orchestrator

    # Create hybrid backend: mock work agent + local verification engine
    mock_inner = MockAgentBackend()

    # Queue a work response that proposes a claim about the G9 fix
    mock_inner.work_queue.append({
        "summary": "Verify that the G9 bug fix correctly handles bidirectional cycles.",
        "claims": [
            {
                "claim_text": "grounded_extension returns UNDECIDED for bidirectional cycle A<->B",
                "evidence": [
                    {
                        "source_kind": "code",
                        "locator": "compiler_core/argumentation.py:grounded_extension",
                        "detail": "Bug fix: rejected = attacked-by-IN, not cids-accepted"
                    },
                    {
                        "source_kind": "juris_test_pass",
                        "test_name": "bidirectional_A_B",
                        "detail": "Regression test passes for A<->B cycle"
                    }
                ],
                "source_kind": "code",
                "verifiable": True,
                "support_kind": "new",
            }
        ],
    })

    # Queue a verification response (will be overridden by local engine if run_local_engine=True)
    mock_inner.verification_queue.append({
        "claim_id": "placeholder",
        "verdict": "needs_more_evidence",
        "evidence_strength": "weak",
        "summary": "placeholder",
    })

    hybrid = JurisCalculusBackend(mock_inner, juris_root)
    orch = Orchestrator(store, registry, templates, hybrid)

    # Patch the orchestrator to set run_local_engine on verification prompts
    original_build = orch._build_verification_prompt

    def patched_build_verification_prompt(task_id, progress, claim_id, claim, candidate):
        prompt = original_build(task_id, progress, claim_id, claim, candidate)
        prompt["run_local_engine"] = True
        return prompt

    orch._build_verification_prompt = patched_build_verification_prompt

    results = orch.run_once()
    print(f"  Orchestrator results: {json.dumps(results, indent=2, ensure_ascii=True)}")

    # Print final state
    final_progress = store.read_progress(task_id)
    print(f"\n  Final status: {final_progress.status}")
    print(f"  Iterations: {final_progress.iteration}")
    print(f"  Validated findings: {final_progress.validated_findings_count}")
    print(f"  Stall pressure: {final_progress.stall_pressure}")

    # Print findings
    findings_text = store.findings_path(task_id).read_text(encoding="utf-8").strip()
    if findings_text:
        print("\n=== Findings ===")
        for line in findings_text.split("\n"):
            finding = json.loads(line)
            print(f"  [{finding.get('claim_id', '?')}] {finding.get('claim', '?')}")
            print(f"    source: {finding.get('source_kind', '?')}, strength: {finding.get('evidence_strength', '?')}")

    print("\nDone.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
