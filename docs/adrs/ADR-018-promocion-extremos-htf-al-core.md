# ADR-018 — Promoción de los extremos HTF al CORE (cierre Fase B de ADR-017)

- **Fecha:** 2026-07-10 (Sesion-114) · **Aceptada 2026-07-10 (Sesion-115)**
- **Estado:** **ACEPTADA** — GATE B (probe) pasó en vivo (S115) y el código se promovió al CORE.
  Ver "Ejecución (S115)" al final. SHA re-baselined `5510361166844bd5` → **`d86bf37aacbd25cf`**
  (CORE 1700 → **1952 líneas**).
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

## Ejecución (Sesion-115, 2026-07-10)

**GATE B (mitad viva) → VERDE.** Probe `PROBE-faseB-oom.pine` (4 `request.security`: 2 nearest +
2 extremos, D1+H1) aplicado en vivo OANDA:EURUSD junto al Visual + LuxAlgo: `pine_get_errors` = 0 a
~25s, **sin CE10117 (token) ni OOM**; checksums no-`na` (`d1 pdHigh`=`xd1 pdHigh`=1.20831 → las 4
securities computan). Server-side ya era 0/0 (S114).

**Promoción ejecutada (B2, ratificada por el usuario S115):**
1. `f_farthestZone/Pool/Event` + `f_tfExtremes` movidas al bloque `// === LIBRARY CORE ===`
   byte-idéntico en los **3** scripts (en Context se absorbieron sustituyendo su header de sección
   `// === EXTREMOS HTF (fuera del CORE) ===` por un sub-comentario `// --- ... ---`; en
   Visual/Strategy se añadieron). `f_computeTFState` (nearest-N, 89) **intacto**.
2. `check-core-sync.ps1` ×3 → **OK**; re-baseline **`5510361166844bd5` → `d86bf37aacbd25cf`**,
   CORE **1952 líneas** (1700 + 252).
3. **Strategy:** +2 `request.security` de extremos (D1 "D" + H1 "60") con `f_tfExtremes`
   (params compartidos = mismos del nearest; `kExt/minStr/inclMit` = defaults Context 6.0/0.5/false),
   reconstitución a arrays `xd1e*/xh1e*` (8 slots), enganche de scoring marcado `// TODO Sprint 2.1`.
4. **Compilación:** `pine_check` **0/0 los 3**. **Apply vivo:** Visual (con las +252 líneas
   promovidas, no usadas) 0/0; Context 0/0 (slot actualizado). Strategy: su riesgo único (4 securities)
   quedó cubierto por el probe GATE B + 0/0 server-side (no se forzó on-chart para no pisar el slot
   `[Strategy]` del usuario; sin slot propio en TV).

**Nota MQL5:** contrato de extremos añadido a `MQL5-PLAN.md` (2º struct espejo, semántica
farthest-important, `kind<0` = traspasado). Fuera de alcance v1 sigue: MB/Breaker/BOS-CHoCH heredados.
