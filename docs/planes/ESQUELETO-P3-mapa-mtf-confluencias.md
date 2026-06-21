# Esqueleto de integración — PARTE 3: Mapa MTF rico + Motor de Confluencias → Entrada

> **Sesión:** S038 · Fase 1 · rama `pine/sistema-completo`. Producido por Claude Code (Opus) sobre el encargo de `docs/planes/HANDOFF-OPUS-MAX-mapa-mtf-confluencias.md` (S037).
> **Qué es:** el *esqueleto* (estructura + contratos + presupuesto + troceo + carriles) de las DOS piezas que faltaban por integrar: **(A)** el **mapa MTF rico** (cada concepto, sus últimos N por dirección, en cascada D1→H1→M5) y **(B)** el **motor de confluencias → entrada** (cómo el sistema "marca todo lo que pasa" y de ahí **decide en qué zona entrar**, con R:R≥1:3). Es lo que el EA, la Strategy y el enjambre comparten como fondo.
> **Qué NO es:** NO es código Pine de producción, NO inventa definiciones SMC ni casos, NO toca ningún `.pine` ni el CORE byte-idéntico (core-sync sigue MISMO SHA `2de06be3a3eb1321`, 644 líneas). Cada valor a medir queda `⏳ a cuantificar [impl]`; cada cuerpo de función `// TODO [impl]`. Es el plano que la siguiente IA (**[impl]**) ejecuta.
> **Partición:** P1 = `ESQUELETO-P1-conceptos-EA-pine-repos.md` (gap de conceptos + motor EA + repos). P2 = `ESQUELETO-P2-hermes-enjambre.md` (runtime del enjambre). **Esta P3** = el **substrato espacial MTF** + la **capa de decisión confluencia→entrada** que une a ambas. Lo de P1/P2 se **referencia, no se duplica**.
> **Léelo junto a:** `CLAUDE.md` (8 reglas duras), `docs/workplan/PINE-PLAN.md` (§4 MTF, §5 dibujo/presupuesto, §7 sprints), `WORKPLAN-MAESTRO-V2.md` §4.8 (42 confluencias), `docs/reglas-smc-ict.md` (fuente SMC + formato ficha), `docs/planes/ESQUELETO-P1-*.md` (§3 motor EA, §5 confluencias #43–#51), `docs/planes/ESQUELETO-P2-*.md` (§2 runtime enjambre, §2.6 árbitro TV, §2.8 push), `docs/planes/ESQUELETO-MITIGACION-conceptos.md` (patrones P1–P4 ciclo de vida), ADR-001/002/005/006/007 + **ADR-008** (reconciliación, este sprint).

---

## §0 — Reglas duras (referencia, no re-copia)

Las 8 reglas duras de `CLAUDE.md` y las 10/12 reglas de implementador de `ESQUELETO-P1 §0` y `ESQUELETO-P2 §0` **siguen vigentes y mandan**. Si el esqueleto y una regla chocan, **manda la regla**. P3 añade **tres invariantes propios** del mapa MTF que el `[impl]` no puede romper:

- **R-P3-1 · La encapsulación NO contamina el chart.** `f_computeTFState`/`f_tfSnapshot` corren dentro de `request.security(sym, tf, expr, lookahead=barmerge.lookahead_off)`. Todo su estado debe ser **interno a la función** (no `var` global del consumidor) para que el contexto D1/H1 no pise el del chart (§2.4). **Verificación obligatoria** antes de T13b (spike test, §6 R-1).
- **R-P3-2 · El mapa HTF viaja aplanado y CAPADO.** `request.security` no transporta UDTs/arrays, solo números/tuples (`PINE-PLAN §4`). El mapa rico del HTF se trae como tuple plano con **tope fijo** por concepto/dirección (cap `N_htf`, §2.2). El TF propio se computa **local** (sin security) y puede ser más rico (`N_chart`). No se "trae todo": se presupuesta.
- **R-P3-3 · La capa de decisión es DETERMINISTA y direccional.** El motor confluencia→entrada (§3) es scoring `scoreLong`/`scoreShort` ponderado (regla #6) con R:R≥1:3 calculable (regla #5) — **NO recetas hardcodeadas** de las 5 imágenes. Las imágenes **validan/calibran** el catálogo de setups; no se cablean como `if exact-match`. Pesos = Fase 3 (ADR-002).

---

## §1 — Qué resuelve P3 y su frontera con P1/P2 (mapa anti-duplicado)

El usuario amplió T13 de "snapshot mínimo" a una **visión de fondo**: el gráfico debe **marcar todo lo que sucede** (todos los conceptos, en todas las escalas, cerca del precio) y, **a medida que eso aparece, decidir en qué zona entrar**. Eso son dos subsistemas que hoy no existen y que P1/P2 **no** cubren:

| Subsistema | Lo aporta | Dónde vive | Estado hoy |
|---|---|---|---|
| **(A) Mapa MTF rico** (substrato espacial: qué conceptos hay, dónde, en qué dirección, en qué TF) | **P3 §2** | Pine: detección + `request.security` + dibujo + panel | stub vacío (`SMC-Visual.pine:962-963`, `SMC-Strategy.pine:906-907`); `SMC_TFState` mínimo (`SMC-Library.pine:113`) |
| **(B) Motor confluencia→entrada** (capa de decisión: leer el mapa y decir "entro aquí, con este SL/TP") | **P3 §3** | Pine-Strategy (Fase 2) + EA (Fase 4) + lo testea el enjambre (P2) | sin diseño integrado; `f_scoreConfluences` es stub planificado (F2-T01) |

**Frontera explícita con lo ya esqueletizado (no se re-hace):**
- **Conceptos atómicos** (OB/FVG/pools/MSS/… y el gap T26–T40) → ya en `reglas-smc-ict.md` + `ESQUELETO-P1`. P3 **los consume**, no los redefine.
- **Motor de razonamiento del EA** (generalización, mínimos por familia, clase de equivalencia) → bosquejado en `ESQUELETO-P1 §3`. P3 **lo completa del lado del MAPA** (de dónde salen los booleanos direccionales que el motor suma) y del **selector de zona de entrada** (§3.4), que P1 no detalla.
- **Runtime del enjambre** (cron/kanban/voto/push/árbitro TV) → `ESQUELETO-P2`. P3 sólo define el **formato de entrega** de los setups testeados al EA (§3.6) — el puente offline.
- **Las 42 confluencias §4.8** → `WORKPLAN §4.8` + expansión #43–#51 en `ESQUELETO-P1 §5`. P3 añade la capa **(b) setups/secuencias** POR ENCIMA de las confluencias atómicas (§3.2), sin tocar la numeración.

---

## §2 — Modelo de datos del Mapa MTF rico (subsistema A)

### §2.1 — Dos capas: TF propio (rico, local) vs HTF (reducido, vía security)

El mapa se construye en **dos planos que no se mezclan**:

1. **Plano del TF propio (chart):** la detección ya corre localmente (sección DETECCIÓN, `SMC-Visual.pine ~697-960`). Sus arrays (`SMC_zones`, `SMC_eventsMSS`, `SMC_pools`, …) **ya contienen el mapa rico** del TF actual. No requiere `request.security`. Aquí `N_chart` puede ser alto (hasta ~10/lado), limitado solo por el **presupuesto de objetos de dibujo** (`PINE-PLAN §5`, 500/tipo).
2. **Plano HTF (D1, H1):** llega **aplanado** por `request.security` (§2.2/§2.4). Capado a `N_htf` (≈3/lado por concepto-zona, §2.2). Se **reconstituye** en el consumidor a estructuras ligeras para dibujar en cascada y para el scoring (§2.5).

**Cascada de herencia (visión del usuario):** cada TF hereda hacia todos los menores — **D1 → {H1, M5}, H1 → {M5}**. En el chart M5 se ven: el mapa nativo de M5 (rico) + el mapa de H1 (reducido, prefijo `"H1:"`) + el de D1 (reducido, prefijo `"D1:"`). En el chart H1 se ven: nativo H1 + D1. Dibujo diferenciado (transp ~85, borde punteado, prefijo) — ya previsto en `PINE-PLAN §5.5`.

### §2.2 — La restricción central: presupuesto de `request.security` (R-P3-2)

`request.security` transporta un **tuple plano** de números, con un tope (`PINE-PLAN §4` lo cifra en ~127; **`⏳ [impl]`: confirmar el límite exacto en Pine v6**). Coste por elemento del mapa:

| Elemento | Campos a transportar | Coste (floats/ints) |
|---|---|---|
| Zona (OB/FVG/BPR/breaker…) | top, bottom, dir, state, barTime | **5** (dir+state empacables → 4) |
| Pool / nivel de liquidez | level, dir, swept(0/1), barTime | **4** |
| Evento de estructura (último BOS/CHoCH/MSS) | price, dir, barTime | **3–4** |
| Escalares por TF | bias, pdHigh, pdLow, pdMid, ema20, ema50, ema200, atr14 | **~8** |

**Cálculo de presupuesto por llamada `security` (un HTF), con `N` zonas/lado:**

```
total ≈ escalares(8) + estructura(BOS+CHoCH+MSS = 3×4=12) + sweep(1×4=4)
        + OB(N×2×5) + FVG(N×2×5) + pool(N×2×4)
      = 24 + 28·N
   N=1 → 52     N=2 → 80     N=3 → 108 ✅     N=4 → 136 ❌ (sobre ~127)
```

**Conclusión de diseño (decision-grade):**
- **`N_htf` ≈ 3 por lado** es el cap práctico si se trae OB+FVG+pool en **una** llamada por TF. `⏳ [impl]` ajustar según el límite real.
- Si se quiere `N_htf` mayor → **dos llamadas `security` por TF** (una para zonas, otra para estructura+escalares), duplicando el cupo. Decisión de tradeoff (más llamadas = más cómputo). `// TODO [impl]: elegir 1 vs 2 llamadas/TF según límite confirmado y coste`.
- El **TF propio NO consume este presupuesto** (es local) → ahí vive la riqueza (`N_chart` alto).

### §2.3 — UDT `SMC_TFState` ampliada (qué añadir)

Hoy `SMC_TFState` (`SMC-Library.pine:113`) es el snapshot **escalar mínimo** (bias + último BOS/CHoCH + P/D + EMAs). Para el mapa rico hay que distinguir **dos representaciones**:

- **(a) UDT enriquecido para el TF propio (consumidor):** `SMC_TFState` puede ganar **arrays** de zonas/pools por dirección PARA USO LOCAL (no cruza security). `⏳ [impl]`: decidir si se amplía el UDT o se reusan los arrays globales existentes (`SMC_zones`, `SMC_pools`, `SMC_eventsMSS`) — **preferible reusar** para no duplicar estado (regla anti-duplicación).
- **(b) Tuple plano para el HTF (transporte):** lo que `f_tfSnapshot()` devuelve (§2.4). **Arrays NO van aquí**: van como `topN_1, botN_1, dirN_1, …` posicional, con cap `N_htf`. El orden del tuple es un **contrato** (§2.4) que productor y consumidor comparten exactamente.

`// TODO [impl]: extender SMC_TFState con los campos escalares que falten (atr14, pdMid) y documentar el contrato del tuple plano como comentario canónico en CORE.`

### §2.4 — Contrato `f_computeTFState` / `f_tfSnapshot` (el corazón técnico)

```
// Vive en LIBRARY CORE (byte-idéntico Visual/Strategy + export en Library) → core-sync
// + paridad MQL5 Fase 4 (SMC_MTF.mqh). PURA en el sentido de no leer globales del
// consumidor; SÍ corre la cadena de detección con estado INTERNO a la función.
f_computeTFState() =>
    // 1. corre swings/estructura/OB/FVG/pools/sweep/MSS sobre el TF de ejecución,
    //    con TODO el estado en variables LOCALES var DENTRO de la función (R-P3-1).
    // 2. selecciona los N_htf más cercanos al precio por dirección y concepto.
    // 3. devuelve un TUPLE PLANO (contrato §2.3.b), nunca un UDT/array.
    [ bias, pdHigh, pdLow, pdMid, ema20, ema50, ema200, atr14,
      bosP,bosD,bosT, chochP,chochD,chochT, mssP,mssD,mssT, sweepLvl,sweepD,sweepT,
      obTop1,obBot1,obDS1,obT1, /* … hasta N_htf OB long + N_htf OB short … */
      fvgTop1,fvgBot1,fvgDS1,fvgT1, /* … FVG … */
      poolLvl1,poolD1,poolSw1,poolT1 /* … pools … */ ]

// En el CONSUMIDOR (Visual y Strategy), nunca en la librería:
[d1_*] = request.security(syminfo.tickerid, "D",  f_computeTFState(), lookahead = barmerge.lookahead_off)
[h1_*] = request.security(syminfo.tickerid, "60", f_computeTFState(), lookahead = barmerge.lookahead_off)
```

**Puntos de contrato (todos `⏳ [impl]` salvo lo marcado):**
- **Dónde vive:** CORE byte-idéntico (regla #2). Tras escribirla → `scripts/check-core-sync.ps1` = OK. Cambia el SHA y la cuenta de líneas (esperado y documentado en el commit).
- **Estado interno (R-P3-1):** sutileza Pine v6 — `request.security(sym, tf, expr)` evalúa `expr` en contexto separado; si `expr` referencia un `var` **interno** a la función, ese estado persiste **por-contexto** (independiente del chart). Si referencia globales `var`, **contamina**. → **toda la cadena debe encapsularse**. Esto es el refactor que `ADR-007` anticipa y que **adelanta Fase 4** (es justo lo que `SMC_MTF.mqh` necesita).
- **Anti-repaint (regla #1):** `lookahead_off` SIEMPRE; eventos en `barstate.isconfirmed`. Las zonas HTF pueden extenderse en vivo, los eventos solo confirman al cierre del TF.
- **Reuso:** helpers existentes — `f_updateZoneMitigation` (`SMC-Library.pine:327`), `f_detectSwings`/`f_detectStructure`/`f_detectMSS` (CORE), constantes `ZS_*` (`SMC-Library.pine:46-49`). La **selección "N más cercanos por dirección"** es nueva: hoy `f_pNearZone` (`SMC-Visual.pine:1232`) y `f_pNearPool` (`:1245`) devuelven **UNO** y son **de presentación** (no CORE). → generalizar a `f_nearestN(array, kind, dir, price, N)` y **promoverla a CORE** si la usa el scoring (paridad). `// TODO [impl]: escribir f_nearestN pura en CORE.`
- **Filtros de calidad del mapa:** "no mitigado" = endurecer `state < ZS_MITIGATED` (no solo `!= ZS_INVALID` como en `f_pNearZone:1238`); pools "no barridos" = `not swept`. `⏳ [impl]: definir el filtro exacto por concepto.`

### §2.5 — Reconstitución + dibujo en cascada

- El consumidor recibe los tuples `d1_*`/`h1_*` y los **reconstituye** a estructuras ligeras de dibujo (cajas/líneas con prefijo de TF). No re-detecta: solo pinta lo que el HTF ya resolvió.
- **Cascada:** en M5 se dibujan las zonas de H1 y D1 (heredadas) además de las de M5; en H1, las de D1. Dibujo diferenciado: transp ~85, punteado, prefijo `"D1:"`/`"H1:"` (`PINE-PLAN §5.5`).
- **Presupuesto de objetos (riesgo, §6 R-3):** mapa rico × 3 TFs puede topar los 500 objetos/tipo. → cuota por familia + modo `Present` desde el inicio (`PINE-PLAN §5`, patrón P4 de `ESQUELETO-MITIGACION`). `// TODO [impl]: asignar cuota por (concepto × TF) y aplicar Present mode.`

### §2.6 — Inputs de densidad (`GRP_MTF`)

Grupo de inputs nuevo: por **concepto × dirección × TF**, cuántos elementos mostrar (0–10). El usuario "apaga lo que no usa" (`PINE-PLAN §5.1`, toggle por concepto → se salta detección Y dibujo).
- `i_mtf_<concepto>_<tf>_long` / `_short` (int 0–10), con **cap a `N_htf`** para los HTF (no se puede pedir más de lo que el tuple transporta).
- Toggle maestro por TF (`i_showD1`, `i_showH1`) + densidad global de fallback.
- `⏳ [impl]: definir el set mínimo de inputs sin explotar el panel de settings (agrupar por TF, no 1 input por celda).`

---

## §3 — Motor de Confluencias → Entrada (subsistema B — el fondo de todo)

> **Lo que pidió el usuario, literal:** que el gráfico **marque todo lo que sucede** (conceptos) y, **a medida que eso aparece, decida en qué zona poner la entrada**, con R:R≥1:3. Que eso lo **discutan los agentes**, lo **testeen en vivo y en replay**, y que el **EA**, alimentado de la lista de confluencias, **determine cuándo entrar según lo que va pasando**. Esta sección es el contrato de esa capa.

### §3.1 — Las 5 imágenes leídas como UNA gramática común

Las 5 referencias del usuario (Sell Setup / Simple BOS / Smart Money / SMC Beginners / Institutional) **no son 5 recetas distintas**: son la **misma secuencia canónica** con variantes. Destilada:

```
①  CONTEXTO / SESGO      →  estructura confirmada: BOS / MSS / CHoCH (dirección)
②  EVENTO DE LIQUIDEZ    →  grab / sweep / IDM / trendline liquidity (toma el lado contrario)
③  ZONA POI (entrada)    →  OB / FVG / BPR / breaker en discount(long)/premium(short), cerca del precio
④  TRIGGER               →  mitigación de la POI + confirmación (CHoCH/MSS menor, vela de rechazo)
⑤  STOP LOSS             →  más allá de la POI / del swing protector
⑥  TARGET                →  siguiente liquidez no usada (pool/EQH-EQL), con R:R ≥ 1:3
```

Mapeo de cada imagen a la gramática (validación cruzada, **cero invención** — es lo que las imágenes muestran):
| Imagen | ① contexto | ② liquidez | ③ POI | ⑥ target |
|---|---|---|---|---|
| Sell Setup Confirmation | downtrend / BOS | liquidity grab sobre zona | (entry en zona) | TP1/TP2/TP3 (R:R 1:3) |
| Simple BOS Entry | BOS | (previo) | FVG + OB (última vela contraria) | liquidez previa |
| Smart Money Entry | BOS + IND + MSS | (QM) | OB + QM entry | target (4RR) |
| SMC for Beginners | BOS/MSS/CHoCH | Sweep / IDM | OB / FVG entre BOS y CHoCH | liquidez no usada |
| Institutional Notes | BOS confirmation | trendline liq. grab + bearish sweep | FVG → OB | take profit (R:R) |

> **Esto es el insumo del catálogo de setups (§3.5), NO código.** El sistema no busca "esta imagen": busca **la gramática** vía scoring direccional (§3.3) + selección de POI (§3.4).

### §3.2 — Dos capas que no se confunden: confluencias atómicas vs setups

| Capa | Qué es | Dónde está | Quién la calcula |
|---|---|---|---|
| **(a) Confluencias atómicas** | las 42 §4.8 (+#43–#51): cada una un booleano direccional con peso | `WORKPLAN §4.8` + `ESQUELETO-P1 §5` | Pine `f_scoreConfluences` (determinista) → `scoreLong`/`scoreShort` |
| **(b) Setups / secuencias** | la gramática §3.1: combinación + **orden temporal** de atómicas que define una entrada | **nuevo, P3 §3.5** | Pine-Strategy + motor EA (combos) + lo testea el enjambre |

**Relación (regla dura, R-P3-3):** la capa (b) **NO recalcula** ni reemplaza el score (a). Un setup cumplido es un **patrón de alto valor** sobre las atómicas; el `[impl]` decide en Fase 2/3 si un setup **(i)** añade peso (bonus al score), **(ii)** actúa como **gate** (sin setup mínimo → no entra aunque el score sume) o **(iii)** solo prioriza/etiqueta. `// TODO [impl]: decidir bonus vs gate vs etiqueta por setup; calibrar en Fase 3.` (mismo dilema abierto en `ESQUELETO-P1 §3.2`).

### §3.3 — Contrato: el mapa MTF → entradas del scoring

Cómo el subsistema A alimenta la capa (a). El scoring lee el **mapa reconstituido** (TF propio + HTF heredados) y produce los booleanos direccionales:
- Cada confluencia §4.8 se evalúa contra el mapa: "¿hay un OB **alcista** no mitigado cerca del precio en H1?" → `#17_long = true`. El TF de la confluencia (chart/H1/D1) lo da la **capa** del mapa de donde sale (confluencias #17/#18 = H1, #19/#20 = chart, #21 = D1 — ya en §4.8).
- **Clase de equivalencia por familia (de `ESQUELETO-P1 §3.1`):** "cualquier zona alcista activa cerca del precio" satisface la confluencia de familia, no un OB-H1 exacto → generaliza (regla del EA, ADR-007). El mapa rico es lo que **hace medible** esa clase: tiene N zonas por dirección para evaluar, no solo la más cercana.
- **Salida:** `[scoreLong, scoreShort, activeList]` (firma planificada de `f_scoreConfluences`, `PINE-PLAN §3.5`). `activeList` = qué confluencias se activaron (para panel/alerta/auditoría del enjambre).
- `// TODO [impl]: por cada confluencia §4.8, escribir el predicado "lee del mapa MTF" exacto. Es F2-T01; aquí queda el contrato.`

### §3.4 — Selector de POI: "decide en qué zona poner la entrada" (lo nuevo)

Este es el paso que el usuario destaca y que ni P1 ni §4.8 detallan: **dado el contexto, elegir LA zona de entrada**. Esqueleto del selector (determinista, R:R-first):

```
f_selectEntryPOI(dir, mapMTF, price, atr) =>
    // 1. candidatas = zonas POI (OB/FVG/BPR/breaker) en dirección `dir`,
    //    no mitigadas (state < ZS_MITIGATED), en discount(long)/premium(short) [§2.3 P/D].
    // 2. filtrar por confluencia: ¿coincide con un pool objetivo / nivel HTF heredado?
    //    (zona en cascada D1/H1 pesa más — confluencia multi-TF).
    // 3. ordenar por calidad: cercanía al precio × alineación de dirección ×
    //    nº de TFs que la confirman (anidación) × frescura.
    // 4. para la mejor candidata: calcular SL (más allá de la POI/swing) y
    //    TP (siguiente liquidez no usada). Si R:R < 3 → DESCARTAR y probar la siguiente.
    // 5. si ninguna da R:R≥3 calculable → no hay zona de entrada (regla #5: no "casi señal").
    [poi, sl, tp, rr]   // o na si no hay
```

- **Reusa:** `f_computeSLTP` (`PINE-PLAN §3.5`, R:R≥1:3 o no hay señal), el mapa de pools (`SMC_pools`) para el target, P/D (`trailing`/`SMC_Trailing`) para premium/discount.
- **La anidación en cascada ES la confluencia de calidad:** una POI de M5 que cae dentro de una zona de H1 que cae dentro de una de D1 es la entrada de máxima confluencia (justo el caso de uso que el usuario describió: "entrar en M5 a una zona de D1 que también se ve en H1"). El selector debe **premiar** ese solapamiento multi-TF. `// TODO [impl]: métrica de solapamiento multi-TF como factor de calidad.`
- `⏳ [impl]: cuantificar el ranking (pesos del orden = Fase 3, ADR-002). Aquí solo la MECÁNICA.`

### §3.5 — Catálogo de setups (fichas, no recetas)

Cada setup de la gramática §3.1 se documenta como **ficha** (formato análogo a las de `reglas-smc-ict.md`), que el enjambre **testea** y la Strategy/EA **reconocen como combo**. **NO se hardcodea como `if`**: es el patrón que el scoring + selector de POI deben producir.

```
### Setup <N> · <Nombre> (imagen ref: <cuál>)
**Gramática.**  ① contexto: <BOS/MSS/CHoCH dir> · ② liquidez: <grab/sweep/IDM> ·
                ③ POI: <OB/FVG/…> en <discount/premium> · ④ trigger: <…> ·
                ⑤ SL: <…> · ⑥ target: <liquidez> (R:R ≥ 1:3)
**Confluencias §4.8 que lo componen.**  #<…>, #<…>, … (atómicas, capa a)
**Ventana temporal / orden.**  <secuencia y tolerancia entre pasos> ⏳ a cuantificar [impl]
**Cómo lo mide el sistema.**  scoreDir ≥ thr ∧ POI seleccionada (§3.4) ∧ R:R≥3
**Casos de prueba (EURUSD, TV MCP + replay).**  ✓ ✓ ✓ + ✗ contraejemplo ⏳PENDIENTE-TVMCP
**Autoría / track record (enjambre).**  docs/laboratorio/ (P2 §2.5/§2.6)
```

Setups semilla (de las 5 imágenes) — `[impl]` rellena: **S-01 Sell/Buy Setup Confirmation** · **S-02 Simple BOS Entry** · **S-03 Smart Money Entry (con MSS)** · **S-04 SMC Beginners (BOS-CHoCH range)** · **S-05 Institutional (trendline liq + FVG→OB)**. El enjambre puede **descubrir más** (P2): ascienden al catálogo solo tras IS/OOS (ADR-002).

### §3.6 — Puente offline: entrega enjambre → EA

Formato de **entrega** de lo que el enjambre valida (confluencias/setups testeados) hacia la calibración del EA — **nunca en runtime** (ADR-005/007/008, pared dura):

- **Producto del enjambre:** entradas DEMO en TradingView (vía MCP) sobre setups del catálogo → resultado resuelto por **TV como árbitro** (`ESQUELETO-P2 §2.6`) → track record por setup/confluencia/agente.
- **Gate de validación:** un setup/peso solo cristaliza si pasa **Strategy Tester IS/OOS 70/30** (ADR-002) — el diario del laboratorio es hipótesis falsable, no verdad.
- **Formato de entrega (`⏳ [impl]`):** tabla `setup/confluencia · dirección · hit-rate · R medio · muestra · veredicto IS/OOS` → entra como **peso/regla** del `f_scoreConfluences` y del selector de POI (§3.4) en Fase 3. `// TODO [impl]: esquema exacto del fichero de entrega (reusar el JSONL de track record de P2 §2.6).`
- **Frontera (R-P3-3 + ADR-008):** el EA **hereda** estos pesos cristalizados; el laboratorio-en-vivo y el EA **no se comunican en runtime**.

---

## §4 — Troceo en tareas por carril (Pine/EA vs Hermes/Enjambre)

Cada tarea lleva los **7 checkboxes del proceso canónico** de `ESQUELETO-P1 §1` (spec → CORE puro → 0/0+core-sync → validación ≥90 → confluencia §4.8 → golden test MQL5 → commit) y un **done medible**. Numeración que **continúa** la de `PINE-PLAN §7` (Sprint 1.4 ya reserva T13/T14/T15).

### §4.1 — CARRIL Pine/EA

| Tarea | Qué | Done medible | Depende de |
|---|---|---|---|
| **T13a · Mapa MTF núcleo** | encapsular el bias + BOS/CHoCH/MSS + P/D + EMAs en `f_computeTFState` (escalares, los que casi están en `chartState` `SMC-Visual.pine:739`); 2 `request.security` (D1, H1); dibujo diferenciado + cascada de esos escalares | compila 0/0 los 3, core-sync OK, D1/H1 bias y niveles visibles en M5/H1 con prefijo; **anti-repaint verificado** | T03/T04/T07/T12 (✅) |
| **T13b · Mapa MTF rico** | ampliar `f_computeTFState` a **N_htf zonas/lado** (OB/FVG/pool/sweep) con el tuple plano capado (§2.2); `f_nearestN` pura en CORE; reconstitución + dibujo en cascada con cuota de objetos | N_htf OB/FVG/pool de D1 y H1 dibujados en cascada; presupuesto de objetos bajo 500/tipo; **spike test R-P3-1 ✅ PASADO (S039)** | **T13a** + spike R-P3-1 (§6) ✅ SUPERADO · ✅ **COMPLETO (S041)** — entrega *mapa de niveles* |
| **T13c · Mapa MTF geométrico** `[NUEVO S041 · ADR-010]` | corregir T13b: ranura **6 campos** `[kind,top,bottom,dir,tA,tB]` (anclaje temporal) + consumidor **reconstruye forma NATIVA por `xloc.bar_time`** (OB/FVG=caja, EQH/EQL=línea, BOS/CHoCH=origen→ruptura, sweep=▲▼ en barra, pool=línea) + **cap 0-10 por concepto para TODOS** + emitir BOS/CHoCH/EQH/EQL al buffer. Buffer genérico de ADR-009 conservado | objetos HTF se dibujan **anclados a su barra real con su forma propia** en M5/H1; cap por concepto efectivo; compila 0/0, core-sync OK, validación ≥90 (paridad vs cambio manual de TF) | **T13b** ✅ · diseño en `revision-T13b-mtf-dibujo-nativo.md` |
| **T14 · Panel multi-columna** | panel con columnas propio / H1 / D1 (bias, último evento, POI más cercana, sesión) | tabla con 3 columnas coherentes con el mapa | **T13c** |
| **T15 · Alertas MTF** | `alertcondition()` en Visual para eventos del mapa (confluencia/POI) — plantilla `PINE-PLAN §5` | alertas disparan en eventos confirmados, sin repaint | **T13c**/T14 |
| **F2-T01′ · Scoring lee el mapa** | `f_scoreConfluences` consume el mapa MTF (§3.3) → `scoreLong/scoreShort/activeList` | scores en panel; confluencias #17–#21 leen del mapa correcto | **T13c** + F2-T01 base |
| **F2 · Selector de POI** | `f_selectEntryPOI` (§3.4) + integración con `f_computeSLTP` (R:R≥3) en Strategy | Strategy entra solo con POI seleccionada y R:R≥3; setups S-01..05 reconocibles | F2-T01′ |
| **F4 · Motor EA** | traducción función-a-función del mapa+scoring+selector a `SMC_MTF.mqh` + motor de decisión (`ESQUELETO-P1 §3`) | golden tests de paridad (0 dif eventos, ±1 tick niveles) | toda la cadena Pine validada + gate Fable |

> **Por qué T13a antes que T13b (gestión de riesgo, regla #8):** T13a es refactor menor sobre escalares ya casi listos en `chartState` y **no toca la cadena de detección validada** (T01–T12). T13b sí exige la encapsulación completa (riesgo de contaminar contexto) → se hace **después** de pasar el spike test R-P3-1. Así no se pone en riesgo lo ya validado.

### §4.2 — CARRIL Hermes/Enjambre (referencia a P2, no se re-hace)

> **Importante (gate §5.3):** la *construcción* del enjambre puede ir en paralelo a Pine, pero el **testeo de setups** (las filas "testeo" de abajo) **NO arranca** hasta que el enjambre esté **completo** (perfiles + archivos/knowledge + skills + MCP + workflow + loop) **y** el Pine esté completo. No se testea con un piloto a medias.

| Tarea | Qué | Doc |
|---|---|---|
| Testeo de setups en replay | el enjambre opina vela a vela sobre los setups §3.5 en histórico | `ESQUELETO-P2 §2.7` |
| Testeo en vivo (copiloto) | entradas DEMO en TV vía MCP + discusión rondas 1/2 + voto | `ESQUELETO-P2 §2.1–2.4` |
| Árbitro TV + track record | TV resuelve win/loss; track record por setup/agente | `ESQUELETO-P2 §2.6` |
| Push al humano | CallMeBot con el setup accionable | `ESQUELETO-P2 §2.8` |
| Entrega offline | tabla de setups validados IS/OOS → calibración | **P3 §3.6** |

### §4.3 — Puntos de integración entre carriles (el puente offline, explícito)

| # | Punto | Carril origen | Carril destino | Cuándo | Regla |
|---|---|---|---|---|---|
| I-1 | Catálogo de setups §3.5 (gramática) | Pine/EA (define) | Enjambre (testea) | al escribir §3.5 | mismo catálogo, dos lecturas |
| I-2 | Mapa MTF como insumo del enjambre | Pine (lo dibuja) | Enjambre (lo lee vía TV MCP) | T13b en adelante | el Vigía lee el chart con el mapa puesto |
| I-3 | Setups validados IS/OOS → pesos/reglas | Enjambre (valida) | Pine/EA (cristaliza) | Fase 3 | **offline**, ADR-002/008 |
| I-4 | Gate determinista de noticias | Enjambre (fuente) | EA (veto binario) | Fase 4 | único puente en vivo, ADR-005/008 |

> **Pared dura (ADR-008):** salvo I-4 (veto binario determinista), **ningún dato del enjambre llega al EA en runtime**. I-3 es el único flujo de "inteligencia" y es **offline** (cristalización por calibración).

---

## §5 — Workplan unificado (orden, dependencias, gates)

### §5.1 — Inserción en los planes canónicos (sin romper numeración)

- **`PINE-PLAN.md §7 · Sprint 1.4`** — desdoblar el ítem 13 en **13a/13b**, mantener 14/15. Pointer a este P3. (edición de este sprint).
- **`WORKPLAN-MAESTRO-V2.md §4.8`** — nota: la capa (b) setups se documenta en `ESQUELETO-P3 §3`; no cambia la numeración de las 42+9. (edición de este sprint).
- **`reglas-smc-ict.md`** — sección nueva (futuro `[impl]`) para el **catálogo de setups** (§3.5) cuando se cuantifiquen con casos TV. No ahora.
- **No se duplica** P1/P2: P3 referencia. El detalle de tareas vive aquí; los planes canónicos solo apuntan (mismo patrón que P1).

### §5.2 — Tabla de dependencias (global)

```
T01–T12 ✅ ──► T13a (núcleo MTF) ──► [spike R-P3-1 ✅ PASA S039] ──► T13b (rico/niveles ✅ S041) ──► T13c (geométrico/anclado, ADR-010) ──► T14 (panel) ──► T15 (alertas)
                                                              │
   Sprint 1.5 (Tier 2) ── Sprint 1.6 (gap T26–T40, ESQUELETO-P1) ──┤ (conceptos que el mapa transportará)
                                                              ▼
                                   F2-T01′ scoring lee mapa ──► F2 selector POI (§3.4) ──► F2 setups (§3.5)
                                                              ▼
        Enjambre (P2) testea setups en replay+vivo ──► IS/OOS (Fase 3) ──► cristaliza pesos/reglas
                                                              ▼
                              GATE DURO Fable (ADR-003) ──► F4 EA: SMC_MTF.mqh + motor decisión + golden tests
```

### §5.3 — Gates (no se saltan, regla #8)

- **Gate T13a→T13b (spike test R-P3-1):** el estado por-contexto no contamina el chart **debe pasar** antes de encapsular la cadena completa. **Protocolo de resultado (decisión Freddy, S038):**
  - **✅ Si pasa (todo OK) — RESULTADO: ✅ PASÓ en Sesion-039:** se continúa el plan tal cual → T13b → T14 → T15. Determinista: `var` interno en `request.security(..., D, ..., lookahead_off)` acumula PER-CONTEXTO sin contaminar chart.
  - **❌ Si NO pasa / aparece cualquier problema:** **DETENER. NO improvisar un workaround** (no forzar detección HTF simplificada por cuenta propia). **Avisar a Freddy** con el diagnóstico exacto (qué se probó, qué falló, hipótesis) para que él **escale a Opus ultracode (Opus Max)** y se decida el rediseño del transporte MTF antes de tocar nada más. T13b queda en pausa hasta esa resolución.
- **GATE PRE-TESTEO DE SETUPS (nuevo, decisión Freddy S038) — el más importante de esta capa.** El testeo de setups del enjambre (replay+demo que alimenta IS/OOS) **NO arranca** hasta que estén listas **las DOS cosas, completas, no parciales**:
  - **(A) Pine COMPLETO:** todos los conceptos integrados y validados — Tier 1 (T01–T15) + Tier 2 (Sprint 1.5) + gap ICT (Sprint 1.6, T26–T40) + el motor confluencia→entrada en Strategy (scoring lee el mapa §3.3 + `f_selectEntryPOI` §3.4 + catálogo de setups §3.5). Nada "casi listo".
  - **(B) Enjambre COMPLETO:** no el piloto mínimo, sino el runtime entero de `ESQUELETO-P2` — **perfiles** de todos los agentes, **archivos/knowledge** (cerebro único), **skills**, **MCP** (TV + los que apliquen), **workflow** y **loop** (cron+kanban+swarm) operativos.
  - **Solo cuando (A) Y (B) estén listos** → se inicia el testeo de setups → IS/OOS → cristalización. Construir el enjambre puede ir en paralelo a Pine, pero **el testeo no empieza antes de este gate**.
- **Gate Fase 1 (PINE-PLAN §7):** validación ≥90 por concepto + gate global tras T15.
- **Gate Fase 3:** pesos/setups solo cristalizan con IS/OOS 70/30 (ADR-002). El enjambre no salta este gate (ADR-008).
- **Gate Fase 4 (ADR-003):** ningún MQL5 hasta cerrar Pine + aprobación Fable.

### §5.4 — Orden paso a paso (el plan que se sigue)

1. **(este sprint, S038)** Aprobar P3 + ADR-008 + edits de workplan. **Sin Pine.**
2. **Spike R-P3-1** (sesión Pine corta): probar `request.security` con función de estado `var` interno en D1 → confirmar que no contamina el chart. **✅ PASÓ en Sesion-039 → paso 3. ❌ Hipótesis: Problemas → DETENER + avisar a Freddy → escalar a Opus ultracode** (protocolo en §5.3). No se improvisa.
3. **T13a** núcleo MTF (escalares) → compila 0/0 → core-sync → validación → commit.
4. **T13b** mapa rico (N_htf zonas/lado, `f_nearestN` CORE, cascada) → validación → commit. **✅ COMPLETO S041** (entrega *mapa de niveles*: líneas extendidas al borde, sin geometría nativa).
4b. **T13c** mapa geométrico `[NUEVO S041, próxima sesión]` — ranura 6 campos (anclaje `tA/tB`) + dibujo nativo por `xloc.bar_time` + cap por concepto para todos + emitir BOS/CHoCH/EQH/EQL. **ADR-010** (supersede transporte ADR-009). Esqueleto implementación-ready: `docs/sprint-runs/revision-T13b-mtf-dibujo-nativo.md` §9. → compila 0/0 → core-sync → validación ≥90 → commit.
5. **T14** panel multi-columna → **T15** alertas → **gate Fase 1** (≥90 + global).
6. **Completar Pine (carril A):** Sprint 1.5 (Tier 2) + Sprint 1.6 (gap ICT T26–T40) + **Fase 2** (`f_scoreConfluences` lee el mapa §3.3 → `f_selectEntryPOI` §3.4 → catálogo de setups §3.5 en Strategy). Resultado: **Pine COMPLETO con todos los conceptos**.
7. **Construir el Enjambre completo (carril B, en paralelo a 3–6):** runtime entero de `ESQUELETO-P2` — perfiles, archivos/knowledge, skills, MCP, workflow, loop (cron+kanban+swarm). No solo el piloto.
8. **★ GATE PRE-TESTEO DE SETUPS (§5.3):** solo cuando **(A) Pine completo [paso 6] Y (B) enjambre completo [paso 7]** estén listos → se habilita el testeo. **No antes.**
9. **Testeo de setups:** el enjambre testea los setups §3.5 en **replay + entradas demo en vivo**, con TV como árbitro → track record por setup/agente (`ESQUELETO-P2 §2.6`).
10. **Fase 3:** IS/OOS 70/30 calibra pesos del scoring + del selector + admite los setups que sobreviven → cristalización (puente offline §3.6).
11. **Gate Fable (ADR-003)** → **Fase 4:** EA nativo (`SMC_MTF.mqh` + motor de decisión §3 de P1) con golden tests de paridad.

---

## §6 — Riesgos y decisiones abiertas

| # | Riesgo / pregunta | Mitigación / acción |
|---|---|---|
| **R-1** | El estado `var` por-contexto en `request.security` (R-P3-1) — la base de T13b. ¿Realmente no contamina? | **Spike test obligatorio (§5.4 paso 2)** antes de T13b. **✅ OK → continuar. ❌ Falla → DETENER, NO improvisar workaround, avisar a Freddy con diagnóstico para escalar a Opus ultracode** (protocolo §5.3). La detección HTF reducida (solo escalares) es UNA hipótesis de rediseño, pero la decide la escalada, no el [impl]. |
| **R-2** | Límite exacto del tuple de `security` en v6 (¿~127?) | `⏳ [impl]` confirmar empíricamente; ajustar `N_htf` y nº de llamadas/TF (§2.2). |
| **R-3** | Presupuesto de objetos de dibujo (mapa rico × 3 TFs > 500/tipo) | Cuota por (concepto × TF) + Present mode desde T13b (§2.5). |
| **R-4** | Setup como gate vs bonus vs etiqueta (§3.2) | Decisión de Fase 2/3; calibrar en IS/OOS, no a ojo (ADR-002). |
| **R-5** | El selector de POI (§3.4) introduce parámetros nuevos | Solo MECÁNICA ahora; pesos del ranking = Fase 3 (ADR-002). |
| **R-6** | Inputs de densidad (§2.6) explotan el panel de settings | Agrupar por TF, no 1 input por celda; defaults sensatos. |
| **R-7** | SMT Divergence (T38, P1) necesita 2º símbolo vía security → compite por presupuesto MTF | Coordinar con §2.2; va tras su ADR (P1 §4 T38). |

---

## §7 — ADR de reconciliación

Ver **`docs/adrs/ADR-008-mapa-mtf-confluencias-pared-dura.md`** (este sprint): reconcilia ADR-005/007 con los matices de S037 — enjambre **opera en vivo** pero "operar" = **entradas demo + notificación** (no reales); **pared dura** EA↔laboratorio-en-vivo; **puente offline** de confluencias/setups testeados; y registra el **mapa MTF rico** + **motor confluencia→entrada** como arquitectura adelantada de Fase 4 (`SMC_MTF.mqh`).

---

## §8 — Documentos relacionados

- Encargo: `docs/planes/HANDOFF-OPUS-MAX-mapa-mtf-confluencias.md` (S037).
- Parte 1 (conceptos + motor EA + repos): `docs/planes/ESQUELETO-P1-conceptos-EA-pine-repos.md` (§3 motor EA, §5 confluencias).
- Parte 2 (runtime enjambre): `docs/planes/ESQUELETO-P2-hermes-enjambre.md` (§2 loop, §2.6 árbitro, §2.8 push).
- Patrones de ciclo de vida: `docs/planes/ESQUELETO-MITIGACION-conceptos.md`.
- Plan Pine (MTF/dibujo/sprints): `docs/workplan/PINE-PLAN.md` §4/§5/§7.
- Confluencias canónicas: `WORKPLAN-MAESTRO-V2.md` §4.8 (+ #43–#51 en P1 §5).
- Fuente SMC + formato ficha: `docs/reglas-smc-ict.md`.
- Golden tests / paridad: `docs/workplan/MQL5-PLAN.md`.
- ADRs: ADR-001 (símbolo-agnóstico), ADR-002 (congelación umbrales), ADR-003 (ramas/gate Fase 4), ADR-005 (enjambre laboratorio), ADR-006 (pools), ADR-007 (EA razona), **ADR-008** (pared dura + mapa MTF).
