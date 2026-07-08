# Sesión 105 — 2026-07-08
> Retomar PASO 6 (budget ≤25) → PASO 4 → firma F1-GATE. Fase 1, Rama pine/sistema-completo.

## Objetivo
Continuar ciclo Fase 1: redefinir PASO 6 (objetivo real no ≤25 sino "pierna poblada"), diagnosticar causa raíz de retención zonas, consultar arquitectura a Fable, implementar PASO 1 del rediseño.

## Completado ✅

### Hallazgo Crítico + Revert S104
**Contexto:** HEAD de S104 (commit `7c9e6e7`, geometría M5 CON VENTANA via `calc_bars_count`) indicador MUERTO en los 3 TFs: "Internal server study error" (confirmado vivo OANDA:EURUSD).

**Root cause identificada:** La geometría M5 **COMPLETA** (`f_computeTFState` sobre contexto `"5"` vía `request.security` con `calc_bars_count`) revienta el límite de recursos server-side de TradingView **a CUALQUIER ventana** — probado hasta i_m5Window=300 mínimo y sigue errando. La "validación H1 sin OOM" de S104 fue contra una instancia aplicada **STALE** (el ritual re-aplicar indicador no refrescó el bytecode compilado en servidor).

**Solución:** Commit `9610f11` revierte HEAD S104 → restaura transporte ligero `f_m5Light` de S103 (17 escalares M5; geometría M5 COMPLETA solo EN M5 nativa). Sistema funcional restaurado, validado vivo EURUSD H1 Operación (sin "Internal server study error").

### Redefinición PASO 6 (Usuario)
Usuario clarificó objetivo PASO 6 vía documentación expandida `docs/planes/swing-ideal-vision-usuario.md` + 3 indicadores referencia (Liquidity Pools Pro, LuxAlgo SMC, fib proyección):
- **Antes:** reducir a ≤25 labels (criterio numérico duro).
- **Después:** poblar **PIERNA COMPLETA del swing** — conceptos IMPORTANTES (fuerza) NO MITIGADOS (nativos + heredados por TF), **1-3 por concepto por banda + clustering** (colapsar instancias cercanas al representante), ambas direcciones:
  - **Arriba:** desde precio vigente hasta origen del swing / BSL
  - **Abajo:** desde precio vigente hacia objetivo liquidez
- Estilo visual: LP-Pro (concentración + limpieza) + fib de proyección (niveles objetivos)
- **≤25 rígido NO es más el gate.** El gate es "pierna poblada por banda, importante, sin mitigación"

### Diagnóstico Root Cause (Retención Zonas)
Investigación: **por qué faltan conceptos arriba y abajo de la pierna?**

**Raíz (en CORE, L225):** `MAX_ZONES=50` es un cap compartido por todos los tipos de zona.

**Mecanismo (en CORE, L356):** `f_pushZone` desaloja POR PURA ANTIGÜEDAD (`array.shift` del más viejo) cuando alcanza cap → **expulsa zonas NO-MITIGADAS viejas EN AMBAS DIRECCIONES**. Mismo patrón en `f_prunePools` (MAX_POOLS=50).

**Síntoma:** Conceptos históricos arriba (antes del origen swing) y abajo (antes del objetivo) desaparecen sin aviso. Banda 0 (lejos del rango vigente) se queda vacía → visualización concentrada solo en rango activo.

### Consulta Fable + Respuesta (Brief → Respuesta)
**Brief enviado:** `docs/planes/BRIEF-FABLE-retencion-zonas-pierna.md` — problema, contexto, restricciones anti-repaint/CORE byte-idéntico.

**Respuesta Fable:** `docs/planes/RESPUESTA-FABLE-retencion-zonas.md` (commit `f7a2514`)

**HALLAZGO CLAVE EN LA RESPUESTA:**
El CORE termina en L1850; los call-sites `f_pushZone(SMC_zones)` (L2101+) y `f_prunePools(SMC_pools)` (L2406) están **FUERA del CORE byte-idéntico**. El parámetro `maxN` YA se pasa a `f_pushZone` → **el rediseño es VISUAL-ONLY, sin tocar CORE, sin riesgo OOM, sin romper SHA `5510361166844bd5`.**

