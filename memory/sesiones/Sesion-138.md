# Sesión 138 — 2026-07-20

## Objetivo con el que arrancó
Ejecutar el **experimento 3** que dejó pendiente S137 (`RESPUESTA-FABLE-S135.md` §3, punto 2):
`base_V` por regresión **local** del Visual, en vez de heredar la pendiente de Context
(calibrada 10× fuera de rango y marcada como no firme por Fable).

## Rama
`pine/sistema-completo`

## Qué se tocó
**`pine/` NO se tocó.** CORE intacto: LIBRARY CORE `9559a0d7fe58b213` (1776 líneas),
EXTREMES CORE `5f851d87e5fda720` (148 líneas), check-core-sync OK ×3. Sin tag.

## Commits
- `009d605` docs(cierre) — acta de S137 + ESTADO-ACTUAL, que habían quedado sin commitear.
- `d25ee52` test(ablacion) — la medición y la primera corrección a ADR-022.
- (cierre) docs — el bracket final, la calibración del instrumento y esta acta.

## Mediciones (5 applies, todas frescas y con valores distintos de los conocidos)

| Build | Tokens | Hora |
|---|---|---|
| `Visual + lastre(600)` | 116818 | 00:58:53 |
| `Visual + lastre(400)` | 110869 | 01:01:34 |
| `Visual + fix-slim`, **sin lastre** | **100262** | 01:05:08 |
| `Visual + lastre(400) + fix-slim` | 110896 | 01:16:41 |

Referencias previas usadas: `Visual + lastre(300)` = 107986 (S135) y
`Visual + lastre(300) + fix-slim` = 108031 (S137). Verificado antes de restar que el Visual
no cambió desde `42207ea` (`git log` vacío).

## Hallazgo 1 — la extrapolación del lastre es inválida
El modelo de 3 puntos (300/400/600) da `u`=28.83 tok/unidad, `F`=183 tok/chunk, intercepto
**98971**, y **ajusta exacto sus tres puntos**. Predice `Visual+fix-slim` = 99016.
Medido: **100262**. ⇒ **1246 tokens de error.**

Un ajuste con tantas incógnitas como puntos **no valida nada**: no hay residuo.

## Hallazgo 2 — el conteo tampoco es aditivo
El mismo `fix-slim` mide **45** sobre `lastre(300)` y **27** sobre `lastre(400)`.
⇒ las restas con lastre igual —la operación que dábamos por limpia— arrastran **~18 tokens**
de dependencia del contexto. Predicción escrita antes (110914, Δ=45): **FALSA**.

## Hallazgo 3 — el 100262 de S135 NO era fantasma
Se reprodujo **exacto** en sesión, build y timestamp distintos. La hipótesis de contaminación
(que llegué a dar por buena durante un rato en esta misma sesión) queda descartada para ese
número.

## CIERRE — bracket sin modelo
```
Visual(HEAD) aplica             ⇒ base_V ≤ 100256
Visual + fix-slim = 100262      ⇒ base_V = 100262 − coste(fix)
coste(fix) ∈ [27, 45] medido    ⇒ base_V ∈ [100217, 100235]
                                ⇒ headroom ∈ [21, 39] tokens
```
**El headroom del Visual es de DOS CIFRAS.** El `39` de S137 es el extremo superior del
bracket, no un error: su conclusión práctica era correcta; lo que se corrige es haberlo
presentado como valor exacto medido.

**Deuda de `pdMid`: sigue abierta, sigue sin caber por 6 tokens.** Vencimiento sin cambios
(antes de los golden tests de Fase 4). Hace falta liberar **≥6 tokens de código que se EJECUTA**.

## Instrumento calibrado
Intercepto **±1246** · restas **±18** ⇒ **el lastre sirve para señales >100 tokens; por debajo
de eso, y para cualquier valor absoluto, no.** Escrito en `docs/reglas-dev.md` §1.6c.

| Hallazgo | Señal vs ruido | ¿Sobrevive? |
|---|---|---|
| Código muerto = 0 tokens (S135) | 0 vs 700 predichos | ✅ |
| Par histórico ADR-022 (S137) | ΔT=142 vs 830 | ✅ |
| `headroom = 39` (S137) | 39, ruido ±18 | ⚠️ pasa a `[21,39]` |
| Extrapolación `base_V` (S138) | 1285, ruido ±1246 | ❌ refutada |

## Context NO queda invalidado — y esto ahorra una sesión
`Context ≈ 85.000 libres` (S135) es una extrapolación del mismo tipo, pero el error del
intercepto (~1,2k) es el **1,5%** de 85.000. La extrapolación es fatal para distinguir
"39 vs 1285" —error del orden de la respuesta— e irrelevante aquí. Se mantiene como
**~83.000 ± 3.000**, suficiente para sostener el plan del **reparto del dibujo**, y se
confirmará solo al ejecutarlo (el compilador dice sí o no). **No hace falta sesión de
medición extra para Context.**

## Error de método propio, atrapado en la misma sesión
Tras el punto 600 concluí `headroom ≈ 1285` y presenté 98971 (mío) y 99160 (retro-cuenta
S135) como **"vías independientes que coinciden"**. Son la **misma extrapolación dos veces**:
coinciden porque comparten el defecto. El experimento 4 lo refutó reproduciendo el 100262.
**NORMA:** dos derivaciones que parten del mismo modelo **no se confirman entre sí**.
El veredicto falso se conserva **tachado, no borrado**, en el documento de medición.

