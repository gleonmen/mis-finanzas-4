# Reportes gráficos por caja

## Overview
Pantalla de reportes con gráficas que resume el dinero registrado: una vista
**mensual** (en qué se fue la plata ese mes, cuánto entró vs cuánto salió, cuánto de
lo gastado era esencial) y una vista **anual** (los mismos totales del año más la
evolución mes a mes). Convierte los movimientos ya cargados en respuestas visuales,
que es el objetivo final de registrar las finanzas.

## Usuario objetivo
Usuario único de la app de finanzas personales (single-user, sin auth). Ya viene
usando la app: configuró sus plantillas y viene cargando sus meses. Perfil no
técnico. Su objetivo acá no es cargar datos sino **entenderlos**: saber si le alcanzó
el mes, en qué categorías se le va la plata, y si mejora o empeora a lo largo del año.

## Contexto del problema
Hoy la app permite registrar movimientos pero no muestra nada agregado: para saber
cuánto gastó en Transporte en marzo habría que revisar los movimientos a mano. Los
datos están, pero no responden preguntas. Esta funcionalidad cierra el ciclo:
registrar → entender.

Regla de negocio que gobierna todos los cálculos: los reportes son **por caja**. Un
monto cae completo en el mes de su fecha, sin prorrateos. La periodicidad
(`frequency`) de un movimiento es solo un dato descriptivo y **no afecta ningún
cálculo**: un gasto anual de $900.000 con fecha de marzo suma $900.000 a marzo, no
$75.000 a cada mes.

## Alcance versión 1

### Incluye
- Nueva pestaña **Reportes**, junto a Plantillas y Carga mensual.
- Selector de **período**: alternar entre reporte **mensual** (mes + año) y **anual**
  (año), eligiendo cuál ver.
- **Vista mensual**, con:
  - Totales del mes: ingresos, gastos y **neto** (ingresos − gastos).
  - **Gasto por categoría**: gráfica de composición con la paleta fija por categoría.
    Muestra las **7 categorías con mayor gasto** y agrupa el resto en **"Otros"** para
    que la gráfica siga siendo legible; el detalle completo se ve en una tabla
    acompañante.
  - **Ingresos vs gastos**: comparación visual de lo que entró contra lo que salió.
  - **Esencial vs no esencial**: qué parte del gasto del mes fue esencial.
- **Vista anual**, con:
  - Totales del año: ingresos, gastos y neto.
  - **Evolución mes a mes**: ingresos, gastos y neto por cada mes del año. Se muestran
    **los 12 meses**, incluidos los que no tienen movimientos (en cero), para que la
    tendencia no engañe.
  - Gasto por categoría del año (misma lógica de top + "Otros") y esencial vs no
    esencial del año.
- Todos los montos con el formato de moneda del proyecto (COP, es-CO) y todos los
  textos en español.
- El color de cada categoría es **estable**: siempre el mismo para la misma categoría,
  en toda la app, sin reasignarse según el ranking del período.

### No incluye
- Comparar dos períodos entre sí (mes contra mes anterior, año contra año).
- Presupuestos, metas de ahorro o proyecciones.
- Exportar (PDF/Excel/CSV) o imprimir.
- Filtrar el reporte por categoría, por esencial, o por rango de fechas libre
  (solo mes completo o año completo).
- Hacer clic en una gráfica para ver el detalle de movimientos (drill-down).
- Reportes de más de un año a la vez.
- Prorrateo de montos según periodicidad (explícitamente contrario a la regla de caja).

## Comportamiento esperado

### Navegación y selección de período
1. El usuario entra a la pestaña **Reportes**. Por defecto ve el reporte **mensual del
   mes actual**.
2. Puede cambiar entre vista **mensual** y **anual**, y elegir el mes/año a consultar.
   Al cambiar la selección, el reporte se actualiza a ese período.

### Vista mensual
3. Muestra los **totales del mes**: total de ingresos, total de gastos y el **neto**.
   El neto se distingue visualmente según sea positivo (sobró) o negativo (faltó).
4. La gráfica de **gasto por categoría** muestra cuánto se gastó en cada categoría del
   mes, ordenado de mayor a menor, con las principales visibles y el resto agrupado en
   **"Otros"**. Una tabla acompañante lista **todas** las categorías con su monto y su
   porcentaje sobre el gasto total del mes.
5. La gráfica de **ingresos vs gastos** compara ambos totales del mes.
6. La gráfica de **esencial vs no esencial** reparte el gasto del mes entre lo que está
   marcado como esencial y lo que no. Los ingresos no participan de este reparto.
7. Los porcentajes mostrados suman 100% del total correspondiente.

### Vista anual
8. Muestra los **totales del año** (ingresos, gastos, neto) calculados como la suma de
   los movimientos con fecha dentro de ese año.
9. La gráfica de **evolución mes a mes** muestra los 12 meses del año en orden, con
   ingresos, gastos y neto de cada uno. Los meses sin movimientos aparecen en cero, no
   se omiten.
10. Muestra también gasto por categoría y esencial vs no esencial, con el mismo
    comportamiento que la vista mensual pero sobre el año completo.

### Consistencia de los cálculos
11. Un movimiento cuenta **completo** en el mes de su fecha; nunca se reparte entre
    meses, sin importar su periodicidad.
12. Los totales anuales coinciden con la suma de los 12 totales mensuales del mismo año.
13. Editar o borrar una plantilla **no altera** los reportes de períodos ya cargados
    (los movimientos guardan su propia foto de los datos).
14. El **ahorro cuenta como salida**: la categoría "Ahorro e Inversión" está modelada
    como gasto, así que suma al total de gastos y reduce el neto. Es coherente con la
    lógica de flujo de caja (el dinero salió de la cuenta corriente). No se lo separa
    ni se lo excluye en esta versión.

## Posibles errores y mitigaciones

| Situación | Comportamiento esperado |
|---|---|
| El período elegido no tiene ningún movimiento | Se muestra un estado vacío claro ("no hay movimientos en este período"), no gráficas vacías ni con ejes rotos. |
| El mes tiene ingresos pero ningún gasto (o al revés) | Los totales se muestran igual; la gráfica que no tiene datos indica que no hay gastos/ingresos en vez de dibujarse vacía. |
| El neto es negativo (se gastó más de lo que entró) | Se muestra el valor negativo de forma explícita y visualmente distinguible; no se oculta ni se muestra en cero. |
| Una categoría no tiene gastos en el período | Simplemente no aparece en la gráfica ni en la tabla de ese período (no se listan categorías en cero). |
| Hay más categorías con gasto que las que la gráfica muestra | Las menores se agrupan en "Otros"; la tabla acompañante siempre lista el detalle completo, de modo que ningún monto queda invisible. |
| Movimientos cuya plantilla fue borrada | Se incluyen normalmente en el reporte usando los datos guardados en el movimiento; el borrado de la plantilla no los excluye ni cambia su categoría. |
| Falla la carga de los datos del reporte (red/servidor) | Se informa el error y se ofrece reintentar; no se muestran gráficas con datos parciales o desactualizados. |
| Se elige un año/mes fuera de rango razonable | La selección se limita a valores válidos; no se rompe la vista. |
| Redondeos en los porcentajes | Los porcentajes se muestran redondeados, pero los **montos** mostrados siempre son los reales; la tabla de detalle es la fuente de verdad de las cifras. |
