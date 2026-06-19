# Esqueleto de integración — PARTE 1: Gap de conceptos → Pine + Motor del EA + Repos

> **Sesión:** S032 · Fase 1 · rama `pine/sistema-completo`.
> **Qué es:** el *esqueleto* (estructura + ruteo + contratos + orden) para integrar al sistema los ~24 conceptos ICT/SMC que los mentores enseñan y el Pine **aún no detecta** (`docs/planes/MATRIZ-conceptos-cobertura.md`), por **el mismo proceso completo** que pasaron T01–T10. Incluye el esqueleto del **motor de razonamiento del EA** (donde viven los "modelos de entrada") y el **orden de integración de los repos** del plano EA/Pine.
> **Qué NO es:** NO es código, NO inventa definiciones SMC ni casos. Cada valor a medir queda `⏳ a cuantificar [impl]` y cada cuerpo de función `// TODO [impl]`. NO toca ningún `.pine` (no rompe *compila 0/0* ni *core byte-idéntico*) ni `reglas-smc-ict.md` todavía. Es el plano que la siguiente IA (**[impl]**) ejecuta.
> **Partición (decisión del usuario, S032):** esta es la **PARTE 1 (EA + Pine + repos)**. Todo lo de **Hermes + enjambre** (runtime del enjambre, agente piloto NSL, almacenamiento, tools de orquestación) es la **PARTE 2** y se diseña en la sesión siguiente — ver §8.
> **Léelo junto a:** `docs/reglas-smc-ict.md` (fuente de verdad SMC + formato de ficha), `docs/planes/MATRIZ-conceptos-cobertura.md` (inventario de entrada), `docs/workplan/PINE-PLAN.md` (§2 UDTs, §3 catálogo `f_*`, §5 dibujo, §7 sprints, §10 testing), `WORKPLAN-MAESTRO-V2.md` §4.8 (42 confluencias), `docs/workplan/MQL5-PLAN.md` §golden tests, `docs/planes/ESQUELETO-MITIGACION-conceptos.md` (patrones P1–P4 de ciclo de vida), `docs/planes/HANDOFF-OPUS-MAX-ea-razonamiento-y-enjambre.md` (§3.A motor EA, §3.D gap, §7/§9 repos), ADR-001/002/005/007.

---

## §0 — Reglas duras que el implementador DEBE respetar (innegociables)

Copiadas de `CLAUDE.md` + `MATRIZ §D` + handoff §4. Si el esqueleto y una regla chocan, **manda la regla**.

