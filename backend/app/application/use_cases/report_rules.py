"""Shared cash-basis rules for reports: period ranges, top-N collapse, padding."""
from __future__ import annotations

from datetime import date
from decimal import Decimal

from app.application.errors import InvalidPeriodError
from app.domain.entities import CategoryAmount, MonthPoint

ZERO = Decimal("0")

# Categories shown individually in the composition chart; the rest fold into OTHER.
TOP_CATEGORY_LIMIT = 7
OTHER_CATEGORY_CODE = "OTHER"

MIN_YEAR = 1970
MAX_YEAR = 9999


def validate_year(year: int) -> None:
    if not (MIN_YEAR <= year <= MAX_YEAR):
        raise InvalidPeriodError(f"El año {year} está fuera de rango.")


def validate_month(month: int) -> None:
    if not (1 <= month <= 12):
        raise InvalidPeriodError(f"El mes {month} no es válido.")


def month_range(year: int, month: int) -> tuple[date, date]:
    """Half-open [first day of month, first day of next month)."""
    validate_year(year)
    validate_month(month)
    start = date(year, month, 1)
    end = date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)
    return start, end


def year_range(year: int) -> tuple[date, date]:
    """Half-open [Jan 1, Jan 1 of next year)."""
    validate_year(year)
    return date(year, 1, 1), date(year + 1, 1, 1)


def collapse_to_top(
    categories: list[CategoryAmount], limit: int = TOP_CATEGORY_LIMIT
) -> list[CategoryAmount]:
    """Keep the `limit` largest categories and fold the tail into OTHER.

    Never generate a new color slot for a 9th category: the tail becomes a single
    neutral "Otros" entry. The collapsed list sums to the same total as the input.
    """
    if len(categories) <= limit:
        return list(categories)
    head = list(categories[:limit])
    tail_total = sum((c.amount for c in categories[limit:]), ZERO)
    head.append(CategoryAmount(category_code=OTHER_CATEGORY_CODE, amount=tail_total))
    return head


def pad_year(points: list[MonthPoint]) -> list[MonthPoint]:
    """Return exactly 12 months in order, filling missing months with zeros so the
    trend never skips a month."""
    by_month = {p.month: p for p in points}
    return [
        by_month.get(m, MonthPoint(month=m, income=ZERO, expense=ZERO, net=ZERO))
        for m in range(1, 13)
    ]
