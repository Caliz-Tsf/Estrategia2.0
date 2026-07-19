# RESPUESTA FABLE — auditoría adversarial del dossier S135

> **2026-07-18 · rama `pine/sistema-completo` · responde a
> `docs/planes/DOSSIER-FABLE-capacidad-y-codigo-muerto-S135.md` y `PROMPT-FABLE-S135.md`.**
> Método: verificación estática sobre el repo + arqueología git. **No ejecuté applies en
> TradingView** — donde una afirmación solo puede cerrarse en vivo, lo digo y dejo el experimento
> especificado con su resultado esperado en cada rama.

---

## 0. VEREDICTO EN UNA PÁGINA

- **Todo lo verificable en estático del dossier lo verifiqué y es CORRECTO** (§1): la Library
  desincronizada, los call-sites, los placeholders, el fallback de `pdMid`, el diseño de los dos
  arneses.
- **La conclusión del tree-shaking es probablemente cierta, pero la evidencia presentada no la
  prueba**: el diseño ×3 = 107986 tiene un agujero — su resultado esperado es **indistinguible de la
  firma del fallo del instrumento** (consola rancia, gotcha documentado por vosotros mismos). Hay
  atenuantes fuertes a favor (§4), y un experimento de 10 minutos que la vuelve irrefutable (§2).
- **Pregunta 1 (paradoja ADR-022): resuelta en hipótesis, con experimento decisivo.** El patrón
  "error con número → retirar muerto → aplica → causa aislada" ocurrió DOS veces (S120 y S133) y las
  dos chocan con las mediciones cuidadosas (S121, S135). Dos datos nuevos de esta auditoría lo
  inclinan: el propio ADR-022 admite que **el Visual final nunca llegó a aplicarse en S133**, y S134
  encontró el slot **con un build roto en rojo**. La hipótesis más económica: **los 100952 eran
  lecturas rancias o de buffers de desarrollo contaminados con código vivo de probes**. Los dos
  artefactos del choque están commiteados (`aee69a7` vs `f91a2bd`, difieren en EXACTAMENTE las 139
  líneas — verificado por numstat) ⇒ se puede re-medir el episodio histórico tal cual (§2).
- **Pregunta 2 (el Visual no cuadra): NO es una contradicción — es un sistema indeterminado mal
  etiquetado.** "Falla por 6" nunca fue el coste del fix: 6 = 100262 − límite. El coste real del fix
  jamás se midió (§3). Dos applies lo cierran.
- **Preguntas 3-7: respondidas en §5-§9.** Discrepo de vuestra recomendación en la Library (borrar,
  no resincronizar) y valido el reparto del dibujo con tres correcciones, una de las cuales
  **abarata el plan**: Context ya contiene toda la detección (CORE byte-idéntico) — mover una
  familia no es copiar código, es añadir call-sites.

---

## 1. LO QUE VERIFIQUÉ YO MISMO (estático + git)

| # | Afirmación del dossier | Cómo la verifiqué | Resultado |
|---|---|---|---|
| 1 | `f_tfExtremes` no tenía call-sites en Visual antes de ADR-022 | `git grep f_tfExtremes f91a2bd^ -- pine/SMC-Visual.pine` | ✅ definición en `:1931`, 0 llamadas (solo 2 comentarios) |
| 2 | El commit ADR-022 quitó "solo esas 139 líneas" | `git show --numstat f91a2bd` | ✅ Visual: **exactamente −139, +0**. Strategy/Context +9 c/u |
| 3 | El Visual apenas cambió desde entonces | `git diff --stat f91a2bd HEAD` | ✅ +20/−17 líneas (fix S134; pdMid neto 0) ⇒ **los artefactos históricos son comparables hoy** |
| 4 | `f_farthest*` muertas en Visual, vivas en Strategy/Context | grep en los 3 | ✅ 0 call-sites Visual; Strategy `:1989-1996`, Context `:1939-1946` |
| 5 | `f_wickNearLevel`: único consumidor sin red de `pdMid` | grep | ✅ exactamente 2 call-sites (`:2741/:2742`), ambos con `chartState.pdMid`; guard costó 38 = 100300−100262 (único delta de §5 medido de verdad) |
| 6 | El dibujo del EQ tiene fallback | lectura `:4465-4467` | ✅ `na(s.pdMid) ? (s.pdHigh+s.pdLow)/2.0 : s.pdMid` en `f_drawMTFState` |
| 7 | `SMC-Library.pine` desincronizada | grep de las 8 funciones | ✅ las 6 del CORE vivo: **0 menciones**; `f_resetTrailingHigh/Low` (Opción A muerta): presentes ×2 |
| 8 | `check-core-sync.ps1` no la verifica | grep "Library" | ✅ 0 menciones |
| 9 | Los 4 placeholders muertos de verdad | grep en los 4 archivos | ✅ solo definición (+ `export` en la Library rancia) |
| 10 | Arneses `gen_ablacion_core.py` / `audit_muerto_transitivo.py` | lectura completa | ✅ diseño correcto: limpieza de strings/comentarios, cierre transitivo a punto fijo, cruce ×3, anti-humo declarado. El agujero no está en los arneses sino en el instrumento (§4) |

