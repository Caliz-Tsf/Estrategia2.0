# DISEÑO — Presupuesto explícito de labels por importancia (Opción 2)

> S124 · Visual-only · NO toca el LIBRARY CORE (SHA `752b4083a7db419d` intacto).
> Estado: **DISEÑO — pendiente de medición (probe de tokens)**. Ningún código en `pine/` hasta que el probe diga que cabe.
> Deuda que ataca: S123 #7 (arquitectura), #5 (estructura vieja), #1 (cap por tipo, lo vuelve barato y seguro).

## 1. El problema, en una ecuación

Pine conserva las **500 labels creadas más recientemente** (`max_labels_count = 500`) y borra las viejas
**en el momento del `label.new`**. Las familias del sistema se parten en dos grupos:

| Grupo | Cuándo se crean | Ejemplos | Edad relativa |
|---|---|---|---|
| **Históricas** | recorrido histórico (`barstate.isnew`) | estructura BOS/CHoCH/MSS (~342 en "Todo"), EQH/EQL (~16) | **las más VIEJAS** |
| **islast** | repintado en `barstate.islast` | swings, ~20 familias de evento, ~9 de zona, IR, pools, marco, MTF | las más NUEVAS |

Vive todo a la vez, así que la única ecuación que importa es:

```
históricas + creadas_en_islast <= 500
```

En "Todo" hoy: `342 + ~500 = 842` → Pine desaloja 342 → **muere justo el grupo histórico = la estructura**.
No hay bug de detección: hay sobregiro de presupuesto.

## 2. Los dos hallazgos que hacen barata la Opción 2

**(a) El presupuesto ya existe y su número ya es correcto — lo que falta es el COBRO.**
`budgetLbl` (L3462) ya declara 25 / 60 / 150 según densidad. Y no es casualidad que "Todo" valga 150:
`500 − 342 (estructura) − 8 (FRAME_RESERVE) ≈ 150`. El número estaba bien calculado. El problema es que
`eventCap` solo se le cobra a **5 familias** (EQ, pools, sweep, flip, gaps) en §6.5, mientras swings, zonas,
IR y las otras ~15 de evento crean sin pagar. De ahí el ×3.3 de S123.

**(b) La §6.5 actual es token muerto que podemos gastar.**
S123 Hallazgo 4 demostró que `f_capLbls`/`f_capLblsOnly` **no pueden funcionar**: borran *después* de crear,
y el desalojo de Pine ya ocurrió en el `label.new`. Estamos pagando ~30-45 tokens por una máquina que no
hace nada. **Esa es la fuente de financiación del rediseño.** No hay que "liberar tokens primero":
la Opción 2 se paga sola borrando la §6.5.

## 3. Diseño

### 3.1 Reserva MEDIDA, no adivinada
Al llegar a islast las familias históricas **ya existen y su tamaño es conocido**. No se estima: se lee.

```pine
// sustituye la línea de eventCap (L3468)
int lblCap = math.min(budgetLbl, 500 - array.size(SMC_structLabels) - array.size(SMC_eqLabels) - FRAME_RESERVE - mtfReserve)
```

`budgetLbl` = cuánto quiere VER el usuario (curación). `500 − históricas` = cuánto PERMITE la plataforma.
Manda el menor de los dos. En Operación la estructura ya está recortada a `STRUCT_OP_CAP=3` → manda 25.
En "Todo" manda la plataforma (~134-150) → y la estructura sobrevive **por construcción**, no por parche.

### 3.2 Un solo contador, cobrado AT-CREATION
S123 Hallazgo 4 obliga: todo cap debe cobrarse al crear. Los cuellos de botella **ya existen** y ya son
tres funciones por las que pasa casi todo el dibujo de islast:

| Helper | Call-sites | Cubre |
|---|---|---|
| `f_evLbl` | 20 | sweep/disp/IDM/CISD/SMT/Judas/Rej/flip/EMA×3/FB/leg/ID/bag/IPR/OG |
| `f_zLbl` | 9 | OTE/OB/Breaker/IFVG/BPR/MB/Vacuum/FVG |
| `f_pushSwingLabel` | 1 | swings HH/HL/LH/LL |

El contador vive en un `array<int>` de tamaño 1 — **mismo truco que `evSeen`** (Pine no deja mutar un global
escalar dentro de una función, pero los arrays van por referencia; tamaño fijo, solo get/set → RE10045-safe):

```pine
var array<int> lblSpent = array.new<int>(1, 0)
```

