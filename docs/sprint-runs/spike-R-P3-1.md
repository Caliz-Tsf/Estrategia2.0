# Spike R-P3-1 — estado `var` interno por-contexto en `request.security`

> Gate técnico de ESQUELETO-P3 §6 R-1 / §5.4 paso 2. Decide si la cadena de
> detección MTF puede encapsularse en `f_computeTFState` sin contaminar el chart.
> **Sesión-039 (2026-06-20).**

## Hipótesis a verificar (R-P3-1)
`request.security(sym, "D", f(), lookahead = barmerge.lookahead_off)`, donde `f()`
usa un `var` **interno a la función**, mantiene su estado **por-contexto** (la serie
D1, independiente del chart H1) y **no contamina** el contexto del chart. Si en cambio
referenciara `var` globales del consumidor, contaminaría (§107 del esqueleto).

## Diseño del spike (script efímero, no guardado como concepto)
Función `f_state()` con `var int bars` + `var float lastClose`, llamada en dos
contextos: directo en el chart (H1) y vía `request.security(..., "D", ...)`.
Cross-check determinista: comparar el contador `var` contra el `bar_index` propio
de cada contexto. Si el `var` incrementa exactamente 1 vez por barra del contexto,
entonces `bars == bar_index + 1` en ese contexto.

## Resultado (EURUSD, chart H1)
| métrica | valor | lectura |
|---|---|---|
| chart var bars | 9120 | = chart `bar_index`+1 (9120) → **match SI** |
| htf var bars (D1) | 6266 | = htf `bar_index`+1 D1 (6266) → **match SI** |
| contextos difieren | SI | 6266 ≠ 9120 |
| **VEREDICTO** | **PER-CONTEXTO OK** | |

`chartBars=9120` (≈1.5 años de H1 cargados) y `htfBars=6266` (≈24 años de historia
D1 que TV carga para el contexto diario). El `var` del contexto D1 acumuló sobre **su
propia** historia, no la del chart. Ambos coinciden al dedillo con el `bar_index+1`
de su contexto → el `var` vive enteramente en el contexto de evaluación. Si hubiera
contaminación, `htfBars` habría seguido al chart (≈9120). No ocurrió.

## Veredicto
**✅ R-P3-1 PASA.** La encapsulación de la cadena de detección en
`f_computeTFState` evaluada vía `request.security(..., lookahead_off)` mantiene
estado por-contexto sin contaminar el chart. **Se habilita T13a → T13b** (protocolo
ESQUELETO-P3 §5.3: ✅ pasa = continuar).

## Notas operativas
- Spike compiló **0/0** en TV. Anti-repaint respetado (`lookahead = barmerge.lookahead_off`).
- El script efímero **no es un slot guardado**; se inyectó en el editor, se midió y
  se restauró `pine/SMC-Visual.pine` al slot `SMC_Library` (git = fuente de verdad).
- CORE de los 3 archivos Pine **intacto** — el spike no tocó `pine/*.pine`.
