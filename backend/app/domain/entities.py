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


class PaymentStatus(str, Enum):
    """Per-movement state (mutable, not a template snapshot). For income it reads
    as received/pending-to-collect; for expense as paid/pending-to-pay."""

    PAID = "PAID"
    PENDING = "PENDING"


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
class TransactionData:
    """Write payload for creating/updating a movement. Uses category_id (what the
    UI selects); the use case resolves the category_code kept in the snapshot.

    On update the transaction_type is IGNORED: the type is fixed at creation.
    """

    transaction_type: TransactionType
    category_id: int
    name: str
    is_essential: bool | None
    amount: Decimal
    occurred_on: date
    payment_status: PaymentStatus = PaymentStatus.PENDING


@dataclass(frozen=True)
class PeriodTotals:
    """Cash-basis totals for a period. net may be negative (spent more than earned)."""

    income: Decimal
    expense: Decimal
    net: Decimal


@dataclass(frozen=True)
class CategoryAmount:
    """Total amount for one category within a period."""

    category_code: str
    amount: Decimal


@dataclass(frozen=True)
class ConceptAmount:
    """Total expense for one concept (name) within a period, with its category."""

    name: str
    category_code: str
    amount: Decimal


@dataclass(frozen=True)
class EssentialSplit:
    """Expense split by is_essential. Income does not participate."""

    essential: Decimal
    non_essential: Decimal


@dataclass(frozen=True)
class MonthPoint:
    """One month of the annual series. Months without data come through as zeros."""

    month: int  # 1-12
    income: Decimal
    expense: Decimal
    net: Decimal


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
    # Mutable per-movement state; NOT part of the template snapshot.
    payment_status: PaymentStatus = PaymentStatus.PENDING
    template_id: int | None = None
    id: int | None = None
