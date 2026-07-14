# Sesion-125 — 2026-07-14 — Opción 1 (cap top-N por tipo en swings): medida, implementada y validada

## Objetivo sesión
Ejecutar el plan B que el usuario designó en S124: **Opción 1, cap top-N por tipo en swings**, que S124
estimaba en "~2 tokens". Norma del proyecto desde S114: medir antes de escribir.

## Resultado
**Opción 1 IMPLEMENTADA, medida y validada en vivo.** El "~2 tokens" era **fantasía: costaba ~345**, y los
financia la **remoción de la §6.5** (token muerto, S123 H4). F1-GATE sigue BLOQUEADA. **Dos hallazgos nuevos
para S126** (leyendo el código de la estructura): el recorte de estructura ya existe y solo está apagado en
Estudio/"Todo"; y **`f_depthBand` es ciega al lado**.

## Completado

### Opción 1 — cap top-N por tipo en swings (commit `c94c7d6`, Visual-only)
**El problema:** el etiquetado se filtraba por **umbral de amplitud** (`sw.strength >= i_swingDomAtr`). Los
HH/LL son extremos de impulso (mucha amplitud) y los HL/LH son pullbacks (poca) → el umbral filtraba
**asimétricamente**: censo D1 "Todo" **HH 31 / LL 19 / HL 11 / LH 4**, que rompe la alternancia H-L-H-L que
era justo el objetivo del rediseño leg-based de S117.

**El fix:** el criterio pasa a ser **RANGO, no amplitud** — los últimos `i_swingTopN` de **cada tipo**.
- Input nuevo `i_swingTopN` (int, default 12, min 1 / max 60, `GRP_STRUCT`), declarado **al final del bloque
  de inputs** a propósito: añadirlo arriba correría todos los `in_N` ([[tv-input-ids-se-corren]]).
- En el bloque de dibujo (`if i_showSwings and barstate.islast`, ~L4683): **primera pasada HACIA ATRÁS**
  (`for i = nMj - 1 to 0` sobre `SMC_majorSwingsV`) que solo calcula el **índice de corte por tipo**
  (`swCnt`/`swCut`, `array<int>` de 4; índice = `sw.kind - KIND_HH`, con KIND_HH..KIND_LL = 40..43
  contiguos). El **dibujo sigue yendo HACIA ADELANTE** para conservar el orden de creación: los más
  recientes se crean al final → sobreviven al desalojo de Pine.
- `i_swingDomAtr` **ya NO decide QUIÉN se dibuja**, solo la **INTENSIDAD** del tag dentro de
  `f_pushSwingLabel` (~L4668): transparencia **45 (fuerte) / 75 (tenue)**. Se corrigió su label, que mentía
  ("solo se etiquetan pivotes >= este umbral" → "pivotes >= este umbral se pintan fuertes").
- `SMC_majorSwingsV` (retención FIFO `i_swingMaxKeep`) **INTACTO**: solo se recorta lo que se DIBUJA.

**Validación viva (OANDA:EURUSD D1, modo "Todo"):**
| Tipo | PRE | POST |
|---|---|---|
| HH | 31 | **12** |
| HL | 11 | **12** |
| LH | 4 | **12** |
| LL | 19 | **12** |

12/12/12/12 exacto (= `i_swingTopN`) y alternancia H-L-H-L restaurada. Apply sin CE10117.

### MEDICIÓN (ablación en vivo; arnés `scripts/gen_probe_swingtopn.py`, commit `de00b6e`)
Protocolo S124: inyectar → apply → esperar → leer tokens. Tope **100256**.

| Variante | Tokens | Veredicto |
|---|---|---|
| A — top-N por **FUERZA** (helper nuevo `f_swThr`, 6 sentencias + `array.sort`) | 100615 | ❌ +359 |
| B — últimos-N por tipo (bucle inline, **sin** función nueva) | 100601 | ❌ +345 |
| B + remoción §6.5 | **no visible** | ✅ compila, aplica y dibuja |

> El número de la 3ª fila **no se puede medir**: Pine solo reporta el conteo **por encima** del techo
> (gotcha S121). Lo único que se sabe es que cabe.

**HALLAZGO PRINCIPAL: A y B distan solo 14 tokens**, pese a que A mete una función nueva de 6 sentencias
con `array.sort` y B no mete ninguna. → **Lo caro es TOCAR el bloque, no la FORMA del código.** Esto
**DEBILITA** (no confirma) la sospecha viva de S124 *"Pine trata distinto las funciones de una sola
expresión"* → **deuda S124 #4 se cierra como DEBILITADA**. Van **3 predicciones de tokens muertas de 3**
(S124 ×2, S125 ×1: se predijo por escrito que B cabría y A no; cabían las dos igual de mal).

