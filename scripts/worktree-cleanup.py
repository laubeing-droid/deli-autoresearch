#!/usr/bin/env python3
"""
worktree-cleanup.py — Remove completed or stale worktrees.

Usage:
    python scripts/worktree-cleanup.py --all          # Remove all worktrees
    python scripts/worktree-cleanup.py --spec SPEC-210 # Remove worktrees for a spec
    python scripts/worktree-cleanup.py --stale 7       # Remove worktrees older than 7 days
    python scripts/worktree-cleanup.py --dry-run       # Show what would be removed
"""
import argparse
import os
import shutil
import subprocess
import sys
import time


def list_worktrees(repo_root):
    """List git worktrees."""
    result = subprocess.run(
        ["git", "worktree", "list", "--porcelain"],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    worktrees = []
    current = {}
    for line in result.stdout.splitlines():
        if line.startswith("worktree "):
            if current:
                worktrees.append(current)
            current = {"path": line.split(" ", 1)[1]}
        elif line.startswith("HEAD "):
            current["head"] = line.split(" ", 1)[1]
        elif line.startswith("branch "):
            current["branch"] = line.split(" ", 1)[1]
    if current:
        worktrees.append(current)
    return worktrees


def main():
    parser = argparse.ArgumentParser(description="Clean up spec worktrees")
    parser.add_argument("--all", action="store_true", help="Remove all .worktrees")
    parser.add_argument("--spec", help="Remove worktrees for a specific spec")
    parser.add_argument("--stale", type=int, help="Remove worktrees older than N days")
    parser.add_argument("--dry-run", action="store_true", help="Show without removing")
    parser.add_argument("--repo-root", default=".", help="Repository root")
    args = parser.parse_args()

    worktrees_base = os.path.join(args.repo_root, ".worktrees")
    if not os.path.isdir(worktrees_base):
        print("worktree-cleanup: no .worktrees/ directory found")
        return 0

    removed = 0
    for spec_dir in os.listdir(worktrees_base):
        spec_path = os.path.join(worktrees_base, spec_dir)
        if not os.path.isdir(spec_path):
            continue

        if args.spec and spec_dir != args.spec.lower().replace("spec-", ""):
            continue

        for task_dir in os.listdir(spec_path):
            task_path = os.path.join(spec_path, task_dir)
            if not os.path.isdir(task_path):
                continue

            # Check age if --stale
            if args.stale:
                mtime = os.path.getmtime(task_path)
                age_days = (time.time() - mtime) / 86400
                if age_days < args.stale:
                    continue

            if args.dry_run:
                print(f"  would remove: {task_path}")
            else:
                # Remove git worktree
                subprocess.run(
                    ["git", "worktree", "remove", "--force", task_path],
                    cwd=args.repo_root,
                    capture_output=True,
                )
                print(f"  removed: {task_path}")
            removed += 1

    if args.all and not args.dry_run:
        if os.path.isdir(worktrees_base):
            shutil.rmtree(worktrees_base, ignore_errors=True)
            print(f"worktree-cleanup: removed all worktrees")
            return 0

    print(f"worktree-cleanup: {'would remove' if args.dry_run else 'removed'} {removed} worktree(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
