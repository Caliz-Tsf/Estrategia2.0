# Sesión 146 — Ciclo de vida de pools resuelto + §3.3 Grab implementado (F1-S1.3-T10b)

- **Fecha:** 2026-07-28
- **Rama:** `pine/sistema-completo`
- **CORE:** 1783 → **1809 líneas** — SHA `7ad95b3e612d041a` → **`5e21ca38b43cf0e4`**. `check-core-sync` OK ×3 en cada commit.
- **TV:** `SMC_Library` v419 (Visual) · `SMC_Context` v22. Compila 0/0 los tres.

## Objetivo

Heredado de S145: el hilo prioritario *"el indicador NO regenera SSL/BSL al avanzar la tendencia"*.

## Resultado 1 — el hilo prioritario queda RESUELTO, y no como se sospechaba

Probe nuevo `scripts/gen_probe_ciclo_pools.py` sobre D1 EURUSD, 6.292 velas confirmadas, cross-checks a 0:

| medida | valor |
|---|---|
| Altas de pool | **704** (362 BSL / 342 SSL) |
| Barridos | 666 · vida media **148 velas** |
| Barridos en ≤ `swingLen` (5 velas) | **9 de 666 = 1,4 %** |
| Censo final | 80 pools (= `MAX_POOLS_CHART`) · 38 vivos / 42 barridos |
| Vivos con 1 toque | **37** |
| Vivos con ≥2 toques | **1** (BSL 1.51421 ·3) |
| SSL vivos bajo el precio | **12**, el más cercano 1.13246 con 24 velas de edad |

Las dos sospechas de S145 quedan **refutadas con medición**: ni "no crea pools" (crea 704) ni "nacen y mueren barridos en la misma pierna" (1,4 %). La causa del "1 solo pool visible" es el **gate de dibujo `p.touches >= i_minTouches`**.

Predicciones escritas ANTES de medir: **4 vivas de 5**. Muerta la P3 (predije >50 % de barras sin SSL dibujable; medido 11 % abajo y 25 % arriba).

## Resultado 2 — el gate NO se toca: es definitorio, no cosmético

Propuse quitar el gate del dibujo. **El usuario me corrigió y tenía razón**: §3.1 define `touches = nº de extremos que lo confirman (≥2)`. Un swing suelto **no es un pool**. Al nivel de 1 toque le corresponde **otro concepto**: §3.3 **Grab**, con menos peso.

Matiz que conviene registrar: desde S145/ADR-026 D2 la fuerza (`f_poolStrength`) ya no decide **qué** pool se dibuja sino **cómo** (ADR-014); **quién** lo decide es la geometría (más cercano por lado + anclas).

## Resultado 3 — F1-S1.3-T10b: §3.3 Grab implementado y validado (96/100)

`KIND_GRAB = 24` llevaba **declarado y sin usar** en los 3 archivos desde el inicio del proyecto. `PINE-PLAN:278` daba *"Sweeps + Grabs"* por cerrado en S030, pero el commit `45c4b40` y `validaciones.md:20` solo acreditan §3.1/§3.2. S057 lo había visto y lo dejó como *"follow-up no bloqueante: §3.3 Grab no es función nombrada separada (implícito en IDM/sweep)"*.

S146 mide que ese "implícito" **no se sostiene**: `f_detectSweep` exige `touches >= minTouches` (excluye el swing aislado por construcción) e IDM usa `structInternal` (liquidez interna, no swings aislados del chart) ⇒ la confluencia **#11 no tenía ninguna fuente**.

**No es concepto nuevo**: entró en la doctrina el 2026-06-10 (commit `429de10`, DOC-01 §3 Liquidez), **antes** del gate VER-09 (tag `ver-09-aprobado`, 2026-06-11), verificado con `git merge-base --is-ancestor`. Es la **#11** de las 42 canónicas (WORKPLAN §4.8). Le faltaba la Fase 1, no la Fase 0.

