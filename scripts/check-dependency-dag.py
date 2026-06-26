#!/usr/bin/env python3
"""
check-dependency-dag.py — Validate that spec dependency graph is a DAG (no cycles).
"""
import os
import sys
import json
import re


def load_dependencies(specs_dir):
    """Load dependency graph from spec.yaml files."""
    deps = {}
    for spec in os.listdir(specs_dir):
        spec_yaml = os.path.join(specs_dir, spec, "spec.yaml")
        if not os.path.isfile(spec_yaml):
            continue

        # Simple YAML parsing for dependencies
        try:
            with open(spec_yaml, "r", encoding="utf-8") as f:
                content = f.read()
            # Extract dependency lines
            spec_deps = []
            in_deps = False
            for line in content.split("\n"):
                if "dependencies:" in line:
                    in_deps = True
                    continue
                if in_deps:
                    m = re.match(r'\s*-\s*"?(.+?)"?\s*$', line)
                    if m:
                        spec_deps.append(m.group(1))
                    elif not line.strip().startswith("-"):
                        in_deps = False
            deps[spec] = spec_deps
        except Exception:
            deps[spec] = []

    return deps


def has_cycle(deps):
    """Check for cycles using DFS."""
    visited = set()
    rec_stack = set()

    def dfs(node):
        visited.add(node)
        rec_stack.add(node)
        for dep in deps.get(node, []):
            if dep not in visited:
                if dfs(dep):
                    return True
            elif dep in rec_stack:
                return True
        rec_stack.remove(node)
        return False

    for node in deps:
        if node not in visited:
            if dfs(node):
                return True
    return False


def main():
    specs_dir = os.path.join(os.path.dirname(__file__), "..", "specs")
    if not os.path.isdir(specs_dir):
        print("check-dependency-dag: SKIP — no specs/ directory")
        return 0

    deps = load_dependencies(specs_dir)
    if has_cycle(deps):
        print("check-dependency-dag: FAIL — cycle detected in dependency graph")
        return 1

    print(f"check-dependency-dag: PASS — {len(deps)} specs, no cycles")
    return 0


if __name__ == "__main__":
    sys.exit(main())
