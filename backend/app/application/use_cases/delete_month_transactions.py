"""Use case: delete every movement of a month in one atomic operation."""
from __future__ import annotations

from app.application.use_cases.report_rules import validate_month, validate_year
from app.domain.repositories import TransactionRepository


class DeleteMonthTransactions:
    def __init__(self, transaction_repo: TransactionRepository) -> None:
        self._transactions = transaction_repo

    def execute(self, year: int, month: int) -> int:
        # Emptying a month also releases the monthly-load guard, which is how a
        # badly loaded month gets redone.
        validate_year(year)
        validate_month(month)
        return self._transactions.delete_in_month(year, month)