---

## 2. PREGUNTA 1 — la paradoja ADR-022, resuelta en hipótesis + experimento decisivo

### 2.1 El patrón es sistemático, no un caso

La misma estructura inferencial ocurrió **dos veces**:

| | Error visto | Acción | Resultado | Conclusión de la sesión | Refutada después por |
|---|---|---|---|---|---|
| **S120** | CE10117 **100819** | borrar 5 funciones muertas + mover VI | aplica | "el muerto cuenta tokens" (ADR-020) | **S121**: "la dieta fue no-op" |
| **S133** | CE10117 **100952** (×2, "antes y después" del UDT) | retirar `f_tfExtremes` (139 líneas muertas) | aplica | "causa aislada" (ADR-022) | **S135**: ×3 = 107986 |

El mismo espejismo dos veces no es azar: es un **modo de fallo del método**. En ambos casos la
inferencia fue *post hoc ergo propter hoc* sobre un instrumento que vosotros mismos habéis
documentado como no confiable (lecturas rancias, applies que solo guardan, slots con builds rotos).

### 2.2 Los datos que lo inclinan (nuevos de esta auditoría)

1. **El propio ADR-022 lo confiesa** (§PENDIENTE): *"el Visual completo no llegó a aplicarse: tras
   varios ciclos la UI de TV dejó el editor en un script 'Sin nombre'... Es la única verificación
   que falta"*. El apply estaba **degradado exactamente durante el episodio**.
2. **S134 encontró el slot con un build roto en rojo** — la constancia de que en S133 quedaron
   applies fallidos dándose por buenos.
3. **El 100952 se leyó dos veces IDÉNTICO** ("antes y después" del refactor UDT). Igual que el
   107986 ×3, un número repetido exacto es tanto la firma de "el cambio no costó nada" como la de
   "la consola no se refrescó". En S133 nadie usaba aún marcador-por-build (llegó en S134/S135).
4. El gate de S133 se pasó **con probes** — y un probe es **código vivo** (labels, dumps): el orden
   de magnitud de la contaminación plausible (~700 tokens) coincide con el exceso (+696).

**Hipótesis que propongo:** los 100952 eran lecturas **rancias o de builds de desarrollo
contaminados con código vivo de probe**; la "ablación" comparó ese estado sucio contra el archivo
limpio regenerado, y el delta atribuido a `f_tfExtremes` era **la contaminación saliendo**, no las
139 líneas muertas.

### 2.3 El experimento decisivo (≈10 min de TV, cero riesgo al repo)

Los dos artefactos del choque están en git y **difieren en exactamente las 139 líneas** (§1.2-1.3):

```
A = git show aee69a7:pine/SMC-Visual.pine   (CON f_tfExtremes, el build "100952")
B = git show f91a2bd:pine/SMC-Visual.pine   (SIN f_tfExtremes)
```

Aplicar `A + lastre(305)` → `T_A`, y `B + lastre(300)` → `T_B`. **Lastres distintos a propósito**
(ver §4: los números esperados difieren en ~130-150 incluso si el muerto cuesta 0, así que dos
lecturas iguales delatarían consola rancia en el acto).

- **Si `T_A − T_B` ≈ coste(5 unidades) ≈ 130-150** ⇒ tree-shaking confirmado **sobre los artefactos
  exactos del episodio** ⇒ el 100952 fue fantasma ⇒ se corrige la justificación de ADR-020/022.
