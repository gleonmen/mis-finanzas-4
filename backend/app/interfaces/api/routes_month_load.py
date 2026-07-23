"""Monthly-load endpoints: presence status + atomic batch confirmation."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Path
from typing import Annotated

from app.application.errors import (
    EmptyDraftError,
    InvalidDraftLineError,
    MonthAlreadyLoadedError,
)
from app.application.use_cases.load_month_from_templates import DraftLine
from app.interfaces.api.deps import LoadMonthDep, PrepareMonthlyLoadDep
from app.interfaces.api.schemas import (
    MonthLoadIn,
    MonthLoadOut,
    MonthStatusOut,
    TemplateOut,
)

router = APIRouter(prefix="/months", tags=["monthly-load"])

MonthPath = Annotated[int, Path(ge=1, le=12)]
YearPath = Annotated[int, Path(ge=1970, le=9999)]


@router.get("/{year}/{month}/status", response_model=MonthStatusOut)
def month_status(
    year: YearPath, month: MonthPath, use_case: PrepareMonthlyLoadDep
) -> MonthStatusOut:
    status = use_case.execute(year=year, month=month)
    return MonthStatusOut(
        year=status.year,
        month=status.month,
        already_loaded=status.already_loaded,
        templates=[
            TemplateOut.model_validate(t, from_attributes=True)
            for t in status.templates
        ],
    )


@router.post("/{year}/{month}/load", response_model=MonthLoadOut, status_code=201)
def load_month(
    year: YearPath,
    month: MonthPath,
    payload: MonthLoadIn,
    use_case: LoadMonthDep,
) -> MonthLoadOut:
    lines = [
        DraftLine(
            template_id=line.template_id,
            amount=line.amount,
            occurred_on=line.occurred_on,
        )
        for line in payload.lines
    ]
    try:
        created = use_case.execute(year=year, month=month, lines=lines)
    except MonthAlreadyLoadedError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except EmptyDraftError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except InvalidDraftLineError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return MonthLoadOut(created=created)
