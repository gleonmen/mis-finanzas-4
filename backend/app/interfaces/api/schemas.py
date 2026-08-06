"""Pydantic request/response schemas for the API."""
from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field

from app.domain.entities import Frequency, PaymentStatus, TransactionType


class TemplateOut(BaseModel):
    id: int
    name: str
    transaction_type: TransactionType
    category_code: str
    is_essential: bool | None
    default_amount: Decimal
    frequency: Frequency


class CategoryOut(BaseModel):
    id: int
    code: str
    transaction_type: TransactionType


class TemplateWriteIn(BaseModel):
    """Body for creating/updating a template. is_essential applies to EXPENSE
    only; for INCOME it is ignored (forced to None by the use case)."""

    transaction_type: TransactionType
    category_id: int
    name: str = Field(min_length=1)
    is_essential: bool | None = None
    default_amount: Decimal = Field(gt=0)
    frequency: Frequency


class MonthStatusOut(BaseModel):
    year: int
    month: int
    already_loaded: bool
    templates: list[TemplateOut]


class DraftLineIn(BaseModel):
    template_id: int
    amount: Decimal = Field(gt=0)
    occurred_on: date


class MonthLoadIn(BaseModel):
    lines: list[DraftLineIn]


class MonthLoadOut(BaseModel):
    created: int


# --- Transactions ----------------------------------------------------------


class TransactionOut(BaseModel):
    id: int
    transaction_type: TransactionType
    category_code: str
    name: str
    is_essential: bool | None
    frequency: Frequency
    amount: Decimal
    occurred_on: date
    payment_status: PaymentStatus
    template_id: int | None


class TransactionWriteIn(BaseModel):
    """Body for creating/updating a movement.

    On update `transaction_type` is ignored: the type is fixed at creation.
    `occurred_on` is free — it need not fall in any particular month.
    payment_status defaults to PENDING (a new ad-hoc movement is born pending).
    """

    transaction_type: TransactionType
    category_id: int
    name: str = Field(min_length=1)
    is_essential: bool | None = None
    amount: Decimal = Field(gt=0)
    occurred_on: date
    payment_status: PaymentStatus = PaymentStatus.PENDING


class MonthDeleteOut(BaseModel):
    deleted: int


class TransactionCreatedOut(BaseModel):
    transaction: TransactionOut
    # True when the movement is now the only one in its month, so the monthly
    # load is blocked there.
    blocks_monthly_load: bool


# --- Reports ---------------------------------------------------------------


class TotalsOut(BaseModel):
    income: Decimal
    expense: Decimal
    net: Decimal  # may be negative


class CategoryAmountOut(BaseModel):
    category_code: str  # "OTHER" for the folded tail
    amount: Decimal


class ConceptAmountOut(BaseModel):
    name: str
    category_code: str
    amount: Decimal


class EssentialSplitOut(BaseModel):
    essential: Decimal
    non_essential: Decimal


class MonthPointOut(BaseModel):
    month: int
    income: Decimal
    expense: Decimal
    net: Decimal


class MonthlyReportOut(BaseModel):
    year: int
    month: int
    totals: TotalsOut
    by_category: list[CategoryAmountOut]  # full detail (table source of truth)
    by_category_chart: list[CategoryAmountOut]  # top N + OTHER
    income_by_category: list[CategoryAmountOut]  # income breakdown (no OTHER)
    essential: EssentialSplitOut
    top_expense_concepts: list[ConceptAmountOut]


class AnnualReportOut(BaseModel):
    year: int
    totals: TotalsOut
    by_category: list[CategoryAmountOut]
    by_category_chart: list[CategoryAmountOut]
    income_by_category: list[CategoryAmountOut]
    essential: EssentialSplitOut
    monthly_series: list[MonthPointOut]  # always 12 points
    top_expense_concepts: list[ConceptAmountOut]


# Defined here (after TotalsOut) so the reference resolves without a forward ref.
class MonthTransactionsOut(BaseModel):
    year: int
    month: int
    totals: TotalsOut
    items: list[TransactionOut]
