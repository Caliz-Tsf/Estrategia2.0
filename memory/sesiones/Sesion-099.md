# Sesión-099 (2026-07-06)

## Objetivo
Validación viva del F1-GATE familia por familia en Operación (arrastrado de S093–S098). Prueba de densidad visual §10 en los 3 TF (D1/H1/M5) con indicador `SMC Engine — Visual` commit `8618cc3` (Fase A A-7, CORE 1700 líneas SHA `5510361166844bd5`).

## Completado
**Tarea:** F1-GATE validación visual familias A1–A7 en TV vivo OANDA:EURUSD, Operación, D1/H1/M5.

**Trabajo realizado:**
- Recorrido COMPLETO 7 familias §7.2 (A1–A7) aisladas (apagar resto → encender todas).
- Densidad verificada en 3 TF: **D1 17 labels** ✓ · **H1 24 labels** ✓ · **M5 23 labels + 55 objetos** ✓ (todos ≤25 labels / ≤60 objetos).
- Ocultos + Desalojo contados en panel T14: nada en silencio (cumple §10-#8).
- Guardián de draws (confDegree≥2 inmune) funciona; BSL ·3 en D1 confirmado.
- Glifo de fuerza en panel (●●●/●●○/●○○) mostrando confDegree ✓
- FLIP promocionado (giro+confDegree≥1 en Operación) ✓
- Dibujo de familias LABEL OK: A1 Estructura, A4 Liquidez EQ/pools/sweeps, A6 Gaps NWOG/NDOG/NYMO, A7 MTF/herencia, A5 P/D grid.

**HALLAZGO CRÍTICO — BUG #1 (bloquea F1-GATE):**
Las cajas de zonas NATIVAS del TF (OB/FVG, ruta band-pick `f_drawOB`/`f_drawFVG` líneas 3742/3969) **NO dibujan en Operación en NINGÚN TF**. Solo dibujan las MTF-heredadas (`f_drawMTFZones` 4054). 

- En H1: solo cajas etiquetadas `D1:`; en M5: solo `H1:`/`D1:`, ninguna nativa.
- **Probado que las zonas SON ACTIVAS** (no mitigadas): transporte MTF `f_nearestN` (línea 1584) solo toma `state < ZS_MITIGATED` ✓; el OB [1.14483,1.14622] (vela 04-jul) aparece como "H1: OB" en M5 ✓; máquina `f_updateZoneMitigation` concordante con §2.1 ✓
- **Root cause:** SELECCIÓN band-pick (`f_isBandPick`/población §A-4, líneas 2886–2942) no asigna TOP 1 banda-OB/FVG nativas como vencedor.
- **Impacto:** Operación queda "casi vacía de zonas nativas" — vaciado excesivo, NO el objetivo ("limpio sí, vacío no").
- Afecta también FVG y presumiblemente Breaker/todas las cajas nativas.

**Entregable:**
- `docs/planes/BUGS-VISUAL-fable-revision.md` (commit `339f748`, doc-only) — documentación de bugs para revisión de Fable:
  - BUG #1 caracterizado (ruta culpable, prueba transporte MTF, restricciones del fix: anti-repaint, CORE byte-idéntico, RE10045-safe, params congelados ADR-002).
  - Placeholder BUG #2 Premium/Discount (por documentar si aplica).
  - Checklist "qué debe verse en Operación por familia" para cierre post-fix.
  - Inconsistencia menor: panel titula zona no dibujada (`f_pNearZone`); glifo ●●○ es FUERZA `f_strGlyph`, no confDegree (requiere nota aclaratoria, no es bug).

## Commits
1. `339f748` — `docs(fase1): S099 BUGS-VISUAL para Fable — zonas nativas no dibujan en Operación` (doc-only, BUG #1 caracterizado + entrega Fable).

## Pendiente
1. **Root cause + fix de BUG #1** (delegado a Fable con documentación).
2. **BUG #2 Premium/Discount** — documentar si falla (aún no observado, placeholder).
3. **Barrido fino** concepto-por-concepto de cajas de refinamiento (Breaker/MB/BPR/Vacuum/IFVG) — puede ser cobrado del BUG #1 fix.
4. **Firma F1-GATE** — **BLOQUEADA por BUG #1** (validación visual no 100% verde mientras falten zonas nativas).

## CORE
- **Intacto:** 1700 líneas SHA `5510361166844bd5`, compila 0/0 los 3, core-sync OK.
- **Sin ADR nuevo, sin gate/tag:** F1-GATE SIGUE SIN FIRMAR, además ahora bloqueado por BUG #1.

## Notas
- **Diagnóstico BUG #1:** No es una regresión de S095/S098; es un sesgo de la lógica band-pick en A-4 que hace que los natives se pierdan respecto a MTF-herencias. La máquina de estado `f_isBandPick` **existe** y funciona para las MTF (por eso se ven las herencias), pero no llama a update para las nativas: ver línea 2942 en `f_drawOB`/`f_drawFVG`.
- El BUG impide que el F1-GATE se firme "verde" — es bloqueante.
- Documentación incluye restricciones del fix: jamás tocar CORE byte-idéntico, anti-repaint, arrays acotados (RE10045-safe), parámetros congelados ADR-002.
- Enlace a [[Sesion-098]], [[Sesion-097]], [[Sesion-096]].

---

**Sesión cerrada con hallazgo crítico identificado y documentado para Fable. Siguiente: revisión usuario + resolución BUG #1.**
