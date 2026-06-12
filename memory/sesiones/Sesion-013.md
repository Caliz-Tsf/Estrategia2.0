# Sesión 013 — F1-S1.1-T03 BOS + CHoCH + modelo de bias estructural
> Fecha: 2026-06-12 · Fase 1 Sprint 1.1 · Claude Code (Opus 4.8) + Freddy
> Registro de QUÉ se hizo, POR QUÉ, CON QUÉ FINALIDAD y QUÉ SE DECIDIÓ.

## Objetivo de la sesión
1. **Pendiente** de Sesion-012: re-guardar los scripts limpios en TradingView (git = fuente de verdad).
2. **Siguiente paso:** F1-S1.1-T03 — BOS / CHoCH (reglas-smc-ict §1.3 + §1.4 + "Modelo de bias estructural").

## Qué se hizo y por qué

### Pendiente — higiene TradingView
- El slot guardado `SMC_Library` (id fe9e04…, el indicador del chart, study 954V2v) tenía una versión del Visual con comentarios despojados (síntoma del overwrite descrito en Sesion-012).
- **Decisión de eficiencia:** plegar el re-guardado dentro del guardado de T03 en vez de re-guardar el T02 desechable. Al validar T03 se inyectó el contenido git limpio → el slot quedó con el Visual T03 limpio (v12, título "SMC Engine — Visual"), corriendo en el chart.
- **Hallazgo documentado:** vía MCP solo persiste de forma fiable **un** slot guardado. `pine_new` (strategy/library) + save NO crearon slots nuevos; el save de la Library (título `library("SMC_Library")`) reusó/sobrescribió el slot homónimo. No es problema: **git es la fuente de verdad** y los 3 archivos compilaron 0/0 sobre su contenido real. Para validación visual solo el Visual necesita estar en el chart.

### F1-S1.1-T03 — BOS / CHoCH (commit abc5988)
- **CORE (byte-idéntico Visual/Strategy + export en Library):**
  - UDT `SMC_Structure` — por escala: `highLevel`/`lowLevel` (último swing high/low confirmado) + flag `crossed` (anti-redisparo) + `bias` (+1/-1).
  - `f_setStructureHigh/Low(st, price, barIdx, barTime)` — fija el swing recién confirmado como nivel estructural vigente y resetea `crossed`.
  - `f_detectStructure(st, breakBarIdx, breakTime, okHigh, okLow)` — ruptura por **CIERRE estricto** (`close > highLevel` / `close < lowLevel`); `tag = bias==BEAR?CHoCH:BOS` (alcista) y `bias==BULL?CHoCH:BOS` (bajista) → BOS rompe el extensor, CHoCH el protector; muta `crossed` + `bias`; devuelve `SMC_Event` (na si no hay).
- **Wiring (DETECCIÓN, ambos consumidores):** `structSwing` (swingLen=5, bias mayor/headline) y `structInternal` (internalLen=3, fino) en instancias separadas. Una ruptura interna NO voltea el bias swing (§1.4). Guard de nivel-distinto del interno (`structInternal.highLevel != structSwing.highLevel`, cf. LuxAlgo `extraCondition`). Todo bajo `barstate.isconfirmed` (anti-repaint D-PINE-03).
- **Dibujo (solo Visual):** `f_drawStructure` — línea del nivel (pivote→ruptura) + etiqueta BOS/CHoCH centrada en el punto medio, **direccional**: alcista teal por encima del nivel (`style_label_down`), bajista rojo por debajo (`style_label_up`). Inputs `i_showStruct` (swing, default ON) e `i_showInternal` (default OFF). Panel: nueva fila **Bias** (Alcista/Bajista/—).

### Decisión clave de algoritmo (paridad)
- Tras leer LuxAlgo `displayStructure` (:551-612) y el oráculo `scripts/ver05/detect.py` (`run_structure`), se eligió la formulación **`close > nivel` + flag `crossed`** (no `ta.crossover`) para máxima paridad con el oráculo ver05 (ADR-002): `crossed` ↔ `topBroken/btmBroken`, `tag` por `bias`. `f_detectStructure` es equivalente línea-a-línea a `run_structure`.

