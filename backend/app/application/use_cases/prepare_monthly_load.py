"""Use case: prepare the data needed to render the monthly-load grid."""
from __future__ import annotations

from dataclasses import dataclass

from app.domain.entities import Template
from app.domain.repositories import TemplateRepository, TransactionRepository


@dataclass(frozen=True)
class MonthlyLoadStatus:
    year: int
    month: int
    already_loaded: bool
    templates: list[Template]


class PrepareMonthlyLoad:
    """Returns all templates for the draft grid plus the presence guard status.

    The frontend builds each draft row locally (amount = default_amount,
    date = first day of the month). If the month is already loaded, the UI warns
    and does not offer to confirm.
    """

    def __init__(
        self,
        template_repo: TemplateRepository,
        transaction_repo: TransactionRepository,
    ) -> None:
        self._template_repo = template_repo
        self._transaction_repo = transaction_repo

    def execute(self, year: int, month: int) -> MonthlyLoadStatus:
        already_loaded = self._transaction_repo.count_in_month(year, month) > 0
        templates = self._template_repo.list_all()
        return MonthlyLoadStatus(
            year=year,
            month=month,
            already_loaded=already_loaded,
            templates=templates,
        )
