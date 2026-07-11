# DISEÑO — Fase B: promoción de los extremos HTF al CORE

> Cierre de la deuda de ADR-017 (Fase A). Diseño local, **antes de tocar el CORE**.
> Sesión-114 (2026-07-10). Decisión de arquitectura → se ratifica en **ADR-018** (Propuesta).
> Regla dura: no se rompe el SHA `5510361166844bd5` hasta que el **probe** (GATE B) pase en vivo.

> **RESUELTO (S115, 2026-07-10):** GATE B pasó en vivo (probe 4 securities 0/0, sin CE10117/OOM).
> **B2 ratificada** por el usuario y **ejecutada**: extremos promovidos al CORE ×3, Strategy +2
> security de extremos. SHA re-baselined **`5510361166844bd5` → `d86bf37aacbd25cf`** (CORE 1952
> líneas). ADR-018 → **Aceptada**. Detalle en ADR-018 §"Ejecución (Sesion-115)".

---

## 0. Qué cierra Fase B

En Fase A (ADR-017, S110-S113) la herencia de extremos HTF vive en un **tercer consumidor**
`pine/SMC-Context.pine` que **solo dibuja**. Su emisión (`f_tfExtremes` + selectores
`f_farthestZone/Pool/Event`) está **FUERA del CORE byte-idéntico**. Consecuencia asumida
(ADR-017 §Consecuencias): el Context es un **cuarto punto de verdad** de la retención/emisión
mientras **Strategy no puntúe los extremos**.

