# Reportes gráficos por caja — Plan de implementación

## Objetivo
Entregar la pestaña **Reportes** con vista mensual y anual: totales (ingresos, gastos,
neto), gasto por categoría, reparto esencial/no esencial y evolución mes a mes del año.
Las agregaciones se calculan en el backend (un endpoint por vista) y el frontend solo
pinta con Recharts, siguiendo las formas y la paleta validadas con el skill dataviz.

## Contexto
Dos features ya construidos definen los patrones a reutilizar:
- **Backend Clean Architecture**: `domain/` (entidades + puertos en `repositories.py`),
  `application/use_cases/`, `infrastructure/` (`models.py` con enums nativos vía
  `SAEnum(create_type=False)`, `repositories.py` adaptadores), `interfaces/api/`
  (`schemas.py`, `deps.py` composition root, routers). El commit por request lo maneja
  `get_session` en `deps.py`.
- **Datos**: `transactions` guarda el snapshot (`transaction_type`, `category_code`,
  `name`, `is_essential`, `frequency`, `amount`, `occurred_on`) con índice
  `idx_transactions_occurred_on` — justo lo que necesitan los `GROUP BY` por período.
  **No hacen falta migraciones nuevas.**
- **Frontend**: `App.tsx` con tabs en estado local, `lib/api.ts` (fetch + `ApiError`),
  `lib/format.ts` (COP es-CO), `lib/month.ts`, `i18n/es.ts` (`categoryNames`,
  `transactionTypeNames`), `lib/colors.ts`, y `pages/` + `components/` como referencia
  de estilo. `styles.css` centraliza el look.

**Decisiones de visualización ya tomadas y validadas** (skill dataviz, ver § Tarea 6):
la paleta placeholder actual **falla** el validador (dos azules con ΔE 7.2 en visión
normal, un par en 2.8 bajo protanopía, 5 colores bajo el piso de croma), así que se
reemplaza por la paleta de referencia validada, que da **ALL CHECKS PASS** sobre la
superficie real de la app (`#ffffff`).

## Problema
Los movimientos están cargados pero no responden preguntas. Técnicamente hay que
agregar por período y por dimensión (categoría, tipo, esencialidad) y mostrarlo.
El enfoque elegido (un endpoint por vista, agregando en SQL) mantiene el cálculo
financiero en `application/use_cases/` como manda `CLAUDE.md`, evita transferir todas
las transacciones al navegador y evita la cascada de requests de un endpoint por
gráfica. Recharts se suma como dependencia porque construir ejes, escalas y tooltips
a mano para 4 formas distintas es trabajo bespoke y propenso a errores.

## Spec de referencia
`docs/specs/2026-07-23-reportes-graficos-por-caja.md` (aprobada, con las dos
sugerencias aceptadas: **top 7 + "Otros"** y **el ahorro cuenta como salida**).

**Discrepancias con el spec, marcadas explícitamente** (surgen de aplicar el skill
dataviz; no cambian *qué* se responde, solo *con qué forma*):
1. El spec dice "gráfica de **ingresos vs gastos**". Se implementa como **KPI row de
   stat tiles** (ingresos, gastos, neto), no como gráfica de barras: son tres números
   cabecera, y "un puñado de números cabecera → stat tiles, no un grouped bar" es un
   anti-patrón explícito del skill. Responde la misma pregunta, mejor.
2. El spec dice "gráfica de **esencial vs no esencial**". Se implementa como **meter**
   (un riel con la porción esencial), no como dona/pie: "un pie de 2 gajos" es
   anti-patrón; "una sola razón contra un total → meter" es la forma documentada.
