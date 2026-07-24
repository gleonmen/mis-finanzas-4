"""Use case: the movements of a month, with the month totals for context."""
from __future__ import annotations

from dataclasses import dataclass

from app.application.use_cases.report_rules import month_range
from app.domain.entities import PeriodTotals, Transaction
from app.domain.repositories import ReportRepository, TransactionRepository


@dataclass(frozen=True)
class MonthTransactions:
    year: int
    month: int
    totals: PeriodTotals
    items: list[Transaction]


class ListMonthTransactions:
    def __init__(
        self,
        transaction_repo: TransactionRepository,
        report_repo: ReportRepository,
    ) -> None:
        self._transactions = transaction_repo
        self._reports = report_repo

    def execute(self, year: int, month: int) -> MonthTransactions:
        start, end = month_range(year, month)  # also validates the period
        return MonthTransactions(
            year=year,
            month=month,
            # Reuse the report aggregation instead of re-summing here.
            totals=self._reports.totals(start, end),
            items=self._transactions.list_in_month(year, month),
        )
