# Sesion-110 — PASOS B, C, D ESQUELETO CONTEXT HTF REVELADO
**Fecha:** 2026-07-08  
**Objetivo:** Ejecutar Pasos B, C, D del esqueleto `docs/planes/ESQUELETO-FABLE-context-htf-revelado.md` (tercer consumidor visual auxiliar SMC-Context.pine para herencia de extremos HTF + revelado al romper).  
**Estado:** ✅ COMPLETADA (Pasos B, C, D). Pasos E (dibujo) y F (validación matriz) pendientes S111.

## Completado

### PASO B (doc-only, reversible) — commit `077df4d`
- **ADR-017:** nuevo `docs/adrs/ADR-017-consumidor-visual-auxiliar-context.md` escrito, estado "Aceptada — Fase A". Describe tercer consumidor visual auxiliar `pine/SMC-Context.pine` (indicator overlay, solo dibuja). Byte-idéntico LIBRARY CORE + 2ª request.security con f_tfExtremes fuera del CORE. Alternativas descartadas: (a) dentro del Visual→CE10117; (b) ensanchar tuple del CORE→Fase B. Precisa ADR-009/010/014/016; no toca ADR-002.
- **check-core-sync.ps1 extendido:** nuevo parámetro opcional `$ContextPath` (default pine/SMC-Context.pine). Verifica los 3 scripts si el archivo existe; si no existe, comportamiento intacto (backward-compatible Fase 0/CI). Solo-ASCII (PS 5.1). Probado 3-vías: verde con Context idéntico, exit 1 DIVERGENT con Context mutado.
- **Notas en documentación:** CLAUDE.md (Arquitectura línea consumidor auxiliar opcional ADR-017; regla dura #2 menciona los 3) + docs/workplan/PINE-PLAN.md (párrafo consumidor auxiliar).
- **§Z del esqueleto:** fila B marcada ✅.

### PASO C (código real) — commit `ec9a1bd`
- **`pine/SMC-Context.pine` creado (~1944 líneas):** header con atribución LuxAlgo + `indicator("SMC Engine — Context (HTF)", overlay, max_*_count=100)` + inputs GRP_CTX (i_extOn, i_ctxAlways, i_kExt=6.0, i_extMinStrength=0.5, i_revealHyst=1.0) + inputs de detección con MISMOS defaults que el Visual (i_swingLen 5, i_pdSwingLen 50, i_mssDispFactor 1.5, i_mssBodyPct 0.70, i_eqlLength 3, i_eqThreshold 0.1, i_obHighVolFactor 2.0, i_obMitClose false, i_fvgThreshold 0.25, i_poolTol 0.1, i_minTouches 2).
- **LIBRARY CORE copiado VERBATIM:** del Visual (L143-1842), SHA `5510361166844bd5`, byte-idéntico. Validado con check-core-sync.ps1.
- **Selectores puros nuevos (fuera del CORE, RE10045-safe):**
  - `f_farthestZone`: zona kind no-mitigada más lejana de px en el lado, strength>=minStr, dentro de bound.
  - `f_farthestPool`: pool no-barrido touches>=minT.
  - `f_farthestEvent`: EQH/EQL sobre buffers evK/evL/evD/evTA/evTB, sin filtro strength.
- **`f_tfExtremes`:** misma cadena de detección que f_computeTFState (cuerpo copiado verbatim L1687-1790) pero emisión cambia: en vez de nearest-N, emite el extremo importante por concepto/lado. Tuple plano de 51 = 3 escalares (pdHigh/pdLow/atr14) + 8 slots×6 campos {kind,top,bottom,dir,tA,tB}. Orden slots: OB↑,OB↓,FVG↑,FVG↓,POOL↑,POOL↓,EQ↑,EQ↓. Ranura vacía = kind 0 + nas (ADR-010). Alcance v1 = OB/FVG/POOL/EQ (MB/Breaker/BOS-CHoCH lejanos = v2/Fase B).
- **2 call-sites globales:** request.security D1 ("D") y H1 ("60") con f_tfExtremes, lookahead_off. Igual que el Visual: se piden D1/H1 SIEMPRE (cascada por chart-TF la resuelve el revelado). Plots de depuración TEMPORALES (se reemplazan por dibujo real en Paso E).
- **Generador reproducible:** gen_context.py en scratchpad (NO commiteado) garantiza CORE byte-idéntico.
- **Validación:** check-core-sync ×3 = CORE_SYNC=OK mismo SHA; pine_check.py = CLEAN_0_0; **APPLY VIVO** (OANDA:EURUSD H1, slot SMC_Context id 9rxgph) esperado 22s → 0 errores, SIN CE10117/OOM, conviviendo con Visual (MQVk7q) + LuxAlgo (3 estudios). Emite valores REALES: ctxD1_pdH=1.20831, ctxH1_pdH=1.14730, chk_kind=89 (slots pobladas). f_tfExtremes corre de punta a punta.
- **§Z del esqueleto:** fila C marcada ✅.

### PASO D (revelado al romper) — commit `b9a2447`
- **Sección REVELADO AL ROMPER:** máquina DORMANT⇄REVEALED por HTF y lado (revD1Up/revD1Dn, revH1Up/revH1Dn) con histéresis i_revealHyst×ATR (anti-parpadeo); solo close CONFIRMADO (regla dura #1 anti-repaint).
- **Al romper el Premium/Discount vigente del HTF** se activa ese lado; se re-oculta al volver dentro.
- **Cascada por chart-TF:** 
  - chart D1 = sin contexto (nativo)
  - chart H1 = solo D1
  - chart M5 = D1+H1
  - Gate vía timeframe.in_seconds (ctxD1Applies=chartSec<1D, ctxH1Applies=chartSec<60)
  - Flags showD1Up/Dn, showH1Up/Dn.
- **Plot reveal_bits** (display.data_window) para observar el estado en vivo.
- **Validación:** core-sync ×3 OK, pine_check 0/0, APPLY VIVO 22s sin CE10117/OOM. reveal_bits=0 = DORMANT correcto (precio 1.14193 dentro del rango D1; H1 no aplica en chart H1). El camino REVEALED-al-romper se valida en Paso F (chart_scroll_to_date a una ruptura histórica). Nota: intento de forzar i_ctxAlways=true vía indicator_set_inputs no casó la clave (no bloqueante, validación diferida a F).
- **§Z del esqueleto:** fila D marcada ✅.

## Notas técnicas
- **CORE de Visual/Strategy INTACTO los 3 pasos:** SHA `5510361166844bd5`, 1700 líneas, compila 0/0 los 3 (ahora Visual+Strategy+Context), core-sync OK ×3.
- **Slot TV SMC_Context:** id c098abf3 / entity 9rxgph en chart, contiene ahora el código real (reemplazó el probe de S109).
- **Método TV:** pine_inject.py + Ctrl+Enter (ui_keyboard) + espera 22s + pine_get_errors; pine_check.py NO cuenta tokens (CE10117 solo en apply vivo).

## Pendiente S111
- **PASO E (dibujo §5.4) — BLOQUEADO por Tarea #2 S108 (regla de solape MTF).** Decisión del usuario S110: adoptar propuesta mínima de Fable → heredado-lejano SIEMPRE detrás, transparencia escalonada nativo<H1<D1, si dos cajas solapan >70% del rango de la menor → solo la del TF mayor. Slots de dibujo FIJOS (var box/label, máx 8 boxes+8 labels/HTF, box.set_* en islast, RE10045-safe). Estilo §5.4 (hue familia COL_OB/COL_FVG/COL_LIQ, transparencia alta, borde punteado, tag D1▲/D1▼). Anclaje xloc.bar_time (patrón f_drawMTFZones del Visual).
- **PASO F (validación matriz 1-7):** incluye ruptura histórica con chart_scroll_to_date, verificar revelado sin parpadeo, i_ctxAlways, cascada M5, convivencia, sin CE10117/RE/OOM, core-sync ×3.
- **Fuera de alcance v1 (anotado):** MB/Breaker/BOS-CHoCH extremos (v2), promoción al CORE (Fase B), Parte A mitigadas gris (F1-CTX-04), Tarea #3 calibración i_kLeg.

## Commits
- **`077df4d`** — PASO B (doc-only): ADR-017 + check-core-sync extendido + notas CLAUDE.md/PINE-PLAN.md
- **`ec9a1bd`** — PASO C (código real): SMC-Context.pine 1944 líneas, f_tfExtremes, 2 security calls, plots temporales, validación vivo 0/0
- **`b9a2447`** — PASO D (revelado): máquina DORMANT⇄REVEALED, cascada por chart-TF, plot reveal_bits, validación 0/0

## Sin gate de fase
Progreso dentro de Fase 1, sin tag. ADR nuevo: ADR-017 (escrito en Paso B).

---
**Enlaza con:** [[Sesion-109]], [[Sesion-108]], `docs/planes/ESQUELETO-FABLE-context-htf-revelado.md`, `docs/adrs/ADR-017-consumidor-visual-auxiliar-context.md`
