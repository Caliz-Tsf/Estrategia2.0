# Revisión T13b — Mapa MTF: de "niveles extendidos" a "dibujo geométrico anclado"

> Revisión técnica pedida por Freddy (S041) sobre la cascada MTF que ya corre en runtime (foto EURUSD M5 con H1/D1 heredados).
> **Veredicto corto:** lo implementado **está bien hecho para lo que su spec pedía** (ADR-009 + spec-T13b), pero **lo que la spec pedía NO es lo que necesitas**. El diagnóstico de Freddy es correcto. Esto es un **cambio de alcance de diseño** (revisión de ADR-009), no un bug. No se tocó ningún `.pine`.

---

## 1. Qué se implementó hoy (y es correcto respecto a su propia spec)

La cascada T13b funciona: `f_computeTFState` corre la detección de OB/FVG/pools/sweep **en el contexto del HTF** con estado `var` interno (R-P3-1, spike S039 ✅), selecciona las K más cercanas al precio y las aplana en un **buffer genérico etiquetado** (`[kind, top, bottom, dir]` × 16) que viaja por **1 sola `request.security`/TF**. El consumidor lo reconstituye y lo dibuja. Todo esto es sólido y **se respeta**:

- **Anti-repaint** ✅ — `lookahead = barmerge.lookahead_off` + eventos en `barstate.isconfirmed` ([SMC-Visual.pine:1184](pine/SMC-Visual.pine:1184), [SMC-Visual.pine:806](pine/SMC-Visual.pine:806)).
- **Estado por-contexto sin contaminar el chart** ✅ — `var` interno a la función ([SMC-Visual.pine:779-791](pine/SMC-Visual.pine:779)).
- **Cascada solo hacia TF estrictamente menores** ✅ — `timeframe.in_seconds()` ([SMC-Visual.pine:1497-1498](pine/SMC-Visual.pine:1497)).
- **Cap por concepto + selección por cercanía** ✅ — `f_nearestN` ([SMC-Visual.pine:716](pine/SMC-Visual.pine:716)).
- **Extensibilidad** ✅ — añadir un concepto = `push` con su `kind`, sin cambiar el contrato.
- **Presupuesto del tuple** ✅ — 81 < ~127.

**El mecanismo de transporte (buffer genérico etiquetado) es bueno y hay que conservarlo.** El problema no está ahí.

---

## 2. El diagnóstico de Freddy es correcto: 5 síntomas, 1 causa

Lo que se ve en la foto (M5 con H1 fucsia / D1 azul):

| Síntoma observado | Realidad en el código | Esperado |
|---|---|---|
| OB y FVG salen como **líneas punteadas, no cajas** | `f_drawMTFZones` dibuja la "caja" como **2 líneas horizontales** (top y bottom), no un `box` ([SMC-Visual.pine:1489-1491](pine/SMC-Visual.pine:1489)) | Caja (`box`) con su alto/bajo reales |
| **Sweep** sale como una línea al lado derecho del precio | Se transporta solo el `price` y se dibuja como línea horizontal extendida ([SMC-Visual.pine:872-877](pine/SMC-Visual.pine:872), dibujo :1488) | Marca (▲/▼) **arriba/abajo de la vela donde ocurrió** |
| **Premium/Discount** se ven superpuestos / fuera de sitio | Líneas punteadas `extend.left` ancladas al borde actual ([SMC-Visual.pine:1466-1468](pine/SMC-Visual.pine:1466)) | OK como niveles, pero compiten visualmente con los del TF propio |
| **EQH/EQL no aparecen** donde se formaron | Solo alimentan pools internamente; **no se transportan como dibujable** ([SMC-Visual.pine:850-853](pine/SMC-Visual.pine:850)) | Línea de techo/suelo igual, **de la barra A a la barra B reales** |
| **BOS/CHoCH no se transfieren** como estructura | Solo viajan como escalares (último precio) para el panel; **no se dibujan en el LTF** | Línea **desde donde inicia hasta donde rompe**, en el LTF |

