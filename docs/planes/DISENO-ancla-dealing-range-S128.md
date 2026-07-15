# DISEÑO — El ancla del dealing range (Opción A vs B vs híbrido) · S128

> Pendiente #1 de S127. Diseño + probe ANTES de tocar `pine/` (norma S114).
> **Estado: PROPUESTA — nada implementado, `pine/` intacto, CORE SHA `752b4083a7db419d`.**
> Fuentes: [docs/decisiones-pd-rango.md](../decisiones-pd-rango.md) (decisión T07 + notas S057/S091),
> [docs/reglas-smc-ict.md §2.3](../reglas-smc-ict.md), [[Sesion-127]].

## 0. Por qué esto se reabre (y por qué no es re-litigar)

La Opción A (trailing extremes de LuxAlgo) fue elegida en S021 y **re-confirmada por el usuario dos
veces** (S057, S091), con el cambio a B congelado hasta **Fase 3 con datos out-of-sample**
(anti-overfitting, ADR-002). `decisiones-pd-rango.md` lo registra explícitamente "para no re-litigar
en Fase 1".

Lo que S127 puso sobre la mesa y S057/S091 **no tenían**: el trailing que solo expande es la causa
estructural de que las **bandas 4/5 sean incapaces por construcción** (la rotación archiva fotos de
un rango que solo crece → toda foto vieja es subconjunto de la actual → `i_profundidad` 4/5 no puede
funcionar nunca). Eso es un argumento sobre el **alcance**, no sobre la lectura premium/discount.

Este documento NO propone cambiar el ancla. Propone **medir** si cambiarla arregla algo, porque la
lectura de código de S128 encontró dos hechos que apuntan a que no — o a que lo empeora.

## 1. Hallazgo de lectura de código (S128): la Opción B ya está computada, y el alcance ya la usa

### 1.1 `structMajor` ES el ancla de la Opción B

La Opción B se definió como "el rango delimitado por el último strong high y strong low marcados por
la estructura". Eso es exactamente `structMajor` ([SMC-Visual.pine:2178](../../pine/SMC-Visual.pine)):
se fija con `f_setStructureHigh/Low` sobre swings confirmados de escala `i_majorLen` = **50** y lo
actualiza `f_detectStructure` (BOS/CHoCH) en [SMC-Visual.pine:2284](../../pine/SMC-Visual.pine).

`i_majorLen` = 50 = `i_pdSwingLen` = 50: **A y B se anclan a la MISMA escala de swing**. La única
diferencia real entre A y B es qué pasa ENTRE reanclajes: A **expande** con el precio
(`f_updateTrailing`), B **no** (el nivel estructural se queda quieto hasta que la estructura lo
mueve). No es "otra escala", es "expande vs. no expande".

Consecuencia inmediata: implementar B **no requiere detección nueva**. Los dos anclajes ya conviven
en el chart. Eso hace el probe barato y descarta el argumento de S021 "B = más estado y más frágil de
portar": el estado ya existe y ya se porta.

### 1.2 El alcance (bandas) YA usa la UNIÓN de A y B — cambiar el ancla no lo puede ensanchar

`f_computeLegExtremes` fase 1 ([SMC-Visual.pine:3149](../../pine/SMC-Visual.pine)) toma el **más
lejano por lado** entre el rango vigente y `structMajor`:

```pine
float hi = chartState.pdHigh
float lo = chartState.pdLow
if not na(structMajor.highLevel) and (na(hi) or structMajor.highLevel > hi)
    hi := structMajor.highLevel
if not na(structMajor.lowLevel) and (na(lo) or structMajor.lowLevel < lo)
    lo := structMajor.lowLevel
```

`legExtHi/Lo` = `max(pdHigh, structMajor.high)` / `min(pdLow, structMajor.low)` (más HTF heredado en
H1/M5). Las bandas 1-3 se miden sobre `legExtHi/Lo`, **no** sobre `pdHigh/pdLow`.

**Por tanto: sustituir A por B en el ancla no puede extender el alcance vivo — B ya está dentro de la
unión.** Y en el estado medido en S127 (`structMajor_low` 1.14110 > `pdLow` 1.13246), el mínimo de la
unión lo aporta **A**: quitar A del ancla subiría `legExtLo` de 1.13246 a 1.14110 y **perdería 86
pips de alcance hacia abajo** — justo lo contrario de lo que pide la pendiente #2.

> **Corrección a la premisa de la pendiente #1 de S127** ("el ancla define la geometría de la que
> depende el alcance, arreglarlo antes evita construir sobre un rango equivocado"): la geometría del
> **alcance vivo** no depende del ancla del P/D, porque ya es la unión de ambos anclajes. El ancla
> del P/D gobierna otras tres cosas (§2), y una de ellas sí es la pendiente #2.

## 2. Qué gobierna realmente `chartState.pdHigh/pdLow` (dónde A→B SÍ muerde)