Dentro de cada helper, antes de crear: si `array.get(lblSpent, 0) >= lblCap` → **devolver `na` sin crear**;
si no, incrementar y crear. Los tres helpers ya toleran `na` (`f_evLbl` ya devuelve `na` cuando la ranura
2D está tomada, y "array.push de un na y label.delete(na) son no-op seguros" — comentario S122).

**GOTCHA de tokens (S122):** el coste está en los CALL-SITES, no en el cuerpo. Meter la lógica DENTRO de
un helper que ya existe ≈ gratis. Por eso NO se añade parámetro de familia a `f_evLbl` (serían 20 tokens).

### 3.3 Importancia = orden de dibujo (ya es así, y da un regalo)
`f_evLbl` ya documenta "Prioridad = ORDEN DE DIBUJO: las familias de más señal se dibujan antes y se quedan
el nombre; las auxiliares ceden". Con el cobro at-creation esa regla pasa a gobernar TODO el presupuesto.

**El regalo:** S117 puso los swings **al final** del dibujo a propósito, para que sobrevivieran al desalojo
por antigüedad. Con el cobro at-creation ese mismo orden se invierte de significado: **el último en dibujar
es el primero que cede.** Los swings son L3 (§2bis de la rúbrica) y deben ceder ante la estructura.
El hack de S117 se convierte en la política correcta **sin mover una línea de orden**.

Las cotas por familia ya existen (`i_maxShow*` = 20 c/u), así que el techo global no puede dejar a una
familia en cero por culpa de otra que inunde: ya está acotada aguas arriba.

### 3.4 Qué se borra (la financiación)
- Cuerpo de `f_capLbls` (L3445-3452) y `f_capLblsOnly` (L3453-3458).
- Bloque §6.5 completo (L4544-4555): 11 sentencias con destructuring de tuplas ×5.
- `gEvtLbl` como contador manual → lo reemplaza `lblSpent`.

`gEvtCut` alimenta la fila "Ocultos · Desalojo" del panel T14 (L4968). **No se pierde el dato**: pasa a
mostrar `lblSpent/lblCap` (presupuesto consumido), que es mejor información al mismo coste — y respeta la
regla §10-#8 "nada desaparece en silencio", que es precisamente la que S123 vio violada.

## 4. Presupuesto de tokens (la medición pendiente)

Headroom actual ≈ **2 tokens**. Medido en S123: el primer fix de `i_maxShowIR` dio **100258** contra un
límite de **100256**; la versión final (2 sentencias menos) entró. O sea vivimos a ras.

| Concepto | Sentencias | Signo |
|---|---|---|
| Borrar `f_capLbls` + `f_capLblsOnly` | ~12 | **−** |
| Borrar §6.5 (11 líneas, 5 destructuring de tupla) | ~16 | **−** |
| `lblCap` (sustituye la línea de `eventCap`) | 0 neto | = |
| `lblSpent` decl | 1 | + |
| Gate en `f_evLbl` / `f_zLbl` / `f_pushSwingLabel` | ~3 × 3 = 9 | + |
| Panel: `gEvtCut` → `lblSpent/lblCap` | 0 neto | = |
| **Estimación neta** | | **claramente negativo** |

**Predicción (ESCRITA ANTES DE MEDIR):** la Opción 2 no solo cabe, **libera** tokens.

### 4.1 MEDICIÓN — la predicción era FALSA ❌

Probe generado con `scratchpad/gen_probe_budget.py` (ablación por flags) y aplicado en vivo sobre
OANDA:EURUSD **D1 modo "Todo"** (el caso saturado). `pine_check` da 0/0 en todas las variantes y **no
sirve para esto**: solo el apply mide (S107).

| Variante | Tokens | Veredicto |
|---|---|---|
| **Diseño completo (3 gates)** | **100450** | ❌ **+194 sobre el límite 100256** |
| Solo remociones (§6.5 + `f_capLbls*` fuera, sin gates) | ≤100256 | ✅ cabe |
| Gates `f_evLbl` + `f_pushSwingLabel` (sin zonas) | ≤100256 | ✅ cabe |
| Solo gate `f_evLbl` | ≤100256 | ✅ cabe |

**Conclusión de la ablación: el gate de `f_zLbl` (zonas) cuesta él solo los ~194 tokens.** El mismo gate,
palabra por palabra, es asequible en `f_evLbl` (20 call-sites) y en `f_pushSwingLabel`.

**Hipótesis descartada por la propia medición:** pensé que el coste era por call-site (referenciar un global
nuevo dentro de un helper llamado desde N sitios). Falso: `f_evLbl` tiene **20** call-sites y cabe;
`f_zLbl` tiene **9** y no. La diferencia estructural es que **`f_zLbl` era una función de UNA SOLA
EXPRESIÓN** hasta que se le metió una rama (`if` + local + return). Sospecha (NO verificada): Pine trata
distinto —¿inlinea?— las funciones de una sola expresión, y romper esa forma es lo que se paga.
**No convertir esto en doctrina sin medirlo aparte.**