**Causa raíz única:** todo el mapa rico se dibuja como **niveles horizontales extendidos al borde derecho**, sin geometría nativa y **sin anclaje a la barra de origen**. Las zonas-caja se degradan a dos líneas; los puntos (sweep/pool) a una línea; y los conceptos que son *tramos* (EQH/EQL, BOS/CHoCH) o *marcas* (sweep) ni siquiera tienen forma propia.

---

## 3. Por qué pasa esto: fue una decisión deliberada de ADR-009

No es un descuido del implementador. **ADR-009 lo dice explícitamente** ([ADR-009 línea 31](docs/adrs/ADR-009-transporte-mtf-buffer-generico-etiquetado.md)):

> *"Se omite `barTime`: las zonas HTF se dibujan como **niveles de referencia extendidos al borde actual (no ancladas a su barra de origen)**, así que la marca temporal no se usa en T13b."*

Es decir: para ahorrar presupuesto del tuple, ADR-009 sacrificó (a) el **anclaje temporal** y (b) la **geometría por concepto**, apostando a que "niveles de referencia" bastaban. La foto demuestra que **para tu caso de uso no bastan**: un *sweep → desplazamiento → FVG en el que quieres entrar* solo es útil si **ves el FVG como caja en el lugar donde está**, y un sweep solo se entiende **marcado en el swing que barrió**.

La ranura `[kind, top, bottom, dir]` no lleva ni *cuándo* ni *qué forma*. Por eso el dibujo no puede hacer otra cosa que una línea.

---

## 4. Mi opinión

**Estás en lo correcto y es el momento correcto para corregirlo.** El T13b actual entrega un **"mapa de niveles"**; tú necesitas un **"mapa geométrico"**: cada concepto cruza de D1→H1→M5 **con su dibujo nativo y anclado a sus coordenadas reales**. La buena noticia es que **el 80% de la arquitectura sirve tal cual** — el buffer genérico etiquetado de ADR-009 es exactamente el vehículo correcto; solo le falta llevar el *anclaje* y al consumidor *reconstruir la forma*. Y la técnica ya existe en el propio código: `f_drawStructure` ya ancla por tiempo con `xloc.bar_time` en la escala `SC_MAJOR` ([SMC-Visual.pine:1228](pine/SMC-Visual.pine:1228)) — es la misma herramienta que necesitamos para HTF→LTF.

Esto **supersede el contrato de transporte de ADR-009** (no el resto: cascada, pared dura, paridad MQL5 siguen vigentes) → toca **ADR-010** + una tarea nueva (**T13c "mapa geométrico"**). No es re-litigar arquitectura; es completar lo que el caso de uso pide.

---

## 4bis. Cómo encaja el "0-10 por concepto, para los ~40-50 conceptos" (aclaración S041)

El cap **0-10 por concepto** que pides es el corazón del control y la arquitectura lo soporta, **con dos niveles de cap** que hay que tener claros porque el segundo es un límite duro de Pine:

1. **Cap por concepto (0-10):** "de este concepto, deja competir hasta N de los más cercanos al precio" (`0` = no transferir ese concepto). Hoy existe **solo para OB/FVG/pool**; la corrección lo extiende a **todos** los conceptos detectados.
2. **Cap global por TF (K):** de TODOS los candidatos que pasaron el filtro por-concepto, **solo se dibujan los K más cercanos al precio**. `request.security` no transporta más de ~127 números por llamada → **no se puede garantizar cupo fijo para cada uno de 40-50 conceptos en una sola llamada**. Se ven los **K más cercanos por TF**.

**Por qué tu escenario funciona igual:** cada HTF viaja en **su propia `request.security` con su propio buffer K** → D1 y H1 NO compiten entre sí.