## Gotchas de método
- Sondeé la consola varias veces **antes** de que terminara la compilación y leí "colgado"
  donde solo había un compilado en curso (~70-90s). Contrastar siempre con el reloj de TV.
- El botón `[title="Actualizar en el gráfico"]` **desaparece del DOM mientras compila** —
  un `NO ENCONTRADO` no significa que no exista.
- El PLAY se queda a veces solo en `"guardado"` (compilado de ~6s = no compiló de verdad);
  hay que repetirlo.
- Verificar la presencia del fix **contra el blob con `grep -c`**, no con `indexOf` en Monaco
  (gotcha S137, respetado).

## Estado del entorno al cierre
Visual restaurado a HEAD y **verificado en pantalla**: dibujo completo, panel de 4 columnas
(D1 Discount 34% · H1 Discount 33% · M5 Premium 56%), sin error rojo, 2 slots
(Context + Visual). Chart en 1D ⇒ por ADR-023 solo la columna D1 es de lectura válida.

## BLOQUE FINAL — la deuda de `pdMid` SE CIERRA (commit `28136e6`)

Tras el cierre del hilo de tokens, el usuario preguntó qué hacer con `pdMid`. Trazando el
código apareció una vía que nadie había mirado: **financiar el fix retirando una rama
inalcanzable del mismo concepto.**

`pine/SMC-Visual.pine:4467`, dentro de `f_drawMTFState`:
```pine
float mid = na(s.pdMid) ? (s.pdHigh + s.pdLow) / 2.0 : s.pdMid   →   float mid = s.pdMid
```
**Es inalcanzable, verificado por trazado completo:** `f_drawMTFState` solo se llama con
`d1State`/`h1State` (`:4578`/`:4581`), **nunca con `chartState`**; ambos vienen de
`f_computeTFState`, cuyo `:1748` pone `pdMid = na` **solo si** `pdHigh` o `pdLow` son `na`;
y el `if` que envuelve la línea ya exige que ambos sean no-`na` ⇒ `na(s.pdMid)` siempre falso.

Es **exactamente** el *"código que se EJECUTA"* que hacía falta liberar.

**Cambio (2 líneas, ambas fuera del CORE 151..~1927 ⇒ SHA intacto):**
- `:2199` `chartState.pdMid := (chartState.pdHigh + chartState.pdLow) / 2.0` (sin guard — la
  aritmética de Pine ya propaga `na`)
- `:4467` la rama muerta fuera

**MEDIDO CON APPLY REAL:** `1:44:57` compilado **sin CE10117** ⇒ entra bajo el techo;
`1:49:27` `"Compilado." + "Añadido al gráfico."`. **P1 (pre-registrada) VERDE: el swap se
autofinancia.**

**VERIFICADO EN VIVO (chart M5, ADR-023):** **P3 VERDE** — `data_get_pine_lines` devuelve
**1.51 / 1.23 / 0.95**, el P/D de D1 documentado en S134 (Premium 1.51441 · **EQ 1.23400** ·
Discount 0.95360). **El 1.23 ES la línea `mid`**: si el cambio la hubiera roto sería `na` y
no existiría. Panel de 3 columnas coherente con la matriz de S134 leído desde M5
(D1 Discount 34% · H1 Premium 72% · M5 Premium 74%). Sin error rojo, 2 slots.

**Efecto funcional a corto plazo: nulo** (S135 midió 0 de 1235 rejections alteradas). El
valor es de **doctrina y paridad**: evita llegar a los golden tests de Fase 4 con `pdMid=na`
y construir el EA *bug-compatible*. **El vencimiento que fijó Fable queda CUMPLIDO.**

⚠️ **Nota de método:** no incluí un marcador nuevo por build en el swap, y durante un rato
no pude distinguir qué build estaba vivo en el chart (el dibujo es idéntico por diseño).
Se resolvió quitando el estudio y re-añadiéndolo para forzar un `"Añadido al gráfico"`
inequívoco. **La regla del marcador aplica también cuando el cambio es invisible — sobre
todo entonces.**

## Siguiente
- **El hilo del presupuesto de tokens queda CERRADO.** No quedan mediciones pendientes en él.
- **La deuda de `pdMid` queda CERRADA** (`28136e6`).
- (1) Matriz concepto × TF × {nativo, heredado} — es lo que bloquea la F1-GATE.
- (2) ADR del reparto del dibujo (eje TF/rol; nombrar sin disfraz la restricción de 2 slots
  del plan gratuito).
- (3) `pdMid` dentro, con su vencimiento duro.
- (4) Pendientes F1-GATE heredadas.
- **NO reabrir:** medir `base_V` con más precisión (el bracket `[21,39]` es suficiente para
  toda decisión pendiente) ni re-medir Context por extrapolación.

## Referencias
`docs/planes/MEDICION-base-v-local-S138.md` · `docs/reglas-dev.md` §1.6c · ADR-022
(CORRECCIÓN S138) · `docs/planes/RESPUESTA-FABLE-S135.md` §3 · [[Sesion-137]].
