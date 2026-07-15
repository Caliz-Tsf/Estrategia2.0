# DISEÑO — La regla de pools: qué pool ancla el rango de cada temporalidad (S131)

> Estado: **PROPUESTA**. Sucede a `DISENO-cascada-pd-anidada-S130.md` §9 (la regla correcta) y **cierra**
> §2 de ese doc (cascada de mitades, refutada) y el mapeo nivel→TF (refutado, S130 probe v6).
> Norma S114: **diseño y probe primero**. `pine/` NO se toca en esta sesión.

## 1. La regla, ya desambiguada (decisión del usuario, S131)

La §9 de S130 decía dos cosas que no eran la misma ("el **siguiente** pool" en la regla 1 y en la
regla 2). Resuelto por el usuario **antes** de medir — la lección de S129 fue que un diseño ambiguo
hace que el probe mida la lectura equivocada:

1. **Qué pool ancla el extremo de un TF:** el pool **MÁS LEJANO** del precio, con fuerza suficiente,
   **dentro del rango del TF superior**. No el más cercano. H1 nace ancho y **anidado por
   construcción**; la regla 2 de §9 (saltar al consumir) solo actúa al romper el bound.
2. **De dónde salen los pools que ve un TF:** de la **UNIÓN** — los pools heredados de D1 **más** los
   nativos del TF. *La liquidez no pertenece a una temporalidad.* Es la única lectura que puede
   reproducir el techo H1 = 1.39972 del usuario, que **no existe en el feed de H1**.

### 1.1 Lo que esto significa en código (leído, no medido)

`f_farthestPool` (`pine/SMC-Visual.pine:1816`) **ya es exactamente esta regla**: "pool con
`touches >= minT` más lejano de `px` en el lado, dentro de `bound`". No hay que inventarla.

La diferencia con lo implementado hoy está en **el `bound`**: `f_tfExtremes` lo calcula como
`close ± kExt × rango` (`:2001-2002`) — una **distancia aritmética alrededor del precio**. La regla
del usuario dice que el bound de H1 **es el rango de D1**. Los call-sites (`:2970/:2971/:2976`) están
**FUERA del CORE** ⇒ el cambio de bound no rompe el SHA `752b4083a7db419d`.

## 2. La consecuencia que hay que dejar por escrito ANTES de medir

**Un pool que el precio ya revisitó está `swept`, y `swept` es el primero en ser borrado.**

- `f_markPoolsSwept` (`:1389`) marca `swept := true` a **todo** pool vivo cuyo nivel cruza la barra:
  BSL si `barHigh >= level`, SSL si `barLow <= level`. No distingue "tomada y sigue" de "tocada hace
  10 años".
- `f_prunePools` (`:1425`) al desbordar `MAX_POOLS = 50` (`:231`) borra **primero el barrido más
  antiguo**. El transporte `f_computeTFState`/`f_tfExtremes` usa 50; solo el chart usa 80
  (`MAX_POOLS_CHART`, `:2084`).
- `f_farthestPool` (`:1830-1844`) **prefiere vivos** y solo cae a barridos si `inclSwept`.

Los niveles que el usuario lee (techo H1 **1.39972**, suelo **1.01854 = `SSL -3`**, suelo D1
**0.95360**) son de 2014-2022. El precio los cruzó muchas veces desde entonces. Si el razonamiento de
arriba se sostiene, **están `swept` y probablemente ya han sido borrados del set** — y entonces la
regla de pools **no tiene a qué anclar**, por muy correcta que sea conceptualmente.

**Esto es una hipótesis de lectura de código, no un hecho.** Es la más barata de medir y la que puede
matar el modelo entero, así que va primero.

## 3. Predicciones (escritas ANTES de medir — van **15 vivas de 32**)

**P-P1 (la que decide, M4).** En D1 EURUSD, con `i_pdSwingLen=1000`, **ninguno** de los tres niveles
del usuario (0.95360, 1.01854, 1.39972) sobrevive como pool **VIVO** en `SMC_pools` al llegar a la
última barra. Concreto: `nAliveAbove` (pools vivos con `level > close`) **<= 3**, y el más alto de
ellos está **por debajo de 1.39972**.

