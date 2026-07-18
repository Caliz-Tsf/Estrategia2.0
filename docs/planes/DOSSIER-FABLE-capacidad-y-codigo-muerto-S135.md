# DOSSIER FABLE — Capacidad del presupuesto de tokens, código muerto y el reparto del dibujo

> **Sesión 135 · 2026-07-18 · rama `pine/sistema-completo`**
> **Autocontenido:** no hace falta leer la sesión. Todo lo necesario está aquí.
> **Estado del repo al entregar:** CORE SHA `9559a0d7fe58b213` (1776 líneas) **intacto**,
> `check-core-sync` OK ×3 + EXTREMES CORE OK, `pine/` sin cambios netos en toda la sesión.

---

## 0. QUÉ TE PEDIMOS

Tres cosas, en este orden:

1. **AUDITAR** — verificar que lo que afirmamos abajo es cierto. Marcamos con `[MEDIDO]`,
   `[NO MEDIDO]` y `[OPINIÓN]` cada afirmación. **Desconfía especialmente de los `[MEDIDO]`:**
   esta sesión ya destapó que dos ADR del proyecto afirmaban algo falso, y que un arnés de
   medición midió humo dos veces antes de funcionar.
2. **RESOLVER 2 CONTRADICCIONES ABIERTAS** que no hemos podido cerrar (§4 y §5).
3. **RECOMENDAR EL CAMINO** para poder cumplir el alcance completo de Fase 1 sin romper el
   workplan ni sus reglas duras (§7). El usuario ha sido explícito: *"debemos cumplir totalmente
   el plan y sus reglas"* — no se acepta deuda permanente contra una regla dura.

Después de tu revisión, la siguiente sesión repasa **qué conceptos hay y cuáles faltan**, y luego
se continúa con las tareas pendientes de la F1-GATE.

---

## 1. CONTEXTO MÍNIMO

- **Arquitectura:** 1 `LIBRARY CORE` byte-idéntico + 3 consumidores: `SMC-Visual.pine` (4981
  líneas), `SMC-Strategy.pine` (2804), `SMC-Context.pine` (2138). **Regla dura #2:** el CORE es
  byte-idéntico en los tres. Verificado por `scripts/check-core-sync.ps1`.
- **Los indicadores NO pueden comunicarse en ejecución** (restricción de TradingView). Cada
  consumidor calcula lo que dibuja.
- **⚠️ RESTRICCIÓN NUEVA Y DURA:** el usuario está en el **plan GRATUITO de TradingView = máximo
  2 indicadores por gráfico.** Hoy están aplicados Visual + Context. **No hay un tercer hueco.**
- **Techo de tokens de Pine: 100256.** Error `CE10117` al superarlo.
- **F1-GATE bloqueada.** El alcance real que exige el usuario para firmarla: *todas las familias
  de concepto, sus variantes, los 3 TF y la herencia MTF*, auditadas concepto × TF ×
  {nativo, heredado}. Esa matriz **no está hecha**.

---

## 2. EL HALLAZGO PRINCIPAL — en Pine una función NO LLAMADA cuesta CERO tokens

`[MEDIDO — triple, apply real en OANDA:EURUSD, límite 100256]`

Método: **lastre calibrado**. El conteo de tokens de TV **solo es visible por encima del techo**,
así que se añade relleno que mantiene el script por encima en *todas* las lecturas; la resta es
exacta y no hace falta calibrar el lastre.

| Build | Tokens |
|---|---|
| Visual + lastre | **107986** |
| Visual + lastre **− 3 funciones sin call-site** (101 líneas) | **107986** |
| Visual + lastre **+ 36 funciones duplicadas y no llamadas** (590 líneas) | **107986** |

**Tres builds, el mismo número exacto.** Quitar 101 líneas no llamadas: 0 tokens. Añadir 590
líneas no llamadas: 0 tokens. ⇒ **Pine hace tree-shaking completo de las funciones sin call-site.**

Arnés: `scripts/gen_ablacion_core.py` (commit `42207ea`). Reproducible.

### 2.1 Esto CONTRADICE dos ADR del proyecto

