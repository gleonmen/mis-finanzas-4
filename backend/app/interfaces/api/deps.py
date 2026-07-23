"""Composition root: session lifecycle + wiring of repositories into use cases.

This is the ONLY place that knows about concrete adapters (SQLAlchemy). Use cases
receive their dependencies through here.
"""
from __future__ import annotations

from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.application.use_cases.create_template import CreateTemplate
from app.application.use_cases.delete_template import DeleteTemplate
from app.application.use_cases.list_categories import ListCategories
from app.application.use_cases.list_templates import ListTemplates
from app.application.use_cases.load_month_from_templates import LoadMonthFromTemplates
from app.application.use_cases.prepare_monthly_load import PrepareMonthlyLoad
from app.application.use_cases.update_template import UpdateTemplate
from app.infrastructure.db import SessionLocal
from app.infrastructure.repositories import (
    SqlAlchemyCategoryRepository,
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
PrepareMonthlyLoadDep = Annotated[PrepareMonthlyLoad, Depends(get_prepare_monthly_load)]
LoadMonthDep = Annotated[
    LoadMonthFromTemplates, Depends(get_load_month_from_templates)
]
