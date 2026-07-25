# Ingresos por categoría

> **Nota de decisión (durante la planificación):** la forma se cambió de **dona** a
> **barra horizontal**. Al re-validar la paleta con el skill dataviz para el caso
> pie (todos-contra-todos), dos pares de colores de ingreso no pasaban el piso de
> separación; la barra horizontal (mismo componente que el desglose de gastos) sí
> pasa, es consistente con gastos y responde igual la pregunta. El usuario aprobó el
> cambio con la evidencia a la vista.

## Overview
Un gráfico nuevo en la pestaña Reportes que muestra **de dónde vienen los ingresos**
del período: una barra horizontal con el aporte de cada categoría de ingreso (sueldo,
freelance, rentas, etc.), ordenada de mayor a menor, acompañada de una tabla con los
montos y porcentajes. Aparece tanto en la vista mensual como en la anual. Es el
simétrico del desglose de gastos que ya existe.

## Usuario objetivo
Usuario único de la app de finanzas personales (single-user, sin auth). Ya viene
cargando sus meses y mirando los reportes. Perfil no técnico. Su objetivo acá es
**entender la composición de sus ingresos**: saber de un vistazo qué fuente aporta la
mayor parte de lo que entra, y cuánto pesan las demás.

## Contexto del problema
Hoy el reporte desglosa el **gasto** por categoría, pero los ingresos aparecen solo
como un número total en las tarjetas de KPI. El usuario ve *cuánto* entró, pero no
*de dónde*. Para alguien con varias fuentes (sueldo + freelance + una renta), esa
composición es información valiosa que hoy no está en ninguna parte. Este gráfico la
expone, reutilizando el mismo período y la misma lógica de caja del resto de reportes.

## Alcance versión 1

### Incluye
- Un gráfico de **ingresos por categoría** en la pestaña Reportes, presente en la
  vista **mensual** y en la **anual**, para el período que el usuario tenga elegido.
- Forma de **barra horizontal**: una barra por cada categoría de ingreso que tuvo
  movimientos en el período, ordenada de mayor a menor, coloreada con la escala de
  color de ingreso y con el nombre de la categoría como etiqueta del eje.
- Una **tabla de detalle** debajo del gráfico con cada categoría de ingreso, su monto
  (en COP) y su porcentaje sobre el total de ingresos del período.
- Cada categoría siempre con **el mismo color** (estable, sigue a la categoría, no al
  ranking).
- Textos en español y montos en COP, como el resto de la app.

### No incluye
- Desglose de ingresos por **fuente/plantilla individual** (solo por categoría).
- Comparar la composición de ingresos entre dos períodos.
- Un desglose combinado ingresos-vs-gastos en un mismo gráfico.
- Agrupar categorías menores en "Otros" (las categorías de ingreso son pocas —hasta
  seis— y entran todas; no hace falta plegar la cola).
- Hacer clic en un gajo para ver el detalle de movimientos (drill-down).
- Cambiar la forma del desglose de **gastos** que ya existe (sigue siendo su barra).

## Comportamiento esperado

### Dónde aparece
1. En la pestaña **Reportes**, con la vista **mensual** seleccionada, el usuario ve el
   gráfico de ingresos por categoría del mes elegido, junto a los demás gráficos.
2. Al cambiar a la vista **anual**, ve el mismo gráfico pero sobre el año completo.
3. Al cambiar el período (mes o año), el gráfico se actualiza a ese período.

### Lo que muestra
4. Hay una barra por cada categoría de ingreso **con monto mayor a cero** en el
   período; las categorías de ingreso sin movimientos no aparecen.
5. La barra más larga (arriba, por el orden descendente) corresponde a la categoría
   que más aportó: eso responde "de dónde viene la mayoría de mis ingresos" a un
   vistazo.
6. La **tabla** lista todas las categorías de ingreso con monto, ordenadas de mayor a
   menor, con su porcentaje sobre el total. Los porcentajes de las categorías suman
   100%.
7. Cada categoría se identifica también por su **nombre** (en la tabla y como
   etiqueta del eje del gráfico), no solo por su color.

### Consistencia
9. El total de ingresos que muestra este gráfico coincide con el total de ingresos de
   las tarjetas de KPI del mismo período.
10. Los montos respetan la regla de caja del resto de reportes (un ingreso cuenta
    completo en el mes de su fecha; los anuales no se prorratean).

## Posibles errores y mitigaciones

| Situación | Comportamiento esperado |
|---|---|
| El período no tiene ningún ingreso | Se muestra un estado vacío claro ("no hay ingresos en este período"), no un gráfico vacío ni con ejes rotos. |
| Una categoría de ingreso no tuvo movimientos | Simplemente no aparece (ni barra ni fila); no se listan categorías en cero. |
| Todo el ingreso viene de una sola categoría | El gráfico muestra una única barra al 100%; sigue siendo legible. |
| Dos categorías con montos muy parecidos | Se distinguen por su **nombre** (etiqueta del eje) y su valor en la tabla, de modo que la lectura no depende solo del color. |
| Redondeo de porcentajes | Los porcentajes se muestran redondeados; los **montos** mostrados son los reales, y la tabla es la fuente de verdad de las cifras. |
| Falla la carga de los datos del reporte | Se informa el error y se ofrece reintentar (igual que el resto de la vista de Reportes); no se muestra un gráfico con datos parciales. |
