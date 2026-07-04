# ESQUELETO — Doctrina de proyección + confluencia (render · score · agentes · EA) — entregable Fable

> **Sesión:** S092/S093 · Fase 1 (F1-GATE, Eje 2 cerrado técnicamente) · rama `pine/sistema-completo`.
> **Qué es:** respuesta al `DOSSIER-FABLE-proyeccion-confluencia.md` §5 (entregables A–F) y a su pregunta abierta §7. Ordena la reformulación del usuario (Sesion-092): la importancia NO es fuerza×cercanía sino **relevancia estructural + confluencia, leída como proyección**.
> **Qué NO es:** NO es código. Fichas `[impl]` con cuerpo TODO; cada número es candidato **CONGELADO hasta Fase 3** (ADR-002). Se rellena bajo el gate `sprint16` (regla cuantificada + casos EURUSD antes de codificar) y los gates normales (0/0 → validador ≥90 → core-sync → un commit = un concepto).
> **Encaja con (no contradice):** `ESQUELETO-FABLE-sistema-visual.md` (capas §3, color §5, antisolape §6, MTF §7, matriz §8.2, checklist §10 — TODO se conserva; este esqueleto **sustituye la llave de orden** §2.5 y **completa** la selección top-N), ADR-012 (protocolo del agente — se extiende, no se reemplaza), ADR-014 (frontera CORE/Visual — se aplica el mismo criterio a los primitivos nuevos), ESQUELETO-P2 (enjambre §2.4/§2.6/§3.1.1), WORKPLAN §4.8 (42 confluencias — NO se infla).

---

## §0 — Respuesta a la pregunta abierta (§7 del dossier): la fuente única de verdad

**Decisión de arquitectura: la doctrina se escribe UNA vez como tabla normativa (§2 de este doc → destino final `docs/reglas-smc-ict.md §7`), y NADIE la re-implementa: todos los consumidores leen DERIVACIONES calculadas por el CORE.**

La doctrina "leer atrás + proyectar adelante bajo confluencia" se reduce a **tres primitivos calculables** por instancia detectada:

| Primitivo | Qué codifica | Dominio |
|---|---|---|
| `posRole` | posición estructural: ¿está en un **GIRO** (pivote HH/LL que produjo BOS/CHoCH), en el **ORIGEN** de un desplazamiento que rompió estructura, o es **INTERNO** (media tendencia)? | `{0=INTERNO, 1=GIRO, 2=ORIGEN}` |
| `confDegree` | confluencia: nº de **familias distintas** con una instancia activa apilada en `±tolConf×ATR` del nivel | `int ≥ 0` |
| `depthBand` | profundidad de proyección: en qué **banda de retroceso** del dealing range vigente cae (1=corta, 2=media, 3=origen; 4/5=rangos previos, "más atrás") | `{1..5}` |

Con esos tres primitivos + el `strength` ya existente (ADR-014), los **cuatro consumidores** derivan sin duplicar:

```
                    DOCTRINA (tabla normativa §2 — texto, una sola vez)
                                      │  se implementa como
                    CORE: strength (ya) + posRole + confDegree + depthBand
                    (funciones puras, al cierre, byte-idénticas Visual/Strategy)
        ┌───────────────┬─────────────────────┬───────────────────┬──────────────────┐
 (1) RENDER Pine   (2) SCORE direccional  (3) CUADERNO EA    (4) DEBATE enjambre
 Visual: score_render  Strategy/F2: los     MQL5: serializa    agentes LEEN el
 v2 + bandas de        MISMOS booleanos     los niveles con    snapshot (ADR-012)
 profundidad (§3)      §4.8 evaluados en    sus primitivos     con primitivos ya
 elige QUÉ dibujar     el nivel = el        (§6) — traducción  incluidos — razonan,
                       apilamiento que      1:1 del CORE       NO recalculan (§0.8)
                       Visual resalta (§4)  (Fase 4)
```