### La §6.5 confirmada como financiación
Predicho en S124 §7.1-1, ahora **medido**: quitar `f_capLbls`/`f_capLblsOnly` (~L3442) + `eventCap`/
`gEvtLbl`/`gEvtCut` (~L3468) + el bloque de desalojo (~L4537) libera **≥345 tokens** (de +345 sobre el techo
a compilar y dibujar).

**VERIFICADO SIN REGRESIÓN** — era exactamente lo que la tarea S125 #5 exigía comprobar antes de commitear:
- `total_labels` **501 → 502** (ruido)
- fila "Ocultos" del panel T14 **idéntica** (`Est 0 · EQ 0 · Liq 0 · Ref 0`)

Coherente con **S123 Hallazgo 4**: no recortaba nada porque no podía (borraba DESPUÉS de crear, cuando Pine
ya había desalojado en el propio `label.new`). **⚠️ Esa financiación YA ESTÁ GASTADA**: los ~194 de `f_zLbl`
hay que buscarlos en otro lado.

### Lo que la Opción 1 NO arregla
`total_labels` sigue en **502 ≥ 500** → la estructura histórica se sigue desalojando. La Opción 1 arregla la
**LEGIBILIDAD** del esqueleto, no el presupuesto. **Confirma el juicio de S124: mientras la estructura ocupe
~404/500, lo demás es cosmética.**

## Hallazgos nuevos (lectura de código, entrada de S126)

### Hallazgo 1 — el recorte de estructura YA EXISTE; en Estudio/"Todo" está APAGADO
`f_drawStructure` (L3734) crea la label en el acto en cada vela histórica donde dispara un BOS/CHoCH (~342
labels = las más viejas del buffer). **Pero ya hay un recorte en L3779** que corre `if barstate.islast`, y
está **antes** de que dibujen las demás familias (~L4200-4700) → borrar ahí **sí libera slots que
sobreviven**. Por eso Operación funciona (`f_keepBestPerBand` con `STRUCT_OP_CAP=3`).

El problema: ese recorte **solo corre en Operación**. En Estudio/"Todo" el código dice literalmente
`hidStruct := 0` = "traza completa" y **no recorta** → las 342 se quedan, las otras familias empujan el
total a ~842, y Pine desaloja las 342 más viejas = la estructura entera.

→ **CORRIGE la tarea S124 #2**, que asumía que hacía falta repintar en islast desde arrays o cap
at-creation en el histórico: **no hace falta ninguna de las dos.** Los arrays, el punto de corte y la
función de política ya existen. **Cuánto cuesta en tokens: sin medir.**

### Hallazgo 2 — `f_depthBand` es CIEGA AL LADO ⚠️
`f_depthBand` (L3112-3128) codifica **DISTANCIA, no LADO**. El código real:
```pine
if level >= px and hi > px
    float r = (level - px) / (hi - px)
    band := r <= 0.33 ? 1 : r <= 0.66 ? 2 : r <= 1.0 ? 3 : 0
else if level < px and px > lo
    float r = (px - level) / (px - lo)
    band := r <= 0.33 ? 1 : r <= 0.66 ? 2 : r <= 1.0 ? 3 : 0
```
**Las dos ramas devuelven 1/2/3** → banda 2 arriba **==** banda 2 abajo.

Consecuencia: `f_keepBestPerBand` (L3683) conserva **1 representante por banda** → **arriba y abajo compiten
por el mismo slot** y un lado puede desaparecer entero. **Subir el cap NO lo arregla: es política, no
número.** Incumple el **"MÍNIMO doctrinal 3 por lado"** escrito en el propio código (L3048, comentario de
`i_profundidad`).

> **NO OBSERVADO EN PANTALLA TODAVÍA.** Esto es una lectura de código, no una medición. El usuario decidió
> **verificarlo VISUALMENTE en S126 antes de tocar nada**.

## Requisito del usuario (textual, S125)
Quiere ver BOS/CHoCH —y *"todos los conceptos, familias y variantes"*, **los más importantes**— **hasta el
INICIO DE LA PIERNA del swing**. En Operación *"no sé si será exactamente solo uno"*, porque quiere ver
**hacia atrás por la banda de ARRIBA y la de ABAJO** para poder hacer **proyecciones tanto hacia arriba como
hacia abajo, pero limpio**.

→ Exige política **N por (BANDA × LADO)**: la misma forma que la Opción 1 aplicó a los swings (top-N por
tipo) y que ya usa el band-pick de zonas (S106 Paso D, `bp3`).

⚠️ **El alcance "hasta el inicio de la pierna" NO lo fija esa política, lo fija `i_kLeg` = 3.0** (L3055): el
extremo se recorta a `px ± K×rango vigente`. Si el inicio real de la pierna cae más allá, no se ve por más
que se arregle el reparto. **Knob a calibrar en pantalla con el usuario.**

