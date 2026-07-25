# Ingresos por categoría — Plan de implementación

## Objetivo
Agregar a Reportes (vista mensual y anual) un gráfico de **ingresos por categoría**:
una barra horizontal ordenada de mayor a menor con su tabla de detalle, que responde
"de dónde viene la mayoría de mis ingresos". Backend agrega la agregación; frontend
reutiliza el componente del desglose de gastos.

## Contexto
El feature de reportes ya dejó casi todo:
- **Backend**: `ReportRepository.expense_by_category(start, end)` hace exactamente el
  `GROUP BY category_code` filtrando por tipo y ordenando desc; `income_by_category`
  es su espejo con `INCOME`. Los use cases `MonthlyReport`/`AnnualReport` arman el
  paquete por vista; los schemas `MonthlyReportOut`/`AnnualReportOut` lo exponen.
- **Frontend**: `components/CategoryBars.tsx` ya dibuja barra horizontal + tabla twin
  (con top-7 + "Otros"), y `Reports.tsx` lo monta con `by_category_chart`/`by_category`.
  `lib/colors.ts` tiene `incomeColors` y `categoryColor(code)` resuelve el color de
  cualquier categoría (ingreso o gasto) por su `code`. `i18n/es.ts` tiene la sección
  `es.reports`.
- **Paleta**: las 6 categorías de ingreso pasan el validador en modo **adyacente**
  (barras), que ya se corrió en el feature de reportes (ALL CHECKS PASS, peor par
  normal ΔE 19.6). El modo pie (todos-contra-todos) **no** pasaba — por eso se
  descartó la dona; la barra no tiene ese problema.

**Sin migraciones.** Ingreso tiene 6 categorías, así que **no se pliega en "Otros"**
(el `collapse_to_top(limit=7)` devolvería las 6 sin tocar; para la barra de ingresos
se pasa la lista completa como `chartData` y `fullData`).

## Problema
Los ingresos hoy solo se ven como total. Técnicamente falta una agregación
`SUM(amount) GROUP BY category_code` filtrando `INCOME`, y exponerla en los dos
paquetes de reporte. En el frontend, el componente de barra + tabla ya existe y está
validado; solo hay que generalizarlo para que sirva a ingresos (título, etiquetas y
estado vacío parametrizables) y montarlo una segunda vez. El color ya es estable por
`code`, así que la escala de ingreso aplica sola.

## Spec de referencia
`docs/specs/2026-07-25-ingresos-por-categoria.md` (aprobada; incluye la nota de la
decisión de cambiar dona → barra tras re-validar la paleta).

## Tareas a implementar

### Backend

**1. Dominio + agregación de ingresos por categoría**
- **Qué**: método `income_by_category` en el puerto y su adaptador.
- **Dónde**: `backend/app/domain/repositories.py` (puerto `ReportRepository`),
  `backend/app/infrastructure/repositories.py` (`SqlAlchemyReportRepository`).
- **Detalles**: firma `income_by_category(start, end) -> list[CategoryAmount]`,
  gemela de `expense_by_category` pero filtrando `transaction_type == INCOME`,
  `GROUP BY category_code`, orden por monto desc. Reutiliza el mismo patrón (`func.sum`,
  `_dec`, rango semiabierto sobre `occurred_on`). No agrega entidades nuevas
  (`CategoryAmount` ya existe).

**2. Use cases: sumar income_by_category a los paquetes**
- **Qué**: incluir el desglose de ingresos en el resultado de las dos vistas.
- **Dónde**: `backend/app/application/use_cases/monthly_report.py`,
  `.../annual_report.py`.
- **Detalles**: agregar el campo `income_by_category: list[CategoryAmount]` a
  `MonthlyReportResult` y `AnnualReportResult`, poblado con
  `report_repo.income_by_category(start, end)`. **No** se colapsa a top-N (6 ≤ 7; y
  el spec pide sin "Otros"). Nada más cambia en la lógica de caja.

**3. API: exponer income_by_category en los schemas y routers**
- **Qué**: agregar el campo a las respuestas.
- **Dónde**: `backend/app/interfaces/api/schemas.py`,
  `.../routes_reports.py`.
