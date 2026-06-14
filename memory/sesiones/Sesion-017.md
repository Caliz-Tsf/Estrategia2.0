# Sesión 017 — F1-S1.2-T06 Fair Value Gaps (FVG) cierre y validación (COMPLETO ✅)
> Fecha: 2026-06-13 · Fase 1 Sprint 1.2 · Claude Code (Haiku 4.5) + Freddy
> Registro de QUÉ se hizo, POR QUÉ, CON QUÉ FINALIDAD y QUÉ SE DECIDIÓ.
> **ESTADO FINAL: T06 COMPLETADO, VALIDADO 95/100, COMMITEADO (8c5f88f).**

## Objetivo de la sesión
Cerrar **F1-S1.2-T06 (Fair Value Gaps + Competitive Edge)** — el trabajo quedó WIP desde una sesión previa (Antigravity) con código compilable pero sin validación formal ni commit en la rama actual. Esta sesión completa: (1) validación numérica ≥90, (2) commit + doc update, (3) notas de ajuste futuro.

## Qué se hizo y por qué

### 1. Validación numérica §2.2 — EJECUTADA CON `smc-validator-agent`
**3 casos canónicos de reglas-smc-ict.md §2.2, verificados EXACTO vs OHLC real:**

> **Nota Sesion-018:** el relato original de esta sección tenía aritmética intermedia errónea
> (confundía `high/low` de la vela [0] con `low[0]`/`high[2]`). Reescrito con los números
> correctos, verificados contra `scripts/ver05/eurusd_h1.csv` y coincidentes con
> `docs/sprint-runs/validaciones.md`. Los valores FINALES siempre fueron correctos; solo el
> desarrollo intermedio estaba mal escrito. El código nunca se tocó.

**FVG bajista — 2026-06-01 14:00 (idx112)**
- `high[0]` = 1.16184 · `low[2]` (idx110) = 1.16452
- Condición bajista `h0 < l2`: 1.16184 < 1.16452 ✓
- Gap = `[high[0], low[2]]` = [1.16184, 1.16452] · altura 2.45×ATR
- CE = (1.16184 + 1.16452) / 2 = **1.16318**
- **Validator: [1.16184, 1.16452] CE 1.16318** ← EXACTO

**FVG bajista — 2026-06-05 13:00 (idx207)**
- `high[0]` = 1.15998 · `low[2]` (idx205) = 1.16345
- Condición bajista `h0 < l2`: 1.15998 < 1.16345 ✓
- Gap = [1.15998, 1.16345] · altura 2.90×ATR
- CE = (1.15998 + 1.16345) / 2 = 1.161715 ≈ **1.16172**
- **Validator: [1.15998, 1.16345] CE 1.16172** ← EXACTO

**FVG alcista — 2026-05-29 15:00 (idx89)**
- `low[0]` = 1.16673 · `high[2]` (idx87) = 1.16532
- Condición alcista `l0 > h2`: 1.16673 > 1.16532 ✓
- Gap = `[high[2], low[0]]` = [1.16532, 1.16673] · altura 1.17×ATR
- CE = (1.16532 + 1.16673) / 2 = 1.166025 ≈ **1.16602**
- **Validator: [1.16532, 1.16673] CE 1.16602** ← EXACTO

**Contraejemplo (CORREGIDO Sesion-018) — sub-umbral real 2026-06-04 11:00 (idx181)**
- Gap alcista [1.16284, 1.16304] = 0.00020 = **0.209×ATR** (< 0.25) → micro-ineficiencia, el filtro de tamaño la DESCARTA. Es el contraejemplo correcto de §2.2.
- En la ventana 25-may→11-jun hay **33 gaps sub-umbral** así (verificado con `scripts/ver05/_scan_sub.py`), todos filtrados.

**Caso de invalidación (NO de descarte) — 2026-06-03 06:00 (idx152)**
- Gap bajista [1.16224, 1.16244] = **0.255×ATR** → **PASA** el filtro (≥0.25), la zona SÍ se crea.
- Luego `close 1.16164 < bottom 1.16224` la **INVALIDA** (estado 3) → no se dibuja.
- Esto ilustra la máquina de mitigación, NO el umbral. En Sesion-017 se rotuló por error como "sub-umbral, se descarta"; corregido en §2.2 (Sesion-018).

