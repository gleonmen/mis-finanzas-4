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
