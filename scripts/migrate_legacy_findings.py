#!/usr/bin/env python3
"""Historical data migration: mark old findings as LEGACY_UNBOUND_VERIFICATION.

Usage:
    python scripts/migrate_legacy_findings.py --workspace <path> [--dry-run] [--task-id <id>]

Dry-run mode reports what would change without modifying files.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Add src to path
_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent / "src"))

from deli_autoresearch.state_store import StateStore
from deli_autoresearch.models import utc_now_iso


LEGACY_TAG = "LEGACY_UNBOUND_VERIFICATION"


def migrate_task(store: StateStore, task_id: str, dry_run: bool) -> dict:
    """Migrate one task's findings to mark legacy entries."""
    findings_path = store.findings_path(task_id)
    if not findings_path.exists():
        return {"task_id": task_id, "migrated": 0, "skipped": 0, "status": "no_findings"}

    lines = findings_path.read_text(encoding="utf-8").strip().split("\n")
    if not lines or all(line == "" for line in lines):
        return {"task_id": task_id, "migrated": 0, "skipped": 0, "status": "empty"}

    migrated = 0
    skipped = 0
    new_lines = []

    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            finding = json.loads(line)
        except json.JSONDecodeError:
            skipped += 1
            continue

        # Already tagged — skip
        if finding.get("verification_status") == LEGACY_TAG:
            skipped += 1
            new_lines.append(json.dumps(finding, ensure_ascii=True, sort_keys=True))
            continue

        # Already has a verification_status (post-Phase-0 finding) — skip
        if finding.get("verification_status") and finding["verification_status"] != "validated":
            skipped += 1
            new_lines.append(json.dumps(finding, ensure_ascii=True, sort_keys=True))
            continue

        # Legacy finding: no verification_status or only has old "validated" string
        # These are pre-Phase-0 findings not bound to a current claim formal payload
        finding["verification_status"] = LEGACY_TAG
        finding["migrated_at"] = utc_now_iso()
        migrated += 1
        new_lines.append(json.dumps(finding, ensure_ascii=True, sort_keys=True))

    if not dry_run:
        findings_path.write_text(
            "\n".join(new_lines) + ("\n" if new_lines else ""),
            encoding="utf-8",
        )

    # Update progress: reset validated_findings_count since legacy findings
    # no longer count toward validated_findings_count
    if not dry_run and migrated > 0:
        progress = store.read_progress(task_id)
        progress.validated_findings_count = max(
            0, progress.validated_findings_count - migrated
        )
        store.write_progress(progress)

    return {
        "task_id": task_id,
        "migrated": migrated,
        "skipped": skipped,
        "status": "ok",
    }


def main():
    parser = argparse.ArgumentParser(description="Migrate legacy findings to LEGACY_UNBOUND_VERIFICATION")
    parser.add_argument("--workspace", required=True, help="Workspace root path")
    parser.add_argument("--dry-run", action="store_true", help="Report changes without modifying files")
    parser.add_argument("--task-id", help="Specific task ID to migrate (default: all tasks)")
    args = parser.parse_args()

    workspace = Path(args.workspace)
    store = StateStore(workspace)
    store.ensure_runtime()

    registry = store.read_registry()
    if args.task_id:
        tasks = [t for t in registry.tasks if t.task_id == args.task_id]
        if not tasks:
            print(f"Task {args.task_id} not found in registry")
            sys.exit(1)
    else:
        tasks = registry.tasks

    total_migrated = 0
    for task in tasks:
        result = migrate_task(store, task.task_id, args.dry_run)
        total_migrated += result["migrated"]
        tag = "[DRY RUN] " if args.dry_run else ""
        print(
            f"{tag}Task {result['task_id']}: migrated={result['migrated']}, "
            f"skipped={result['skipped']}, status={result['status']}"
        )

    print(f"\nTotal findings migrated: {total_migrated}")
    if args.dry_run:
        print("Dry run complete. Run without --dry-run to apply changes.")


if __name__ == "__main__":
    main()
