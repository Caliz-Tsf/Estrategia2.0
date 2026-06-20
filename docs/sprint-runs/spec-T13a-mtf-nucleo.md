# Spec — F1-S1.4-T13a · Mapa MTF núcleo (`f_computeTFState`, escalares)

> Sprint 1.4 · rama `pine/sistema-completo`. Fuente de diseño: `docs/planes/ESQUELETO-P3-mapa-mtf-confluencias.md` §2.4/§4.1; gate técnico `docs/sprint-runs/spike-R-P3-1.md` (✅ S039); ADR-008. Aprobación humana del gate P3+ADR-008: Sesión-040.
> **Alcance T13a = SOLO escalares.** El mapa rico (N zonas/lado, `f_nearestN`, cascada de zonas) es **T13b**.

## Objetivo

Encapsular la cadena de detección de **escalares** de un TF (bias + BOS/CHoCH + MSS + P/D + EMAs + ATR) en una función única `f_computeTFState`, evaluable vía `request.security(sym, tf, f_computeTFState(...), lookahead = barmerge.lookahead_off)` **sin contaminar el contexto del chart** (R-P3-1, ya verificado en el spike S039). Traer D1 y H1 al chart, reconstituirlos y dibujarlos en cascada con estilo diferenciado.

## Contrato del tuple plano (canónico — replicar en MQL5 `SMC_MTF.mqh`, Fase 4)

`f_computeTFState(int swingLen, int pdLen, float dispFactor, float bodyPct)` devuelve, **en este orden exacto** (R-P3-2: `request.security` no transporta UDT/array, solo números):

| # | campo | tipo | origen |
|---|---|---|---|
| 1 | bias | int (DIR_*) | `f_updateTFState` sobre ruptura swing |
| 2–4 | lastBOSPrice, lastBOSDir, lastBOSTime | float,int,int | último BOS swing |
| 5–7 | lastCHoCHPrice, lastCHoCHDir, lastCHoCHTime | float,int,int | último CHoCH swing |
| 8–10 | lastMSSPrice, lastMSSDir, lastMSSTime | float,int,int | `f_detectMSS` del CHoCH de la barra |
| 11–13 | pdHigh, pdLow, pdMid | float | dealing range P/D (`SMC_Trailing`) |
| 14–16 | ema20, ema50, ema200 | float | `ta.ema(close, n)` |
| 17 | atr14 | float | `ta.atr(14)` |

**Presupuesto:** 17 valores ≪ ~127 (límite tuple v6). Holgura amplia para T13b (R-2 pendiente: confirmar límite exacto).

## Reglas duras aplicadas

- **R-P3-1 (no contaminación):** todo el estado de la función es `var` **interno** (`st`/`structTf`/`trailTf`), nunca `var` global del consumidor. Verificado por el spike (S039).
- **R-P3-2 (aplanado y capado):** tuple de números; sin objetos/arrays. T13a no transporta zonas (eso es T13b).
- **Regla #1 anti-repaint:** `lookahead = barmerge.lookahead_off` SIEMPRE; eventos (estructura/MSS) solo en `barstate.isconfirmed`. Las EMAs/ATR/P/D-expand corren cada barra (series consistentes).
- **Regla #2 core-sync:** `f_computeTFState` + extensión de `SMC_TFState` van al `// === LIBRARY CORE ===` byte-idéntico (Visual/Strategy) + `export` en Library. SHA cambia (esperado, documentado en commit).
- **Regla #3 ATR-relativo / Regla #8 gates:** sin umbrales nuevos; T13a es refactor + transporte, no calibración.

## Cambios

1. **CORE — UDT `SMC_TFState`:** añadir campos `lastMSSPrice/Dir/Time`, `pdMid`, `atr14` (ema20/50/200 ya existían sin poblar). Byte-idéntico × 3.
2. **CORE — `f_computeTFState`:** nueva función al final del CORE (tras `f_killZone`), byte-idéntica Visual/Strategy + `export` Library. Reusa helpers existentes; estado `var` interno.
3. **Consumidores — sección `=== MTF ===`:** 2 `request.security` (D1="D", H1="60") + reconstitución a `var SMC_TFState d1State/h1State`. Idéntico en ambos (no es CORE; igual por higiene).
4. **Visual — INPUTS `GRP_MTF`:** `i_showD1`, `i_showH1` (toggles de cascada).
5. **Visual — DIBUJO:** `f_drawMTFState` (presentación, no CORE): niveles P/D del HTF como líneas punteadas tenues con prefijo `"D1:"`/`"H1:"` + marca de bias. Cascada: solo se hereda hacia TF estrictamente menores (`timeframe.in_seconds()` guard).
6. **Strategy — PANEL:** referenciar `d1State.bias`/`h1State.bias` en el label de estado (evita warning de variable sin usar; los escalares quedan listos para el scoring Sprint 2.1).

## Done medible (ESQUELETO-P3 §4.1)

- [ ] Compila **0/0** los 3 (EURUSD, chart H1 y M5).
- [ ] `check-core-sync.ps1` = OK (SHA nuevo documentado).
- [ ] D1 y H1 bias + niveles P/D visibles en M5/H1 con prefijo, estilo diferenciado.
- [ ] **Anti-repaint verificado:** `lookahead_off`; valores HTF no repintan al cerrar la barra del chart.
- [ ] Validación ≥90 (paridad visual D1/H1 del mapa vs cambio de TF manual).

## Fuera de alcance (T13b+)

- N zonas/lado (OB/FVG/pool/sweep) por `request.security` aplanado y capado (`N_htf≈3`).
- `f_nearestN` pura en CORE; reconstitución + dibujo en cascada de **zonas** con cuota de objetos.
- Panel multi-columna (T14), alertas MTF (T15).
