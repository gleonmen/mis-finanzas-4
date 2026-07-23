"""SQLAlchemy ORM models mapping the tables from supabase/migrations.

The schema is owned by the SQL migrations; these models only map onto it (they
are not used to create the tables). Enum columns are mapped as plain strings and
validated by the DB's native enum types + CHECK constraints.
"""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import BigInteger, Boolean, Date, DateTime, ForeignKey, Numeric, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.entities import Frequency, TransactionType
from app.infrastructure.db import Base

# Map onto the existing native Postgres enum types (created by the migrations, so
# create_type=False). values_callable makes SQLAlchemy bind the enum *values*
# (e.g. 'INCOME') rather than casting to VARCHAR, which the enum column rejects.
_TRANSACTION_TYPE = SAEnum(
    TransactionType,
    name="transaction_type",
    create_type=False,
    values_callable=lambda enum: [m.value for m in enum],
)
_FREQUENCY = SAEnum(
    Frequency,
    name="frequency",
    create_type=False,
    values_callable=lambda enum: [m.value for m in enum],
)


class CategoryModel(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String, unique=True)
    transaction_type: Mapped[TransactionType] = mapped_column(_TRANSACTION_TYPE)


class TemplateModel(Base):
    __tablename__ = "templates"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String)
    transaction_type: Mapped[TransactionType] = mapped_column(_TRANSACTION_TYPE)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    is_essential: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    default_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    frequency: Mapped[Frequency] = mapped_column(_FREQUENCY)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class TransactionModel(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    # Snapshot columns (frozen at creation time).
    transaction_type: Mapped[TransactionType] = mapped_column(_TRANSACTION_TYPE)
    category_code: Mapped[str] = mapped_column(String)
    name: Mapped[str] = mapped_column(String)
    is_essential: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    frequency: Mapped[Frequency] = mapped_column(_FREQUENCY)
    # Movement data.
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    occurred_on: Mapped[date] = mapped_column(Date)
    template_id: Mapped[int | None] = mapped_column(
        ForeignKey("templates.id", ondelete="SET NULL"), nullable=True
    )
    # created_at is filled by the DB default (now()); intentionally not mapped so
    # inserts omit it instead of sending NULL.
