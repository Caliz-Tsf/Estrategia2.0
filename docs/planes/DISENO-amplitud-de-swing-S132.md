# DISEÑO — La amplitud del swing como propiedad del pool (S132)

> Estado: **PROPUESTA**. `pine/` NO se toca hasta que la medición decida.
> Continúa [DISENO-regla-de-pools-S131.md](DISENO-regla-de-pools-S131.md) §6.1.
> Norma S114: **medir antes de tocar el CORE**. Norma S130/S131: **predicción escrita ANTES de medir**.

## 1. Por qué esta vía, y por qué es la última

S131 refutó con medición las cuatro alternativas baratas:

- **fuerza-por-toques** — los toques miden CONGESTIÓN, el usuario marca EXTREMOS: propiedades opuestas.
  Un máximo histórico no puede tener 2 toques (si los tuviera no sería el máximo). 37 de 38 pools vivos
  tienen 1 toque.
- **barrido de `i_poolTol`** (0.1 / 0.3 / 0.5=maxval) — satura en 0.3; los 5 niveles siguen a 1 toque
  en todo el barrido.
- **escala fija ×4**, **ventana `close ± X`**, **escala por ATR** — las tres descartadas contra los
  números del usuario (S131 §3bis.4).

Queda **una** propiedad que su ojo usa y el motor no registra: **la amplitud del swing que creó el pool**.

## 2. El hallazgo que abarata la medición

**La amplitud ya está calculada en el código.** `pine/SMC-Visual.pine:2246`:

```pine
float ampH = na(legPrev) or sAtr14 <= 0 ? 0.0 : math.abs(legPh - legPrev) / sAtr14
```

Máquina leg-based de S117 (`i_swingStructLen`), **L2232-2251 = FUERA del CORE** (CORE = L154..~L2019).
Es adimensional (÷ATR de la barra de confirmación = ATR histórico correcto) ⇒ multi-símbolo por
construcción (ADR-001). Ya se consume en `f_pushSwingLabel` vía `i_swingDomAtr`=8.0×ATR, que decide la
INTENSIDAD del tag (dominante 45 / menor 75), no su existencia (S125).

**Lo que falta NO es calcular la amplitud: es que el pool la RECUERDE.** `SMC_Pool` (L266) guarda
`level/dir/touches/barTime/swept/barIdx/strength`. La amplitud del swing que lo originó se pierde en
`f_upsertPool` (L1363), que recibe solo `level`.

Consecuencia de método: **la medición cabe entera fuera del CORE.** Solo el fix —si la medición sale
verde— rompe el SHA.

## 3. Los dos grupos a separar (datos medidos en S131)

Precio de referencia 1.14660. Los 38 pools vivos del set D1 con `i_poolTol`=0.1.

| Grupo | Niveles | Qué son |
|---|---|---|
| **A — los del usuario (5)** | 0.90494 · 0.95360 · 1.02108 · 1.39972 · 1.60063 | extremos que SÍ marca |
| **B — los intermedios (6)** | 1.036 · 1.0733 · 1.10654 · 1.12105 · 1.13246 · 1.1473 | pools vivos que NO considera pisos |

Los del grupo A están vivos y clavados al pip (S131: `hitD1lo` a 0.0 pips, `hitH1hi` a 3.6, `hitH1lo`
a 7.5). El motor no puede distinguirlos de B hoy.

## 4. La hipótesis

> **H:** la amplitud del swing (en ATR) separa A de B. Existe un umbral `T` tal que todo pool del
> grupo A tiene `amp >= T` y todo pool del grupo B tiene `amp < T`.

## 5. PREDICCIONES — escritas ANTES de medir

