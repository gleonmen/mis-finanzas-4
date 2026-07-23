"""Use case: list all templates (feeds the draft grid / template views)."""
from __future__ import annotations

from app.domain.entities import Template
from app.domain.repositories import TemplateRepository


class ListTemplates:
    def __init__(self, template_repo: TemplateRepository) -> None:
        self._template_repo = template_repo

    def execute(self) -> list[Template]:
        return self._template_repo.list_all()
