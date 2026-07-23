"""Use case: create a new template."""
from __future__ import annotations

from app.application.use_cases.template_rules import validate_and_normalize
from app.domain.entities import Template, TemplateData
from app.domain.repositories import CategoryRepository, TemplateRepository


class CreateTemplate:
    def __init__(
        self,
        template_repo: TemplateRepository,
        category_repo: CategoryRepository,
    ) -> None:
        self._template_repo = template_repo
        self._category_repo = category_repo

    def execute(self, data: TemplateData) -> Template:
        normalized = validate_and_normalize(data, self._category_repo)
        return self._template_repo.create(normalized)
