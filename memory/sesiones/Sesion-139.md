# Sesión 139 — 2026-07-20

## Objetivo con el que arrancó
Revisión visual de la familia OB en EURUSD D1 (todo lo demás apagado). El usuario reportó
ruido: ~23 cajas OB rellenas cruzando todo el gráfico (OBs viejos nunca mitigados,
ZS_ACTIVE, `right=time` en `f_zBox`).

## Rama
`pine/sistema-completo`

## Qué se tocó
CORE intacto: LIBRARY CORE SHA `9559a0d7fe58b213` (1776 líneas), EXTREMES CORE SHA
`5f851d87e5fda720` (148 líneas). check-core-sync OK ×3. Sin tag (no se cerró gate).

## Commits (6)
- `75ee126` docs(adr) — ADR-024 reparto del dibujo Visual/Context — eje heredado vs nativo.
- `df15207` docs(adr) — ADR-024 acotada — mueve maquinaria, no decide la herencia.
- `499b680` docs(adr) — ADR-024 premisa central REFUTADA — el panel también consume la geometría.
- `9d41479` refactor(pine-visual) — S139 retirar andamiaje muerto del §6.5 + invertir el loop de OB.
- `e32d387` refactor(pine-visual) — ADR-024 retirar geometría heredada del Visual (call-site swap).
- `f460e00` feat(pine-visual) — atenuado de OB por ANTIGÜEDAD (dim-to-focus).

## Diagnóstico medido: sobre CAJAS no existe ningún mecanismo
Ni el presupuesto §6.5 (solo cubría labels, y su cobro se eliminó en S125), ni solape, ni
merge. El anti-solape `f_ySlot` solo actúa sobre labels. ⇒ el reparto ADR-024 es
**prerrequisito**, no la siguiente tarea de ruido.

## Error propio 1 — el andamiaje muerto ya costaba cero
Se retiró `budgetLbl`/`FRAME_RESERVE`/`budMtfD1`/`budMtfH1`/`mtfReserve` + el cuerpo de
`f_mtfLblYield` (§6.5). **Medido: NO liberó headroom apreciable.** ⇒ Pine tree-shakea también
las **VARIABLES** top-level sin consumidor, no solo funciones — el matiz "se ejecuta" que se
venía usando aplicaba a funciones, no a variables. La predicción escrita ("financia el resto
del fix") queda **REFUTADA** (6.ª predicción muerta del hilo de tokens). Se retiró de todos
modos por higiene de código.

## Error propio 2 — inversión del loop de OB, efecto nulo
El loop de dibujo de OB se invirtió a nueva→vieja (el anti-solape de S120 reclamaba la
ranura Y desde el OB más antiguo, operando al revés). Coste ~0. Efecto visible nulo: censo
idéntico 23/23, porque en D1 solo-OB el dedup nunca llega a dispararse.

## Gotcha medido — el censo redondea
`data_get_pine_labels`/`data_get_pine_boxes` **redondean a 2 decimales**. Se habían
fabricado colisiones inexistentes (OB@1.25 vs OB⇈@1.25 en ranuras en realidad distintas). El
sufijo de tipo que las separaría de verdad cuesta **≥6 tokens** y no cabía en ese momento.

## ADR-024 — reparto del dibujo Visual/Context
Recorrido PROPUESTA → ACOTADA → REFUTADA en su premisa central: el "corte limpio" (el panel
usa solo 17 escalares) era **FALSO** — 5 filas del panel (OB/FVG/Pool cercano, Último Sweep,
EQ H/L) consumen el buffer de geometría heredada, no los escalares. Lo que sobrevive del ADR:
el eje heredado-vs-nativo, y que la unidad de reparto es el **call-site**.

## Ejecutado igualmente (`e32d387`)
Las 2 `request.security` D1/H1 pasan de `f_computeTFState` (17 escalares + 72 de geometría) a
`f_m5Light` (mismos 17 escalares, espejo de ADR-021). `f_computeTFState` queda sin call-site
⇒ el tree-shaking la retira del Visual.

Se conservan en el archivo **sin llamar** (0 tokens, reconectables con `git revert`):
`f_computeTFState`, `f_drawMTFZones`, `f_bufNear`, `f_bufZoneCell`, `f_bufCountEQ`.

Se retiran temporalmente: el mapa de zonas heredadas + las 5 filas de geometría del panel
(pasan a mostrar "—").

**Verificado en vivo:** panel D1 Discount 34% (idéntico a S134/S138), 23 cajas OB nativas
idénticas. check-core-sync OK.

## Atenuado de OB por ANTIGÜEDAD (`f460e00`)
Los OB viejos se desvanecen gradualmente (relleno y borde más tenues cuanto más viejos), los
recientes quedan sólidos. Discriminador: edad en barras (`bar_index - z.barIdx`), símbolo-
agnóstico (ADR-001). Inputs nuevos: `i_obAgeBars` (default 2000), `i_obAgeDim` (default 40).

Sustituye un intento previo con `f_depthBand==0`, que era el discriminador **equivocado**:
`f_depthBand` mide alcance contra el extremo de pierna, estirado por el swing dominante, así
que casi nada calificaba como lejano.

Calibrado en vivo sobre D1: `age 300` saturaba (todo lavado); `2000` deja los recientes
sólidos. Compiló 21:27:03 sin CE10117 ⇒ confirma que el reparto ADR-024 liberó headroom
suficiente.

## Defectos abiertos (registrados para próxima sesión)
- El atenuado por edad **no se reactiva por relevancia**: un OB viejo que se vuelve el
  próximo objetivo (porque el precio consumió los cercanos) sigue apagado. Falta combinar
  edad con alcance/proximidad.
- El umbral en barras **no es equivalente entre TFs** (2000 en M5 ≈ 1 semana; en D1 ≈ 8
  años). Se revisa junto al degradado por temporalidad, en la fase de herencias.

## Orden acordado para la próxima sesión
1. Terminar las variantes de OB que quedan (Breaker, Mitigation Block, Propulsion, Vacuum,
   comportamiento entre sí).
2. Recién después, en fase de herencias: degradado en TFs bajos + reactivación por relevancia.

## Regla de orden del usuario (vigente)
La herencia se decide **después** de verificar todos los conceptos en su TF propio/nativo.
Un plan puede MOVER la maquinaria de herencia, no FIJAR qué se hereda ni por qué. El solape
que duele es el **anidamiento** (heredar un OB de H1 y que dentro caigan otros OB/FVG +
etiquetas), no el solape por porcentaje entre pares — las etiquetas son la familia que más
ruido hace.

## Estado del hilo de tokens
Ya no es "no hay headroom": el reparto ADR-024 lo libera, y quedó ejecutado y confirmado en
vivo (compilación sin CE10117 tras el swap + el atenuado de OB añadido encima).

## Fase
Sigue FASE 1, F1-GATE ABIERTA.

## Referencias
ADR-024 · [[Sesion-138]].