- **ADR-020** y **ADR-022** afirman: *"en Pine una función no-llamada SÍ cuenta tokens
  (confirmado empíricamente en S120)"*. **Según esta medición, es FALSO.**
- **S121** había medido lo contrario: *"Pine tree-shakea funciones no-llamadas; la dieta S120 fue
  no-op"*. **Concuerda con lo medido ahora.**
- El proyecto arrastraba **dos hallazgos incompatibles** sin que nadie los cruzara.

**`[NO MEDIDO]` — PREGUNTA 1 PARA TI:** entonces, **¿por qué el fix de ADR-022 (retirar
`f_tfExtremes`, 139 líneas que el Visual no llamaba) resolvió el `CE10117` en S133?** No lo hemos
re-medido. Hipótesis sin comprobar: que `f_tfExtremes` sí tuviera un call-site en Visual, o que su
retirada coincidiera con otro cambio. **Si ADR-020/ADR-022 se sostienen sobre una premisa falsa,
hay que corregirlos.**

### 2.2 Consecuencia práctica

La regla correcta **no** es *"solo retirar código ahorra"* sino **"solo retirar código QUE SE
EJECUTA ahorra"**. Todo plan de dieta basado en retirar código muerto es un **no-op**.

---

## 3. CAPACIDAD MEDIDA DE LOS DOS CONSUMIDORES

`[MEDIDO]` — dos lecturas propias + un cross-check independiente.

| Build | Tokens |
|---|---|
| Context + 2500 unidades de lastre | bajo el techo (sin número) |
| Context + 3000 unidades | **103355** |
| Context + 3800 unidades | **126892** |

⇒ unidad de lastre = (126892 − 103355)/800 = **29.42 tokens**
⇒ **Context solo ≈ 15.100 tokens** (15% del techo)
⇒ **hueco libre en Context ≈ 85.000 tokens (85%)**

**Cross-check que pasa:** la corrida de 2500 predice 88.644 < 100256 ⇒ coherente con que saliera
bajo el techo sin número.

**Reparto del Visual por bloques (líneas, no tokens):** `LIBRARY CORE` ~1776 · `DETECCIÓN TF
PROPIO` ~953 · `MTF` ~455 · **`DIBUJO` ~1411** · `PANEL`+`ALERTAS` ~236.

⇒ `[OPINIÓN]` Context tiene sitio de sobra para absorber dibujo vivo. Pero **no** porque vaya a
soltar código muerto (ese ya cuesta cero), sino porque **ejecuta muy poco**.

---

## 4. ⚠️ CONTRADICCIÓN ABIERTA #1 — el Visual no cuadra consigo mismo

`[NO MEDIDO — no la hemos resuelto, y NO construimos nada encima]`

- Retro-cuenta desde el lastre: Visual ≈ **99.160** tokens.
- Pero las medidas de `pdMid` de esta misma sesión lo situaban en ≈ **100.250** (ver §5).
- **Diferencia ≈ 1.100 tokens.** Una sola sentencia no explica eso.

Dos hipótesis, **ninguna comprobada**:

- **(a)** el coste del lastre no es perfectamente lineal — hay un término por función de troceo
  (~84 tokens) que un modelo de 2 puntos no separa.
- **(b) INTERACCIÓN DE TREE-SHAKING:** asignar `chartState.pdMid` mantiene vivo código que hoy se
  elimina ⇒ el fix no cuesta *una línea*, cuesta **la cadena que revive**.

**PREGUNTA 2 PARA TI:** ¿cuál es? Si es la **(b)**, **reencuadra por completo** el episodio de
`pdMid` (§5): dejaría de ser *"una línea que no cabe por 6 tokens"* y pasaría a ser *"una línea que
resucita ~1.100 tokens de código muerto"* — y eso cambia también cómo hay que leer cualquier futura
adición al Visual.

---

## 5. EL EPISODIO `pdMid` — un fallo silencioso real, medido como inerte, y revertido

`[MEDIDO]`

**El defecto:** el bloque chart-TF asignaba `pdLow`/`pdHigh` pero **nunca** `pdMid`, que quedaba en
su default `na`. Las lecturas de `f_wickNearLevel` (Rejection §2.7) recibían ese `na` ⇒ **el borde
EQ nunca participaba en la confluencia de mecha**. Muerto desde el Sprint 1.5 (commit `5bc4828`).

