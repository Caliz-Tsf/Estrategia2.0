# Sesion-114 — Fase B: Diseño + Probe (mitad)

**Fecha:** 2026-07-10  
**Objetivo:** Arrancar Fase B (promoción de extremos HTF al CORE). Decisión usuario al inicio: "diseño + probe primero" — NO romper el SHA hasta que un probe valide token/OOM.  
**Duración estimada:** ~2h (mitad completada; mitad viva GATE B quedó pendiente por CDP/TV caído).

## Completado (1 commit `79c76b1`)

### 1. Diseño Fase B — `docs/planes/DISEÑO-fase-B-promocion-core.md`

**Recomendación B2 documentada (vs. alternativa descartada B1):**

- **Medición real emisiones (CORRECCIÓN de ESTADO-ACTUAL):**
  - `f_computeTFState` (CORE, nearest-N): **89 campos** = 17 escalares + 12 slots×6 campos
  - `f_tfExtremes` (Context, FUERA CORE): **51 campos** = 3 escalares + 8 slots×6 campos
  - **NO se sostiene "~62 campos" de ESTADO-ACTUAL;** medición real más alta.

- **Arquitectura Strategy HOY:** 2 `request.security` (D1+H1) nearest, NO consume extremos (nota L2495).

- **Opción B1 descartada:** tupla física único de 137 campos (nearest+farthest fusionados)
  - Riesgo alto token CE10117 (Strategy 2546 líneas)
  - Riesgo OOM (histórico S104/S105)
  - Frágil MQL5 en Fase 4

- **Opción B2 recomendada (ELEGIDA):**
  - Promover `f_tfExtremes` + `f_farthestZone/Pool/Event` al CORE como **funciones SEPARADAS**
  - `f_computeTFState` (89 campos) NO se toca
  - Strategy añade 2ª `request.security` de extremos (D1+H1)
  - "Tupla único" de ADR-017 se reinterpreta como **single-source-of-truth**, no tupla física
  - Fallbacks si falla: extremos solo-D1 (token) o bajo input `i_scoreExtremes` default OFF (OOM)

- **Fuera alcance v1:** MB/Breaker/BOS-CHoCH heredados (v2). Solo OB/FVG/POOL/EQ.

- **GATE B (probe):** aísla riesgo nuevo = 4 `request.security` (2 nearest + 2 extremos) en un solo Strategy.

### 2. ADR-018 — `docs/adrs/ADR-018-promocion-extremos-htf-al-core.md`

Estado: **Propuesta** (no se acepta hasta que GATE B pase).
- Ratifica opción B2
- Define qué rompe el SHA
- Cómo consume Strategy
- Actualización MQL5-PLAN
- Alternativas descartadas (B1, C)

### 3. Probe — `scripts/gen_probe_faseB.py` (commiteado)

**Genera `PROBE-faseB-oom.pine` en scratchpad (NO commit):**
- 1971 líneas
- CORE de Strategy + funciones de extremos + 4 securities
- **Compila 0/0 server-side** (pine_check.py confirmado)

**Mitad GATE B completada:** compilación server-side OK  
**Mitad GATE B PENDIENTE:** apply en TV (CDP caído toda la sesión)
- Verificar CE10117 token
- Verificar OOM
- Ambos solo aparecen en apply, no en compile

## Estado CORE

- **SHA INTACTO:** `5510361166844bd5` (1700 líneas)
- **Core-sync:** OK ×3 (Visual, Strategy, Context)
- **Compilación:** 0/0 todos los 3
- **F1-GATE:** BLOQUEADA (aprobación humana pendiente)

## Commits

1. `79c76b1` — docs(planes) DISEÑO-fase-B-promocion-core.md + docs(adrs) ADR-018 Propuesta + scripts gen_probe_faseB.py

## PENDIENTE S115

**(a) Ratificar B2** — usuario decide si opción recomendada B2 avanza, o descarta Fase B completa.

**(b) Correr mitad viva GATE B:**
```bash
python scripts/gen_probe_faseB.py <scratchpad>
pine_check 0/0
tv_launch
pine_inject PROBE-faseB-oom.pine + Ctrl+Enter en tab sin slot
esperar ~20s
pine_get_errors (solo ahora aparecen CE10117/OOM)
```

**(c) Si GATE B verde:**
- Ejecutar promoción real (mover funciones al CORE ×3)
- Re-baseline SHA
- Strategy +2 security
- ADR-018 → Aceptada
- MQL5-PLAN actualizado

**(d) Firma F1-GATE** (aprobación humana)

**(e) Tarea #3 defaults** (S112: i_kLeg=3.0 / MAX_ZONES_CHART=120, ya validados)

## GOTCHA S114

- **CDP/TV caído toda la sesión** → halted mitad viva GATE B
- **Pine_check falso-0:** compila OK no garantiza apply (CE10117 solo en apply 18-25s después)
- **Diseño medición CORRECCIÓN:** ESTADO-ACTUAL decía "~62 campos", real es 89 (nearest) + 51 (extremos) = 140 separados, no fusionados

## Links

- [[Sesion-113]] — F1-CTX-06 EQ-tomado-gris (completado)
- [[Sesion-112]] — F1-CTX-04/05 traspaso-gris (completado)
- docs/adrs/ADR-018-promocion-extremos-htf-al-core.md (Propuesta)
- docs/adrs/ADR-017-consumidor-visual-auxiliar-context.md (Aceptada)
- WORKPLAN-MAESTRO-V2.md §3 Fase B

## Notas

- Fase B es **deuda técnica de ADR-017:** al introducir `f_tfExtremes` y `f_farthestZone/Pool/Event` en Context (fuera CORE), quedó pendiente su **promoción al CORE** (necesaria para Strategy heredar y MQL5 unificar).
- Riesgo histórico OOM/CE10117 (S104/S105/S107) justifica estrategia "probe primero" antes de tocar CORE.
- Función de extremos ya vive probada en Context (S110-S113) sin OOM/errors → confianza relativa alta en B2.
- Sin this decisión, F1-GATE jamás firma (Fase 4 MQL5 no puede replarse sin CORE extremos accesible).
