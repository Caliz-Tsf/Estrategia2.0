# reglas-smc-ict.md — Fuente de verdad SMC/ICT
> Estrategia 2.0 · Bot SMC/ICT EURUSD · DOC-01 del WORKPLAN-MAESTRO-V2
> Estado: **EN CONSTRUCCIÓN** — se aprueba sección por sección con el usuario.
> Regla de oro: cada concepto se define con **números, no prosa**. Si no se puede medir, no se puede codificar ni validar.

Este documento es la spec que valida TANTO el Pine Script (Fases 1-2) COMO el MQL5 (Fase 4). `smc-validator-agent` puntúa cada implementación contra estas definiciones. Si una definición cambia aquí, cambia en todo el sistema.

---

## 0. CONVENCIONES GLOBALES

Aplican a todos los conceptos salvo que la sección indique lo contrario.

| Tema | Convención |
|---|---|
| **Timeframes** | Contexto = D1 (`"D"`) · Bias = H1 (`"60"`) · Entrada/chart = M5 (`"5"`). "TF de evaluación" = el TF sobre el que corre la detección. |
| **Vela confirmada** | Todo **evento** (BOS, CHoCH, MSS, sweep, displacement…) se evalúa SOLO al cierre (`barstate.isconfirmed`). Nunca intra-vela. Las **zonas** (OB, FVG…) pueden extenderse en vivo, pero su *creación* se confirma al cierre. `[D-PINE-03 — anti-repaint]` |
| **ATR de referencia** | `ATR(14)` (Wilder) sobre el TF de evaluación. Todo umbral relativo a volatilidad se expresa en **múltiplos de este ATR**, nunca en pips fijos (un umbral en pips se rompe entre regímenes de volatilidad). |
| **Pip / point EURUSD** | 1 pip = `0.0001`. Broker de 5 decimales: 1 pip = 10 points. Spread típico EURUSD ≈ 0.8 pip. |
| **Desigualdades** | Estrictas (`>`, `<`) salvo indicación expresa. Los empates exactos NO forman estructura → se derivan a EQH/EQL (§Liquidez). |
| **Sesiones / horario** | Definidas en **hora local de mercado y convertidas a GMT con DST** (no GMT fijo) `[P-25]`. London open = 08:00 `Europe/London`; NY open = 08:30 (estándar de bonos: 08:30 ET) `America/New_York`. Detalle de Kill Zones en §3. |
| **Lookahead MTF** | `request.security(..., lookahead = barmerge.lookahead_off)` SIEMPRE. |
| **Dirección** | `+1` = alcista/bullish · `-1` = bajista/bearish · `0` = neutral. |

> **Casos de prueba:** cada concepto cierra con ≥3 ocurrencias reales y ≥1 contraejemplo en EURUSD, con fecha-hora GMT. Esos casos se **extraen del gráfico real vía TradingView MCP** (no se inventan); hasta poblarlos quedan marcados `⏳ PENDIENTE-TVMCP` con el procedimiento de extracción.

---

## 1. TIER 1 — ESTRUCTURA DE MERCADO

La estructura es la columna vertebral: define el *bias* y habilita o invalida todo lo demás. Todo nace de un único primitivo: el **swing**.

### 1.1 Swing High / Swing Low `f_detectSwings`

**Concepto.** Extremo local confirmado por simetría temporal (un "fractal"). Es el átomo estructural.

**Definición cuantificada.**
- **Swing High** en la vela de índice `t`: su `high` es **estrictamente mayor** que el `high` de las `swingLen` velas anteriores (`t-1 … t-swingLen`) **y** de las `swingLen` velas posteriores (`t+1 … t+swingLen`). Equivale a `ta.pivothigh(swingLen, swingLen)`.
- **Swing Low** en `t`: simétrico, su `low` estrictamente **menor** a ambos lados.
- **Estructura interna:** idéntica definición pero con `internalLen` (default 3). Detecta swings menores ("internal liquidity") dentro de las piernas del swing mayor.

**Parámetros default.**
| Param | Default | Rango sugerido | Nota |
|---|---|---|---|
| `swingLen` | **5** | 3–10 | Estructura mayor (swing structure). |
| `internalLen` | **3** | 2–5 | Estructura interna. Debe ser `< swingLen` siempre. |

