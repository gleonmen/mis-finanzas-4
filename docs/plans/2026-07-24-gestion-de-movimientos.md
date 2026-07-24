# Gestión de movimientos — Plan de implementación

## Objetivo
Entregar la pestaña **Movimientos**: listar por mes con sus totales, crear un
movimiento suelto, editar (valor, fecha, concepto, categoría, esencial) y borrar con
confirmación. Al terminar, un mes mal cargado se puede corregir o rehacer sin tocar
la base de datos a mano.

## Contexto
Tres features ya construidos dejan casi todo el andamiaje:
- **Backend Clean Architecture**: `domain/` (entidades + puertos), `application/
  use_cases/`, `infrastructure/` (`models.py`, `repositories.py`), `interfaces/api/`
  (`schemas.py`, `deps.py` composition root, routers). `get_session` en `deps.py` ya
  da una transacción por request (commit al final, rollback ante excepción).
- **Reutilizable directo**: `SqlAlchemyCategoryRepository` (validar categoría↔tipo),
  `ReportRepository.totals(start, end)` (los totales del mes, ya implementados y
  testeados), `TransactionModel` con los enums nativos mapeados y `created_at` sin
  mapear, `month_range()` de `report_rules.py`, y el patrón de errores→HTTP
  (422/404) de `routes_templates.py`.
- **Frontend**: `Modal.tsx` genérico, `TemplateFormModal.tsx` como plantilla del
  formulario (categoría filtrada por tipo, `is_essential` solo en gasto, validación
  local espejo), `StatTiles.tsx` para los totales, `lib/api.ts` con `ApiError`,
  `lib/format.ts`, `lib/month.ts`, `i18n/es.ts`, y los estilos ya definidos
  (`.card`, `.kpi-row`, `.grid`, `.form`, `.modal`, `.row-actions`).

**No hacen falta migraciones**: la tabla `transactions` ya tiene todo, incluido
`template_id` nullable con `ON DELETE SET NULL`.

## Problema
Los movimientos hoy son de solo escritura: se crean en lote y quedan congelados, sin
endpoints para leerlos, editarlos ni borrarlos. Eso deja al usuario sin salida cuando
un mes queda mal cargado (el guard por presencia impide recargarlo) y lo obliga a
crear plantillas descartables para gastos puntuales. El enfoque elegido (CRUD REST
sobre `/transactions` + tabla con formulario modal) reutiliza los patrones ya
probados en Plantillas y mantiene la validación de negocio en `application/use_cases/`.

## Spec de referencia
`docs/specs/2026-07-24-gestion-de-movimientos.md` (aprobada, incluidos los tres
puntos que decidí y el usuario confirmó: fecha libre, totales en pantalla, y aviso
cuando el alta bloquea la carga mensual).

**Decisiones que el spec no fija y el plan resuelve** (marcadas para no resolverlas
en silencio):
1. **`frequency` de un movimiento ad-hoc**: la columna es `NOT NULL` y un movimiento
   suelto no tiene plantilla de la que heredarla → se graba **`ONE_TIME`**. Al editar
   se **preserva** el valor existente (no está entre los campos editables del spec).
2. **Cómo se detecta el aviso del guard**: en vez de adivinarlo en el frontend, el
   backend devuelve en la respuesta del alta un flag `blocks_monthly_load`, calculado
   como "este movimiento quedó siendo el único de su mes". Es exacto y cuesta un
   `count` que el repo ya sabe hacer.

## Tareas a implementar

### Backend

**1. Dominio: DTO de escritura y puertos de transacción**
- **Qué**: ampliar el puerto de transacciones con las operaciones que faltan.
- **Dónde**: `backend/app/domain/entities.py`, `backend/app/domain/repositories.py`.
- **Detalles**:
  - `TransactionData(transaction_type, category_id, name, is_essential, amount,
    occurred_on)` — usa `category_id` (lo que elige la UI); el use case resuelve el
    `category_code` para el snapshot.
  - Ampliar `TransactionRepository` con: `list_in_month(year, month) -> list[Transaction]`
    (ordenado por `occurred_on`, luego `id`), `get(id) -> Transaction | None`,
    `create_one(data, category_code, frequency, template_id=None) -> Transaction`,
    `update(id, data, category_code) -> Transaction | None`, `delete(id) -> bool`.
  - `Transaction` ya tiene `id` opcional; los métodos de lectura lo devuelven poblado.

