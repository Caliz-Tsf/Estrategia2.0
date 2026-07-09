# ADR-017 — Tercer consumidor visual auxiliar `pine/SMC-Context.pine` (herencia de extremos HTF + revelado al romper)

- **Fecha:** 2026-07-08 (Sesion-110)
- **Estado:** Aceptada — **Fase A** (script Visual-only separado, LIBRARY CORE byte-idéntico, 2ª `request.security` con `f_tfExtremes` fuera del CORE); **Fase B** promueve el mecanismo al CORE (tuple único nearest+farthest que Strategy consume para scoring + re-baseline SHA + ADR nuevo).
- **Precisa (no contradice):** ADR-009/010 (transporte MTF por buffer aplanado etiquetado / dibujo geométrico anclado — intactos: el Context añade una emisión distinta, no reemplaza la nearest-N), ADR-014 (`strength` es propiedad de detección del CORE — aquí se **consume** como filtro de importancia, no se recalcula), ADR-016 (retención por importancia — el Context hereda su misma frontera CORE/Visual). No toca la calibración del scoring (ADR-002).
- **Tarea:** S110 Paso B del esqueleto `docs/planes/ESQUELETO-FABLE-context-htf-revelado.md` (diseño Fable). Veredicto de viabilidad: `docs/planes/RESPUESTA-FABLE-herencia-pierna-htf.md`. Gates A0/A2/A3 ejecutados VERDES en S109 (motor D1+H1 corre 2× en el chart sin OOM/CE10117).

## Contexto

La idea mayor del usuario (S108, `docs/planes/BRIEF-FABLE-herencia-pierna-htf-revelado.md`): el LTF (H1/M5) debe **heredar del HTF (D1) las zonas/estructura importantes más allá del Premium/Discount vigente**, en ambas direcciones, **reveladas solo cuando el precio rompe la frontera** del rango HTF (draw-on-liquidity: "si allá arriba hay un EQH que desplazó el precio hasta aquí, hay que saberlo").

**Dos bloqueadores reales impiden hacerlo dentro del Visual:**

1. **El transporte actual no lleva los extremos.** `f_nearestN` / `f_computeTFState` (CORE, byte-idéntico) emite solo los K conceptos **más cercanos** al precio → los extremos lejanos del D1 nunca viajan al H1/M5. Ensanchar la tuple del CORE rompe el SHA `5510361166844bd5`, obliga a tocar Strategy y reintroduce el riesgo OOM server-side (lección S104/S105).
2. **El Visual está pegado al techo CE10117** (~100 256 tokens compilados, S107). No cabe una feature nueva de este tamaño dentro del mismo script.

**Hallazgo que habilita Fase A sin tocar el CORE (validado vivo S109):** cada script Pine tiene su **propio presupuesto de tokens y de memoria**. Un tercer consumidor con el mismo LIBRARY CORE copiado byte-idéntico dispone de presupuesto fresco, y puede hacer su **propia 2ª `request.security` por HTF** con una función de extremos FUERA del CORE (patrón `f_m5Light`, Visual L2722; la nota L2769 ya anticipaba esta 2ª llamada). Los gates A2/A3 de S109 confirmaron empíricamente que el chart aguanta el motor completo D1+H1 corriendo **dos veces** (Visual + Context) sin "Internal server study error" ni CE10117.

## Decisión

**Se crea un tercer consumidor visual auxiliar `pine/SMC-Context.pine` (`indicator` overlay, solo dibuja) que hereda la capa de contexto HTF. El CORE y su transporte no cambian en Fase A.**