1. **Proceso completo, sin atajos.** Cada concepto nuevo recorre las **7 etapas** de §1, exactamente como T01–T10. No se "marca como hecho" un concepto que no pasó validación ≥90 ni golden test.
2. **Anti-repaint `[D-PINE-03]`.** Todo *evento* se evalúa SOLO en `barstate.isconfirmed`; las *zonas* pueden extenderse en vivo pero su creación se confirma al cierre. `request.security(..., lookahead = barmerge.lookahead_off)` SIEMPRE.
3. **Core byte-idéntico (regla #2).** Toda función nueva del núcleo va en la sección `// === LIBRARY CORE ===` **idéntica** en `SMC-Visual.pine` y `SMC-Strategy.pine`, y en versión `export` en `SMC-Library.pine`. Tras tocar el CORE → `scripts/check-core-sync.ps1` = OK.
4. **Funciones CORE puras.** Reciben datos por parámetro (precios, arrays), no leen series globales ni `request.security()`, no dibujan. Esto habilita los **golden tests MQL5 (ADR-002)**. El estado `var` y el dibujo viven en el consumidor.
5. **Umbrales relativos a ATR (regla #3).** Nada de pips fijos. Toda tolerancia/umbral nuevo se expresa `× ATR(n)` (declarar qué ATR) y entra como `input`. Reusar inputs existentes donde aplique (`i_fvgThreshold`, `i_poolTol`, `i_eqThreshold`…).
6. **Compila 0/0 (regla #7).** Un commit = un concepto verificado, 0 errores / 0 warnings en los 3 scripts.
7. **Símbolo-agnóstico `[ADR-001]`** y **umbrales/pesos congelados hasta Fase 3 `[ADR-002]`.** El esqueleto define la **mecánica** de cada concepto; los pesos y el threshold se calibran en Fase 3 (IS/OOS). NO se "ajustan" a ojo.
8. **No duplicar lo existente.** Antes de esqueletizar/implementar un concepto, **verificar en `MATRIZ §B` y en `reglas-smc-ict.md`** que no exista ya (T01–T10). Solo se construye lo ❌ faltante o se refina lo 🔶, nunca se recrea un ✅.
9. **No inflar las 42 confluencias sin criterio (handoff §3.D).** Cada primitiva nueva se decide explícitamente: ¿confluencia propia nueva o refina una existente? (ver §5). Una herramienta de medición/proyección (p. ej. Standard Deviation) puede NO ser confluencia sino insumo de SL/TP o de bias.
10. **El EA no consulta LLM en runtime (ADR-005/007).** El motor del EA (§3) razona **determinista**; el enjambre alimenta vía validación IS/OOS, nunca en vivo.

---

## §1 — El proceso canónico por concepto (el "mismo paso a paso" que pasó T01–T10)

Derivado de `PINE-PLAN §7/§10`, `reglas-smc-ict.md §0` y `MQL5-PLAN §golden tests`. **Cada ficha de §4 lleva estos 7 checkboxes**; el `[impl]` no avanza al siguiente hasta cerrar el anterior.

1. **[ ] Spec cuantificada** en `reglas-smc-ict.md` con el formato canónico (ver plantilla abajo). Incluye **≥3 casos reales + ≥1 contraejemplo en EURUSD con fecha-hora GMT**, extraídos del gráfico vía **TradingView MCP** (no se inventan) → mientras no se extraen, quedan `⏳PENDIENTE-TVMCP`.
2. **[ ] Función CORE pura** `f_detect<X>` en la sección LIBRARY CORE (Visual+Strategy idénticos) + `export` en Library. Define UDT/`kind`, parámetros (inputs ATR-relativos) y el **patrón de ciclo de vida** (P1–P4 de `ESQUELETO-MITIGACION §2`) si la marca/zona persiste.
3. **[ ] Compila 0/0** los 3 scripts (`pine_set_source` → `pine_smart_compile` → `pine_get_errors`) + `scripts/check-core-sync.ps1` = OK.
4. **[ ] Validación `smc-validator-agent` ≥90** contra la spec, con screenshots de TV como evidencia; score a `docs/sprint-runs/validaciones.md`.
5. **[ ] Confluencia §4.8** registrada (nueva # o refinamiento de existente, según §5) con `input.float` peso = 1.0 (plano hasta Fase 3) — wiring real del scoring es Fase 2 (F2-T01).
6. **[ ] Golden test MQL5** anotado: ≥5 casos OHLC reales EURUSD con la detección esperada (evento+precio+tiempo); criterio **0 dif en eventos, ±1 tick en niveles** (`MQL5-PLAN §167`). Se construye en Fase 4, pero la **firma pura** debe quedar lista para él desde ya.
7. **[ ] Commit individual** (`feat(pine-core): F1-S1.6-T<NN> <concepto>`) + checkbox en `WORKPLAN-MAESTRO-V2.md` + actualización `ESTADO-ACTUAL.md`.

**Plantilla de ficha (formato `reglas-smc-ict.md`)** — el `[impl]` la rellena y la migra a la fuente de verdad:

```
### <§N.N> <Nombre del concepto> `f_detect<X>`
**Concepto.** <descripción en prosa — de la ficha del mentor, cero invención>
**Definición cuantificada.** <reglas medibles; toda tolerancia × ATR(n)>  ⏳ a cuantificar [impl]
**Mitigación / ciclo de vida.** <patrón P1–P4 o "evento puntual"; estados>  ⏳
**Parámetros default.** | Param | Default | Nota |  ⏳ (rango plausible; valor exacto = Fase 3)
**Confirmación / anti-repaint.** <cuándo se confirma; isconfirmed>
**Contraejemplo.** <qué NO es — para no marcar ruido>  ⏳
**Casos de prueba** (EURUSD, TV MCP): ✓ ✓ ✓ + ✗  ⏳PENDIENTE-TVMCP
```

---

## §2 — Tabla maestra de ruteo (todos los conceptos faltantes → destino)

Refina `MATRIZ §C` en **6 rutas**. Solo se listan ❌ y 🔶; los ✅ (T01–T10) **no se re-esqueletizan** (regla §0.8). "Tarea" usa la numeración nueva de §6.

| # MATRIZ | Concepto | Estado | **Ruta** | Destino / Tarea |
|---|---|---|---|---|
| 7 | Vacuum Block | ❌ | **A** primitiva | Pine — T33 |
| 13 | Propulsion Block | ❌ | **A** primitiva | Pine — T34 |
| 17 | Volume Imbalance | ❌ | **A** primitiva | Pine — T31 (familia con SIVI/BIVI) |
| 23 | SIVI / BIVI | ❌ | **A** primitiva | Pine — T31 (familia) |
| 27 | Immediate Rebalance (IR) | ❌ | **A** primitiva | Pine — T29 (familia FVG) |
| 46 | Balanced Price Range (BPR) | ❌ | **A** primitiva | Pine — T28 (familia FVG) |
| 43 | CISD (Change in State of Delivery) | ❌ | **A** primitiva | Pine — T32 (familia estructura) |
| 45 | Breakaway Gap (BAG) | ❌ | **A** primitiva | Pine — T30 (familia gaps de apertura) |
| 60 | IPR (Imbalanced Price Range) | ❌ | **A** primitiva | Pine — T35 |
| 36 | Standard Deviation | ❌ | **A** herramienta | Pine — T36 (proyección; ¿no-confluencia? ver §5) |
| 26 | IFVG (Inversion FVG) | 🔶 | **A** variante propia | Pine — T27 (FVG + inversión de rol) |
| 61 | True FVG (T.FVG) | 🔶 | **A** variante propia | Pine — T26 (refina FVG) |
| 64 | Inside Day | ❌ | **A** patrón diario | Pine — T37 |
| 19/29/30/42 | NWOG / NYMO / ORG / NDOG | 🔶 | **A** serie de niveles | Pine — T30 (extiende `f_sessionOpens` §4.2) |
| 14 | SMT Divergence | ❌ | **A** primitiva especial | Pine — T38 **(requiere símbolo correlacionado → sub-decisión de arquitectura / ADR, §4 Ruta A)** |
| 49 | Draw on Liquidity (DOL) | ❌ | **B** sesgo | bias/scoring — Sprint 2.1 |
| 22 | IRL vs ERL | 🔶 | **B** framework | bias/scoring — Sprint 2.1 (formaliza interna/externa) |
| 54 | HRLR (High Resistance Liquidity) | ❌ | **B** framework | calidad de pool — Sprint 2.1 |
| 55 | LRLR (Low Resistance Liquidity) | ❌ | **B** framework | calidad de pool — Sprint 2.1 |
| 16 | IPDA & PD Arrays | ❌ | **B** framework | contexto/lookback — Sprint 2.1 |
| 40 | PDArray Matrix | ❌ | **B** framework | contexto — Sprint 2.1 |
| 21 | IOFED | ❌ | **C** modelo de entrada | **Motor EA §3** (Fase 4) |
| 31 | ICT Entry Model 2022 | ❌ | **C** modelo de entrada | **Motor EA §3** (Fase 4) |
| 33 | Low Hanging Fruit | ❌ | **C** modelo de entrada | **Motor EA §3** (Fase 4) |
| 39 | Unicorn Model | 🔶 | **C** composición | **Motor EA §3** (Breaker #22 + FVG #26) |
| 41 | MMXM (Market Maker Model) | ❌ | **C** modelo completo | **Motor EA §3** (Fase 4) |
| 63 | Silver Bullet | ❌ | **C** modelo time-based | **Motor EA §3** (Fase 4) |
| 12 | Power of 3 (AMD) | ❌ | **C** modelo/contexto | **Motor EA §3** (compone Judas+displacement) |
| 28 | NY Lunch Macro | ❌ | **D** tiempo/macro | extiende `f_killZone` §3.4 — T39 |
| 37/38 | Opening Range / NY Lunch Hour Macro | ❌ | **D** tiempo/macro | extiende `f_killZone` §3.4 — T39 |
| 29 | NY Midnight Open (NYMO) | 🔶 | **D**+**A** | nivel (T30) + ventana macro (T39) |
| 57 | RTH vs ETH | ❌ | **D** tiempo/sesión | extiende `f_killZone` §3.4 — T40 |
| 59 | NFP Protocol | ❌ | **E** noticias | **gate determinista (ADR-005)**, NO confluencia — Fase 4/5 |
| 52 | Early Buyer & Early Seller | ❌ | **F** teoría | experimental post-Fase 3 (escrutar valor, campo 9) |
| 53 | Gray Pool Theory | ❌ | **F** teoría | experimental post-Fase 3 |
| 58 | Event Horizon | ❌ | **F** teoría | experimental post-Fase 3 |
| 62 | Price Delivery Continuum | ❌ | **F** teoría | experimental post-Fase 3 |
| 24 | Advanced Price Balancing | 🔶 | **F** / refina §2.2-§2.3 | escrutar: ¿aporta medible o reempaque? |
| 47 | Fair Valuation | 🔶 | **F** / refina §2.3 | escrutar: relacionado equilibrium |
| 35 | Reclaimed Order Block | 🔶 | refina §2.6/§2.1 | nota de refinamiento (sin tarea nueva salvo que la ficha lo justifique) |
| 48 | Liquidity Swap vs Run | 🔶 | refina §3.1/§3.2 | nota de refinamiento (formaliza distinción) |

> **Cobertura:** todos los ❌/🔶 de `MATRIZ §B` están aquí. Los ✅ (OB, FVG, P/D, EQH/EQL, OTE, Breaker, Rejection, Flip, MSS, Killzones, Pools, Sweep, Displacement, Dealing Range, Turtle Soup, Stop Raid, etc.) ya viven en `reglas-smc-ict.md` y no se tocan.

---

## §3 — Esqueleto del MOTOR DE RAZONAMIENTO DEL EA (handoff §3.A · Fase 4 · spec, no código)

> **Línea dura (ADR-007):** el EA razona **determinista y generalizable**; **nunca** consulta LLM en runtime. Aquí se define la *mecánica*, no se calibran pesos (ADR-002 — eso es Fase 3). Reutiliza `f_scoreConfluences` y `f_computeSLTP` (`PINE-PLAN §3.5`); **señala los refactors de Pine** que necesita.

### §3.1 — Modelo de combinación que GENERALIZA (no exact-match)
El scoring direccional (scoreLong/scoreShort, §4.8) debe **disparar con confluencia suficiente** aunque no sea la combinación exacta entrenada. Esqueleto del modelo a especificar:
- **Suma ponderada por familia** (Estructura / Liquidez / Zonas / P-D-Fib / ICT / EMAs): `scoreDir = Σ (peso_i × activa_i)` con `activa_i ∈ {0,1}` por confluencia direccional.
- **Mínimos por familia (gating):** la señal exige un mínimo en familias núcleo (p. ej. ≥1 de Estructura **y** ≥1 de Zonas/Liquidez) para evitar señales "infladas por EMAs". `// TODO [impl]: definir qué familias son obligatorias y el mínimo`.
- **Generalización:** una confluencia "similar-no-exacta" cuenta si pertenece a la misma familia y dirección (p. ej. cualquier zona alcista activa cerca del precio satisface "zona alcista", no un OB-H1 específico). `// TODO [impl]: definir la clase de equivalencia por familia`.
- **Threshold + dominancia direccional:** `scoreDir ≥ threshold ∧ scoreDir > scoreOpuesto` (threshold = Fase 3). `⏳`.
- **Cómo se MIDE** (handoff §3.A): cada confluencia expone un booleano direccional + su peso; el EA no "interpreta", **suma y compara**. Mismo cálculo que Pine → paridad.

### §3.2 — Los "modelos de entrada" (Ruta C) como patrones de confluencias + timing
NO son primitivas de Pine: son **combinaciones** que el motor reconoce. Esqueleto de mapeo (el `[impl]` cuantifica cada uno desde su ficha de mentor):
| Modelo (Ruta C) | Se expresa como | Primitivas que combina |
|---|---|---|
| **Unicorn** | Breaker + FVG solapados | #22 breaker + #26 FVG-CE (zona común) |
| **Silver Bullet** | displacement + FVG dentro de ventana horaria fija | #32 displacement + FVG + ventana (§3.4/D) |
| **Power of 3 (AMD)** | acumulación → manipulación (Judas/sweep) → distribución (displacement) | #13 Judas + #10 sweep + #32 displacement, secuenciados |
| **ICT Entry Model 2022** | sweep → CHoCH/MSS → FVG de retorno | #10/#16 + #1/#5 + #18/#20 |
| **IOFED** | entrada en FVG tras desplazamiento institucional | composición FVG + displacement |
| **Low Hanging Fruit** | objetivo de liquidez de baja resistencia | #9 pool objetivo + sesgo DOL (Ruta B) |
| **MMXM** | fases completas de market maker (acumulación/distribución) | composición de varias fases — el más interpretativo |
`// TODO [impl]: por modelo → secuencia exacta, ventana temporal, tolerancias (× ATR), y peso como "combo" (¿bonus al score o gate?). Decidir si un modelo cumplido añade peso o solo prioriza.`

### §3.3 — Contexto de zona en tiempo real (sin repaint / sin LLM)
El EA pondera "lo que pasa ahora en la zona donde puede actuar": mitigación viva (`SMC_Zone.state/mitigatedPct`), sweep reciente (`pool.swept`+`sweptBarTime`), premium/discount actual, sesión activa. `// TODO [impl]: definir el vector de contexto que entra al scoring y cómo modula los pesos sin violar D-PINE-03`.

### §3.4 — Trazabilidad Pine→MQL5 + refactors señalados
- Mapeo función-a-función (golden tests, ADR-002): cada `f_detect*`/`f_score*` → módulo `.mqh` (ver `MQL5-PLAN`).
- **Refactors de Pine que la generalización requiere** (marcar impacto en core-sync; nada se implementa aquí):
  - Exponer **scores parciales por familia** (no solo `scoreLong/scoreShort` agregados) → cambio en `f_scoreConfluences` (firma de salida). *Impacto:* CORE → core-sync + re-validación.
  - **Normalización ATR** de los aportes para portabilidad multi-símbolo (ADR-001).
  - **Umbrales por familia configurables** como inputs (no constantes).
  - Estos refactors entran como tareas de **Sprint 2.1 / Fase 4**, NO ahora (ADR-002 congela; aquí solo se señalan).
- R:R≥1:3 y SL/TP como parte del razonamiento: reusa `f_computeSLTP` (`PINE-PLAN §3.5`); si no hay R:R≥3 calculable → **no hay señal** (regla dura #5).

---

## §4 — Fichas esqueleto por concepto (Rutas A, B, D; C en §3; E/F resumidas)

> Cada ficha = plantilla de §1 en esqueleto. Reusa UDTs de `PINE-PLAN §2` (`SMC_Zone`/`SMC_Event`/`SMC_Pool`/`SMC_Swing`) y patrones de ciclo de vida P1–P4 de `ESQUELETO-MITIGACION §2`. **Cero invención**: la definición fina sale de la ficha del mentor + casos TV.

### RUTA A — Primitivas nuevas de Pine (pipeline estándar §1)

Familias para no duplicar máquina:
- **Familia FVG/imbalance** (reusa la máquina de `f_detectFVG` + `f_updateZoneMitigation`): T26 True FVG, T27 IFVG, T28 BPR, T29 Immediate Rebalance, T31 Volume Imbalance (+SIVI/BIVI).
- **Familia gaps de apertura** (reusa/extiende `f_sessionOpens` §4.2): T30 NWOG/NDOG/NYMO/ORG + Breakaway Gap.
- **Familia estructura** (reusa `f_detectBOS/CHoCH/MSS`): T32 CISD.
- **Propias:** T33 Vacuum, T34 Propulsion, T35 IPR, T36 Standard Deviation, T37 Inside Day, T38 SMT.

---

**T26 · True FVG (T.FVG) `f_detectTrueFVG`** — *variante 🔶 de FVG (§2.2)*
- **Concepto.** FVG "verdadero" dentro de un rango/contexto institucional (subtipo de FVG con criterio de calidad extra). ⏳ confirmar definición con ficha.
- **Definición cuantificada.** Sobre `f_detectFVG` existente, añade un filtro de validez (p. ej. dentro del dealing range, alineado con displacement). `⏳ a cuantificar [impl]`.
- **CORE.** NO nueva máquina: bandera/refinamiento sobre `SMC_Zone` KIND_FVG (¿`KIND_TFVG` o flag?). Patrón **P2** (4 estados, reusa `f_updateZoneMitigation`).
- **Confluencia §4.8.** Refina #18/#20 (FVG H1/chart), no nueva. Ver §5.
- **Checkboxes §1:** [ ]spec [ ]core [ ]0/0+sync [ ]val≥90 [ ]confluencia [ ]golden [ ]commit.

**T27 · IFVG — Inversion FVG `f_detectIFVG`** — *variante propia 🔶 de FVG*
- **Concepto.** Un FVG **roto** (mitigado/invalidado) que **invierte su rol** (alcista→resistencia y viceversa), análogo al breaker pero sobre FVG.
- **Definición cuantificada.** Cuando una `SMC_Zone` KIND_FVG pasa a `state=3 invalidada` → re-crear como `KIND_IFVG` con `dir` invertido (mismo patrón que `f_detectBreaker` §2.6 sobre OB). `⏳`.
- **CORE.** Patrón **P2** + génesis tipo breaker. Reusa `f_updateZoneMitigation`. Nuevo `KIND_IFVG`.
- **Confluencia §4.8.** **Nueva candidata** (#43 IFVG alineado) o agrupada con breaker #22. Ver §5.
- **Checkboxes §1.**

**T28 · BPR — Balanced Price Range `f_detectBPR`** — *primitiva nueva (FVGs opuestos solapados)*
- **Concepto.** Dos FVG de dirección opuesta que se solapan → zona de "precio balanceado" de fuerte reacción.
- **Definición cuantificada.** Detectar solape entre un FVG alcista y uno bajista recientes; zona BPR = intersección. `⏳ (ventana de búsqueda, solape mínimo × ATR)`.
- **CORE.** Patrón **P2** (zona con 4 estados). Nuevo `KIND_BPR`. Reusa `f_detectFVG` como insumo + `f_updateZoneMitigation`.
- **Confluencia §4.8.** Nueva candidata. Ver §5.
- **Checkboxes §1.**

**T29 · Immediate Rebalance (IR) `f_detectImmediateRebalance`** — *primitiva nueva*
- **Concepto.** Vela que **rebalancea de inmediato** (sin dejar gap): el precio vuelve a su rango en la vela siguiente — contrario al FVG (que deja ineficiencia).
- **Definición cuantificada.** ⏳ (patrón de 2-3 velas sin gap residual; criterio de "rebalance completo").
- **CORE.** Evento puntual (patrón **P4**) o marca sobre `SMC_Event` (`KIND_IR`). Puro.
- **Confluencia §4.8.** Probable refinamiento de contexto (no zona). Ver §5.
- **Checkboxes §1.**

**T30 · Serie de gaps de apertura — NWOG/NDOG/NYMO/ORG + Breakaway Gap `f_detectOpeningGaps`** — *extiende `f_sessionOpens` (§4.2)*
- **Concepto.** Niveles-gap por apertura: New Week Opening Gap, New Day Opening Gap, NY Midnight Open, Opening Range Gap; + Breakaway Gap (gap de ruptura).
- **Definición cuantificada.** Sobre la frontera de sesión/día/semana, capturar el gap entre cierre previo y apertura → nivel(es) de S/R. ⏳ (qué fronteras, cómo se mide el gap en FX 24h, prox × ATR).
- **CORE.** Extiende `f_sessionOpens`; niveles como `SMC_Event`/líneas. Breakaway Gap puede ser `KIND_BAG` propio.
- **Confluencia §4.8.** Refina #36 (session open cercano) como **serie de niveles**; Breakaway Gap candidato a nueva. Ver §5.
- **Checkboxes §1.**

**T31 · Volume Imbalance + SIVI/BIVI `f_detectVolumeImbalance`** — *familia primitiva nueva*
- **Concepto.** Micro-gap entre **cuerpos** de velas con solape de **mechas** (a diferencia del FVG, que es gap entre extremos). SIVI/BIVI = variantes (sell-side / buy-side imbalance).
- **Definición cuantificada.** ⏳ (gap entre `close[n]` y `open[n-1]` con solape de mechas; umbral × ATR). SIVI/BIVI = lado.
- **CORE.** Zona micro (patrón **P2** ligero) o marca; nuevo `KIND_VI` (+ subtipo). Reusa máquina de mitigación.
- **Confluencia §4.8.** Nueva candidata (imbalance fino) o refina FVG. Ver §5.
- **Checkboxes §1.**

**T32 · CISD — Change in State of Delivery `f_detectCISD`** — *familia estructura*
- **Concepto.** Cambio en el "estado de entrega" del precio por **cierre** (pariente de CHoCH/MSS, pero con criterio de delivery).
- **Definición cuantificada.** ⏳ (cierre que rompe la secuencia de entrega previa; relación exacta con CHoCH/MSS — distinguir, no duplicar §1.4/§1.5).
- **CORE.** `SMC_Event` `KIND_CISD`. Reusa lógica de cierre de `f_detectCHoCH`. Anti-repaint por cierre.
- **Confluencia §4.8.** Candidata a refinar familia Estructura (#1–#8) o nueva. Ver §5.
- **Checkboxes §1.**

**T33 · Vacuum Block `f_detectVacuumBlock`** — *primitiva nueva*
- **Concepto.** Bloque-vacío por apertura/noticia (gap grande sin negociación), imán de retorno.
- **Definición cuantificada.** ⏳ (gap de apertura ≥ umbral × ATR; zona = vacío).
- **CORE.** Zona (patrón **P2**), `KIND_VACUUM`. Relación con T30 (gaps de apertura) — decidir si es subtipo.
- **Confluencia §4.8.** Nueva candidata. Ver §5.
- **Checkboxes §1.**

**T34 · Propulsion Block `f_detectPropulsionBlock`** — *primitiva nueva*
- **Concepto.** OB **dentro de** otro OB (continuación): el precio respeta una sub-zona del OB original y propulsa.
- **Definición cuantificada.** ⏳ (OB anidado; criterio de "dentro de"; dir de continuación).
- **CORE.** Zona derivada de OB (patrón **P2**), `KIND_PROPULSION`. Reusa `f_detectOB` + `f_updateZoneMitigation`.
- **Confluencia §4.8.** Nueva candidata o refina #17/#19 (OB). Ver §5.
- **Checkboxes §1.**

**T35 · IPR — Imbalanced Price Range `f_detectIPR`** — *primitiva nueva*
- **Concepto.** Rango de precio desbalanceado (acumulación de ineficiencias en una dirección).
- **Definición cuantificada.** ⏳ (rango con N FVG/imbalances del mismo lado; medida del desbalance).
- **CORE.** Zona/contexto (patrón **P2** o bias). `KIND_IPR`. Posible insumo de §3 (motor EA).
- **Confluencia §4.8.** Ver §5.
- **Checkboxes §1.**

**T36 · Standard Deviation `f_projStdDev`** — *herramienta de proyección (¿NO confluencia?)*
- **Concepto.** Proyección por desviaciones estándar de un swing/rango para fijar objetivos (no es una zona detectada, es una **medición**).
- **Definición cuantificada.** ⏳ (anclas del rango; múltiplos -1/-2/-2.5/-4 como objetivos).
- **CORE.** Función pura de proyección (no detección). Devuelve niveles. **Probable insumo de `f_computeSLTP`/TP, NO confluencia de score** (regla §0.9). Ver §5.
- **Checkboxes §1** (sin confluencia; en su lugar: integración a SL/TP).

**T37 · Inside Day `f_detectInsideDay`** — *patrón diario*
- **Concepto.** Día cuyo rango está contenido en el del día previo (compresión → expansión).
- **Definición cuantificada.** ⏳ (`high[D] < high[D-1] ∧ low[D] > low[D-1]`; se evalúa en D1).
- **CORE.** `SMC_Event` `KIND_INSIDEDAY` sobre snapshot D1 (MTF, `PINE-PLAN §4`). Anti-repaint (D1 confirmado).
- **Confluencia §4.8.** Contexto/volatilidad. Ver §5.
- **Checkboxes §1.**

**T38 · SMT Divergence `f_detectSMT`** — *primitiva especial — REQUIERE DECISIÓN DE ARQUITECTURA*
- **Concepto.** Divergencia entre dos símbolos correlacionados (uno hace HH, el otro LH) → señal de manipulación.
- **Bloqueo de diseño.** Necesita **datos de un símbolo correlacionado** (segundo `request.security` a otro ticker). Esto es una decisión de arquitectura (símbolo-agnóstico ADR-001: ¿qué par correlaciona con cuál? input de "símbolo SMT"). **Candidato a ADR propio** antes de implementar.
- **CORE.** Función pura que recibe dos series de swings (la del chart + la del correlacionado, obtenida en el consumidor vía security). `KIND_SMT`.
- **Confluencia §4.8.** Nueva candidata fuerte (señal de calidad). Ver §5.
- **Checkboxes §1** + **[ ] ADR de arquitectura SMT** (precede a la implementación).

### RUTA B — Sesgo / contexto (alimenta bias/scoring, NO es zona) → Sprint 2.1

> No son `f_detect*` de zona; **modulan la dirección/calidad** del scoring. Detección ligera donde haga falta (p. ej. clasificar pools), wiring real en el scoring (Fase 2/3).

- **DOL — Draw on Liquidity.** Sesgo direccional clave: hacia dónde es atraído el precio (siguiente pool de alta liquidez no barrido). Alimenta el bias global y el motor EA (§3.2 Low Hanging Fruit). `// TODO [impl]: derivar DOL del set de pools (SMC_pools) no barridos + estructura; ¿confluencia de dirección o input de bias?`.
- **IRL vs ERL (Internal/External Range Liquidity).** Formaliza qué liquidez es interna al rango (FVG/OB) vs externa (EQH/EQL/swings). Clasifica los pools/zonas existentes. `// TODO [impl]: etiquetar SMC_Pool/SMC_Zone como IRL/ERL según el dealing range (§2.3)`.
- **HRLR / LRLR (High/Low Resistance Liquidity Run).** Calidad de la liquidez: cuán "limpio" es el camino a un pool (pocos obstáculos = LRLR, fácil de alcanzar). Modula el **peso** de la confluencia "pool objetivo" #9. `// TODO [impl]: métrica de obstáculos entre precio y pool`.
- **IPDA (Interbank Price Delivery Algorithm) + PD Arrays + PDArray Matrix.** Marco de lookback (20/40/60 días) + paraguas que organiza todas nuestras zonas como "PD arrays" en premium/discount. Es **contexto**, no detección nueva: reencuadra lo que ya detectamos. `// TODO [impl]: ventana de lookback como input; matriz que rankea zonas por premium/discount (reusa §2.3)`.

### RUTA D — Tiempo / sesión / macro → extiende `f_killZone` (§3.4)

- **T39 · Macros intradía** (NY Lunch, Opening Range, NY Lunch Hour). Ventanas de **minutos** dentro de las KZ. Extiende `f_killZone` para devolver también "macro activa". `⏳ (horarios exactos local+DST, como §3.4)`. Confluencia: refina #34 (Kill Zone) con sub-ventana, no nueva. Anti-repaint por reloj (no repinta).
- **T40 · RTH vs ETH** (Regular/Extended Trading Hours — relevante a futuros/índices, símbolo-agnóstico ADR-001). Input de perfil de sesión. `⏳`. Modula confluencia #34 / filtro de calidad.
- **NYMO (NY Midnight Open).** Doble naturaleza: **nivel** (→ T30) + **ancla temporal de macro** (→ T39).

### RUTA E — Noticias → gate determinista (ADR-005), NO confluencia

- **NFP Protocol.** No es confluencia de gráfico. Es el **gate funcional determinista** de ADR-005 (veto binario alrededor de noticias de alto impacto). Vive en el EA (Fase 4) + el puente vivo del enjambre (Parte 2). Fuente de calendario = TBD (decisión Fase 4). `// Anotar en MQL5-PLAN como SMC_NewsGate; NO entra a §4.8`.

### RUTA F — Teorías a escrutar → experimental post-Fase 3 (R-08/P-10)

> Se esqueletizan con ficha **mínima** + criterio de admisión: **solo entran si demuestran lift OOS** o si la ficha del mentor (campo 9 "Conflictos con el sistema") prueba que son medibles y no reempaque de lo existente. NO entran al pipeline Fase 1.

- **Gray Pool Theory, Event Horizon, Price Delivery Continuum, Early Buyer/Seller:** ficha mínima (concepto + ¿qué sería medible?) → bucket `Tier 3 experimental`. Decisión de incluir = gate de lift OOS (post-Fase 3).
- **Advanced Price Balancing, Fair Valuation:** probable **reempaque** de FVG/equilibrium (§2.2/§2.3). Escrutar contra la ficha; si no aportan medida nueva → se descartan (no se implementan por completitud).

### Variantes 🔶 que solo refinan (sin tarea nueva salvo justificación)

- **Reclaimed OB** (#35): nota sobre §2.6/§2.1 (OB recuperado tras invalidación parcial). El `[impl]` decide si es un estado extra de la máquina OB o un caso de breaker/flip ya cubierto.
- **Liquidity Swap vs Run** (#48): nota sobre §3.1/§3.2 formalizando la distinción (swap = intercambio de roles de liquidez; run = barrido direccional).

---

## §5 — Expansión de las 42 confluencias (§4.8) sin romper lo validado

> **Marco (ADR-002 + handoff §3.D):** la **lista** de confluencias puede ampliarse ahora (el scoring aún no está implementado — F2-T01 es Fase 2), pero los **pesos** se calibran en Fase 3. **No inflar sin criterio:** cada primitiva nueva se decide *confluencia propia* vs *refina existente*. El número final y la inclusión los confirma el `[impl]` al implementar, validados contra el scoring.

| Concepto (tarea) | Propuesta | # | Justificación |
|---|---|---|---|
| True FVG (T26) | **Refina** #18/#20 | — | Es un FVG de mayor calidad, no un objeto nuevo. |
| IFVG (T27) | **Nueva** (o agrupa con #22) | #43? | Comportamiento propio (inversión de rol), como el breaker para OB. |
| BPR (T28) | **Nueva** | #44? | Zona de reacción distinta (solape de FVGs opuestos). |
| Immediate Rebalance (T29) | **Refina** contexto | — | Matiza la eficiencia; no es zona operable independiente. |
| Gaps de apertura (T30) | **Refina** #36 (serie) | — | #36 ya es "session open cercano"; se amplía a serie de niveles. |
| Breakaway Gap (T30) | **Nueva** | #45? | Gap de ruptura con dirección propia. |
| Volume Imbalance/SIVI/BIVI (T31) | **Nueva** (1 confluencia familia) | #46? | Imbalance fino direccional; 1 sola confluencia (no 3, evita doble conteo P-05). |
| CISD (T32) | **Nueva** o refina Estructura | #47? | Pariente de CHoCH/MSS; decidir si suma señal propia o refina #5. |
| Vacuum Block (T33) | **Nueva** | #48? | Imán de retorno propio. |
| Propulsion Block (T34) | **Refina** #17/#19 (OB) | — | Es un OB de continuación; refuerzo, no objeto nuevo. |
| IPR (T35) | **Nueva** o contexto | #49? | Probable contexto de bias más que confluencia puntual. |
| Standard Deviation (T36) | **NO confluencia** | — | Herramienta de proyección → insumo de SL/TP (`f_computeSLTP`), no suma al score. |
| Inside Day (T37) | **Nueva** (contexto) | #50? | Señal de compresión/expansión; peso bajo. |
| SMT Divergence (T38) | **Nueva** (fuerte) | #51? | Señal de calidad; sujeta a ADR de símbolo correlacionado. |
| DOL (Ruta B) | **Bias global** | — | Modula dirección, no es confluencia sumable individual. |
| IRL/ERL, HRLR/LRLR, IPDA, PDArray (Ruta B) | **Modulan pesos** | — | Calidad/contexto: afectan el peso de #9 (pool) y la localización P/D, no añaden #. |
| Macros / RTH-ETH (Ruta D) | **Refina** #34 | — | Sub-ventanas de Kill Zone. |

**Conclusión §5:** ~8–9 confluencias nuevas candidatas (#43–#51, números tentativos), el resto refina. El `[impl]` cierra la numeración al cablear F2-T01; los pesos = Fase 3.

---

## §6 — Orden de sprints y tareas nuevas (extiende `PINE-PLAN §7` / WORKPLAN Fase 1)

**Nuevo Sprint 1.6 — "Gap conceptos ICT (primitivas)"** — continúa tras T25 (Tier 2). Orden **de mayor palanca/menor riesgo a menor** (primero lo que reusa máquinas validadas):

1. **Reusan la máquina FVG/zona (riesgo bajo):** T26 True FVG → T27 IFVG → T28 BPR → T29 Immediate Rebalance.
2. **Extiende `f_sessionOpens` (riesgo bajo):** T30 gaps de apertura (NWOG/NDOG/NYMO/ORG + Breakaway).
3. **Reusan estructura/OB:** T32 CISD → T34 Propulsion Block.
4. **Detección propia (riesgo medio):** T31 Volume Imbalance (+SIVI/BIVI) → T33 Vacuum Block → T35 IPR → T37 Inside Day.
5. **Herramienta:** T36 Standard Deviation (integra a SL/TP, no a score).
6. **Bloqueada por arquitectura:** T38 SMT Divergence (precede **ADR SMT**).

**Otras rutas:**
- **Ruta D** → **T39 macros intradía + T40 RTH/ETH**: extensión de T11 (Kill Zones), Sprint 1.3 ampliado o anexo a 1.6.
- **Ruta B** (DOL, IRL/ERL, HRLR/LRLR, IPDA, PDArray) → **Sprint 2.1** (scoring): se cablean cuando exista `f_scoreConfluences`.
- **Ruta C** (modelos de entrada) → **Motor EA §3, Fase 4**.
- **Ruta E** (NFP) → **gate determinista, Fase 4/5**.
- **Ruta F** (teorías) → **bucket experimental post-Fase 3** (gate de lift OOS).

**Gate del nuevo sprint:** mismo que F1-GATE — cada concepto ≥90, anti-repaint, performance 20k barras, 0/0, core-sync. **Re-evaluar el presupuesto de objetos de dibujo** (`PINE-PLAN §5`): +~12 conceptos puede topar los 500 objetos/tipo → aplicar P4 "Present mode"/cuota por familia desde el inicio.

**Tabla de dependencias (qué necesita qué ya implementado):**
| Tarea | Depende de (ya ✅) |
|---|---|
| T26/T27/T28/T29 | T06 FVG + `f_updateZoneMitigation` (T05) |
| T30 | T (Session Opens §4.2 — pendiente de implementar en su sprint) |
| T32 | T03 BOS/CHoCH + T12 MSS |
| T34 | T05 OB |
| T31/T33/T35/T37 | UDTs base (T01) |
| T38 | **ADR SMT** + segundo `request.security` (MTF, `PINE-PLAN §4`) |
| T39/T40 | T11 Kill Zones |
| Ruta B | T09b pools + T08 EQH/EQL + T07 P/D |
| Motor EA §3 | scoring F2-T01 + todas las primitivas Ruta A/B |

---

## §7 — Repos / herramientas del plano EA/Pine: veredicto + orden de integración

> Construye sobre la investigación de S031 (handoff §7/§9). Decisión explícita por repo: **Adoptar / Probar / Rechazar / Diferir** + "qué verificar antes". **Solo el plano EA/Pine/repos**; lo de Hermes/enjambre → §8 (Parte 2). Regla: **no adoptar a ciegas**, elegir el set mínimo coherente.

| # | Repo / herramienta | Plano | Decisión | Orden | Qué verificar antes de adoptar |
|---|---|---|---|---|---|
| 1 | **`MobiusQuant/OpenMobius-skill`** (conocimiento ICT/SMC) | Gap de conceptos | **Probar (alta prioridad)** | **AHORA** (acelera §4 Ruta A) | Cruzar su catálogo de conceptos vs `MATRIZ §B`: ¿cubre Vacuum/CISD/VI/IPR con definiciones cuantificables que aceleren las fichas? ¿Licencia compatible? NO copiar definiciones sin verificarlas contra TV (cero invención). |
| 2 | **`multi-agent-investment` / `FinStep-AI/ContestTrade`** | Precedente de diseño | **Adoptar como referencia** (no software) | AHORA (informa §3) | Solo como precedente de ADR-007 ("LLM propone, capa determinista decide"). Su integración como software es plano enjambre → Parte 2. |
| 3 | **MT5 MCPs** (`ariadng/metatrader-mcp-server`, `Qoyyuum/mcp-metatrader5-server`) | EA Fase 4 | **Diferir a Fase 4** | Fase 4 | Solo-lectura para laboratorio MT5 (la escritura la hace el EA nativo). Verificar al elegir broker (F4-T00). No instalar ahora. |
| 4 | **`DietrichGebert/ponytail`** (anti-sobre-ingeniería) | EA/MQL5 Fase 4 | **Diferir / opcional** | Fase 4 | Filosofía ya cubierta por `reglas-dev.md` + regla #7. Valor incremental bajo en Pine; posible en MQL5. No prioridad. |
| 5 | **CallMeBot** (API WhatsApp/Telegram) | Notificador EA/gate | **Diferir a Fase 4-5** | Fase 4-5 | Encaja como notificador del EA vivo / gate de noticias. Solo alertas, **nada sensible** (publica a un tercero). Anotar en MQL5-PLAN. |
| 6 | **`atilaahmettaner/tradingview-mcp`** (TV alterno) | Tooling | **Rechazar (por ahora)** | — | Ya tenemos el fork TV MCP operativo (MCP-02). Solo de referencia si el fork se rompe. |

**→ Plano enjambre/Hermes (NO en esta parte, ver §8):** `mnemox-ai/tradememory-protocol`, `TauricResearch/TradingAgents`, `itechmeat/open-second-brain`, `witt3rd/oh-my-hermes`, `Headroom`, ZenMux/Nemotron. Se evalúan y ordenan en la Parte 2 (un solo sustrato de memoria + un solo andamiaje de orquestación, no apilar).

---

## §8 — Qué queda para la PARTE 2 (Hermes / enjambre — siguiente sesión)

Diferido por decisión del usuario (S032). Para que la siguiente sesión arranque sin re-derivar, queda pendiente diseñar el **esqueleto** de:
- **Runtime del enjambre** (handoff §3.B): vigía/cron que toma confluencias vía TV MCP (single-instance CDP 9222), protocolo de discusión rondas 1/2 + voto estructurado, regla de registro de positivas con autoría, scoring/atribución de agentes.
- **Agente piloto NSL completo** (handoff §3.E): perfil/skill, carpetas de knowledge, herramientas Hermes que usa, cómo entra al loop y emite voto → **plantilla parametrizable** para clonar al resto de mentores.
- **Traza end-to-end + almacenamiento** (handoff §3.C/§8): enjambre → diario laboratorio → validación IS/OOS → cristalización → Pine → EA; fuente única en Obsidian, lectura on-demand, sin duplicar transcripciones crudas.
- **Set mínimo de repos/tools de enjambre** (handoff §7/§9.A): elegir UNO de {tradememory-protocol, open-second-brain, gbrain} como memoria y UNO de {oh-my-hermes, construir a mano} como orquestación; ZenMux/Nemotron como proveedores; Headroom solo si topan límites.
- **Conexión con esta Parte 1:** el enjambre **descubre/valida** confluencias del set ampliado (§2/§4) y alimenta el motor EA (§3) vía IS/OOS — nunca en runtime.

---

## §9 — Documentos relacionados
- Inventario de entrada: `docs/planes/MATRIZ-conceptos-cobertura.md`.
- Plantilla de estilo + patrones de ciclo de vida P1–P4: `docs/planes/ESQUELETO-MITIGACION-conceptos.md`.
- Fuente de verdad SMC + formato de ficha (modelo §2.1/§2.2/§2.3): `docs/reglas-smc-ict.md`.
- Plan Pine (UDTs/catálogo/sprints/dibujo/testing): `docs/workplan/PINE-PLAN.md`.
- Confluencias §4.8 + tareas Fase 1: `WORKPLAN-MAESTRO-V2.md`.
- Golden tests (criterio etapa 6): `docs/workplan/MQL5-PLAN.md`.
- Encargo y repos: `docs/planes/HANDOFF-OPUS-MAX-ea-razonamiento-y-enjambre.md` §3.A/§3.C/§3.D + §7/§9.
- ADRs: ADR-001 (símbolo-agnóstico), ADR-002 (congelación umbrales), ADR-005 (enjambre=laboratorio), ADR-007 (EA razona determinista).
