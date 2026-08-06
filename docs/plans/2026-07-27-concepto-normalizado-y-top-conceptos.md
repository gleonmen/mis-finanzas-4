# Concepto normalizado y top-5 conceptos — Plan de implementación

## Objetivo
Que el concepto de un movimiento se guarde normalizado (trim + espacios colapsados +
title-case) en todos los caminos que crean un movimiento, y agregar a Reportes
(mensual y anual) un bloque "Top conceptos de gasto" con los 5 conceptos de mayor
gasto del período (concepto, categoría, monto, % del gasto total).

## Contexto
Todo encaja en lo existente:
- **Backend**: `transaction_rules.validate_and_normalize` ya hace `name.strip()` — ahí
  entra el normalizador. `LoadMonthFromTemplates` arma cada `Transaction` con
  `template.name` — ahí se normaliza también. `SqlAlchemyReportRepository` ya tiene el
  patrón de agregaciones (`_by_category` con `GROUP BY` + `order_by(...).desc()`);
  `top_expense_concepts` es una más. `MonthlyReport`/`AnnualReport` arman su paquete;
  `routes_reports` mapea a schemas con helpers.
- **Frontend**: `components/CategoryBars.tsx` es la referencia del patrón barra+tabla
  (Recharts `BarChart` horizontal, `Cell` con `categoryColor`, `chartInk`,
  `formatCompact`/`formatCurrency`, tabla `report-table`). `Reports.tsx` monta los
  bloques; `report` es la unión Monthly|Annual y ambos tendrán `top_expense_concepts`,
  así que el bloque va en la parte común (sale en las dos vistas). `i18n/es.ts` sección
  `es.reports`. `categoryNames` para el nombre de categoría, `categoryColor` (Impuestos
  gris) para el color.
- **Sin migración**: `name` ya existe; la normalización es a nivel app.

## Problema
El concepto es texto libre y hoy se guarda crudo, lo que se ve desprolijo e impide
agrupar variantes. Normalizarlo al guardar (una regla de negocio, en la capa
`application`) resuelve ambas cosas y habilita el reporte por concepto. El top-5 es una
agregación `GROUP BY name, category_code` — misma familia que las que ya existen — y el
render reusa el patrón de barra+tabla validado, en un componente propio porque rotula
por concepto y suma una columna de categoría (no encaja en `CategoryBars`).

## Spec de referencia
`docs/specs/2026-07-27-concepto-normalizado-y-top-conceptos.md` (aprobada; title-case
con el costo de acrónimos, y concepto+categoría como unidad de agrupación).

## Tareas a implementar

### Backend

**1. Normalizador de concepto + aplicarlo**
- **Qué**: helper `normalize_concept` y su uso en los caminos que crean/editan un
  movimiento.
- **Dónde**: `backend/app/application/use_cases/transaction_rules.py` (definir y usar),
  `backend/app/application/use_cases/load_month_from_templates.py` (usar).
- **Detalles**:
  - `normalize_concept(name: str) -> str`: `" ".join(w.capitalize() for w in
    name.split())`. `str.split()` sin args recorta y colapsa cualquier espacio; el
    resultado es title-case. Cadena solo-espacios → `""`.
  - En `validate_and_normalize`: reemplazar `name = data.name.strip()` por
    `name = normalize_concept(data.name)`; la validación "no vacío" (que hoy usa el
    strip) sigue aplicando sobre el resultado — si queda `""`, `TransactionValidationError`.
  - En `LoadMonthFromTemplates`: al construir cada `Transaction`, usar
    `name=normalize_concept(template.name)` en vez de `template.name`.
  - Caso borde: concepto obligatorio y no vacío tras normalizar (del spec).

**2. Dominio: entidad y puerto**
- **Qué**: `ConceptAmount` y el método de agregación.
- **Dónde**: `backend/app/domain/entities.py`, `backend/app/domain/repositories.py`.
- **Detalles**:
  - `ConceptAmount(name: str, category_code: str, amount: Decimal)` (frozen).
  - `ReportRepository.top_expense_concepts(start, end, limit: int = 5) ->
    list[ConceptAmount]`.

**3. Infraestructura: agregación SQL**
- **Qué**: implementar `top_expense_concepts`.
- **Dónde**: `backend/app/infrastructure/repositories.py` (`SqlAlchemyReportRepository`).
- **Detalles**: `select(name, category_code, func.sum(amount).label("total"))` con
  `where(in_range)` + `transaction_type == EXPENSE`, `group_by(name, category_code)`,
  `order_by(total.desc())`, `.limit(limit)`. Mapear a `ConceptAmount` con `_dec`.