**Por qué esto no se duplica:**
1. **Render y score comparten el apilamiento.** `confDegree` de una instancia ES el conteo de las mismas condiciones de zona/liquidez del catálogo §4.8 (#9, #17–#26) evaluadas a ese nivel. Lo que el chart resalta y lo que el score suma son la misma lectura — no dos métricas paralelas.
2. **Los agentes no miden nada.** ADR-012 ya fija snapshot determinista leído del Pine; este esqueleto solo AMPLÍA el snapshot para que cada nivel viaje con `posRole/confDegree/depthBand/proyección` (§5). El protocolo de proyección del agente es razonamiento sobre datos ya calculados.
3. **El EA es traducción, no reinterpretación.** El cuaderno (§6) es la serialización runtime de las mismas funciones CORE traducidas 1:1 (MQL5-PLAN §3, golden tests).
4. **El outcome cierra el ciclo en un solo sitio.** La "proyección verificable" (§4.3) se mide con UNA definición de exactitud (§7.2), que sirve igual para calibrar pesos (Fase 3) y para el darwinismo del enjambre (F).

**Frontera CORE/Visual (mismo criterio ADR-014):** `posRole`, `confDegree` y `depthBand` son propiedades de **detección/lectura del mercado** con dos consumidores (Visual ordena tinta; Strategy modula score; el EA los traduce) → pertenecen al CORE. PERO se implementan en **dos fases** para no tocar el CORE antes de la firma del F1-GATE: primero una aproximación **Visual-only** (los cálculos viven en Visual leyendo los arrays del CORE, §3.6 fase A), y al abrir Fase 2 se **promueven al CORE** con un ADR breve + SHA nuevo (§3.6 fase B). La fase A no crea deuda: las fórmulas de A y B son la misma; solo cambia el archivo donde viven.

---

## §1 — Principios (axiomas de esta capa; suman a los §1 del esqueleto visual)

1. **Backward-read → forward-projection → outcome.** Toda instancia se lee en tres tiempos: qué la causó (contexto estructural atrás), qué escenario proyecta (dónde reaccionará el precio / a qué draw apunta), y qué pasó de verdad (outcome verificable). El sistema entero — tinta, score, agente, EA — habla en ese formato.
2. **La importancia es posición × apilamiento, no distancia.** `posRole` y `confDegree` mandan; la cercanía al precio SOLO desempata dentro de una banda de profundidad. Lo interno se detecta y se cuenta (panel T14), no se resalta.
3. **"3 por lado" = MÍNIMO de escenarios de profundidad, no cap.** Un representante por banda de retroceso (corta / media / origen). El usuario puede pedir el 4.º/5.º **más atrás en el tiempo** con un input de profundidad (`i_profundidad`, §3.3). No es "los 3 más fuertes": es "el mejor de cada profundidad".
4. **Los draws lejanos con confluencia NO se recortan.** El rango P/D D1 es contexto para razonar premium/discount, no una tijera. Un pool/EQ/old-high fuera del rango se mantiene si es objetivo de proyección (regla del guardián de draws, §3.4). Corrige el "adiós al BSL 1.51".
5. **Granularidad por variación, no por familia.** FVG ≠ trueFVG ≠ IFVG ≠ BPR: misma familia (hue, capa), doctrina distinta (qué caso importa). La tabla §2 baja a ese grano.
6. **Nada nuevo suma al catálogo §4.8.** `posRole/confDegree/depthBand` son moduladores/lecturas, no confluencias #53+ (mismo argumento que ADR-014 §3 para `strength`). El conteo 42 (+expansiones ya aprobadas) no cambia.
7. **Buscar confluencias = buscar patrones.** El agente/EA no pregunta "¿qué hay cerca?" sino "¿dónde se apila?": los niveles con `confDegree ≥ 2` son los candidatos de proyección por defecto.

---

## §2 — ENTREGABLE A · Doctrina por concepto/variación (40 fichas)

> **Template por entrada:** *Significa* · *Dónde vive* (capa §3 del esqueleto visual / TF natural) · *Qué casos importan* (posRole requerido + confluencia + profundidad) · *MTF* · *Modo mínimo*. Los casos que NO cumplen su criterio se detectan igual (arrays + panel), pero no reciben tinta en Operación.
> **Convención de profundidad:** "por lado × banda" = un representante por banda 1/2/3 arriba y abajo del precio (§3.3). "n/a" = concepto no bandeado (eventos puntuales, marcos).
> Esta tabla es la **fuente normativa**; al rellenarse (gate sprint16) cada fila migra a `docs/reglas-smc-ict.md §7` con sus umbrales cuantificados + casos EURUSD.

### A1 · Estructura (`GRP_STRUCT`, capa L3, teal/rojo)

| # | Concepto | Significa | Qué casos importan | MTF | Modo mín. |
|---|---|---|---|---|---|
| 1 | Swing interno | pivote menor dentro de una pierna | ninguno en tinta: alimenta detección (IDM, legs). Solo panel/Todo | no baja | Todo |
| 2 | Swing dominante HH/HL/LH/LL | pivote del tramo que define el bias | SOLO los de **GIRO** (el HH/LL donde se tomó liquidez y el precio se desplazó al lado contrario) — no la traza completa. 1 por banda de profundidad por lado (los 3 giros que estructuran el rango) | el giro dominante D1 baja a H1/M5 (ya, §7.4) | Estudio (labels) / el giro vigente en Operación |
| 3 | BOS (interno) | continuación en estructura menor | nunca en Operación; Estudio si `strength` alta | no baja | Estudio |
| 4 | BOS (swing/dominante `+`) | continuación confirmada del bias | el **vigente** + el que abrió la pierna actual (su origen = ancla del OB causal). posRole=ORIGEN implícito | hereda SIEMPRE con tag (ya) | Operación |
| 5 | CHoCH | primer quiebre contra-tendencia (aviso de giro) | el **vigente** (define el posible giro en curso). Históricos → Estudio | hereda (ya) | Operación |
| 6 | CHoCH-MSS | giro validado con displacement | el vigente SIEMPRE (es EL evento de giro; posRole=GIRO por definición) | hereda (ya) | Operación |
| 7 | Flip | zona S/R invertida tras quiebre | solo el flip en un GIRO con `confDegree≥1` (flip+OB o flip+FVG). Internos → panel | baja solo Primario (ya) | Operación (P) |

### A2 · Order Blocks (`GRP_OB`, capa L2, azul)

| # | Concepto | Significa | Qué casos importan | MTF | Modo mín. |
|---|---|---|---|---|---|
| 8 | OB | última vela contraria antes del desplazamiento (origen institucional) | el que **originó la ruptura de estructura** (posRole=ORIGEN) por lado: demanda abajo / oferta arriba, **1 por banda de profundidad** (mín. 3/lado disponibles, Operación dibuja el de cada banda activa). Activo (no mitigado). Los internos → Estudio | D1 primarios heredan (ya); nativos se SUMAN a lo heredado | Operación |
| 9 | OB-propulsión `⇈` | OB que relanzó el movimiento sin mitigarse | no es entrada aparte: eleva `strength` del OB base + glifo (ya decidido F3). Prioriza al OB dentro de su banda | sigue al OB | Operación (glifo) |
| 10 | Breaker | OB fallado → S/R invertido | el breaker del **GIRO vigente** (el OB que falló al girar la estructura es la zona de re-test canónica). 1/lado | hereda si Primario | Operación |
| 11 | Mitigation Block | bloque mitigado que aún actúa | solo con `confDegree≥2` (apilado con FVG/pool); si no → Estudio | no baja | Estudio |
| 12 | Vacuum | hueco de liquidez tras gap | contexto de paso (el precio lo cruza rápido): panel + Estudio | no baja | Estudio |
| 13 | Rejection block | mechas de rechazo en extremo | solo en el HH/LL de GIRO (es la variante de OB del extremo). Internos nunca | no baja | Estudio |

### A3 · FVG (`GRP_FVG`, capa L2, naranja)

| # | Concepto | Significa | Qué casos importan | MTF | Modo mín. |
|---|---|---|---|---|---|
| 14 | FVG | imbalance de 3 velas a rebalancear | el FVG del **desplazamiento que rompió acumulación+estructura** (posRole=ORIGEN, normalmente coincide con `trueFvg`) — es donde REACCIONA. 1 por banda por lado. Los micro-internos = draws de paso → panel/Estudio | D1/H1 heredan (ya); nativos se suman | Operación |
| 15 | trueFVG (displacement) | FVG con displacement validado | flag que eleva `strength` (ya) y **satisface por sí solo el criterio ORIGEN** del FVG base. No entrada aparte | sigue al FVG | Operación (implícito) |
| 16 | gradedFVG `·g` | FVG validado por gradient (T43) | flag: eleva strength + refina #18/#20 (ya, ADR-013). Sin tinta propia | sigue al FVG | — |
| 17 | IFVG (invertida) | FVG violado que invierte su rol | SOLO el que calza con el **inicio del swing**: el FVG generado antes del OB / antes de formarse el LL cuando el precio venía cayendo y va a girar (posRole=GIRO, `confDegree≥1` con el OB/estructura del giro). Los IFVG de media tendencia → Estudio | hereda si Primario | Operación |
| 18 | BPR | solape de FVGs opuestos (balanced price range) | el BPR en el ORIGEN de la pierna vigente o con `confDegree≥2`; resto Estudio (doctrina madre-2026: PD-array defensiva) | hereda si Primario | Estudio (P sube a Operación con confluencia) |
| 19 | VI (volume imbalance) | gap entre cuerpos con mechas solapadas | micro-concepto: refina el nivel exacto dentro de una zona ya importante (`confDegree` del padre). Nunca solo | no baja | Todo |
| 20 | IPR | rango de precio institucional | micro: solo Todo/panel | no baja | Todo |

### A4 · Liquidez (`GRP_LIQ`+`GRP_EQHL`, capa L3, violeta)

| # | Concepto | Significa | Qué casos importan | MTF | Modo mín. |
|---|---|---|---|---|---|
| 21 | Pool BSL/SSL vivo | liquidez en reposo = candidato a draw | el **draw del bias** (objetivo, ancla) + los pools en extremos del marco D1/H1 a cualquier distancia — **guardián de draws §3.4: un pool lejano con `confDegree≥2` o alineado al bias NO se recorta por rango** (el BSL 1.51 vive) | across D1/H1/M5 (ya) | Operación |
| 22 | Pool objetivo | el draw activo de la proyección vigente | ancla SIEMPRE (§2.3 esqueleto visual, ya) | sí | Operación |
| 23 | Pool barrido | historial de liquidez tomada | contexto de lectura atrás (¿ya liquidaron?): Estudio; el ÚLTIMO barrido relevante alimenta posRole=GIRO de otros conceptos | no | Estudio |
| 24 | Sweep/Raid/Grab | toma de liquidez (mecha+cierre de vuelta) | el sweep en el **HH/LL que antecede el giro** al lado contrario (posRole=GIRO). Internos → panel | el del extremo operativo | Operación (último) |
| 25 | IDM (inducement) | trampa previa a la zona real | el que **custodia el extremo operativo** (entre el precio y la zona de reacción del giro): es el "primer escenario" de profundidad. Top por lado por banda 1–2 | nativo (no baja) | Operación (sube de Estudio+ — decisión S092) |
| 26 | Judas | barrido falso de apertura de sesión | el de la sesión activa, solo fresco | no baja | Estudio |
| 27 | EQH/EQL | liquidez obvia (doble techo/suelo) | los que están en un **HH/LL de GIRO** donde se toma liquidez y hay desplazamiento; si hay 3 ciclos, importan los 3 EQ de los giros significativos (1 por banda). Media tendencia neutra → panel | heredan si Primarios (ya, cuadre §7.3-b) | Operación |

### A5 · Premium/Discount + Gradient (`GRP_PD`/`GRP_GRAD`, capa L1, marco)

| # | Concepto | Significa | Qué casos importan | MTF | Modo mín. |
|---|---|---|---|---|---|
| 28 | P/D + EQ | mitades del dealing range vigente | ancla SIEMPRE (marco §2.3). Es **contexto de razonamiento** (dónde comprar/vender barato/caro), JAMÁS filtro de recorte de draws | 3 líneas D1 rotuladas en LTF (ya) | Operación |
| 29 | Quadrants LQ/EQ/UQ | cuartos del rango | líneas del marco (ya) — dan el `depthBand` visualmente | grid global (ya) | Operación |
| 30 | Eighths 1/8–7/8 | octavos | afinado de Estudio (ya) | ídem | Estudio |
| 31 | OTE / Golden Pocket | zona de retroceso óptimo 0.62–0.79 | solo con pierna activa alineada al bias (ya); coincide con banda 2–3 → sube `confDegree` de las zonas que caen dentro | no baja (panel indica OTE D1) | Operación (activo) |

### A6 · Gaps de apertura (capa L2, naranja)

| # | Concepto | Significa | Qué casos importan | MTF | Modo mín. |
|---|---|---|---|---|---|
| 32 | NWOG | gap de apertura semanal | zona-referencia recurrente: la más cercana por lado si `confDegree≥1`; resto panel | gaps D1 heredan si Primarios (ya) | Estudio (P sube con confluencia) |
| 33 | NDOG | gap de apertura diaria | ídem NWOG, ventana más corta | ídem | Estudio |
| 34 | NYMO | apertura NY midnight | nivel de referencia intradía en KZ activa | no | Estudio |
| 35 | BAG (breakaway) | gap que NO se rellena (expansión) | señal de displacement: eleva strength/posRole=ORIGEN de las zonas de su pierna; tinta propia solo Estudio | no | Estudio |

### A7 · Contexto (`GRP_CTX`/`GRP_KZ`, capas L0/L1/L3)

| # | Concepto | Significa | Qué casos importan | MTF | Modo mín. |
|---|---|---|---|---|---|
| 36 | EMAs 20/50/200 (rebote/cruce/stack) | tendencia media | líneas tenues (ya); eventos solo panel. NO participan en posRole/confDegree (son confluencias #37–42 propias) | no baja | Estudio (eventos) |
| 37 | Kill Zones + macros | ventanas temporales de manipulación | ribbon (ya); una zona tocada DENTRO de KZ activa no cambia su tinta (el tiempo va al score #34, no al chart) | no (ribbon local) | Operación (ribbon) |
| 38 | Displacement | vela(s) de expansión institucional | no tiene tinta propia: ES el certificador de posRole=ORIGEN (y de trueFVG/MSS) | implícito | — (panel) |
| 39 | Legs IMP/CORR + Inside Day + CISD | fase de la pierna / compresión / cambio en delivery | lectura de contexto: leg vigente define qué lado se proyecta; CISD solo fresco+GIRO (Estudio) | no baja | Estudio |
| 40 | Std-Dev + SMT | proyecciones de desviación / divergencia entre pares | herramientas de proyección del agente (targets banda 4–5) y confluencia inter-símbolo (SMT, futuro multi-par) — panel/Estudio, sin tinta en Operación | no | Estudio |

> **Regla transversal de la tabla:** cuando una fila dice "sube a Operación con confluencia", el mecanismo es único: `confDegree ≥ 2` fuerza nivel visual ≥ Secundario aunque la familia sea de Estudio (la confluencia promociona, nunca degrada). `[impl]` §3.5-d.

---

## §3 — ENTREGABLE B · Mecánica de selección Pine/Visual

> Todo en `pine/SMC-Visual.pine` (fase A). Reutiliza: `f_renderScore` (:2723), bloque de anclas (:2732), patrón registrar→recortar-en-`islast` (:3001/:3076), desalojo §6.5 (:2759), buffers MTF ADR-009/010, `f_famOK`/`f_densOK`/`f_visualLevel` (:2712-2720). RE10045-safe: **cero `array.push` en rutas de dibujo MTF; toda la selección con escalares best-per-band o el patrón registrar/recortar ya probado.**

### §3.1 `score_render` v2 (la llave nueva — sustituye fuerza×cercanía)

```
score_render_v2 = strength × wPos(posRole) × (1 + kConf × min(confDegree, 3))
   wPos: ORIGEN=1.0 · GIRO=0.9 · INTERNO=0.35          (cand. CONGELADO)
   kConf = 0.25                                          (cand. CONGELADO)
   La cercanía NO entra en la llave: la profundidad ya la codifica depthBand.
   Tie-break dentro de una banda: mayor strength; a igualdad, más fresco.
```

`[impl B-1]` — `f_renderScoreV2(float strength, int posRole, int confDegree)` en Visual (junto a `f_renderScore`, que se CONSERVA para las anclas §2.3 hasta migrarlas — no regresar lo aprobado). Cuerpo TODO.

### §3.2 Primitivos (fase A: Visual; fase B: CORE)

`[impl B-2]` — `f_posRole(top, bot, barIdx)` → 0/1/2. Lectura de arrays existentes, sin detección nueva:
- **GIRO:** la zona/nivel se solapa (±`tolPos×ATR`, cand. 0.5) con un swing dominante que fue seguido de CHoCH/MSS o de sweep contrario (`SMC_swings` + `SMC_eventsMajor` + sweeps ya detectados).
- **ORIGEN:** la zona nace en el arranque de la pierna cuyo desplazamiento produjo el BOS/CHoCH vigente (compara `barIdx` de la zona con el origen del evento — ambos ya viajan en los UDTs/eventos).
- **INTERNO:** resto. TODO: casos borde (zona que es giro Y origen → ORIGEN gana).

`[impl B-3]` — `f_confDegree(level)` → int. Cuenta familias distintas con instancia **activa** en `±tolConf×ATR` (cand. 0.25 = `labelClusterTol` §6.2 — misma tolerancia, deliberado: el cluster de labels y el apilamiento son el mismo fenómeno). Familias contadas: OB/Breaker, FVG/IFVG/BPR, pool, EQH/EQL, IDM, gap, OTE-zona. Se calcula SOLO en `islast` y SOLO para los candidatos finalistas (O(candidatos×arrays), acotado) — no por vela. Sin arrays nuevos (contador int por candidato).

`[impl B-4]` — `f_depthBand(level, px)` → 1..5. Sobre el dealing range vigente (origen de la pierna dominante → extremo, ya disponible vía P/D):
- banda 1 = retroceso [0, 0.33] desde el precio hacia el origen (escenario corto: toca y sigue)
- banda 2 = (0.33, 0.66] (retroceso medio)
- banda 3 = (0.66, 1.0] (el origen / inducement inicial: soporte último)
- bandas 4/5 = **fuera del rango vigente, más atrás en el tiempo**: niveles del dealing range previo (banda 4) y del anterior (banda 5). TODO: cómo identificar los 2 rangos previos sin arrays nuevos (candidato: escalares que se archivan al rotar el rango, como los grids P3).

### §3.3 Input de profundidad (el "ver más atrás" bajo demanda)

`[impl B-5]` — `i_profundidad = input.int(3, "Profundidad de proyección (bandas por lado)", minval=3, maxval=5, group=GRP_DENS)`. Default 3 = el mínimo doctrinal; 4/5 habilitan las bandas de rangos previos. Aplica por concepto bandeado (OB, FVG, EQH/EQL, swings-giro). NO es un cap de calidad: es alcance temporal/espacial de la proyección.

### §3.4 Guardián de draws (NO recortar lejanos con confluencia)

`[impl B-6]` — regla de excepción en los recortes (top-N, desalojo §6.5, curado MTF S091): una instancia con `confDegree ≥ 2`, o un pool alineado al bias como draw, es **inmune al recorte por distancia/frescura** (se trata como mandatoria, mismo rango que anclas/MTF en el §6.5). El desalojo compensa cortando más INTERNO discrecional. TODO: verificar que `f_mtfLblYield`/`eventCap` reserven hueco para estas mandatorias nuevas.

### §3.5 Selección por bandas (generaliza el ancla §2.3 a top-por-banda por lado por concepto)

`[impl B-7]` — extender el bloque `islast` de anclas (:2732): en la misma pasada O(n) sobre `SMC_zones`, rastrear **por concepto (OB/FVG/Breaker/IDM) × lado (hi/lo) × banda (1..i_profundidad)** el mejor `score_render_v2`, guardando ÍNDICE por celda. Son ≤ 4×2×5 = 40 escalares int (sin arrays → RE10045-safe; mismo estilo que `anchorHiIdx`). Los drawers comparan su `i` contra la celda → `isBandPick` → dibuja aunque `f_densOK` diga no:
- a. OB (:3488): gate `… or isBandPick` — cubre el "2 nativos/lado" de S092 y lo mejora (2→uno por banda activa).
- b. FVG (:3715): ídem; línea CE solo en el pick de banda 1 (el más operable).
- c. Breaker (:3520): top-1/lado (banda del giro).
- d. Promoción por confluencia (§2 regla transversal): `confDegree≥2` fuerza dibujo aun en familias de Estudio. TODO: orden de evaluación con `f_famOK` (la promoción va DESPUÉS del whitelist §8.2 — la matriz por modo se respeta salvo esta única excepción documentada).
- e. IDM (:3211): top por lado bandas 1–2 en Operación (sale de `f_famOK(FAM_EST)`), reemplazando el cap por recencia `i_maxShowIDM` en ese modo.
- f. Estructura/EQ: los recortes `STRUCT_OP_CAP`/`EQ_OP_CAP` pasan de "más recientes" a "mejor `score_render_v2` por banda" (patrón registrar→recortar intacto, cambia la llave del recorte).

### §3.6 Secuencia de implementación (un commit = un concepto; gates completos)

| Paso | Pieza | Toca | Gate |
|---|---|---|---|
| A-1 | `f_depthBand` + `i_profundidad` (bandas 1–3; 4–5 stub) | Visual | 0/0 + core-sync |
| A-2 | `f_posRole` (lectura de swings/eventos existentes) | Visual | 0/0 + casos EURUSD (sprint16) |
| A-3 | `f_confDegree` (solo finalistas en `islast`) | Visual | 0/0 + budget vivo sin crash (RE10045) |
| A-4 | `f_renderScoreV2` + selección top-por-banda OB/FVG (§3.5-a/b) | Visual | 0/0 + checklist §10 #1–#3 + vivo D1/H1/M5 |
| A-5 | Breaker + IDM + promoción por confluencia (§3.5-c/d/e) | Visual | ídem |
| A-6 | Guardián de draws + reserva en desalojo §6.5 (§3.4) | Visual | §10-#8 (nada desaparece en silencio) + caso BSL 1.51 |
| A-7 | Estructura/EQ re-llaveados (§3.5-f) + bandas 4/5 | Visual | ídem + firma usuario (cierra la parte visual) |
| B-1 | ADR-01X: promover `posRole/confDegree/depthBand` al CORE (UDT + funciones puras al cierre) | **CORE** | 0/0 ×3 + core-sync + SHA nuevo + golden refs |
| B-2 | Strategy consume los primitivos en `f_scoreConfluences` (§4) | Strategy/F2-T01 | gate Fase 2 |

> Pasos A-* son post-firma F1 o negociables con el usuario como parte del afinado del gate (el plan S092 de top-N 2/lado es un SUBCONJUNTO de A-4 — puede implementarse primero tal cual está aprobado y A-4 lo generaliza después). Paso B-* abre Fase 2.

---

## §4 — ENTREGABLE C · Lógica de SCORE (visual ↔ Fase 2 ↔ EA)

### §4.1 La identidad central
**La importancia visual ES el score de confluencia direccional leído a un nivel.** No hay dos métricas: cuando el precio está EN un nivel, las confluencias de zona/liquidez del §4.8 que se activan (#9 pool objetivo, #17–#21 en OB/FVG, #22 breaker, #26 CE, #33 IDM…) son exactamente las familias que `confDegree` contó al apilar. Formalmente:

```
scoreDir(nivel) ≈ Σ pesos(confluencias §4.8 activas en ese nivel, direccionales)
confDegree(nivel) = |familias apiladas|            (la versión sin pesos, para render)
```
Visual usa el conteo (rápido, sin pesos → nada que calibrar antes de Fase 3); Strategy usa la suma ponderada. Misma vecindad `±tolConf×ATR`, mismos arrays, misma dirección. `[impl C-1]` — en F2-T01, `f_scoreConfluences` recibe los primitivos del CORE y NO re-detecta vecindades (una sola función de apilamiento compartida).

### §4.2 Moduladores (sin inflar el catálogo)
`posRole` y `depthBand` NO son confluencias: **modulan el peso** de las de zona (mismo estatus que `strength`, ADR-014 §3): una confluencia #17 "en OB" en posRole=ORIGEN pesa más que la misma en INTERNO. Forma candidata (CONGELADA): `peso_efectivo = peso_base × wPos × g(strength)`. Compatible con el multiplicador gradient ADR-013 (se aplican en cascada: aditivo modulado → × gradientBonus).

### §4.3 Proyección verificable (el score deja de ser estático)
Cada señal/nivel resaltado define implícitamente una **proyección**: `{nivel, dirección esperada de la reacción, draw objetivo, invalidación}`. El outcome es medible sin ambigüedad:

```
REACCIONÓ  si el precio entró en ±tolConf×ATR del nivel y se desplazó ≥ kReact×ATR
           (cand. 1.0) en la dirección proyectada antes de cerrar más allá de la
           invalidación (el extremo opuesto de la zona / el nivel de invalidación ADR-012 Q).
FALLÓ      si cerró más allá de la invalidación sin la reacción.
PENDIENTE  mientras no toque.
```
`[impl C-2]` — Fase 3: el CSV de backtest registra por señal las confluencias activas + posRole/depthBand + outcome de reacción → `smc-backtesting-analyst` calcula **lift por confluencia condicionado a posición estructural** → pesos v2. Es el mismo pipeline F3 ya planeado; solo se enriquece el registro. La retroalimentación de pesos es OFFLINE (IS/OOS), nunca auto-ajuste en vivo (ADR-002).

### §4.4 Qué NO cambia
Threshold direccional, scoreLong/scoreShort separados, R:R≥1:3, señal solo en vela confirmada, 42+expansiones aprobadas — intactos. Este entregable solo fija DE DÓNDE salen los pesos efectivos y CÓMO se auditan.

---

## §5 — ENTREGABLE D · Protocolo de pensamiento del agente (extiende ADR-012)

ADR-012 se **conserva íntegro** (snapshot determinista multi-TF, 7 preguntas, contrato ESPERAR/ENTRAR/DESCARTAR). Este esqueleto añade dos piezas:

### §5.1 Snapshot enriquecido (el Vigía transporta los primitivos)
`[impl D-1]` — el YAML del snapshot (PROTOCOLO-razonamiento-agente §1.2) añade por cada nivel/zona: `posRole`, `confDegree`, `depthBand`, `strength(glifo)`, `estado`. Fuente: los MISMOS labels/tablas Pine (los glifos y tags ya viajan; los primitivos nuevos se exponen en labels/panel al implementar §3 — cero invención, regla ADR-012 §1).

### §5.2 La "lectura de dos tiempos" por concepto (sub-rutina de Q1–Q2)
Antes de responder Q1 (¿la zona importa?) y Q2 (draw), el agente ejecuta por cada concepto del snapshot este molde común (idéntico para todo el enjambre; la VOZ va en la ficha del mentor):

```
ATRÁS   ¿qué lo causó?      → posRole del snapshot + narrativa (qué liquidez se tomó,
                              qué estructura rompió) — el agente CITA, no mide.
APILADO ¿con qué confluye?  → confDegree + lista de familias apiladas.
ADELANTE proyección          → escenario por banda: si el precio retrocede a banda 1
                              ¿reacciona y sigue?; si perfora, banda 2; soporte último
                              banda 3. Cada escenario con {gatillo, invalida, objetivo}.
```
La salida alimenta directamente el campo `proyeccion{gatillo, invalida, objetivo}` del voto extendido (ADR-012 §3) — **una proyección por banda considerada**, no una sola. `[impl D-2]` — actualizar `PLANTILLA-agente-mentor.md §C` + el prompt de ronda 1 (ESQUELETO-P2 §2.3) con el molde; validar contra el formato real del Kanban.

### §5.3 Qué sigue prohibido
Recalcular confluencias (§0.8), inventar niveles, proyectar sin gatillo+invalidación medibles (voto inválido). El agente razona sobre las bandas/roles del sistema; su valor añadido es la NARRATIVA y la elección de escenario, no la medición.

---

## §6 — ENTREGABLE E · Cuaderno de confluencias del agente decisor MT5

El cuaderno es la **serialización runtime de la doctrina** en el EA (Fase 4): un estado estructurado por símbolo, reconstruible cada vela desde las funciones CORE traducidas (MQL5-PLAN §3). No es un log de texto: es el insumo del razonamiento del EA (ADR-007: el EA razona confluencias) y su rastro auditable.

### §6.1 Formato (candidato — struct MQL5 `SMC_Cuaderno`, volcado a JSON por vela de decisión)

```yaml
cuaderno:
  simbolo: EURUSD          # símbolo-agnóstico: todo ×ATR
  contexto:                # LECTURA ATRÁS (backward-read)
    bias: {D1: alcista, H1: alcista, M5: correctivo}
    estructura_vigente: {evento: MSS, tf: H1, nivel: x, posRole: GIRO}
    dealing_range: {origen: x, extremo: y, pd: discount, banda_precio: 2}
    ultima_liquidez: {tipo: SSL_sweep, nivel: x, barras: n}
  niveles:                 # PROYECCIÓN ADELANTE — por lado, por banda
    abajo: [ {banda: 1, nivel: x, conceptos: [OB, FVG], posRole: ORIGEN,
              confDegree: 3, strength: 0.8, proyeccion: {reaccion: alcista,
              objetivo: BSL_y, invalida: z}, estado: pendiente}, … ]
    arriba: [ … ]
  draws: [ {nivel: y, tipo: BSL, alineado_bias: true, fuera_de_rango: true} ]
  proyecciones_abiertas:   # OUTCOME — el ciclo verificable
    - {id, nivel, emitida_en, gatillo, invalida, objetivo, estado: pendiente|reacciono|fallo}
  score: {long: n, short: m, threshold: t, rr_calculable: bool}
```

### §6.2 Cómo consume B/C
- Los `niveles` salen de la MISMA selección por bandas (§3.5) traducida — el cuaderno del EA y el chart del Visual muestran los mismos picks (golden test de paridad natural en Fase 4).
- La decisión usa **pasado+futuro**: entra solo si el nivel tocado tiene posRole∈{GIRO,ORIGEN}, `scoreDir ≥ threshold` (§4), un draw objetivo identificado que dé R:R≥1:3, y ninguna proyección contraria de mayor banda sin resolver.
- `proyecciones_abiertas` implementa el outcome (§4.3) en runtime: el EA marca reaccionó/falló al cierre de cada vela → alimenta los logs de Fase 5 (re-calibración por símbolo).
- `[impl E-1]` — MQL5-PLAN §3: añadir fila de mapeo `f_posRole/f_confDegree/f_depthBand → SMC_Contexto.mqh` + módulo `SMC_Cuaderno.mqh` (solo serialización, cero detección propia). `[impl E-2]` — formato JSON exacto + rotación de archivos (1/día).

---

## §7 — ENTREGABLE F · Debate del enjambre + evolución darwiniana por exactitud de proyección

Encaja con ESQUELETO-P2: confluencia no consenso (§3.1.1), olas de 3 (§2.10), track-record §2.6, votos ponderados §2.4, TV como árbitro. Se añade UNA métrica y su cableado:

### §7.1 El debate entrega PROYECCIONES, no opiniones
Cada agente de la ola responde el molde §5.2 y su voto extendido incluye ≥1 proyección `{nivel, dirección, objetivo, gatillo, invalida, banda}` (ya obligatorio para ESPERAR en ADR-012; se generaliza: TODA postura lleva proyección — también DESCARTAR proyecta "no reaccionará ahí"). El Supervisor de Confluencia consolida por **niveles**, no por direcciones sueltas: dos agentes que señalan el mismo nivel±tolConf×ATR con la misma reacción esperada = confluencia de proyección (más fuerte que coincidir en "alcista").

### §7.2 Exactitud de proyección (la métrica darwiniana — candidata CONGELADA)

Al resolverse el outcome (§4.3; el Vigía/árbitro lo lee del gráfico, ESQUELETO-P2 §2.6):

```
exactitud = wDir·hitDireccion + wNivel·(1 − min(|nivelProyectado − nivelReaccionReal| / ATR_tf, 1)) + wObj·hitObjetivo
  hitDireccion ∈ {0,1}: el precio reaccionó en la dirección proyectada
  nivelReaccionReal: el extremo de la vela/cluster donde giró (leído del Pine, no estimado)
  hitObjetivo ∈ {0, 0.5, 1}: alcanzó el draw / a medias (≥50% del trayecto) / no
  wDir=0.4 · wNivel=0.4 · wObj=0.2                       (cand. CONGELADO)
  FALLÓ (invalidación) ⇒ exactitud = 0. PENDIENTE no puntúa (sin autoadjudicación).
```

### §7.3 Evolución del score del agente
`score_agente ← EMA(exactitud, α cand. 0.1)` con **muestra mínima** (cand. 20 proyecciones resueltas) antes de ponderar votos — resuelve el `[impl]` abierto de §2.6 ("fórmula de ponderación por desempeño + tamaño mínimo"). El score pondera el voto en el Supervisor (§2.4) y decide la poda darwiniana (§3.1.1: el que no aporta, se saca; el de mayor exactitud sostenida sube). Registro: columnas nuevas en el JSONL de track-record (`nivelProy, nivelReal, banda, exactitud`). `[impl F-1]` — ampliar `docs/laboratorio/` (schema JSONL + script de resolución de proyecciones abiertas del Vigía, que ya está `[impl]` en ADR-012). `[impl F-2]` — anti-gaming: proyecciones triviales (banda 1 pegada al precio con gatillo laxo) puntúan con `wObj` reforzado — TODO definir el ajuste exacto al rellenar.

---

## §8 — Cumplimiento de restricciones (dossier §6)

| Restricción | Cómo la cumple |
|---|---|
| CORE byte-idéntico | Fase A 100% Visual (SHA intacto); fase B toca CORE con ADR + core-sync + SHA nuevo, DESPUÉS de la firma F1 |
| Frontera ADR-014 | primitivos = detección → CORE (fase B); selección/tinta/bandas-de-render → Visual |
| Anti-repaint | posRole/confDegree/depthBand se calculan sobre instancias confirmadas al cierre; la selección en `islast` solo elige tinta (no crea eventos) |
| RE10045-safe | selección por celdas escalares (≤40 ints), confDegree con contador int, cero `array.push` en rutas MTF |
| Símbolo-agnóstico | tolConf/tolPos/kReact/bandas todo ×ATR o fracción de rango |
| No inflar las 42 | posRole/confDegree/depthBand = moduladores/lecturas (mismo estatus que strength, ADR-014 §3) |
| Congelados Fase 3 | §9 |
| Gate sprint16 | cada ficha §2 migra a reglas-smc-ict §7 cuantificada + casos EURUSD ANTES de codificar su selección |

## §9 — Congelados explícitos (ADR-002)
`wPos {1.0/0.9/0.35}` · `kConf 0.25` · `tolConf 0.25×ATR` · `tolPos 0.5×ATR` · bandas `{0.33/0.66/1.0}` · `i_profundidad default 3, max 5` · `kReact 1.0×ATR` · `exactitud {0.4/0.4/0.2}` · `EMA α 0.1` · muestra mínima 20 · promoción `confDegree≥2`. Se calibran en Fase 3 (IS/OOS) y Fase 5 (por símbolo).

---

*Fin del esqueleto. Siguiente paso: (1) el plan S092 de top-N 2/lado se implementa tal cual está aprobado (subconjunto de A-4); (2) las fichas §2 se cuantifican bajo sprint16; (3) los pasos §3.6 A-1…A-7 corren post-firma F1; (4) B-1/B-2 abren Fase 2 con el ADR de promoción al CORE.*
