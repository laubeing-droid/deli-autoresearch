"""Report disclosure gate for public/private source-bounded evidence."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


PUBLIC_KERNEL = "PUBLIC_KERNEL"
PRIVATE_LAYER = "PRIVATE_LAYER"
BLOCKED = "BLOCKED"
DRAFT_ONLY = "DRAFT_ONLY"

ALLOWED_CLASSIFICATIONS = {PUBLIC_KERNEL, PRIVATE_LAYER, BLOCKED, DRAFT_ONLY}

PRIVATE_MARKERS = {
    "client",
    "customer",
    "lawyer_workflow",
    "litigation_strategy",
    "private_benchmark",
    "commercial_rulebase",
}


@dataclass(frozen=True)
class ReportRow:
    """Disclosure-checked row required before a Deli report can be release evidence."""

    claim_id: str
    claim_text: str
    source_id: str
    evidence_path: str
    verifier: str
    verifier_status: str
    public_private_classification: str
    allowed_disclosure: bool
    blocked_reason: str = ""
    source_span: str = ""

    def __post_init__(self) -> None:
        if self.public_private_classification not in ALLOWED_CLASSIFICATIONS:
            raise ValueError(
                f"invalid public/private classification: {self.public_private_classification}"
            )
        if not self.allowed_disclosure and not self.blocked_reason:
            raise ValueError("blocked disclosure requires blocked_reason")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def classify_disclosure(payload: dict[str, Any]) -> tuple[str, bool, str]:
    """Classify report material without allowing private assets into release evidence."""

    joined = " ".join(str(value).lower() for value in payload.values())
    for marker in PRIVATE_MARKERS:
        if marker in joined:
            return PRIVATE_LAYER, False, f"private marker present: {marker}"
    if payload.get("draft") is True:
        return DRAFT_ONLY, False, "draft reports cannot be release evidence"
    if not payload.get("source_id") or not (payload.get("source_span") or payload.get("evidence_path")):
        return BLOCKED, False, "missing source span or evidence path"
    return PUBLIC_KERNEL, True, ""


def build_report_row(payload: dict[str, Any]) -> ReportRow:
    """Build one disclosure-checked report row from a finding-like payload."""

    classification, allowed, reason = classify_disclosure(payload)
    return ReportRow(
        claim_id=str(payload.get("claim_id", "")),
        claim_text=str(payload.get("claim_text") or payload.get("claim", "")),
        source_id=str(payload.get("source_id", "")),
        evidence_path=str(payload.get("evidence_path", "")),
        source_span=str(payload.get("source_span", "")),
        verifier=str(payload.get("verifier") or payload.get("backend_name", "")),
        verifier_status=str(payload.get("verifier_status") or payload.get("verification_status", "")),
        public_private_classification=classification,
        allowed_disclosure=allowed,
        blocked_reason=reason,
    )
