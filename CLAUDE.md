# proyecto-finanzas-4

**Estado actual:** proyecto recién iniciado, aún sin código. Este archivo es la
especificación de arranque; `README.md` y `docs/PLAN.md` se crearán al construir.

## Qué es
App de finanzas personales (MVP, **single-user, sin auth**). React+TS (Vite) /
Python+FastAPI / Postgres (Supabase). Stack objetivo, pensado para correr dockerizado.

## Convenciones
- **Código en inglés** (tablas, columnas, variables, funciones, comentarios).
- **UI en español** vía `frontend/src/i18n/es.ts`, keyed por el `code` en inglés.
  Nunca hardcodear texto de usuario en componentes; agregar al diccionario i18n.
- Moneda/locale centralizados en `frontend/src/lib/format.ts` (default COP `es-CO`,
  miles con punto). No formatear números fuera de ahí.
- Colores de gráficas: paleta fija validada (skill dataviz) en `frontend/src/lib/colors.ts`.
  El color sigue al `code` de categoría, en orden fijo — no reasignar por ranking.

## Modelo de dominio (reglas clave)
- **Templates** = los "tipos" configurables: `category` + `is_essential` +
  `default_amount` + `frequency`. Al registrar un movimiento se **precargan**
  valor y periodicidad (editables).
- **Transactions** guardan un **snapshot** de `type/category/name/is_essential/
  frequency` de la plantilla → los reportes históricos no cambian si la plantilla
  se edita/borra.
- **Reportes por caja**: un monto cae completo en su mes; los anuales NO se
  prorratean. `frequency` es solo metadato, no afecta cálculos.
- `is_essential`: obligatorio en `EXPENSE`, `NULL` en `INCOME`.
- **Categorías fijas**, se sembrarán en `supabase/migrations/0002_seed_categories.sql`,
  no editables por el usuario. FK compuesta `(category_id, transaction_type)`
  garantiza a nivel de BD que la categoría corresponde al tipo.

## Arquitectura backend (Clean Architecture)
`domain → application → infrastructure/interfaces`. Dependencias apuntan al dominio;
los repos son interfaces (puertos) en `domain/repositories.py` con adaptadores
SQLAlchemy en `infrastructure/`. Composition root (wiring de deps) en
`interfaces/api/deps.py`. Lógica de negocio SOLO en `application/use_cases/`.

## Entorno de desarrollo (importante)
El scaffolding (Docker, `docker-compose`, migraciones) aún no existe; esto es el
flujo previsto para cuando el código esté en su sitio.
- El host tiene **Python 3.11 y sin Node** → correr tests/builds **dentro de Docker**:
  - Backend tests: `docker run --rm -v "$PWD":/app -w /app python:3.12-slim bash -c "pip install -e '.[dev]' && pytest -q"` (desde `backend/`).
  - Frontend build/typecheck: `docker run --rm -v "$PWD":/app -w /app node:20-alpine sh -c "npm install && npm run build"` (desde `frontend/`).
- Stack completo: `docker compose up -d --build`. Las migraciones se aplican solas
  al Postgres local vía `/docker-entrypoint-initdb.d` (orden por nombre: 0001, 0002).
  `docker compose down -v` resetea los datos.

## Git
Pendiente: `git init` + configurar identidad **local al repo** (no global). Config
prevista: rama `main`, remoto SSH `git@github.com:gleonmen/finanzas-by-plan-4.git`,
identidad `gleonmen <gleonmen@gmail.com>`.

## Flujo de trabajo (features nuevos)

Todo feature nuevo sigue este ciclo, en orden:

1. **Entender** — aclarar el requerimiento y las reglas de dominio afectadas antes
   de tocar código; preguntar si hay ambigüedad.
2. **Explorar** — buscar código, patrones y utilidades existentes reutilizables
   antes de escribir algo nuevo.
3. **Generar plan** — proponer el enfoque (archivos a tocar, casos borde) y
   validarlo antes de implementar.
4. **Implementar** — seguir el plan y las convenciones.
5. **Verificar contra el plan.**

## Skills del proyecto

El ciclo anterior se apoya en estos skills (en `.claude/skills/`), en este orden:

- **brainstorming** — al arrancar un desarrollo nuevo. Desambigua el pedido con
  pocas preguntas esenciales y propone 2-3 alternativas con una recomendación.
  Cubre las fases **Entender** y parte de **Generar plan**.
- **design-spec** — una vez claro el problema y el enfoque. Redacta el documento de
  especificaciones desde el punto de vista del usuario y lo guarda en
  `docs/specs/YYYY-MM-DD-title.md`. Tiene un **approval gate**: la spec se itera
  hasta que el usuario la aprueba explícitamente antes de continuar.
- **design-plan** — una vez que el usuario aprueba la spec. Traduce la spec en un
  plan de implementación (objetivo, contexto, problema, spec de referencia y
  tareas detalladas) y lo guarda en `docs/plans/YYYY-MM-DD-title.md`. Formaliza el
  **plan** antes de implementar.
- **verify-after-changes** — cuando la implementación se considera terminada.
  Levanta el servidor, prueba 5 casos importantes en el navegador, compara contra
  el plan y el spec, y arregla lo que falle o da luz verde. Es la fase **Verificar
  contra el plan**. El **design-plan** (`docs/plans/YYYY-MM-DD-title.md`) es el
  documento de referencia contra el cual se verifica: cada tarea del plan y cada
  comportamiento del spec deben quedar cubiertos y comprobados antes de dar luz verde.
