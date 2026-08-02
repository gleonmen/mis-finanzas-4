# Estado de pago y borrado masivo — Plan de implementación

## Objetivo
Agregar un estado de pago (pagado/pendiente) a cada movimiento, un borrado masivo de
todos los movimientos de un mes, y dos medidores de pago (gastos e ingresos) en la
vista mensual de Reportes. Al terminar: se marca lo pagado/pendiente, se vacía un mes
de un clic, y se ve cuánto falta pagar y cobrar.

## Contexto
- Backend Clean Architecture ya montado: `domain/` (entidades + puertos),
  `application/use_cases/`, `infrastructure/` (`models.py`, `repositories.py`),
  `interfaces/api/` (`schemas.py`, `deps.py`, routers). Enums nativos vía
  `SAEnum(create_type=False)` (patrón `_TRANSACTION_TYPE`/`_FREQUENCY`). `get_session`
  da una transacción por request. Las migraciones **solo corren en el primer init**
  del volumen (→ hay que aplicar 0005 a mano a la BD viva, como con `0004`).
- `transactions` ya tiene CRUD (`SqlAlchemyTransactionRepository`: list_in_month, get,
  create_one, update, delete, count_in_month, bulk_create) y el flujo de carga mensual
  (`LoadMonthFromTemplates`) + reportes (`SqlAlchemyReportRepository` con
  `totals/expense_by_category/essential_split/monthly_series`, ya usa `SUM ... FILTER`).
- Frontend: `pages/Movements.tsx` (lista + form modal + borrado individual con `Modal`
  danger), `components/TransactionFormModal.tsx`, `components/EssentialMeter.tsx`
  (meter de 2 partes, ya con props `title/emptyText`), `pages/Reports.tsx` (vista
  mensual con StatTiles + CategoryBars + EssentialMeter), `lib/api.ts`, `i18n/es.ts`,
  `lib/month.ts`.
- **Reglas que se mantienen:** el `payment_status` NO es snapshot (es estado propio,
  mutable); los totales/reportes por categoría suman **todos** los movimientos sin
  importar el estado; el guard por presencia sigue igual (borrar todos libera el mes).

## Problema
Falta un campo de estado por movimiento y dos operaciones nuevas (borrado masivo,
agregación por estado). El estado es una columna normal (no toca el snapshot). Todo lo
demás encaja en los patrones existentes: un enum nativo más, un método de repo de
borrado por rango, una agregación `SUM ... FILTER` por estado, y en el frontend reuso
del meter y del patrón de confirmación de borrado.

## Spec de referencia
`docs/specs/2026-07-26-estado-de-pago-y-borrado-masivo.md` (aprobada; medidores solo
en mensual; un movimiento pendiente igual suma a los totales).

## Tareas a implementar

### Backend

**1. Migración 0005 (enum + columna + backfill)**
- **Dónde**: `supabase/migrations/0005_add_payment_status.sql`.
- **Detalles** (idempotente, sirve para init fresco y para aplicar a mano):
  - `DO $$ BEGIN CREATE TYPE payment_status AS ENUM ('PAID','PENDING'); EXCEPTION WHEN
    duplicate_object THEN null; END $$;`
  - `ALTER TABLE transactions ADD COLUMN IF NOT EXISTS payment_status payment_status
    NOT NULL DEFAULT 'PAID';` → las filas existentes quedan **PAID** (backfill gratis).
  - `ALTER TABLE transactions ALTER COLUMN payment_status SET DEFAULT 'PENDING';` →
    los nuevos nacen **PENDING**. (La app igual lo setea explícito.)

**2. Dominio: enum, campos y puertos**
- **Dónde**: `backend/app/domain/entities.py`, `backend/app/domain/repositories.py`.
- **Detalles**:
  - `class PaymentStatus(str, Enum): PAID; PENDING`.
  - `Transaction` y `TransactionData` agregan `payment_status: PaymentStatus`
    (en `Transaction`, default `PENDING`).
  - `PaymentSplit(paid: Decimal, pending: Decimal)` (frozen).
  - `TransactionRepository` +`delete_in_month(year, month) -> int`.
  - `ReportRepository` +`payment_split(start, end, tx_type) -> PaymentSplit`.

