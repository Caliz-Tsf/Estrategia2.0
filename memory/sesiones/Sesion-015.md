# Sesión 015 — F1-S1.2-T05 Order Blocks + mitigación (WIP, sin commit)
> Fecha: 2026-06-12 · Fase 1 Sprint 1.2 (inicio) · Claude Code (Opus 4.8) + Freddy
> Registro de QUÉ se hizo, POR QUÉ, CON QUÉ FINALIDAD y QUÉ SE DECIDIÓ.
> **ESTADO: TRABAJO EN CURSO — NO COMMITEADO.** El commit + tag + validación
> formal + smc-doc-updater se harán en la PRÓXIMA sesión, cuando se cierren TODAS
> las tareas pendientes (decisión de Freddy).

## Objetivo de la sesión
Iniciar **Sprint 1.2 (Zonas core)** con **F1-S1.2-T05 — Order Blocks + mitigación**:
portar el algoritmo OB de LuxAlgo (reglas-smc-ict §2.1) a funciones puras del CORE
+ máquina de estados de mitigación en el UDT `SMC_Zone`.

## Qué se hizo y por qué

### Implementación (CORE byte-idéntico Visual/Strategy + export en Library)
- **`f_detectOB(ev, originBarIdx, bHighs, bLows, bIdxs, bTimes, bVols, highVolFactor, kind)`**
  — porta `storeOrdeBlock` de LuxAlgo (ref :502-525, v5→v6). El OB es la vela origen
  del impulso que rompe estructura SWING: en ruptura ALCISTA = vela de **mínimo** de la
  pierna `[pivote roto → ruptura]`; en BAJISTA = vela de **máximo**. SWAP high↔low en
  barras de alta volatilidad (`(hi-lo) ≥ highVolFactor×ATR200`, default 2×) para excluir
  la vela de impulso → el OB es la última consolidación ANTES del impulso. Zona =
  `[low, high]` de esa vela (`obBounds = high/low`, §2.1). Solo se llama con ruptura
  CONFIRMADA → no repinta (D-PINE-03).
- **`f_updateZoneMitigation(z, useClose)`** — máquina de **4 estados** del `SMC_Zone`
  (§2.1, más rica que el borrado binario de LuxAlgo): `0 activa → 1 parcial
  (mitigatedPct) → 2 mitigada → 3 invalidada`. OB alcista: cercano=top, lejano/protector
  =bottom; parcial al perforar top, mitigada al alcanzar bottom, invalidada si CIERRA bajo
  bottom (→ Breaker §Tier2). Bajista simétrico. `useClose` = fuente HIGHLOW (default) vs
  CLOSE (obMitigation §2.1). Invalidación (close) prioritaria; INVALID terminal; MITIGATED
  no regresa a parcial.
- **Constante `MAX_BARBUF = 50`→`500`** añadida al CORE (límite del buffer rolling).
- **Dibujo (solo Visual):** `f_drawOB` cajas coloreadas por estado (activa sólida /
  parcial tenue / mitigada gris; alcista teal / bajista rojo; invalida no se dibuja),
  gestión con `SMC_obBoxes` (clear+repintar en `barstate.islast`). Inputs grupo
  `GRP_OB`: `i_showOB`, `i_obHighVolFactor`, `i_obMitClose`.

### Decisión técnica importante — buffers rolling en vez de referencia histórica dinámica
El diseño inicial usaba `high[o]` con índice dinámico para recorrer la pierna. Falló con
**runtime RE10045** (la referencia histórica dinámica excede la historia cargada, ~300
velas; ADR-002) y además **no tiene equivalente limpio en MQL5** (golden tests). Se
rediseñó a **buffers ROLLING de barras** (`obBufHigh/Low/Idx/Time/Vol`, poblados cada
barra confirmada, acotados a `MAX_BARBUF`): `f_detectOB` los recorre con acceso estático
de array → runtime-safe Y portable a golden tests MQL5. Documentado en el header de la
función. **Mejora la paridad MQL5** respecto al diseño original.

### Bug encontrado y resuelto — footgun del `for 0 to size-1` con array vacío
Causa raíz definitiva del RE10045 (persistía tras el rediseño de buffers): el loop
`for i = 0 to array.size(SMC_zones) - 1` con array **vacío** se vuelve `for i = 0 to -1`,
que Pine ejecuta **descendente** (i=0, i=-1) → `array.get` sobre array vacío → RE10045 en
las barras tempranas (antes del primer OB) → halt total (no dibujaba NADA). **Fix:** guard
`if array.size(...) > 0` antes de los loops nuevos (mitigación + dibujo OB) — el mismo
patrón que T02 ya usaba en `f_classifySwing`. El loop interno de `f_detectOB` ya estaba
protegido por `if n > 0`.