## Decisiones del usuario al cierre
1. El hallazgo de bandas ciegas al lado se **verificará VISUALMENTE en S126** antes de tocar nada.
2. Confirma que hay que **auditar familia por familia** cuáles tienen política ciega al lado: es la
   **matriz de auditoría F1 abierta desde S115**, que era exactamente lo que se estaba haciendo cuando
   aparecieron estos errores.

## GOTCHAS S125
1. **Render lag 60-120s tras `Pine Save`.** El Save SÍ recompila la instancia aplicada, pero mientras
   renderiza **el chart muestra el dibujo VIEJO** → un censo leído temprano da los números de antes (aquí
   HH=31, idéntico al pre-cambio) y parece "no aplicó" cuando en realidad **el estudio estaba MUERTO por
   CE10117**. El badge rojo `(!)` junto al nombre del estudio es la señal fiable.
2. **La fuente del número de tokens es `pine_get_console`** (trae el histórico con timestamps), NO
   `pine_get_errors` (marcadores de Monaco = 0 aunque el estudio esté muerto). Reconfirma el falso-0
   S107/S124. Y el conteo **solo es visible por encima del techo** (S121) → la ablación es binaria
   (cabe / no cabe) salvo cuando falla.
3. **Los comentarios NO cuentan para el techo** (se compilan fuera); los **strings de tooltip/label de los
   inputs SÍ**.
4. **`git commit -m @'...'@` (heredoc de PowerShell) NO funciona en la herramienta Bash** → el `@` acabó de
   subject. Usar `git commit -F -` con heredoc POSIX.

## Commits S125
- `de00b6e` chore(scripts): arnés de ablación `gen_probe_swingtopn.py` (flags: default = variante A por
  fuerza, `recency` = variante B, `sin65` = + remoción §6.5, `solo65`; el `.pine` sale a `%TEMP%`, fuera del
  repo — gotcha S124 #2)
- `c94c7d6` feat(pine-visual): cap top-N por tipo en swings + remoción de la §6.5
- `20e0387` docs(planes): la Opción 1 medida — el "~2 tokens" era fantasía (añade §8 a
  `docs/planes/DISEÑO-presupuesto-labels-S124.md`)

## CORE
- **SHA `752b4083a7db419d`** (1866 líneas) — **INTACTO** (todo el cambio es Visual-only)
- core-sync OK ×3
- pine_check 0/0
- apply en vivo D1 OANDA:EURUSD sin CE10117

## Estado
- **F1-GATE BLOQUEADA**
- SIN ADR nuevo (Visual-only bajo ADR-016/ADR-019)
- SIN tag
- Rama `pine/sistema-completo`
- Working tree limpio

## Tareas S126 (ordenadas por prioridad)
1. **Verificar VISUALMENTE el hallazgo de bandas ciegas al lado** (arriba vs abajo) — decisión del usuario:
   antes de cambiar la política.
2. **Política N por (banda × lado)** para la estructura + **auditar qué otras familias son ciegas al lado**
   (matriz de auditoría F1 abierta desde S115).
3. **Recorte de la estructura en Estudio/"Todo"** (hoy `hidStruct := 0` = sin recorte) → bajaría
   `total_labels` < 500 y dejaría de desalojarse todo. Los arrays, el punto de corte y la política ya
   existen; el coste en tokens está **sin medir**.
4. **Calibrar `i_kLeg` = 3.0** en pantalla (fija hasta dónde llega la pierna).
5. **Recalibrar `i_swingDomAtr`** (8.0 provisional, commit `fd54448`) en su **rol NUEVO**: ya no filtra,
   solo sombrea (fuerte 45 / tenue 75) → con 8.0 casi todo sale tenue.
6. **Los ~194 tokens de `f_zLbl`**: la §6.5 ya NO está disponible como financiación. Caminos vivos (S124
   §7.2, ninguno medido): (b) cobrar las zonas en `f_isBandPick`; (c) atacar la estructura; (d) dieta estilo
   S121. El camino (a) ("no romper la forma una-expr") pierde fuerza tras el hallazgo de los 14 tokens.
7. Deuda S123 #2: meter EQ + estructura en `f_evLbl` (anti-solape).
8. Deuda S123 #3: zoom, calibración de la ranura X.
9. Deuda S123 #4: nudo de confluencia (CONFLUENCIA real que el usuario QUIERE ver).
10. Herencia H1/M5, auditoría → firma F1-GATE.

## Enlaces
[[Sesion-124]] · [[Sesion-123]] · [[Sesion-122]] · [[Sesion-121]] ·
`docs/planes/DISEÑO-presupuesto-labels-S124.md` (§8 = la medición S125)