- **Si `T_A − T_B` ≈ 830-850** (≈700 del muerto + las 5 unidades) ⇒ el muerto SÍ costaba en ese
  archivo ⇒ **la medición rancia era la de S135** y todo el edificio (tree-shaking, §2 del dossier)
  se rehace con el instrumento nuevo.

Ambas ramas producen números **distintos entre sí y de los conocidos** ⇒ el experimento no puede
"pasar por rancio". Al terminar: re-aplicar el Visual de HEAD y verificar panel vivo.

### 2.4 Qué hacer con ADR-020/ADR-022

**No revocar** (vuestros avisos ya lo dicen bien: la decisión arquitectónica se sostiene por
mantenibilidad; lo cuestionado es la justificación por tokens). Tras el experimento, **anexar a
ambos la explicación resuelta** y sustituir la regla provisional por la que gane:
*"solo el código EJECUTADO cuesta tokens"* (rama 1) o la contraria (rama 2). El bloque
`EXTREMES CORE` se queda en cualquier caso — dos copias verificadas son mejores que tres aunque los
tokens no lo exijan.

---

## 3. PREGUNTA 2 — la "contradicción" del Visual NO es una contradicción

Es **un sistema con dos incógnitas y una sola ecuación**, mal etiquetado como dos hechos:

- Lo medido de verdad: `base_V + coste(fix) = 100262` (un número), y `base_V ≤ 100256` (el revert
  aplica). **Nada más.**
- *"Falla por 6"* fue una **etiqueta incorrecta**: 6 = 100262 − límite, que es el coste del fix
  **solo si** `base_V = 100256` exacto — cosa que nunca se midió. El coste real del fix es
  desconocido en [6, ∞).
- La retro-cuenta 99160 tampoco es firme: extrapola la pendiente de Context (calibrada en
  **3000-3800** unidades) a **300** unidades **en otro script** — 10× fuera del rango de
  calibración y cruzando de host. Los términos fijos (el `plot`, la cadena de suma, las cabeceras
  de chunk) se amortizan distinto a cada escala.

**Sobre la hipótesis (b) — la analicé en estático y no da la talla:** los 2 únicos call-sites de
`f_wickNearLevel` reciben `chartState.pdMid` ≡ `na` constante; lo único que un plegado de constantes
podría eliminar hoy (y el fix reviviría) es **la 4ª comprobación** (unas comparaciones) ×2
call-sites ⇒ **decenas de tokens, no ~1.100**. Si el experimento diera ~1.100, el mecanismo sería
otro no identificado — sorpresa garantizada en cualquiera de las ramas.

**Experimento que cierra §4 y §5 del dossier a la vez (2 applies):**

1. `Visual + lastre(300) + fix-slim` → `T`. Entonces **`coste(fix) = T − 107986`**, directo.
   - `≈ +6` ⇒ `base_V = 100256` y la pendiente de Context **no transfiere** (hipótesis (a)).
   - `≈ +1.100` ⇒ hipótesis (b) real a esa escala (contra mi análisis) — investigar el mecanismo.
2. `Visual + lastre(600)` → segundo punto **local de Visual** ⇒ pendiente e intercepto propios sin
   transferir nada ⇒ `base_V` medido de verdad, y de paso la no-linealidad del lastre queda
   caracterizada para siempre.

**Nota importante:** bajo CUALQUIER resolución, el fix de `pdMid` no cabe hoy (100262 > 100256 está
medido directo). La resolución de §4 cambia el **diagnóstico**, no la decisión: **el revert
`f9357a4` fue correcto.**

---

## 4. CRÍTICA DE MÉTODO — la medición ×3 = 107986 (me pedisteis desconfiar: desconfío)

**El agujero:** el resultado esperado del experimento (tres números idénticos) es **indistinguible
de la firma del fallo conocido del instrumento** (consola rancia). Un experimento cuyo éxito luce
exactamente igual que el fallo del aparato no puede autovalidarse, por muchas repeticiones que haga
— las repeticiones son precisamente lo que el fallo produce gratis.

**Atenuantes — por esto creo que la conclusión ES correcta pese al agujero:**

1. **En la misma sesión y con el mismo pipeline**, la pareja de Context dio números **distintos**
   (103355 → 126892) y la corrida de 2500 dio **"sin número"** — la consola demostró refrescarse
   entre builds. Para que el ×3 fuera rancio, el instrumento tendría que haber fallado exactamente
   en los tres builds del Visual y en ninguno de los de Context.
