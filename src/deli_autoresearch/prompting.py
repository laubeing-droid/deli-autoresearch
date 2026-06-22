"""Prompt builders for external work and verification agents."""

from __future__ import annotations

import json
from typing import Any


def _pretty_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=True, indent=2, sort_keys=True)


def build_work_instruction(prompt: dict[str, Any]) -> str:
    return "\n".join(
        [
            "You are the work agent for a long-horizon autonomous research task.",
            "Return strict JSON only. No markdown. No prose outside JSON.",
            'Required JSON shape: {"summary": string, "claims": [{'
            '"claim_text": string, "evidence": [object], "source_kind": string, '
            '"verifiable": boolean, "support_kind": "new|new_direction_basis", '
            '"reopen_of": string|null}]}',
            "Constraints:",
            "- At most 3 claims total.",
            "- At most 3 evidence objects per claim.",
            "- Evidence must be structured objects.",
            "- Do not write files or mutate task state directly.",
            "Task context JSON:",
            _pretty_json(prompt),
        ]
    )


def build_verification_instruction(prompt: dict[str, Any]) -> str:
    return "\n".join(
        [
            "You are the independent verification agent.",
            "Return strict JSON only. No markdown. No prose outside JSON.",
            'Required JSON shape: {"claim_id": string, '
            '"verdict": "validated|rejected|needs_more_evidence", '
            '"evidence_strength": string, "summary": string, '
            '"supporting_evidence": [object]}',
            "Rules:",
            "- Judge only the supplied claim and evidence.",
            "- Reuse the exact provided claim_id.",
            "- Use needs_more_evidence when the direction looks viable but the evidence is insufficient.",
            "- Do not write files or mutate task state directly.",
            "Task context JSON:",
            _pretty_json(prompt),
        ]
    )
