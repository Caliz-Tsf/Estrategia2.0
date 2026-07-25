# Sesión 144 — 2026-07-25

## Objetivo con el que arrancó
Cerradas las familias OB+FVG (S143), arrancar la **curación de la familia Liquidez** —
empezando aislando EQH/EQL y pools (regla de método: un concepto encendido, el resto apagado).

## Rama
`pine/sistema-completo`

## Commits (1)
- `074223f` refactor(pine-visual) — S144 retira el DIBUJO de pools barridos (invisible + redundante
  con el marcador de sweep). Elimina input `i_showSwept`; eligibility `not p.swept`; `f_drawPools`
  simplificado a solo-vivo. Los barridos se siguen MARCANDO en el array (los necesita `f_detectSweep`).

check-core-sync OK ×3 (LIBRARY CORE SHA `7ad95b3e612d041a`, 1783 líneas, **sin cambios** vs S143.
EXTREMES CORE SHA `5f851d87e5fda720`). Compila 0/0 (pine_check + TV markers []). TV script v386.
Sin tag (F1-GATE sigue sin firmar).

## Lo que se hizo / hallazgos

**1. EQH/EQL nativo — SANO, y una corrección medida.** Aislado en D1: render limpio (violeta,
línea punteada corta conectando los dos pivotes iguales, sin solape intra-familia). **Corrección:
NO son escasos en D1 — son 62** (censo `data_get_pine_labels`). Mi afirmación inicial de "escasos"
era **falsa**; la causa era que la **auto-escala de TV estaba OFF (bloqueada)** → comprimía las velas
a una banda fina y ocultaba los labels. Al reactivarla (`ui_evaluate` → `setMode({autoScale:true})`)
aparecieron los 62.

**2. Pools — 4 vivos en D1 = CORRECTO por §3.1.** `minTouches=2`: un swing suelto pesa 1 (no
califica), un EQH/EQL pesa 2 (sí). Reconciliación 62 EQH/EQL vs 4 pools vivos: **la mayoría ya
fueron barridos** sobre la historia; solo los NO barridos siguen siendo imanes vivos
(§3.1: *"solo los niveles no barridos son imanes"*). No es sub-detección.

**3. Pools barridos (`i_showSwept`, "historial") — investigado a fondo → Fix 1.** El array los
conserva (`f_markPoolsSwept` marca, no elimina; `f_prunePools` solo poda >80) y por código son
elegibles+objetivo en Estudio → *deberían* dibujar. Pero no se ven: `data_get_pine_lines` solo
reporta niveles **VIVOS** (línea full-width a la barra actual); los barridos son **segmentos cortos**
formación→barrido con **transp 75** → invisibles en la práctica. Y son **redundantes** con el
marcador de sweep (`f_detectSweep`: trampa/Spring/Raid). ⇒ **Fix 1: retirar su DIBUJO** (commit).

**4. DOL — es Ruta B / Sprint 2.1, no se adelanta.** La "escalera de máximos/mínimos sueltos como
objetivos de liquidez" que el usuario esperaba ver = **Draw On Liquidity**. El proyecto ya lo tiene
scopeado como **Ruta B / Sprint 2.1** (moduladores de bias/scoring): `reglas-smc-ict.md:1082` +
`ADR-012:27` (Q2 "draw on liquidity" como dirección). El **pool** (§3.1) es liquidez *agrupada* a
propósito; el DOL (old highs/lows como objetivo direccional) es un módulo aparte. Diseñarlo ahora =
front-runear Sprint 2.1 → NO.

**5. Far/old pivots (BSL 1.51, ~7 años) — SE CONSERVAN.** Decisión del usuario, correcta: un old
high sin barrer **sigue siendo liquidez** (el guardián S106 tenía razón: objetivo de proyección).
**Rechazado capar por edad/distancia** (Fix 2) — borraría objetivos válidos. La compresión de
auto-escala que causa la línea a 1.51 es **cosmética** (cualquier línea a ese precio fuerza la
escala de TV); el fix elegante (**marcador de borde** para objetivos lejanos sin romper escala) es
**diseño de DOL → Sprint 2.1**.

## Diagnósticos (sin código)
- El script `name:"SMC_Library"` tiene `title:"SMC Engine — Visual"` = es el estudio Visual. No
  confundir "SMC_Library" (nombre interno) con la library eliminada en S136.
- Los 2 círculos azules abajo-derecha del chart persisten con TODO apagado → **no son del estudio**
  (objeto nativo de TV / dibujo del usuario en el layout).

## Gotchas de método (S144)
- **Auto-escala de TV puede estar OFF (bloqueada)** → comprime las velas y **OCULTA** labels/pools;
  casi diagnostico "EQH/EQL escaso" por leer una pantalla comprimida. Reset por API:
  `_exposed_chartWidgetCollection.activeChartWidget.value().model().panes()[0].defaultPriceScale().setMode({autoScale:true})`.
  Y **una línea de pool lejana (1.51) fuerza la auto-escala** a incluir ese nivel → comprime todo.
- `data_get_pine_lines` solo reporta niveles **VIVOS full-width**; no cuenta segmentos barridos.
- **`pine_inject.py` (setValue) NO marca dirty en Monaco** ⇒ el "Guardar" queda no-op ("Todos los
  cambios guardados") y la versión NO sube. Para persistir: `ed.trigger('kbd','type',{text:' '})` +
  `ed.trigger('kbd','deleteLeft',null)` (dirty) + **Ctrl+S**. La versión subió 385→386.
- TV Desktop se cayó 2× en la sesión (relanzar con `tv_launch`).

## Siguiente
- **PRÓXIMA SESIÓN — arrancar DOL (Ruta B / Sprint 2.1):** resolver de una vez (a) el **marcador de
  borde** para objetivos de liquidez lejanos (mostrarlos sin romper la auto-escala) y (b) la
  **escalera de draw-on-liquidity** (old highs/lows como objetivos). Requiere ADR-DOL + coordinar con
  IRL/ERL, IPDA, HRLR/LRLR del mismo módulo. Afecta bias/scoring, no solo dibujo.
- **LUEGO — retomar la curación de la familia Liquidez** donde quedó: EQH/EQL (sano ✓) y pools
  (verificados ✓); conceptos que faltan aislar: **sweeps, IDM, Judas, False Breakouts**. Defectos
  cross-concepto pendientes: **hue violeta sobrecargado** (EQ + pools heredados + IDM/Judas/sweeps
  comparten `COL_LIQ`) y **anti-solape EQL↔Sweep** (S123).
- **Deudas diferidas heredadas:** IPR verificación visual, anclaje weekend-safe FVG (CORE),
  W_ZREACT (ADR-025) — todas Fase 3.
