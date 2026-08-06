"""Use case: confirm a monthly load — create all transactions atomically."""
from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from app.application.errors import (
    EmptyDraftError,
    InvalidDraftLineError,
    MonthAlreadyLoadedError,
)
from app.application.use_cases.transaction_rules import normalize_concept
from app.domain.entities import PaymentStatus, Transaction
from app.domain.repositories import TemplateRepository, TransactionRepository


@dataclass(frozen=True)
class DraftLine:
    """A single editable row coming from the frontend draft grid."""

    template_id: int
    amount: Decimal
    occurred_on: date


class LoadMonthFromTemplates:
    def __init__(
        self,
        template_repo: TemplateRepository,
        transaction_repo: TransactionRepository,
    ) -> None:
        self._template_repo = template_repo
        self._transaction_repo = transaction_repo

    def execute(self, year: int, month: int, lines: list[DraftLine]) -> int:
        # Presence guard, re-checked here (not only when the grid opened) so a
        # race that loaded the month in the meantime is still rejected.
        if self._transaction_repo.count_in_month(year, month) > 0:
            raise MonthAlreadyLoadedError(
                f"El mes {year}-{month:02d} ya tiene movimientos cargados."
            )

        if not lines:
            raise EmptyDraftError("No hay movimientos para cargar.")

        templates_by_id = {t.id: t for t in self._template_repo.list_all()}

        first_day = date(year, month, 1)
        last_day = date(year, month, calendar.monthrange(year, month)[1])

        transactions: list[Transaction] = []
        for line in lines:
            template = templates_by_id.get(line.template_id)
            if template is None:
                raise InvalidDraftLineError(
                    f"El template {line.template_id} no existe."
                )
            if line.amount <= 0:
                raise InvalidDraftLineError(
                    f"El monto de '{template.name}' debe ser mayor a cero."
                )
            if not (first_day <= line.occurred_on <= last_day):
                raise InvalidDraftLineError(
                    f"La fecha de '{template.name}' debe pertenecer al mes "
                    f"{year}-{month:02d}."
                )

            # Freeze a snapshot of the template fields into the transaction.
            # Loaded movements are born pending (you load what you expect to pay).
            transactions.append(
                Transaction(
                    transaction_type=template.transaction_type,
                    category_code=template.category_code,
                    name=normalize_concept(template.name),
                    is_essential=template.is_essential,
                    frequency=template.frequency,
                    amount=line.amount,
                    occurred_on=line.occurred_on,
                    payment_status=PaymentStatus.PENDING,
                    template_id=template.id,
                )
            )

        return self._transaction_repo.bulk_create(transactions)
