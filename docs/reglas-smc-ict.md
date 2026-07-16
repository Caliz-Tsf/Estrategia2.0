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

**Definición cuantificada.** Sea el rango `[L, H]` entre el strong low `L` y strong high `H` vigentes (ver "Strong / weak" abajo):
- `eq = (H + L) / 2` (nivel 50%).
- **Discount:** precio `< eq` (mitad inferior) → favorece **long**.
- **Premium:** precio `> eq` (mitad superior) → favorece **short**.
- **Equilibrium (banda):** precio dentro de `[45%, 55%]` del rango → zona neutral. Confluencia #31: si el precio está en equilibrium, **resta** 50% del peso (no hay ventaja de localización).

#### 2.3.1 Strong / weak — cuantificación *(S133; antes era un término primitivo)*

**Strong es RELACIONAL, no una propiedad local del nivel.** No lo determinan ni los toques, ni la amplitud, ni la antigüedad (las tres vías medidas y **refutadas** en S131/S132). Lo determina **lo que hizo la pierna que nació en él**:

- **Strong low** := el mínimo de la pierna cuya subida posterior **rompió estructura** (BOS/CHoCH alcista de la escala del TF). Queda *protegido/defendido*.
- **Strong high** := simétrico, con eventos **bajistas**.
- Se fijan **en la barra de la ruptura**, con `min/max` de barras pasadas → anti-repaint `[D-PINE-03]`.

**Strong / weak depende del BIAS, nunca del lado:**

| bias estructural vigente | lado STRONG (defendido) | lado WEAK (liquidez pendiente) |
|---|---|---|
| **BAJISTA** | high | low |
| **ALCISTA** | low | high |

> **Corolario (S133).** Que el rango "camine hacia el precio" **en el lado weak es CORRECTO**: un weak low es liquidez y su destino es ser barrido. En una divisa bajista el discount pegado al precio **no es un bug**. El defecto es que el lado **strong** también camine.

**Símbolo-agnóstico `[ADR-001]`:** anclar al bias — no a un lado — es simétrico por construcción. En un símbolo de tendencia secular alcista el latch se va solo al low. **Nunca se hardcodea un lado ni un símbolo.**

#### 2.3.2 El dealing range: el **2.º** extremo estructural *(S133)*

Por cada TF, sobre los strong lows/highs **de su propia escala**, acumulados en toda su historia:

| Nivel | Definición | Uso |
|---|---|---|
| `histLow` / `histHigh` | el strong low **más bajo** / el strong high **más alto** | **Se marcan aparte. NO entran en el dealing range.** Son el extremo histórico del símbolo. |
| `pdLow` / `pdHigh` | el **2.º** más bajo / el **2.º** más alto | **Son el dealing range** `[L, H]`. |

**Por qué el 2.º y no el 1.º:** el extremo histórico es el arranque del feed (o un evento único de hace décadas) — un rango anclado ahí es cierto pero **no operable**. El 2.º extremo da un rango *"no tan lejos"* y sigue siendo **estructural**, no aritmético.

**Fallback en cascada** (garantiza el invariante `pct ∈ [0,1]`; simétrico arriba):

1. `close >= pdLow` → suelo = `pdLow` *(caso normal)*
2. `histLow <= close < pdLow` → suelo = `histLow` *(franja histórica: el rango **se estira**)*
3. `close < histLow` → suelo = el trailing extreme *(el precio rompió el histórico: expande hasta que se confirme el pivote nuevo, que pasa a ser el nuevo `histLow` y desplaza al antiguo a `pdLow`)*

**Anidamiento MTF gratis:** cada TF usa la escala de sus propios pivotes ⇒ el 2.º extremo de M5 está más cerca del precio que el de H1, y el de H1 más que el de D1. **La cascada D1 ⊃ H1 ⊃ M5 sale sola, sin código por-TF ni parámetro de escalado.**

> ## ⚠️ LA VENTANA ES OBLIGATORIA — corregido por 3.ª vez (S133, medido EN VIVO tras implementar)
>
> **MEDIDO en el indicador real:** la columna **M5 del panel** da **Discount 21%** con el chart en H1 y
> **Premium 90%** con el chart en M5. **El mismo TF, dos veredictos**, según dónde estés mirando. (El 90%
> es el correcto: coincide con el probe del gate, `pct`=0.929.)
>
> **Causa:** `request.security("5", …)` desde un chart H1 recibe **mucha más historia M5** que un chart M5
> nativo (5253 barras). Más historia ⇒ más strong acumulados ⇒ **el 2.º extremo se va más lejos** ⇒ el
> rango se ensancha y el veredicto cambia.
>
> **Consecuencia doctrinal:** sin ventana, el 2.º extremo depende de **cuántas barras sirva el
> bróker/TV**, no de la estructura ⇒ **el resultado no es determinista** y viola la regla dura #1
> (determinismo) y el espíritu de ADR-001. **La ventana no es un remedio del fósil: es lo que hace que
> "el M5" sea M5.** Lo de abajo queda como registro de las dos correcciones previas; **la ventana
> declarada por TF es obligatoria** y su calibración está **pendiente**.

**La VENTANA `pdWindow`** *(historial de correcciones en S133: v1 "no hay parámetro de escala" (**falso**); v2 "obligatoria por el fósil" (**falso: no era esa la razón**); v3 "opcional" (**falso**, ver el aviso de arriba); **v4: obligatoria, por determinismo**)*.

**MEDIDO — la regla base, SIN ventana, ya cumple todo** (EURUSD, S133):

| TF | rango = [2.º strong low, 2.º strong high] | `pct` | veredicto |
|---|---|---|---|
| D1 | [0.95360, 1.51441] | 0.344 | **DISCOUNT** |
| H1 | [1.02105, 1.19188] | 0.733 | **PREMIUM** |
| M5 | [1.13335, 1.14730] | 0.929 | **PREMIUM extremo** |

**Anida** (D1 ⊃ H1 ⊃ M5) y **rota** (3 veredictos simultáneos distintos), **con cero parámetros**. La escala la fija el TF; no hace falta declarar nada.

⚠️ **Contraejemplo medido — la ventana corta ROMPE la regla:** con `pdWindow` pequeño en H1/M5 solo cae **1** strong dentro ⇒ **no existe 2.º extremo** ⇒ la regla se queda **sin candidatos** (`pdLow`=`na`). Es el mismo modo de fallo que `minTouches`=2 (S131). **Una ventana nunca puede ser menor que la que contiene ≥2 strong del lado.**

**Cuándo SÍ declararla (único caso):** símbolos de **tendencia secular fuerte**, donde el 2.º extremo del lado que el precio nunca vuelve a visitar **se fosiliza** en el arranque del feed:

**Medido, NAS100USD D1 vs H1:**

| | D1 (feed de ~24 años) | H1 (feed de ~1.5 años) |
|---|---|---|
| `pdLow` | **1021.1** *(de 2001)* | 19013 *(reciente)* |
| rango | 29752 pts | 11709 pts |
| `pct` | **0.958 — clavado, no rota** | 0.898 |

**El 2.º extremo del lado que el precio nunca vuelve a visitar se fosiliza en el arranque del feed** ⇒ ese rango deja de ser operable. **H1 no lo sufre solo porque su feed es corto** — la ventana ya actuaba de hecho, sin declararse. **Remedio: declarar `pdWindow` SOLO en el TF afectado** (no en los tres, y no por defecto). Alternativa legítima: **no hacer nada** — un D1 que dice "premium extremo" en un símbolo en máximos de 24 años **está diciendo la verdad**, y el dealing range operable es el de H1/M5.

> **Nota histórica.** `i_pdSwingLen`=1000 (S130) acertaba el rango D1 de EURUSD **por este mismo mecanismo, sin saberlo**: no era una escala de pivote, actuaba como ventana de facto. Ver `decisiones-pd-rango.md` nota S133(b).

**Contraejemplo `[cuantificado]`.** Reanclar el rango en **cualquier** swing confirmado (sin exigir que haya roto estructura) hace que el lado strong camine hacia el precio: **medido en S133**, el techo así calculado queda a **9-13×ATR** del strong high real. Tampoco vale tomar **el último** strong high en vez del 2.º más alto: cada evento lo re-fija más abajo → mismo defecto (medido, 4 configuraciones).

**Parámetros default.**
| Param | Default | Nota |
|---|---|---|
| `eqBand` | **45–55%** | ancho de la banda de equilibrium. |
| rango | `[pdLow, pdHigh]` = **2.º** strong low / **2.º** strong high de la escala del TF | se actualiza **solo** con un nuevo strong high/low (§2.3.1), **no** con pivotes. |
| `pdWindow` | **desactivada** (toda la historia del TF) | **OPCIONAL y por-TF.** Solo para el fósil en símbolos seculares. **Nunca menor que la ventana que contiene ≥2 strong del lado** (si no, la regla se queda sin candidatos). |

**Contraejemplo.** Comprar en **premium** (precio en el 80% del rango) porque "hay un OB alcista" es operar contra la localización — el OB en premium tiene mucha menor probabilidad. Premium/Discount es el filtro que evita entradas caras.

> ⚠️ **Los casos de prueba de abajo NO son un oráculo independiente — quedan como REGISTRO HISTÓRICO de la Opción A** *(S133)*. Se generaron **desde la implementación ya escrita** (`decisiones-pd-rango.md`, tabla de validación "al 5.º decimal") ⇒ **validan el código contra sí mismo**. No pueden usarse para validar §2.3.1/§2.3.2. **Se regeneran** tras implementar el 2.º extremo estructural.

**Casos de prueba** *(⚠️ NO-ORÁCULO — registro de la Opción A. EURUSD, TV MCP 2026-06-11; H1, rango dominante strong_high 1.16859 / strong_low 1.14997, eq 1.15928)*:
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

**⚠️ BLOQUEO DE ARQUITECTURA (precede a la implementación):** SMT necesita un **2º `request.security` a otro ticker**. Choca con la doctrina símbolo-agnóstico (ADR-001): ¿qué par correlaciona con cuál? ¿se hardcodea o es input por perfil? ¿coste de performance del 2º security? → requería ADR-SMT propio. **ADR-011 ACEPTADO (2026-06-21)** — `docs/adrs/ADR-011-smt-simbolo-correlacionado.md`: **default EURUSD↔GBPUSD, correlación POSITIVA** (preferencia por pares positivos; `i_smtInverse` queda como capacidad, no default); par + signo como inputs por perfil (honra ADR-001); transporte vía 2º `request.security` aplanado (patrón ADR-009); `f_detectSMT` pura. **Desbloqueado para codear** en su turno de Sprint 1.6 (tras Fase 0 de reglas + validación Tier 2). Confluencia **candidata #51** (fuerte). *(No verificable con `eurusd_h1.csv` — un solo símbolo; la verificación de casos se hará con el par correlacionado en la pasada TV, tras el ADR.)*

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

---

## 5B. GRADIENT LEVELS — grading por quadrants/eighths (T41–T44)

> Familia derivada del ESQUELETO-P4 (S079). **T41** = herramienta núcleo (grid del rango). **T42** = confluencia exponencial candidata **#52** (multiplicador, requiere **ADR-013** antes del wiring en Fase 2). **T43** = refina el FVG (§2.2) con flag `gradedFvg` (sin # nueva). **T44** = grading de mecha (opcional, diferible). Todo umbral numérico CONGELADO hasta calibración Fase 3 (ADR-002).

### 5.16 Gradient Levels — grading del rango `f_computeGradientLevels` · T41 — herramienta (NO confluencia)

**Concepto.** Toda referencia de rango se trata como una **escala graduada**, no como una línea suelta: se mide un rango-fuente y se divide en `low (0)` / `lower-quadrant (0.25)` / `equilibrium-CE (0.5)` / `upper-quadrant (0.75)` / `high (1.0)`, y opcionalmente en **eighths** (0.125/0.375/0.625/0.875). Generaliza `f_premiumDiscount` (§2.3) de 2 zonas a un grid de N puntos. Doctrina: *"we're just measuring a range and dividing it into mid range, upper quadrant, lower quadrant and high and the low"* (`madre-2026.md:90-94`). No suma al score por sí sola (regla §0.9, igual que Standard Deviation §5.11): es el **insumo** de T42 (confluencia exponencial) y T43 (FVG válido).

**Definición cuantificada.** Dado el rango-fuente `[bottom, top]` (con `top > bottom`), `nivel(f) = bottom + f·(top − bottom)` para cada fracción `f`:
- **Quadrants (SIEMPRE):** `f ∈ {0, 0.25, 0.5, 0.75, 1}`.
- **Eighths (si `gradEighths=true`):** además `f ∈ {0.125, 0.375, 0.625, 0.875}`. Sixteenths **fuera de alcance** (no se calculan).
- El `0.5` es idéntico al `eq` de §2.3; el grid es una extensión estricta del dealing range (no lo reemplaza).

**Política de rango-fuente (determinista, en orden de prioridad):**
1. **P1 — Dealing range Premium/Discount (§2.3, `f_premiumDiscount`).** Rango-fuente **por defecto** siempre que haya un dealing range vigente (strong high ↔ strong low, escala `pdSwingLen=50`). Ya es determinista, símbolo-agnóstico y anti-repaint.
2. **P2 — Suspension block diario (Fib highest-high→low del día del broker, `madre-2026.md:135,:207`).** Se **construye** cuando el P/D de P1 es "stale" (swing origen a más de `gradStaleBars` velas) o gana el desempate por cuerpos. `top=highest(high, díaBroker)`, `bottom=lowest(low, díaBroker)`, confirmado en el cierre D1 (misma frontera que Opening Gaps §5.10).
3. **P3 — Gaps de apertura (§5.10, `f_detectOpeningGaps`).** Cada gap `(close_previo, open_nuevo)` es un mini-rango graduable. Corre en **paralelo** (no reemplaza a P1/P2 como rango principal); alimenta el filtro FVG-válido (T43) cuando el FVG cae cerca de un gap reciente.

**Desempate cuerpos-vs-nivel (`madre-2026.md:408,:440,:479`).** Cuando dos rangos-fuente candidatos producen grids con niveles distintos cerca del precio, gana el grid cuyos niveles los **cuerpos** (open/close, no mechas) de las últimas `gradBodyLookback` velas confirmadas respetan más (más cierres dentro de `gradTol×ATR14` de algún nivel). Determinista y auditable (cuenta, no interpreta) → `f_bodyRespectsLevel`.

**Persistencia.** Cada rango-fuente que se fija genera un grid **nuevo**; los grids de los últimos `gradPersistDays` se mantienen como referencia (ghost); los más viejos se descartan (mecanismo de cuota como Present-mode, para no reventar el presupuesto de ~500 objetos).

**Mitigación / ciclo de vida.** No es P1–P4 puro: es un **grid persistente recomputado en frontera** (más cercano a la "serie de niveles globales" de Opening Gaps §5.10 que a una zona con 4 estados). Un grid nuevo no invalida al anterior; el anterior pasa a `ageDays++` y se dibuja ghost hasta `gradPersistDays`, luego se descarta. El grid se **reemplaza** cuando su rango-fuente cambia (nuevo swing dominante / nuevo día / nuevo gap), **no** por precio cruzándolo (no es un nivel que se "consuma").

**Parámetros default.**
| Param | Default | Nota |
|---|---|---|
| `gradEighths` | **true** | incluir 0.125/0.375/0.625/0.875 (la doctrina los trata como la escala real de trabajo); sixteenths fuera de alcance. |
| `gradPersistDays` | **5** | doctrina `madre-2026.md:93,:322`; tope real sujeto a presupuesto de objetos. |
| `gradStaleBars` | **150** | = 3×`pdSwingLen`; velas desde el swing origen del P/D tras las que se evalúa el candidato P2 (suspension diario). |
| `gradBodyLookback` | **5** | velas para `f_bodyRespectsLevel` (desempate). |
| `gradTol` | **0.12** | × ATR14 (entre `eqThreshold`=0.1 y holgura media); "toca/está sobre un gradient level" (compartido con T42/T43). |

**Confirmación / anti-repaint.** El grid se fija SOLO cuando su rango-fuente confirma (`barstate.isconfirmed`: swing dominante confirmado / cierre D1 / gap de apertura confirmado en frontera) — nunca intra-vela. Heredado de fuentes ya anti-repaint (§2.3/§5.10).

**Contraejemplo.** Calcular el grid sobre un rango-fuente **no confirmado** (p.ej. un swing candidato sin BOS de confirmación, o el rango intradía en formación) → grid discrecional/repintable, **PROHIBIDO**. Tampoco es gradient level un **número redondo** arbitrario (1.14000, 1.15000…): el grading exige un rango-fuente real (dealing range / suspension / gap), no la retícula del eje de precio.

**Casos de prueba** *(EURUSD, TV MCP 2026-07-01; OANDA:EURUSD H1, dealing range vigente leído del panel T14 / etiquetas P/D del indicador)*:
- ✓ **Grid H1.** Dealing range `[bottom=1.13246 (Discount), top=1.16221 (Premium)]`, span 0.02975. Quadrants: `0→1.13246 · 0.25→1.13990 · 0.5→1.14733 · 0.75→1.15477 · 1→1.16221`. El `0.5=1.14733` coincide **exacto** con la etiqueta EQ del indicador (`(1.16221+1.13246)/2=1.147335`). Precio 1.13851 → pct 20.3% (lower-quadrant/discount), coincide con el panel "Discount 20%".
- ✓ **Eighth que atrae al precio (doctrina "runs to the level").** Eighth `0.125 = 1.13246+0.125·0.02975 = 1.13618`. La vela H1 de mayor volumen del tramo (21 346, institucional) hizo **low exacto 1.13618** y revirtió al alza (cerró 1.13956) → el precio corrió al gradient level y rebotó. Además el OB cercano `[1.13542, 1.13628]` **contiene** 1.13618 y el FVG `[1.13628, 1.13686]` se apoya en su borde → confluencia de PD arrays sobre el mismo eighth (insumo directo de T42/T43).
- ✓ **Grids anidados MTF (niveles globales).** Dealing range D1 `[1.13246, 1.20831]` (etiquetas "D1: Discount/Premium"), span 0.07585, quadrants `0.25→1.15142 · 0.5→1.17039 · 0.75→1.18935`. Comparte el extremo discount `1.13246` con el grid H1 → los gradient levels de un rango-fuente HTF son **globales** (mismos en todo TF), no se recomputan por TF (§6.3.36).
- ✗ **Contraejemplo (número redondo ≠ gradient level).** Los niveles 1.13000/1.14000/1.15000 de la retícula de precio NO son gradient levels aunque el precio los toque: no derivan de un rango-fuente medido → no disparan T42 ni validan un FVG (T43).
- ✓ **P2 — Suspension diario (rango-fuente D1, anti-repaint).** Último día D1 **confirmado** (OANDA:EURUSD, TV MCP 2026-07-01, ts 1782853200 ≈ 2026-06-30): `high=1.14233`, `low=1.13618`, span 0.00615. Grid: `0→1.13618 · 0.25→1.13772 · 0.5→1.13926 (CE) · 0.75→1.14079 · 1→1.14233`. El día en formación (ts 1782939600, vol 11826 parcial) **se excluye** (se usa `highest(high)/lowest(low)` del día ya cerrado, no del vigente). Confluencia notable: la `low=1.13618` del suspension = **exactamente** el eighth 0.125 del dealing range H1 (caso 2 arriba) → los cuerpos institucionales que respetaron 1.13618 alimentan el desempate `f_bodyRespectsLevel` a favor de este rango-fuente.
- ✓ **P3 — Opening gap (mini-rango en paralelo).** Único gap real del tramo = fin de semana (Vie ts 1782421200 `close=1.13850` → Lun ts 1782680400 `open=1.13897`), mini-rango `[1.13850, 1.13897]`, span 0.00047 (4.7 pips), CE `0.5=1.138735`. Corre en paralelo (no reemplaza a P1/P2): un FVG cuyo CE caiga dentro de `gradTol×ATR14` de un nivel de este mini-grid → `gradedFvg=true` por P3 aunque esté lejos del dealing range grande (T43).
- ✗ **Contraejemplo P3 (gap no-measurable en FX).** Los gaps diarios intra-semana `close→open` de EURUSD son ~0.00001–0.00002 (mercado cuasi-continuo intradía): por debajo de `gapMin×ATR` → **NO** generan grid P3 (solo el gap de fin de semana / NWOG es un rango-fuente real). Evita graduar ruido de 0.1–0.2 pips.

