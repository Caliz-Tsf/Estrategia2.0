# ADR-026 — DOL: la **escalera** de draw-on-liquidity y el **marcador de borde** para objetivos fuera de escala

- **Estado:** 🟡 **Propuesto** — pendiente de aprobación del usuario y de los 3 probes de §7. **Ningún cambio en `pine/` hasta que P-DOL-1 y P-DOL-2 estén medidos.**
- **Fecha:** 2026-07-25 (Sesion-145).
- **Contexto de fase:** Fase 1 (curación visual F1-GATE) **tocando Ruta B / Sprint 2.1**. El DOL estaba asignado a Sprint 2.1 como *modulador de bias* (`ESQUELETO-P1 §342`, `MATRIZ-conceptos-cobertura §87`, reglas §1082). Se adelanta **solo la parte de objetivos/dibujo** porque la curación de la familia Liquidez está bloqueada por ella (S144); el **cableado al scoring queda en Sprint 2.1**.
- **Relacionado:** [[ADR-006]] (ciclo de vida de pools), [[ADR-016]] (retención por importancia), [[ADR-017]]/[[ADR-024]] (reparto Visual/Context), [[ADR-021]] (dealing range 2.º extremo), [[ADR-023]] (el panel se lee desde el TF más bajo), `DOSSIER-FABLE-proyeccion-confluencia.md` §2.2/§2.3.

---

## 1. Contexto — qué disparó esto

### 1.1 La frase del usuario (S145, literal)

> «Arrancar DOL (Ruta B / Sprint 2.1) — resolver de raíz: marcador de borde para objetivos lejanos
> (sin romper escala) + escalera de draw-on-liquidity.»

Y la decisión heredada de S144, que este ADR **no re-litiga**:

> Los far/old pivots (BSL 1.51, ~7 años) **SE CONSERVAN** como objetivos válidos (old high sin barrer
> = liquidez). **RECHAZADO** capar por edad o por distancia.

Esto es la misma corrección doctrinal que el dossier ya había fijado (§2.3): *«Fuera del Premium/Discount
D1 hay lugares a donde proyectar. NO se borran por estar lejos. El rango D1 es contexto, JAMÁS tijera.»*

### 1.2 El defecto operativo

Un objetivo válido y lejano (BSL 1.51 en D1 EURUSD) es **incompatible con el dibujo actual**: la línea
se dibuja a su precio real, y **una línea lejana fuerza la escala del gráfico**. Con auto-escala activa,
incluirla comprime las velas y **oculta labels**; con auto-escala bloqueada, el objetivo simplemente no
se ve. Las dos salidas conocidas son malas. **No hay una tercera dentro del paradigma "dibujar el nivel
a su precio"** — de ahí "resolver de raíz".

### 1.2.1 La medición (S145, D1 EURUSD, familia Liquidez aislada, auto-escala ON)

| Magnitud | Valor |
|---|---|
| Escala impuesta al panel | **1.10000 → 1.54000** = 4400 pips |
| Banda real de las velas | 1.135 → 1.185 = 500 pips |
| **Altura del panel que ocupan las velas** | **≈ 11%** |
| **Espacio vertical perdido** | **≈ 89%** |
| Niveles horizontales vivos reportados por `data_get_pine_lines` | **`[1.51]` — exactamente UNO** |

**El hallazgo que convierte esto en un problema de diseño y no de calibración: una sola línea consume
el 89% del espacio vertical del gráfico.** No es un cúmulo de dibujo, no es densidad, no es saturación
de labels. Es **una** primitiva emitida a un precio lejano. Ninguna cuota, cap ni filtro de densidad
puede arreglarlo — solo cambiar *dónde se emite la primitiva*, que es exactamente lo que hace D3.

### 1.3 Hoy ya existe media máquina, mal repartida

`f_drawPools` (`pine/SMC-Visual.pine:3750-3849`) selecciona qué pool dibujar con **tres reglas
solapadas y ad-hoc**, ninguna llamada "DOL":

