# Carga mensual de movimientos desde templates — Plan de implementación

## Objetivo
Dejar funcionando, punta a punta, la carga mensual de movimientos desde templates:
el usuario elige un mes, ve una grilla precargada con todos los templates (INCOME +
EXPENSE), edita valor/fecha, descarta renglones y confirma en un único commit atómico
que crea las transactions con snapshot. Incluye las fundaciones mínimas del slice
(BD, categorías sembradas, templates, transactions) para que el flujo corra completo.

## Contexto
Proyecto recién iniciado: el repo solo tiene `CLAUDE.md`. No hay scaffolding, ni
Docker, ni código backend/frontend todavía, así que este plan crea la base además de
la feature. Stack objetivo (de `CLAUDE.md`): React+TS (Vite) / Python+FastAPI /
Postgres (Supabase), dockerizado. Backend en Clean Architecture
(`domain → application → infrastructure/interfaces`), lógica de negocio solo en
`application/use_cases/`, repos como puertos en `domain/repositories.py` con
adaptadores SQLAlchemy, composition root en `interfaces/api/deps.py`.

Convenciones que el plan debe respetar:
- Código en inglés; UI en español vía `frontend/src/i18n/es.ts` (keyed por `code`).
- Formato moneda/locale centralizado en `frontend/src/lib/format.ts` (COP, es-CO).
- Categorías fijas sembradas en `supabase/migrations/0002_seed_categories.sql`, con
  FK compuesta `(category_id, transaction_type)`.
- Templates precargan valor y periodicidad; transactions guardan **snapshot** de
  `type/category/name/is_essential/frequency`; reportes por caja (no se prorratea).
- `is_essential`: obligatorio en EXPENSE, NULL en INCOME.

No hay código reutilizable existente; sí se reutilizan las utilidades que este mismo
slice crea (`format.ts`, cliente API, i18n) en la pantalla de carga.

## Problema
Instanciar cada mes los movimientos recurrentes a mano es tedioso y repite datos que
ya viven en los templates. La solución elegida (Opción B) arma el borrador en el
frontend a partir de `GET /templates`, permite edición local sin tocar la BD, y
persiste todo en un único POST batch atómico validado en el backend. Es el mejor
encaje para un MVP single-user: UX fluida, sin filas basura en la BD, operación
todo-o-nada, y la lógica de negocio centralizada en el use case (el front solo asiste
con validación inmediata). El guard "mes ya cargado" por presencia mantiene v1 simple.

## Spec de referencia
`docs/specs/2026-07-22-carga-mensual-desde-templates.md` (aprobada). El plan implementa
ese spec sin desviarse; cualquier discrepancia que surja se marca explícitamente aquí.

## Tareas a implementar

### Fundaciones

**1. Scaffolding del repositorio y entorno dockerizado**
- **Qué**: estructura de carpetas + Docker para correr backend, frontend y Postgres.
- **Dónde**: raíz (`docker-compose.yml`, `.env.example`, `.gitignore`, `README.md`),
  `backend/` (`Dockerfile`, `pyproject.toml` con deps FastAPI/SQLAlchemy/psycopg +
  `[dev]` pytest), `frontend/` (`Dockerfile`, `package.json`, Vite+TS scaffold),
  `supabase/migrations/`.
- **Detalles**: `docker-compose` con servicio `db` (postgres) que monta
  `supabase/migrations/` en `/docker-entrypoint-initdb.d` (orden 0001, 0002), servicio
  `api` y `web`. Recordar que el host no tiene Node y usa Python 3.11 → tests/builds
  dentro de Docker (ver comandos en `CLAUDE.md`). `git init` + identidad **local** al
  repo (rama `main`, `gleonmen <gleonmen@gmail.com>`), sin config global.

**2. Migración de esquema (0001)**
- **Qué**: crear tablas `categories`, `templates`, `transactions`.
- **Dónde**: `supabase/migrations/0001_schema.sql`.
- **Detalles**:
  - `transaction_type` como enum (`INCOME`/`EXPENSE`) o CHECK.
  - `categories(id, code, name, transaction_type, ...)` con UNIQUE
    `(id, transaction_type)` para soportar la FK compuesta.
  - `templates(id, name, transaction_type, category_id, is_essential, default_amount,
    frequency, ...)` con FK compuesta `(category_id, transaction_type)` →
    `categories(id, transaction_type)`. CHECK: `is_essential` NOT NULL si EXPENSE,
    NULL si INCOME.
  - `transactions` con **columnas de snapshot**: `transaction_type`, `category_code`
    (texto estable en inglés, copiado en la transacción — NO FK viva a categories),
    `name`, `is_essential`, `frequency`, más `amount` y `date`. El snapshot debe
    sobrevivir a edición/borrado del template o de la categoría → no depender de FK
    viva para los reportes históricos. Mismo CHECK de `is_essential` por tipo.
  - Índice por mes/fecha en `transactions` para el guard por presencia y futuros
    reportes.

