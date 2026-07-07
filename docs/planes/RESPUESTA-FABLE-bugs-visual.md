# RESPUESTA-FABLE — BUGS-VISUAL + esqueleto de ejecución para Opus

> **Responde a:** [`BUGS-VISUAL-fable-revision.md`](BUGS-VISUAL-fable-revision.md) (S099–S101) + 5 puntos nuevos entregados por el usuario en vivo (S102, 2026-07-07).
> **Emitido por:** Fable (revisión integral). **Ejecuta:** Opus, siguiendo el Bloque C **en orden estricto**.
> **Regla de oro de este documento:** todo campo `[RELLENAR-OPUS: …]` lleva su criterio de relleno. Si un criterio no se cumple o el código real difiere del ancla citada, **Opus se detiene y reporta — no improvisa**.
> **Anclas verificadas** sobre `pine/SMC-Visual.pine` @ commit `8618cc3` (CORE 1700 líneas, SHA `5510361166844bd5`). Si el archivo cambió, re-verificar cada ancla por contenido (grep del símbolo), no por número de línea.

---

## BLOQUE A — Veredictos sobre el documento BUGS-VISUAL

### A.1 · BUG #1 — VEREDICTO: root cause CONFIRMADO ✅ · fix aprobado

El análisis de S100/S101 es correcto al 100%. Verificación independiente (grep sobre el archivo completo):
- **No existe ninguna asignación `chartState.atr14 :=` en todo `SMC-Visual.pine`.** El default del UDT es `na` (línea 300).
- El local `float atr14 = ta.atr(14)` (línea **2006**) se usa en decenas de sitios pero **nunca se copia** a `chartState.atr14`.
- Consumidores que leen el campo muerto (los 6 colaterales): band-pick/anclas (`aAtr`, 2888, guard 2893), `f_posRole` (2788), `f_confDegree` (2808), rotación de bandas de profundidad (gate 2739 — exige `not na(chartState.atr14) and chartState.atr14 > 0`, siempre FALSE), guardián de pools (3394, vía `f_confDegree`), ribbon KZ (3012–3013, 3021).
- La ruta MTF (`f_drawMTFZones`) no lo lee → dibuja siempre. Síntoma exacto del doc.

**Respuesta a la Pregunta 1 (¿gatear en `isconfirmed`?):** NO gatear. La asimetría con `pdHigh/pdLow` es **correcta y deliberada**:
- `pdHigh/pdLow` son un **snapshot de niveles** (semántica: "el rango P/D congelado al cierre") → gate `isconfirmed` correcto.
- `atr14` es un **escalar de suavizado** que el path de presentación (`islast`, barra viva) necesita disponible SIEMPRE. La regla dura #1 (D-PINE-03) aplica a **eventos**; el dibujo en `islast` es presentación y no repinta eventos. Además, el único consumidor de `chartState.atr14` que toma decisiones persistentes (rotación de bandas, 2739) **ya exige `barstate.isconfirmed` por su cuenta** — doble protección.

**Respuesta a la Pregunta 2 (¿leer el atr local directo en el path de dibujo?):** NO. Razones: (a) un punto único de asignación = diff mínimo y auditable; (b) el contrato `SMC_TFState.atr14` **existe y debe estar poblado** para la paridad MQL5 (Fase 4, `SMC_MTF.mqh` traduce el UDT campo a campo — un campo fantasma que "a veces está" es una trampa de traducción); (c) tocar cada call-site (2788, 2808, 2888, 3012…) multiplica la superficie de error.

**Respuesta a la Pregunta 3 (¿vía de promoción para nativas importantes, tipo MB/BPR `confDegree≥2`?):** SÍ conceptualmente, pero **DIFERIDA al PASO 6** y **condicional al re-barrido**. Motivo: `f_confDegree` también estaba muerto por este mismo bug — no se sabe cómo se comporta la selección §7 completa (bandas + band-pick + guardianes) con el ATR vivo. Primero revivir el diseño existente, medirlo, y solo entonces decidir si hace falta la vía extra. No bloquea F1-GATE.

