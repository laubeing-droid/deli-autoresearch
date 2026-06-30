"""Source approval registry for source-bounded retrieval."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Any


APPROVED = "approved"
PROPOSED = "proposed"
REJECTED = "rejected"
VALID_STATUSES = {APPROVED, PROPOSED, REJECTED}


@dataclass(frozen=True)
class SourceRecord:
    """A registered evidence source and its review-bounded retrieval state."""

    source_id: str
    review_status: str
    kind: str = ""
    location: str = ""
    trust_tier: str = ""
    license: str = ""
    provenance: str = ""
    allowed_tasks: tuple[str, ...] = ()
    forbidden_tasks: tuple[str, ...] = ()
    reviewer: str = ""
    rationale: str = ""

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "SourceRecord":
        source_id = str(payload.get("id") or payload.get("source_id") or "").strip()
        status = str(payload.get("review_status") or payload.get("status") or "").strip().lower()
        if not source_id:
            raise ValueError("source record missing id")
        if status not in VALID_STATUSES:
            raise ValueError(f"source {source_id} has invalid status: {status}")
        return cls(
            source_id=source_id,
            review_status=status,
            kind=str(payload.get("kind", "")),
            location=str(payload.get("location") or payload.get("locator") or ""),
            trust_tier=str(payload.get("trust_tier", "")),
            license=str(payload.get("license", "")),
            provenance=str(payload.get("provenance", "")),
            allowed_tasks=_coerce_string_tuple(payload.get("allowed_tasks", ())),
            forbidden_tasks=_coerce_string_tuple(payload.get("forbidden_tasks", ())),
            reviewer=str(payload.get("reviewer", "")),
            rationale=str(payload.get("rationale", "")),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class SourceRegistry:
    """Read-only source registry used to fail closed before retrieval."""

    def __init__(self, records: list[SourceRecord]) -> None:
        self._records = {record.source_id: record for record in records}

    @classmethod
    def from_file(cls, path: str | Path) -> "SourceRegistry":
        payload = _load_registry_payload(Path(path))
        raw_records = payload.get("sources", [])
        if not isinstance(raw_records, list):
            raise ValueError("source registry must contain a sources list")
        return cls([SourceRecord.from_dict(item) for item in raw_records])

    def get(self, source_id: str) -> SourceRecord | None:
        return self._records.get(source_id)

    def status(self, source_id: str) -> str:
        record = self.get(source_id)
        return record.review_status if record else "unregistered"

    def is_approved(self, source_id: str) -> bool:
        return self.status(source_id) == APPROVED

    def approved_sources(self) -> list[SourceRecord]:
        return [record for record in self._records.values() if record.status == APPROVED]

    def to_dict(self) -> dict[str, Any]:
        return {"sources": [record.to_dict() for record in self._records.values()]}


def _load_registry_payload(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        payload = json.loads(text)
    elif path.suffix.lower() in {".yml", ".yaml"}:
        payload = _load_minimal_yaml(text)
    else:
        raise ValueError(f"unsupported source registry format: {path.suffix}")
    if not isinstance(payload, dict):
        raise ValueError("source registry root must be an object")
    return payload


def _load_minimal_yaml(text: str) -> dict[str, Any]:
    """Parse the small YAML subset used by config/source_registry.example.yml."""

    records: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    in_sources = False
    for raw_line in text.splitlines():
        line = raw_line.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        if line.strip() == "sources:":
            in_sources = True
            continue
        if not in_sources:
            continue
        stripped = line.strip()
        if stripped.startswith("- "):
            if current is not None:
                records.append(current)
            current = {}
            stripped = stripped[2:].strip()
            if stripped:
                key, value = _parse_yaml_pair(stripped)
                current[key] = value
            continue
        if current is None:
            raise ValueError("YAML source field appeared before list item")
        key, value = _parse_yaml_pair(stripped)
        current[key] = value
    if current is not None:
        records.append(current)
    return {"sources": records}


def _parse_yaml_pair(text: str) -> tuple[str, str]:
    if ":" not in text:
        raise ValueError(f"unsupported YAML line: {text}")
    key, value = text.split(":", 1)
    return key.strip(), value.strip().strip('"').strip("'")


def _coerce_string_tuple(value: Any) -> tuple[str, ...]:
    """Normalize schema list fields while keeping the dependency footprint zero."""

    if value is None:
        return ()
    if isinstance(value, str):
        stripped = value.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            stripped = stripped[1:-1]
        if not stripped:
            return ()
        return tuple(item.strip().strip('"').strip("'") for item in stripped.split(",") if item.strip())
    if isinstance(value, (list, tuple)):
        return tuple(str(item) for item in value)
    raise ValueError(f"expected string list field, got {type(value).__name__}")