**P-P2 (M4, el prune).** El set de pools **desborda** `MAX_POOLS=50` en D1: `nPruned > 0` y de hecho
`nPruned > 500` en n=6283 barras. El pool de 1.39972, si existió, **fue borrado** (`nPruned` incluye
barridos antiguos que es justo lo que él es).

**P-P3 (M1, la fuerza).** La fuerza de anclaje **no discrimina** porque casi no hay pools fuertes: de
los pools vivos en D1, `nTouches>=3` será **<= 2** en todo el set. El `SSL -3` que el usuario lee
tiene 3 toques ⇒ si P-P1 es cierta, ese pool **no está en el array**, y el `-3` que él ve viene del
**chart** (`MAX_POOLS_CHART=80` + `f_prunePoolsV`, desalojo por importancia, `:2089`), **no** del
transporte que alimenta `f_tfExtremes` (que usa 50 y `f_prunePools`, desalojo por antigüedad).
**Corolario:** el usuario y el motor P/D están mirando **dos sets de pools distintos**.

**P-P4 (M3, el anidamiento).** Con bound = rango D1, el anidamiento D1 ⊇ H1 ⊇ M5 se sostiene
**trivialmente por construcción** (el bound lo fuerza) ⇒ **medirlo es tautológico y no discrimina
nada**. Lo que NO es tautológico y sí hay que medir: **cuántas barras H1 se queda SIN pool dentro del
bound** (`nNoPoolUp` / `nNoPoolDown`) ⇒ eso es M2. Predicción: `nNoPoolDown` **> 30%** de las barras
(el lado de abajo está vacío, S127).

**P-P5 (M2, el fallback).** Cuando no hay pool en un lado dentro del bound, hoy `f_farthestPool`
devuelve `na` ⇒ el extremo de ese lado **es `na`** ⇒ `f_premiumDiscount` no puede calcular. Predicción:
**el lado de abajo de H1 cae en el fallback más del 30% de las barras** ⇒ el fallback **no es un detalle,
es la mitad del sistema**, y no puede ser arbitrario (§9.2).

### 3.1 Anti-humo (lecciones S128/S129/S130)

- **S128:** `legExtHi/Lo` solo se pueblan en `islast` ⇒ contadores con guard `not na()` miden **humo**.
  Aquí: todo contador debe computarse sobre **toda la historia** y **descomponerse por lado**, con
  cross-check aritmético.
- **S129/S130:** `data_get_study_values` devuelve **builds rancios** y sigue el crosshair ⇒ **`P_marker`
  nuevo por build** (S131 usa **1310**) y verificar que el marker leído es el inyectado.
- **P-P4 se declara tautológica de antemano**: si sale verde, **no cuenta como predicción viva**
  (S130 tuvo 2 tautológicas coladas como verdes).

## 3bis. RESULTADO MEDIDO (S131, probes v7/v9, marker 1310/1312, D1 OANDA:EURUSD, n=6283)

**Cross-checks los 3 en 0** (`P_xcheckCenso`, `P_xcheckUp`, `P_xcheckDown`) ⇒ el censo no miente.

| Pred. | Resultado | |
|-------|-----------|---|
| P-P1 | `hitD1lo=1` a **0.0 pips** · `hitH1lo=2` a 7.5 · `hitH1hi=1` a **3.6** · `nAliveAbove=26` · `maxAliveLvl=1.60389` | ❌ |
| P-P2 | `nAtCap=5456` · `maxSize=80` | ✅ |
| P-P3 | `nAliveT3=1` (<=2 predicho). **El corolario es FALSO**: los niveles del usuario SÍ están en el set. | ✅ (número) |
| P-P4 | declarada tautológica antes de medir ⇒ **no cuenta** | — |
| P-P5 | `nNoPoolDown` = 1130/6283 = **18.0%** (>30% predicho) | ❌ |
| P-P6 | los extremos siguen a 1 toque en todo el barrido ✅; pero `touches>=2` llega a **3**, no >10 ❌ | ✅ (lo que decidía) |

**Vivas: 18 de 37** (P-P2, P-P3, P-P6 nuevas).

