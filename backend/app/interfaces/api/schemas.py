"""Pydantic request/response schemas for the API."""
from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field

from app.domain.entities import Frequency, TransactionType


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