| # | Predicción | Qué la refuta | Letalidad |
|---|-----------|---------------|-----------|
| **P-A1** | **LA QUE DECIDE.** Existe un umbral `T` que separa A de B **sin solape**: `min(amp_A) > max(amp_B)`. | Cualquier solape: un solo pool de B con amplitud >= el más débil de A. | **Mata la vía entera.** |
| **P-A2** | El margen de separación es holgado, no marginal: `min(amp_A) >= 1.5 × max(amp_B)`. | Separación existe pero `< 1.5×` ⇒ umbral frágil, no calibrable multi-símbolo. | Media |
| **P-A3** | `T` cae en el entorno de `i_swingDomAtr`=8.0 (rango 4-15 ATR) ⇒ el umbral ya existente sirve y **no hace falta un input nuevo**. | `T` fuera de 4-15 ⇒ input nuevo ⇒ más superficie de calibración. | Baja |
| **P-A4** | Los 5 de A quedan en el **top-8** del set de 38 pools vivos ordenado por amplitud descendente. | Algún nivel de A cae fuera del top-8 ⇒ un "top-N por amplitud" no basta como política. | Media |
| **P-A5** | La amplitud NO correlaciona con los toques: de los 3 pools con `touches>=2` (1.51421, 1.25753, 0.97175), **ninguno** entra en el top-5 por amplitud. | Que coincidan ⇒ la amplitud sería un proxy de los toques, ya refutados ⇒ no aporta información nueva. | Media |

**Nota anti-tautología** (lección S130 P-G2/P-G5): P-A1 NO es tautológica. Nada garantiza que un pool
extremo nazca de un swing amplio — un máximo histórico puede ser el último pip de un tramo largo
*o* un pico estrecho sobre un techo ya alto. Es exactamente lo que la medida decide.

**Riesgo de definición** (lección S129 §3): "la amplitud del swing que creó el pool" es ambigua entre
dos lecturas. Se declara **antes** de medir cuál se usa:
- **(a) AMPLITUD DE LLEGADA** — `|level − pivote anterior| / ATR`: cuánto recorrió el precio para
  *llegar* a ese nivel. **Es la que ya calcula L2246 y la que se mide.**
- (b) amplitud de salida — cuánto se alejó el precio *después*. Requiere el pivote siguiente ⇒ no
  disponible en el momento del upsert ⇒ descartada (además huele a lookahead).

## 5bis. RONDA 2 — el probe v10 midió la ESCALA EQUIVOCADA (auto-corrección)

**Resultado de v10 (marker 1320, D1 EURUSD, 38 pools vivos = los de S131):**

| Grupo | nivel | amp (ATR) |
|---|---|---|
| A | 0.95360 | 5.05 |
| A | 1.02105 | 3.81 |
| A | 1.39937 | 3.41 |
| A | 1.60389 | 3.19 |
| A | 0.90275 | **0.0 (artefacto: primer pivote, sin previo)** |
| **B** | **1.13246** | **4.80** |
| **B** | **1.10654** | **4.75** |
| B | 1.1473 | 2.63 |
| B | 1.0733 | 2.19 |
| B | 1.036 | 1.65 |
| B | 1.12105 | 1.51 |

Anti-humo limpio: `P_nSinMatch`=0, `P_xcheckDump`=0, `P_nAlive`=`P_nPoolsDump`=38, `P_nPiv`=729,
`P_nAmpCeroPiv`=1 (solo el primer pivote de la historia). **El arnés no mide humo.**

P-A1 sale **falsa** (`P_margen` < 0), y el solape **no depende del artefacto**: aun excluyéndolo,
`min(A)`=3.41 < `max(B)`=4.80.

**PERO la lectura no es "la vía está muerta" — es "medí la escala equivocada".** La señal:
`max(amp)` de todo el set = **6.07** y `i_swingDomAtr` = **8.0** ⇒ *ningún* pool alcanza el umbral de
"swing dominante" ya existente. Eso es incoherente y delata el error: los pools nacen de
`f_detectSwings(i_swingLen)` con **i_swingLen=5** (zigzag de 5 barras) y v10 midió la amplitud contra
*ese* pivote anterior; la máquina de la que sale el 8.0 (L2232-2251) usa **i_swingStructLen=20**.
Mismo fallo que S129 (probe midiendo la lectura equivocada) y S130 (no era el ancla, era la escala).