### 3bis.1 La hipótesis letal de §2 es FALSA

`swept` NO mata los niveles del usuario. Razón (no prevista): el precio **bajó de 1.39972 y nunca volvió**
⇒ ese BSL jamás fue barrido ⇒ sigue VIVO. El razonamiento "el precio los cruzó muchas veces" era falso.
`P_minAliveLvl=0.90275` y `P_maxAliveLvl=1.60389` son pools VIVOS = **los extremos históricos**.

**Corolario doctrinal (resuelve el bloqueante de S129 §COSTE NUEVO):** "min/max histórico" y "pool
estructural" **no compiten**. El extremo histórico es *necesariamente* un pool vivo — nada lo superó
nunca. §2.3 no se viola. **El ADR ya no tiene que elegir entre min/max y §2.3.**

### 3bis.2 HALLAZGO PRINCIPAL — `i_minTouches=2` deja la regla sin candidatos (gemelo de S130)

Volcado de los 38 pools vivos (label, `data_get_pine_labels`): **37 tienen `touches=1`**; el único con 3
es **1.51421**, que NO es ninguno del usuario. Como `f_farthestPool` exige `touches >= i_minTouches` (=2):

- **arriba solo 1.51421 pasa el gate** ⇒ medido `P_reglaUp = 1.51421` (el motor ancla ahí por ser el
  único candidato legal, no por criterio);
- **abajo NINGÚN pool vivo tiene 2 toques** ⇒ el suelo sale `na` ⇒ **no hay rango**.

Causa: `f_upsertPool` fusiona solo si `|Δlevel| <= i_poolTol × ATR`, con `i_poolTol=0.1` y ATR D1
~0.0055 ⇒ **5.5 pips**. Dos swings de años distintos casi nunca caen tan cerca ⇒ **el clusterizado está
apagado por un input.**

### 3bis.3 BARRIDO de `i_poolTol` — la opción barata queda CERRADA

| `i_poolTol` | pools vivos | `touches>=2` | los 5 niveles del usuario |
|---|---|---|---|
| 0.1 | 38 | 1 (1.51421) | todos a **1 toque** |
| 0.3 | 34 | 3 (+1.25753, +0.97175) | todos a **1 toque** |
| 0.5 (**maxval**) | 34 | 3 (idéntico: **satura**) | todos a **1 toque** |

**Los toques miden CONGESTIÓN; el usuario marca EXTREMOS. Son propiedades opuestas** — un máximo
histórico no puede tener 2 toques, porque si los tuviera no sería el máximo. Ningún valor legal de
`i_poolTol` hace emerger sus niveles. **La vía de la fuerza-por-toques está refutada.**

### 3bis.4 Lo que SÍ distingue sus niveles (y el motor no registra)

> ⚠️ **CORREGIDO EN S132 — ESTA SECCIÓN CONTIENE UNA PREMISA FABRICADA.** La afirmación "6 pools que
> el usuario NO considera pisos / no los descarta por toques sino por ser swings pequeños" **NUNCA la
> dijo el usuario**. Preguntado en S132: *"yo no descarto nada, todo lo que he dicho es observación"*.
> S132 midió la amplitud de swing en 5 escalas contra este contraste A-vs-B ficticio y gastó la sesión.
> **Su observación real es otra:** dónde marca el indicador el premium/discount **de cada temporalidad**
> ahora mismo, y que no da (causa medida en S132: `i_pdSwingLen` es un contador de barras compartido por
> los 3 TF ⇒ 1000 barras = 4 años en D1 pero 41 días en H1).
> Ver [DISENO-amplitud-de-swing-S132.md](DISENO-amplitud-de-swing-S132.md) §5quater.
> **Norma nueva: ninguna medición arranca sin citar la frase literal del usuario que la motiva.**

Entre 1.02108 y el precio hay **6 pools vivos** (1.036, 1.0733, 1.10654, 1.12105, 1.13246, 1.1473) que el
usuario NO considera pisos. No los descarta por toques ni por edad: son **swings pequeños**. `SMC_Pool`
guarda `level/dir/touches/barTime/swept/barIdx` — **no la amplitud del swing que lo creó**. Esa es la
única propiedad que su ojo usa y el motor no tiene. Ya existe para swings (`i_swingDomAtr`=8×ATR, S125),
es adimensional ⇒ multi-símbolo (ADR-001) por construcción.

