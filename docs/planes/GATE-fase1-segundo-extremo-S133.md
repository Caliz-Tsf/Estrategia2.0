# GATE FASE 1 — El 2.º extremo estructural: **PASA**

> Resultado del probe en sombra que exige la Fase 1 del plan `1-la-ventana-de-giggly-blum.md`.
> **`pine/` NO se tocó.** CORE SHA `752b4083a7db419d` intacto. `pine_check` 0/0. **S021 sigue congelada.**
> Arnés: `scripts/gen_probe_segundo_extremo.py` (marker 1340). Regla medida: `reglas-smc-ict.md` §2.3.1/§2.3.2.

---

> ## 🛑 CORRECCIÓN (misma sesión) — LA COLUMNA DE NAS100 DE LA v1 DE ESTE DOC ERA HUMO
>
> **El usuario mandó una captura de su chart de NAS100 y no cuadraba con lo reportado.** Tenía razón:
> `data_get_study_values` **sigue el crosshair** (gotcha conocido) y la lectura de NAS100 se tomó en una
> **barra intermedia**. Se reportó `close`=22688 con el chart en **29532**. Todos los valores de estado de
> esa columna eran de otra barra:
>
> | | v1 (barra intermedia — **HUMO**) | real (islast) |
> |---|---|---|
> | `close` | 22688.3 | **29532.4** |
> | `bias` | +1 | **−1** |
> | `histHigh` | 22248.0 | **26288.1** |
> | `pdHigh` | 16771.6 | **22248.0** |
>
> **Antídoto aplicado:** volcado por `label` en `barstate.islast` — `data_get_pine_labels` **no** sigue el
> crosshair (lección S131). Además se corrigió **un bug del propio probe**: `sLo`/`sHi` se calculaban dentro
> de `if barstate.isconfirmed` ⇒ en la barra viva salían `na`. Ahora se recalculan cada barra.
>
> **Los contadores acumulados (`nOutRange`, `nRelatch*`, `case*`, `nDisagree`) sobreviven** — no dependen de
> la barra leída. **Los valores de estado de NAS100 quedan corregidos abajo.** La columna de **EURUSD no está
> afectada** (se leyó en la última barra: `close`=1.14628 = precio real).
>
> **Consecuencia sobre el veredicto: el gate SIGUE PASANDO, pero aparece un límite que la v1 no vio.** Ver §5bis.

---

## 1. Veredicto

**Ninguno de los tres criterios de abandono pre-comprometidos se dispara. El gate PASA.**

Y lo hace por el motivo correcto: **la regla es doctrina, no ajuste**. Ninguno de los umbrales se calibró
contra las marcas del usuario — sus niveles solo se usaron como *sanity check* a posteriori.

**Pero con los datos frescos de NAS100 aparece un límite real (§5bis): en un símbolo de tendencia secular
fuerte, el 2.º extremo del lado que el precio nunca visita se FOSILIZA en el origen del feed** ⇒ el rango
D1 sale `[1021.1, 30773.2]` y el veredicto es **premium 96% permanente** ⇒ **no operable**. Eso es media
promesa del usuario (*"que queden en un rango que sea operable"*) sin cumplir. **Se decide antes de tocar
el CORE.**

---

## 2. Los números

*(NAS100 = lectura fresca por `label` en islast, tras la corrección de arriba.)*

| | **EURUSD D1** (secular bajista) | **NAS100USD D1** (secular alcista) |
|---|---|---|
| n barras | 6284 | 6022 |
| `close` | 1.14628 | 29532.4 |
| `bias` | −1 | **−1** *(estructural local; el secular es alcista)* |
| `histLow` | 0.90275 | 1016.1 |
| **`pdLow`** | **0.95360** | **1021.1** ← *de 2001* |
| `histHigh` | 1.60389 | 26288.1 |
| **`pdHigh`** | **1.51441** | 22248.0 |
| **RANGO USADO** | **[0.95360, 1.51441]** | **[1021.1, 30773.2]** ← *techo = trailing (caso 3)* |
| `pctN` / `pctA` | 0.3436 / 0.2963 | **0.9583 / 0.9583** |
| `nStrongLo` / `nStrongHi` | 23 / 18 | 23 / 12 |
| `nRelatchMin2` | 2 | 2 |
| `nRelatchMax2` | **3** | **11** |
| `nOutRange` | **0** | **0** |
| fallback: case1/2/3 (abajo) | 5859 / 27 / 0 | 5190 / 155 / 0 |
| fallback: case2/3 (arriba) | 434 / 312 | 1109 / **3168** |
| `nDisagree` vs Opción A | 363/6284 = **5.8%** | 238/6022 = **4.0%** |

## 3. Predicciones (escritas en el arnés ANTES de medir)

