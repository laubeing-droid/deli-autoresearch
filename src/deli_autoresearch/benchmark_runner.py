"""Replay benchmark runner for canned task scenarios."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from .agent_backend_codex import MockAgentBackend
from .orchestrator import Orchestrator
from .registry_manager import RegistryManager
from .state_store import StateStore
from .task_assets import load_seed_directions
from .template_runtime import TemplateRuntime
from .utils import claim_id_for


class BenchmarkRunner:
    def __init__(self, workspace: Path):
        self.workspace = workspace.resolve()

    def run(self, scenario_path: Path) -> dict:
        scenario = json.loads(scenario_path.read_text(encoding="utf-8"))
        runtime_workspace = self.workspace / ".benchmark_runtime" / scenario["name"]
        if runtime_workspace.exists():
            shutil.rmtree(runtime_workspace)
        runtime_workspace.mkdir(parents=True, exist_ok=True)

        store = StateStore(runtime_workspace)
        registry = RegistryManager(store)
        templates = TemplateRuntime()
        backend = MockAgentBackend()
        orchestrator = Orchestrator(store, registry, templates, backend)

        task_spec_path = (scenario_path.parent / scenario["task_spec"]).resolve()
        task_spec = task_spec_path.read_text(encoding="utf-8")
        template = templates.get(scenario["template"])
        policy = template.completion_policy(task_spec=task_spec)
        store.initialize_task(
            scenario["task_id"],
            scenario["template"],
            task_spec,
            load_seed_directions(task_spec_path, template),
            target_validated_findings=policy.target_validated_findings,
            max_iterations=policy.max_iterations,
            tail_pass_required=policy.require_tail_pass,
        )
        registry.register_task(scenario["task_id"], store.task_root(scenario["task_id"]), scenario["template"])

        iterations = []
        for round_payload in scenario["rounds"]:
            backend.work_queue.append(round_payload["work"])
            verification_payloads = []
            work_claims = round_payload["work"]["claims"]
            for index, verification in enumerate(round_payload["verification"]):
                if "claim_id" not in verification:
                    verification = {
                        **verification,
                        "claim_id": claim_id_for(work_claims[index]["claim_text"]),
                    }
                verification_payloads.append(verification)
            backend.verification_queue.extend(verification_payloads)
            iterations.extend(orchestrator.run_once())
            progress = store.read_progress(scenario["task_id"])
            if progress.status != "active":
                break

        progress = store.read_progress(scenario["task_id"])
        return {
            "scenario": scenario["name"],
            "task_id": scenario["task_id"],
            "iterations": iterations,
            "final_progress": progress.to_dict(),
            "findings_log": store.findings_path(scenario["task_id"]).read_text(encoding="utf-8").splitlines(),
        }