### 5.17 Confluencia exponencial nivel∩quadrant `f_gradientConfluenceBonus` · T42 — candidata #52 (multiplicador, requiere ADR-013)

**Concepto.** La probabilidad de que el precio corra hacia un nivel (REH/REL, FVG, pool) aumenta **exponencialmente** si ese nivel coincide con un **quadrant** del rango mayor (`madre-2026.md:92,:287`, verbatim *"the probability of it running to them increases exponentially if it's part of or around a quadrant level of the entirety of the range"*). NO es un voto plano: es un **multiplicador** sobre el score direccional ya calculado.

**Definición cuantificada.** `⏳ forma exacta y tope a calibrar Fase 3 (ADR-002)` — mecanismo fijado:
```
scoreDir_raw   = Σ(peso_i × activa_i)                        // arquitectura actual §4.8, SIN cambios
gradientBonus  = f_gradientConfluenceBonus(nSobreQuadrant, gradMultMax, k)   // 0 .. (gradMultMax−1)
scoreDir_final = scoreDir_raw × (1 + gradientBonus)
```
- `nSobreQuadrant` = nº de confluencias de zona YA activas en `scoreDir_raw` (OB #17/#19, FVG #18/#20, pool #9) cuyo nivel cae dentro de `gradTol×ATR14` de un punto **isQuadrant=true** (0/0.25/0.5/0.75/1). Los **eighths NO** disparan el bonus (la doctrina lo liga a "quadrant level de la entereza del rango").
- `f_gradientConfluenceBonus(n, gradMultMax, k) = (gradMultMax − 1)·(1 − e^(−k·n))` — **creciente saturante**: `n=0 → bonus=0 → multiplicador=1` (neutro); `n→∞ → multiplicador→gradMultMax` (tope). `k` (velocidad de saturación) y `gradMultMax` (tope) se calibran en Fase 3.
- **Requiere ADR-013** (aceptado, S080) antes del wiring real en `f_scoreConfluences` (Fase 2, F2-T01): cambia el contrato de puramente aditivo a aditivo+multiplicativo. En Fase 1 T42 solo entrega la **función pura** (ya en el CORE) + esta spec; **cero wiring al scoring**.

**Parámetros default.**
| Param | Default | Nota |
|---|---|---|
| `gradTol` | (reusa T41) | mismo input, no duplicar tolerancia. |
| `gradMultMax` | `⏳` | tope del multiplicador; calibración Fase 3 (ADR-002). |
| `k` | `⏳` | pendiente de saturación; Fase 3. |

**Confirmación / anti-repaint.** Se evalúa en `barstate.isconfirmed`, sobre el `scoreDir_raw` ya calculado de esa vela.

**Contraejemplo.** Un nivel que coincide con un **eighth** (0.125/0.375/0.625/0.875) pero NO con un quadrant → NO dispara el bonus exponencial (sí puede validar un FVG en T43, que admite cualquier punto del grid, pero eso no es el multiplicador de T42).

**Casos de prueba** *(EURUSD)*: la confluencia OB+FVG sobre el eighth 1.13618 (§5.16 caso 2) coincide con un **eighth**, no un quadrant → **NO** dispara T42 (sí T43). Un caso que SÍ dispararía: confluencia de zona sobre el `0.25=1.13990` (quadrant). `⏳ conteo de instancias sobre quadrant pendiente de pasada dedicada TV + calibración k/gradMultMax Fase 3`.

### 5.18 FVG válido = toca gradient level (refina `f_detectFVG` §2.2) `f_nearGradientLevel` · T43

**Concepto.** No todos los FVG son iguales: los de alta probabilidad se forman **tocando un gradient level**; los que no, no son "FVG válidos" (`madre-2026.md:101-103,:209`, verbatim *"high probability FVGs form in close proximity and are touching one of the gradient levels… if it's not doing these things it's not a valid fair value gap"*). Refina #18/#20 con un **flag de calidad** (`gradedFvg`), sin número de confluencia nuevo (patrón `trueFvg` §5.1 / `propulsion` §5.8).

**Definición cuantificada.** Al confirmarse un FVG (`f_detectFVG`, §2.2):
- Evaluar `f_nearGradientLevel(fvg.ce, levels, gradTol×ATR14)` contra el grid T41 más relevante (preferencia: suspension diario / gap de apertura sobre el dealing range grande, §5.16 P2/P3).
- Si `true` → `gradedFvg = true` en `SMC_Zone` (nuevo campo) → eleva `strength` en la capa de discriminación (§6, NO suma # nueva). Admite quadrant **o** eighth (cualquier punto del grid).
- Si `false` → el FVG sigue existiendo (no se descarta), pero sin el bono de calidad.
- Guard con T44: si hay una mecha adyacente a **0 velas** del FVG → preferir graduar la mecha (§5.19), no el FVG.

**Parámetros default.** `gradTol` = reusa T41/T42 (mismo input).

**Confirmación / anti-repaint.** Mismo instante en que el FVG se confirma (`barstate.isconfirmed`, §2.2); el flag no reintroduce repaint.

**Contraejemplo.** Un FVG "suelto" cuyo CE cae lejos de todo nivel del grid (el "fake-ICT FVG" que cita la doctrina) → detectado igual por `f_detectFVG`, pero `gradedFvg=false`, `strength` baja.

**Casos de prueba** *(EURUSD, TV MCP 2026-07-01)*: ✓ FVG H1 `[1.13628, 1.13686]`, CE = `(1.13628+1.13686)/2 = 1.13657`; distancia al eighth 0.125 (1.13618) = 0.00039 ≈ 0.22×ATR14 (ATR≈0.0018) → con `gradTol=0.12` queda **fuera** por poco (borde), pero su borde inferior 1.13628 sí toca el eighth → caso límite útil para calibrar `gradTol`. ✓ OB `[1.13542, 1.13628]` contiene el eighth 1.13618 (graded). ✗ Contraejemplo: `⏳ FVG lejos de todo nivel — pasada dedicada TV`.

### 5.19 [OPCIONAL — diferible] Grading de mecha REH/REL `f_gradeWick` · T44 — herramienta (NO confluencia)

**Concepto.** El anchor de un REH/REL es la vela más a la izquierda del swing extremo; si tiene mecha, se gradúa la mecha (LQ/CE/UQ) igual que un rango — *"we grade those because they're gaps"* (`madre-2026.md:96-99,:183`). El precio a menudo entra solo a un quadrant de la mecha y rechaza (parcial obligatorio LQ↔CE); si ni alcanza el CE → señal de debilidad/reversión. La mecha se gradúa **premium** si está sobre el precio actual, **discount** si por debajo (`madre-2026.md:116`). Regla de separación (`madre-2026.md:263`): si un FVG está a **0 velas** de una mecha → graduar la mecha, no el FVG; si **≥1 vela** → coexisten como PD arrays independientes.

**Definición cuantificada.** `⏳ a cuantificar [impl]`
- Anchor = vela izquierda del swing extremo (`f_detectSwings`, §1.1) — ya determinista.
- `[top, bottom]` de la mecha = `[high, max(open,close)]` (mecha superior) o `[min(open,close), low]` (inferior) según lado → reusa `f_computeGradientLevels` sobre ese rango pequeño.
- Separación FVG-vs-mecha: `|barIdx(FVG) − barIdx(mecha)| == 0` → preferir mecha; `≥1` → ambos coexisten.

**Parámetros default.** Reusa `gradEighths`/`gradTol` de T41/T42 (sin parámetros propios).

**Confirmación / anti-repaint.** El swing extremo debe estar confirmado (criterio `f_detectSwings`) antes de graduar su mecha.

**Contraejemplo.** Graduar la mecha de un swing **no confirmado** (candidato que aún puede cambiar) → discrecional, prohibido.

**Casos de prueba** *(EURUSD)*: `⏳PENDIENTE-TVMCP` (pasada dedicada tras cerrar T41–T43). **Nota de prioridad:** confirmar con usuario si T44 entra en el sprint de T41–T43 o queda en backlog explícito.

---

## 6. CAPA DE CALIDAD / DISCRIMINACIÓN (graduada) — *variante · fuerza · invalidación · visual*

> **Estado: POBLADO (Sesion-056).** Esqueleto creado en S054; 4 slots §6.2.2–6.2.5 rellenados (S055/056); **§6.3 poblado con los ~35 conceptos restantes (S056)**. Añade una capa **graduada** sobre las §1–§5 (que solo *detectan*). NO modifica ninguna definición ni umbral congelado de §0–§5 — es **aditiva**. Pendiente del set: implementar el tag `strength` + jerarquía visual en Pine (HANDOFF §5–§6) y ejecutar la verificación graduada (F1-GATE ampliado). Mapea a la columna vertebral **Detectar → Graduar → Contextualizar → Decidir** (ver [`METODOLOGIA-VERIFICACION-VISUAL.md`](METODOLOGIA-VERIFICACION-VISUAL.md)).
>
> **Decisión Freddy (HÍBRIDA):** Pine expone un **tag de fuerza barato por marca** reusando primitivos que el CORE ya calcula; el peso/grading completo vive aguas abajo (scoring + cadena ADR-012). Se marca todo, cada marca lleva su `strength`.
>
> **Cómo se rellena (cualquier IA):** cada concepto de §1–§5 recibe un sub-bloque con la **plantilla §6.0**, citando **solo** primitivos del **inventario §6.1**. Aquí (§6.2) viven los **ejemplos trabajados** de referencia (1 completo + 4 slots). El resto de los 40+ se rellenan concepto a concepto siguiendo el HANDOFF ([`HANDOFF-OPUS-ULTRACODE-discriminacion-visual.md`](planes/HANDOFF-OPUS-ULTRACODE-discriminacion-visual.md) §8 checklist). Los `strength` y pesos son **candidatos CONGELADOS por defecto hasta calibración Fase 3** (ADR-002), igual que todos los umbrales.

### 6.0 Plantilla del sub-bloque por concepto (canónica)

```
**Variante correcta / desempate.** Cuando hay N candidatos, cuál es EL relevante (regla DETERMINISTA).
   Qué descarta y por qué (citables). [cubre el FALLO #1]
**Fuerza (0–1).** Fórmula con primitivos de §6.1: cuerpo%, ×ATR, ¿con displacement?, ¿barrió liquidez (sweep)?,
   distancia al nivel (×ATR), ¿mitigado?, edad/frescura, alineación con bias. Define el tag `strength` que Pine
   expone (alta/media/baja o número 0–1). [cubre el FALLO #2]
**Invalidación externa.** Qué contexto lo anula aunque la regla se cumpla, y DÓNDE se chequea
   (Pine `state` / scoring / cadena ADR-012 Q1–Q7). NO se hardcodea "no marcar". [cubre el FALLO #3]
**Visual (jerarquía).** Cómo se rinde según fuerza/relevancia → Primario (render completo) / Secundario
   (atenuado/pequeño) / Terciario (oculto o colapsado al panel T14). Mapea a su `i_show*` / `GRP_*`.
**MTF (si transferible).** ¿Baja a TF menores? con qué cap 0–10; cae en mismo `bar_time`/nivel que el origen HTF.
```

### 6.1 Inventario de primitivos de fuerza (citar SOLO de aquí — no inventar)

Todo lo que el CORE ya calcula hoy y sirve para componer `strength`. Si un concepto necesita un primitivo que no está aquí, el HANDOFF pide **proponer el cálculo** como indicación (no rellenarlo a ciegas).

| Primitivo | Fuente en el código / § | Mide |
|---|---|---|
| **cuerpo%** | `f_detectDisplacement` (§4.1) | convicción de la vela (cuerpo / rango) |
| **rango ×ATR** | ATR(14) / ATR(200) (§0) | tamaño relativo de la vela/gap |
| **displacement** | `f_detectDisplacement` (§4.1: ≥1.5×ATR ∧ cuerpo≥70%) | impulso institucional de la pierna |
| **mitigado / state** | `f_updateZoneMitigation` · `SMC_Zone.state` 0/1/2/3 (§2.1) | frescura: activa/parcial/mitigada/invalidada |
| **sweep / grab** | `f_detectSweep` (§3.2) · `f_detectGrab` (§3.3) | ¿barrió liquidez antes de la marca? |
| **distancia al nivel ×ATR** | precio actual vs nivel (§0) | cercanía/inmediatez |
| **edad/frescura** | `barTime` de la marca vs barra actual | decaimiento histórico |
| **alineación con bias** | bias estructural (§"Modelo de bias", P/D §2.3) | ¿a favor del sesgo del TF? |
| **flags de refinamiento** | `SMC_Zone.trueFvg` (T26), `.propulsion` (T34) | calidad institucional ya marcada |
| **cap / cercanía MTF** | `f_nearestN` / `f_nearestNPools` (ADR-010) | presupuesto de tinta top-N |

### 6.2 Ejemplos trabajados (1 completo + 4 slots)

> Cubren los 3 tipos de fallo. El OB está **completo** como calibración de profundidad/tono; los otros 4 son **slots** con el fallo objetivo, los primitivos y el caso PLAN-049 ya fijados — listos para rellenar.

#### 6.2.1 Order Block (§2.1) — EJEMPLO COMPLETO *(cubre fallo #1 variante + #2 fuerza)*

**Variante correcta / desempate.** En una pierna que rompe estructura puede haber **N velas contrarias** candidatas a OB. EL relevante = la **última vela contraria** (la más cercana al origen del impulso/BOS) que cumple las dos condiciones de §2.1: (i) su pierna contiene ≥1 vela de **alta volatilidad** (`(high−low) ≥ 2× volMeasure`) y (ii) **no está mitigada** (`state < 2`). **Empate** entre dos igual de cercanas → gana la de mayor rango ×ATR. **Descarta** (citable): las velas contrarias anteriores de la misma pierna, y cualquier OB con `state ≥ 2` (mitigado) o `state = 3` (invalidado → es Breaker §2.6, no OB).

**Fuerza (0–1).** Combinación normalizada de: `rango_vela_OB ×ATR` (mayor = más fuerte) · `displacement` de la pierna que rompió (§4.1, binario que sube la fuerza) · `frescura` (`state`: activa=1, parcial=0.5, mitigada=0) · `¿sweep previo?` (§3.2, sube la fuerza: el OB que nace tras barrer liquidez es más fiable). Quantización sugerida: **alta** (displacement ∧ activa ∧ sweep), **media** (displacement ∨ sweep, activa), **baja** (sin displacement, rango normal). Tag expuesto = `SMC_Zone.strength`.

**Invalidación externa.** Aunque sea OB válido: (1) **OB en premium** cuando se busca long (o en discount para short) → opera contra localización (§2.3) — **se marca**, lo degrada el scoring (#31 P/D). (2) **borde protector cerrado a través** (`state = 3`) → la tesis falló, deja de ser OB (candidato Breaker). DÓNDE: localización = scoring; `state=3` = Pine; secuencia "1er toque débil vs 2º válido" = cadena ADR-012 **Q4** (¿barrieron a los tempranos?).

**Visual (jerarquía).** **Primario:** OB activo, alta `strength`, cercano y alineado al bias → caja sólida + etiqueta. **Secundario:** parcial/lejano o `strength` media → caja atenuada, etiqueta corta. **Terciario:** mitigado total → oculto o colapsado al panel T14; invalidado → se dibuja como Breaker, no como OB. Toggle `i_showOB` / `GRP_*` zonas.

**MTF.** Transferible (cap `i_mtfCapOB`, 0–10). Caja anclada `xloc.bar_time`; cae en la misma vela/nivel que el OB nativo del TF alto (ADR-010). *Casos de verificación (de §2.1):* OB bajista 06-01 12:00 [1.16452, 1.16506]; OB bajista 06-05 11:00 [1.16345, 1.16420] (pierna −5.27×ATR → strength alta); OB alcista 06-08 08:00 [1.15079, 1.15235].

#### 6.2.2 FVG / variantes (§2.2 · True FVG §5.1 · IFVG §5.2) — SLOT *(fallo #1 variante)*

> **Objetivo del slot:** desempate **cuál de FVG / True FVG / IFVG** es el relevante. Primitivos: tamaño ×ATR (§2.2), displacement de la **vela media** (`trueFvg` flag, §5.1), `state` (invalidado → IFVG §5.2). Caso PLAN-049: True FVG H1 (etiqueta "T.FVG", 10/34 en H1); IFVG (27 FVG invalidados). Toggle `i_showFVG`/`i_showIFVG`.

- **Variante correcta / desempate.** Tres estados mutuamente excluyentes de la **misma coordenada de gap**: (1) **True FVG** (§5.1) = la vela media es displacement (`rango ≥ 1.5×ATR ∧ cuerpo ≥ 70%`) → variante de mayor calidad; (2) **FVG normal** (§2.2) = gap válido (`≥ 0.25×ATR`) sin displacement en la media; (3) **IFVG** (§5.2) = un FVG que **cerró a través** de su borde protector (`state = ZS_INVALID`) → invierte `dir` y rol. EL relevante entre los **vivos** = el de mayor `strength` (abajo), más cercano al precio y alineado al bias; a igualdad de cercanía **True FVG > FVG normal** (flag `trueFvg`). **Descarta** (citable): micro-gaps `< 0.25×ATR` (§2.2 contraejemplo, ruido); y **no** sumar el FVG original muerto junto a su IFVG (§5.2: 1 sola confluencia — `[FIX P-05]`).
- **Fuerza (0–1).** `tamaño_gap ×ATR` (mayor = más fuerte) · `trueFvg` (displacement de la vela media, sube la fuerza) · `state` (activa=1 / parcial CE no tocado=0.7 / mitigada CE tocado=0.3) · `¿sweep previo?` (§3.2). Quant: **alta** (trueFvg ∧ activa ∧ CE intacto), **media** (FVG normal activo ∨ True FVG parcial), **baja** (mitigado / micro). Tag = `SMC_Zone.strength` (con `.trueFvg`).
- **Invalidación externa.** Cierre a través del borde → **no se borra**, transiciona a **IFVG** con `dir` invertida (§5.2, `state = 3`); FVG en **equilibrium / contra-localización** resta (§2.3 #31). DÓNDE: transición `state=3` = Pine (`f_updateZoneMitigation`); localización P/D = scoring; secuencia "1er toque débil vs 2º válido" = cadena ADR-012 **Q4**.
- **Visual (jerarquía).** **Primario:** True FVG fresco, cercano, CE intacto → caja sólida + etiqueta "T.FVG" + línea CE. **Secundario:** FVG normal activo o True FVG parcial → caja atenuada. **Terciario:** micro/mitigado → oculto o panel T14; invalidado → se redibuja como **IFVG**, no como FVG. Toggle `i_showFVG` / `i_showIFVG`.
- **MTF.** Transferible (cap `i_mtfCapFVG`, 0–10); caja anclada `xloc.bar_time` en la **vela media real** (`time[1]`, ADR-010); cae en el mismo gap que el FVG nativo del TF alto.

#### 6.2.3 Cruce de EMA (§4.3 #40) — SLOT *(fallo #2 fuerza — caso explícito del usuario)*

> **Objetivo del slot:** distinguir cruce **alineado al sesgo + con separación/fuerza** vs. cruce **pegado al precio en neutro** (ruido). La fuerza viene del **ángulo/separación + alineación**, NO del cruce en sí. Primitivos: separación entre EMAs ×ATR, alineación con bias, pendiente. Caso PLAN-049: 20×50 / 50×200. Toggle `i_showEmaCross`.

- **Variante correcta / desempate.** Cuál **par** cruza importa por **escala** (§4.3): `20×50` = frecuente, menor peso (momentum corto); `50×200` / `20×200` = raros, mayor peso (death/golden cross, cambio de régimen). EL relevante = el cruce de **mayor escala reciente alineado al bias**. El **Stack Flip** (§4.3: 20 **y** 50 cruzando al mismo lado de la 200) **domina** sobre cualquier cruce de par aislado. **Descarta** (citable): cruce `20×50` aislado mientras ambas siguen del **mismo lado** de la 200 (§4.3 contraejemplo) → no cambia el régimen → es ruido `#40`, no evento reforzado.
- **Fuerza (0–1).** `separación entre EMAs post-cruce ×ATR` (mayor = más convicción) · `alineación con bias` estructural (a favor sube; en contra ~0) · `pendiente/ángulo`. **Cruce pegado en neutro** (separación ~0, EMAs planas) → `strength ~0` aunque el cruce ocurra (caso explícito del usuario). Quant: **alta** (`50×200` o Stack Flip alineado + separación creciente), **media** (`20×50` alineado con pendiente), **baja** (cruce plano / contra-bias).
- **Invalidación externa.** Cruce **contra el bias dominante** (majorLen=50 / EMA200) = ruido contratendencia, no señal. DÓNDE: el peso lo aplica el **scoring** (#37–#39 direccionales **únicas** `[FIX P-05]`; #42 stack); ADR-012 **Q1** (¿el contexto mayor lo respalda?).
- **Visual (jerarquía).** **Primario:** cruce de gran escala (`50×200` / Stack Flip) alineado con separación → marca destacada. **Secundario:** `20×50` alineado. **Terciario:** cruce plano / contra-bias → oculto o panel T14. Toggle `i_showEmaCross`.
- **MTF.** Normalmente **NO** se transfiere como objeto: la EMA es **contexto del TF propio** (cada TF tiene su 20/50/200). Se hereda como **estado de bias** del HTF en el panel T14, no como marca anclada por `bar_time`.

#### 6.2.4 Rejection (§2.7) — SLOT *(fallo #2 fuerza + #3 invalidación)*

> **Objetivo del slot:** variante real (**mecha ≥2× cuerpo TOCANDO nivel**) vs. ruido (mecha larga **sin nivel**); invalidación: si el **retorno cruza el nivel**. Primitivos: ratio mecha/cuerpo, ¿hay nivel? (pool/EQH/OB), cierre vs nivel. Caso PLAN-049: 06-08 09:00, 05-27 12:00. Toggle `i_showRej`.

- **Variante correcta / desempate.** Rejection **real** = mecha `≥ rejWickFactor × cuerpo` (default 2×) **TOCANDO un nivel clave** (OB/FVG/pool/EQHL/PD/EMA) y cierre en la mitad favorable del rango (§2.7). Mecha larga **SIN nivel** = ruido → se descarta (§2.7 contraejemplo: 06-02 21:00, mecha 32× a media estructura). EL relevante entre varias = la de **mayor ratio mecha/cuerpo sobre el nivel más fuerte** (pool/EQH > OB/FVG > EMA).
- **Fuerza (0–1).** `ratio mecha/cuerpo` (mayor = más fuerte; casos §2.7: 2.1× / 2.8× / 4.5×) · **jerarquía del nivel** tocado (SSL/BSL/EQH/pool > OB/FVG > EMA) · `¿sweep del nivel justo antes?` (§3.2 — sube mucho la fuerza: barrer y volver = trampa confirmada) · `alineación con bias`. Quant: **alta** (ratio alto + sweep + alineada), **media** (ratio ≥2 sobre nivel sin sweep), **baja** (apenas ≥2× sobre EMA).
- **Invalidación externa.** Si el **retorno posterior cruza el nivel por cierre** → la rejection queda **anulada** (se marca como fallida, no se borra). DÓNDE: cadena ADR-012 **Q3** (¿rompió por cierre?); el `state` del nivel subyacente (Pine) y el scoring la degradan.
- **Visual (jerarquía).** **Primario:** rejection en nivel fuerte (pool/EQH) con sweep, alineada → marca ▲/▼ destacada. **Secundario:** rejection sobre OB/EMA sin sweep. **Terciario:** mecha sin nivel → no se marca (ya filtrada por §2.7). Toggle `i_showRej`.
- **MTF.** Transferible como **marca en su `bar_time`** (la mecha es de su vela); cae en el nivel del HTF que tocó. Cap moderado (evento puntual y frecuente; no saturar).

#### 6.2.5 MSS (§1.5) — SLOT *(fallo #1 desempate + #3 invalidación)*

> **Objetivo del slot:** desempate **MSS vs CHoCH normal** por **displacement** (ya en §1.5: rango ≥1.5×ATR ∧ cuerpo≥70%); invalidación externa contra el **bias dominante** (majorLen=50). Primitivos: `f_detectDisplacement`, escala swing vs dominante. Caso PLAN-049: 06-01 13:00 (3.5×ATR). Toggle `i_showMSS`.

- **Variante correcta / desempate.** **MSS** = CHoCH de nivel **swing** **CON displacement** (`rango ≥ 1.5×ATR ∧ cuerpo ≥ 70%`, §1.5). CHoCH swing **SIN displacement** = CHoCH normal / aviso → **se descarta como MSS** (§1.5 contraejemplo: 05-29 14:00, rango 2.93×ATR pero **cuerpo 63%** → no MSS, mecha dominante). El MSS **nunca es interno** (solo escala swing). Desempate a igualdad → gana el de mayor `displacement ×ATR`.
- **Fuerza (0–1).** `magnitud del displacement ×ATR` de la vela de ruptura (caso 06-01 13:00 = **3.51×ATR** → muy alta) · `cuerpo%` de esa vela (98% en el caso) · **escala** (swing dominante majorLen=50 > swing simple). Quant: **alta** (displacement ≥3×ATR ∧ cuerpo ≥90% en swing dominante), **media** (≥1.5×ATR ∧ ≥70%); por debajo **no es MSS** (es CHoCH normal).
- **Invalidación externa.** MSS **contra el bias dominante** de gran escala (majorLen=50) = **menor convicción** (giro contra la corriente mayor, más propenso a deviation). DÓNDE: **scoring** (peso del MSS vs bias dominante); cadena ADR-012 **Q1** (¿el contexto mayor lo respalda?).
- **Visual (jerarquía).** **Primario:** MSS swing de alta convicción → línea origen→ruptura destacada + etiqueta "MSS". **Secundario:** MSS-interno de apoyo (§1.5 nota: CHoCH interno con displacement, p.ej. 06-02 16:00 1.57×ATR/85%), menor peso. **Terciario:** N/A (un MSS siempre es relevante si existe). Toggle `i_showMSS`.
- **MTF.** Transferible **origen→ruptura** (buffer de eventos ADR-010); cae en el mismo `bar_time`/nivel que el MSS del HTF; **anti-duplicado** con estructura nativa (S042: si coincide con la nativa M5, no se redibuja).

### 6.3 Sub-bloques del resto de conceptos (§1–§5)

> Mismo formato que §6.0 (variante · fuerza · invalidación · visual · MTF). Cada fórmula de fuerza cita **solo** primitivos de §6.1. Los **refinamientos `[FIX P-05]`** (True FVG §5.1, Propulsion §5.8, familia Volume Imbalance, Macros §5.14) **no** llevan sub-bloque independiente: **elevan el `strength`** del concepto base. Todos los `strength`/pesos son **candidatos CONGELADOS hasta calibración Fase 3** (ADR-002). Los nombres de toggle `i_show*` / `GRP_*` son los de diseño (igual que en §6.2); el `[impl]` los confirma al cablear el tag de fuerza en Pine (HANDOFF §5).

#### TIER 1 — Estructura

##### 6.3.1 Swings (§1.1) *(fallo #1 desempate)*

- **Variante correcta / desempate.** Entre N pivotes candidatos lo relevante es **la escala** (§1.1: interno `internalLen=3` < swing `swingLen=5` < dominante `majorLen=50`) **y el rol estructural**: EL primario = el **structure high/low vigente y NO roto** (el que extiende o protege el bias, §"Modelo de bias"). Desempate de *detección* ya cerrado en §1.1 (empate al tick a ambos lados → no se estampa swing). **Descarta** (citable): pivote **no confirmado** (le faltan `swingLen` velas a la derecha → marcarlo es repaint, §1.1 contraejemplo); swing interno ya roto por cierre (deja de ser nivel activo).
- **Fuerza (0–1).** Sin cuerpo%/×ATR (el swing es geométrico): `escala` (dominante > swing > interno) · `edad/frescura` (`barTime`: swing reciente no roto > viejo) · `alineación con bias` (¿es el nivel protector/extensor del TF?). Quant: **alta** (structure high/low dominante vigente), **media** (swing simple no roto), **baja** (interno o ya rozado). Tag = `strength` del evento-swing (buffer ADR-010).
- **Invalidación externa.** Un swing **roto por cierre** (lo consume un BOS/CHoCH) deja de ser imán y pasa a contexto histórico. DÓNDE: estado estructural (Pine); el scoring ya no lo cuenta como nivel vivo.
- **Visual (jerarquía).** **Primario:** structure high/low vigente (etiqueta + línea). **Secundario:** swing confirmado no-protector. **Terciario:** interno viejo / roto → oculto o contado en panel T14. Toggle `i_showSwings`.
- **MTF.** Transferible como **nivel** anclado a `bar_time` del pivote; presupuesto de tinta top-N (`f_nearestN`, ADR-010); cae en el mismo nivel que el swing nativo del HTF.

##### 6.3.2 BOS / CHoCH **swing** (§1.3/§1.4) *(fallo #1 desempate + #3 invalidación)*

- **Variante correcta / desempate.** Determinista por **qué swing se rompe** (§"Modelo de bias"): romper el nivel que **extiende** = **BOS** (continuación); romper el que **protege** = **CHoCH** (cambio). Base de ruptura = **`close`**, no mecha (§1.3). EL relevante = el evento de **escala swing** más reciente que cambia el estado estructural. **Descarta** (citable): **mecha** que pincha el nivel y cierra de vuelta → es **sweep/grab** (§3.2/§3.3), NO BOS (§1.3 contraejemplo 05-27 12:00 high 1.16615 / close 1.16440); ruptura **interna** que no toca el swing protector → es CHoCH interno (§6.3.3), no voltea el bias swing.
- **Fuerza (0–1).** `magnitud del cierre más allá del nivel ×ATR` · `displacement` de la vela de ruptura (§4.1 — si la lleva, sube; un CHoCH swing **con** displacement ya es **MSS**, §6.2.5) · `alineación con bias` (BOS siempre alineado = alta convicción de continuación; CHoCH va contra el bias vigente = aviso) · `¿sweep previo del pool objetivo?` (§3.2). Quant: **alta** (BOS con displacement tras sweep), **media** (BOS/CHoCH limpio sin displacement), **baja** (cierre apenas más allá del nivel).
- **Invalidación externa.** Un CHoCH swing **aislado** contra el bias **dominante** (`majorLen=50`) puede ser deviation que revierte (§1.5 nota): menor convicción hasta que un BOS confirme la nueva dirección. DÓNDE: cadena ADR-012 **Q1** (¿el contexto mayor lo respalda?) y **Q3** (¿rompió por cierre real?); el scoring pondera BOS (#2/#4) vs CHoCH (#5 vía MSS).
- **Visual (jerarquía).** **Primario:** BOS/CHoCH swing que cambia el bias → línea de nivel roto + etiqueta "BOS"/"CHoCH". **Secundario:** BOS de continuación rutinario en tendencia ya establecida. **Terciario:** N/A (evento estructural siempre relevante). Toggle `i_showStructure` / `GRP_*` estructura.
- **MTF.** Transferible **origen→ruptura** (buffer de eventos ADR-010); cae en mismo `bar_time`/nivel que el del HTF; **tag `(D1/H1)`** en eventos fusionados (pendiente diferido (a), metodología §6.b); anti-duplicado con la estructura nativa del TF (S042).

##### 6.3.3 BOS / CHoCH **interno** (§1.4) *(fallo #2 fuerza)*

- **Variante correcta / desempate.** Misma mecánica de cierre que §6.3.2 pero sobre estructura `internalLen=3` (gatillo fino / IDM). EL relevante = el CHoCH interno **a favor** del bias swing vigente (gatillo de entrada limpio). **Descarta como giro mayor** (citable): tratar un CHoCH interno como vuelta del bias swing (§1.4 contraejemplo 06-02 04:00: rompe swing interno 1.16370 pero NO el LH swing → el bias mayor sigue bajista). Regla dura §1.4: **no voltear el bias mayor con una ruptura interna.**
- **Fuerza (0–1).** Inherentemente **menor** que el swing (escala fina): `magnitud ×ATR` · `displacement` (§4.1) · `alineación con el bias swing` (interno a favor del swing = útil; en contra = ruido). Quant: **media** (interno alineado con displacement, buen gatillo), **baja** (interno contra el bias swing — ruido típico). Nunca **alta** solo por ser interno.
- **Invalidación externa.** Interno **contra** el bias swing/dominante = ruido de pullback, no señal. DÓNDE: scoring (peso interno < swing); cadena ADR-012 **Q1**.
- **Visual (jerarquía).** **Secundario** por defecto (es estructura fina): marca pequeña/atenuada. **Terciario:** interno contra-bias → panel T14. **Primario:** solo si es el gatillo de entrada confirmado a favor del swing. Toggle `i_showInternal`.
- **MTF.** Normalmente **no** se transfiere a TF menores (sería ruido sobre ruido); se consume en su TF. Cap muy bajo si se hereda.

##### 6.3.4 Estructura **dominante** (`majorLen=50`) (§1.1/§1.4) *(fallo #1 desempate + #3 invalidación)*

- **Variante correcta / desempate.** La **escala grande** [T07B] (= swing structure de LuxAlgo). EL relevante = el último BOS/CHoCH dominante que define el **contexto mayor**. **Descarta** (citable): confundir un BOS swing/interno con cambio de contexto — la capa dominante **no voltea el bias headline por sí sola** hasta calibración Fase 3 (§1.3/§1.4). El dominante **se detecta y dibuja**, pero su efecto sobre el bias está **diferido**.
- **Fuerza (0–1).** `escala` (dominante = máxima por definición) · `displacement ×ATR` de la vela de ruptura dominante · `frescura` (el dominante confirma ~2 días tarde en H1, §1.1 — es correcto, no bug). Quant: **alta** siempre que exista (es contexto rector); el matiz lo da si está **respaldado** o **enfrentado** al precio actual.
- **Invalidación externa.** Un CHoCH dominante recién confirmado **antes** de que el precio dé continuación = cambio de régimen **candidato**, no confirmado (efecto diferido a Fase 3). DÓNDE: cadena ADR-012 **Q1** (es la respuesta misma al "¿contexto mayor?"); el scoring lo usa como **modulador de bias**, no como voto puntual.
- **Visual (jerarquía).** **Primario:** estructura dominante vigente → línea gruesa/destacada + etiqueta de bias dominante en panel T14. **Secundario/Terciario:** N/A (siempre es el marco rector). Toggle `i_showMajor` / panel de bias.
- **MTF.** Es **el** insumo de herencia HTF→LTF (§6.3.35): baja a M5 como **estado de bias dominante** del panel T14, no como marca puntual.

#### TIER 2 — Zonas

> **True FVG (§5.1) — NO sub-bloque [FIX P-05]:** eleva el `strength` del FVG base (ver §6.2.2, primitivo `trueFvg`). Una vela media de displacement → variante de mayor calidad del MISMO gap, no confluencia ni objeto nuevo.

##### 6.3.5 Premium / Discount / Equilibrium (§2.3) *(fallo #3 invalidación — es el invalidador de localización)*

- **Variante correcta / desempate.** No es "una marca entre varias": es el **filtro de localización** del *dealing range* `[strong_low, strong_high]` vigente (§2.3). EL relevante = el rango **dominante** activo (`majorLen`). **Descarta** (citable): medir P/D sobre un rango ya superado por estructura (el rango se actualiza con cada nuevo strong high/low).
- **Fuerza (0–1).** `distancia al `eq` (50%) ×ATR` o % del rango (más extremo = más ventaja de localización): discount profundo (≤25%) = alta para long; premium profundo (≥75%) = alta para short · `alineación con bias`. **Banda equilibrium [45–55%]** (§2.3: `[1.15835, 1.16021]` en el caso) → `strength ~0` de localización. No es zona dibujable con `strength` propia; es un **multiplicador** del `strength` de las demás zonas según dónde caigan.
- **Invalidación externa.** Es **ella** la que invalida a otras: un OB/FVG en **contra-localización** (OB alcista en premium) se marca pero el **scoring lo degrada** (#31 resta 50% en equilibrium; §2.1/§6.2.1 invalidación #1). DÓNDE: **scoring** (#31); cadena ADR-012 (contexto de valor).
- **Visual (jerarquía).** **Primario:** las tres bandas (premium/eq/discount) como fondo/zonas tenues del rango vigente + línea `eq`. **Secundario:** rangos de escala menor. No satura (es contexto de fondo, no marca puntual). Toggle `i_showPD`.
- **MTF.** Transferible como **bandas del HTF** heredadas a M5 (el dealing range D1/H1 colorea el fondo de M5); el `eq` HTF es un nivel ancla por `bar_time` del rango.

##### 6.3.6 Equal Highs / Equal Lows (§2.4) *(fallo #1 desempate + #2 fuerza)*

- **Variante correcta / desempate.** EQH/EQL = **≥2 swings confirmados** a `|Δ| ≤ eqThreshold×ATR` (default 0.1, §2.4). EL relevante entre varios = el de **más toques** y más cercano al precio (más liquidez acumulada → mejor objetivo de sweep). **Descarta** (citable): dos highs a `0.6×ATR` (§2.4 contraejemplo) → no son EQH, son HH/LH; un EQH **ya barrido** deja de ser pool activo (§3.1: su liquidez se tomó).
- **Fuerza (0–1).** `nº de toques` (`touches`, §3.1 — más = más fuerte) · `igualdad` (Δ menor ×ATR = doble techo más limpio) · `frescura` (no barrido) · `alineación` (EQH sobre el precio = objetivo BSL para bias bajista). Quant: **alta** (≥3 toques, no barrido, alineado al objetivo), **media** (2 toques limpios), **baja** (2 toques con Δ cerca del umbral).
- **Invalidación externa.** Un EQH/EQL **barrido** (sweep §3.2) cumple su función y deja de atraer → pasa a contexto (y suele preceder el giro contrario). DÓNDE: `pool.swept` (Pine); el scoring lo reconvierte en señal de sweep (#10).
- **Visual (jerarquía).** **Primario:** EQH/EQL de alto `touches` no barrido cercano → línea de liquidez + etiqueta "BSL"/"SSL". **Secundario:** 2 toques lejano. **Terciario:** barrido → oculto o panel T14. Toggle `i_showEQHL` (alimenta `i_showPools`).
- **MTF.** Transferible como **nivel de liquidez** (`bar_time` del cluster); cuadre fino HTF/LTF es el pendiente diferido (b) (metodología §6.b); cae en el mismo nivel que el EQH/EQL nativo del HTF.

##### 6.3.7 OTE / Golden Pocket (§2.5) *(fallo #1 variante)*

- **Variante correcta / desempate.** Fib `[0=origen, 1=extremo]` **solo sobre la última pierna IMPULSIVA que produjo BOS** (§2.5/§4.4). GP = `[50–61.8%]` (#28); OTE = `[61.8–79%]` (#27, más profundo = mejor R:R). EL relevante = el fib de la pierna impulsiva **vigente** (se redibuja con cada nuevo impulso). **Descarta** (citable): medir fib sobre una pierna **correctiva** sin BOS propio (§2.5/§4.4 contraejemplo 06-09→06-10) → OTE sin significado institucional.
- **Fuerza (0–1).** `profundidad del retroceso` (OTE 79% > GP 50% en precio/R:R) · `confluencia con OB/FVG dentro de la zona` (sube mucho: OTE+OB = entrada premium) · `alineación con bias` · `calidad de la pierna` (impulsiva con displacement §4.4). Quant: **alta** (OTE con OB/FVG alineado), **media** (GP solo), **baja** (toque superficial del 50%).
- **Invalidación externa.** Si el retroceso **supera el 100%** (cierra más allá del origen de la pierna) → la pierna se anuló, el fib deja de valer (es CHoCH/cambio). DÓNDE: estado de la pierna (Pine); cadena ADR-012 **Q1**.
- **Visual (jerarquía).** **Primario:** zona OTE/GP de la pierna vigente con confluencia → caja fib + niveles 0.618/0.79. **Secundario:** GP sin confluencia. **Terciario:** fib de pierna ya superada → oculto. Toggle `i_showOTE`.
- **MTF.** Transferible como **zona** anclada a la pierna HTF (`bar_time` origen/extremo); cae en el mismo rango fib que el nativo del HTF.

##### 6.3.8 Breaker (§2.6) *(fallo #1 desempate + #3 invalidación)*

- **Variante correcta / desempate.** Un **OB invalidado** (`state = 3`, cierre a través del borde protector, §2.1) → `KIND_BREAKER` con `dir` invertido (§2.6). EL relevante = el breaker **fresco** retesteado desde el otro lado. **Descarta** (citable): un OB solo **mitigado** (`state 2`, lo tocó y respetó, §2.6 contraejemplo) → sigue siendo OB en su dir original, NO breaker; el breaker exige **invalidación por cierre**, no un toque.
- **Fuerza (0–1).** `magnitud del cierre que invalidó ×ATR` (rompió con convicción) · `¿sweep previo?` (§3.2 — el breaker "real" ICT nace tras barrer liquidez antes de fallar) · `frescura del retest` (`state` del breaker) · `alineación con el nuevo bias`. Quant: **alta** (invalidación con displacement tras sweep, retest fresco), **media** (invalidación limpia sin sweep), **baja** (invalidación marginal).
- **Invalidación externa.** Si el precio **cierra de vuelta** a través del breaker → el flip de polaridad falló (doble invalidación). DÓNDE: `f_updateZoneMitigation` (Pine, hereda máquina del OB); cadena ADR-012 **Q4** (¿barrieron a los tempranos antes del flip?).
- **Visual (jerarquía).** **Primario:** breaker fresco alineado con el nuevo bias → caja con borde de "flip" + etiqueta "BRK". **Secundario:** breaker lejano/parcial. **Terciario:** breaker re-invalidado → oculto. Toggle `i_showBreaker`. *(Nota §2.6: el retest limpio es escaso en ventana bajista persistente — gate Fase 1 T19 pide ≥1.)*
- **MTF.** Transferible como **zona** (`bar_time` de las coordenadas del OB original); cae en el mismo nivel que el breaker nativo del HTF.

##### 6.3.9 Flip (§2.8 · #25) *(fallo #1 variante)*

- **Variante correcta / desempate.** Nivel (swing/OB/EQHL) roto por **`close` limpio** y luego **retesteado desde el lado opuesto** y respetado → cambio de rol (§2.8). EL relevante = el flip cuyo retest **respeta** (cierre que no lo vuelve a cruzar). **Descarta** (citable): nivel roto **solo por mecha** sin cierre limpio (§2.8 contraejemplo: sweep BSL 1.16615 del 05-27 sin cierre) → no es flip, el cierre definitorio nunca ocurrió. Distinción dura: `breaker`=falló tras barrido; `flip`=cambio de rol por retest; `mitigation block`=relleno sin barrido.
- **Fuerza (0–1).** `limpieza de la ruptura` (cierre claro ×ATR) · `respeto del retest` (rechazo con mecha, §2.7) · `jerarquía del nivel flippeado` (swing/EQHL > OB) · `alineación con bias`. Quant: **alta** (ruptura limpia + retest rechazado en nivel fuerte), **media** (flip de OB), **baja** (retest tibio).
- **Invalidación externa.** Si el retest **cruza por cierre** el nivel flippeado → el flip se anula (el rol no cambió). DÓNDE: estado del nivel (Pine); cadena ADR-012 **Q3** (¿rompió por cierre?).
- **Visual (jerarquía).** **Primario:** flip confirmado por retest en nivel fuerte → línea con marca de cambio de rol. **Secundario:** flip de OB. **Terciario:** ruptura sin retest aún → latente/atenuado. Toggle `i_showFlip`.
- **MTF.** Transferible como **nivel** (`bar_time`); cae en el mismo nivel que el flip nativo del HTF.

##### 6.3.10 Mitigation Block (§2.8 · #24) *(fallo #1 desempate)*

- **Variante correcta / desempate.** Última vela contraria antes de un impulso que rompe estructura interna **SIN sweep previo** de un pool (§2.8). EL relevante = el mitigation block que rellena un desequilibrio previo sin haber barrido liquidez. **Descarta** (citable): si **hubo sweep** antes del impulso → es contexto de **breaker/OB**, no mitigation block (§2.8). Es la distinción que lo separa del breaker (que sí invalida tras barrido).
- **Fuerza (0–1).** `magnitud del impulso que lo origina ×ATR` (displacement §4.1) · `frescura` (`state`) · `alineación con bias`. Inherentemente **menor peso** que OB/breaker (rellena desequilibrio sin la limpieza de liquidez que da convicción). Quant: **media** (impulso con displacement, fresco), **baja** (impulso normal).
- **Invalidación externa.** Cierre a través de su borde → invalidado (deja de ser zona). Si retrospectivamente **sí hubo sweep**, se reclasifica a OB/breaker. DÓNDE: `f_updateZoneMitigation` (Pine); scoring (#24, peso bajo).
- **Visual (jerarquía).** **Secundario** por defecto (zona de apoyo, menor convicción): caja atenuada. **Terciario:** mitigado → panel T14. Toggle `i_showMitBlock` (puede colapsarse en `GRP_*` zonas).
- **MTF.** Transferible como **zona** (`bar_time`) con cap bajo (zona secundaria; no saturar).

#### LIQUIDEZ

##### 6.3.11 Pools de liquidez BSL / SSL (§3.1) *(fallo #2 fuerza)*

- **Variante correcta / desempate.** Cluster de EQH/EQL + swings no barridos dentro de `poolTol×ATR` (default 0.1, ≥`minTouches`=2, §3.1). EL relevante = el pool **no barrido** con **más toques** más cercano al precio (mayor imán). **Descarta** (citable): swing aislado **ya barrido** (§3.1 contraejemplo: 1.14997 tras el rally) → su liquidez se tomó, no es pool activo.
- **Fuerza (0–1).** `touches` (más toques = más liquidez acumulada = más fuerte, §3.1) · `frescura` (`swept=false`) · `distancia al precio ×ATR` (cercano = imán inmediato) · `alineación` (pool sobre el precio = objetivo para bias bajista). Quant: **alta** (≥3 toques, no barrido, cercano), **media** (2 toques), **baja** (pool lejano).
- **Invalidación externa.** Pool **barrido** (`swept=true`, §3.2) → deja de ser imán (cumplió su rol). DÓNDE: `pool.swept` (Pine); el scoring lo convierte en input de sweep (#10), no de pool activo.
- **Visual (jerarquía).** **Primario:** pool de alto `touches` no barrido cercano → línea de liquidez + etiqueta con nº toques. **Secundario:** 2 toques lejano. **Terciario:** barrido → oculto o contado en panel T14. Toggle `i_showPools`.
- **MTF.** Transferible como **nivel** (`bar_time` del cluster, persistente — ADR pools); presupuesto top-N (`f_nearestNPools`, ADR-010); cae en el mismo nivel que el pool nativo del HTF.

##### 6.3.12 Sweep (§3.2) + Grab (§3.3) *(fallo #1 variante + #2 fuerza)*

- **Variante correcta / desempate.** **Sweep** = perfora un **pool confirmado** (≥2 touches) intra-vela y `close` vuelve dentro (§3.2). **Grab** = misma mecánica sobre un **swing aislado** sin pool (§3.3, más fino/frecuente, menor peso). EL relevante = el sweep sobre el pool de **más liquidez** (mayor `touches` → Raid §3.7 si `touches≥3`). **Descarta** (citable): perfora **y cierra más allá** (no vuelve) → es BOS/false breakout (§3.2 contraejemplo 06-05 12:00), NO sweep; mecha que no alcanza ningún nivel (§3.3) → no hay liquidez que tomar.
- **Fuerza (0–1).** `touches del pool barrido` (sweep de pool > grab de swing aislado) · `profundidad de la perforación ×ATR` y `fuerza del cierre de retorno` (cuánto vuelve dentro = convicción de la trampa) · `displacement posterior` (§4.1 — si reversiona con impulso, es Judas/Spring, sube mucho). Quant: **alta** (sweep de pool alto + displacement contrario = trampa confirmada), **media** (sweep simple con retorno claro), **baja** (grab de swing aislado).
- **Invalidación externa.** Si tras el sweep el precio **continúa** en la dirección del barrido sin reversión → no era trampa, era ruptura genuina (degrada a contexto de BOS). DÓNDE: cadena ADR-012 **Q3/Q4** (¿rompió por cierre? ¿barrieron a los tempranos?); scoring (#10 sweep, #11 grab).
- **Visual (jerarquía).** **Primario:** sweep de pool alto con reversión → marca de barrido destacada (✸) en su `bar_time`. **Secundario:** grab de swing aislado. **Terciario:** sweep sin reversión → panel T14. Toggle `i_showSweep`.
- **MTF.** Transferible como **marca puntual** (`bar_time` de la vela del barrido); cae sobre el pool/nivel del HTF barrido. Cap moderado (evento frecuente en M5).

##### 6.3.13 IDM — Inducement (§3.6 · #33) *(fallo #2 fuerza)*

- **Variante correcta / desempate.** Swing low/high **interno** (`internalLen`) más cercano cuya liquidez se barre **antes** de que el precio alcance el OB/FVG objetivo (§3.6). EL relevante = el inducement **entre el origen del impulso y la zona objetivo** que se toma justo antes del movimiento real. **Descarta** (citable): si el precio llega al OB **sin** barrer ningún inducement intermedio (§3.6 contraejemplo) → entrada de menor calidad (camino no "limpio"), no hay IDM que sumar.
- **Fuerza (0–1).** `¿se barrió el inducement antes de tocar el objetivo?` (binario clave: camino limpio sube la fuerza de la entrada) · `proximidad del IDM al objetivo` · `alineación con el impulso esperado`. Es **calificador de calidad de la entrada**, no zona propia. Quant: **alta** (IDM barrido limpio justo antes del empuje, p.ej. 06-11 06:05 nivel 1.15426), **baja** (sin IDM previo).
- **Invalidación externa.** Si tras barrer el IDM el precio **no** alcanza el objetivo (revierte antes) → el inducement no validó el camino. DÓNDE: scoring (#33 IDM barrido); cadena ADR-012 **Q4** (¿barrieron a los tempranos? — el IDM **es** esa liquidez señuelo).
- **Visual (jerarquía).** **Secundario** (es contexto fino de la entrada): marca pequeña sobre el swing interno barrido. **Primario** solo cuando es el gatillo confirmado hacia el objetivo. **Terciario:** IDM no barrido → no se marca. Toggle `i_showIDM`.
- **MTF.** Normalmente **no** se transfiere (liquidez interna del TF de entrada); se consume en M5.

##### 6.3.14 Judas Swing (§3.5 · #13) *(fallo #1 variante + #3 invalidación)*

- **Variante correcta / desempate.** Sweep/grab en la **primera mitad de una Kill Zone** (§3.4) seguido de **displacement contrario** en `≤ judasBars` velas (default 6 M5, §3.5). `dir` = el del displacement (el movimiento real). EL relevante = la trampa de apertura de sesión. **Descarta** (citable): sweep a mitad de sesión **sin** displacement contrario (§3.5 contraejemplo 06-11 12:25, continuó a la baja) → solo sweep, NO Judas (exige la reversión con fuerza); barrido **fuera de la 1ª mitad de KZ** → clasifica como Spring/sweep (§3.7), no Judas.
- **Fuerza (0–1).** `magnitud del displacement de reversión ×ATR` (§4.1) · `cercanía al open de sesión` · `touches del pool barrido` (barrer liquidez real antes de la trampa). Quant: **alta** (sweep de pool + displacement fuerte en 1ª mitad de KZ, p.ej. 06-11 06:05→06:10 1.62×ATR), **media** (Judas con displacement moderado), **baja** (reversión apenas ≥umbral).
- **Invalidación externa.** Si el displacement contrario **no** llega en ≤6 velas, o el precio retoma la dirección del barrido → la trampa no se confirmó. DÓNDE: ventana temporal (Pine, §3.5); cadena ADR-012 **Q4**.
- **Visual (jerarquía).** **Primario:** Judas confirmado en KZ → marca de trampa + flecha del movimiento real. **Terciario:** sweep sin reversión → no es Judas. Toggle `i_showJudas`. *(Nota §3.5: Judas completo escaso — gate Fase 1 T18 pide ≥3.)*
- **MTF.** Concepto de **M5 intradía** (ligado a la KZ); no se transfiere a HTF (es evento de sesión).

##### 6.3.15 False Breakout / Spring / Raid (§3.7 · #14/#15/#16) *(fallo #1 variante)*

- **Variante correcta / desempate.** Tres variantes de barrido en extremo de rango: **False Breakout** = `close` cruza el nivel + reversión que cierra de vuelta en `≤fbBars` velas (default 2) — a diferencia del sweep (solo mecha); **Spring** = sweep de SSL bajo el mínimo de un rango lateral + reversión rápida al alza (`dir+1`); **Raid** = sweep de pool con `touches≥raidTouches` (default 3, mayor peso). EL relevante = el de **pool más líquido** (Raid > Spring > FB simple). **Descarta** (citable): cierre más allá que **no** revierte en ≤2 velas (§3.7 contraejemplo 06-05 12:00) → breakout real (BOS), no falso.
- **Fuerza (0–1).** `touches del pool` (Raid alto = máxima) · `velocidad/magnitud de la reversión ×ATR` (Spring: rally 4.84×ATR del 06-11 17:15) · `¿coincide con extremo de rango/mínimo de consolidación?`. Quant: **alta** (Raid de cluster alto con reversión explosiva), **media** (Spring/FB sobre 2 toques), **baja** (FB marginal).
- **Invalidación externa.** Si la reversión excede `fbBars` o no se materializa → era ruptura genuina. DÓNDE: ventana `fbBars` (Pine); cadena ADR-012 **Q3/Q4**; scoring (#14/#15/#16).
- **Visual (jerarquía).** **Primario:** Raid/Spring en extremo con reversión → marca destacada. **Secundario:** False Breakout simple. **Terciario:** sin confirmar → panel T14. Toggle `i_showFalseBreak` (familia con `i_showSweep`).
- **MTF.** Transferible como **marca** (`bar_time`) sobre el extremo del rango del HTF; cap moderado.

##### 6.3.16 Kill Zones (§3.4 · #34) + Macros (§5.14) *(fallo #2 fuerza — peso, no veto)*

- **Variante correcta / desempate.** Ventana horaria por `sessionProfile` (default FX-London-NY, §3.4). **NO es filtro duro** (ADR-001): aporta **peso** a #34, no bloquea. **Macros (§5.14, `[FIX P-05]`)** = sub-ventanas de minutos dentro de la KZ → **refinan #34** (mayor peso), no suman confluencia. EL relevante = la sesión activa (+ macro si coincide). **Descarta** como veto (citable): bloquear una señal a las 03:00 GMT por reloj (§3.4 contraejemplo) → el reloj informa, gobierna spread/score.
- **Fuerza (0–1).** `¿sesión activa?` (binario, suma peso #34) · `¿primera mitad?` (relevante para Judas §3.5) · `¿macro activa?` (§5.14, sube el peso). El reloj **no** tiene `strength` de marca; **modula** el peso de las demás señales que caen en la ventana. Quant: **alta** (señal en macro dentro de KZ), **media** (señal en KZ sin macro), **baja**/neutra (fuera de KZ — no resta, solo no aporta).
- **Invalidación externa.** No invalida nada (no es señal): es modulador. NY Lunch (§5.14: 12:00–13:00 NY) = **filtro de baja actividad** (no entrada). DÓNDE: scoring (#34, peso por símbolo Fase 3/5); en `sessionProfile=None` (cripto/índices 24h) #34 no aporta.
- **Visual (jerarquía).** **Primario:** sombreado de la KZ activa en el fondo del chart (contexto, no marca). Macros como sub-sombreado fino. Toggle `i_showKZ` / `i_showMacros`. Anti-repaint: por reloj.
- **MTF.** Es **contexto de M5 intradía**; no se transfiere como objeto (cada TF lee su propio reloj).

#### CONTEXTO / ICT / EMAs

##### 6.3.17 Displacement (§4.1 · #32) *(fallo #2 fuerza — es la fuente del primitivo)*

- **Variante correcta / desempate.** Vela/tramo con `rango ≥ dispFactor×ATR14` (1.5) **y** `cuerpo ≥ bodyPct×rango` (0.70), opcional tras ≥3 velas de compresión (§4.1). EL relevante = el displacement **a favor del bias** que crea el OB/FVG o califica el MSS/Judas. **Descarta** (citable): rango grande con **cuerpo pequeño** (mecha dominante, §4.1 contraejemplo 05-29 14:00 cuerpo 63%) → indecisión/rechazo, NO displacement. Es **el primitivo de fuerza** que alimenta a casi todos los demás (§6.1).
- **Fuerza (0–1).** Él **es** un primitivo de §6.1, pero como evento propio su fuerza = `rango ×ATR` (5.27×ATR del 06-05 12:00 = extrema) · `cuerpo%` (97–98% = máxima convicción) · `¿tras compresión?`. Quant: **alta** (≥3×ATR, cuerpo ≥90%), **media** (≥1.5×ATR, ≥70%), **baja**: por debajo no es displacement.
- **Invalidación externa.** Displacement **contra el bias dominante** = expansión correctiva (puede ser una vela fuerte en pierna correctiva §4.4) → no implica cambio de tendencia. DÓNDE: cadena ADR-012 **Q1**; el scoring lo pondera por alineación.
- **Visual (jerarquía).** **Primario:** displacement extremo a favor del bias → realce de la vela (color/marca). **Secundario:** displacement moderado. **Terciario:** rara vez se oculta (es informativo). Toggle `i_showDisp`.
- **MTF.** Transferible como **marca de vela** (`bar_time`); cae en la misma vela que el displacement nativo del HTF. La **exactitud vela-a-vela** es el pendiente diferido (c) (metodología §6.b).

##### 6.3.18 EMAs — estado / alineación (§4.3 · #37–#39, #42) *(fallo #2 fuerza)*

- **Variante correcta / desempate.** Estados direccionales **únicos** `[FIX P-05]`: #37 vs EMA200, #38 vs EMA50, #39 vs EMA20 (cada uno suma a long **O** short, nunca infla), #42 = 3 EMAs alineadas (`E20>E50>E200` → +1 fuerte). EL relevante para convicción = la **alineación completa** (#42) > estado vs una sola EMA. **Descarta** (citable): contar "close>EMA200" Y "close<EMA200" como confluencias separadas (§4.3 contraejemplo `[FIX P-05]`) → una siempre activa, +peso garantizado.
- **Fuerza (0–1).** `nº de EMAs alineadas` (3 alineadas = alta) · `separación entre EMAs ×ATR` (abanico abierto = tendencia fuerte; pegadas = chop) · `pendiente`. Quant: **alta** (#42 con abanico abierto, 06-08→06-11 E20<E50<E200), **media** (sobre/bajo 1–2 EMAs), **baja** (EMAs entrelazadas/planas). Confirman, no lideran (§4.3: peso base bajo).
- **Invalidación externa.** EMAs **entrelazadas/planas** = sin tendencia → el estado no aporta dirección fiable (no resta, neutraliza). DÓNDE: scoring (#37–#42, peso base bajo calibrado Fase 3).
- **Visual (jerarquía).** **Primario:** las 3 EMAs (20/50/200) siempre visibles como contexto; realce cuando #42 alineado. No es marca puntual. Toggle `i_showEMAs`.
- **MTF.** **NO** se transfiere como objeto (cada TF tiene sus 20/50/200, §6.2.3); se hereda como **estado de bias** del HTF en panel T14.

##### 6.3.19 EMA rebote (§4.3 · #41) *(fallo #2 fuerza + #3 invalidación)*

- **Variante correcta / desempate.** El precio toca una EMA y cierra de vuelta con `mecha ≥ rejWickFactor×cuerpo` (2×, reusa §2.7) **en dirección de la tendencia** (§4.3 #41). EL relevante = el rebote en la EMA **alineada con el bias** (rebote en EMA50/200 en tendencia > toque de EMA20 en chop). **Descarta** (citable): toque de EMA **contra** la tendencia (rebote en contra = no confirma); mecha sin rebote real (cierra del lado equivocado).
- **Fuerza (0–1).** `ratio mecha/cuerpo` (reusa Rejection §2.7) · `jerarquía de la EMA tocada` (200 > 50 > 20) · `alineación con bias`. Quant: **alta** (rebote fuerte en EMA200 a favor), **media** (rebote en EMA50), **baja** (toque tibio de EMA20).
- **Invalidación externa.** Si el precio **cierra a través** de la EMA tras el rebote → el rebote falló (la EMA no aguantó). DÓNDE: cadena ADR-012 **Q3**; scoring (#41).
- **Visual (jerarquía).** **Secundario** por defecto (confirmación, peso bajo): marca pequeña sobre la EMA. **Primario** solo si confluye con OB/FVG en la EMA. Toggle `i_showEmaBounce` (familia EMAs).
- **MTF.** Como las EMAs, **contexto del TF propio**; no se transfiere como marca.

##### 6.3.20 EMA Stack Flip (§4.3) *(fallo #1 desempate)*

- **Variante correcta / desempate.** **EMA20 y EMA50 ambas cruzan al mismo lado de la EMA200** habiendo estado al otro (golden/death cross del grupo rápido, §4.3). Es la **entrada** al estado #42 y **domina** sobre cualquier cruce de par aislado (§6.2.3). **Descarta** (citable): cruce 20×50 aislado mientras ambas siguen del mismo lado de la 200 (§4.3 contraejemplo) → no cambia el régimen, es ruido #40, no Stack Flip.
- **Fuerza (0–1).** `magnitud del cruce respecto a la 200 ×ATR` · `separación posterior` (régimen consolidándose) · `alineación con la estructura dominante` (Stack Flip bajista 06-08 coincidió con el inicio del tramo dominante bajista). Es **evento de mayor convicción** (§4.3). Quant: **alta** siempre que es flip real alineado con el cambio de régimen estructural; **media** si va por delante del precio.
- **Invalidación externa.** Stack Flip **contra** la estructura dominante (`majorLen=50`) = posible whipsaw → menor convicción hasta confirmación estructural. DÓNDE: scoring (#42/#40 reforzado); cadena ADR-012 **Q1**.
- **Visual (jerarquía).** **Primario:** Stack Flip (cambio de régimen) → marca destacada `KIND_EMASTACK` + etiqueta. **Secundario/Terciario:** N/A (siempre es evento relevante). Toggle `i_showStackFlip`.
- **MTF.** Como las EMAs, **contexto del TF propio**; se hereda como cambio de bias del HTF en panel T14.

##### 6.3.21 Session Opens (§4.2 · #36) *(fallo #2 fuerza)*

- **Variante correcta / desempate.** Niveles de apertura diaria/semanal/mensual (§4.2); #36 activa cuando el precio está dentro de `openProx×ATR` (0.5) de uno. EL relevante = la apertura **más cercana** al precio actuando como S/R inmediato. **Descarta** (citable): apertura a `~3×ATR` del precio (§4.2 contraejemplo) → el nivel existe pero NO es confluencia activa (lejos para influir).
- **Fuerza (0–1).** `proximidad al nivel ×ATR` (cuanto más cerca, más peso #36) · `jerarquía` (semanal/mensual > diaria) · `lado` (direccional según de qué lado esté el precio). Quant: **alta** (precio pegado a apertura semanal/mensual), **media** (cerca de la diaria), **baja**/inactiva (lejos).
- **Invalidación externa.** El precio se aleja >`openProx×ATR` → #36 se desactiva (sin resta). DÓNDE: scoring (#36, direccional).
- **Visual (jerarquía).** **Primario:** apertura semanal/mensual como líneas ancla persistentes. **Secundario:** diaria. **Terciario:** aperturas viejas lejanas → ocultas. Toggle `i_showOpens`. *(Se extiende como **serie de gaps** en §6.3.32.)*
- **MTF.** Niveles **globales** (mismos en todo TF); se dibujan una vez y heredan naturalmente a M5.

##### 6.3.22 Impulsive / Corrective (§4.4 · #7/#8) *(fallo #1 variante — es clasificador de estado)*

- **Variante correcta / desempate.** **No es confluencia aditiva**: clasifica el **tramo** contra el bias dominante (§4.4). **IMPULSIVO** = `hasDisplacement` (§4.1) **Y** `breakAligned` (BOS alineado o MSS que voltea). **CORRECTIVO** = lo demás (retroceso contra-sesgo, solapado). EL relevante = la clasificación del tramo **vigente** (define si §2.5 OTE tiene sentido). **Descarta** (citable): clasificar impulsivo un retroceso contra-sesgo por **una** vela fuerte (§4.4 contraejemplo 06-09→06-10) → es correctivo (no rompe estructura dominante a su favor); el ER **no** es el criterio (verificado: 0.28 impulso < 0.6–0.89 correcciones).
- **Fuerza (0–1).** Para el tramo impulsivo: `magnitud del displacement ×ATR` · `nº de BOS encadenados` (2+ sin CHoCH = #7 impulso) · `alineación con bias dominante`. Para el correctivo: es el **insumo** del OTE (su "fuerza" = profundidad del retroceso fib §6.3.7). Quant impulso: **alta** (displacement extremo + BOS encadenados, caída 06-04→06-08), **media** (1 displacement + 1 BOS).
- **Invalidación externa.** Un "impulso" sin displacement (BOS aislado de rango normal, §1.6 contraejemplo 06-08 08:00 1.21×ATR cuerpo 52%) → no califica como impulso. DÓNDE: cadena ADR-012 **Q1**; scoring (#7 impulso previo / #8 corrección en curso).
- **Visual (jerarquía).** **Contexto, no marca puntual:** colorea/etiqueta el tramo vigente (impulsivo vs correctivo) en el panel T14 o como sombreado de pierna. **Primario:** tramo impulsivo dominante. Toggle `i_showLegs`.
- **MTF.** Se hereda como **estado del tramo HTF** en el panel T14 (el M5 sabe si el H1 está impulsivo o correctivo).

#### GAP ICT (§5)

> **Refinamientos `[FIX P-05]` (sin sub-bloque propio):** **True FVG §5.1** eleva `strength` del FVG (§6.2.2); **Propulsion Block §5.8** eleva `strength` del OB de continuación (§6.2.1); la familia **Volume Imbalance/SIVI/BIVI** cuenta como **1 sola** confluencia (§6.3.26).

##### 6.3.23 IFVG — Inversion FVG (§5.2 · #43) *(fallo #3 invalidación)*

- **Variante correcta / desempate.** Análogo exacto del Breaker pero sobre FVG: un FVG que pasa a `ZS_INVALID` (cierre a través del borde, §2.1) → `KIND_IFVG` con `dir` invertido (§5.2). EL relevante = el IFVG **fresco** retesteado desde el otro lado. **Descarta** (citable): FVG solo **mitigado** (`ZS_MITIGATED`, lo tocó y respetó, §5.2 contraejemplo) → sigue siendo FVG válido, NO IFVG (exige invalidación por cierre); **no** sumar el FVG muerto + su IFVG (1 sola confluencia, `[FIX P-05]`).
- **Fuerza (0–1).** `magnitud del cierre que invalidó ×ATR` · `¿el FVG original era True FVG?` (`trueFvg` — invertir un gap de calidad pesa más) · `frescura del retest` · `alineación con el nuevo bias`. Quant: **alta** (invalidación con displacement de un True FVG, retest fresco), **media** (IFVG normal), **baja** (invalidación marginal).
- **Invalidación externa.** Cierre de vuelta a través del IFVG → doble invalidación. DÓNDE: `f_updateZoneMitigation` (Pine, misma máquina del FVG); cadena ADR-012 **Q4**.
- **Visual (jerarquía).** **Primario:** IFVG fresco alineado → caja con marca de inversión + etiqueta "IFVG". **Secundario:** IFVG lejano. **Terciario:** re-invalidado → oculto. Toggle `i_showIFVG`. *(Ventana: 27 FVG invalidados → 27 IFVG candidatos.)*
- **MTF.** Transferible como **zona** (`bar_time` de las coordenadas del FVG original); cae en el mismo gap que el IFVG nativo del HTF.

##### 6.3.24 BPR — Balanced Price Range (§5.3 · #44 cand.) *(fallo #1 variante)*

- **Variante correcta / desempate.** Intersección de un FVG **alcista** con uno **bajista** creados en `≤bprWindow` velas (20), altura `≥bprMinOverlap×ATR` (0.05), §5.3 → `KIND_BPR` = `[max(bottoms), min(tops)]`, `dir` neutro (reacción bidireccional). EL relevante = el solape **vivo** más cercano. **Descarta** (citable): dos FVG del **mismo** lado, o dos opuestos que **no se tocan** (§5.3 contraejemplo) → no hay BPR. Opuesto conceptual del IPR (§6.3.29: mismo lado, apilados).
- **Fuerza (0–1).** `altura de la intersección ×ATR` (solape mayor = zona de reacción más fuerte) · `trueFvg de los gaps que lo forman` · `frescura` (`state`) · `proximidad al precio`. Quant: **alta** (solape amplio de dos True FVG frescos), **media** (solape normal), **baja** (solape mínimo cerca del umbral).
- **Invalidación externa.** El precio cierra a través de toda la zona → BPR mitigado/anulado. La dirección de reacción la da el **contexto** (P/D, bias), no el BPR en sí. DÓNDE: `f_updateZoneMitigation` (Pine); el sesgo lo aporta el scoring.
- **Visual (jerarquía).** **Primario:** BPR fresco cercano → caja con doble borde (zona de equilibrio). **Secundario:** lejano/parcial. **Terciario:** mitigado → panel T14. Toggle `i_showBPR`. *(Ventana: 15 solapes, p.ej. BPR 05-28 [1.16235, 1.16260].)*
- **MTF.** Transferible como **zona** (`bar_time`); cae en la misma intersección que el BPR nativo del HTF.

##### 6.3.25 Immediate Rebalance (§5.4) *(fallo #1 variante — matiz de contexto)*

- **Variante correcta / desempate.** Lo **contrario** al FVG: vela de impulso (`rango≥irFactor×ATR`=1.0, `cuerpo≥irBodyPct`=0.60) cuyo desequilibrio es **rebalanceado de inmediato** por la vela siguiente (cierra de vuelta dentro del cuerpo), §5.4 → `KIND_IR`, evento puntual. EL relevante = el IR que confirma que **no quedará FVG imán** ahí. **Descarta** (citable): vela de impulso que **deja FVG** (la siguiente no rellena, §5.4 contraejemplo) → es contexto de FVG (§2.2), NO Immediate Rebalance.
- **Fuerza (0–1).** Es **matiz de contexto, no zona operable** (§5.4): su "fuerza" = `cuán completo fue el rebalance` (qué fracción del cuerpo se devolvió). No genera marca de entrada con `strength` alta; informa que la ineficiencia se curó. Quant: **baja**/informativa.
- **Invalidación externa.** N/A operativo (es marca histórica P4). Si retrospectivamente queda hueco residual, se reclasifica a FVG. DÓNDE: detección (Pine).
- **Visual (jerarquía).** **Terciario** por defecto (marca histórica, peso bajo): pequeño marcador o solo en panel T14. Toggle `i_showIR`. *(Ventana: 11 IR.)*
- **MTF.** Rara vez se transfiere (evento de microestructura del TF); cap mínimo.

##### 6.3.26 Volume Imbalance — SIVI / BIVI (§5.5 · #46 cand.) *(fallo #1 variante)*

- **Variante correcta / desempate.** Micro-gap entre **cuerpos** de velas consecutivas con **mechas solapadas** (`open[i]` con gap ≥`viThreshold×ATR`=0.05 sobre `close[i-1]`, y mechas se tocan), §5.5. **BIVI** alcista / **SIVI** bajista. **Una sola confluencia** para la familia `[FIX P-05]` (no 3×). EL relevante = el VI más cercano sin mitigar. **Descarta** (citable): gap **sin** solape de mechas (`low[i]>high[i-1]`, §5.5 contraejemplo) → es FVG/gap real (§2.2), NO Volume Imbalance (el VI exige que las mechas se toquen).
- **Fuerza (0–1).** `tamaño del gap de cuerpo ×ATR` (micro por naturaleza) · `frescura` (`state`) · `¿en zona de displacement?`. Inherentemente **baja-media** (es microestructura). Quant: **media** (VI grande en impulso), **baja** (micro típico).
- **Invalidación externa.** El precio rellena el micro-gap → mitigado. DÓNDE: `f_updateZoneMitigation` (Pine); scoring (1 confluencia familia).
- **Visual (jerarquía).** **Terciario** por defecto (microestructura, satura fácil): solo en `i_densidad=Todo` o panel T14. **Secundario** si confluye con zona mayor. Toggle `i_showVI`. *(Ventana H1: 13; M5: 53 — coherente con su naturaleza micro.)*
- **MTF.** **No** se transfiere a TF menores (ya es lo más fino); en HTF puede tener valor puntual con cap mínimo.

##### 6.3.27 CISD — Change in State of Delivery (§5.6 · #47 cand.) *(fallo #1 desempate + #3 invalidación)*

- **Variante correcta / desempate.** Giro **más temprano y fino** que el CHoCH: tras un run de `≥cisdMinRun` velas del mismo color (default 2), el precio **cierra cruzando el `open` origen del run** (§5.6). **Distinto de CHoCH/MSS** (rompe el *open de la pierna*, no un pivote swing → ocurre antes; guard obligatorio). EL relevante = el CISD sobre el run de delivery más largo/reciente. **Descarta** (citable): cierre que cruza el open de **una sola** vela (run de 1, §5.6 contraejemplo) → ruido (39 señales/300 velas con minRun=1; con ≥2 → 8 distinguibles).
- **Fuerza (0–1).** `longitud del run de delivery` (run de 6 del 06-05 12:00 = shift mayor > run de 2) · `displacement del cierre de giro ×ATR` (§4.1) · `alineación con el bias esperado`. Quant: **alta** (run largo + giro con displacement, 06-05 12:00), **media** (run de 2–3 limpio), **baja**: run de 1 no es CISD.
- **Invalidación externa.** Si el precio retoma la dirección del run original tras el CISD → el cambio de entrega no se sostuvo. Si además rompe el pivote swing → ya es CHoCH/MSS (no lo duplica). DÓNDE: cadena ADR-012 **Q3**; scoring (#47).
- **Visual (jerarquía).** **Primario:** CISD de run largo (shift mayor) → marca + etiqueta "CISD". **Secundario:** CISD de run de 2–3. **Terciario:** N/A (run de 1 ya filtrado). Toggle `i_showCISD`. *(Ventana: 8 CISD.)*
- **MTF.** Transferible como **marca** (`bar_time` del cierre de giro); cae en el mismo punto que el CISD nativo del HTF; gatillo fino más útil en LTF.

##### 6.3.28 Vacuum Block (§5.7 · #48 cand.) *(fallo #1 variante)*

- **Variante correcta / desempate.** Un **único gap grande de apertura** (frontera de día/semana del broker) `≥vacuumFactor×ATR` (0.5), §5.7 → `KIND_VACUUM` = `[min,max]` de `(close[i-1], open[i])`, imán de retorno. EL relevante = el Vacuum no rellenado más cercano. **Descarta** (citable): micro-gap de cuerpo con mechas solapadas <0.5×ATR (§5.7 contraejemplo) → es Volume Imbalance (§5.5), NO Vacuum (el Vacuum exige salto grande de apertura). Distinto de FVG (hueco de 3 velas).
- **Fuerza (0–1).** `tamaño del gap ×ATR` (0.72/0.53/0.85×ATR en los casos) · `frescura` (no rellenado) · `tipo de frontera` (semanal NWOG > diaria). Quant: **alta** (gap semanal grande no rellenado), **media** (gap de día), **baja** (cerca del umbral).
- **Invalidación externa.** El precio rellena el gap → mitigado (cumplió de imán). DÓNDE: `f_updateZoneMitigation` (Pine); scoring (#48).
- **Visual (jerarquía).** **Primario:** Vacuum grande no rellenado → caja + etiqueta. **Secundario:** parcial. **Terciario:** rellenado → oculto. Toggle `i_showVacuum`. *(Ventana FX: 3, todos en frontera 21:00 GMT — escasos en FX, más frecuentes en índices/futuros con cierre, ADR-001.)*
- **MTF.** Transferible como **zona** (`bar_time` de la frontera); coincide con NWOG (§6.3.32); cae en el mismo gap del HTF.

##### 6.3.29 IPR — Imbalanced Price Range (§5.9 · #49 cand.) *(fallo #1 variante — es contexto/bias)*

- **Variante correcta / desempate.** `≥iprMinGaps` FVG del **mismo `dir`** en `≤iprWindow` velas sin opuesto que neutralice (default 3/10), §5.9 → `KIND_IPR` = `[min(bottoms), max(tops)]`, **contexto/bias** (no zona puntual). EL relevante = la ventana con más gaps apilados unidireccionales. **Descarta** (citable): ventana con FVG **mezclados** (§5.9 contraejemplo) → balanceada, tiende a BPR/equilibrio (§5.3), NO IPR. Opuesto del BPR (§6.3.24).
- **Fuerza (0–1).** `nº de gaps apilados del mismo lado` (más = más desbalance = más "tirón") · `tamaño total del rango ×ATR` · `alineación con bias`. Es **input de bias**, no voto puntual (§5.9). Quant: **alta** (≥4 gaps apilados en impulso direccional), **media** (3 gaps).
- **Invalidación externa.** Aparición de gaps opuestos en la ventana → se rebalancea, el IPR se disuelve. DÓNDE: scoring/motor de bias (modulador, no voto); cadena ADR-012 **Q1**.
- **Visual (jerarquía).** **Secundario** (es zona de contexto, no entrada): sombreado del rango desbalanceado. **Terciario:** disuelto → panel T14. Toggle `i_showIPR`. *(Ventana: 5 IPR, en tramos de impulso.)*
- **MTF.** Transferible como **rango de contexto** (`bar_time`); se hereda como modulador de bias del HTF en panel T14.

##### 6.3.30 Inside Day (§5.12 · #50 cand.) *(fallo #1 variante — contexto de volatilidad)*

- **Variante correcta / desempate.** Día D1 con `high[D]<high[D-1]` **y** `low[D]>low[D-1]` (contención de ambos extremos, §5.12) → `KIND_INSIDEDAY`, compresión que precede expansión, `dir` neutro (la ruptura del rango previo lo define). EL relevante = el inside day **más reciente** confirmado (D1 cerrado, anti-repaint). **Descarta** (citable): día con `high` mayor **o** `low` menor (outside/trending day, §5.12 contraejemplo) → no es inside day (rompe la contención).
- **Fuerza (0–1).** `cuán contenido` (rango D vs rango D-1; más estrecho = más compresión = expansión más probable) · `nº de inside days consecutivos` (compresión acumulada). Es **contexto de volatilidad, peso bajo** (§5.12). Quant: **media** (contención fuerte), **baja** (contención marginal).
- **Invalidación externa.** Una vez el precio **rompe** el rango del día previo → el inside day se "resuelve" (la dirección de ruptura pasa a mandar). DÓNDE: scoring (#50, peso bajo); el bias lo da la ruptura.
- **Visual (jerarquía).** **Secundario/Terciario:** marca en la barra D1 o sombreado del rango contenido (heredado a M5). Toggle `i_showInsideDay`. *(Ventana: 3 inside days: 05-31, 06-02, 06-11.)*
- **MTF.** Es un patrón **D1**; se hereda a H1/M5 como sombreado del rango D1 contenido (visibilidad cruzada por `bar_time`, §6.3.35).

##### 6.3.31 Standard Deviation (§5.11) — **HERRAMIENTA, no confluencia** *(no aplica fallo de discriminación)*

- **Variante correcta / desempate.** **No es una zona detectada** (§0.9/§5.11): es una **proyección** `nivel(k)=B+k·(B−A)` para `k∈{−1,−2,−2.5,−4}` sobre un rango ancla (pierna de manipulación / dealing range). No hay "variante relevante entre candidatos": hay un cálculo determinista de objetivos. **Descarta** (citable): usarla como confluencia que **suma al score** (§5.11 contraejemplo) → error de categoría (es proyección de TP, no señal).
- **Fuerza (0–1).** **N/A** — no tiene `strength` de marca. Alimenta `f_computeSLTP` (TP del motor EA), no el scoring.
- **Invalidación externa.** N/A (es una regla/fórmula). El ancla se redibuja con cada nuevo rango.
- **Visual (jerarquía).** **Líneas de objetivo** (no marca de confluencia): niveles −1/−2/−2.5/−4 como targets opcionales. **Terciario** por defecto (solo cuando se estudia SL/TP). Toggle `i_showStdDev`.
- **MTF.** Se proyecta sobre el rango del TF que se opera; los niveles son globales una vez fijado el ancla.

##### 6.3.32 Serie de gaps de apertura — NWOG/NDOG/NYMO/ORG + Breakaway (§5.10 · #45 cand. Breakaway) *(fallo #1 variante)*

- **Variante correcta / desempate.** Extiende Session Opens (§4.2/§6.3.21) como **serie de niveles**: en cada frontera (semana/día broker/00:00 NY) capturar `(close_previo, open_nuevo)`. **Nivel ancla** siempre (NWOG/NDOG/NYMO); **gap medible** si `≥gapMin×ATR` (0.5); **Breakaway Gap** (`KIND_BAG`) si el gap **además rompe estructura** (BOS §1.3 en su dir) → gap direccional. EL relevante = el ancla más cercana / el Breakaway si rompe estructura. **Descarta** (citable): `open` ≈ `close` previo (gap <0.5×ATR, típico FX intradía, §5.10 contraejemplo) → solo aporta el **nivel** (#36 serie), no zona-gap ni Breakaway.
- **Fuerza (0–1).** Para el **nivel**: `proximidad ×ATR` + jerarquía (NWOG semanal > NDOG diario). Para el **Breakaway**: `tamaño del gap ×ATR` + `¿confirmó BOS?` (binario, lo hace direccional) + `alineación`. Quant: **alta** (Breakaway que rompe estructura), **media** (gap medible neutro), **baja** (nivel ancla puro).
- **Invalidación externa.** Gap rellenado → nivel mitigado; Breakaway negado si el BOS se revierte. DÓNDE: scoring (#36 serie / #45 Breakaway); cadena ADR-012 **Q1/Q3**.
- **Visual (jerarquía).** **Primario:** NWOG y Breakaway → líneas ancla persistentes + punto medio. **Secundario:** NDOG/NYMO. **Terciario:** gaps viejos rellenados → ocultos. Toggle `i_showOpeningGaps`. *(Ventana FX: NWOG fin de semana 06-07 ~0.85×ATR, 05-31 ~0.72×ATR; gaps diarios ≈0.)*
- **MTF.** Niveles **globales** (mismos en todo TF), se heredan a M5 naturalmente; el Breakaway transfiere su `bar_time` de frontera.

##### 6.3.33 SMT Divergence (§5.13 · #51 cand.) — **requiere símbolo correlacionado (ADR-011)** *(fallo #1 variante)*

- **Variante correcta / desempate.** Divergencia entre el chart y un `smtSymbol` correlacionado (default EURUSD↔GBPUSD **correlación positiva**, ADR-011): uno hace HH/LL y el otro **no confirma**, equiparados por `smtTol` velas (3), §5.13 → `KIND_SMT`. EL relevante = la divergencia en el swing equiparable más reciente. **Descarta** (citable): ambos símbolos hacen **el mismo** extremo (se confirman, §5.13 contraejemplo) → no es SMT (exige que **uno falle** en confirmar).
- **Fuerza (0–1).** `claridad de la divergencia` (cuánto falla el correlacionado en confirmar) · `escala del swing divergente` (swing > interno) · `¿coincide con sweep de liquidez?` (§3.2 — uno barrió, el otro no = manipulación confirmada). Señal de **calidad alta** (§5.13). Quant: **alta** (divergencia de swing dominante con sweep), **media** (divergencia de swing simple).
- **Invalidación externa.** Si el símbolo rezagado **luego confirma** el extremo → la divergencia se cierra (no era manipulación). DÓNDE: scoring (#51 fuerte); cadena ADR-012 **Q4** (es manipulación de liquidez).
- **Visual (jerarquía).** **Primario:** SMT confirmado → marca de divergencia + etiqueta en ambos extremos. **Secundario/Terciario:** N/A (siempre relevante si existe). Toggle `i_showSMT`. *(No verificable con `eurusd_h1.csv` — un solo símbolo; casos en pasada TV con el par correlacionado tras ADR-011.)*
- **MTF.** Transferible como **marca** (`bar_time` del swing divergente); requiere el 2º `request.security` aplanado (ADR-009) en cada TF.

##### 6.3.34 RTH vs ETH (§5.15 · modula #34) — **N/A en FX (Fase 5, par nuevo)** *(no aplica a EURUSD)*

- **Variante correcta / desempate.** Por `rthProfile` (input por símbolo): hora local en ventana RTH → `RTH`, si no → `ETH` (§5.15). Modula el peso de #34. **EURUSD (FX 24h) → no aplica** (§5.15 contraejemplo): el perfil FX neutraliza (RTH≡ETH, toda hora es "regular"). EL relevante solo en instrumentos con sesión acotada (índices/futuros, p.ej. RTH 09:30–16:00 NY).
- **Fuerza (0–1).** **N/A en FX.** En instrumentos acotados: `¿RTH?` (binario, sube el peso de #34; ETH = menor calidad). Quant (no-FX): **alta** RTH, **baja** ETH.
- **Invalidación externa.** No invalida (modula #34). En FX está **desactivado** por perfil. DÓNDE: scoring (#34, solo no-FX).
- **Visual (jerarquía).** En FX: **no se dibuja** (perfil neutraliza). En no-FX: sombreado RTH/ETH del fondo. Toggle `i_showRTH` (oculto en perfil FX).
- **MTF.** Contexto de reloj del TF propio (como KZ §6.3.16); no se transfiere como objeto.

#### MTF — Herencia cross-timeframe

##### 6.3.35 Herencia D1/H1 (bias + P/D + zonas) en M5 *(fallo #1 desempate — qué baja y con qué prioridad)*

- **Variante correcta / desempate.** El M5 hereda del HTF: **bias dominante** (§6.3.4), **bandas P/D** (§6.3.5), **zonas** (OB/FVG/breaker/pools) ancladas por `bar_time`/nivel (ADR-010). EL relevante en M5 = la herencia HTF **más cercana al precio** dentro del presupuesto top-N (`f_nearestN`/`f_nearestNPools`). **Descarta** (citable): saturar M5 con todas las zonas HTF → se respeta el cap top-N por familia; el resto se **cuenta** en panel T14 (no se dibuja). Anti-duplicado con la estructura nativa M5 (S042: si el evento HTF coincide con el nativo, no se redibuja).
- **Fuerza (0–1).** La marca heredada conserva el `strength` de su origen HTF, **modulado por `cap/cercanía MTF`** (§6.1, `f_nearestN`, 0–10) — el cap 0–10 es el presupuesto de tinta, **distinto** del `strength` 0–1 y del nivel visual (gotcha S054). Quant: hereda alta/media/baja del HTF; las que no entran en el cap caen a Terciario.
- **Invalidación externa.** Una zona HTF invalidada en su TF de origen deja de heredarse a M5. DÓNDE: estado de la zona en su TF (Pine, vía ADR-010); el panel T14 refleja el conteo HTF.
- **Visual (jerarquía).** **Primario:** bias dominante + P/D + top-N zonas HTF cercanas (con tag `(D1)`/`(H1)` — pendiente diferido (a), metodología §6.b). **Secundario:** zonas HTF medias. **Terciario:** sobrantes del cap → panel T14. Master input `i_densidad` (Operación/Estudio/Todo) filtra por nivel.
- **MTF.** **Es** la capa MTF: la dirección de transferencia es siempre HTF→LTF (`lookahead_off`, §0); nunca LTF→HTF. Los 3 pendientes diferidos (tag D1/H1, cuadre EQH/EQL, exactitud vela OB/FVG) se cierran aquí (metodología §6.b).

---

## 7. CAPA DE PROYECCIÓN / CONFLUENCIA (relevancia estructural) — *lee-atrás · proyecta-adelante · outcome*

> **Estado: EN RELLENO (Sesion-093+).** Capa **aditiva** sobre §1–§6 — igual que la §6 lo fue sobre §1–§5. **NO modifica ninguna definición, umbral ni `strength` de §0–§6** (siguen byte-idénticas). **NO añade confluencias al catálogo §4.8** (siguen 42+expansiones aprobadas): `posRole/confDegree/depthBand` son **moduladores/lecturas**, mismo estatus que `strength` (ADR-014 §3). Migra la doctrina de `ESQUELETO-FABLE-proyeccion-confluencia.md §2` a su destino normativo bajo gate [[sprint16-gate-reglas-antes-de-codigo]]: **cada ficha se cuantifica + casos EURUSD ANTES de codificar su selección** en Fase A (Visual-only). Todos los números son **candidatos CONGELADOS hasta Fase 3** (ADR-002).
>
> **Qué reformula (decisión Freddy S092):** la importancia deja de ser `fuerza × cercanía` y pasa a ser **relevancia estructural + confluencia, leída como proyección**. Cambia UNA cosa concreta en Pine: la llave de orden del render (`score_render` → `score_render_v2`, §7.1), que vive en `SMC-Visual.pine`. La **detección** (§1–§5) y el **grading** (§6) no se tocan. Lo único que cambia es **cuál** de las instancias ya detectadas recibe tinta en Operación y **qué escenario proyecta**.
>
> **Fuente única (§0 del esqueleto):** la doctrina se escribe UNA vez aquí; los cuatro consumidores (render Pine, score direccional F2, cuaderno EA F4, debate del enjambre) LEEN derivaciones de los mismos tres primitivos, no re-implementan. Frontera CORE/Visual (ADR-014): los primitivos son detección → CORE, pero se implementan en **dos fases** — fase A aproximación Visual-only (leyendo arrays del CORE, SHA intacto), fase B los promueve al CORE en Fase 2 (ADR nuevo + SHA nuevo). Las fórmulas de A y B son idénticas; solo cambia el archivo.

### 7.0 Los tres primitivos de proyección (normativos — fuente de render + score + EA + enjambre)

> Se calculan **por instancia detectada** (zona/evento/pool ya existentes en §1–§5), al cierre, sobre datos confirmados (anti-repaint). No crean detección nueva: leen `SMC_swings`/`SMC_events`/`SMC_zones`/`SMC_pools` + P/D (§2.3). Candidatos CONGELADOS (ADR-002).

#### 7.0.1 `posRole` — posición estructural `{0=INTERNO, 1=GIRO, 2=ORIGEN}`

- **Qué codifica.** El rol de la instancia en la narrativa estructural: ¿es un **GIRO** (el HH/LL donde se tomó liquidez y el precio se desplazó al lado contrario), el **ORIGEN** de un desplazamiento que rompió estructura (la vela/zona que lanzó el BOS/CHoCH vigente), o **INTERNO** (media tendencia, ruido de proyección)? Es la variable #1 de importancia (manda sobre la cercanía).
- **Regla determinista (cuantificada).**
  - **GIRO (1):** la instancia se solapa `±tolPos×ATR` (cand. **0.5×ATR14**) con un swing dominante (`majorLen=50`, §1.1) que fue **seguido** de CHoCH/MSS (§1.4/§1.5) o de un sweep contrario (§3.2) dentro de las siguientes `posLookfwd` velas (cand. **20**). Es decir: el extremo donde el mercado cambió de mano.
  - **ORIGEN (2):** la instancia **nace** (su `barIdx` de creación) en el arranque de la pierna cuyo desplazamiento (§4.1: `≥1.5×ATR ∧ cuerpo≥70%`) produjo el BOS/CHoCH **vigente**. Compara `zona.barIdx` contra el `originBarIdx` del evento estructural vigente (ambos ya viajan en los UDTs).
  - **INTERNO (0):** resto (no solapa giro ni es origen del evento vigente).
  - **Desempate (borde):** una instancia que es GIRO **y** ORIGEN a la vez → **ORIGEN gana** (`posRole=2`; el origen del desplazamiento pesa más que el pivote).
- **Peso en la llave (§7.1):** `wPos` = ORIGEN **1.0** · GIRO **0.9** · INTERNO **0.35** (CONGELADO). Lo interno se detecta y se **cuenta** (panel T14), nunca se resalta en Operación.
- **Casos EURUSD (pasada TV S094, live H1 04-07, px 1.14376, ATR14 0.00085).** **GIRO+ORIGEN → ORIGEN gana:** MSS H1 **1.13827 · 01-07 12:00** — giro dominante vigente (extremo inferior del tramo) y a la vez origen de la pierna vigente. **ORIGEN puro:** OB D1 **[1.15726,1.16221]** (premium, origen de la pierna bajista dominante, §6.2.1). **INTERNO:** BOS M5 **1.14380 · 03-07 19:35** (continuación fina, no voltea el swing dominante, §6.3.3). *Verificación fina `posLookfwd=20`/`tolPos=0.000425` pendiente en A-2 (confirmar solape del MSS 1.13827 con el swing `majorLen=50` roto dentro de 20 velas).* Caso histórico archivado (S092): MSS 06-01 13:00 (displacement 3.51×ATR); OB bajista 06-05 11:00 [1.16345,1.16420].
- **Frontera / `[impl]`.** Fase A: `f_posRole(top, bot, barIdx)` en Visual (`[impl B-2]`). Fase B: al CORE (ADR-01X).

#### 7.0.2 `confDegree` — grado de confluencia `int ≥ 0`

- **Qué codifica.** Nº de **familias distintas** con una instancia **activa** apilada en `±tolConf×ATR` del nivel. Es la versión sin pesos del score de confluencia direccional (§7.1 identidad central): lo que el chart resalta y lo que el score suma son la **misma** lectura del apilamiento.
- **Regla determinista (cuantificada).** `tolConf` = **0.25×ATR14** (CONGELADO; deliberadamente igual a `labelClusterTol` §6.2 — el cluster de labels y el apilamiento son el mismo fenómeno). **Familias contadas (una por familia, no por instancia):** {OB/Breaker} · {FVG/IFVG/BPR} · {pool BSL/SSL} · {EQH/EQL} · {IDM} · {gap NWOG/NDOG} · {zona OTE/GP}. Las EMAs (§4.3) **NO** cuentan (son confluencias #37–42 propias, no de zona). Se cuenta SOLO en `islast` y SOLO para los candidatos finalistas de cada banda (O(candidatos×arrays), acotado) — nunca por vela. Contador `int` por candidato, **cero arrays nuevos** (RE10045-safe).
- **Umbral de promoción (regla transversal §7.2):** `confDegree ≥ 2` **fuerza** nivel visual ≥ Secundario aunque la familia sea de Estudio (la confluencia promociona, nunca degrada). Se evalúa **después** del whitelist por modo §8.2 (única excepción documentada a la matriz por modo).
- **Peso en la llave (§7.1):** `1 + kConf × min(confDegree, 3)`, `kConf` = **0.25** (CONGELADO). Se satura a 3 familias (evita que un cluster raro domine).
- **Casos EURUSD (pasada TV S094, tolConf=0.25×ATR14=0.000213).** **≥2 (promociona) #1:** OB M5 [1.14380,1.14406] + Pool **1.14408 BSL** (top OB 1.14406 vs pool 1.14408 = 0.00002 < tol) = {OB}+{pool} → **confDegree 2** (banda 1 arriba, junto al precio). **≥2 (promociona) #2:** OB D1 [1.15726,1.16221] + FVG D1 [1.15283,1.15748] (OB low 1.15726 vs FVG top 1.15748 = 0.00022, dentro de tolConf D1) = {OB}+{FVG} → **confDegree 2** (premium, banda 3 arriba). **=1 (contraejemplo, NO promociona):** OB H1 [1.13740,1.13794] — ninguna otra familia contada dentro de tol (sweep 1.13722 no es familia contada; MSS 1.13827 a 0.00033 > tol) → **confDegree 1** (banda 3 abajo). La tolerancia 0.25×ATR ya está validada como `labelClusterTol` en la consolidación §6.2 vigente.
- **Frontera / `[impl]`.** Fase A: `f_confDegree(level)` en Visual (`[impl B-3]`). Fase B: al CORE.

#### 7.0.3 `depthBand` — banda de profundidad de proyección `{1..5}`

- **Qué codifica.** En qué **banda de retroceso** del dealing range vigente (§2.3) cae la instancia, medida desde el precio hacia el origen de la pierna dominante. Es el eje que sustituye a "cercanía": la proyección tiene **profundidades** (escenarios), no una sola distancia.
- **Regla determinista (cuantificada).** Sobre el rango vigente `[origen_pierna, extremo]` (ya disponible vía P/D §2.3), fracción de retroceso `r` desde el precio actual hacia el origen:
  - **banda 1** = `r ∈ [0, 0.33]` — retroceso corto (toca y sigue; escenario más probable/operable).
  - **banda 2** = `r ∈ (0.33, 0.66]` — retroceso medio.
  - **banda 3** = `r ∈ (0.66, 1.0]` — el origen / inducement inicial (soporte último de la pierna).
  - **bandas 4/5** = **fuera del rango vigente, más atrás en el tiempo**: niveles del dealing range **previo** (4) y del **anterior a ese** (5). Se habilitan solo con `i_profundidad` ≥ 4/5.
  - Cortes `{0.33, 0.66, 1.0}` CONGELADOS. "Un representante por banda por lado" = el mejor `score_render_v2` de cada celda (§7.1), no los N más fuertes en bruto.
- **Selección "3 por lado" = MÍNIMO doctrinal, no cap.** Default `i_profundidad = 3` (bandas 1–3). El usuario pide el 4.º/5.º "más atrás" con el input (min 3, max 5). No es filtro de calidad: es alcance temporal/espacial de la proyección.
- **Casos EURUSD (pasada TV S094, live H1 04-07).** Rango vigente (§2.3): **[1.13618, 1.16221]**, EQ 1.14919, px 1.14376 (Discount 29%). Cortes 0.33/0.66/1.0. **Arriba (hi, hacia origen 1.16221):** banda1 [1.14376–1.14985] = OB M5 [1.14380,1.14406] · FVG M5 [1.14562,1.14590]; banda2 [1.14985–1.15594] = FVG D1 [1.15283,1.15748] · UQ 1.15570; banda3 [1.15594–1.16221] = OB D1 [1.15726,1.16221] · Premium 1.16221. **Abajo (lo, hacia extremo 1.13618):** banda1 [1.14126–1.14376] = FVG H1 [1.14309,1.14360] · Pool H1 1.14207 SSL; banda2 [1.13874–1.14126] = BOS H1 1.14095 (sin OB/FVG limpio en esta banda); banda3 [1.13618–1.13874] = OB H1 [1.13740,1.13794] · MSS 1.13827 (GIRO). **Bandas 4/5 (rangos previos):** proxy D1 Discount 1.13246 / Premium 1.20831. **TODO** (`[impl B-4]`): archivar los 2 rangos previos con escalares que rotan (patrón de los grids P3, §5.16 — sin arrays nuevos).
- **Frontera / `[impl]`.** Fase A: `f_depthBand(level, px)` + `i_profundidad` en Visual (`[impl B-4/B-5]`). Fase B: al CORE.

### 7.1 La llave de render v2 + guardián de draws (normativo — sustituye fuerza×cercanía)

> Vive en `SMC-Visual.pine` (fase A). Es lo ÚNICO que se **sustituye** del render actual; el resto del pipeline visual (capas §3, color §5, antisolape §6, MTF §7, matriz §8.2, checklist §10 del esqueleto visual) se **conserva**.

- **Llave nueva (`[impl B-1]` `f_renderScoreV2`):**
  ```
  score_render_v2 = strength × wPos(posRole) × (1 + kConf × min(confDegree, 3))
     wPos: ORIGEN=1.0 · GIRO=0.9 · INTERNO=0.35     kConf = 0.25     (CONGELADOS)
     La cercanía NO entra: la profundidad la codifica depthBand.
     Tie-break dentro de una banda: mayor strength; a igualdad, más fresco.
  ```
  `f_renderScore` (cercanía) se **conserva** para las anclas §2.3 hasta migrarlas — no se regresa lo ya aprobado.
- **Selección por bandas (`[impl B-7]`):** en la pasada `islast` de anclas, rastrear por **concepto (OB/FVG/Breaker/IDM) × lado (hi/lo) × banda (1..i_profundidad)** el mejor `score_render_v2`, guardando **índice** por celda (≤ 4×2×5 = **40 escalares int**, sin arrays → RE10045-safe). Cada drawer compara su `i` contra la celda → `isBandPick` → dibuja aunque `f_densOK` diga no.
- **Guardián de draws (`[impl B-6]` — regla dura anti-recorte):** una instancia con `confDegree ≥ 2`, **o** un pool alineado al bias como draw objetivo, es **inmune al recorte** por distancia/frescura (top-N, desalojo §6.5, curado MTF) — se trata como **mandatoria**, mismo rango que anclas/MTF. El desalojo compensa cortando más INTERNO discrecional. **Corrige el "adiós al BSL 1.51":** un pool/EQ/old-high fuera del rango P/D se mantiene si es objetivo de proyección. El rango P/D es **contexto de razonamiento (dónde comprar/vender barato/caro), JAMÁS tijera de draws**.
- **Congelados (ADR-002):** ver §9 del esqueleto — `wPos {1.0/0.9/0.35}` · `kConf 0.25` · `tolConf 0.25×ATR` · `tolPos 0.5×ATR` · bandas `{0.33/0.66/1.0}` · `i_profundidad {3..5}` · promoción `confDegree≥2`.

### 7.2 Fichas por concepto/variación (migración de `ESQUELETO-FABLE §2`)

> **Plantilla por ficha:** *Lee-atrás* (qué la causó) · *posRole requerido* (para tinta en Operación) · *confDegree* (umbral de promoción) · *depthBand* (bandeo) · *Proyección adelante* (escenario + outcome verificable §4.3) · *MTF · Modo mín.* · *Casos EURUSD*. Los casos que NO cumplen su criterio se **detectan igual** (arrays + panel T14), pero no reciben tinta en Operación. Granularidad **por variación** (FVG ≠ trueFVG ≠ IFVG ≠ BPR: misma familia/hue/capa, doctrina distinta). Reutiliza la detección §1–§5 y el `strength` §6 — **no los redefine**.
>
> **Regla transversal:** cuando una ficha dice "sube a Operación con confluencia", el mecanismo es único: `confDegree ≥ 2` fuerza nivel visual ≥ Secundario (la confluencia promociona, nunca degrada; se evalúa tras el whitelist §8.2).

#### A1 · Estructura (`GRP_STRUCT`, capa L3 — teal/rojo) — fichas 1–7

##### 7.2.1 Swing interno (§1.1 · `internalLen=3`)

- **Lee-atrás.** Pivote menor dentro de una pierna. Alimenta la detección de IDM y de legs; no es objeto de proyección por sí mismo.
- **posRole requerido.** Ninguno en tinta: es material de detección (INTERNO por naturaleza). **No recibe tinta en Operación** bajo ningún `confDegree`.
- **confDegree.** No promociona (excepción explícita: un swing interno nunca sube a Operación aunque apile — lo que apila es la **zona** que lo contiene, no el pivote).
- **depthBand.** n/a (no bandeado).
- **Proyección.** No proyecta; es insumo. Se **cuenta** en panel T14 / modo Todo.
- **MTF · Modo mín.** No baja a TF menores · **Todo**.
- **Casos EURUSD.** Los swings internos `internalLen=3` ya detectados en §1.1 (marca fina, modo Todo).

##### 7.2.2 Swing dominante HH/HL/LH/LL (§1.1 · `majorLen=50` / §6.3.4)

- **Lee-atrás.** El pivote del tramo que define el bias. La traza completa NO importa; importa **dónde giró el mercado**.
- **posRole requerido.** **SOLO los de GIRO** — el HH/LL donde se tomó liquidez y el precio se desplazó al lado contrario. Los HH/HL/LH/LL de continuación (media traza) → INTERNO → panel/Estudio.
- **confDegree.** Refuerza pero no es requisito (el giro dominante ya es Primario por `posRole=GIRO`, `wPos=0.9`).
- **depthBand.** 1 por banda por lado: los **3 giros que estructuran el rango vigente** (banda 1/2/3). Con `i_profundidad ≥ 4` aparecen los giros de rangos previos.
- **Proyección.** El giro dominante proyecta el **bias**: desde él se mide el dealing range (§2.3) y las bandas. Outcome = ¿el precio respeta el giro como extremo del rango o lo rompe (nuevo giro)?
- **MTF · Modo mín.** El giro dominante D1 baja a H1/M5 con tag (§7.4 esqueleto visual, ya) · **Estudio** (labels) / **el giro vigente en Operación**.
- **Casos EURUSD (pasada TV S094, rango [1.13618,1.16221]).** Los **3 giros que estructuran el rango vigente:** (1) giro inferior = **MSS 1.13827 · 01-07 12:00** (GIRO vigente, extremo bajo del tramo, §6.2.5); (2) giro superior = zona premium **~1.16221** (origen de la pierna bajista dominante, D1 OB/Premium); (3) giro intermedio = **CHoCH H1 1.14119 · 02-07 08:00** / BOS 1.14095 · 30-06 (quiebre que define el sub-rango actual). Con `i_profundidad ≥ 4`: giros de rangos previos (proxy D1 Premium 1.20831 / Discount 1.13246).

##### 7.2.3 BOS interno (§1.3 · `internalLen=3` / §6.3.3)

- **Lee-atrás.** Continuación en estructura menor (gatillo fino / IDM).
- **posRole requerido.** INTERNO por definición → **nunca en Operación**. Estudio solo si `strength` alta (buen gatillo alineado al bias swing con displacement, §6.3.3).
- **confDegree.** No promociona a Operación por sí solo (es estructura fina).
- **depthBand.** n/a (evento puntual).
- **Proyección.** Confirma la continuación de la pierna vigente dentro de su banda; no abre escenario nuevo.
- **MTF · Modo mín.** No baja · **Estudio**.
- **Casos EURUSD.** BOS/CHoCH interno §6.3.3 (06-02 04:00, gatillo a favor del bias bajista).

##### 7.2.4 BOS swing/dominante `+` (§1.3 / §6.3.2 / §6.3.4)

- **Lee-atrás.** Continuación confirmada del bias (rompe por `close` el swing que extiende).
- **posRole requerido.** **ORIGEN implícito** — el BOS vigente + el que abrió la pierna actual (su origen = ancla del OB causal, §7.2.8). Es evento de proyección: define hacia dónde continúa.
- **confDegree.** No requiere (el BOS vigente es Primario por rol).
- **depthBand.** El **vigente** (banda del precio) + el origen de la pierna (banda 3, ancla del OB causal).
- **Proyección.** Proyecta el **draw** de continuación (el pool objetivo del bias, §7.2.22). Outcome = ¿alcanza el draw antes de un CHoCH contrario?
- **MTF · Modo mín.** Hereda SIEMPRE con tag (ya) · **Operación**.
- **Casos EURUSD.** BOS swing de §6.3.2 (base de ruptura `close`, contraejemplo sweep 05-27 12:00).

##### 7.2.5 CHoCH (§1.4 / §6.3.2)

- **Lee-atrás.** Primer quiebre contra-tendencia = **aviso de giro** (rompe el swing que protege).
- **posRole requerido.** El **vigente** (define el posible giro en curso → posRole=GIRO candidato). Los CHoCH históricos → Estudio.
- **confDegree.** Refuerza; un CHoCH vigente en un giro con `confDegree≥1` (CHoCH+OB / CHoCH+sweep) es de alta convicción.
- **depthBand.** El vigente (define el nuevo extremo candidato del rango).
- **Proyección.** Proyecta un **cambio de bias candidato**: escenario de reacción en la zona de origen del CHoCH. Outcome = ¿un BOS confirma la nueva dirección o revierte (deviation, §1.5 nota)?
- **MTF · Modo mín.** Hereda (ya) · **Operación**.
- **Casos EURUSD.** CHoCH swing §6.3.2 (aislado contra bias dominante = menor convicción hasta BOS).

##### 7.2.6 CHoCH-MSS (§1.5 / §6.2.5)

- **Lee-atrás.** Giro **validado con displacement** (`≥1.5×ATR ∧ cuerpo≥70%`): EL evento de giro.
- **posRole requerido.** **GIRO por definición** — el vigente SIEMPRE recibe tinta (es el certificador del cambio de estructura).
- **confDegree.** No requiere (GIRO + displacement ya es máxima convicción; `wPos=0.9` + `strength` alta §6.2.5).
- **depthBand.** El vigente; su origen ancla el OB/FVG causal (banda 3).
- **Proyección.** Proyecta el nuevo bias con gatillo confirmado: escenario de retroceso a la zona de origen del MSS. Outcome = reacción en el origen → continuación al draw contrario.
- **MTF · Modo mín.** Hereda (ya) · **Operación**.
- **Casos EURUSD.** MSS 06-01 13:00, displacement **3.51×ATR**, cuerpo 98% (§6.2.5) = GIRO vigente arquetípico.

##### 7.2.7 Flip (§2.8 / §6.3.9)

- **Lee-atrás.** Zona S/R invertida tras un quiebre (soporte roto → resistencia y viceversa).
- **posRole requerido.** Solo el flip en un **GIRO** con `confDegree≥1` (flip+OB o flip+FVG). Los flips internos → panel.
- **confDegree.** **Requisito ≥1** para tinta en Operación (un flip aislado sin zona apilada es ruido de S/R).
- **depthBand.** Sigue al giro que lo produjo (típicamente banda 3, el origen).
- **Proyección.** Proyecta re-test del nivel invertido: escenario de rechazo en el flip. Outcome = ¿rechaza (confirma inversión) o lo recupera (flip fallido)?
- **MTF · Modo mín.** Baja solo si Primario (ya) · **Operación (P)**.
- **Casos EURUSD.** Giro alcista 30-06/01-07 (tras sweep de Discount 1.13618 → CHoCH 1.14119): `FLIP ↑` 1.14150 (= low del bar 30-06 11:00) y `FLIP ↑` 1.14095 (= nivel del BOS H1 30-06 14:00, resistencia rota→soporte, arquetipo). Ambos con tinta en Operación (pasaron `confDegree≥1`, flip en giro apilado). Verificado vivo S096 (EURUSD H1, `data_get_pine_labels` + graphics del estudio; niveles exactos, giro cruzado contra OHLCV/panel).

#### A2 · Order Blocks (`GRP_OB`, capa L2 — azul) — fichas 8–13

##### 7.2.8 Order Block (§2.1 / §6.2.1)

- **Lee-atrás.** Última vela contraria antes del desplazamiento = **origen institucional** de la pierna.
- **posRole requerido.** **ORIGEN** — el OB que originó la ruptura de estructura por lado (demanda abajo / oferta arriba). Activo (`state < 2`, no mitigado). Los OB internos (media tendencia) → Estudio.
- **confDegree.** No requiere (ORIGEN ya es Primario, `wPos=1.0`); apilado con FVG/pool sube su prioridad dentro de la banda.
- **depthBand.** **1 por banda de profundidad** (mín. 3/lado disponibles; Operación dibuja el de cada banda activa). Reemplaza el "2 nativos/lado" de S092 (2→uno por banda).
- **Proyección.** Escenario de reacción: si el precio retrocede a este OB ¿rebota en la dirección del bias? Outcome (§4.3) = REACCIONÓ si tocó `±tolConf×ATR` y se desplazó `≥kReact×ATR` (1.0) antes de cerrar más allá del borde protector.
- **MTF · Modo mín.** D1 primarios heredan (ya); los nativos se **suman** a lo heredado · **Operación**.
- **Casos EURUSD.** OB bajista 06-05 11:00 [1.16345,1.16420] (pierna −5.27×ATR, `strength` alta = ORIGEN, §6.2.1); OB alcista 06-08 08:00 [1.15079,1.15235].

##### 7.2.9 OB-propulsión `⇈` (§5.8 / §6.3.28)

- **Lee-atrás.** OB que relanzó el movimiento sin mitigarse (propulsión).
- **posRole requerido.** Hereda el del OB base (típicamente ORIGEN). **No es entrada aparte:** eleva `strength` del OB + glifo `⇈` (ya decidido F3).
- **confDegree.** Hereda del OB base.
- **depthBand.** Prioriza al OB dentro de su banda (a igualdad de banda, el propulsión gana el tie-break por `strength`).
- **Proyección.** Refuerza el escenario del OB base (mayor probabilidad de reacción); no abre escenario propio.
- **MTF · Modo mín.** Sigue al OB · **Operación (glifo)**.
- **Casos EURUSD.** Flag `.propulsion` §5.8 (eleva strength del OB base, `[FIX P-05]`).

##### 7.2.10 Breaker (§2.6 / §6.3.8)

- **Lee-atrás.** OB fallado (`state=3`, cerrado a través) → S/R invertido. El OB que falló **al girar la estructura** es la zona de re-test canónica.
- **posRole requerido.** **GIRO** — el breaker del giro vigente (nace del OB que falló en el HH/LL de giro).
- **confDegree.** Refuerza; un breaker en giro con `confDegree≥1` es de alta convicción.
- **depthBand.** 1/lado (la banda del giro).
- **Proyección.** Escenario de rechazo en el nivel invertido: outcome = ¿rechaza (confirma el giro) o lo recupera (breaker fallido → invalidación)?
- **MTF · Modo mín.** Hereda si Primario · **Operación**.
- **Casos EURUSD.** Transición OB `state=3` → Breaker (§2.6/§6.2.1 invalidación #2).

##### 7.2.11 Mitigation Block (§2.8 / §6.3.10)

- **Lee-atrás.** Bloque mitigado que aún actúa como referencia.
- **posRole requerido.** Indiferente, pero **solo con `confDegree≥2`** (apilado con FVG/pool) recibe tinta en Operación; si no → Estudio (regla dura: un bloque ya mitigado sin apilamiento es contexto histórico).
- **confDegree.** **Requisito ≥2** (es el caso arquetípico de "promoción por confluencia").
- **depthBand.** Sigue la zona apilada que lo promociona.
- **Proyección.** Solo proyecta cuando confluye (refuerza el escenario del apilado); aislado no proyecta.
- **MTF · Modo mín.** No baja · **Estudio**.
- **Casos EURUSD.** Ventana julio EURUSD H1: ningún Mitigation Block alcanza `confDegree≥2` → cero tinta en Operación; todos permanecen en Estudio (panel "Ocultos: Est"). Confirma la regla dura (promoción solo por confluencia): un bloque ya mitigado y aislado queda como contexto histórico, no como zona de reacción operable. Verificado vivo S096 (EURUSD H1: 0/24 labels de Operación son MB).

##### 7.2.12 Vacuum (§5.7 / §6.3.28-área)

- **Lee-atrás.** Hueco de liquidez tras gap; el precio lo cruza rápido (zona de paso).
- **posRole requerido.** Ninguno para tinta en Operación: es **contexto de paso**, no de reacción → panel + Estudio.
- **confDegree.** No promociona (por naturaleza el precio no reacciona en él, lo atraviesa).
- **depthBand.** n/a.
- **Proyección.** Marca dónde el precio se moverá **rápido** (ausencia de reacción esperada); informa la narrativa, no un escenario de entrada.
- **MTF · Modo mín.** No baja · **Estudio**.
- **Casos EURUSD.** Vacuum Block §5.7 (T33).

##### 7.2.13 Rejection block (§2.7 / §6.2.4)

- **Lee-atrás.** Mechas de rechazo en un extremo = la variante de OB del extremo.
- **posRole requerido.** **SOLO en el HH/LL de GIRO** (es el OB de mecha del extremo donde giró el mercado). Internos → nunca.
- **confDegree.** Refuerza (rejection + sweep del nivel = trampa confirmada, §6.2.4).
- **depthBand.** Sigue al giro (banda del extremo).
- **Proyección.** Escenario de rechazo en el extremo: outcome = ¿el retorno respeta el nivel o lo cruza (rejection anulada, §6.2.4 invalidación)?
- **MTF · Modo mín.** No baja · **Estudio**.
- **Casos EURUSD.** Rejection §6.2.4 (06-08 09:00 / 05-27 12:00, ratio mecha/cuerpo sobre nivel).

#### A3 · FVG (`GRP_FVG`, capa L2 — naranja) — fichas 14–20

##### 7.2.14 FVG (§2.2 / §6.2.2)

- **Lee-atrás.** Imbalance de 3 velas a rebalancear. El relevante = el del **desplazamiento que rompió acumulación + estructura** (donde REACCIONA), normalmente coincide con `trueFvg`.
- **posRole requerido.** **ORIGEN** (el FVG del desplazamiento que rompió estructura). Los micro-internos = draws de paso → panel/Estudio.
- **confDegree.** No requiere (ORIGEN Primario); apilado con OB/pool sube prioridad de banda.
- **depthBand.** 1 por banda por lado. Línea CE solo en el pick de banda 1 (el más operable).
- **Proyección.** Escenario de rebalanceo: ¿el precio rellena el FVG y reacciona? Outcome = reacción `≥kReact×ATR` desde el CE antes de cerrar a través del borde.
- **MTF · Modo mín.** D1/H1 heredan (ya); nativos se suman · **Operación**.
- **Casos EURUSD.** True FVG H1 "T.FVG" (10/34 en H1, §6.2.2); los 3 FVG vivos sin "·g" (caso límite §5.18).

##### 7.2.15 trueFVG / displacement (§5.1 / §6.2.2)

- **Lee-atrás.** FVG cuya vela media es displacement (`≥1.5×ATR ∧ cuerpo≥70%`).
- **posRole requerido.** Flag que **eleva `strength`** (ya) y **satisface por sí solo el criterio ORIGEN** del FVG base. No entrada aparte.
- **confDegree.** Hereda del FVG base.
- **depthBand.** Sigue al FVG.
- **Proyección.** Certifica que el FVG es de origen institucional → escenario de mayor probabilidad de reacción.
- **MTF · Modo mín.** Sigue al FVG · **Operación (implícito)**.
- **Casos EURUSD.** Flag `trueFvg` §5.1 (etiqueta "T.FVG").

##### 7.2.16 gradedFVG `·g` (§5.18 / T43 / ADR-013)

- **Lee-atrás.** FVG cuyo CE cae en un gradient level (§5.16).
- **posRole requerido.** Flag: eleva `strength` + refina #18/#20 (ya, ADR-013). **Sin tinta propia.**
- **confDegree.** No cuenta como familia aparte (es refinamiento del FVG).
- **depthBand.** Sigue al FVG.
- **Proyección.** Eleva la probabilidad del escenario del FVG base (confluencia con el grid).
- **MTF · Modo mín.** Sigue al FVG · **—**.
- **Casos EURUSD.** `gradedFvg` §5.18 (sufijo "·g"; los 3 FVG actuales correctamente sin graduar, §6.2.2).

##### 7.2.17 IFVG — invertida (§5.2 / §6.3.23)

- **Lee-atrás.** FVG violado que invierte su rol (`state=ZS_INVALID`, `dir` invertida).
- **posRole requerido.** **SOLO el que calza con el inicio del swing** — el FVG generado antes del OB / antes del LL cuando el precio venía cayendo y va a girar → **GIRO** con `confDegree≥1` (con el OB/estructura del giro). Los IFVG de media tendencia → Estudio.
- **confDegree.** **Requisito ≥1** para tinta en Operación.
- **depthBand.** Sigue al giro.
- **Proyección.** Escenario de reacción en el nivel invertido del giro. `[FIX P-05]`: no suma el FVG muerto junto a su IFVG (1 confluencia).
- **MTF · Modo mín.** Hereda si Primario · **Operación**.
- **Casos EURUSD.** IFVG §5.2/§6.3.23 (27 FVG invalidados en el caso PLAN-049).

##### 7.2.18 BPR — Balanced Price Range (§5.3 / §6.3.24)

- **Lee-atrás.** Solape de FVGs opuestos = PD-array **defensiva** (doctrina madre-2026).
- **posRole requerido.** **ORIGEN** de la pierna vigente **o** `confDegree≥2`; el resto → Estudio.
- **confDegree.** Ruta de promoción: `≥2` sube de Estudio a Operación.
- **depthBand.** Sigue la pierna/apilamiento.
- **Proyección.** Zona de reacción defensiva (stop, no entrada primaria; doctrina defensive-array): outcome = ¿respeta el BPR o lo perfora?
- **MTF · Modo mín.** Hereda si Primario · **Estudio (P sube a Operación con confluencia)**.
- **Casos EURUSD.** BPR §5.3/§6.3.24 (candidata #44).

##### 7.2.19 VI — Volume Imbalance (§5.5 / §6.3.26)

- **Lee-atrás.** Gap entre cuerpos con mechas solapadas (micro-imbalance).
- **posRole requerido.** Micro-concepto: **refina el nivel exacto dentro de una zona ya importante** (hereda `confDegree` del padre). **Nunca solo.**
- **confDegree.** No cuenta como familia propia (afina el nivel del padre).
- **depthBand.** La del padre.
- **Proyección.** Precisa el nivel de reacción dentro de la zona padre; no proyecta escenario propio.
- **MTF · Modo mín.** No baja · **Todo**.
- **Casos EURUSD.** SIVI/BIVI §5.5 (`[FIX P-05]` eleva strength).

##### 7.2.20 IPR — Imbalanced Price Range (§5.9 / §6.3.29)

- **Lee-atrás.** Rango de precio institucional (contexto/bias).
- **posRole requerido.** Micro: solo Todo/panel (contexto de bias, no zona de reacción).
- **confDegree.** No promociona.
- **depthBand.** n/a.
- **Proyección.** Informa el sesgo del rango; no abre escenario de entrada.
- **MTF · Modo mín.** No baja · **Todo**.
- **Casos EURUSD.** IPR §5.9 (candidata #49).

#### A4 · Liquidez (`GRP_LIQ` + `GRP_EQHL`, capa L3 — violeta) — fichas 21–27

##### 7.2.21 Pool BSL/SSL vivo (§3.1 / §6.3.11)

- **Lee-atrás.** Liquidez en reposo = candidato a **draw** (imán de precio).
- **posRole requerido.** El **draw del bias** (objetivo, ancla) + los pools en extremos del marco D1/H1 **a cualquier distancia**.
- **confDegree.** **Guardián de draws (§7.1):** un pool lejano con `confDegree≥2` **o** alineado al bias **NO se recorta por rango** (inmune al top-N/desalojo). Corrige el "adiós al BSL 1.51".
- **depthBand.** Puede caer en bandas 4/5 (fuera del rango vigente) y aún así mantenerse por el guardián.
- **Proyección.** Es el **objetivo** de la proyección: outcome = ¿el precio alcanza el pool (draw cumplido) o gira antes?
- **MTF · Modo mín.** Across D1/H1/M5 (ya) · **Operación**.
- **Casos EURUSD.** BSL D1 ~1.51 (cluster de máximos EURUSD 2009-2011 no barridos, diagnosticado S092) = pool lejano alineado al bias → **vive** por el guardián.

##### 7.2.22 Pool objetivo (§3.1 / §2.3-ancla)

- **Lee-atrás.** El draw activo de la proyección vigente (a dónde apunta el bias ahora).
- **posRole requerido.** **Ancla SIEMPRE** (§2.3 esqueleto visual, ya) — inmune a todo recorte.
- **confDegree.** N/A (mandatorio por ser el objetivo).
- **depthBand.** La del objetivo vigente.
- **Proyección.** ES la proyección adelante: define el objetivo del escenario dominante y el R:R.
- **MTF · Modo mín.** Sí · **Operación**.
- **Casos EURUSD.** El draw del bias vigente (`⚡Raid↓`@1.17 tomado → siguiente draw D1, S092).

##### 7.2.23 Pool barrido (§3.1 / §3.2)

- **Lee-atrás.** Historial de liquidez tomada = ¿ya liquidaron? (lectura atrás pura).
- **posRole requerido.** Contexto: Estudio. El **último barrido relevante** alimenta `posRole=GIRO` de otros conceptos (el sweep que antecede el giro).
- **confDegree.** No promociona (ya cumplió su función).
- **depthBand.** n/a.
- **Proyección.** No proyecta; informa que un draw ya se consumió (suele preceder el giro contrario).
- **MTF · Modo mín.** No · **Estudio**.
- **Casos EURUSD.** `pool.swept` §3.1 (reconvertido en señal de sweep #10).

##### 7.2.24 Sweep / Raid / Grab (§3.2 / §3.3 / §6.3.12)

- **Lee-atrás.** Toma de liquidez (mecha + cierre de vuelta).
- **posRole requerido.** El sweep en el **HH/LL que antecede el giro** al lado contrario → **GIRO**. Internos → panel.
- **confDegree.** Refuerza el giro (sweep + CHoCH/OB = manipulación confirmada).
- **depthBand.** El del extremo operativo.
- **Proyección.** Certifica el giro: escenario de reacción tras la trampa. Outcome = ¿gira (sweep válido) o continúa (era ruptura)?
- **MTF · Modo mín.** El del extremo operativo · **Operación (último)**.
- **Casos EURUSD.** Sweep §3.2/§6.3.12 (mecha que pincha y cierra de vuelta, contraejemplo de BOS 05-27 12:00).

##### 7.2.25 IDM — Inducement (§3.6 / §6.3.13)

- **Lee-atrás.** Trampa previa a la zona real (liquidez que se toma antes de la reacción).
- **posRole requerido.** El que **custodia el extremo operativo** (entre el precio y la zona de reacción del giro) = el **"primer escenario" de profundidad** (banda 1).
- **confDegree.** Refuerza; es parte del giro.
- **depthBand.** **Top por lado bandas 1–2** en Operación.
- **Proyección.** Marca el nivel de inducement que se barre antes de que la zona real reaccione: escenario de "toma inducement → reacción en la zona".
- **MTF · Modo mín.** Nativo (no baja) · **Operación** (sube de Estudio+ — **decisión S092**; reemplaza el cap por recencia `i_maxShowIDM`).
- **Casos EURUSD.** IDM §3.6/§6.3.13 (custodia del extremo, gatillo fino interno).

##### 7.2.26 Judas (§3.5 / §6.3.14)

- **Lee-atrás.** Barrido falso de apertura de sesión.
- **posRole requerido.** El de la **sesión activa, solo fresco** (dentro de la KZ en curso). Los históricos → Estudio/panel.
- **confDegree.** Refuerza si apila con OB/FVG de sesión.
- **depthBand.** El del extremo de sesión.
- **Proyección.** Escenario de reversión post-Judas: outcome = ¿la sesión revierte tras el barrido falso?
- **MTF · Modo mín.** No baja · **Estudio**.
- **Casos EURUSD.** Judas §3.5/§6.3.14 (barrido de apertura KZ).

##### 7.2.27 EQH / EQL (§2.4 / §6.3.6)

- **Lee-atrás.** Liquidez obvia (doble techo/suelo) = imán claro.
- **posRole requerido.** Los que están en un **HH/LL de GIRO** donde se toma liquidez y hay desplazamiento. Media tendencia neutra → panel.
- **confDegree.** Refuerza (EQH + pool + sweep).
- **depthBand.** Si hay 3 ciclos, importan los **3 EQ de los giros significativos** (1 por banda).
- **Proyección.** Objetivo de sweep: outcome = ¿se barre el EQH/EQL (draw cumplido)?
- **MTF · Modo mín.** Heredan si Primarios (ya, cuadre §7.3-b) · **Operación**.
- **Casos EURUSD.** EQH/EQL §2.4/§6.3.6 (≥2 swings a `|Δ|≤0.1×ATR`; contraejemplo 0.6×ATR = HH/LH, no EQH).

#### A5 · Premium/Discount + Gradient (`GRP_PD` / `GRP_GRAD`, capa L1 — marco) — fichas 28–31

##### 7.2.28 P/D + EQ (§2.3 / §6.3.5)

- **Lee-atrás.** Mitades del dealing range vigente (dónde comprar/vender barato/caro).
- **posRole requerido.** **Ancla SIEMPRE** (marco §2.3). Es **contexto de razonamiento, JAMÁS filtro de recorte de draws** (regla dura §7.1).
- **confDegree.** N/A (es el marco que modula, no una zona apilable).
- **depthBand.** Define el eje de bandas (§7.0.3 se mide sobre el rango P/D).
- **Proyección.** Contexto premium/discount del escenario: modula la dirección esperada (comprar en discount, vender en premium).
- **MTF · Modo mín.** 3 líneas D1 rotuladas en LTF (ya) · **Operación**.
- **Casos EURUSD (pasada TV S094, live H1 04-07).** Rango dominante vigente `[1.13618, 1.16221]`, EQ **1.14919**, px 1.14376 → **Discount 29%** (§2.3/§6.3.5).

##### 7.2.29 Quadrants LQ/EQ/UQ (§5.16 / T41)

- **Lee-atrás.** Cuartos del rango (grid de gradient levels).
- **posRole requerido.** Líneas del marco (ya) — **dan el `depthBand` visualmente** (el usuario ve la banda).
- **confDegree.** N/A (marco); pero una zona que cae en un quadrant sube su `confDegree` (gradient, ADR-013).
- **depthBand.** Son la referencia visual de las bandas.
- **Proyección.** Estructura el espacio de proyección (dónde caen los escenarios).
- **MTF · Modo mín.** Grid global (ya) · **Operación**.
- **Casos EURUSD (pasada TV S094, live H1 04-07).** LQ **1.14269** / EQ **1.14919** / UQ **1.15570** (exactos al 5º decimal desde labels del grid, §5.16/T41). *(Junio archivado: LQ 1.13990 / EQ 1.14733 / UQ 1.15477.)*

##### 7.2.30 Eighths 1/8–7/8 (§5.16)

- **Lee-atrás.** Octavos del rango (afinado del grid).
- **posRole requerido.** Afinado de **Estudio** (ya): no participan en la selección de Operación.
- **confDegree.** Un eighth tocado por una zona sube su `confDegree` gradient (ADR-013), pero el eighth en sí no recibe protagonismo.
- **depthBand.** Sub-banda dentro de las 3 principales.
- **Proyección.** Precisa niveles de reacción para Estudio.
- **MTF · Modo mín.** Grid global · **Estudio**.
- **Casos EURUSD (pasada TV S094).** Sobre rango [1.13618, 1.16221]: eighth 1/8 ≈ **1.13943**, 7/8 ≈ **1.15896** (§5.16, salta 0/0.5/1 que ya dibuja P/D). *(Junio archivado: eighth 1/8=1.13618 tocado al tick, vol 21346.)*

##### 7.2.31 OTE / Golden Pocket (§2.5 / §6.3.7)

- **Lee-atrás.** Zona de retroceso óptimo 0.62–0.79 de la última pierna impulsiva con BOS.
- **posRole requerido.** Solo con **pierna activa alineada al bias** (ya). Coincide con banda 2–3.
- **confDegree.** **Sube el `confDegree`** de las zonas que caen dentro de la OTE (OTE+OB/FVG = entrada premium).
- **depthBand.** Banda 2–3 (retroceso óptimo).
- **Proyección.** Escenario de entrada óptima: outcome = reacción dentro de la OTE antes de superar el 100% (anula la pierna).
- **MTF · Modo mín.** No baja (panel indica OTE D1) · **Operación (activo)**.
- **Casos EURUSD.** OTE/GP §2.5/§6.3.7 (contraejemplo: fib sobre pierna correctiva 06-09→06-10 = sin significado).

#### A6 · Gaps de apertura (capa L2 — naranja) — fichas 32–35

##### 7.2.32 NWOG — New Week Opening Gap (§5.10 / §6.3.32)

- **Lee-atrás.** Gap de apertura semanal = zona-referencia recurrente.
- **posRole requerido.** La **más cercana por lado si `confDegree≥1`**; el resto → panel.
- **confDegree.** **Requisito ≥1** para tinta (un gap sin apilar es solo nivel de referencia).
- **depthBand.** La banda donde cae el gap.
- **Proyección.** Nivel de reacción recurrente: outcome = ¿reacciona en el NWOG?
- **MTF · Modo mín.** Gaps D1 heredan si Primarios (ya) · **Estudio (P sube con confluencia)**.
- **Casos EURUSD.** NWOG fin de semana 06-07 ~0.85×ATR, 05-31 ~0.72×ATR (§6.3.32).

##### 7.2.33 NDOG — New Day Opening Gap (§5.10 / §6.3.32)

- **Lee-atrás.** Gap de apertura diaria (ventana más corta que NWOG).
- **posRole requerido.** Ídem NWOG: la más cercana por lado si `confDegree≥1`.
- **confDegree.** **Requisito ≥1**.
- **depthBand.** La del gap.
- **Proyección.** Ídem NWOG, horizonte intradía.
- **MTF · Modo mín.** Ídem NWOG · **Estudio (P sube con confluencia)**.
- **Casos EURUSD.** Gaps diarios FX ≈0 típicamente (§6.3.32 contraejemplo: `open`≈`close` previo <0.5×ATR).

##### 7.2.34 NYMO — NY Midnight Open (§5.10 / §4.2)

- **Lee-atrás.** Apertura NY 00:00 = nivel de referencia intradía.
- **posRole requerido.** Nivel de referencia intradía **en KZ activa**; fuera de KZ → panel.
- **confDegree.** Refuerza si apila con OB/FVG de sesión.
- **depthBand.** La del precio en sesión.
- **Proyección.** Referencia premium/discount intradía (por encima/debajo del NYMO).
- **MTF · Modo mín.** No · **Estudio**.
- **Casos EURUSD.** NYMO §5.10 (nivel global, se hereda a M5 naturalmente).

##### 7.2.35 BAG — Breakaway Gap (§5.10 / `KIND_BAG` / §6.3.32)

- **Lee-atrás.** Gap que NO se rellena (expansión) y **además rompe estructura** (BOS en su dir).
- **posRole requerido.** Señal de displacement: **eleva `strength`/`posRole=ORIGEN`** de las zonas de su pierna; tinta propia solo Estudio.
- **confDegree.** No cuenta como familia (certifica el origen de las zonas de su pierna).
- **depthBand.** La de la pierna que lanzó.
- **Proyección.** Certifica un desplazamiento direccional (como el displacement §4.1): refuerza escenarios de la pierna.
- **MTF · Modo mín.** No · **Estudio**.
- **Casos EURUSD.** Breakaway §5.10/§6.3.32 (#45 cand.: gap que confirma BOS → direccional).

#### A7 · Contexto (`GRP_CTX` / `GRP_KZ`, capas L0/L1/L3) — fichas 36–40

##### 7.2.36 EMAs 20/50/200 — rebote/cruce/stack (§4.3 / §6.2.3 / §6.3.18-20)

- **Lee-atrás.** Tendencia media (contexto del TF propio).
- **posRole requerido.** Líneas tenues (ya); los eventos (cruce/rebote/stack) solo panel. **NO participan en `posRole`/`confDegree`** (son confluencias #37–42 propias, no de zona).
- **confDegree.** **No cuentan** en el apilamiento de zona (§7.0.2).
- **depthBand.** n/a.
- **Proyección.** Contexto de bias medio; su peso va al score (#37–42), no a la tinta de zona.
- **MTF · Modo mín.** No baja (contexto del TF propio, §6.2.3) · **Estudio (eventos)**.
- **Casos EURUSD.** Cruce 20×50 / 50×200, Stack Flip (§6.2.3); rebote §6.3.19.

##### 7.2.37 Kill Zones + macros (§3.4 / §5.14 / §6.3.16)

- **Lee-atrás.** Ventanas temporales de manipulación (eje de tiempo).
- **posRole requerido.** **Ribbon** (ya, S087) — solo sesión en curso. Una zona tocada **dentro** de KZ activa **no cambia su tinta** (el tiempo va al score #34, no al chart).
- **confDegree.** No cuenta (es contexto temporal, no zona apilable).
- **depthBand.** n/a (eje de tiempo, no de precio).
- **Proyección.** Marca **cuándo** es probable la manipulación (ventana del escenario); el peso temporal va al score #34.
- **MTF · Modo mín.** No (ribbon local) · **Operación (ribbon)**.
- **Casos EURUSD.** Ribbon KZ §6.3.16/S087 (bgcolor solo Estudio+; macros solo Estudio+).

##### 7.2.38 Displacement (§4.1 / §6.3.17)

- **Lee-atrás.** Vela(s) de expansión institucional (`≥1.5×ATR ∧ cuerpo≥70%`).
- **posRole requerido.** **No tiene tinta propia:** ES el **certificador de `posRole=ORIGEN`** (y de trueFVG/MSS). Es la fuente del primitivo.
- **confDegree.** No cuenta como familia (es el mecanismo que asigna ORIGEN).
- **depthBand.** n/a.
- **Proyección.** Certifica que una pierna es de origen institucional → habilita los escenarios ORIGEN de sus zonas.
- **MTF · Modo mín.** Implícito · **— (panel)**.
- **Casos EURUSD.** Displacement §4.1 (06-01 13:00 3.51×ATR; fuente del primitivo `posRole`).

##### 7.2.39 Legs IMP/CORR + Inside Day + CISD (§4.4 / §5.12 / §5.6 / §6.3.22-30-27)

- **Lee-atrás.** Fase de la pierna (impulsiva/correctiva) / compresión (Inside Day) / cambio en delivery (CISD).
- **posRole requerido.** **Lectura de contexto:** el leg vigente **define qué lado se proyecta**. CISD solo **fresco + GIRO** (Estudio).
- **confDegree.** No cuentan como familia; informan qué lado apilar.
- **depthBand.** El leg vigente delimita el rango de bandas activo.
- **Proyección.** Determinan la **dirección** del escenario (leg impulsivo = continuación; correctivo = retroceso a zona).
- **MTF · Modo mín.** No baja · **Estudio**.
- **Casos EURUSD.** Impulsive/Corrective §4.4/§6.3.22; Inside Day §5.12; CISD §5.6/§6.3.27.

##### 7.2.40 Std-Dev + SMT (§5.11 / §5.13 / §6.3.31-33)

- **Lee-atrás.** Proyecciones de desviación (Std-Dev) / divergencia entre pares correlacionados (SMT).
- **posRole requerido.** **Herramientas de proyección del agente** (targets banda 4–5) y confluencia inter-símbolo (SMT, futuro multi-par). Panel/Estudio, **sin tinta en Operación**.
- **confDegree.** SMT es confluencia inter-símbolo (#51), no de apilamiento local; Std-Dev es herramienta de TP (§5.11, no suma al score).
- **depthBand.** Std-Dev alimenta bandas 4–5 (targets fuera del rango); SMT es transversal.
- **Proyección.** Std-Dev = niveles de objetivo `−1/−2/−2.5/−4` (§5.11); SMT = confirmación de manipulación inter-símbolo. Son **el instrumento** de la proyección del agente/EA.
- **MTF · Modo mín.** No · **Estudio**.
- **Casos EURUSD.** Std-Dev §5.11 (proyección TP, no confluencia); SMT §5.13 requiere par correlacionado (ADR-011, no verificable con un solo símbolo).

---

> **§7 completa: 40/40 fichas en doctrina.** Fundación (§7.0 primitivos + §7.1 llave/guardián) + A1–A7. **Falta (pre-código, gate sprint16):** (1) una **pasada TV concentrada** que clave los casos EURUSD marcados `[Extracción TV…]` con niveles reales por banda + confDegree≥2 + los 2 rangos previos (bandas 4/5), y (2) **aprobación del usuario** por familia. Al cerrarse → corren los pasos **A-1…A-7** de `ESQUELETO-FABLE-proyeccion-confluencia.md §3.6` en `SMC-Visual.pine` (Fase A, Visual-only, CORE intacto), y tras A-7 (cierra la parte visual) → **firma F1-GATE**. Fase B (promoción de primitivos al CORE + ADR nuevo) abre Fase 2.
