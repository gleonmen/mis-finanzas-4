"""SQLAlchemy adapters implementing the domain repository ports."""
from __future__ import annotations

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.domain.entities import (
    Category,
    Frequency,
    Template,
    TemplateData,
    Transaction,
    TransactionType,
)
from app.domain.repositories import (
    CategoryRepository,
    TemplateRepository,
    TransactionRepository,
)
from app.infrastructure.models import CategoryModel, TemplateModel, TransactionModel


def _next_month(year: int, month: int) -> tuple[int, int]:
    return (year + 1, 1) if month == 12 else (year, month + 1)


def _category_entity(model: CategoryModel) -> Category:
    return Category(
        id=model.id,
        code=model.code,
        transaction_type=TransactionType(model.transaction_type),
    )


class SqlAlchemyCategoryRepository(CategoryRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_all(self) -> list[Category]:
        rows = (
            self._session.execute(
                select(CategoryModel).order_by(
                    CategoryModel.transaction_type, CategoryModel.id
                )
            )
            .scalars()
            .all()
        )
        return [_category_entity(c) for c in rows]

    def get(self, category_id: int) -> Category | None:
        model = self._session.get(CategoryModel, category_id)
        return None if model is None else _category_entity(model)


class SqlAlchemyTemplateRepository(TemplateRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def _to_entity(self, model: TemplateModel) -> Template:
        code = self._session.scalar(
            select(CategoryModel.code).where(CategoryModel.id == model.category_id)
        )
        return Template(
            id=model.id,
            name=model.name,
            transaction_type=TransactionType(model.transaction_type),
            category_code=code or "",
            is_essential=model.is_essential,
            default_amount=model.default_amount,
            frequency=Frequency(model.frequency),
        )

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

    def get(self, template_id: int) -> Template | None:
        model = self._session.get(TemplateModel, template_id)
        return None if model is None else self._to_entity(model)

    def create(self, data: TemplateData) -> Template:
        model = TemplateModel(
            name=data.name,
            transaction_type=data.transaction_type,
            category_id=data.category_id,
            is_essential=data.is_essential,
            default_amount=data.default_amount,
            frequency=data.frequency,
        )
        self._session.add(model)
        self._session.flush()
        return self._to_entity(model)

    def update(self, template_id: int, data: TemplateData) -> Template | None:
        model = self._session.get(TemplateModel, template_id)
        if model is None:
            return None
        model.name = data.name
        model.transaction_type = data.transaction_type
        model.category_id = data.category_id
        model.is_essential = data.is_essential
        model.default_amount = data.default_amount
        model.frequency = data.frequency
        self._session.flush()
        return self._to_entity(model)

    def delete(self, template_id: int) -> bool:
        model = self._session.get(TemplateModel, template_id)
        if model is None:
            return False
        self._session.delete(model)
        self._session.flush()
        return True


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
