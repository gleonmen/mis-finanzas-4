# Gestión de movimientos

## Overview
Pantalla para administrar los movimientos ya registrados: verlos mes a mes,
corregir uno que quedó mal, borrarlo, y registrar un movimiento suelto que no
viene de ninguna plantilla. Cierra el ciclo de la app — hasta ahora los
movimientos solo se podían crear en lote desde la carga mensual y, una vez
guardados, no había forma de tocarlos.

## Usuario objetivo
Usuario único de la app de finanzas personales (single-user, sin auth). Ya
configuró sus plantillas y viene cargando sus meses. Perfil no técnico. Su
objetivo acá es **mantener la exactitud de sus datos**: arreglar el monto que
tipeó mal, borrar el gasto que en realidad no ocurrió, y anotar el gasto
inesperado que no tiene plantilla.

## Contexto del problema
Hoy los movimientos son de solo escritura: se crean en bloque al cargar un mes y
después quedan congelados. Eso deja dos problemas concretos:

1. **Un mes mal cargado no se puede arreglar.** Si al confirmar quedó un monto
   equivocado, no hay forma de editarlo, y tampoco de volver a cargar el mes
   (la carga se bloquea cuando el mes ya tiene movimientos). El usuario queda sin
   salida desde la aplicación.
2. **No se puede registrar lo inesperado.** Todo movimiento debe venir de una
   plantilla, así que un gasto puntual (una multa, una urgencia médica) obliga a
   crear una plantilla que no se va a volver a usar.

En una app cuyo valor depende de que los números sean correctos, no poder
corregirlos es la carencia más grave que queda.

## Alcance versión 1

### Incluye
- Nueva pestaña **Movimientos**, junto a Plantillas, Carga mensual y Reportes.
- **Filtro por mes**: se elige un mes y se ven los movimientos de ese mes.
- **Listar** los movimientos del mes, mostrando tipo, categoría, concepto, si es
  esencial, valor y fecha; ordenados por fecha.
- **Crear** un movimiento suelto (sin plantilla), eligiendo tipo, categoría,
  concepto, si es esencial (solo en gastos), valor y fecha.
- **Editar** un movimiento existente: valor, fecha, concepto, categoría y si es
  esencial.
- **Borrar** un movimiento, con confirmación previa. El borrado es definitivo.
- Totales del mes visible (ingresos, gastos y neto) para dar contexto mientras se
  corrige.
- Moneda en COP y textos en español, como el resto de la app.

### No incluye
- **Cambiar el tipo** (ingreso ↔ gasto) de un movimiento ya creado. El tipo se
  define al crearlo y después es inmutable; para cambiarlo se borra y se crea de
  nuevo.
- Editar o crear **categorías** (siguen siendo fijas).
- Deshacer un borrado, o papelera.
- Edición masiva (cambiar varios movimientos a la vez) o borrado múltiple.
- Editar movimientos directamente desde la grilla de la carga mensual o desde las
  gráficas de Reportes (drill-down).
- Buscar o filtrar por algo que no sea el mes (por categoría, por texto, por rango
  de fechas libre).
- Adjuntar comprobantes, notas o etiquetas.
- Vincular o revincular un movimiento a una plantilla.

## Comportamiento esperado

### Navegación y filtro
1. El usuario entra a la pestaña **Movimientos** y ve, por defecto, los del **mes
   actual**.
2. Cambia el mes con el selector y la lista se actualiza a ese mes.
3. Se muestran los totales del mes (ingresos, gastos, neto) junto a la lista.
4. Si el mes elegido no tiene movimientos, se muestra un estado vacío que invita a
   crear uno.

### Listar
5. Cada fila muestra: tipo (ingreso/gasto), categoría en español, concepto, si es
   esencial (solo aplica a gastos), valor en formato COP y fecha. Las filas se
   ordenan por fecha.
6. Cada fila ofrece **Editar** y **Borrar**.

### Crear un movimiento suelto
7. El usuario pulsa "Nuevo movimiento" y se abre un formulario.
8. Elige el **tipo** (ingreso o gasto). Al elegirlo, el selector de **categoría**
   se filtra para mostrar solo las de ese tipo.
9. Si el tipo es **gasto**, aparece el control **es esencial** (obligatorio). Si es
   **ingreso**, ese control no se muestra.
10. Completa concepto, valor (mayor a cero) y fecha. La fecha es libre: puede
    quedar fuera del mes que está filtrando.
11. Al guardar, el movimiento se crea. Si su fecha cae en el mes filtrado, aparece
    en la lista; si no, se avisa que quedó registrado en otro mes.

### Editar
12. Desde una fila, el usuario elige "Editar" y se abre el mismo formulario
    precargado.
13. Puede cambiar **valor, fecha, concepto, categoría y si es esencial**. El
    **tipo se muestra pero no se puede cambiar**, y por eso las categorías
    disponibles siguen siendo las de ese tipo.
14. Al guardar, la lista refleja los nuevos valores y los totales del mes se
    recalculan.
15. Editar un movimiento **no modifica la plantilla** de la que salió, ni al
    revés: son datos independientes.

### Borrar
16. Desde una fila, el usuario elige "Borrar" y se le pide confirmación explícita.
17. Al confirmar, el movimiento desaparece de la lista y los totales se recalculan.
    Si cancela, no pasa nada.

### Relación con la carga mensual
18. **Borrar destraba la carga**: si el usuario borra todos los movimientos de un
    mes, ese mes vuelve a estar vacío y la carga mensual se puede ejecutar de
    nuevo. Ésta es la vía para rehacer un mes mal cargado.
19. **Crear bloquea la carga**: si el usuario agrega un movimiento suelto a un mes
    que estaba vacío, ese mes pasa a tener movimientos y la carga mensual quedará
    bloqueada para él. Es coherente con la regla existente, pero conviene que el
    usuario lo entienda, así que se le advierte al respecto.

### Relación con los reportes
20. Cualquier alta, edición o borrado se refleja en los reportes del período
    correspondiente la próxima vez que se consulten.

## Posibles errores y mitigaciones

| Situación | Comportamiento esperado |
|---|---|
| Concepto vacío | Se impide guardar; mensaje indicando que es obligatorio. |
| Valor vacío, no numérico o ≤ 0 | Se impide guardar; mensaje indicando que debe ser un monto mayor a cero. |
| Fecha vacía o inválida | Se impide guardar; la fecha es obligatoria. |
| No se eligió categoría | Se impide guardar; la categoría es obligatoria. |
| Gasto sin definir "es esencial" | Se impide guardar; el campo es obligatorio para gastos. |
| Categoría que no corresponde al tipo | No debería ocurrir desde la UI (el selector se filtra por tipo); además el sistema rechaza la combinación y muestra el error. |
| Ingreso con "es esencial" definido | El sistema lo deja sin valor: en ingresos ese campo no aplica. |
| Se guarda un movimiento con fecha de otro mes | Se acepta (la fecha es libre) y se informa que quedó registrado en ese otro mes, para que el usuario no crea que se perdió. |
| Editar o borrar un movimiento que ya no existe | Se informa que el movimiento ya no está disponible y se refresca la lista. |
| Falla la operación (red o servidor) | Se informa el error y no se aplica un cambio parcial; el usuario puede reintentar. Los totales no se actualizan hasta que la operación tenga éxito. |
| Agregar un movimiento a un mes vacío y luego intentar la carga mensual | La carga se bloquea (regla vigente). Se advierte al usuario al crear el movimiento para que la consecuencia no lo tome por sorpresa. |
| Borrar un movimiento que vino de una plantilla ya borrada | Se borra normalmente; no depende de la plantilla para existir. |