**FIX APROBADO (exacto):**
```pine
// tras la línea 2006 (float atr14 = ta.atr(14)):
chartState.atr14 := atr14
```
Sin gate. Sin `nz()` (si `ta.atr(14)` es `na` en las primeras barras, los guards `not na(...) and > 0` aguas abajo ya lo manejan — un `nz()` a 0 sería equivalente pero menos honesto).

### A.2 · BUG #2 / duda P/D del usuario — VEREDICTO doctrinal completo

El usuario pidió explícitamente saber si su entendimiento es correcto. Respuesta en cuatro partes:

1. **Anidamiento por TF: CORRECTO y YA IMPLEMENTADO.** Los rangos vivos anidan tal como su intuición espera: D1 [1.13246–1.20831] ⊃ H1 [1.13618–1.14730] ⊃ M5 [1.14085–1.14481] (verificado en vivo S100/S102). "Bajo más bajo pero más arriba / alto más alto pero más abajo al bajar de TF" = exactamente lo que ocurre.
2. **Ancla ATH/ATL histórico: NO es la doctrina ICT.** El Premium/Discount se mide sobre el **dealing range vigente** — el swing que se está operando. Con ATH (≈1.60, 2008) ↔ ATL, el precio quedaría marcando "discount" durante **años** y la lectura sería inoperable (nunca daría "premium" en un swing operable). Por eso el Premium D1 está en 1.20831 (alto del swing vigente) y no en 1.60. **En este punto el indicador está bien y la expectativa era la equivocada** — confusión razonable: son dos definiciones de rango que coexisten en la literatura SMC.
3. **El defecto REAL de la Opción A** (trailing extremes, LuxAlgo): el extremo cercano "camina" hacia el precio en tendencia. Conocido, decidido 2× por el usuario (S057, S091), documentado en [`docs/decisiones-pd-rango.md`](../decisiones-pd-rango.md) y **diferido a Fase 3 con datos OOS**. No se re-litiga aquí.
4. **Opción B candidata para el A/B de Fase 3** (registrar, sin código ahora): ancla **ESTRUCTURAL** — el rango entre el último swing high mayor y el último swing low mayor **confirmados por estructura** (structMajor), que solo rota cuando la estructura rota. Es lo más cercano a lo que el usuario espera sin caer en el ATH: rango estable dentro del swing, anidado por TF, sin "caminar".
   → `[RELLENAR-OPUS: añadir apéndice "Opción B — ancla estructural (candidata A/B Fase 3)" a docs/decisiones-pd-rango.md con este párrafo; criterio: no tocar la Opción A vigente ni ningún .pine]`

### A.3 · BUG #3 — VEREDICTO: sí es defecto de semántica · fix aprobado (solo panel)

**Respuesta a la Pregunta 1:** SÍ — la fila "Ocultos" debe contar **detectado − dibujado**, no el recorte de `f_keepBestPerBand`. La garantía §10-#8 / §1-7 ("nada desaparece en silencio") se refiere a lo detectado; medir solo el recorte del array de labels dibujadas es contar el último eslabón de la cadena e ignorar los anteriores.

**Respuesta a la Pregunta 2 (¿por qué H1 da 498/105 y M5 da 0/0?):** porque el contador actual mide el tamaño del array de labels **dibujadas** que el recorte tira. En M5 ese array llega minúsculo al recorte (Pine `max_labels_count` auto-borra las viejas + pocas labels se pushean en `islast`) → recorta ~0 → reporta 0, aunque de los 81 EQ detectados casi ninguno esté en el chart. En H1/D1 el array llega grande → números grandes. Mismo código, insumo distinto. SÍ conviene contar sobre los buffers nativos.