### Corrección visual (pedido de Freddy)
- Las etiquetas BOS/CHoCH estaban al extremo derecho de la línea. 1ª corrección: centradas y todas arriba. 2ª corrección (final): **direccionales** — alcistas arriba, bajistas debajo, centradas. Cambio solo-DIBUJO (no toca CORE).

### Compilación y sincronización
- **Compile 0/0** los 3 archivos en TV (EURUSD H1). ✅
- **check-core-sync.ps1 OK** (207 líneas, SHA `a742779738bee0f2`). ✅

### Validación SMC
- **smc-validator-agent: 97/100 APROBADO** (sin correcciones).
  - 12/12 eventos swing del oráculo `ver05/detect.py` presentes en el chart.
  - 4 casos canónicos: CHoCH baj 06-01 13:00 (1.16101<1.16416, =MSS), BOS baj 06-05 12:00 (1.15866<1.16082), CHoCH alc 05-27 06:00 (1.16456>1.16452), CHoCH alc 05-29 14:00 (1.16687>1.16566).
  - Contraejemplo wick-no-BOS 05-27 12:00 (high 1.16615 supera nivel pero close 1.16440 no rompe → correctamente ausente).
  - Score y detalle en `docs/sprint-runs/validaciones.md`. Screenshots: `t03-bos-choch-direccional.png`, `t03-zoom-0601-0608-mss-bos.png`.

## Decisiones de esta sesión
- Plegar el pendiente de higiene TV en el guardado de T03 (evita trabajo desechable).
- Formulación `close>nivel + crossed` (no `ta.crossover`) por paridad exacta con el oráculo ver05.
- Etiquetas BOS/CHoCH direccionales (alcista arriba / bajista debajo, centradas).
- Estructura interna y swing como instancias `SMC_Structure` independientes; el bias headline = el del swing.

## Estado al cierre
- **Fase:** FASE 1 Sprint 1.1 EN CURSO. **T01 ✅** (S011, 45449f3), **T02 ✅** (S012, aa4ed23), **T03 ✅** (S013, abc5988). Falta **T04** (bias por TF / consolidación MTF) y resto del sprint.
- **Working tree:** limpio tras el commit de cierre.
- **Core sync:** OK (207 líneas, SHA a742779738bee0f2).
- **Rama:** `pine/sistema-completo`.

## Siguiente paso (próxima sesión)
**F1-S1.1-T04 — Bias estructural por TF / consolidación** (reglas-smc-ict §1.4 + Modelo de bias). El bias swing ya se trackea en `structSwing.bias`; T04 lo consolida en `SMC_TFState` (campos `bias`, `lastBOSPrice/Dir/Time`, `lastCHoCHPrice/Dir/Time`) de cara al MTF (Sprint 1.4) y al scoring. Revisar PINE-PLAN para el alcance exacto de T04. Ciclo estándar: check-rule → implement CORE → compile 0/0 → screenshot → smc-validator ≥90 → check-core-sync → aprobación → commit.

## Cambios en archivos (esta sesión)
- `pine/SMC-Library.pine` — añadido `export type SMC_Structure` + `export f_setStructureHigh/Low` + `export f_detectStructure` (+48 líneas).
- `pine/SMC-Visual.pine` — CORE (SMC_Structure + 3 funciones), wiring DETECCIÓN (structSwing/structInternal), `f_drawStructure`, inputs `i_showStruct`/`i_showInternal`, panel fila Bias (+144 líneas netas).
- `pine/SMC-Strategy.pine` — CORE idéntico + wiring (sin dibujo) + bias en el label de estado (+99 líneas netas).
- `docs/sprint-runs/validaciones.md` — fila T03 + sección de detalle (score 97/100).
- `memory/ESTADO-ACTUAL.md` — actualizado en protocolo de cierre.
- `memory/sesiones/Sesion-013.md` — este documento.

## Notas
- TV se desconectó (CDP) una vez a mitad de sesión; relanzado por `tv_launch`. El guardado del Visual T03 persistió antes del crash.
- Higiene TV: queda **resuelta** para el indicador del chart (slot `SMC_Library` = Visual T03 limpio). Strategy/Library no persisten como slots TV separados vía MCP — git es la fuente de verdad.
- Numeración: Sesion-013, secuencial a Sesion-012.
