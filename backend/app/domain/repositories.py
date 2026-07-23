"""Repository ports (interfaces). Adapters live in infrastructure/."""
from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.entities import Template, Transaction


class TemplateRepository(ABC):
    @abstractmethod
    def list_all(self) -> list[Template]:
        """Return every template, with its category_code resolved."""


class TransactionRepository(ABC):
    @abstractmethod
    def count_in_month(self, year: int, month: int) -> int:
        """How many transactions fall within the given calendar month."""

    @abstractmethod
    def bulk_create(self, transactions: list[Transaction]) -> int:
        """Persist all transactions atomically. Returns the number created."""