**Ronda 2: barrido de escala** — en vez de otro viaje de ida y vuelta, se miden varias sensibilidades
de tramo a la vez: L ∈ {5 (=v10), 10, 20, 50, 100}, replicando la máquina leg-based con registro
propio SIN cap (`SMC_majorSwingsV` es FIFO con `i_swingMaxKeep`=350 ⇒ podría haber desalojado los
tramos de 2014 y dejar sin match los pools viejos).

| # | Predicción | Qué la refuta |
|---|-----------|---------------|
| **P-A6** | **LA QUE DECIDE (ronda 2).** Existe alguna escala L ∈ {10,20,50,100} con separación limpia: `min(amp_A) > max(amp_B)`. | Ninguna escala separa ⇒ la amplitud NO es la propiedad ⇒ **vía muerta, ahora sí**. |
| **P-A7** | La escala que separa (si existe) es L >= 20, y en L=20 `max(amp)` alcanza el entorno de `i_swingDomAtr`=8.0 ⇒ confirma el diagnóstico de desajuste de escala de v10. | En L=20 las amplitudes siguen muy por debajo de 8.0 ⇒ el 8.0 mide otra cosa y hay que averiguar qué. |
| **P-A8** | `max(amp)` crece monótonamente con L (tramos más largos ⇒ recorridos mayores). | No monótono ⇒ la máquina de tramos no hace lo que su comentario dice. |

## 5ter. RESULTADO RONDA 2 — la amplitud NO separa en NINGUNA escala (P-A6 FALSA)

Probe v11, marker 1321, D1 OANDA:EURUSD. Anti-humo limpio: `P_nHitA_L`=5 en las 5 escalas (tras
ampliar TOL_GRP a 40 pips — con 30, 1.60063 no casaba con el pool real 1.60389, a 32.6 pips);
`P_nAmpCeroPiv_L`=1 por escala (solo el primer pivote); `P_nPiv_L` = 740/409/204/86/38 (decreciente
con L, como debe).

| escala L | `min(amp_A)` | `max(amp_B)` | `P_margen_L` | `P_maxAmp_L` |
|---|---|---|---|---|
| 5 | 3.06 | 4.80 | **−1.74** | 6.07 |
| 10 | 2.70 | 6.21 | **−3.51** | 9.10 |
| 20 | 4.08 | 7.55 | **−3.48** | 13.48 |
| 50 | 3.30 | 22.46 | **−19.16** | 25.78 |
| 100 | 10.47 | 15.54 | **−5.06** | 42.61 |

**P-A6 FALSA en las 5 escalas.** Y no por poco: en L=50 el nivel **1.10654 (grupo B, descartado por el
usuario) nace de un tramo de 22.46×ATR** mientras su techo 1.60389 nace de uno de 3.30. En L=20,
1.12105 (B) da 7.55 y supera a **cuatro de los cinco** niveles de A.

**P-A7 — mitad confirmada, mitad vacía:** el diagnóstico de desajuste de escala de v10 era CORRECTO
(en L=20 `max(amp)`=13.48 supera el `i_swingDomAtr`=8.0 que en L=5 era inalcanzable, 6.07). Pero
corregir la escala **no salvó la hipótesis** ⇒ la mitad "la escala que separa es L>=20" es vacía:
ninguna separa. **P-A8 VERDE:** `max(amp)` crece monótonamente (6.07 → 9.10 → 13.48 → 25.78 → 42.61).

### Conclusión: la amplitud queda REFUTADA. Era la última vía de la lista.

Han caído, todas con medición: toques (S131 §3bis.3), clusterizado `i_poolTol` (S131 §3bis.3), tres
reglas aritméticas (S131 §3bis.4) y ahora la amplitud de swing en 5 escalas (S132). **Lo que el ojo
del usuario usa NO es una propiedad intrínseca del pool** de las que se han sabido nombrar.

