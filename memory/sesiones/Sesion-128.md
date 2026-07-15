# Sesion-128 — 2026-07-14/15 — El ancla del dealing range: la Opción B no compra nada, y la tesis de S127 cae

## Objetivo sesión
Pendiente #1 de S127: el ancla del dealing range (Opción B, "el orden importa — define la geometría de
la que depende el alcance"). Decisión del usuario al arrancar: **diseño + probe primero, sin tocar
`pine/`** (norma S114).

## Resultado
F1-GATE SIGUE BLOQUEADA. **CORE INTACTO** (SHA `752b4083a7db419d`, 1866 líneas, core-sync OK ×3).
`pine_check` 0/0. Rama `pine/sistema-completo`. SIN ADR (los dos diseños quedan en PROPUESTA). SIN tag.
`pine/` NO se tocó en toda la sesión.

## Commits (2)
- `3317efc` chore(scripts): F1-S128 diseño + arnés del ancla del dealing range (A vs B), medido
- `64d5773` docs(planes): F1-S128 diseño de la Opción C — dealing range pegajoso por temporalidad

## Lo primero: la Opción B no estaba "aparcada", estaba descartada y re-confirmada 2 veces
`docs/decisiones-pd-rango.md` registra la decisión T07/S021 (Opción A, trailing extremes de LuxAlgo) y
**dos re-confirmaciones del propio usuario**: nota S057 ("Decisión S057 del usuario: mantener Opción A")
y nota S091 ("2.ª confirmación... dejar constancia para no re-litigar en Fase 1"), con el cambio a B
congelado hasta **Fase 3 con datos out-of-sample** (anti-overfitting, ADR-002).

Se le presentó al usuario antes de tocar nada. **Decisión: diseño + probe primero.**

## Tarea 1 — Diseño + probe del ancla (A vs B) · `3317efc`
Doc: `docs/planes/DISENO-ancla-dealing-range-S128.md`. Arnés: `scripts/gen_probe_ancla_rango.py`.

### Medido en vivo — D1 OANDA:EURUSD, n = **6283 barras confirmadas**, marker 1283, `close` 1.14357
(sobre historia acumulada con contadores, no en un punto — que era el hueco de S057/S091)

| Métrica | Valor | Predicción |
|---|---|---|
| desacuerdo veredicto P/D A vs B | **204/6283 = 3.2%** | **P1 ✅** (<20%) |
| `structMajor.lowLevel` < `pdLow` | **0 de 6283** | **P2 ✅** |
| `legExtLo − min(pdLow, structMajor.lowLevel)` | **0** (identidad) | **P3 ✅** |
| archivo de A bajo el alcance (`pdPrev1Lo`) | **680 = 10.8%** | **P4 ❌** |
| idem `pdPrev2Lo` | **898 = 14.3%** | |
| archivo de B bajo el alcance | **1504 = 23.9%** | |

### HALLAZGO PRINCIPAL — se refuta la tesis central de S127
**"Las bandas 4/5 son incapaces POR CONSTRUCCIÓN" es FALSO.** El error de razonamiento de S127:
`f_updateTrailing` solo expande, cierto — **pero `f_resetTrailingHigh/Low` REANCLA**, y reanclar mueve
el nivel hacia dentro → el rango **sí contrae** → el archivo **sí** puede quedar no-anidado. Medido:
**680/6283 (10.8%)**. **Están dormidas hoy, no muertas.** No hace falta el rediseño ni el ADR que S127
daba por necesarios.

Cross-check aritmético: `nA_arch_out` 1221 − `nA_arch_aboveHi` 541 = **680** exacto ⇒ los lados
descomponen sin solape.

## Tarea 2 — Los DOS errores propios (documentados, no enterrados)
1. **`structMajor` NO es el ancla de la Opción B.** Reancla en **cada pivote confirmado** (:2216); la
   Opción B documentada dice *"los niveles cuya **ruptura** generó el último BOS/CHoCH"*. Proxy malo.
2. **Por tanto el probe midió el contraste equivocado:** A vs `structMajor` = **dos anclas que
   caminan**. La conclusión "el ancla no puede ensanchar el alcance" **solo vale para ese B**. El
   modelo del usuario (pegajoso hasta ruptura) es una **tercera** opción que ninguno implementa — y ya
   la había descrito igual en S091 ("que D1 quede lejos mientras el precio no rompa ese bajo").

