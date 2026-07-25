from datetime import date
from decimal import Decimal

import pytest

from app.application.errors import InvalidPeriodError
from app.application.use_cases.annual_report import AnnualReport
from app.application.use_cases.monthly_report import MonthlyReport
from app.application.use_cases.report_rules import (
    OTHER_CATEGORY_CODE,
    collapse_to_top,
    month_range,
    pad_year,
    year_range,
)
from app.domain.entities import (
    CategoryAmount,
    EssentialSplit,
    MonthPoint,
    PeriodTotals,
)

ZERO = Decimal("0")


class FakeReportRepo:
    """Aggregates a plain list of (type, category, is_essential, amount, date)."""

    def __init__(self, rows=()):
        self.rows = list(rows)

    def _in(self, start, end):
        return [r for r in self.rows if start <= r["date"] < end]

    def totals(self, start, end):
        rows = self._in(start, end)
        income = sum((r["amount"] for r in rows if r["type"] == "INCOME"), ZERO)
        expense = sum((r["amount"] for r in rows if r["type"] == "EXPENSE"), ZERO)
        return PeriodTotals(income=income, expense=expense, net=income - expense)

    def _by_category(self, start, end, tx_type):
        acc = {}
        for r in self._in(start, end):
            if r["type"] == tx_type:
                acc[r["category"]] = acc.get(r["category"], ZERO) + r["amount"]
        ordered = sorted(acc.items(), key=lambda kv: kv[1], reverse=True)
        return [CategoryAmount(category_code=c, amount=a) for c, a in ordered]

    def expense_by_category(self, start, end):
        return self._by_category(start, end, "EXPENSE")

    def income_by_category(self, start, end):
        return self._by_category(start, end, "INCOME")

    def essential_split(self, start, end):
        ess, non = ZERO, ZERO
        for r in self._in(start, end):
            if r["type"] != "EXPENSE":
                continue
            if r["essential"]:
                ess += r["amount"]
            else:
                non += r["amount"]
        return EssentialSplit(essential=ess, non_essential=non)

    def monthly_series(self, year):
        start, end = date(year, 1, 1), date(year + 1, 1, 1)
        by_month = {}
        for r in self._in(start, end):
            m = r["date"].month
            inc, exp = by_month.get(m, (ZERO, ZERO))
            if r["type"] == "INCOME":
                inc += r["amount"]
            else:
                exp += r["amount"]
            by_month[m] = (inc, exp)
        return [
            MonthPoint(month=m, income=i, expense=e, net=i - e)
            for m, (i, e) in sorted(by_month.items())
        ]


def row(type_, category, essential, amount, d):
    return {
        "type": type_,
        "category": category,
        "essential": essential,
        "amount": Decimal(amount),
        "date": d,
    }


# --- period ranges (cash basis) -------------------------------------------

def test_month_range_is_half_open():
    assert month_range(2026, 7) == (date(2026, 7, 1), date(2026, 8, 1))


def test_month_range_wraps_december():
    assert month_range(2026, 12) == (date(2026, 12, 1), date(2027, 1, 1))


def test_year_range():
    assert year_range(2026) == (date(2026, 1, 1), date(2027, 1, 1))


def test_invalid_month_rejected():
    with pytest.raises(InvalidPeriodError):
        month_range(2026, 13)


# --- top N + Otros ---------------------------------------------------------

def cat(code, amount):
    return CategoryAmount(category_code=code, amount=Decimal(amount))


def test_collapse_keeps_list_when_within_limit():
    items = [cat(f"c{i}", 10) for i in range(7)]
    assert collapse_to_top(items) == items


def test_collapse_folds_tail_into_other_preserving_total():
    items = [cat(f"c{i}", 100 - i) for i in range(10)]
    collapsed = collapse_to_top(items)
    assert len(collapsed) == 8
    assert collapsed[-1].category_code == OTHER_CATEGORY_CODE
    # The collapsed list must sum to exactly the same total as the full list.
    assert sum(c.amount for c in collapsed) == sum(c.amount for c in items)


# --- annual padding --------------------------------------------------------

def test_pad_year_returns_twelve_months_with_zeros():
    padded = pad_year([MonthPoint(3, Decimal("10"), Decimal("4"), Decimal("6"))])
    assert len(padded) == 12
    assert [p.month for p in padded] == list(range(1, 13))
    assert padded[2].income == Decimal("10")
    assert padded[0].income == ZERO and padded[0].net == ZERO


# --- report use cases ------------------------------------------------------