**3. Aplicación: use cases**
- **Dónde**: `backend/app/application/use_cases/` (`transaction_rules.py`,
  `create_transaction.py`, `update_transaction.py`, `load_month_from_templates.py`,
  nuevo `delete_month_transactions.py`, `monthly_report.py`).
- **Detalles**:
  - `transaction_rules.validate_and_normalize`: propagar `payment_status` al
    `TransactionData` normalizado (sin regla cruzada; el valor es un enum válido).
  - `LoadMonthFromTemplates`: cada `Transaction` que arma lleva
    `payment_status=PENDING` (los cargados nacen pendientes).
  - `CreateTransaction`/`UpdateTransaction`: pasan el `payment_status` del payload
    (create ad-hoc: default PENDING vía schema; update: editable).
  - `DeleteMonthTransactions(year, month) -> int`: valida el período (`month_range`)
    y llama `transaction_repo.delete_in_month`; devuelve el conteo borrado.
  - `MonthlyReport`: agrega `expense_payment` e `income_payment` (PaymentSplit) al
    resultado, poblados con `report_repo.payment_split(start, end, EXPENSE|INCOME)`.
    **AnnualReport no cambia** (medidores solo mensual).

**4. Infraestructura: modelo y repos**
- **Dónde**: `backend/app/infrastructure/models.py`, `.../repositories.py`.
- **Detalles**:
  - `TransactionModel` +`payment_status` mapeada con un `SAEnum(PaymentStatus,
    name="payment_status", create_type=False, values_callable=…)` (patrón existente).
  - `create_one`/`bulk_create`/`update` setean `payment_status` **siempre** (nunca
    NULL; igual que se hizo con los otros enums).
  - `SqlAlchemyTransactionRepository.delete_in_month`: `DELETE` por rango semiabierto
    de `occurred_on` (usa `idx_transactions_occurred_on`); retornar el rowcount.
    Corre dentro de la transacción del request (atómico) — commit lo hace `deps`.
  - `SqlAlchemyReportRepository.payment_split`: `SUM(amount) FILTER (WHERE
    payment_status='PAID')` y `... 'PENDING'`, filtrando por tipo y rango; NULL→0.

**5. API: schemas, routers, wiring**
- **Dónde**: `backend/app/interfaces/api/schemas.py`, `routes_transactions.py`,
  `routes_reports.py`, `deps.py`, `main.py` (no hace falta), .
- **Detalles**:
  - `TransactionWriteIn` +`payment_status: PaymentStatus = PaymentStatus.PENDING`
    (default en el schema → alta ad-hoc sin elegir queda PENDING).
  - `TransactionOut` +`payment_status`.
  - `PaymentSplitOut(paid, pending)`; `MonthlyReportOut` +`expense_payment`,
    `income_payment`.
  - `DELETE /transactions/{year}/{month}` → `{ "deleted": n }` (200). Reusa
    `MonthPath/YearPath`. Mapear período inválido → 422.
  - Fábrica del use case `DeleteMonthTransactions` en `deps.py`.
  - Los endpoints de transaction ya existentes pasan el `payment_status` al use case
    (via `_to_data`).

**6. Aplicar 0005 a la BD viva**
- **Dónde**: comando puntual `docker exec -i … psql … < …0005….sql`.
- **Detalles**: verificar que la columna existe, filas viejas en PAID, default PENDING.

**7. Tests backend**
- **Dónde**: `backend/tests/` (ampliar `test_transaction_crud.py`,
  `test_reports.py`; use case de borrado masivo).
- **Detalles**: create ad-hoc default PENDING; update cambia estado; load mensual →
  PENDING en todos; `DeleteMonthTransactions` retorna el conteo y vacía el mes;
  `payment_split` suma bien por estado y tipo y **paid+pending == total del tipo**
  (invariante). Extender los fakes con `delete_in_month`/`payment_split`/`payment_status`.

### Frontend

**8. Cliente API y tipos**
- **Dónde**: `frontend/src/lib/api.ts`.
- **Detalles**: `PaymentStatus = "PAID" | "PENDING"`; agregar `payment_status` a
  `Transaction` y `TransactionWrite`; `PaymentSplit { paid: string; pending: string }`
  y sumarlo (`expense_payment`, `income_payment`) a `MonthlyReport`; función
  `deleteMonthTransactions(year, month) -> {deleted:number}`.

