"""Use case: the monthly report package (one request feeds the whole view)."""
from __future__ import annotations

from dataclasses import dataclass

from app.application.use_cases.report_rules import collapse_to_top, month_range
from app.domain.entities import CategoryAmount, EssentialSplit, PeriodTotals
from app.domain.repositories import ReportRepository


@dataclass(frozen=True)
class MonthlyReportResult:
    year: int
    month: int
    totals: PeriodTotals
    # Full breakdown (source of truth for the table) and the chart-sized list
    # (top N + "Otros"). Both sum to the same total.
    by_category: list[CategoryAmount]
    by_category_chart: list[CategoryAmount]
    # Income breakdown by category. Income has <= 6 categories, so no "Otros"
    # folding: the full list feeds both the chart and the table.
    income_by_category: list[CategoryAmount]
    essential: EssentialSplit


class MonthlyReport:
    def __init__(self, report_repo: ReportRepository) -> None:
        self._repo = report_repo

    def execute(self, year: int, month: int) -> MonthlyReportResult:
        # Cash basis: the range is driven by occurred_on only. `frequency` is
        # metadata and never takes part in the calculation.
        start, end = month_range(year, month)

        totals = self._repo.totals(start, end)
        by_category = self._repo.expense_by_category(start, end)
        essential = self._repo.essential_split(start, end)

        return MonthlyReportResult(
            year=year,
            month=month,
            totals=totals,
            by_category=by_category,
            by_category_chart=collapse_to_top(by_category),
            income_by_category=self._repo.income_by_category(start, end),
            essential=essential,
        )