**Esqueleto del fix (PASO 3):**
- `hidEq := array.size(SMC_eqhl) − (nº de labels EQ vivas tras el recorte)` — el sustraendo es `array.size(SMC_eqLabels)` DESPUÉS de `f_keepBestPerBand` (línea 3336).
- `hidStruct` análogo: `(nº de eventos de estructura detectados) − array.size(SMC_structLabels)` tras el recorte (3299).
  → `[RELLENAR-OPUS: identificar el buffer contable de estructura detectada — candidatos: SMC_eventsMajor, el acumulador de f_drawStructure, o un contador int incremental nuevo en isconfirmed; criterio: debe contar TODOS los BOS/CHoCH/MSS confirmados de la historia visible, las 3 escalas o al menos la swing+major coherente con lo que se dibuja; si ningún buffer existente lo da, usar contador int var incremental (RE10045-safe), NUNCA un array nuevo]`
- Solo celdas del panel T14. Cero arrays nuevos en `islast`. No toca detección ni dibujo.

---

## BLOQUE B — Puntos nuevos (#4–#9, no estaban en BUGS-VISUAL)

### B.4 · #4 — El giro vigente (CHoCH/MSS) desaparece del chart nativo 🟠

**Síntoma (S102, D1):** el panel reporta "Último CHoCH 1.16551 · 14-05" pero en el chart no hay ninguna label CHoCH; se ven 2 BOS + 1 "BOS +". El usuario preguntó si el "BOS +" era su CHoCH — **NO**: el sufijo " +" es la escala dominante (SC_MAJOR, `f_drawStructure` con grosor 3, línea 3283–3289). El CHoCH existe pero su label fue desalojada.

