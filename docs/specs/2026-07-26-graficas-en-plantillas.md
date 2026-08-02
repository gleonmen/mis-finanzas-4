# Gráficas en plantillas

## Overview
Agrega gráficas a la pantalla **Plantillas** para leer de un vistazo lo que hoy está
solo en números: una **barra por categoría** (equivalente mensual) en cada sección
—Ingresos y Egresos— y un **medidor de esencial vs no esencial** en Egresos. Todo
sobre el mismo "presupuesto base mensual" que ya muestran los subtotales de la página.

## Usuario objetivo
Usuario único de la app de finanzas personales (single-user, sin auth). Ya tiene sus
plantillas cargadas, agrupadas por categoría y con subtotales. Perfil no técnico. Su
objetivo acá es **ver la forma de su presupuesto de un vistazo**: qué categorías
pesan más en lo que gana y en lo que gasta, y qué proporción de su gasto base es
esencial, sin tener que leer y comparar números fila por fila.

## Contexto del problema
La página ya calcula y muestra, en texto, el subtotal mensual de cada categoría y el
resumen de esencial/no esencial. Pero comparar categorías leyendo montos es lento: no
se ve "de un golpe" cuál es la más grande ni cuánto más pesa una que otra. Una barra
ordenada de mayor a menor responde eso al instante, y un medidor muestra la proporción
esencial/no esencial mejor que dos números sueltos.

## Alcance versión 1

### Incluye
- En la sección **Ingresos**: una **gráfica de barras** con el total por categoría de
  ingreso (equivalente mensual), ordenada de mayor a menor, ubicada arriba de la
  tabla de la sección.
- En la sección **Egresos**: una **gráfica de barras** con el total por categoría de
  gasto (equivalente mensual), ordenada de mayor a menor; y un **medidor** de gasto
  **esencial vs no esencial** (equivalente mensual). Ambos arriba de la tabla.
- Los montos son el **equivalente mensual**, idénticos a los subtotales que la página
  ya muestra (anual÷12, etc.; las plantillas de periodicidad Único no cuentan).
- Cada categoría conserva su **color** estable (la categoría Impuestos, sin color
  propio, se muestra en gris; su identidad va por la etiqueta).
- Las gráficas **no repiten** la tabla de detalle: el listado con filas y subtotales
  sigue siendo el que ya está debajo en cada sección.
- Montos en COP y textos en español.

### No incluye
- Repetir la tabla de detalle dentro/junto a la gráfica (se evita la duplicación).
- Un gráfico combinado que mezcle ingresos y egresos en el mismo eje.
- Medidor de esencial en **Ingresos** (los ingresos no tienen "esencial").
- Gráficas de movimientos reales (eso vive en Reportes; esto es sobre plantillas).
- Poder alternar el gráfico entre equivalente mensual y valor crudo, u otras
  periodicidades.
- Interacción de drill-down (clic en una barra para ver sus plantillas).
- Cambiar la forma de las gráficas de Reportes.

## Comportamiento esperado

### Ingresos
1. Arriba de la tabla de Ingresos, el usuario ve una barra horizontal con una barra
   por cada categoría de ingreso que tenga plantillas, ordenadas de mayor a menor por
   su total mensual.
2. La barra más larga (arriba) es la categoría de ingreso que más aporta al mes.
3. Cada barra está etiquetada con el nombre de la categoría, de modo que se identifica
   por nombre y no solo por color.

### Egresos
4. Arriba de la tabla de Egresos, el usuario ve una barra horizontal con una barra por
   categoría de gasto con plantillas, ordenadas de mayor a menor por su total mensual.
5. También ve un **medidor** que reparte el gasto base mensual entre **esencial** y
   **no esencial**, mostrando la proporción y ambos montos.
6. La categoría **Impuestos** aparece con su barra en **gris** (color reservado), con
   su nombre como etiqueta.

### Consistencia con los números
7. El total de cada barra coincide con el subtotal de esa categoría que la tabla de la
   misma sección muestra debajo.
8. En el medidor, esencial + no esencial coincide con el total de gasto mensual del
   resumen de la sección Egresos.
9. Al **crear, editar o borrar** una plantilla, las gráficas se actualizan igual que
   los subtotales (reflejan el cambio de inmediato).

### Secciones vacías
10. Si una sección no tiene plantillas, no se muestra su gráfica (ni el medidor); se
    mantiene el estado vacío de la sección que ya existe.

## Posibles errores y mitigaciones

| Situación | Comportamiento esperado |
|---|---|
| Una sección no tiene plantillas | No se dibuja gráfica ni medidor; se muestra el estado vacío ya existente de la sección. |
| Egresos sin ningún gasto esencial (o sin ninguno no esencial) | El medidor muestra el lado correspondiente en cero y el otro al 100%; sigue siendo legible. |
| Todas las plantillas de una categoría son de periodicidad Único | Su total mensual es 0; esa categoría no aporta barra (o aporta una barra en cero), consistente con su subtotal $0 de la tabla. |
| La categoría Impuestos comparte el gris con otras marcas neutras | Se distingue por su etiqueta/nombre en la barra; la lectura no depende del color. |
| Montos con decimales al normalizar a mensual | Se muestran redondeados al formato COP, igual que los subtotales; la tabla sigue siendo la fuente de verdad de las cifras exactas. |
| Muchas categorías de gasto (hasta 9) | La barra las muestra todas ordenadas por monto; al ser barras con etiqueta no hay límite de color como en una torta (cada una va rotulada). |
