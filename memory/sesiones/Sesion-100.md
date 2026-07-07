# Sesión-100 (2026-07-06)

## Objetivo
Continuar la agenda S099: root cause de BUG #1, documentar BUG #2 (P/D) en vivo, y barrido fino de familias en Operación — con `docs/planes/BUGS-VISUAL-fable-revision.md` como base para entregar a Fable. Firma F1-GATE (sigue bloqueada).

## Decisión del usuario (esta sesión)
NO aplicar el fix de BUG #1 ahora. Guardar el bug documentado y **continuar el barrido de las familias NO bloqueadas por BUG #1** para cazar más bugs e integrarlos al MISMO documento → entregar a Fable **UNA sola vez** (consolidado).

## Completado

### 1. BUG #1 — ROOT CAUSE CONFIRMADO (análisis estático, alta confianza)
`chartState.atr14` **NUNCA se asigna** en `SMC-Visual.pine`:
- Únicas asignaciones a `chartState` = `pdHigh`/`pdLow` (líneas 1962-1963).
- `f_updateTFState` (única función que muta `chartState` por referencia, línea 1980) solo toca `bias`/`lastBOS*`/`lastCHoCH*`.
- El ATR local `atr14` (línea 2006) nunca se copia a `chartState.atr14` → queda en su default de UDT (`na`).

**Mecanismo del fallo:** la población de anclas + band-pick (línea 2886) cuelga de `if not na(aAtr) and aAtr > 0` con `aAtr = chartState.atr14` (línea 2888/2893) → SIEMPRE FALSE → `anchorHiIdx/anchorLoIdx` y `bandPickIdx` quedan vacíos → en Operación (`densMin=2`) ninguna nativa pasa `f_densOK(anchor) OR f_isBandPick`. La ruta MTF (`f_drawMTFZones`) no lee `chartState.atr14` → sí dibuja. Explica el síntoma exacto y la asimetría Operación vs Estudio/Todo. El fallo está **aguas arriba** del band-pick (por eso volcar band/state en S099 no revelaba nada).

**Descartado formalmente:** índices `i` desalineados — `SMC_zones` no se muta en Visual (0 `array.push(SMC_zones` en el archivo); población y loops de dibujo recorren el mismo array final en `islast`.

**Efectos colaterales del mismo `na`:** `f_posRole` siempre INTERNO, bandas 4/5 muertas, ribbon KZ colapsado (todos se sanan con la misma asignación).

**Fix candidato (para que Fable confirme/apruebe):** `chartState.atr14 := atr14` una vez por barra, SIN gatear en `isconfirmed` (ATR necesario en barra viva para el dibujo `islast`, a diferencia del snapshot P/D). + 3 preguntas para Fable. Confirmado en vivo H1 y M5.

### 2. BUG #2 (Premium/Discount) — CERRADO, no era bug
Barrido en vivo (Operación), grid P/D numéricamente correcto en los 3 TFs:
- **H1** [1.13618, 1.14730], precio 1.14401 → Premium 71% ✓ (EQ 1.14174 / LQ 1.13896 / UQ 1.14452 exactos).
- **M5** [1.14085, 1.14481], precio 1.14414 → Premium 82% ✓.
- **D1** [1.13246, 1.20831] → Discount 15% ✓.

El "Discount camina hacia el precio en tendencia" es la **Opción A** operando como se diseñó (trailing extremes LuxAlgo), ya decidida y re-confirmada 2× (S057/S091), diferida a Fase 3. Cierra el placeholder de BUG #2.

### 3. BUG #3 (nuevo) — contador "Ocultos" sub-reporta Est/EQ nativas en M5
En M5 Operación la fila **Ocultos** reporta `Est 0 · EQ 0`, pero el panel `EQ H/L` (columna M5) = 81 detectados y solo se dibujan 2 EQH → ~79 no mostradas contadas como 0. En H1 el mismo contador sí funciona (`Est 498 · EQ 105`). Causa (código estático): `EQ H/L` M5 = `array.size(SMC_eqhl)` (detectados, línea 4342); `hidEq`/`hidStruct` (líneas 3336/3195) miden solo el recorte de `f_keepBestPerBand` sobre las labels DIBUJADAS, no `detectado − dibujado` → rompe §10-#8 "nada desaparece en silencio". Solo panel/presentación, independiente de BUG #1. + 2 preguntas para Fable.

### 4. Barrido de familias no-bloqueadas por BUG #1 (H1 + M5)
A1 Estructura, A4 Liquidez, A5 P/D, A6 Gaps (NDOG/NYMO), A7 MTF: dibujan OK. Verificado que las cajas MTF heredadas SÍ extienden a la barra actual (falsa alarma descartada). **A2 OB / A3 FVG nativos DIFERIDOS a post-fix de BUG #1** (ahora no dibujan; cualquier barrido solo re-confirmaría #1).

## Commits
1. `8ca2f6d` — `docs(fase1): S100 BUGS-VISUAL — root cause BUG #1 confirmado + BUG #2 cerrado + BUG #3` (doc-only).

## Pendiente (S101)
1. **Fix de BUG #1** — delegado a Fable con el doc, o aplicarlo el usuario/Claude (`chartState.atr14 := atr14`).
2. **Barrido D1 + concepto-por-concepto con toggles** (apagar todo → encender uno) — no hecho aún.
3. **Re-validar A2/A3 OB/FVG nativos post-fix.**
4. **Firma F1-GATE — SIGUE BLOQUEADA por BUG #1.**
5. Entregar el documento consolidado a Fable UNA sola vez cuando el usuario decida.

## CORE
- **Intacto:** 1700 líneas SHA `5510361166844bd5`, compila 0/0 los 3, core-sync OK.
- **Sin ADR nuevo, sin gate/tag.**

## Notas
- El doc `BUGS-VISUAL-fable-revision.md` ahora contiene BUG #1 (root cause + fix candidato + 3 preguntas), BUG #2 (cerrado), BUG #3 (abierto + 2 preguntas) y el checklist por familia actualizado.
- Memoria [[bug-ob-cercano-no-dibuja-operacion]] actualizada con root cause + resultado del barrido.
- Enlaces: [[Sesion-099]], [[Sesion-098]], [[fork-rediseno-proyeccion-s7]].

---

**Sesión cerrada. Root cause de BUG #1 confirmado, BUG #2 descartado, BUG #3 abierto. Documento consolidado listo para Fable. F1-GATE sigue bloqueada.**