**HIPÓTESIS QUE QUEDA VIVA (barata, y encaja con lo dicho por el usuario en S130):** puede que NO
exista propiedad intrínseca, y que la regla sea **puramente relacional** — "el pool más lejano dentro
del rango del TF superior", que es literalmente `f_farthestPool` (:1816), ya en el CORE. Los 6
intermedios no serían "débiles": serían *no-los-más-lejanos*. Si es así, el bloqueante **no** es un
campo que falte en `SMC_Pool`, sino el gate `i_minTouches`=2 que S131 midió dejando el suelo en `na`
(37 de 38 pools tienen 1 toque) ⇒ **el CORE no se toca**. Pendiente de confirmación del usuario.

## 5quater. LA PREMISA ERA FALSA — y la observación real del usuario

**El "grupo B — los 6 niveles que el usuario descarta" NUNCA EXISTIÓ.** Lo afirmó el doc de S131
(§3bis.4: *"6 pools vivos que el usuario NO considera pisos... son swings pequeños"*) y S132 lo heredó
como dato. El usuario, al ser preguntado: *"yo no descarto nada, todo lo que he dicho es observación"*.

⇒ **El contraste A-vs-B de §3 es una ficción.** Lo medido de verdad es "la amplitud no separa dos
grupos inventados" — los números de §5ter son correctos pero **la pregunta era falsa**. Se conservan
por honestidad y porque documentan el método, no porque decidan nada.

**Tercera vez con la misma causa raíz:** S129 midió la lectura equivocada (diseño ambiguo), S130
discutió 3 sesiones el ancla cuando era la escala, S132 midió una propiedad de un grupo ficticio. Las
tres veces: no volver a la observación original del usuario. **Norma nueva: ninguna medición arranca
sin citar la frase literal del usuario que la motiva.**

### La observación REAL (sus palabras): dónde marca el indicador el P/D de cada TF, ahora mismo, y no da

Medido en vivo (Visual limpio, una instancia, sin overrides, todo apagado salvo P/D + panel +
herencia D1/H1):

| TF | rango que marca el motor | amplitud | lectura del usuario | ¿cuadra? |
|---|---|---|---|---|
| D1 | **[0.95360, 1.60389]** (Discount 30%) | 6503 pips | [0.90494, 1.60063] | **sí** |
| H1 | **[1.13246, 1.18492]** (Discount 27%) | **525 pips** | [1.02108, 1.39437] = 3733 pips | **NO — 1100 pips de error en el suelo** |
| M5 | (Premium 89%) | — | local | no |

En el chart H1 el propio indicador etiqueta: `Premium 1.18492` · `EQ 1.15869` · `Discount 1.13246`,
y al fondo `D1: Discount 0.95360` (heredado, que sí cuadra).

### La causa: `i_pdSwingLen` es un CONTADOR DE BARRAS compartido por los 3 TF

| TF | 1000 barras = | resultado |
|---|---|---|
| D1 | ~4 años | cuadra con el usuario |
| H1 | **41 días** | 525 pips |
| M5 | ~3.5 días | local |

S130 arregló D1 barriendo este input (50→1000). **Nadie lo barrió para H1/M5 porque es el MISMO input
para los tres.** Lo que en D1 son 4 años, en H1 son 41 días.

### La salida (ya documentada como gotcha de S130, sin explotar)

`f_computeTFState(swingLen, pdLen, ...)` **ya recibe `pdLen` como parámetro**; sus call-sites
(:2970/:2971/:2976) están **FUERA del CORE** ⇒ un `pdLen` por TF cuesta **2 inputs, sin ADR, sin
romper el SHA `752b4083a7db419d`**.

**Techo conocido (S129, honestidad antes de ilusionarse):** el techo H1 del usuario (1.39972) es de
2014 ≈ 75.000 barras H1; TV da 9.535 ⇒ barriendo el input, H1 alcanza como mucho
**[~1.01779, 1.20831]** ⇒ **daría su SUELO (1.01779 ≈ su 1.02108) pero NUNCA su techo**. Coherente
con S129: su techo de H1 vive en D1 ⇒ herencia, no recálculo nativo.

## 6. Cómo se mide (todo fuera del CORE)

