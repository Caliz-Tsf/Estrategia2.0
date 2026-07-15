# DISEÑO — Opción C: dealing range PEGAJOSO por temporalidad · S128

> Continuación de [DISENO-ancla-dealing-range-S128.md](DISENO-ancla-dealing-range-S128.md), cuyo probe
> midió el contraste EQUIVOCADO (ver §1). Diseño pedido por el usuario en S128.
> **Estado: PROPUESTA — nada implementado. `pine/` intacto, CORE SHA `752b4083a7db419d`, core-sync OK ×3.**
> Fuentes: [reglas-smc-ict.md §2.3](../reglas-smc-ict.md) · [§5.16](../reglas-smc-ict.md) ·
> [decisiones-pd-rango.md](../decisiones-pd-rango.md) (S021/S057/S091) · [[Sesion-127]] · [[Sesion-128]].

## 1. Dos errores propios que hay que dejar por escrito

1. **`structMajor` NO es el ancla de la Opción B.** El diseño previo (§1.1) lo afirmó y es falso:
   `structMajor` reancla en **cada pivote confirmado** ([:2216](../../pine/SMC-Visual.pine)), mientras que
   la Opción B documentada dice *"los niveles cuya **ruptura** generó el último BOS/CHoCH"*. Es un
   proxy malo.
2. **Por tanto el probe de S128 midió el contraste equivocado.** Comparó A (trailing) vs `structMajor`:
   **las dos caminan**. Que `structMajor.lowLevel` nunca baje de `pdLow` (0 de 6283) es un hecho real
   pero **no dice nada** sobre un ancla pegajosa. La conclusión "el ancla no puede ensanchar el
   alcance" **solo vale para ese B**, no para la Opción C.

Lo que sí sobrevive del probe anterior: **P1** (A y B coinciden 96.8% — pero entre dos anclas que
caminan, así que es tautológico), **P3** (`legExtLo` ≡ `min(pdLow, structMajor.lowLevel)`, identidad
útil) y sobre todo **P4 refutada**: el archivo NO es anidado por construcción (680/6283 = 10.8%).

## 2. El problema real: la jerarquía está INVERTIDA (no solo desplazada)

Medido en vivo (D1 OANDA:EURUSD, 500 velas, `close` 1.14380):

| Rango | Amplitud | Debería ser |
|---|---|---|
| **D1 implementado** `[1.13246, 1.20831]` | **758 pips** | el más ancho |
| Lectura del usuario **D1** `[~0.9536, 1.60554]` | **~6500 pips** | ✔ |
| Lectura del usuario **H1** `[1.02175, 1.39970]` | **~3780 pips** | ✔ |
| Lectura del usuario **M5** | local (~decenas de pips) | ✔ |

**El rango D1 de hoy (758 pips) es MÁS ESTRECHO que lo que debería medir el de H1 (~3780).** No es que
el ancla esté "un poco desplazada": la escala está invertida. Ese es el defecto, y explica de un tirón:
- el alcance de abajo (115 pips) vs arriba (643) del censo S127;
- los 5 OB + 11 FVG + 1 BRK + 3 IFVG vivos e invisibles bajo `pdLow`;
- que `i_profundidad` 4/5 parezca inútil (el archivo de un rango-ventana no puede cubrir nada).

## 3. La regla (Opción C) — y por qué se auto-escala sin parámetros nuevos

**C1 (lados independientes, la mínima):**

```
// por TF, en barstate.isconfirmed:
strongHigh:  se queda.  Solo reancla si close > strongHigh  (violado)  -> nuevo pivote de escala pdSwingLen
strongLow:   se queda.  Solo reancla si close < strongLow   (violado)  -> nuevo pivote de escala pdSwingLen
```

Es **el mismo `i_pdSwingLen`=50 que ya existe**. Lo único que cambia es *cuándo* se llama al reset:
hoy en **cada** pivote confirmado, en C **solo tras violación**.

**Por qué reproduce las tres lecturas del usuario con una sola regla:**
- **D1** (50 velas ≈ 2.5 meses): el último bajo cerrado por debajo fue 2022 (~0.95) → se queda desde
  entonces. El último alto cerrado por encima fue 2008 (1.60554) → se queda. → `[0.95, 1.60554]` ✔
- **H1** (50 velas ≈ 2 días): altos/bajos se violan cada pocos días → anclajes recientes →
  `[1.02175, 1.39970]` ✔
- **M5**: se viola constantemente → camina ✔

