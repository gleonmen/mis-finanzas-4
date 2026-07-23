"""Repository ports (interfaces). Adapters live in infrastructure/."""
from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.entities import Category, Template, TemplateData, Transaction


class CategoryRepository(ABC):
    @abstractmethod
    def list_all(self) -> list[Category]:
        """Return every fixed category, ordered by type then id."""

    @abstractmethod
    def get(self, category_id: int) -> Category | None:
        """Return a category by id, or None if it does not exist."""


class TemplateRepository(ABC):
    @abstractmethod
    def list_all(self) -> list[Template]:
        """Return every template, with its category_code resolved."""

    @abstractmethod
    def get(self, template_id: int) -> Template | None:
        """Return a template by id, or None if it does not exist."""

    @abstractmethod
    def create(self, data: TemplateData) -> Template:
        """Persist a new template and return it (with category_code resolved)."""

    @abstractmethod
    def update(self, template_id: int, data: TemplateData) -> Template | None:
        """Update an existing template; return it, or None if it does not exist."""

    @abstractmethod
    def delete(self, template_id: int) -> bool:
        """Delete a template. Returns True if a row was deleted, False otherwise."""


class TransactionRepository(ABC):
    @abstractmethod
    def count_in_month(self, year: int, month: int) -> int:
        """How many transactions fall within the given calendar month."""

    @abstractmethod
    def bulk_create(self, transactions: list[Transaction]) -> int:
        """Persist all transactions atomically. Returns the number created."""
