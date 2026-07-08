# Sesion-106 — 2026-07-08 — Pasos A–D Diseño Fable (Poblar Pierna Fase A)

## Objetivo
Implementar el diseño Fable de 6 pasos (A–F) para poblar la pierna del swing. Contexto: S105 redefinió el gate de PASO 6 de "≤25 labels" a "pierna poblada COMPLETA por banda, conceptos no-mitigados, 1-3 por banda + clustering". Decisión usuario: Paso E (fib proyección) descartado (herramienta medición, §0.9 reglas-smc-ict.md, NO concepto §4.8). S106 ejecuta A→D solamente.

## Completado (Verificado por git)

### Commits principales
- **`28c8a10`** `feat(pine-visual): F1 S106 Pasos A-D — poblar la pierna (Visual-only)`
  - Pasos A–D implementados en SMC-Visual.pine (Fase A Visual-only, CORE intacto 1700 líneas SHA `5510361166844bd5`)
  - Compila 0/0, core-sync OK, lookahead_off verificado
  
- **`d0cb10c`** `docs(adr): ADR-016 retención de zonas del chart por importancia (Fase A)`
  - Documento formal ADR-016 (estado: Aceptada — Fase A wrapper Visual / Fase B promoción CORE)

### Detalles de Implementación

#### Paso A: Extremo de pierna acotado
- Nueva función `f_computeLegExtremes(px)`: devuelve [hi,lo] candidato bruto (máximo entre rango vigente/structMajor/HTF)
- CLAMP a `px ± i_kLeg×(rango vigente)` → ancla a pool fuerte vigente (touches≥2 o strength≥0.5) más lejano por lado dentro clamp
- Input `i_kLeg` default 3.0 (min 1/max 6, GRP_DENS)
- `f_depthBand` refactorizada: consume globales `legExtHi/legExtLo` precomputadas 1×/vela en islast (antes recomputaba costos CORE)
- **Resultado:** mata outlier 1.51

#### Paso B: Retención zonas por importancia — ROOT CAUSE fix
- Nuevo `MAX_ZONES_CHART=120` + wrapper Visual-only `f_pushZoneV`
- Desalojo por importancia: INVALID más viejo → MITIGATED más viejo → ACTIVA/PARCIAL menor strength
- Guarda extremos: jamás expulsa ACTIVA top o bottom más lejana por lado
- 10 call-sites chart migrados de `f_pushZone(...,MAX_ZONES,...)` a `f_pushZoneV(...,MAX_ZONES_CHART,...)`
  - SMC_zones (8 usos)
  - SMC_vi (1 uso)
  - SMC_ipr (1 uso)
- Transporte `f_computeTFState` sigue MAX_ZONES=50 (cero riesgo OOM)
- **ADR-016 escrito** (docs/adrs/ADR-016-retencion-zonas-por-importancia.md)

#### Paso C: Pools LP-Pro
- Nuevo `MAX_POOLS_CHART=80` + wrapper `f_prunePoolsV`
- Desalojo: viejo → menor strength; guarda extremos por lado
- Call-site chart migrado (L2462) de `f_prunePools(SMC_pools,MAX_POOLS)` a `f_prunePoolsV(SMC_pools,MAX_POOLS_CHART)`
- Transporte L1793 sigue MAX_POOLS=50 (sin cambio)
- Render LP-Pro: ahora dibuja nearest+top-2 fuertes/lado (flag `strongLP` + `isObjetivo`)

#### Paso D: Band-pick top-3 + clustering + early-out
- Arrays bandPickIdx/Score (40 elementos) → bp3Idx/bp3Score/bp3Lvl/bp3Bar (120 = 40×3, fijo = RE10045-safe)
- Nueva `f_bp3Insert` (clustering: candidatos ≤CONF_TOL_ATR×atr colapsados al de mayor v2; inserta slot más débil; reordena desc)
- Early-out obligatorio: `v2max = strength×POS_W_ORIGIN×(1+CONF_K×3) = strength×1.75`; si no supera bp3Score[base+2] salta f_posRole/f_confDegree (caros)
- Aplicado a zonas + IDM
- `f_isBandPick` conserva firma bool (membership entre 3 slots) → 4 drawers (OB/FVG/Breaker/IDM) SIN cambios