Sobreviven del probe: P1 (tautológico entre dos anclas que caminan), P3 (identidad útil) y P4
(refutación sólida).

## Tarea 3 — Diseño de la Opción C (pedido por el usuario) · `64d5773`
Doc: `docs/planes/DISENO-opcion-C-rango-pegajoso-S128.md`. **PROPUESTA, nada implementado.**

**El problema real: la jerarquía está INVERTIDA, no desplazada.** El rango D1 mide hoy **758 pips** —
menos que lo que debería medir el de H1. Lectura del usuario (líneas dibujadas en el chart): D1
`[~0.9536, 1.60554]` ≈ 6500 pips · H1 `[1.02175, 1.39970]` ≈ 3780 · M5 local.

**Regla C1:** por TF, el extremo **se queda** y solo reancla al ser **violado** (close más allá). Mismo
`i_pdSwingLen`=50, **cero parámetros nuevos**. Único cambio: hoy el reset se llama en cada pivote
confirmado; en C solo tras violación.

**Se AUTO-ESCALA** (la propiedad clave): D1 se viola cada años (→ `[0.95, 1.60554]`), H1 cada días (→
`[1.02175, 1.39970]`), M5 constantemente. Reproduce las tres lecturas del usuario **sin hack por
timeframe**.

**El cascadeo que pidió el usuario sale GRATIS:** cada TF ancla con sus pivotes y reancla solo al
romperse; como cada escala se viola con distinta frecuencia, el bloqueo escalonado **es la
consecuencia**, no algo a coordinar. `f_computeTFState` ya calcula estado independiente por TF vía
`request.security` → **los tres rangos ya existen en estado**; hoy los tres caminan.

**"Del rango de D1 calcular premium/discount para H1/M5" YA EXISTE:** §5.16 Gradient Levels,
`f_computeGradientLevels` (:1214), cuya política **P1 ya usa `trailing.top/bottom`** (:2344) — son los
`UQ 1.18935` / `EQ 1.17038` / `7/8` / `5/8` del chart. **Arreglado el ancla, la subdivisión sale sola,
cero código.** Es complementaria a C, no alternativa.

**C2 (acoplada a BOS, ICT ortodoxa)** se mide como control, pero **no** reproduce lo pedido: con C2 el
`strongHigh` D1 no se quedaría en 1.60554, y el usuario lo quiere ahí.

### Honestidad sobre los números (corrige una afirmación de Claude en el chat)
| Ancla D1 | pct de 1.14380 | Zona |
|---|---|---|
| Implementado `[1.13246, 1.20831]` | 14.6% | Discount |
| `[1.01779, 1.20831]` | 66.1% | Premium |
| **Lectura del usuario `[0.9536, 1.60554]`** | **29.6%** | **Discount** |

**NO se puede afirmar "el veredicto se invierte a premium": depende del par de anclas.** Con las líneas
que el usuario dibujó, D1 **sigue en discount** — pero un discount **con sentido** (precio bajo en un
rango de 6500 pips), no el artefacto de una ventana de 758. **El defecto es la ESCALA, no el signo.**

### Predicciones escritas para S129 (P-C3 es la que decide)
P-C1 C1 en D1 converge a `[~0.95, ~1.60554]` · P-C2 amplitud D1 > H1 > M5 · **P-C3 `legExtLo` baja de
1.13246 a ~0.95-1.02 → los 5 OB + 11 FVG + 1 BRK + 3 IFVG del censo S127 entran en banda 1-3** · P-C4
anidamiento D1 ⊇ H1 ⊇ M5 > 90% (**plausible, NO identidad matemática → medir, no asumir**) · P-C5 C1
reancla ≲5 veces en D1 y muchas en M5.