| Selector | Qué elige | Líneas |
|---|---|---|
| `poolBSLIdx` / `poolSSLIdx` | pool vivo **más cercano** por lado (§8.2 F8, modo Operación) | `:3796-3803` |
| `poolDrawIdx` | pool vivo **alineado al bias más LEJANO** (§7.1 guardián — el que "rescata el BSL 1.51") | `:3805-3809` |
| `upS1/upS2/loS1/loS2` | **top-2 por `strength`** por lado (render LP-Pro, S106) | `:3811-3826` |

Más `f_confDegree(p.level) >= 2` como inmunidad extra. Es decir: **el sistema ya intenta expresar una
escalera de objetivos, pero por tres caminos que no se hablan** y sin nombre de concepto. El DOL no es
una capa nueva encima: es **la unificación de esas tres reglas en una sola ordenación**.

### 1.4 El techo de tokens sigue vivo

`headroom(Visual) ∈ [21, 39]` tokens sobre el límite de 100256 (S138, bracket sin modelo). **Cualquier
diseño que solo AÑADA dibujo al Visual no compila.** Este ADR se diseña para ser **financiado por lo
que retira** (§4), no para pedir presupuesto que no existe.

---

## 2. Decisión

### D1 — El DOL es una **escalera anclada en los extremos**, leída hacia el precio

> **Corrección del usuario (S145, literal):** «¿No se puede hacer que conserve la detección del BSL que
> se ve? yo quiero que desde allá hacia abajo y así mismo del bajo más bajo cuál sería el SSL más bajo
> hacia el precio.»
>
> La primera redacción de este ADR anclaba la escalera **en el precio** (`T1` = el más cercano) y dejaba
> el extremo como cola. Está mal: **en esa lectura el far pivot es lo primero que cae** si algo capa,
> justo el objeto que S144 decidió conservar. La escalera se ancla **en el extremo**.

Se define `f_dolLadder(pools, px, minTouches, N)`: sobre el set de pools **vivos** (`swept == false`)
con `touches >= minTouches`, devuelve **dos escaleras que arrancan en los extremos y se leen hacia
el precio**:

```
BSL (arriba):  L1 = el BSL MÁS ALTO vivo (1.51)  →  L2  →  L3  →  …  →  precio
SSL (abajo):   L1 = el SSL MÁS BAJO vivo         →  L2  →  L3  →  …  →  precio
```

- **`L1` es el ancla, no un candidato.** El "BSL 1.51" **es la cabeza** de la escalera de arriba y por
  construcción **nunca puede ser recortado**: la escalera empieza en él. Esto conserva la detección que
  el usuario ve hoy, que era el requisito explícito.
- **Sin cap por edad ni por distancia** (S144). Si aparece un BSL vivo más alto que 1.51, ése pasa a ser
  `L1` y el 1.51 baja a `L2` — el ancla se recalcula sola, no se hardcodea.
- La lectura resultante es la que el usuario pidió: **"desde allá hacia abajo"** = la secuencia completa
  de old highs entre el extremo y el precio, y simétricamente hacia arriba desde el low más bajo.
- `N` es la **profundidad de proyección** (dossier §2.2: "3 por lado" es el mínimo, con 4.º/5.º bajo
  demanda). **Si `N` recorta, recorta por el MEDIO**: se conservan siempre `L1` (el extremo, ancla) y el
  escalón más pegado al precio; los intermedios son los que ceden. Nunca se pierde ninguno de los dos
  bordes de la lectura.
- **El bias no filtra la escalera, la ORIENTA**: se calculan ambos lados siempre; el lado alineado al
  bias es el **DOL primario** (destacado), el opuesto queda atenuado. Motivo: el ICT lee el draw como
  "a dónde va", pero el lado contrario sigue siendo el mapa de dónde está la liquidez opuesta.

> **Deuda de knob (abierta):** ya existe `i_profundidad` ("Profundidad de proyección (bandas)", 3-5,
> `in_119`) para las bandas P/D. Un `i_dolDepth` nuevo sería un **segundo** knob de profundidad con
> nombre casi idéntico. Decidir al implementar: reusar `i_profundidad` o renombrar ambos. **No crear
> dos "profundidades" sin resolver esto.**

**El DOL es una vista derivada, no un dato nuevo:** no crea arrays, no persiste estado, no toca
`SMC_pools`. Es una ordenación de lo que ya existe ⇒ función **pura**, portable a golden tests MQL5.

