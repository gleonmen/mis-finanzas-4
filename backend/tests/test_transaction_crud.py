from datetime import date
from decimal import Decimal

import pytest

from app.application.errors import (
    TransactionNotFoundError,
    TransactionValidationError,
)
from app.application.use_cases.create_transaction import CreateTransaction
from app.application.use_cases.delete_month_transactions import (
    DeleteMonthTransactions,
)
from app.application.use_cases.delete_transaction import DeleteTransaction
from app.application.use_cases.update_transaction import UpdateTransaction
from app.domain.entities import (
    Category,
    Frequency,
    PaymentStatus,
    Transaction,
    TransactionData,
    TransactionType,
)

CATEGORIES = {
    1: Category(1, "salaries", TransactionType.INCOME),
    2: Category(2, "transport", TransactionType.EXPENSE),
    3: Category(3, "health", TransactionType.EXPENSE),
}


class FakeCategoryRepo:
    def list_all(self):
        return list(CATEGORIES.values())

    def get(self, category_id):
        return CATEGORIES.get(category_id)


class FakeTransactionRepo:
    def __init__(self):
        self.items: dict[int, Transaction] = {}
        self._next = 1

    def count_in_month(self, year, month):
        return sum(
            1
            for t in self.items.values()
            if t.occurred_on.year == year and t.occurred_on.month == month
        )

    def bulk_create(self, transactions):
        for t in transactions:
            self.create_one(t, t.category_code, t.frequency, t.template_id)
        return len(transactions)

    def list_in_month(self, year, month):
        return sorted(
            (
                t
                for t in self.items.values()
                if t.occurred_on.year == year and t.occurred_on.month == month
            ),
            key=lambda t: (t.occurred_on, t.id),
        )

    def get(self, transaction_id):
        return self.items.get(transaction_id)

    def create_one(self, data, category_code, frequency, template_id=None):
        tid = self._next
        self._next += 1
        tx = Transaction(
            id=tid,
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
        self.items[tid] = tx
        return tx

    def update(self, transaction_id, data, category_code):
        existing = self.items.get(transaction_id)
        if existing is None:
            return None
        updated = Transaction(
            id=transaction_id,
            # type / frequency / template_id are preserved by the repo
            transaction_type=existing.transaction_type,
            category_code=category_code,
            name=data.name,
            is_essential=data.is_essential,
            frequency=existing.frequency,
            amount=data.amount,
            occurred_on=data.occurred_on,
            payment_status=data.payment_status,
            template_id=existing.template_id,
        )
        self.items[transaction_id] = updated
        return updated

    def delete(self, transaction_id):
        return self.items.pop(transaction_id, None) is not None

    def delete_in_month(self, year, month):
        ids = [
            tid
            for tid, t in self.items.items()
            if t.occurred_on.year == year and t.occurred_on.month == month
        ]
        for tid in ids:
            del self.items[tid]
        return len(ids)


def expense_data(**kw):
    d = dict(
        transaction_type=TransactionType.EXPENSE,
        category_id=2,
        name="Taxi al aeropuerto",
        is_essential=False,
        amount=Decimal("60000"),
        occurred_on=date(2026, 7, 10),
    )
    d.update(kw)
    return TransactionData(**d)


def income_data(**kw):
    d = dict(
        transaction_type=TransactionType.INCOME,
        category_id=1,
        name="Bono",
        is_essential=None,
        amount=Decimal("500000"),
        occurred_on=date(2026, 7, 10),
    )
    d.update(kw)
    return TransactionData(**d)


def make():
    repo = FakeTransactionRepo()
    return repo, CreateTransaction(repo, FakeCategoryRepo())


# --- create ---------------------------------------------------------------

def test_create_expense_is_one_time_and_has_no_template():
    repo, uc = make()
    result = uc.execute(expense_data())
    tx = result.transaction
    assert tx.frequency == Frequency.ONE_TIME
    assert tx.template_id is None
    assert tx.category_code == "transport"
    assert tx.is_essential is False


def test_create_income_forces_is_essential_none():
    _, uc = make()
    tx = uc.execute(income_data(is_essential=True)).transaction
    assert tx.is_essential is None


def test_create_flags_blocking_when_month_was_empty():
    _, uc = make()
    assert uc.execute(expense_data()).blocks_monthly_load is True


def test_create_does_not_flag_when_month_already_had_movements():
    repo, uc = make()
    uc.execute(expense_data())
    second = uc.execute(expense_data(occurred_on=date(2026, 7, 20)))
    assert second.blocks_monthly_load is False


def test_create_empty_name_rejected():
    _, uc = make()
    with pytest.raises(TransactionValidationError):
        uc.execute(expense_data(name="   "))


def test_create_non_positive_amount_rejected():
    _, uc = make()
    with pytest.raises(TransactionValidationError):
        uc.execute(expense_data(amount=Decimal("0")))


def test_create_category_of_other_type_rejected():
    _, uc = make()
    with pytest.raises(TransactionValidationError):
        uc.execute(expense_data(category_id=1))  # salaries is INCOME


def test_create_unknown_category_rejected():
    _, uc = make()
    with pytest.raises(TransactionValidationError):
        uc.execute(expense_data(category_id=999))


def test_create_expense_without_is_essential_rejected():
    _, uc = make()
    with pytest.raises(TransactionValidationError):
        uc.execute(expense_data(is_essential=None))


# --- update ---------------------------------------------------------------

def test_update_changes_editable_fields():
    repo, create = make()
    create.execute(expense_data())
    uc = UpdateTransaction(repo, FakeCategoryRepo())
    updated = uc.execute(
        1,
        expense_data(
            name="Taxi centro",
            amount=Decimal("75000"),
            occurred_on=date(2026, 7, 15),
            category_id=3,
            is_essential=True,
        ),
    )
    assert updated.name == "Taxi centro"
    assert updated.amount == Decimal("75000")
    assert updated.occurred_on == date(2026, 7, 15)
    assert updated.category_code == "health"
    assert updated.is_essential is True


def test_update_ignores_attempt_to_change_type():
    """The type is fixed at creation: a payload claiming INCOME must not flip an
    EXPENSE, and the category is validated against the STORED type."""
    repo, create = make()
    create.execute(expense_data())
    uc = UpdateTransaction(repo, FakeCategoryRepo())
    # Payload says INCOME but keeps an EXPENSE category -> stays EXPENSE, valid.
    updated = uc.execute(
        1, expense_data(transaction_type=TransactionType.INCOME, category_id=2)
    )
    assert updated.transaction_type == TransactionType.EXPENSE
    assert updated.category_code == "transport"


def test_update_with_income_category_on_an_expense_is_rejected():
    repo, create = make()
    create.execute(expense_data())
    uc = UpdateTransaction(repo, FakeCategoryRepo())
    with pytest.raises(TransactionValidationError):
        uc.execute(1, expense_data(category_id=1))  # salaries is INCOME


def test_update_preserves_frequency_and_template_id():
    repo, create = make()
    create.execute(expense_data())
    repo.items[1] = Transaction(
        id=1,
        transaction_type=TransactionType.EXPENSE,
        category_code="transport",
        name="Gasolina",
        is_essential=True,
        frequency=Frequency.MONTHLY,
        amount=Decimal("250000"),
        occurred_on=date(2026, 7, 1),
        template_id=42,
    )
    uc = UpdateTransaction(repo, FakeCategoryRepo())
    updated = uc.execute(1, expense_data(is_essential=True))
    assert updated.frequency == Frequency.MONTHLY
    assert updated.template_id == 42


def test_update_missing_rejected():
    repo = FakeTransactionRepo()
    uc = UpdateTransaction(repo, FakeCategoryRepo())
    with pytest.raises(TransactionNotFoundError):
        uc.execute(99, expense_data())


# --- delete ---------------------------------------------------------------

def test_delete_ok_and_frees_the_month():
    repo, create = make()
    create.execute(expense_data())
    assert repo.count_in_month(2026, 7) == 1
    DeleteTransaction(repo).execute(1)
    # An empty month is what releases the monthly-load guard.
    assert repo.count_in_month(2026, 7) == 0


def test_delete_missing_rejected():
    repo = FakeTransactionRepo()
    with pytest.raises(TransactionNotFoundError):
        DeleteTransaction(repo).execute(1)


# --- payment status --------------------------------------------------------

def test_create_defaults_to_pending():
    _, uc = make()
    tx = uc.execute(expense_data()).transaction
    assert tx.payment_status == PaymentStatus.PENDING


def test_create_can_be_paid():
    _, uc = make()
    tx = uc.execute(expense_data(payment_status=PaymentStatus.PAID)).transaction
    assert tx.payment_status == PaymentStatus.PAID


def test_update_can_change_payment_status():
    repo, create = make()
    create.execute(expense_data())  # pending
    uc = UpdateTransaction(repo, FakeCategoryRepo())
    updated = uc.execute(1, expense_data(payment_status=PaymentStatus.PAID))
    assert updated.payment_status == PaymentStatus.PAID


# --- bulk delete of a month ------------------------------------------------

def test_delete_month_returns_count_and_empties_the_month():
    repo, create = make()
    create.execute(expense_data(occurred_on=date(2026, 7, 3)))
    create.execute(expense_data(occurred_on=date(2026, 7, 20)))
    create.execute(expense_data(occurred_on=date(2026, 8, 1)))  # other month
    deleted = DeleteMonthTransactions(repo).execute(2026, 7)
    assert deleted == 2
    assert repo.count_in_month(2026, 7) == 0
    assert repo.count_in_month(2026, 8) == 1  # untouched


def test_delete_month_empty_returns_zero():
    repo = FakeTransactionRepo()
    assert DeleteMonthTransactions(repo).execute(2026, 7) == 0
