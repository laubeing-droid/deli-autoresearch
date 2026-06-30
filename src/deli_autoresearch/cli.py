"""CLI entrypoints."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .agent_backend_codex import CodexAgentBackend, MockAgentBackend
from .benchmark_runner import BenchmarkRunner
from .orchestrator import Orchestrator
from .registry_manager import RegistryManager
from .state_store import StateStore
from .task_assets import load_seed_directions
from .template_runtime import TemplateRuntime
from .heartbeat_service import HeartbeatService
from .lean_manifest import discover_cross_repo_status


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="deli-autoresearch")
    parser.add_argument("--workspace", default=".", help="Workspace root")
    parser.add_argument("--backend", choices=["mock", "codex-bridge", "juris-calculus"], default="mock")
    parser.add_argument("--backend-timeout-seconds", type=int, default=300)
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_task = subparsers.add_parser("init-task")
    init_task.add_argument("--task-id", required=True)
    init_task.add_argument("--template", required=True)
    init_task.add_argument("--task-spec-file", required=True)
    init_task.add_argument("--priority", type=int, default=100)

    register = subparsers.add_parser("register-task")
    register.add_argument("--task-id", required=True)
    register.add_argument("--template", required=True)
    register.add_argument("--priority", type=int, default=100)

    subparsers.add_parser("run-orchestrator-once")
    subparsers.add_parser("run-heartbeat-once")

    resume = subparsers.add_parser("resume-task-with-direction")
    resume.add_argument("--task-id", required=True)
    resume.add_argument("--strategy-type", required=True)
    resume.add_argument("--summary", required=True)
    resume.add_argument("--rationale", required=True)

    subparsers.add_parser("doctor")
    bridge = subparsers.add_parser("bridge-status")
    bridge.add_argument("--show-files", action="store_true")
    benchmark = subparsers.add_parser("run-benchmark")
    benchmark.add_argument("--scenario", required=True)
    return parser


def make_services(workspace: Path, *, backend_name: str = "mock", backend_timeout_seconds: int = 300):
    store = StateStore(workspace)
    registry = RegistryManager(store)
    templates = TemplateRuntime()
    if backend_name == "mock":
        backend = MockAgentBackend()
    elif backend_name == "codex-bridge":
        backend = CodexAgentBackend(store.runtime_root, timeout_seconds=backend_timeout_seconds)
    elif backend_name == "juris-calculus":
        from .juris_calculus_backend import JurisCalculusBackend
        from .constants import JURIS_CALCULUS_ROOT
        inner = MockAgentBackend()
        backend = JurisCalculusBackend(inner, JURIS_CALCULUS_ROOT)
    else:
        raise ValueError(f"Unknown backend: {backend_name}")
    orchestrator = Orchestrator(store, registry, templates, backend)
    heartbeat = HeartbeatService(store, registry)
    return store, registry, templates, orchestrator, heartbeat, backend


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    workspace = Path(args.workspace).resolve()
    store, registry, templates, orchestrator, heartbeat, backend = make_services(
        workspace,
        backend_name=args.backend,
        backend_timeout_seconds=args.backend_timeout_seconds,
    )
    store.ensure_runtime()

    if args.command == "init-task":
        template = templates.get(args.template)
        task_spec_file = Path(args.task_spec_file)
        task_spec = task_spec_file.read_text(encoding="utf-8")
        policy = template.completion_policy(task_spec=task_spec)
        progress = store.initialize_task(
            args.task_id,
            args.template,
            task_spec,
            load_seed_directions(task_spec_file, template),
            target_validated_findings=policy.target_validated_findings,
            max_iterations=policy.max_iterations,
            tail_pass_required=policy.require_tail_pass,
        )
        task_path = store.task_root(args.task_id)
        registry.register_task(args.task_id, task_path, args.template, args.priority)
        print(json.dumps(progress.to_dict(), ensure_ascii=True, indent=2))
        return 0
    if args.command == "register-task":
        task = registry.register_task(args.task_id, store.task_root(args.task_id), args.template, args.priority)
        print(json.dumps(task.to_dict(), ensure_ascii=True, indent=2))
        return 0
    if args.command == "run-orchestrator-once":
        print(json.dumps(orchestrator.run_once(), ensure_ascii=True, indent=2))
        return 0
    if args.command == "run-heartbeat-once":
        print(json.dumps(heartbeat.run_once(), ensure_ascii=True, indent=2))
        return 0
    if args.command == "resume-task-with-direction":
        progress = orchestrator.resume_task_with_direction(
            args.task_id,
            args.strategy_type,
            args.summary,
            args.rationale,
        )
        print(json.dumps(progress.to_dict(), ensure_ascii=True, indent=2))
        return 0
    if args.command == "doctor":
        report = {
            "runtime_exists": store.runtime_root.exists(),
            "registry_exists": store.registry_path.exists(),
            "registered_tasks": len(store.read_registry().tasks),
            "backend": args.backend,
            "cross_repo": discover_cross_repo_status(workspace),
        }
        print(json.dumps(report, ensure_ascii=True, indent=2))
        return 0
    if args.command == "bridge-status":
        report = {
            "backend": args.backend,
            "bridge_supported": isinstance(backend, CodexAgentBackend),
        }
        if isinstance(backend, CodexAgentBackend):
            request_files = sorted(path.name for path in backend.requests_dir.glob("*.json"))
            response_files = sorted(path.name for path in backend.responses_dir.glob("*.json"))
            report.update(
                {
                    "requests_dir": str(backend.requests_dir),
                    "responses_dir": str(backend.responses_dir),
                    "pending_request_count": len(request_files),
                    "available_response_count": len(response_files),
                }
            )
            if args.show_files:
                report["request_files"] = request_files
                report["response_files"] = response_files
        print(json.dumps(report, ensure_ascii=True, indent=2))
        return 0
    if args.command == "run-benchmark":
        runner = BenchmarkRunner(workspace)
        print(json.dumps(runner.run(Path(args.scenario)), ensure_ascii=True, indent=2))
        return 0
    raise AssertionError("unreachable")
