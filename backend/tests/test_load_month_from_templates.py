from datetime import date
from decimal import Decimal

import pytest

from app.application.errors import (
    EmptyDraftError,
    InvalidDraftLineError,
    MonthAlreadyLoadedError,
)
from app.application.use_cases.load_month_from_templates import (
    DraftLine,
    LoadMonthFromTemplates,
)
from app.application.use_cases.prepare_monthly_load import PrepareMonthlyLoad
from app.domain.entities import Frequency, Template, Transaction, TransactionType


def make_template(**kwargs) -> Template:
    defaults = dict(
        id=1,
        name="Netflix",
        transaction_type=TransactionType.EXPENSE,
        category_code="lifestyle",
        is_essential=False,
        default_amount=Decimal("44900"),
        frequency=Frequency.MONTHLY,
    )
    defaults.update(kwargs)
    return Template(**defaults)


class FakeTemplateRepo:
    def __init__(self, templates: list[Template]) -> None:
        self._templates = templates

    def list_all(self) -> list[Template]:
        return list(self._templates)


class FakeTransactionRepo:
    def __init__(self, existing_count: int = 0) -> None:
        self._count = existing_count
        self.created: list[Transaction] = []

    def count_in_month(self, year: int, month: int) -> int:
        return self._count

    def bulk_create(self, transactions: list[Transaction]) -> int:
        self.created.extend(transactions)
        return len(transactions)


def make_use_case(templates, existing_count=0):
    tx_repo = FakeTransactionRepo(existing_count)
    uc = LoadMonthFromTemplates(FakeTemplateRepo(templates), tx_repo)
    return uc, tx_repo


def test_happy_path_creates_transactions_with_snapshot():
    tpl_income = make_template(
        id=1, name="Sueldo", transaction_type=TransactionType.INCOME,
        category_code="salaries", is_essential=None, frequency=Frequency.MONTHLY,
    )
    tpl_expense = make_template(id=2, name="Arriendo", category_code="housing_utilities",
                                is_essential=True, frequency=Frequency.MONTHLY)
    uc, tx_repo = make_use_case([tpl_income, tpl_expense])

    created = uc.execute(2026, 7, [
        DraftLine(1, Decimal("3500000"), date(2026, 7, 5)),
        DraftLine(2, Decimal("1300000"), date(2026, 7, 1)),
    ])

    assert created == 2
    income = next(t for t in tx_repo.created if t.name == "Sueldo")
    assert income.transaction_type == TransactionType.INCOME
    assert income.category_code == "salaries"
    assert income.is_essential is None
    assert income.frequency == Frequency.MONTHLY
    assert income.template_id == 1
    expense = next(t for t in tx_repo.created if t.name == "Arriendo")
    assert expense.is_essential is True
    assert expense.category_code == "housing_utilities"


def test_month_already_loaded_is_blocked():
    uc, tx_repo = make_use_case([make_template()], existing_count=3)
    with pytest.raises(MonthAlreadyLoadedError):
        uc.execute(2026, 7, [DraftLine(1, Decimal("100"), date(2026, 7, 1))])
    assert tx_repo.created == []


def test_empty_draft_is_rejected():
    uc, _ = make_use_case([make_template()])
    with pytest.raises(EmptyDraftError):
        uc.execute(2026, 7, [])


def test_unknown_template_is_rejected():
    uc, _ = make_use_case([make_template(id=1)])
    with pytest.raises(InvalidDraftLineError):
        uc.execute(2026, 7, [DraftLine(999, Decimal("100"), date(2026, 7, 1))])


def test_date_outside_month_is_rejected():
    uc, _ = make_use_case([make_template(id=1)])
    with pytest.raises(InvalidDraftLineError):
        uc.execute(2026, 7, [DraftLine(1, Decimal("100"), date(2026, 8, 1))])


def test_last_day_of_month_is_accepted():
    uc, tx_repo = make_use_case([make_template(id=1)])
    uc.execute(2026, 2, [DraftLine(1, Decimal("100"), date(2026, 2, 28))])
    assert len(tx_repo.created) == 1


def test_non_positive_amount_is_rejected():
    uc, _ = make_use_case([make_template(id=1)])
    with pytest.raises(InvalidDraftLineError):
        uc.execute(2026, 7, [DraftLine(1, Decimal("0"), date(2026, 7, 1))])


def test_prepare_reports_already_loaded_flag():
    uc = PrepareMonthlyLoad(FakeTemplateRepo([make_template()]), FakeTransactionRepo(2))
    status = uc.execute(2026, 7)
    assert status.already_loaded is True
    assert len(status.templates) == 1
