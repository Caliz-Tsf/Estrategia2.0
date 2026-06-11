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
| **ATR de referencia** | Default = `ATR(14)` (Wilder) sobre el TF de evaluación, para umbrales de **corto plazo** (displacement, FVG, EQH). Conceptos que necesitan un baseline **largo** declaran su propio período: el filtro de Order Blocks usa `ATR(200)` o *Cumulative Mean Range* (`ta.cum(ta.tr)/bar_index`), heredado de LuxAlgo. **Regla:** todo umbral de volatilidad se expresa en múltiplos de un ATR, nunca en pips fijos (un umbral en pips se rompe entre regímenes de volatilidad). Cada concepto indica qué ATR usa. |
| **Pip / point EURUSD** | 1 pip = `0.0001`. Broker de 5 decimales: 1 pip = 10 points. Spread típico EURUSD ≈ 0.8 pip. |
| **Desigualdades** | Estrictas (`>`, `<`) salvo indicación expresa. Los empates exactos NO forman estructura → se derivan a EQH/EQL (§Liquidez). |
| **Sesiones / horario** | Definidas en **hora local de mercado y convertidas a GMT con DST** (no GMT fijo) `[P-25]`. London open = 08:00 `Europe/London`; NY open = 08:30 (estándar de bonos: 08:30 ET) `America/New_York`. **Nota: Kill Zone ≠ hora de apertura** — las ventanas KZ (§3.4) arrancan a propósito ANTES del open (convención ICT: London KZ 07:00–10:00 hora de Londres = 02:00–05:00 ET), porque la actividad institucional se concentra alrededor de la apertura, no después de ella. No es contradicción. |
| **Lookahead MTF** | `request.security(..., lookahead = barmerge.lookahead_off)` SIEMPRE. |
| **Dirección** | `+1` = alcista/bullish · `-1` = bajista/bearish · `0` = neutral. |
| **Símbolo-agnóstico** `[ADR-001]` | El bot opera en **cualquier símbolo**, gobernado por confluencias y datos. NADA se hardcodea a EURUSD. Todo umbral va relativo a ATR (no pips fijos). Lo inherentemente por-símbolo va como **input/perfil**, no como constante: pip/point, spread típico, `sessionProfile` (§3.4), y **los pesos del scoring** (perfil de pesos por símbolo — los de EURUSD no transfieren 1:1). Validación: primero EURUSD (gate Fase 3); cada símbolo nuevo repite validación abreviada (Fase 5). Sin filtros de reloj que bloqueen; la calidad la gobiernan score + filtro de spread. |

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

---

## 2. TIER 2 — ZONAS

Las zonas son las áreas donde se busca la **entrada**: donde el precio institucional dejó órdenes (OB), ineficiencias por rellenar (FVG), o niveles de valor (Premium/Discount). Todas portan algoritmos del LuxAlgo base (§9 PINE-PLAN).

### 2.1 Order Block (OB) `f_detectOB` + `f_updateZoneMitigation`

**Concepto.** La **última vela contraria antes del impulso** que rompe estructura (BOS/CHoCH). Representa el origen de las órdenes institucionales que movieron el precio. Un OB alcista nace de la última vela bajista antes de un tramo alcista que rompe estructura.

