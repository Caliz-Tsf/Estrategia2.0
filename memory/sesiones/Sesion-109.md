# Sesión 109 — 2026-07-08

**Objetivo:** Revisar el ESQUELETO-FABLE-context-htf-revelado.md (que escribió Fable) y comenzar su ejecución.

**Estado:** ✅ COMPLETADA

## Completado

### 1. Revisión del esqueleto verificando contra código real (pine/SMC-Visual.pine)
- Hallazgos corregidos en el doc:
  - Fix `z.bot` → `z.bottom` (campo real del UDT SMC_Zone L228) en snippet C.2.
  - Nota [OPUS] para verificar constantes ZS_MITIGATED / KIND_* / MTF_K antes de escribir C.2/C.3.
  - Aclaración: el probe emite 12 slots (MTF_K, peor-caso de memoria) vs f_tfExtremes de producción 8 conceptos.
- Verificaciones OK: marcadores CORE L143→L1843; f_computeTFState cuerpo 1687-1790 y nearest-N 1791-1828; f_m5Light L2722; security calls L2761-2762; check-core-sync = Visual vs Strategy por SHA.

### 2. GATE A0/A2/A3 del esqueleto — EJECUTADO EN VIVO (OANDA:EURUSD H1)
- **A0 sanity:** TV+CDP OK, Visual aplicado, pine_check Visual 0/0, CORE_SYNC=OK.
- **A2 (probe solo):** generado PROBE-context-oom.pine (1712 líneas, scratchpad, NO commiteado) vía scripts/gen_probe_context.py; compila 0/0 server-side; aplicado vivo → 0 errores, sin CE10117, sin OOM. Motor completo D1+H1 (proxy exacto del futuro Context) cabe solo.
- **A3 (convivencia):** probe aplicado como 3er estudio JUNTO al Visual + LuxAlgo simultáneos → 0 errores, panel T14 del Visual vivo, probe emitiendo valores reales (d1_pdHigh=1.20831, h1_pdHigh=1.14730, checksums no-na). **VEREDICTO: el chart aguanta el motor pesado corriendo dos veces (Visual + Context). Arquitectura del 3er consumidor SMC-Context.pine CONFIRMADA VIABLE EN MEMORIA, sin degradar alcance.**

### 3. Slot TV `SMC_Context` creado
- ID c098abf3 vía UI del editor ("Hacer una copia" del Visual).
- Método verificado y documentado en Paso B.5 del esqueleto.
- Actualmente contiene el probe (se reemplazará con el código real en Paso C).
- SMC_Library (Visual v168) intacto y aplicado; chart limpio (probe removido tras medir).

### 4. Hallazgo metodológico importante
- `pine_new` NO da un tab sin slot en esta build de TV — inject+save sobrescribe el slot vinculado SMC_Library (recuperable re-inyectando el Visual).
- Por eso A3 requiere el slot SMC_Context propio.
- Anotado en el esqueleto.

### 5. Commit
- **`5ab55a2`** "docs(planes): S109 revision esqueleto Context + gate A0/A2/A3 VERDE (de-riesgo OOM)"

## Pendiente (S110)

**Paso B (doc-only, reversible):**
- ADR-017 (tercer consumidor visual auxiliar SMC-Context.pine)
- Extender check-core-sync.ps1 a 3 archivos (opcional si SMC-Context.pine existe)
- Nota en CLAUDE.md y PINE-PLAN.md
- 1 commit

**Paso C (esqueleto SMC-Context.pine + f_tfExtremes):**
- Slot SMC_Context ya existe y listo para reemplazar probe

## Sin gate de fase
- No hay tag (es progreso dentro de Fase 1).

## Sin ADR nuevo aún
- ADR-017 es Paso B, siguiente sesión.

## Notas técnicas
- **CORE INTACTO:** 1700 líneas SHA `5510361166844bd5`, compila 0/0 los 3.
- **Core-sync:** OK (Visual vs Strategy byte-idéntico).
- **Método TV:** `pine_inject.py` (inyecta vía CDP), `pine_check.py` (compila server-side).
- **Hallazgo de riesgo mitigado:** OOM confirmado DESCARTADO para el motor 2× en memoria (Visual + Context). El límite fue el piso, confirmado empíricamente.

## Referencias
- esqueleto origen: `docs/planes/ESQUELETO-FABLE-context-htf-revelado.md` (entregado Fable S109)
- probe de validación: PROBE-context-oom.pine (generado scripts/gen_probe_context.py, scratchpad, 1712 líneas, NO en git)
- slot TV: SMC_Context (id c098abf3)