**2. Aplicación: reglas y use cases**
- **Qué**: validación compartida y los cuatro use cases.
- **Dónde**: `backend/app/application/errors.py` (ampliar),
  `backend/app/application/use_cases/transaction_rules.py`,
  `.../{list_month_transactions,create_transaction,update_transaction,delete_transaction}.py`.
- **Detalles** (validación autoritativa acá; casos borde del spec):
  - Error nuevo: `TransactionNotFoundError`. Reusar `TemplateValidationError`? **No**:
    agregar `TransactionValidationError` para no mezclar dominios.
  - `transaction_rules.validate_and_normalize(data, category_repo) -> (TransactionData,
    category_code)`: `name` no vacío (trim); `amount > 0`; `occurred_on` presente;
    la categoría existe y su `transaction_type` **coincide** con el del movimiento;
    `is_essential` obligatorio en `EXPENSE` y **forzado a `None`** en `INCOME`.
  - `CreateTransaction`: valida, graba con `frequency=ONE_TIME` y `template_id=None`,
    y devuelve el movimiento creado **más** `blocks_monthly_load =
    (count_in_month(fecha) == 1)`.
  - `UpdateTransaction`: carga el existente (404 si no está) y **usa su
    `transaction_type` como inmutable** — valida la categoría contra ese tipo e
    ignora cualquier tipo que venga en el payload. Preserva `frequency` y
    `template_id`.
  - `DeleteTransaction`: hard delete; 404 si no existe.
  - `ListMonthTransactions`: usa `month_range()` y devuelve la lista **más los
    totales**, reutilizando `ReportRepository.totals(start, end)` (no reimplementar
    la suma).

**3. Infraestructura: adaptador SQLAlchemy**
- **Qué**: implementar los métodos nuevos.
- **Dónde**: `backend/app/infrastructure/repositories.py`.
- **Detalles**: en `SqlAlchemyTransactionRepository` agregar `list_in_month` (filtro
  por rango semiabierto sobre `occurred_on`, usa `idx_transactions_occurred_on`),
  `get`, `create_one` (insert + `flush` + devolver entidad con `id`), `update`
  (cargar, setear los campos permitidos, `flush`) y `delete`. El commit lo sigue
  manejando `get_session`; nada de commits dentro del repo.

**4. Interfaces API: schemas, router y wiring**
- **Qué**: los cuatro endpoints.
- **Dónde**: `backend/app/interfaces/api/schemas.py`, nuevo `routes_transactions.py`,
  `deps.py`, `main.py`.
- **Detalles**:
  - Schemas: `TransactionOut(id, transaction_type, category_code, name, is_essential,
    frequency, amount, occurred_on, template_id)`,
    `TransactionWriteIn(transaction_type, category_id, name, is_essential,
    amount>0, occurred_on)`, `MonthTransactionsOut(year, month, totals, items)`,
    `TransactionCreatedOut(transaction, blocks_monthly_load)`.
  - Endpoints: `GET /transactions/{year}/{month}`, `POST /transactions`,
    `PUT /transactions/{id}`, `DELETE /transactions/{id}` (204).
  - Mapeo de errores: `TransactionValidationError` → 422,
    `TransactionNotFoundError` → 404. `year`/`month` validados con `Path` como en
    `routes_month_load.py`.
  - Fábricas en `deps.py` (inyectando los repos concretos) y router en `main.py`.

**5. Tests backend**
- **Qué**: cubrir las reglas con repos falsos.
- **Dónde**: `backend/tests/test_transaction_crud.py`.
- **Detalles**: alta de gasto e ingreso OK; nombre vacío / monto ≤ 0 / categoría
  inexistente / categoría de otro tipo → error; ingreso con `is_essential` → forzado
  a `None`; gasto sin `is_essential` → error; **update no cambia el tipo aunque el
  payload lo intente**; update preserva `frequency` y `template_id`; update/delete de
  id inexistente → `TransactionNotFoundError`; alta ad-hoc graba `ONE_TIME` y
  `template_id=None`; `blocks_monthly_load` es `True` solo cuando el movimiento queda
  como único del mes.

### Frontend

**6. Cliente API y tipos**
- **Qué**: llamadas y tipos.
- **Dónde**: `frontend/src/lib/api.ts`.
- **Detalles**: `Transaction`, `TransactionWrite`, `MonthTransactions`;
  `getMonthTransactions(year, month)`, `createTransaction`, `updateTransaction`,
  `deleteTransaction`. Reusar `ApiError` para mapear 422/404 a mensajes.