3. El spec pide "evolución mes a mes con ingresos, gastos y neto". Se separa en **dos
   gráficas de un solo eje**: una línea de 2 series (ingresos, gastos) y una barra
   divergente para el neto. Meterlos juntos empujaría a un dual-axis (el anti-patrón
   #1 del skill) o a una lectura confusa del cruce por cero.

## Tareas a implementar

### Backend

**1. Dominio: puerto de reportes**
- **Qué**: contratos para las agregaciones que necesitan las dos vistas.
- **Dónde**: `backend/app/domain/entities.py`, `backend/app/domain/repositories.py`.
- **Detalles**:
  - Entidades de resultado (dataclasses frozen): `PeriodTotals(income, expense, net)`,
    `CategoryAmount(category_code, amount)`, `EssentialSplit(essential, non_essential)`,
    `MonthPoint(month, income, expense, net)`.
  - `ReportRepository(ABC)` con, todos acotados por rango de fechas `[desde, hasta)`:
    - `totals(start, end) -> PeriodTotals`
    - `expense_by_category(start, end) -> list[CategoryAmount]` (desc por monto)
    - `essential_split(start, end) -> EssentialSplit`
    - `monthly_series(year) -> list[MonthPoint]` (solo para la vista anual)
  - Trabajar con `Decimal` de punta a punta (nunca float) — es dinero.

**2. Aplicación: use cases de reporte**
- **Qué**: `MonthlyReport` y `AnnualReport`, que arman el paquete de cada vista.
- **Dónde**: `backend/app/application/use_cases/{monthly_report,annual_report}.py`.
- **Detalles** (aquí vive la regla de negocio):
  - **Regla de caja**: el rango se calcula por `occurred_on` (mes: día 1 al día 1 del
    mes siguiente; año: 1-ene al 1-ene siguiente). `frequency` **no se usa jamás** en
    ningún cálculo — es solo metadato.
  - **Top 7 + "Otros"**: el use case ordena las categorías desc y colapsa de la 8ª en
    adelante en un ítem `OTHER` con la suma. Devuelve **ambas cosas**: la lista
    completa (para la tabla) y la lista recortada (para la gráfica), para que el front
    no tenga que decidir nada.
  - **Serie anual**: siempre **12 puntos**, rellenando con cero los meses sin datos
    (caso borde del spec: la tendencia no debe saltear meses).
  - `net = income - expense`. Puede ser negativo y se devuelve tal cual (caso borde
    del spec: no se oculta ni se lleva a cero).
  - Período sin movimientos → totales en cero y listas vacías; **no** es un error (el
    front decide mostrar el estado vacío).
  - Validar `month` 1-12 y un rango razonable de año.

**3. Infraestructura: adaptador SQL**
- **Qué**: `SqlAlchemyReportRepository` con los `GROUP BY`.
- **Dónde**: `backend/app/infrastructure/repositories.py`.
- **Detalles**:
  - `totals`: `SUM(amount) FILTER (WHERE transaction_type=...)` por tipo, en una query.
  - `expense_by_category`: `GROUP BY category_code` filtrando `EXPENSE`, orden desc.
  - `essential_split`: `SUM(amount)` agrupado por `is_essential` sobre `EXPENSE`.
  - `monthly_series`: agrupar por mes (`date_trunc`/`EXTRACT(MONTH)`) y tipo dentro del
    año; el relleno de meses faltantes lo hace el use case (tarea 2), no el SQL.
  - Todas filtran por el rango de `occurred_on` (usa `idx_transactions_occurred_on`).
  - `SUM` sobre conjunto vacío devuelve `NULL` → normalizar a `Decimal("0")`.

**4. Interfaces API: schemas, router y wiring**
- **Qué**: los dos endpoints de vista.
- **Dónde**: `backend/app/interfaces/api/schemas.py`, nuevo `routes_reports.py`,
  `deps.py`, `main.py`.
- **Detalles**:
  - `GET /reports/monthly/{year}/{month}` y `GET /reports/annual/{year}`.
  - Schemas: `TotalsOut(income, expense, net)`, `CategoryAmountOut(category_code,
    amount)`, `EssentialSplitOut(essential, non_essential)`, `MonthPointOut(month,
    income, expense, net)`, y los envoltorios `MonthlyReportOut` (totals, by_category,
    by_category_chart, essential) y `AnnualReportOut` (lo mismo + `monthly_series`).
  - Validar `month` con `Path(ge=1, le=12)` y `year` con rango, igual que
    `routes_month_load.py`. Registrar el router en `main.py` y las fábricas en `deps.py`.

**5. Tests backend**
- **Qué**: cubrir las reglas de cálculo con repos falsos y/o datos controlados.
- **Dónde**: `backend/tests/test_reports.py`.
- **Detalles**: `net` negativo se preserva; top 7 + "Otros" colapsa bien y **la suma de
  la lista recortada = la suma de la completa**; la serie anual trae 12 puntos con
  ceros; un gasto `ANNUAL` cae completo en su mes (no se prorratea); período vacío da
  ceros; el total anual = suma de los 12 mensuales (invariante #12 del spec).

### Frontend

**6. Paleta validada (reemplaza el placeholder)**
- **Qué**: sustituir `colors.ts` por la paleta de referencia validada.
- **Dónde**: `frontend/src/lib/colors.ts`.
- **Detalles**:
  - **Por qué**: la paleta actual FALLA el validador — `#6A8EAD`↔`#4E79A7` ΔE 7.2 en
    visión normal (piso 15), `#B07AA1`↔`#6A8EAD` ΔE 2.8 en protanopía (objetivo 8), y
    5 colores bajo el piso de croma. Evidencia en el output del validador.
  - **Qué queda**: los 8 slots validados en orden fijo — blue `#2a78d6`, orange
    `#eb6834`, aqua `#1baf7a`, yellow `#eda100`, magenta `#e87ba4`, green `#008300`,
    violet `#4a3aa7`, red `#e34948`. Resultado sobre `#ffffff`: **ALL CHECKS PASS**
    (peor par adyacente CVD ΔE 9.1; visión normal 19.6).
  - **Dos escalas separadas**: ingreso (6 categorías → slots 1-6) y egreso (8 → slots
    1-8). Nunca aparecen en la misma gráfica, así que no se superan los 8 hues (la
    regla dura: jamás generar un 9º hue).
  - `"Otros"` usa el **gris muted** (`#898781`), no un hue categórico.
  - El color sigue al `code`, en orden fijo — **nunca** se reasigna por ranking.
  - Guardar también los steps dark documentados (para cuando exista modo oscuro) y las
    tintas de chrome (grid `#e1e0d9`, ejes `#c3c2b7`, muted `#898781`).
  - **Relief obligatorio**: el validador marca WARN de contraste (<3:1) en aqua, yellow
    y magenta → toda gráfica que los use debe llevar etiquetas visibles y tabla-twin
    (ya previsto en las tareas 9-11).

**7. Dependencia Recharts + cliente API + i18n**
- **Qué**: instalar Recharts y preparar datos/textos.
- **Dónde**: `frontend/package.json`, `frontend/src/lib/api.ts`, `frontend/src/i18n/es.ts`.
- **Detalles**: agregar `recharts`; tipos `MonthlyReport`/`AnnualReport` y funciones
  `getMonthlyReport(year, month)` / `getAnnualReport(year)` reusando `ApiError`.
  Sección `es.reports` con títulos, ejes, leyendas, estado vacío, errores y el label
  `"Otros"`. Nombres de mes en español vía `formatMonthYear`/`Intl`.

**8. Tab Reportes + selector de período**
- **Qué**: la pantalla contenedora y su filtro.
- **Dónde**: `frontend/src/App.tsx` (agregar tab), `frontend/src/pages/Reports.tsx`.
- **Detalles**: tercer tab "Reportes". **Una sola fila de filtros arriba de todo** —
  nunca filtros dentro de cada card (anti-patrón): toggle Mensual/Anual + selector de
  mes/año. Por defecto: mensual del mes actual. Al cambiar el período **todas** las
  gráficas se re-renderizan contra la misma porción de datos. En refetch, mantener el
  render previo con opacidad reducida (**sin** flash de skeleton).

**9. KPI row de totales**
- **Qué**: ingresos, gastos y neto como stat tiles.
- **Dónde**: `frontend/src/components/StatTiles.tsx`.
- **Detalles**: tres tiles con valor en COP. **No** es una gráfica de barras
  (discrepancia 1 del spec). El neto lleva signo explícito y se distingue con el token
  de estado (`#006300` positivo / `#d03b3b` negativo) **acompañado de icono/label** —
  nunca color solo. Figuras proporcionales en los valores grandes (nada de
  `tabular-nums` en números display), tipografía del sistema.

**10. Gasto por categoría (barra horizontal) + tabla**
- **Qué**: la composición del gasto del período.
- **Dónde**: `frontend/src/components/CategoryBars.tsx`.
- **Detalles**: **barra horizontal** ordenada de mayor a menor (horizontal por los
  nombres largos en español), top 7 + "Otros"; **no** dona (anti-patrón para comparar
  valores cercanos y con >6 gajos). Color fijo por `category_code`; nombre de categoría
  como etiqueta del eje (así la identidad nunca depende del color). Extremos
  redondeados 4px anclados a la línea base, gap de 2px entre barras, grid hairline
  **sólido** (nunca punteado), sin número en cada barra: valor al final de la barra solo
  si entra con padding, si no va al tooltip. Tooltip por marca con hit area ≥24px.
  **Tabla acompañante** con TODAS las categorías, monto y % sobre el gasto del período
  (fuente de verdad; `tabular-nums` acá sí).

**11. Esencial vs no esencial (meter)**
- **Qué**: qué parte del gasto fue esencial.
- **Dónde**: `frontend/src/components/EssentialMeter.tsx`.
- **Detalles**: **meter** de un solo riel con la porción esencial rellena y el % + ambos
  montos etiquetados; **no** dona de 2 gajos (discrepancia 2). Gap de 2px entre
  segmentos. Si el período no tiene gastos, se indica en vez de dibujar un riel vacío.

**12. Evolución anual: línea + neto divergente**
- **Qué**: las dos gráficas de la vista anual.
- **Dónde**: `frontend/src/components/AnnualTrend.tsx`.
- **Detalles** (discrepancia 3):
  - **Línea de 2 series** (ingresos, gastos), 12 meses siempre, líneas de 2px,
    marcadores ≥8px, **leyenda presente** (≥2 series) + direct-label del extremo,
    **crosshair + tooltip** al hacer hover.
  - **Barra divergente del neto** por mes, con midpoint gris en cero: positivo en blue
    `#2a78d6`, negativo en red `#e34948` (el par divergente documentado). Se evita a
    propósito verde/rojo, que es la trampa clásica de daltonismo.
  - **Un solo eje** en ambas (todo en COP). Nunca dual-axis.
  - Tabla-twin con los 12 meses (ingresos, gastos, neto).

**13. Estados vacío y de error**
- **Qué**: cubrir los casos borde del spec.
- **Dónde**: `Reports.tsx` y componentes de gráfica.
- **Detalles**: período sin movimientos → estado vacío claro (no gráficas rotas); solo
  ingresos o solo gastos → la gráfica sin datos lo dice en vez de dibujarse vacía;
  fallo de red → mensaje + reintentar, sin mostrar datos parciales.

### Cierre

**14. Verificación punta a punta**
- **Qué**: comprobar contra spec y plan.
- **Dónde**: `docker compose up -d --build`; tests backend y build/typecheck frontend
  en Docker.
- **Detalles**: skill `verify-after-changes`, 5 casos: (1) mensual con datos (totales,
  categorías, meter); (2) **invariante de caja**: un gasto anual cae completo en su mes
  y el total anual = suma de los 12 meses; (3) anual con evolución de 12 meses incluidos
  los vacíos; (4) período sin movimientos → estado vacío; (5) neto negativo se muestra
  correctamente. Además: **abrir y mirar** las gráficas (el validador chequea color, no
  layout) buscando colisiones de etiquetas, recortes y overflow.

## Casos borde y manejo de errores (del spec, a no perder)
- Período sin movimientos → estado vacío, no gráficas rotas.
- Solo ingresos o solo gastos → se informa, no se dibuja vacío.
- Neto negativo → explícito y distinguible (color + icono/label, nunca color solo).
- Categoría sin gastos → no se lista (no aparecen ceros).
- Más categorías que las que muestra la gráfica → "Otros" + tabla completa como respaldo.
- Movimientos cuya plantilla fue borrada → entran normalmente (usan su snapshot).
- Fallo de red → mensaje + reintentar, sin datos parciales.
- Redondeo: los % se redondean, los **montos** son reales; la tabla es la fuente de verdad.
- `frequency` nunca participa de un cálculo; los montos no se prorratean.