| Consumidor | Dónde | ¿Le afecta A→B? |
|---|---|---|
| **Veredicto P/D** (zona + pct) → panel y confluencia #31 | [:5035](../../pine/SMC-Visual.pine) | **SÍ** — es la objeción del usuario. S127 midió que ambos anclajes dan *discount* en este estado (no resuelto con 1 punto). |
| **Archivo `pdPrev1/2`** → bandas 4/5 | [:3087-3102](../../pine/SMC-Visual.pine) | **SÍ — y es la clave.** Ver §3. |
| **Alcance `legExtHi/Lo`** → bandas 1-3 | [:3147](../../pine/SMC-Visual.pine) | **NO** (unión, §1.2). Naive incluso lo empeora. |
| **Clamp `i_kLeg × rng`** | [:3169](../../pine/SMC-Visual.pine) | Irrelevante — S126/S127 midieron que el clamp nunca actúa. |

## 3. La hipótesis fuerte: B es el mecanismo que puede resucitar las bandas 4/5

S127 probó que con A el archivo es **siempre anidado**: `pdHigh/pdLow` solo expanden entre
reanclajes, así que una foto vieja de un rango creciente es siempre subconjunto del actual → banda
4/5 no cubre nada que no fuera ya banda 1-3.

Con B eso **deja de ser cierto por construcción**: un nivel estructural sí puede CONTRAER (cuando la
estructura reancla a un swing más alto/bajo, el extremo viejo se abandona). Un rango estructural
previo **puede quedar fuera** del actual → el archivo dejaría de ser subconjunto → `i_profundidad`
4/5 tendría algo real que cubrir bajo el suelo actual.

**Esto justifica el orden que pidió el usuario** ("el orden importa"): no porque el ancla defina el
alcance vivo (no lo define, §1.2), sino porque el ancla define **el archivo**, y el archivo es la
única vía existente hacia la pendiente #2.

## 4. PREDICCIONES (escritas ANTES de medir — van 1 viva de 8)

