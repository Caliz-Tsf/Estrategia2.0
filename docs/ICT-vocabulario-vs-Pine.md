# ICT — Vocabulario maestro vs Pine (qué falta agregar)

> **Qué es esto.** Documento-puente entre el **módulo MENTOR ICT** (5 cursos leídos íntegros: 2022 · MMP · OTE · 2024 · 2026) y el **sistema Pine** (`pine/SMC-*.pine` + `docs/reglas-smc-ict.md`). Inventaría TODO el vocabulario/conceptos que ICT entregó y lo cruza con lo que el Pine YA tiene, para decidir qué falta.
>
> **Cómo se usa (decisión usuario S074).** Este maestro lista los **FALTA**. Cada FALTA cuantificable se le pasa a **Ultracode** para que genere el **esqueleto de regla** (plantilla §6.0 de `reglas-smc-ict.md`: concepto + definición cuantificada ATR-relativa + parámetros + contraejemplo + casos EURUSD). Luego **rellenamos** la regla y, solo después, se codifica en Pine. **Una tarea por sesión.**
>
> **Gobernanza (innegociable, [[sprint16-gate-reglas-antes-de-codigo]]).** Nada se codifica en Pine sin su regla cuantificada en `reglas-smc-ict.md` (umbrales relativos a ATR + casos EURUSD + contraejemplo). Aquí solo se **clasifica y prioriza**. Anti-doble-conteo `[FIX P-05]`: una variante que *refina* un concepto existente NO suma confluencia nueva, eleva el **peso**.
>
> **Fuentes.** Inventario Pine = constantes `KIND_*` de `SMC-Library.pine` + headers §0–§6 de `reglas-smc-ict.md`. Vocabulario ICT = `Mentores/ict/knowledge/{2022-mentorship,mmp,ote,2024,madre-2026}.md` (§LOG por archivo + tablas vs-Pine de 2024 §106-128 y 2026 ITER2).

## Principio rector (S074) — MARCAR ≠ generar SEÑAL

> **Corrección de fondo (usuario S074).** "No genera señal dura" **NO** es "se descarta". El sistema tiene dos capas distintas y **casi nada se tira**:
>
> 1. **Capa de SEÑAL (motor de decisión):** lo que dispara una entrada con SL/TP. Gobernada por reglas duras — **R:R ≥ 1:3**, **ADR-001** (sin filtro horario duro), determinista. Aquí entran pocos conceptos como *gate*.
> 2. **Capa de MARCA/DIBUJO (lo que el agente VE en la gráfica):** **TODO lo observable se dibuja/etiqueta** para que el enjambre lo lea y lo use como **confluencia** o como **insumo de una decisión posterior**. Un concepto que no genera señal dura igual se MARCA si es observable en precio.
>
> **Regla operativa:** por defecto, **se marca**. Solo se excluye del Pine lo que **no es observable en el chart** (gestión de capital, psicología, datos externos como COT) — y aun eso se **conserva documentado** para el agente-mentor / Fase 4 EA. Nada se pierde.
>
> Por eso la columna **Tipo** incluye `marca/contexto` y `confluencia` como roles de primera clase, no solo `señal/gate`. La antigua etiqueta "NO-ADOPTAR" se reemplaza por **dónde vive** el concepto (marca · confluencia · gate · gestión-EA · externo · mentor).

## Leyenda de estado

| Estado | Significado |
|--------|-------------|
| **YA-EN-PINE** | Existe con regla cuantificada en `reglas-smc-ict.md` + función pura en el CORE. Nada que hacer. |
| **PARCIAL** | El primitivo base existe, pero ICT añade un **refinamiento/grado/gate** que el Pine aún no aplica. → regla de refinamiento (no objeto nuevo). |
| **FALTA** | Concepto no presente. → candidato a esqueleto Ultracode. |
| **NO-ADOPTAR** | Choca con regla dura del proyecto (R:R 1:3, ADR-001) o es discrecional/gestión. Documentado, fuera del Pine. |

**Tipo** (para qué sirve el concepto en el sistema): `zona` (objeto a dibujar/mitigar) · `confluencia` (suma/pondera score direccional) · `filtro/gate` (habilita o veta el setup) · `target` (estimación de objetivo/SL) · `contexto` (nivel/régimen de fondo) · `gestión` (post-entrada, normalmente NO-Pine).

**Alcance** (símbolo): `FX` (aplica a EURUSD/multi-símbolo, ADR-001) · `índice-only` (RTH/futuros US; diferir a perfil índices, Fase 5).