> **Ejemplo trabajado (tu caso):** CHoCH en D1 + desplazamiento que deja FVG en H1, quieres entrar en M5 al mitigar.
> - Buffer **D1** (cap CHoCH ≥1): el CHoCH está cerca del precio → entra en sus K → se dibuja en M5 como **línea origen→ruptura** azul con prefijo `D1:`.
> - Buffer **H1** (cap FVG ≥1): el FVG está cerca del precio → entra en sus K → se dibuja en M5 como **caja** fucsia con prefijo `H1:`.
> - Resultado: ves AMBOS en M5, cada uno con su forma, en su sitio, esperando la mitigación. ✅

**Consecuencia práctica:** subir el cap de los 40 conceptos a 10 NO muestra 400 objetos — muestra los **~K más cercanos por TF**. El cap por concepto sirve para **priorizar la mezcla** (p.ej. "quiero hasta 3 FVG pero solo 1 EQH"), no para forzar todo. Si en Fase 3 hace falta más densidad, se activa la **2ª llamada/TF** que ADR-009 ya dejó preparada (≈ duplica K).

---

## 5. Diseño corregido (propuesta para ADR-010 / T13c)

### 5.1 Ampliar la ranura con anclaje temporal

Ranura nueva (uniforme para todos los conceptos, paridad MQL5):

```
ranura_i = [ kind, top, bottom, dir, tA, tB ]   // 6 números
  tA : tiempo de la barra de ORIGEN (left de la caja / 1er toque EQ / inicio del tramo / barra del sweep)
  tB : tiempo de FIN (right de la caja o na=extiende a la vela actual / 2º toque EQ / barra de ruptura BOS/CHoCH)
```

- **Puntos** (pool, sweep): `top==bottom==level`, `tA`=barra del hecho, `tB`=na.
- **Cajas** (OB, FVG): `top/bottom`=rango real, `tA`=origen, `tB`=na (extiende al borde) o tiempo de mitigación.
- **Tramos** (EQH/EQL, BOS/CHoCH): `top`/`bottom`=nivel(es), `tA`→`tB`=los dos extremos del tramo.

> `time` epoch-ms (~1.75e12) cabe exacto en float64 (< 2^53). Viaja por `security` sin pérdida.

### 5.2 Presupuesto del tuple (la única restricción dura)

| Config | Cálculo | ¿Cabe en 1 `security`? |
|---|---|---|
| K=16, ranura 6 | 17 + 16×6 = **113** | Sí, pero al límite (~127) |
| K=12, ranura 6 | 17 + 12×6 = **89** | Sí, con holgura ✅ (recomendado) |
| K=16, ranura 6, **2ª llamada/TF** | 2×(17+...) | Sí — ADR-009 ya dejó la 2ª llamada *preparada, no activada* |

**Recomendación:** arrancar con **K=12 + ranura de 6** (1 llamada, holgado). Si en Fase 3 falta densidad, activar la 2ª llamada que ADR-009 ya previó.

### 5.3 Dibujo por `kind` (consumidor, `f_drawMTFZones` reescrita)

`xloc.bar_time` para que el objeto caiga en su lugar real del chart LTF aunque se detectara en D1/H1:

| Concepto | Dibujo nativo en el LTF |
|---|---|
| OB | `box.new(left=tA, right=tB/now, top, bottom)` color tenue + prefijo `D1:`/`H1:` |
| FVG | `box.new(...)` con tono propio (distinto de OB) + línea CE punteada |
| EQH/EQL | `line.new(tA→tB, level)` + label "EQH"/"EQL" en el sitio |
| BOS/CHoCH | `line.new(origen tA → ruptura tB, nivel)` + label (reusa el estilo de `f_drawStructure` SC_MAJOR) |
| Sweep | `label`/triángulo **arriba (BSL) o abajo (SSL)** en la barra `tA` |
| Pool (BSL/SSL) | línea corta al nivel, anclada a su barra |

Mantener: estilo tenue/punteado, prefijo de TF, **cuota de objetos por (concepto × TF) + Present mode** (R-3) — crítico ahora que son `box`/`line` reales y rotan con la mitigación.

