# Plantillas agrupadas y ordenadas — Plan de implementación

## Objetivo
La pantalla Plantillas muestra dos secciones con título (Ingresos / Egresos), cada
una con su estado vacío, y cada grupo ordenado con reglas fijas (egresos: categoría →
esencial primero → valor desc; ingresos: categoría → valor desc). Cambio solo de
frontend, sin tocar backend ni el CRUD.

## Contexto
- `frontend/src/pages/Templates.tsx` es hoy una sola tabla. Ya carga **ambas** cosas
  con `Promise.all([getTemplates(), getCategories()])`: tiene en estado `templates`
  y `categories`. `categories` viene del backend ordenado por `transaction_type, id`
  → es la fuente del **orden canónico** de categorías (no hace falta exportar los
  arrays privados de `colors.ts`).
- La fila de la tabla ya arma tipo (pill), categoría (dot con `categoryColor(code)` +
  `categoryNames`), concepto, esencial (`Sí/No/—`), valor (`formatCurrency`),
  periodicidad, y los botones Editar/Borrar. Todo eso se reutiliza tal cual.
- `Template` (de `lib/api.ts`) trae `category_code` (no `category_id`),
  `transaction_type`, `is_essential`, `default_amount` (string). El orden por
  categoría se resuelve mapeando `category_code → posición` con la lista `categories`.
- i18n en `es.templates`; formato en `format.ts`; colores en `colors.ts`.

**Sin backend, sin migraciones.** El endpoint `GET /templates` y su orden actual
(por tipo/id) quedan igual — otras pantallas (carga mensual) no se ven afectadas
porque el nuevo orden se aplica solo en esta vista.

## Problema
La lista mezcla tipos y va en orden de creación, difícil de escanear. La solución es
presentación pura: en el frontend, partir la lista por `transaction_type` y ordenar
cada grupo con un comparador de varias claves. Va en el frontend (no en el `ORDER BY`
del backend) para no acoplar el endpoint compartido ni lidiar con el `is_essential`
NULL de ingresos en SQL; y porque es una decisión de esta vista.

## Spec de referencia
`docs/specs/2026-07-26-plantillas-agrupadas-y-ordenadas.md` (aprobada).

**Discrepancia detectada y ya corregida en la spec:** el tipo de una plantilla **sí
es editable** (los radios de tipo en `TemplateFormModal` no están deshabilitados, a
diferencia de los movimientos). Consecuencia asumida en el plan: cambiar el tipo al
editar mueve la plantilla de sección; como la lista se re-parte y re-ordena en cada
render a partir del estado, esto **funciona solo** sin lógica extra.

## Tareas a implementar

**1. i18n: títulos de sección y estados vacíos**
- **Qué**: textos nuevos.
- **Dónde**: `frontend/src/i18n/es.ts` (sección `es.templates`).
- **Detalles**: `sectionIncome: "Ingresos"`, `sectionExpense: "Egresos"`,
  `emptyIncome: "No tenés plantillas de ingreso todavía."`,
  `emptyExpense: "No tenés plantillas de gasto todavía."`. Mantener el `emptyState`
  actual solo si se sigue usando para "no hay ninguna en absoluto"; si cada sección
  tiene su vacío, `emptyState` puede quedar sin uso (removerlo si queda huérfano).

**2. Helper de orden y agrupación (función pura)**
- **Qué**: partir en ingresos/egresos y ordenar cada grupo.
- **Dónde**: `frontend/src/lib/templateSort.ts` (nuevo, función pura y testeable a mano
  desde el navegador/consola).
- **Detalles**:
  - `categoryRank(categories): Record<string, number>` — mapa `code → índice` según el
    orden de la lista `categories` (que ya viene canónica del backend). Un `code`
    ausente cae al final (rank alto), sin romper.
  - `sortTemplates(list, rank)`:
    - **Egresos**: comparar por `rank[category_code]` asc; luego **esencial primero**
      (`is_essential === true` antes que `false`); luego `Number(default_amount)`
      **desc**.
    - **Ingresos**: por `rank[category_code]` asc; luego `default_amount` desc.
    - Empates: comparador **estable** (no reordena arbitrariamente; ninguna fila se
      pierde ni se duplica) — usar `Array.prototype.sort` de JS (estable) con un
      comparador que devuelva 0 en empate.
  - `groupByType(list, rank) -> { income: Template[], expense: Template[] }` que aplica
    el filtro por `transaction_type` + el sort correspondiente a cada grupo.

**3. Render de dos secciones en Templates**
- **Qué**: reemplazar la tabla única por dos secciones.
- **Dónde**: `frontend/src/pages/Templates.tsx`.
- **Detalles**:
  - Calcular `rank = categoryRank(categories)` y `{ income, expense } =
    groupByType(templates, rank)` en el render (memoizar con `useMemo` sobre
    `[templates, categories]` si conviene; no es crítico por el tamaño).
  - Extraer la tabla actual a un helper local `renderTable(rows: Template[])` (o un
    subcomponente `TemplateTable`) para no duplicar el markup de columnas/acciones;
    recibe la lista ya ordenada y mantiene los mismos handlers (`openEdit`,
    `setDeleting`).
  - Renderizar **dos** secciones, cada una con su `<h2>` (`sectionIncome` /
    `sectionExpense`): si el grupo tiene filas, la tabla; si está vacío, el banner de
    estado vacío de esa sección. El botón "Nueva plantilla" y el feedback quedan
    arriba, como ahora.
  - El estado de carga y error (`loading`, `loadError`) se maneja igual que hoy
    (mostrar error, no dibujar secciones a medias).

**4. Verificación punta a punta**
- **Qué**: comprobar contra spec y plan en el navegador.
- **Dónde**: `docker compose up -d --build`; build/typecheck del frontend en Docker.
- **Detalles**: skill `verify-after-changes`, 5 casos: (1) la pantalla muestra dos
  secciones tituladas, ingresos arriba y egresos abajo; (2) en egresos, dentro de una
  categoría con esenciales y no esenciales, los esenciales van primero y dentro de
  cada grupo el valor va de mayor a menor; (3) en ingresos, orden por categoría y
  valor desc (sin columna esencial en juego); (4) crear una plantilla nueva y ver que
  aparece en su posición ordenada, no al final; (5) editar una plantilla cambiándole
  el **tipo** y ver que se mueve a la otra sección; y un caso de borde: una sección sin
  plantillas muestra su estado vacío. Además: confirmar que el CRUD (crear/editar/
  borrar) sigue funcionando igual.

## Casos borde y manejo de errores (del spec, a no perder)
- Un tipo sin plantillas → esa sección muestra su estado vacío; la otra, normal.
- Ninguna plantilla → ambas secciones vacías; botón "Nueva plantilla" disponible.
- Empate total (misma categoría, misma esencialidad, mismo valor) → orden estable, no
  se pierde ni duplica ninguna fila.
- Categoría sin plantillas → no aparece como grupo (no hay encabezados por categoría,
  solo el título de sección; el agrupado por categoría es por el orden, no por
  subtítulos).
- Cambiar el tipo al editar → la plantilla se reubica en la otra sección (re-sort).
- Fallo de carga → manejo de error actual; no se dibujan secciones a medias.
