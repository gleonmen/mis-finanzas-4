"""Composition root: session lifecycle + wiring of repositories into use cases.

This is the ONLY place that knows about concrete adapters (SQLAlchemy). Use cases
receive their dependencies through here.
"""
from __future__ import annotations

from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.application.use_cases.list_templates import ListTemplates
from app.application.use_cases.load_month_from_templates import LoadMonthFromTemplates
from app.application.use_cases.prepare_monthly_load import PrepareMonthlyLoad
from app.infrastructure.db import SessionLocal
from app.infrastructure.repositories import (
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
PrepareMonthlyLoadDep = Annotated[PrepareMonthlyLoad, Depends(get_prepare_monthly_load)]
LoadMonthDep = Annotated[
    LoadMonthFromTemplates, Depends(get_load_month_from_templates)
]
