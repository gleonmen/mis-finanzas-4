# Totales en plantillas — Plan de implementación

## Objetivo
En la pantalla Plantillas, mostrar un **subtotal equivalente-mensual por categoría**
al cerrar cada grupo, y un **resumen por sección** (Egresos: esencial/no esencial/
total por mes; Ingresos: total por mes). Cálculo puro en el frontend sobre la lista
ya cargada; sin backend.

## Contexto
El feature previo dejó la base:
- `frontend/src/pages/Templates.tsx` ya renderiza dos secciones (Ingresos/Egresos) con
  un helper local `renderSection(title, rows, emptyText)` y una tabla por sección.
- `frontend/src/lib/templateSort.ts` ya expone `categoryRank(categories)` y
  `groupByType(templates, rank) -> { income, expense }` con el orden fijo
  (categoría → esencial → valor desc). Las filas de cada sección ya vienen **ordenadas
  y contiguas por categoría**, así que detectar el "fin de grupo" es comparar el
  `category_code` con el de la fila siguiente.
- `Template` (de `lib/api.ts`) trae `default_amount` (string), `frequency` (string:
  `MONTHLY|BIMONTHLY|QUARTERLY|SEMIANNUAL|ANNUAL|ONE_TIME`), `is_essential`,
  `category_code`, `transaction_type`.
- `frontend/src/lib/format.ts` tiene `formatCurrency` (COP). `i18n/es.ts` tiene
  `es.templates` y `frequencyNames`. `styles.css` tiene los estilos de la grilla y de
  secciones (`.template-section`).

**Sin backend, sin migraciones.** Todo se calcula sobre `templates` ya en memoria.

## Problema
Falta sumar las plantillas de forma significativa. Sumar `default_amount` crudo
mezclaría periodicidades; por eso se normaliza a **equivalente mensual** (ver mapa) y
se rotula como tal. La lógica de normalización y de armado de "grupos con subtotal +
resumen" es pura y testeable, así que va en `lib/`; `Templates.tsx` solo pinta. Es un
cálculo de **planeación** sobre valores por defecto, distinto de los reportes por caja
de movimientos reales (por eso normalizar acá es correcto y no rompe esa convención).

## Spec de referencia
`docs/specs/2026-07-26-totales-en-plantillas.md` (aprobada; la pregunta abierta quedó
resuelta: categoría solo-Únicos muestra subtotal $0).

## Tareas a implementar

**1. Helper de normalización y agregación (puro)**
- **Qué**: funciones para el equivalente mensual, los grupos con subtotal y el resumen
  de sección.
- **Dónde**: `frontend/src/lib/templateTotals.ts` (nuevo).
- **Detalles**:
  - `MONTHLY_DIVISOR: Record<string, number>` = `{ MONTHLY:1, BIMONTHLY:2, QUARTERLY:3,
    SEMIANNUAL:6, ANNUAL:12 }`. `ONE_TIME` **no** está en el mapa → se excluye.
  - `monthlyEquivalent(tpl): number` → `Number(default_amount) / divisor`, o **0** si
    la frecuencia es `ONE_TIME` o desconocida-sin-divisor. (Resguardo del spec:
    una frecuencia desconocida que no sea ONE_TIME se trata como mensual ÷1 para no
    perder el monto; ONE_TIME sí se excluye. Implementar: si `freq === "ONE_TIME"` → 0;
    si `freq in MONTHLY_DIVISOR` → `/divisor`; si no → `/1`.)
  - `groupWithSubtotals(rows): { categoryCode; templates: Template[]; subtotalMonthly:
    number }[]` — recorre la lista **ya ordenada** y corta por `category_code`,
    acumulando el subtotal (suma de `monthlyEquivalent`). Mantiene el orden de entrada.
  - `sectionSummary(rows): { essentialMonthly, nonEssentialMonthly, totalMonthly }` —
    para Egresos; suma equivalentes mensuales partiendo por `is_essential`. Para
    Ingresos, con las mismas sumas, `totalMonthly` es lo único que se usa.
  - Trabajar en `number` (equivalente mensual con decimales); el redondeo es solo al
    formatear (tarea 3). Los totales se derivan de los mismos equivalentes, así que
    "suma de subtotales == total de sección" se cumple por construcción.