### Verificaciones
- **Compilación:** 0 errores / 0 warnings (Pine v6 server-side)
- **Core-sync:** OK (SHA `5510361166844bd5` intacto 1700 líneas)
- **Lookahead:** `lookahead_off` SIEMPRE (anti-repaint)
- **RE10045:** arrays fijos (bp3Idx/bp3Score/bp3Lvl/bp3Bar), cero `.push` dinámico en islast

## Decisiones Tomadas

- **Paso E descartado:** fib proyección es herramienta medición (§0.9 reglas-smc-ict.md), NO concepto para §4.8 scoring. `f_detectOTE` ya existe. Usuario confirmó: ejecutar solo A→D.
- **MAX_ZONES_CHART=120 vs MAX_POOLS_CHART=80:** candidatos a parametrización ADR-002, NO calibrados en S106 (pendiente validación viva S107).
- **i_kLeg=3.0:** default conservador, ajustable GRP_DENS (rango 1-6).

## Estado

- **F1-GATE:** BLOQUEADA (pendiente validación en vivo S107)
- **Pasos A→D:** implementados + compilando 0/0 + core-sync OK + ADR-016 escrito
- **Validación:** NO realizada (S107 = validación viva D1/H1/M5)
- **CORE:** 1700 líneas SHA `5510361166844bd5`, compila 0/0 los 3 scripts, core-sync OK

## Pendiente (S107)

**VALIDACIÓN EN VIVO D1/H1/M5:**
- Ritual re-aplicar: `pine_inject.py` → editor + Ctrl+Enter → `indicator_set_inputs in_123=Operación`
- Verificar:
  1. NO RE10045-crash al aplicar (Paso D arrays fijos)
  2. Pierna poblada arriba Y abajo sin outlier 1.51 (Paso A)
  3. OB/FVG no-mitigadas reaparecen a ambos lados (Paso B)
  4. Pools top-2 fuertes/lado dibujados (Paso C)
  5. 1-3 representantes por banda con clustering (Paso D)
- Calibrar `i_kLeg=3.0` y `MAX_ZONES_CHART=120` (candidatos ADR-002, no validados)
- Verificar densidad OK (bandas no se desalojan por nuevos límites)

## Referencias

- [[Sesion-105]] — revert S104 + redefinición PASO 6 + PASO 1 extremo pierna
- [[Sesion-104]] — geometría M5 con ventana (revertida S105)
- [[s105-revert-s104-y-diseno-fable-poblar-pierna]] — brief de diseño Fable
- `docs/planes/RESPUESTA-FABLE-retencion-zonas.md` — diseño 6 pasos A–F Fable
- `docs/adrs/ADR-016-retencion-zonas-por-importancia.md` — decisión arquitectónica
- [[bug-ob-cercano-no-dibuja-operacion]] — root cause desalojo antigüedad pura

## Notas

- Fase A Visual-only (sin tocar CORE) permite iterar sin riesgo OOM
- Transporte `f_computeTFState` sigue a MAX_ZONES=50 (capacidad de memoria constante)
- Wrappers Visual-only (`f_pushZoneV`, `f_prunePoolsV`) permiten Fase B promocionar al CORE sin conflicto de byte-idénticidad
- Early-out en band-pick (Paso D) optimiza coste de confDegree (función cara)
- Clustering coloca candidatos cercanos (≤CONF_TOL_ATR×atr) en el mismo slot → reduce ruido visual

---

**Sesión ejecutada sin incidentes.** Commits verificados git. ESTADO: listo para validación viva S107.
