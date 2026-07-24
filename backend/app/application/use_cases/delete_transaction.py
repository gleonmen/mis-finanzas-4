"""Use case: delete a movement (hard delete)."""
from __future__ import annotations

from app.application.errors import TransactionNotFoundError
from app.domain.repositories import TransactionRepository


class DeleteTransaction:
    def __init__(self, transaction_repo: TransactionRepository) -> None:
        self._transactions = transaction_repo

    def execute(self, transaction_id: int) -> None:
        # Hard delete. Emptying a month also releases the monthly-load guard, which
        # is how a badly loaded month gets redone.
        if not self._transactions.delete(transaction_id):
            raise TransactionNotFoundError(
                f"El movimiento {transaction_id} no existe."
            )