**Diseño Fable (6 pasos A–F, todo Visual-only):**
- **Paso A:** Clamp extremo de pierna `K_LEG=3×rango` + ancla a liquidez fuerte (mata outlier ~1.51)
- **Paso B:** `MAX_ZONES_CHART=120` + wrapper `f_pushZoneV` desalojo por importancia (INVALID→MITIGATED→menor strength) con guarda de extremos por lado; escribir ADR-016
- **Paso C:** Pools estilo LP-Pro (`MAX_POOLS_CHART=80` + `f_prunePoolsV` + render nearest+2 fuertes/lado)
- **Paso D:** Band-pick top-3 + clustering (arrays fijos, early-out confDegree)
- **Paso E:** Fib de proyección
- **Paso F (Fase B):** Promover desalojo al CORE + Strategy + ADR nueva

### PASO 1 Implementado (Extremo de Pierna)
**Commit `6c586e1`** (Visual-only, +docs visión, 0/0, core-sync OK):

Extremo de pierna (`f_depthBand`, L2800) redefinido como el **MÁS LEJANO entre:**
1. Rango vigente (`chartState.pdHigh/pdLow`)
2. Swing dominante propio (`structMajor.highLevel/lowLevel`)
3. Rango HTF heredado (`d1State.pdHigh/pdLow` o `h1State.pdHigh/pdLow` según TF)

**Antes:** Bandas 1-3 solo cubrían dealing range estrecho del TF → conceptos históricos (arriba/abajo) caían a banda 0.

**Después:** Bandas 1-3 ahora se expanden hasta los límites extremos del swing → visualización "pierna poblada" arriba Y abajo.

**Validación viva:** EURUSD D1 Operación — pierna reciente se puebla conceptos en dirección arriba/abajo:
- OB/FVG/MB/estructura repartidos entre 1.13–1.20 (vs. antes apelotonados ~1.14)
- Extremo alcanzó HH histórico ~1.51 (outlier, será clamped Paso A)

## Pendiente
- **PASOS A–F del diseño Fable:** S106 continuará implementación (Paso A clamp + ancla, Paso B f_pushZoneV + ADR-016, C, D, E)
- **Firma F1-GATE:** Depende de validación viva completa pierna poblada (banda 1-3 ambas direcciones, conceptos sin mitigación)

## Commits
- `9610f11` — revert(pine-visual): F1 S105 — revertir geometría M5 con ventana (S104) que dejaba HEAD muerto
- `6c586e1` — feat(pine-visual): F1 S105 PASO 1 — extremo de pierna al swing dominante/HTF (f_depthBand)
- `f7a2514` — docs(fase1): RESPUESTA-FABLE retención zonas por importancia (diseño Fase A Visual-only) — ref S105

## Estado
- **CORE:** 1700 líneas, SHA `5510361166844bd5`, compila 0/0 los 3 scripts, core-sync OK
- **Archivos:** Redefinición PASO 6 documentada en `docs/planes/swing-ideal-vision-usuario.md` (expandido). Brief+Respuesta Fable en `docs/planes/BRIEF-FABLE-retencion-zonas-pierna.md` + `docs/planes/RESPUESTA-FABLE-retencion-zonas.md`
- **Sin ADR nuevo:** ADR-016 se escribirá en S106 Paso B (f_pushZoneV)
- **Sin gate completado:** F1-GATE sigue bloqueada, redefinida a "pierna poblada por banda, importante, no-mitigada"

## Siguiente Sesión (S106)
Implementar el diseño de Fable, empezando por:
1. **Paso A:** Clamp extremo (`K_LEG=3×rango`) + ancla a liquidez fuerte
2. **Paso B:** `f_pushZoneV` desalojo por importancia + ADR-016
3. **Pasos C, D, E:** Pools, band-pick, fib
4. Validación viva familia-por-familia tras cada paso

---
**Ejecutada por:** Claude Code (supervisor sesión)  
**Duración estimada:** ~2h (revert + diagnosis + Fable brief/response + PASO 1)