**3. Migración de seed de categorías (0002)**
- **Qué**: sembrar las **14 categorías fijas** (grupos) por tipo. No editables por el
  usuario. Los sub-ítems de la lista del usuario (Arriendo, Netflix, Combustible…) NO
  son categorías: viven en el `name` del template.
- **Dónde**: `supabase/migrations/0002_seed_categories.sql`.
- **Detalles**: insertar cada categoría con su `code` (inglés, estable) y
  `transaction_type`. El `name` en español NO va en la BD: va en `frontend/src/i18n/es.ts`
  keyed por `code` (convención del proyecto). Set definitivo:

  | transaction_type | code | Nombre UI (es, va en i18n) |
  |---|---|---|
  | INCOME | `salaries` | Sueldos y Salarios |
  | INCOME | `freelance` | Trabajos Independientes / Freelance |
  | INCOME | `rentals` | Rentas y Alquileres |
  | INCOME | `investment_income` | Rendimientos e Inversiones |
  | INCOME | `business` | Negocios / Emprendimientos |
  | INCOME | `other_income` | Otros Ingresos |
  | EXPENSE | `housing_utilities` | Vivienda y Servicios Públicos |
  | EXPENSE | `food_household` | Alimentación y Hogar |
  | EXPENSE | `transport` | Transporte y Vehículos |
  | EXPENSE | `health` | Salud y Bienestar |
  | EXPENSE | `education` | Educación y Desarrollo |
  | EXPENSE | `lifestyle` | Entretenimiento y Estilo de Vida |
  | EXPENSE | `debt_finance` | Deudas y Finanzas |
  | EXPENSE | `savings_investment` | Ahorro e Inversión |

  Los sub-ítems del usuario quedan documentados como **ejemplos/hints** por categoría
  (útiles al crear templates), no como filas de BD.

### Backend (Clean Architecture)

**4. Capa de dominio: entidades y puertos**
- **Qué**: entidades y contratos de repositorio.
- **Dónde**: `backend/app/domain/entities.py`, `backend/app/domain/repositories.py`.
- **Detalles**: entidades `Category`, `Template`, `Transaction` (con sus campos de
  snapshot). Puertos: `TemplateRepository.list_all()`,
  `TransactionRepository.count_in_month(year, month) -> int` (guard),
  `TransactionRepository.bulk_create(transactions) -> None` (atómico). Sin dependencias
  a SQLAlchemy en esta capa.

**5. Use case: preparar borrador de carga mensual**
- **Qué**: obtener los templates que alimentan la grilla.
- **Dónde**: `backend/app/application/use_cases/list_templates.py` (o
  `build_month_draft.py`).
- **Detalles**: devuelve todos los templates para que el front arme el borrador. En
  v1 la construcción de renglones (fecha día 1, valor=default) puede vivir en el
  front, pero el use case es la fuente de los templates. Incluye, opcionalmente, el
  estado del guard (si el mes ya tiene transactions) para no pintar la grilla en vano.

**6. Use case: confirmar carga mensual (batch atómico)**
- **Qué**: crear todas las transactions del borrador, todo-o-nada, con guard.
- **Dónde**: `backend/app/application/use_cases/load_month_from_templates.py`.
- **Detalles** (núcleo de negocio, cubrir casos del spec):
  - Recibe `year`, `month` y la lista de renglones (cada uno: template_id, amount,
    date). Para cada renglón, **re-hidrata el snapshot desde el template** en el
    servidor (no confiar en snapshot enviado por el front) → snapshot de
    `type/category/name/is_essential/frequency`.
  - **Guard por presencia, re-chequeado aquí** (no solo al abrir): si
    `count_in_month(year, month) > 0` → rechazar toda la carga (error dedicado). Cubre
    el caso de carrera del spec.
  - Validaciones: `amount` numérico > 0; `date` dentro de `[año-mes-01, fin de mes]`;
    `is_essential` según tipo del template (EXPENSE no nulo, INCOME nulo). Si algún
    renglón es inválido → rechazar todo con detalle de qué falló (todo-o-nada).
  - Borrador vacío / sin templates → error/estado "nada que cargar".
  - Persistir con `bulk_create` en una sola transacción de BD (rollback ante fallo).

**7. Infraestructura: modelos y adaptadores SQLAlchemy**
- **Qué**: mapear entidades a tablas e implementar los puertos.
- **Dónde**: `backend/app/infrastructure/models.py`,
  `backend/app/infrastructure/repositories.py`, `.../db.py` (engine/session).
- **Detalles**: modelos SQLAlchemy para `categories/templates/transactions`.
  Adaptadores `SqlAlchemyTemplateRepository` y `SqlAlchemyTransactionRepository`
  implementando los puertos; `bulk_create` dentro de una transacción; `count_in_month`
  con filtro por rango de fecha usando el índice de la tarea 2.