---

## A. Lo que el Pine YA tiene (inventario autoritativo)

> 40 conceptos T01–T40 + MTF, todos con regla cuantificada §1–§5 y constante `KIND_*`. **No re-litigar.** Solo se listan para que las columnas "PARCIAL/FALTA" de abajo sean fieles.

**§1 Estructura:** Swings (`f_detectSwings`) · HH/HL/LH/LL (`f_classifySwing`) · BOS · CHoCH · MSS · Impulso/Corrección.
**§2 Zonas:** Order Block (+mitigación) · FVG (+CE/mean-threshold) · Premium/Discount/Equilibrium · EQH/EQL · OTE/Golden Pocket · Breaker · Rejection · Flip + Mitigation Block.
**§3 Liquidez:** Pools BSL/SSL · Sweep · Grab · Kill Zones · Judas Swing · IDM/Inducement · False Breakout/Spring/Raid.
**§4 Contexto/EMAs:** Displacement · Session Opens · EMAs (estado/cruce/rebote/stack) · Impulsive/Corrective.
**§5 GAP ICT (T26–T40):** True FVG · **IFVG (inversion)** · **BPR** · Immediate Rebalance · Volume Imbalance (+SIVI/BIVI) · CISD · Vacuum Block · **Propulsion Block** · IPR · **Opening Gaps NWOG/NDOG/NYMO/ORG + Breakaway** · Standard Deviation (proyección) · Inside Day · **SMT Divergence** · **Macros intradía** · **RTH/ETH**.
**§6 MTF:** herencia cross-timeframe de todos los anteriores.

**Lectura clave:** el Pine ya es muy completo a nivel de *primitivas* (incluye IFVG, BPR, ORG como zona, SMT, macros, RTH/ETH, std-dev). **Lo que falta es casi todo de la capa de CALIDAD/GRADING y de MODELOS COMPUESTOS** que ICT cristalizó sobre todo en 2024 y 2026.

---

## B. Tabla maestra de candidatos (PARCIAL + FALTA)

### B1 · Capa de GRADING / calidad de zona (la tesis unificadora 2026) — la más importante

| # | Concepto | Curso | Estado | Tipo | Alcance | Nota / definición breve |
|---|----------|-------|--------|------|---------|--------------------------|
| 1 | **Gradient levels / grading por quadrants–eighths del rango** | 2026 (feb-28 tesis, jan-12) | **FALTA** | confluencia/contexto | FX | Dividir el rango fuente (ORG/NWOG/NDOG/swing) en high/UQ/CE/LQ/low + octavos. Las PD arrays válidas **viven sobre un gradient level**. Reto: fijar el rango-fuente determinista. **Es la columna vertebral del 2026.** |
| 2 | **Confluencia EXPONENCIAL nivel∩quadrant** | 2026 (jan-12 verbatim) | **FALTA** | confluencia (multiplicador) | FX | "the probability increases **exponentially** if it's part of/around a quadrant level of the entire range." → multiplicador de score cuando REH/REL/FVG/pool coincide con un quadrant. Fijar factor + tolerancia ATR. |
| 3 | **PD array válida = toca gradient level** (OB/FVG) | 2026 (march-13, feb-28) | **PARCIAL** | filtro/score | FX | Hoy Pine detecta OB/FVG sin filtrar por gradient. Refinamiento: OB/FVG sobre quadrant = mayor peso; OB suelto sin gradient = no validado ("por eso fallan los fake-ICT"). |
| 4 | **Premium/Discount WICK graduada** | 2026 (april-20, april-06) | **FALTA** | zona/confluencia | FX | La **mecha** tratada como gap→CE: mecha premium (sobre precio actual) / discount (bajo). Cuerpos en upper-half = bullish; "rip through" = bearish. PD array fina relativa al precio actual. |
| 5 | **Inversion-FVG "Triple-A" (AAA)** | 2026 (april-18) | **PARCIAL** | confluencia (grado) | FX | Refina IFVG (§5.2): si el retroceso **NO toca el CE y los cuerpos no se recuestan** = AAA (máxima fuerza); IFVG común solo lo toca. Grado de calidad → peso. |
| 6 | **Validación IFVG = 2 pasadas (body/closing) + sin cuerpo en lower-half** | 2026 (march-27, april-14) | **PARCIAL** | filtro | FX | Refina §5.2: un SIBI es IFVG SOLO tras cruzarlo por arriba en closing/body (balance-price-range) y luego no dejar cuerpo en la mitad inferior. Gate de validación, no objeto nuevo. |
| 7 | **"Stay-open" signature / no-retoque por mitad-cuadrante** | 2024 (§candidatos) | **FALTA** | confluencia | FX | Mitad protegida sin tocar = zona on-side/válida. Liga con CE+cuadrantes. |