**Verificación en vivo** (probe v15, EURUSD M5, chart en M5, 5759 barras confirmadas, A/B de
`f_wickNearLevel` con `pdMid` vs con `na`, en el mismo punto del script):

```
pdHigh=1.14737  pdLow=1.13335  pdMid=1.14036  (esperado 1.14036)  nMidNa=0
nDiffLow=2  nDiffHigh=9   impacto=0.19%
nRejTotal=1235  nRejDiff=0
```

⇒ el ancla difiere en **11 barras de 5759**, y en **ninguna** de ellas se cumple además la
geometría de rechazo ⇒ **CERO rejections cambian**. Con 1235 rejections detectadas, **no es un cero
trivial**. Causa: `f_wickNearLevel` **cortocircuita** (zonas → pools → EQH/EQL → **EQ** → EMAs); el
borde EQ es la 4.ª comprobación y casi siempre queda tapado.

**Y no cabe:**

| build | tokens | vs 100256 |
|---|---|---|
| fix con guard `na(...) ? na :` | 100300 | **+44** |
| fix adelgazado (aritmética pura; Pine ya propaga `na`) | 100262 | **+6** |

El guard costaba **38 tokens**. Ni la versión mínima entra. **Revertido** (`f9357a4`).

**Dato adicional verificado en pantalla:** el **dibujo** del EQ nunca estuvo afectado —`:4467` ya
tiene el fallback `na(s.pdMid) ? (s.pdHigh + s.pdLow)/2.0 : s.pdMid`. El único consumidor sin red
era `f_wickNearLevel`.

**Error de método propio, registrado:** se commiteó el fix afirmando *"compila 0/0"* como si eso lo
validara. **`pine_check.py` es server-side y NO CUENTA TOKENS.** Rompió el apply en vivo.
Norma nueva: con el presupuesto en ~0, **ningún cambio a `pine/` se da por bueno sin apply real**.

**PREGUNTA 3 PARA TI:** ¿merece la pena reabrirlo? Es un defecto real de doctrina (§2.7 admite el
borde EQ como ancla válida) pero **medido como inocuo** en EURUSD M5. Y el coste real depende de
resolver la §4.

---

## 6. AUDITORÍA DE CÓDIGO MUERTO — qué es borrable de verdad

`[MEDIDO estáticamente, con cierre transitivo hasta punto fijo, sobre código sin comentarios ni
strings]` · arnés `scripts/audit_muerto_transitivo.py` (commit `3e1b448`)

| Archivo | Funciones | Muertas (transitivo) | Constantes sin uso |
|---|---|---|---|
| `SMC-Visual.pine` | 120 | 3 | 4 |
| `SMC-Strategy.pine` | 71 | 1 | 3 |
| `SMC-Context.pine` | 71 | **43** | **53** |

**Resultado que manda: NINGUNA función está muerta en los 3.** Las 43 que Context no llama están
**vivas en Visual o Strategy**. Borrarlas de Context rompería la **regla dura #2**. Eso no es
limpieza, es **relocalización** (patrón ADR-020/ADR-022) — y, tras §2, **no compra ni un token**.

### 6.1 Lo único borrable, y por qué recomendamos NO borrarlo

`KIND_GRAB` (=24), `KIND_GRADIENT` (=53), `MTF_SLOT` (=6) e `i_scoreThresh`. Verificados a mano uno
a uno, incluyendo strings y comentarios: muertos de verdad. Pero `[OPINIÓN]` **son andamiaje
deliberado**:

- Los `KIND_*` son **IDs de la taxonomía de eventos**, que el EA MQL5 replicará en Fase 4. Borrarlos
  arriesga que alguien reutilice el 53 y **los golden tests diverjan** sin causa aparente.
- `i_scoreThresh` lleva la etiqueta literal *"Score threshold (calibrar Fase 3)"*.

Y borrarlos **ahorra 0 tokens** (§2). **PREGUNTA 4 PARA TI:** ¿confirmas dejarlos documentados como
reservas, o los quitamos?

