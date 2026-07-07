# Sesión 101 — 2026-07-07

**Objetivo:** Cierre de sesión 101 — (1) entregar fix del agente `smc-doc-updater` que escribía fuera del repo, (2) barrido D1 concepto-por-concepto en TV vivo para cazar bugs, (3) consolidación doc BUGS-VISUAL si no aparecen nuevos.

**Completado:**

## 1. FIX AGENTE `smc-doc-updater`

**Root cause:** Existen dos carpetas llamadas `memory`:
- Carpeta **válida:** `REPO/memory/` (dentro del repositorio git).
- Carpeta **prohibida:** `~/.claude/projects/.../memory/` (auto-memoria del harness Claude Code, inyectada vía system-prompt).

El agente `smc-doc-updater` recibía ruta absoluta a la auto-memoria e intentaba escribir ahí (fuera del repo). Esto fue confirmado por discrepancia: archivos aparecían en el harness pero NO en `git status`.

**Fix (commit `746004b`):**
- Paso 0: Resolver REPO vía `git rev-parse --show-toplevel`.
- Todas las rutas son absolutas ancladasa `REPO/memory/...`.
- Prohibición explícita de `.claude/projects/` en validación.
- Verificación final: confirmación con `git status` de que los archivos aparecen como cambios del repo.
- Además se borró el stub extraviado `Sesion-086.md` de la auto-memoria (legítimo vive en el repo, idénticos).

**Protocolo revisado y documentado en system-prompt del agente para sesiones futuras.**

## 2. BARRIDO D1 EN TV VIVO

**Contexto:** S100 confirmó root cause de BUG #1 (análisis estático). S101 ejecuta barrido D1 concepto-por-concepto en vivo para:
- Reforzar evidencia BUG #1 en el TF techo (D1 = sin herencia MTF que enmascare).
- Acotar BUG #3 a M5 (validar que D1 cuenta bien Ocultos).
- Detectar nuevos bugs antes de entregar doc consolidado a Fable.

**Setup TV:** OANDA:EURUSD D1, indicador `Hcihce` (SMC Engine — Visual, commit `8618cc3`), Operación + Estudio.

**Resultados (commit `8855f38`):**

### BUG #1 — CONFIRMADO CON MEJOR EVIDENCIA
- **Estudio:** 14 cajas nativas (OB/FVG) visibles.
- **Operación:** 0 cajas nativas.
- **D1 = TF techo, sin herencia MTF que enmascare → aísla definitivamente el fallo al gate de Operación** (`chartState.atr14=na` → `aAtr>0` siempre FALSE → ninguna nativa pasa).
- **Confirmación:** Mismo instante (vela D1 07-07 00:00), identidad zona invariante, solo difiere densMin (Operación 2 vs Estudio sin mínimo).

### BUG #3 — ACOTADO A M5
- **D1:** Contador "Ocultos" reporta valores correctos y grandes (Est 339, EQ 60) — refleja recorte top-N de la detección completa → comportamiento esperado §10-#8.
- **M5:** Contador sub-reporta (reporta 0 cuando EQ detectados 81 y dibujados ≤2) → bug de panel-only, independiente de BUG #1.
- **Causa:** `hidEq`/`hidStruct` miden recorte de labels DIBUJADOS (post-`f_keepBestPerBand`), no detectado−dibujado.

### FAMILIAS NO-BLOQUEADAS — TODAS OK EN D1
- **A1 (Estructura BOS/CHoCH):** 8 labels visibles, corrección posRole/confDegree validada, grid P/D exacto al 5º decimal.
- **A4 (Liquidez Pool):** 6 labels, distancia/contexto esperado.
- **A5 (P/D + Gradient):** Grid Premium 1.20831/Discount 1.13246 correcto, gradient-eighths alineados, anti-repaint OK.
- **A6 (Gaps apertura):** 2 labels, fuera-de-sesión.
- **A7 (Contexto):** 1 label validado.
- **TOTAL D1:** 17 labels ≤25 ✓.
- **Cajas MTF (heredadas D1→H1/M5):** extienden correctamente a barra actual.

### A2 / A3 — DIFERIDOS A POST-FIX
- **OB/FVG nativos:** Bajo bloqueo BUG #1 (no dibujan en Operación). Validarán tras fix.
- **Resumen:** de 42 confluencias, 5 familias (A1/A4/A5/A6/A7) = 17/42 validadas en D1.

### COMPARACIÓN D1 vs H1 vs M5
| TF  | Labels | Objetos | BUG #1 | BUG #3 | A2/A3 |
|-----|--------|---------|--------|--------|-------|
| D1  | 17     | 41      | ✓ Confirma | OK | Diferido |
| H1  | 24     | 52      | ✓ Confirma | OK | Diferido |
| M5  | 23     | 55      | ✓ Confirma | BUG ⚠️ | Diferido |

## 3. ENTREGABLE CONSOLIDADO

**Documento:** `docs/planes/BUGS-VISUAL-fable-revision.md` (actualizado commit `8855f38`)

Contiene:
- Root cause BUG #1 con evidencia D1/H1/M5.
- BUG #2 cerrado (confirmado statu quo).
- BUG #3 aislado a contador panel M5.
- Checklist por familia (A1–A7) con columnas por TF (D1/H1/M5).
- 2 preguntas para Fable sobre BUG #1 + fix candidato.
- 2 preguntas sobre BUG #3 (contador panel).
- **LISTO PARA ENTREGA ÚNICA A FABLE** (no requiere re-validación TV, doc estable).

## Estado CORE

- **1700 líneas** SHA `5510361166844bd5` — **INTACTO**.
- **Compila 0/0** (los 3 scripts: Library, Visual, Strategy).
- **core-sync OK** (`check-core-sync.ps1`).

## Estado F1-GATE

**BLOQUEADA POR BUG #1.** Necesita:
1. Fix `chartState.atr14 := atr14` (Fable o Claude directo).
2. Re-validación A2/A3 (OB/FVG nativos) post-fix.
3. Firma usuario.

## ADRs

**Sin ADR nuevo.** Sin gate/tag de fase.

## Próximas sesiones

**S102:**
1. Ejecutar fix BUG #1 (coordinar con Fable).
2. Re-validar A2/A3 en TV vivo.
3. Cerrar firma F1-GATE.
4. Entregar doc a Fable.

---

**Commits hoy:**
- `746004b` fix(agents): smc-doc-updater ancla a repo root
- `8855f38` docs(fase1): S101 barrido D1 en BUGS-VISUAL

**Tiempo:** ~2h (fix agente + barrido TV + doc).
