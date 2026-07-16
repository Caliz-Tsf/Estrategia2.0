# MEDICIÓN S133 — El relatch estructural de Fable, en sombra: la expansión anula el latch

> **Qué es esto:** el resultado del probe en sombra que pide §7 de `RESPUESTA-FABLE-premium-discount-S132.md`.
> **Decisión del usuario al arrancar S133:** *"solo el probe, decisión después"* — la decisión S021 (Opción A)
> **NO se descongeló**. Este documento la informa, no la revierte.
> **`pine/` NO SE TOCÓ.** CORE SHA `752b4083a7db419d` INTACTO. `pine_check` 0/0 en los 2 probes.
> **Arnés:** `scripts/gen_probe_relatch_estructural.py` (parametrizado por escala).

---

## 1. Veredicto en una línea

**El criterio de abandono pre-comprometido de Fable se dispara: P1 y P2 fallan AMBAS, en las DOS escalas
medidas.** Y la causa no es la parametrización: es que **el componente C3 del propio esqueleto ("expansión
intacta") anula al componente C2 ("relatch por evento")**. El latch propone; la expansión dispone.

---

## 2. Los números (D1 OANDA:EURUSD, n=6284 barras confirmadas)

| Lectura | corrida `swing` (marker 1330) | corrida `major` (marker 1331) |
|---|---|---|
| Evento disparador | `evStructSwing` (escala `i_swingLen`=5) — **lo que Fable §2 especifica** | `evStructMajor` (escala `i_majorLen`=50) — la escala del dealing range |
| `sHi` (strong high latcheado) | 1.16445 | 1.18492 |
| **`sLo`** (strong low latcheado) | **1.13246** | **1.13246** |
| `pctL` | 0.46202 | 0.28174 |
| amplitud del rango | 319.9 pips | 524.6 pips |
| `nRelatch` (Hi+Lo) | 301 (140+161) | 41 (18+23) |
| `nPiv` (escala P/D) | 78 | 3 *(con `i_pdSwingLen`=1000)* |
| `nDisagree`/`nBars` | 1896/6284 = **30.2%** | 2311/6284 = **36.8%** |
| `nOutRange` | 0 | 0 |
| `nSeed` | 2 | 2 |

**ATR_D1 = 0.00565. Precio = 1.14724.**

### Predicciones de Fable (§7)

| # | Predicción | `swing` | `major` |
|---|---|---|---|
| P1 | `sHi` ≤ 1.0×ATR de **1.23697** (el rojo de Freddy) | ❌ **12.8×ATR** | ❌ **9.2×ATR** |
| P2 | `pct` < 20% y **no reaparece 1.13246 como ancla** | ❌ pct=0.46 · **1.13246 reaparece** | ❌ pct=0.28 · **1.13246 reaparece** |
| P4 | `nRelatch` > 0 **y ≪ nPiv** | ~ mitad: 301>0 ✔ pero **3.86× nPiv**, no ≪ | ✅ 41 > 0 y < 78 |
| P7 | veredicto cambia ≥15% de las barras | ✅ 30.2% | ✅ 36.8% |

### Predicciones propias de la corrida `major` (escritas ANTES de medir, en el arnés)

| # | Predicción | Resultado |
|---|---|---|
| P-R1 | `nRelatch(major)` < 78 y ≪ 301 | ✅ VERDE (41) — *declarada fácil de antemano* |
| P-R2 | `ampL(major)` > 758 pips (el rango doctrinal de A con pdLen=50) | ❌ **FALSA** — 524.6 pips, sale **menor** |
| P-R3 | **LA QUE DECIDE:** `sHi(major)` ≤ 1.0×ATR de 1.23697 | ❌ **FALSA** — 9.2×ATR |
| P-R4 | P7 se mantiene ≥15% con escala 50 | ✅ VERDE (36.8%) |

**Marcador: 3 vivas de 4 nuevas** (P-R1 fácil, P-R4 verde; P-R2 y P-R3 falsas). Acumulado ≈ 27 de 48.

---

## 3. Anti-humo (el probe mide lo que dice medir)

- **Cross-check de fechas que exigió Fable:** `lastRelHiT` de la corrida `swing` = **2026-06-17** = exactamente
  el **"BOS 17-06"** que el panel lista en D1. El probe relatcha donde el panel dice. ✔
- `nOutRange`=0 en ambas ⇒ el invariante `pct∈[0,1]` se conserva (como Fable predijo — y ver §4: es
  precisamente ese invariante el que mata la propuesta).
- `nSeed`=2 (un lado cada uno, el arranque) ⇒ no hay siembras espurias.
- `nPiv` contado en la misma pasada ⇒ P4 compara peras con peras.
- `P_marker` verificado fresco en cada lectura (**1330 y 1331**).

**Incidente de método (atrapado, no sufrido):** el primer intento de la corrida `major` devolvió `P_marker`=1330
— **rancio**. El apply se había bloqueado en el modal *"¿Desea guardar este script antes de añadirlo?"*
(gotcha S131) y `data_get_study_values` habría reportado los números de la escala 5 **como si fueran de la 50**.
Sin el marcador de identidad por build, la conclusión de esta sesión habría sido basura. Se resolvió con
`ui_click(text="Guardar")` + Ctrl+Enter; la consola confirmó *"Compilado." + "Añadido al gráfico."*

**Nota de comparabilidad:** la instancia vieja arrastraba un override `i_pdSwingLen`=50 y la nueva usa el
default del repo (=1000, del fix S130 `61dcc36`). Por eso `nPiv` y `nDisagree` **no son comparables entre
corridas** (dependen de la Opción A de referencia). `sHi`/`sLo`/`pctL`/`nRelatch`/`ampL` **sí lo son**: no
dependen de `i_pdSwingLen`. Las conclusiones sólo usan estos últimos.

---

## 4. EL HALLAZGO: C3 anula a C2 (la expansión y el latch son incompatibles)

**`sLo` = 1.13246 en las DOS escalas.** Ese número es el mínimo reciente del precio — y es *exactamente* el
ancla que la predicción P2 de Fable marcaba como señal de fallo (*"o si reaparece 1.13246 como ancla"*).
Que salga idéntico con 301 relatches y con 41 no es casualidad: **el nivel latcheado es irrelevante**.

El mecanismo, del propio §3 de Fable:

- **C2** fija `sLo` := `runMin` (el origen de la pierna) en la barra del BOS/CHoCH.
- **C3** ("expansión intacta", `f_updateTrailing` sin tocar) hace `if low < sLo → sLo := low` **cada barra**.

En una tendencia bajista el precio hace mínimos nuevos constantemente ⇒ **C3 arrastra `sLo` hasta el precio,
borrando lo que C2 acababa de fijar.** El latch dura hasta la siguiente vela que haga un mínimo. Por eso da
igual la escala del evento, y por eso `sLo` converge al mismo 1.13246 que ya da la Opción A vigente.

El lado alto lo confirma por contraste: con el precio cayendo, nada empuja `sHi` hacia arriba ⇒ **ahí el latch
sí sobrevive** (1.16445 / 1.18492 ≠ 1.20831 = el techo de A). El latch funciona exactamente en el lado donde
el precio no lo toca — es decir, donde no hace falta.

**Fable escribió el defecto sin verlo**, en su §2:

> *"Si el precio supera un lado, la expansión lo sigue ⇒ `pct∈[0,1]` garantizado por construcción, como hoy."*

Eso no es un efecto colateral: **es la refutación**. No se puede tener a la vez `pct∈[0,1]` garantizado por
expansión y un extremo pegajoso. Son la misma variable tirando en direcciones opuestas.

**Y es el mismo modo de fallo que mató la Opción C en S129** (`nHiReset=nLoReset=0`: con la expansión
conservada, `close > top` es imposible ⇒ la violación nunca se dispara ⇒ degeneró en min/max de ventana).
S129 lo encontró por el lado del *disparador*; S133 lo encuentra por el lado del *nivel*. **Misma causa.**

---

## 5. Lo que esto le hace a la propuesta de Fable

**Muere tal como está especificada** (su propio criterio: P1 ∧ P2 falsas). Pero muere de forma informativa,
y hay que decir qué sobrevive:

- **SOBREVIVE — P7 es real:** 30.2% / 36.8% de desacuerdo de veredicto. Esto **no** es la variante muerta de
  S128 (3.2%). El relatch por evento estructural **sí** es una mecánica distinta de la Opción A, no un
  cambio de pivote disfrazado. Fable tenía razón en eso.
- **SOBREVIVE — el diagnóstico doctrinal de §1/§2:** que el "Strong High/Low" de LuxAlgo es una etiqueta y no
  un ancla, y que §2.3 tiene "strong high/low" sin cuantificar, **no depende de esta medición**. El hueco
  doctrinal sigue abierto y sigue siendo real.
- **SOBREVIVE — "strong es relacional, no local":** el principio que explica por qué murieron toques,
  amplitud y tolerancia (hipótesis #6/#7/#9) sigue en pie. Esta medición no lo toca.
- **MUERE — C3 "expansión intacta":** es incompatible con C1+C2. Cualquier rediseño tiene que elegir.
- **MUERE — la escala como palanca:** medida en 5 y en 50. Ninguna salva P1/P2. (Cuarta vez que la escala se
  propone como causa y no lo es: S130 `pdLen`, S132 amplitud, y ahora las dos escalas de evento.)

---

## 6. La grieta que esto abre (para el usuario, no para implementar)

El modelo del usuario, medido en S130 (TAREA 4), **no tiene expansión**:

> *"el rango NO se mueve porque aparezca un pivote nuevo, se mueve cuando el precio CONSUME el extremo →
> salta al SIGUIENTE pool"*

**Saltar al siguiente pool ≠ expandirse hasta el precio.** Las Opciones A, B, C y el esqueleto de Fable
**todas conservan `f_updateTrailing`** — y por tanto todas expanden. Ninguna de las cuatro ha implementado
nunca el modelo del usuario. Ese es el denominador común de 5 sesiones de refutaciones.

**El precio de quitar la expansión** está medido y es conocido: `pct` sale de `[0,1]` (S129 midió `pctC`=1.1
en NAS100USD). Pero eso **ya está contemplado en el proyecto**: `decisiones-pd-rango.md:105` registra el
micro-pulido diferido *"cuando el precio queda fuera del rango... podría mostrar 'bajo rango'/'sobre rango'"*.
Es decir: el invariante `pct∈[0,1]` es una **decisión de diseño**, no una ley — y es la que bloquea todo.

**NO se propone nada aquí.** Esto es el dato que S134 necesita para decidir con el usuario, y hay una
pregunta previa que ninguna medición puede responder: *¿el rango que él lee tiene el precio siempre dentro,
o acepta que el precio se salga por abajo mientras el suelo aguanta?* Su frase de S091 (*"que D1 quede lejos
mientras el precio no rompa ese bajo"*) sugiere lo segundo, pero **eso hay que preguntárselo con la frase
literal delante** (norma S132), no inferirlo.

---

## 7. Estado

- **Decisión S021: SIGUE CONGELADA.** No se descongeló nada. No hay ADR. No hay tag.
- **`pine/` intacto**, CORE SHA `752b4083a7db419d`, `pine_check` 0/0 ×2.
- **NO medido** (requería pasar el gate, que no se pasó): P3 (rotación entre TF), P5 (los 9 niveles anotados),
  P6 (NAS100/ADR-001).
- **Coste de implementación que el probe destapó** (si algún día se implementa algo así): el bloque P/D
  (`:2261-2265`) corre **antes** que la estructura (`:2276`), así que el relatch tendría que reordenarse o
  usaría el evento de la barra anterior. El probe lo esquiva yendo al final del archivo.
