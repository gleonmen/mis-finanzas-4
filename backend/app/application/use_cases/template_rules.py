"""Shared business-rule validation for creating/updating a template."""
from __future__ import annotations

from app.application.errors import TemplateValidationError
from app.domain.entities import TemplateData, TransactionType
from app.domain.repositories import CategoryRepository


def validate_and_normalize(
    data: TemplateData, category_repo: CategoryRepository
) -> TemplateData:
    """Validate a template write payload and return a normalized copy.

    Rules:
      - name required (trimmed, non-empty)
      - default_amount > 0
      - category exists and its transaction_type matches the template's type
      - is_essential: required for EXPENSE; forced to None for INCOME
    """
    name = data.name.strip()
    if not name:
        raise TemplateValidationError("El nombre es obligatorio.")

    if data.default_amount <= 0:
        raise TemplateValidationError("El valor por defecto debe ser mayor a cero.")

    category = category_repo.get(data.category_id)
    if category is None:
        raise TemplateValidationError("La categoría seleccionada no existe.")
    if category.transaction_type != data.transaction_type:
        raise TemplateValidationError(
            "La categoría no corresponde al tipo de movimiento."
        )

    if data.transaction_type == TransactionType.EXPENSE:
        if data.is_essential is None:
            raise TemplateValidationError(
                "Indicá si el gasto es esencial."
            )
        is_essential = data.is_essential
    else:  # INCOME: is_essential does not apply
        is_essential = None

    return TemplateData(
        transaction_type=data.transaction_type,
        category_id=data.category_id,
        name=name,
        is_essential=is_essential,
        default_amount=data.default_amount,
        frequency=data.frequency,
    )
