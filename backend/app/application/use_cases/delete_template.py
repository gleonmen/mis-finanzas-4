"""Use case: delete a template (hard delete)."""
from __future__ import annotations

from app.application.errors import TemplateNotFoundError
from app.domain.repositories import TemplateRepository


class DeleteTemplate:
    def __init__(self, template_repo: TemplateRepository) -> None:
        self._template_repo = template_repo

    def execute(self, template_id: int) -> None:
        # Hard delete. History is protected: transactions keep their snapshot and
        # their template_id becomes NULL (ON DELETE SET NULL in the schema).
        deleted = self._template_repo.delete(template_id)
        if not deleted:
            raise TemplateNotFoundError(f"La plantilla {template_id} no existe.")
