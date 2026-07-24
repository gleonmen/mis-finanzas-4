"""Use case: create a stand-alone movement (no template behind it)."""
from __future__ import annotations

from dataclasses import dataclass

from app.application.use_cases.transaction_rules import validate_and_normalize
from app.domain.entities import Frequency, Transaction, TransactionData
from app.domain.repositories import CategoryRepository, TransactionRepository


@dataclass(frozen=True)
class CreatedTransaction:
    transaction: Transaction
    # True when this movement ended up being the only one in its month, i.e. the
    # month just went from empty to non-empty and the monthly load is now blocked
    # for it. The UI warns about this.
    blocks_monthly_load: bool


class CreateTransaction:
    def __init__(
        self,
        transaction_repo: TransactionRepository,
        category_repo: CategoryRepository,
    ) -> None:
        self._transactions = transaction_repo
        self._categories = category_repo

    def execute(self, data: TransactionData) -> CreatedTransaction:
        normalized, category_code = validate_and_normalize(data, self._categories)

        created = self._transactions.create_one(
            data=normalized,
            category_code=category_code,
            # An ad-hoc movement has no template to inherit a periodicity from,
            # and the column is NOT NULL, so it is a one-off.
            frequency=Frequency.ONE_TIME,
            template_id=None,
        )

        occurred = normalized.occurred_on
        blocks = (
            self._transactions.count_in_month(occurred.year, occurred.month) == 1
        )
        return CreatedTransaction(transaction=created, blocks_monthly_load=blocks)
