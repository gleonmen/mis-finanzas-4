# Gestión de plantillas (CRUD) — Plan de implementación

## Objetivo
Permitir al usuario administrar sus plantillas de punta a punta desde la UI: crear,
listar, editar y borrar (hard delete), con navegación por pestañas junto a la carga
mensual. Al terminar, el catálogo de plantillas deja de depender del seed de ejemplo.

## Contexto
El slice de carga mensual ya está construido y define los patrones a reutilizar:
- Backend Clean Architecture: `domain/` (entidades + puertos), `application/use_cases/`,
  `infrastructure/` (SQLAlchemy `models.py`/`repositories.py`), `interfaces/api/`
  (`schemas.py`, `deps.py` composition root, routers). Ya existen
  `SqlAlchemyTemplateRepository.list_all()` y el modelo `TemplateModel`/`CategoryModel`.
- El esquema (`0001_schema.sql`) ya tiene la FK compuesta `(category_id,
  transaction_type)`, el CHECK de `is_essential` por tipo, y `transactions.template_id`
  con `ON DELETE SET NULL`. **No hacen falta migraciones nuevas.**
- Frontend: `lib/api.ts` (cliente fetch + `ApiError`), `i18n/es.ts` (categoryNames,
  transactionTypeNames, frequencyNames + strings), `lib/format.ts` (COP), `lib/colors.ts`
  (`categoryColor`), y `pages/MonthLoad.tsx` + `components/DraftGrid.tsx` como
  referencia de estilo. `App.tsx` hoy renderiza solo `MonthLoad`.

## Problema
Falta la gestión del catálogo de plantillas: hoy solo existen por el seed `0003`. Se
resuelve extendiendo las capas ya montadas con las operaciones de escritura (create/
update/delete) y una pantalla nueva. El enfoque (formulario modal + lista) encaja con
las reglas condicionales del dominio (categoría filtrada por tipo, `is_essential` solo
en gasto), que se validan de forma autoritativa en los use cases. El hard delete es
seguro porque el historial está protegido por el snapshot y el `ON DELETE SET NULL`.

## Spec de referencia
`docs/specs/2026-07-22-gestion-de-plantillas-crud.md` (aprobada). Discrepancia resuelta
con el usuario y marcada aquí: el borrado usa **confirmación simple** (sin contar los
movimientos que quedan desvinculados), para no agregar una consulta/endpoint extra en v1.

## Tareas a implementar

### Backend

**1. Dominio: entidad Category y puertos de escritura**
- **Qué**: entidad `Category` y ampliar los puertos con las operaciones que faltan.
- **Dónde**: `backend/app/domain/entities.py`, `backend/app/domain/repositories.py`.
- **Detalles**:
  - `Category(id: int, code: str, transaction_type: TransactionType)`.
  - `CategoryRepository(ABC)` con `list_all() -> list[Category]` y
    `get(id) -> Category | None`.
  - Ampliar `TemplateRepository` con: `get(id) -> Template | None`,
    `create(data) -> Template`, `update(id, data) -> Template`, `delete(id) -> bool`.
  - Definir un DTO de escritura `TemplateData` (transaction_type, category_id, name,
    is_essential, default_amount, frequency) — en `domain/entities.py` o en el módulo
    del use case. `category_id` (no `category_code`) porque es lo que elige la UI.

**2. Aplicación: errores y use cases de escritura + listar categorías**
- **Qué**: use cases `ListCategories`, `CreateTemplate`, `UpdateTemplate`,
  `DeleteTemplate`, con validación de reglas de negocio.
- **Dónde**: `backend/app/application/errors.py` (ampliar),
  `backend/app/application/use_cases/{list_categories,create_template,update_template,delete_template}.py`.