### 4.2 ¿Y si se deja el gate de zonas fuera? — También medido, también NO ❌

La variante de 2 gates cabe y **cobra de verdad**: el panel T14 mostró `Presup 88/88` (saturado, y visible
en vez de silencioso). Pero el censo numérico dio **`total_labels = 501`**: las ~96 labels de zona, al no
pagar, devuelven el total al tope y **la estructura se sigue desalojando**.

→ **El gate de zonas NO es opcional. Los tres gates son necesarios y los tres no caben.**

Dato secundario del censo: `lblCap = 88` en D1/"Todo" ⇒ `estructura + EQ ≈ 404` de los 500 slots. La
estructura sola es mayor que los ~342 estimados en S123. **Caveat conocido:** `array.size(SMC_structLabels)`
cuenta labels *creadas*, y Pine ya desalojó algunas → una vez saturado, el array incluye labels muertas y la
reserva se auto-infla. La reserva medida solo es fiable **por debajo** del tope; hay que resolverlo antes de
confiar en `lblCap`.

## 5. Qué deuda cierra y cuál no

| Deuda S123 | ¿La cierra? |
|---|---|
| #7 arquitectura frágil (parches) | **Sí** — el presupuesto pasa a ser explícito, medido y cobrado en un solo punto |
| #5 estructura vieja pre-2016 sin nombre | **Sí, por construcción** — se reserva su tamaño real antes de gastar |
| Fragilidad "un default volvió a 1.5 y la estructura desapareció sin error" | **Sí** — aunque los swings inunden, ceden ellos (dibujan últimos), no la estructura |
| #1 cap top-N por tipo (balance HH/LL/HL/LH) | **No lo cierra, pero lo vuelve barato y seguro** (~2 tokens) — el techo global decide *cuántos*, el top-N por tipo decide *cuáles*. Se aplica dentro de la cuota de swing |
| #2 EQ+estructura en `f_evLbl` (anti-solape) | No — sigue pendiente, ortogonal |
| #3 zoom (límite de plataforma) | No — no tiene arreglo de fondo |
| #4 confluencia | No — es decisión de diseño, no de presupuesto |

## 6. Riesgos

1. **La estimación de tokens es aritmética de sentencias, no medición.** Pine no inlinea funciones (S107),
   así que borrar cuerpos SÍ ahorra; pero el conteo real solo existe al aplicar. → probe.
2. **`lblCap` en Operación puede quedar más apretado que hoy** (25 cobrado a TODAS las familias vs. solo a
   5). Puede que 25 sea demasiado bajo una vez se cobra de verdad. → es una recalibración de número
   (ADR-002, congelado Fase 3), no un fallo de diseño. Medir en vivo D1/H1/M5.
3. **`array.size(SMC_structLabels)` se lee en L3468, antes de que la estructura de la última barra se dibuje
   (L3773).** Desfase máximo: 1 label. Irrelevante frente a FRAME_RESERVE=8.
4. **Orden de dibujo = política.** Queda implícito en la posición del código. Documentar en §6.5bis para que
   nadie reordene sin saber que está reordenando prioridades.

## 7. VEREDICTO: la Opción 2 NO cabe hoy — faltan ~194 tokens

El plan de S124 contemplaba esta rama: *"si no cabe, ya sabremos cuántos tokens hay que liberar primero, y
caemos al plan B"*. **La cifra es 194** (100450 medido vs. 100256 de límite). Nada de esto se escribió en
`pine/`: el probe vivió en scratchpad y el slot se restauró al repo.

### 7.1 Lo que el probe deja PROBADO y capitalizable
1. **La §6.5 es token muerto y su remoción es gratis o mejor.** Confirmado en vivo. Es una fuente de
   financiación real y disponible, independiente de todo lo demás.
2. **El presupuesto se puede cobrar at-creation y se ve en el panel** (`Presup 88/88`), cumpliendo §10-#8.
3. **`estructura + EQ ≈ 404/500`**: el sistema no tiene sitio para lo demás ni acercándose. Ningún reparto
   arregla eso mientras la estructura histórica no se recorte — es la deuda #5, y es más grande de lo creído.
4. El coste está **concentrado en una sola función** (`f_zLbl`), no repartido. Eso hace el problema atacable.