## Verificación realizada
- ✅ **Compila 0/0** los 3 (Visual, Strategy, Library) en TV — EURUSD H1.
- ✅ **check-core-sync.ps1 OK** — 313 líneas, SHA `1bb5ad9c07e9ce2f`.
- ✅ **Runtime limpio** (RE10045 resuelto) — 10 cajas OB dibujando; panel Zonas=50.
- Evidencia: `screenshots/t05_ob_eurusd_h1.png`.

## ⚠️ PENDIENTE para la próxima sesión (antes de commit)
1. **BUG A INVESTIGAR — asimetría direccional de OB.** En el chart se ven **varios OB
   bajistas pero solo ~1 OB alcista**. Hacia atrás en el historial deberían verse cantidades
   **aprox. iguales** de OB alcistas y bajistas. Hipótesis a revisar: (a) la condición de
   selección/origen del OB alcista (`structSwing.lowBarIdx` / mínimo de la pierna) o el
   SWAP de volatilidad están sesgando; (b) el dibujo omite alcistas por estado (¿muchos
   marcados mitigados/invalidados?); (c) el bias alcista vigente genera más rupturas
   bajistas registradas. **Diagnóstico requerido antes de validar.**
2. **Validación numérica fina** vs los 3 casos canónicos §2.1 — `data_get_pine_boxes`
   redondea a 2 decimales; usar `smc-validator-agent` (≥90):
   - ✓ OB bajista 2026-06-01 12:00 → `[1.16452, 1.16506]`
   - ✓ OB bajista 2026-06-05 11:00 → `[1.16345, 1.16420]`
   - ✓ OB alcista 2026-06-08 08:00 → `[1.15079, 1.15235]`
3. **Aprobación humana → commit → git tag (si gate) → smc-doc-updater** (ESTADO-ACTUAL +
   esta sesión + checkboxes + `docs/sprint-runs/validaciones.md`).
4. **Higiene TV:** los 3 scripts guardados en TradingView comparten nombre desordenado
   de sesiones previas (todo guardó sobre "SMC_Library"). No afecta archivos locales
   (fuente de verdad) ni compilación; re-guardar limpios con sus nombres.

## Estado al cierre
- **Fase:** FASE 1 Sprint 1.2 — T05 EN CURSO (implementado, compila 0/0, core-sync OK,
  runtime resuelto; **NO validado formalmente, NO commiteado**).
- **Ramas:** `pine/sistema-completo` (desarrollo Pine), `main` estable.
- **Working tree:** SUCIO a propósito — cambios de T05 sin commitear (por decisión de
  Freddy: commit la próxima sesión al cerrar todas las tareas).
- **Core sync:** OK (313 líneas, SHA `1bb5ad9c07e9ce2f`).

## Cambios en archivos (esta sesión, SIN commit)
- `pine/SMC-Visual.pine` — inputs GRP_OB; CORE +`f_detectOB`/`f_updateZoneMitigation`/
  `MAX_BARBUF`; wiring buffers+mitigación+detección OB; dibujo `f_drawOB`+`SMC_obBoxes`;
  panel header "OB T05".
- `pine/SMC-Strategy.pine` — inputs GRP_OB; CORE idéntico; wiring OB (sin dibujo); label "OB T05".
- `pine/SMC-Library.pine` — `export f_detectOB` + `export f_updateZoneMitigation` +
  `export const int MAX_BARBUF`.
- `screenshots/t05_ob_eurusd_h1.png` — evidencia visual (10 cajas OB, runtime limpio).
- `memory/sesiones/Sesion-015.md` — este documento.
- `memory/ESTADO-ACTUAL.md` — actualizado al cierre (estado WIP de T05).

## Notas
- `max_bars_back` se añadió y luego se quitó de las declaraciones `indicator()`/`strategy()`
  al rediseñar a buffers (ya no hay referencia histórica dinámica que lo requiera).
- El alcance de T05 es OB de **escala SWING** (confluencia #19 OB chart). El OB **interno**
  (structInternal) reusa la misma `f_detectOB` y queda anotado para su tarea; los 3 casos
  de prueba §2.1 son todos rupturas swing, así que el alcance cubre la validación.