### 5.4 Qué se añade al buffer en el productor

Hoy se pueblan OB, FVG, pools, sweep — pero **solo OB/FVG/pool tienen cap por concepto**. La corrección: **cada concepto detectado tiene su toggle de traspaso + su cap 0-10**, y todos se emiten como ranuras con `tA/tB` (ya se detectan internamente, solo falta exponerlos):

| Concepto | Estado hoy | Corrección |
|---|---|---|
| OB | cap ✅, dibujo línea | cap ✅ + **caja** anclada |
| FVG | cap ✅, dibujo línea | cap ✅ + **caja** anclada |
| Pool (BSL/SSL) | cap ✅, línea | cap ✅ + línea anclada a su barra |
| **Sweep** | sin cap (solo el último), línea | **cap propio** + **marca ▲▼** en la barra `tA` |
| **EQH/EQL** | no se emite (solo alimenta pools) | **cap propio** + **línea tramo** `tA→tB` (`evEqH/evEqL` ya existen, :838-845) |
| **BOS/CHoCH** | solo escalar para panel | **cap propio** + **línea origen→ruptura** (estructura HTF ya calculada, :809) |
| ~40 conceptos ICT (T26-T40) | no existen aún | mismo mecanismo: al detectarse, `push` con su `kind` + cap. **El contrato del tuple NO cambia** |

El resto del pipeline (`f_nearestN`, selección global por cercanía, aplanado) no cambia de forma — solo crece la ranura a 6 campos y se añaden los `kind` nuevos.

---

## 6. Impacto y reglas duras

