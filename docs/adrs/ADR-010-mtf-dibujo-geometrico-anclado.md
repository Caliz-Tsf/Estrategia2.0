# ADR-010 — Mapa MTF geométrico: anclaje temporal + dibujo nativo por concepto (supersede el transporte de ADR-009)

- **Fecha:** 2026-06-20 (Sesion-041)
- **Estado:** Aceptado — **implementación diferida a T13c** (próxima sesión, decisión Freddy S041).
- **Precisa / reemplaza:** supersede **solo el contrato de transporte y el dibujo** de **ADR-009** (ranura de 4 campos `[kind,top,bottom,dir]` sin anclaje, dibujada como niveles extendidos al borde) → ranura de **6 campos con anclaje temporal** + **dibujo de la forma nativa** por concepto. **El resto de ADR-009 queda intacto y vigente:** buffer genérico etiquetado por `kind`, selección por cercanía al precio, mitigación dinámica por filtro, 1 llamada `security`/TF (2ª preparada), paridad MQL5 `SMC_MTF.mqh`, cascada D1→{H1,M5} / H1→{M5}.
- **Tarea:** F1-S1.4-T13c (mapa MTF geométrico). Origen: revisión pedida por Freddy, S041.
- **Diseño y esqueleto implementación-ready:** `docs/sprint-runs/revision-T13b-mtf-dibujo-nativo.md` (§4bis, §5, §6, §9).

## Contexto

T13b (✅ S041) implementó el transporte de zonas/eventos HTF como **buffer genérico etiquetado** (ADR-009) y funciona: la cascada corre en runtime, con cap por concepto y anti-repaint. Pero **ADR-009 decidió a propósito omitir `barTime`** y dibujar todo como *"niveles de referencia extendidos al borde actual, no anclados a su barra de origen"* (ADR-009, sección de contrato de la ranura), para ahorrar presupuesto del tuple.

La validación visual (EURUSD M5 con H1/D1 heredados, S041) mostró que esa simplificación **no cubre el caso de uso**:
- las cajas (OB/FVG) se degradan a **dos líneas punteadas** (no se ve la caja);
- el **sweep** sale como una línea a la derecha del precio, no como una marca en el swing barrido;
- **EQH/EQL** y **BOS/CHoCH** ni siquiera se transfieren con forma propia.

Freddy: *"si se determina que el dibujo de un concepto es una caja, se tiene que ver la caja en las temporalidades más bajas; si son líneas como EQH/EQL deben verse en M5 donde realmente se crearon y de qué línea a qué línea; un BOS o un CHoCH al transferirse debe ir desde donde inicia hasta donde termina, pero en la temporalidad menor."* Y el caso central: *CHoCH en D1 + desplazamiento/FVG en H1 → quiero verlos en M5, cada uno con su forma, para esperar la mitigación y entrar.*

## Decisión

**El mapa rico de cada HTF transporta el anclaje temporal de cada objeto, y el consumidor reconstruye su forma nativa anclada por tiempo (`xloc.bar_time`) en el TF menor.**

### 1. Contrato de la ranura (canónico — replicar en MQL5 `SMC_MTF.mqh`, Fase 4)

```
ranura_i = [ kind, top, bottom, dir, tA, tB ]   // 6 números (antes 4)
  tA : tiempo de la barra de ORIGEN (left de la caja / 1er toque EQ / inicio del tramo BOS-CHoCH / barra del sweep / barra del pool)
  tB : tiempo de FIN (na = extiende al borde actual; 2º toque EQ; barra de ruptura BOS-CHoCH)
  puntos (pool/sweep): top==bottom==level, tB=na
```

Tuple de `f_computeTFState` = **17 escalares (T13a) + K ranuras × 6**. Con **K=12** → `17 + 72 = 89 < ~127` (1 llamada `security`/TF; holgado). Si en Fase 3 falta densidad → 2ª llamada/TF (ADR-009 ya la dejó preparada). `time` epoch-ms cabe exacto en float64.

### 2. Dibujo nativo por `kind` en el consumidor (`xloc.bar_time`)

El `bar_index` del contexto HTF NO mapea al chart; el **tiempo SÍ**. El consumidor hace `switch` sobre `kind`:

