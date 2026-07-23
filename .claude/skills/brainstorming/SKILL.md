---
name: brainstorming
description: Ritual de arranque para CUALQUIER desarrollo nuevo de software en proyecto-finanzas-4 — una feature, módulo, componente, endpoint, refactor grande o integración. Antes de escribir una línea de código, este skill desambigua el pedido con pocas preguntas esenciales y luego presenta 2-3 alternativas concretas de implementación con su recomendación. Úsalo siempre que el usuario diga que va a "empezar algo nuevo", "arrancar un desarrollo", "implementar/agregar/crear" una funcionalidad, o traiga una idea de feature todavía difusa, aunque no nombre el skill. Si el pedido es ambiguo o de alcance no trivial, prefiere disparar este skill antes de asumir supuestos y ponerte a codear. NO lo uses para bugs puntuales de una línea, cambios triviales ya especificados, o preguntas de consulta que no inician un desarrollo.
---

# Brainstorming — arranque de desarrollos

Este skill es el primer paso de todo desarrollo nuevo en este proyecto. Su razón de ser: la mayoría del retrabajo nace de arrancar a codear sobre supuestos no confirmados. Antes de tocar código, alineamos qué se va a construir y elegimos un camino de forma deliberada.

El flujo tiene tres momentos: **desambiguar → proponer → recomendar**. No los saltes, pero tampoco los infles: el objetivo es llegar rápido a un punto donde el usuario pueda decir "sí, arranquemos por acá".

## 1. Desambiguar (pocas preguntas, bien elegidas)

Haz **entre 3 y 5 preguntas esenciales** en una sola tanda. La meta no es interrogar sino cerrar las ambigüedades que de verdad cambiarían la implementación. Antes de preguntar, revisa el código existente y el contexto de la conversación — no preguntes lo que puedes deducir tú mismo leyendo el repo.

Una pregunta esencial es la que, si la respondes mal, te obliga a rehacer trabajo. Prioriza según lo que esté genuinamente abierto en este pedido; guías típicas:

- **Objetivo y usuario**: ¿qué problema resuelve y para quién? ¿Cómo se ve "terminado"?
- **Alcance / límites**: ¿qué entra y qué explícitamente NO entra en esta primera versión?
- **Entradas y salidas**: datos, formatos, contratos, con qué integra.
- **Restricciones**: stack o librerías que ya usa el proyecto, rendimiento, compatibilidad, deadlines.
- **Casos borde y fallo**: qué pasa cuando faltan datos, hay errores o valores límite (relevante en un proyecto de finanzas, donde la precisión importa).

Formula las preguntas concretas y sin jerga innecesaria. Si el usuario contesta y **aún queda un supuesto crítico sin cerrar**, haz una segunda tanda corta — pero no conviertas esto en rondas infinitas. Con lo esencial resuelto, avanza.

Si el usuario dice algo como "no me preguntes tanto, tú decide", respeta eso: declara los supuestos que estás tomando de forma explícita y pasa directo a las alternativas.

## 2. Proponer 2-3 alternativas

Con el pedido ya claro, presenta **2 o 3 caminos distintos** para implementarlo. No variaciones cosméticas del mismo enfoque: alternativas que representen decisiones de diseño genuinamente diferentes (p. ej. dónde vive la lógica, cuánta infraestructura nueva, build-vs-reuse, simple-ahora-vs-extensible-después).

Para cada alternativa incluye:

- **Nombre corto** que capture la esencia del enfoque.
- **En qué consiste**: 1-3 frases de cómo se implementaría.
- **A favor / en contra**: los trade-offs reales — esfuerzo, complejidad, mantenibilidad, riesgo, cuánto encaja con lo que ya existe en el repo.

Usa este formato:

```
### Opción A — <nombre>
Qué es: <descripción breve>
A favor: <ventajas concretas>
En contra: <costos/riesgos concretos>

### Opción B — <nombre>
...
```

Sé honesto con los trade-offs: si una opción es más rápida pero deja deuda técnica, dilo. El valor está en el contraste, no en que todas suenen bien.

## 3. Recomendar

Cierra con una **recomendación explícita**: por cuál de las opciones empezarías y por qué, atada a lo que dijo el usuario en la fase 1 (sus prioridades, restricciones y alcance). Una recomendación no es "depende" — es una postura defendible. Si tu recomendación asume algo que no confirmaste, hazlo visible ("recomiendo A asumiendo que priorizas X sobre Y").

Termina invitando a decidir, no imponiendo: el usuario elige y a partir de ahí se arranca el desarrollo.

## Qué NO hacer

- No empieces a escribir código durante el brainstorming. Este skill termina cuando hay un camino elegido, no cuando está implementado.
- No presentes una sola opción disfrazada de varias.
- No hagas 15 preguntas "por si acaso". La disciplina está en preguntar poco y certero.
