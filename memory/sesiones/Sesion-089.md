# Sesión 089 — 2026-07-03

**Rama:** `pine/sistema-completo` · **Fase:** 1 · Eje 2 "Fuerza" (esqueleto Fable §11.2)
**CORE:** intacto — 1700 líneas SHA `5510361166844bd5`, core-sync OK, compila 0/0 los 3.
**Tipo:** Visual-only (6 commits, 3 de ellos con crash diagnosticado y arreglado) + validación en vivo TV + aplicación autónoma del indicador.

## Objetivo
Cerrar el gate visual ≤25 labels del Eje 2 "Fuerza", completando Paso 6 §6.2 (fundir duplicados MTF), Paso 7 §7.2 (procedencia MTF), y Paso 8 §9-2 (glifos strength). Diagnosticar y resolver crash runtime RE10045 en el proceso.

## Hallazgo crítico: RE10045 (Crash de runtime por arrays)
**Problema:** commits `dbf5459` (Paso 6 §6.2 fundir dedup), `ee4d8e2` (Paso 6 §6.5 presupuesto Operación), y `87abab1` (guard) **CRASHEAN en runtime** (compilan 0/0, revienta al aplicar; chart vacío).
**Causa raíz:** cualquier `array.new`+`array.push` dentro de `f_drawMTFZones` (que corre en cada tick de `barstate.islast`) dispara el **límite de recursos runtime de Pine** → crash total.
**Bisect empírico:** `array.new`+`array.size`=corre sin problema; `+array.push`=CRASH inmediato.
**Afectados:** las versiones array-basadas del dedup MTF (búsqueda en array previos, push de nuevos). **SIN afectar a CORE**, que está intacto.
**Fix:** reemplazar lógica array por **acumulador string + `str.contains()`**. El dedup ahora: Operación top-1 por kind,dir mata los duplicados D1:EQH×2, ▼×2, D1:EQL×2 del buffer capN sin usar arrays.

## Commits (secuencia real)
1. **`dbf5459` — Paso 6 §6.2 dedup MTF (versión array).** ⚠️ **CRASHEA en runtime** (compila 0/0, chart vacío al aplicar).
2. **`ee4d8e2` — Paso 6 §6.5 presupuesto Operación (top-1 por kind,dir + quita "D1 bias").** ⚠️ **CRASHEA en runtime** (consecuencia del push en dbf5459).
3. **`87abab1` — Guard/fix para array (innecesario).** ⚠️ **SIGUE CRASHEANDO**.
4. **`9c146d3` — Paso 7 §7.2 procedencia MTF.** ✅ **FUNCIONA** (no arrays). Grosor por TF: D1=3px, H1=2px. Tag `(D1)`/`(H1)` en sweep. Byte-idéntico Visual/Strategy.
5. **`862928b` — Paso 8 §9-2 glifos strength.** ✅ **FUNCIONA**. Glifos `●●●`/`●●○`/`●○○` en filas OB/FVG/Pool cercano del panel T14 columna M5, vía `f_strGlyph(f_strengthLevel)`.
6. **`ed0c46e` FIX DEFINITIVO — dedup MTF SIN arrays.** ✅ **ESTE FUNCIONA CORRECTAMENTE.** Acumulador string + `str.contains()` para Operación. Capacidad nueva: apply del indicador autónomo.

## Validación en vivo (OANDA:EURUSD H1, después del FIX)
- Aplicación **autónoma** vía `scripts/launch-tv-agent.ps1` (CDP 9222 + agent-browser): TV lanzada → indicador "Agregar al gráfico" clickeable por `agent-browser --cdp 9222 click [ref=e19]`. **Usuario YA NO necesita re-aplicar manualmente.**
- **Resultado: Operación = 25 labels ✓ (≤25 budget CERRADO).**
  - Duplicados MTF fundidos a ×1.
  - Sin crash, sin "D1 bias" fantasma.
  - Tag `▼ (D1)` vigente en sweep.
  - **Todo = 501 labels, sin crash.**
- Desglose de los 25: estructura (BOS/CHoCH swing+major top-N) + P/D + quadrants + pool + sweep + FLIP + gaps + MTF D1 (sin duplicados).

## Capacidad nueva establecida
**Apply autónomo del indicador:** TV se lanza **SIEMPRE** con `./scripts/launch-tv-agent.ps1` (CDP 9222 + agent-browser); el botón "Añadir al gráfico" es clickeable por CLI de agent-browser. Eliminada la necesidad del usuario de re-aplicar manualmente tras cada inyección. Flujo: inyectar → click automático → cambiar Densidad a mano → medir.

## Estado plan §11.2
✅ pasos 0-8 · ⬜ paso 9 verificación + firma usuario F1-GATE.

## Pendientes menores (bajo riesgo, sin arrays)
1. **Contador "Dup" panel T14** (§1-7 "nada desaparece en silencio") — se soltó durante el bisect al descartar versión array. Restaurar si falta.
2. **Level-dedup de Estudio+** — el string-dedup actual es Operación-only. Opcional para Estudio+.
3. **Historial git limpieza** — commits `dbf5459`..`87abab1` crashean; HEAD `ed0c46e` funciona. Posible squash si usuario prefiere historial limpio (decisión usuario).

## GOTCHAs vigentes
- `indicator_set_inputs` con "Densidad" → `updated_inputs:{}` (TV preserva input guardado). Usuario cambia a mano.

## Siguiente (S090)
**Paso 9 verificación completa:** Re-validar Ejes 0/1/2/3 en vivo OANDA:EURUSD H1 (el overhaul pasos 6-8 puede regresar presencia/variante/invalidación). Panel T14: restaurar contador "Dup" si falta. Validar tag procedencia MTF `(D1)` / `(H1)`. Validar glifos strength. **Firma usuario F1-GATE** tras verificación OK → cerrar Eje 2 y gate visual.

Ver [[Sesion-088]] · [[Sesion-087]] · esqueleto Fable §11.2 · [[re10045-arrays-y-agent-browser]].
