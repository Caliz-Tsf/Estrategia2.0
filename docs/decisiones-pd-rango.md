# Decisión de diseño — Rango de Premium/Discount (T07)

> F1-S1.2-T07. Registro de la decisión sobre **qué rango** usa `f_premiumDiscount`.
> Sesion-021 (2026-06-14). Decisión del usuario: **Opción A**. Este doc queda como
> referencia permanente para no re-litigar. Ver también [reglas-smc-ict.md §2.3] y
> el comentario del bloque T07 en `pine/SMC-Library.pine` / consumidores.

## Contexto

Premium/Discount/Equilibrium divide un **rango de negociación (dealing range)** en zonas
de valor: vender en premium (caro), comprar en discount (barato), evitar el equilibrium.
La **lógica** de clasificación no estaba en duda (premium > 50 %, discount < 50 %, banda
equilibrium [45 %, 55 %] que resta peso — confluencia #31, §2.3). Lo que había que decidir
es **cómo se define el rango [bottom, top]** sobre el que se mide esa posición.

Se presentaron dos opciones al usuario.

## Opción A — Trailing extremes de LuxAlgo *(ELEGIDA)*

El rango es el de LuxAlgo (`type trailingExtremes`, `updateTrailingExtremes`,
`drawPremiumDiscountZones`; ref. `pine/reference/LuxAlgo-SMC-base.pine` :181, :709-713,
:755-761):

- `top`/`bottom` se **re-anclan** al nivel del **último swing high / swing low confirmado**
  de **escala P/D** — `f_resetTrailingHigh/Low`.
- Entre re-anclajes, el rango **se expande** vela a vela con el precio
  (`top = max(high)`, `bottom = min(low)`) — `f_updateTrailing`.

**Longitud de swing P/D = 50 (input `i_pdSwingLen`, default LuxAlgo), NO el `swingLen=5`
estructural.** LuxAlgo basa su dealing range en `getCurrentStructure(swingsLengthInput=50)`
(ref `LuxAlgo-SMC-base.pine` :95 input=50, :782 la llamada), mientras la estructura interna
usa 5 (:783). Nuestro T03/T04 eligió `swingLen=5` para BOS/CHoCH (más local), así que el
swing de P/D se detecta **aparte**, con su propia longitud, para reproducir el rango
**dominante** de LuxAlgo.

> **Bug encontrado y corregido en Sesion-021:** la primera implementación alimentó los
> trailing extremes con los swings estructurales `swingLen=5` → rango **local** (~60 pips,
> p.ej. `[1.15572, 1.16176]`), que NO coincidía con LuxAlgo ni con §2.3. Lo detectó el
> usuario al comparar con el indicador LuxAlgo (discount en el LL del 8-jun ~1.15000). Fix:
> swing P/D dedicado `i_pdSwingLen=50`. Resultado: el rango pasó a `[1.14997, 1.16859]`,
> **idéntico** a §2.3 y a LuxAlgo (ver "Validación" abajo).

### Por qué se eligió A
1. **Paridad con la única referencia externa permitida.** El proyecto solo puede portar
   algoritmos del indicador SMC de LuxAlgo (regla absoluta de CLAUDE.md). A reproduce su
   comportamiento función a función → coherencia con OB/FVG/EQHL que ya se portaron de ahí.
2. **Portabilidad limpia a MQL5 (Fase 4, ADR-002).** El estado es **plano**
   (`SMC_Trailing` = 6 campos) y determinista: no depende del historial de eventos
   estructurales (BOS/CHoCH) ni de heurísticas para elegir "el" rango dominante. Golden
   tests directos.
3. **Determinismo y anti-repaint.** El rango se re-ancla solo con swings confirmados; el
   snapshot para el scoring (`chartState.pdHigh/pdLow`) se congela en
   `barstate.isconfirmed`. La expansión en vivo del dibujo replica a LuxAlgo y no repinta
   la historia.

## Opción B — Último strong high/low por estructura (BOS/CHoCH) *(descartada)*

El rango sería el delimitado por el **último strong high y strong low** marcados por la
estructura ya implementada (T03/T04): los niveles cuya ruptura generó el último BOS/CHoCH.
Es la lectura "ICT pura" del *dealing range* (el rango del movimiento estructural vigente),
y se acerca más al **rango dominante** que usan los casos fechados de §2.3.

### Por qué NO se eligió B
1. **Se aleja de LuxAlgo** → rompe la doctrina de portar la referencia única.
2. **Más estado y más frágil de portar.** Habría que decidir qué par de swings "strong"
   delimitan el rango y mantener esa elección coherente con el bias — más lógica
   condicional, más difícil de reproducir 1:1 en MQL5.
3. **Mezcla responsabilidades.** Atar el rango de localización al motor de estructura
   acopla dos conceptos que conviene mantener independientes hasta la calibración (Fase 3).

> B no está "mal": es la lectura ICT más ortodoxa y da un rango más amplio/significativo.
> Si en **Fase 3** se observa que el rango local de A degrada el scoring de localización,
> B (o un híbrido "rango significativo") queda como alternativa documentada para revisitar.

## Validación contra reglas-smc-ict.md §2.3

Con el swing P/D = 50, el indicador reproduce los casos fechados de §2.3 (EURUSD H1,
2026-06-11) **al 5.º decimal**:

| Nivel | Indicador T07 (label) | reglas §2.3 |
|---|---|---|
| Premium (strong high) | 1.16859 | 1.16859 ✓ |
| EQ (50 %) | 1.15928 | 1.15928 ✓ |
| Discount (strong low) | 1.14997 | 1.14997 ✓ |
| Banda EQ [45 %, 55 %] | [1.15835, 1.16021] | [1.15835, 1.16021] ✓ |

La **lógica** también se verificó numéricamente (close en premium → panel "Premium NN %",
coincide con `(close-bottom)/(top-bottom)`). No hace falta reconciliar §2.3: la opción A con
`i_pdSwingLen=50` **coincide** con el rango dominante que describe la spec y con LuxAlgo.

## Estado
- Implementado en CORE (byte-idéntico Visual/Strategy) + export en Library. Compila 0/0.
- Dibujo solo en Visual: **3 líneas** (premium roja en strong high / discount verde en
  strong low / equilibrium punteada gris al 50 %) + etiquetas + fila de panel. Se cambió
  de cajas rellenas a líneas (Sesion-021, preferencia del usuario: menos ruido visual,
  estilo LuxAlgo `drawTrailingExtremes`).
- Decisión **congelada** hasta Fase 3 (anti-overfitting, ADR-002). Revisitar B solo con
  evidencia out-of-sample.

## Nota S057 (2026-06-24) — observación del usuario confirma el disparador de revisit Fase 3
Durante la validación visual (S057), el usuario observó en vivo que el rango P/D **"camina" hacia el precio en tendencia bajista**: el premium se reancló de ~1.14388 a ~1.13845 (cerca del precio) y los discounts de D1/H1/M5 se amontonaron cerca del precio. **Diagnóstico (datos reales, precio 1.1365):** D1 discount 1.13757 (panel −1%, precio por debajo del piso D1), H1 ~1.13613 (2%), M5 ~1.13613 (20%). El D1 aparece arriba (junto al EQ del M5) porque su estado viene por `request.security("D", lookahead_off)` y **solo se actualiza al cierre de la vela diaria** (anti-repaint); H1/M5 se solapan porque capturaron el mismo mínimo fresco.

**Conclusión:** es la **Opción A operando como se diseñó** (re-anclaje de cada extremo al swing P/D de 50 más reciente → el rango sigue a la tendencia), NO un bug. El comportamiento que el usuario esperaba (mantener anclado el extremo no roto; reanclar solo el roto) **es la Opción B**, ya descartada para Fase 1. Esta observación es **evidencia cualitativa que confirma el disparador documentado** ("si el rango local de A degrada el scoring de localización, revisitar B/híbrido en Fase 3"). **Decisión S057 del usuario: mantener Opción A**; el cambio a B/híbrido se evalúa en Fase 3 con datos OOS.

**Micro-pulido cosmético OPCIONAL (diferido):** cuando el precio queda fuera del rango (pct<0 o >100%), el panel muestra "Discount −1%"; podría mostrar "bajo rango"/"sobre rango" (solo Visual, no toca CORE).

## Nota S091 (2026-07-03) — el usuario RE-CONFIRMA Opción A
El usuario volvió a observar el mismo síntoma (D1 Discount 1.13246 pegado al mínimo reciente ≈ precio, Premium 1.20831 lejos) y planteó explícitamente el modelo Opción B (*"anclar el Discount al bajo más bajo del swing; que D1 quede lejos mientras el precio no rompa ese bajo, y así por temporalidad"*). Se le presentó el trade-off A / B / híbrido vía AskUserQuestion. **Decisión: mantener Opción A (statu quo).** El cambio a B/híbrido sigue diferido a **Fase 3** con datos out-of-sample, igual que en S057. Esta es la **2.ª confirmación** del disparador de revisit documentado — dejar constancia para no re-litigar en Fase 1.

---

## Nota S133 (2026-07-15) — DOS CORRECCIONES a este documento, y la razón #1 de S021 se cayó

### (a) La razón #1 de la Opción A ("paridad con LuxAlgo") era COSMÉTICA — verificado
Este doc justifica A con *"Paridad con la única referencia externa permitida... A reproduce su comportamiento función a función"*. **Verificado en la referencia (S133):** el **"Strong High"/"Strong Low" de LuxAlgo es una ETIQUETA DE TEXTO**, decidida por el bias **después** de calcular el rango (`pine/reference/LuxAlgo-SMC-base.pine:728`, `:733`: `swingTrend.bias == BEARISH ? 'Strong High' : 'Weak High'`). **Su ancla nunca mira el bias** (`:409-457`: resetea al pivote de escala 50, cualquier pivote). ⇒ **LuxAlgo jamás calculó un rango anclado en strong high/low.** Mantener A no preserva una semántica de LuxAlgo — solo preserva **su atajo**. La razón #2 (portabilidad MQL5) y la #3 (determinismo) siguen en pie y **el diseño de S133 las respeta** (estado plano de 6 floats; `f_premiumDiscount` intacta).

### (b) El veredicto de S132 sobre `i_pdSwingLen`=1000 era ERRÓNEO — no revertir
S132 declaró el fix de S130 (`i_pdSwingLen` 50→1000, commit `61dcc36`) **"doctrinalmente incorrecto"** con este razonamiento: *"con 1000 casi ningún pivote reancla ⇒ solo actúa el trailing ⇒ el rango tiende a fósil, justo lo que §6.3.5 prohíbe"*.

**El razonamiento es falso.** §6.3.5 prohíbe medir P/D sobre un rango **YA SUPERADO por la estructura**. Un rango que **solo expande** nunca está superado: **contiene el precio por construcción** (`nOutRange`=0, medido en S129 y S133). El "rango fósil" que S132 vio como defecto **es el requisito explícito del usuario** (S133: *"debe quedarse con los premium o discount hasta que genere de nuevo un bajo más bajo o un alto más alto"*). ⇒ **NO revertir `pdLen`=1000** mientras la Opción A siga vigente. *(Nota: el input desaparece con el diseño de S133 — el 2.º extremo no necesita escala de pivote.)*

Pero acierta **por accidente del mecanismo**: da `[0.95360, 1.60389]` (= la lectura del usuario) solo porque con `pdLen`=1000 el reset casi nunca dispara, y porque el pool 0.95360 tiene **edad 984 < 1000**. **Coincidencia frágil, no regla.**

### (c) El disparador de revisit SE ACTIVA — pero el modelo NO es la Opción B
Las notas S057 y S091 dejaron el revisit condicionado a Fase 3. **Se reabre en S133 con evidencia nueva** (la de (a)), y por mandato del usuario (*"si tienes mejoras o ideas mejores para hacer este cálculo bien, implementémosla, pero que sea LA solución"*). **La Opción B tampoco es el modelo** — se midió muerta en S128 (mueve el veredicto solo **3.2%**, n=6283) porque anclaba en pivotes de otra escala: misma mecánica que A.

**El modelo elegido es una TERCERA vía**, del usuario y cerrada con sus respuestas en S133: **el 2.º extremo estructural** (`reglas-smc-ict.md` §2.3.1/§2.3.2) — históricos marcados aparte, dealing range en el 2.º strong low/high de la escala de cada TF, strong/weak decidido por el **bias**. Ver `docs/planes/DOCTRINA-strong-high-low-S133.md` y el plan `1-la-ventana-de-giggly-blum.md`.

### (d) La tabla de "Validación contra §2.3" de este doc NO es un oráculo
Los 4 valores al 5.º decimal se generaron **desde la Opción A ya implementada** ⇒ **validan la implementación contra sí misma**. Marcado también en `reglas-smc-ict.md` §2.3. Se regeneran tras implementar §2.3.2.

**Estado:** el ADR-021 supersederá este documento si la Fase 1 (probe en sombra, multi-símbolo) pasa su gate. **Nada implementado a fecha de esta nota; `pine/` intacto; S021 sigue congelada hasta el gate humano.**
