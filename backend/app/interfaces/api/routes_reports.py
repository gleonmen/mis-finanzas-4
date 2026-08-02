"""Report endpoints: one request per view, all aggregations included."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, HTTPException, Path

from app.application.errors import InvalidPeriodError
from app.interfaces.api.deps import AnnualReportDep, MonthlyReportDep
from app.interfaces.api.schemas import (
    AnnualReportOut,
    CategoryAmountOut,
    EssentialSplitOut,
    MonthPointOut,
    MonthlyReportOut,
    PaymentSplitOut,
    TotalsOut,
)

router = APIRouter(prefix="/reports", tags=["reports"])

MonthPath = Annotated[int, Path(ge=1, le=12)]
YearPath = Annotated[int, Path(ge=1970, le=9999)]


def _totals(t) -> TotalsOut:
    return TotalsOut(income=t.income, expense=t.expense, net=t.net)


def _categories(items) -> list[CategoryAmountOut]:
    return [
        CategoryAmountOut(category_code=c.category_code, amount=c.amount)
        for c in items
    ]


def _essential(e) -> EssentialSplitOut:
    return EssentialSplitOut(essential=e.essential, non_essential=e.non_essential)


def _payment(p) -> PaymentSplitOut:
    return PaymentSplitOut(paid=p.paid, pending=p.pending)


@router.get("/monthly/{year}/{month}", response_model=MonthlyReportOut)
def monthly_report(
    year: YearPath, month: MonthPath, use_case: MonthlyReportDep
) -> MonthlyReportOut:
    try:
        result = use_case.execute(year=year, month=month)
    except InvalidPeriodError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return MonthlyReportOut(
        year=result.year,
        month=result.month,
        totals=_totals(result.totals),
        by_category=_categories(result.by_category),
        by_category_chart=_categories(result.by_category_chart),
        income_by_category=_categories(result.income_by_category),
        essential=_essential(result.essential),
        expense_payment=_payment(result.expense_payment),
        income_payment=_payment(result.income_payment),
    )


@router.get("/annual/{year}", response_model=AnnualReportOut)
def annual_report(year: YearPath, use_case: AnnualReportDep) -> AnnualReportOut:
    try:
        result = use_case.execute(year=year)
    except InvalidPeriodError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return AnnualReportOut(
        year=result.year,
        totals=_totals(result.totals),
        by_category=_categories(result.by_category),
        by_category_chart=_categories(result.by_category_chart),
        income_by_category=_categories(result.income_by_category),
        essential=_essential(result.essential),
        monthly_series=[
            MonthPointOut(
                month=p.month, income=p.income, expense=p.expense, net=p.net
            )
            for p in result.monthly_series
        ],
    )