### B2 · Filtros / gates del motor de decisión (calidad del setup) — alto valor

| # | Concepto | Curso | Estado | Tipo | Alcance | Nota / definición breve |
|---|----------|-------|--------|------|---------|--------------------------|
| 8 | **Time distortion** (precio dentro de inefficiency = no-trade; subir de TF revela) | 2024, 2026 (march-21, april-06) | **FALTA** | filtro/gate | FX | Anti-chop **cuantificable**: nº de velas dentro del FVG / shared-ranges en 1-min = inversion-FVG de 5-min siendo usado → subir TF. Candidato FUERTE para ADR-012. |
| 9 | **Gate de probabilidad one-sided vs two-sided** | 2026 (feb-23, march-21) | **FALTA** | filtro/gate de bias | FX | Solo hay bias direccional si **un solo lado** es defendible (~90% strike). Dos PD arrays en "arm-wrestle" = LOW-prob = no forzar. → gate de emisión de bias. |
| 10 | **HRLR / LRLR** (calidad del run a liquidez, "barcoding") | 2024, 2026 (feb-11) | **FALTA** | filtro/gate de régimen | FX | Vela dentro de la previa (solape de cuerpos) = HRLR (evitar); displacement limpio = LRLR (operar). Cuantificable: % solape de cuerpos en N velas. ICT **prefiere no operar HRLR**. |
| 11 | **Displacement OBLIGATORIO off PD array** (como gate) | 2024 | **PARCIAL** | gate | FX | T16 Displacement existe; falta **exigirlo** tras tocar una PD array como condición de entrada (filtro anti-chop). |
| 12 | **Mean-threshold = criterio MÍNIMO de propulsion válido** | 2026 (march-09) | **PARCIAL** | filtro | FX | Refina §5.8: el propulsion se valida al cruzar el **opening price** (no closing) y alcanzar el mean-threshold (½ OB) = mínimo. |
| 13 | **Decoupling de correlación = no-trade filter** | 2024, 2026 (april-10) | **FALTA** | filtro/gate | FX (multi-símbolo) | Si los correlacionados (NQ/ES/Dow → en FX: EURUSD/GBPUSD/DXY) están desacoplados → penalizar/abstener. **Distinto de SMT** (SMT puntual=señal; decoupling general=filtro). Requiere ADR multi-símbolo como T38. |
| 14 | **Sick sister por swing-high FECHADO** | 2026 (april-07) | **FALTA** | filtro/contexto | FX (multi-símbolo) | Comparar pares: cuál ya superó un swing-high de fecha X = el fuerte; el rezagado = sick sister. Operacionaliza la selección de par. |
| 15 | **Range contraction** (cuerpos < wicks precede expansión) | MMP, 2024 | **FALTA** | contexto/filtro | FX | Cuerpos pequeños (lookback 5-7d, ignorar wicks) preceden movimientos grandes. Contexto de volatilidad. |
| 16 | **Large-range-day filter** (rango > avg 3d → no operar mañana siguiente) | 2024 | **FALTA** | contexto/filtro | FX | Penaliza el día siguiente a un día de rango extremo. |

### B3 · Modelos compuestos / setups nombrados 2026 (FALTA, son combinaciones de primitivos)

