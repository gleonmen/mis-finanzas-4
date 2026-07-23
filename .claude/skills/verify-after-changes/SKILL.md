---
name: verify-after-changes
description: Verifica de punta a punta un desarrollo recién implementado, ejercitándolo en el navegador antes de darlo por terminado. Dispara este skill SIEMPRE que consideres que ya terminaste de implementar el plan o el spec y estás por declarar el trabajo como "listo" — en vez de asumir que funciona, levanta el servidor, eliges 5 casos de prueba importantes, los pruebas en el navegador, recoges el resultado, lo comparas contra el plan y el design-spec, y luego arreglas lo que falle o das luz verde. Úsalo cuando digas cosas como "ya terminé la implementación", "creo que está listo", "probemos que funcione", "verifiquemos los cambios", o al cerrar cualquier feature no trivial. NO lo uses para cambios sin superficie ejecutable (solo docs, comentarios o config sin efecto observable).
---

# verify-after-changes — probar antes de dar por terminado

El propósito de este skill es cerrar la brecha entre "escribí el código" y "el código hace lo que debía". La implementación no está terminada cuando compila; está terminada cuando la ejercitas y observas que cumple el objetivo. Este skill se dispara en ese momento — cuando estás por declarar el trabajo como hecho — y convierte esa declaración en algo verificado, no supuesto.

Encadena con [[design-spec]] y [[design-plan]]: el spec es el contrato desde la vista del usuario y el plan es la hoja de ruta técnica; ambos son la referencia contra la cual se verifica. Tráelos a la vista antes de empezar — son tu referencia de "qué debería pasar":

- El **plan** está en `docs/plans/YYYY-MM-DD-title.md`.
- El **spec** correspondiente está en `docs/specs/YYYY-MM-DD-title.md` (comparte el mismo `title` que el plan).

## Paso 1 — Levantar el servidor

Arranca la aplicación con la herramienta de preview del entorno (`preview_start` con la config de `.claude/launch.json`, o creándola si no existe). No uses un `Bash` suelto con `&` para el servidor: usa la herramienta de preview para que quede gestionado.

Después de levantarlo, revisa los logs (`preview_logs`) para confirmar que arrancó sin errores de build antes de probar nada. Si el servidor no levanta, ese es el primer bug a resolver.

## Paso 2 — Elegir 5 casos de prueba importantes

Selecciona **5 casos** que de verdad ejerciten el objetivo del desarrollo. No 5 variantes triviales de lo mismo: busca cobertura real. Guíate por el spec y el plan, y prioriza:

- **El flujo feliz principal**: el caso de uso central para el que se hizo el desarrollo.
- **Casos borde relevantes**: valores límite, datos faltantes o inusuales.
- **Manejo de errores**: qué pasa cuando algo sale mal (entradas inválidas, estados imposibles) — especialmente crítico en un proyecto de finanzas, donde un cálculo mal validado es un problema real.
- **Interacciones clave del usuario**: los puntos donde el comportamiento esperado del spec es más específico.

Antes de probar, enuncia brevemente los 5 casos y qué esperas que pase en cada uno (según el spec). Eso vuelve la prueba verificable: sabes de antemano cuál es el resultado correcto.

## Paso 3 — Probar en el navegador

Ejercita cada caso **directamente en el navegador** con las herramientas de browser (`navigate`, `read_page`/`find` para ubicar elementos, `computer`/`form_input` para interactuar, y `read_console_messages` / `read_network_requests` para detectar errores no visibles). No te limites a mirar tests unitarios ni a asumir por el código: conduce el flujo real y **observa** lo que ocurre.

Para cada caso registra: qué hiciste, qué observaste, y si coincide o no con lo esperado.

## Paso 4 — Recoger feedback y comparar con plan + spec

Consolida los resultados de los 5 casos y compáralos punto por punto contra el **plan** y el **design-spec**:

- ¿El comportamiento observado cumple el "Comportamiento esperado" del spec?
- ¿El alcance implementado corresponde al "Alcance versión 1"?
- ¿Los errores se manejan como dice la sección de "Posibles errores y mitigaciones"?

Marca cada caso como ✅ cumple / ⚠️ cumple parcial / ❌ falla, con evidencia concreta de lo que viste.

## Paso 5 — Arreglar o dar luz verde

Según la comparación:

- **Si hay fallos o algo no alcanza el objetivo**: arréglalo. Corrige el código, y vuelve a los pasos 3-4 para re-verificar ese caso (y cualquier otro que el arreglo pueda haber afectado). Itera hasta que los 5 casos cumplan.
- **Si todo cumple**: da **luz verde explícita**. Resume qué se probó, el resultado de cada caso y por qué el desarrollo cumple el spec. Recién ahí el trabajo está terminado.

No des luz verde con fallos abiertos "menores" sin señalarlos: si algo no cumple pero decides no arreglarlo ahora, dilo explícitamente y deja que el usuario decida.

## Qué NO hacer

- No declares "listo" sin haber ejercitado los cambios en el navegador.
- No sustituyas la prueba real por "los tests pasan" o "el código se ve bien".
- No elijas 5 casos triviales para inflar el conteo: el valor está en que cubran el objetivo y los riesgos reales.
