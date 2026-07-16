# DISEÑO S133 — El modelo del usuario: expansión pura + cascada de pivotes

> **Estado: PROPUESTA PARCIAL.** La capa D1 está resuelta y medida. La cascada H1/M5 **NO**: su regla
> candidata ("cada N pivotes") está **REFUTADA con medición**. Falta un dato que solo el usuario tiene.
> `pine/` NO se tocó. CORE SHA `752b4083a7db419d` intacto. Sin ADR.

---

## 1. La frase literal que gobierna este diseño (norma S132)

> *"el precio en este caso siempre está por dentro, pero vuelvo y digo, en algún minuto puede salir del
> rango de los altos más altos y de los bajos más bajos y este debe quedarse con los premium o discount
> hasta que genere de nuevo un bajo más bajo o un alto más alto y ahí se quedaría la etiqueta de D1,
> luego un par de pivotes más arriba el discount de h1 y un par de pivotes más arriba el discount de m5
> o es algo así lo que pienso debes ayudarme a diseñar esto. No sé si está bien el salto o que se expanda
> pero se supone que si sale del premium de las 3 temporalidades se expande hasta el nuevo alto más alto
> y así como expliqué con lo del bajo más bajo"* — **usuario, S133 (2026-07-15)**

---

## 2. Lo que la frase RESUELVE (cerrado, no volver a litigar)

| # | Lo que dice | Consecuencia de diseño |
|---|---|---|
| 1 | *"se expande hasta el nuevo alto más alto"* | **NO ES SALTO, ES EXPANSIÓN PURA.** |
| 2 | *"el precio siempre está por dentro"* | **`pct∈[0,1]` SE CONSERVA.** El invariante no se toca. |
| 3 | *"debe quedarse... hasta que genere de nuevo un bajo más bajo"* | **El extremo NO se reancla en pivotes.** |

**(1)+(2)+(3) = `f_updateTrailing` SIN `f_resetTrailing`.**

### 2bis. Dos hipótesis del supervisor que la frase MATA

- **"Saltar al siguiente pool" (S130 §9, y repetida por el supervisor en S133):** el usuario **nunca dijo
  saltar**. Dijo *"se expande"*. El "salta al siguiente pool" fue **interpretación del supervisor** sobre
  su *"salta"* de S130 — que en su boca describía el efecto observado, no el mecanismo. **Hipótesis muerta
  por su propia frase.** (Cuarta vez que el supervisor le atribuye un modelo que no dijo: cf. S129 §3
  ambiguo, S131 §3bis.4 premisa fabricada, S132.)
- **"pct∈[0,1] es lo que bloquea todo" (supervisor, S133):** **falso**. Él lo quiere. No hay que quitarlo.

### 2ter. Un error de S132 que hay que corregir en el ADR

S132 declaró el fix de S130 (`i_pdSwingLen` 50→1000, `61dcc36`) **"doctrinalmente incorrecto"** porque
*"solo actúa el trailing ⇒ rango tiende a fósil, justo lo que §6.3.5 prohíbe"*.

**Ese razonamiento es erróneo.** §6.3.5 prohíbe medir P/D sobre un rango **ya superado por la estructura**.
Un rango que **solo expande** nunca está superado: **contiene el precio por construcción** (`nOutRange`=0,
medido en S129 y en S133/L1). El "rango fósil" que S132 vio como defecto **es el requisito explícito del
usuario**: *"debe quedarse... hasta que genere de nuevo un bajo más bajo"*.

⇒ **`i_pdSwingLen`=1000 NO hay que revertirlo.** Y S130 midió que produce **exactamente** su lectura de D1:
`[0.95360, 1.60389]`. Pero lo produce **por accidente del mecanismo** (con pdLen=1000 el reset casi nunca
dispara) — eso es lo que hay que hacer **explícito**, no revertir.

---

## 3. La capa D1 — RESUELTA (y ya está medida)

**Regla:** el rango D1 = `[bajo más bajo, alto más alto]`, con **expansión pura**: solo cambia cuando el
precio hace un extremo nuevo. Sin reanclaje por pivotes.

**Medido hoy (probe v13, marker 1333, D1 OANDA:EURUSD):** `pdLow`=**0.95360** · `pdHigh`=**1.60389** =
la lectura del usuario (S130), con `pct∈[0,1]` conservado.

**Lo que falta cuantificar: LA VENTANA.** Es el único parámetro libre, y S129 ya lo había concluido
(*"la ventana es el único parámetro ⇒ declararla"*). Medido hoy, el dato que lo prueba:

| pool | nivel | edad (velas) |
|---|---|---|
| **#1** | **0.90275** | **6277** ← el mínimo absoluto del feed (≈2001) |
| **#2** | **0.95360** | **984** ← **el "bajo más bajo" del usuario** (≈2022) |

**Su "bajo más bajo" es el pool #2, NO el #1** — 508 pips y ~21 años de diferencia. ⇒ **su rango D1 NO es
el mínimo histórico absoluto: es el mínimo de una ventana que excluye 2001.** `pdLen`=1000 acierta porque
la edad de #2 (984) cae justo dentro de 1000 velas. **Eso es una coincidencia frágil, no una regla.**
La ventana hay que **declararla** (input explícito), no heredarla del `pdLen` de un detector de pivotes.