1. Probe en sombra sobre `SMC-Visual.pine`, marker `P_marker`=1320 (identidad de build, gotcha S127/S129).
2. En el bloque chart-level de pools (L2687, fuera del CORE), calcular la amplitud de llegada de cada
   swing con la misma fórmula de L2246 y volcarla en paralelo al nivel.
3. Censo de los 38 pools vivos por `data_get_pine_labels` (canal que **no** sigue el crosshair —
   gotcha S131; `data_get_study_values` sí lo sigue y devolvió `nPools`=0).
4. Contraste: `min(amp_A)` vs `max(amp_B)`, orden por amplitud, y cruce con `touches`.

**Cross-checks obligatorios** (lección S128: el arnés midió humo): contador que confirme que las
amplitudes NO son todas 0.0 (el `na(legPrev)` de L2246 devuelve 0.0 como fallback silencioso) y que el
nº de pools volcados == 38.

## 7. Coste SI la medición sale verde

Añadir `float swingAmp` a `SMC_Pool` (L266) + un parámetro a `f_upsertPool` (L1363) ⇒ **toca el CORE**
⇒ rompe SHA `752b4083a7db419d` ⇒ re-baseline ×3 (`check-core-sync`) ⇒ contrato MQL5 (Fase 4) ⇒
**ADR obligatorio** — ya con evidencia medida detrás, no con una corazonada.

Cuestión abierta para el ADR (no para esta sesión): al fusionar dos pools, ¿qué amplitud sobrevive?
La máxima es lo coherente con "el pool hereda la fuerza de su mejor swing", pero es una decisión.

**OBSOLETO:** §5ter refutó la amplitud en 5 escalas y §5quater mostró que el contraste que la motivaba
era ficticio. **No se implementa. No hay ADR.** Esta sección se conserva como registro.

## 7bis. LA DOCTRINA vs LA IMPLEMENTACIÓN — y el fix de S130 es incorrecto

Pregunta del usuario: *"según mi método sí, ¿y según la metodología?"*. Contestado contra
`docs/reglas-smc-ict.md` (fuente de verdad, CLAUDE.md).

**La doctrina le da la razón en lo esencial:**
- **§2.3:** el dealing range va del último **strong high** al **strong low**; su tabla dice
  *"rango | strong high/strong low vigentes | **se actualiza con la estructura**"* ⇒ **swings
  estructurales**, no una ventana de N barras. **La implementación actual (ventana de `i_pdSwingLen`
  barras por TF) YA VIOLA §2.3.** El ruido del usuario es incumplimiento de doctrina, no preferencia.
- **§6.3.5:** *"EL relevante = el rango **dominante** activo. **Descarta** (citable): medir P/D sobre
  un rango ya superado por estructura"* ⇒ **el rango fósil está prohibido por regla**. Es exactamente
  su objeción de operabilidad ("en un mercado alcista quizás nunca vuelvan a su bajo más bajo").

**Dónde su modelo EXTIENDE la doctrina (⇒ ADR):** la cascada de pivotes anidados por TF **no** está en
la doctrina. §2.3 (MTF) dice *"transferible como **bandas del HTF heredadas** a M5"* y §5.16 remacha:
*"los gradient levels de un rango-fuente HTF son **globales** (mismos en todo TF), **no se recomputan
por TF**"*. La doctrina = **un rango dominante por escala, heredado hacia abajo**.

### El fix de S130 (`i_pdSwingLen` 50→1000) es DOCTRINALMENTE INCORRECTO

`i_pdSwingLen` **no es un lookback**: es la **sensibilidad del pivote**. Va a `f_detectSwings(pdLen)`
(exige superar `pdLen` barras **a cada lado**); luego `f_resetTrailingHigh/Low` (:1176-1186) ancla el
rango a ese swing y `f_updateTrailing` lo expande. **§5.16 dice literalmente: *"strong high ↔ strong
low, escala `pdSwingLen=50`"***.

