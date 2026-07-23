---
name: design-spec
description: Redacta el documento de especificaciones de un desarrollo desde el punto de vista del usuario, una vez que el problema y el enfoque ya están claros (típicamente después de correr el skill brainstorming). Genera un markdown con secciones fijas (Overview, Usuario objetivo, Contexto del problema, Alcance versión 1, Comportamiento esperado, Posibles errores y mitigaciones) y lo guarda en docs/specs/ con el nombre YYYY-MM-DD-title.md. Úsalo siempre que el usuario diga que quiere "escribir la spec", "documentar el diseño/comportamiento", "hacer el design doc/documento de especificaciones", "dejar por escrito qué vamos a construir", o cuando ya se eligió un camino y toca formalizarlo antes de codear. NO lo uses cuando todavía hay ambigüedad sobre qué construir (para eso está brainstorming) ni para documentación técnica de implementación ya escrita.
---

# design-spec — documento de especificaciones

Este skill produce el **contrato escrito** de un desarrollo antes de implementarlo. Se usa cuando el problema y el enfoque ya están claros — normalmente justo después de `[[brainstorming]]`, cuando ya se eligió un camino. Su valor es fijar, desde la perspectiva del usuario, qué se va a construir y cómo debe comportarse, para que la implementación tenga un blanco claro y verificable.

El punto de vista es **del usuario, no del implementador**: describe qué experimenta y qué espera la persona que usará la funcionalidad, no cómo está construido por dentro. Nada de detalles de implementación (clases, endpoints internos, esquemas de base de datos) salvo que sean parte del comportamiento observable.

## Antes de escribir

Reúne el contexto necesario para que la spec no tenga huecos. Si vienes de un `brainstorming`, ya tienes casi todo; si no, revisa la conversación y el repo. Si falta algo esencial para completar una sección, **pregúntalo de forma breve** en lugar de inventarlo — una spec con supuestos silenciosos es peor que una con una pregunta abierta.

Antes de generar el archivo, confirma con el usuario un **título corto** para el documento. De ahí derivas el `title` del nombre de archivo.

## Formato del nombre y ubicación

- Carpeta: `docs/specs/` (créala si no existe).
- Nombre: `YYYY-MM-DD-title.md`, donde:
  - `YYYY-MM-DD` es la fecha de hoy.
  - `title` es el título en **kebab-case**, en minúsculas, sin acentos ni caracteres especiales (p. ej. `conciliacion-bancaria-automatica`).
- Ejemplo: `docs/specs/2026-07-21-conciliacion-bancaria-automatica.md`.

## Estructura del documento

Usa EXACTAMENTE estas secciones, en este orden. Los encabezados van en español tal cual:

```markdown
# <Título del desarrollo>

## Overview
Resumen en 2-4 frases: qué es esta funcionalidad y qué valor entrega. Alguien que
lea solo esto debe entender de qué se trata.

## Usuario objetivo
Quién va a usar esto y con qué nivel/rol. Sus objetivos y su contexto al usarlo.
Si hay más de un tipo de usuario, distínguelos.

## Contexto del problema
Qué problema o necesidad motiva este desarrollo. Cómo se resuelve hoy (si se
resuelve) y por qué eso no alcanza. El "por qué" detrás de la funcionalidad.

## Alcance versión 1
Qué entra en esta primera versión y —igual de importante— qué NO entra
(explícitamente fuera de alcance por ahora). Sé concreto: esta sección es la que
evita el scope creep. Usa listas de "Incluye" y "No incluye".

## Comportamiento esperado
Cómo debe comportarse desde la perspectiva del usuario: los flujos principales,
paso a paso, y qué observa el usuario en cada caso. Cubre el flujo feliz y las
variantes relevantes. Redáctalo de forma verificable — cada afirmación debería
poder convertirse en una prueba.

## Posibles errores y mitigaciones
Qué puede salir mal (datos faltantes o inválidos, casos límite, fallos externos)
y cómo debe responder el sistema en cada caso. En un proyecto de finanzas la
corrección importa: sé explícito sobre validaciones, mensajes al usuario y qué
pasa con datos parciales o inconsistentes. Una tabla error → mitigación funciona bien.
```

## Al terminar

Guarda el archivo en la ruta correcta e informa al usuario la ruta creada.

## Approval gate

La spec NO es final hasta que el usuario la aprueba explícitamente. Después de guardarla, preséntala para revisión y detente a esperar su decisión — no avances por tu cuenta. El usuario tiene dos caminos:

- **Iterar**: si algo falta, sobra o está mal, ajusta la spec según su feedback, guarda la versión actualizada y vuelve a presentarla. Repite este ciclo tantas veces como haga falta; la spec es un documento vivo y es normal que dé varias vueltas antes de quedar bien.
- **Aprobar**: cuando el usuario dé luz verde explícita, la spec queda como contrato del desarrollo. Ese es el momento de continuar con el skill `[[design-plan]]` para generar el plan de implementación a partir de esta spec.

No generes el plan ni empieces a implementar mientras la spec no esté aprobada: ese es justamente el punto del gate — asegurar que construimos sobre un acuerdo confirmado, no sobre un borrador.

## Qué NO hacer

- No mezcles detalles de implementación interna en el comportamiento observable.
- No dejes secciones vacías ni con "TBD" silenciosos: si algo no se sabe, márcalo como pregunta abierta explícita.
- No inventes alcance ni requisitos que el usuario no confirmó; ante la duda, pregunta.