| # | Concepto | Curso | Estado | Tipo | Alcance | Nota / definición breve |
|---|----------|-------|--------|------|---------|--------------------------|
| 17 | **BOLO / BPR defensivas** ("fuera de las 81") | 2026 (april-18/20/21) | **FALTA** | zona (defensiva) | FX | PD array DEFENSIVA (rejection-block + CE del lower-wick = "landmine") usada para **STOP, no entrada**. Si el precio llega = estás equivocado, no re-entrar. Distinguir de las PD arrays de ENTRADA ("las 81"). |
| 18 | **REAPER** (FVGs anidados OPUESTOS dentro de un breaker) | 2026 (june-08/09) | **FALTA** | zona/setup | índice-only(?) | Entrega de doble lado: FVGs anidados de dirección opuesta dentro de un breaker. Setup compuesto. |
| 19 | **ICT GRAY POOL** (entre CE de 2 discount-wicks) | 2026 (april-28), 2024 (gray pool) | **FALTA** | liquidez (baja calidad) | FX | Liquidez difusa entre los CE de dos mechas discount/múltiples wicks. Marca de liquidez de baja calidad. |
| 20 | **Suspension block** (VI doble / gray box diario) | 2026 (feb-11, april-08) | **PARCIAL** | zona | FX | Refina Volume Imbalance (§5.5): doble-VI que actúa como draw/gray-box. Disciplina de retroceso (máx lower-quadrant). |
| 21 | **Complex opening range delivery** | 2026 (june-22 calub) | **FALTA** | setup | índice-only | Toma stops de shorts → long-reclaim dentro de la ORG. Modelo de la apertura. |
| 22 | **MMSM / Judas fade-at-ATH** | 2026 (april-22) | **PARCIAL** | setup | FX | Refina Judas (§3.5): market-maker-sell-model fadeando un run-to-ATH (short al fallar el ATH, rechazo al CE del suspension-block). |
| 23 | **Mitigation block contextual** (down-close en run-a-liquidez ≠ bullish OB) | 2026 (march-13) | **PARCIAL** | zona/filtro | FX | Refina §2.8: el **propósito** (run a liquidez vs reversión) decide si una vela es OB o mitigation block. Gate de contexto sobre el OB. |
| 24 | **FPFVG** (First Presented FVG = el FVG con displacement de la sesión) | 2024, 2026 (april-06, june-03) | **FALTA** | confluencia/contexto | FX | El 1er FVG con displacement post-apertura. Confirmación en la vela **siguiente** al toque, no la del toque. Flag de contexto → peso extra. |

### B4 · Modelos de TIEMPO × PRECIO (mayormente índice-only → diferir Fase 5)

| # | Concepto | Curso | Estado | Tipo | Alcance | Nota / definición breve |
|---|----------|-------|--------|------|---------|--------------------------|
| 25 | **Modelo matutino ORG** (30-min 9:30-10:00 + octantes + 70% mid-gap + pre-session-FVG preferida) | 2026 (april-16/07, 2024) | **PARCIAL** | contexto/target | índice-only | Pine tiene ORG como **zona** (§5.10); falta el **modelo** de grading + estadística 70% + selección de FVG ancla. RTH/índices. |
| 26 | **First-Hour Dealing Range** (9:30-10:30) + 10am-high=target lunch | 2026 (march-28) | **FALTA** | contexto/target | índice-only | Rango graduado distinto del OR. Índices/RTH. |
| 27 | **TIME×PRICE "tabla de multiplicar" / zircon** (std-dev del ORG ∩ lunch-macro-time para ATH) | 2026 (may-14) | **FALTA** | modelo tiempo×precio | índice-only | Cruce de proyección std-dev del ORG con la ventana de macro de lunch para operar all-time-highs. "zircon" = esta estrategia de timing. |
| 28 | **Silver Bullet windows** (3-4 / 10-11 / 14-15 ET) | 2024 | **PARCIAL** | contexto | índice-only | Macros T39 + Kill Zones cubren parte; falta etiquetar las SB específicas. |
| 29 | **Discount-gap / Premium-gap morning model** | 2026 (april-20/07) | **FALTA** | contexto/bias | índice-only | discount-gap (open<settlement) → bullish, 70% al CE; premium-gap → bearish. Cierre bajo lowest-octant = no full-gap-closure. |

### B5 · Herramientas de TARGET / proyección (familia std-dev)