2. **S121 midió lo mismo por otra vía** ("la dieta S120 fue no-op") — corroboración independiente y
   anterior.
3. Coherente con la familia "la forma no cambia el coste" (S125: delta 14 ≠ 0, que además prueba
   que ALLÍ la consola sí se refrescó).

**Regla de método nueva (propuesta para `docs/reglas-dev.md`):**

> **Lastre desplazado:** todo par de builds de una ablación lleva lastres distintos (N y N+5
> unidades) de forma que los números esperados difieran en una cantidad conocida (~130-150) incluso
> si el bloque medido cuesta cero. Dos lecturas iguales = consola rancia, detectada en el acto.
> La resta sigue midiendo el bloque: `coste = ΔT − Δlastre`.

Con esa regla, el experimento de §2.3 revalida (o refuta) el hallazgo central de S135 de paso.

---

## 5. PREGUNTA 3 — `pdMid`: deuda documentada, pero con VENCIMIENTO duro

**No reabrir ahora.** Medido inerte (0 de 1235 rejections en EURUSD M5), no cabe (100262, directo),
y su coste real depende de §3. Todo correcto en el dossier.

**Pero no es deuda indefinida — tiene fecha de vencimiento estructural:** si Pine llega a la captura
de golden tests con `pdMid = na` y el EA implementa §2.7 como manda la doctrina, **`F4-GATE-A`
(paridad 100%) revienta** — o peor, se construye el EA **bug-compatible** para que los goldens
pasen, congelando el defecto en el producto final.

**Vencimiento: antes de capturar los golden tests de Fase 4.** Y el cierre natural es gratis: el
reparto del dibujo (§8) devuelve headroom al Visual; el fix de una línea (sin guard — la aritmética
de Pine ya propaga `na`) entra entonces sin pelea. Re-medir el 11/5759 tras el cierre.

---

## 6. PREGUNTA 4 — los 4 placeholders: CONSERVAR, documentados fuera del código

Confirmo vuestra recomendación de no borrar: los `KIND_*` reservan IDs de la taxonomía que el EA
replicará (el riesgo de reutilizar el 53 y divergir goldens "sin causa" es real y barato de evitar),
e `i_scoreThresh` es material declarado de Fase 3. Matiz de rigor: lo que S135 midió fue **funciones**
no llamadas; el coste de **constantes** sin uso no se midió — irrelevante a este tamaño (3
constantes), y `i_scoreThresh` sí ejecuta su `input.int` en Strategy, que tiene holgura.