### 1. Naturaleza del script
- `indicator("SMC Engine — Context (HTF)", overlay = true, ...)` — **solo dibuja**. Sin `strategy.*`, sin `alertcondition()`, sin panel de estado (eso es del Visual).
- Contiene la sección `// === LIBRARY CORE ===` **byte-idéntica** a la de Visual/Strategy (misma regla dura #2, ahora verificada a 3 bandas).
- Su emisión MTF es **distinta al Visual**: en vez de nearest-N, `f_tfExtremes` emite el **extremo importante por concepto y por lado** (OB/FVG/POOL/EQ en v1). Vive fuera del CORE, junto a los selectores puros `f_farthestZone`/`f_farthestPool`/`f_farthestEvent`.
- 2ª `request.security` por HTF (D1 y H1) con `f_tfExtremes` + `lookahead = barmerge.lookahead_off` (anti-repaint, regla dura #1).

### 2. Frontera exacta (qué es nuevo, qué es intocable)
| Pieza | Ubicación | Cambio |
|---|---|---|
| `// === LIBRARY CORE ===` (detectores puros + UDTs) | Context | **copia byte-idéntica** del Visual (SHA `5510361166844bd5`) |
| `f_computeTFState` / `f_nearestN` (transporte nearest-N) | CORE | **sin cambio** (el Visual/Strategy los siguen usando igual) |
| `MAX_ZONES = 50` (transporte) | CORE | **sin cambio** |
| `f_tfExtremes` + `f_farthestZone`/`f_farthestPool`/`f_farthestEvent` | Context, fuera del CORE | nuevo |
| Máquina de revelado (DORMANT⇄REVEALED + histéresis) y dibujo §5.4 | Context | nuevo |
| `pine/SMC-Visual.pine`, `pine/SMC-Strategy.pine` | — | **sin cambio** por esta ADR |

### 3. Alternativas descartadas
- **(a) Implementar dentro del Visual** → choca con CE10117 (Ruta 2, formalmente muerta; A1 opcional lo cuantifica). Descartada.
- **(b) Ensanchar la tuple del CORE** (tuple único nearest + farthest) para que el transporte lleve los extremos y Strategy los consuma → obliga a re-baseline del SHA, réplica en Strategy, ADR nuevo y reacopla el riesgo OOM del transporte. Correcta a largo plazo pero fuera de alcance ahora → queda como **Fase B**, junto a la promoción de ADR-016.

## Consecuencias

- **Positivas:** la herencia de extremos HTF se implementa sin tocar el CORE ni su SHA, sin riesgo OOM en el transporte (sigue a nearest-N/50) y sin gastar el headroom CE10117 del Visual. Reversible: borrar `pine/SMC-Context.pine` + revertir esta ADR deja el sistema exactamente como estaba.
- **`check-core-sync.ps1` a 3 bandas:** el script gana un `[string]$ContextPath` opcional (default `pine/SMC-Context.pine`). Si el archivo existe, exige que su bloque CORE tenga el mismo SHA que Visual (y Visual == Strategy). Si NO existe → comportamiento actual intacto (no rompe Fase 0/CI). Solo-ASCII (PS 5.1).
- **Slot TV manual:** el MCP no crea slots nombrados; el slot `SMC_Context` (id `c098abf3`) se creó a mano en S109 vía "Hacer una copia" del Visual. Deuda operativa conocida, no de código.
- **Motor D1/H1 corre 2× en el chart:** validado viable en memoria (A2/A3 S109). Si en algún par/timeframe futuro degradara, la vía de escape es Context solo-bajo-demanda (el usuario lo activa al operar) — no bloquea Fase A.
- **Deuda asumida (se cierra en Fase B):** el Context es un cuarto punto de verdad de la retención/emisión mientras Strategy no puntúe extremos. Aceptada porque Strategy aún no consume la capa de contexto. Fase B promueve `f_tfExtremes` al CORE como tuple único, replica a Strategy, re-baseline del SHA y actualiza `MQL5-PLAN`.
- **Presupuesto de tinta:** el Context tiene su PROPIO `max_*_count` (=100) y no compite con el ≤25/≤60 del Visual. En régimen normal (sin ruptura, `i_ctxAlways=false`) añade **0 tinta**; revelado, ≤16 objetos por HTF con slots fijos (RE10045-safe). Aún así respeta la regla de solape MTF (Tarea #2 S108, prerrequisito del Paso E).
