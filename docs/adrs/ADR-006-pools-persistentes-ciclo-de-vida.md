# ADR-006 — Pools de liquidez PERSISTENTES con ciclo de vida (reemplaza el rebuild stateless de T09)

- **Fecha:** 2026-06-17 (Sesion-030)
- **Estado:** Aceptado
- **Tarea:** F1-S1.3-T09b (pools persistentes) + T10 (sweep)
- **Contexto DOC-01:** pools de liquidez = `docs/reglas-smc-ict.md` §3.1; sweep/grab = §3.2.
- **Plano de implementación:** `docs/planes/ESQUELETO-MITIGACION-conceptos.md` (patrón **P1**); decisión y display en `docs/planes/HANDOFF-OPUS-MAX-pools-mitigacion.md` (Opción A + Propuesta B).

## Contexto

T09 (Sesion-027, commit `139e1c1`) construía los pools con `f_buildPools`: **reconstrucción completa**
(`array.clear(SMC_pools)` + rebuild) en cada vela relevante. Ese modelo *stateless* es incapaz de
recordar si un pool ya fue **barrido** (`swept`): al reconstruir, el estado se pierde. Consecuencia
observada por el usuario: el gráfico se satura porque **todos** los pools se dibujan como imanes vivos,
incluidos los que el precio ya cruzó (ya no son liquidez objetivo). El ruido "sin mitigación" era el
problema; la mitigación de los niveles de liquidez es la palanca grande para limpiarlo.

Además, T10 (Sweep/Grab) es precisamente **el evento que consume un pool** (`reglas-smc-ict.md` §3.2):
diseñar el marcador de barrido y la detección de sweep por separado habría duplicado el dibujo del
mismo cruce. Por eso T09b y T10 se unificaron en una sola tarea.

## Decisión

**Reemplazar el rebuild stateless por un set PERSISTENTE de pools con ciclo de vida** (patrón P1 del
esqueleto), y detectar el Sweep sobre ese set vivo.

- **CORE byte-idéntico ×3** (Visual / Strategy / Library `export`):
  - UDT `SMC_Pool` ampliado con `barIdx`, `sweptBarTime`, `sweptBarIdx` (anclas robustas a gaps de
    fin de semana, para el marcador de barrido).
  - Funciones **puras** nuevas: `f_upsertPool` (alta/merge incremental de UN candidato contra el set
    vivo, reusando la proximidad `×ATR` de `f_buildPools`), `f_markPoolsSwept` (marca `swept` los
    pools vivos cruzados por high/low de la barra), `f_detectSweep` (T10: clasifica la trampa —
    perfora el nivel y el cierre vuelve — con sesgo direccional contrario para el scoring §3.2),
    `f_prunePools` (acota a `MAX_POOLS=50`, borrando primero el barrido más antiguo).
  - `f_buildPools` se **conserva** (export / golden test / seeding) pero **ya no se llama** en
    detección. Su comentario lo documenta.
- **Detección persistente** (Visual y Strategy, idéntica salvo dibujo), en `barstate.isconfirmed`:
  orden **upsert → mark → detectSweep → prune**, sin `array.clear`. El set persiste entre velas.
- **Dibujo (solo Visual, Propuesta B):** pool `swept==false` → línea viva dashed `barTime`→ahora +
  etiqueta `BSL/SSL ·N`. Pool `swept==true` → línea dotted tenue que **TERMINA en `sweptBarTime`**
  (no se extiende a la derecha) + marcador `✗ Sweep ↑/↓` anclado en el barrido. Inputs nuevos:
  `i_showSwept`, `i_showSweeps`, `i_maxShowSweeps=20` (cuota de presentación, patrón P4).

## Alternativas descartadas

- **(Statu quo) mantener el rebuild de T09:** descartada — no puede recordar `swept`, el gráfico
  queda saturado de imanes "muertos", T10 no tendría sobre qué operar.
- **Display "desaparecer en silencio"** (borrar el pool al barrerse): descartada en el handoff a favor
  de la **Propuesta B** (marcar el barrido). El barrido es información de trading (dónde se tomó
  liquidez = sesgo); ocultarlo pierde señal y rompe la lectura del sweep.

## Consecuencias

- **Paridad MQL5 (golden tests, ADR-002):** el EA opera incremental/vivo, así que el modelo
  persistente es **más fiel** al EA que el rebuild — ventaja, no deuda. Los golden tests se construyen
  sobre el **estado vivo** (upsert/mark), no sobre el set reconstruido.
- **Observación NO bloqueante (−7 en validación, diferida a Fase 3):** `f_markPoolsSwept` usa `>=`/`<=`
  (tocar = tomar liquidez) en vez de `>`/`<` estricto (perforar) de la convención §0. Es una
  ambigüedad real (§3.2 "perfora" sugiere estricto; la semántica de barrido favorece tocar).
  Afecta paridad de golden tests → **congelado hasta calibración de Fase 3 (ADR-002)**, no se cambia
  aquí.
- **Ruido residual = calibración Fase 3 (ADR-002):** con defaults `i_poolTol=0.1×ATR14` /
  `i_minTouches=2` aún pueden quedar muchos pools; afinarlos es Fase 3 (IS/OOS), NO se baja el umbral
  ahora (regla #8 + ADR-001/002).
- **Diseño propio (LuxAlgo no tiene pools):** el clustering de liquidez y su ciclo de vida son del
  proyecto → obligan a golden tests dedicados en Fase 4.
- **Caso piloto de P1:** este refactor valida el patrón P1 del esqueleto; T17 (IDM) reutilizará el
  mismo mecanismo de "nivel consumido por barrido".

## Validación

- `smc-validator-agent`: **93/100 APROBADO** (`docs/sprint-runs/validaciones.md`). 4/4 casos §3.1 +
  sweep §3.2 + contraejemplo (BOS 06-05 12:00 no genera sweep) confirmados en EURUSD H1.
- `check-core-sync`: **OK, 592 líneas, SHA `8967d31bdbb7ed13`.**
- Compila **0/0** los 3 scripts en TV (EURUSD H1). Bug runtime de marcadores en historia profunda
  (>10000 barras) corregido anclando en `sweptBarTime`/`xloc.bar_time`.

## Referencias

- Esqueleto / patrón P1: `docs/planes/ESQUELETO-MITIGACION-conceptos.md`
- Handoff (decisión + Propuesta B): `docs/planes/HANDOFF-OPUS-MAX-pools-mitigacion.md`
- Spec SMC: `docs/reglas-smc-ict.md` §3.1 (pools), §3.2 (sweep/grab)
- Plan Pine: `docs/workplan/PINE-PLAN.md` §2/§4/§5
- T09 original: commit `139e1c1` (Sesion-027)
- Congelación de umbrales/semánticas: ADR-002
