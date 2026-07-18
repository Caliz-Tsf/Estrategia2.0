# PROMPT PARA FABLE — auditoría S135 (copiar y pegar)

> Adjuntar junto a este prompt: `docs/planes/DOSSIER-FABLE-capacidad-y-codigo-muerto-S135.md`
> Acceso útil (opcional): rama `pine/sistema-completo`, archivos `pine/*.pine`,
> `scripts/gen_ablacion_core.py`, `scripts/audit_muerto_transitivo.py`, `docs/adrs/ADR-020`,
> `ADR-021`, `ADR-022`, `ADR-023`, `docs/reglas-smc-ict.md` §2.3.1/§2.3.2.

---

Hola Fable. Necesito una **auditoría adversarial**, no una validación amable.

En la sesión 135 del proyecto Estrategia 2.0 (bot SMC/ICT: Pine Script v6 primero, EA MQL5 nativo
después) medimos varias cosas sobre el presupuesto de tokens de Pine y encontramos que **dos ADR del
propio proyecto se apoyan en una premisa que ahora mide falsa**. Antes de reestructurar nada quiero
que lo verifiques tú.

El dossier adjunto es **autocontenido** y marca cada afirmación como `[MEDIDO]`, `[NO MEDIDO]` u
`[OPINIÓN]`.

## Lo que te pido, en orden

**1. Audita los `[MEDIDO]`.** Desconfía de ellos. En esta misma sesión el arnés de medición **midió
humo dos veces** antes de funcionar (un lastre que Pine eliminaba por tree-shaking, y un límite de
tamaño del cuerpo principal), y se commiteó un cambio afirmando "compila 0/0" cuando `pine_check` no
cuenta tokens y el cambio rompía el apply en vivo. Si el método tiene un agujero, dilo.

Presta atención especial al hallazgo central: **tres builds distintos —base, menos 101 líneas de
funciones no llamadas, y más 590 líneas de funciones duplicadas no llamadas— dieron exactamente
107986 tokens.** De ahí concluimos que Pine hace tree-shaking completo. ¿Se sostiene esa conclusión
con esa evidencia, o hay una explicación alternativa que no hemos considerado?

**2. Resuelve las dos contradicciones abiertas** (§2.1 y §4 del dossier):
- Si el código muerto cuesta cero, **¿por qué el fix de ADR-022 —retirar `f_tfExtremes`— resolvió el
  `CE10117`?** ¿Hay que corregir ADR-020 y ADR-022?
- El Visual **no cuadra consigo mismo por ~1.100 tokens** según por dónde se calcule. Planteamos dos
  hipótesis y no hemos medido ninguna. ¿Cuál es? Si es la de interacción de tree-shaking, reencuadra
  todo el episodio de `pdMid`.

**3. Responde las 7 preguntas** del §11 del dossier.

**4. Recomienda el camino.** El problema de fondo: el alcance completo de la Fase 1 —todas las
familias de concepto, sus variantes, los 3 timeframes y la herencia MTF— **no cabe en un solo
indicador**, el Visual está a ~0 de headroom, Context tiene ~85% libre, y **el plan gratuito de
TradingView solo permite 2 indicadores por gráfico**. Los indicadores **no pueden comunicarse en
ejecución**.

## Restricciones que NO se pueden violar

El usuario ha sido explícito: *"debemos cumplir totalmente el plan y sus reglas"*. **No se acepta
deuda permanente contra una regla dura.**

- **#1 Determinismo / anti-repaint.** Hay una violación viva y declarada (§8 del dossier) que hay
  que **cerrar**, no diferir.
- **#2 CORE byte-idéntico** entre los 3 consumidores.
- **#8 Ningún gate se salta ni se ajusta el criterio.** Si un gate falla se retrocede con
  diagnóstico.
- **ADR-001 / ADR-002:** símbolo-agnóstico y nada se calibra a ojo sobre un símbolo.
- **2 slots de indicador.** No hay tercero.

## Formato de respuesta que me sirve

Para cada punto:
- **qué has verificado tú mismo** y cómo (no "parece correcto");
- **qué refutas** de lo que afirmamos, con el razonamiento;
- el **esqueleto** de la solución que recomiendas, su **coste estimado**, y **qué medición habría
  que hacer ANTES de tocar `pine/`**.

**No hace falta que escribas código.** Lo que necesito es el diseño, el coste y el orden.

Si crees que alguna de nuestras conclusiones es sobreajuste, un artefacto de medición o una
racionalización, dilo directamente. Este proyecto lleva 11+ hipótesis refutadas con medición y
prefiere una refutación temprana a una confirmación cómoda.
