# Totales en plantillas

## Overview
Agrega a la pantalla **Plantillas** una lectura de "cuánto suman" las plantillas:
un **subtotal por cada categoría** y un **resumen por sección**. Como las plantillas
tienen distintas periodicidades (mensual, anual, etc.), todos los totales se expresan
como **equivalente mensual** para que sean comparables. En Egresos el resumen separa
lo **esencial** de lo **no esencial**; en Ingresos muestra solo el total. Es una vista
de planeación —un "presupuesto base mensual"— sobre los valores por defecto de las
plantillas.

## Usuario objetivo
Usuario único de la app de finanzas personales (single-user, sin auth). Ya tiene sus
plantillas cargadas y las ve agrupadas por tipo y categoría. Perfil no técnico. Su
objetivo acá es **dimensionar su presupuesto base**: cuánto pesa cada categoría al
mes, cuánto suma en total lo que gana y lo que gasta, y qué parte de su gasto mensual
es esencial (no recortable) frente a lo prescindible.

## Contexto del problema
Hoy Plantillas lista cada plantilla con su valor por defecto, pero no suma nada: el
usuario no ve cuánto representa una categoría entera ni cuánto es su gasto base
mensual. Y como cada plantilla puede tener una periodicidad distinta, sumar los
montos "tal cual" mezclaría un gasto anual con uno mensual y daría un número
engañoso. Para que los totales sean útiles y comparables, hay que llevarlos a una
base común: el equivalente mensual.

Nota de dominio: esto **no** contradice la regla de "reportes por caja sin prorrateo".
Esa regla aplica a los reportes de **movimientos reales**. Acá se trata de una vista
de **planeación** sobre los montos por defecto de las plantillas, donde normalizar a
mensual es lo que la vuelve significativa.

## Alcance versión 1

### Incluye
- **Subtotal por categoría**: al final de cada grupo de categoría (dentro de cada
  sección), una fila destacada con el **total equivalente mensual** de las plantillas
  de esa categoría.
- **Resumen de la sección Egresos**: total **esencial** por mes, total **no esencial**
  por mes, y **total** por mes (esencial + no esencial).
- **Resumen de la sección Ingresos**: **total** por mes (sin corte esencial, que en
  ingresos no aplica).
- **Equivalente mensual**: cada valor por defecto se normaliza a mensual según su
  periodicidad —mensual ÷1, bimestral ÷2, trimestral ÷3, semestral ÷6, anual ÷12—.
  Las plantillas de periodicidad **Único** se **excluyen** de estos totales (un gasto
  único no es un costo mensual recurrente).
- **Rótulo claro**: todos los totales y subtotales se muestran indicando que son
  **equivalente mensual** (p. ej. "/mes"), porque no coinciden con la suma directa de
  los montos visibles en las filas.
- Las **filas de plantilla no cambian**: siguen mostrando su valor por defecto real y
  su periodicidad; solo se agregan filas de subtotal y el resumen.
- Todos los montos en COP y textos en español.

### No incluye
- Sumar los montos "tal cual" sin normalizar (se descartó por engañoso).
- Incluir las plantillas de periodicidad **Único** en los totales mensuales.
- Un total anualizado, o poder alternar entre vista mensual/anual de los totales.
- Totales que crucen ingresos y egresos (p. ej. un "neto" de plantillas).
- Subtotales de esencial/no esencial **por categoría** (el corte esencial va solo a
  nivel de la sección Egresos).
- Cualquier cambio en el CRUD, en el orden de las plantillas, o en el backend.
- Totales de movimientos reales (eso ya vive en Reportes).

## Comportamiento esperado

### Subtotal por categoría
1. Dentro de cada sección (Ingresos y Egresos), al terminar las plantillas de una
   categoría, aparece una fila de **subtotal** con el nombre de la categoría (o una
   marca equivalente) y su **total equivalente mensual**.
2. El subtotal de una categoría es la suma de los equivalentes mensuales de sus
   plantillas (excluyendo las de periodicidad Único).
3. La fila de subtotal se distingue visualmente de las filas de plantilla y **no**
   tiene acciones (Editar/Borrar).

### Resumen de sección
4. La sección **Egresos** muestra un resumen con: **total esencial /mes**, **total no
   esencial /mes** y **total /mes**. El total es la suma de los otros dos.
5. La sección **Ingresos** muestra un resumen con el **total /mes**.
6. El total /mes de una sección coincide con la suma de los subtotales por categoría
   de esa sección.
7. En Egresos, la suma de todos los subtotales de categoría coincide con el total /mes
   del resumen (esencial + no esencial).

### Consistencia y actualización
8. Al **crear, editar o borrar** una plantilla, los subtotales y el resumen se
   recalculan automáticamente para reflejar el cambio.
9. Si se edita el **valor**, la **periodicidad**, la **categoría**, el **tipo** o el
   **esencial** de una plantilla, los totales afectados cambian en consecuencia.

### Interpretación para el usuario
10. Queda claro (por el rótulo) que los totales son un **equivalente mensual**: por
    ejemplo, un SOAT anual de $900.000 contribuye $75.000 al total /mes, aunque su
    fila siga mostrando $900.000 (anual).

## Posibles errores y mitigaciones

| Situación | Comportamiento esperado |
|---|---|
| Una categoría solo tiene plantillas de periodicidad Único | Sus plantillas se listan igual (son válidas), y su fila de subtotal muestra **$0 /mes** (todas excluidas del equivalente mensual). No se esconde la categoría. |
| Una sección no tiene plantillas | No hay subtotales ni resumen que mostrar; se mantiene el estado vacío de la sección ya existente. |
| Todas las plantillas de gasto son esenciales (o todas no esenciales) | El resumen muestra el otro total en $0 /mes; el total /mes sigue siendo correcto. |
| Periodicidad no contemplada en el mapa de normalización | No debería ocurrir (las periodicidades son un conjunto fijo). Si apareciera una desconocida, esa plantilla se trata como mensual (÷1) para no perder su monto, y no se rompe el total. |
| Valores que producen decimales al dividir (p. ej. anual no divisible por 12) | El equivalente mensual se muestra redondeado al formato de moneda del proyecto; el usuario ve un monto limpio en COP. |
| Diferencia por redondeo entre la suma de subtotales y el total de la sección | Los totales se calculan sobre los montos exactos y se redondean solo al mostrarse, para minimizar descuadres visibles. |
