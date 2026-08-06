# Concepto normalizado y top-5 conceptos

## Overview
Dos mejoras conectadas. Primero, el **concepto** de un movimiento se guarda
**normalizado** (sin espacios sobrantes y con mayúscula inicial en cada palabra), para
que quede prolijo y consistente. Segundo, un reporte nuevo muestra los **5 conceptos
que más gasto generan** en el período —sin importar la categoría—, con su categoría,
su monto y su porcentaje sobre el gasto total. La normalización es lo que permite que
el reporte agrupe bien los movimientos del mismo concepto.

## Usuario objetivo
Usuario único de la app de finanzas personales (single-user, sin auth). Ya carga sus
movimientos y mira sus reportes. Perfil no técnico. Sus objetivos: que los conceptos se
vean prolijos y uniformes sin tener que cuidar el formato al tipear, y ver de un vistazo
en qué conceptos puntuales (no solo categorías) se le va más plata.

## Contexto del problema
El concepto es texto libre, así que hoy se guarda tal cual se tipea: `"netflix"`,
`"Netflix "` y `"NETFLIX"` conviven como cosas distintas. Eso se ve desprolijo y, sobre
todo, impide agrupar: si quisiéramos ver "cuánto gasté en Netflix" sumando todos los
meses, esas variantes no se juntarían. Además, los reportes actuales resumen por
**categoría**, pero una categoría como "Entretenimiento" puede esconder que un solo
concepto (una suscripción, un gasto recurrente) pesa mucho. Ver el ranking por concepto
—cruzando categorías— destapa esos gastos puntuales grandes.

## Alcance versión 1

### Incluye
- **Normalización del concepto** al **crear** o **editar** un movimiento, y al
  **cargar un mes** desde plantillas (el concepto del movimiento se toma del nombre de
  la plantilla, ya normalizado). La normalización:
  - recorta espacios al inicio y al final,
  - colapsa espacios dobles internos a uno solo,
  - pone en **mayúscula la primera letra de cada palabra** y el resto en minúscula
    (ej.: `"netflix  hbo "` → `"Netflix Hbo"`).
- Un **reporte de top-5 conceptos de gasto** en Reportes, en la vista **mensual** y en
  la **anual**:
  - lista los **5 conceptos con mayor gasto** del período, ordenados de mayor a menor,
    **sin importar la categoría** (el ranking cruza todas las categorías);
  - por cada uno muestra el **concepto**, su **categoría**, el **monto** y el
    **porcentaje** sobre el gasto total del período;
  - una gráfica de barras (una barra por concepto, coloreada según la categoría del
    concepto) acompaña a la tabla.

### No incluye
- Normalizar los **movimientos ya existentes** de forma retroactiva (solo se normaliza
  lo que se cree o edite de ahora en más; los viejos se emparejan cuando se re-guarden).
- Normalizar el nombre de las **plantillas** (queda como está; solo se normaliza el
  concepto del movimiento).
- Preservar acrónimos en mayúscula: el title-case baja `"SOAT"` a `"Soat"` y `"IVA"` a
  `"Iva"` (costo aceptado a cambio de unificar variantes de mayúsculas).
- Top-N configurable (es fijo en 5), ni top de **ingresos** por concepto.
- Agrupar conceptos "parecidos" (typos, sinónimos): se agrupan solo los que quedan con
  el **mismo texto exacto** tras normalizar, dentro de la misma categoría.
- Hacer clic en un concepto para ver sus movimientos (drill-down).

## Comportamiento esperado

### Normalización del concepto
1. Al **crear** un movimiento, el usuario tipea el concepto como quiera; al guardar,
   queda normalizado (ej. escribe `"  luz   epm "` y en la lista aparece `"Luz Epm"`).
2. Al **editar** un movimiento y cambiar el concepto, al guardar queda normalizado.
3. Al **cargar un mes** desde plantillas, cada movimiento nace con el concepto
   normalizado.
4. La normalización no cambia el resto del movimiento (monto, categoría, fecha,
   estado).

### Reporte de top-5 conceptos
5. En Reportes, con la vista **mensual**, el usuario ve un bloque "Top conceptos de
   gasto" con hasta 5 filas: concepto, categoría, monto y % del gasto del mes.
6. En la vista **anual**, ve el mismo bloque calculado sobre el año.
7. Las filas están ordenadas por monto de mayor a menor; la primera es el concepto que
   más gasto generó en el período.
8. Un mismo concepto que aparece en dos categorías distintas se muestra como dos filas
   (una por categoría), cada una con su categoría y su monto.
9. La barra de cada concepto se colorea con el color de **su categoría** (la categoría
   Impuestos, sin color propio, se muestra en gris); el concepto se identifica por su
   **nombre** como etiqueta, no por el color.
10. Los porcentajes son sobre el **total de gastos** del período; si se sumaran los % de
    los 5, no necesariamente dan 100% (son los 5 mayores, no todo el gasto).

### Consistencia
11. El monto de un concepto en el reporte coincide con la suma de los movimientos de
    gasto de ese concepto (misma categoría) en el período.
12. La normalización es lo que hace que dos movimientos "Netflix" y "netflix" (creados
    tras esta función) cuenten como el mismo concepto en el ranking.

## Posibles errores y mitigaciones

| Situación | Comportamiento esperado |
|---|---|
| El período no tiene gastos | El bloque de top conceptos muestra un estado vacío ("no hay gastos en este período"), no una gráfica vacía. |
| Hay menos de 5 conceptos con gasto | Se muestran los que haya (1 a 4 filas); no se rellena con vacíos. |
| Un concepto queda vacío tras normalizar (todo espacios) | No debería ocurrir: el concepto es obligatorio y no vacío tras recortar; si quedara vacío, se rechaza el guardado con el mensaje de concepto obligatorio. |
| Movimientos viejos con variantes ("Netflix" y "netflix ") | Cuentan como conceptos distintos hasta que se re-guarden; es el comportamiento esperado (no hay migración retroactiva). |
| Mismo concepto en dos categorías | Se listan por separado (concepto + categoría es la unidad de agrupación); ningún monto se pierde ni se duplica. |
| Acrónimos y nombres propios (SOAT, iPhone) | Quedan en title-case (Soat, Iphone); es el costo aceptado de unificar mayúsculas. |
| Redondeo de porcentajes | Los % se muestran redondeados; los montos son los reales y son la fuente de verdad. |
