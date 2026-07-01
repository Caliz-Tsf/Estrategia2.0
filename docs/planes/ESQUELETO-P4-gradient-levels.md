# Esqueleto de integración — PARTE 4: Gradient Levels (candidato #1 + #2 + #3, opcional #5)

> **Sesión:** S079 · Fase 1 · rama `pine/sistema-completo`.
> **Qué es:** el **esqueleto de regla** de la familia **Gradient Levels / grading por quadrants–eighths** — la tarea que `docs/planes/DOSSIER-gradient-levels-para-ultracode.md` (S077) encargó, ejecutada directamente en esta sesión (rol "ultracode" = arquitectura profunda dentro de Claude Code, mismo patrón que `ESQUELETO-P1`/`ESQUELETO-MITIGACION`). Sigue el mismo molde que esos dos documentos: estructura + firmas + contratos + fichas listas para rellenar.
> **Qué NO es:** NO es código. NO toca ningún `.pine`. NO toca `docs/reglas-smc-ict.md` todavía (eso es el paso de "relleno" bajo el gate [[sprint16-gate-reglas-antes-de-codigo]]). NO cuantifica ningún umbral final ni inventa casos EURUSD — todo eso queda `⏳ a cuantificar [impl]` / `⏳PENDIENTE-TVMCP`. Cualquier IA (**[impl]**) puede tomar este documento y ejecutar el proceso canónico de 7 pasos sin tener que re-decidir arquitectura.
> **Léelo junto a:** `docs/planes/DOSSIER-gradient-levels-para-ultracode.md` (el briefing/doctrina de origen — este documento resuelve punto por punto su §0), `docs/reglas-smc-ict.md` (fuente de verdad SMC + formato de ficha §6.0, ejemplos §2.3/§5.10/§5.11/§6.3.x), `docs/planes/ESQUELETO-P1-conceptos-EA-pine-repos.md` (mismo proceso, mismo formato), `docs/planes/ESQUELETO-MITIGACION-conceptos.md` (patrones P1–P4 de ciclo de vida — este esqueleto añade una variante), `docs/workplan/PINE-PLAN.md` §2/§3/§5, `WORKPLAN-MAESTRO-V2.md` §4.8 (42 confluencias), `CLAUDE.md`, ADR-001/002/010/011.
> **Siguiente paso (NO en este documento):** Claude Code rellena — extrae casos EURUSD por TV MCP, cuantifica los `⏳`, implementa las `f_*` puras, compila 0/0, valida ≥90, registra confluencia, commit — y **entonces** integra T41–T44 a `PINE-PLAN.md §7` / `WORKPLAN-MAESTRO-V2.md §4.8` / `MATRIZ-conceptos-cobertura.md` (tabla B1, hoy no existe físicamente — ver §9).

---

## §0 — Alcance decidido *(resuelve dossier §3 + pregunta §7.7)*

| # | Pieza | Tarea asignada | ¿Entra a este esqueleto? | Naturaleza |
|---|-------|-----------------|---------------------------|------------|
| **1** | Grading quadrants/eighths del rango | **T41** | **SÍ — núcleo obligatorio** | contexto/herramienta (como Std Dev §5.11) |
| **2** | Confluencia exponencial nivel∩quadrant | **T42** | **SÍ — la razón de ser de #1** | confluencia candidata **#52**, **multiplicador** (no voto plano) |
| **3** | FVG válido = toca gradient level | **T43** | **SÍ — refinamiento de `f_detectFVG`** | refina #18/#20 (sin número nuevo, patrón True FVG §5.1) |
| 5 | Grading de mecha REH/REL + parcial LQ–CE | **T44** | **SÍ, pero OPCIONAL/diferida** — ver nota abajo | herramienta de gestión/invalidación (no confluencia) |
| 4 | HRLR vs LRLR por barcoding | — | **NO** | familia distinta, candidato aparte (no gradient) |
| 6–9 | OR 9:30–10:00 / FHDR / 10am-high / wick-ATH | — | **NO** | índice-only, diferir Fase 5 (`[ADR-001]`) |
| 10 | Event Horizon | — | **NO** | candidato propio, no gradient |

**Decisión sobre #5 (T44):** el anchor de REH/REL (vela más a la izquierda del swing extremo) **ya es determinista** — se apoya en `f_detectSwings` (§1.1), que ya existe. Por tanto SÍ se esqueletiza (§4.4/§5.4 de este documento), pero se marca **opcional y de implementación diferida**: el `[impl]` cierra primero T41→T42→T43 (el núcleo + su consumidor de score + su primer refinamiento aplicado) y solo entonces decide si T44 aporta suficiente valor incremental para codificarse en el mismo sprint o quedar en backlog. Ningún gate de fase depende de T44.

---

## §1 — Reto central resuelto: política de rango-fuente determinista *(resuelve dossier §4 + pregunta §7.1)*

**Problema:** el grading en sí es trivial (dividir `[low, high]` en fracciones); lo difícil es **qué rango se gradúa**, de forma determinista, reproducible y símbolo-agnóstica.

**Política de selección (3 rangos-fuente candidatos, en este orden de prioridad):**

