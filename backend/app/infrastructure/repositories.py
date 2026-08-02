"""SQLAlchemy adapters implementing the domain repository ports."""
from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import delete as sa_delete
from sqlalchemy import extract, func, select
from sqlalchemy.orm import Session

from app.domain.entities import (
    Category,
    CategoryAmount,
    EssentialSplit,
    Frequency,
    MonthPoint,
    PaymentSplit,
    PaymentStatus,
    PeriodTotals,
    Template,
    TemplateData,
    Transaction,
    TransactionData,
    TransactionType,
)
from app.domain.repositories import (
    CategoryRepository,
    ReportRepository,
    TemplateRepository,
    TransactionRepository,
)
from app.infrastructure.models import CategoryModel, TemplateModel, TransactionModel

ZERO = Decimal("0")


def _next_month(year: int, month: int) -> tuple[int, int]:
    return (year + 1, 1) if month == 12 else (year, month + 1)


def _dec(value) -> Decimal:
    """Normalize a SUM result (which is NULL on an empty set) to Decimal."""
    return ZERO if value is None else Decimal(value)


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


class SqlAlchemyReportRepository(ReportRepository):
    """Cash-basis aggregations in SQL. All ranges are half-open [start, end) on
    occurred_on, which uses idx_transactions_occurred_on. `frequency` is never
    part of any calculation."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def _in_range(self, start: date, end: date):
        return (TransactionModel.occurred_on >= start) & (
            TransactionModel.occurred_on < end
        )

    def totals(self, start: date, end: date) -> PeriodTotals:
        income_sum = func.sum(TransactionModel.amount).filter(
            TransactionModel.transaction_type == TransactionType.INCOME
        )
        expense_sum = func.sum(TransactionModel.amount).filter(
            TransactionModel.transaction_type == TransactionType.EXPENSE
        )
        row = self._session.execute(
            select(income_sum, expense_sum)
            .select_from(TransactionModel)
            .where(self._in_range(start, end))
        ).one()
        income, expense = _dec(row[0]), _dec(row[1])
        return PeriodTotals(income=income, expense=expense, net=income - expense)

    def _by_category(
        self, start: date, end: date, tx_type: TransactionType
    ) -> list[CategoryAmount]:
        total = func.sum(TransactionModel.amount).label("total")
        rows = self._session.execute(
            select(TransactionModel.category_code, total)
            .where(self._in_range(start, end))
            .where(TransactionModel.transaction_type == tx_type)
            .group_by(TransactionModel.category_code)
            .order_by(total.desc())
        ).all()
        return [
            CategoryAmount(category_code=code, amount=_dec(amount))
            for code, amount in rows
        ]

    def expense_by_category(self, start: date, end: date) -> list[CategoryAmount]:
        return self._by_category(start, end, TransactionType.EXPENSE)

    def income_by_category(self, start: date, end: date) -> list[CategoryAmount]:
        return self._by_category(start, end, TransactionType.INCOME)

    def essential_split(self, start: date, end: date) -> EssentialSplit:
        rows = self._session.execute(
            select(TransactionModel.is_essential, func.sum(TransactionModel.amount))
            .where(self._in_range(start, end))
            .where(TransactionModel.transaction_type == TransactionType.EXPENSE)
            .group_by(TransactionModel.is_essential)
        ).all()
        essential, non_essential = ZERO, ZERO
        for is_essential, amount in rows:
            if is_essential:
                essential = _dec(amount)
            else:
                non_essential = _dec(amount)
        return EssentialSplit(essential=essential, non_essential=non_essential)

    def monthly_series(self, year: int) -> list[MonthPoint]:
        month_col = extract("month", TransactionModel.occurred_on).label("month")
        income_sum = func.sum(TransactionModel.amount).filter(
            TransactionModel.transaction_type == TransactionType.INCOME
        )
        expense_sum = func.sum(TransactionModel.amount).filter(
            TransactionModel.transaction_type == TransactionType.EXPENSE
        )
        rows = self._session.execute(
            select(month_col, income_sum, expense_sum)
            .where(self._in_range(date(year, 1, 1), date(year + 1, 1, 1)))
            .group_by(month_col)
            .order_by(month_col)
        ).all()
        points = []
        for month, income, expense in rows:
            inc, exp = _dec(income), _dec(expense)
            points.append(
                MonthPoint(month=int(month), income=inc, expense=exp, net=inc - exp)
            )
        return points

    def payment_split(
        self, start: date, end: date, tx_type: TransactionType
    ) -> PaymentSplit:
        paid_sum = func.sum(TransactionModel.amount).filter(
            TransactionModel.payment_status == PaymentStatus.PAID
        )
        pending_sum = func.sum(TransactionModel.amount).filter(
            TransactionModel.payment_status == PaymentStatus.PENDING
        )
        row = self._session.execute(
            select(paid_sum, pending_sum)
            .select_from(TransactionModel)
            .where(self._in_range(start, end))
            .where(TransactionModel.transaction_type == tx_type)
        ).one()
        return PaymentSplit(paid=_dec(row[0]), pending=_dec(row[1]))


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
                payment_status=t.payment_status,
                template_id=t.template_id,
            )
            for t in transactions
        ]
        self._session.add_all(models)
        # Flush (not commit) so the whole request stays in one transaction; the
        # API dependency commits once on success and rolls back on any error.
        self._session.flush()
        return len(models)

    def _to_entity(self, model: TransactionModel) -> Transaction:
        return Transaction(
            id=model.id,
            transaction_type=TransactionType(model.transaction_type),
            category_code=model.category_code,
            name=model.name,
            is_essential=model.is_essential,
            frequency=Frequency(model.frequency),
            amount=model.amount,
            occurred_on=model.occurred_on,
            payment_status=PaymentStatus(model.payment_status),
            template_id=model.template_id,
        )

    def list_in_month(self, year: int, month: int) -> list[Transaction]:
        start = date(year, month, 1)
        ny, nm = _next_month(year, month)
        rows = (
            self._session.execute(
                select(TransactionModel)
                .where(TransactionModel.occurred_on >= start)
                .where(TransactionModel.occurred_on < date(ny, nm, 1))
                .order_by(TransactionModel.occurred_on, TransactionModel.id)
            )
            .scalars()
            .all()
        )
        return [self._to_entity(m) for m in rows]

    def get(self, transaction_id: int) -> Transaction | None:
        model = self._session.get(TransactionModel, transaction_id)
        return None if model is None else self._to_entity(model)

    def create_one(
        self,
        data: TransactionData,
        category_code: str,
        frequency: Frequency,
        template_id: int | None = None,
    ) -> Transaction:
        model = TransactionModel(
            transaction_type=data.transaction_type,
            category_code=category_code,
            name=data.name,
            is_essential=data.is_essential,
            frequency=frequency,
            amount=data.amount,
            occurred_on=data.occurred_on,
            payment_status=data.payment_status,
            template_id=template_id,
        )
        self._session.add(model)
        self._session.flush()
        return self._to_entity(model)

    def update(
        self, transaction_id: int, data: TransactionData, category_code: str
    ) -> Transaction | None:
        model = self._session.get(TransactionModel, transaction_id)
        if model is None:
            return None
        # Only the editable fields. transaction_type, frequency and template_id
        # are deliberately left untouched.
        model.category_code = category_code
        model.name = data.name
        model.is_essential = data.is_essential
        model.amount = data.amount
        model.occurred_on = data.occurred_on
        model.payment_status = data.payment_status
        self._session.flush()
        return self._to_entity(model)

    def delete(self, transaction_id: int) -> bool:
        model = self._session.get(TransactionModel, transaction_id)
        if model is None:
            return False
        self._session.delete(model)
        self._session.flush()
        return True

    def delete_in_month(self, year: int, month: int) -> int:
        start = date(year, month, 1)
        ny, nm = _next_month(year, month)
        result = self._session.execute(
            sa_delete(TransactionModel)
            .where(TransactionModel.occurred_on >= start)
            .where(TransactionModel.occurred_on < date(ny, nm, 1))
        )
        # Atomic within the request transaction; deps commits on success.
        return result.rowcount or 0
