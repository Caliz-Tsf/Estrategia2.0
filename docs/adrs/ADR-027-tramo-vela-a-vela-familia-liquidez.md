# ADR-027 — El **tramo vela→vela** de la familia Liquidez: dónde nació el nivel y dónde murió

- **Estado:** 🟡 **PROPUESTO — acordado con el usuario en S146, NO implementado.** La implementación va a **S147, por subconjuntos, verificando cada uno** (decisión explícita del usuario). Ninguna línea de este ADR está en el código todavía.
- **Fecha:** 2026-07-28 (Sesion-146).
- **Contexto de fase:** Fase 1 · curación visual (F1-GATE), familia **Liquidez** — el objetivo original de S144 que S145 dejó sin retomar.
- **Relacionado:** [[ADR-006]] (ciclo de vida de pools), [[ADR-014]] (strength decide *cómo* se dibuja), [[ADR-026]] (DOL: puerta de banda y escalera), `reglas-smc-ict.md` §3.1/§3.2/§3.3/§3.5/§3.7, §6.3.11/§6.3.12.

---

## 1. Contexto — qué lo disparó

S146 implementó §3.3 Grab (`f_detectGrab`, validación 96/100). Al explicarle al usuario **cómo se ve**
un grab, pidió esto, literal:

> «cuando se cumpla un grab se dibuje como me los dibujaste, o sea que desde la vela 0 hasta la vela 1
> y donde se produce el 2 debe correr una línea, parecido a los EQH o EQL, y dejar el nombre al medio
> […] Quiero también que los BSL y los SSL al momento de ser barridos también me generen una línea de
> la vela a la vela que lo barrió o lo mitigó.»

### 1.1 El defecto que arregla

Hoy cada evento de la familia se dibuja como **una etiqueta suelta en la vela del barrido**. Eso comunica
*qué pasó y dónde terminó*, pero **pierde el origen**: de qué pivote venía ese nivel y cuánto tiempo
estuvo vivo. En un gráfico con historia profunda esa etiqueta queda huérfana — el lector no puede
reconstruir de dónde salió el nivel sin buscarlo a ojo.

El precedente en el propio sistema es EQH/EQL, que ya se dibuja como **tramo toque→toque**: ahí sí se
ve el nivel como objeto con extensión temporal, no como un punto.

## 2. Decisión

### D1 — Tramo vela→vela en **cuatro** conceptos

Línea punteada desde la **vela que creó el nivel** (el primer toque del pool / el pivote aislado) hasta
la **vela que lo consume**, con la etiqueta del concepto sobre el **punto medio** del tramo:

| concepto | origen del tramo | fin del tramo |
|---|---|---|
| **Grab** (§3.3) | el pivote aislado (1 toque) | la vela que lo perfora y cierra de vuelta |
| **Sweep / Raid / Spring** (§3.2, §3.7) | el **primer** toque del pool | la vela del barrido |
| **Pool BSL/SSL barrido** (§3.1) | el primer toque | la vela que lo barrió o mitigó |

Raid y Spring son subtipos del sweep (`f_classifySweep`), así que heredan el mismo tramo con su glifo.

### D2 — **Judas** y **False breakout** se quedan como están: etiqueta en la vela

**Rechazado** el tramo para estos dos. Motivo: **no tienen un fin único**.

- **Judas** (§3.5): el barrido ocurre en una vela, pero el concepto no se confirma hasta el
  displacement contrario, **hasta `i_judasBars` (6) velas después**. El tramo tendría dos finales
  posibles ("dónde se tomó la liquidez" vs "cuánto duró la trampa") y elegir uno haría que la misma
  primitiva significase cosas distintas según el concepto.
- **False breakout** (§3.7): mismo problema en pequeño — cierra más allá y revierte en
  `≤ i_fbBars` (2) velas.

Un tramo cuyo extremo derecho significa una cosa en unos conceptos y otra en otros es **información
falsa**, que es exactamente el criterio con el que ADR-026 D14 rechazó apilar etiquetas fuera de banda.

### D3 — La etiqueta va **hacia afuera del precio**, no siempre encima

El usuario pidió primero "el nombre por encima de la línea". Al dibujarlo se vio que en el lado de
abajo (SSL, Spring) "encima" cae **dentro de las velas**. Regla acordada:

- **BSL / lado alto** → etiqueta **encima** del tramo
- **SSL / lado bajo** → etiqueta **debajo** del tramo

Es la misma lógica que ya usa el marcador de sweep (`label.style_label_down` / `_up`) y la columna de
marcadores del DOL (ADR-026 D10): el texto se aleja del precio, no lo invade.

## 3. Lo que este ADR **reabre a propósito** (y por qué no es una regresión)

S144 **retiró** el dibujo de los pools barridos, con este motivo registrado en el código
(`SMC-Visual.pine`, comentario de `f_drawPools`):

> «Los pools BARRIDOS ya NO se dibujan: su historial era invisible en la práctica (segmentos cortos
> transp 75) y redundante con el MARCADOR de sweep.»

Ese diagnóstico era correcto **para lo que había**: un trazo corto, tenue y sin nombre. Lo que D1
propone es distinto en los dos puntos que lo hacían inútil: el tramo **va al origen real** (no un
segmento corto) y **lleva el nombre al medio** (no es anónimo). Se acepta reabrirlo **con esa
diferencia explícita**, para no repetir una decisión ya tomada sin darse cuenta.

## 4. Riesgo declarado y NO medido

**Coste en objetos de dibujo.** Hoy cada evento de la familia es **1 etiqueta**. Con tramo pasa a
**1 etiqueta + 1 línea**. Restricciones vigentes:

- Pine tope duro **500 labels** y **500 lines**. Con todo encendido el Visual ya roza el de labels
  (S145 §5.3).
- La familia Liquidez es de las más frecuentes: en D1 EURUSD hay **666 barridos** en la historia
  (medido en S146), acotados en pantalla por `i_maxShowSweeps` (20).

**No se estima a ojo.** Memoria del proyecto: *los tokens y los objetos de Pine no se predicen, solo se
miden* (~8 predicciones muertas). La medición es la **primera tarea de S147**, antes de extender el
tramo a los tres conceptos.

## 5. Plan de ejecución (S147) — por subconjuntos, verificando cada uno

Decisión del usuario: **no implementar los tres de golpe**. Orden propuesto:

1. **Medir** el coste en objetos del tramo sobre UN concepto (el grab, que es el más reciente y el más
   frecuente en 1 toque).
2. **Grab** → aplicar → verificar → decidir si sigue.
3. **Sweep / Raid / Spring** → aplicar → verificar.
4. **Pool BSL/SSL barrido** → aplicar → verificar.
5. Retomar la **curación de la familia Liquidez** (hue violeta sobrecargado, anti-solape EQL↔Sweep),
   que sigue siendo el objetivo original heredado de S144.

## 6. Pendiente independiente de este ADR

**Verificación de §3.3 Grab en H1 y M5 con casos nativos de cada TF.** La validación de S146 (96/100)
se apoyó en la correspondencia regla↔código porque los 3 casos canónicos de §3.3 son de **M5
2026-06-10/11** y el histórico M5 de OANDA solo alcanza ~2026-07-13 ⇒ **no reproducibles**. Hace falta
levantar casos nuevos, fechados, en el propio TF. Va a S147.
