#!/usr/bin/env python3
"""
worktree-create.py — Create a git worktree for a spec task.

Usage:
    python scripts/worktree-create.py --spec SPEC-210 --task TASK-210-005
    python scripts/worktree-create.py --spec SPEC-210 --task TASK-210-005 --base main

Creates a worktree at .worktrees/<spec>/<task>/ on branch spec/<spec>/<task>.
"""
import argparse
import os
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description="Create a spec worktree")
    parser.add_argument("--spec", required=True, help="Spec ID (e.g., SPEC-210)")
    parser.add_argument("--task", required=True, help="Task ID (e.g., TASK-210-005)")
    parser.add_argument("--base", default="main", help="Base branch (default: main)")
    parser.add_argument("--repo-root", default=".", help="Repository root")
    args = parser.parse_args()

    spec_id = args.spec.lower().replace("spec-", "")
    task_id = args.task.lower().replace("task-", "")
    branch_name = f"spec/{spec_id}/{task_id}"
    worktree_path = os.path.join(args.repo_root, ".worktrees", spec_id, task_id)

    # Check if worktree already exists
    if os.path.isdir(worktree_path):
        print(f"worktree-create: SKIP — worktree already exists at {worktree_path}")
        return 0

    # Create worktree directory
    os.makedirs(os.path.dirname(worktree_path), exist_ok=True)

    # Create branch and worktree
    try:
        subprocess.run(
            ["git", "worktree", "add", "-b", branch_name, worktree_path, args.base],
            cwd=args.repo_root,
            check=True,
            capture_output=True,
            text=True,
        )
        print(f"worktree-create: OK — {worktree_path} on branch {branch_name}")
        return 0
    except subprocess.CalledProcessError as e:
        # Branch may already exist
        if "already exists" in e.stderr:
            subprocess.run(
                ["git", "worktree", "add", worktree_path, branch_name],
                cwd=args.repo_root,
                check=True,
            )
            print(f"worktree-create: OK — {worktree_path} on existing branch {branch_name}")
            return 0
        print(f"worktree-create: FAIL — {e.stderr}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
