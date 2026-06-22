"""Template loader."""

from __future__ import annotations

from .templates.general_research import GeneralResearchTemplate
from .templates.legal_proof import LegalProofTemplate
from .templates.math_proof import MathProofTemplate


class TemplateRuntime:
    def __init__(self) -> None:
        templates = [GeneralResearchTemplate(), MathProofTemplate(), LegalProofTemplate()]
        self._templates = {template.name: template for template in templates}

    def get(self, template_type: str):
        if template_type not in self._templates:
            raise KeyError(f"Unknown template type: {template_type}")
        return self._templates[template_type]

    def names(self) -> list[str]:
        return sorted(self._templates)
