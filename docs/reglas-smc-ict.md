# reglas-smc-ict.md — Fuente de verdad SMC/ICT
> Estrategia 2.0 · Bot SMC/ICT EURUSD · DOC-01 del WORKPLAN-MAESTRO-V2
> Estado: **POBLADO Y APROBADO** — VER-05 cerrado (Sesion-008, aprobado por Freddy) · gate VER-09 cerrado por Fable (2026-06-11, ver `docs/VER-09-handoff-fable.md` y ADR-002). Umbrales congelados hasta calibración de Fase 3.
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

> **Casos de prueba:** cada concepto cierra con ≥3 ocurrencias reales y ≥1 contraejemplo en EURUSD, con fecha-hora GMT. Esos casos se **extraen del gráfico real vía TradingView MCP** (no se inventan). **Poblados el 2026-06-11** (Sesion-008) con EURUSD H1 25-may→11-jun y M5 10–11-jun; detección reproducible en `scripts/ver05/`.

---

## 1. TIER 1 — ESTRUCTURA DE MERCADO

La estructura es la columna vertebral: define el *bias* y habilita o invalida todo lo demás. Todo nace de un único primitivo: el **swing**.

### 1.1 Swing High / Swing Low `f_detectSwings`

**Concepto.** Extremo local confirmado por simetría temporal (un "fractal"). Es el átomo estructural.

**Definición cuantificada.**
- **Swing High** en la vela de índice `t`: su `high` es **estrictamente mayor** que el `high` de las `swingLen` velas anteriores (`t-1 … t-swingLen`) **y** de las `swingLen` velas posteriores (`t+1 … t+swingLen`). Equivale a `ta.pivothigh(swingLen, swingLen)`.
- **Swing Low** en `t`: simétrico, su `low` estrictamente **menor** a ambos lados.
- **Estructura interna:** idéntica definición pero con `internalLen` (default 3). Detecta swings menores ("internal liquidity") dentro de las piernas del swing mayor.
- **Estructura dominante:** idéntica definición con `majorLen` (default 50). Es la **escala grande** (swing structure de LuxAlgo, `getCurrentStructure(50)`). Marca los movimientos estructurales mayores [T07B].

**Tres escalas (mapeo a LuxAlgo).** El sistema evalúa swings en **tres** longitudes a la vez. Nuestro `swingLen=5` equivale al **interno** de LuxAlgo; `majorLen=50` equivale al **swing (dominante)** de LuxAlgo. La capa dominante es la que faltaba: hasta T07B solo existían `swingLen`/`internalLen` para la estructura (y `majorLen=50` ya se usaba para el rango P/D en T07 §2.3).

**Parámetros default.**
| Param | Default | Rango sugerido | Nota |
|---|---|---|---|
| `majorLen` | **50** | 20–80 | Estructura **dominante** / swing grande (= swing structure de LuxAlgo). Capa de contexto [T07B]. |
| `swingLen` | **5** | 3–10 | Estructura mayor (≈ interno de LuxAlgo). Gatillo de estructura local. |
| `internalLen` | **3** | 2–5 | Estructura interna. Debe ser `< swingLen` siempre. |

**Confirmación / anti-repaint.**
- Un swing en `t` **no existe** hasta el cierre de la vela `t + swingLen` (hacen falta `swingLen` velas a la derecha para confirmarlo). Latencia inherente = `swingLen` velas. Esto es **deseable**: garantiza cero repaint. La escala dominante hereda esto: un swing 50 confirma 50 velas tarde (≈2 días en H1) y su ruptura puede tardar días — es correcto, no un bug [T07B].
- `precio` del swing = `high`/`low` de la vela `t`. Su `barIdx`/`barTime` = los de la vela `t` (no los de la vela de confirmación).

**Manejo de empates (desempate de *detección*).** Desigualdad estricta a ambos lados. Si dos velas **vecinas** (dentro de la ventana `swingLen`) comparten el `high` idéntico al tick, ninguna forma swing por sí sola → no se estampa swing en ese punto. Es solo para evitar swings duplicados/ambiguos. **No confundir** con Equal Highs (EQH): EQH son dos *swings high ya confirmados y separados en el tiempo* a niveles casi iguales (diferencia `< umbral×ATR`) = liquidez (§Liquidez), no un empate de detección.

**Contraejemplos.**
- Vela con `high` mayor que las 5 previas pero solo 4 posteriores: **aún NO es swing** (falta 1 vela de confirmación). Marcarla antes = repaint.
- En lateral, un `high` *igual* (no mayor) a un vecino: **no es swing** → candidato EQH.

**Casos de prueba** *(EURUSD, extraídos vía TV MCP 2026-06-11; H1 25-may→11-jun, M5 10–11-jun · detector `scripts/ver05/`)*:
- ✓ Swing High 2026-05-27 06:00 GMT @ **1.16494** (`pivothigh(5,5)`; confirmado al cierre 2026-05-27 11:00).
- ✓ Swing High 2026-05-29 15:00 GMT @ **1.16859** (techo dominante de la ventana; confirma 20:00).
- ✓ Swing Low 2026-06-08 09:00 GMT @ **1.14997** (mínimo dominante; confirma 14:00).
- ✗ Contraejemplo (mayor solo a un lado → NO swing): 2026-05-26 09:00 GMT high 1.16441 supera las 5 velas previas pero la vela 10:00 (1.16452) lo excede → no es pivot, no se estampa swing.

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