**7. i18n y cuarta pestaña**
- **Qué**: textos y navegación.
- **Dónde**: `frontend/src/i18n/es.ts`, `frontend/src/App.tsx`.
- **Detalles**: `es.transactions` (título, intro, columnas, botones, labels del form,
  estado vacío, confirmación de borrado, mensajes de error/éxito, el aviso de "quedó
  registrado en otro mes" y el aviso del guard). `tabs.transactions`. Agregar el tab
  y su rama de render en `App.tsx` (ya hay tres, el patrón está).

**8. Pantalla de movimientos**
- **Qué**: filtro por mes + totales + tabla.
- **Dónde**: `frontend/src/pages/Transactions.tsx`.
- **Detalles**: selector de mes (patrón de `Reports.tsx`), **`StatTiles` reutilizado**
  para ingresos/gastos/neto, y tabla con tipo (pill), categoría (dot + nombre),
  concepto, esencial, valor (COP) y fecha, ordenada por fecha; botones Editar/Borrar
  por fila; botón "Nuevo movimiento". Estado vacío del mes. Refrescar lista y totales
  tras cada alta/edición/borrado.

**9. Formulario modal crear/editar**
- **Qué**: el formulario reutilizado para alta y edición.
- **Dónde**: `frontend/src/components/TransactionFormModal.tsx`.
- **Detalles** (calcado de `TemplateFormModal`, con las diferencias del spec):
  - Campos: tipo, categoría (filtrada por tipo), concepto, `es esencial` (solo si
    `EXPENSE`), valor (COP con `parseAmount`/`formatThousands`) y **fecha**
    (`input type="date"`, **sin `min`/`max`** — la fecha es libre).
  - **En edición el tipo se muestra deshabilitado** (inmutable). Al crear, cambiar el
    tipo limpia la categoría seleccionada y muestra/oculta `es esencial`.
  - Validación local espejo (concepto, monto > 0, fecha, categoría, esencial en
    gasto) → deshabilita Guardar. Manejo de `ApiError` (422/404).

**10. Borrado con confirmación y avisos**
- **Qué**: confirmación y los dos avisos del spec.
- **Dónde**: `frontend/src/pages/Transactions.tsx`.
- **Detalles**: diálogo "¿Seguro que querés borrar este movimiento?" (patrón del
  borrado de plantillas) → borra, refresca, feedback. Tras un alta: si la fecha cae
  **fuera del mes filtrado**, avisar que quedó registrado en ese otro mes; si la
  respuesta trae `blocks_monthly_load`, avisar que la carga mensual de ese mes queda
  bloqueada.

### Cierre

**11. Verificación punta a punta**
- **Qué**: comprobar contra spec y plan.
- **Dónde**: `docker compose up -d --build`; tests backend y build/typecheck en Docker.
- **Detalles**: skill `verify-after-changes`, 5 casos: (1) editar el monto de un
  movimiento y ver que los totales del mes y el reporte se actualizan; (2) borrar
  todos los movimientos de un mes y comprobar que **la carga mensual se destraba**;
  (3) alta ad-hoc en un mes vacío → aparece, y avisa que bloquea la carga mensual;
  (4) validaciones del form (concepto vacío, monto 0, gasto sin esencial) y **tipo
  deshabilitado en edición**; (5) alta con fecha de otro mes → se acepta y se avisa.

## Casos borde y manejo de errores (del spec, a no perder)
- Concepto vacío / monto ≤ 0 / fecha vacía / categoría sin elegir → no guarda, mensaje.
- Gasto sin `es esencial` → no guarda; ingreso con esencial → forzado a `None`.
- Categoría que no corresponde al tipo → UI lo evita (filtro) + backend 422.
- **Tipo inmutable al editar**: la UI lo deshabilita y el backend lo ignora.
- Fecha fuera del mes filtrado → se acepta y se avisa dónde quedó.
- Editar/borrar un movimiento inexistente → 404, se informa y se refresca la lista.
- Fallo de red/servidor → sin cambio parcial; los totales no se actualizan hasta el éxito.
- Alta en mes vacío → se avisa que bloquea la carga mensual de ese mes.
- Borrar un movimiento cuya plantilla fue borrada → funciona (no depende de ella).