**Cómo documentarlo — NO con comentarios en el código:** las `KIND_*` viven **dentro del LIBRARY
CORE** (`:173/:202/:233`, y el CORE empieza en `:154`) ⇒ añadirles un comentario-etiqueta cambia los
bytes ⇒ edición ×3 + re-baseline del SHA, fricción sin ganancia. **Registrar la reserva en docs**
(una línea en el catálogo de la taxonomía o en el informe de auditoría: "KIND_GRAB=24,
KIND_GRADIENT=53, MTF_SLOT=6, i_scoreThresh — reservas deliberadas F3/F4, no re-señalar") y, si se
quiere blindar, una lista de exclusión en `audit_muerto_transitivo.py`.

---

## 7. PREGUNTA 5 — `SMC-Library.pine`: DISCREPO — borrar (opción 2), no resincronizar

Verifiqué la desincronización completa (§1.7-1.8): faltan las 6 del motor ADR-021 y conserva las 2
de la Opción A muerta. El archivo miente, en eso estamos de acuerdo. Pero vuestra opción (1) es la
que yo no firmaría:

- **Resincronizar institucionaliza una 4ª copia sincronizada a mano** — exactamente el patrón que
  la regla dura #2 existe para matar. Y no puede entrar en `check-core-sync` tal cual: la Library
  lleva `export` y anotaciones de tipo distintas ⇒ la comparación no sería byte-a-byte sino
  **transformada** ⇒ herramienta nueva ⇒ más superficie de error, para proteger un archivo que
  **nadie importa** hasta el cierre de Fase 2.
- **La Library es DERIVABLE:** el día que toque publicarla, se regenera mecánicamente desde el CORE
  vivo (que es la única fuente de verdad, en 3 copias verificadas). Mantener fresca una derivada sin
  consumidores es trabajo recurrente a cambio de nada.
- La opción (3) deja la mentira en el árbol, solo que etiquetada: quien audite seguirá leyendo el
  diseño del P/D superado.

**Recomendación: borrarla** (git la conserva íntegra; el propósito "library publicada al cerrar
Fase 2" se anota en el ADR del reparto o en PINE-PLAN con una línea: *"se regenerará desde el CORE
al cerrar F2"*). Si el usuario prefiere conservar un placeholder físico: un archivo de 10 líneas con
el aviso y el puntero, no 1498 líneas rancias.

---

## 8. PREGUNTA 6 — LA QUE DECIDE: sí, el reparto del dibujo es el camino — con 3 correcciones

**Valido la dirección:** con 2 slots, indicadores incomunicados, Visual a ~0 y Context a ~85k
libres, repartir el **dibujo vivo** es la única vía que escala dentro de las restricciones. Pero el
plan mejora con tres correcciones:

### 8.1 El coste está sobreestimado en el dossier

*"Mover el dibujo obliga a llevar también su detección"* sugiere copiar código. **No hay nada que
copiar:** Context ya contiene el CORE completo byte-idéntico — las 43 funciones que hoy no llama son
exactamente la detección, **apagada a coste 0** por tree-shaking. Mover una familia =
**añadir call-sites** (+ su bloque de dibujo) en Context y **retirar call-sites de dibujo** en
Visual. Lo que se paga es la **ejecución** en el presupuesto de Context — que es para lo que están
sus ~85k.

### 8.2 El eje del reparto: por TF/ROL, no por familia arbitraria

**Context absorbe TODO el dibujo HTF (D1/H1); Visual conserva la operación chart-TF/M5.**

- Coincide con la razón de existir de Context (**ADR-017**: contexto HTF heredado) — el usuario lee
  "un indicador = contexto, el otro = operación", no una partición arbitraria de familias.
- **Evita el muro de S105** (motor M5 vía `request.security` = OOM): la dirección segura es Context
  pidiendo D1/H1 por security — mover conceptos M5 a Context sería nadar hacia la cascada.
- El panel de Visual no cambia (usa su propia detección) y **ADR-023 sigue válido tal cual**.

### 8.3 El tercer slot existe EN EL TIEMPO

La Strategy solo ocupa slot **cuando se backtestea**. Visual + Context para sesiones visuales; swap
a Strategy para Fase 2/3. La restricción real es de 2 slots **por momento**, no por proyecto — el
reparto solo tiene que servir al workflow de validación visual.

### 8.4 Mediciones previas obligatorias (con el instrumento de §4), en orden

1. `base_V` real con 2 puntos de lastre **en Visual** (§3.2) — sin esto, todo presupuesto es fe.
2. **Ablación por familia del bloque DIBUJO** del Visual bajo lastre ⇒ coste real en tokens de cada
   familia de dibujo (las líneas engañan — lección repetida del proyecto).
3. **Probe de Context con una familia HTF viva** (detección encendida + dibujo) ⇒ coste real de
   "encender" una familia allí. Con 1-2-3, el reparto es **aritmética, no fe**.

### 8.5 Dos cosas que el ADR del reparto debe decir explícitamente

- **La alternativa financiera, nombrada:** los 2 slots son una restricción del **plan gratuito** de
  TradingView, no de la técnica. Un plan de pago da más slots por unos dólares al mes. No es mi
  decisión ni la recomiendo por defecto — pero una restricción financiera no debe quedar disfrazada
  de restricción técnica en un ADR. Si las mediciones 1-3 salen limpias, probablemente ni haga falta.
- **ADR nuevo obligatorio:** ADR-017 declaró Context "reversible, no toca Visual/Strategy/SHA". El
  reparto lo convierte en **pieza estructural del sistema**. Eso es un cambio de estatus que
  requiere su propio ADR con la lista explícita de familias por consumidor (y evita el doble render
  del P/D si ambos dibujaran lo mismo).

---

## 9. PREGUNTA 7 — determinismo: el criterio es correcto en la idea, incompleto en la letra

**Reformulación que propongo** (la vuestra + la cláusula que le falta):

> El dealing range es **función pura de las últimas W(TF) barras confirmadas**, con W declarado por
> TF: para cualquier profundidad de historia ≥ W(TF), el resultado es **idéntico barra a barra**
> (**invariancia al prefijo**).

Sin la cláusula de invariancia, "reproducible dado un conteo mínimo" solo es comprobable contra sí
mismo. Con ella, el test existe y ya lo tenéis: **la matriz de 9 celdas de S134 ES el test de
invariancia** (el chart-TF es el generador natural de profundidades distintas). Hoy falla por
diseño; con W real, pasa — y la F1-GATE gana un criterio medible.

**Fase de cierre: ANTES de arrancar el backtesting de Fase 3.** No basta "antes de Fase 4": `F3-T01`
(corte IS/OOS) presupone determinismo — si la calibración entera de Fase 3 se hace sobre un motor
historia-dependiente, **toda la Fase 3 es irrepetible**, y los goldens de F4 heredan el vicio. El
coste que ADR-023 evitó (ventana real: SHA ×3, riesgo OOM, tokens) no desaparece: **se paga en la
frontera F2→F3, con el headroom que el reparto habrá devuelto al Visual**. Eso ordena el plan solo:
reparto primero, ventana después.

**Independiente del cierre:** los golden tests de F4 deben capturarse sobre **datasets congelados y
versionados** (OHLCV exportado), nunca sobre "la historia que TV sirva ese día". Es buena práctica
aunque el determinismo ya esté cerrado — hace los goldens re-ejecutables para siempre.

---

## 10. ORDEN RECOMENDADO (y por qué)

1. **S136-A — sesión de instrumento y medición (~6 applies):** regla del lastre desplazado (§4) +
   los 3 experimentos: par histórico `aee69a7`/`f91a2bd` (§2.3), `Visual+lastre+fix` y 2º punto de
   lastre en Visual (§3). Cierra las Preguntas 1 y 2 **con números** y revalida (o tumba) el
   hallazgo central de S135 de paso.
2. **Anexar la resolución a ADR-020/ADR-022** (no revocar) y fijar la regla de tokens definitiva.
3. **Matriz concepto × TF × {nativo, heredado}** (la sesión de conceptos ya planificada) — es el
   **inventario de familias** que el reparto necesita como entrada. Hacerla antes del reparto evita
   auditarla dos veces.
4. **ADR del reparto por TF/rol** con la aritmética de §8.4 y la lista explícita de familias;
   ejecutar por familias con gate visual por familia.
5. **`pdMid` se cierra dentro del reparto** (headroom recuperado) — antes de cualquier golden.
6. **Pendientes F1-GATE** (fallback M2, IFVG por banda/lado, gate MB/BPR, `elig`/ZS_MITIGATED,
   `LEG_ANCH_TOL_ATR`, deudas S123, herencia MTF) — y la **ventana real del determinismo en la
   frontera F2→F3** (§9).

---

## 11. LAS 7 PREGUNTAS EN UNA LÍNEA CADA UNA

| # | Pregunta | Respuesta |
|---|---|---|
| 1 | ¿Por qué "funcionó" ADR-022? | Hipótesis: lecturas rancias/contaminadas por probes en S133 (patrón repetido de S120); decisivo: par histórico `aee69a7` vs `f91a2bd` con lastre desplazado. No revocar ADRs; anexar la resolución. |
| 2 | ¿(a) o (b)? | Ninguna tal como están planteadas: era un sistema indeterminado ("falla por 6" ≠ coste del fix). Mi análisis estático hace implausible (b) a escala 1.100. Dos applies lo cierran. |
| 3 | ¿Reabrir `pdMid`? | No ahora; deuda con vencimiento duro: **antes de capturar goldens F4** (si no, EA bug-compatible). Se cierra gratis dentro del reparto. |
| 4 | ¿Placeholders? | Conservar los 4; documentar la reserva en docs + lista de exclusión del arnés, **no** con comentarios dentro del CORE (romperían el SHA ×3). |
| 5 | ¿Library? | **Borrar** (discrepo de resincronizar): es derivable del CORE, nadie la importa, y una 4ª copia manual es el anti-patrón de la regla dura #2. Se regenera al cerrar F2. |
| 6 | ¿Reparto del dibujo? | **Sí**, con eje TF/rol (Context=HTF, Visual=operación), coste corregido a la baja (el código ya está en Context), 3 mediciones previas, ADR nuevo, y la alternativa financiera nombrada. |
| 7 | ¿Criterio de determinismo? | Añadir **invariancia al prefijo** con W(TF) declarado; el test es la matriz de 9 celdas de S134; cierre en la **frontera F2→F3**; goldens F4 sobre datasets congelados en cualquier caso. |