### D2 — Sustituye a los tres selectores, no se suma a ellos

Con el anclaje de D1 el mapeo es exacto y **no se pierde nada de lo que hoy se ve**:

| Selector actual | Equivalente en la escalera |
|---|---|
| `poolBSLIdx` / `poolSSLIdx` (más cercano) | el **último** escalón de cada escalera (el pegado al precio) — siempre conservado |
| `poolDrawIdx` (más lejano alineado al bias) | **`L1`, el ancla** — deja de ser un guardián con inmunidad y pasa a ser la cabeza de la escalera |
| `f_confDegree(p.level) >= 2` (inmunidad extra) | innecesaria: nada que esté entre `L1` y el precio se recorta por distancia |
| `upS1/upS2/loS1/loS2` (top-2 por `strength`) | **desaparecen** |

**El orden geométrico sustituye al orden por `strength`** en la selección de *qué dibujar*. `strength`
sigue vivo y sigue decidiendo **cómo** se dibuja (grosor / transparencia / glifo), que es su papel según
ADR-014.

> **Justificación del cambio de criterio:** un objetivo de liquidez se alcanza **en orden geométrico**
> (el precio no puede llegar a `T3` sin cruzar `T1` y `T2`). Ordenar objetivos por `strength` produce
> una lista que el precio no puede recorrer. `strength` responde "cuál es mejor zona"; el DOL responde
> "cuál viene primero". Son preguntas distintas y hoy están mezcladas.

### D3 — Marcador de borde: **el escalón fuera de banda NO se dibuja a su precio**

Se define una **banda de dibujo seguro** `[bandLo, bandHi]` = mínimo/máximo del precio en las barras
visibles. Para cada escalón `Tk`:

- **dentro de la banda** → línea horizontal en su nivel real (comportamiento actual, sin cambios);
- **fuera de la banda** → **no se emite ninguna primitiva a ese precio**. Se emite un único
  **marcador de borde**: una etiqueta anclada **dentro** de la banda (a `bandHi - m·ATR` / `bandLo + m·ATR`)
  con el texto `▲ BSL T3 · 1.51000 · +3520p` (glifo de dirección · lado · orden · precio real · distancia).

Como ninguna primitiva se crea fuera de `[bandLo, bandHi]`, **la escala no puede ser forzada**. Esa es
la raíz: *el objetivo lejano se comunica por TEXTO en el borde, no por GEOMETRÍA a su precio.*

Si varios escalones caen fuera por el mismo lado, se **apilan** en el borde (offset vertical de
`0.35·ATR` entre marcadores, orden `Tk` creciente hacia el borde) — máximo `i_dolDepth` por lado, que
ya está capado a 6.

### D4 — La banda visible se deriva de `chart.*_visible_bar_time`, **y hay que medirla antes de creerla**

Pine v6 **no expone el rango de precio visible**. El proxy propuesto:

```
barras visibles ≈ (chart.right_visible_bar_time - chart.left_visible_bar_time) / (tiempo por barra)
bandHi = ta.highest(high, nVis)    bandLo = ta.lowest(low, nVis)
```

**Tres riesgos declarados, ninguno medido todavía:**

1. `chart.left_visible_bar_time` / `chart.right_visible_bar_time` hacen que el script **recalcule en
   cada scroll/zoom**. Coste de refresco desconocido en un script de este tamaño → **P-DOL-1**.
2. El proxy mide la banda de **precio de las velas**, no la del **viewport** (que incluye el margen
   superior/inferior de TradingView y cualquier otro dibujo). Es una **cota interior**: los marcadores
   quedarán algo dentro del borde real. Aceptable — el fallo es "el marcador se ve un poco adentro",
   no "se rompe la escala".
3. Si el usuario tiene **auto-escala OFF** (el escenario de S144), la banda de velas y el viewport
   pueden divergir mucho. **El marcador de borde no arregla la auto-escala OFF** — eso sigue siendo
   operación del usuario, no código.

