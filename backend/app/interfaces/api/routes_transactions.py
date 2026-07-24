"""Movement endpoints: list a month, create ad-hoc, edit, delete."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Response

from app.application.errors import (
    InvalidPeriodError,
    TransactionNotFoundError,
    TransactionValidationError,
)
from app.domain.entities import TransactionData
from app.interfaces.api.deps import (
    CreateTransactionDep,
    DeleteTransactionDep,
    ListMonthTransactionsDep,
    UpdateTransactionDep,
)
from app.interfaces.api.schemas import (
    MonthTransactionsOut,
    TotalsOut,
    TransactionCreatedOut,
    TransactionOut,
    TransactionWriteIn,
)

router = APIRouter(prefix="/transactions", tags=["transactions"])

MonthPath = Annotated[int, Path(ge=1, le=12)]
YearPath = Annotated[int, Path(ge=1970, le=9999)]


def _to_data(payload: TransactionWriteIn) -> TransactionData:
    return TransactionData(
        transaction_type=payload.transaction_type,
        category_id=payload.category_id,
        name=payload.name,
        is_essential=payload.is_essential,
        amount=payload.amount,
        occurred_on=payload.occurred_on,
    )


def _out(tx) -> TransactionOut:
    return TransactionOut.model_validate(tx, from_attributes=True)


@router.get("/{year}/{month}", response_model=MonthTransactionsOut)
def list_month(
    year: YearPath, month: MonthPath, use_case: ListMonthTransactionsDep
) -> MonthTransactionsOut:
    try:
        result = use_case.execute(year=year, month=month)
    except InvalidPeriodError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return MonthTransactionsOut(
        year=result.year,
        month=result.month,
        totals=TotalsOut(
            income=result.totals.income,
            expense=result.totals.expense,
            net=result.totals.net,
        ),
        items=[_out(t) for t in result.items],
    )


@router.post("", response_model=TransactionCreatedOut, status_code=201)
def create_transaction(
    payload: TransactionWriteIn, use_case: CreateTransactionDep
) -> TransactionCreatedOut:
    try:
        created = use_case.execute(_to_data(payload))
    except TransactionValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return TransactionCreatedOut(
        transaction=_out(created.transaction),
        blocks_monthly_load=created.blocks_monthly_load,
    )


@router.put("/{transaction_id}", response_model=TransactionOut)
def update_transaction(
    transaction_id: int, payload: TransactionWriteIn, use_case: UpdateTransactionDep
) -> TransactionOut:
    try:
        updated = use_case.execute(transaction_id, _to_data(payload))
    except TransactionNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except TransactionValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return _out(updated)


@router.delete("/{transaction_id}", status_code=204)
def delete_transaction(
    transaction_id: int, use_case: DeleteTransactionDep
) -> Response:
    try:
        use_case.execute(transaction_id)
    except TransactionNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return Response(status_code=204)