| # | Concepto | Curso | Estado | Tipo | Alcance | Nota / definición breve |
|---|----------|-------|--------|------|---------|--------------------------|
| 30 | **Event Horizon** (50% entre 2 pools) | 2026 (feb-27, march-19) | **FALTA** | target/nivel | FX | Midpoint entre dos pools de liquidez = punto de parcial (~25%) y de adición. **Símbolo-agnóstico, cuantificable, candidato LIMPIO.** |
| 31 | **Fulcrum point** (+ measured move + −2 std-dev) | 2026 (may-27) | **FALTA** | target | FX | Punto de apoyo + proyección measured-move y −2 std-dev. Familia std-dev (extiende §5.11). |
| 32 | **Proyección −0.5 std-dev del ORG** | 2026 (april-16/17) | **FALTA** | target | índice-only | Tras llenar el gap hasta el low y cruzarlo: target en fib −0.5 del rango ORG. |
| 33 | **Proyección ½-del-stop-hunt** | 2026 (april-15) | **FALTA** | target | FX | Medir ½ del leg del stop-hunt y proyectarla sobre los highs rotos = nivel algorítmico. |
| 34 | **Judas accumulation projection** (`max-buy = open + (open − low del drop)`) | 2026 (april-14) | **FALTA** | target/nivel | FX | Zona de acumulación smart-money: comprar hasta ese nivel, no chasear más allá. Operacionaliza el Judas como nivel medible. |
| 35 | **Measuring gap** (50% proyecta ½ del move) | 2024 | **FALTA** | target | FX | Herramienta de objetivo (como std-dev T36). |
| 36 | **Measured move ×2 / 1-cuarto-del-rango-tras-breakout** | 2022, 2024 | **FALTA** | target | FX | Tras romper un rango, objetivo ≈ +25% del rango previo. |
| 37 | **Range reset** (tomar low de run mayor reinicia premium/discount) | 2026 (march-19) | **FALTA** | recálculo P/D | FX | Al tomar liquidez de un run mayor el rango se reinicia → el CE del nuevo rango = PREMIUM aunque parezca deep-discount en el chart grande. Corrige el error "demasiado discount para shortear". |

### B6 · Niveles de CONTEXTO (bias/sesión)

| # | Concepto | Curso | Estado | Tipo | Alcance | Nota / definición breve |
|---|----------|-------|--------|------|---------|--------------------------|
| 38 | **Opening price como fulcro** (monthly/weekly/daily bias) | MMP, 2026 (april-08) | **FALTA** | contexto/bias | FX | Buy at/below open = alcista. "No hay análisis válido hasta que entra el opening price." Fulcro innegociable. |
| 39 | **Key levels rodantes** (yearly/quarterly/monthly/weekly H-L) | MMP | **FALTA** | contexto | FX | Niveles de referencia rodantes. Candidato a niveles de contexto. |
| 40 | **Algorithmic levels 00/20/50/80** (big figures) | MMP | **FALTA** | contexto/nivel | FX | Niveles institucionales redondos; old-high "feo"→soporte en el nivel cercano. |
| 41 | **Asian Range + std-dev** para fijar high/low del día | MMP, 2026 (april-11) | **FALTA** | contexto/sesión | FX | Rango asiático (7pm-medianoche NY) + std-devs encima para elegir high/low del día. |
| 42 | **Power Three / AMD** (accumulation-manipulation-distribution) | 2022 | **PARCIAL** | contexto | FX | Judas + sessions cubren parte; falta el marco AMD explícito del día. |
| 43 | **AM session re-cotiza dentro del London Range** (2-5am ET) | 2024 | **FALTA** | contexto/draw | FX | Primer movimiento post-7am = volver al rango de Londres. Nivel de draw de contexto. |

### B7 · Día de semana / estacional

| # | Concepto | Curso | Estado | Tipo | Alcance | Nota / definición breve |
|---|----------|-------|--------|------|---------|--------------------------|
| 44 | **TGIF** (retroceso 20-30%/hasta 40% del rango semanal; ventana jue→lun→martes-abandono; fib 0.4/0.3/0.2) | 2026 (april-20, march-27), 2022 | **FALTA** | contexto/target | FX | Viernes: retroceso del rango semanal. Cuantificada la ventana y los fib settings propios. |
| 45 | **Weekly profile** (martes 70% forma high/low de la semana) | 2026, 2022 | **FALTA** | contexto | FX | Estadística de qué día forma el extremo semanal. |

### B8 · Baja prioridad / terminología

| # | Concepto | Curso | Estado | Tipo | Nota |
|---|----------|-------|--------|------|------|
| 46 | **Three-drives** | 2024 | FALTA | patrón | Patrón de giro, baja prioridad. |
| 47 | **Mohawk** | 2024 | FALTA | terminología | No es motor nuevo. |
| 48 | **Turtle soup** | 2024, 2026 | **PARCIAL** | ≈ False Break (§3.7) | Restatement: toma un high pero cuerpos bajo el wick-high + relative-equal-lows sobre octant. |
| 49 | **Breakaway gap** | 2024 | PARCIAL | ≈ Opening Gaps (§5.10) | Refinamiento de NWOG/NDOG. |

---

### B9 · Recuperados del re-barrido 2022 / MMP / OTE (S074) — conceptos que faltaban en la tabla