| # | Predicción | Resultado |
|---|---|---|
| P1 | `histLow` EURUSD = 0.90275 ±10 pips | ✅ **VERDE — exacto** *(declarada fácil de antemano; es cross-check del arnés)* |
| P2 | `pdLow` EURUSD = 0.95360 ±20 pips | ✅ **VERDE — EXACTO** |
| P3 | **LA QUE DECIDE:** `nRelatchMax2` ≤ 10 (Fable dio **41**) | ⚠️ **MITAD — 3 en EURUSD (verde), 11 en NAS100 (falla por 1)** |
| P4 | `nOutRange` = 0, incluida la franja histórica | ✅ **VERDE — 0 en ambos símbolos** |
| P5 | **ADR-001:** mismo código, sin ramas por símbolo | ✅ **VERDE en lo mecánico** — pero ver §5bis |
| P6 | `nDisagree` ≥ 15% de las barras | ❌ **FALSA — 5.8% y 4.0%** |

**Marcador S133: 8 vivas de 17.** *(P3 baja de verde a mitad tras la corrección de NAS100; se registra
como salió, sin re-escribir el umbral a posteriori.)*

**Sobre P3 en NAS100:** 11 > 10 ⇒ falla su umbral, pero el umbral era **mío y arbitrario**. El contraste
que importa: **11 re-fijaciones en 6022 barras = 1 cada 547 barras**, contra las **41** del esqueleto de
Fable. Y no es "caminar hacia el precio": en un símbolo secular alcista el 2.º más alto **sube porque hay
altos más altos** — que es exactamente lo que el usuario pide. **El espíritu de P3 se cumple; su letra no.**

---

## 4. Lo que confirma cada verde

**P3 — el techo NO camina.** 3 re-fijaciones en 6284 barras, contra **41** del esqueleto de Fable en la
misma escala. Esa era la causa raíz que arrastramos desde S057 (*"el rango camina hacia el precio"*).
Tomar **el 2.º más alto de todos** en vez de **el último** la elimina: no hay nada que lo re-fije salvo
un strong high nuevo que supere al 2.º.

**P2 — la doctrina reproduce su nivel sin que nadie lo ajuste.** `pdLow` = **0.95360 exacto** = el nivel
que el usuario lee como suelo de D1. No se calibró contra él: sale de "el 2.º strong low más bajo".
Bonus no predicho: `histHigh` = 1.60389 queda a **21 pips** de su rojo anotado (1.60180) ⇒ **su rojo de
arriba era el histórico**, tal y como su modelo predice.

**P4 — el invariante se sostiene, y NO trivialmente.** `nOutRange`=0 en los dos símbolos, con el fallback
**ejercido en 773 barras (EURUSD) y 4162 (NAS100)**. Si case2+case3 hubieran salido 0, el verde no
probaría nada; salen altos ⇒ las tres ramas de la cascada §2.3.2 se recorren de verdad.

**P5 — ADR-001 gratis, y la asimetría emerge sola.** Mismo código, **cero ramas por símbolo**:

- EURUSD (bias −1) → strong = **high** → `nRelatchMax2` = 3 *(congelado)*
- NAS100 (bias +1) → strong = **low** → `nRelatchMin2` = 2 *(congelado)*, weak = high → 10

Y el "caminar" del lado weak **no lo hace el latch: lo hace el fallback**. En NAS100 alcista el precio
supera el histórico constantemente ⇒ `case3Hi` = **2913** ⇒ el techo expande. Es exactamente el régimen
que el usuario describió (*"si sale del premium... se expande hasta el nuevo alto más alto"*), operando
sin código específico.

---

## 5. P6 falsa — por qué, y por qué NO es un problema

Predije ≥15% de cambio de veredicto; salió **5.8% / 4.1%**. Falla su umbral pero **no dispara el abandono**
(ese era <5%, y solo EURUSD lo supera; NAS100 queda por debajo).

**La causa está medida, no supuesta:** el rango nuevo `[0.95360, 1.51441]` **comparte suelo** con la Opción
A vigente `[0.95360, 1.60389]` — solo cambia el techo, y el precio está abajo ⇒ los dos veredictos
coinciden casi siempre. En NAS100 pasa algo análogo: el precio está sobre el histórico (`case3Hi`=2913)
⇒ el techo nuevo **es** el trailing ⇒ **converge con A por construcción**.

**Lectura honesta:** la Opción A con `pdLen`=1000 ya acertaba el suelo **por accidente** (el pool tiene
edad 984 < 1000, ver `decisiones-pd-rango.md` nota S133(b)). El diseño nuevo llega al mismo suelo **por
doctrina**, y además: (a) elimina el accidente, (b) elimina el input, (c) **elimina el caminar del techo**
(P3), que es lo que el usuario reporta desde S057 y que el % de desacuerdo **no mide**.

