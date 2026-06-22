"""Helpers for task asset files such as seed directions."""

from __future__ import annotations

import json
from pathlib import Path

from .models import Direction


def load_seed_directions(task_spec_file: Path, template) -> list[Direction]:
    seed_path = task_spec_file.parent / "seed_directions.json"
    if seed_path.exists():
        payload = json.loads(seed_path.read_text(encoding="utf-8"))
        return [Direction.from_dict(item) for item in payload]
    task_spec = task_spec_file.read_text(encoding="utf-8")
    return template.seed_directions(task_spec=task_spec)