def test_monthly_report_totals_and_split():
    repo = FakeReportRepo([
        row("INCOME", "salaries", None, "3500000", date(2026, 7, 5)),
        row("EXPENSE", "housing_utilities", True, "1300000", date(2026, 7, 1)),
        row("EXPENSE", "lifestyle", False, "44900", date(2026, 7, 10)),
        row("EXPENSE", "transport", True, "250000", date(2026, 8, 1)),  # other month
    ])
    result = MonthlyReport(repo).execute(2026, 7)
    assert result.totals.income == Decimal("3500000")
    assert result.totals.expense == Decimal("1344900")
    assert result.totals.net == Decimal("2155100")
    assert result.essential.essential == Decimal("1300000")
    assert result.essential.non_essential == Decimal("44900")
    assert result.by_category[0].category_code == "housing_utilities"


def test_negative_net_is_preserved():
    repo = FakeReportRepo([
        row("INCOME", "salaries", None, "100", date(2026, 7, 1)),
        row("EXPENSE", "lifestyle", False, "500", date(2026, 7, 2)),
    ])
    result = MonthlyReport(repo).execute(2026, 7)
    assert result.totals.net == Decimal("-400")


def test_empty_period_returns_zeros_not_error():
    result = MonthlyReport(FakeReportRepo()).execute(2026, 7)
    assert result.totals.income == ZERO
    assert result.totals.expense == ZERO
    assert result.totals.net == ZERO
    assert result.by_category == []
    assert result.by_category_chart == []


def test_annual_expense_lands_whole_in_its_month_not_prorated():
    """Cash basis: an ANNUAL 900k expense dated March counts 900k in March,
    not 75k per month. `frequency` never affects the calculation."""
    repo = FakeReportRepo([
        row("EXPENSE", "transport", True, "900000", date(2026, 3, 15)),
    ])
    series = AnnualReport(repo).execute(2026).monthly_series
    assert series[2].expense == Decimal("900000")  # March
    assert all(p.expense == ZERO for i, p in enumerate(series) if i != 2)


def test_annual_totals_equal_sum_of_twelve_months():
    repo = FakeReportRepo([
        row("INCOME", "salaries", None, "1000", date(2026, 1, 5)),
        row("INCOME", "salaries", None, "1000", date(2026, 6, 5)),
        row("EXPENSE", "lifestyle", False, "300", date(2026, 6, 20)),
        row("EXPENSE", "transport", True, "700", date(2026, 12, 31)),
    ])
    result = AnnualReport(repo).execute(2026)
    assert sum(p.income for p in result.monthly_series) == result.totals.income
    assert sum(p.expense for p in result.monthly_series) == result.totals.expense
    assert sum(p.net for p in result.monthly_series) == result.totals.net


def test_annual_series_always_has_twelve_points():
    result = AnnualReport(FakeReportRepo()).execute(2026)
    assert len(result.monthly_series) == 12


# --- income by category ----------------------------------------------------

def test_income_by_category_sorted_desc_and_sums_to_income_total():
    repo = FakeReportRepo([
        row("INCOME", "salaries", None, "3500000", date(2026, 7, 1)),
        row("INCOME", "freelance", None, "800000", date(2026, 7, 12)),
        row("INCOME", "rentals", None, "1200000", date(2026, 7, 20)),
        row("EXPENSE", "transport", True, "250000", date(2026, 7, 5)),  # ignored
    ])
    result = MonthlyReport(repo).execute(2026, 7)
    codes = [c.category_code for c in result.income_by_category]
    assert codes == ["salaries", "rentals", "freelance"]  # desc by amount
    # Invariant: the income breakdown sums to the income total.
    assert sum(c.amount for c in result.income_by_category) == result.totals.income


def test_income_by_category_omits_categories_without_movements():
    repo = FakeReportRepo([
        row("INCOME", "salaries", None, "3500000", date(2026, 7, 1)),
    ])
    result = MonthlyReport(repo).execute(2026, 7)
    assert [c.category_code for c in result.income_by_category] == ["salaries"]


def test_income_by_category_empty_when_no_income():
    repo = FakeReportRepo([
        row("EXPENSE", "transport", True, "250000", date(2026, 7, 5)),
    ])
    result = MonthlyReport(repo).execute(2026, 7)
    assert result.income_by_category == []


def test_annual_income_by_category_present():
    repo = FakeReportRepo([
        row("INCOME", "salaries", None, "1000", date(2026, 3, 1)),
        row("INCOME", "business", None, "4000", date(2026, 9, 1)),
    ])
    result = AnnualReport(repo).execute(2026)
    assert [c.category_code for c in result.income_by_category] == [
        "business",
        "salaries",
    ]
    assert sum(c.amount for c in result.income_by_category) == result.totals.income