Con 1000: "un swing necesita 1000 barras a cada lado" ⇒ casi ningún pivote califica ⇒ el ancla queda en
un extremo casi global y **solo actúa el trailing** ⇒ **es el rango fósil que §6.3.5 manda descartar**.
Cuadró con el ojo del usuario en D1 **por accidente del mecanismo**, no porque el ancla se volviera
estructural. Y es lo que destrozó H1/M5 (1000 barras a cada lado en H1 = el ancla nunca se refresca).

### MEDIDO (in_69: 1000 → 50, D1 OANDA:EURUSD, cero código)

Predicciones escritas antes: **P-D1, P-D2, P-D3 las tres VERDES.**

| TF | `pdLen`=1000 (repo hoy) | `pdLen`=50 (doctrina §5.16) |
|---|---|---|
| D1 | Discount 30% | **Discount 18%** — rango [1.13246, 1.20831] = 758 pips (líneas 1.21/1.17/1.13) |
| H1 | Discount 27% | **Premium 82%** ← **se INVIERTE** |
| M5 | Premium 88% | **Premium 76%** |

**HALLAZGO NO PREDICHO (el importante): con la escala doctrinal, D1 Discount 18% y H1 Premium 82%
SIMULTÁNEAMENTE** = la lectura anidada que pide el usuario (barato en el rango grande, caro en el
pequeño; el pullback está extendido en local pero el macro sigue abajo). **La cascada ROTA.**

Con 1000 era imposible: D1 y H1 salían casi iguales (30% / 27%) porque ambos eran rangos fósiles
gobernados solo por el trailing — **decir lo mismo en las 3 TF es no decir nada**. El 1000 no solo
rompía §5.16: **destruía la rotación que hace operable el sistema**. Es lo que S130 perseguía con la
"cascada de mitades" (que midió ROTA) y que **con la escala doctrinal sale sola y sin código**.

**P-D3 — la tensión, nombrada:** D1 doctrinal = 758 pips vs lectura del usuario = 6503 pips. No cuadran
y no van a cuadrar. **No es que uno esté mal: son DOS OBJETOS DISTINTOS** (mismo patrón que S130: su H1
de 3780 y el H1 nativo de 1905 eran objetos distintos). Su rango de 6503 **no es el dealing range de
D1: es el CONTEXTO MACRO**. El dealing range de D1 es la estructura dominante vigente (758 pips) y se
actualiza — que es lo que §6.3.5 exige y lo que lo hace operable.

**ARQUITECTURA PROPUESTA (3 capas, no una peleándose consigo misma):**
1. **Contexto macro** — el rango de 6503 pips del usuario ⇒ para eso existen el consumidor Context
   (ADR-017) y la herencia §5.16/ADR-018. No es el dealing range.
2. **Dealing range operable por TF** — doctrinal, escala 50, rotando (§2.3 + §6.3.5). **Revertir el
   fix de S130.**
3. **Cascada de pivotes anidados del usuario** — encima de (2), con ADR (extiende §2.3 MTF).

## 8. SIGUIENTE (S133) — barrer `i_pdSwingLen` por TF (el método que SÍ funcionó)

**Cero código, cero CORE, cero ADR** para medir — igual que S130.

1. **Barrido de `pdLen` para H1** vía `indicator_set_inputs` (in_69 hoy es global; para barrer por TF
   hace falta el input nuevo, así que el barrido de la medición se hace **cambiando el TF del chart** y
   observando el rango dibujado, o con un probe que parametrice los call-sites :2970/:2971/:2976).
   **Predicción a escribir ANTES:** existe un `pdLen_H1` que lleva el suelo de H1 de 1.13246 a
   ~1.01779 (≈ su 1.02108); el techo se queda en ~1.20831 y **nunca** alcanza su 1.39972 (límite del
   feed, S129) ⇒ el techo de H1 debe **heredarse de D1**, no recalcularse.
2. Si el barrido confirma ⇒ implementar `pdLen` por TF = **2 inputs fuera del CORE, sin ADR**.
3. Repetir para M5.
4. **NO repetir** (todos refutados con medición): cascada de mitades y mapeo nivel→TF (S130),
   fuerza-por-toques y barrido de `i_poolTol` (S131), amplitud de swing en 5 escalas (S132).