### Costes (NO es Visual-only)
Toca el **LIBRARY CORE** (`f_resetTrailing*`/`f_updateTrailing` :1166-1190, consumidas por
`f_computeTFState` :1633) → **rompe el SHA**, re-baseline ×3, contrato MQL5 (ADR-002) → **ADR
obligatorio**. Rompe la **paridad LuxAlgo** (la Opción A *es* su `trailingExtremes`). **Invalida los
casos de prueba de §2.3** (validados al 5.º decimal contra LuxAlgo) → hay que rederivarlos = cambio de
doctrina. Lectura de Claude: CLAUDE.md dice que `reglas-smc-ict.md` es la fuente de verdad SMC y §2.3
dice "vigentes" ⇒ la doctrina gana sobre la paridad, **pero es decisión del usuario y va en el ADR**.

## Gotchas de método nuevos
1. **El arnés v2 midió HUMO.** `legExtHi/Lo` solo se pueblan en `islast` (`f_updateLegExtremes` corre
   1×/vela en la última barra) → en **toda la historia son `na`** → cualquier contador con guard
   `not na(legExtLo)` da **0 trivialmente**, no por evidencia. **Se delató por aritmética** (1221 vs
   541 ⇒ ≥680 abajo, incompatible con el 0). Antídoto: proxy computable en toda la historia
   (`min(nz(pdLow), nz(structMajor.lowLevel))`) + **descomponer contadores por lado** (un OR de dos
   lados no decide nada) + cross-check aritmético.
2. **TV solo deja 2 indicadores encendidos** (dato del usuario). Cada Ctrl+Enter crea instancia
   **NUEVA** en vez de reemplazar → el cupo se llena y **el apply deja de aterrizar EN SILENCIO**.
   Limpiar con `chart_manage_indicator remove` antes de aplicar.
3. **Patrón real del apply:** `pine_inject.py` **guarda**; 1.er Ctrl+Enter **guarda**; 2.º Ctrl+Enter
   **aplica** ("Compilado." + "Añadido al gráfico"). Confirma en console; `pine_get_errors` no sirve.
4. `data_get_study_values` devuelve **todas** las instancias: con duplicados conviven builds rancios y
   frescos lado a lado (se vio 1282 vs 1283 con contadores distintos). El `P_marker` por build es lo
   único que los distingue.

## CORE
- **SHA `752b4083a7db419d`** (1866 líneas) — **INTACTO** (`pine/` no se tocó)
- core-sync OK ×3 · `pine_check` 0/0

## Estado
- **F1-GATE BLOQUEADA** · SIN ADR · SIN tag · rama `pine/sistema-completo`
- Chart restaurado: Visual real aplicado, 1 solo estudio, slot `SMC_Library` v258 = repo

## Pendiente S129 (decidido con el usuario)
1. **Construir el probe de C1/C2 en sombra** (`scripts/gen_probe_rango_pegajoso.py`) y medir P-C1..P-C5.
   Sin tocar `pine/`. **P-C3 decide.**
2. Si P-C3 verde → **ADR** (sustituye T07/S021; resuelve doctrina §2.3 vs paridad LuxAlgo) + rederivar
   los casos de prueba de §2.3.
3. Implementar en CORE + re-baseline SHA ×3 + core-sync + MQL5-PLAN.
4. Recién entonces #3 (IFVG: disciplina banda/lado) y #4 (MB/BPR: gate de banda) — **hoy se medirían
   sobre una geometría equivocada**.
5. Calibrar `LEG_ANCH_TOL_ATR` (provisional 1.0) · `elig` excluye ZS_MITIGATED del band-pick en Visual
   (Parte A de S108) · deudas S123 #2/#3/#4 + auditoría de herencia MTF.
6. Deuda nueva: con C, `i_pdSwingLen` deja de fijar la ventana y pasa a fijar solo la escala del pivote
   de reanclaje → su default (50) se hereda **sin recalibrar**.
7. DESCARTADO definitivamente: calibrar `i_kLeg` (su clamp nunca actúa).

## Predicciones
**P1 ✅ · P2 ✅ · P3 ✅ · P4 ❌** (falló justo la tesis heredada de S127). Van **4 vivas de 12**.

## Enlaces
[[Sesion-127]] · [[Sesion-126]] · [[Sesion-125]] · `docs/planes/DISENO-ancla-dealing-range-S128.md` ·
`docs/planes/DISENO-opcion-C-rango-pegajoso-S128.md` · `docs/decisiones-pd-rango.md`