**Fallback sin API de viewport (si P-DOL-1 sale caro):** banda = `[ta.lowest(low, n), ta.highest(high, n)]`
sobre un `n` fijo por input (`i_dolBandBars`, default 200). Pierde adaptación al zoom, no recalcula en
scroll, y cumple igual el invariante "no dibujar fuera de la banda". **Es la opción por defecto si
el coste de recálculo no es despreciable.**

### D5 — Dónde vive el código

| Pieza | Archivo | Motivo |
|---|---|---|
| `f_dolLadder` (ordenación pura) | **LIBRARY CORE** (byte-idéntico ×3) | La necesita Strategy para el bias en Sprint 2.1 y el EA en Fase 4 (ADR-002 golden tests). |
| Dibujo (líneas + marcadores de borde) | **`SMC-Visual.pine`** | Es dibujo **nativo** del chart-TF, no heredado ⇒ por ADR-024 el eje de reparto (heredado vs nativo) lo deja en el Visual. |
| Cableado a `scoreLong/scoreShort` | **`SMC-Strategy.pine`** | **NO en esta sesión.** Sprint 2.1, con `f_scoreConfluences`. |

**Sobre el coste en tokens del CORE:** una función del CORE **sin call-site cuesta 0 tokens** en ese
consumidor (tree-shaking, medido ×3 en S135/S137). Mientras Strategy no llame a `f_dolLadder`, el
Visual solo paga lo que **ejecuta**: la llamada y el dibujo. Y ese dibujo se financia retirando los
tres selectores de §1.3 (§4).

> ⚠️ **Esto es una predicción, y en este proyecto las predicciones de tokens mueren** (5 de 5, S133).
> No se implementa "porque debería salir gratis": se mide (**P-DOL-3**) y si no cabe, se para.

### D6 — Abrir el CORE arrastra la deuda parqueada

Tocar el CORE exige `check-core-sync` ×3 y un apply real. Si se abre, **se cierra en el mismo movimiento
la deuda de anclaje weekend-safe de FVG** (parqueada desde S143 "a la próxima apertura real del CORE").
No abrir el CORE dos veces para dos cosas.

---

## 3. Lo que este ADR **no** decide

- **No cablea el DOL al scoring.** El bias sigue siendo el de hoy. Ruta B / Sprint 2.1.
- **No define IRL/ERL, HRLR/LRLR, IPDA ni PDArray.** Son el resto de la Ruta B; el DOL es la primera
  y la única que la curación visual necesita ahora.
- **No cambia la detección de pools** (§3.1 de reglas): `minTouches`, `poolTol`, el ciclo de vida y el
  marcado de barridos quedan **exactamente** como están. El DOL solo **ordena** y **dibuja**.
- **No calibra nada.** `i_dolDepth = 3` y el offset `0.35·ATR` son candidatos; la calibración es Fase 3
  (ADR-002).

---

## 4. Alternativas consideradas y rechazadas

| # | Alternativa | Por qué se rechaza |
|---|---|---|
| A | **Capar objetivos por distancia o antigüedad** (que el 1.51 desaparezca) | Rechazada explícitamente por el usuario en S144 y por el dossier §2.3. Un old high sin barrer **es** liquidez. |
| B | **Dejar la línea a su precio y pedir auto-escala ON** | Es el statu quo y es el defecto: comprime las velas y oculta labels (S144). Además delega en operación lo que es un problema de dibujo. |
| C | **`plot` con `display.none` / escalas secundarias** | No resuelve: el objetivo debe ser **legible**; ocultarlo del eje es no dibujarlo. |
| D | **Dibujar el escalón lejano como línea corta cerca del precio, a escala comprimida** | Miente sobre la geometría: el usuario leería un nivel que no está ahí. El texto no miente. |
| E | **Ordenar la escalera por `strength`** | Produce una secuencia que el precio no puede recorrer (§D2). |
| F | **Mover el dibujo del DOL al Context** para esquivar el techo de tokens | El DOL es **nativo** del chart-TF; por ADR-024 el Context es el consumidor de lo **heredado**. Además partiría la familia Liquidez entre dos indicadores en pleno gate de curación. Se reconsidera **solo si P-DOL-3 dice que no cabe**. |

---

## 5. Consecuencias

**Positivas**