| # | Predicción | Falsa si |
|---|---|---|
| **P1** | `zoneA == zoneB` en la **gran mayoría** de barras confirmadas (desacuerdo **< 20%**). El punto único de S127 no era casualidad. | desacuerdo ≥ 20% |
| **P2** | `structMajor.lowLevel >= pdLow` en la **mayoría** de barras (B es **más estrecho por abajo**) → B a secas **reduce** el alcance. | B es más ancho por abajo la mayoría del tiempo |
| **P3** | `legExtLo` ≡ `min(pdLow, structMajor.lowLevel)` salvo clamp/snap → confirma la unión de §1.2 por identidad, no por lectura. | difieren fuera de clamp/snap |
| **P4** | **La de la casa.** Con la MISMA regla de rotación, el archivo de A da **0** casos no-anidados y el de B da **> 0**. Es decir: B resucita las bandas 4/5 y A no puede. | ambos 0 (B tampoco arregla la #2) o A > 0 (S127 estaba mal) |

**P4 es la que decide la sesión.** Si sale 0/0, la Opción B no compra nada de lo que pediste y el
re-baseline del CORE no se justifica; la pendiente #2 necesita otro mecanismo. Si sale 0/>0, hay un
argumento medido — nuevo respecto de S057/S091 — para levantar la congelación con ADR.

## 5. El probe (`scripts/gen_probe_ancla_rango.py`)

Solo LEE. No cambia `pine/`. Truncado en `// === DIBUJO ===` (obligatorio: CE10117, gotcha S127 #3).

Mide sobre **historia acumulada** (contadores en `barstate.isconfirmed`), no en un punto — que es
exactamente lo que le faltaba a S057 y S091:

- `P_nBars` — denominador.
- `P_nDisagree` — barras con `zoneA != zoneB` → **P1**.
- `P_nBnarrowLo` / `P_nBwiderLo` — comparación `structMajor.lowLevel` vs `pdLow` → **P2**.
- `P_legExtLo_id` — `legExtLo - min(pdLow, structMajor.lowLevel)` → **P3** (0 = identidad).
- `P_nA_arch_out` / `P_nB_arch_out` — **P4**: misma regla de rotación (borde > 0.5×ATR, copiada de
  [:3093](../../pine/SMC-Visual.pine)) aplicada a los dos anclajes; cuenta las barras en que el
  archivo previo cae FUERA del rango vigente (no-anidado = la banda 4/5 cubriría algo nuevo).
- `P_pctA` / `P_pctB` — la lectura P/D de cada ancla, para el ojo.

**Control de identidad de build** (gotcha S127 #2): `P_marker` = 128.

## 6. Opciones sobre la mesa (para el ADR, si P4 lo justifica)

- **A (statu quo).** Trailing extremes. Paridad LuxAlgo, estado plano, MQL5 limpio. Bandas 4/5
  muertas para siempre.
- **B pura.** Ancla estructural. Resucita el archivo; **pierde alcance vivo por abajo** (§1.2) salvo
  que se conserve la unión en `f_computeLegExtremes` — que ya está ahí y no hay por qué tocar.
- **Híbrido (el que describió el usuario en S057/S091).** Mantener anclado el extremo NO roto;
  reanclar solo el roto. Conserva alcance y da contracción → archivo no-anidado.
- **B solo-para-el-archivo (mínimo invasivo, propuesta S128).** Dejar `chartState.pdHigh/pdLow` = A
  intactos (CORE INTACTO, SHA intacto, paridad LuxAlgo intacta, scoring intacto) y alimentar la
  rotación `pdPrev1/2` desde `structMajor` (Visual-only, fuera del CORE, sin ADR de CORE). Si P4 sale
  0/>0, **esto arregla la pendiente #2 sin re-litigar el ancla del P/D en absoluto** y sin romper el
  SHA. Es la opción que el hallazgo §1.2 pone sobre la mesa y que no existía en S057/S091.

## 6bis. RESULTADO MEDIDO (S128, en vivo D1 OANDA:EURUSD)

Probe v3 aplicado, `P_marker` = 1283 verificado (build fresco, no rancio), console "Compilado." +
"Añadido al gráfico" sin CE10117. **n = 6283 barras D1 confirmadas.** `close` 1.14357.

| Métrica | Valor | Lectura |
|---|---|---|
| `P_nBars` | 6283 | denominador |
| `P_nDisagree` | **204 (3.2%)** | **P1 ✅** — A y B coinciden en el veredicto P/D el **96.8%** del tiempo |
| `P_nBnarrowLo` / `P_nBwiderLo` | 1759 / **0** | **P2 ✅ (más fuerte de lo predicho)** — `structMajor.lowLevel` **NUNCA** baja de `pdLow` en 6283 barras |
| `P_legExtLo_id` | **0** | **P3 ✅** — `legExtLo` ≡ `min(pdLow, structMajor.lowLevel)`: la unión de §1.2 queda probada por identidad |
| `P_nA_arch_out` / `P_nA_arch_aboveHi` | 1221 / 541 | descomponen exacto: 1221 − 541 = **680** = lado bajo (sin solape) |
| `P_nA_arch_belowLeg` | **680 (10.8%)** | **P4 ❌ REFUTADA** — el archivo de A **SÍ** cae bajo el alcance |
| `P_nA_arch2_belowLeg` | **898 (14.3%)** | idem `pdPrev2` |
| `P_nB_arch_belowLeg` | **1504 (23.9%)** | B cubriría **2.2×** más que A |

Estado actual: `pdPrev1Lo` 1.13757 · `pdPrev2Lo` 1.14110 · `bPrev1Lo` 1.14686 — **todos por ENCIMA de
`pdLow` 1.13246** → hoy el archivo está anidado y la banda 4/5 no revela nada. **Dormido ≠ muerto.**

### Veredicto

1. **P1+P2+P3 sostienen §1 y §2: cambiar el ancla A→B NO se justifica.** Mueve el veredicto P/D en
   el 3.2% de las barras y **no puede** ensanchar el alcance (P2: B nunca está más abajo, en 0 de
   6283 barras) — a cambio de romper el SHA del CORE, re-baseline ×3, la paridad LuxAlgo y el
   contrato MQL5 de Fase 4. **Recomendación: mantener Opción A.** La congelación de S057/S091 se
   sostiene, ahora con medición detrás y no solo por diferimiento.
2. **P4 refutada → se corrige S127.** "Las bandas 4/5 son incapaces POR CONSTRUCCIÓN" es **FALSO**.
   El error de razonamiento: S127 asumió que `pdHigh/pdLow` solo expanden, pero `f_resetTrailingHigh/Low`
   **REANCLA** (mueve el nivel hacia dentro), así que el rango **sí contrae** al reanclar y el archivo
   **sí** puede quedar no-anidado. Medido: **680/6283 barras (10.8%)** con `pdPrev1Lo` por debajo del
   alcance. Las bandas 4/5 funcionan ~11-14% del tiempo; **hoy están dormidas, no muertas**.
3. **La pendiente #2 sigue viva pero cambia de forma.** No hace falta rediseño ni ADR para
   "resucitar" las bandas 4/5: ya funcionan a veces. Lo que hay que decidir es si el 10.8% basta, y
   si conviene la opción §6-D (alimentar el archivo desde `structMajor`, Visual-only, sin tocar el
   CORE) que lo llevaría a 23.9%. **Pero hoy ni A ni B revelan nada** (los tres archivos están
   anidados en esta barra) → el lado de abajo vacío del censo S127 **no lo explica el archivo**;
   apunta a la geometría ya medida en S127 (banda arriba 643 pips vs abajo 115, precio en discount
   14%).

Predicciones: **P1 ✅ · P2 ✅ · P3 ✅ · P4 ❌**. Van **4 vivas de 12**.

## 7. Riesgos / notas

- Tocar `f_updateTrailing` / `f_resetTrailing*` es **CORE** ([:1166-1190](../../pine/SMC-Visual.pine),
  consumido por `f_computeTFState` [:1633](../../pine/SMC-Visual.pine)) → rompe el SHA, re-baseline
  ×3, core-sync ×3, contrato MQL5 de Fase 4 (ADR-002). La opción §6-D **no** toca el CORE.
- `pdPrev1/2` y `f_depthBand` ya viven fuera del CORE ([:3087](../../pine/SMC-Visual.pine)) → la
  opción §6-D es Visual-only bajo ADR-016/ADR-019, precedente S118/S125/S127.
