# Carga mensual de movimientos desde templates

## Overview
Funcionalidad para registrar los movimientos de un mes de forma rápida: el usuario
elige un mes y el sistema le precarga, en una grilla editable, un renglón por cada
template configurado (ingresos y gastos) con su valor y periodicidad por defecto.
El usuario ajusta valores y fechas, descarta lo que no aplique ese mes y confirma
todo de una sola vez. El objetivo es pasar de "una plantilla mensual repetida" a
"los movimientos reales del mes" en un solo paso, sin cargar cada movimiento a mano.

## Usuario objetivo
Usuario único de la app de finanzas personales (single-user, sin auth). Es la misma
persona que administra sus finanzas: ya configuró sus templates (sus "tipos"
habituales de ingreso y gasto con montos y periodicidad por defecto) y ahora, mes a
mes, necesita instanciar esos movimientos con los valores reales de ese mes. Perfil
no técnico; busca velocidad y no volver a tipear lo mismo cada mes.

## Contexto del problema
Los templates definen los movimientos recurrentes esperados, pero no son los datos
reales: cada mes los montos varían (la factura de luz no es idéntica), algunas fechas
cambian y a veces un movimiento no aplica. Sin esta funcionalidad, el usuario tendría
que crear cada transacción del mes una por una, reescribiendo categoría, nombre y
tipo que ya viven en el template — tedioso y propenso a errores. La necesidad es
**precargar** el mes desde los templates y solo tocar lo que cambió.

Además, las transactions guardan un **snapshot** de los datos del template al momento
de crearse, para que editar o borrar un template más adelante no altere los reportes
históricos de meses ya cargados.

## Alcance versión 1

### Incluye
- Selección de un mes/año objetivo para la carga.
- Precarga en una grilla editable de **todos** los templates existentes (INCOME y
  EXPENSE) con:
  - valor inicial = `default_amount` del template,
  - periodicidad inicial = `frequency` del template,
  - fecha inicial = **día 1 del mes elegido**.
- Edición local (sin persistir) de cada renglón: cambiar el **valor** y la **fecha**.
- Descartar renglones que no apliquen ese mes (quitarlos del borrador antes de
  confirmar).
- Confirmación en un solo paso que crea todas las transacciones del borrador de forma
  atómica (o todas, o ninguna).
- Cada transacción creada guarda un **snapshot** de `type`, `category`, `name`,
  `is_essential` y `frequency` tomado del template.
- Guard de "mes ya cargado" **por presencia**: si el mes elegido ya tiene
  transacciones, se avisa al usuario y no se realiza la carga (no se duplica).
- El slice incluye lo mínimo de fundaciones para que esto funcione punta a punta:
  base de datos, categorías fijas sembradas, gestión de templates y de transactions.

### No incluye
- Editar en la grilla campos distintos de valor y fecha (categoría, nombre, tipo,
  is_essential o periodicidad no se editan aquí; vienen fijos del template).
- Selección con checkboxes de qué templates incluir (en v1 entran todos y el usuario
  descarta renglones).
- Recargar/mergear un mes que ya tiene movimientos (agregar solo los faltantes,
  reemplazar, etc.): en v1 simplemente se bloquea con aviso.
- Agregar renglones nuevos que no provengan de un template durante la carga mensual.
- Reportes, gráficas y demás pantallas del MVP no necesarias para este flujo.
- Edición o borrado de transacciones ya confirmadas desde esta pantalla (se maneja
  fuera de este flujo).

## Comportamiento esperado

### Flujo principal (feliz)
1. El usuario entra a la carga mensual y elige un **mes y año** (ej. Julio 2026).
2. El sistema verifica que ese mes no tenga transacciones cargadas. Al estar vacío,
   muestra una **grilla** con un renglón por cada template existente.
3. Cada renglón muestra, de forma no editable, el **tipo** (ingreso/gasto), la
   **categoría** y el **nombre** del template; y de forma editable, el **valor**
   (precargado con `default_amount`) y la **fecha** (precargada con el día 1 del mes).
   La periodicidad viaja con el renglón pero no es foco de edición en v1.
4. El usuario ajusta los **valores** de los renglones que cambian respecto del default.
5. El usuario ajusta las **fechas** que correspondan; toda fecha debe caer dentro del
   mes seleccionado.
6. El usuario **descarta** los renglones que no apliquen ese mes; desaparecen del
   borrador.
7. El usuario presiona **Confirmar**. El sistema crea todas las transacciones del
   borrador de una sola vez, cada una con su snapshot, y muestra confirmación de que
   el mes quedó cargado.
8. Tras confirmar, si el usuario vuelve a intentar cargar ese mismo mes, el sistema
   se lo impide (ver guard más abajo).

### Variantes relevantes
- **Descartar todos los renglones**: si el borrador queda vacío, Confirmar no crea
  nada y el sistema lo indica (no hay nada que cargar).
- **No modificar nada**: si el usuario confirma sin editar, se crean las transacciones
  con exactamente los valores por defecto y fecha día 1.
- **Formato de números**: los valores se muestran y editan con el formato de moneda/
  locale del proyecto (COP, es-CO, miles con punto); el usuario no lidia con formatos
  crudos.
- **Textos en pantalla**: toda la interfaz de este flujo está en español.

## Posibles errores y mitigaciones

| Situación | Comportamiento esperado |
|---|---|
| El mes elegido ya tiene transacciones (guard por presencia) | Se avisa claramente que ese mes ya fue cargado y **no** se realiza ninguna carga. No se duplican movimientos. |
| Una fecha editada cae fuera del mes seleccionado | Se marca el renglón como inválido y se impide confirmar hasta corregirlo; mensaje explicando que la fecha debe pertenecer al mes. |
| Un valor vacío, no numérico o negativo | Se marca el renglón como inválido y se impide confirmar; mensaje indicando qué se espera (monto válido). |
| No existen templates configurados | La grilla se muestra vacía y se informa que primero hay que crear templates; no se puede confirmar una carga vacía. |
| El usuario intenta confirmar con el borrador vacío (descartó todo) | No se crea nada y se informa que no hay movimientos por cargar. |
| Falla la confirmación a mitad de camino (error de persistencia) | La operación es atómica: o se crean todas las transacciones o ninguna. Se informa el error y el mes queda sin cambios para reintentar. |
| Carrera: el mes queda cargado por otra vía entre que se abrió la grilla y se confirmó | La validación del guard se aplica también al confirmar (no solo al abrir): si el mes ya tiene transacciones al confirmar, se rechaza la carga con aviso. |
| Regla de dominio del snapshot: `is_essential` obligatorio en gastos, nulo en ingresos | Cada transacción confirmada respeta el snapshot del template; los gastos conservan su `is_essential` y los ingresos lo dejan nulo. |
