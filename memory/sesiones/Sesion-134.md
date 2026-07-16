# Sesión 134 — 2026-07-16

## Objetivo con el que arrancó
Calibrar `pdWindow` por TF (plan heredado de S133). **No se calibró nada: la medición cambió el problema.**

## Rama
`pine/sistema-completo`

## Commits (2)
- `133eeff` fix(pine-visual): F1-S134 el dibujo del P/D pintaba el trailing range, no el dealing range del ADR-021. Toca `pine/SMC-Visual.pine` (solo el bloque de dibujo, :3516) y crea `docs/planes/MEDICION-matriz-chart-tf-S134.md`.
- `b43d3f5` docs(doctrina): F1-S134 §2.3.2 — el defecto del chart-TF también hita H1, no solo M5. Toca `docs/reglas-smc-ict.md`.

## Estado técnico
CORE intacto. SHA `9559a0d7fe58b213` (1776 líneas). EXTREMES CORE `5f851d87e5fda720` (148 líneas). pine_check 0/0. check-core-sync OK ×3 + EXTREMES CORE OK. Sin ADR (fix Visual-only, fuera del CORE que termina en L1850). Sin tag. F1-GATE sigue bloqueada.

## Hallazgo 0 — el diagnóstico era humo
La sesión empezó leyendo docs y código sin medir, y concluyó (erróneamente) que el defecto del M5 estaba en el acumulador de `f_pdRelatch` y que `pdWindow` no cabía en el UDT. El estudio estaba caído en rojo en TradingView y nadie lo había mirado: se iba a calibrar contra un indicador muerto. Lo destapó el usuario ("no está renderizando, está con un error rojo"). El error no era del repo: el slot de TV tenía un build roto. Inyectado el Visual del repo: pine_check 0/0, consola "Compilando... / Compilado. / Añadido al gráfico.", panel vivo.

**Norma nueva:** ninguna conclusión sobre el comportamiento en vivo se emite sin haber mirado la pantalla; `study_count=0` no significa "renderizando", puede ser un estudio en error → screenshot antes de esperar.

## Hallazgo 1 — la matriz de 9 celdas
Medida en vivo, OANDA:EURUSD, instancia limpia sin overrides, precio ~1.1467. Veredicto P/D por columna × chart-TF:

- Columna D1: chart D1 = Discount 34% | chart H1 = Discount 34% | chart M5 = Discount 34%
- Columna H1: chart D1 = Discount 34% (truncada) | chart H1 = Premium 74% | chart M5 = Premium 74%
- Columna M5: chart D1 = Premium 58% (truncada) | chart H1 = Discount 21% (truncada) | chart M5 = Premium 91%

Regla: una columna se lee correcta SII chart-TF <= TF de la columna.

**El sistema funciona:** desde chart M5 las tres dan 34/74/91 = la tabla del gate de §2.3.2 (D1 0.344 · H1 0.733 · M5 0.929) celda por celda. La cascada anida y rota con cero parámetros. Lo que S133 entregó estaba bien; se leyó desde un chart H1, donde D1 y H1 son válidos.

**Correcciones:**
- §2.3.2 decía que el defecto es solo del M5 — falso, el H1 también falla (34% desde chart D1).
- La hipótesis con la que arrancó S134 ("solo M5 sufre, D1/H1 a salvo") era mitad falsa: D1 sí es estable, H1 no.

**Consecuencia:** "calibrar pdWindow" deja de ser obviamente la respuesta. Aparece opción de coste cero no considerada: declarar que el panel es válido leído desde el TF más bajo (regla de operación, no código), frente a la ventana real (array de strong con barIdx en el CORE ⇒ rompe SHA + riesgo OOM de S105 + tokens contra el CE10117). Decisión abierta, no se implementó nada.

## Hallazgo 2 — bug encontrado y arreglado (el principal)
El bloque de dibujo del P/D (`pine/SMC-Visual.pine:3516`) leía `trailing.top`/`trailing.bottom` (la Opción A que el ADR-021 sustituyó) y nunca miraba `chartState.pdHigh`/`pdLow` ⇒ el panel mostraba un rango y las líneas otro.

Medido en chart D1 antes del fix: dibujaba Premium 1.60389 (correcto 1.51441, ~900 pips de error), EQ 1.25332 (correcto 1.23400), Discount 0.90275 (correcto 0.95360, ~508 pips). `[0.90275, 1.60389]` es el trailing range (min/max de toda la historia D1, el mismo que S129 midió como "Opción C literal"). El ADR-021 cambió el motor y el panel y se olvidó del dibujo; el comentario de encima aún describía el diseño viejo.