**9. EssentialMeter: rótulos parametrizables**
- **Dónde**: `frontend/src/components/EssentialMeter.tsx`.
- **Detalles**: props opcionales `leftLabel`/`rightLabel` (default =
  `es.reports.essential`/`nonEssential`). El `split` sigue siendo `{essential,
  non_essential}` → para pago se pasa `{essential: paid, non_essential: pending}` con
  los rótulos "Pagado"/"Pendiente de pago" (o "Recibido"/"Pendiente de cobro").
  Reportes de esencial no pasa props → intacto.

**10. i18n**
- **Dónde**: `frontend/src/i18n/es.ts`.
- **Detalles**: `paymentStatusNames` por tipo:
  `EXPENSE: { PAID:"Pagado", PENDING:"Pendiente de pago" }`,
  `INCOME: { PAID:"Recibido", PENDING:"Pendiente de cobro" }`. Strings del form
  (label "Estado"), de la lista (columna "Estado"), del botón/confirmación de borrado
  masivo, y títulos de los medidores de pago en Reportes.

**11. Form de movimiento: campo estado**
- **Dónde**: `frontend/src/components/TransactionFormModal.tsx`.
- **Detalles**: control de estado (dos opciones) con rótulos según el `type` actual
  (gasto/ingreso); default `PENDING` al crear; precargado al editar; se envía en el
  payload. Al cambiar el tipo, los rótulos del estado cambian (el valor PAID/PENDING
  se mantiene).

**12. Movimientos: columna estado + borrar todos**
- **Dónde**: `frontend/src/pages/Movements.tsx`.
- **Detalles**:
  - Nueva **columna Estado** en la tabla, con el rótulo por tipo.
  - Botón **"Borrar todos"** visible solo si el mes tiene movimientos; abre un `Modal`
    danger de confirmación que dice cuántos se borran (`items.length`). Confirmar →
    `deleteMonthTransactions`, refrescar lista+totales, feedback. Reusa el patrón del
    borrado individual (mismo `Modal`, botón `danger`).

**13. Reportes: dos medidores de pago (mensual)**
- **Dónde**: `frontend/src/pages/Reports.tsx`.
- **Detalles**: solo en la rama `view === "monthly"` (o cuando el reporte es mensual),
  agregar dos `EssentialMeter`:
  - gastos: `split={{essential: expense_payment.paid, non_essential:
    expense_payment.pending}}`, `title` "Pagos: gastos", `leftLabel` "Pagado",
    `rightLabel` "Pendiente de pago".
  - ingresos: `split={{essential: income_payment.paid, non_essential:
    income_payment.pending}}`, `title` "Cobros: ingresos", `leftLabel` "Recibido",
    `rightLabel` "Pendiente de cobro".
  - Cada meter con su estado vacío (sin gastos / sin ingresos). La vista **anual** no
    los muestra.

### Cierre

**14. Verificación punta a punta**
- **Dónde**: `docker compose up -d --build`; tests backend y build/typecheck en Docker.
- **Detalles**: skill `verify-after-changes`, casos: (1) crear un gasto ad-hoc → nace
  Pendiente de pago; editarlo a Pagado y ver el cambio en la lista; (2) cargar un mes
  desde plantillas → todos Pendientes; (3) **borrar todos** de un mes: confirmación con
  conteo correcto, lista queda vacía, y la **carga mensual se destraba** (409 → 201);
  (4) Reportes mensual: dos medidores; pagado+pendiente de cada uno == total de KPI del
  tipo (invariante); (5) un mes con solo gastos → el medidor de ingresos dice "sin
  datos". Además: rótulos correctos por tipo (gasto vs ingreso), la vista anual **no**
  muestra los medidores, y el snapshot/otros reportes por categoría no cambian.

## Casos borde y manejo de errores (del spec, a no perder)
- BD existente → backfill PAID; nuevos PENDING (migración).
- Alta/edición sin tocar estado → PENDING (default del schema).
- Borrar todos en mes vacío → botón oculto; no hay operación.
- Borrado masivo atómico → todo o nada; error informado, mes intacto.
- Confirmación explícita con conteo; sin deshacer.
- Reporte con solo un tipo → el medidor del ausente dice "sin datos".
- Estado no altera snapshot ni totales/reportes por categoría (suman todo).
- Medidor todo pagado / todo pendiente → un lado 100% / otro 0%.
- Guard por presencia intacto → borrar todos libera el mes para recargar.
