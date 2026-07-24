"""Composition root: session lifecycle + wiring of repositories into use cases.

This is the ONLY place that knows about concrete adapters (SQLAlchemy). Use cases
receive their dependencies through here.
"""
from __future__ import annotations

from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.application.use_cases.annual_report import AnnualReport
from app.application.use_cases.create_template import CreateTemplate
from app.application.use_cases.create_transaction import CreateTransaction
from app.application.use_cases.delete_template import DeleteTemplate
from app.application.use_cases.delete_transaction import DeleteTransaction
from app.application.use_cases.list_month_transactions import ListMonthTransactions
from app.application.use_cases.monthly_report import MonthlyReport
from app.application.use_cases.update_transaction import UpdateTransaction
from app.application.use_cases.list_categories import ListCategories
from app.application.use_cases.list_templates import ListTemplates
from app.application.use_cases.load_month_from_templates import LoadMonthFromTemplates
from app.application.use_cases.prepare_monthly_load import PrepareMonthlyLoad
from app.application.use_cases.update_template import UpdateTemplate
from app.infrastructure.db import SessionLocal
from app.infrastructure.repositories import (
    SqlAlchemyCategoryRepository,
    SqlAlchemyReportRepository,
    SqlAlchemyTemplateRepository,
    SqlAlchemyTransactionRepository,
)


def get_session() -> Generator[Session, None, None]:
    """One DB transaction per request: commit on success, rollback on error."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


SessionDep = Annotated[Session, Depends(get_session)]


def get_list_templates(session: SessionDep) -> ListTemplates:
    return ListTemplates(template_repo=SqlAlchemyTemplateRepository(session))


def get_list_categories(session: SessionDep) -> ListCategories:
    return ListCategories(category_repo=SqlAlchemyCategoryRepository(session))


def get_create_template(session: SessionDep) -> CreateTemplate:
    return CreateTemplate(
        template_repo=SqlAlchemyTemplateRepository(session),
        category_repo=SqlAlchemyCategoryRepository(session),
    )


def get_update_template(session: SessionDep) -> UpdateTemplate:
    return UpdateTemplate(
        template_repo=SqlAlchemyTemplateRepository(session),
        category_repo=SqlAlchemyCategoryRepository(session),
    )


def get_delete_template(session: SessionDep) -> DeleteTemplate:
    return DeleteTemplate(template_repo=SqlAlchemyTemplateRepository(session))


def get_monthly_report(session: SessionDep) -> MonthlyReport:
    return MonthlyReport(report_repo=SqlAlchemyReportRepository(session))


def get_annual_report(session: SessionDep) -> AnnualReport:
    return AnnualReport(report_repo=SqlAlchemyReportRepository(session))


def get_list_month_transactions(session: SessionDep) -> ListMonthTransactions:
    return ListMonthTransactions(
        transaction_repo=SqlAlchemyTransactionRepository(session),
        report_repo=SqlAlchemyReportRepository(session),
    )


def get_create_transaction(session: SessionDep) -> CreateTransaction:
    return CreateTransaction(
        transaction_repo=SqlAlchemyTransactionRepository(session),
        category_repo=SqlAlchemyCategoryRepository(session),
    )


def get_update_transaction(session: SessionDep) -> UpdateTransaction:
    return UpdateTransaction(
        transaction_repo=SqlAlchemyTransactionRepository(session),
        category_repo=SqlAlchemyCategoryRepository(session),
    )


def get_delete_transaction(session: SessionDep) -> DeleteTransaction:
    return DeleteTransaction(
        transaction_repo=SqlAlchemyTransactionRepository(session)
    )


def get_prepare_monthly_load(session: SessionDep) -> PrepareMonthlyLoad:
    return PrepareMonthlyLoad(
        template_repo=SqlAlchemyTemplateRepository(session),
        transaction_repo=SqlAlchemyTransactionRepository(session),
    )


def get_load_month_from_templates(session: SessionDep) -> LoadMonthFromTemplates:
    return LoadMonthFromTemplates(
        template_repo=SqlAlchemyTemplateRepository(session),
        transaction_repo=SqlAlchemyTransactionRepository(session),
    )


ListTemplatesDep = Annotated[ListTemplates, Depends(get_list_templates)]
ListCategoriesDep = Annotated[ListCategories, Depends(get_list_categories)]
CreateTemplateDep = Annotated[CreateTemplate, Depends(get_create_template)]
UpdateTemplateDep = Annotated[UpdateTemplate, Depends(get_update_template)]
DeleteTemplateDep = Annotated[DeleteTemplate, Depends(get_delete_template)]
MonthlyReportDep = Annotated[MonthlyReport, Depends(get_monthly_report)]
AnnualReportDep = Annotated[AnnualReport, Depends(get_annual_report)]
ListMonthTransactionsDep = Annotated[
    ListMonthTransactions, Depends(get_list_month_transactions)
]
CreateTransactionDep = Annotated[CreateTransaction, Depends(get_create_transaction)]
UpdateTransactionDep = Annotated[UpdateTransaction, Depends(get_update_transaction)]
DeleteTransactionDep = Annotated[DeleteTransaction, Depends(get_delete_transaction)]
PrepareMonthlyLoadDep = Annotated[PrepareMonthlyLoad, Depends(get_prepare_monthly_load)]
LoadMonthDep = Annotated[
    LoadMonthFromTemplates, Depends(get_load_month_from_templates)
]