**Definición cuantificada.**
- **OB alcista:** la última vela **bajista** (`close < open`) dentro de la pierna que precede a un **BOS/CHoCH alcista**, siempre que esa pierna contenga al menos una **vela de alta volatilidad** (`(high-low) ≥ highVolFactor × volMeasure`, default 2× — filtra impulsos débiles). Zona = `[low, high]` de esa vela (default; alternativa: cuerpo `[min(o,c), max(o,c)]`).
- **OB bajista:** simétrico — última vela **alcista** antes de un BOS/CHoCH bajista.
- **Escala interna vs swing:** el OB se ancla a la ruptura que lo origina; OB interno (sobre estructura `internalLen`) y OB swing (sobre `swingLen`) se trackean por separado (confluencias #17 OB H1, #19 OB chart, #21 OB D1).

**Mitigación e invalidación** (`f_updateZoneMitigation`, máquina de estados del UDT `SMC_Zone.state`):
- `0 activa`: el precio no ha vuelto a la zona.
- `1 parcial`: el precio entró en la zona pero no la cruzó del todo. `mitigatedPct` = profundidad de penetración / altura de la zona.
- `2 mitigada`: el precio alcanzó el borde lejano (la zona "hizo su trabajo" como entrada).
- `3 invalidada`: una vela **cierra** atravesando el borde protector (OB alcista: `close < OB.low`) → la tesis falló; candidato a **Breaker** (§Tier 2 breaker).
- **Fuente de mitigación** (`obMitigation`): `HIGHLOW` (default, basta que la mecha toque) o `CLOSE` (exige cierre dentro). Igual que LuxAlgo.

**Parámetros default.**
| Param | Default | Nota |
|---|---|---|
| `obFilter` | `ATR` → `ATR(200)` | alternativa `Cumulative Mean Range`. |
| `highVolFactor` | **2.0** | rango de vela ≥ 2× volMeasure para contar como impulso. |
| `obMitigation` | `HIGHLOW` | vs `CLOSE`. |
| `obBounds` | `high/low` | ✓ decidido (vs `body`): vela completa, SL detrás de la mecha. Entrada fina refinable al CE. |

**Confirmación / anti-repaint.** El OB solo se crea cuando el BOS/CHoCH que lo origina está **confirmado al cierre**. La zona puede extenderse a la derecha en vivo, pero su origen no repinta.

**Contraejemplo.** Una vela bajista antes de una subida **débil** (sin ninguna vela ≥2×volMeasure y sin romper estructura): **NO** es OB — es ruido. El filtro de volatilidad + el requisito de ruptura estructural es lo que separa un OB real de "cualquier vela contraria".

**Casos de prueba.** ⏳ PENDIENTE-TVMCP.

---

### 2.2 Fair Value Gap (FVG) + CE `f_detectFVG`

**Concepto.** Una **ineficiencia** de precio: un hueco de 3 velas donde el mercado se movió tan rápido que dejó un rango sin negociar. El precio tiende a volver a "rellenarlo". El nivel medio (CE, *Consequent Encroachment*, 50%) es el punto de equilibrio clave del gap.

**Definición cuantificada** (evaluada en la vela central, al cierre de la 3.ª):
- **FVG alcista:** `low[0] > high[2]` → gap `= [high[2], low[0]]` (hueco entre el techo de hace 2 velas y el suelo de la actual).
- **FVG bajista:** `high[0] < low[2]` → gap `= [high[0], low[2]]`.
- **Filtro de tamaño:** altura del gap `≥ fvgThreshold`. Dos modos:
  - `fixed` (default): `≥ 0.25 × ATR(14)`.
  - `auto` (LuxAlgo): umbral derivado del promedio acumulado del tamaño de gaps recientes.
- **CE (50%):** `(top + bottom) / 2`. Nivel de mitigación/entrada principal (confluencia #26 *FVG-CE tocado*).

**Mitigación.** Igual máquina de estados que el OB: `mitigatedPct` por penetración; `2 mitigada` cuando el precio rellena hasta el borde lejano; el toque del **CE** es el evento de entrada de referencia.

**Parámetros default.**
| Param | Default | Nota |
|---|---|---|
| `fvgThresholdMode` | `fixed` | ✓ decidido (vs `auto`): umbral estable y optimizable, respeta disciplina IS/OOS. |
| `fvgThreshold` | **0.25** | × ATR(14), solo en modo `fixed`. |
| `ce` | **0.5** | nivel de equilibrio del gap. |

**Confirmación / anti-repaint.** El FVG se confirma al **cierre de la 3.ª vela** (la que completa el patrón). No se marca antes.

**Contraejemplo.** Un gap de `low[0] > high[2]` pero de tamaño `< 0.25×ATR`: ineficiencia trivial → **se descarta**. Marcar micro-FVGs llena el gráfico de ruido y degrada el scoring.

**Casos de prueba.** ⏳ PENDIENTE-TVMCP.

---

### 2.3 Premium / Discount / Equilibrium `f_premiumDiscount`

**Concepto.** El *dealing range* (rango de negociación entre el último **strong high** y **strong low**) dividido en zonas de valor. Vender en **premium** (caro), comprar en **discount** (barato), evitar el **equilibrium** (zona de chop sin ventaja).

**Definición cuantificada.** Sea el rango `[L, H]` entre el strong low `L` y strong high `H` vigentes (los swings que delimitan el rango operativo actual):
- `eq = (H + L) / 2` (nivel 50%).
- **Discount:** precio `< eq` (mitad inferior) → favorece **long**.
- **Premium:** precio `> eq` (mitad superior) → favorece **short**.
- **Equilibrium (banda):** precio dentro de `[45%, 55%]` del rango → zona neutral. Confluencia #31: si el precio está en equilibrium, **resta** 50% del peso (no hay ventaja de localización).

**Parámetros default.**
| Param | Default | Nota |
|---|---|---|
| `eqBand` | **45–55%** | ancho de la banda de equilibrium. |
| rango | strong high / strong low vigentes | se actualiza con la estructura. |

**Contraejemplo.** Comprar en **premium** (precio en el 80% del rango) porque "hay un OB alcista" es operar contra la localización — el OB en premium tiene mucha menor probabilidad. Premium/Discount es el filtro que evita entradas caras.

**Casos de prueba.** ⏳ PENDIENTE-TVMCP.

---

### 2.4 Equal Highs / Equal Lows (EQH/EQL) `f_detectEQHL`

**Concepto.** Dos o más swings al **mismo nivel** = doble (o triple) techo/suelo. Marcan **liquidez** acumulada (stops) que el precio tiende a barrer. (Es el Caso B de §1.1.)

**Definición cuantificada.**
- **EQH:** dos swing highs confirmados con `|high₁ − high₂| ≤ eqThreshold × ATR(14)`. Análogo EQL con lows.
- `eqThreshold` default **0.1** (sensibilidad de LuxAlgo, rango 0–0.5). Más bajo = menos EQH pero más pertinentes.
- **Confirmación:** swings detectados con `eqlLength = 3` barras a cada lado (igual que LuxAlgo).
- Un EQH/EQL confirmado alimenta los **pools de liquidez** (§Liquidez) y es objetivo de **sweep**.

**Parámetros default.**
| Param | Default | Nota |
|---|---|---|
| `eqThreshold` | **0.1** | × ATR(14). Tolerancia de "igualdad". |
| `eqlLength` | **3** | barras de confirmación del swing. |

**Contraejemplo.** Dos highs separados por `0.6×ATR`: **no** son EQH (demasiado distintos) — son simplemente dos swings, uno LH o HH del otro. El umbral evita llamar "equal" a niveles que no lo son.

**Casos de prueba.** ⏳ PENDIENTE-TVMCP.

---

### 2.5 OTE / Golden Pocket `f_detectOTE`

**Concepto.** Tras un impulso confirmado, la zona de **retroceso fib óptima** para entrar a favor del impulso. OTE (*Optimal Trade Entry*) es la zona "premium" del retroceso; el Golden Pocket es el corazón.

**Definición cuantificada.** Sobre la última pierna impulsiva que produjo un BOS, fib con `0` en el origen de la pierna y `1` en el extremo:
- **Golden Pocket (GP):** retroceso en `[50%, 61.8%]`. Confluencia #28.
- **OTE:** retroceso en `[61.8%, 79%]`. Confluencia #27. (La zona más profunda = mejor precio, mayor R:R.)
- **Dirección:** impulso alcista (low→high) → el retroceso a la baja hacia 61.8–79% es zona de **long**. Simétrico para short.

**Parámetros default.**
| Param | Default | Nota |
|---|---|---|
| `gpRange` | 0.50–0.618 | Golden Pocket. |
| `oteRange` | 0.618–0.79 | OTE. |
| pierna | último impulso que produjo BOS | se redibuja con cada nuevo impulso. |

**Contraejemplo.** Medir fib sobre una pierna **correctiva** (no impulsiva, sin BOS): el OTE resultante no tiene significado institucional. OTE/GP solo válidos sobre impulso confirmado.

**Casos de prueba.** ⏳ PENDIENTE-TVMCP.

---

### 2.6 Breaker `f_detectBreaker`

**Concepto.** Un OB que **falló** (fue invalidado) cambia de polaridad y pasa a actuar en sentido contrario. Un OB alcista roto a la baja se convierte en resistencia (breaker bajista) en el retest.

**Definición cuantificada.** Cuando un OB pasa a `state = 3 invalidada` (§2.1: una vela cierra atravesando su borde protector) → se crea una `SMC_Zone` KIND_BREAKER en las mismas coordenadas con `dir` **invertido**. En el **retest** desde el otro lado, opera como zona en la nueva dirección. Hereda la máquina de mitigación del OB.

**Parámetros default.** Heredados de OB (§2.1). Confluencia #22.

**Contraejemplo.** Un OB simplemente **mitigado** (`state 2`, el precio lo testeó y respetó) **no** es breaker — sigue siendo OB válido en su dirección original. El breaker requiere **invalidación** (cierre a través), no un mero toque.

**Casos de prueba.** ⏳ PENDIENTE-TVMCP.

---

### 2.7 Rejection `f_detectRejection`

**Concepto.** Una vela de **rechazo** (mecha larga) en un nivel clave: el precio intentó penetrar y fue devuelto con fuerza. Señal de defensa de la zona.

**Definición cuantificada.**
- **Rejection alcista:** vela con **mecha inferior ≥ `rejWickFactor × cuerpo`** (default 2×) cuyo low toca una zona/nivel clave (OB, FVG, pool, EQH/EQL, borde de premium/discount, EMA) y cierra en la mitad superior de su rango.
- **Rejection bajista:** simétrico con **mecha superior**.
- `cuerpo = |close − open|`; `mecha inferior = min(open,close) − low`; `mecha superior = high − max(open,close)`.

**Parámetros default.**
| Param | Default | Nota |
|---|---|---|
| `rejWickFactor` | **2.0** | mecha ≥ 2× cuerpo. |
| nivel clave | OB/FVG/pool/EQHL/PD/EMA | la mecha debe tocar uno de estos. |

**Contraejemplo.** Una vela con mecha larga **en medio de la nada** (sin tocar ningún nivel clave): es ruido, **no** rejection operable. El ancla a un nivel clave es lo que la hace significativa. Confluencia #23.

**Casos de prueba.** ⏳ PENDIENTE-TVMCP.

---

### 2.8 Flip y Mitigation Block `f_detectFlip`

**Concepto.** Dos refinamientos de cómo un nivel cambia de rol:
- **Flip:** un nivel roto con **cierre limpio** y luego **retesteado desde el otro lado** → soporte que pasa a resistencia o viceversa (KIND_FLIP, confluencia #25).
- **Mitigation block:** zona de la última vela contraria antes de un movimiento que mitiga un desequilibrio previo **sin** haber barrido liquidez (a diferencia del breaker, que sí invalida tras barrido). Confluencia #24.

**Definición cuantificada.**
- **Flip:** nivel `N` (swing/OB/EQHL) roto por `close` (limpio, no mecha); en una visita posterior el precio lo testea desde el lado opuesto y respeta (cierre que no lo vuelve a cruzar). Marca el cambio de rol.
- **Mitigation block:** última vela contraria antes de un impulso que rompe estructura interna **pero** sin sweep previo de un pool (si hubo sweep → es contexto de breaker/OB, no mitigation block). Zona = high/low de esa vela.

**Parámetros default.** Heredan de OB/estructura. Distinción operativa: `breaker` = falló tras barrido; `flip` = cambio de rol por retest; `mitigation block` = relleno de desequilibrio sin barrido.

**Contraejemplo.** Un nivel roto solo por **mecha** (sin cierre limpio) que luego se retestea: no es flip — el cierre que define el flip nunca ocurrió.

**Casos de prueba.** ⏳ PENDIENTE-TVMCP.

---

---

## 3. LIQUIDEZ

El subsistema más grande y el más distintivo del SMC/ICT: el mercado se mueve **hacia la liquidez** (los stops acumulados) y desde las **ineficiencias**. Toda la lógica de entrada gira en torno a *dónde está la liquidez* y *cuándo se barre*.

### 3.1 Pools de liquidez — BSL / SSL `f_buildPools`

**Concepto.** Zonas donde se acumulan órdenes stop. **BSL** (Buyside Liquidity) = stops de compra **por encima** de los highs (imán al alza). **SSL** (Sellside Liquidity) = stops de venta **por debajo** de los lows (imán a la baja).

**Definición cuantificada.**
- Un **pool** se forma clusterizando EQH/EQL (§2.4) + swings **no barridos** cuyos niveles están dentro de `poolTol × ATR(14)` entre sí (default `poolTol = 0.1`).
- `SMC_Pool.level` = promedio de los extremos clusterizados · `dir` = `+1` BSL (sobre highs) / `-1` SSL (bajo lows) · `touches` = nº de extremos que lo confirman (≥2) · `swept` = false hasta ser barrido.
- Cuantos más `touches`, más relevante el pool (más liquidez acumulada).

**Parámetros default.**
| Param | Default | Nota |
|---|---|---|
| `poolTol` | **0.1** | × ATR(14). Tolerancia de clustering. |
| `minTouches` | **2** | toques mínimos para formar pool. |

**Contraejemplo.** Un único swing high aislado **ya barrido** no es un pool activo — su liquidez ya se tomó. Solo los niveles **no barridos** son imanes.

**Casos de prueba.** ⏳ PENDIENTE-TVMCP.

---

### 3.2 Sweep (barrido) `f_detectSweep`

**Concepto.** El precio **supera** un pool intra-vela (toma la liquidez) pero **cierra de vuelta** dentro del rango: la liquidez fue barrida sin continuación → suele preceder el movimiento contrario. Es la señal de "trampa" más importante del SMC.

**Definición cuantificada** (al cierre):
- **Sweep de SSL (alcista):** el `low` de la vela perfora por debajo de `pool.level` (SSL) pero el `close` queda **por encima** del nivel → `pool.swept := true`; sesgo alcista. Confluencia #10 (sweep contrario).
- **Sweep de BSL (bajista):** el `high` perfora por encima de un pool BSL pero el `close` queda **por debajo**.
- Requiere un **pool confirmado** (§3.1) como objetivo.

**Contraejemplo.** Una vela que perfora el pool **y cierra más allá** (no vuelve): eso **no** es sweep → es BOS/false breakout (§3.7). El sweep exige el cierre de **retorno**.

**Casos de prueba.** ⏳ PENDIENTE-TVMCP.

---

### 3.3 Grab `f_detectGrab`

**Concepto.** Subconjunto del sweep: una **mecha** toma la liquidez de un nivel **sin** exigir un pool confirmado (un solo swing). Más fino y frecuente que el sweep.

**Definición cuantificada.** La mecha de la vela supera un swing high/low no barrido y el `close` queda de vuelta dentro, **sin** requerir cluster/pool (≥2 touches). Si el nivel barrido ES un pool confirmado → cuenta como **sweep** (mayor peso); si es un swing aislado → **grab**. Confluencia #11.

**Contraejemplo.** Una mecha larga que **no** alcanza ningún swing/nivel previo: no hay liquidez que tomar → no es grab.

**Casos de prueba.** ⏳ PENDIENTE-TVMCP.

---

### 3.4 Kill Zones `f_killZone` `[ADR-001]`

**Concepto.** Ventanas horarias de **alta actividad institucional**. En el diseño multi-símbolo NO son un filtro duro (un bloqueo por reloj sabotea símbolos con otras sesiones o sin sesiones —cripto/índices 24h—). Son una **confluencia ponderada** opcional + un **perfil configurable por símbolo**. El guardián universal de calidad de liquidez es el **filtro de spread** (§6 Strategy), no el reloj.

**Definición cuantificada.**
- `f_killZone(time, sessionProfile)` devuelve **qué sesión está activa** (o ninguna) + si estamos en la **primera mitad** de la ventana (necesario para Judas, §3.5).
- Ventanas definidas en **hora local de mercado con DST automático** (no GMT fijo) `[P-25]`, vía `time(timeframe.period, session, timezone)` de Pine.
- **Perfiles de sesión** (input `sessionProfile`, configurable por símbolo):
  | Perfil | Sesiones | Para |
  |---|---|---|
  | `FX-London-NY` (default) | London `07:00–10:00` `Europe/London` + NY AM `08:00–11:00` `America/New_York` | EURUSD, GBPUSD, XAUUSD |
  | `FX-Asia` | + Tokyo `09:00–11:00` `Asia/Tokyo` | USDJPY, AUDUSD, NZDUSD |
  | `None` | sin sesiones | cripto / índices 24h |
- **Uso en scoring:** la sesión activa suma su peso a la confluencia #34 (peso calibrado **por símbolo** en Fase 3 / Fase 5). NO bloquea la entrada. Si `sessionProfile = None`, la confluencia #34 simplemente no aporta.

> **Por qué local+DST:** "London 08:00–10:00 GMT" solo es correcto en invierno; en verano (BST) la sesión real ocurre a las 07:00 GMT. Hora local → TradingView ajusta el DST solo y la ventana sigue pegada a la apertura real todo el año.

**Contraejemplo.** Una señal a las 03:00 GMT en EURUSD ya **no se bloquea** por la hora; se filtra (si procede) por **spread alto** (baja liquidez real) o por **no alcanzar el umbral de score**. El reloj informa, no veta.

**Casos de prueba.** ⏳ PENDIENTE-TVMCP.

---

### 3.5 Judas Swing `f_detectJudas`

**Concepto.** El **movimiento falso** al inicio de una sesión: un barrido engañoso en la primera mitad de una KZ que atrapa traders, seguido del movimiento real en dirección contraria. El "beso de Judas".

**Definición cuantificada.** Un **sweep/grab** (§3.2/3.3) en la **primera mitad** de una Kill Zone, seguido de un **displacement** (§4) en dirección **contraria** dentro de `≤ judasBars` velas (default **6** en M5). `dir` del Judas = dirección del displacement (la real). Confluencia #13.

**Parámetros default.**
| Param | Default | Nota |
|---|---|---|
| `judasBars` | **6** | velas M5 máximo entre sweep y displacement contrario. |
| ventana | primera mitad de la KZ | requiere §3.4. |

**Contraejemplo.** Un sweep a mitad de sesión sin displacement contrario posterior: es solo un sweep, **no** Judas. El Judas exige la **reversión con fuerza** que confirma la trampa.

**Casos de prueba.** ⏳ PENDIENTE-TVMCP.

---

### 3.6 IDM — Inducement `f_detectIDM`

**Concepto.** La **liquidez señuelo**: un pullback menor cuya liquidez (interna) es barrida **antes** de que el precio alcance el OB/FVG objetivo. Es la liquidez que "induce" entradas tempranas que el smart money toma antes del movimiento real.

**Definición cuantificada.** En una tendencia alcista hacia un OB/FVG objetivo, el IDM es el **swing low interno** (`internalLen`) más cercano por debajo del precio cuya liquidez se barre **antes** de que el precio toque el objetivo. Detección: pool/grab interno tomado entre el origen del impulso y la zona objetivo. Confluencia #33 (IDM barrido). Simétrico bajista.

**Contraejemplo.** Si el precio alcanza el OB **sin** haber barrido ningún inducement intermedio, la entrada es de menor calidad (no hubo limpieza de liquidez señuelo) — el IDM barrido es lo que valida que el camino está "limpio".

**Casos de prueba.** ⏳ PENDIENTE-TVMCP.

---

### 3.7 False Breakout, Spring y Raid `f_detectFalseBreakout`

**Concepto.** Variantes de ruptura fallida / barrido en extremos de rango.
- **False Breakout:** cierre **más allá** de un nivel + reversión que cierra de vuelta dentro en `≤ fbBars` velas (default 2). Confluencia #14.
- **Spring (Wyckoff):** sweep de **SSL bajo el mínimo de un rango** lateral con reversión rápida al alza. Confluencia #15 (subtipo de sweep en extremo de rango, dir alcista).
- **Raid:** barrido **agresivo** de un pool de alta liquidez (stop raid). Confluencia #16 (sweep de pool con `touches` alto).

**Definición cuantificada.**
- False breakout: `close` cruza el nivel `N` (a diferencia del sweep, que es solo mecha) y dentro de `≤ fbBars` velas otra vela **cierra** de vuelta al lado original. `fbBars` default **2**.
- Spring = sweep (§3.2) cuyo pool SSL coincide con el mínimo de un rango de consolidación → `dir +1`.
- Raid = sweep cuyo pool tiene `touches ≥ raidTouches` (default 3) → mayor peso.

**Contraejemplo.** Un cierre más allá del nivel que **no** revierte en ≤2 velas: es un breakout **real** (BOS), no falso. La reversión rápida es lo que lo define.

**Casos de prueba.** ⏳ PENDIENTE-TVMCP.

---

---

## 4. CONTEXTO / ICT / EMAs

Conceptos que dan **contexto direccional** y confirman (o no) la confluencia: la fuerza del movimiento (displacement), los niveles de apertura (session opens) y la tendencia media (EMAs). Todos símbolo-agnósticos.

### 4.1 Displacement `f_detectDisplacement`

**Concepto.** El movimiento **impulsivo** que delata intención institucional: una expansión brusca tras un periodo de calma. Es lo que crea FVGs y OBs, y el calificador de fuerza para MSS (§1.5) y Judas (§3.5).

**Definición cuantificada.** Una vela (o tramo de 1–3 velas) es displacement si:
- `rango ≥ dispFactor × ATR(14)` (default `dispFactor = 1.5`), **y**
- `cuerpo ≥ bodyPct × rango` (default `bodyPct = 0.70`), **y**
- (opcional, `requireContraction = true`) ocurre tras **≥3 velas** de `rango < ATR(14)` (expansión tras compresión).
- `dir` = signo de la vela (`close > open` → `+1`). Confluencia #32.

**Parámetros default.**
| Param | Default | Nota |
|---|---|---|
| `dispFactor` | **1.5** | × ATR(14) para el rango. |
| `bodyPct` | **0.70** | cuerpo mínimo / rango. |
| `requireContraction` | **true** | exige 3 velas previas de baja volatilidad. Relajable. |

**Contraejemplo.** Una vela de rango grande pero con **cuerpo pequeño** (mecha dominante, `cuerpo < 70%`): NO es displacement → es indecisión/rechazo. La fuerza está en el cuerpo, no en el rango total.

**Casos de prueba.** ⏳ PENDIENTE-TVMCP.

---

### 4.2 Session Opens `f_sessionOpens`

**Concepto.** Los niveles de **apertura** (diaria/semanal/mensual) actúan como referencia institucional de valor: el precio por encima/debajo de la apertura semanal marca sesgo, y la apertura suele actuar como soporte/resistencia.

**Definición cuantificada.**
- Niveles: apertura **diaria** (frontera de día del broker — para 24h = medianoche del broker), **semanal** y **mensual**. Trazados como líneas horizontales.
- **Confluencia #36 (session open cercano):** el precio está dentro de `openProx × ATR(14)` de un nivel de apertura → ese nivel es relevante como S/R inmediato. Direccional según de qué lado del nivel esté el precio.
- Símbolo-agnóstico: cualquier instrumento tiene aperturas; en 24h la diaria usa la frontera de día del broker.

**Parámetros default.**
| Param | Default | Nota |
|---|---|---|
| `openProx` | **0.5** | × ATR(14): distancia para contar como "cercano". |
| niveles | diaria + semanal + mensual | toggles individuales. |

**Contraejemplo.** El precio a 3×ATR de la apertura semanal: el nivel existe pero **no es confluencia activa** (demasiado lejos para influir la entrada ahora).

**Casos de prueba.** ⏳ PENDIENTE-TVMCP.

---

### 4.3 EMAs — estado, cruces, rebotes, alineación `f_emaState`

**Concepto.** Las medias móviles exponenciales 20/50/200 dan **confirmación de tendencia**. Son la única familia no-puramente-SMC: confirman, no lideran → peso base bajo (se calibra en Fase 3). Colapsadas de 15 confluencias originales a **6** `[FIX P-05]` para evitar doble conteo de pares mutuamente excluyentes.

**Definición cuantificada** (6 confluencias direccionales, #37–#42):
- **#37 vs EMA200:** `close > EMA200` → +1 / `close < EMA200` → −1. **Una sola** confluencia direccional (no dos sumando al mismo score).
- **#38 vs EMA50:** ídem con EMA50.
- **#39 vs EMA20:** ídem con EMA20.
- **#40 cruce reciente alineado:** un cruce de cualquier par (20×50, 50×200, 20×200) ocurrido en `≤ crossBars` velas (default 20) cuya dirección coincide con el sesgo. +peso al lado del cruce.
- **#41 rebote en EMA alineado:** el precio toca una EMA y cierra de vuelta con mecha (`mecha ≥ rejWickFactor × cuerpo`, §2.7) en la dirección de la tendencia.
- **#42 3 EMAs alineadas:** `EMA20 > EMA50 > EMA200` (→ +1 fuerte) o `EMA20 < EMA50 < EMA200` (→ −1). Tendencia limpia.

**Parámetros default.**
| Param | Default | Nota |
|---|---|---|
| `emaFast/Mid/Slow` | **20 / 50 / 200** | periodos estándar. |
| `crossBars` | **20** | antigüedad máxima de un cruce para contar. |
| `rejWickFactor` | 2.0 | reusa el de Rejection (§2.7) para el rebote. |

**Contraejemplo `[FIX P-05]`.** Contar "precio sobre EMA200" Y "precio bajo EMA200" como confluencias separadas que suman al mismo score: una de las dos está SIEMPRE activa → +peso garantizado a cualquier señal. Por eso #37–#39 son **direccionales únicas** (suman a long O short, nunca inflan el total).

**Casos de prueba.** ⏳ PENDIENTE-TVMCP.

---

> **DEFINICIONES DE reglas-smc-ict.md COMPLETAS** — Tier 1 Estructura (§1), Tier 2 Zonas (§2), Liquidez (§3), Contexto/ICT/EMAs (§4). Cubren los 42 confluencias canónicas (§4.8 del workplan) y todas las funciones de PINE-PLAN §3.
>
> **Falta para cerrar DOC-01 (gate VER-05):**
> 1. **Pasada TradingView MCP:** poblar todos los casos ⏳PENDIENTE-TVMCP con velas reales de EURUSD (fecha-hora GMT + precio) — una sola sesión de gráfico.
> 2. **Aprobación final del usuario** del documento completo.
>
> **Tier 3 (Wyckoff, PO3, Volume Surge):** fuera de este doc — experimental post-Fase 3 `[P-10]`.
