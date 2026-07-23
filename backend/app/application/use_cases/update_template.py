"""Use case: update an existing template."""
from __future__ import annotations

from app.application.errors import TemplateNotFoundError
from app.application.use_cases.template_rules import validate_and_normalize
from app.domain.entities import Template, TemplateData
from app.domain.repositories import CategoryRepository, TemplateRepository


class UpdateTemplate:
    def __init__(
        self,
        template_repo: TemplateRepository,
        category_repo: CategoryRepository,
    ) -> None:
        self._template_repo = template_repo
        self._category_repo = category_repo

    def execute(self, template_id: int, data: TemplateData) -> Template:
        if self._template_repo.get(template_id) is None:
            raise TemplateNotFoundError(f"La plantilla {template_id} no existe.")
        normalized = validate_and_normalize(data, self._category_repo)
        updated = self._template_repo.update(template_id, normalized)
        if updated is None:  # deleted between the check and the update
            raise TemplateNotFoundError(f"La plantilla {template_id} no existe.")
        return updated
