# Sesion-082 (2026-07-02)
> Paso 2 de Gradient Levels: cableado P2/P3 + `f_selectGradientSource` + ghost/persistencia. Fase 1 · rama `pine/sistema-completo`. 1 commit Pine + 1 de docs.

## Objetivo

Ejecutar el **paso 2** del plan S082: completar el cableado de Gradient Levels tras P1 (dealing range) — construir los rangos-fuente **P2 (suspension diario)** y **P3 (opening gaps en paralelo)**, la selección determinista `f_selectGradientSource`, el re-wire de T43 `gradedFvg` al alcance completo, y el ghost/persistencia del grid. Bajo gate [[sprint16-gate-reglas-antes-de-codigo]].

## Decisiones del usuario (AskUserQuestion)
1. **Alcance selección = COMPLETO/fiel a la regla:** `f_selectGradientSource` elige el grid ganador (P1 default, P2 cuando P1 stale/gana desempate) Y `gradedFvg` evalúa contra el grid seleccionado + grids P3 en paralelo. Cambia el comportamiento validado de T43 → re-validar en S083.
2. **Lanzar TV** para extraer casos EURUSD P2/P3.

## Completado

### 1. Casos EURUSD extraídos (TV MCP, D1 OANDA:EURUSD)
- **P2 suspension diario** (último día D1 **confirmado**, ts 1782853200 ≈ 2026-06-30): high=`1.14233`, low=`1.13618`, span 0.00615. Grid `0→1.13618 · 0.25→1.13772 · 0.5→1.13926 · 0.75→1.14079 · 1→1.14233`. La low=eighth 0.125 del grid H1 (confluencia P1∩P2). Día en formación excluido (anti-repaint).
- **P3 opening gap**: único real = fin de semana (Vie ts1782421200 close `1.13850` → Lun ts1782680400 open `1.13897`), mini-rango `[1.13850, 1.13897]`, span 0.00047.
- **Contraejemplo P3**: gaps intra-semana FX ~0.00001–0.00002 < gapMin·ATR → no-measurable, no generan grid. Registrados en regla §5.16.

### 2. CORE — `f_selectGradientSource` (byte-idéntico Visual/Strategy, export Library)
Pura: recibe niveles P1/P2 ya calculados + arrays open/close recientes; P1 por defecto; P2 desafía SOLO cuando P1 stale (`bar_index - trailing.barIdx > gradStaleBars`) y gana `f_bodyRespectsLevel` (desempate cuerpos-vs-nivel). Devuelve `[top, bottom, srcKind]`. CORE 1615→1647 líneas, SHA `0ae1f9de2ea3cd23`.

### 3. Cableado consumidores (Visual + Strategy)
- **P2**: `request.security(syminfo.tickerid, "D", [high[1], low[1]], lookahead_off)` = highest/lowest del último día D1 confirmado (anti-repaint, TF-agnóstico).
- **P3**: mini-grids measurables (`|open−close[1]| ≥ gapMin·ATR`) en `SMC_gapGrids` (cuota `gradPersistDays`).
- **T43 `gradedFvg` (alcance completo)**: `f_nearGradientLevel(CE)` contra `gradSelLevels` (grid ganador) + cada grid P3.
- **Ghost/persistencia**: `SMC_gradGhosts` — archiva el grid primario al RE-FIJARSE la fuente (cambio de kind / nuevo swing barIdx / nueva frontera día), hasta `gradPersistDays`. Dibujo Visual tenue (solo quadrants, gris); Strategy mantiene el estado por paridad de cálculo, no dibuja.
- **Inputs nuevos**: `gradStaleBars=150`, `gradBodyLookback=5`, `gradPersistDays=5` (+ `gradEighths` en Strategy).

### 4. Verificación
- Compila **0/0** los 3 (`pine_check.py` server-side, mismo endpoint que el MCP).
- **core-sync OK** — CORE byte-idéntico Visual/Strategy, SHA `0ae1f9de2ea3cd23` (1647 líneas).
- **Render vivo H1** (indicador inyectado v105, slot `SMC_Library`): 0 errores; P1 seleccionado (dealing range NO stale → sin sufijo "s"); `LQ 1.13990`/`UQ 1.15477` exactos → comportamiento validado T41/T43 (96/98) **intacto**. Maquinaria P2/P3/selección/ghost activa pero dormante en este escenario (P1 fresco). Screenshot `S082-gradient-P2P3-selection-ghost.png`.

## GOTCHAs de la sesión
- **CDP cayó 2×** (TV Desktop se reinició) → `tv_launch` de nuevo.
- **`pine_open` matchea por NOMBRE de slot** (`SMC_Library`), NO por título ("SMC Engine — Visual") → usar el nombre. `pine_inject.py` no depende de eso (CDP directo al Monaco).

## Commits
- `8edbcf4` — `feat(pine-core): F1-S1.7 Paso 2 — Gradient Levels P2/P3 + selección + ghost` (4 archivos: CORE ×3 + regla §5.16).
- `3372505` — `docs(estado): S082 — Paso 2 Gradient Levels completo`.

## Siguiente sesión (S083)
1. **⚠️ Re-validación FORMAL `smc-validator-agent` de T43** (alcance completo P1/P2/P3) — el path P1 no cambió, pero falta escenario con P1 stale (→P2) y con FVG cerca de gap (→P3).
2. **PASO 3 = Eje 2 "FUERZA" / orden visual**: motor `strength` (`f_zoneStrength`/`f_eventStrength`/`f_strengthLevel`) + jerarquía §6 (Primario/Secundario/Terciario) + densidad/antisolape (grid gradient+P/D se solapa con Kill Zones). Incluye crear fichas §6.3.36-39 (gradient) que §5.16 ya referencia.

Ver [[Sesion-081]] · [[ESTADO-ACTUAL]] · [[s054-esqueleto-discriminacion-visual]].