**2. i18n: rótulos de totales**
- **Qué**: textos nuevos.
- **Dónde**: `frontend/src/i18n/es.ts` (`es.templates`).
- **Detalles**: `subtotalLabel` (p. ej. "Subtotal /mes"), `perMonthSuffix` ("/mes"),
  `summaryEssential` ("Esencial /mes"), `summaryNonEssential` ("No esencial /mes"),
  `summaryTotal` ("Total /mes"), y una aclaración corta reutilizable
  `monthlyEquivNote` ("Equivalente mensual — los montos anuales, etc. se prorratean a
  mensual; los Únicos no se cuentan."). El sufijo/label deja explícito que es mensual.

**3. Render: subtotales por categoría + resumen de sección**
- **Qué**: mostrar las filas de subtotal y el resumen en cada sección.
- **Dónde**: `frontend/src/pages/Templates.tsx`, `frontend/src/styles.css`.
- **Detalles**:
  - En `renderSection`, en vez de mapear filas planas, usar `groupWithSubtotals(rows)`:
    por cada grupo, renderizar sus filas de plantilla (igual que hoy) y **una fila de
    subtotal** al cierre — fila destacada, **sin** botones de acción, con el nombre de
    la categoría y `formatCurrency(round(subtotalMonthly))` + rótulo "/mes".
  - Agregar el **resumen de sección**: para Egresos, una tira/encabezado compacto con
    esencial /mes, no esencial /mes y total /mes (usando `sectionSummary`); para
    Ingresos, solo total /mes. Ubicarlo arriba de la tabla (bajo el `<h2>`), con una
    nota chica `monthlyEquivNote`.
  - `renderSection` necesita saber si la sección es de egresos (para mostrar el corte
    esencial) o de ingresos (solo total). Pasar un parámetro `kind: "income" |
    "expense"` o el summary ya calculado.
  - Estilos: clase `.subtotal-row` (fondo tenue, negrita, sin hover de acción) y
    `.section-summary` (fila de stats compacta). Reusar tokens ya definidos.
  - Las filas de subtotal usan una `key` estable distinta de las de plantilla (p. ej.
    `subtotal-<categoryCode>`), para no colisionar con las `key` de `tpl.id`.
  - El estado vacío de sección no muestra resumen ni subtotales (no hay filas).

**4. Verificación punta a punta**
- **Qué**: comprobar contra spec y plan.
- **Dónde**: `docker compose up -d --build`; build/typecheck del frontend en Docker.
- **Detalles**: skill `verify-after-changes`, 5 casos: (1) un subtotal por categoría
  aparece al cerrar cada grupo, con el equivalente mensual correcto (ej. una categoría
  con un ANUAL de $900.000 aporta $75.000 al subtotal); (2) resumen de Egresos:
  esencial /mes + no esencial /mes == total /mes, y ese total == suma de los subtotales
  de egresos; (3) resumen de Ingresos: total /mes == suma de subtotales de ingresos;
  (4) crear/editar una plantilla (cambiando valor o periodicidad) recalcula subtotales
  y resumen; (5) una plantilla **Único** no suma al total (queda excluida) y, si una
  categoría es solo-Únicos, su subtotal es $0. Además: **mirar** que las filas de
  subtotal se distingan de las plantillas y no tengan acciones, y que el rótulo "/mes"
  quede claro. Confirmar que el CRUD, el orden y las secciones siguen intactos.

## Casos borde y manejo de errores (del spec, a no perder)
- Categoría solo con Únicos → subtotal $0 /mes; sus filas se listan igual.
- Sección sin plantillas → estado vacío actual; sin resumen ni subtotales.
- Todo esencial o todo no esencial → el otro total en $0 /mes; total /mes correcto.
- Periodicidad sin divisor conocido (que no sea Único) → se trata como mensual ÷1.
- Decimales por división → se muestran redondeados al formato COP.
- Suma de subtotales vs total de sección → coinciden por construcción (mismos
  equivalentes); redondeo solo al mostrar.
- Recalcular al crear/editar/borrar → sale de recomputar sobre `templates` en cada
  render (ya se re-fetch tras cada operación del CRUD).
