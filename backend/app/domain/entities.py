"""Domain entities and value objects. No framework/DB dependencies here."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import Enum


class TransactionType(str, Enum):
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"


class Frequency(str, Enum):
    MONTHLY = "MONTHLY"
    BIMONTHLY = "BIMONTHLY"
    QUARTERLY = "QUARTERLY"
    SEMIANNUAL = "SEMIANNUAL"
    ANNUAL = "ANNUAL"
    ONE_TIME = "ONE_TIME"


@dataclass(frozen=True)
class Category:
    """A fixed catalog category (a "group"). Not user-editable."""

    id: int
    code: str
    transaction_type: TransactionType


@dataclass(frozen=True)
class Template:
    """A configurable movement "type"; preloads amount + frequency on entry."""

    id: int
    name: str
    transaction_type: TransactionType
    category_code: str
    is_essential: bool | None  # required for EXPENSE, None for INCOME
    default_amount: Decimal
    frequency: Frequency


@dataclass(frozen=True)
class TemplateData:
    """Write payload for creating/updating a template. Uses category_id (what the
    UI selects), not category_code."""

    transaction_type: TransactionType
    category_id: int
    name: str
    is_essential: bool | None
    default_amount: Decimal
    frequency: Frequency


@dataclass(frozen=True)
class Transaction:
    """A real movement. Carries a frozen SNAPSHOT of the template fields so that
    editing/deleting the template or category never changes historical reports."""

    transaction_type: TransactionType
    category_code: str
    name: str
    is_essential: bool | None
    frequency: Frequency
    amount: Decimal
    occurred_on: date
    template_id: int | None = None
    id: int | None = None
