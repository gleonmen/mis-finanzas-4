# proyecto-finanzas-4

App de finanzas personales (MVP, single-user, sin auth).
React+TS (Vite) / Python+FastAPI / Postgres, dockerizado.

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
Postgres local (orden por nombre: `0001`, `0002`...). `docker compose down -v`
resetea los datos.

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

## Estructura

```
backend/app/
  domain/          # entidades + puertos (repositorios) — sin dependencias externas
  application/     # use_cases: la lógica de negocio vive solo aquí
  infrastructure/  # adaptadores SQLAlchemy de los puertos
  interfaces/api/  # routers + schemas + deps.py (composition root)
frontend/src/
  i18n/es.ts       # textos de usuario (keyed por code en inglés)
  lib/format.ts    # formato moneda/locale (COP, es-CO)
  lib/colors.ts    # paleta fija de colores por code de categoría
supabase/migrations/  # 0001 schema, 0002 seed categorías
docs/
  specs/   # design-specs aprobados
  plans/   # planes de implementación
```

## Documentación del desarrollo en curso

- Spec: [`docs/specs/2026-07-22-carga-mensual-desde-templates.md`](docs/specs/2026-07-22-carga-mensual-desde-templates.md)
- Plan: [`docs/plans/2026-07-22-carga-mensual-desde-templates.md`](docs/plans/2026-07-22-carga-mensual-desde-templates.md)
