"""Utility helpers."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def normalize_claim_text(text: str) -> str:
    compact = re.sub(r"\s+", " ", text.strip().lower())
    return compact


def claim_id_for(text: str) -> str:
    digest = hashlib.sha1(normalize_claim_text(text).encode("utf-8")).hexdigest()[:12]
    return f"claim_{digest}"


def json_dumps(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=True, indent=2, sort_keys=True)
