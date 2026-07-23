---
name: design-plan
description: Genera el plan de implementación de un desarrollo, UNA VEZ que el usuario aprobó el design-spec. Traduce el spec (qué se va a construir, desde la vista del usuario) en un plan técnico ejecutable — objetivo, contexto, problema, referencia al spec, y la lista detallada de tareas a implementar — y lo guarda en docs/plans/YYYY-MM-DD-title.md. Úsalo siempre que el usuario apruebe el spec y diga "generemos el plan", "arma el plan de implementación", "ya está el spec, ahora cómo lo hacemos", o cuando termines de correr design-spec y el usuario dé luz verde para avanzar. NO lo uses si el spec aún no está aprobado (primero itera el spec) ni para desarrollos sin un spec de referencia.
---

# design-plan — plan de implementación

Este skill produce el **plan técnico** de un desarrollo a partir de un `[[design-spec]]` ya aprobado. La división es intencional: el spec dice *qué* se construye desde la perspectiva del usuario; el plan dice *cómo* se construye desde la perspectiva del implementador. Uno es el contrato, el otro la hoja de ruta.

**Requisito de entrada:** el plan se genera solo después de que el usuario aprobó el spec. Si no hay un spec aprobado, no arranques aquí — vuelve a `design-spec` e itéralo hasta que el usuario le dé luz verde. El plan sin spec aprobado se construye sobre supuestos no confirmados.

## Antes de escribir

Parte del spec aprobado como fuente de verdad. Además, **explora el código existente** antes de listar tareas: qué patrones, utilidades y componentes ya existen y se pueden reutilizar. Un buen plan reutiliza lo que hay en lugar de reinventarlo, y sus tareas reflejan la realidad del repo, no un proyecto en abstracto.

Confirma con el usuario un **título corto** para el documento (idealmente el mismo del spec, para que se correspondan). De ahí derivas el `title` del nombre de archivo.

## Formato del nombre y ubicación

- Carpeta: `docs/plans/` (créala si no existe).
- Nombre: `YYYY-MM-DD-title.md`, donde:
  - `YYYY-MM-DD` es la fecha de hoy.
  - `title` es el título en **kebab-case**, en minúsculas, sin acentos ni caracteres especiales.
- Ejemplo: `docs/plans/2026-07-21-conciliacion-bancaria-automatica.md`.
- Si existe un spec correspondiente, conviene que compartan el mismo `title` para que se emparejen entre `docs/specs/` y `docs/plans/`.

## Estructura del documento

Usa estas secciones, en este orden:

```markdown
# <Título del desarrollo> — Plan de implementación

## Objetivo
Qué se logra al completar este plan, en 1-3 frases. El resultado concreto y
verificable, no la actividad.

## Contexto
El trasfondo necesario para entender el plan: dónde encaja en el proyecto, qué
existe hoy, qué componentes/módulos se ven afectados. Menciona el código y los
patrones reutilizables que encontraste al explorar.

## Problema
Qué necesidad técnica resuelve este desarrollo y por qué el enfoque elegido es el
adecuado. Es la traducción técnica del "Contexto del problema" del spec.

## Spec de referencia
Enlace/ruta al design-spec aprobado que este plan implementa
(p. ej. `docs/specs/2026-07-21-conciliacion-bancaria-automatica.md`). El plan debe
ser fiel a ese spec; si durante la planificación surge una discrepancia con el
spec, márcala explícitamente en vez de resolverla en silencio.

## Tareas a implementar
La lista ordenada de tareas para construir el desarrollo. Cada tarea debe ser
accionable y con suficiente detalle para ejecutarla sin adivinar. Para cada una:

- **Qué**: la tarea concreta.
- **Dónde**: archivos/módulos a crear o modificar.
- **Detalles**: enfoque, casos borde a cubrir, validaciones (importantes en
  finanzas), y dependencias con otras tareas del plan.

Ordena las tareas de forma que cada una se pueda implementar y verificar sobre la
anterior. Marca cuáles son casos borde y manejo de errores que vienen del spec,
para no perderlos en la implementación.
```

## Al terminar

Guarda el archivo, informa la ruta y ofrece revisión. El plan es la referencia contra la cual luego se verifica el desarrollo con `[[verify-after-changes]]`, así que conviene que quede sólido antes de arrancar a codear.

## Qué NO hacer

- No generes el plan si el spec no está aprobado.
- No listes tareas vagas ("implementar el módulo"): cada tarea debe decir qué, dónde y con qué detalle.
- No te desvíes del spec sin señalarlo; el plan implementa el spec, no lo reescribe.
