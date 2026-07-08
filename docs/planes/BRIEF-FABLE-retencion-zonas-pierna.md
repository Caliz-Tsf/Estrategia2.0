# BRIEF-FABLE — Retención y render de zonas/liquidez a lo largo de la pierna del swing

> Estrategia 2.0 · Fase 1 (Pine Visual) · S105 (2026-07-08) · autor: Claude Code (Opus 4.8)
> Para: **Fable** (revisión de diseño). Objetivo: cómo poblar la pierna COMPLETA del swing
> (ambas direcciones) con los conceptos IMPORTANTES NO MITIGADOS, dentro de las restricciones duras.
> Contexto de visión: [swing-ideal-vision-usuario.md](swing-ideal-vision-usuario.md) (leer primero).

## 1. Qué quiere el usuario (visión validada)
Para el **swing vigente** (dealing range desde su ORIGEN hasta el extremo), ver **poblada por
banda de profundidad** la lista de conceptos importantes **generados dentro del swing**, en
**AMBAS direcciones** (arriba = liquidez/POIs objetivo; abajo = hacia donde va el precio), de modo
que el trader/enjambre pueda **proyectar** ("el precio cae a ~X, luego sube a tomar el BSL / el OB").
- Conceptos: OB, FVG, Breaker, MB, pools SSL/BSL, EQH/EQL, BOS/CHoCH (grande y chico), IDM, etc.
- **Solo NO MITIGADOS** e **importantes** (por `strength`/score). "Limpio pero NO vacío."
- **1–3 por concepto por banda**, con **clustering**: N instancias cercanas del mismo concepto
  colapsan a **1 representante** (el que generó el impulso: displacement > score > el primero).
- **Nativos + heredados** de cada TF mayor (D1→H1→M5), por familia.
- Estilo de render deseado (indicadores de referencia del usuario): liquidez tipo "Liquidity Pools
  Pro" (líneas con magnitud + estado swept, fuertes + nearest por lado); estructura tipo LuxAlgo
  (HH/LL solo pivotes mayores, BoS/CHoCH grande+chico); **fib de proyección** sobre el swing vigente.

## 2. Síntoma observado (en vivo, EURUSD D1/H1, modo "Todo" y "Operación")
- La porción **reciente** de la pierna (cercana al precio) SÍ se puebla de cajas.
- **Hacia arriba de la pierna** (hasta el Premium D1 / BSL histórico) **NO hay cajas** OB/FVG.
- **Hacia abajo** (hacia donde el precio se dirige AHORA) **tampoco**: hay FVG y OB **sin mitigar**
  y **SSL** que existen pero **no se ven**. (Esto es lo más crítico operativamente.)
- Las marcas de ESTRUCTURA (HH/LL/CHoCH/BOS/Stack/Raid) sí aparecen más atrás; las **cajas de zona
  y varios pools no**.

## 3. Diagnóstico técnico (código actual, `pine/SMC-Visual.pine`)
### 3.1 Rango de las bandas (§7 `f_depthBand`) — PARCIALMENTE resuelto en S105
- `f_depthBand` calculaba las bandas 1–3 sobre `chartState.pdHigh/pdLow` = dealing range del **TF
  del chart** (estrecho). Todo lo de arriba caía en **banda 0** (fuera de alcance) → excluido del band-pick.
- **Paso 1 (S105, ya implementado, Visual-only, compila 0/0):** el extremo de pierna en `f_depthBand`
  pasa a ser el **más lejano** entre {rango vigente, swing dominante propio `structMajor.highLevel/
  lowLevel`, rango HTF heredado `d1State`/`h1State`}. Resultado vivo: la pierna RECIENTE ya se puebla
  arriba y abajo. **Pero** aparece un outlier (extremo alcanzó un HH de 2011 ~1.51) → pendiente acotar.

### 3.2 Retención de ZONAS — ROOT CAUSE principal (en el LIBRARY CORE)
- `MAX_ZONES = 50` (línea 225) es un cap **compartido por TODOS los tipos de zona** (OB, FVG,
  Breaker, MB, BPR, VAC, GP, OTE, IPR…) en el mismo array `SMC_zones`.
- `f_pushZone` (línea 356) desaloja por **PURA ANTIGÜEDAD**: `array.push` + `if size>maxN:
  array.shift(a)` (borra el índice 0 = el más viejo), **sin mirar mitigación ni importancia**.
- Consecuencia: como muchos tipos empujan al mismo array de 50, se llena de zonas **recientes** y
  expulsa las viejas **aunque sigan NO MITIGADAS**, en AMBAS direcciones. Por eso arriba/abajo de la
  pierna faltan OB/FVG vivos.

### 3.3 Retención de POOLS (liquidez SSL/BSL)
- `MAX_POOLS = 50`. `f_prunePools` (línea 1508) ya es **importance-aware parcial**: borra primero
  los pools **BARRIDOS** (swept) más viejos y conserva los "imanes vivos". Mejor que las zonas, pero
  aún capado a 50 → con mucha liquidez viva, se pierden SSL/BSL válidos lejanos.

### 3.4 Selección de dibujo (band-pick §7.1)
- `bandPickIdx`/`bandPickScore` = 40 escalares (concepto {OB,FVG,BRK,IDM} × lado {hi,lo} × banda
  {1..5}). Guarda **1 mejor** `score_render_v2 = strength × wPos(posRole) × (1+kConf·confDegree)`
  por celda (top-1). Filtra **no mitigados** (`state != MITIGATED/INVALID`) para OB/FVG/Breaker.
