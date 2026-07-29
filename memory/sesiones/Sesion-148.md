# Sesión 148 — 2026-07-28

## Objetivo
Ejecutar el plan que S147 dejó íntegro: medir el coste en objetos del tramo, implementar
**ADR-027** por subconjuntos verificando cada uno en TradingView, y verificar el grab en
H1/M5 con casos nativos fechados. Tareas 1-3 de 4 completadas; la tarea 4 (curación de la
familia Liquidez, objetivo original heredado de S144) queda para S149.

## Tarea 1 — Medición del coste en objetos (completada)

Instrumento: `data_get_pine_lines` / `data_get_pine_labels` devuelven **`total_lines` /
`total_labels`**, el censo CRUDO de objetos (lo que engañaba desde S144 era
`horizontal_levels`, que deduplica). Truco de medición barato: `max_labels: 1` da el total
sin pagar el volcado completo.

**Trampa metodológica descubierta a mitad de la medición:** la banda del DOL depende del
RANGO VISIBLE (ADR-026), así que dos lecturas con distinto rango no son comparables. Las
dos primeras medidas (+21 y +20) estaban contaminadas por mover el rango entre lecturas
para sacar capturas; repetidas con rango fijo dieron **+40 exactas**.

**Coste de ADR-027** (D1 EURUSD, familia Liquidez aislada, densidad *Todo*, rango visible
fijo):
- Grab + Sweep/Raid/Spring: **+40 líneas exactas** (20+20, los dos caps), aislado con
  toggle `in_84` off/on.
- Pool barrido: **+2**, aislado bajando la cuota de 20 a 1 (Δ = 1).
- Total: **+42 líneas** sobre las 125 de la familia.

**HALLAZGO 1 (el importante).** El tope de 500 **ya estaba desbordado antes de este ADR**,
y la culpable no es Liquidez sino **ESTRUCTURA**. Con todos los toggles encendidos: *Todo*
**501 líneas / 503 etiquetas**; *Estudio* **504 / 500**; *Operación* 59 / 136. Los topes
son 500 y 500 ⇒ el Visual lleva tiempo desalojando objetos en silencio, y Pine borra los
creados PRIMERO (los de más señal). Aislando familia por familia: Liquidez completa **97**,
grid (`in_72`+`in_73`) **6**, y **`in_10` («Mostrar BOS/CHoCH (swing)») él solo 302 líneas +
302 etiquetas** — el 60% del presupuesto en un único toggle, que además es el único
concepto de estructura **sin cuota `i_maxShow*`** (flip, CISD, displacement, sweep... todos
tienen la suya en 20). El diagnóstico intuitivo del propio ADR-027 §4 («la familia Liquidez
es la más frecuente, el tramo la va a reventar») era falso: la frecuencia del evento no
predice el gasto, lo predice si el dibujo tiene cuota o no.

**HALLAZGO 2.** El subconjunto 3 (pool barrido) nace casi inerte: solo **2 tramos** en toda
la historia D1. No es por el filtro anti-duplicado, es por el ciclo de vida (ADR-006):
`f_prunePools` borra primero los pools barridos, así que apenas sobreviven en el array para
llegar a dibujarse. Si se quiere ver de verdad el historial de pools tomados, hay que tocar
la poda, no el dibujo.

## Tarea 2 — ADR-027 D1 implementado por subconjuntos (completada)

Tres commits, uno por subconjunto, cada uno aplicado en TV y medido antes de pasar al
siguiente:

- `e57c68a` — **grab**. CORE gana `SMC_Event.origBarTime`; `f_detectGrab` lo rellena con
  `p.barTime`. Línea punteada del pivote aislado a la vela que lo perfora, nombre en el
  punto medio (idioma de `f_drawEQHL`), etiqueta hacia afuera del precio (ADR-027 D3).
- `4f59c83` — **sweep/raid/spring**. Bug encontrado al implementarlo, que habría dado un
  tramo falso: el ADR pide el PRIMER toque del pool como origen, pero `SMC_Pool.barTime`
  guarda el ÚLTIMO (`f_upsertPool`, `if barTime > p.barTime`). Para el grab da igual
  (`touches`=1 por definición, primero == último); para el sweep no. Se añade
  `SMC_Pool.firstBarTime`, fijado en el ALTA y nunca tocado por el merge; `f_detectSweep`
  lo propaga.
- `4988819` — **pool barrido**. Reabre lo que S144 retiró, con la diferencia que el ADR §3
  exige (va al origen real y lleva el nombre al medio). Dotted y muere en la vela del
  barrido (el pool vivo es dashed y llega hasta la barra actual). Solo Estudio+. Filtro
  anti-duplicado: si ese barrido ya emitió un sweep, el tramo sería el MISMO segmento;
  `f_evLbl` deduplicaría la etiqueta pero NO la línea, así que se filtra en origen.

`390164e` — ADR-027 pasa de PROPUESTO a **ACEPTADO E IMPLEMENTADO (D1 completo)**, con §4.1
nueva que documenta la medición y los dos hallazgos. **D2 (Judas y False breakout SIN
tramo) sigue vigente y sin código**, que es lo que decide.

