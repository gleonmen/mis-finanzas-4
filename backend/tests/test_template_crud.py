from decimal import Decimal

import pytest

from app.application.errors import TemplateNotFoundError, TemplateValidationError
from app.application.use_cases.create_template import CreateTemplate
from app.application.use_cases.delete_template import DeleteTemplate
from app.application.use_cases.update_template import UpdateTemplate
from app.domain.entities import (
    Category,
    Frequency,
    Template,
    TemplateData,
    TransactionType,
)

CATEGORIES = {
    1: Category(1, "salaries", TransactionType.INCOME),
    2: Category(2, "transport", TransactionType.EXPENSE),
}


class FakeCategoryRepo:
    def list_all(self):
        return list(CATEGORIES.values())

    def get(self, category_id):
        return CATEGORIES.get(category_id)


class FakeTemplateRepo:
    def __init__(self):
        self.items: dict[int, Template] = {}
        self._next = 1

    def _entity(self, template_id, data: TemplateData) -> Template:
        return Template(
            id=template_id,
            name=data.name,
            transaction_type=data.transaction_type,
            category_code=CATEGORIES[data.category_id].code,
            is_essential=data.is_essential,
            default_amount=data.default_amount,
            frequency=data.frequency,
        )

    def list_all(self):
        return list(self.items.values())

    def get(self, template_id):
        return self.items.get(template_id)

    def create(self, data):
        tid = self._next
        self._next += 1
        tpl = self._entity(tid, data)
        self.items[tid] = tpl
        return tpl

    def update(self, template_id, data):
        if template_id not in self.items:
            return None
        tpl = self._entity(template_id, data)
        self.items[template_id] = tpl
        return tpl

    def delete(self, template_id):
        return self.items.pop(template_id, None) is not None


def expense_data(**kw):
    d = dict(
        transaction_type=TransactionType.EXPENSE,
        category_id=2,
        name="Gasolina",
        is_essential=True,
        default_amount=Decimal("250000"),
        frequency=Frequency.MONTHLY,
    )
    d.update(kw)
    return TemplateData(**d)


def income_data(**kw):
    d = dict(
        transaction_type=TransactionType.INCOME,
        category_id=1,
        name="Sueldo",
        is_essential=None,
        default_amount=Decimal("3500000"),
        frequency=Frequency.MONTHLY,
    )
    d.update(kw)
    return TemplateData(**d)


def make_create():
    repo = FakeTemplateRepo()
    return CreateTemplate(repo, FakeCategoryRepo()), repo


# --- create ---------------------------------------------------------------

def test_create_expense_ok():
    uc, repo = make_create()
    tpl = uc.execute(expense_data())
    assert tpl.id == 1
    assert tpl.is_essential is True
    assert tpl.category_code == "transport"
    assert repo.items[1].name == "Gasolina"


def test_create_income_forces_is_essential_none():
    uc, _ = make_create()
    tpl = uc.execute(income_data(is_essential=True))  # should be ignored
    assert tpl.is_essential is None


def test_create_empty_name_rejected():
    uc, _ = make_create()
    with pytest.raises(TemplateValidationError):
        uc.execute(expense_data(name="   "))


def test_create_non_positive_amount_rejected():
    uc, _ = make_create()
    with pytest.raises(TemplateValidationError):
        uc.execute(expense_data(default_amount=Decimal("0")))


def test_create_category_wrong_type_rejected():
    uc, _ = make_create()
    # EXPENSE template pointing at an INCOME category (id 1).
    with pytest.raises(TemplateValidationError):
        uc.execute(expense_data(category_id=1))


def test_create_unknown_category_rejected():
    uc, _ = make_create()
    with pytest.raises(TemplateValidationError):
        uc.execute(expense_data(category_id=999))


def test_create_expense_without_is_essential_rejected():
    uc, _ = make_create()
    with pytest.raises(TemplateValidationError):
        uc.execute(expense_data(is_essential=None))


# --- update ---------------------------------------------------------------

def test_update_ok():
    repo = FakeTemplateRepo()
    CreateTemplate(repo, FakeCategoryRepo()).execute(expense_data())
    uc = UpdateTemplate(repo, FakeCategoryRepo())
    updated = uc.execute(1, expense_data(name="Gasolina moto", default_amount=Decimal("300000")))
    assert updated.name == "Gasolina moto"
    assert updated.default_amount == Decimal("300000")


def test_update_missing_rejected():
    repo = FakeTemplateRepo()
    uc = UpdateTemplate(repo, FakeCategoryRepo())
    with pytest.raises(TemplateNotFoundError):
        uc.execute(42, expense_data())


# --- delete ---------------------------------------------------------------

def test_delete_ok():
    repo = FakeTemplateRepo()
    CreateTemplate(repo, FakeCategoryRepo()).execute(expense_data())
    DeleteTemplate(repo).execute(1)
    assert repo.items == {}


def test_delete_missing_rejected():
    repo = FakeTemplateRepo()
    with pytest.raises(TemplateNotFoundError):
        DeleteTemplate(repo).execute(1)
