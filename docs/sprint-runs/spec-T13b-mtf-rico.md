# Spec — F1-S1.4-T13b · Mapa MTF rico (buffer genérico etiquetado, `f_nearestN`)

> Sprint 1.4 · rama `pine/sistema-completo`. Diseño: **ADR-009** (transporte buffer genérico etiquetado) + `ESQUELETO-P3 §2.5` (cascada/dibujo). Base: T13a (`spec-T13a-mtf-nucleo.md`, escalares ✅). Gate técnico: spike R-P3-1 ✅ S039.
> **Alcance T13b = zonas/eventos activos del HTF en cascada.** El selector de POI (§3.4) y el scoring son Fase 2.

## Objetivo

Ampliar `f_computeTFState` para que, además de los 17 escalares (T13a), corra **internamente** (estado `var` interno, R-P3-1) la detección de OB/FVG/pools/sweep del HTF y emita los **K objetos activos más cercanos al precio** como un **buffer genérico etiquetado por `kind`** (ADR-009). El consumidor los reconstituye y dibuja en cascada D1→{H1,M5}, H1→{M5} con estilo diferenciado y cuota de objetos.

## Contrato del tuple (canónico — replicar en MQL5 `SMC_MTF.mqh`)

`f_computeTFState(...)` devuelve, en orden: **[17 escalares T13a] ++ [K ranuras × 5]**.

- Ranura `i`: `[ kind_i, top_i, bottom_i, dir_i ]` (ADR-009, 4 campos; se omite barTime). `kind=0` = ranura vacía. Para puntos (sweep/pool) `top==bottom==level`.
- **K = `MTF_K` = 16.** Total = `17 + 16×4 = 81 < ~127` (1 llamada `security`/TF). Límite empírico a confirmar al compilar (R-2).

## Cambios

### CORE (byte-idéntico ×3 + export en Library)
1. **Const nuevas:** `KIND_POOL = 8` (pool como objeto del buffer; dir = BSL/SSL); `MTF_K = 16`; `MTF_SLOT = 4`.
2. **`f_nearestN(array<SMC_Zone> src, int kind, float px, int capN, array<int> ck, array<float> ct, array<float> cb, array<int> cd, array<float> cdist)`** — pura. Recorre `src`, filtra `kind` + `state < ZS_MITIGATED`, y **anexa** a los arrays-candidato compartidos los **capN más cercanos al precio**. Generaliza `f_pNearZone` (presentación, devuelve 1). Variante `f_nearestNPools` filtra `not swept` y etiqueta `KIND_POOL`.
3. **`f_computeTFState` ampliada:** acepta los params de OB/FVG/pool (`internalLen, eqlLength, eqThreshold, obHighVolFactor, obMitClose, fvgThreshold, poolTol, minTouches`) + caps por concepto + toggles de traspaso. Corre OB/FVG/pool/sweep con `var` arrays internos (mismos helpers que el consumidor: `f_detectOB`/`f_detectFVG`/`f_detectEQHL`/`f_upsertPool`/`f_markPoolsSwept`/`f_detectSweep`/`f_prunePools`/`f_updateZoneMitigation`). Selecciona y aplana las K ranuras. **Anti-repaint:** eventos en `barstate.isconfirmed`; `lookahead_off` lo pone el llamador.

### Consumidor (Visual + Strategy, idéntico por higiene, NO core-sync)
4. **Sección `=== MTF ===`:** 2 `request.security` (D1, H1) con el tuple ampliado → reconstitución de las K ranuras a arrays ligeros por TF.
5. **Visual — INPUTS `GRP_MTF`:** por concepto (OB/FVG/pool): toggle de traspaso `i_mtf_<c>` + cap `i_mtf_<c>_n` (0-10, cap efectivo a `MTF_K`). Toggles maestros `i_showD1`/`i_showH1` (ya existen).
6. **Visual — DIBUJO cascada de zonas:** `f_drawMTFZones` (presentación, no CORE) dibuja cada ranura según su `kind` con estilo tenue/punteado + prefijo `D1:`/`H1:`. **Cuota de objetos por (concepto × TF) + Present mode** (R-3): solo se dibujan las K cercanas (ya capadas en transporte). Herencia solo a TF estrictamente menores (`timeframe.in_seconds`).
7. **Strategy:** reconstitución idéntica + wiring mínimo (las ranuras quedan listas para el scoring Sprint 2.1).

## Reglas duras aplicadas
- **R-P3-1:** estado de detección HTF `var` interno a `f_computeTFState` (verificado spike S039).
- **R-P3-2 / ADR-009:** tuple plano capado; buffer genérico etiquetado, no slots por concepto.
- **Regla #1:** `lookahead_off` + eventos en `barstate.isconfirmed`.
- **Regla #2:** `f_nearestN` + `f_computeTFState` en CORE byte-idéntico; SHA nuevo documentado.
- **Regla #8:** 1 llamada/TF ahora; 2ª llamada preparada sin refactor (no sobre-construir).

## Done medible
- [ ] Compila **0/0** los 3 (EURUSD, chart M5 y H1).
- [ ] `check-core-sync.ps1` = OK (SHA nuevo documentado).
- [ ] Zonas OB/FVG/pool de D1 y H1 dibujadas en cascada en M5 con prefijo/estilo diferenciado.
- [ ] Mitigación dinámica: al mitigarse la zona más cercana, aparece la siguiente.
- [ ] Presupuesto de objetos bajo 500/tipo; presupuesto de tuple confirmado < límite v6.
- [ ] **Anti-repaint:** valores HTF no repintan al cerrar la barra del chart.
- [ ] Validación ≥90 (paridad: zonas HTF del mapa vs cambio manual de TF a D1/H1).

## Fuera de alcance (T14+)
- Panel multi-columna (T14), alertas MTF (T15).
- 2ª llamada `security`/TF (preparada, no activada).
- Selector de POI `f_selectEntryPOI` + scoring (Fase 2).
- Poblar el buffer con conceptos aún no detectados (Sprint 1.5/1.6: breaker, BPR, IDM, gaps…) — el mecanismo ya los admite vía `push` + `kind`.
