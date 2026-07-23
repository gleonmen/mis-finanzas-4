# Gestión de plantillas (CRUD)

## Overview
Pantalla para administrar las plantillas ("tipos" configurables de ingreso y gasto):
crear, listar, editar y borrar. Las plantillas son la base de la carga mensual —
cada mes se copian con sus valores por defecto— así que el usuario necesita poder
configurarlas él mismo en vez de depender de datos precargados. Esta funcionalidad
cierra esa precondición: da control total sobre el catálogo de plantillas.

## Usuario objetivo
Usuario único de la app de finanzas personales (single-user, sin auth). Es quien
define sus movimientos recurrentes: su sueldo, su arriendo, sus suscripciones, etc.
Perfil no técnico; quiere armar y mantener su lista de plantillas de forma simple,
con los montos y periodicidades que usa como punto de partida cada mes.

## Contexto del problema
La carga mensual copia todas las plantillas, pero hoy las plantillas solo existen
porque vinieron sembradas como datos de ejemplo: no hay forma de crear las propias,
ajustar un monto por defecto, corregir un nombre o eliminar las que no aplican. Sin
gestión, el usuario está atado a un catálogo fijo que no es el suyo. Esta pantalla
resuelve eso permitiéndole administrar sus plantillas de principio a fin.

Regla de negocio importante que da tranquilidad al editar/borrar: los movimientos ya
registrados guardan una **foto** (snapshot) de la plantilla al momento de crearse.
Por eso, editar o borrar una plantilla **no altera** los movimientos históricos ya
cargados; solo cambia lo que se precargará de ahí en adelante.

## Alcance versión 1

### Incluye
- Nueva navegación por pestañas entre **Plantillas** y **Carga mensual** (la pantalla
  de carga ya existente).
- **Listar** todas las plantillas, agrupadas/legibles por tipo (ingreso/gasto) y
  categoría, mostrando nombre, categoría, si es esencial, valor por defecto y
  periodicidad.
- **Crear** una plantilla mediante un formulario, definiendo:
  - tipo (ingreso o gasto),
  - categoría (elegida de las categorías fijas, filtradas según el tipo),
  - nombre,
  - si es esencial (**solo** para gastos),
  - valor por defecto,
  - periodicidad.
- **Editar** una plantilla existente con el mismo formulario, precargado.
- **Borrar** una plantilla, con confirmación previa. El borrado es definitivo
  (no hay papelera).
- Mensajería en español y formato de moneda COP consistentes con el resto de la app.

### No incluye
- Editar o crear **categorías**: siguen siendo fijas y no editables por el usuario.
- Borrado suave / archivar / activar-desactivar plantillas (el borrado es definitivo).
- Deshacer un borrado.
- Editar movimientos ya registrados desde esta pantalla (el historial es intocable
  aquí; su snapshot no cambia al editar/borrar la plantilla).
- Duplicar/clonar plantillas, importación masiva, orden manual (drag & drop).
- Búsqueda/filtrado avanzado del listado (más allá del agrupado por tipo/categoría).

## Comportamiento esperado

### Navegación
1. La app muestra dos pestañas: **Plantillas** y **Carga mensual**. Al abrir
   Plantillas, se ve el listado de plantillas existentes.

### Listar
2. El listado muestra todas las plantillas con: nombre, categoría (en español), tipo
   (ingreso/gasto), si es esencial (solo aplica a gastos), valor por defecto
   (formato COP) y periodicidad (en español).
3. Si no hay ninguna plantilla, se muestra un estado vacío que invita a crear la
   primera.

### Crear
4. El usuario pulsa "Nueva plantilla" y se abre un formulario (modal).
5. Elige el **tipo** (ingreso/gasto). Al elegirlo, el selector de **categoría** se
   filtra para mostrar solo las categorías de ese tipo.
6. Si el tipo es **gasto**, aparece el control **es esencial** (obligatorio). Si es
   **ingreso**, ese control no se muestra (queda sin valor).
7. Completa nombre, valor por defecto (mayor a cero) y periodicidad.
8. Al guardar, la plantilla se crea y aparece en el listado; el formulario se cierra
   y se confirma la creación.

### Editar
9. Desde una fila del listado, el usuario elige "Editar". Se abre el mismo formulario
   precargado con los valores actuales.
10. Aplica los cambios y guarda. El listado refleja los nuevos valores. Se le comunica
    (o es evidente por el contexto) que los movimientos ya cargados no cambian.

### Borrar
11. Desde una fila, el usuario elige "Borrar". Se le pide **confirmación explícita**
    antes de eliminar.
12. Al confirmar, la plantilla desaparece del listado. Los movimientos históricos que
    se hayan originado en esa plantilla se conservan intactos (su snapshot no cambia);
    solo pierden el vínculo con la plantilla ya inexistente.
13. Si cancela la confirmación, no pasa nada.

### Interacción con la carga mensual
14. Los cambios se reflejan en la carga mensual: una plantilla nueva aparecerá en la
    grilla del próximo mes que se cargue; una editada se precargará con sus nuevos
    valores; una borrada ya no aparecerá. (Los meses ya cargados no se ven afectados.)

## Posibles errores y mitigaciones

| Situación | Comportamiento esperado |
|---|---|
| Nombre vacío | Se impide guardar; mensaje indicando que el nombre es obligatorio. |
| Valor por defecto vacío, no numérico o ≤ 0 | Se impide guardar; mensaje indicando que debe ser un monto mayor a cero. |
| No se eligió categoría | Se impide guardar; mensaje indicando que la categoría es obligatoria. |
| Gasto sin definir "es esencial" | Se impide guardar; el campo es obligatorio para gastos. |
| Categoría que no corresponde al tipo elegido | No debería poder ocurrir desde la UI (el selector se filtra por tipo); además el sistema rechaza la combinación inválida y muestra error. |
| Ingreso con "es esencial" definido | El sistema lo ignora/deja sin valor: en ingresos ese campo no aplica. |
| Cambiar el tipo con una categoría ya seleccionada (crear/editar) | La categoría seleccionada se limpia o revalida contra el nuevo tipo, para no quedar con una combinación inválida. |
| Borrar una plantilla usada en meses ya cargados | El borrado procede; los movimientos históricos se conservan intactos (snapshot) y solo pierden el vínculo con la plantilla. Se puede informar cuántos movimientos quedaron desvinculados. |
| Editar/guardar/borrar y falla la operación (error de red o servidor) | Se informa el error y no se aplica un cambio parcial; el usuario puede reintentar. |
| Editar una plantilla que otro proceso borró entretanto | Se informa que la plantilla ya no existe y se refresca el listado. |
