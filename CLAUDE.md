# proyecto-finanzas-4

**Estado actual:** MVP en desarrollo, con base y dos features completos y verificados.
Ver detalle en "Estado del proyecto" más abajo. `README.md` documenta el arranque.

## Qué es
App de finanzas personales (MVP, **single-user, sin auth**). React+TS (Vite) /
Python+FastAPI / Postgres (Supabase). Stack objetivo, pensado para correr dockerizado.

## Estado del proyecto

Construido y verificado (cada feature recorrió el ciclo brainstorming → spec → plan
→ implementar → verify):

- **Scaffolding** — Docker (`db`/`api`/`web`), backend Clean Architecture, frontend
  Vite+React+TS, git en `main`.
- **Capa de datos** — `supabase/migrations/`: `0001` esquema (categories/templates/
  transactions), `0002` seed de 14 categorías fijas, `0003` seed de ~15 templates de
  ejemplo (datos de dev, editables desde la UI).
- **Carga mensual desde templates** — elegir un mes, precargar una grilla con todos
  los templates (valor por defecto + fecha día 1), editar/descartar y confirmar en un
  commit batch atómico. Guard por presencia (bloquea si el mes ya tiene movimientos).
- **CRUD de plantillas** — pantalla con tabs (Plantillas / Carga mensual): crear,
  listar, editar y borrar (hard delete) plantillas. Formulario modal con categoría
  filtrada por tipo e `is_essential` solo en gasto.
- **Reportes gráficos por caja** — tab Reportes con vista mensual y anual:
  KPI tiles (ingresos/gastos/neto), gasto por categoría (barra horizontal, top 7 +
  "Otros", con tabla completa), meter de esencial vs no esencial, y en la anual la
  evolución de 12 meses (línea de 2 series) más el neto por mes (barra divergente).
  Un endpoint por vista (`/reports/monthly/{y}/{m}`, `/reports/annual/{y}`) con las
  agregaciones ya calculadas. **Recharts** es la única dependencia de UI.

- **Gestión de movimientos** — tab Movimientos con filtro por mes: listar con los
  totales del mes, crear un movimiento suelto (sin plantilla), editar y borrar.
  El **tipo es inmutable** una vez creado (el use case lo toma del movimiento
  existente e ignora el payload). Un movimiento ad-hoc se graba `ONE_TIME` con
  `template_id` NULL. Borrar todos los movimientos de un mes **libera el guard** y
  permite recargarlo — es la vía para rehacer un mes mal cargado.

Frontend: navegación por **tabs en estado local** (sin router). Specs en `docs/specs/`
y planes en `docs/plans/` (emparejados por fecha-título).

**Próximo paso natural del MVP:** a definir (p. ej. comparar períodos, presupuestos,
o exportar) — todo eso quedó explícitamente fuera del alcance de los reportes v1.

## Convenciones
- **Código en inglés** (tablas, columnas, variables, funciones, comentarios).
- **UI en español** vía `frontend/src/i18n/es.ts`, keyed por el `code` en inglés.
  Nunca hardcodear texto de usuario en componentes; agregar al diccionario i18n.
- Moneda/locale centralizados en `frontend/src/lib/format.ts` (default COP `es-CO`,
  miles con punto). No formatear números fuera de ahí.
- Colores de gráficas: paleta fija **ya validada** con el skill dataviz en
  `frontend/src/lib/colors.ts` (ALL CHECKS PASS sobre la superficie `#ffffff`).
  El color sigue al `code` de categoría, en orden fijo — no reasignar por ranking.
  Ingreso (6) y egreso (8) son **escalas separadas** para no pasar de 8 hues; la cola
  se pliega en "Otros" en gris neutro. **No elegir hues a mano**: cambiarlos solo
  re-corriendo `scripts/validate_palette.js` del skill.
- Formas de gráfica: seguir el skill dataviz (números cabecera → stat tiles, no
  grouped bar; una razón → meter, no pie de 2 gajos; nunca dual-axis; tabla-twin
  por gráfica).

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
- **Categorías fijas** (14: 6 INCOME + 8 EXPENSE), sembradas en
  `supabase/migrations/0002_seed_categories.sql`, no editables por el usuario. FK
  compuesta `(category_id, transaction_type)` garantiza a nivel de BD que la categoría
  corresponde al tipo. El snapshot de transactions guarda `category_code` (texto
  estable), no una FK viva, para sobrevivir a cambios del catálogo.

## Arquitectura backend (Clean Architecture)
`domain → application → infrastructure/interfaces`. Dependencias apuntan al dominio;
los repos son interfaces (puertos) en `domain/repositories.py` con adaptadores
SQLAlchemy en `infrastructure/`. Composition root (wiring de deps) en
`interfaces/api/deps.py`. Lógica de negocio SOLO en `application/use_cases/`.

## Entorno de desarrollo (importante)
El scaffolding (Docker, `docker-compose`, migraciones) ya está en su sitio.
- El host tiene **Python 3.11 y sin Node** → correr tests/builds **dentro de Docker**:
  - Backend tests: `docker run --rm -v "$PWD":/app -w /app python:3.12-slim bash -c "pip install -e '.[dev]' && pytest -q"` (desde `backend/`).
  - Frontend build/typecheck: `docker run --rm -v "$PWD":/app -w /app node:20-alpine sh -c "npm install && npm run build"` (desde `frontend/`).
- Stack completo: `docker compose up -d --build` (web `:5173`, api `:8000`, db `:5432`).
  Las migraciones se aplican solas al Postgres local vía `/docker-entrypoint-initdb.d`
  (orden por nombre: 0001, 0002, 0003). `docker compose down -v` resetea los datos.
- Nota de esquema/ORM: los modelos SQLAlchemy mapean sobre el esquema de las
  migraciones (no lo crean). Enums nativos de Postgres vía `SAEnum(..., create_type=
  False)`; columnas `created_at` no se mapean para que el INSERT use el `DEFAULT now()`.

## Git
Repo inicializado en rama `main` con identidad **local al repo** (no global):
`gleonmen <gleonmen@gmail.com>`. Remoto SSH previsto (aún sin configurar):
`git@github.com:gleonmen/finanzas-by-plan-4.git`. Commits por feature siguiendo el
ciclo (db → backend → frontend).

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