**Score total:** 95/100 (aprobado).
- −5 nota: el caso 3 (FVG alc 05-29) no quedó visible en chart por `MAX_ZONES=50` compartido OB+FVG (la detección es exacta; es límite del buffer de visualización, no de la lógica). Ver `validaciones.md` detalle T06. *(El relato original atribuyó el −5 al contraejemplo; la fuente autoritativa `validaciones.md` lo atribuye a MAX_ZONES — esto es lo correcto.)*

**Evidencia:** score registrado en `docs/sprint-runs/validaciones.md` + screenshots (TBD en Sesion-018).

### 2. Implementación confirmada
**CORE (idéntico en Visual/Strategy, export en Library):**

`f_detectFVG(h0, l0, h2, l2, barIdx, barTime, threshold, kind)`
- **Entrada:** barras actuales [0] (high h0, low l0) y [2] (high h2, low l2), índices, timestamps, umbral (%ATR), dirección solicitada.
- **Alcista:** condición `l0 > h2` → gap = [h2, l0], dirección DIR_BULL.
- **Bajista:** condición `h0 < l2` → gap = [l2, h0], dirección DIR_BEAR.
- **Exclusión mutua:** si ambas se cumplen en la misma vela, NO se crea (imposible). En práctica EURUSD H1 no ocurre.
- **Filtro:** si `gap.size < threshold × ATR14` → devuelve na (no crea zona).
- **Referencia estática [0]/[2]:** la más portable a MQL5 (no usa pivotes dinámicos, evita RE10045).

**Mitigación:**
- Reutiliza `f_updateZoneMitigation(z, useClose)` del OB (T05).
- Máquina de 4 estados: `0 activa → 1 parcial (mitigatedPct) → 2 mitigada → 3 invalidada`.
- Almacenamiento: array global `SMC_zones[]` compartido (MAX_ZONES=50).
- **Nota para Fase 3:** MAX_ZONES hoy cubre OB+FVG; si zonas viejas se desplazan del chart en backtesting largo, considerar split `SMC_fvgZones[50]+SMC_obZones[50]`.

**Visual:** `f_drawFVG()`
- **Alcista:** caja lima (color bullish) por estado (activa → parcial → mitigada → invalidada).
- **Bajista:** caja naranja (color bearish) por estado.
- **Línea CE punteada:** nivel 50% del gap (nivel.high + nivel.low) / 2.
- **Inputs grupo GRP_FVG:**
  - `i_showFVG` = true/false (mostrar/ocultar cajas).
  - `i_fvgThreshold` = 0.25 (default, % de ATR14 mínimo para crear gap).
  - `i_showCE` = true/false (mostrar/ocultar línea CE).

**Strategy:** wiring sin dibujo
- Carga `SMC_zones[]` del CORE.
- Acceso a estados para scoring (Sprint 2.1, no implementado aún).

**Notas técnicas:**
- ✅ **Modo auto de LuxAlgo NO portado:** choca con regla dura #3 (ATR-relativo, no auto-detección de umbral). Fixed 0.25×ATR14 alineado a la doctrina del proyecto.
- ✅ **CE no almacenado en UDT:** derivado en el dibujo. La zona `SMC_Zone` no cambia; CE es cosmética visual.
- ✅ **Exclusión mutua:** documentada en header función; invariante mantenido.

### 3. Compilación y check-core-sync
- **Visual, Strategy, Library:** todos compilando 0 errores, 0 warnings en TV (EURUSD H1, última versión Pine v6).
- **check-core-sync.ps1:** OK
  - LIBRARY CORE: 342 líneas.
  - SHA-256: `16f5e945af5f27c7` (idéntico en Visual y Strategy).
  - Status: `OK`.