**8. Interfaces API: routers, schemas y composition root**
- **Qué**: exponer los endpoints y cablear dependencias.
- **Dónde**: `backend/app/interfaces/api/` (`routes_templates.py`,
  `routes_month_load.py`, `schemas.py`, `deps.py`), `backend/app/main.py`.
- **Detalles**:
  - `GET /templates` → lista para la grilla.
  - `GET /months/{year}-{month}/status` (o `/transactions?month=`) → guard por
    presencia para decidir si se puede cargar.
  - `POST /months/{year}-{month}/load` → cuerpo con los renglones del borrador; llama
    al use case 6. Respuestas: 201 (creado), 409 (mes ya cargado / guard), 422
    (validación de renglones), 400 (borrador vacío). Mensajes de error claros para
    que el front los muestre.
  - `deps.py` es el único lugar que arma los adaptadores concretos y los inyecta en
    los use cases (composition root). Pydantic schemas para request/response.

### Frontend

**9. Scaffolding frontend + utilidades base**
- **Qué**: app Vite+TS con i18n, formato y cliente API.
- **Dónde**: `frontend/src/i18n/es.ts`, `frontend/src/lib/format.ts`,
  `frontend/src/lib/colors.ts` (placeholder, no crítico para este flujo),
  `frontend/src/lib/api.ts`, estructura de rutas/páginas.
- **Detalles**: `format.ts` con moneda COP/es-CO (miles con punto) — todo número pasa
  por acá. `es.ts` keyed por `code` en inglés; ningún texto de usuario hardcodeado en
  componentes. `api.ts` con las llamadas a los 3 endpoints.

**10. Pantalla de carga mensual: selección de mes + guard**
- **Qué**: elegir mes/año y decidir si se puede cargar.
- **Dónde**: `frontend/src/pages/MonthLoad.tsx` (o equivalente) + entrada i18n.
- **Detalles**: selector mes/año. Al elegir, consulta el status; si el mes ya tiene
  transactions → muestra aviso ("mes ya cargado") y no pinta la grilla. Si está vacío
  → carga templates (`GET /templates`) y arma el borrador.

**11. Grilla de borrador editable + validación local**
- **Qué**: renglones editables con descarte y validación inmediata.
- **Dónde**: `frontend/src/pages/MonthLoad.tsx` / componente `DraftGrid`.
- **Detalles**:
  - Un renglón por template: **no editable** tipo/categoría/nombre; **editable**
    valor (precargado `default_amount`, formateado COP) y fecha (precargada día 1).
  - Descartar renglón = quitarlo del estado local (sin persistir, sin "deshacer" en
    v1, según spec).
  - Validación local que **espeja** la del backend para feedback inmediato: fecha
    dentro del mes, monto > 0 válido. Renglones inválidos se marcan y deshabilitan
    Confirmar. (La validación autoritativa vive en el use case; el front solo asiste.)
  - Estados: sin templates → mensaje; borrador vacío tras descartar todo → Confirmar
    deshabilitado con aviso "nada que cargar".

**12. Confirmación batch + manejo de respuestas**
- **Qué**: enviar el borrador y reflejar el resultado.
- **Dónde**: `frontend/src/pages/MonthLoad.tsx` + `api.ts` + i18n.
- **Detalles**: Confirmar → `POST /months/{ym}/load` con los renglones vigentes. Éxito
  → mensaje de mes cargado y bloqueo de recarga. Manejar 409 (mes ya cargado, incluso
  por carrera), 422 (renglón inválido — mostrar cuál), 400 (borrador vacío). Todos los
  mensajes desde i18n en español.

### Cierre

**13. Verificación punta a punta**
- **Qué**: comprobar el slice contra spec y plan.
- **Dónde**: stack completo vía `docker compose up -d --build`; tests backend en
  Docker (`pytest`), build/typecheck frontend en Docker.
- **Detalles**: se ejecuta con el skill `verify-after-changes` (5 casos clave en el
  navegador): flujo feliz, mes ya cargado (guard), fecha fuera de mes, monto inválido,
  descartar todo / sin templates. Cada tarea del plan y cada comportamiento del spec
  debe quedar cubierto antes de dar luz verde.

## Casos borde y manejo de errores (del spec, a no perder)
- Mes ya cargado → 409, sin duplicar (guard re-chequeado al confirmar por carrera).
- Fecha fuera del mes → renglón inválido, no confirma.
- Monto vacío/no numérico/negativo → renglón inválido, no confirma.
- Sin templates → grilla vacía, no se puede confirmar.
- Borrador vacío (descartó todo) → no crea nada, avisa.
- Fallo de persistencia → atómico, rollback, mes intacto.
- `is_essential` según tipo respetado en cada snapshot.