1. **Prioridad 1 — Dealing range Premium/Discount (`f_premiumDiscount`, §2.3).** Ya existe, ya es determinista (último strong high ↔ strong low), ya se actualiza con la estructura, ya es símbolo-agnóstico. Es el rango-fuente **por defecto** siempre que haya un dealing range vigente. Generaliza directamente: hoy divide en 2 (premium/discount) + banda eq; T41 lo extiende a 5 puntos (quadrants) + opcionalmente 9 (eighths).
2. **Prioridad 2 — Suspension block diario (Fib highest-high→low del día, `madre-2026.md:135,:207`).** **PARCIAL en Pine** — no existe como rango-fuente propio todavía (solo hay Volume Imbalance §5.5 y la nota "suspension = VI doble", MATRIZ #20). T41 debe **construirlo**: `top = highest(high, lookbackDiario)`, `bottom = lowest(low, lookbackDiario)` del día del broker vigente (misma frontera horaria que `f_detectOpeningGaps` §5.10), confirmado en el cierre de la vela D1 (anti-repaint). Se activa como candidato cuando el dealing range de Prioridad 1 es demasiado ancho/viejo (swing origen a más de `gradStaleBars` velas) o cuando el test de desempate (regla 3) lo favorece.
3. **Prioridad 3 — Serie de gaps de apertura (`f_detectOpeningGaps`, §5.10).** Cada gap individual `(close_previo, open_nuevo)` es en sí un mini-rango graduable (alimenta directamente §2.7 del dossier: "grading del gap tras displacement"). Se usa como rango-fuente **adicional** (no excluyente de 1/2): cada gap medible abre su propio grid de eighths, útil para el filtro FVG-válido (T43) cuando el FVG cae cerca de un gap de apertura reciente en vez de dentro del dealing range grande.

**Regla de desempate — test cuerpos-vs-nivel (`madre-2026.md:408,:440,:479`, dossier §2.8):** cuando dos rangos-fuente candidatos (P1 vs P2, o cualquiera vs P3) producen grids con niveles distintos cerca del precio, se adopta el grid cuyos niveles los **cuerpos** (open/close, no mechas) de las últimas `gradBodyLookback` velas confirmadas **respetan más** (más cierres dentro de `gradTol×ATR` de un nivel del grid). Esto es determinista y auditable (cuenta, no interpreta). Ver `f_bodyRespectsLevel` en §2.

**Persistencia (`madre-2026.md:93,:322`, pregunta §7.5):** cada rango-fuente que se fija (nuevo swing dominante, nuevo día, nuevo gap) genera un grid **nuevo**; los grids de los últimos `gradPersistDays` (default doctrinal **5**, `⏳` calibrar tope real por presupuesto de objetos) se mantienen dibujados como referencia (ghost); los más viejos se descartan. Esto reusa el mecanismo P4 "Present mode"/cuota de `ESQUELETO-MITIGACION §2` (dibujar solo las N ocurrencias más recientes), aplicado a grids en vez de eventos puntuales.

---

## §2 — Firmas propuestas: UDT, `KIND`, funciones CORE puras *(resuelve dossier §0.3)*

**Constante `KIND` nueva** (siguiente libre tras `KIND_SMT=52`, `pine/SMC-Library.pine:49`):
```
export const int KIND_GRADIENT = 53   // [T41] nivel de un grid gradient (línea, no zona)
```

**Constantes de rango-fuente** (namespace propio, no confundir con `PD_*`):
```
export const int GRAD_SRC_PD         = 0   // dealing range Premium/Discount (§2.3) — prioridad 1
export const int GRAD_SRC_SUSPENSION = 1   // suspension block diario (Fib highest-high/low) — prioridad 2
export const int GRAD_SRC_OPENGAP    = 2   // gap individual de f_detectOpeningGaps (§5.10) — prioridad 3
```

**UDT nuevo — `SMC_GradientGrid`** (grid completo de un rango-fuente ya fijado; vive junto a `SMC_Zone`/`SMC_Pool` en la sección UDTs):
```
export type SMC_GradientGrid
    float  top              // límite superior del rango-fuente
    float  bottom           // límite inferior del rango-fuente
    int    srcKind          // GRAD_SRC_PD / GRAD_SRC_SUSPENSION / GRAD_SRC_OPENGAP
    int    barTimeAnchor    // cuándo se fijó el rango-fuente (ancla temporal, anti-repaint)
    int    barIdxAnchor
    array<float> levels     // niveles calculados: [0, 0.125?, 0.25, 0.375?, 0.5, 0.625?, 0.75, 0.875?, 1]
    array<bool>  isQuadrant // paralelo a levels: true en {0,0.25,0.5,0.75,1}, false en eighths
    int    ageDays  = 0     // NUEVO cada frontera de día; controla el ghost/descarte (§1 persistencia)
```

**Funciones CORE puras** (sección `// === LIBRARY CORE ===`, `export` en Library — cuerpos `// TODO [impl]`):

```
// f_computeGradientLevels: generaliza f_premiumDiscount (§2.3) de 2 zonas a un grid de N puntos.
// Contrato: dado [bottom, top] fijo, devuelve un array de fracciones de precio en
// {0, 0.25, 0.5, 0.75, 1} SIEMPRE + {0.125, 0.375, 0.625, 0.875} si includeEighths=true
// (input i_gradEighths, pregunta §7.2). Sixteenths NO se calculan (fuera de alcance, §7.2).
// PURA -> golden test MQL5 directo (ADR-002). NO dibuja, NO lee series globales.
export f_computeGradientLevels(float top, float bottom, bool includeEighths) =>
    // TODO [impl]: levels[i] = bottom + frac*(top-bottom) por cada frac de la escala elegida;
    // devolver también el array paralelo isQuadrant. Rango invalido (top<=bottom) -> arrays vacios.
    array.new<float>()

// f_gradientZone: clasifica 'price' contra un grid ya calculado. Análogo N-way de
// f_premiumDiscount (que sólo devuelve premium/discount/equilibrium). Devuelve el índice
// del nivel más cercano + la distancia en ATR. PURA.
export f_gradientZone(float price, array<float> levels, float atr) =>
    // TODO [impl]: recorrer levels, hallar el de menor |price-level|; devolver
    // [idxMasCercano, distanciaEnATR]. Grid vacío -> [na, na].
    [int(na), float(na)]

// f_nearGradientLevel: test booleano "price toca/está sobre un gradient level" —
// el filtro que consumen T42 (confluencia) y T43 (FVG-válido). tol = gradTol×ATR14 (input).
// PURA.
export f_nearGradientLevel(float price, array<float> levels, float tol) =>
    // TODO [impl]: true si existe algún level con |price-level| <= tol.
    false

// f_bodyRespectsLevel: el test de desempate cuerpos-vs-nivel (§1, doctrina §2.8). Cuenta,
// de las ultimas 'lookback' velas CONFIRMADAS, cuántas cerraron (open Y close, no mecha)
// dentro de tol de CUALQUIER nivel del grid candidato. Se llama una vez por rango-fuente
// candidato; el que tenga mayor conteo gana el desempate (§1). PURA (recibe arrays de
// open/close recientes por parámetro, no request.security).
export f_bodyRespectsLevel(array<float> recentOpens, array<float> recentCloses, array<float> levels, float tol) =>
    // TODO [impl]: contar velas donde min(open,close) y max(open,close) están ambos
    // dentro de tol de algún nivel (cuerpo "recostado" sobre el nivel, no solo el close).
    0

// f_gradientConfluenceBonus: T42 — el multiplicador exponencial (dossier §2.2, "the
// probability... increases EXPONENTIALLY"). NO sustituye la suma ponderada (P-05/P-06/P-22);
// se aplica DESPUÉS como factor multiplicativo (§3 de este documento). Devuelve el bonus
// (0..gradMultMax-1) según cuántas confluencias YA activas (zonas: OB/FVG/pool) coinciden
// con un nivel isQuadrant=true del grid vigente. PURA (recibe el conteo de coincidencias
// por parámetro, no recalcula el scoring).
export f_gradientConfluenceBonus(int nConfluenciasSobreQuadrant, float gradMultMax) =>
    // TODO [impl]: función creciente saturante (ej. 1 - exp(-k*n), tope gradMultMax);
    // fijar 'k' en Fase 3 (IS/OOS), aquí solo la forma funcional. n=0 -> bonus=0.
    0.0
```

**Selección de rango-fuente (wiring, no 100% pura — combina candidatos ya calculados):**
```
// f_selectGradientSource: aplica §1 — prioridad 1→2→3, con el test f_bodyRespectsLevel
// como desempate cuando hay ambigüedad (candidatos con niveles distintos cerca del precio).
// Recibe los 3 grids YA calculados (uno por f_computeGradientLevels por candidato) +
// los arrays recientes de open/close para el test de desempate. Devuelve el SMC_GradientGrid
// ganador. Vive en el consumidor (Visual/Strategy), llama a las puras de arriba.
// TODO [impl]: 1) si solo P/D vigente -> ese. 2) si P/D "stale" (>gradStaleBars desde el
// swing origen) y suspension disponible -> comparar con f_bodyRespectsLevel. 3) gaps de
// apertura NUNCA reemplazan a P1/P2 como rango PRINCIPAL; corren en PARALELO como grids
// adicionales (§1 prioridad 3) para T43.
```

---

## §3 — Naturaleza de confluencia por pieza *(resuelve dossier §5.5 + pregunta §7.3)*

| Pieza | ¿Confluencia propia? | Mecanismo | Nota de arquitectura |
|---|---|---|---|
| **T41 — grading (núcleo)** | **NO** | contexto/herramienta pura, igual que Standard Deviation `§5.11`/`§6.3.31` ("no es zona detectada, es un cálculo") | No suma al score por sí solo; es el insumo de T42/T43. |
| **T42 — confluencia exponencial** | **SÍ — candidata #52** | **multiplicador**, no voto plano (dossier §2.2 dixit "exponencial") | Ver mecanismo abajo. **Requiere ADR nuevo** (candidato **ADR-013**) antes de wiring en Fase 2 (F2-T01) — cambia el contrato de `f_scoreConfluences` de puramente aditivo a aditivo+multiplicativo. No se implementa el wiring de scoring sin ese ADR aprobado; T42 en Fase 1 solo entrega la función pura `f_gradientConfluenceBonus` y su spec. |
| **T43 — FVG válido por gradient** | **NO — refina FVG existente** | flag booleano adicional en `SMC_Zone` (patrón `trueFvg`/`propulsion`, `pine/SMC-Library.pine:108-109`) — p.ej. `gradedFvg` | Igual que True FVG (§5.1) eleva `strength` sin sumar # nueva (`[FIX P-05]`). Un FVG que NO toca gradient level sigue existiendo pero con `strength` degradada. |
| **T44 — grading de mecha (opcional)** | **NO** | herramienta de gestión/invalidación: informa "parcial obligatorio entre LQ y CE" y "si no alcanza CE = debilidad/reversión" — se lee como *matiz de SL/TP y bias*, no como zona nueva | Análogo a Immediate Rebalance (§5.4/§6.3.25): "matiz de contexto, no zona operable". |

**Mecanismo propuesto para T42 (multiplicador, para que Fase 2 no lo re-litigue):**
```
scoreDir_raw   = Σ(peso_i × activa_i)                          // arquitectura actual, SIN cambios (§4.8)
gradientBonus  = f_gradientConfluenceBonus(nSobreQuadrant, gradMultMax)   // 0 .. (gradMultMax-1)
scoreDir_final = scoreDir_raw × (1 + gradientBonus)
```
`nSobreQuadrant` = cuántas confluencias de zona (OB #17/19, FVG #18/20, pool #9) YA activas en `scoreDir_raw` tienen su nivel dentro de `gradTol` de un punto **isQuadrant=true** del grid vigente (los eighths NO disparan el bonus — la doctrina dice "quadrant level de la entereza del rango", no cualquier punto de la escala). `gradMultMax` (tope del multiplicador) y la forma exacta de `f_gradientConfluenceBonus` se calibran en Fase 3 (IS/OOS), consistente con `[ADR-002]`.

---

## §4 — Fichas de regla (formato canónico §6.0 — listas para el paso de "relleno")

> Formato exacto de `docs/reglas-smc-ict.md §6.0`. Estas 4 fichas van a **§5.16–§5.19** (siguiente número libre tras `§5.15 RTH vs ETH · T40`) cuando el `[impl]` las cuantifique con casos EURUSD y las migre a la fuente de verdad.

### §5.16 [Propuesta] Gradient Levels — grading del rango `f_computeGradientLevels` · T41 (núcleo)

**Concepto.** Toda referencia de rango se trata como una escala graduada, no como una línea suelta: se mide un rango-fuente (§1 de este esqueleto) y se divide en high / upper-quadrant (0.75) / midpoint-CE-equilibrium (0.5) / lower-quadrant (0.25) / low, y opcionalmente en eighths (0.125/0.375/0.625/0.875). Generaliza `f_premiumDiscount` (§2.3) de 2 zonas a N puntos. Doctrina: "we're just measuring a range and dividing it into mid range, upper quadrant, lower quadrant and high and the low" (`madre-2026.md:90-94`).

**Definición cuantificada.** `⏳ a cuantificar [impl]`
- Rango-fuente por la política de prioridad §1 de este esqueleto (P/D → suspension diario → gaps de apertura, desempate por `f_bodyRespectsLevel`).
- `levels = f_computeGradientLevels(top, bottom, i_gradEighths)`.
- Grid recomputado cuando el rango-fuente vigente cambia (nuevo swing dominante para P/D, nuevo día para suspension, nuevo gap para opening-gap) — anti-repaint: confirmación en el cierre de la vela/frontera que fija el nuevo rango.

**Mitigación / ciclo de vida.** No es P1–P4 puro de `ESQUELETO-MITIGACION`: es un **grid persistente recomputado en frontera**, más cercano al patrón de "serie de niveles globales" de Opening Gaps (§5.10/§6.3.32) que a un barrido o una zona con 4 estados. Cada grid nuevo no invalida al anterior; el anterior pasa a `ageDays++` y se dibuja como ghost hasta `gradPersistDays` (§1), luego se descarta.

**Parámetros default.**
| Param | Default | Nota |
|---|---|---|
| `gradEighths` | **true** ⏳ | incluir 0.125/0.375/0.625/0.875 (pregunta §7.2; sixteenths fuera de alcance). |
| `gradPersistDays` | **5** ⏳ | doctrina `madre-2026.md:93,:322`; tope real sujeto a presupuesto de objetos. |
| `gradStaleBars` | ⏳ | velas desde el swing origen del P/D tras las que se considera "viejo" y se evalúa candidato #2. |
| `gradBodyLookback` | ⏳ (plausible 3-5) | velas para `f_bodyRespectsLevel` (desempate §1). |

**Confirmación / anti-repaint.** El grid se fija SOLO cuando su rango-fuente confirma (swing dominante confirmado / cierre D1 / gap de apertura confirmado en frontera) — nunca intra-vela. `barstate.isconfirmed` en los 3 casos, heredado de las fuentes ya anti-repaint (§2.3/§5.10).

**Contraejemplo.** `⏳` Calcular el grid sobre un rango-fuente que todavía no confirmó (p.ej. un swing candidato sin BOS de confirmación) → grid discrecional/repintable, PROHIBIDO.

**Casos de prueba** (EURUSD, TV MCP): ✓ ✓ ✓ + ✗ `⏳PENDIENTE-TVMCP`

---

### §5.17 [Propuesta] Confluencia exponencial nivel∩quadrant `f_gradientConfluenceBonus` · T42 — candidata #52

**Concepto.** La probabilidad de que el precio corra hacia un nivel (REH/REL, FVG, pool) aumenta **exponencialmente** si ese nivel coincide con un quadrant del rango mayor (`madre-2026.md:92,:287`, verbatim "the probability of it running to them increases exponentially if it's part of or around a quadrant level of the entirety of the range").

**Definición cuantificada.** `⏳ a cuantificar [impl]`
- Contar `nSobreQuadrant` = confluencias de zona activas (OB/FVG/pool, ya evaluadas en `scoreDir_raw`) con nivel dentro de `gradTol×ATR14` de un punto **isQuadrant=true** del grid T41 vigente.
- `gradientBonus = f_gradientConfluenceBonus(nSobreQuadrant, gradMultMax)`, forma funcional creciente saturante (§2 de este esqueleto).
- `scoreDir_final = scoreDir_raw × (1 + gradientBonus)` — mecanismo fijado en §3 de este esqueleto; **requiere ADR-013** antes de wiring real en Fase 2.

**Mitigación / ciclo de vida.** Evento de scoring por vela confirmada (se recalcula cada vez que `scoreDir_raw` se recalcula); no persiste estado propio más allá del grid T41 del que depende.

**Parámetros default.**
| Param | Default | Nota |
|---|---|---|
| `gradTol` | ⏳ (plausible 0.10–0.15) | × ATR14. Tolerancia "sobre un gradient level" (pregunta §7.4). |
| `gradMultMax` | ⏳ | tope del multiplicador; calibración Fase 3 `[ADR-002]`. |

**Confirmación / anti-repaint.** Se evalúa en `barstate.isconfirmed`, sobre el `scoreDir_raw` ya calculado de esa vela (nunca sobre score intra-vela).

**Contraejemplo.** `⏳` Un nivel que coincide con un **eighth** pero no con un **quadrant** (0/0.25/0.5/0.75/1) → NO dispara el bonus exponencial (la doctrina lo liga a "quadrant level de la entereza del rango", no a cualquier punto de la escala fina).

**Casos de prueba** (EURUSD, TV MCP): ✓ ✓ ✓ + ✗ `⏳PENDIENTE-TVMCP`

---

### §5.18 [Propuesta] FVG válido = toca gradient level (refinamiento de `f_detectFVG`) `f_nearGradientLevel` · T43

**Concepto.** No todos los FVG son iguales: los de alta probabilidad se forman **tocando un gradient level**; los que no, no son "FVG válidos" (`madre-2026.md:101-103,:209`, verbatim "high probability FVGs form in close proximity and are touching one of the gradient levels... if it's not doing these things it's not a valid fair value gap"). Fuente preferida del grid para este filtro: el Fib del suspension block diario (`madre-2026.md:135,:207`) o el grid del gap de apertura más cercano (§1 prioridad 3), no necesariamente el dealing range grande.

**Definición cuantificada.** `⏳ a cuantificar [impl]`
- Al detectar un FVG (`f_detectFVG`, §2.2), evaluar `f_nearGradientLevel(fvg.ce, levels, gradTol)` contra el grid T41 más relevante (§1: preferir suspension diario / gap-de-apertura sobre el P/D si ambos aplican).
- Si `true` → flag `gradedFvg = true` en `SMC_Zone` (nuevo campo, patrón `trueFvg`/`propulsion`, `pine/SMC-Library.pine:108-109`) → eleva `strength` en la capa de discriminación (§6, NO suma # nueva).
- Si `false` → el FVG sigue existiendo (no se descarta), pero sin el bono de calidad.

**Mitigación / ciclo de vida.** Reusa 100% la máquina de 4 estados del FVG (`f_updateZoneMitigation`, patrón **P2** de `ESQUELETO-MITIGACION §2`) — `gradedFvg` es un flag adicional, no un ciclo de vida propio.

**Parámetros default.**
| Param | Default | Nota |
|---|---|---|
| `gradTol` | (reusa T42) | mismo `input` que la confluencia exponencial — no duplicar tolerancia. |

**Confirmación / anti-repaint.** Se evalúa en el mismo instante en que el FVG se confirma (`barstate.isconfirmed`, ya establecido en §2.2) — el flag `gradedFvg` no reintroduce repaint.

**Contraejemplo.** `⏳` Un FVG "suelto" sin gradient level cercano (el caso citado por el mentor como "fake-ICT FVGs") → detectado igual por `f_detectFVG` pero `gradedFvg=false`, `strength` baja.

**Casos de prueba** (EURUSD, TV MCP): ✓ ✓ ✓ + ✗ `⏳PENDIENTE-TVMCP`

---

### §5.19 [Propuesta, OPCIONAL — diferible] Grading de mecha REH/REL `f_gradeWick` · T44

**Concepto.** El anchor de un REH/REL es la vela más a la izquierda del swing extremo; si ese anchor tiene mecha, se gradúa la mecha (LQ/CE/UQ) igual que un rango — "we grade those because they're gaps" (`madre-2026.md:96-99,:183`). El precio a menudo solo entra a un quadrant de la mecha y rechaza (parcial obligatorio LQ↔CE); si ni siquiera alcanza el CE al acercarse → señal de debilidad/reversión. La mecha se gradúa **premium** si está sobre el precio actual, **discount** si por debajo (`madre-2026.md:116`, abril-20). Regla asociada (`madre-2026.md:263`): si un FVG está a 0 velas de una mecha → NO usar el FVG, graduar la mecha; si ≥1 vela de separación → el FVG sí es válido como PD array independiente.

**Definición cuantificada.** `⏳ a cuantificar [impl]`
- Anchor = vela izquierda del swing extremo (`f_detectSwings`, §1.1) — ya determinista.
- `top/bottom` de la mecha = `[min(open,close), high]` o `[low, max(open,close)]` según lado — reusa `f_computeGradientLevels` sobre este rango pequeño.
- Regla de separación FVG-vs-mecha (`madre-2026.md:263`): si `|barIdx(FVG) - barIdx(mecha)| == 0` → preferir la mecha; si `≥1` → ambos coexisten como PD arrays independientes.

**Mitigación / ciclo de vida.** Herramienta de gestión (matiz de SL/TP y de bias), no zona con estados propios — análogo a Standard Deviation (§5.11/§6.3.31) e Immediate Rebalance (§5.4/§6.3.25).

**Parámetros default.** `⏳` (reusa `gradEighths`/`gradTol` de T41/T42; sin parámetros propios previstos).

**Confirmación / anti-repaint.** El swing extremo debe estar confirmado (mismo criterio que `f_detectSwings`) antes de graduar su mecha.

**Contraejemplo.** `⏳` Graduar la mecha de un swing **no confirmado** (candidato a extremo que aún puede cambiar) → discrecional, prohibido.

**Casos de prueba** (EURUSD, TV MCP): ✓ ✓ ✓ + ✗ `⏳PENDIENTE-TVMCP`

**Nota de prioridad:** confirmar con el usuario/`[impl]` si T44 entra en el mismo sprint que T41–T43 o queda en backlog explícito (§0 de este esqueleto).

---

## §5 — Sub-fichas MTF (formato §6.3.x — 5 ejes del proyecto)

> Formato exacto de `docs/reglas-smc-ict.md §6.3.x` (ver `§6.3.29 IPR`, `§6.3.31 Standard Deviation`, `§6.3.32 Opening Gaps` como precedentes directos). Van a **§6.3.36–§6.3.39** (siguiente número libre tras `§6.3.35 Herencia D1/H1`).

##### 6.3.36 [Propuesta] Gradient Levels — grid del rango (§5.16 · T41) — **HERRAMIENTA, no confluencia** *(no aplica fallo de discriminación, precedente §6.3.31)*

- **Variante correcta / desempate.** El grid **relevante** es el del rango-fuente ganador de la política §1 (prioridad P/D → suspension → opening-gap, desempate `f_bodyRespectsLevel`). **Descarta** (citable): graduar un rango-fuente "stale" cuando hay un candidato de mayor prioridad vigente y no-stale.
- **Fuerza (0–1).** **N/A directo** — es un cálculo, no una marca con `strength` propia (igual que Std Dev §6.3.31). Su "fuerza" se transmite indirectamente vía T42 (bonus de confluencia) y T43 (`gradedFvg`).
- **Invalidación externa.** El grid se invalida/reemplaza cuando su rango-fuente cambia (nuevo swing dominante, nuevo día, nuevo gap) — no por precio cruzándolo (no es un nivel que se "consuma").
- **Visual (jerarquía).** **Primario:** grid del rango-fuente vigente (líneas finas en cada fracción, quadrants más gruesos que eighths). **Secundario:** grids `ageDays 1-gradPersistDays` como ghost tenue. **Terciario:** descartado tras `gradPersistDays`. Toggle `i_showGradient` (+ `i_gradEighths` para eighths on/off).
- **MTF.** Los gradient levels de un rango-fuente HTF (p.ej. suspension diario) son **globales** (mismos en todo TF, igual que Opening Gaps §6.3.32) — se computan UNA VEZ en el TF-fuente y se heredan por nivel, no se recomputan por TF (pregunta §7.8, recomendación fijada).

##### 6.3.37 [Propuesta] Confluencia exponencial nivel∩quadrant (§5.17 · #52 cand. T42) *(fallo #2 fuerza)*

- **Variante correcta / desempate.** El bonus se dispara SOLO por coincidencia con un punto **isQuadrant=true** (0/0.25/0.5/0.75/1), NUNCA por un eighth. **Descarta** (citable): confluencia que coincide con un eighth (0.125/0.375/0.625/0.875) → cuenta para T43 (FVG-válido puede usar cualquier punto de la escala) pero NO dispara el multiplicador exponencial de T42.
- **Fuerza (0–1).** `nSobreQuadrant` (cuántas confluencias de zona coinciden) · forma funcional saturante `f_gradientConfluenceBonus`. Quant: **alta** (≥2 confluencias de zona sobre el mismo quadrant), **media** (1), **N/A** (0, bonus=0).
- **Invalidación externa.** Si el grid T41 del que depende se reemplaza (rango-fuente cambia), el bonus se recalcula contra el grid nuevo — no hay estado propio que invalidar.
- **Visual (jerarquía).** No dibuja marca propia — se refleja en el panel T14 (score direccional ya multiplicado) y opcionalmente resaltando (borde extra) las zonas cuyo nivel SÍ coincide con un quadrant. Toggle `i_showGradientBonus` (solo panel/resaltado, no objeto nuevo).
- **MTF.** El bonus se calcula sobre el `scoreDir_raw` del TF que se opera; el grid del que depende puede ser HTF (heredado, §6.3.36) pero el cálculo del bonus es local al TF de scoring.

##### 6.3.38 [Propuesta] FVG válido por gradient level (§5.18 · refina #18/#20, T43) *(fallo #1 variante)*

- **Variante correcta / desempate.** `gradedFvg=true` si el CE del FVG está dentro de `gradTol×ATR` de cualquier nivel (quadrant o eighth) del grid relevante (preferencia: suspension diario / gap-de-apertura sobre P/D grande, §1 prioridad 3). **Descarta** (citable): FVG cuyo CE cae lejos de todo nivel del grid (el "fake-ICT FVG" que cita la doctrina) → sigue siendo FVG (§2.2), pero `gradedFvg=false`, sin el bono de calidad. Guard con §2.6 del dossier (mecha adyacente 0 velas → preferir graduar la mecha, T44, no el FVG).
- **Fuerza (0–1).** `gradedFvg` (binario, eleva `strength` igual que `trueFvg` §6.2.2) · distancia en ATR al nivel más cercano (más cerca = mayor bono). Quant: **alta** (FVG True + graded), **media** (graded solo), **baja** (ni true ni graded).
- **Invalidación externa.** Mitigación estándar del FVG (`f_updateZoneMitigation`, §2.2) — `gradedFvg` no añade invalidación propia, es un flag de calidad sobre el ciclo de vida existente.
- **Visual (jerarquía).** **Primario:** FVG `gradedFvg=true` fresco → caja con borde reforzado (mismo tratamiento que True FVG). **Secundario/Terciario:** heredan de la jerarquía FVG existente (§6.2.2). Sin toggle propio (usa `i_showFVG` existente + el flag interno).
- **MTF.** Transferible como parte del FVG (`bar_time` ya existente); el grid contra el que se evalúa puede ser HTF heredado (§6.3.36).

##### 6.3.39 [Propuesta, OPCIONAL] Grading de mecha REH/REL (§5.19 · T44) — **HERRAMIENTA, no confluencia** *(no aplica fallo de discriminación)*

- **Variante correcta / desempate.** Grid pequeño sobre `[min(open,close), high]` o `[low, max(open,close)]` del anchor REH/REL. **Descarta** (citable): graduar la mecha de un swing no confirmado.
- **Fuerza (0–1).** N/A directo (herramienta) — informa parcial obligatorio LQ↔CE y señal de debilidad si no alcanza CE.
- **Invalidación externa.** El anchor swing se invalida (nuevo swing dominante lo reemplaza) → el grid de mecha se descarta con él.
- **Visual (jerarquía).** **Terciario** por defecto (matiz fino, satura fácil): solo `i_densidad=Todo` o panel T14. Toggle `i_showWickGrading`.
- **MTF.** Rara vez se transfiere (microestructura del anchor en su propio TF); cap mínimo, igual que Volume Imbalance (§6.3.26).

---

## §6 — Checklist de 7 pasos por concepto (T41–T44)

Idéntico al proceso canónico de `ESQUELETO-P1 §1` / `reglas-smc-ict.md §0`. Por cada uno de T41, T42, T43, (T44 si se activa):

1. **[ ] Spec cuantificada** en `reglas-smc-ict.md` (migrar la ficha de §4 de este documento, resolver los `⏳` con `≥3 casos reales + ≥1 contraejemplo` EURUSD vía TV MCP).
2. **[ ] Función CORE pura** en `// === LIBRARY CORE ===` (Visual+Strategy idénticos) + `export` en Library — implementar los cuerpos `// TODO [impl]` de §2 de este documento.
3. **[ ] Compila 0/0** los 3 scripts + `scripts/check-core-sync.ps1` = OK.
4. **[ ] Validación `smc-validator-agent` ≥90`** contra la spec, con screenshots TV.
5. **[ ] Confluencia §4.8 registrada** — T41 NO (herramienta), T42 SÍ como candidata **#52** (mecanismo multiplicador, requiere **ADR-013** antes del wiring real F2-T01), T43 NO (refina #18/#20 vía flag `gradedFvg`), T44 NO (herramienta).
6. **[ ] Golden test MQL5** anotado (≥5 casos OHLC EURUSD; T41/T44 → verificar el cálculo del grid; T42 → verificar el bonus dado un `nSobreQuadrant` fijo; T43 → verificar el flag `gradedFvg`).
7. **[ ] Commit individual** por concepto (`feat(pine-core): F1-S1.7-T41 gradient levels núcleo`, etc.) + checkbox en `WORKPLAN-MAESTRO-V2.md` + `ESTADO-ACTUAL.md`.

**Orden de implementación recomendado:** T41 (núcleo, todo depende de él) → T43 (refinamiento FVG, bajo riesgo, no toca scoring) → T42 (requiere ADR-013 aprobado primero) → T44 (opcional, al final si se decide activar).

---

## §7 — Respuestas a las 8 preguntas de diseño abiertas (dossier §7)

1. **Rango-fuente.** Conjunto priorizado de 3 (P/D → suspension diario → opening gaps), NO un solo rango-fuente canónico. Selección determinista por prioridad + desempate `f_bodyRespectsLevel` (cuerpos-vs-nivel). Ver §1 de este esqueleto.
2. **Granularidad.** Quadrants **siempre** computados (0/0.25/0.5/0.75/1); eighths vía `input i_gradEighths` (default **true**, la doctrina los trata como la escala real de trabajo). Sixteenths **fuera de alcance** por ahora (declarado explícitamente, no se implementa).
3. **Naturaleza de confluencia.** T41 = contexto puro (no vota, como Std Dev). T42 = multiplicador post-hoc sobre `scoreDir_raw` (fórmula en §3), **requiere ADR-013** antes de wiring Fase 2 — no se improvisa dentro de `f_scoreConfluences` sin ese ADR. T43 = flag de calidad (`gradedFvg`) que eleva `strength`, sin número de confluencia nuevo.
4. **Tolerancia "toca/sobre un gradient level".** `input gradTol`, plausible **0.10–0.15×ATR14** (mismo orden que `eqThreshold`=0.1, `viThreshold`=0.05, `bprMinOverlap`=0.05) — valor exacto `⏳ [impl]` con casos EURUSD.
5. **Persistencia/carry-forward.** `gradPersistDays=5` (doctrina), grids viejos como ghost hasta ese tope y luego descartados — mismo mecanismo de cuota que P4/Present mode (`ESQUELETO-MITIGACION §2`) para no reventar el presupuesto de objetos (~500).
6. **Cuerpos vs mechas.** SÍ — la validación de "sobre un nivel" para el desempate de rango-fuente (§1) y para T43 usa **cuerpos** (open/close); las mechas son tolerancia adicional, no el criterio primario (doctrina §2.8 explícita: "cuerpos = order-flow institucional").
7. **T44 (grading de mecha).** Entra al esqueleto (§5.19/§6.3.39) pero **opcional/diferible** — el `[impl]` decide si se codifica en el mismo sprint que T41–T43 o queda en backlog explícito.
8. **MTF.** Los gradient levels de un rango-fuente HTF son **globales**: se computan UNA VEZ en el TF-fuente (igual que Opening Gaps §6.3.32 y el propio P/D) y se heredan por nivel a TFs menores — NO se recomputan por TF.

---

## §8 — Restricciones duras verificadas (checklist de cumplimiento, dossier §8)

- [x] **Anti-repaint.** Todo grid se fija en la confirmación de su rango-fuente (`barstate.isconfirmed`); ningún cálculo intra-vela (§1, §4 "Confirmación/anti-repaint" de cada ficha).
- [x] **Core byte-idéntico.** Todas las funciones de §2 van en `// === LIBRARY CORE ===` idéntico Visual/Strategy + `export` Library.
- [x] **Funciones CORE puras.** `f_computeGradientLevels`, `f_gradientZone`, `f_nearGradientLevel`, `f_bodyRespectsLevel`, `f_gradientConfluenceBonus` reciben datos por parámetro; `f_selectGradientSource` es wiring de consumidor, no CORE.
- [x] **Símbolo-agnóstico.** Ningún horario ni nivel hardcodeado a EURUSD ni a índices; índice-only (#6-9 del dossier) queda fuera (§0).
- [x] **No duplicar.** T41 generaliza `f_premiumDiscount` (no lo reemplaza — sigue existiendo para el uso binario premium/discount existente); T43 refina `f_detectFVG` con un flag, no crea un FVG paralelo.
- [x] **No inflar las 42 confluencias sin criterio.** Solo T42 es candidata nueva (**#52**), y explícitamente gateada por ADR-013 antes de contar en el scoring real.
- [x] **Pesos/umbrales congelados hasta Fase 3.** Todo valor numérico queda `⏳` en §4; `gradMultMax` y la forma de `f_gradientConfluenceBonus` explícitamente marcados "calibración Fase 3".
- [x] **Compila 0/0.** N/A todavía (esqueleto, no código) — queda como criterio del checklist §6 paso 3.

---

## §9 — Integración pendiente (a futuro — NO ejecutada en este documento)

Por instrucción explícita del usuario, este documento entrega **solo el esqueleto**. Cuando se decida avanzar al relleno, faltará:

1. **`docs/planes/MATRIZ-conceptos-cobertura.md`** — el dossier original (S077) refería una "tabla B1" con los candidatos #1–#10 de la familia gradient; **esa tabla NO existe físicamente todavía** en `MATRIZ-conceptos-cobertura.md` (el archivo actual es de S032, base "No soy liquidez", 64 conceptos, y no menciona gradient levels). Falta añadirla como sección nueva cuando se integre.
2. **`docs/workplan/PINE-PLAN.md §7`** — añadir T41–T44 al checklist de sprint (mismo tratamiento que T26–T40 en Sprint 1.6).
3. **`WORKPLAN-MAESTRO-V2.md §4.8`** — nota de expansión análoga a la de Sprint 1.6 ("~8-9 confluencias candidatas... #43-#51"), agregando **#52** y aclarando que T41/T43/T44 NO inflan el conteo.
4. **`ADR-013`** (candidato, nuevo) — el mecanismo multiplicador de T42 antes de tocar `f_scoreConfluences` en Fase 2 (F2-T01).
5. **`ESTADO-ACTUAL.md`** — reemplazar la entrada "Gradient Levels → Ultracode (pendiente)" por "esqueleto entregado (`ESQUELETO-P4-gradient-levels.md`), pendiente relleno" (vía `smc-doc-updater`, protocolo de cierre normal).

El siguiente paso real de ejecución (fuera de este documento): Claude Code toma T41 primero, extrae ≥3 casos EURUSD + 1 contraejemplo por TV MCP para cada `⏳`, implementa `f_computeGradientLevels`/`f_gradientZone`/`f_nearGradientLevel`/`f_bodyRespectsLevel` en el CORE, compila 0/0, valida ≥90, commit — y repite para T43, luego T42 (tras ADR-013), luego decide T44.

---

## §10 — Índice de referencias (trazabilidad)

- **Dossier de origen:** `docs/planes/DOSSIER-gradient-levels-para-ultracode.md` (S077) — doctrina verbatim §2, alcance §3, reto §4, infraestructura §5, formato §6, preguntas §7, restricciones §8.
- **Doctrina fuente:** `Mente/Mentores/ict/knowledge/madre-2026.md` (VAULT, fuera de git) — mismas referencias `:línea` que el dossier (§2.1-§2.8).
- **Formato + proceso + reglas duras:** `docs/planes/ESQUELETO-P1-conceptos-EA-pine-repos.md` §0/§1 (mismo proceso de 7 pasos, mismo formato de ficha); `docs/planes/ESQUELETO-MITIGACION-conceptos.md` §2 (patrones P1-P4 de ciclo de vida, de donde se deriva la variante "grid persistente en frontera" de T41).
- **Infra Pine existente (no duplicar):** `docs/reglas-smc-ict.md` §2.3 P/D (`:299-321`), §5.10 Opening Gaps (`:863-881`), §5.11 Std Dev (`:883-894`), §5.1 True FVG (patrón de flag de calidad, `:728-739`), §6.3.29/§6.3.31/§6.3.32 (precedentes MTF de herramienta/serie-de-niveles).
- **CORE actual:** 1517 líneas SHA `80fad14dd8d03758`; `pine/SMC-Library.pine` (KIND hasta 52, `SMC_Zone`/`SMC_Pool`/`SMC_Event` en líneas 96-138, `f_premiumDiscount` línea 919, `f_projStdDev` línea 663).
- **Confluencias:** `WORKPLAN-MAESTRO-V2.md §4.8` (catálogo actual + nota de expansión Sprint 1.6, candidatos #43-#51 ya asignados a T26-T40).

---

*Fin del esqueleto. Ningún `.pine` tocado, ningún valor numérico final decidido, ningún caso EURUSD inventado. Listo para que cualquier IA ejecute el relleno (§6) empezando por T41.*