> **La auto-escala es la propiedad clave.** El usuario pidió "en M5/H1 que persiga pivotes, en D1 que se
> quede". No hace falta ningún hack por timeframe: es la **frecuencia de violación** la que difiere, y
> eso lo da el mercado, no un input.

**C2 (acoplada a BOS, la ortodoxa ICT):** al violarse un lado, el otro reancla al origen de la pierna
que rompió (es la lectura "se actualiza con la estructura" de §2.3 y la Opción B literal del doc T07).
**Contrapartida:** con C2 el `strongHigh` D1 **no** se quedaría en 1.60554 (se re-anclaría al romperse
el low), y el usuario **quiere** 1.60554 ("el pivote histórico hasta donde llegan los OB y FVG").
→ **C1 es la que reproduce lo pedido; C2 se mide como control.**

## 4. El cascadeo ("¿eso se puede?") — sale GRATIS

Pregunta del usuario: que al romperse las 3 hacia abajo, el último pivote de discount ancle D1; luego,
según el precio recorra, ancle H1; y luego M5.

**Sale solo de C1, sin coordinación entre TFs.** Cada temporalidad ancla con sus propios pivotes y se
reancla solo al ser violada; como cada escala se viola con distinta frecuencia, el bloqueo es
**escalonado por construcción**: D1 queda clavado meses, H1 se re-ancla cada pocos días, M5 sigue
corriendo. No hay que calcular el cascadeo — **es la consecuencia**.

**La arquitectura ya lo soporta:** `f_computeTFState` ya calcula un estado independiente por TF vía
`request.security` (D1 y H1) + el nativo del chart ([:2970-2976](../../pine/SMC-Visual.pine)). Los tres
rangos **ya existen en estado**; hoy los tres caminan y solo se dibuja el del chart-TF.

### 4.1 Anidamiento D1 ⊇ H1 ⊇ M5 — PLAUSIBLE, NO GARANTIZADO → medir

Intuitivamente un bajo que sobrevive a escala D1 es más profundo que uno que sobrevive a escala H1.
Pero **no es una identidad matemática** (son pivotes de escalas distintas sobre series distintas).
**No se asume: se mide** (§7, P-C4). Si el anidamiento se rompe a veces, hay que decidir si se fuerza
(clamp) o se acepta.

## 5. "Del rango de D1 calcular premium/discount para H1 y M5" — YA EXISTE (§5.16)

Es una segunda cosa, distinta de C, y **ya está implementada y cableada**:
- `f_computeGradientLevels(top, bottom, includeEighths)` ([:1214](../../pine/SMC-Visual.pine)) divide un
  rango-fuente en `0 / 0.25 / 0.5 (=EQ) / 0.75 / 1` + eighths.
- Su política **P1** (§5.16, prioridad por defecto) usa **`trailing.top/bottom`** — el dealing range —
  en [:2344](../../pine/SMC-Visual.pine). Son los `UQ 1.18935` / `EQ 1.17038` / `7/8` / `5/8` visibles hoy
  en el chart.
- Doctrina §5.16: *"el `0.5` es idéntico al `eq` de §2.3; el grid es una extensión estricta del dealing
  range (no lo reemplaza)"*.

**Consecuencia: arreglado el ancla, la subdivisión sale sola.** Si el rango D1 pasa a `[0.95, 1.60554]`,
el grid gradúa automáticamente ese rango y los quadrants pasan a ser las referencias macro. **Cero
código nuevo.**

> **Ojo a la distinción** (importa para no mezclar conceptos):
> - **Opción C** → cada TF con su **propio** rango pegajoso = las líneas verdes del usuario.
> - **§5.16** → **subdividir** el rango de D1 en quadrants = niveles de referencia DENTRO de D1.
> Son **complementarias**, no alternativas. La #2 ya está hecha; solo la #1 falta.

## 6. Efecto sobre el veredicto P/D — honestidad sobre los números

| Ancla D1 | pct de 1.14380 | Zona |
|---|---|---|
| Implementado `[1.13246, 1.20831]` | 14.6% | Discount |
| `[1.01779, 1.20831]` (bajo vigente + alto vigente reciente) | **66.1%** | **Premium** |
| Lectura del usuario `[0.9536, 1.60554]` | **29.6%** | **Discount** |