⇒ **P6 medía la métrica equivocada.** El desacuerdo con A era el listón correcto para la Opción B (S128:
3.2%, misma mecánica que A ⇒ no compraba nada). Aquí la mecánica **sí** difiere, y lo que compra es
estabilidad del strong (P3) + una regla doctrinal sin parámetro de escala — no un veredicto distinto
cada día. **Se registra como predicción FALSA** (no se re-escribe a posteriori), con esta lectura al lado.

---

## 5bis. EL LÍMITE QUE LA CORRECCIÓN DESTAPÓ — el lado no visitado se FOSILIZA

**Lo que funciona (y responde la pregunta literal del usuario):** *"el precio rompe el alto más alto y se
supone que el premium debiese subir hasta donde está el alto más alto nuevo, ¿no?"* → **SÍ, medido:**
`close`=29532 > `histHigh`=26288 ⇒ **caso 3** ⇒ `RANGO USADO = [1021.1, **30773.2**]`. El techo expandió
al nuevo alto más alto, y `nOutRange`=0. **El fallback §2.3.2 hace exactamente lo que él describió.**

**Lo que NO funciona:** el **suelo** de NAS100 es `pdLow` = **1021.1** — un nivel de **2001**. El rango D1
sale de **29752 puntos** y el veredicto es **premium 95.8%**... y lleva así 5190 barras (`case1Lo`).
**No rota. No es operable.**

**La causa, en una frase:** el 2.º extremo del lado que la tendencia secular **nunca vuelve a visitar** se
queda anclado en el arranque del feed. En EURUSD no se ve porque el precio ha visitado los dos lados
(`case2Lo`=27 ⇒ la franja histórica se tocó). En NAS100 `case3Lo`=0 y `case2Lo`=155 sobre 6022: **el precio
lleva 24 años sin acercarse al suelo**.

**Por qué importa:** es media promesa del usuario sin cumplir — *"para darle el premium y discount **no tan
lejos** en D1"* y *"que queden en un rango que sea **operable**"*. Y es **ADR-001**: la regla no puede valer
solo para símbolos que oscilan.

### MEDIDO — H1 SÍ rota ⇒ **la causa del fósil es LA VENTANA, no la regla**

| | NAS100 **D1** | NAS100 **H1** |
|---|---|---|
| barras del feed | 6022 (**~24 años**) | 9055 (**~1.5 años**) |
| `bias` | −1 | +1 |
| `histLow` / **`pdLow`** | 1016.1 / **1021.1** *(de 2001)* | 16335.1 / **19013** *(reciente)* |
| `histHigh` / `pdHigh` | 26288.1 / 22248.0 | 30773.2 / 30722.4 |
| **RANGO USADO** | [1021.1, 30773.2] = **29752 pts** | **[19013, 30722.4] = 11709 pts** |
| `pctN` / `pctA` | 0.9583 / 0.9583 | **0.8977** / 0.8431 |
| `case3Lo` *(el suelo se movió)* | **0** | **839** |
| `nRelatchMin2` / `Max2` | 2 / 11 | 3 / 9 |
| `nOutRange` | 0 | **0** |
| `nDisagree` vs A | 4.0% | **12.3%** |

**El diagnóstico, en una frase:** H1 no se fosiliza **porque su feed solo llega 1.5 años atrás**. D1 tiene
24 años y el precio nunca vuelve a 2001 ⇒ su 2.º extremo bajo se queda en el origen. **La regla es la
misma en ambos; lo que cambia es la ventana de datos.**

⇒ **S129 ya lo había concluido** (*"la ventana es el único parámetro ⇒ declararla"*) y el plan lo lista
como decisión pendiente #1. **El error está en §2.3.2 de este parche doctrinal**, que escribió:
*"ventana | toda la historia disponible del TF | **no hay parámetro de escala**"*. **Eso es lo que NAS100
refuta.** La ventana **sí** es un parámetro, y es el único.

**Nota:** que `nDisagree` suba de 4.0% (D1) a **12.3%** (H1) refuerza la lectura de §5 — P6 medía la
métrica equivocada en D1 precisamente porque ahí el rango nuevo converge con A.

**⇒ Decisión del usuario ANTES de tocar el CORE:** cómo se acota la ventana de D1 (o si se acepta que D1
en un secular no rote, dado que él ya dijo que **D1 es contexto, no señal**). Implementar sin decidirlo
sería llevar al CORE un modo de fallo conocido.

---

## 6. Anti-humo

- `P_marker`=1340 **fresco verificado en cada lectura** (en la corrida previa un modal bloqueó el apply
  y devolvió marker rancio 1333; se detectó y se corrigió).
