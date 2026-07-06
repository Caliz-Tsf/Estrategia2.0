# Sesion-097 — Esqueleto Fable Fase 4 EA MT5

**Fecha:** 2026-07-06  
**Objetivo:** Entrega del DOSSIER completo para Fable sobre la arquitectura Fase 4 (EA MT5), separado del workplan.

## Completado

### Trabajo realizado

**(1) Refresco MQL5-PLAN.md contra CORE actual (1700 líneas SHA `5510361166844bd5`):**
- Structs espejo Pine→MQL5 ahora incluyen campo `strength` (ADR-014)
- Agregados campos `gradedFvg`/`trueFvg`/`propulsion` (§5.16/§5.18)
- Enum KIND extendido a KIND_GRADIENT=53 (totaliza ≤53)
- Campos §7 `posRole`/`confDegree`/`depthBand` marcados [Fase B] — hoy el EA los recalcula, Fase B los promueve al CORE
- Filas de mapeo Pine→MQL5 para gradient levels, strength, §7, #52 (confluencia exponencial)
- Sección §0 "NOTA DE REFRESCO S097" indicando fecha y cambios

**(2) Creación docs/planes/DOSSIER-FABLE-fase4-ea-mt5.md (patrón DOSSIER→ESQUELETO):**

Entregable completo (separado del workplan, usuario lo pasa a Fable directamente).

Estructura 8 bloques A–H:

- **Bloque A: Capa determinista EA** — flujo decisional principal, puntos de evaluación, requisitos de dato (precio, tiempo, confluencias)
- **Bloque B: Percepción — cómo llega información al EA** — inputs vivos (TV canales, scoring enjambre, cuaderno confluencias), latencia, garantías anti-repaint
- **Bloque C: Score direccional (Fase 2)** — cálculo bruto Fase 2, 42 confluencias formales, pesos de entrada Fase 3
- **Bloque D: Score-de-perfiles darwiniano** — score agregado del enjambre (NSL, Wyckoff, FX, ICT), votación/confluencia interna, sesgo por timeframe
- **Bloque E: Debate del enjambre** — comunicación inter-agentes, resolución de conflictos, regla de mayoría
- **Bloque F: Cuaderno de confluencias + qué/cuándo NO entrar + proyección a zonas** — tabla de 42 confluencias canónicas, criterios de exclusión (Fase 3), proyección de precio-objetivo por tipo de confluencia, qué hacer al llegar a zona
- **Bloque G: Bucle cognitivo tiempo real (8 pasos)** — tick a tick: data refresh → score → confluencias → debate → decisión → entrada/salida → logging
- **Bloque H: Fases 4→adelante** — roadmap Fase 4.1 (EA core) / Fase 4.2 (portabilidad multi-símbolo) / Fase 4.3 (optimización Fase 3) / Fase 5 (validación segundo símbolo)

### Commits

- **`9318c54`** `docs(fase4): S097 — DOSSIER Fable esqueleto EA MT5 completo + refresco MQL5-PLAN`
  - Archivos nuevos: `docs/planes/DOSSIER-FABLE-fase4-ea-mt5.md`
  - Archivos modificados: `docs/workplan/MQL5-PLAN.md`

### CORE — sin cambios

- CORE 1700 líneas SHA `5510361166844bd5`
- Compila 0/0 los 3 scripts (`SMC-Library.pine` / `SMC-Visual.pine` / `SMC-Strategy.pine`)
- `core-sync OK` (bin/check-core-sync.ps1)

## Hallazgos / Aclaraciones

**ACLARACIÓN IMPORTANTE:** No existía un "brief de Fable pendiente sin pasar" para Fase 4.

- Sesion-092 entregó `DOSSIER-FABLE-sistema-visual.md` → respondido por Fable (`ESQUELETO-FABLE-sistema-visual.md`)
- Sesion-077 creó `DOSSIER-gradient-levels-para-ultracode.md` (para herramienta externa)
- El brief de Fase 4 (EA MT5, arquitectura completa) **nunca existía documentalmente**

El usuario decidió materializar directamente el DOSSIER en sesión y pasarlo a Fable él mismo (sin intermediario).

**NOTA DE SECUENCIA:** Materializar el esqueleto MT5 **en código fuente** es más limpio y evita re-work si se hace **DESPUÉS de Fase 2 (scoring).** El DOSSIER/diseño puede elaborarse ahora sin riesgo; pero llevar a código estable es Fase 4.1, no antes.

## Pendiente

1. **Validación viva Fase A (Visual-only), familia-por-familia** — D1/H1/M5, apagar el resto → todo encendido. Checklist §10 (#1-#3 densidad, #8 nada desaparece, ≤25/60 con guardián+IDM)
2. **Firma F1-GATE** — sigue sin firmar tras A-7 (cierre visual)
3. **Fable devuelve ESQUELETO-FABLE-fase4-ea-mt5.md** — revisión ("punto 3" citado en ESTADO-ACTUAL)

## Sin cambios de arquitectura

- Sin ADR nuevo
- Sin gate de fase completado (no hay tag)
- Bloqueos/decisiones pendientes: ídem S096 (validación familia, firma F1-GATE)

## Referencias

- [[ESTADO-ACTUAL]]: Última tarea Sesion-097
- [[mt5-esqueleto-timing-fase2]]: Nota sobre secuencia materialización MT5 (Fase 4.1)
- [[Sesion-096]]: Cierre anterior (Flip/MB casos EURUSD)