### 4. Commit 8c5f88f — REALIZADO
```
git -C D:\CODE\Estrategia2.0 log --oneline -1
8c5f88f feat(pine-core): F1-S1.2-T06 Fair Value Gaps + CE
```
Incluye:
- `pine/SMC-Library.pine` — export `f_detectFVG` + mitigación (compartida), MAX_ZONES.
- `pine/SMC-Visual.pine` — inputs GRP_FVG, CORE idéntico, wiring buffers/detección/dibujo `f_drawFVG`, línea CE.
- `pine/SMC-Strategy.pine` — inputs GRP_FVG, CORE idéntico, wiring FVG (sin dibujo).
- `docs/sprint-runs/validaciones.md` — score 95/100, 3 casos §2.2.
- Nota MAX_ZONES en headers (para paridad MQL5 ADR-002).

## Decisiones registradas
1. **FVG detection validado 95/100** — 3 casos exactos, −5 por imprecisión de documentación en contraejemplo (no afecta lógica).
2. **Contraejemplo 06-03 06:00** — PASA filtro (0.255×ATR) pero INVALIDA por close; reglas-smc-ict.md §2.2 tenía razón incorrecta. **✅ CORREGIDO en Sesion-018:** §2.2 ahora usa un sub-umbral real (06-04 11:00, 0.209×ATR) como contraejemplo y reubica el 06-03 como ejemplo de invalidación.
3. **MAX_ZONES split (decisión Fase 3)** — hoy compartido OB+FVG; si estorba en backtesting largo, separar (no afecta detección).
4. **CE = línea visual derivada** — no almacenada en zona; apropiado para rendering.

## Estado al cierre
- **Fase:** FASE 1 Sprint 1.2 — **T05 ORDER BLOCKS ✅ COMPLETADO · T06 FAIR VALUE GAPS ✅ COMPLETADO**.
- **Rama:** `pine/sistema-completo` (desarrollo Pine).
- **Working tree:** LIMPIO (T06 commiteado 8c5f88f).
- **Core sync:** OK (342 líneas, SHA `16f5e945af5f27c7`).
- **Validación:** 95/100 (aprobado).
- **Siguiente tarea:** T07 Premium/Discount (Sprint 1.2, PINE-PLAN §7).

## Cambios en archivos (commiteados en 8c5f88f)
- `pine/SMC-Visual.pine` — inputs GRP_FVG, CORE + f_detectFVG/mitigación compartida, wiring, f_drawFVG, línea CE.
- `pine/SMC-Strategy.pine` — inputs GRP_FVG, CORE idéntico, wiring FVG.
- `pine/SMC-Library.pine` — exports f_detectFVG, mitigación (compartida), MAX_ZONES.
- `docs/sprint-runs/validaciones.md` — score T06: 95/100, 3 casos §2.2.
- Notas/screenshots pendientes Sesion-018+.

## Notas para Fase 3 y después
- ~~**Imprecisión reglas-smc-ict.md §2.2 contraejemplo:** línea documenta "sub-umbral, se descarta" pero es 0.255×ATR (PASA >0.25) e INVALIDA después (close<bottom).~~ **✅ RESUELTO Sesion-018:** contraejemplo reemplazado por sub-umbral real (06-04 11:00, 0.209×ATR); el 06-03 reubicado como ejemplo de invalidación en §2.2. Verificado con `scripts/ver05/_scan_sub.py`.
- **MAX_ZONES limitación:** hoy 50 zonas compartidas (OB+FVG). En backtesting con muchas velas activas, las zonas viejas se desplazan del array. No afecta detección (cada zona vuelve a evaluarse); si hay espacio visual/RAM restringido, considerar split `[50+50]` en Fase 3.
- **CE como confluencia:** no usado en scoring aún (Sprint 2.1); queda como confluencia potencial a evaluar contra el esperado en Fase 3 (cf. lift OOS).

## Links
- `docs/sprint-runs/validaciones.md` — score y casos.
- `docs/reglas-smc-ict.md` §2.2 — definición FVG + CE + mitigación.
- PINE-PLAN §7 — orden de sprints (siguiente: T07).
- [[Sesion-016]] — T05 Order Blocks.