### 6.2 🔴 EL PROBLEMA DE AUDITABILIDAD MÁS SERIO — `pine/SMC-Library.pine`

`[MEDIDO]` 1498 líneas. **No lo importa nadie** (cero `import` en los 3 consumidores). Y está
**desincronizado con el CORE vivo**:

- Le **faltan 6** funciones del CORE: `f_farthestEvent` / `f_farthestPool` / `f_farthestZone` y
  **`f_pdBottom` / `f_pdRelatch` / `f_pdTop`** (el motor del 2.º extremo, **ADR-021**).
- **Conserva 2** que el CORE ya no tiene: **`f_resetTrailingHigh` / `f_resetTrailingLow`** — que son
  exactamente las de la **Opción A que ADR-021 sustituyó**.

⇒ No está solo rancio: **encierra el diseño del P/D que ya fue superado**. Último commit S120;
`check-core-sync.ps1` **no lo verifica**, así que deriva en silencio. Para quien audite el repo,
**ese archivo miente**.

**PREGUNTA 5 PARA TI:** ¿(1) resincronizarlo y meterlo en `check-core-sync`, ¿(2) borrarlo (git lo
conserva), o ¿(3) congelarlo con un aviso de SUPERSEDIDO? Nuestra `[OPINIÓN]`: la (1), porque
conserva su propósito declarado (migrarlo a library publicada al cerrar Fase 2) y elimina la
mentira.

---

## 7. EL PROBLEMA ESTRUCTURAL — y la pregunta que de verdad importa

El alcance que el usuario exige para firmar la F1-GATE (todas las familias × variantes × 3 TF ×
herencia) **no cabe en un solo indicador**. Datos duros:

- Visual: ~99.200–100.250 tokens de 100256 (el rango es la §4 sin resolver). **Headroom ≈ 0.**
- Context: ~15.100 de 100256. **Headroom ≈ 85.000.**
- **Solo hay 2 slots** (plan gratuito).
- El código muerto **no libera nada** (§2). **Solo mover/retirar código VIVO libera.**

`[OPINIÓN]` La única vía que escala es **repartir el DIBUJO vivo entre los 2 consumidores** — pero
con un coste que hay que cuantificar: como los indicadores **no se comunican**, mover el dibujo de
una familia a Context obliga a llevar **también su detección**, y eso duplica coste en Context (no
en el total, pero sí en su presupuesto).

**PREGUNTA 6 — LA QUE DECIDE:** ¿es ése el camino, o ves uno mejor? Restricciones que **no** se
pueden violar: regla dura #2 (CORE byte-idéntico), regla dura #1 (determinismo, ver §8), regla dura
#8 (ningún gate se salta ni se ajusta el criterio), 2 slots, y ADR-002 (nada se calibra a ojo
sobre un símbolo).

---

## 8. LA DEUDA DE DETERMINISMO (ADR-023) — el usuario NO la acepta como permanente

**ADR-023** (esta sesión) cerró el defecto chart-TF con una **regla de operación, cero código**:
*el panel y el dibujo del P/D son válidos leídos desde el TF más bajo de los que se muestran* (3
columnas ⇒ chart en M5). Base `[MEDIDO en S134]`: una columna vale **SII `chart-TF <= TF de la
columna`**, y desde chart M5 las tres dan 34/74/91 = la tabla del gate.

**Deuda: BLOQUEANTE, no aceptada** (corregido por decisión del usuario). El 2.º extremo sigue
dependiendo de **cuánta historia sirva TV** ⇒ viola la **regla dura #1**.

**Criterio de cierre propuesto** `[OPINIÓN, valídalo]`: *el dealing range debe ser reproducible dado
un conteo mínimo de barras declarado por TF*.

**Riesgo aguas abajo, corrigiendo una afirmación demasiado cómoda del propio ADR-023:** dijimos que
*"el artefacto no existe en MQL5"*. Es cierto **solo del artefacto chart-TF**. La dependencia de
profundidad de historia **no desaparece**, y aterriza en:

- **Fase 3** — reproducibilidad del backtest; `F3-T01` (corte IS/OOS) presupone determinismo.
- **Fase 4** — **paridad de golden tests**: si Pine calcula el 2.º extremo sobre la historia que TV
  sirvió y el EA sobre un conteo fijo, **no tienen por qué coincidir**. `F4-GATE-A` exige 100%.

**PREGUNTA 7 PARA TI:** ¿el criterio de cierre es el correcto, y en qué fase debe cerrarse para no
comprometer `F4-GATE-A`?

---

## 9. TRAMPAS DE MÉTODO ATRAPADAS (para que no las repitas al verificar)

Todas `[MEDIDAS]` en esta sesión:

1. **`pine_check.py` NO cuenta tokens** (server-side). 0/0 no valida nada cerca del techo. El número
   real está en `pine_get_console`.
2. **Un lastre que se asigna y no se lee lo TREE-SHAKEA Pine entero** ⇒ el build sale bajo el techo
   y *no hay medición* (`Compilando... → guardado`, sin número). Hay que hacerlo desembocar en un
   `plot`.
3. **Demasiadas sentencias en el cuerpo principal** ⇒ `The main body of the script is too long`.
   El lastre debe vivir **dentro de funciones**.
4. **Una sola función gigante** vuelve a topar ese límite ⇒ trocear (200 sentencias por función).
5. `pine_inject.py` **solo GUARDA** (busca botones en inglés; el TV está en español). Apply real =
   inject + clic en "Añadir al gráfico"/PLAY + confirmar en consola. **El clic a veces solo guarda y
   hay que repetirlo.**
6. `data_get_study_values` **sigue el crosshair** y devuelve builds rancios ⇒ volcar por `label` en
   `islast` y usar un marcador nuevo por build.

---

## 10. COMMITS DE LA SESIÓN (todo verificable)

```
5094d2a  fix(pine-visual)      pdMid nunca se asignaba          [REVERTIDO por f9357a4]
16600dd  docs(doctrina)        ADR-023 + §2.3.2 reescrita
e860553  test(probe)           arnés v15 de pdMid + medición
f9357a4  revert(pine-visual)   pdMid no cabe (+6) y es inerte
d1166d4  docs(cierre)          Sesion-135
e033dd3  test(audit)           auditoría estática de código muerto
42207ea  test(ablacion)        el código muerto cuesta CERO tokens
df2cf72  test(ablacion)        Context ~15k usados, ~85k libres
3e1b448  test(audit)           auditoría transitiva + cruce de los 3
```

---

## 11. RESUMEN DE LO QUE TE PEDIMOS

| # | Pregunta | Dónde |
|---|---|---|
| 1 | ¿Por qué "funcionó" el fix de ADR-022 si el código muerto cuesta cero? ¿Hay que corregir ADR-020/ADR-022? | §2.1 |
| 2 | ¿(a) no-linealidad del lastre o (b) interacción de tree-shaking? Reencuadra `pdMid`. | §4 |
| 3 | ¿Reabrir `pdMid` o dejarlo como deuda documentada? | §5 |
| 4 | ¿Los 4 placeholders se quedan documentados o se borran? | §6.1 |
| 5 | `SMC-Library.pine`: ¿resincronizar, borrar o congelar? | §6.2 |
| 6 | **LA QUE DECIDE** — ¿repartir el dibujo entre 2 slots es el camino? ¿Coste? ¿Alternativa mejor? | §7 |
| 7 | ¿Criterio de cierre del determinismo y fase en que debe cerrarse? | §8 |

**Formato de respuesta que nos sirve:** para cada punto, **qué has verificado tú mismo** (y cómo),
qué **refutas**, y el **esqueleto** de la solución que recomiendas con su **coste estimado** y la
**medición previa** que habría que hacer antes de tocar `pine/`. No hace falta código.

**Después de tu revisión** la siguiente sesión repasa qué conceptos hay y cuáles faltan
(matriz concepto × TF × {nativo, heredado}), y luego se continúa con las tareas pendientes de la
F1-GATE: fallback M2, IFVG por banda/lado, gate MB/BPR, `elig` excluye `ZS_MITIGATED`, calibrar
`LEG_ANCH_TOL_ATR`, deudas S123 y herencia MTF.