| `kind` | Forma nativa en el LTF |
|---|---|
| `KIND_OB` / `KIND_FVG` | `box.new(left=tA, right=tB|borde, top, bottom)` tenue + prefijo `D1:`/`H1:`; OB y FVG con tono distinto |
| `KIND_EQH` / `KIND_EQL` | `line.new(tA→tB, level)` punteada + etiqueta |
| `KIND_BOS` / `KIND_CHOCH` | `line.new(origen tA → ruptura tB, level)` + etiqueta (estilo `f_drawStructure` SC_MAJOR, que ya usa `xloc.bar_time`) |
| `KIND_SWEEP` | marca ▲ (BSL, arriba) / ▼ (SSL, abajo) en la barra `tA` |
| `KIND_POOL` | línea horizontal del nivel anclada a su barra |

### 3. Cap 0-10 por concepto para TODOS los conceptos

Hoy solo OB/FVG/pool tienen cap. Se extiende: **cada concepto detectado tiene su toggle de traspaso + su cap 0-10** (0 = no transferir). Recordatorio (heredado de ADR-009): el cap por concepto es un **filtro de elegibilidad**; el **cap global K por TF** decide qué se dibuja (los K más cercanos al precio). Con ~40-50 conceptos no hay cupo garantizado por concepto: se ven los K más cercanos por TF. Cada HTF tiene su propio buffer K → D1 y H1 no compiten entre sí (por eso el caso "CHoCH D1 + FVG H1" se ve completo).

### 4. Emitir al buffer los conceptos que faltan

BOS/CHoCH (hoy solo escalar) y EQH/EQL (hoy solo alimentan pools) se **emiten también** como ranuras con sus `tA/tB`. El pipeline (`f_nearestN`, selección global, aplanado) no cambia de forma — solo crece la ranura a 6 campos y `f_nearestN` anexa los tiempos.

## Alternativas descartadas

- **Mantener el mapa de niveles de ADR-009 (4 campos):** no cubre el caso de uso (cajas degradadas, sweep mal ubicado, EQ/estructura ausentes). Descartada por la validación S041.
- **Anclar por `bar_index` en vez de `xloc.bar_time`:** el `bar_index` del contexto HTF no corresponde al del chart LTF → el objeto caería en la barra equivocada. Descartada (gotcha documentado en §9).
- **Slots por concepto en el tuple:** ya descartada en ADR-009 (no escala a 50-60 conceptos). Se conserva el buffer genérico.
- **Subir K a 16 con ranura 6 (= 113):** cabe pero al límite (~127, empírico). Se elige **K=12** por holgura; subir solo si compila y se necesita densidad.

## Consecuencias

- **CORE byte-idéntico (regla #2):** crecen `f_computeTFState` (emite 6 campos + conceptos nuevos) y `f_nearestN`/`f_nearestNPools` (anexan tiempos); nueva selección para conceptos con dos extremos. SHA y nº de líneas cambian (documentar en el commit de T13c) + `check-core-sync.ps1`.
- **Presentación (Visual-only):** `f_drawMTFZones` se reescribe con `switch` + `xloc.bar_time` + un `var array<box>` propio para las cajas. NO entra al CORE (no rompe core-sync).
- **Settings (`GRP_MTF`):** caps nuevos por concepto (sweep/EQ/BOS/CHoCH) + opcional estilo de sweep.
- **Paridad MQL5 (ADR-002):** la ranura de 6 campos con anclaje es el formato canónico de `SMC_MTF.mqh`; el anclaje temporal **mejora** la paridad (el EA dibuja por tiempo igual que Pine).
- **Anti-repaint (regla #1):** sin cambios; `lookahead_off` + eventos en `barstate.isconfirmed`.
- **Extensibilidad:** los ~40-50 conceptos futuros (Sprint 1.5/1.6) se añaden con `push` + `kind` + sus `tA/tB`; el contrato del tuple NO cambia.

## Documentos relacionados

- `docs/sprint-runs/revision-T13b-mtf-dibujo-nativo.md` — revisión completa + esqueleto implementación-ready (§9).
- `docs/adrs/ADR-009-transporte-mtf-buffer-generico-etiquetado.md` — buffer genérico (vigente); su contrato de transporte/dibujo queda superado por este ADR.
- `docs/sprint-runs/spec-T13b-mtf-rico.md` — T13b (mapa de niveles, base de T13c).
- `docs/workplan/PINE-PLAN.md` §7 (ítem 13c) · `docs/planes/ESQUELETO-P3-mapa-mtf-confluencias.md` §4.1/§5.
