# Sesión 012 — F1-S1.1-T02 swings + clasificación HH/HL/LH/LL
> Fecha: 2026-06-11 · Fase 1 Sprint 1.1 · Claude Code (Haiku 4.5) + Freddy
> Registro de QUÉ se hizo, POR QUÉ, CON QUÉ FINALIDAD y QUÉ SE DECIDIÓ.

## Objetivo de la sesión
Segunda tarea del Sprint 1.1: **F1-S1.1-T02 — Detección de swings y clasificación HH/HL/LH/LL** (migración v5→v6 del algoritmo LuxAlgo).

## Qué se hizo y por qué

### Estado inicial
- WIP sin commitear en rama `pine/sistema-completo`: `f_detectSwings` y `f_classifySwing` ya escritas SOLO en SMC-Visual.pine. Rompía regla #2 (core byte-idéntico). Freddy tomó decisión: continuar y completar T02 (cierre de sesión en anterior = lógico; completar = mejor que postergar).

### F1-S1.1-T02 — Swings (commit aa4ed23)
- **Implementación en CORE (byte-idéntico Visual/Strategy):**
  - `f_detectSwings(len)` — wrapper de `[ta.pivothigh(len, len), ta.pivotlow(len, len)]` (reglas-smc-ict §1.1 def. cuantificada).
  - `f_classifySwing(isHigh, price, swings[])` — compara contra swing previo del mismo tipo (HH vs HL si alto, LH vs LL si bajo). Lógica: HH = high > high anterior; HL = high < high anterior; LH = low > low anterior; LL = low < low anterior. Empate en precio = hereda kind del anterior (candidato EQH/EQL, regla §1.2). Seed: primer swing alto = HH, primer swing bajo = LL.
  - **Versión `export`** en `SMC-Library.pine` para referencia (PINE-PLAN §2).
  - **Sección CORE idéntica** en Visual y Strategy (143 líneas, SHA `584109b`).

### Wiring y dibujo
- Wiring en sección DETECCIÓN de ambos consumidores con guard `barstate.isconfirmed` (anti-repaint D-PINE-03).
- Swing anclado en vela t = `bar_index - len` (la vela del pivote, no la confirmación).
- Tiempo registrado como `time[len]`.
- **Dibujo** (solo Visual, no afecta CORE):
  - `f_drawSwing()` — labels teal (HH/HL) arriba, rojo (LH/LL) abajo.
  - Input `i_showSwings` para mostrar/ocultar (default off → se activa para verificación).
- Panel actualizado a "swings T02" en sección de estado.

### Compilación y sincronización
- **Compile 0/0** los 3 archivos en TV (EURUSD H1, study "SMC Engine — Visual" id 954V2v). ✅
- **check-core-sync.ps1 OK** (143 líneas, SHA `584109b`). ✅

### Validación SMC
- **smc-validator-agent: 97/100 APROBADO.**
  - 4 casos canónicos confirmados contra OHLCV real de EURUSD H1 (histórico TV descargado):
    1. SH 2026-05-27 06:00 @ 1.16494 (pivote 5 velas atrás).
    2. SH 2026-05-29 15:00 @ 1.16859 (pivote 5 velas atrás).
    3. SL 2026-06-08 09:00 @ 1.14997 (pivote 5 velas atrás).
    4. Secuencia de giro estructural (2026-06-08 a 06-09): LL → HH → HL → HH (transición bajista → alcista).
  - Contraejemplo: no-swing cuando falta confirmación de pivote.
  - Score registrado en `docs/sprint-runs/validaciones.md` (archivo nuevo).

### Observación no bloqueante
- Durante validación: **swing high + swing low confirmados en la MISMA vela t** (caso spike/reversión abrupta; muy raro con swingLen=5 en H1, pero posible).
- **No es bug:** `f_classifySwing` filtra por tipo (isHigh/isLow), sin guard de exclusión mutua. Análisis: ningún concepto downstream (BOS, CHoCH, MSS) asume alternancia obligatoria, por lo que no interfiere.
- **Decisión:** NO se añadió guard adicional. Se dejó **comentario de invariante** en CORE y ambos consumidores: `INVARIANTE [T02]: en spillovers (same-bar high/low), cada uno clasifica independientemente sin mutua exclusión — downstream los procesa por separado sin asumir alternancia.`
- **Elevado a Fable** en `docs/notas-revision-fable.md` (nuevo) como **N-01** para revisión en gate pre-Fase 4, con contexto MQL5 (paridad ADR-002) — si el EA debe replicar comportamiento bit-a-bit, esta situación necesita decisión arquitectural.

