"""Source-bounded local-history profile for Minnan cultural research."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


MINNAN_PROFILE_ROOT = r"D:\Codex\闽南文史ALLinAI"

REQUIRED_DIRECTORIES = (
    "config",
    "data/raw",
    "data/ocr",
    "data/processed",
    "docs/provenance",
    "runtime/tasks",
    "runtime/findings",
    "runtime/rejected_claims",
)

CLAIM_EVIDENCE_REQUIREMENTS = {
    "transcription": ("source_span", "ocr_alignment", "human_review"),
    "translation": ("source_span", "glossary_version"),
    "historical_fact": ("source_span", "primary_or_official_source"),
    "place_person_relation": ("source_span", "disambiguation_record"),
    "chronology": ("source_span", "date_conversion_rule", "uncertainty_note"),
    "folklore_interpretation": ("source_category", "uncertainty_note"),
}


@dataclass(frozen=True)
class LocalHistoryProfile:
    """Fail-closed profile: web material can only create candidates by default."""

    root: str = MINNAN_PROFILE_ROOT
    open_web_fact_ingestion: bool = False
    required_directories: tuple[str, ...] = REQUIRED_DIRECTORIES
    claim_evidence_requirements: dict[str, tuple[str, ...]] | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["claim_evidence_requirements"] = {
            key: list(value)
            for key, value in (self.claim_evidence_requirements or CLAIM_EVIDENCE_REQUIREMENTS).items()
        }
        return payload

    def planned_paths(self) -> list[str]:
        return [str(Path(self.root) / relative) for relative in self.required_directories]

    def validate_claim(self, claim_type: str, evidence: dict[str, Any]) -> list[str]:
        requirements = (self.claim_evidence_requirements or CLAIM_EVIDENCE_REQUIREMENTS).get(claim_type)
        if requirements is None:
            return [f"unknown local-history claim type: {claim_type}"]
        missing = [key for key in requirements if not evidence.get(key)]
        return [f"missing required evidence: {key}" for key in missing]


def default_minnan_profile() -> LocalHistoryProfile:
    """Return the default profile without creating directories or ingesting web facts."""

    return LocalHistoryProfile()
