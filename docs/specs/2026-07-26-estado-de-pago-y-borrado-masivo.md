# Estado de pago y borrado masivo

## Overview
Tres mejoras alrededor de los movimientos: (1) un **estado de pago** en cada movimiento
—pagado o pendiente— que se elige al crearlo y se puede cambiar; (2) un botón para
**borrar todos los movimientos de un mes** de una vez; y (3) en Reportes, **dos
medidores** que muestran, por mes, cuánto de los gastos ya se pagó y cuánto de los
ingresos ya se recibió. Sirve para llevar el control de lo que falta pagar y cobrar.

## Usuario objetivo
Usuario único de la app de finanzas personales (single-user, sin auth). Ya carga sus
meses (desde plantillas o sueltos) y mira sus reportes. Perfil no técnico. Su objetivo
acá es **saber qué le falta pagar y qué le falta cobrar** en el mes, marcar cosas como
pagadas a medida que ocurren, y poder rehacer un mes entero rápido cuando lo cargó mal.

## Contexto del problema
Hoy un movimiento no distingue entre "esto ya lo pagué" y "esto lo espero pagar": una
vez cargado, es un hecho consumado. Pero al planear el mes, la mayoría de los
movimientos son cosas que **todavía no ocurrieron** (el arriendo que pagaré, el sueldo
que cobraré). Sin un estado, no hay forma de ver de un vistazo cuánto falta pagar o
cobrar. Además, corregir un mes mal cargado hoy obliga a borrar los movimientos **uno
por uno** antes de poder recargarlo; borrar todos de una vez lo vuelve inmediato.

Regla que se mantiene: el estado de pago **no** forma parte de la foto (snapshot) que el
movimiento guarda del template — es un estado propio del movimiento, que cambia con el
tiempo.

## Alcance versión 1

### Incluye
- **Estado de pago** en cada movimiento, con dos valores: **pagado** o **pendiente**.
  - En **gastos** se muestra como "Pagado" / "Pendiente de pago".
  - En **ingresos** se muestra como "Recibido" / "Pendiente de cobro".
- Al **crear** un movimiento (suelto) o al **cargar un mes** desde plantillas, el
  estado nace en **pendiente**. En el alta suelta el usuario puede elegir el estado.
- Al **editar** un movimiento, el usuario puede cambiar su estado.
- En la **lista de Movimientos**, cada fila muestra su estado de pago.
- **Borrar todos los movimientos del mes**: en el tab Movimientos, con un mes elegido
  que tenga movimientos, un botón "Borrar todos" pide confirmación indicando **cuántos**
  se borrarán. Al confirmar, se borran todos los de ese mes y el mes queda libre para
  volver a cargarse desde plantillas.
- En **Reportes**, vista **mensual**, dos medidores:
  - Gastos: **pagado vs pendiente de pago** (cuánto del gasto del mes ya se pagó).
  - Ingresos: **recibido vs pendiente de cobro** (cuánto del ingreso del mes ya entró).
- Los montos son los **reales** del movimiento (por caja), como el resto de Reportes.
- Los movimientos que ya existían antes de esta función quedan marcados como
  **pagados/recibidos** (se asumen ya asentados).

### No incluye
- Los medidores de pago en la vista **anual** (solo mensual).
- Estados de pago intermedios (parcial, vencido, etc.): solo pagado o pendiente.
- Fechas de vencimiento, recordatorios o alertas de lo pendiente.
- Filtrar la lista de Movimientos por estado (se muestra la columna, no el filtro).
- Marcar como pagado/pendiente de forma masiva (se cambia movimiento por movimiento
  al editar).
- Borrado masivo en otras pantallas (solo en Movimientos, por mes).
- Cambiar el comportamiento de la carga mensual más allá de que sus movimientos nacen
  pendientes.

## Comportamiento esperado

### Estado de pago en el alta y edición
1. En el formulario de **nuevo movimiento**, hay un control de estado con las dos
   opciones, rotuladas según el tipo elegido (gasto: pagado/pendiente de pago; ingreso:
   recibido/pendiente de cobro). Por defecto viene **pendiente**.
2. Al **cargar un mes** desde plantillas, todos los movimientos creados quedan
   **pendientes**.
3. Al **editar** un movimiento, el usuario ve su estado actual y puede cambiarlo; al
   guardar, queda con el nuevo estado.

### En la lista de Movimientos
4. Cada fila muestra su estado de pago con el rótulo correspondiente a su tipo.
5. Los totales del mes (ingresos/gastos/neto) que ya muestra la lista no cambian por el
   estado (siguen sumando todos los movimientos).

### Borrar todos los movimientos del mes
6. Con un mes elegido que **tiene** movimientos, aparece un botón para borrarlos todos.
7. Al pulsarlo, se pide **confirmación** indicando cuántos movimientos se van a borrar.
8. Al confirmar, desaparecen todos los movimientos de ese mes; la lista queda vacía y
   los totales en cero.
9. Tras borrarlos, ese mes vuelve a poder **cargarse desde plantillas** (el bloqueo por
   "mes ya cargado" se libera).
10. Si el usuario cancela la confirmación, no se borra nada.
11. Si el mes no tiene movimientos, el botón no está disponible.

### Reportes (vista mensual)
12. En la vista mensual, además de lo que ya hay, se muestran dos medidores:
    - uno reparte el **gasto del mes** entre pagado y pendiente de pago;
    - otro reparte el **ingreso del mes** entre recibido y pendiente de cobro.
13. Cada medidor muestra la proporción y ambos montos (pagado/pendiente).
14. Si el mes no tiene gastos (o no tiene ingresos), el medidor correspondiente indica
    que no hay datos, en vez de dibujarse vacío.
15. La suma de pagado + pendiente de cada medidor coincide con el total de gastos (o de
    ingresos) del mes que muestran las tarjetas de KPI.

## Posibles errores y mitigaciones

| Situación | Comportamiento esperado |
|---|---|
| Base de datos ya existente | El estado de pago se agrega con un valor por defecto y los movimientos previos quedan como pagados/recibidos; en bases nuevas la estructura se crea sola. En ambos casos, todo movimiento tiene un estado válido. |
| Crear/editar sin elegir estado | No puede quedar sin estado: si no se toca, queda **pendiente** (el valor por defecto). |
| Borrar todos en un mes sin movimientos | El botón no está disponible; no hay nada que borrar. |
| Borrado masivo a mitad de camino falla | La operación es atómica: o se borran todos o ninguno; se informa el error y el mes queda como estaba. |
| Confirmar el borrado por accidente | Requiere una confirmación explícita que dice cuántos se borran; es una acción deliberada. No hay "deshacer" (igual que el borrado individual). |
| Un mes con solo ingresos (o solo gastos) en el reporte | El medidor del tipo ausente indica "no hay datos"; el otro se muestra normal. |
| Estado de pago y snapshot | El estado es propio del movimiento, no del template; editar o borrar un template no lo afecta, y el estado no altera los reportes por categoría ni los totales (que suman todo). |
| Montos con pendiente en cero (todo pagado) o pagado en cero (todo pendiente) | El medidor muestra un lado al 100% y el otro en cero; sigue siendo legible. |