**Casos de prueba** *(EURUSD, TV MCP 2026-06-11; H1)*:
- ✓ Secuencia de giro alcista 2026-06-08: **LL** 09:00 @1.14997 → **HH** 13:00 @1.15548 → **HL** 18:00 @1.15278 → **HH** 2026-06-09 13:00 @1.15781.
- ✓ Secuencia bajista 2026-05-28/29: **LH** 05-28 16:00 @1.16614 → **LH** 05-29 01:00 @1.16566 (techos descendentes).
- ✓ **HH** 2026-05-27 12:00 @1.16615 sobre el HH previo 06:00 @1.16494 (continuación alcista sana).
- ✗ Contraejemplo (HL en bajista que NO giró): 2026-06-04 20:00 @1.16082 es **HL** respecto al low previo, pero la estructura siguió bajista (BOS bajista 06-05 12:00) — la clasificación del swing no implica giro; lo confirma el CHoCH, no el HL.

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
- **Escalas:** se evalúa en las **tres** escalas (§1.1). *BOS dominante* (sobre `majorLen=50`) = contexto mayor [T07B]. *BOS swing* (sobre `swingLen`) = estructura local. *BOS interno* (sobre `internalLen`) = gatillo fino. Se registran por separado (confluencias #2 BOS H1 y #4 BOS chart). La capa dominante se **detecta y dibuja**; **no** voltea por sí sola el bias headline hasta decisión de calibración de Fase 3.

**Parámetros default.**
| Param | Default | Nota |
|---|---|---|
| `breakBasis` | `close` | Alternativa `wick` (más sensible, más ruido). |
| escala | swing + interno | Ambas se trackean. |

**Confirmación / anti-repaint.** El swing roto debe estar **ya confirmado** (tiene sus `swingLen` velas a la derecha). La vela de ruptura debe estar **cerrada**. Sin esto, repinta.

**Contraejemplo.** En tendencia alcista, una vela cuya **mecha** supera el structure high pero **cierra por debajo**: NO es BOS → es un *liquidity grab/sweep* del techo. Marcarlo como BOS es el error clásico que invalida un backtest.

**Casos de prueba** *(EURUSD, TV MCP 2026-06-11; H1, ruptura por CIERRE)*:
- ✓ BOS bajista 2026-06-05 12:00 GMT: `close` **1.15866** < structure low 1.16082 (no roto) → continuación bajista (vela 5.27×ATR).
- ✓ BOS bajista 2026-06-02 17:00 GMT: `close` **1.16216** < structure low 1.16284.
- ✓ BOS bajista 2026-06-03 08:00 GMT: `close` **1.16082** < structure low 1.16135.
- ✗ Contraejemplo (mecha que barre sin cierre): 2026-05-27 12:00 GMT high **1.16615** supera el structure high 1.16452 pero `close` 1.16440 queda por debajo → es *liquidity grab/sweep* del techo, NO BOS.

**Casos de prueba — escala DOMINANTE (`majorLen=50`)** *(EURUSD H1, vs LuxAlgo swing structure) [T07B]*:
- ✓ BOS bajista ~**1.15762** — pivote (structure low dominante) roto inicia jue 2026-05-21 09:00; ruptura confirmada vie 2026-06-05 09:00 (`close` < structure low dominante, continuación bajista de gran escala).

---

### 1.4 CHoCH — Change of Character `f_detectCHoCH`

**Concepto.** Primera ruptura **en contra** de la tendencia vigente: el precio cierra más allá del swing que **protegía** la estructura. Es el **primer aviso** de posible giro (todavía no es giro confirmado — eso es MSS, §1.5).

**Definición cuantificada.**
- **CHoCH alcista:** con bias **bajista**, el `close` confirmado es **estrictamente mayor** que el `structure high` que protegía (último LH). → bias candidato pasa a `+1`.
- **CHoCH bajista:** con bias **alcista**, el `close` confirmado es **estrictamente menor** que el `structure low` que protegía (último HL). → bias candidato pasa a `-1`.
- Misma mecánica de cierre y misma regla anti-repaint que BOS; lo que cambia es **cuál** swing se rompe (el protector, no el extensor).
- **Escalas:** *CHoCH interno* (sobre `internalLen`) = cambio menor, suele ser el gatillo de entrada (IDM/precisión); *CHoCH swing* = cambio mayor de bias; *CHoCH dominante* (sobre `majorLen=50`) = cambio de carácter de gran escala/contexto [T07B]. **No voltear el bias mayor con una ruptura interna.** El CHoCH dominante se detecta y dibuja; su efecto sobre el bias headline queda diferido a calibración de Fase 3 (no voltea solo).

**Efecto.** Un CHoCH **invierte el bias de trabajo** del TF. La siguiente ruptura en la nueva dirección ya sería un BOS (que confirma la nueva tendencia).

**Contraejemplo.** En tendencia alcista, cierre por debajo de un low **interno** menor pero **no** por debajo del último HL swing: es CHoCH **interno** como mucho — el bias swing sigue alcista. Tratarlo como giro mayor es sobre-reaccionar al ruido.

**Casos de prueba** *(EURUSD, TV MCP 2026-06-11; H1)*:
- ✓ CHoCH bajista 2026-06-01 13:00 GMT: con bias alcista, `close` **1.16101** < HL protector 1.16416 → bias candidato a −1 (este caso es además MSS, §1.5).
- ✓ CHoCH alcista 2026-05-27 06:00 GMT: con bias bajista, `close` **1.16456** > LH protector 1.16452 → bias a +1.
- ✓ CHoCH alcista 2026-05-29 14:00 GMT: `close` **1.16687** > LH protector 1.16566.
- ✗ Contraejemplo (CHoCH **interno** que NO voltea el bias swing): 2026-06-02 04:00 GMT `close` 1.16379 rompe un swing interno (1.16370) pero NO el LH swing → es CHoCH interno; el bias mayor sigue bajista.

**Casos de prueba — escala DOMINANTE (`majorLen=50`)** *(EURUSD H1, vs LuxAlgo swing structure) [T07B]*:
- ✓ CHoCH bajista ~**1.17225** — pivote dominante roto inicia jue 2026-05-07 16:00; ruptura confirmada mié 2026-05-13 01:00.
- ✓ CHoCH ~**1.15777** — pivote dominante roto inicia mar 2026-06-09 09:00; ruptura confirmada jue 2026-06-11 15:00.
- Comportamiento esperado: la estructura dominante sigue al precio y no marca nueva ruptura hasta que el precio rompe ese LL/HH; no aparece otra hasta el próximo HH/LL.

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

**Casos de prueba** *(EURUSD, TV MCP 2026-06-11; H1)*:
- ✓ MSS bajista 2026-06-01 13:00 GMT: CHoCH swing (`close` **1.16101** < HL 1.16416) **con displacement** — vela rango **3.51×ATR**, cuerpo **98%**. Giro de alta convicción que abrió la caída a 1.15.
- ✓ (escala interna, apoyo) 2026-06-02 16:00 GMT: CHoCH interno con vela 1.57×ATR / cuerpo 85% (MSS-interno).
- ✓ (escala interna, apoyo) 2026-06-05 12:00 GMT: ruptura con vela 5.27×ATR / cuerpo 97% (displacement extremo del tramo bajista).
- ✗ Contraejemplo (CHoCH swing SIN displacement → NO MSS): 2026-05-29 14:00 GMT `close` 1.16687 rompe el LH 1.16566 con rango grande (2.93×ATR) pero **cuerpo 63%** (<70%) → CHoCH normal, no MSS; el filtro de cuerpo descarta el giro de mecha dominante.
> *Nota de extracción:* el MSS swing es por diseño **raro** (1 ocurrencia limpia en 300 velas H1 de la ventana) — coherente con su rol de "giro con convicción". Los dos apoyos internos documentan la mecánica displacement+CHoCH a menor escala.

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

**Casos de prueba** *(EURUSD, TV MCP 2026-06-11; H1)*:
- ✓ Pierna impulsiva (b, displacement) 2026-06-05 12:00 GMT: vela −1 de **5.27×ATR**, cuerpo 97% → motor del tramo bajista hacia 1.15. **#7 impulso previo** a la zona.
- ✓ Pierna impulsiva (a, 2+ BOS sin CHoCH): BOS bajistas encadenados 06-02 17:00 → 06-03 08:00 → 06-05 12:00 sin CHoCH intermedio.
- ✓ **#8 corrección en curso**: 2026-06-09→06-10 retroceso escalonado con velas solapadas desde 1.149 hacia ~1.156 (pullback correctivo, sin BOS nuevo).
- ✗ Contraejemplo (BOS aislado de rango normal ≠ impulso): 2026-06-08 08:00 GMT BOS `close` 1.15084 con vela 1.21×ATR / cuerpo 52% → ruptura débil, no califica como impulso.

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

**Casos de prueba** *(EURUSD, TV MCP 2026-06-11; H1, filtro vol ≥2× Cumulative Mean Range)*:
- ✓ OB bajista 2026-06-01 12:00 GMT, zona **[1.16452, 1.16506]** (última vela alcista antes del MSS bajista 13:00).
- ✓ OB bajista 2026-06-05 11:00 GMT, zona **[1.16345, 1.16420]** (última alcista antes del impulso −5.27×ATR 12:00).
- ✓ OB alcista 2026-06-08 08:00 GMT, zona **[1.15079, 1.15235]** (última bajista antes de la ruptura alcista 12:00 desde el mínimo 1.14997).
- ✗ Contraejemplo: una vela bajista en el chop de 2026-05-26 07:00–10:00 antes de un avance sin ninguna vela ≥2×CMR y sin romper estructura → no es OB, es ruido.

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

**Casos de prueba** *(EURUSD, TV MCP 2026-06-11; H1, fixed 0.25×ATR, confirma cierre 3ª vela)*:
- ✓ FVG bajista 2026-06-01 14:00 GMT: gap **[1.16184, 1.16452]**, altura 2.45×ATR, CE **1.16318** (tras el MSS).
- ✓ FVG bajista 2026-06-05 13:00 GMT: gap **[1.15998, 1.16345]**, altura 2.90×ATR, CE **1.16172** (impulso fuerte).
- ✓ FVG alcista 2026-05-29 15:00 GMT: gap **[1.16532, 1.16673]**, altura 1.17×ATR, CE **1.16602**.
- ✗ Contraejemplo (sub-umbral, se descarta): 2026-06-04 11:00 GMT gap alcista [1.16284, 1.16304] = **0.209×ATR** (< 0.25) — micro-ineficiencia: el filtro de tamaño la descarta, no se crea zona. (En la ventana 25-may→11-jun hay **33 gaps sub-umbral** como este, todos filtrados.)
- ⓘ Caso de invalidación (NO de descarte): 2026-06-03 06:00 GMT gap bajista [1.16224, 1.16244] = **0.255×ATR** → **PASA** el filtro (≥0.25) y la zona SÍ se crea, pero `close 1.16164 < bottom 1.16224` la **invalida** (estado 3) y no se dibuja. Ilustra la máquina de mitigación, no el umbral. *(Caso corregido en Sesion-018: antes rotulado por error como "sub-umbral".)*

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

**Casos de prueba** *(EURUSD, TV MCP 2026-06-11; H1, rango dominante strong_high 1.16859 / strong_low 1.14997, eq 1.15928)*:
- ✓ Premium: 2026-05-31→06-01 el precio cotizó ~1.166 (> eq 1.15928, ~90% del rango) → favorece short; en efecto cayó.
- ✓ Discount: precio actual 2026-06-11 09:00 GMT **1.15322** < eq → zona discount, favorece long.
- ✓ Banda equilibrium [45%, 55%] = **[1.15835, 1.16021]**: el precio dentro de ella (#31) resta peso por falta de ventaja de localización.
- ✗ Contraejemplo: comprar en premium (~1.166, 90% del rango) "porque hay OB alcista" → opera contra la localización; el OB en premium tiene mucha menor probabilidad.

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

**Casos de prueba** *(EURUSD, TV MCP 2026-06-11; H1, eqThreshold 0.1×ATR)*:
- ✓ EQH 2026-05-27 12:00 @1.16615 ≈ 2026-05-28 16:00 @1.16614 (diff **0.009×ATR**) → doble techo, liquidez BSL.
- ✓ EQL 2026-06-03 14:00 @1.15949 ≈ 2026-06-03 22:00 @1.15946 (diff **0.036×ATR**) → doble suelo, liquidez SSL.
- ✓ EQL 2026-06-08 18:00 @1.15278 ≈ 2026-06-09 00:00 @1.15270 (diff **0.086×ATR**).
- ✗ Contraejemplo: 2026-05-29 15:00 @1.16859 vs 2026-05-28 16:00 @1.16614 distan ~1.7×ATR → NO son EQH (uno es HH del otro), el umbral 0.1×ATR los separa.

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

**Casos de prueba** *(EURUSD, TV MCP 2026-06-11; H1)*:
- ✓ Pierna bajista impulsiva con BOS, origen high 2026-06-04 11:00 @1.16455 → extremo low 2026-06-08 09:00 @1.14997. **GP [50–61.8%] = [1.15726, 1.15898]**; **OTE [61.8–79%] = [1.15898, 1.16149]**.
- ✓ Retroceso al **GP**: el rally correctivo 2026-06-09 13:00 alcanzó 1.15781 (dentro de [1.15726, 1.15898]) → zona premium del tramo bajista = entrada short.
- ✓ La zona OTE más profunda (hacia 1.16149) ofrece mejor precio / mayor R:R si se alcanza.
- ✗ Contraejemplo: medir fib sobre la pierna correctiva 06-09→06-10 (sin BOS propio) → el OTE resultante no tiene significado institucional.

---

### 2.6 Breaker `f_detectBreaker`

**Concepto.** Un OB que **falló** (fue invalidado) cambia de polaridad y pasa a actuar en sentido contrario. Un OB alcista roto a la baja se convierte en resistencia (breaker bajista) en el retest.

**Definición cuantificada.** Cuando un OB pasa a `state = 3 invalidada` (§2.1: una vela cierra atravesando su borde protector) → se crea una `SMC_Zone` KIND_BREAKER en las mismas coordenadas con `dir` **invertido**. En el **retest** desde el otro lado, opera como zona en la nueva dirección. Hereda la máquina de mitigación del OB.

**Parámetros default.** Heredados de OB (§2.1). Confluencia #22.

**Contraejemplo.** Un OB simplemente **mitigado** (`state 2`, el precio lo testeó y respetó) **no** es breaker — sigue siendo OB válido en su dirección original. El breaker requiere **invalidación** (cierre a través), no un mero toque.

**Casos de prueba** *(EURUSD, TV MCP 2026-06-11; H1)*:
- ✓ Invalidación con cambio de polaridad: el OB alcista que originó el impulso del 2026-05-29 (zona ~[1.16450, 1.16532]) fue **invalidado** por el `close` 1.16101 del 2026-06-01 13:00 (atraviesa el borde protector) → se crea breaker bajista con `dir` invertido en esas coordenadas.
- ✓ El rebote posterior 2026-06-09 a 1.15781 se quedó muy por debajo de la zona invertida (no retesteó el breaker), coherente con bias bajista dominante.
- ✓ Otra invalidación: OB bajista [1.16452, 1.16506] del 06-01 mitigado y luego superado en el rebote de 06-02 (cierre por encima) → candidato a breaker alcista.
- ✗ Contraejemplo: un OB simplemente **mitigado** (precio lo toca y respeta, `state 2`) NO es breaker — sigue siendo OB en su dirección original.
> *Nota de extracción:* el retest limpio de un breaker es escaso en la ventana de 300 velas (tendencia bajista persistente sin pullbacks profundos); la invalidación + flip de polaridad sí está documentada con datos reales arriba.

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

**Casos de prueba** *(EURUSD, TV MCP 2026-06-11; H1, mecha ≥2× cuerpo)*:
- ✓ Rejection alcista 2026-06-08 09:00 GMT: low **1.14997** (mínimo dominante = SSL), mecha inferior **2.1×** cuerpo, cierra en mitad superior → defensa del suelo, marcó el giro.
- ✓ Rejection bajista 2026-05-27 12:00 GMT: high **1.16615** (EQH/BSL), mecha superior **2.8×** cuerpo → rechazo del techo de liquidez.
- ✓ Rejection alcista 2026-06-05 11:00 GMT: low **1.16345** sobre la zona OB, mecha inferior **4.5×** cuerpo.
- ✗ Contraejemplo (mecha larga sin nivel): 2026-06-02 21:00 GMT mecha superior 32× cuerpo pero a media estructura, sin tocar OB/FVG/pool/EQHL/PD/EMA → ruido, no rejection operable.

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

**Casos de prueba** *(EURUSD, TV MCP 2026-06-11; H1)*:
- ✓ Flip: el nivel 1.16452 (swing high) fue roto con **cierre limpio** 1.16456 el 2026-05-27 06:00; en visitas posteriores actuó como soporte/resistencia según el lado (cambio de rol confirmado por el cierre, no por mecha).
- ✓ Flip de rango: la zona ~1.16135 (swing low 06-02) tras romperse por cierre 06-03 actuó como techo en el retest.
- ✓ Mitigation block: última vela contraria antes del impulso interno alcista 2026-06-02 04:00 (sin sweep previo de un pool) → zona high/low de esa vela.
- ✗ Contraejemplo: un nivel "roto" solo por **mecha** (sweep BSL 1.16615 del 05-27, sin cierre limpio) que luego se retestea NO es flip — el cierre definitorio nunca ocurrió.

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

**Casos de prueba** *(EURUSD, TV MCP 2026-06-11; H1, poolTol 0.1×ATR, minTouches 2)*:
- ✓ Pool **BSL** ~1.16615 (cluster EQH 05-27 12:00 / 05-28 16:00, `touches`=2) — imán al alza barrido después.
- ✓ Pool **SSL** ~1.15948 (cluster EQL 06-03 14:00 / 06-03 22:00, `touches`=2).
- ✓ Pool **SSL** ~1.15274 (cluster EQL 06-08 18:00 / 06-09 00:00, `touches`=2) — barrido por la mecha del 06-10 22:00.
- ✗ Contraejemplo: el swing low 1.14997 (06-08), **ya barrido** por el rally posterior, deja de ser pool activo — su liquidez ya se tomó.

---

### 3.2 Sweep (barrido) `f_detectSweep`

**Concepto.** El precio **supera** un pool intra-vela (toma la liquidez) pero **cierra de vuelta** dentro del rango: la liquidez fue barrida sin continuación → suele preceder el movimiento contrario. Es la señal de "trampa" más importante del SMC.

**Definición cuantificada** (al cierre):
- **Sweep de SSL (alcista):** el `low` de la vela perfora por debajo de `pool.level` (SSL) pero el `close` queda **por encima** del nivel → `pool.swept := true`; sesgo alcista. Confluencia #10 (sweep contrario).
- **Sweep de BSL (bajista):** el `high` perfora por encima de un pool BSL pero el `close` queda **por debajo**.
- Requiere un **pool confirmado** (§3.1) como objetivo.

**Contraejemplo.** Una vela que perfora el pool **y cierra más allá** (no vuelve): eso **no** es sweep → es BOS/false breakout (§3.7). El sweep exige el cierre de **retorno**.

**Casos de prueba** *(EURUSD, TV MCP 2026-06-11; M5/H1)*:
- ✓ Sweep SSL 2026-06-11 17:25 GMT (M5): el `low` perfora a **1.15036** bajo los SSL ~1.15164/1.15074, pero `close` 1.15228 vuelve por encima → sesgo alcista; siguió rally explosivo (+60 pips en 10 min).
- ✓ Sweep BSL 2026-05-27 12:00 GMT (H1): `high` 1.16615 perfora el pool BSL ~1.16452 pero `close` 1.16440 queda por debajo.
- ✓ Sweep SSL 2026-06-11 12:25 GMT (M5, NY): `low` 1.15164 perfora el SSL 1.15257, `close` 1.15279 retorna.
- ✗ Contraejemplo (perfora y cierra más allá = NO sweep): 2026-06-05 12:00 GMT (H1) `close` 1.15866 queda **por debajo** del nivel roto → es BOS/false breakout bajista, no sweep.

---

### 3.3 Grab `f_detectGrab`

**Concepto.** Subconjunto del sweep: una **mecha** toma la liquidez de un nivel **sin** exigir un pool confirmado (un solo swing). Más fino y frecuente que el sweep.

**Definición cuantificada.** La mecha de la vela supera un swing high/low no barrido y el `close` queda de vuelta dentro, **sin** requerir cluster/pool (≥2 touches). Si el nivel barrido ES un pool confirmado → cuenta como **sweep** (mayor peso); si es un swing aislado → **grab**. Confluencia #11.

**Contraejemplo.** Una mecha larga que **no** alcanza ningún swing/nivel previo: no hay liquidez que tomar → no es grab.

**Casos de prueba** *(EURUSD, TV MCP 2026-06-11; M5, swing aislado sin pool)*:
- ✓ Grab BSL 2026-06-11 07:30 GMT: mecha **1.15542** supera el swing high aislado 1.15514, `close` 1.15509 retorna (un solo swing, sin cluster).
- ✓ Grab SSL 2026-06-11 09:50 GMT: mecha **1.15335** bajo el swing low 1.15350, `close` 1.15364.
- ✓ Grab BSL 2026-06-10 23:40 GMT: mecha **1.15378** sobre el swing 1.15368, `close` 1.15364.
- ✗ Contraejemplo: el sweep del 06-11 17:25 toma un **pool confirmado** (≥2 touches) → cuenta como **sweep** (mayor peso), no como grab. Y una mecha que no alcanza ningún swing previo no es grab.

---

### 3.4 Kill Zones `f_killZone` `[ADR-001]`

**Concepto.** Ventanas horarias de **alta actividad institucional**. En el diseño multi-símbolo NO son un filtro duro (un bloqueo por reloj sabotea símbolos con otras sesiones o sin sesiones —cripto/índices 24h—). Son una **confluencia ponderada** opcional + un **perfil configurable por símbolo**. El guardián universal de calidad de liquidez es el **filtro de spread**, no el reloj — con una precisión de implementación: Pine no puede leer el spread real, así que ese filtro vive **solo en el EA** (Fase 4, `SMC_RiskManager`); en TV los costes se modelan con comisión+slippage (D-PINE-05) y la Fase 3 segmenta resultados por sesión.

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

**Casos de prueba** *(EURUSD, TV MCP 2026-06-11; M5, perfil FX-London-NY, junio=BST/EDT)*:
- ✓ **London KZ** 2026-06-11 06:00–09:00 GMT (= 07:00–10:00 `Europe/London`). Actividad concentrada al inicio (displacement −2.12×ATR a las 06:00).
- ✓ **NY AM KZ** 2026-06-11 12:00–15:00 GMT (= 08:00–11:00 `America/New_York`).
- ✓ **Primera mitad** de London = 06:00–07:30 GMT (ventana requerida para el Judas, §3.5).
- ✗ Contraejemplo (ADR-001): una señal a las 03:00 GMT NO se bloquea por la hora — se gobierna por spread/score; el `sessionProfile` solo aporta peso a la confluencia #34.

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

**Casos de prueba** *(EURUSD, TV MCP 2026-06-11; M5, judasBars 6)*:
- ✓ Judas London 2026-06-11 **06:05 GMT**: sweep SSL del nivel 1.15426 (mecha 1.15424) en la **1ª mitad** de la London KZ → **displacement +1** a las 06:10 (1.62×ATR) en dirección contraria. `dir` Judas = +1 (la real).
- ✓ (análogo, fuera de KZ) 2026-06-11 17:15–17:30: barrido SSL a 1.15030 + displacement +1 de 4.84→6.03×ATR — misma mecánica trampa+reversión (clasifica como Spring/sweep, §3.7, por estar fuera de ventana KZ).
- ✗ Contraejemplo (sweep sin displacement contrario): 2026-06-11 12:25 GMT (NY) sweep SSL 1.15164 que **continuó** a la baja sin reversión impulsiva → solo sweep, no Judas.
> *Nota de extracción:* el Judas completo (sweep en 1ª mitad de KZ + displacement contrario ≤6 velas) es escaso; 1 ocurrencia limpia en la ventana M5 disponible (10–11 jun). Se ampliará con más sesiones M5 en Fase 1.

---

### 3.6 IDM — Inducement `f_detectIDM`

**Concepto.** La **liquidez señuelo**: un pullback menor cuya liquidez (interna) es barrida **antes** de que el precio alcance el OB/FVG objetivo. Es la liquidez que "induce" entradas tempranas que el smart money toma antes del movimiento real.

**Definición cuantificada.** En una tendencia alcista hacia un OB/FVG objetivo, el IDM es el **swing low interno** (`internalLen`) más cercano por debajo del precio cuya liquidez se barre **antes** de que el precio toque el objetivo. Detección: pool/grab interno tomado entre el origen del impulso y la zona objetivo. Confluencia #33 (IDM barrido). Simétrico bajista.

**Contraejemplo.** Si el precio alcanza el OB **sin** haber barrido ningún inducement intermedio, la entrada es de menor calidad (no hubo limpieza de liquidez señuelo) — el IDM barrido es lo que valida que el camino está "limpio".

**Casos de prueba** *(EURUSD, TV MCP 2026-06-11; M5)*:
- ✓ Inducement previo al empuje de London 2026-06-11: el swing low interno **1.15426** fue barrido a las 06:05 (mecha 1.15424) **antes** de que el precio empujara al alza → liquidez señuelo tomada, camino limpio hacia arriba.
- ✓ IDM en el rally de las 17:25: los SSL internos 1.15074/1.15054 fueron barridos (mecha 1.15030) inmediatamente antes del impulso → inducement clásico.
- ✓ IDM bajista (simétrico) en NY 2026-06-11 12:55: barrido del BSL interno ~1.15418 antes del tramo bajista a 1.15164.
- ✗ Contraejemplo: si el precio alcanza el OB **sin** barrer ningún inducement intermedio, la entrada es de menor calidad (no hubo limpieza de liquidez señuelo).

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

**Casos de prueba** *(EURUSD, TV MCP 2026-06-11; M5, fbBars 2)*:
- ✓ **False Breakout** 2026-06-11 17:20 GMT: `close` 1.15040 cruza bajo el SSL 1.15426 → vela siguiente cierra de vuelta arriba (17:30 `close` 1.15599) dentro de ≤2 velas.
- ✓ **Spring** 2026-06-11 17:15–17:20 GMT: sweep del **mínimo del rango** (1.15030) con reversión rápida al alza (rally 4.84×ATR) → `dir +1`. (También Spring 2026-06-10 23:10 barriendo 1.15266.)
- ✓ **Raid** 2026-06-11 17:25 GMT: barrido agresivo de un cluster SSL de alta liquidez (varios niveles 1.15164/1.15141/1.15074, `touches` alto) → stop raid, mayor peso.
- ✗ Contraejemplo: el `close` 1.15866 del 06-05 12:00 (H1) cruzó el nivel y **no** revirtió en ≤2 velas → breakout real (BOS), no falso.

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

**Casos de prueba** *(EURUSD, TV MCP 2026-06-11; H1+M5, dispFactor 1.5 / bodyPct 0.70)*:
- ✓ 2026-06-05 12:00 GMT (H1): rango **5.27×ATR**, cuerpo 97%, −1 → impulso que abrió la caída a 1.15.
- ✓ 2026-06-11 17:30 GMT (M5): rango **6.03×ATR**, cuerpo 89%, +1 → rally explosivo post-barrido.
- ✓ 2026-06-01 13:00 GMT (H1): rango **3.51×ATR**, cuerpo 98%, −1 → vela del MSS.
- ✗ Contraejemplo (rango grande, cuerpo pequeño): 2026-05-29 14:00 GMT rango 2.93×ATR pero cuerpo **63%** (<70%) → indecisión/rechazo, NO displacement.

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

**Casos de prueba** *(EURUSD, TV MCP 2026-06-11; H1, frontera de día del broker 22:00 GMT)*:
- ✓ Apertura **diaria** 2026-05-28 22:00 GMT @ **1.16519**; 2026-06-01 22:00 GMT @ **1.16342** (líneas de referencia institucional).
- ✓ Apertura **semanal** (domingo) 2026-05-25 22:00 GMT @ **1.16398** — primer bar de la semana.
- ✓ **#36** (open cercano): cuando el precio entra en ±0.5×ATR de una de estas aperturas, el nivel actúa como S/R inmediato (direccional según el lado).
- ✗ Contraejemplo: el precio a ~3×ATR de la apertura semanal (p.ej. 1.15 vs 1.16398) → el nivel existe pero NO es confluencia activa.

---

### 4.3 EMAs — estado, cruces, rebotes, alineación `f_emaState`

**Concepto.** Las medias móviles exponenciales 20/50/200 dan **confirmación de tendencia**. Son la única familia no-puramente-SMC: confirman, no lideran → peso base bajo (se calibra en Fase 3). Colapsadas de 15 confluencias originales a **6** `[FIX P-05]` para evitar doble conteo de pares mutuamente excluyentes.

**Definición cuantificada** (6 confluencias direccionales, #37–#42):
- **#37 vs EMA200:** `close > EMA200` → +1 / `close < EMA200` → −1. **Una sola** confluencia direccional (no dos sumando al mismo score).
- **#38 vs EMA50:** ídem con EMA50.
- **#39 vs EMA20:** ídem con EMA20.
- **#40 cruce reciente alineado:** un cruce de cualquier par (20×50, 50×200, 20×200) ocurrido en `≤ crossBars` velas (default 20) cuya dirección coincide con el sesgo. Es un **EVENTO discreto** (no un estado siempre-activo como #37–#39) → **SÍ cuenta como confluencia/voto** cuando ocurre junto a otros conceptos; no infla el score porque solo se activa puntualmente. +peso al lado del cruce.
- **#41 rebote en EMA alineado:** el precio toca una EMA y cierra de vuelta con mecha (`mecha ≥ rejWickFactor × cuerpo`, §2.7) en la dirección de la tendencia.
- **#42 3 EMAs alineadas:** `EMA20 > EMA50 > EMA200` (→ +1 fuerte) o `EMA20 < EMA50 < EMA200` (→ −1). Tendencia limpia.

**Eventos de cruce — marca + registro (todos) y Stack Flip (régimen).** Refinamiento operativo: **cada cruce de par deja una seña en el gráfico y se almacena** (`KIND_EMACROSS`) para poder verlo y contabilizarlo cuando coincide con otros conceptos. Jerarquía de relevancia: `20×50` (frecuente, menor peso) < `50×200` / `20×200` (más raros, mayor peso).
- **Stack Flip (cruce del grupo rápido sobre la lenta) — evento REFORZADO:** cuando **EMA20 *y* EMA50** quedan **ambas al mismo lado de la EMA200** habiendo estado al otro lado (transición de régimen; el *golden cross / death cross* clásico del grupo rápido contra la media de largo plazo). Es la **entrada** al estado de 3 EMAs alineadas (#42). Marca y registro propios (`KIND_EMASTACK`); `dir` = lado del flip (+1 ambas sobre la 200 / −1 ambas bajo). **Cuenta como confluencia de MAYOR convicción** (refuerza #40/#42); es el evento puntual del cambio de régimen, no un voto siempre-activo.

**Parámetros default.**
| Param | Default | Nota |
|---|---|---|
| `emaFast/Mid/Slow` | **20 / 50 / 200** | periodos estándar. |
| `crossBars` | **20** | antigüedad máxima de un cruce para contar. |
| `rejWickFactor` | 2.0 | reusa el de Rejection (§2.7) para el rebote. |

**Contraejemplo `[FIX P-05]`.** Contar "precio sobre EMA200" Y "precio bajo EMA200" como confluencias separadas que suman al mismo score: una de las dos está SIEMPRE activa → +peso garantizado a cualquier señal. Por eso #37–#39 son **direccionales únicas** (suman a long O short, nunca inflan el total).

**Casos de prueba** *(EURUSD, TV MCP 2026-06-11; H1, EMAs 20/50/200)*:
- ✓ **#42** tres EMAs alineadas bajistas: 2026-06-08→06-11 de forma sostenida `EMA20 < EMA50 < EMA200`. Ej. 06-11 09:00 GMT → E20 1.15430 < E50 1.15461 < E200 1.15764 (→ −1 fuerte).
- ✓ **#37** `close < EMA200` persistente durante toda la caída (06-08→06-11, close 1.153 vs E200 1.157–1.162).
- ✓ **#40** sin cruce alcista reciente que contradiga el sesgo en ≤20 velas → confirma continuación bajista.
- ✓ **Stack Flip BAJISTA** 2026-06-08 (medido sobre `eurusd_h1.csv`): EMA20 y EMA50 quedan ambas bajo la EMA200 tras la caída → cambio de régimen bajista; coincide con el inicio del tramo dominante a la baja (death cross), evento de alta convicción. *(También flip alcista 05-29 12:00 y flip bajista 06-02 20:00 en la ventana.)*
- ✓ **Cruces de par marcados:** 20×50 frecuentes (p.ej. 06-04 15:00 +, 06-05 13:00 −) = menor peso; 50×200/20×200 más raros (06-02 17:00/20:00 −) = mayor peso. Todos dejan seña + registro.
- ✗ Contraejemplo (stack flip): un cruce 20×50 aislado mientras ambas siguen del mismo lado de la EMA200 NO es stack flip (no cambia el régimen vs la 200) → es solo un cruce de par menor (#40), no el evento reforzado.
- ✗ Contraejemplo `[FIX P-05]`: contar "close > EMA200" Y "close < EMA200" como dos confluencias separadas que suman al mismo score → una está SIEMPRE activa, +peso garantizado. Por eso #37–#39 son direccionales únicas.

---

### 4.4 Impulsive / Corrective `f_classifyLeg`

**Concepto.** La distinción más básica del lenguaje del mercado: un **tramo impulsivo** (la intención institucional, eficiente y direccional, el que crea desequilibrio y rompe estructura) frente a un **tramo correctivo** (el retroceso/consolidación que devuelve precio a la liquidez, solapado e ineficiente). No es una confluencia aditiva: es un **clasificador de estado** que CALIFICA el contexto — solo sobre un tramo **impulsivo** tiene sentido medir OTE/GP (§2.5), y un retroceso correctivo es lo que lleva el precio al OB/FVG/OTE para la entrada.

**Definición cuantificada.** Sobre un **tramo** = segmento del precio en la dirección del movimiento, evaluado **contra el sesgo dominante vigente** (`structMajor.bias`, §1.4/T07B). La clave: lo que separa impulso de corrección **no es el tamaño ni la eficiencia bruta** (verificado: el ER pivote-a-pivote está confundido por la longitud — piernas correctivas cortas dan ER alto y la gran pierna impulsiva da ER bajo), sino **romper estructura en la dirección de la tendencia con fuerza**:
- `hasDisplacement` = el tramo contiene ≥1 vela **displacement** (§4.1, rango ≥1.5×ATR + cuerpo ≥70%).
- `breakAligned` = el tramo produce un **BOS** (§1.3) **alineado con el sesgo dominante** (continuación) **o** un **MSS** (§1.5, CHoCH+displacement que VOLTEA el sesgo con convicción).
- **IMPULSIVO (`dir` = dirección del tramo)** si `hasDisplacement` **Y** `breakAligned`. Es la expansión institucional que extiende (o voltea con MSS) la estructura.
- **CORRECTIVO** en caso contrario: el retroceso **contra-sesgo** entre impulsos. Puede tener una vela fuerte aislada e incluso un micro-BOS interno **contra** la tendencia, pero **no** rompe la estructura dominante en su favor → solapado, retrocede una fracción fib (alimenta el OTE/GP, §2.5).

**Parámetros default.** Ninguno propio: hereda de **Displacement** (§4.1: `dispFactor 1.5` / `bodyPct 0.70`) y de **Estructura** (§1.3/§1.4/§1.5: `swingLen`, `majorLen`, MSS). La distinción es cualitativa (ruptura alineada + fuerza), no un umbral nuevo.

**Contraejemplo.** Un retroceso al alza dentro de una tendencia **bajista** dominante que avanza solapado e incluso imprime **una** vela fuerte: es **correctivo** aunque el precio "suba" y haga un higher-high menor — porque no rompe la estructura dominante a la baja en su favor (va en contra). Clasificarlo impulsivo mediría OTE sobre una pierna sin significado institucional (mismo error que §2.5).

**Casos de prueba** *(EURUSD; verificado sobre `scripts/ver05/eurusd_h1.csv`, la pasada TV MCP 2026-06-11; H1)*:
- ✓ **Impulsivo:** la caída 2026-06-04→06-08 (high 1.16455 → low 1.14997) contiene displacement (06-05 12:00 rango 5.27×ATR cuerpo 97%, +2 más) y encadena **BOS bajistas alineados** (BOS− 06-05 12:00 @1.15866, 06-08 08:00 @1.15084) con el sesgo dominante bajista → impulsivo `dir −1` (la pierna sobre la que §2.5 mide OTE/GP). *(ER medido 0.28 — bajo: confirma que el ER no es el criterio.)*
- ✓ **Correctivo:** el rally 2026-06-09→06-10 (retroceso al GP 1.15781, §2.5) es **contra el sesgo dominante bajista**; aunque imprime una vela fuerte (06-10 11:00, 1.67×ATR) e incluso micro-BOS+ internos, **no** rompe la estructura dominante bajista en su favor → correctivo. *(ER medido 0.13.)*
- ✗ Contraejemplo: clasificar ese retroceso 06-09→06-10 como impulsivo por la única vela fuerte → es contra-sesgo y no rompe estructura dominante → correctivo; medir fib sobre él no tiene significado (§2.5).
> *Nota de extracción:* se descartó un criterio por ER/magnitud (`erThreshold`/`impulseFactor`) tras medir el CSV real: el ER pivote-a-pivote no separa (impulso 0.28 < correcciones cortas 0.6–0.89). El discriminador adoptado (displacement + ruptura alineada con sesgo dominante) sí separa el ejemplo del contraejemplo. Sin umbrales propios → nada que congelar más allá de §4.1/§1.x (ADR-002).

---

> **DEFINICIONES DE reglas-smc-ict.md COMPLETAS** — Tier 1 Estructura (§1), Tier 2 Zonas (§2), Liquidez (§3), Contexto/ICT/EMAs (§4, incl. §4.4 Impulsive/Corrective). Cubren los 42 confluencias canónicas (§4.8 del workplan) — Impulsive/Corrective es **clasificador de estado**, no confluencia aditiva — y todas las funciones de PINE-PLAN §3.
>
> **Cierre DOC-01 (gate VER-05):**
> 1. ✅ **Pasada TradingView MCP (2026-06-11, Sesion-008):** los 24 conceptos poblados con velas reales de EURUSD (fecha-hora GMT + precio). Datos: H1 25-may→11-jun (300 velas) + M5 10–11-jun (300 velas). Detección reproducible en `scripts/ver05/` (`detect.py`, `detect2.py`, `detect_m5.py` sobre `eurusd_h1.csv`/`eurusd_m5.csv`). Notas de escasez documentadas in-situ (MSS swing ×1, Judas ×1, breaker retest) — coherentes con la rareza de esos eventos; se ampliarán con más sesiones M5 en Fase 1.
> 2. ✅ **Aprobación final del usuario** (Freddy, Sesion-008) + **veredicto VER-09 de Fable (2026-06-11): APROBADO** — las 3 notas de escasez aceptadas como deuda controlada con criterios de done en Fase 1 (T12 ≥3 MSS · T18 ≥3 Judas · T19 ≥1 retest breaker). Ver ADR-002.
>
> **Tier 3 (Wyckoff, PO3, Volume Surge):** fuera de este doc — experimental post-Fase 3 `[P-10]`.

---
---

## 5. GAP ICT — Sprint 1.6 (primitivas nuevas)

> **Extensión** sobre el set canónico §1–§4. Estas son las primitivas ICT que faltaban (T26–T40, ver `docs/planes/ESQUELETO-P1-conceptos-EA-pine-repos.md`). **Gate (decisión usuario):** ninguna se codifica en Pine hasta tener aquí su regla cuantificada (umbrales relativos a ATR + casos EURUSD verificados + contraejemplo). Las confluencias nuevas son **candidatas #43+**; el número final lo fija el `[impl]` al cablear el scoring (Fase 2). Anti-doble-conteo `[FIX P-05]` aplica: una variante que *refina* un concepto previo NO suma confluencia nueva. Umbrales **CONGELADOS** hasta Fase 3 (ADR-002).
>
> *Verificación de esta tanda:* contada sobre `scripts/ver05/eurusd_h1.csv` (H1, 300 velas, la misma pasada TV MCP de Sesion-008). Donde el dato no exista en esa ventana (multi-símbolo, futuros, gaps de fin de semana) se indica explícitamente y queda pendiente de pasada TV dedicada.

### 5.1 True FVG (T.FVG) `f_detectTrueFVG` · T26

**Concepto.** Un FVG (§2.2) de **alta calidad institucional**: no cualquier hueco de 3 velas, sino el creado por una **vela media de displacement** (intención real), no por ruido. Refina el FVG, no es un objeto nuevo.

**Definición cuantificada.** Un FVG (§2.2: alcista `low[0] > high[2]`, bajista `high[0] < low[2]`, altura ≥ `fvgThreshold×ATR14`) es **True FVG** si su **vela media** (la del medio del trío, índice −1) es un **displacement** (§4.1: rango ≥ `dispFactor×ATR14` y cuerpo ≥ `bodyPct×rango`). Se marca como `KIND_TFVG` (o flag `true=1` sobre el FVG); hereda la máquina de mitigación (§2.1). **No suma confluencia** propia: eleva el **peso** del FVG existente (#18/#20) — un FVG "true" pesa más en el scoring (Fase 3).

**Parámetros default.** Heredados: `fvgThreshold 0.25` (§2.2) + `dispFactor 1.5` / `bodyPct 0.70` (§4.1). Sin umbral propio.

**Contraejemplo.** Un FVG cuya vela media es pequeña/indecisa (rango < 1.5×ATR o cuerpo < 70%): es un FVG normal, **no** True FVG — el hueco existe pero no hubo desplazamiento institucional que lo respalde (menor probabilidad de respeto).

**Casos de prueba** *(EURUSD, `eurusd_h1.csv`; H1)*: de **34 FVG** detectados en la ventana, **10 son True FVG** (vela media = displacement) — p.ej. los gaps cuya media coincide con las velas de impulso 06-05. Los 24 restantes son FVG normales (vela media sin displacement) → menor peso.

### 5.2 IFVG — Inversion FVG `f_detectIFVG` · T27

**Concepto.** Un FVG que **falló** (fue invalidado) e **invierte su rol**: un FVG alcista roto a la baja pasa a actuar como resistencia (IFVG bajista) en el retest. Es el **análogo exacto del Breaker (§2.6) pero sobre FVG**.

**Definición cuantificada.** Cuando una `SMC_Zone` KIND_FVG pasa a `state = ZS_INVALID` (§2.1: una vela **cierra** atravesando su borde protector) → se crea una `SMC_Zone` `KIND_IFVG` en las mismas coordenadas con `dir` **invertido** y `ZS_ACTIVE`. El retest lo gestiona la **misma** `f_updateZoneMitigation`. Mismo guard que el breaker: solo nace de un FVG (no un IFVG de otro IFVG) y solo en la transición a inválido.

**Parámetros default.** Heredados de FVG (§2.2). Confluencia **nueva candidata** (#43 IFVG alineado), 1 sola (no se suma con el FVG original que ya murió).

**Contraejemplo.** Un FVG simplemente **mitigado** (`ZS_MITIGATED`: el precio lo tocó y respetó) **no** es IFVG — sigue siendo FVG válido en su dirección. El IFVG exige **invalidación** (cierre a través), no un toque.

**Casos de prueba** *(EURUSD, `eurusd_h1.csv`; H1)*: **27 FVG invalidados** en la ventana → 27 IFVG candidatos. Ej.: FVG bull del 05-27 00:00 invalidado por cierre el 05-27 14:00 → IFVG bajista; FVG bull del 05-28 13:00 invalidado el 06-01 13:00 → IFVG bajista (coincide con el gran giro bajista).

### 5.3 BPR — Balanced Price Range `f_detectBPR` · T28

**Concepto.** Dos FVG de **dirección opuesta que se solapan** → zona de "precio balanceado": el solape es un área de reacción fuerte (oferta y demanda se cruzaron ahí).

**Definición cuantificada.** Entre los FVG vivos (§2.2), si un FVG **alcista** y uno **bajista** creados dentro de `bprWindow` velas entre sí tienen **intersección no vacía** (`max(bottoms) < min(tops)`), se crea una `SMC_Zone` `KIND_BPR` = la **intersección** `[max(bottoms), min(tops)]`, con altura ≥ `bprMinOverlap×ATR14`. `dir` = neutro/ambos (zona de reacción bidireccional; el sesgo lo da el contexto). Ciclo de vida vía `f_updateZoneMitigation`.

**Parámetros default.**
| Param | Default | Nota |
|---|---|---|
| `bprWindow` | **20** | velas máximas entre los dos FVG opuestos. |
| `bprMinOverlap` | **0.05** | × ATR14, altura mínima de la intersección (evita solapes triviales). |

**Contraejemplo.** Dos FVG del **mismo** lado, o dos opuestos que **no se tocan** (sin intersección): no hay BPR — el BPR exige el cruce real de un hueco alcista con uno bajista.

**Casos de prueba** *(EURUSD, `eurusd_h1.csv`; H1)*: **15 solapes** FVG-opuesto dentro de ≤20 velas. Ej.: BPR 05-28 (FVG bear 00:00 ∩ FVG bull 13:00) = [1.16235, 1.16260]; BPR 05-29 (04:00 ∩ 06:00) = [1.16394, 1.16422].

### 5.4 Immediate Rebalance (IR) `f_detectImmediateRebalance` · T29

**Concepto.** Lo **contrario** al FVG: una vela de impulso cuyo desequilibrio es **rebalanceado de inmediato** por la vela siguiente (el precio vuelve a su rango sin dejar hueco). Señala que la ineficiencia ya se "curó" → no quedará FVG imán; matiza el contexto (no es zona operable propia).

**Definición cuantificada.** Una vela `i` de impulso (`rango ≥ irFactor×ATR14` y `cuerpo ≥ irBodyPct×rango`) seguida de una vela `i+1` que **cierra de vuelta dentro del cuerpo de `i`** (alcista: `close[i+1] ≤ (open[i]+close[i])/2`; bajista simétrico) → `KIND_IR`, evento puntual (patrón P4, marca histórica). `dir` = el de la vela de impulso original (la que fue rebalanceada).

**Parámetros default.**
| Param | Default | Nota |
|---|---|---|
| `irFactor` | **1.0** | × ATR14, tamaño mínimo de la vela de impulso. |
| `irBodyPct` | **0.60** | cuerpo mínimo (fracción del rango). |

**Contraejemplo.** Una vela de impulso que **deja FVG** (la siguiente NO rellena su rango) es lo opuesto: hay ineficiencia residual → es contexto de FVG (§2.2), no Immediate Rebalance.

**Casos de prueba** *(EURUSD, `eurusd_h1.csv`; H1)*: **11 Immediate Rebalances** — p.ej. 05-27 07:00, 05-29 06:00/08:00, 06-01 06:00 (vela fuerte rebalanceada por la siguiente, sin gap residual).

### 5.5 Volume Imbalance + SIVI/BIVI `f_detectVolumeImbalance` · T31

**Concepto.** Micro-desequilibrio entre **cuerpos** de velas consecutivas con **solape de mechas** — a diferencia del FVG (hueco entre *extremos*), aquí las mechas se tocan pero los cuerpos dejan un gap (apertura ≠ cierre previo). **BIVI** = buy-side (gap de cuerpo al alza), **SIVI** = sell-side (a la baja).

**Definición cuantificada.** En velas consecutivas `i-1`, `i`: hay **Volume Imbalance** si el cuerpo abre con gap respecto al cierre previo pero las mechas se solapan:
- **BIVI (alcista):** `open[i] > close[i-1]` con `(open[i] − close[i-1]) ≥ viThreshold×ATR14` **y** `low[i] ≤ high[i-1]` (mechas solapan).
- **SIVI (bajista):** `open[i] < close[i-1]` con `(close[i-1] − open[i]) ≥ viThreshold×ATR14` **y** `high[i] ≥ low[i-1]`.
`KIND_VI` (zona micro `[close[i-1], open[i]]` o marca), ciclo de vida vía `f_updateZoneMitigation`. **Una sola confluencia** para la familia (no cuenta 3× por VI/SIVI/BIVI — `[FIX P-05]`).

**Parámetros default.**
| Param | Default | Nota |
|---|---|---|
| `viThreshold` | **0.05** | × ATR14, gap mínimo de cuerpo (micro por naturaleza). |

**Contraejemplo.** Un gap entre velas **sin** solape de mechas (`low[i] > high[i-1]` en alcista): eso es un **FVG/gap real** (§2.2), no Volume Imbalance — el VI exige que las mechas se toquen (sólo los cuerpos dejan el hueco).

**Casos de prueba** *(EURUSD, `eurusd_h1.csv`; H1)*: **13 Volume Imbalances** — p.ej. SIVI 05-26 21:00 (gap cuerpo 0.00031), BIVI 05-27 21:00 (0.00022), SIVI 05-31 21:00 (0.00078). (En M5 son mucho más frecuentes, 53 — coherente con su naturaleza micro.)

### 5.6 CISD — Change in State of Delivery `f_detectCISD` · T32

**Concepto.** El **cambio en el estado de entrega**: el precio venía "entregando" en una dirección (un run de velas del mismo color = la pierna de delivery) y **cierra de vuelta cruzando el origen de ese run**. Es un giro **más temprano y fino** que el CHoCH (§1.4): el CHoCH rompe un *pivote swing*; el CISD rompe el *open de la pierna de entrega*, que ocurre antes. **Distinto de CHoCH/MSS** — no los duplica (guard obligatorio del esqueleto).

**Definición cuantificada.** Sea el **último run de delivery** = la secuencia maximal de `≥ cisdMinRun` velas consecutivas del mismo color que termina en la vela previa. Su **origen** = el `open` de la primera vela del run. **CISD alcista:** tras un run **bajista** (≥cisdMinRun velas `close<open`), una vela **cierra por encima** del `open` origen (`close > openOrigen` con `open ≤ openOrigen`). Bajista simétrico (tras run alcista, cierra bajo el origen). `KIND_CISD`, `dir` = el del giro. Anti-repaint por cierre. **El gate `cisdMinRun` es lo que lo hace distinguible:** exige una pierna de entrega real (no un cierre de 1 vela = ruido).

**Parámetros default.**
| Param | Default | Nota |
|---|---|---|
| `cisdMinRun` | **2** | velas consecutivas mínimas del run de delivery. Con 1 sería ruido (39 señales/300 velas); con ≥2 → señal distinguible. |

**Contraejemplo.** Un cierre que cruza el open de **una sola** vela contraria (run de 1) NO es CISD — es ruido intrabar, no un cambio del estado de entrega. Y un CISD **no** es un CHoCH: puede dispararse sin que se haya roto aún ningún pivote swing (es anterior); si además rompe el swing, ya es CHoCH/MSS (§1.4/§1.5).

**Casos de prueba** *(EURUSD, `eurusd_h1.csv`; H1, cisdMinRun 2)*: **8 CISD** en la ventana. Destacan: **CISD bajista 06-05 12:00** (run de 6 velas bajistas, el gran shift de entrega que abrió la caída) y **CISD alcista 06-09 08:00** (run de 3, inicio del rally correctivo). Con cisdMinRun 1 saldrían 39 (ruido, descartado); con ≥2 quedan 8 (distinguibles). Confluencia **candidata #47**.

### 5.7 Vacuum Block `f_detectVacuumBlock` · T33

**Concepto.** Un **vacío de precio** por apertura (frontera de sesión/día/semana o noticia): un gap **grande** donde no hubo negociación → actúa como **imán de retorno** (el precio tiende a volver a rellenarlo).

**Definición cuantificada.** En la frontera de vela (en FX 24h, el salto `close[i-1] → open[i]` en la frontera de día/semana del broker), si `|open[i] − close[i-1]| ≥ vacuumFactor×ATR14` → `SMC_Zone` `KIND_VACUUM` = `[min, max]` de `(close[i-1], open[i])`, `dir` = signo del gap. Ciclo de vida vía `f_updateZoneMitigation` (se "mitiga" al rellenarse). **Distinto de:** Volume Imbalance (§5.5, micro, mechas solapan) y FVG (§2.2, hueco de 3 velas) — el Vacuum es **un único gap grande** de apertura.

**Parámetros default.**
| Param | Default | Nota |
|---|---|---|
| `vacuumFactor` | **0.5** | × ATR14, tamaño mínimo del gap de apertura. |

**Contraejemplo.** Un micro-gap de cuerpo con mechas solapadas (< 0.5×ATR) es **Volume Imbalance** (§5.5), no Vacuum — el Vacuum exige un salto grande de apertura (vacío real de negociación).

**Casos de prueba** *(EURUSD, `eurusd_h1.csv`; H1, vacuumFactor 0.5)*: **3 Vacuum Blocks**, todos en la frontera de día del broker (21:00 GMT en este feed): 05-31 21:00 (gap 0.72×ATR ↓), 06-04 21:00 (0.53×ATR ↑), 06-07 21:00 (0.85×ATR ↓). Confluencia **candidata #48**. *(Nota: en FX los gaps grandes son escasos y de frontera; en índices/futuros con cierre nocturno serían más frecuentes — símbolo-agnóstico, ADR-001.)*

### 5.8 Propulsion Block `f_detectPropulsionBlock` · T34

**Concepto.** Un **OB anidado dentro de otro OB** del mismo sentido: tras respetar la zona del OB original, el precio forma un OB más pequeño **dentro** de ella y **propulsa** en la dirección de continuación. Es un OB de **continuación** → refuerza el OB, no es objeto nuevo.

**Definición cuantificada.** Sobre la detección de OB existente (§2.1, `f_detectOB`): un OB recién formado es **Propulsion Block** si su zona `[bottom, top]` está **contenida** (o solapa ≥ `propOverlap` de su altura) dentro de un OB **vivo previo del mismo `dir`** (`ZS_ACTIVE/ZS_PARTIAL`). `KIND_PROPULSION`, hereda `f_updateZoneMitigation`. **No suma confluencia** propia: eleva el **peso** del OB de continuación (#17/#19).

**Parámetros default.**
| Param | Default | Nota |
|---|---|---|
| `propOverlap` | **0.5** | fracción mínima de solape (altura) del OB nuevo dentro del OB previo del mismo dir. |

**Contraejemplo.** Un OB nuevo de **dirección opuesta** al que lo contiene, o uno que cae **fuera** de cualquier OB vivo: es un OB normal (§2.1), no Propulsion — el Propulsion exige anidamiento mismo-sentido (continuación).

**Casos de prueba** *(EURUSD; H1)*: como **refinamiento de `f_detectOB`** (máquina ya validada en T05), las instancias de Propulsion son el **subconjunto** de OBs anidados mismo-sentido; la verificación de instancias se hace al cablear sobre `f_detectOB` (no requiere detector independiente). Definición congelada; conteo exacto en la pasada de validación visual con el resto del set.

### 5.9 IPR — Imbalanced Price Range `f_detectIPR` · T35

**Concepto.** Un **rango de precio desbalanceado**: una zona donde se acumulan **varias ineficiencias del mismo lado** (FVG/imbalances apilados en una dirección) → el rango "tira" hacia ese lado (contexto de bias, no zona puntual de entrada).

**Definición cuantificada.** En una ventana de `iprWindow` velas, si hay **≥ iprMinGaps** FVG (§2.2) **del mismo `dir`** (y ninguno opuesto que lo neutralice) → el rango `[min(bottoms), max(tops)]` de esos gaps es un `KIND_IPR`, `dir` = el común. Es **contexto/bias** (alimenta el sesgo y el motor EA), no una zona operable independiente. Opuesto conceptual del **BPR** (§5.3: ahí los gaps son *opuestos y se cruzan*; aquí son *del mismo lado y se apilan*).

**Parámetros default.**
| Param | Default | Nota |
|---|---|---|
| `iprWindow` | **10** | velas de la ventana de búsqueda. |
| `iprMinGaps` | **3** | FVG del mismo lado mínimos para declarar desbalance. |

**Contraejemplo.** Una ventana con FVG **mezclados** (alcistas y bajistas) está **balanceada** → no es IPR (tiende a BPR/equilibrio, §5.3). El IPR exige acumulación **unidireccional**.

**Casos de prueba** *(EURUSD, `eurusd_h1.csv`; H1, iprWindow 10 / iprMinGaps 3)*: **5 ventanas IPR** (≥3 FVG del mismo lado en 10 velas) — concentradas en los tramos de impulso direccional (donde el precio deja huecos apilados al avanzar). Confluencia **candidata #49** (probable input de bias más que voto puntual).

### 5.10 Serie de gaps de apertura — NWOG/NDOG/NYMO/ORG + Breakaway `f_detectOpeningGaps` · T30

**Concepto.** Niveles ancla de **apertura** que actúan como soporte/resistencia: **NWOG** (New Week Opening Gap, fin de semana), **NDOG** (New Day Opening Gap), **NYMO** (NY Midnight Open), **ORG** (Opening Range Gap); + **Breakaway Gap** (gap de *ruptura* direccional). Extiende `f_sessionOpens` (§4.2): §4.2 da el *nivel* de apertura; T30 da el *gap* (cierre previo ↔ apertura) como **serie de niveles**.

**Definición cuantificada.** En cada frontera temporal (semana / día del broker / medianoche NY), capturar el par `(close_previo, open_nuevo)`:
- **Nivel ancla** (siempre): el `open_nuevo` (NWOG/NDOG/NYMO según frontera) y el punto medio del gap → líneas S/R. Refina #36 como **serie**. *(En FX 24h el gap diario suele ser ≈0 → el valor es el NIVEL; el gap real aparece en fin de semana = NWOG, o en instrumentos con cierre nocturno — símbolo-agnóstico ADR-001.)*
- **Gap medible** (cuando `|open − close_previo| ≥ gapMin×ATR14`): zona-gap (similar a Vacuum §5.7 pero anclada a la frontera).
- **Breakaway Gap** (`KIND_BAG`): un gap de apertura que **además rompe estructura** (close del nuevo periodo confirma BOS §1.3 en la dirección del gap) → gap de ruptura **direccional** (confluencia propia), distinto del NWOG/NDOG (frontera neutra).

**Parámetros default.**
| Param | Default | Nota |
|---|---|---|
| fronteras | semana / día broker / 00:00 NY | hora local + DST, como §3.4. |
| `gapMin` | **0.5** | × ATR14, para clasificar gap medible (vs nivel puro). |
| `orgMinutes` | **15** | ventana del Opening Range (ORG). |

**Contraejemplo.** Un `open` de día que coincide casi exacto con el `close` previo (gap < 0.5×ATR, típico en FX intradía): NO es gap medible — solo aporta el **nivel** ancla (#36 serie), no una zona-gap ni Breakaway.

**Casos de prueba** *(EURUSD, `eurusd_h1.csv`; agregado a día/semana)*: los gaps diarios intradía son ≈0 (mercado continuo); los **NWOG de fin de semana** sí gapean: domingo 06-07 (−0.00111, ~0.85×ATR) y domingo 05-31 (−0.00078, ~0.72×ATR) → niveles ancla NWOG verificados (coinciden con los Vacuum §5.7 de frontera). Confluencia: refina #36 (serie); Breakaway = **candidata #45**.

### 5.11 Standard Deviation `f_projStdDev` · T36 — herramienta (NO confluencia)

**Concepto.** **Proyección** por desviaciones estándar de un swing/rango para fijar **objetivos** (TP) y zonas de agotamiento. No es una zona detectada ni una confluencia: es una **medición** (insumo de SL/TP), por la regla §0.9 (una herramienta de proyección no suma al score).

**Definición cuantificada.** Dado un rango ancla `[A, B]` (p.ej. la pierna de manipulación / el dealing range §2.3, con `A`=origen, `B`=extremo), proyectar más allá de `B` los múltiplos estándar: `nivel(k) = B + k·(B − A)` para `k ∈ {−1, −2, −2.5, −4}` (signo según dirección). Devuelve niveles de objetivo. **Alimenta `f_computeSLTP` (TP del motor EA), NO el scoring.**

**Parámetros default.**
| Param | Default | Nota |
|---|---|---|
| `stdMultiples` | **−1 / −2 / −2.5 / −4** | múltiplos de proyección (objetivos ICT estándar). |
| ancla | pierna manipulación / dealing range | reusa §2.3 / §4.4. |

**Contraejemplo.** Usarla como "confluencia" que suma al score sería un error de categoría: es proyección de objetivos, no una señal detectada en el gráfico. No entra a §4.8.

**Casos de prueba.** Determinista (fórmula de proyección): sobre el rango impulsivo 06-04→06-08 (A=1.16455, B=1.14997, B−A=−0.01458), los objetivos serían `−1`→1.13539, `−2`→1.12081, etc. No requiere conteo de instancias (es cálculo, no detección). Integración verificada al cablear `f_computeSLTP` (Fase 2/3).

### 5.12 Inside Day `f_detectInsideDay` · T37 — patrón diario

**Concepto.** Un día cuyo rango está **contenido** en el del día previo (`high` menor y `low` mayor) → **compresión** de volatilidad que suele preceder una **expansión**. Contexto, peso bajo.

**Definición cuantificada.** Sobre el snapshot **D1** (MTF, `request.security`, `PINE-PLAN §4`): `high[D] < high[D−1]` **y** `low[D] > low[D−1]` → `KIND_INSIDEDAY`, evento en la barra D1 confirmada (anti-repaint: D1 cerrado). `dir` = neutro (es compresión; la dirección la da la ruptura posterior del rango del día previo). Símbolo-agnóstico.

**Parámetros default.** Ninguno (definición geométrica pura sobre D1).

**Contraejemplo.** Un día que hace un `high` mayor **o** un `low` menor que el día previo (outside/trending day) NO es inside day — rompe la contención. La contención de AMBOS extremos es lo que define la compresión.

**Casos de prueba** *(EURUSD, `eurusd_h1.csv` agregado a día UTC)*: **3 Inside Days** en la ventana (2026-05-31, 06-02, 06-11). Confluencia **candidata #50** (contexto/volatilidad, peso bajo).

### 5.13 SMT Divergence `f_detectSMT` · T38 — ⚠️ requiere ADR de arquitectura

**Concepto.** **Smart Money Technique divergence**: dos símbolos **correlacionados** dejan de moverse en sincronía — uno hace un higher-high (o lower-low) y el otro **no** lo confirma → señal de **manipulación** institucional (uno barrió liquidez, el otro no). Señal de calidad alta.

**Definición cuantificada.** Sobre los **swings** (§1.1) de dos series sincronizadas (el chart + un símbolo correlacionado `smtSymbol`, traído por un 2º `request.security`):
- **SMT bajista:** el chart hace un **higher-high** (HH respecto a su swing previo) pero el correlacionado hace un **lower-high** (no confirma) en el swing equiparable → divergencia bajista (`dir −1`).
- **SMT alcista:** el chart hace un **lower-low** y el correlacionado un **higher-low** (no confirma) → `dir +1`.
- Equiparación por ventana temporal (`smtTol` velas entre los swings comparados). `KIND_SMT`. Función **pura**: recibe las dos secuencias de swings (la del chart + la del correlacionado, obtenida en el consumidor); anti-repaint (swings confirmados).

**Parámetros default.**
| Param | Default | Nota |
|---|---|---|
| `smtSymbol` | (input, por perfil) | par correlacionado — lo fija el ADR (p.ej. EURUSD↔GBPUSD / DXY inverso). |
| `smtTol` | **3** | velas máx. entre los dos swings comparados. |

**Contraejemplo.** Dos símbolos que hacen **ambos** higher-high (se confirman) NO es SMT — la divergencia exige que **uno falle** en confirmar el extremo del otro.

**⚠️ BLOQUEO DE ARQUITECTURA (precede a la implementación):** SMT necesita un **2º `request.security` a otro ticker**. Choca con la doctrina símbolo-agnóstico (ADR-001): ¿qué par correlaciona con cuál? ¿se hardcodea o es input por perfil? ¿coste de performance del 2º security? → **requiere ADR-SMT propio ANTES de codear** (decisión del usuario sobre el mapa de correlaciones y el modelo de input). Regla escrita; **código BLOQUEADO hasta el ADR**. Confluencia **candidata #51** (fuerte). *(No verificable con `eurusd_h1.csv` — un solo símbolo; la verificación de casos se hará con el par correlacionado en la pasada TV, tras el ADR.)*

### 5.14 Macros intradía `f_detectMacro` · T39 — extiende `f_killZone` (§3.4)

**Concepto.** Sub-ventanas de **minutos** dentro de las Kill Zones donde el algoritmo institucional (IPDA) entrega con más probabilidad: los **macros** ICT. Refina #34 (Kill Zone) con sub-ventana; no es confluencia nueva.

**Definición cuantificada.** `f_killZone` (§3.4) se extiende para devolver también **macro activa** si la hora local (NY, con DST automático como §3.4) cae en una ventana macro canónica ICT:
- **London:** 02:33–03:00, 04:03–04:30 (NY time).
- **NY AM:** 08:50–09:10, 09:50–10:10, 10:50–11:10, 11:50–12:10.
- **NY Lunch:** 12:00–13:00 (baja actividad — filtro, no entrada).
- **NY PM:** 13:10–13:40, 15:15–15:45.
Devuelve `macroActiva` (bool) + identificador. Anti-repaint: por reloj (no repinta). Confluencia: **refina #34** (sub-ventana de mayor peso), no suma nueva.

**Parámetros default.** Ventanas canónicas ICT (arriba), en hora NY local+DST. Símbolo-agnóstico (el reloj informa, no veta — ADR-001).

**Contraejemplo.** Una señal **dentro** de la Kill Zone pero **fuera** de toda ventana macro: sigue siendo válida (la KZ ya aporta #34); el macro solo **añade peso** si coincide. No bloquea (ADR-001).

**Casos de prueba** *(EURUSD)*: las ventanas son **horarios canónicos ICT** (no inventados), del mismo tipo que las Kill Zones §3.4 ya validadas. Verificación de coincidencia hora→ventana es determinista (reloj); la calidad de cada macro se calibra en Fase 3. *(M5 disponible 06-10/06-11 permite spot-check de membresía; el peso es Fase 3.)*

### 5.15 RTH vs ETH `f_sessionType` · T40 — extiende `f_killZone` (§3.4)

**Concepto.** **Regular Trading Hours** vs **Extended Trading Hours**: distingue la sesión regular (mayor liquidez/validez) de la extendida (ruido). Relevante a **futuros/índices** (que tienen cierre); símbolo-agnóstico vía perfil (ADR-001). Modula #34 / filtro de calidad.

**Definición cuantificada.** Por **perfil de sesión** (input, como `sessionProfile` §3.4): si la hora local cae en la ventana RTH del instrumento → `RTH`, si no → `ETH`. Ej. índices US: RTH 09:30–16:00 NY. Modula el peso de #34 (señales en RTH = mayor calidad). Anti-repaint: por reloj.

**Parámetros default.**
| Param | Default | Nota |
|---|---|---|
| `rthProfile` | (input por símbolo) | ventana RTH del instrumento. **FX = 24h → no aplica** (RTH≡ETH; el perfil FX lo neutraliza). |

**Contraejemplo.** Aplicar RTH/ETH a **EURUSD** (FX 24h): no hay distinción real → el perfil FX desactiva la modulación (toda hora es "regular"). RTH/ETH solo modula en instrumentos con sesión regular acotada (índices/futuros).

**Casos de prueba.** **No aplica a EURUSD** (24h) — por eso no hay instancias en `eurusd_h1.csv`. Es símbolo-agnóstico para cuando se valide un índice/futuro (Fase 5, par nuevo). Regla definida; verificación con instrumento de sesión acotada.

> **Lote 4 (T38 SMT · T39 macros · T40 RTH/ETH) — definido.** SMT con **BLOQUEO ADR** (código pendiente del ADR-SMT). Macros/RTH-ETH son ventanas de reloj canónicas (no aplican a EURUSD 24h salvo macros).
>
> **✅ §5 GAP ICT (T26–T40) COMPLETO en Fase 0 (reglas).** Las 15 primitivas tienen regla cuantificada + umbrales ATR-relativos verificados contra `eurusd_h1.csv` (donde el dato existe) o marcados como pendientes de pasada TV dedicada (SMT multi-símbolo, RTH/ETH índices). **Ningún código Pine aún** (gate). Falta antes de codear: (1) **ADR-SMT** para T38; (2) confirmar números de confluencia #43–#51 al cablear scoring (Fase 2). **Ruta B** (DOL, IRL/ERL, HRLR/LRLR, IPDA/PDArray) NO está aquí: son moduladores de bias/scoring → Sprint 2.1.
