# ADR-018 — Promoción de los extremos HTF al CORE (cierre Fase B de ADR-017)

- **Fecha:** 2026-07-10 (Sesion-114)
- **Estado:** **Propuesta** — no se ejecuta hasta que el **GATE B (probe)** pase en vivo (token + OOM).
  Al pasar el probe y promover el código → pasa a **Aceptada** y se re-baseline el SHA.
- **Cierra:** la deuda de **ADR-017** (Fase A): "Fase B promueve `f_tfExtremes` al CORE, replica a
  Strategy, re-baseline del SHA y actualiza `MQL5-PLAN`".
- **Precisa (no contradice):** ADR-009/010 (transporte nearest-N por buffer aplanado / dibujo
  anclado — **intactos**, el nearest-N de 89 campos no se toca), ADR-014 (`strength` es propiedad de
  detección del CORE — aquí se **consume** como filtro de importancia), ADR-016 (retención por
  importancia — misma frontera), ADR-017 (esta ADR es su Fase B). No cambia la calibración del
  scoring (ADR-002).
- **Diseño de base:** `docs/planes/DISEÑO-fase-B-promocion-core.md` (S114).

## Contexto

En Fase A la herencia de extremos HTF (`f_tfExtremes` + `f_farthestZone/Pool/Event`) vive **FUERA
del CORE**, solo en `SMC-Context.pine`, que **solo dibuja**. Mientras Strategy no puntúe los
extremos, el Context es un **cuarto punto de verdad** de la emisión (deuda aceptada en ADR-017).

Fase B promueve ese mecanismo al CORE para que **Strategy consuma los extremos en el scoring
direccional** (§4.8: objetivos de liquidez / confluencias de contexto en ambas direcciones), quede
bajo `check-core-sync` a 3 bandas (single source of truth) y se traduzca a MQL5 (Fase 4).

**Costo:** rompe el SHA `5510361166844bd5`, obliga a tocar Strategy y **reacopla el riesgo OOM** del
transporte MTF (lección S104/S105: el motor pesado vía `request.security` puede reventar el límite
server-side). Por eso el paso va **precedido de un probe** (GATE B) que aísla ese riesgo antes de
romper nada.

## Decisión

**Se promueven `f_tfExtremes` + `f_farthestZone/Pool/Event` al bloque `// === LIBRARY CORE ===`
(byte-idénticos en Visual/Strategy/Context) como funciones SEPARADAS. `f_computeTFState` (nearest-N,
89 campos) NO cambia. Strategy añade una 2ª `request.security` por HTF (D1+H1) que llama a la
`f_tfExtremes` promovida y reconstituye los extremos para el scoring.** (Opción **B2** del diseño.)

### Por qué B2 y no "tuple único" físico (B1)

ADR-017 escribió "tuple único nearest+farthest". Se **reinterpreta** como **"única fuente de verdad
en el CORE"**, no como una sola tupla física de 137 campos:

- **B1 (fusionar en un tuple de 137)** obliga a Strategy a destructurar 137 vars × 2 securities
  (×3 si activa M5), empuja el techo de token CE10117 (Strategy ya tiene 2546 líneas) y mezcla dos
  semánticas (cercano vs. lejano) en la misma ranura → MQL5 más frágil.
- **B2** deja el tuple nearest de **89 campos —lo más probado del sistema— intacto** (cero regresión
  en Visual/Strategy ya validado), y el código que se promueve es **exactamente el que corre 0/0 en
  Context desde S110**. Menor token, menor riesgo, dos structs MQL5 limpios.

### Frontera de cambio

| Pieza | Fase B |
|---|---|
| `f_computeTFState` / `f_nearestN*` / `MAX_ZONES=50` | **sin cambio** |
| `f_tfExtremes` + `f_farthestZone/Pool/Event` | **entran al CORE** byte-idéntico ×3 |
| `SMC-Visual.pine` | re-baseline CORE; **no consume extremos** |
| `SMC-Strategy.pine` | **+2 `request.security` extremos (D1+H1)** + reconstitución + `// TODO Sprint 2.1` |
| `SMC-Context.pine` | la llamada a `f_tfExtremes` **no cambia**; la función migra dentro del marcador CORE |
| `check-core-sync.ps1` | sin cambio de script; nuevo SHA cubre las funciones promovidas |
| SHA `5510361166844bd5` | **re-baseline** (nuevo hash ×3 + ESTADO-ACTUAL + memorias) |
| `MQL5-PLAN.md` | **+ contrato de extremos** (2º struct espejo) |

**Fuera de alcance v1:** MB / Breaker / BOS-CHoCH como extremos heredados (v2). Solo OB/FVG/POOL/EQ.

### GATE B (prerrequisito de ejecución)

Probe con forma de Strategy corriendo **4 `request.security`** (2 nearest + 2 extremos, D1+H1) en un
solo script. Pasa si: `pine_check` 0/0 **y** apply en TV sin CE10117 **y** sin OOM **y** checksums
no-`na`. Fallbacks si falla: extremos solo-D1 (1 security) por token; extremos bajo input
`i_scoreExtremes` (default off) por OOM. Detalle: DISEÑO §5.

## Alternativas descartadas

- **(B1) Tuple físico único de 137 campos** → token/OOM/MQL5 peor; descartada a favor de B2 (misma meta).
- **(No promover, dejar Context como está)** → deja el 4º punto de verdad abierto y Strategy nunca
  puntúa extremos; incompatible con Fase 2 scoring. Descartada.
- **Promover también el nearest-N a un tuple combinado** → innecesario; nearest ya está en el CORE.

## Consecuencias

- **Positivas:** Strategy puede puntuar contexto HTF; la emisión de extremos queda bajo
  `check-core-sync` (cierra el 4º punto de verdad); MQL5 recibe el contrato. El tuple nearest de 89
  no se toca (cero regresión). El código promovido ya está validado vivo (S110-S113).
- **Rompe el SHA:** re-baseline en los 3 scripts + ESTADO-ACTUAL + memorias. Primera ruptura desde
  que se fijó `5510361166844bd5`.
- **Riesgo OOM/token reacoplado:** mitigado por el probe (GATE B) que corre **antes** de romper el
  SHA, con fallbacks definidos.
- **Reversibilidad:** menor que Fase A (Fase A se revertía borrando un archivo). Revertir Fase B =
  sacar las funciones del CORE + revertir Strategy + volver al SHA anterior. Los commits por concepto
  lo hacen acotado, pero **no es un borrado limpio** → se ejecuta solo con probe verde + confirmación.
- **F1-GATE:** Fase B es prerrequisito de cierre, no la firma. La firma sigue siendo humana.