> Re-leídos `2022-mentorship.md`, `mmp.md`, `ote.md` para no perder nada (los de 2024/2026 ya estaban). Todos **observables en precio → se MARCAN** salvo donde se indique. Varios son refinamientos de estructura/liquidez ya en Pine.

| # | Concepto | Curso | Estado | Tipo | Alcance | Nota / definición breve |
|---|----------|-------|--------|------|---------|--------------------------|
| 50 | **Nesting de estructura STH / ITH / LTH** (nivel del swing, Larry Williams) | 2022 (ep11-13), OTE | **PARCIAL** | marca/confluencia | FX | Pine tiene swings + HH/HL/LH/LL; falta la **jerarquía anidada** (short/intermediate/long-term). El **nivel** del swing da el contexto: un ITH no debe ser superado mientras el draw esté abajo. Candidato FUERTE (define invalidación + peso). |
| 51 | **IRL / ERL** (internal vs external range liquidity) | 2022 (ep3,6) | **PARCIAL** | marca/target | FX | Pine tiene pools BSL/SSL; falta etiquetar **IRL** (swings/FVG dentro del rango, entre 50% y extremos = 1er target/parcial) vs **ERL** (stops fuera de los extremos = target final). Marco de targeting. |
| 52 | **Institutional Order Flow** (up-close = resistencia bajista / down-close = soporte alcista) | 2022 (ep12-13) | **PARCIAL** | confluencia | FX | La vela de origen del displacement define S/R direccional. Liga con OB; falta como regla de order-flow explícita que pondera. |
| 53 | **ATM method** ("checkmark" / "7 torcido" = sweep + BOS + retest del nivel roto) | MMP (§11) | **PARCIAL** | marca/setup | FX | Sweep de un key swing → rompe el swing opuesto (BOS) → **retest del nivel roto** = entrada. ≈ Breaker/Flip pero con secuencia propia + reducción de stop bajando de TF. |
| 54 | **Market Maker buy/sell model** (ciclo Wyckoff-like: consol → runaway → re-accum → SMR → ruptura) | MMP (§14), 2022 (ep22) | **PARCIAL** | marca/contexto | FX | Marco macro del día (se solapa con Power Three/Judas #42). Marcar las fases ayuda al agente a ubicarse en el ciclo. |
| 55 | **EMAs 10/20 swing crossover + "stacking"** | MMP (§9) | **PARCIAL** | confluencia | FX | Pine ya tiene EMAs (§4.3) con stack-flip; ICT especifica **10/20** (zona sombreada cruce-a-cruce + apertura = momentum). Verificar longitudes vs default Pine. |
| 56 | **Días no operables: "Z-day" y "seek-and-destroy day"** | MMP (§17), 2024 | **FALTA** | marca/filtro | FX | Z-day = consolidación quieta; seek-destroy = choppy salvaje que solo corre stops. Marcar el régimen → el agente evita/penaliza. Cuantificable por rango/solape. |
| 57 | **Outside day** (rango del día previo violado por ambos extremos) | MMP (§5) | **FALTA** | marca/contexto | FX | Outside + down-close = típicamente alcista (con contexto). Espejo de Inside Day (§5.12, ya en Pine). |
| 58 | **Sunday gap / weekend gap como S/R dinámico** | 2022 | **FALTA** | marca/nivel | FX | El gap de apertura del domingo actúa como soporte/resistencia dinámico durante la semana. |
| 59 | **Target clustering / convergencia** (overlaps ≤10-15 pips = confluencia; equilibrium entre 2 targets) | MMP (§10) | **FALTA** | target | FX | Cuando varias proyecciones (std-dev, measured-move, big-figure) convergen dentro de tolerancia ATR → target de alta calidad. Herramienta de confluencia de objetivos. |
| 60 | **Daily FVG (high-end / low-end)** | 2022 (ep9) | **PARCIAL** | marca | FX | FVG en la vela diaria, operado por sus extremos. Pine detecta FVG; falta el del TF diario como nivel de contexto MTF. |
| 61 | **Overnight run rule** (run grande en Londres → evitar AM NY, esperar post-lunch) | 2022 (ep9) | **FALTA** | filtro | índice-only | Tras un run grande overnight → consolidación → no perseguir la mañana. Índices. |
| 62 | **Weekly "line in the sand" (miércoles)** | MMP (§6) | **FALTA** | marca/temporal | FX | Si el miércoles rompe el weekly-open, no debe volver a él → el algoritmo expande lejos. Nivel temporal de contexto semanal. |
| 63 | **COT — Commitment of Traders** (commercials = smart money, extremos 12m) | MMP (§12) | **EXTERNO** | contexto externo | FX | **NO derivable del precio** (dato semanal CFTC). Se conserva como posible feed de contexto macro para el agente, no como marca de chart. |

---

## C. Priorización para Ultracode (los FALTA cuantificables, símbolo-agnósticos primero)

> Orden sugerido para pedir esqueletos de regla. Criterio: (1) cuantificable y determinista, (2) FX/símbolo-agnóstico, (3) refuerza el motor de DECISIÓN/scoring (ADR-012), no zonas nuevas que dibujar.

**Tier A — núcleo del motor de calidad (pedir primero):**
1. **Gradient levels / grading quadrants-eighths** (#1) — es la base de la que cuelga casi todo el 2026.
2. **Confluencia exponencial nivel∩quadrant** (#2) — el multiplicador de score.
3. **Time distortion** (#8) — anti-chop, muy cuantificable.
4. **Gate de probabilidad one/two-sided** (#9) — gate de emisión de bias.
5. **HRLR/LRLR barcoding** (#10) — gate de régimen del run.
6. **Event Horizon** (#30) — target limpio, símbolo-agnóstico.

**Tier B — refinamientos de primitivos existentes (PARCIAL → regla de refinamiento):**
7. PD array válida = toca gradient (#3) · IFVG Triple-A (#5) · validación IFVG 2-pasadas (#6) · displacement-gate (#11) · mean-threshold mínimo propulsion (#12) · mitigation block contextual (#23).

**Tier C — modelos compuestos y targets FX:**
8. Range reset (#37) · ½-stop-hunt (#33) · Judas accumulation (#34) · Fulcrum (#31) · premium/discount wick graduada (#4) · BOLO defensivas (#17) · gray pool (#19) · FPFVG (#24).

**Tier D — multi-símbolo (requieren ADR como SMT §5.13):**
9. Decoupling (#13) · sick sister (#14).

**Tier E — índice-only → DIFERIR a perfil índices (Fase 5):**
10. Modelo matutino ORG (#25) · FHDR (#26) · TIME×PRICE/zircon (#27) · Silver Bullet (#28) · discount/premium-gap morning (#29) · complex-opening-range (#21) · REAPER (#18, verificar si aplica FX).

---

## D. Conceptos que NO son detección de chart — se conservan íntegros (nada se pierde)

> Esto **no es un cementerio de descartes.** Son conceptos que **no se dibujan como patrón de precio** (son gestión de capital, ejecución, datos externos o psicología), pero **se documentan completos** para la Fase 4 (EA) y para el agente-mentor. Donde un concepto SÍ tiene una parte observable, esa parte **se marca** (y ya está en las tablas B).

### D1 · Lo que SÍ se marca aunque no genere señal dura (aclaración)

- **Kill Zones / sesiones (filtro horario):** **NO** es no-adoptar. Ya están en Pine (§3.4) como **confluencia ponderada + sessionProfile**, y se DIBUJAN. Lo único que NO se hace es usarlas como **bloqueo duro** de toda entrada (ADR-001). El agente las VE y las pondera.
- **Zonas/targets de R:R:** el ratio 1:1 de ICT no se adopta como *política*, pero los **niveles de target** (std-dev #30-#36, clustering #59) **se dibujan**; el agente los usa para verificar si un setup llega al 1:3 exigido.
- **Días no operables (Z-day / seek-destroy #56), outside day #57, gap domingo #58:** observables → **se marcan** como contexto/régimen (ya en B9).

### D2 · Gestión de capital y posición → Fase 4 (EA), documentado íntegro

> Se conserva el detalle EXACTO para cuando se construya el EA; no es detección, no va al motor de señal, pero **no se pierde**.

- **Money management "flat-line the equity drawdown" (MMP §7, §16 — ICT lo llama su lección más importante):** escalado de leverage por unidades. **Tras una pérdida → bajar a la unidad mínima** y quedarse; subir solo al ganar Y estar sobre el balance inicial. **Tras 5 wins consecutivos → bajar a mínima** (forecast del próximo drawdown), extensible a 7-10 en racha. **Halving:** 1ª pérdida 2% → 1% → 0.5%/1%. Matemática: fijo al 2% revienta en ~8 pérdidas (−13%); halving aguanta **24 pérdidas con −12% DD**. **Escalera de recuperación:** subir de tier solo tras recuperar ≥50% del dip; ante cualquier pérdida, volver a cortar. NUNCA Martingale/averaging-down. **Mental capital** = lo que estás dispuesto a perder, no lo depositado.
- **Parciales IRL→ERL / "pay yourself" (2022, OTE Vol 15, MMP §6):** tomar parcial en IRL (1er objetivo) y dejar correr a ERL; a cada **100 pips** tomar algo (day trader 80%, short-term ≥50%); mover stop a BE tras 1er parcial. "Partial pays."
- **Regla 2:1 sobre el PRIMER scaling (MMP §14, OTE):** la distancia entrada→1er profit ≥ 2× el riesgo entrada→stop (por eso entra cerca de 62% buscando 70.5%). Critica el "1R/2R/3R" medido al target lejano.
- **Regla del LEADER 80/20 (OTE Vols 16-18):** en −2 std-dev cerrar 80% y dejar 20% leader si el daily sostiene objetivo mayor.
- **Regla de los 100 pips (OTE):** si da 100 pips flat antes de −2 → tomar parcial igual.
- **TIME-STOP (2026 april-22/28):** salir por tiempo si el precio pasa demasiado en zona sin willingness. Input de gestión del EA.
- **Leader orders / "premium por Intel" (2022, George Angel):** meter 1 contrato sin spot elegido solo para sentir la entrega; las pérdidas pequeñas = costo de información, no error. Discrecional.
- **Riesgo por trade:** ICT 3-4.5%; **alumno nuevo <1.25-1.5%**. Config del EA.
- **Fluff exits:** no apuntar al nivel exacto; +3-5 pips (novato 10) por el spread variable del broker.

### D3 · Operativa de contratos / mercado (futuros) — documentado

- **Códigos de mes (índices e-mini):** H=marzo · M=junio · U=septiembre · Z=diciembre. Expiración = 3er viernes. **Rolar ~1 semana antes** al mes con mayor open interest. (Reaparece en 2026 con el "contrato continuo" #B1-tesis.)
- **Margin hike = "tipping their hand":** si el exchange sube márgenes → vienen movimientos grandes.
- **Data feed FX:** ICT usa forex.com (evita OANDA/MAM). Informativo.

### D4 · Psicología / proceso del mentor — para el agente-mentor, no para el Pine

- **Ejercicio del primer mes:** 1-2 pares, marcar equal highs/lows, **NO operar**, estudiar barridos (activa el "reticular activating system"). Paper → demo → micro-live (6 meses consistente).
- **Journaling = 80% del aprendizaje;** separar resultado de proceso. Fear-of-missing se cura entendiendo el setup (timing); fear-of-losing con leverage/frecuencia bajos.
- **Getting-in-sync tras ausencia (2026 april-06):** al volver, no registrar niveles nuevos, solo observar.
- **Sentiment contrarian por emojis de streamers (2026 april-13):** masas one-sided/giddy = mejor indicador de sentimiento. Lectura humana, no automatizable (pero el agente-enjambre podría aproximarlo con un feed de sentimiento — anotado).

---

## E. Tensiones de fondo (recordatorio)

- **R:R:** ICT relativiza (parciales, 1:1 por frecuencia) ↔ proyecto exige **1:3 fijo**. → la *política* 1:1 no se adopta; los targets std-dev (#30-#36) y el clustering (#59) **sí se dibujan** y sirven para verificar el 1:3.
- **Horario:** ICT es índice/RTH-céntrico con ventanas NY estrictas ↔ **ADR-001** (FX 24h, multi-símbolo). → las KZ **se marcan y ponderan** (no bloquean); lo `índice-only` se difiere a perfil índices (Fase 5); lo `FX` se valida primero en EURUSD.
- **Discrecional vs determinista:** mucho del grading de mechas/contexto es visual/discrecional. → cada concepto a MARCAR necesita un **rango-fuente determinista** antes de ser regla (el principal reto de #1 gradient levels). Marcar algo no exige que genere señal — basta que sea observable y reproducible.

---

*Generado S074 (2026-06-30). Fuente mentor: 5 cursos íntegros (ver [[ict-mentor-madre-build]]). Re-barrido 2022/MMP/OTE para completar (B9). CORE Pine intacto 1517 líneas SHA `80fad14dd8d03758`. Principio: **MARCAR ≠ señal** — todo lo observable se dibuja para el agente; solo la capa de señal está gobernada por 1:3/ADR-001. Siguiente: pasar Tier A a Ultracode para esqueletos de regla.*