---

## 4. La cascada H1/M5 — SU REGLA CANDIDATA, REFUTADA

**Hipótesis medida:** *"un par de pivotes más arriba el discount de H1, y un par de pivotes más arriba el
de M5"* ⇒ los verdes del usuario deberían estar separados por un **número constante** de pools.

**Los 12 pools vivos bajo el precio** (volcado v13; anti-humo: `nAliveDown`=12 **cuadra exacto** con S131):

| # | nivel | edad | verde del usuario | dist |
|---|---|---|---|---|
| 1 | 0.90275 | 6277 | — | |
| **2** | **0.95360** | 984 | **0.95751** | 39.1 pips |
| 3 | 0.96315 | 973 | — | |
| 4 | 0.97049 | 967 | — | |
| 5 | 0.97302 | 958 | — | |
| **6** | **1.01779** | 391 | **1.01814** | **3.5 pips** |
| **7** | **1.02105** | 376 | **1.02182** | **7.7 pips** |
| 8 | 1.03600 | 357 | — | |
| **9** | **1.07330** | 338 | **1.07408** | **7.8 pips** |
| **10** | **1.10654** | 306 | **1.10640** | **1.4 pips** |
| 11 | 1.12105 | 293 | — | |
| 12 | 1.13246 | 16 | — | |

### Predicciones (escritas antes, en el arnés)

| # | Predicción | Resultado |
|---|---|---|
| P-C1 | Los 5 verdes son pools vivos a ≤10 pips | ~ **MITAD** — 4 de 5 a ≤7.8 pips; el 5.º (0.95751) a **39.1** |
| P-C2 | **LA QUE DECIDE:** espaciado constante ±1 entre verdes consecutivos | ❌ **FALSA** — sale **[4, 1, 2, 1]** |
| P-C3 | El pool más bajo = `pdLow` | ❌ **FALSA** — el #1 está a 508 pips de `pdLow` (ver §3) |

**P-C2 FALSA ⇒ "cada N pivotes" no es la regla.** Sus verdes caen en los pools **#2, #6, #7, #9, #10**;
los saltados son #1, #3, #4, #5, #8, #11, #12. El espaciado varía de 1 a 4. **Ninguna N funciona.**

**Lo que SÍ quedó firme:** sus verdes **son pools reales del sistema** (4 de 5 a ≤7.8 pips). El motor **ya
tiene** los niveles que él lee. El problema **no es detectarlos: es elegir cuáles**. (Mismo patrón que
S131/S132: su ojo usa un criterio de selección que el motor no registra.)

### 4bis. La pista no predicha: los pools vienen en CLUSTERS por edad

Las edades no son continuas — **se agrupan**, con saltos enormes entre grupos:

| cluster | pools | edad |
|---|---|---|
| A | #1 | 6277 |
| B | #2 · #3 · #4 · #5 | 958-984 |
| C | #6 · #7 · #8 | 357-391 |
| D | #9 · #10 · #11 | 293-338 |
| E | #12 | 16 |

**Sus verdes son los 1-2 pools MÁS BAJOS de cada cluster** (B→#2 · C→#6,#7 · D→#9,#10), y **descarta los
clusters extremos** (A demasiado viejo, E demasiado cerca del precio). **Esto es observación, NO una regla
propuesta** — el ajuste no es exacto (toma 1 de B pero 2 de C y 2 de D) y con n=1 símbolo sería
overfitting (ADR-002). **Se registra como pista para la pregunta de §5, no como diseño.**

---

## 5. LO QUE FALTA — un dato que solo el usuario tiene

Él dijo *"o es algo así lo que pienso, debes ayudarme a diseñar esto"* ⇒ sus 5 verdes **no son un oráculo
exacto**, son una aproximación suya. Y la regla que propuso está refutada. Por tanto **no se puede derivar
la cascada de estos datos sin inventar** (que es exactamente lo que produjo las premisas fabricadas de
S129/S131/S132).

**La pregunta, con la tabla de §4 delante:** de esos 12 pools, **¿cuál es el discount de D1, cuál el de H1
y cuál el de M5 — y qué los distingue de los que no elegiste?**

Con esos 3 puntos anclados, la regla se deriva y se valida contra el resto. Sin ellos, no.

**NO preguntar** (ya contestado por él, §2): si es salto o expansión; si el precio puede salirse.

---

## 6. Estado

- **S021 SIGUE CONGELADA.** Nada de esto se implementó. Sin ADR, sin tag.
- **`pine/` intacto**, `pine_check` 0/0 ×4 (markers 1330/1331/1332/1333).
- **Anti-humo v13:** `nAliveDown`=12 cuadra exacto con el censo de S131; `nAliveUp`=25 (S131 midió 26 —
  uno barrido en 2 sesiones, plausible); `P_marker`=1333 fresco verificado.
- **Predicciones S133: 5 vivas de 11** (P-C1 mitad; P-C2, P-C3 falsas).
- **Pendiente para el ADR:** corregir el veredicto de S132 sobre `i_pdSwingLen`=1000 (§2ter) y **declarar
  la ventana** en vez de heredarla del detector de pivotes (§3).