### Higiene TradingView (no bloqueante)
- Durante compilación y verificación, los `pine_set_source` + save manuales en Strategy/Library sobrescribieron los scripts guardados en TV (asincronía: `.pine` en git = fuente verdad; TV = reflejo).
- **Acción:** Re-guardar scripts limpios en TV en próxima sesión TV (ni del lado Pine ni de la compilación — simplemente "save to Pine Editor" en cada estudio).
- **No afecta histórico de git** (commits son limpios).

## Decisiones de esta sesión
- Continuar T02 dentro de la misma sesión iniciada en Sesion-011 (aprovecha contexto continuado).
- El invariante [T02] se documenta pero no se bloquea (observación arquitectural, no bug).
- Elevación de N-01 a Fable para decisión pre-Fase 4 (ADR-002 ya cubre el principio).

## Estado al cierre
- **Fase:** FASE 1 Sprint 1.1 EN CURSO. **T01 ✅** (Sesion-011, commit 45449f3), **T02 ✅** (Sesion-012, commit aa4ed23). Faltan T03 (BOS+CHoCH), T04 (bias por TF).
- **Working tree:** limpio.
- **Core sync:** OK (143 líneas, SHA 584109b).
- **Rama:** `pine/sistema-completo`.

## Siguiente paso (próxima sesión)
**F1-S1.1-T03 — BOS / CHoCH** (reglas-smc-ict §1.3 + Modelo de bias estructural).
- Implementar `f_detectBOS()` y `f_detectCHoCH()` en el CORE.
- Usa structure high/low y el modelo de bias (§1.4, vinculado a T04).
- Regla: ruptura por CIERRE (no mecha), BOS interno usa internalLen.
- **Vigilancia especial:** orden cronológico de swings con invariante [T02] (si llegan mismo-bar high/low).
- Cross-check paridad ver05 (ADR-002): `scripts/ver05/detect*.py` ya tiene lógica BOS, comparar.
- Ciclo: check-rule → implement CORE → compile 0/0 → screenshot → smc-validator ≥90 → check-core-sync → aprobación → commit.

## Cambios en archivos (esta sesión)
- `pine/SMC-Library.pine` — añadidas `f_detectSwings()` + `export f_classifySwing()` (+37 líneas).
- `pine/SMC-Visual.pine` — añadido completo `f_detectSwings`, `f_classifySwing`, `f_drawSwing`, input `i_showSwings`, wiring y panel (+77 líneas, -4 netas).
- `pine/SMC-Strategy.pine` — añadido `f_detectSwings`, `f_classifySwing`, wiring (+52 líneas, -1 netas).
- `docs/sprint-runs/validaciones.md` — NUEVO. Registro de validaciones smc-validator-agent para T02 (4 casos + score 97/100).
- `docs/notas-revision-fable.md` — NUEVO. Notas de observaciones arquitecturales pendientes de Fable (N-01 sobre invariante [T02]).
- `memory/ESTADO-ACTUAL.md` — se actualizará en protocolo de cierre (siguiente acción).
- `memory/sesiones/Sesion-012.md` — este documento.

## Notas
- Diferencia vs Sesion-011: esta tarea partió de WIP (decisión Freddy de completar), no de cero. Ambas sesiones forman el ciclo "esqueleto + primer concepto".
- Los archivos `validaciones.md` y `notas-revision-fable.md` son nuevos, creados como parte de T02, no existían antes.
- Numeración: esta es Sesion-012, secuencial a Sesion-011.
- **Higiene TV pendiente:** guardar scripts Clean en próxima sesión TV (no es bloqueante).
