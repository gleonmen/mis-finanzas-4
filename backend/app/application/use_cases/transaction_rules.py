"""Shared business-rule validation for creating/updating a movement."""
from __future__ import annotations

from app.application.errors import TransactionValidationError
from app.domain.entities import TransactionData, TransactionType
from app.domain.repositories import CategoryRepository


def validate_and_normalize(
    data: TransactionData,
    category_repo: CategoryRepository,
    forced_type: TransactionType | None = None,
) -> tuple[TransactionData, str]:
    """Validate a movement payload; return the normalized copy + category_code.

    Rules:
      - name required (trimmed, non-empty)
      - amount > 0
      - occurred_on required (the date itself is free: it need not fall in any
        particular month)
      - category exists and its transaction_type matches the movement's type
      - is_essential: required for EXPENSE, forced to None for INCOME

    `forced_type` is passed on update: the type is fixed at creation, so whatever
    the payload carries is ignored and the stored type wins.
    """
    tx_type = forced_type if forced_type is not None else data.transaction_type

    name = data.name.strip()
    if not name:
        raise TransactionValidationError("El concepto es obligatorio.")

    if data.amount <= 0:
        raise TransactionValidationError("El valor debe ser mayor a cero.")

    if data.occurred_on is None:
        raise TransactionValidationError("La fecha es obligatoria.")

    category = category_repo.get(data.category_id)
    if category is None:
        raise TransactionValidationError("La categoría seleccionada no existe.")
    if category.transaction_type != tx_type:
        raise TransactionValidationError(
            "La categoría no corresponde al tipo de movimiento."
        )

    if tx_type == TransactionType.EXPENSE:
        if data.is_essential is None:
            raise TransactionValidationError("Indicá si el gasto es esencial.")
        is_essential = data.is_essential
    else:  # INCOME: is_essential does not apply
        is_essential = None

    normalized = TransactionData(
        transaction_type=tx_type,
        category_id=data.category_id,
        name=name,
        is_essential=is_essential,
        amount=data.amount,
        occurred_on=data.occurred_on,
        payment_status=data.payment_status,
    )
    return normalized, category.code