**Confirmación / anti-repaint.**
- Un swing en `t` **no existe** hasta el cierre de la vela `t + swingLen` (hacen falta `swingLen` velas a la derecha para confirmarlo). Latencia inherente = `swingLen` velas. Esto es **deseable**: garantiza cero repaint.
- `precio` del swing = `high`/`low` de la vela `t`. Su `barIdx`/`barTime` = los de la vela `t` (no los de la vela de confirmación).

**Manejo de empates (desempate de *detección*).** Desigualdad estricta a ambos lados. Si dos velas **vecinas** (dentro de la ventana `swingLen`) comparten el `high` idéntico al tick, ninguna forma swing por sí sola → no se estampa swing en ese punto. Es solo para evitar swings duplicados/ambiguos. **No confundir** con Equal Highs (EQH): EQH son dos *swings high ya confirmados y separados en el tiempo* a niveles casi iguales (diferencia `< umbral×ATR`) = liquidez (§Liquidez), no un empate de detección.

**Contraejemplos.**
- Vela con `high` mayor que las 5 previas pero solo 4 posteriores: **aún NO es swing** (falta 1 vela de confirmación). Marcarla antes = repaint.
- En lateral, un `high` *igual* (no mayor) a un vecino: **no es swing** → candidato EQH.

**Casos de prueba.** ⏳ PENDIENTE-TVMCP — *Procedimiento:* en EURUSD H1, `data_get_ohlcv` sobre un rango → localizar 3 velas que cumplan `pivothigh(5,5)`/`pivotlow(5,5)` claros + 1 falso (high mayor solo a un lado). Registrar fecha-hora GMT y precio.

---

### 1.2 Clasificación HH / HL / LH / LL `f_classifySwing`

**Concepto.** Cada swing confirmado se etiqueta comparándolo con el **swing previo del mismo tipo** (high contra high, low contra low). Es lo que convierte una lista de extremos en una *narrativa* de tendencia.

**Definición cuantificada.** Sea `S` el swing recién confirmado y `P` el swing previo del mismo tipo:
- **HH** (Higher High): `S` es swing high y `S.price > P.price`.
- **LH** (Lower High): `S` es swing high y `S.price < P.price`.
- **HL** (Higher Low): `S` es swing low y `S.price > P.price`.
- **LL** (Lower Low): `S` es swing low y `S.price < P.price`.
- Igualdad exacta (`S.price == P.price`): **no reclasifica** → candidato EQH/EQL.

**Lectura de tendencia (base de BOS/CHoCH/MSS).**
- Secuencia alcista sana = `HH` y `HL` alternados (cada techo y cada suelo más altos).
- Secuencia bajista sana = `LH` y `LL` alternados.
- La **ruptura** de la secuencia vigente es lo que define BOS (continuación) y CHoCH (cambio) — §1.3.

**Contraejemplo.** Un swing low más alto que el low previo es `HL` **aunque** el mercado venga bajista — no implica cambio de tendencia por sí solo; el cambio lo confirma el cierre estructural (CHoCH), no la mera clasificación del swing.

**Casos de prueba.** ⏳ PENDIENTE-TVMCP — *Procedimiento:* tomar 4 swings consecutivos confirmados de §1.1 y etiquetar la secuencia (p.ej. LL→LH→HL→HH como giro alcista). 1 contraejemplo: HL aislado en tendencia bajista que NO produjo giro.

---

### Modelo de bias estructural (compartido por BOS y CHoCH)

En cada TF se mantiene una **estructura vigente** definida por dos niveles:
- **Structure High** = último swing high confirmado y NO roto.
- **Structure Low** = último swing low confirmado y NO roto.

Y un **bias** (`+1`/`-1`) según la última ruptura estructural. En tendencia:
- **Alcista** (haciendo HH/HL): el *structure high* es el techo que **extiende** la tendencia; el *structure low* (el último HL) es el suelo que la **protege**.
- **Bajista** (haciendo LH/LL): el *structure low* (último LL) **extiende**; el *structure high* (último LH) **protege**.

La diferencia BOS vs CHoCH es **qué swing se rompe**:
- Romper el nivel que **extiende** la tendencia → **BOS** (continuación).
- Romper el nivel que **protege** la tendencia → **CHoCH** (cambio de carácter).