**No se puede afirmar "el veredicto se invierte a premium": depende del par de anclas.** Con las
líneas del propio usuario el D1 sigue en **discount (29.6%)** — pero es un discount **con sentido**
(el precio está bajo dentro de un rango de 6500 pips), no el artefacto de una ventana de 758 pips. Y
coincide con su lectura de mercado ("cayó lo que más podía caer, ahora va hacia arriba").

*(Corrección: en el chat afirmé "el veredicto se invierte a premium" apoyándome en `[1.01779, 1.20831]`.
Con el par que el usuario efectivamente dibujó, no se invierte. El defecto real es la **escala**, no el
signo.)*

## 7. Predicciones (a escribir ANTES de medir) y qué mide el probe

Probe `scripts/gen_probe_rango_pegajoso.py` (a construir): sombrea C1 y C2 en paralelo al trailing
vigente, **sin tocar `pine/`**, truncado en `// === DIBUJO ===`, con `P_marker` de identidad.

| # | Predicción | Falsa si |
|---|---|---|
| **P-C1** | C1 en D1 converge a `[~0.95, ~1.60554]` (± un pivote de 50) = las líneas del usuario. | difiere > 1 pivote |
| **P-C2** | Amplitud C1: **D1 > H1 > M5** en la gran mayoría de barras (la jerarquía se endereza). | se invierte |
| **P-C3** | `legExtLo` con C1 baja de 1.13246 a ~0.95-1.02 → los 5 OB + 11 FVG + 1 BRK + 3 IFVG del censo S127 entran en banda 1-3. | siguen en banda 0 |
| **P-C4** | Anidamiento D1 ⊇ H1 ⊇ M5 se cumple **> 90%** de las barras. | < 90% |
| **P-C5** | C1 reancla **muy pocas veces** en D1 (≲ 5 veces en 6283 barras) y **muchas** en M5. | D1 reancla seguido |

**P-C3 es la que decide**, porque es la que ata la pendiente #1 con la #2: si el alcance no se
ensancha, C no resuelve el requisito del usuario y solo cambia el veredicto.

## 8. Costes y riesgos (esto NO es Visual-only)

1. **Toca el CORE.** `f_resetTrailingHigh/Low` + `f_updateTrailing` viven en el LIBRARY CORE
   ([:1166-1190](../../pine/SMC-Visual.pine)) y los consume `f_computeTFState` ([:1633](../../pine/SMC-Visual.pine))
   → **rompe el SHA `752b4083a7db419d`**, re-baseline ×3, core-sync ×3, y arrastra el contrato MQL5 de
   Fase 4 (ADR-002). **Requiere ADR** que sustituya la decisión T07/S021.
2. **Rompe la paridad con LuxAlgo** — la única referencia externa permitida. La Opción A ES el
   `trailingExtremes` de LuxAlgo. Conflicto de doctrina: CLAUDE.md dice que `docs/reglas-smc-ict.md` es
   la **fuente de verdad SMC**, y §2.3 dice "strong high/low **vigentes**" (= la lectura del usuario).
   **La doctrina gana sobre la paridad, pero es decisión del usuario y va en el ADR.**
3. **Invalida los casos de prueba de §2.3.** Los casos fechados (EURUSD H1 2026-06-11: 1.16859 /
   1.15928 / 1.14997) se validaron al 5.º decimal **contra LuxAlgo** = contra la Opción A. Con C
   **dejan de cuadrar y hay que rederivarlos**. Es un cambio de doctrina, no solo de código.
4. **Riesgo de rango "fósil".** Un ancla que lleva 18 años sin violarse (1.60554, de 2008) puede volver
   el P/D de D1 un filtro inerte. **Contra-argumento:** eso es precisamente lo que se le pide a D1 (el
   filtro macro), y §5.16 ya provee la graduación fina dentro de él. **Medir P-C5.**
5. **`i_pdSwingLen` deja de ser lo que era.** Hoy fija la ventana; con C fija solo la escala del pivote
   de reanclaje. Su default (50) se hereda sin recalibrar → anotar como deuda.

## 9. Orden propuesto

1. Probe de C1/C2 en sombra → medir P-C1..P-C5. **Sin tocar `pine/`.**
2. Si P-C3 sale verde → ADR (sustituye T07/S021; decide doctrina vs. paridad LuxAlgo) + rederivar los
   casos de §2.3.
3. Implementar en CORE + re-baseline SHA ×3 + core-sync ×3 + actualizar MQL5-PLAN.
4. Recién entonces revisitar #3 (IFVG) y #4 (MB/BPR), que hoy se miden sobre una geometría equivocada.