- **Detalles** (validación autoritativa aquí; casos borde del spec):
  - Errores nuevos: `TemplateValidationError`, `TemplateNotFoundError`.
  - Reglas comunes a create/update (helper compartido):
    - `name` no vacío (trim).
    - `default_amount > 0`.
    - categoría existe (`CategoryRepository.get`) y su `transaction_type` **coincide**
      con el tipo del template → si no, `TemplateValidationError`.
    - `is_essential`: en `EXPENSE` obligatorio (no None); en `INCOME` se **fuerza a
      None** (se ignora lo que venga).
  - `UpdateTemplate` y `DeleteTemplate`: si el id no existe → `TemplateNotFoundError`.
  - `DeleteTemplate`: hard delete; el `ON DELETE SET NULL` del esquema preserva el
    historial (no requiere lógica extra).
  - `CreateTemplate`/`UpdateTemplate` devuelven el `Template` resultante (con
    `category_code` resuelto) para refrescar la UI.

**3. Infraestructura: adaptadores SQLAlchemy**
- **Qué**: implementar los nuevos métodos de repo.
- **Dónde**: `backend/app/infrastructure/repositories.py` (y usar `CategoryModel`/
  `TemplateModel` ya existentes en `models.py`).
- **Detalles**:
  - `SqlAlchemyCategoryRepository`: `list_all()` (ordenado por tipo/id), `get(id)`.
  - Ampliar `SqlAlchemyTemplateRepository`: `get(id)` (join categoría para resolver
    `category_code`), `create(data)` (insert + flush + devolver entidad con code),
    `update(id, data)` (cargar `TemplateModel`, setear campos, flush), `delete(id)`
    (borrar la fila; devolver si existía). El commit lo maneja `get_session` de
    `deps.py` (una transacción por request), igual que el resto.

**4. Interfaces API: schemas, routers y wiring**
- **Qué**: endpoints REST y composition root.
- **Dónde**: `backend/app/interfaces/api/schemas.py`, nuevo
  `routes_templates_admin.py` (o ampliar `routes_templates.py`),
  nuevo `routes_categories.py`, `deps.py`, `main.py`.
- **Detalles**:
  - Schemas: `CategoryOut(id, code, transaction_type)`,
    `TemplateCreateIn`/`TemplateUpdateIn(transaction_type, category_id, name,
    is_essential | None, default_amount>0, frequency)`. Reusar `TemplateOut`.
  - Endpoints:
    - `GET /categories` → lista para el selector.
    - `POST /templates` → 201 `TemplateOut`.
    - `PUT /templates/{id}` → 200 `TemplateOut`.
    - `DELETE /templates/{id}` → 204.
  - Mapeo de errores → HTTP: `TemplateValidationError` → 422,
    `TemplateNotFoundError` → 404. (`GET /templates` ya existe y se reutiliza.)
  - `deps.py`: fábricas para los 4 use cases nuevos (inyectando
    `SqlAlchemyCategoryRepository` y `SqlAlchemyTemplateRepository`). Incluir los
    routers en `main.py`.

**5. Tests backend (use cases con repos falsos)**
- **Qué**: cubrir las reglas de negocio sin BD.
- **Dónde**: `backend/tests/test_template_crud.py`.
- **Detalles**: create OK (income y expense); nombre vacío → error; monto ≤ 0 → error;
  categoría de otro tipo → error; income con is_essential → se fuerza a None; expense
  sin is_essential → error; update de id inexistente → NotFound; delete OK / delete de
  inexistente → NotFound. Extender fakes con `CategoryRepository`.

### Frontend

**6. Cliente API y tipos**
- **Qué**: llamadas y tipos para categorías y escritura de templates.
- **Dónde**: `frontend/src/lib/api.ts`.
- **Detalles**: `Category` type; `getCategories()`, `createTemplate(payload)`,
  `updateTemplate(id, payload)`, `deleteTemplate(id)`. Reusar `ApiError` para mapear
  422/404 a mensajes. Tipo `TemplateWrite` para el body.