- Falta: **top-N (1–3) por celda** y **clustering** (colapsar cercanos). Y extender el filtro
  no-mitigado + band-pick a más familias (pools, MB, EQ…).

## 4. Restricciones DURAS (innegociables)
1. **Anti-repaint** `[D-PINE-03]`: eventos solo en `barstate.isconfirmed`; `request.security(...,
   lookahead=barmerge.lookahead_off)` SIEMPRE.
2. **RE10045:** `array.push` dentro de funciones que corren en `islast` (script ~4500 líneas)
   revienta el límite de recursos de Pine → **prohibido crecer arrays en el dibujo `islast`**
   (por eso el band-pick usa escalares planos, no arrays).
3. **OOM `request.security`:** el motor completo `f_computeTFState` (que usa `MAX_ZONES` para su
   `zonesTf` interno) sobre `"5"` desde HTF da "Internal server study error" a CUALQUIER ventana
   (probado hasta el mínimo 300). **Subir `MAX_ZONES` agravaría el OOM de los transportes D1/H1**
   (que también corren `f_computeTFState` vía `request.security`). Ver S104/S105 (revertido).
4. **CORE byte-idéntico:** `MAX_ZONES`/`f_pushZone`/`MAX_POOLS`/`f_prunePools` viven en el
   `// === LIBRARY CORE ===` (líneas 151–~1851), byte-idéntico entre Visual y Strategy →
   cualquier cambio se replica en `SMC-Strategy.pine` + `scripts/check-core-sync.ps1`. Es territorio
   ADR-002 (params/estructuras congelados para paridad MQL5 Fase 4).
5. **Budget de tinta:** Operación era ≤25 labels (ahora relajado a "poblado pero limpio: 1–3 por
   banda por concepto"). Estudio 60 / Todo 150. El desalojo de labels §6.5 es por recencia (aparte
   del de zonas). `max_labels_count`/`max_boxes_count`/`max_lines_count = 500`.
6. **Símbolo-agnóstico, umbrales relativos a ATR, R:R, etc.** (no afectan esto directamente).

## 5. Lo ya intentado / estado
- **Paso 1** (extender extremo de pierna en `f_depthBand`) — hecho, Visual-only, valida parcial.
- **Recomendación pendiente de Claude Code:** cambiar `f_pushZone` de desalojo-por-antigüedad a
  **desalojo por importancia** (expulsar INVÁLIDAS → MITIGADAS → más débiles/lejanas primero,
  conservar las NO MITIGADAS importantes) al **mismo cap 50** (memory-neutral → sin nuevo OOM).
  Pero: es cambio al CORE, y no está claro si 50 zonas totales alcanzan para poblar toda la pierna
  en ambas direcciones con varios tipos de concepto.

## 6. Preguntas para Fable (diseño de solución)
1. **Retención de zonas:** ¿desalojo por importancia al mismo cap 50 basta, o hace falta separar el
   cap del **chart** (`SMC_zones`, que sí puede ser mayor sin OOM porque NO va por `request.security`)
   del cap del **transporte** (`zonesTf` dentro de `f_computeTFState`, que DEBE quedarse chico por
   OOM)? ¿Cómo separarlo sin romper la byte-identidad del CORE (misma función `f_pushZone`, distinto
   `maxN` por call-site — ¿es suficiente y limpio)?
2. **Criterio de importancia para retener:** ¿qué llave usar para "conservar lo importante NO
   mitigado a lo largo de la pierna en ambas direcciones"? ¿`score_render_v2`? ¿+ un término de
   cobertura por banda (para no llenar una sola banda y vaciar las demás)? ¿cómo evitar que zonas
   frescas irrelevantes desalojen zonas viejas clave del origen del swing?
3. **Pools (liquidez):** ¿elevar/rediseñar `MAX_POOLS`/`f_prunePools` para conservar SSL/BSL vivos
   relevantes en ambas direcciones (estilo "Liquidity Pools Pro": fuertes + nearest por lado)?
4. **Render band-pick:** diseño de **top-N (1–3) por celda + clustering** (colapsar cercanos al
   representante del impulso) **sin arrays en `islast`** (RE10045). ¿Ampliar los 40 escalares a
   120 (top-3)? ¿otra codificación?
5. **Extremo de pierna:** ¿cómo acotar el extremo (Paso 1) para que llegue al swing/objetivo de
   liquidez VIGENTE (BSL/SSL relevante, HH dominante) y NO a extremos históricos lejanos (1.51 de
   2011)? ¿anclar a la liquidez fuerte más cercana por lado en vez de a `structMajor` puro?
6. **Fib de proyección** sobre el swing dominante vigente: ¿candidato nuevo Visual-only viable?
7. **Orden de implementación** recomendado y qué toca (o no) el CORE / la byte-identidad / el OOM.

## 7. Archivos y anclas de código
- `pine/SMC-Visual.pine`: `MAX_ZONES` L225, `f_pushZone` L356, `f_prunePools` L1508, `f_depthBand`
  L2800 (con Paso 1), band-pick `bandPickIdx` L2913 + loop L2943, `f_renderScoreV2` L2897,
  `f_posRole` L2834, `f_confDegree`, `f_keepBestPerBand` L3248, desalojo labels §6.5 L4013.
- `pine/SMC-Strategy.pine`: mismo CORE byte-idéntico (replicar cambios).
- Reglas: `docs/reglas-smc-ict.md` §7 (proyección/band-pick). CORE actual: 1700 líneas SHA `5510361166844bd5`.
