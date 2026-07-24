"""Repository ports (interfaces). Adapters live in infrastructure/."""
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date

from app.domain.entities import (
    Category,
    CategoryAmount,
    EssentialSplit,
    Frequency,
    MonthPoint,
    PeriodTotals,
    Template,
    TemplateData,
    Transaction,
    TransactionData,
)


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

    @abstractmethod
    def list_in_month(self, year: int, month: int) -> list[Transaction]:
        """Movements of the month, ordered by date then id."""

    @abstractmethod
    def get(self, transaction_id: int) -> Transaction | None:
        """Return a movement by id, or None if it does not exist."""

    @abstractmethod
    def create_one(
        self,
        data: TransactionData,
        category_code: str,
        frequency: Frequency,
        template_id: int | None = None,
    ) -> Transaction:
        """Persist a single movement and return it with its id."""

    @abstractmethod
    def update(
        self, transaction_id: int, data: TransactionData, category_code: str
    ) -> Transaction | None:
        """Update the editable fields. Type, frequency and template_id are
        preserved. Returns None if the movement does not exist."""

    @abstractmethod
    def delete(self, transaction_id: int) -> bool:
        """Delete a movement. True if a row was deleted."""


class ReportRepository(ABC):
    """Cash-basis aggregations. All ranges are half-open: [start, end).

    A movement counts in full in the month of its date; `frequency` never takes
    part in any calculation.
    """

    @abstractmethod
    def totals(self, start: date, end: date) -> PeriodTotals:
        """Income, expense and net for the period."""

    @abstractmethod
    def expense_by_category(self, start: date, end: date) -> list[CategoryAmount]:
        """Expense totals per category, ordered by amount descending."""

    @abstractmethod
    def essential_split(self, start: date, end: date) -> EssentialSplit:
        """Expense split into essential / non-essential."""

    @abstractmethod
    def monthly_series(self, year: int) -> list[MonthPoint]:
        """Per-month totals for the year. Only months WITH data are returned;
        the use case pads the year to 12 points."""