CORE byte-idéntico ×3 verificado en cada paso → **1813 líneas, SHA `b2be604143c08a83`**
(venía de 1809 / `5e21ca38b43cf0e4`). Compila 0 errores. TV: `SMC_Library` v419 → **v422**
guardado.

## Tarea 3 — Verificación del grab en H1 y M5, nativa y fechada (completada)

Cierra el pendiente que ADR-027 §6 declaraba independiente (la validación de S146, 96/100,
se apoyaba en la correspondencia regla↔código porque los 3 casos canónicos de §3.3 son de
M5 2026-06-10/11 y el histórico M5 de OANDA ya no los alcanza).

El censo de dibujos no sirve para fechar: devuelve índices de una tabla de coordenadas y
precios redondeados a 2 decimales. Se resolvió con reimplementación independiente de §3.3
sobre las velas nativas de cada TF (`scripts/gen_probe_grab_nativo.js`: pivotes simétricos
len=5 → upsert de pools con tol 0.1×ATR14 → marcado de barridos → grab con `touches<2` y
`close` de vuelta dentro), contrastada contra lo que dibuja el indicador y verificada en
pantalla.

- **H1** (401 velas desde 2026-07-06, 46 pools, 18 grabs). Caso ancla: Grab BSL
  2026-07-22 13:00 UTC, nivel 1.14184 (pivote aislado del mismo día 07:00, 1 toque), mecha
  1.14217 > nivel, close 1.14135 < nivel, ATR14 0.00077. El tramo dibujado va de 03:00 a
  09:00 hora del chart (UTC-4) = 07:00→13:00 UTC con el nombre en el medio: coincide.
- **M5** (300 velas desde 2026-07-27 23:55, 23 pools, 6 grabs, todos del 2026-07-28). Grab
  BSL 12:50 UTC nivel 1.13679 (pivote del 11:50), mecha 1.13685, close 1.13654. Grab SSL
  12:30 UTC nivel 1.13612, mecha 1.13608, close 1.13624; su punto medio cae en 08:10 hora
  del chart, que es donde el indicador pone la etiqueta.
- Salvedad anotada en el propio doc: la sonda solo ve las velas cargadas por TV, Pine
  recorre un buffer más largo ⇒ el indicador dibuja más grabs (20 en H1, su cuota, y 14 en
  M5) que los que cuenta la sonda (18 y 6). No es discrepancia; los casos concretos
  coinciden uno a uno.

Commits `31ba71b` (§3.3 de `reglas-smc-ict.md` + la sonda versionada) y `8ede405`
(ADR-027 §6 → RESUELTO).

## Obstáculo de herramienta (costó tiempo real)

Un modal promocional de TradingView ("intervalos personalizados / Prueba gratuita de 30
días") bloqueó la UI: `chart_set_timeframe` devolvía `{success:true}` sin cambiar nada y
`chart_set_visible_range` daba un `actual` absurdo. Además, pedir un rango visible largo
estando en M5 hace que TV auto-cambie la resolución (acabó en 6M). Se sale cerrando el
modal por DOM con `document.querySelector('button[aria-label="Cierre"]').click()` — está en
español, buscar `/close|cerrar/i` NO lo encuentra — y forzando el TF con
`TradingViewApi._activeChartWidgetWV.value().setResolution('5')`. Reaparece: hay que
cerrarlo más de una vez. Y otra vez la lección de S145: la sonda de DOM decía que el modal
no estaba y la captura lo mostraba — la captura tenía razón.

## Estado de gates y bloqueos
- F1-GATE sigue sin firmar. Ninguna fase completada ⇒ sin tag git.
- Sin bloqueos nuevos.

## Commits de la sesión
`e57c68a`, `4f59c83`, `4988819`, `390164e`, `31ba71b`, `8ede405`.

## Pendiente (pasa a S149)
1. Tarea 4 de S148, no ejecutada: la curación de la familia Liquidez (hue violeta
   sobrecargado, anti-solape EQL↔Sweep) — objetivo original heredado de S144, sigue
   abierto. Es lo primero de S149.
2. Poner cuota a BOS/CHoCH (`in_10`), el desbordamiento del hallazgo 1. Va por CONSTANTE,
   NO por input nuevo: un input corre los ids `in_N` ya guardados y eso mordió en S145.
   Fuera del alcance de ADR-027.
3. Si se quiere que el tramo del pool barrido se vea de verdad, hay que revisar la poda de
   `f_prunePools` (ADR-006), no el dibujo.

## Estado en que queda el entorno (para el arranque de S149)
- TV abierto, `SMC_Library` v422 guardado, editor de Pine abierto con el Visual.
- Chart en M5 (se cambió para la tarea 3), ventana visible 2026-07-28 11:00→14:30 UTC. Para
  retomar la curación de Liquidez hay que volver a D1.
- Inputs: solo `in_84` (sweeps/grabs) encendido de la familia Liquidez; `in_78`, `in_81`,
  `in_87`, `in_90`, `in_92` quedaron apagados por el aislamiento de la tarea 3, y todos los
  demás toggles de dibujo también. `in_118` (Densidad) = Todo. `in_85` (max sweeps) = 20,
  restaurado.
- Recordatorio permanente: antes de escribir inputs, mapear `in_N` en vivo (los índices se
  corren; en S145 se corrompieron 6 inputs numéricos por adivinar).
