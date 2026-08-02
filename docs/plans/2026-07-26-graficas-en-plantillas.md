# Gráficas en plantillas — Plan de implementación

## Objetivo
En la pantalla Plantillas, mostrar arriba de cada sección una barra por categoría
(equivalente mensual, ordenada desc) y, en Egresos, un medidor esencial/no esencial —
reutilizando los componentes de gráfica ya validados, sin repetir la tabla de detalle.

## Contexto
Todo lo necesario ya existe:
- `frontend/src/pages/Templates.tsx` tiene `renderSection(title, rows, emptyText, kind)`
  que ya calcula `groupWithSubtotals(rows)` y `sectionSummary(rows)` y muestra el
  resumen en texto + la tabla con subtotales.
- `frontend/src/lib/templateTotals.ts`: `groupWithSubtotals(rows) -> { categoryCode,
  templates, subtotalMonthly }[]` y `sectionSummary(rows) -> { essentialMonthly,
  nonEssentialMonthly, totalMonthly }` (equivalente mensual, Único excluido).
- `frontend/src/components/CategoryBars.tsx`: barra horizontal + tabla twin, ya
  generalizada con `title/shareLabel/emptyText`. Recibe `chartData` y `fullData`
  (`CategoryAmount[]` = `{category_code, amount:string}`), colorea con
  `categoryColor(code)`. **No re-ordena**: pinta en el orden recibido.
- `frontend/src/components/EssentialMeter.tsx`: medidor de una razón; recibe
  `{ split: EssentialSplit }` = `{essential:string, non_essential:string}`. Usa textos
  de `es.reports`.
- `CategoryAmount`/`EssentialSplit` viven en `lib/api.ts`. `categoryColor` ya devuelve
  gris para `taxes`. Paleta y formas ya validadas → **no se re-valida nada**.

**Sin backend.** Los datos salen de `templates` ya en memoria.

## Problema
Los totales por categoría y el esencial/no esencial ya se calculan, pero solo se ven
como números. Falta el canal visual. Como las formas (barra por magnitud, medidor por
razón) y la paleta ya están aprobadas y hay componentes que las implementan, el trabajo
es: (a) permitir usar la barra sin su tabla (para no duplicar el detalle que ya está en
la página), (b) parametrizar el wording del medidor, y (c) alimentarlos con el
equivalente mensual y montarlos en cada sección. Reusar en vez de crear evita re-validar
y mantiene una sola fuente de las formas.

## Spec de referencia
`docs/specs/2026-07-26-graficas-en-plantillas.md` (aprobada).

## Tareas a implementar

**1. CategoryBars: prop `showTable`**
- **Qué**: poder ocultar la tabla twin.
- **Dónde**: `frontend/src/components/CategoryBars.tsx`.
- **Detalles**: agregar prop opcional `showTable?: boolean` con **default `true`** (así
  la llamada de Reportes no cambia). Envolver el bloque `<table className="grid
  report-table">…</table>` en `{showTable && (…)}`. Nada más cambia (la barra, el
  tooltip y el estado vacío quedan igual). Verificar que Reportes sigue mostrando su
  tabla.

**2. EssentialMeter: props `title` y `emptyText`**
- **Qué**: permitir wording de planeación en Plantillas.
- **Dónde**: `frontend/src/components/EssentialMeter.tsx`.
- **Detalles**: agregar `title?: string` (default = `es.reports.essentialTitle`) y
  `emptyText?: string` (default = el texto de "no hay gastos" actual). Usarlos en el
  `<h2>` y en el estado vacío. Los labels internos (Esencial/No esencial) se dejan
  como están (son correctos en ambos contextos). Reportes no pasa props → sin cambios.

**3. Datos + montaje en Templates**
- **Qué**: construir los datos de gráfica y renderizar las gráficas por sección.
- **Dónde**: `frontend/src/lib/templateTotals.ts`, `frontend/src/pages/Templates.tsx`,
  `frontend/src/i18n/es.ts`.
- **Detalles**:
  - En `templateTotals.ts`, agregar `categoryAmountsMonthly(rows): CategoryAmount[]`:
    toma `groupWithSubtotals(rows)` y devuelve `{ category_code, amount:
    String(subtotalMonthly) }` **ordenado por `subtotalMonthly` desc** (la barra se
    pinta en el orden recibido, y la tabla de la página mantiene su orden canónico —
    son vistas distintas del mismo dato, ok).
  - En `renderSection` (Templates.tsx), cuando `rows.length > 0`, **arriba de la
    tabla** (bajo el resumen de texto que ya está):
    - la barra: `<CategoryBars chartData={data} fullData={data} showTable={false}
      title={kind==='income' ? t.chartIncomeByCategory : t.chartExpenseByCategory} />`
      donde `data = categoryAmountsMonthly(rows)`.
    - si `kind === 'expense'`, además el `<EssentialMeter split={essentialSplit}
      title={t.chartEssentialTitle} />` con `essentialSplit` derivado de
      `sectionSummary(rows)` (`{essential:String(essentialMonthly), non_essential:
      String(nonEssentialMonthly)}`).
  - i18n en `es.templates`: `chartIncomeByCategory` ("Ingreso por categoría (mensual)"),
    `chartExpenseByCategory` ("Gasto por categoría (mensual)"), `chartEssentialTitle`
    ("Esencial vs no esencial (mensual)").
  - Orden en la página: `<h2>` sección → resumen de texto → **gráfica(s)** → tabla. (O
    resumen → gráficas arriba de la tabla; ubicar de forma que se lea claro.)
  - Caso vacío: si `rows.length === 0` no se entra a este bloque (ya hay early-return
    con el estado vacío) → no se dibuja gráfica ni medidor. ✔ spec.

**4. Verificación punta a punta**
- **Qué**: comprobar contra spec y plan.
- **Dónde**: `docker compose up -d --build` (o el ya corriendo); build/typecheck en
  Docker.
- **Detalles**: skill `verify-after-changes`, casos: (1) Ingresos muestra su barra por
  categoría ordenada desc, montos = subtotales de su tabla; (2) Egresos muestra su
  barra (con Impuestos en gris si tiene plantillas) + el medidor; (3) **invariante**:
  el total de cada barra coincide con el subtotal de la tabla, y esencial+no esencial
  del medidor = total /mes del resumen de Egresos; (4) crear/editar/borrar una
  plantilla actualiza las gráficas; (5) **regresión**: Reportes sigue mostrando la
  barra CON su tabla (showTable default true) y el medidor con su título original.
  Además: **mirar** que no haya solape de etiquetas/overflow y que el gris de Impuestos
  se distinga por su nombre.

## Casos borde y manejo de errores (del spec, a no perder)
- Sección sin plantillas → sin gráfica ni medidor (early-return de estado vacío).
- Egresos todo esencial o todo no esencial → medidor con un lado en 0 / 100%.
- Categoría solo-Únicos → aporta 0 al mensual → sin barra (o barra en cero),
  consistente con su subtotal $0.
- Impuestos gris → identidad por etiqueta.
- Decimales por normalización → redondeados al mostrar; la tabla es la fuente de verdad.
- Regresión Reportes → `showTable` default true y `EssentialMeter` sin props → intactos.
