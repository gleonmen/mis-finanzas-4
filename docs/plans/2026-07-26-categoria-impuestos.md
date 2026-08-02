# Categoría Impuestos — Plan de implementación

## Objetivo
Agregar la categoría fija **Impuestos** (gasto, `code="taxes"`) al catálogo, disponible
en toda la app y con color gris neutro. Al terminar, se puede crear una plantilla o
movimiento de gasto con categoría Impuestos, y aparece en Plantillas y Reportes.

## Contexto
- Las categorías se siembran en `supabase/migrations/`: `0002_seed_categories.sql`
  inserta las 14 (sin `id`, dejando que `GENERATED ALWAYS AS IDENTITY` asigne 1-14).
  El siguiente `id` libre es **15**.
- El backend es **genérico** sobre el catálogo: `GET /categories` devuelve todas
  (ordenadas por `transaction_type, id`); el form filtra por tipo; la FK compuesta
  `(category_id, transaction_type)` valida categoría↔tipo; el snapshot guarda
  `category_code`. **Nada de código backend cambia.**
- Frontend: `i18n/es.ts` tiene `categoryNames` (code→nombre). `lib/colors.ts` mapea los
  8 codes de egreso a los 8 slots validados (`EXPENSE_ORDER`) y `categoryColor(code)`
  cae a `OTHER_COLOR` (gris) para un code desconocido — que es justo el comportamiento
  deseado para `taxes`. El orden canónico en Plantillas sale de la lista `categories`
  (por `id`), así que `taxes` (id 15) queda **última** en Egresos.
- **Migraciones y volumen:** `/docker-entrypoint-initdb.d` corre **solo en el primer
  init** del volumen de Postgres. Una BD ya inicializada **no** re-aplica migraciones,
  así que hay que insertar la fila también a mano en la BD viva.

## Problema
Falta una fila en `categories`. Como el resto ya es genérico, el trabajo es: sembrarla
(migración para bases nuevas + INSERT puntual para la base actual) y darle nombre en
español. El color gris sale solo por el fallback; se documenta para que no se
"arregle" agregando un 9º slot que rompería la paleta validada.

## Spec de referencia
`docs/specs/2026-07-26-categoria-impuestos.md` (aprobada).

## Tareas a implementar

**1. Migración de seed (0004) — para bases nuevas**
- **Qué**: insertar la categoría Impuestos.
- **Dónde**: `supabase/migrations/0004_seed_taxes_category.sql` (nuevo).
- **Detalles**: `INSERT INTO categories (code, transaction_type) VALUES ('taxes',
  'EXPENSE');` — **sin `id`** (igual que `0002`), para que IDENTITY le asigne 15 en un
  init fresco. Comentario arriba explicando que es aditivo al catálogo fijo.

**2. Aplicar el alta a la base ya inicializada**
- **Qué**: correr el mismo INSERT contra el Postgres del compose en curso.
- **Dónde**: comando puntual (no es código): `docker exec ... psql ...` ejecutando el
  contenido de `0004`.
- **Detalles**: idempotencia — el INSERT crudo fallaría si se corre dos veces (código
  duplicado). Para que sea seguro, la sentencia usa
  `INSERT ... WHERE NOT EXISTS (SELECT 1 FROM categories WHERE code='taxes')`
  (o `ON CONFLICT` si hubiera unique sobre code — sí lo hay: `code TEXT UNIQUE`, así
  que `ON CONFLICT (code) DO NOTHING` es lo más limpio). Usar la **misma** sentencia en
  la migración 0004 y en el alta manual, para una sola fuente. Verificar que quede con
  `id=15` y `transaction_type=EXPENSE`.

**3. Frontend: nombre i18n + color explícito**
- **Qué**: nombre en español y dejar el gris documentado.
- **Dónde**: `frontend/src/i18n/es.ts` (`categoryNames`), `frontend/src/lib/colors.ts`.
- **Detalles**:
  - `categoryNames.taxes = "Impuestos"`.
  - En `colors.ts`, **no** agregar `taxes` a `EXPENSE_ORDER` (ese array alimenta la
    paleta validada de 8; un 9º code la desbalancearía). Agregar un comentario junto a
    `EXPENSE_ORDER`/`categoryColor` dejando explícito que `taxes` usa a propósito el
    gris neutro (`OTHER_COLOR`) por el fallback, decisión tomada para no introducir un
    9º hue que no pasa el validador CVD.

**4. Verificación punta a punta**
- **Qué**: comprobar contra spec y plan.
- **Dónde**: stack `docker compose up -d --build` (o el ya corriendo); build/typecheck
  del frontend en Docker.
- **Detalles**: skill `verify-after-changes`, casos: (1) `GET /categories` trae
  `taxes/EXPENSE` con id 15; (2) en el form de plantilla con tipo **gasto**, "Impuestos"
  aparece en el selector; con tipo **ingreso**, no aparece; (3) crear una plantilla de
  Impuestos y verla en Plantillas agrupada bajo "Impuestos" con su subtotal, **última**
  en Egresos, con el punto de color en **gris**; (4) esa plantilla suma a los totales de
  Egresos como cualquier otra; (5) opcional: cargarla en un mes y ver que el reporte de
  gasto la agrupa por su code. Además: confirmar que las otras 8 categorías conservan
  su color validado (no se corrió ningún slot). Limpiar la plantilla de prueba al final.

## Casos borde y manejo de errores (del spec, a no perder)
- BD ya inicializada → el alta manual (tarea 2) la agrega; la migración 0004 cubre
  bases nuevas. `ON CONFLICT (code) DO NOTHING` hace ambas idempotentes.
- Impuestos en ingreso → el form filtra por tipo y la FK compuesta lo rechaza.
- Gris compartido con "Otros" en gráficos → se distingue por la etiqueta/nombre.
- Reportes históricos → intactos (snapshot); Impuestos solo afecta lo nuevo.
- Las 8 categorías de gasto existentes → conservan su color; `taxes` no entra a
  `EXPENSE_ORDER`.
