# RESPUESTA-FABLE — Retención y render de zonas a lo largo de la pierna

> Respuesta de Fable al [BRIEF-FABLE-retencion-zonas-pierna.md](BRIEF-FABLE-retencion-zonas-pierna.md).
> S105 (2026-07-08). Diseño accionable, todo **Fase A = Visual-only** (CORE SHA `5510361166844bd5` intacto).

## HALLAZGO QUE CAMBIA TODO
El **CORE termina en L1850** (`=== DETECCIÓN TF PROPIO ===` L1851). Los call-sites del CHART
—`f_pushZone(SMC_zones, ...)` L2101–2297 y `f_prunePools(SMC_pools, ...)` L2406— están **FUERA**
de la sección byte-idéntica. Y `f_pushZone` ya recibe `maxN` por parámetro. → **Casi todo el
rediseño es Visual-only, sin tocar el CORE, sin riesgo OOM** (el transporte `f_computeTFState`
sigue con MAX_ZONES/MAX_POOLS=50). La promoción al CORE se difiere a Fase B (ADR).

## Decisiones por pregunta
- **Q1 Retención zonas:** separar caps por call-site (sale gratis). Transporte queda a 50 (cero OOM).
  Chart: `MAX_ZONES_CHART=120` + wrapper `f_pushZoneV` (Visual-only) con desalojo por importancia.
  50 compartido por ~9 tipos NO basta. Byte-identidad intacta; deuda: unificar en Fase B (MQL5-PLAN §3).
- **Q2 Llave de importancia:** `z.state` (tier) + `z.strength` (ya materializado por el CORE), NO
  `score_render_v2` (caro, para islast). Orden de desalojo: INVALID viejo → MITIGATED viejo → ACTIVA
  de menor strength. **Guarda anti-vaciado:** nunca desalojar la ACTIVA más alta ni la más baja
  (extremos por lado = origen y techo de la pierna siempre conservan representante).
- **Q3 Pools:** `MAX_POOLS_CHART=80` + `f_prunePoolsV` (barridos viejos → vivo de menor strength;
  guarda de extremos por lado). Render LP-Pro en islast: escalares fijos con nearest + top-2 fuertes
  por lado, línea + magnitud + estado swept. No usa el band-pick de 40 celdas.
- **Q4 Band-pick top-3 + clustering:** ampliar el patrón de arrays FIJOS preasignados (RE10045
  prohíbe `push` que CRECE, no `set` sobre fijos). `SLOTS=3`; 4 arrays fijos de 120 (`bp3Idx/Score/
  Lvl/Bar`). Cluster-check: si `abs(lvl−bp3Lvl[s]) ≤ CONF_TOL_ATR×atr` → colapsa al de mayor v2 (a
  igualdad, el primero por barIdx). Representante-displacement queda cubierto vía posRole en v2 (v1);
  flag explícito = v2. `f_isBandPick` devuelve rank 0/1/2 → gradar opacidad (limpio pero no vacío).
  **Early-out obligatorio** antes de `f_confDegree`: `v2max=strength×1.0×1.75`; si `≤ bp3Score[base+2]`
  saltar. Paso 3 (no-mitigado a más familias) = ampliar `elig` del loop L2963.
- **Q5 Acotar extremo (outlier 1.51):** precomputar `legExtHi/Lo` UNA vez por vela en islast (sacarlo
  de `f_depthBand`, que hoy lo recomputa por llamada — caro). Regla: candidato bruto (S105) → **clamp**
  `legExtHi ≤ px + K_LEG×(pdHigh−pdLow)`, `K_LEG=3.0` (input) → **ancla a liquidez**: pool VIVO fuerte
  (touches≥2 o strength≥0.5) más lejano por lado DENTRO del clamp. Mata el 1.51 mecánicamente.
- **Q6 Fib de proyección:** SÍ, viable/barato. Pool FIJO ~10 `var line`+10 `var label` (set_xy en
  islast, sin crecer arrays). Niveles 0.236…1.618 sobre la pierna `legExt`→pivote origen `structMajor`.
  Input `i_fibProy` (off en Operación hasta calibrar). No consume budget rotativo (objetos `var`).
- **Q7 Nada toca el CORE ni el OOM en Fase A.**

## Orden de implementación (pasos verificables en vivo)
- **A** — Refactor `legExtHi/Lo` precomputado + clamp `K_LEG` + ancla a pool fuerte (Q5). Barato,
  arregla lo visible (outlier 1.51, bandas abarcan la pierna operativa).
- **B** — `MAX_ZONES_CHART=120` + `f_pushZoneV` (desalojo por importancia + guarda extremos) en
  call-sites L2101/2108/2120/2126/2157/2159/2174/2176/2236/2297. Root cause: reaparecen OB/FVG no
  mitigados arriba Y abajo. **Escribir `ADR-016-retencion-zonas-por-importancia`** aquí (estado
  "Aceptada — Fase A wrapper Visual / Fase B promoción a CORE").
- **C** — `MAX_POOLS_CHART=80` + `f_prunePoolsV` + render LP-Pro (nearest + 2 fuertes/lado).
- **D** — Band-pick top-3 + clustering + early-out confDegree + filtro no-mitigado ampliado.
  **Verificar aplicando en TV (agent-browser), no solo pine_check** — RE10045 compila 0/0 y revienta
  al aplicar (lección S089).
- **E** — Fib de proyección.
- **F (Fase B, ADR)** — promover desalojo al CORE (`f_pushZone`/`f_prunePools` v2 parametrizadas),
  replicar a Strategy, re-baseline SHA, MQL5-PLAN §3 (módulo `SMC_Zones.mqh`).

## Riesgos
1. Divergencia Visual/Strategy en retención (Fase A) — aceptada (Strategy aún no puntúa); cierre en F.
2. Crash recursos islast (paso D) — 120 zonas ⇒ más `f_confDegree`; early-out obligatorio; probar en TV.
3. Budget de tinta (paso D) — mantener fila "Ocultos" + desalojo §6.5 como red; si Todo>150, ranks 1-2 a Estudio+.
4. `K_LEG=3.0` conjetura — calibrar en EURUSD D1/H1 y XAUJPY D1 antes de congelar.