**Causa doble (verificada):**
1. `STRUCT_OP_CAP = 3` (línea 3191): Operación conserva solo 3 labels de estructura vía `f_keepBestPerBand` (3299).
2. El "mejor giro por banda" de `f_keepBestPerBand` **degrada a recencia pura** porque las bandas de profundidad están muertas (gate 2739 con `chartState.atr14 = na` → BUG #1). Dos BOS recientes + un BOS+ desalojan al CHoCH vigente.

**Instrucción:** NO tocar nada en el PASO 1. El fix del BUG #1 revive las bandas → `f_keepBestPerBand` vuelve a repartir por banda y es plausible que el giro vigente sobreviva solo. **Si el re-barrido (PASO 2) muestra que sigue cayendo**, aplicar PASO 5: guardián del giro vigente — una label de estructura cuyo nivel coincide con `chartState.lastCHoCHPrice` o `chartState.lastMSSPrice` (±tol) es **inmune al recorte**, espejo exacto del guardián de pools (3394). El checklist §7.2 ya lo exige: "Giro vigente + flips en giro" debe verse.

### B.5 · #5 — Herencia de estructura D1→H1→M5 insuficiente 🟠

**Lo que el usuario pidió:** que los BOS/CHoCH **importantes** de D1 se hereden a H1, y los de D1+H1 a M5 — hoy se hereda alguno (el "CHoCH (H1)" visible en M5) pero no de forma fiable ni por importancia.

**Diagnóstico (verificado):** la herencia de estructura existe pero con dos defectos de diseño:
1. **Criterio de selección equivocado:** `f_nearestNEvents` (1809–1810) exporta los `capN` eventos **más cercanos al precio** — no los más importantes. Caps por defecto: `i_mtfCapBOS=1`, `i_mtfCapCHoCH=1` (143–144).
2. **Dedupe con pérdida:** el skip de la capa MTF (4079) calla el evento heredado cuando el nativo ya lo dibuja como "BOS+/CHoCH+" — pero si el recorte nativo luego lo tira (#4), el evento se pierde **por ambas vías**.

**Fix (PASO 4) — herencia estructural GARANTIZADA por escalares:** los campos `lastBOSPrice/Dir/Time`, `lastCHoCHPrice/Dir/Time`, `lastMSSPrice/Dir/Time` del HTF **ya viajan** en `SMC_TFState` (tuple 1837; el panel los muestra en sus columnas D1/H1). Solo falta dibujarlos:
- Extender `f_drawMTFState` (4007) para dibujar, además de bias+P/D, **el último BOS + último CHoCH (+ MSS si difiere del CHoCH)** del HTF como línea horizontal + label `"D1: CHoCH 1.16551"` (estilo/color de la capa MTF, grosor por procedencia como 4036).
- Determinista, ≤3 labels extra por HTF (M5 = +6 peor caso).
- **Presupuesto:** actualizar el mirror `f_mtfLblYield` (~2955) para contar las nuevas labels — si no, el budget ≤25 se rompe en silencio.
  → `[RELLENAR-OPUS: decidir si MSS se dibuja solo cuando |lastMSSPrice − lastCHoCHPrice| > tol (evitar doble label en el mismo nivel); criterio: tol = mtfMajTol ya existente (4118)]`
- **Dedupe (4079):** mantener el skip del nearest-N, pero las líneas garantizadas por escalares NO pasan por ese skip (son la red de seguridad). Si nativo y garantizada coinciden en nivel, deduplicar por tolerancia `mtfMajTol` **a favor de la garantizada MTF** solo cuando la nativa no exista ya en el chart.
- La herencia nearest-N actual se conserva como complemento (caps intactos — ADR-002 no cubre estos caps, pero no se suben sin ver el re-barrido).

### B.6 · #6 — Objetivos de liquidez en AMBAS direcciones y a cualquier distancia 🟠 REQUISITO FIRME

**Lo que el usuario pidió (criterio de aceptación, no negociable):** estando en un TF debe poder **proyectar hasta dónde puede ir el precio en ambas direcciones**: el SSL más cercano abajo, el BSL más cercano arriba, **y** los majors históricos no barridos (sus "Bajo más bajo 1/2" en 0.95653 / 0.90400; hacia arriba más allá del "BSL −3"). En caída con bajos-más-bajos por delante, hoy el chart no ofrece ningún objetivo inferior.

**Diagnóstico (anclas verificadas, gate en 3390–3405):**
- El diseño actual SÍ contempla `poolSSLIdx` (nearest SSL bajo el precio, 3381–3383) y `poolBSLIdx` (nearest BSL arriba) + `poolDrawIdx` (objetivo alineado al bias, el más lejano, 3385–3389) + guardián `f_confDegree(p.level) >= 2` (3394 — **muerto por BUG #1**).
- Sospechosos de por qué aun así no se ve el SSL de abajo en D1:
  1. `eligible` exige `p.touches >= i_minTouches` (3393) — un low histórico con 1 toque no entra.
  2. `f_poolStrength` (347–350) castiga la lejanía (término de cercanía a 2×ATR) → los majors históricos pierden fuerza y pueden caer del top-N de `f_pushPool` (374) antes de llegar al dibujo.
  3. Retención en `SMC_pools`: los majors viejos pueden ser desalojados por el cap MAX del buffer.
  4. Pools barridos = Estudio+ (§F8, doctrina) — correcto, pero en tendencia hay que verificar que los NO barridos lejanos sobrevivan.

**Instrucción (dos tiempos):**
1. **PASO 2 (re-barrido tras fix #1):** con `f_confDegree` vivo, verificar en D1/H1/M5: ¿dibuja el nearest SSL abajo Y el nearest BSL arriba? ¿Sobreviven en `SMC_pools` los lows/highs históricos no barridos (dump de niveles vía `data_get_pine_lines` + contraste con OHLCV)? Registrar qué falta exactamente.
2. **PASO 6 (implementar lo que falte):** vía "major histórico" inmune a la distancia:
   → `[RELLENAR-OPUS según el hallazgo del PASO 2 — candidatos en orden de menor invasividad: (a) incluir siempre poolSSLIdx y poolBSLIdx en isObjetivo aunque falle eligible-touches (cambio de gate, 1 línea, solo Visual); (b) eximir del decay de cercanía a pools con touches≥2 (tocar f_poolStrength = CORE → exige check-core-sync y justificación; preferir NO tocarla y compensar en el gate de dibujo Visual); (c) si los majors ni siquiera están en SMC_pools, subir retención SOLO vía gate de desalojo en Visual, nunca ensanchando MAX_ZONES/MAX del CORE sin ADR. Criterio de cierre: en D1 el usuario ve ≥1 objetivo inferior y ≥1 superior SIEMPRE que existan niveles no barridos en la historia cargada]`

### B.7 · #7 — Duda P/D del usuario → resuelta en A.2 (respuesta doctrinal). Sin código en este ciclo; solo el apéndice Opción B en `decisiones-pd-rango.md`.

### B.8 · #8 — "Cola del swing" proyectable 🔴 REQUISITO con criterio de aceptación (no mejora opcional)

**Lo que el usuario pidió:** en el swing vigente (discount→premium o inverso), la cola debe mostrar los conceptos importantes que se generaron durante la pierna (FVG, OB, EQH/L, estructura) — pocos pero visibles, **hacia abajo de un swing alcista y hacia arriba de uno bajista** — para proyectar desde M5 hasta dónde puede subir/bajar/rebotar. "Limpio pero NO vacío."

**Veredicto:** el mecanismo que entrega exactamente eso **ya está diseñado y escrito** — bandas de profundidad §7 (`f_depthBand`) + band-pick (mejor zona por banda a lo largo del rango, 40 celdas) + anclas. Está **completamente muerto por el BUG #1** (todo cuelga del guard `aAtr > 0`). **PROHIBIDO añadir mecanismos nuevos antes del re-barrido.**

**Criterio de aceptación (obligatorio, se valida en el PASO 2):** con el ATR vivo, en Operación cada banda de profundidad del rango vigente debe mostrar su(s) mejor(es) zona(s) — la cola del swing queda poblada en ambas direcciones. **Si el band-pick revivido no lo logra, el tuning pasa a ser obligatorio en este mismo ciclo** (PASO 6): caps por banda y/o promoción `confDegree≥2` — siempre dentro del budget ≤25 y sin tocar parámetros ADR-002 sin ADR.

### B.9 · #9 — Panel T14: columnas TF duplicadas + inventario de filas 🟡 solo panel

**Síntoma (S102):** las columnas del panel son `D1 | H1 | TF-actual` (headers 4267–4268 fijos + `f_tfLabel()` 4269). En M5 → D1/H1/M5 ✓. En H1 → D1/H1/**H1** (columna duplicada). En D1 → D1/H1/**D1** (duplicada).

**Restricción de plataforma (documentada, no negociable):** NO se puede añadir una columna M5 estando en D1/H1. `request.security` hacia un TF **inferior** solo muestrea una intrabar por vela del chart → el estado SMC de M5 computado desde D1 sería basura. La herencia solo fluye hacia abajo (coherente con el orquestador 3-TF: la info de M5 se consume estando en M5, con D1/H1 de contexto).

**Fix (PASO 3, junto con BUG #3):** eliminar la duplicación — cuando `f_tfLabel() ∈ {"D1","H1"}`:
→ `[RELLENAR-OPUS: elegir e implementar UNA de las dos variantes: (a) colapsar la tercera columna (tabla de 3 columnas en D1/H1); (b) mantener 4 columnas pero la celda header del TF heredado que coincide con el nativo se marca "H1 ●" (nativa resaltada) y la tercera columna se omite. Criterio: la que menos reestructure table.cell existentes; en ambas, cero información duplicada]`

**Inventario de filas (decisión explícita, no accidente):** hoy el panel tiene ~13 filas resumen (Bias, Bias dom, Último BOS/CHoCH/MSS, OB/FVG/Pool cercano, Último Sweep, EMA, EQ H/L, Kill Zone, Ocultos). Breaker, MB, gaps, OTE, IDM **no están**. Veredicto Fable: el panel es un **resumen operativo**, no un inventario — mantener las ~13 filas actuales como lista canónica y NO añadir filas por familia (el detalle vive en el chart y en "Ocultos"). Si el usuario quiere una fila extra (p.ej. "Breaker cercano"), es una decisión suya de UI, no un bug.

---

## BLOQUE C — Esqueleto de ejecución para Opus (ORDEN OBLIGATORIO)

> Formato de cada paso: `OBJETIVO / ANCLA / CAMBIO / PROHIBIDO / VALIDACIÓN / COMMIT`.
> **Restricciones globales en TODOS los pasos:** ① CORE byte-idéntico (tras tocar cualquier sección compartida → `scripts/check-core-sync.ps1`); ② anti-repaint D-PINE-03; ③ RE10045-safe: cero `array.push` nuevos en `islast` sobre estructuras grandes (acumuladores string o contadores int); ④ parámetros ADR-002 congelados; ⑤ compila 0/0 o no se commitea; ⑥ 1 commit = 1 concepto.

### PASO 1 — Fix BUG #1 (la línea)
- **OBJETIVO:** revivir `chartState.atr14` y con él los 6 colaterales.
- **ANCLA:** `SMC-Visual.pine:2006` (`float atr14 = ta.atr(14)`).
- **CAMBIO:** añadir inmediatamente después: `chartState.atr14 := atr14` — sin gate, sin `nz()`.
- **PROHIBIDO:** tocar `pdHigh/pdLow` (1962–1963), tocar el CORE, tocar cualquier consumidor.
- **VALIDACIÓN:** compila 0/0 → aplicar al chart (protocolo launch-tv-agent + click e19) → en D1 Operación `data_get_pine_boxes` debe pasar de 0 a >0 cajas nativas. Verificar los 6 colaterales uno a uno: band-pick puebla (cajas nativas), `f_posRole` ≠ siempre INTERNO (labels con rol), `f_confDegree` > 0 en confluencias obvias, bandas rotan (panel/Ocultos Grad), guardián pools activo, ribbon KZ con 3 líneas.
- **COMMIT:** `fix(pine-visual): F1 BUG#1 — chartState.atr14 sin asignar colapsaba band-pick/posRole/confDegree/bandas/guardianes/KZ`.

### PASO 2 — Re-barrido vivo EXHAUSTIVO (sin código)
- **OBJETIVO:** medir el sistema con el ATR vivo y decidir los pasos 4/5/6. **Regla firme del usuario: TODAS las familias y TODOS los conceptos, sin muestreo.**
- **MÉTODO:** matriz del Bloque D, TF por TF (D1 → H1 → M5), concepto por concepto, cada uno en {nativo, heredado}. Panel T14 + `data_get_pine_boxes/lines/labels` + screenshots + contraste OHLCV. Presupuesto ≤25 labels por TF en Operación.
- **CRITERIOS DE ACEPTACIÓN que se evalúan aquí:** (i) #8 cola del swing poblada por bandas en ambas direcciones; (ii) #6 ≥1 objetivo de liquidez arriba Y abajo cuando existan niveles no barridos; (iii) #4 giro vigente visible; (iv) 6 colaterales sanos; (v) budget.
- **SALIDA:** matriz rellenada + veredicto por cada condicional (¿PASO 5 necesario? ¿qué variante del PASO 6?). Anexar a este documento o a BUGS-VISUAL.
- **PROHIBIDO:** escribir código durante el barrido.

### PASO 3 — Panel: BUG #3 (Ocultos) + #9 (columnas TF)
- **OBJETIVO:** panel honesto (§10-#8) y sin columnas duplicadas.
- **ANCLAS:** hidEq/recorte 3336, hidStruct 3299, `EQ H/L` 4342, headers 4266–4269, `f_tfLabel` 4167–4169.
- **CAMBIO:** semántica "detectado − dibujado" (esqueleto en A.3, con su `[RELLENAR-OPUS]`) + variante elegida de #9 (con su `[RELLENAR-OPUS]`).
- **PROHIBIDO:** tocar detección, dibujo de zonas o CORE; arrays nuevos en `islast`.
- **VALIDACIÓN:** M5 Operación debe reportar Ocultos Est/EQ ≈ (detectados − dibujados) — con 81 EQ detectados y 2 dibujados, la fila debe decir ~79, no 0. H1/D1 coherentes. En D1/H1 la tabla sin columna duplicada.
- **COMMIT:** `fix(pine-visual): F1 BUG#3+OBS#9 — Ocultos = detectado−dibujado + panel sin columna TF duplicada`.

### PASO 4 — Herencia de estructura garantizada (D1→H1→M5)
- **OBJETIVO:** el último BOS/CHoCH(/MSS) de cada HTF SIEMPRE visible en los TF inferiores.
- **ANCLAS:** `f_drawMTFState` 4007, llamadas 4120/4123, tuple TFState 1837, mirror presupuesto `f_mtfLblYield` ~2955, dedupe 4079, `mtfMajTol` 4118.
- **CAMBIO:** según B.5 (líneas garantizadas por escalares + mirror de presupuesto + regla de dedupe; resolver el `[RELLENAR-OPUS]` del MSS).
- **PROHIBIDO:** subir los caps `i_mtfCapBOS/CHoCH` en este paso; tocar el transporte del CORE (`f_nearestNEvents` y el tuple NO cambian).
- **VALIDACIÓN:** en H1 se ven las líneas `D1: BOS 1.14997` y `D1: CHoCH 1.16551`; en M5 las de D1 y H1. Budget ≤25 se mantiene (el mirror descuenta). Los valores coinciden con el panel al 5º decimal.
- **COMMIT:** `feat(pine-visual): F1 #5 — herencia estructural garantizada (últimos BOS/CHoCH/MSS del HTF por escalares TFState)`.

### PASO 5 — Guardián del giro vigente (CONDICIONAL al PASO 2)
- **EJECUTAR SOLO SI** el re-barrido muestra que el CHoCH/MSS vigente sigue cayendo del recorte con bandas vivas.
- **ANCLAS:** recorte estructura 3291–3299, espejo del guardián de pools 3394, `chartState.lastCHoCHPrice/lastMSSPrice`.
- **CAMBIO:** label cuyo nivel ∈ ±tol del último CHoCH o MSS vigente → inmune a `f_keepBestPerBand` (fuera del cap, como el pool objetivo).
  → `[RELLENAR-OPUS: tol = misma tolerancia de banda/cluster usada por f_keepBestPerBand; verificar cómo identifica la label su nivel (array SMC_structLevels, 3299)]`
- **VALIDACIÓN:** en D1 el CHoCH 1.16551 visible aunque haya N BOS más recientes; budget OK.
- **COMMIT:** `fix(pine-visual): F1 #4 — giro vigente (CHoCH/MSS) inmune al recorte de estructura`.

### PASO 6 — Liquidez bidireccional (#6) + tuning de cola (#8) (según PASO 2)
- **OBJETIVO:** cumplir los dos criterios de aceptación del usuario que queden pendientes tras revivir el diseño.
- **CAMBIO:** las variantes están en B.6 y B.8 con sus `[RELLENAR-OPUS]`. Regla: elegir siempre la menos invasiva que cumpla el criterio; cualquier cambio que roce el CORE exige `check-core-sync` + justificación explícita; cualquier parámetro congelado exige ADR.
- **VALIDACIÓN:** los criterios de aceptación literales de B.6 y B.8, en los 3 TFs.
- **COMMIT:** uno por concepto (`#6` y `#8` separados).

### Cierre del ciclo
- Re-barrido final corto (las filas 🔴 de la matriz → ✅), actualizar BUGS-VISUAL (estados), `smc-doc-updater`, y recién entonces plantear la firma del F1-GATE.

---

## BLOQUE D — Matriz de validación (plantilla del PASO 2)

> Celdas: ✅ correcto · 🔴 falla (anotar síntoma) · ➖ no aplica (p.ej. herencia en D1, techo) · ⬜ pendiente.
> "Heredado" en H1 = capa D1; en M5 = capas D1 y H1 (anotar cada una).

| # | Concepto (familia §7.2) | D1 nativo | H1 nativo | H1 heredado | M5 nativo | M5 her. D1 | M5 her. H1 |
|---|---|---|---|---|---|---|---|
| 1 | BOS (3 escalas) | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| 2 | CHoCH | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| 3 | MSS | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| 4 | FLIP | ⬜ | ⬜ | ➖ | ⬜ | ➖ | ➖ |
| 5 | Swings / giro vigente visible (#4) | ⬜ | ⬜ | ➖ | ⬜ | ➖ | ➖ |
| 6 | OB | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| 7 | Breaker | ⬜ | ⬜ | ➖ | ⬜ | ➖ | ➖ |
| 8 | Mitigation Block | ⬜ | ⬜ | ➖ | ⬜ | ➖ | ➖ |
| 9 | FVG | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| 10 | IFVG | ⬜ | ⬜ | ➖ | ⬜ | ➖ | ➖ |
| 11 | BPR | ⬜ | ⬜ | ➖ | ⬜ | ➖ | ➖ |
| 12 | EQH / EQL | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| 13 | Pools BSL (arriba) | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| 14 | Pools SSL (abajo) | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| 15 | Sweeps / Raid | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| 16 | P/D grid (Premium/UQ/EQ/LQ/Discount) | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| 17 | Gradient / eighths | ⬜ | ⬜ | ➖ | ⬜ | ➖ | ➖ |
| 18 | Gaps apertura (NWOG/NDOG/NYMO) | ⬜ | ⬜ | ➖ | ⬜ | ➖ | ➖ |
| 19 | IDM | ⬜ | ⬜ | ➖ | ⬜ | ➖ | ➖ |
| 20 | OTE / Golden Pocket | ⬜ | ⬜ | ➖ | ⬜ | ➖ | ➖ |
| 21 | Vacuum / VI / IPR / IR / Displacement | ⬜ | ⬜ | ➖ | ⬜ | ➖ | ➖ |
| 22 | Kill Zone ribbon | ➖ | ⬜ | ➖ | ⬜ | ➖ | ➖ |
| 23 | SMT (si activo) | ⬜ | ⬜ | ➖ | ⬜ | ➖ | ➖ |

**Criterios transversales (una fila por TF):**

| Criterio | D1 | H1 | M5 |
|---|---|---|---|
| ≥1 objetivo liquidez ABAJO y ≥1 ARRIBA visibles (#6) | ⬜ | ⬜ | ⬜ |
| Cola del swing poblada por bandas, ambas direcciones (#8) | ⬜ | ⬜ | ⬜ |
| Giro vigente (CHoCH/MSS) visible (#4) | ⬜ | ⬜ | ⬜ |
| Budget ≤25 labels Operación | ⬜ | ⬜ | ⬜ |
| Panel: Ocultos = detectado−dibujado (#3) | ⬜ | ⬜ | ⬜ |
| Panel: sin columna TF duplicada (#9) | ⬜ | ⬜ | ➖ |
| 6 colaterales BUG #1 sanos | ⬜ | ⬜ | ⬜ |

---

*Fable · S102 · anclas verificadas en vivo sobre commit `8618cc3` · CORE intacto (este documento no toca código).*