- El "adiós al BSL 1.51" queda cerrado **por diseño**, no por un guardián ad-hoc con inmunidades.
- Tres selectores solapados → una regla nombrada. Menos superficie de bug y menos código que ejecutar.
- La curación de la familia Liquidez se desbloquea: los pools dejan de competir por escala con el resto.
- `f_dolLadder` es la pieza que Sprint 2.1 necesitaba de todos modos; se adelanta **una** función pura,
  no una arquitectura.

**Negativas / riesgos**

- **Riesgo de tokens.** Si el saldo neto (§4 retirado − dibujo nuevo) es positivo, el Visual no compila
  y hay que replegar a la alternativa F. Es el riesgo principal.
- **Riesgo de recálculo en scroll** (D4-1) si se usa la vía `chart.*_visible_bar_time`.
- **Cambio de comportamiento visible:** los pools "top-2 por strength" dejarán de mostrarse como tales.
  Es intencional (§D2) pero **el usuario debe verlo y aprobarlo** antes del commit.
- Se toca Ruta B antes de Sprint 2.1. Se acota: **una función pura + dibujo**, cero scoring.

---

## 6. Invariantes que este cambio NO puede romper

1. **Anti-repaint** — la escalera se recalcula en `barstate.islast` para dibujo (como el bloque actual);
   nada del futuro, ningún `request.security` nuevo.
2. **CORE byte-idéntico ×3** — `check-core-sync.ps1` verde antes de cada commit.
3. **Símbolo-agnóstico** — todo umbral en ATR (`0.35·ATR`), ninguna constante en pips.
4. **Compila 0 errores / 0 warnings** con **apply real** (no basta `pine_check`, S135).
5. **RE10045-safe** — sin `array.push` dentro de bucles de dibujo MTF; arrays de tamaño fijo.
6. **`SMC_pools` intacto** — el DOL lee, no escribe.

---

## 7. Plan de ejecución (probes primero — norma S114)

| Paso | Qué | Criterio de parada |
|---|---|---|
| **P-DOL-1** | Probe aislado: script mínimo con `chart.left/right_visible_bar_time` → medir si el recálculo en scroll es perceptible y si `nVis` es fiable en D1/H1/M5. | Si el recálculo molesta o `nVis` es inestable ⇒ **D4 fallback** (`i_dolBandBars` fijo). Decisión, no debate. |
| **P-DOL-2** | ✅ **MEDIDO Y PASADO (S145, D1)** — ver §1.2.1. Banda de velas 500 pips vs escala impuesta 4400; **1 nivel horizontal vivo (`1.51`) causa el 89% de pérdida vertical**. El sujeto existe y es de una sola primitiva. **Pendiente repetir en H1/M5.** | — |
| **P-DOL-3** | **Medir** el coste en tokens: (a) build con los 3 selectores retirados, (b) build con la escalera. Apply real + `pine_get_console` (el número real **no** está en `pine_get_errors`). | Saldo neto > headroom ⇒ **parar** y evaluar alternativa F. Escribir la predicción **antes** de medir. |
| **I-1** | `f_dolLadder` al CORE + deuda weekend-safe FVG (§D6). `check-core-sync` ×3. | 0/0 con apply real. |
| **I-2** | Dibujo: escalera + marcadores de borde. Validación visual D1/H1/M5 con el usuario. | Aprobación humana explícita (incluye el cambio de §D2). |
| **I-3** | Commit por concepto + actualizar `reglas-smc-ict.md` §3.1 con la sección DOL. | `pine_check` 0/0 + core-sync verde. |

**No se ejecuta I-1 sin P-DOL-1/2/3 medidos y sin el visto bueno del usuario sobre §D2.**

---

## 8. Traza a Fase 4 (MQL5)

`f_dolLadder` es pura y determinista (ordenación por distancia sobre un array de niveles) ⇒ **golden
test trivial**: mismo set de pools + mismo precio ⇒ misma secuencia `T1..Tn`. El **marcador de borde
no se traduce**: es un artefacto de la escala de TradingView. En MT5 el EA consume la escalera como
lista de objetivos (TP escalonados / DOL para el bias), donde el problema de escala no existe — el
mismo argumento que hizo ganar a ADR-023.