**Por qué sobrevivió a S133:** en pct casi no se nota (35% dibujado vs 34% del panel) ⇒ dos rangos distintos dan casi el mismo pct ⇒ el pct es un discriminador pésimo, solo los niveles delatan. El gate de S133 se pasó con un probe truncado antes del bloque de dibujo y el panel (correcto) tapaba el resto. Además es invisible en M5 (ahí trailing ≈ pd range: dibujaba 1.14824/1.13246 = pct 0.906 ≈ el 91% del panel) ⇒ hay que probar en D1. La tarea pendiente "nadie ha visto los 3 P/D dibujados" era el único test capaz de atraparlo, y no era cosmética.

**Fix:** `:3516` pasa a dibujar `chartState.pdHigh`/`pdLow`. Ancla `chart.left_visible_bar_time` (neutra) porque `SMC_PdRange` no guarda el tiempo del extremo y el UDT vive EN el CORE (:1176) ⇒ añadírselo rompería el SHA. Deuda anotada: ancla real al 2.º extremo si algún día se re-baselinea.

**Verificado en vivo** con predicción escrita antes: Premium 1.51441 (predicho 1.51441) ✅; Discount 0.95360 (predicho 0.95360) ✅; EQ 1.23400 (predicho 1.23401, diferencia por redondeo mintick de 1.234005); panel D1 Discount 34% sin moverse ✅.

## Hallazgo 3 — bug abierto, no tocado
`chartState.pdMid` se lee en `:2741`/`:2742` (f_wickNearLevel, Rejection §2.7) pero nunca se asigna — el bloque chart-TF (:2193-2198) solo pone pdHigh/pdLow ⇒ queda en su default `na` (:296) ⇒ el nivel EQ nunca participa en la confluencia de mecha de rechazo. Fallo silencioso. `f_computeTFState` (:1748) y `f_m5Light` (:2873) sí lo asignan; `:4464` ya se defiende del `na` con un fallback, `:2741` no. No lo introdujo el ADR-021: `git log -S "chartState.pdMid"` devuelve un solo commit, `5bc4828` (T20 Rejection), el que añadió las lecturas ⇒ la asignación nunca existió ⇒ muerto desde el Sprint 1.5. Concepto distinto ⇒ commit distinto (regla dura #7).

## Gotchas nuevos de método
- `scripts/pine_inject.py` no aplica, solo guarda: su clic busca botones en INGLÉS (`Add to chart`/`Update on chart`) y el TV del usuario está en ESPAÑOL ⇒ cae siempre al fallback y devuelve `CLICK: Pine Save`, señal de que no aterrizó.
- Receta de apply que sí funcionó: `chart_manage_indicator` remove con entity_id (de chart_get_state) ⇒ 0 estudios; `python scripts\pine_inject.py pine\SMC-Visual.pine`; clic en el botón PLAY junto al nombre del script en el editor (~x=1790,y=79); confirmar en `pine_get_console` que dice "Compilando... / Compilado. / Añadido al gráfico." — si solo dice "guardado", no aplicó (pasó una vez y hubo que repetir el clic); esperar 60-75s.
- El error de runtime se lee del atributo `title` del icono del legend ("Error de ejecución · Abierto en el Editor de Pine"), no de `pine_get_console`.
- `data_get_pine_labels` truncó a 50 de 498 labels (`total_labels`=498, cerca del tope de 500) ⇒ no sirve para censar; se leyó por screenshot.
- PowerShell no soporta heredocs ⇒ los mensajes de commit largos van a archivo y `git commit -F`.

## Pendiente / siguiente (S135)
1. Decidir el remedio del chart-TF: regla de operación de coste cero ("el panel vale leído desde el TF más bajo") vs ventana real con array de strong en el CORE (SHA + OOM S105 + CE10117). Bloquea la F1-GATE.
2. Arreglar `chartState.pdMid` (Hallazgo 3), fix de una línea fuera del CORE.
3. Resolver la contradicción viva de §2.3.2: el aviso dice `pdWindow` "obligatoria" y la tabla de parámetros dice "desactivada · OPCIONAL". Es decisión de diseño, no un hecho medible; quedó anotada sin resolver.
4. No repetir las 11 hipótesis ya refutadas con medición (ancla S128, cascada de mitades y mapeo nivel→TF S130, toques y poolTol S131, amplitud S132, escala ×4, expansión, origen-de-última-pierna, 3-ventanas-sobre-D1 S133).
5. Pendientes de antes: fallback M2, IFVG por banda/lado, gate MB/BPR, `elig` excluye ZS_MITIGATED, `LEG_ANCH_TOL_ATR`, deudas S123, herencia MTF.

## Referencias
`docs/planes/MEDICION-matriz-chart-tf-S134.md` · ADR-021 · ADR-022 · Sesion-133.