**4. Use cases: sumar top_expense_concepts a los dos paquetes**
- **Qué**: incluir el top-5 en el resultado mensual y anual.
- **Dónde**: `backend/app/application/use_cases/monthly_report.py`,
  `.../annual_report.py`.
- **Detalles**: campo `top_expense_concepts: list[ConceptAmount]` en
  `MonthlyReportResult` y `AnnualReportResult`, poblado con
  `report_repo.top_expense_concepts(start, end)`. (El mismo método sirve a ambos por el
  rango.)

**5. API: schemas + routers**
- **Qué**: exponer el nuevo campo.
- **Dónde**: `backend/app/interfaces/api/schemas.py`, `.../routes_reports.py`.
- **Detalles**: `ConceptAmountOut(name, category_code, amount)`; agregar
  `top_expense_concepts: list[ConceptAmountOut]` a `MonthlyReportOut` y
  `AnnualReportOut`. Helper `_concepts(...)` en `routes_reports` y mapearlo en ambos
  endpoints. Sin endpoints nuevos.

**6. Tests backend**
- **Qué**: normalización + agregación.
- **Dónde**: `backend/tests/test_transaction_crud.py` (normalización en create),
  `backend/tests/test_reports.py` (top conceptos; extender `FakeReportRepo`).
- **Detalles**: create con `"  netflix  hbo "` → `"Netflix Hbo"`; nombre solo-espacios
  → `TransactionValidationError`; `top_expense_concepts` ordena desc, limita a 5, agrupa
  por (name, category_code) (mismo nombre en dos categorías = dos filas), suma correcta;
  período sin gastos → lista vacía. (La normalización en load se cubre en verify.)

### Frontend

**7. Cliente API: tipos**
- **Dónde**: `frontend/src/lib/api.ts`.
- **Detalles**: `ConceptAmount { name: string; category_code: string; amount: string }`;
  agregar `top_expense_concepts: ConceptAmount[]` a `MonthlyReport` y `AnnualReport`.

**8. Componente TopConcepts + i18n**
- **Qué**: el bloque barra+tabla del top-5.
- **Dónde**: `frontend/src/components/TopConcepts.tsx` (nuevo), `frontend/src/i18n/es.ts`.
- **Detalles**:
  - Props: `concepts: ConceptAmount[]`, `totalExpense: number`.
  - Barra horizontal (Recharts `BarChart` layout vertical, como `CategoryBars`),
    `dataKey` = monto, eje Y = **nombre del concepto**, cada `Cell` con
    `categoryColor(category_code)` (Impuestos gris). Alto según cantidad de filas.
  - Tabla `report-table`: columnas **Concepto**, **Categoría** (`categoryNames[code] ??
    code`), **Monto** (`formatCurrency`), **%** (`round(amount/totalExpense*100)`, 0 si
    `totalExpense<=0`).
  - Estado vacío (`concepts.length === 0`): card con el título y un texto "sin gastos".
  - i18n `es.reports`: `topConceptsTitle` ("Top conceptos de gasto"), `topConceptsEmpty`,
    `colConcept` ("Concepto"), y reusar `tableCategory`/`tableAmount`/`tableShare`.

**9. Montar en Reports**
- **Qué**: mostrar el bloque en mensual y anual.
- **Dónde**: `frontend/src/pages/Reports.tsx`.
- **Detalles**: en el bloque común (no gateado por vista, dentro del `!isEmpty`),
  `<TopConcepts concepts={report.top_expense_concepts} totalExpense={Number(report.totals.expense)} />`.
  Ubicarlo junto al resto (p. ej. después del gasto por categoría).

### Cierre

**10. Verificación punta a punta**
- **Dónde**: `docker compose up -d --build`; tests backend y build/typecheck en Docker.
- **Detalles**: skill `verify-after-changes`, casos: (1) crear un movimiento
  `"  netflix  hbo "` → se guarda/lista como `"Netflix Hbo"`; (2) cargar un mes → los
  conceptos quedan normalizados; (3) Reportes mensual: bloque top-5 ordenado desc, con
  categoría y % correctos; el monto de un concepto = suma real de sus movimientos;
  (4) anual muestra el mismo bloque sobre el año; (5) período sin gastos → estado vacío
  del bloque. Además: barras coloreadas por la categoría del conceto (Impuestos gris),
  y confirmar que los otros reportes/movimientos siguen intactos.

## Casos borde y manejo de errores (del spec, a no perder)
- Concepto vacío tras normalizar → rechazo (obligatorio).
- Menos de 5 conceptos → se muestran los que haya.
- Mismo concepto en dos categorías → dos filas.
- % sobre gasto total; los 5 no necesariamente suman 100%.
- Período sin gastos → estado vacío.
- Históricos con variantes → no se fusionan hasta re-guardarse (sin migración).
- Acrónimos → title-case (Soat, Iva), costo aceptado.
