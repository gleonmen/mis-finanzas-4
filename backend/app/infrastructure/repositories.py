"""SQLAlchemy adapters implementing the domain repository ports."""
from __future__ import annotations

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.domain.entities import Frequency, Template, Transaction, TransactionType
from app.domain.repositories import TemplateRepository, TransactionRepository
from app.infrastructure.models import CategoryModel, TemplateModel, TransactionModel


def _next_month(year: int, month: int) -> tuple[int, int]:
    return (year + 1, 1) if month == 12 else (year, month + 1)


class SqlAlchemyTemplateRepository(TemplateRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_all(self) -> list[Template]:
        rows = self._session.execute(
            select(TemplateModel, CategoryModel.code)
            .join(CategoryModel, CategoryModel.id == TemplateModel.category_id)
            .order_by(TemplateModel.transaction_type, TemplateModel.id)
        ).all()
        return [
            Template(
                id=tpl.id,
                name=tpl.name,
                transaction_type=TransactionType(tpl.transaction_type),
                category_code=code,
                is_essential=tpl.is_essential,
                default_amount=tpl.default_amount,
                frequency=Frequency(tpl.frequency),
            )
            for tpl, code in rows
        ]


class SqlAlchemyTransactionRepository(TransactionRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def count_in_month(self, year: int, month: int) -> int:
        start = date(year, month, 1)
        ny, nm = _next_month(year, month)
        end = date(ny, nm, 1)
        return self._session.scalar(
            select(func.count())
            .select_from(TransactionModel)
            .where(TransactionModel.occurred_on >= start)
            .where(TransactionModel.occurred_on < end)
        ) or 0

    def bulk_create(self, transactions: list[Transaction]) -> int:
        models = [
            TransactionModel(
                transaction_type=t.transaction_type,
                category_code=t.category_code,
                name=t.name,
                is_essential=t.is_essential,
                frequency=t.frequency,
                amount=t.amount,
                occurred_on=t.occurred_on,
                template_id=t.template_id,
            )
            for t in transactions
        ]
        self._session.add_all(models)
        # Flush (not commit) so the whole request stays in one transaction; the
        # API dependency commits once on success and rolls back on any error.
        self._session.flush()
        return len(models)