**Fase B = promover ese mecanismo al CORE** para que:
1. `Strategy` consuma los extremos HTF (scoring direccional §4.8: "si allá arriba hay un EQH que
   desplazó el precio hasta aquí, cuenta como objetivo de liquidez / confluencia").
2. La emisión de extremos quede bajo `check-core-sync` (single source of truth a 3 bandas),
   cerrando el cuarto punto de verdad.
3. `MQL5-PLAN` se actualice con el contrato de extremos (Fase 4 lo traduce).

Esto **rompe el SHA** (el CORE gana funciones), **obliga a tocar Strategy**, y **reacopla el
riesgo OOM** del transporte MTF (lección S104/S105). Por eso es el paso pesado.

---

## 1. Estado real medido (S114)

| Función | Ubicación hoy | Params | Emisión | Campos del tuple | Consumidores |
|---|---|---|---|---|---|
| `f_computeTFState` | **CORE** (byte-idéntico ×3) | 18 | nearest-N (K más cercanos a px) | **89** = 17 escalares + 12 slots×6 | Visual (panel), Strategy (D1+H1) |
| `f_tfExtremes` | **FUERA CORE** (solo Context) | 14 | farthest-important (extremo por concepto/lado) | **51** = 3 escalares + 8 slots×6 | Context (D1+H1) |
| `f_farthestZone/Pool/Event` | FUERA CORE (Context) | — | selectores puros RE10045-safe | — | los llama `f_tfExtremes` |

**Strategy hoy** (`SMC-Strategy.pine` L2490-2491): **2** `request.security` (D1 "D", H1 "60")
con `f_computeTFState` → destructura 89 campos ×2. **No corre M5** (nota L2495). **No consume
extremos** todavía.

**Params:** `f_computeTFState` y `f_tfExtremes` comparten los 11 params de detección; difieren en
la cola: `f_computeTFState` toma 7 `cap*` (nearest-N), `f_tfExtremes` toma `kExt, minStr, inclMit`
(selección de extremos). Los cuerpos de **detección son idénticos** (mismo motor, garantía de
paridad; por eso Context copió el cuerpo verbatim).

---

## 2. Dos realizaciones posibles

### B1 — Tuple único (un solo `f_computeTFState` que emite nearest **y** farthest)

Ensanchar `f_computeTFState`: añadir params `kExt, minStr, inclMit` y, tras el bloque nearest-N,
correr los 8 selectores farthest y **anexar 48 campos** al tuple → **137 campos** (89 + 48).

- **Strategy** destructura **137 vars × 2 securities** (D1+H1). Si algún día activa M5 → ×3.
- **Visual** tendría que destructurar 137 aunque ignore los 48 (o mantener una firma dual).
- **Token (CE10117):** Strategy ya es un script grande (2546 líneas). Añadir 48 vars×2 al
  destructure + los 8 selectores dentro del CORE (que se compila en los 3) empuja hacia el techo
  100 256. **Riesgo alto y difícil de medir** antes del apply (lección S107: `pine_check` no
  cuenta tokens).
- **OOM:** un solo motor por security hace **ambas** selecciones → +8 llamadas `f_farthest*` por
  security. En Strategy son 2 securities (×3 si M5). Sensible.
- **MQL5:** un struct espejo con 137 campos, mezclando dos semánticas (cercano vs. lejano) en la
  misma ranura → más difícil de traducir con golden tests.

### B2 — Función promovida separada (RECOMENDADA)

Mover `f_tfExtremes` + `f_farthestZone/Pool/Event` **al CORE tal cual** (funciones separadas,
byte-idénticas ×3). `f_computeTFState` **no cambia** (los 89 campos siguen intactos). Cada
consumidor pide extremos **solo si los necesita**, con su propia `request.security`.

- **Strategy** añade **un 2º par** de `request.security` (D1+H1) con `f_tfExtremes` → +51 vars×2,
  **solo cuando el scoring los use**. El destructure de 89 nearest **no se toca** (cero regresión
  en lo ya validado).
- **Visual:** **sin cambio** (no consume extremos; sigue con nearest-N).
- **Context:** su llamada a `f_tfExtremes` **no cambia una coma** — la función ahora vive en el
  CORE, así que queda cubierta por `check-core-sync`. Cierra el 4º punto de verdad **sin reescribir
  Context**.
- **Token:** el CORE gana ~130 líneas (f_tfExtremes + 3 selectores). Strategy gana +51 vars×2 de
  destructure. Menor que B1. Aun así hay que medirlo (GATE B).
- **OOM:** Strategy pasa de 2 a **4** securities (D1nearest, H1nearest, D1ext, H1ext). Es el punto
  a probar. Precedente favorable: en Context el motor D1+H1 corre 2× **junto al Visual** sin OOM
  (A2/A3 S109) — pero ahí eran scripts distintos con presupuestos separados; **aquí las 4 caben en
  un solo Strategy**. Ese es exactamente el riesgo que aísla el probe.
- **MQL5:** dos structs espejo limpios (nearest vs. extremos), cada uno con su semántica. Traducción
  directa.

### Recomendación

**B2.** Misma meta que ADR-017 (Strategy puntúa extremos; emisión bajo single-source; MQL5
actualizado) con **mucho menor riesgo de regresión y token**: el tuple nearest de 89 campos —lo más
probado del sistema— queda **intacto**, y el código de extremos que se promueve es **exactamente el
que ya corre 0/0 en Context** desde S110. "Tuple único" de ADR-017 se reinterpreta como **"única
fuente de verdad en el CORE"**, no como "una sola tupla física de 137 campos". Esta reinterpretación
es la decisión central de **ADR-018**.

> Nota sobre "~62 campos" (estimación en ESTADO-ACTUAL): no se sostiene contra la medición. El tuple
> de extremos real es **51 campos** (B2, sin cambio) o **137** (B1, tuple fusionado). Se corrige aquí.

---

## 3. Frontera de cambio (B2)

| Pieza | Hoy | Fase B |
|---|---|---|
| `f_computeTFState` (nearest-N, 89) | CORE | **sin cambio** |
| `f_nearestN/NPools/NEvents`, `MAX_ZONES=50` | CORE | **sin cambio** |
| `f_tfExtremes` (51) | fuera CORE (Context) | **→ entra al CORE** (byte-idéntico ×3) |
| `f_farthestZone/Pool/Event` | fuera CORE (Context) | **→ entran al CORE** |
| Cuerpo de detección duplicado en `f_tfExtremes` | copia verbatim | queda; el CORE ahora lo contiene una vez, byte-idéntico ×3 |
| `SMC-Visual.pine` | — | CORE re-baseline (mismo bloque nuevo) — **no consume extremos** |
| `SMC-Strategy.pine` | 2 security nearest | **+2 security extremos (D1+H1)** + reconstitución + wiring de scoring |
| `SMC-Context.pine` | llama `f_tfExtremes` fuera CORE | **la llamada no cambia**; la función migra al bloque CORE |
| `check-core-sync.ps1` | ×3 sobre bloque CORE | **sin cambio de script**; el nuevo SHA cubre las funciones promovidas |
| `MQL5-PLAN.md` | structs nearest | **+ contrato de extremos** |
| SHA CORE `5510361166844bd5` | — | **re-baseline** (nuevo hash en los 3 + ESTADO-ACTUAL + memorias) |

**Lo que NO entra en v1** (ADR-017 §alcance): MB / Breaker / BOS-CHoCH como extremos heredados
(v2). Solo OB/FVG/POOL/EQ, exactamente como Context hoy.

---

## 4. Contrato del tuple de extremos promovido (51 campos)

Idéntico al que `f_tfExtremes` ya emite (SMC-Context.pine L1975-1983):

```
[ pdHigh, pdLow, atr14,                              // 3 escalares
  kind, top, bottom, dir, strengthAnchor, tB ] ×8    // 8 slots × 6 campos
```

Orden de slots: **OB↑, OB↓, FVG↑, FVG↓, POOL↑, POOL↓, EQH↑, EQL↓**.

- `kind` con **signo NEGATIVO = traspasado/tomado** (mitigada / pool barrido / EQ cruzado) — patrón
  F1-CTX-04/05/06. `0` = slot vacío (ADR-010).
- Anti-repaint: `request.security(..., lookahead = barmerge.lookahead_off)` (regla #1). El cuerpo
  solo emite en el contexto HTF confirmado.

**Cómo lo consume Strategy (scoring §4.8, wiring Sprint 2.1):** los extremos son **objetivos de
liquidez / confluencias de contexto**, no señales de entrada por sí solas. Entran al `scoreLong/
scoreShort` como:
- EQH↑/POOL↑ vivos por encima → **objetivo de liquidez alcista** (peso `wLiqTarget`).
- OB↑/FVG↑ vivos por encima → **confluencia de origen/mitigación pendiente** en la pierna.
- `kind<0` (traspasado) → **contexto histórico**, peso reducido o cero (no es objetivo vigente).
El wiring fino de pesos es Sprint 2.1 (no Fase B); Fase B **entrega los datos** al Strategy y deja
el enganche marcado con `// TODO Sprint 2.1` como el resto del scoring.

---

## 5. GATE B — el probe (antes de romper el SHA)

Análogo a GATE A2/A3 (S109). **Aísla el único riesgo nuevo de B2:** que las **4 `request.security`
en un solo Strategy** (2 nearest + 2 extremos) quepan en token **y** memoria.

**Forma del probe:** copia de `SMC-Strategy.pine` (o script mínimo con el CORE + las 4 securities)
que:
1. Corre `f_computeTFState` D1+H1 (89 ×2) — como hoy.
2. Corre `f_tfExtremes` D1+H1 (51 ×2) — lo nuevo.
3. Destructura los 4 tuples y emite unos `plot` de checksum (kind0, pdHigh, extremo) para probar que
   los valores viajan.

**Criterios de paso:**
- `pine_check.py` (server-side) → **0/0**.
- Apply en TV (OANDA:EURUSD H1, junto a nada más) → **sin CE10117** (esperar ~20s, `pine_get_errors`;
  lección S107: el token real solo aparece en apply).
- Apply → **sin "Internal server study error" / OOM** (lección S104/S105).
- Checksums no-`na` (los 4 tuples pueblan).

**Si el probe PASA** → se procede a promover al CORE real (Fase B ejecución).
**Si FALLA por token (CE10117)** → fallback a **B2-lite**: Strategy pide extremos **solo D1** (1
security nueva, no 2), o comparte el motor (extremos derivados del mismo `zonesTf` sin 2ª security —
requiere que nearest y farthest salgan de UNA llamada, que es B1 parcial). Se decide con el número real.
**Si FALLA por OOM** → Strategy consume extremos **bajo demanda** (input `i_scoreExtremes`, default
off hasta Fase 3), igual que la vía de escape de ADR-017.

**Bloqueo actual:** TV/CDP caído (S114). El probe **no corre hoy**; queda el script listo y se
ejecuta al relanzar `tv_launch`.

---

## 6. Secuencia de ejecución (cuando el probe pase)

1. **Promover** `f_farthestZone/Pool/Event` + `f_tfExtremes` al final del bloque `// === LIBRARY
   CORE ===` en los **3** scripts, byte-idénticos. (En Context ya existen fuera del CORE → se
   MUEVEN dentro del marcador; en Visual/Strategy se AÑADEN.)
2. `scripts/check-core-sync.ps1` → recalcular SHA, confirmar los 3 iguales. **Re-baseline** el hash
   en ESTADO-ACTUAL + memorias + este doc + ADR-018.
3. **Strategy:** añadir las 2 `request.security` de extremos (D1+H1), reconstituir a struct/arrays,
   marcar el enganche de scoring `// TODO Sprint 2.1`.
4. `pine_check` 0/0 los 3 + apply vivo los 3 sin CE10117/OOM.
5. **ADR-018 → Aceptada.** Actualizar `MQL5-PLAN.md` (contrato extremos). Commit(s) por concepto.
6. Firma **F1-GATE** (aprobación humana) — desbloqueada solo tras 4 verde.

---

## 7. Riesgos y mitigaciones

| Riesgo | Prob. | Mitigación |
|---|---|---|
| CE10117 en Strategy (4 destructure) | media | GATE B mide antes de romper SHA; fallback B2-lite (extremos solo D1) |
| OOM 4 securities en un script | media | precedente A2/A3 favorable pero distinto; fallback bajo-demanda `i_scoreExtremes` |
| Regresión en nearest-N (89) | **baja** | B2 **no toca** `f_computeTFState` ni su tuple |
| Desincronía CORE ×3 | baja | `check-core-sync` a 3 bandas ya operativo (S110) |
| Paridad MQL5 | baja | dos structs limpios; contrato en MQL5-PLAN |

---

## 8. Decisión pendiente del usuario

- **B2 vs B1:** este doc recomienda **B2**. Ratificar en ADR-018.
- **Alcance extremos en scoring:** ¿Strategy consume extremos **siempre** o **bajo input**
  (`i_scoreExtremes` default off) hasta Fase 3? (afecta el fallback del probe).
- **F1-GATE:** la firma sigue siendo humana; Fase B es prerequisito de cierre, no la firma en sí.
