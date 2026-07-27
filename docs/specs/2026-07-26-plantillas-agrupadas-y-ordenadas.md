# Plantillas agrupadas y ordenadas

## Overview
Cambio en la pantalla **Plantillas** para que la lista sea más fácil de leer:
separa los **ingresos** de los **egresos** en dos secciones con su propio título, y
muestra cada grupo con un orden fijo y predecible (por categoría, luego por si el
gasto es esencial, luego por valor de mayor a menor). Es una mejora de presentación:
no cambia qué se puede hacer con las plantillas, solo cómo se ven.

## Usuario objetivo
Usuario único de la app de finanzas personales (single-user, sin auth). Ya tiene sus
plantillas cargadas y las administra desde esta pantalla. Perfil no técnico. Su
objetivo acá es **encontrar rápido una plantilla** y entender de un vistazo cómo se
reparte lo que gana y lo que gasta, sin tener que barrer una lista mezclada y en
orden de creación.

## Contexto del problema
Hoy la pantalla de Plantillas es una sola tabla con todo junto: ingresos y egresos
mezclados, y dentro, en orden de creación (la última que creaste queda al final, sin
relación con su categoría ni su monto). A medida que se acumulan plantillas, cuesta
ubicar una, y no hay forma de ver "todos mis gastos de Transporte juntos" o "cuáles
son mis gastos más grandes". Agrupar por tipo y ordenar por categoría/valor vuelve la
lista escaneable.

## Alcance versión 1

### Incluye
- La pantalla Plantillas muestra **dos secciones separadas**, cada una con su título:
  **Ingresos** y **Egresos**.
- Dentro de **Egresos**, las plantillas se ordenan por: **categoría** (en el orden
  canónico del catálogo, el mismo que usan el selector del formulario y los colores),
  luego **esenciales primero** (los marcados como esencial antes que los no
  esenciales), luego por **valor por defecto de mayor a menor**.
- Dentro de **Ingresos**, las plantillas se ordenan por: **categoría** (mismo orden
  canónico), luego por **valor por defecto de mayor a menor**. (Los ingresos no tienen
  "esencial", así que esa clave no aplica.)
- El orden es **fijo**: al crear o editar una plantilla, aparece automáticamente en su
  lugar según esas reglas, sin que el usuario tenga que ordenar nada.
- Cada sección tiene su propio **estado vacío** cuando no hay plantillas de ese tipo.
- Se conservan las columnas y acciones actuales de cada fila (categoría, concepto,
  esencial, valor, periodicidad, Editar, Borrar).

### No incluye
- **Ordenar haciendo clic en las columnas** (encabezados clicables, cambiar de
  ascendente a descendente): el orden es fijo, no interactivo.
- Cambiar el criterio de orden desde la UI, ni recordar preferencias de orden.
- Cambiar el CRUD de plantillas (crear/editar/borrar siguen igual).
- Cambiar el orden en **otras** pantallas que listan plantillas (p. ej. la grilla de
  carga mensual): este cambio es solo de la pantalla Plantillas.
- Colapsar/expandir las secciones, buscar o filtrar plantillas.
- Cualquier cambio de backend o de datos.

## Comportamiento esperado

### Estructura de la pantalla
1. Al abrir **Plantillas**, el usuario ve dos secciones, una debajo de la otra:
   primero **Ingresos**, luego **Egresos**, cada una con su encabezado visible.
2. El botón "Nueva plantilla" sigue disponible como hasta ahora.

### Orden dentro de Egresos
3. Las plantillas de gasto aparecen agrupadas por categoría, en el orden canónico del
   catálogo (todas las de una categoría juntas antes de pasar a la siguiente).
4. Dentro de una misma categoría, las plantillas **esenciales** van antes que las **no
   esenciales**.
5. Dentro del mismo grupo (misma categoría y misma condición de esencial), se ordenan
   por **valor por defecto de mayor a menor**.

### Orden dentro de Ingresos
6. Las plantillas de ingreso aparecen agrupadas por categoría, en el orden canónico
   del catálogo.
7. Dentro de una misma categoría, se ordenan por **valor por defecto de mayor a
   menor**.

### Al crear / editar
8. Cuando el usuario crea una plantilla nueva, al cerrarse el formulario la lista se
   muestra ya ordenada y la nueva plantilla aparece en la posición que le corresponde
   según su tipo, categoría, esencialidad y valor (no al final).
9. Cuando el usuario edita una plantilla y cambia algo que afecta el orden (categoría,
   esencial o valor), al guardar la plantilla se reubica en la posición correcta.
10. El tipo de una plantilla **sí se puede editar** (a diferencia de los movimientos,
    una plantilla no tiene historial que proteger). Si al editar se cambia el tipo de
    ingreso a gasto o viceversa, al guardar la plantilla **desaparece de una sección y
    aparece en la otra**, en la posición que le corresponde por su nuevo orden.

### Secciones vacías
11. Si no hay ninguna plantilla de ingreso, la sección **Ingresos** muestra un estado
    vacío que lo indica; lo mismo para **Egresos**. Si no hay ninguna plantilla en
    absoluto, ambas secciones muestran su estado vacío.

## Posibles errores y mitigaciones

| Situación | Comportamiento esperado |
|---|---|
| No hay plantillas de un tipo | La sección correspondiente muestra su estado vacío; la otra sección se muestra normal. |
| No hay ninguna plantilla | Ambas secciones muestran su estado vacío; el botón "Nueva plantilla" sigue disponible. |
| Dos plantillas con misma categoría, misma esencialidad y mismo valor | Empatan en las claves de orden; se muestran ambas en un orden estable (no se pierde ni se duplica ninguna). El empate no rompe la vista. |
| Una categoría sin plantillas | Simplemente no aparece como grupo; no se muestran encabezados de categoría vacíos. |
| Falla la carga de las plantillas | Se mantiene el manejo de error actual de la pantalla (mensaje de error); las secciones no se dibujan a medias. |
| Valor por defecto igual en cero o ausente | No debería ocurrir (el CRUD exige valor mayor a cero); si existiera, se ordena como el menor valor sin romper la lista. |