- **Detalles**: agregar `income_by_category: list[CategoryAmountOut]` a
  `MonthlyReportOut` y `AnnualReportOut`; mapearlo en `routes_reports.py` reutilizando
  el helper `_categories(...)`. Sin endpoints nuevos.

**4. Tests backend**
- **Qué**: cubrir la nueva agregación.
- **Dónde**: `backend/tests/test_reports.py` (ampliar).
- **Detalles**: con datos de varias categorías de ingreso en un mes, `income_by_category`
  devuelve las categorías con monto > 0, ordenadas desc, y **su suma == totals.income**
  (invariante); una categoría de ingreso sin movimientos no aparece; período sin
  ingresos → lista vacía. Extender el `FakeReportRepo` con el método.

### Frontend

**5. Cliente API: tipos**
- **Qué**: reflejar el campo nuevo.
- **Dónde**: `frontend/src/lib/api.ts`.
- **Detalles**: agregar `income_by_category: CategoryAmount[]` a las interfaces
  `MonthlyReport` y `AnnualReport`. (El tipo `CategoryAmount` ya existe.)

**6. Generalizar CategoryBars para ingreso o gasto**
- **Qué**: parametrizar título, etiqueta de porcentaje y estado vacío.
- **Dónde**: `frontend/src/components/CategoryBars.tsx`, `frontend/src/i18n/es.ts`.
- **Detalles**: agregar props `title`, `shareLabel`, `emptyText` (con **defaults** =
  los textos actuales de gasto, para no tocar la llamada existente). Agregar a
  `es.reports` las claves `byIncomeTitle` ("Ingreso por categoría"), `tableShareIncome`
  ("% del ingreso") y `byIncomeEmpty` ("No hay ingresos en este período."). El color
  ya sale de `categoryColor(code)` sin cambios (resuelve la escala de ingreso por el
  `code`). El `radius`/gap/grid/tooltip/tabla se reutilizan tal cual.

**7. Montar el gráfico de ingresos en Reports**
- **Qué**: instanciar `CategoryBars` para ingresos en ambas vistas.
- **Dónde**: `frontend/src/pages/Reports.tsx`.
- **Detalles**: donde hoy se monta el desglose de gastos, agregar una segunda
  instancia de `CategoryBars` alimentada con `report.income_by_category` (como
  `chartData` **y** `fullData`, sin colapso), pasando `title=byIncomeTitle`,
  `shareLabel=tableShareIncome`, `emptyText=byIncomeEmpty`. Aparece en mensual y
  anual (el bloque es común a las dos). Ubicación: junto al resto de gráficos del
  período; el de gastos queda igual.

### Cierre

**8. Verificación punta a punta**
- **Qué**: comprobar contra spec y plan.
- **Dónde**: `docker compose up -d --build`; tests backend y build/typecheck en Docker.
- **Detalles**: skill `verify-after-changes`, 5 casos: (1) mensual con varias fuentes
  de ingreso → barra ordenada desc, la mayor arriba, tabla con % que suman 100%;
  (2) **invariante**: la suma de la tabla de ingresos == KPI de ingresos del período;
  (3) anual → mismo gráfico sobre el año; (4) período sin ingresos → estado vacío del
  gráfico, sin romper el resto; (5) una sola fuente → una barra al 100%. Además:
  **mirar** que no haya colisión de etiquetas ni overflow, y confirmar que el desglose
  de **gastos** sigue intacto (no se rompió al generalizar el componente).

## Casos borde y manejo de errores (del spec, a no perder)
- Período sin ingresos → estado vacío del gráfico (los demás gráficos siguen).
- Categoría de ingreso sin movimientos → no aparece (ni barra ni fila).
- Una sola fuente → una barra al 100%.
- Montos parecidos → se distinguen por nombre (etiqueta del eje) + valor en la tabla.
- Redondeo: los % se redondean, los montos son reales; la tabla es la fuente de verdad.
- Fallo de carga → el manejo de error de la vista de Reportes ya lo cubre.
- El total de la tabla de ingresos coincide con el KPI de ingresos (invariante de caja).