- **CORE byte-idéntico (regla #2):** `f_computeTFState` + `f_nearestN` viven en el CORE → cambia SHA y nº de líneas (esperado, documentar en commit) + `check-core-sync.ps1`.
- **Paridad MQL5 (ADR-002):** la ranura de 6 campos es el formato canónico que `SMC_MTF.mqh` replicará — anclaje temporal **mejora** la paridad (el EA dibuja igual por tiempo).
- **Anti-repaint (regla #1):** sin cambios; sigue `lookahead_off` + `isconfirmed`.
- **Documentos:** ADR-010 (supersede *solo el transporte* de ADR-009) + spec T13c + actualizar PINE-PLAN §7. ADR-009 queda como historia de la decisión previa.
- **Escalación:** por la regla dura de S038, las decisiones del transporte MTF se escalan a **Opus ultracode**. Este documento es justamente el insumo de ese handoff.

---

## 7. Decisiones

**Confirmadas por Freddy (S041):**
- ✅ **BOS/CHoCH SÍ se dibujan en el LTF** (con su línea origen→ruptura), con **toggle + cap propio** como todo concepto.
- ✅ **Cap 0-10 por concepto para TODOS los conceptos** (no solo OB/FVG/pool).
- ✅ Anclaje + dibujo nativo por concepto (cajas, líneas, marcas).

**Pendientes de confirmar (menores, no bloquean el diseño):**
1. **K por TF:** recomiendo **K=12 en 1 llamada** (holgado, 89<127) para arrancar; 2ª llamada se activa en Fase 3 si falta densidad.
2. **Caja extendida al borde** (recomendado, por el caso de uso "zona a la que el precio retrocede") vs cortada donde el HTF la dejó.
3. **Sweep:** ▲▼ en la barra (recomendado) vs label de texto.

---

## 8. Estado y plan (cierre S041)

- **0 cambios en `.pine`** en esta sesión. Esto es revisión + diseño aprobado.
- **Decisión Freddy (S041):** se cierra el documento; la **implementación es T13c, próxima sesión**. Esqueleto implementación-ready en §9 (cualquier IA puede rellenar los cuerpos con esta guía).
- **Integrado al workplan unificado:** `docs/workplan/PINE-PLAN.md §7` (ítem 13c) + `docs/planes/ESQUELETO-P3-mapa-mtf-confluencias.md` §4.1 (fila T13c), §5.2 (diagrama), §5.4 (paso 4b).
- **Pendiente formal antes de codear:** escribir **ADR-010** (supersede el transporte de ADR-009; el resto de ADR-009 sigue vigente) — su contenido ya está esbozado en §4bis+§5+§6 de este doc.

---

## 9. Esqueleto de implementación T13c (paso a paso, implementación-ready)

> Objetivo: que cualquier IA implemente esto rellenando cuerpos con esta guía. **Regla de oro:** se cambia el **contrato de la ranura** y el **dibujo del consumidor**; el **mecanismo** (buffer genérico, `f_nearestN`, selección global por cercanía, 2 `request.security`) se conserva. CORE byte-idéntico ×3 (Library + Visual + Strategy) → al terminar, `scripts/check-core-sync.ps1` y documentar SHA nuevo.

### Constantes `kind` ya existentes (no inventar — `SMC-Library.pine:15-45`)
`KIND_OB=1 · KIND_FVG=2 · KIND_POOL=8 · KIND_BOS=20 · KIND_CHOCH=21 · KIND_SWEEP=23 · KIND_EQH=44 · KIND_EQL=45`. El productor etiqueta con estas; el consumidor hace `switch` sobre ellas para elegir la forma.

### Paso 0 — Constantes y contrato (CORE, byte-idéntico ×3)
- `MTF_SLOT = 4` → **`MTF_SLOT = 6`** ([SMC-Visual.pine:117](pine/SMC-Visual.pine:117)).
- `MTF_K = 16` → **`MTF_K = 12`** (decisión §7-1; 17 + 12×6 = 89 < ~127). *(Si al compilar se quiere más densidad y cabe, subir K; si no cabe, activar 2ª llamada — ver Paso 6.)*
- **Contrato nuevo de la ranura** (actualizar el comentario canónico en `f_computeTFState`, [SMC-Visual.pine:774-777](pine/SMC-Visual.pine:774)):
  ```
  ranura_i = [ kind, top, bottom, dir, tA, tB ]   // 6 números (antes 4)
    tA : tiempo barra ORIGEN   (left caja / 1er toque EQ / inicio tramo BOS-CHoCH / barra del sweep / barra del pool)
    tB : tiempo barra FIN      (na = extiende al borde; 2º toque EQ; barra de ruptura BOS-CHoCH)
    puntos (pool/sweep): top==bottom==level, tB=na
  ```
  Tuple completo = `[17 escalares T13a] ++ [MTF_K ranuras × 6]`.

### Paso 1 — `f_nearestN` / `f_nearestNPools`: añadir tiempos a los candidatos (CORE)
Hoy los arrays-candidato son `ck/ct/cb/cd/cdist` ([SMC-Visual.pine:716](pine/SMC-Visual.pine:716), :740). **Añadir dos arrays `ctA` (tiempo A) y `ctB` (tiempo B)** a la firma y al `push`:
- `f_nearestN`: `ctA ← z.barTime` (origen de la zona), `ctB ← na` (las cajas OB/FVG extienden al borde; decisión §7-2). *Verificar que `SMC_Zone` tiene `barTime`; si la zona OB/FVG guarda también su fin, usarlo en `ctB`, si no `na`.*
- `f_nearestNPools`: `ctA ← p.barTime` (la barra del pool; `SMC_Pool` ya tiene `barTime` y `barIdx`), `ctB ← na`.
- **Nueva `f_nearestNEvents`** (o reusar patrón) para conceptos basados en `SMC_Event` con dos extremos (EQH/EQL, BOS/CHoCH): empuja `top=bottom=level` o `top/bottom` según aplique, `ctA=inicio`, `ctB=fin`.

### Paso 2 — Productor `f_computeTFState`: emitir TODOS los conceptos con cap propio (CORE)
Hoy solo OB/FVG/pool tienen cap y sweep se empuja suelto ([SMC-Visual.pine:869-877](pine/SMC-Visual.pine:869)). Cambios:
1. **Firma:** añadir caps por concepto que faltan → `capSweep, capEQ, capBOS, capCHoCH` (0-10; 0 = no transferir). Total params de cap: OB/FVG/pool (ya) + estos 4.
2. **Detección interna ya existe** dentro de la función (no re-implementar): estructura/BOS/CHoCH ([:809](pine/SMC-Visual.pine:809)), MSS ([:811](pine/SMC-Visual.pine:811)), OB ([:832](pine/SMC-Visual.pine:832)), FVG ([:835](pine/SMC-Visual.pine:835)), EQH/EQL ([:840-845](pine/SMC-Visual.pine:840)), pools/sweep ([:847-857](pine/SMC-Visual.pine:847)). **Falta persistir** sus extremos en arrays `var` internos para poder seleccionarlos:
   - mantener `var array<SMC_Event>` (o arrays paralelos de nivel+tiempos) para **BOS/CHoCH** (origen=`structTf.high/lowBarIdx`+su time, fin=barra de ruptura), **EQH/EQL** (los dos toques), y **sweep** (barra + dirección). Hoy solo se guarda `lastSweepTf`.
3. **Selección:** tras los `f_nearestN` actuales, añadir llamadas para los conceptos nuevos respetando su cap, anexando a los mismos arrays-candidato (`cKind/cTop/cBot/cDir/cDist/ctA/ctB`).
4. **Aplanado:** el bloque de orden global por `cDist` y relleno de `MTF_K` ranuras ([:878-894](pine/SMC-Visual.pine:878)) ahora copia **6 campos** por ranura (añadir `mtA`, `mtB`). El `return` tuple ([:895+](pine/SMC-Visual.pine:895)) crece a `…, mk_i, mt_i, mb_i, mdr_i, mta_i, mtb_i` por ranura.

### Paso 3 — Consumidor (Visual **y** Strategy idéntico): reconstituir 6 campos
- Las 2 `request.security` ([SMC-Visual.pine:1184-1185](pine/SMC-Visual.pine:1184)): el destructuring crece a 17 + K×6 nombres por TF (mecánico; mantener el patrón `d1_k0,d1_t0,d1_b0,d1_d0,d1_ta0,d1_tb0, …`).
- Reconstituir **6 arrays** por TF: `d1Kind/d1Top/d1Bot/d1Dir/**d1TA/d1TB**` (y `h1…`) con `array.from(...)` ([:1190-1197](pine/SMC-Visual.pine:1190)).
- *(Higiene: Strategy replica la reconstitución aunque no dibuje, para que el scoring de Fase 2 lea las mismas ranuras.)*

### Paso 4 — Reescribir `f_drawMTFZones` con forma nativa anclada por tiempo (Visual, presentación)
Reemplazar el dibujo actual de 2 líneas ([SMC-Visual.pine:1479-1492](pine/SMC-Visual.pine:1479)) por un `switch` sobre `kind` que use **`xloc.bar_time`** (clave: el `bar_index` del HTF NO mapea al chart; el tiempo SÍ). Firma nueva: recibe también `tas`/`tbs`. Por ranura `i` con `kind k`:
```
nowT = time                       // borde actual (para extender)
switch k
  KIND_OB, KIND_FVG =>
      // CAJA anclada: left=tA, right = na(tB)? nowT : tB  (decisión §7-2: extender al borde)
      box.new(left=tA, top, right=(na(tB)?nowT:tB), bottom, xloc=xloc.bar_time,
              border/ bgcolor tenue (transp ~85), prefijo "D1:"/"H1:"; OB y FVG con tono distinto)
  KIND_EQH, KIND_EQL =>
      line.new(tA, level, tB, level, xloc=xloc.bar_time, dotted)  + label "EQH/EQL"
  KIND_BOS, KIND_CHOCH =>
      line.new(tA, level, tB, level, xloc=xloc.bar_time)          + label (reusar estilo f_drawStructure SC_MAJOR :1228, que YA usa xloc.bar_time)
  KIND_POOL =>
      line.new(tA, level, nowT, level, xloc=xloc.bar_time, dashed) + label "BSL/SSL"
  KIND_SWEEP =>
      label.new(tA, level, "▲"/"▼" según dir, xloc=xloc.bar_time,
                style label_up (SSL, abajo) / label_down (BSL, arriba))   // MARCA en su barra, NO línea
```
Mantener todo en `SMC_mtfLines`/`SMC_mtfLabels` + **añadir `var array<box> SMC_mtfBoxes`** (las cajas son `box`, no `line`) y limpiarlas en el mismo bloque `barstate.islast` ([:1499-1505](pine/SMC-Visual.pine:1499)). **Cuota de objetos** (R-3): ya capado a K en transporte; vigilar el total de `box`+`line` < 500/tipo.

### Paso 5 — Inputs `GRP_MTF`: cap por concepto para TODOS (Visual + Strategy)
Hoy `i_mtfCapOB/FVG/Pool` ([SMC-Visual.pine:1184](pine/SMC-Visual.pine:1184) wiring). **Añadir** `i_mtfCapSweep`, `i_mtfCapEQ`, `i_mtfCapBOS`, `i_mtfCapCHoCH` (`input.int`, minval 0, maxval 10, default 2 salvo BOS/CHoCH default 1 por carga visual). Pasarlos a las 2 llamadas `f_computeTFState`. (Toggles maestros `i_showD1/i_showH1` ya existen.) *Opcional §7-3: input `i_mtfSweepMark` bool ▲▼ vs label.*

### Paso 6 — (preparado, NO activar) 2ª llamada/TF
Si en Fase 3 falta densidad: duplicar K vía 2ª `request.security` por TF como previó ADR-009 §"Cupo". No tocar ahora (regla #8, no sobre-construir).

### Verificación (gates, en orden)
1. **Compila 0/0 los 3** — `python scripts/pine_check.py` (o `pine_smart_compile` en TV). **Si el tuple excede el límite v6** → bajar `MTF_K` hasta que compile (mensaje "tuple too large") y anotarlo.
2. **`scripts/check-core-sync.ps1` = OK** — `f_computeTFState`/`f_nearestN` byte-idénticas en Visual y Strategy; documentar **SHA nuevo** y nº de líneas en el commit.
3. **Anti-repaint** (regla #1): `lookahead = barmerge.lookahead_off` intacto en las 2 llamadas; eventos del productor en `barstate.isconfirmed` (ya está). Verificar que al cerrar la barra del chart los objetos HTF no saltan.
4. **Validación ≥90** (smc-validator-agent): en EURUSD M5, comparar una caja OB/FVG y un tramo BOS/CHoCH del mapa **contra el cambio manual a D1/H1** → deben caer en la misma barra/nivel. Screenshot a disco.
5. **Commit** Conventional + ID: `feat(pine-core): F1-S1.4-T13c mapa MTF geométrico (ranura 6, dibujo nativo anclado)`.

### Gotchas (errores a evitar)
- **No usar `bar_index` para anclar HTF** → usar `xloc.bar_time` SIEMPRE en el dibujo MTF (el `bar_index` del contexto D1/H1 no corresponde al del chart).
- **`time` por `security`:** epoch-ms cabe exacto en float64; al reconstituir, castear a `int` para `xloc.bar_time`.
- **Cajas = `box`**, no `line` (array y limpieza propios).
- **No romper core-sync:** el dibujo (`f_drawMTFZones`, `GRP_MTF` inputs) es **presentación → Visual-only**, fuera del CORE; solo `f_computeTFState`/`f_nearestN`/constantes van en el CORE byte-idéntico.
- **MQL5 (ADR-002):** la ranura de 6 campos es el formato canónico de `SMC_MTF.mqh` (Fase 4) — mantener el orden idéntico.
