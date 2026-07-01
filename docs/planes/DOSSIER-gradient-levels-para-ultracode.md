# DOSSIER — Gradient Levels (candidato #1) → información completa para ULTRACODE

> **Sesión:** S077 · Fase 1 · rama `pine/sistema-completo`.
> **Qué es:** el **paquete de información completa** sobre el concepto **Gradient Levels / grading por quadrants–eighths** (candidato **#1** de `MATRIZ-conceptos-cobertura.md`, "la columna vertebral del 2026") para que **ULTRACODE construya el ESQUELETO de regla**. Este documento **NO es el esqueleto** y **NO es código**: es el briefing con doctrina verbatim, mecánica cuantificable, infraestructura Pine ya existente, el reto de diseño central y las restricciones duras.
> **Reparto de trabajo (confirmado por el usuario, S077):**
> - **Ultracode** → diseña el **esqueleto de regla** (estructura de secciones en formato `reglas-smc-ict.md`, funciones `f_*` a crear, UDT/`KIND`, `inputs` ATR-relativos, decisión de confluencia, orden de integración, preguntas de diseño resueltas y slots `⏳ [impl]`).
> - **Claude Code (después)** → **rellena** el esqueleto (cuantifica umbrales, extrae casos EURUSD por TV MCP, implementa las funciones puras, compila 0/0, valida ≥90, commit) siguiendo el proceso canónico de 7 pasos.
> - **Gobernanza [[sprint16-gate-reglas-antes-de-codigo]]:** NADA se codifica sin regla cuantificada en `docs/reglas-smc-ict.md` (umbrales + casos EURUSD) ANTES. El esqueleto es el paso previo a ese relleno.
> **Léelo junto a:** `docs/reglas-smc-ict.md` (fuente de verdad SMC + formato de ficha), `docs/planes/MATRIZ-conceptos-cobertura.md` (inventario/priorización), `docs/planes/ESQUELETO-P1-conceptos-EA-pine-repos.md` (§0 reglas duras, §1 proceso canónico + plantilla de ficha), `docs/workplan/PINE-PLAN.md` (§2 UDTs, §3 catálogo `f_*`, §5 dibujo), `CLAUDE.md` (reglas duras del proyecto), ADR-001/002.

---

## §0 — La tarea concreta de ULTRACODE

Construir el **esqueleto de regla** de la **familia Gradient Levels** para insertarlo (como sección nueva `§N.N` y sub-fichas MTF `§6.3.x`) en `docs/reglas-smc-ict.md`, en el **formato canónico del proyecto** (ver §6 de este dossier). El esqueleto debe:

1. **Decidir el alcance** de la familia a esqueletizar ahora (ver §3): el **núcleo #1** (grading de un rango en quadrants/eighths) es obligatorio; #2 (confluencia exponencial), #3 (FVG-válido-por-gradient) y #5 (grading de mecha) son los refinamientos que cuelgan de él. Ultracode decide cuáles entran como fichas propias y cuáles como notas de refinamiento.
2. **Resolver el reto central** (§4): definir la política determinista de **rango-fuente** — de qué rangos concretos y ya-computables en Pine se derivan los gradient levels. Sin esto, el concepto es discrecional y NO pasa el gate.
3. **Proponer la firma de funciones** `f_*` puras del CORE (nombre, parámetros, qué devuelven), el/los `KIND`/UDT nuevos si aplican, y los `inputs` (todos ATR-relativos donde sean tolerancias).
4. **Decidir la naturaleza de confluencia** de cada pieza (¿confluencia propia nueva en las 42? ¿multiplicador/peso? ¿filtro? ¿herramienta de contexto?) — ver §5.5 y la regla dura §5.9 de `ESQUELETO-P1`.
5. **Dejar slots `⏳ a cuantificar [impl]`** en todo valor numérico que dependa de casos EURUSD reales (que Claude Code extraerá por TV MCP), y `// TODO [impl]` en cuerpos de función. Ultracode **no inventa** umbrales finales ni casos.
6. **Enumerar las preguntas de diseño abiertas** (§7) con una recomendación por cada una, para que el relleno no re-litigue.

---

## §1 — El concepto en una frase

**Gradient levels** = tratar **toda referencia como un RANGO graduado, no como una línea suelta**: se mide un rango fuente y se divide en **high / upper-quadrant (0.75) / midpoint = CE = equilibrium (0.5) / lower-quadrant (0.25) / low**, y opcionalmente en **eighths (octavos: 0.125, 0.375, 0.625, 0.875)** y hasta sixteenths. La tesis del 2026 (february-28, verbatim del mentor): **este grid de gradient levels PRE-UBICA todas las PD arrays** — "all of your key PD arrays are going to form around in close proximity to one of these gradient levels". Un OB/FVG/pool que **yace sobre un gradient level está validado**; uno suelto sin gradient level **no** ("por eso fallan las FVG/OB de los fake-ICT").

Es **contexto + capa de calidad/scoring**, no una zona de entrada nueva. Generaliza lo que Pine ya hace en pequeño con **Premium/Discount/Equilibrium** (§2.3, que es exactamente "rango dividido en mitad superior/inferior con banda de equilibrium al 50%") a: (a) **más granularidad** (quadrants → eighths), y (b) **más rangos-fuente** que solo el dealing range swing-high↔swing-low.

---

## §2 — Doctrina fuente (verbatim + cuantificado)

Todo extraído de `Mente/Mentores/ict/knowledge/madre-2026.md` (VAULT, fuera de git — es conocimiento propio del proyecto, no referencia externa prohibida). Referencias `archivo:línea` para trazar.

### 2.1 Núcleo — grading del rango (january-12, "la pieza central de 2026") · `madre-2026.md:90-94`
- **"We're just measuring a range and dividing it into mid range, upper quadrant, lower quadrant and high and the low."** Esto **elimina la ambigüedad** de trendlines/soporte diagonal.
- **Escala continua** (`:182`): quadrant levels + upper/lower quadrant ("encroachment") + **eighths (octavos)** + sixteenths. "I originally started with gradients because saying quadrants makes it hard to segue into eighths and sixteenths." → el grading NO es solo 4 cuadrantes; es una escala.
- **Eighth 0.125** (`:232`) = mitad entre el high del gap y el primer quadrant (0.25). Relative-equal-highs convergen en el eighth.
- **Persistencia ≥5 días** (`:93`, `:322`): mantener PD arrays/opening gaps viejos en el chart aunque se llenen — son puntos de referencia del algoritmo. Los cuerpos respetan los octant/quadrant de los ORG de días **pasados** (carry-forward, "ghosting": niveles agrupados en consolidación = se usa uno por varios).

### 2.2 Confluencia EXPONENCIAL nivel∩quadrant (january-12 verbatim, núcleo del año) · `madre-2026.md:92, :287`
- **"the probability of it running to them increases *exponentially* if it's part of or around a *quadrant level* of the entirety of the range."** → un nivel (REH/REL, FVG, pool) que coincide con un quadrant del rango mayor tiene probabilidad mucho más alta. **Candidato a multiplicador de score** (no voto plano).

### 2.3 FVG válido = toca un gradient level (february-11, filtro operable) · `madre-2026.md:101-103, :209`
- **"high probability FVGs form in close proximity and are *touching one of the gradient levels*... if it's not doing these things it's *not a valid fair value gap*. Not all FVGs are created equal."**
- Fuente del grid para FVG: **Fib del suspension block diario** (highest-high → low) extendido a la derecha (`:135, :207`). Uso del FVG válido: target / stop / partial / entry.

### 2.4 Validación del OB por gradient + jerarquía parent/propulsion (march-13) · `madre-2026.md:327-328`
- **El parent OB DEBE yacer sobre un gradient level** (p.ej. quadrant 0.25 del ORG) — "this is what's validating it". El **propulsion block** (la vela que baja DENTRO del parent OB) NO necesita gradient level: "toma prestada" la discount-sensitivity del parent. (Jerarquía padre-hijo de PD arrays.)

### 2.5 Grading de la MECHA de un REH/REL (january-12, refinamiento fino) · `madre-2026.md:96-99, :183`
- REH/REL: **anchor = la vela más a la IZQUIERDA** (swing high/low más extremo). Si ese anchor tiene mecha, **graduar la mecha** (LQ / CE / UQ) — "we grade those because they're gaps".
- El precio a menudo **solo entra a un quadrant de la mecha y rechaza** (no toma el nivel completo) → donde el novato falla. **Parcial obligatorio entre LQ y CE de la mecha**; si no alcanza siquiera el CE al subir → **debilidad → señal de reversión**.
- **Premium/discount wick relativo al precio ACTUAL** (april-20, `:116`): mecha **premium** si está por encima del precio de mercado actual, **discount** si por debajo; usar su **CE** como nivel.

### 2.6 Regla WICK vs FVG adyacente (fina, operable) · `madre-2026.md:263`
- Si un SIBI (FVG bajista) está **inmediatamente a la derecha de una mecha** (0 velas de separación) → NO usar el FVG, **graduar la MECHA**. Si hay **≥1 vela de separación** → el FVG SÍ es válido como PD array. (Criterio determinista para elegir wick-grading vs FVG.)

### 2.7 Grading del gap tras displacement (escala operable) · `madre-2026.md:253, :360`
- El retroceso que no llega al CE (0.5) → cuerpos bajo CE = debilidad; wicks pueden llegar a 0.625 pero **fallar el 0.75 (upper quadrant) = reversión**. Escala **0.5 / 0.625 / 0.75** operable.
- **Discount gap vs premium gap + octantes del ORG** (`:360`): cerrar por debajo del "lowest octant" del gap = señal de que NO correrá a full-gap-closure (cuerpos en mitad inferior = bearish).

### 2.8 Cuerpos-vs-mecha = el TEST determinista de qué nivel adoptar · `madre-2026.md:408, :440, :479`
- Firma recurrente de todo abril: **los CUERPOS respetan el gradient level; las MECHAS pueden dañar** más allá. "Test cuerpos-vs-gradient-line = order-flow institucional." Si el precio NO usa los gradientes de un rango-fuente y SÍ los de otro (los cuerpos se recuestan sobre el nivel) → adoptar ese. (Criterio de desempate entre rangos-fuente candidatos.)

---

## §3 — Alcance de la familia (qué esqueletizar ahora)

De `MATRIZ-conceptos-cobertura.md` (tabla B1) y `madre-2026.md:143-158`. La familia gradient cuelga de #1:

| # | Pieza | Estado Pine | Candidato a | ¿En esqueleto S077? |
|---|-------|-------------|-------------|---------------------|
| **1** | **Grading quadrants/eighths del rango** | FALTA | contexto/score (base) | **SÍ — núcleo obligatorio** |
| **2** | **Confluencia exponencial nivel∩quadrant** | FALTA | **multiplicador de score** | **SÍ — la razón de ser de #1** |
| **3** | **FVG válido = toca gradient level** | PARCIAL (FVG ya existe) | filtro/peso de FVG | **SÍ — refinamiento de `f_detectFVG`** |
| 5 | Grading de mecha REH/REL + parcial LQ–CE | FALTA | gestión/invalidación | Ultracode decide (más discrecional; ver §7) |
| 4 | HRLR vs LRLR por barcoding | FALTA | gate de régimen del run | **NO** — familia distinta (candidato aparte, no gradient) |
| 6–9 | OR 9:30–10:00 / FHDR / 10am-high / wick-ATH | FALTA | **índice-only** | **NO** — diferir a Fase 5 (perfil índices), ADR-001 |
| 10 | Event Horizon = 50% entre 2 pools | FALTA | nivel/target | **NO** — candidato limpio propio, no gradient |

**Recomendación de alcance:** el esqueleto cubre **#1 + #2 + #3** como una sola familia coherente (grading como motor, confluencia exponencial como su consumidor de score, FVG-válido como el primer refinamiento aplicado). #5 (grading de mecha) es opcional — es el más discrecional y el que más depende de resolver el anchor de REH/REL. Los índice-only NO entran (contaminarían EURUSD-primero, ADR-001).

---

## §4 — EL RETO CENTRAL: rango-fuente determinista

Este es el problema que hace-o-rompe el concepto. El grading es trivial (dividir `[low, high]` en fracciones); lo difícil es **qué rango se gradúa**, de forma **determinista y reproducible** (no discrecional), y **símbolo-agnóstica**. El mentor usa muchos rangos-fuente; hay que mapear cuáles ya existen en Pine y son deterministas.

**Rangos-fuente que el mentor gradúa (de la doctrina §2):**
- Dealing range swing-high↔swing-low → **YA EN PINE** como `f_premiumDiscount` (§2.3, strong high↔strong low). *Base natural.*
- Suspension block diario (Fib highest-high→low) → **PARCIAL**: hay Volume Imbalance (§5.5) y "suspension = VI doble" (MATRIZ #20, PARCIAL); el rango-fuente diario habría que construirlo.
- Opening gaps: NWOG / NDOG / NYMO / ORG → **YA EN PINE** como `f_detectOpeningGaps` (§5.10, T30) = serie de niveles con `(close_previo, open_nuevo)` y punto medio. *Rango-fuente listo para graduar.*
- Primera hora 9:30–10:30 (FHDR) / OR 9:30–10:00 → **índice-only, DIFERIR** (Fase 5).
- Mecha de un swing/REH-REL → geométrico (§2.5), determinista si el anchor del REH/REL lo es.

**Inventario de infraestructura Pine ya disponible para el rango-fuente** (ver §5): Premium/Discount (dealing range), Opening Gaps (serie NWOG/NDOG/ORG), swings (strong/weak high-low), pools/EQH-EQL. Todos deterministas y ATR-relativos.

**Lo que ultracode debe fijar en el esqueleto:** una **política de selección de rango-fuente** — p.ej. "el gradient grid se computa sobre {dealing range P/D, opening gaps serie, suspension block diario}, cada uno con su `f_*` fuente ya existente; se prioriza por [criterio]; el desempate entre rangos candidatos usa el test cuerpos-vs-nivel (§2.8)". Sin esta política, el relleno no tiene dónde anclar los casos EURUSD.

---

## §5 — Qué YA existe en Pine (no duplicar; construir encima)

CORE actual: **1517 líneas, SHA `80fad14dd8d03758`**, compila 0/0 los 3, core-sync OK. Piezas relevantes (de `reglas-smc-ict.md`):

- **§2.3 Premium / Discount / Equilibrium `f_premiumDiscount`** (`reglas:299-321`) — **el germen directo de gradient levels.** Dealing range = último **strong high** ↔ **strong low**; `eq` = 50%; banda equilibrium `[45%, 55%]`; confluencia **#31** (en equilibrium resta 50% del peso). *Gradient levels = generalizar esto a quadrants/eighths y a más rangos-fuente.*
- **§5.10 Serie de gaps de apertura `f_detectOpeningGaps`** (T30, `reglas:863-881`) — NWOG/NDOG/NYMO/ORG + Breakaway; nivel ancla `open_nuevo` + punto medio del gap; `gapMin=0.5×ATR14`, `orgMinutes=15`. *Rango-fuente listo.*
- **§2.1 Order Blocks `f_detectOB`** + §2.2 FVG `f_detectFVG` — las PD arrays que el grading debe **validar/filtrar** (#3). FVG ya distingue True FVG (T26), IFVG (T27), BPR (T28). OB ya tiene invalidación por localización P/D (`reglas:1018`, #31).
- **Swings** `f_detectSwings` (strong/weak high-low, swingLen=5/internalLen=3) — anclas de rango y de REH/REL.
- **Pools / EQH-EQL** (§3, `f_detectEQ`, pools persistentes T09b/T10) — niveles que el grading marca como "sobre quadrant" o no.
- **§5.11 Standard Deviation `f_projStdDev`** (T36) — herramienta de proyección, **no confluencia**; precedente de "pieza que mide sin votar" (útil para decidir la naturaleza de #1 como contexto).
- **Infra MTF** (ADR-010, buffers de 6 campos `[kind,top,bottom,dir,tA,tB]`, `f_computeTFState`, `f_drawMTFZones`) — cómo un concepto se hereda cross-timeframe. Los gradient levels de un rango HTF (diario) deben poder heredarse a M5 (son globales una vez fijado el ancla — ver §6.3.x precedentes).

**Constantes `KIND` en uso:** hasta 52 (VI/BAG/CISD/VACUUM/IPR/INSIDEDAY/SMT). Si el grid necesita un `KIND` nuevo (p.ej. `KIND_GRADIENT`), sería ≥53.

---

## §6 — Formato de salida esperado (esqueleto en formato canónico)

El esqueleto que produzca ultracode debe seguir la **plantilla de ficha de `reglas-smc-ict.md`** (copiada de `ESQUELETO-P1 §1`):

```
### <§N.N> <Nombre del concepto> `f_detect<X>` · T<NN>
**Concepto.** <prosa desde la doctrina §2 de este dossier; cero invención>
**Definición cuantificada.** <reglas medibles; toda tolerancia × ATR(n)>   ⏳ a cuantificar [impl]
**Mitigación / ciclo de vida.** <patrón P1–P4 de ESQUELETO-MITIGACION, o "evento/contexto persistente">
**Parámetros default.** | Param | Default | Nota |   ⏳ (rango plausible; valor exacto = Fase 3)
**Confirmación / anti-repaint.** <cuándo se confirma; barstate.isconfirmed>
**Contraejemplo.** <qué NO es>   ⏳
**Casos de prueba** (EURUSD, TV MCP): ✓ ✓ ✓ + ✗   ⏳PENDIENTE-TVMCP
```

Más, por cada pieza, la **sub-ficha MTF `§6.3.x`** con los 5 ejes del proyecto (ver cualquier §6.3.x existente, p.ej. `reglas:1330`): **Variante correcta/desempate · Fuerza (0–1) · Invalidación externa · Visual (jerarquía primario/secundario/terciario + toggle) · MTF (cómo se hereda)**.

Y el **checklist de proceso canónico de 7 pasos** (`ESQUELETO-P1 §1`) por cada concepto, para que el relleno lo ejecute en orden: (1) spec cuantificada → (2) función CORE pura → (3) compila 0/0 + core-sync → (4) validación ≥90 → (5) confluencia §4.8 registrada → (6) golden test MQL5 anotado → (7) commit individual.

---

## §7 — Preguntas de diseño abiertas (ultracode resuelve con recomendación)

Para que el relleno NO re-litigue, el esqueleto debe pronunciarse sobre:

1. **Rango-fuente (el reto §4):** ¿un solo rango-fuente canónico (recomendado: dealing range P/D como base + opening gaps serie) o un conjunto priorizado? ¿Cómo se selecciona determinísticamente? ¿Se aplica el test cuerpos-vs-nivel (§2.8) como desempate?
2. **Granularidad:** ¿quadrants (0/0.25/0.5/0.75/1) siempre y eighths como `input` opcional? ¿Sixteenths se implementan o se declaran fuera de alcance?
3. **Naturaleza de confluencia:** #1 grading = ¿contexto puro (como Std Dev, no vota) o entra a las 42? #2 confluencia exponencial = **multiplicador** de score, no voto plano — ¿cómo se modela un multiplicador en un scoring que hoy es suma ponderada? (impacta Fase 2/3). #3 FVG-válido = ¿peso extra al FVG existente (#) o filtro que lo degrada si NO toca gradient?
4. **Tolerancia "toca/sobre un gradient level":** ¿`≤ k×ATR14` de distancia al nivel? Fijar el `input` (p.ej. `gradTol`), valor exacto ⏳ [impl].
5. **Persistencia / carry-forward:** ¿se mantienen los grids de rangos-fuente de los últimos N días (doctrina ≥5, §2.1)? ¿Cómo se limita el nº de líneas para no reventar el límite de objetos Pine (~500)?
6. **Cuerpos vs mechas:** ¿la validación usa CUERPOS (close/open) contra el nivel, con la mecha como tolerancia? (doctrina §2.8 dice cuerpos = institucional).
7. **#5 grading de mecha:** ¿entra al esqueleto o se difiere? Depende de tener el anchor de REH/REL determinista.
8. **MTF:** los gradient levels de un rango diario son **globales** (mismos en todo TF) — ¿se computan una vez en el TF-fuente y se heredan por nivel (como P/D), o se recomputan por TF?

---

## §8 — Restricciones duras que el esqueleto DEBE respetar (de `CLAUDE.md` + `ESQUELETO-P1 §0`)

1. **Anti-repaint `[D-PINE-03]`:** eventos solo en `barstate.isconfirmed`; `request.security(..., lookahead=barmerge.lookahead_off)` SIEMPRE. Un rango-fuente HTF se confirma al cierre del HTF.
2. **Core byte-idéntico (regla #2):** funciones nuevas en la sección `// === LIBRARY CORE ===` idéntica en Visual+Strategy, `export` en Library. Tras tocar CORE → `scripts/check-core-sync.ps1` = OK.
3. **Funciones CORE puras:** reciben datos por parámetro, no leen series globales ni `request.security()`, no dibujan (habilita golden tests MQL5, ADR-002). Estado `var` y dibujo en el consumidor.
4. **Umbrales relativos a ATR (regla #3):** toda tolerancia `× ATR(n)` como `input`. Reusar inputs existentes donde aplique.
5. **Símbolo-agnóstico `[ADR-001]`:** nada hardcodeado a EURUSD ni a horarios de índices; lo por-símbolo va como perfil/input. Índice-only → diferir Fase 5.
6. **No duplicar (regla §0.8):** verificar en §5 de este dossier y en `reglas-smc-ict.md` que no exista ya (Premium/Discount, Opening Gaps, FVG ya están).
7. **No inflar las 42 confluencias sin criterio:** decidir explícitamente confluencia-propia vs refinamiento/multiplicador/herramienta.
8. **Pesos/umbrales congelados hasta Fase 3 `[ADR-002]`:** el esqueleto define **mecánica**; los valores exactos se calibran IS/OOS. Slots `⏳`.
9. **Compila 0/0 (regla #7):** el relleno commitea un concepto verificado a la vez.

---

## §9 — Índice de referencias (trazabilidad)

- **Doctrina:** `Mente/Mentores/ict/knowledge/madre-2026.md` — §A grading `:90-94`, confluencia exponencial `:92,:287`, §C FVG-válido `:101-103,:209`, jerarquía OB/parent `:327-328`, §B mecha REH/REL `:96-99`, eighths `:182,:232`, wick vs FVG adyacente `:263`, cuerpos-vs-nivel `:408,:440,:479`, carry-forward `:322`, discount/premium gap octantes `:360`.
- **Inventario/priorización:** `docs/planes/MATRIZ-conceptos-cobertura.md` tabla B1 (#1–#5), líneas de Tier A (`:172-173`), reto rango-fuente (`:237`).
- **Formato + proceso + reglas duras:** `docs/planes/ESQUELETO-P1-conceptos-EA-pine-repos.md` §0 (reglas duras), §1 (7 pasos + plantilla).
- **Infra Pine existente:** `docs/reglas-smc-ict.md` §2.3 P/D (`:299-321`), §5.10 Opening Gaps (`:863-881`), §5.11 Std Dev (`:847-861`), §6.3.x formato MTF (`:1330-1336`).
- **CORE actual:** 1517 líneas SHA `80fad14dd8d03758`; `pine/SMC-Visual.pine`, `pine/SMC-Strategy.pine`, `pine/SMC-Library.pine`.

---

*Fin del dossier. Ultracode: produce el esqueleto de regla de la familia Gradient Levels (#1+#2+#3, opcional #5) en el formato §6, resolviendo el reto §4 y las preguntas §7 con recomendación, respetando §8. Claude Code rellenará después (casos EURUSD + implementación + validación).*