**Reglas aritméticas descartadas contra sus números** (antes de medir, con su lectura D1
`[0.90494, 1.60063]` / H1 `[1.02108, 1.39437]`, precio 1.14660):
- escala fija (×4): encoger por ambos lados **conserva el pct** ⇒ D1 34.7% vs H1 33.6% ⇒ H1 no aporta
  información nueva. **Un escalado simétrico nunca comprará rotación.**
- ventana `close ± X`: con la X que alcanza 1.39437 arriba (2478 pips), abajo llega a 0.90180 ⇒ cogería
  0.95364, **no** su 1.02108. No puede reproducir su lectura.
- escala por ATR: ratio ATR D1/H1 ~4.9 vs ratio de sus rangos 1.86. No cuadra.

## 4. Qué se mide (las 4 de §9, en orden de letalidad)

| # | Medición (§9 de S130) | Cómo | Predicción |
|---|----------------------|------|-----------|
| M4 | Qué pools se heredan/sobreviven | censo del set en la última barra + `nPruned` sobre historia | P-P1, P-P2 |
| M1 | Qué fuerza mínima ancla | histograma de `touches` de pools vivos por lado | P-P3 |
| M2 | Qué pasa sin pool a un lado | `nNoPoolUp`/`nNoPoolDown` sobre historia, por TF | P-P4, P-P5 |
| M3 | Si el anidamiento se sostiene | **declarado tautológico** con bound=D1; se mide solo el fallback | — |

**M4 primero.** Si P-P1 sale verde, la regla de pools no puede implementarse tal cual y el trabajo se
mueve a *"qué set de pools debe alimentar el P/D"*, que es una decisión, no una medición.

## 5. Coste (si se implementara — NO en esta sesión)

- Cambiar el `bound` de `f_tfExtremes` a `pdHigh/pdLow` de D1: call-sites **fuera del CORE** ⇒ **sin
  ADR, sin romper el SHA**.
- Herencia D1∪H1 de pools: **sí toca el CORE** (`f_tfExtremes` recibiría el set de D1) ⇒ rompe SHA,
  re-baseline ×3, contrato MQL5 ⇒ **ADR obligatorio**.
- Si P-P3 acierta, `MAX_POOLS=50`/`f_prunePools` es el bloqueante real ⇒ tocar el CORE ⇒ **ADR**.

## 6. SIGUIENTE (S132) — lo que queda en pie después de refutar lo gratis

**El estado:** `pine/` NO se tocó en S131. CORE SHA `752b4083a7db419d` intacto. Todo medido en sombra.
El barrido de `i_poolTol` se hizo con `indicator_set_inputs` sobre la instancia del chart ⇒ el default
del repo sigue en 0.1.

1. **Añadir la amplitud del swing (en ATR) a `SMC_Pool`** — la única propiedad que queda. Toca el CORE
   ⇒ rompe el SHA, re-baseline ×3, contrato MQL5 ⇒ **ADR obligatorio**. Ya NO es corazonada: es lo que
   sobrevive tras refutar toques (§3bis.3) y las tres reglas aritméticas (§3bis.4).
   **Medir primero** (norma S114): si se etiquetan los pools por amplitud de swing en ATR, ¿emergen los
   5 niveles del usuario y NO los 6 intermedios que descarta? Predicción **antes** de tocar el CORE.
2. **El fallback sigue sin resolver** (M2): `nNoPoolDown`=18% medido con el gate roto; hay que
   re-medirlo cuando el gate de anclaje funcione — el número de hoy no vale para decidir.
3. **NO repetir:** cascada de mitades, mapeo nivel→TF (S130), fuerza-por-toques ni barrer `i_poolTol`
   (S131) — los cuatro refutados con medición.
4. **Abierto de antes:** IFVG por banda/lado · gate MB/BPR · `elig` excluye ZS_MITIGATED en Visual ·
   calibrar `LEG_ANCH_TOL_ATR` · deudas S123 #2/#3/#4 · herencia MTF.