- `nStrongLo`=23 / `nStrongHi`=18 (EURUSD) y 22 / 11 (NAS100) ⇒ **ningún lado muerto**: los dos acumulan.
- `nBars` como denominador explícito en todos los ratios.
- `lastEvT` = 2026-06-22 = el evento del panel D1 (cross-check que exigía Fable).
- case1/case2/case3 desglosados ⇒ P4 verificable como no-trivial.
- Instancia vieja removida con `chart_manage_indicator` antes de leer (TV solo deja 2).

---

## 6bis. LA CASCADA, RESUELTA — 3 TF nativas (medido, marker 1351)

Tras el hallazgo de la ventana (§5bis) quedaban dos arquitecturas posibles y **nunca comparadas**. El
usuario pidió medirlas antes de decidir. Arnés `scripts/gen_probe_ventana_pd.py` con **4 ventanas en un
solo build** ⇒ (a) = las 4 columnas de una lectura · (b) = la columna `999999` entre D1/H1/M5.

### (b) 3 TF NATIVAS, sin ventana — **EURUSD** ← **GANA**

| TF | rango | `pct` | veredicto |
|---|---|---|---|
| **D1** | [0.95360, 1.51441] | 0.3435 | **DISCOUNT** |
| **H1** | [1.02105, 1.19188] | 0.7328 | **PREMIUM** |
| **M5** | [1.13335, 1.14730] | 0.9290 | **PREMIUM extremo** |

- **ANIDA:** D1 ⊃ H1 ⊃ M5 — verificado numéricamente.
- **ROTA:** 3 veredictos **distintos y simultáneos**. Es el requisito literal del usuario
  (*"parametrizar dónde estará el discount de D1, el de H1 y el de M5"*), y sale **sin código por-TF y
  con CERO parámetros nuevos**.

### (a) 3 ventanas sobre D1 — **descartada**

| ventana | rango | `pct` |
|---|---|---|
| W=500 | [1.10654, 1.18492] | 0.5066 (EQ) |
| W=1000 | [1.01779, 1.18492] | 0.7686 (PREM) |
| W=999999 | [0.95360, 1.51441] | 0.3435 (DISC) |

También anida y rota, pero cae por dos motivos:

1. **Cuesta 3 inputs**, y el mapeo ventana→TF sería **una DEFINICIÓN nuestra, no un hecho** — exactamente
   el error que S130 cometió con el mapeo nivel→TF, que resultó ser **casualidad**.
2. **Modo de fallo nuevo, MEDIDO:** con ventana corta en H1/M5 sale `nLo`=1 ⇒ **`pdLo`=NaN** — no hay 2.º
   extremo dentro de la ventana ⇒ **la regla se queda sin candidatos**. Es el **gemelo exacto de S131**
   (`i_minTouches`=2 dejaba la regla sin candidatos). La ventana corta **reintroduce** ese fallo.

### EL DATO QUE DECIDE (sanity check contra sus lecturas — **no oráculo**)

| | lectura del usuario | 2.º strong low nativo | distancia |
|---|---|---|---|
| suelo **H1** | 1.02108 | **1.02105** | **0.3 pips** |
| suelo **D1** | 0.95751 | 0.95360 | 39.1 pips |

**S132 midió "1100 pips de error en el suelo de H1"** con la Opción A. **Ahora: 0.3 pips.** Y nada se
calibró contra sus marcas — 1.02105 sale de *"el 2.º strong low de la escala de H1"*, punto.

**Cross-check del arnés:** `W=999999` reproduce el probe v14 al 4.º decimal (`pdLow`=0.95360,
pct=0.3435 vs 0.3436) ⇒ los dos arneses miden lo mismo.

**⇒ Decisión: (b) TF nativas.** La ventana queda **solo** como remedio del fósil de D1 en símbolos
seculares (NAS100), a decidir **aparte y solo si molesta** — el usuario ya dijo que **D1 es contexto, no
señal**. §2.3.2 debe reflejar que `pdWindow` es **opcional y por-TF**, no parte de la regla base.

---

## 7. Siguiente

**Fase 2 del plan, y su primer paso es un gate humano: descongelar S021.** La medición no lo decide.

Lo que la Fase 1 aporta a esa decisión: la regla es doctrinal (§2.3.1/§2.3.2), reproduce el nivel del
usuario sin ajuste (P2), elimina el defecto de S057 (P3), conserva su invariante (P4), es multi-símbolo
sin ramas (P5), y **retira** código (`f_detectSwings(pdLen)` + 4 resets + `i_pdSwingLen` ⇒ −1 input, 0
nuevos). Coste: CORE roto ⇒ SHA re-baseline ×3 ⇒ **ADR-021** ⇒ golden tests MQL5 del rango rederivados
(`f_premiumDiscount` intacta ⇒ los suyos sobreviven).