`f_detectGrab` es PURA, vive en el CORE byte-idéntico ×3. Partición **excluyente** con `f_detectSweep` por `touches`. NO alimenta `lastSweepBar` ni `sweptRecently` (son el gate del Mitigation Block §2.8 y del peso de evento; colar ahí el grab lo ascendería de categoría). Dibujo `"· Grab"` transp 85 vs `"✗ Sweep"` transp 70 (§6.3.12: sweep primario, grab secundario), compartiendo toggle `i_showSweeps` para no correr los ids `in_N`.

## Resultado 4 — ADR-027 PROPUESTO (acordado, NO implementado)

`docs/adrs/ADR-027-tramo-vela-a-vela-familia-liquidez.md`. Tramo punteado vela→vela con la etiqueta al medio, en **cuatro** conceptos: Grab, Sweep/Raid/Spring, y **pool BSL/SSL barrido**. **Judas y False breakout se quedan con etiqueta en la vela** — no tienen fin único (Judas se confirma hasta 6 velas después; FB hasta 2). Etiqueta **hacia afuera del precio**: BSL encima, SSL debajo. Reabre a propósito lo que S144 retiró, con la diferencia explícita de que ahora el tramo va al origen real y lleva nombre.

---

## Gotchas de método (caros, van al registro)

1. **`pine_inject.py` escribe en `getEditors()[0]`, que puede ser el editor OCULTO.** Reconfirmado en vivo: con dos scripts abiertos, `[0]` = plantilla oculta, `[1]` = Visual visible. Es lo que en S145 sobrescribió el Visual con el Context dos veces. Antídoto escrito: `scripts/pine_inject_v2.py` — elige por `getDomNode().offsetParent`, escribe con `executeEdits` (marca dirty; `setValue` NO ⇒ Ctrl+S no-op) e imprime huella antes/después.
2. **Cero dibujos ≠ build rancio.** El grab dibujaba 0 y diagnostiqué build rancio; **el usuario dijo que mirara los toggles** y era eso: `in_84` (`i_showSweeps`) llevaba en `false` desde el aislamiento de familia de S145, y el bloque de grabs cuelga del mismo toggle. Discriminador barato: si el concepto **hermano** tampoco dibuja, es el toggle. Se lee cruzando el metainfo (array `{id,name}`) con el estado vivo (objeto `{in_N: valor}`) de `getStudyTemplateSnapshot()`.
3. **El Pine Editor no está en la barra inferior** sino en el botón lateral derecho `pine-dialog-button`; `ui_open_panel("pine-editor")` devuelve éxito pero no abre nada.
4. **El histórico M5 de OANDA solo alcanza ~2 semanas.** Los 3 casos canónicos de §3.3 son de 2026-06-10/11 ⇒ **no reproducibles**.

## Hilos abiertos para S147

1. **Medir el coste en objetos del tramo** (ADR-027 §4) sobre UN concepto antes de extenderlo. Tope duro de Pine: 500 labels y 500 lines; el Visual ya roza el de labels.
2. **Implementar ADR-027 por subconjuntos, verificando cada uno**: grab → sweep/raid/spring → pool barrido.
3. **Verificar §3.3 Grab en H1 y M5 con casos nativos de cada TF**, fechados. Pendiente porque los canónicos ya no están en el dato.
4. **Curación de la familia Liquidez** — el objetivo original heredado de S144, aún sin retomar.
5. **El set de pools está al tope** (80/80, con 42 barridos ocupando slot sin dibujar nada desde S144). `f_prunePoolsV` desaloja barridos primero, así que no tira imanes vivos. Anotado, sin medir el daño.
6. **Estado del chart al cerrar:** M5 con ventana de las últimas 7 h e `in_84` ENCENDIDO. Si se retoma el DOL hay que volver al aislamiento de S145 (apagarlo) y a D1.

## Commits (2)

- `bcf398c` `tools(pine): S146 — probe del ciclo de vida de pools + inyector que elige el editor VISIBLE`
- `2e80717` `feat(pine-core): F1-S1.3-T10b — f_detectGrab (§3.3 liquidity grab, confluencia #11)`