---

### 1.3 BOS — Break of Structure `f_detectBOS`

**Concepto.** Ruptura **a favor** de la tendencia vigente: el precio cierra más allá del swing que extiende la estructura. Confirma continuación.

**Definición cuantificada.**
- **BOS alcista:** con bias alcista, el `close` de una vela confirmada es **estrictamente mayor** que el `structure high` (último swing high no roto). → se actualiza el structure high; bias sigue `+1`.
- **BOS bajista:** con bias bajista, el `close` confirmado es **estrictamente menor** que el `structure low` (último swing low no roto). → se actualiza el structure low; bias sigue `-1`.
- **Base de ruptura = `close`**, no la mecha (`breakBasis = close`, default). Una mecha que pincha el nivel pero cierra de vuelta **no es BOS** (es sweep/grab, §Liquidez).
- **Interno vs swing:** se evalúa en ambas escalas. *BOS swing* (sobre swings `swingLen`) = mayor. *BOS interno* (sobre swings `internalLen`) = menor (suele ser el gatillo fino). Se registran por separado (confluencias #2 BOS H1 y #4 BOS chart).

**Parámetros default.**
| Param | Default | Nota |
|---|---|---|
| `breakBasis` | `close` | Alternativa `wick` (más sensible, más ruido). |
| escala | swing + interno | Ambas se trackean. |

**Confirmación / anti-repaint.** El swing roto debe estar **ya confirmado** (tiene sus `swingLen` velas a la derecha). La vela de ruptura debe estar **cerrada**. Sin esto, repinta.

**Contraejemplo.** En tendencia alcista, una vela cuya **mecha** supera el structure high pero **cierra por debajo**: NO es BOS → es un *liquidity grab/sweep* del techo. Marcarlo como BOS es el error clásico que invalida un backtest.

**Casos de prueba.** ⏳ PENDIENTE-TVMCP — *Procedimiento:* EURUSD H1, localizar 3 cierres que superen un swing high/low previo no roto en dirección del bias + 1 contraejemplo (mecha que barre sin cierre).

---

### 1.4 CHoCH — Change of Character `f_detectCHoCH`

**Concepto.** Primera ruptura **en contra** de la tendencia vigente: el precio cierra más allá del swing que **protegía** la estructura. Es el **primer aviso** de posible giro (todavía no es giro confirmado — eso es MSS, §1.5).

**Definición cuantificada.**
- **CHoCH alcista:** con bias **bajista**, el `close` confirmado es **estrictamente mayor** que el `structure high` que protegía (último LH). → bias candidato pasa a `+1`.
- **CHoCH bajista:** con bias **alcista**, el `close` confirmado es **estrictamente menor** que el `structure low` que protegía (último HL). → bias candidato pasa a `-1`.
- Misma mecánica de cierre y misma regla anti-repaint que BOS; lo que cambia es **cuál** swing se rompe (el protector, no el extensor).
- **Interno vs swing:** *CHoCH interno* (sobre `internalLen`) = cambio menor, suele ser el gatillo de entrada (IDM/precisión); *CHoCH swing* = cambio mayor de bias. **No voltear el bias mayor con una ruptura interna.**

**Efecto.** Un CHoCH **invierte el bias de trabajo** del TF. La siguiente ruptura en la nueva dirección ya sería un BOS (que confirma la nueva tendencia).

**Contraejemplo.** En tendencia alcista, cierre por debajo de un low **interno** menor pero **no** por debajo del último HL swing: es CHoCH **interno** como mucho — el bias swing sigue alcista. Tratarlo como giro mayor es sobre-reaccionar al ruido.

**Casos de prueba.** ⏳ PENDIENTE-TVMCP — *Procedimiento:* localizar 3 giros donde el primer cierre contra-tendencia rompe el swing protector + 1 contraejemplo (ruptura interna que no cambió el bias swing).

---

### 1.5 MSS — Market Structure Shift `f_detectMSS`

**Concepto.** El **giro confirmado con fuerza**: un CHoCH de nivel swing cuya ruptura ocurre **con displacement** (vela impulsiva institucional). Mientras el CHoCH es el *primer aviso*, el MSS dice "el giro vino con convicción". Confluencia #5 del scoring.

**Definición cuantificada.**
- **MSS alcista:** se cumple un **CHoCH alcista de nivel swing** (§1.4: con bias bajista, `close` confirmado > último LH protector) **Y** la vela que produce ese cierre de ruptura es un **displacement**: `rango ≥ dispFactor×ATR14` (default 1.5) **y** `cuerpo ≥ bodyPct×rango` (default 70%). → giro a `+1` de alta convicción.
- **MSS bajista:** simétrico (CHoCH bajista swing + vela de ruptura displacement). → giro a `-1`.
- **Solo escala swing.** Un MSS es por definición un cambio mayor; la estructura interna no genera MSS (genera CHoCH interno).
- **Relación con CHoCH:** todo MSS es un CHoCH, pero no todo CHoCH es MSS. CHoCH sin displacement = aviso temprano (confluencia CHoCH). CHoCH swing **con** displacement = MSS (confluencia adicional, mayor peso esperado).

**Parámetros default.** Heredados de displacement.
| Param | Default | Nota |
|---|---|---|
| `dispFactor` | **1.5** | múltiplo de ATR14 para el rango de la vela de ruptura. |
| `bodyPct` | **0.70** | cuerpo mínimo como fracción del rango. |
| escala | swing | MSS nunca es interno. |

**Confirmación / anti-repaint.** Swing protector confirmado + vela de ruptura cerrada. El cálculo de ATR14 usa solo velas cerradas.

**Contraejemplo.** Un CHoCH swing cuya vela de ruptura es de **rango normal** (`< 1.5×ATR`): es un CHoCH "normal", **NO** un MSS. El giro sin fuerza es más propenso a ser una desviación (deviation) que se revierte — exactamente el tipo de señal que el peso extra del MSS debe evitar premiar.

**Casos de prueba.** ⏳ PENDIENTE-TVMCP — *Procedimiento:* localizar 3 giros donde el cierre que rompe el swing protector lo hace con vela ≥1.5×ATR y cuerpo ≥70% + 1 contraejemplo (CHoCH swing con vela débil que no debe contar como MSS).

---

### 1.6 Impulso / Corrección `f_isImpulsive`

**Concepto.** Distinguir las piernas **impulsivas** (motor de la tendencia, generan BOS y dejan OB/FVG) de las **correctivas** (pullbacks donde se busca la entrada). Dos confluencias del scoring (#7 impulso previo, #8 corrección en curso).

**Definición cuantificada.**
- **Pierna impulsiva:** cumple ≥1 de:
  - (a) produce ≥2 BOS consecutivos en la misma dirección **sin** CHoCH intermedio, **o**
  - (b) contiene ≥1 vela de **displacement** (rango ≥ `1.5×ATR14` y cuerpo ≥ 70% del rango — def. completa en Tier 2 §Displacement).
- **Pierna correctiva (corrección en curso):** desde el último swing, **no** hay BOS nuevo **y** el precio retrocede con velas **solapadas** (el rango de cada vela solapa el de la previa — movimiento "escalonado", no impulsivo), típicamente hacia un OB/FVG o zona de descuento/premium.
- **#7 Impulso previo (confluencia):** la pierna que llevó el precio a la zona de interés actual fue impulsiva (a o b). Direccional.
- **#8 Corrección en curso (confluencia):** el precio está ahora mismo en pierna correctiva hacia la zona de entrada. Direccional (corrección dentro de tendencia alcista → suma a long).

**Contraejemplo.** Un único BOS aislado **no** es "impulso" por sí solo si la vela que lo produjo fue de rango normal (< 1.5×ATR) — podría ser una ruptura débil propensa a fallar. El impulso exige fuerza (displacement) o continuidad (2+ BOS).

**Casos de prueba.** ⏳ PENDIENTE-TVMCP.

---

> **Tier 1 restante tras decidir MSS:** ninguno — Estructura quedaría completa (1.1 swings, 1.2 clasificación, 1.3 BOS, 1.4 CHoCH, 1.5 MSS, 1.6 impulso/corrección). Siguiente Tier a definir: **Tier 2 — Zonas** (OB, FVG, Premium/Discount, EQH/EQL) o **Liquidez** (pools, sweeps, Kill Zones), según prioridad.
