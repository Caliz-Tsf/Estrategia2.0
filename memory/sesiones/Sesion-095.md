# Sesion-095 (2026-07-04)

## Objetivo
Implementar los pasos **A-2…A-7** de la Fase A (capa §7 de proyección/confluencia) enteramente en `SMC-Visual.pine` (Visual-only, sin tocar CORE), continuación de A-1 (S094). Bajo gate [[sprint16-gate-reglas-antes-de-codigo]]. Tras A-7 se cierra la parte visual → firma F1-GATE.

## Completado

### A-2…A-7 implementados — commit `8618cc3` (feat(pine-visual), Visual-only)
CORE byte-idéntico intacto (1700 líneas, SHA `5510361166844bd5`, core-sync OK); **los 3 scripts compilan 0/0** (pine_check server-side).

- **A-2 `f_posRole(top,bot,barIdx)`** → {0=INTERNO,1=GIRO,2=ORIGEN}. GIRO = solape ±tolPos×ATR (0.5) con el giro vigente `chartState.lastMSSPrice`; ORIGEN = `barIdx` en ventana ±posLookfwd (20) del pivote-origen de la pierna dominante (`structMajor.low/highBarIdx` por bias); desempate ORIGEN gana. Lectura pura de swings/eventos ya detectados.
- **A-3 `f_confDegree(level)`** → int. Cuenta 6 familias {OB/Breaker · FVG/IFVG/BPR · pool vivo · EQH/EQL · IDM · OTE/GP} activas apiladas en ±tolConf×ATR (0.25 = labelClusterTol §6.2). La familia propia cuenta (OB aislado = 1, casa con contraejemplo §7.0.2). Contador int, cero arrays nuevos (RE10045-safe). **Desviación de spec:** familia `gap` omitida (no hay array limpio de NWOG/NDOG) → 6 de 7 familias.
- **A-4 `f_renderScoreV2` + selección por bandas.** Llave `strength×wPos×(1+kConf·min(cfg,3))`. Selección top-por-celda (concepto OB/FVG/Breaker/IDM × lado hi/lo × banda 1..i_profundidad) con **40 escalares int** (`bandPickIdx`/`bandPickScore`, SET/GET indexado, cero `array.push` → RE10045-safe), poblada en la misma pasada `islast` de las anclas. `f_isBandPick` recomputa la celda; gates OB/FVG/Breaker `OR f_isBandPick` (dibujan aunque `f_densOK` diga no).
- **A-5** Breaker (band-pick concepto 2) + **IDM sube a Operación** por band-pick (bandas 1-2, concepto 3 sobre `SMC_idm`) + **promoción por confluencia** `confDegree≥2` (Mitigation §7.2.11 requisito ≥2 ✓, BPR §7.2.18) + **Flip §7.2.7** en Operación solo GIRO(`posRole≥1`)+`confDegree≥1` (reemplaza el cap por recencia).
- **A-6 guardián de draws.** En el selector de pools de Operación: pool con `confDegree≥2` **o** el draw alineado al bias más lejano (`poolDrawIdx`) son inmunes al recorte. Rescata el "adiós al BSL 1.51". P/D = contexto, jamás tijera.
- **A-7** bandas 4/5 (archivo rotatorio de 2 rangos previos `pdPrev1/2Hi/Lo`, rotan al moverse el borde P/D >0.5×ATR, patrón grids P3; `f_depthBand` extendida; **dormante con i_profundidad=3**) + estructura/EQ **re-llaveados** por mejor `score_render_v2` por banda (`f_keepBestPerBand` sobre arrays paralelos label+line+level; `SMC_structLevels`/`SMC_eqLevels` nuevos) **con relleno de seguridad por recencia**.

### Bug cazado y corregido (durante el propio A-7)
`f_keepBestPerBand`: si ningún nivel cae en banda (p.ej. P/D no fijado en barras tempranas → todos band 0) borraba TODA la estructura/EQ en Operación. Fix: relleno de seguridad que completa hasta `cap` con los más recientes no-conservados → **nunca borra por debajo del cap** (sin regresión).

## Congelados aplicados (ADR-002)
`wPos {1.0/0.9/0.35}` · `kConf 0.25` · `tolConf 0.25×ATR` · `tolPos 0.5×ATR` · bandas `{0.33/0.66/1.0}` · `i_profundidad {3..5}` · promoción `confDegree≥2`.

## Pendiente (necesita sesión TV)
1. **Validación viva familia por familia** (apagar el resto → todo encendido) en EURUSD D1/H1/M5 + checklist §10 (#1-#3 densidad, #8 nada desaparece en silencio; confirmar ≤25/60 con el guardián + IDM-en-Operación añadiendo tinta).
2. **Cerrar casos de pasada Flip (§7.2.7) + Mitigation Block (§7.2.11)** con niveles EURUSD reales (ahora que el código los selecciona).
3. **Firma F1-GATE** tras 1 y 2.

## Riesgos a confirmar en vivo
- **Coste `islast`:** `f_confDegree` corre por cada zona candidata (no solo finalistas como sugiere §0.8). Acotado (arrays ≤50-100) → compila; si el vivo muestra timeout, optimizar a finalistas-only.
- **Presupuesto de labels:** guardián + IDM-en-Operación añaden tinta → confirmar budget §6.5.

Ver [[fork-rediseno-proyeccion-s7]] · [[Sesion-094]] · [[re10045-arrays-y-agent-browser]].
