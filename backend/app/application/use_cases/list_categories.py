"""Use case: list the fixed categories (feeds the template form selector)."""
from __future__ import annotations

from app.domain.entities import Category
from app.domain.repositories import CategoryRepository


class ListCategories:
    def __init__(self, category_repo: CategoryRepository) -> None:
        self._category_repo = category_repo

    def execute(self) -> list[Category]:
        return self._category_repo.list_all()
