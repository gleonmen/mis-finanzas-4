"""Use case: the annual report package (one request feeds the whole view)."""
from __future__ import annotations

from dataclasses import dataclass

from app.application.use_cases.report_rules import (
    collapse_to_top,
    pad_year,
    year_range,
)
from app.domain.entities import (
    CategoryAmount,
    EssentialSplit,
    MonthPoint,
    PeriodTotals,
)
from app.domain.repositories import ReportRepository


@dataclass(frozen=True)
class AnnualReportResult:
    year: int
    totals: PeriodTotals
    by_category: list[CategoryAmount]
    by_category_chart: list[CategoryAmount]
    essential: EssentialSplit
    monthly_series: list[MonthPoint]  # always 12 points, in order


class AnnualReport:
    def __init__(self, report_repo: ReportRepository) -> None:
        self._repo = report_repo

    def execute(self, year: int) -> AnnualReportResult:
        start, end = year_range(year)

        totals = self._repo.totals(start, end)
        by_category = self._repo.expense_by_category(start, end)
        essential = self._repo.essential_split(start, end)
        # Pad to 12 months so the trend never skips a month with no movements.
        series = pad_year(self._repo.monthly_series(year))

        return AnnualReportResult(
            year=year,
            totals=totals,
            by_category=by_category,
            by_category_chart=collapse_to_top(by_category),
            essential=essential,
            monthly_series=series,
        )
