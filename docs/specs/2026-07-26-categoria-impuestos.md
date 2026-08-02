# Categoría Impuestos

## Overview
Agrega una categoría fija nueva, **Impuestos**, al catálogo de categorías de **gasto**.
A partir de ahí, el usuario puede crear plantillas y movimientos bajo esa categoría, y
verla en los reportes de gasto. El catálogo pasa de 14 a 15 categorías (6 ingreso + 9
gasto).

## Usuario objetivo
Usuario único de la app de finanzas personales (single-user, sin auth). Registra sus
finanzas y quiere clasificar por separado lo que paga en impuestos (predial, renta,
vehículo, etc.), en vez de mezclarlo con otras categorías.

## Contexto del problema
Hoy las categorías son un catálogo fijo de 14 y no incluye Impuestos: los pagos de
impuestos hay que meterlos en una categoría que no les corresponde (p. ej. Deudas y
Finanzas o Transporte), lo que ensucia los reportes por categoría. Tener una categoría
propia deja ver cuánto pesa el rubro de impuestos por sí solo.

## Alcance versión 1

### Incluye
- Una categoría fija nueva **Impuestos** de tipo **gasto**, disponible en toda la app
  como cualquier otra categoría de gasto.
- Al crear o editar una **plantilla** o un **movimiento** de tipo gasto, "Impuestos"
  aparece como opción en el selector de categoría.
- Los **reportes de gasto** por categoría contabilizan Impuestos como una categoría
  más (participa del "top 7 + Otros" según su monto).
- En la vista de **Plantillas** agrupada, las plantillas de Impuestos forman su propio
  grupo (con su subtotal), en la posición que le corresponda por el orden canónico.
- El **color** de Impuestos es el **gris neutro** de la app (el mismo que usa la cola
  "Otros"): decisión tomada para no introducir un noveno color que no pasa la
  validación de accesibilidad. Su identidad se apoya en el **nombre** de la categoría,
  no en el color.

### No incluye
- Impuestos como categoría de **ingreso** (las devoluciones de impuestos siguen
  cayendo en "Otros Ingresos").
- Un color propio distintivo para Impuestos (usa el gris neutro por decisión).
- Reordenar, renombrar o borrar otras categorías del catálogo.
- Hacer el catálogo de categorías editable por el usuario (sigue siendo fijo).
- Migrar automáticamente movimientos/plantillas viejos a la nueva categoría.

## Comportamiento esperado

### Disponibilidad de la categoría
1. En el formulario de **plantilla** o de **movimiento**, con el tipo en **gasto**, el
   selector de categoría incluye **Impuestos** junto a las demás categorías de gasto.
2. Con el tipo en **ingreso**, Impuestos **no** aparece (es una categoría de gasto).
3. El usuario puede crear una plantilla o un movimiento con categoría Impuestos y
   guardarlo normalmente; se comporta como cualquier otra categoría de gasto.

### En las pantallas
4. En **Plantillas**, las plantillas de Impuestos aparecen agrupadas bajo su categoría,
   con su subtotal equivalente-mensual, dentro de la sección Egresos.
5. En **Reportes**, el gasto en Impuestos de un período se suma a su categoría; si está
   entre las mayores, aparece como su propia barra (en gris) y, si no, se pliega en
   "Otros" como cualquier categoría.
6. En cualquier lugar donde se muestre el color de la categoría (punto de color, barra),
   Impuestos se ve en **gris neutro**, siempre acompañado de su nombre.

### Persistencia
7. Los movimientos creados con categoría Impuestos guardan su categoría como parte de
   su foto (snapshot), así que aunque el catálogo cambiara, esos movimientos siguen
   mostrando "Impuestos".

## Posibles errores y mitigaciones

| Situación | Comportamiento esperado |
|---|---|
| La base de datos ya existía antes de agregar Impuestos | Las migraciones solo corren al inicializar la base por primera vez, así que en una base ya creada la categoría se agrega aplicando el alta puntual; en bases nuevas, la migración la siembra sola. En ambos casos, el resultado es que Impuestos queda disponible. |
| Intentar crear un gasto con Impuestos pero el catálogo no la tiene todavía | No debería ocurrir una vez aplicada; si faltara, el selector simplemente no la ofrece y no se puede elegir (no hay estado a medias). |
| Elegir Impuestos en un movimiento/plantilla de ingreso | No es posible: Impuestos es de gasto y el selector filtra por tipo; el sistema rechaza la combinación categoría↔tipo inválida. |
| Impuestos coincide en gris con la cola "Otros" en un gráfico | Ambos se distinguen por su **etiqueta/nombre** en el eje y en la tabla; la lectura no depende del color. Es el costo aceptado de no inventar un color nuevo. |
| Reportes históricos anteriores a la categoría | No cambian: los movimientos viejos conservan su categoría original (snapshot); Impuestos solo afecta a lo que se registre con esa categoría de ahora en más. |