### 7.2 Caminos para los 194 tokens (por orden de coste/beneficio, NINGUNO medido aún)
- **(a) Gate de zonas sin romper la forma de `f_zLbl`.** Si la sospecha "una sola expresión" es cierta,
  mantener el cuerpo como UNA expresión: p. ej. `label.new(...)` condicionado con un ternario que devuelva
  `na`, o mover el gate a la expresión del `x`. **Medir antes de creer.**
- **(b) Cobrar las zonas en su punto de entrada existente** (`f_isBandPick`/band-pick ya decide qué zona se
  dibuja) en vez de en `f_zLbl`.
- **(c) Recortar la estructura histórica** (deuda #5): es la partida de 404. Ataca la causa, no el reparto.
- **(d) Buscar los 194 en otra dieta** (patrón S121: refactor feature-preserving con helpers).

### 7.3 Plan B inmediato (lo que el usuario ya designó)
**Opción 1 suelta**: cap top-N POR TIPO en swings (~2 tokens, S123 #1) — arregla el esqueleto desbalanceado
(HH 31 / LL 19 / HL 11 / **LH 4**) que rompe la alternancia H-L-H-L de S117, y es lo que más acerca la firma
de F1-GATE. Recalibrar `i_swingDomAtr` al hacerlo (hoy 8.0 provisional, commit `fd54448`).

Opcionalmente y aparte: **aplicar solo las remociones de la §6.5** (probadas gratis) para abrir headroom
sin cambiar comportamiento — pero ojo, hoy la §6.5 es lo único que recorta EQ/pools/sweep/flip/gaps aunque
sea tarde; verificar que quitarla no empeora antes de commitear.

### 7.4 ADR
En pausa. Un ADR describe una decisión tomada; esto es un diseño **medido y rechazado por presupuesto**.
Cuando (a)/(b)/(c) den los 194, se retoma como candidato ADR-021.

## 8. S125 · La Opción 1 medida: el "~2 tokens" era fantasía (y la §6.5 la paga)

El §7.3 daba la Opción 1 por barata ("~2 tokens"). **Medido en vivo D1 "Todo", es falso**, y por el mismo
motivo que S124 ya había aprendido y que aquí se repite: *los tokens de Pine no se predicen, se miden.*

| Variante (arnés `scripts/gen_probe_swingtopn.py`) | Tokens | vs. 100256 |
|---|---|---|
| A — top-N por **fuerza** (helper nuevo `f_swThr` + `array.sort`) | 100615 | ❌ +359 |
| B — últimos-N por tipo (**sin** función nueva, bucle inline) | 100601 | ❌ +345 |
| **B + remoción de la §6.5** | cabe | ✅ **aplica y dibuja** |

### 8.1 El hallazgo que corrige la sospecha de S124
A y B se diferencian en **14 tokens**. La variante A mete una **función nueva de 6 sentencias con
`array.sort`** y la B no mete ninguna: si el coste dependiera de la *forma* del código (la sospecha
"Pine trata distinto las funciones de una sola expresión", S124 §7.2/deuda #4), la diferencia sería
enorme, no 14. **Lo caro no es la forma: es tocar el bloque.** La sospecha de S124 no queda confirmada
por esta medición — queda **debilitada**, y sigue sin ser doctrina.

### 8.2 La §6.5 confirmada como financiación real
Predicho en §7.1-1 y ahora **medido**: quitarla libera ≥345 tokens (de +345 sobre el techo a compilar y
dibujar). Verificado que **no hay regresión** (el §7.3 pedía comprobarlo antes de commitear): total de
labels 501 → 502 y la fila "Ocultos" del panel idéntica (`Est 0 · EQ 0 · Liq 0 · Ref 0`). Es coherente con
S123 H4: no recortaba nada porque no podía.

### 8.3 Resultado de la Opción 1
Censo D1 "Todo" tras el apply: **HH 12 / HL 12 / LH 12 / LL 12** (antes 31 / 11 / 4 / 19), alternancia
H-L-H-L restaurada. Criterio nuevo = **rango, no amplitud**: los últimos `i_swingTopN` de cada tipo.
`i_swingDomAtr` deja de decidir QUIÉN se dibuja y pasa a decidir solo la INTENSIDAD del tag.

### 8.4 Lo que NO arregla (y confirma la prioridad del usuario)
`total_labels` sigue en **502 ≥ 500**: la estructura histórica se sigue desalojando. La Opción 1 arregla la
LEGIBILIDAD del esqueleto, no el presupuesto. **Se confirma el juicio de S124: mientras la estructura ocupe
~404/500, lo demás es cosmética.** El cobro at-creation sigue siendo la deuda viva, ahora con la §6.5 ya
gastada como financiación — los ~194 de `f_zLbl` hay que buscarlos en otro lado (§7.2 b/c/d).
