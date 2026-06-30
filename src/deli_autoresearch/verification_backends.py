"""Verification backend contracts for source-bounded research gates."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from typing import Any

from .constants import VERDICT_NEEDS_MORE_EVIDENCE, VERDICT_REJECTED, VERDICT_VALIDATED
from .models import utc_now_iso


LEAN_MANIFEST_BACKEND = "lean_manifest_backend"
JC_RUNTIME_BACKEND = "jc_runtime_backend"
SPEC_SHADOW_BACKEND = "spec_shadow_backend"
SOURCE_SPAN_BACKEND = "source_span_backend"
OCR_ALIGNMENT_BACKEND = "ocr_alignment_backend"
CITATION_UPGRADE_BACKEND = "citation_upgrade_backend"
HUMAN_REVIEW_BACKEND = "human_review_backend"

BACKEND_CONTRACTS: dict[str, str] = {
    LEAN_MANIFEST_BACKEND: "Lean build, theorem manifest, and no-sorry scan.",
    JC_RUNTIME_BACKEND: "juris-calculus pytest, checker, and fixtures.",
    SPEC_SHADOW_BACKEND: "Reference evaluator versus JC shadow output.",
    SOURCE_SPAN_BACKEND: "Source span, hash, and citation-context consistency.",
    OCR_ALIGNMENT_BACKEND: "OCR output aligned to original image or PDF span.",
    CITATION_UPGRADE_BACKEND: "Candidate citation upgrade without changing source tier by assertion.",
    HUMAN_REVIEW_BACKEND: "Human-reviewed anchor with recorded reviewer and evidence path.",
}

VALID_BACKEND_STATUSES = {VERDICT_VALIDATED, VERDICT_REJECTED, VERDICT_NEEDS_MORE_EVIDENCE}


@dataclass(frozen=True)
class BackendResult:
    """Machine-readable verifier result with digests required for findings."""

    backend_name: str
    backend_version: str
    status: str
    input_digest: str
    output_digest: str
    summary: str = ""
    evidence_path: str = ""
    ts: str = ""

    def __post_init__(self) -> None:
        if self.backend_name not in BACKEND_CONTRACTS:
            raise ValueError(f"unknown verification backend: {self.backend_name}")
        if self.status not in VALID_BACKEND_STATUSES:
            raise ValueError(f"invalid verification backend status: {self.status}")

    def to_dict(self) -> dict[str, str]:
        payload = asdict(self)
        payload["ts"] = self.ts or utc_now_iso()
        return payload


def digest_payload(payload: dict[str, Any]) -> str:
    """Return a stable digest for verifier inputs or outputs."""

    canonical = json.dumps(payload, ensure_ascii=True, sort_keys=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def fail_closed_backend_result(
    backend_name: str,
    *,
    input_payload: dict[str, Any] | None = None,
    reason: str,
    backend_version: str = "contract-v1",
) -> BackendResult:
    """Build a needs-more-evidence result when a backend is missing or failed."""

    input_payload = dict(input_payload or {})
    output_payload = {"status": VERDICT_NEEDS_MORE_EVIDENCE, "reason": reason}
    return BackendResult(
        backend_name=backend_name,
        backend_version=backend_version,
        status=VERDICT_NEEDS_MORE_EVIDENCE,
        input_digest=digest_payload(input_payload),
        output_digest=digest_payload(output_payload),
        summary=reason,
    )
