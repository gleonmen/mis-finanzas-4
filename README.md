# proyecto-finanzas-4

App de finanzas personales (MVP, single-user, sin auth).
React+TS (Vite) / Python+FastAPI / Postgres, dockerizado.

## Qué hace

La app se organiza en tres pestañas:

- **Plantillas** — el catálogo de movimientos recurrentes (los "tipos": categoría,
  valor por defecto, periodicidad, y si el gasto es esencial). CRUD completo.
- **Carga mensual** — elegís un mes y se precarga una grilla con todas las
  plantillas; ajustás valor y fecha, descartás lo que no aplique y confirmás todo
  en una sola operación atómica. Si el mes ya tiene movimientos, se bloquea.
- **Reportes** — vista mensual y anual: ingresos/gastos/neto, gasto por categoría,
  cuánto del gasto es esencial, y la evolución mes a mes del año.

Dos reglas de dominio que explican el resto:

- **Reportes por caja**: un monto cae completo en el mes de su fecha. Los anuales
  **no** se prorratean; la periodicidad es solo un dato descriptivo.
- **Snapshot**: cada movimiento guarda una foto de los datos de su plantilla, así
  que editar o borrar una plantilla nunca altera los reportes ya cargados.

## Stack

| Capa      | Tecnología                          | Puerto |
|-----------|-------------------------------------|--------|
| `web`     | React + TypeScript (Vite)           | 5173   |
| `api`     | FastAPI (Clean Architecture)        | 8000   |
| `db`      | Postgres 16                         | 5432   |

## Arranque rápido

```bash
cp .env.example .env
docker compose up -d --build
```

- Frontend: http://localhost:5173
- API (health): http://localhost:8000/health
- API docs: http://localhost:8000/docs

Las migraciones de `supabase/migrations/` se aplican solas al inicializar el
Postgres local, en orden por nombre: `0001` esquema, `0002` seed de las 14
categorías fijas, `0003` seed de plantillas de ejemplo (datos de dev, editables
desde la UI). `docker compose down -v` resetea los datos.

## Desarrollo

El host tiene Python 3.11 y **sin Node** → correr tests/builds dentro de Docker.

```bash
# Backend tests (desde backend/)
docker run --rm -v "$PWD":/app -w /app python:3.12-slim \
  bash -c "pip install -e '.[dev]' && pytest -q"

# Frontend build/typecheck (desde frontend/)
docker run --rm -v "$PWD":/app -w /app node:20-alpine \
  sh -c "npm install && npm run build"
```

## API

| Método | Ruta | Para qué |
|---|---|---|
| `GET` | `/categories` | Las 14 categorías fijas (pobla el selector del formulario) |
| `GET` | `/templates` | Listar plantillas |
| `POST` | `/templates` | Crear plantilla |
| `PUT` | `/templates/{id}` | Editar plantilla |
| `DELETE` | `/templates/{id}` | Borrar plantilla (hard delete) |
| `GET` | `/months/{año}/{mes}/status` | Plantillas + si el mes ya fue cargado |
| `POST` | `/months/{año}/{mes}/load` | Confirmar la carga mensual (batch atómico) |
| `GET` | `/reports/monthly/{año}/{mes}` | Paquete completo del reporte mensual |
| `GET` | `/reports/annual/{año}` | Paquete completo del reporte anual |

Detalle interactivo en http://localhost:8000/docs.

## Estructura

```
backend/app/
  domain/          # entidades + puertos (repositorios) — sin dependencias externas
  application/     # use_cases: la lógica de negocio vive solo aquí
  infrastructure/  # adaptadores SQLAlchemy de los puertos
  interfaces/api/  # routers + schemas + deps.py (composition root)
frontend/src/
  pages/           # una pantalla por pestaña (Templates, MonthLoad, Reports)
  components/      # grilla, modal, gráficas (Recharts)
  i18n/es.ts       # textos de usuario (keyed por code en inglés)
  lib/format.ts    # formato moneda/locale (COP, es-CO)
  lib/colors.ts    # paleta fija VALIDADA, color por code de categoría
supabase/migrations/  # 0001 esquema, 0002 categorías, 0003 plantillas de ejemplo
docs/
  specs/   # design-specs aprobados
  plans/   # planes de implementación
```

Los colores de las gráficas no se eligen a mano: la paleta de `lib/colors.ts` pasó
el validador del skill `dataviz` (contraste, croma y separación bajo daltonismo).
Si hay que cambiarla, se re-corre el validador.

## Documentación de los desarrollos

Cada feature tiene su spec (qué se construye, desde la vista del usuario) y su plan
(cómo), emparejados por fecha-título:

| Feature | Spec | Plan |
|---|---|---|
| Carga mensual desde plantillas | [spec](docs/specs/2026-07-22-carga-mensual-desde-templates.md) | [plan](docs/plans/2026-07-22-carga-mensual-desde-templates.md) |
| Gestión de plantillas (CRUD) | [spec](docs/specs/2026-07-22-gestion-de-plantillas-crud.md) | [plan](docs/plans/2026-07-22-gestion-de-plantillas-crud.md) |
| Reportes gráficos por caja | [spec](docs/specs/2026-07-23-reportes-graficos-por-caja.md) | [plan](docs/plans/2026-07-23-reportes-graficos-por-caja.md) |