**7. i18n y navegación por pestañas**
- **Qué**: strings de la pantalla/formulario y tabs.
- **Dónde**: `frontend/src/i18n/es.ts`, `frontend/src/App.tsx`, `frontend/src/styles.css`.
- **Detalles**: sección `es.templates` (título, botones Nueva/Editar/Borrar/Guardar/
  Cancelar, labels del form, estado vacío, confirmación de borrado, mensajes de error
  y éxito). `App.tsx` pasa a manejar estado de pestaña activa (`"templates" |
  "monthLoad"`) y renderiza `Templates` o `MonthLoad`. Estilos de tabs + modal.

**8. Pantalla de listado de plantillas**
- **Qué**: tab "Plantillas" con la lista y acciones.
- **Dónde**: `frontend/src/pages/Templates.tsx`.
- **Detalles**: al montar, `getTemplates()`; render en tabla (mismo estilo que
  `DraftGrid`): nombre, categoría (con `categoryColor` + `categoryNames`), tipo (pill),
  esencial (solo gasto), valor (COP), periodicidad; botones Editar/Borrar por fila y
  botón "Nueva plantilla". Estado vacío que invita a crear. Refrescar la lista tras
  crear/editar/borrar.

**9. Formulario modal crear/editar**
- **Qué**: componente de formulario en modal, reutilizado para alta y edición.
- **Dónde**: `frontend/src/components/TemplateFormModal.tsx` (+ `Modal.tsx` genérico si
  conviene).
- **Detalles** (reglas condicionales del spec):
  - Campos: tipo (radio/select income/expense), categoría (select **filtrado por
    tipo** usando `getCategories()`), nombre, valor (input COP con `parseAmount`/
    `formatThousands`), periodicidad (select), y `es esencial` (checkbox) **visible
    solo si tipo=EXPENSE**.
  - Al cambiar el **tipo**, limpiar/revalidar la categoría seleccionada (no dejar una
    combinación inválida) y mostrar/ocultar `es esencial`.
  - Validación local espejo del backend (nombre no vacío, valor > 0, categoría
    elegida, gasto con esencial definido) → deshabilitar Guardar si inválido.
  - En edición: precargar valores del template. Guardar → `create`/`update`, cerrar
    modal, refrescar lista, feedback. Manejar `ApiError` (422/404).

**10. Borrado con confirmación**
- **Qué**: confirmación simple antes de borrar.
- **Dónde**: `frontend/src/pages/Templates.tsx` (+ `ConfirmDialog` o modal simple).
- **Detalles**: "¿Seguro que querés borrar esta plantilla?" con Confirmar/Cancelar.
  Confirmar → `deleteTemplate(id)`, refrescar lista, feedback. Cancelar → nada.
  (Confirmación simple, sin contar movimientos — decisión registrada arriba.)

### Cierre

**11. Verificación punta a punta**
- **Qué**: comprobar el CRUD contra spec y plan en el navegador.
- **Dónde**: stack `docker compose up -d --build`; tests backend en Docker; build/
  typecheck frontend en Docker.
- **Detalles**: skill `verify-after-changes`, 5 casos: (1) crear plantilla de gasto
  (con esencial) y verla en la lista y en la carga mensual; (2) crear ingreso (sin
  esencial); (3) editar valor/nombre y ver que un mes ya cargado no cambia; (4)
  validaciones del form (nombre vacío / valor 0 / cambiar tipo revalida categoría);
  (5) borrar con confirmación y verificar que el historial persiste (snapshot).

## Casos borde y manejo de errores (del spec, a no perder)
- Nombre vacío / valor ≤ 0 / categoría sin elegir → no guarda, mensaje.
- Gasto sin `es esencial` → no guarda; ingreso con esencial → se fuerza a None.
- Categoría que no corresponde al tipo → UI lo evita (filtro) + backend 422.
- Cambiar tipo con categoría ya elegida → se limpia/revalida.
- Borrar plantilla usada en meses cargados → historial intacto (snapshot + SET NULL).
- Fallo de red/servidor en guardar/borrar → sin cambio parcial, se informa, reintentable.
- Editar/borrar plantilla ya inexistente → 404, se informa y se refresca la lista.
