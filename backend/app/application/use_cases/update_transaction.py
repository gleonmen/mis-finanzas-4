"""Use case: edit an existing movement."""
from __future__ import annotations

from app.application.errors import TransactionNotFoundError
from app.application.use_cases.transaction_rules import validate_and_normalize
from app.domain.entities import Transaction, TransactionData
from app.domain.repositories import CategoryRepository, TransactionRepository


class UpdateTransaction:
    def __init__(
        self,
        transaction_repo: TransactionRepository,
        category_repo: CategoryRepository,
    ) -> None:
        self._transactions = transaction_repo
        self._categories = category_repo

    def execute(self, transaction_id: int, data: TransactionData) -> Transaction:
        existing = self._transactions.get(transaction_id)
        if existing is None:
            raise TransactionNotFoundError(
                f"El movimiento {transaction_id} no existe."
            )

        # The type is fixed at creation. Whatever the payload carries is ignored,
        # and the category is validated against the STORED type.
        normalized, category_code = validate_and_normalize(
            data, self._categories, forced_type=existing.transaction_type
        )

        updated = self._transactions.update(transaction_id, normalized, category_code)
        if updated is None:  # deleted between the read and the write
            raise TransactionNotFoundError(
                f"El movimiento {transaction_id} no existe."
            )
        return updated
