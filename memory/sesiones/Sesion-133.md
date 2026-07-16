# Sesión 133 — ADR-021: el dealing range es el 2.º extremo estructural (IMPLEMENTADO, 1 defecto abierto)

> **Fecha:** 2026-07-15/16 · **Rama:** `pine/sistema-completo` · **17 commits** (`e13af86`…`d79fc74`)
> **`pine/` TOCADO** (primera vez en 6 sesiones). **CORE re-baselined ×2.** **F1-GATE sigue BLOQUEADA.**

---

## Resultado

**Se cierra el hilo P/D abierto desde S057 (9 sesiones).** El dealing range ya no se reancla en cualquier
pivote: se reancla **por ruptura de estructura**, y **al 2.º extremo**, no al último.

**Panel del indicador REAL (no probe), EURUSD:**

| | D1 | H1 | M5 |
|---|---|---|---|
| P/D | **Discount 34%** | **Premium 74%** | ⚠️ 21% o 90% (defecto abierto) |

**3 veredictos simultáneos = la cascada ROTA, con CERO parámetros nuevos.** D1 y H1 cuadran **exactos**
con el gate en sombra (0.3435→34%, 0.7328→74%).

- **El techo NO camina: 3 re-fijaciones en 6284 barras**, contra **41** del esqueleto de Fable ⇒ **muere
  el síntoma de S057**.
- **Su suelo de H1 clavado a 0.3 pips** (1.02105 nativo vs 1.02108 leído). **S132 midió 1100 pips de
  error** en ese mismo suelo. **Nada se calibró contra sus marcas.**
- **CORE 1866 → 1776 líneas** (¡**por debajo** del baseline!) · **−1 input** · aplica en vivo sin CE10117.

---

## El giro que reordenó 6 sesiones (lo dio el usuario)

> *"lo marco como referencia en dónde creo que quizás debiesen ir… como estamos en una divisa bajista
> estamos con este error pero también sé que pasará así con uno que sea alcista"*

**Sus niveles NO son el oráculo.** S128→S133 midieron hipótesis **contra sus líneas**, tomadas sobre **un
símbolo bajista** ⇒ sobreajuste a EURUSD-en-caída (viola ADR-001/ADR-002). **Lo señaló él antes que el
supervisor.** El oráculo es la **metodología**.

**Y el hallazgo doctrinal:** `strong`/`weak` depende del **BIAS**, no del lado. En bajista el low **es
weak** y **debe** caminar (es liquidez) ⇒ **la mitad del síntoma de S057 era la doctrina operando bien**.
El bug: **el lado STRONG también caminaba**. ⇒ **El fallo no era simétrico, y por eso las 8 palancas
simétricas fallaron** (escala ×4, toques, tolerancia, ancla, expansión, origen-de-pierna).

---

## Cronología

| # | Qué | Veredicto |
|---|---|---|
| 1 | **Probe del esqueleto de Fable** (relatch al origen de **la última** pierna) | ❌ **Refutado en 4 configuraciones** (escala {5,50} × lectura {L1,L2}): re-fija el techo en **cada** evento ⇒ **reproduce el defecto que venía a corregir** (9-13×ATR de error). Su ambigüedad L1/L2 se midió: **idénticas**. |
| 2 | **Auto-corrección** | Mi 1.er diagnóstico (*"la expansión anula el latch"*) lo **refutó mi propia 2.ª medición**: quitar la expansión no cambia **ni un dígito**. |
| 3 | **Doctrina §2.3.1/§2.3.2** (Fase 0) | Cuantifica `strong high/low` (era un **término primitivo**). Casos de prueba marcados **NO-ORÁCULO** (se generaron desde la propia Opción A). |
| 4 | **GATE Fase 1** (probe en sombra, 2 símbolos) | ✅ **PASA — 5 verdes de 6.** Ningún criterio de abandono. |
| 5 | **ADR-021 + implementación CORE** | Descongelada S021 por el usuario. |
| 6 | **CE10117: 100952 vs 100256** | Resuelto con **ADR-022**. |
| 7 | **Defecto M5 encontrado** | 🛑 **`pdWindow` NO era opcional.** |

---

## ADR-022 — el CE10117, y dos lecciones de tokens

1. **REFACTORIZAR NO AHORRA TOKENS.** El UDT `SMC_PdRange` (4 copias → 1) midió **CERO** (100952 antes y
   después). Predije 450-500. **5.ª predicción de tokens muerta de 5** — y la memoria **ya lo decía**
   (*"helper vs inline distan 14: lo caro es TOCAR el bloque, no la FORMA"*, S125) **y la ignoré**.
   **Solo RETIRAR código ahorra.** El refactor se conservó igual: no compra tokens, pero elimina 4 copias
   que había que mantener a mano.
2. **La causa se aísla por ABLACIÓN, no deduciendo:** `f_tfExtremes` = **139 líneas que el Visual carga y
   NUNCA llama**. Quitarlas → compila **y aplica**.

**Decisión:** `f_tfExtremes` sale del CORE a un bloque **`EXTREMES CORE`** byte-idéntico entre Strategy y
Context. **Regla nueva:** el CORE es lo que usan **TODOS**; lo que comparte un **subconjunto** va a su
propio bloque verificado. `check-core-sync.ps1` **extendido** + **guardrail: falla si el Visual vuelve a
contener `f_tfExtremes`**.

---

## 🛑 DEFECTO ABIERTO — bloquea F1-GATE

**`M5 Discount 21%` (chart en H1) vs `M5 Premium 90%` (chart en M5).** Mismo TF, 2 veredictos. El 90% es
el correcto (= probe del gate). **Causa:** `request.security("5", …)` desde un chart H1 recibe **mucha más
historia M5** que un chart M5 nativo (5253 barras) ⇒ más strong ⇒ **el 2.º extremo se va más lejos**.

⇒ **`pdWindow` DEFINE la escala.** Sin ella el rango depende de **cuánta historia sirva TV**, no de la
estructura ⇒ **no determinista** (regla dura #1). **4 versiones de §2.3.2 en una sesión, 3 mías y
erróneas.**

**NO refuta la regla:** D1/H1 exactos, el techo no camina, la cascada rota. **Es acotación, no diseño.**

---

## 2 errores propios atrapados ANTES de commitear (ambos habrían sido silenciosos)

1. Iba a usar `structTf` (escala **5**) para los strong. **El gate se midió con escala 50.** Con 5 el
   rango sale **LOCAL (319 pips) = el bug de S021 reencarnado**. Fix: `structPd`/`evStructMajor`.
2. En **Strategy** el bloque P/D quedó **ANTES** de `evStructMajor` ⇒ habría usado el evento de la barra
   **anterior**: el gotcha que el propio probe detectó y que yo iba a introducir. En Visual estaba bien.

## Y 1 que atrapó el USUARIO

Mandó una **captura de su NAS100** que no cuadraba con lo reportado. Tenía razón:
`data_get_study_values` **sigue el crosshair** y la lectura salió de una **barra intermedia**
(`close`=22688 con el chart en **29532**; `bias` +1 cuando era −1). **Antídoto: volcado por `label` en
`islast`.** Además destapó **un bug del probe**: `sLo`/`sHi` dentro de `if barstate.isconfirmed` ⇒ `na` en
la barra viva.

---

## Estado del código

- **LIBRARY CORE 1776 líneas** · SHA `752b4083a7db419d` → **`9559a0d7fe58b213`**
- **EXTREMES CORE 148 líneas** · SHA **`5f851d87e5fda720`** (Strategy + Context)
- `pine_check` **0/0 ×3** · `check-core-sync` **OK ×2 bloques** · **aplica en vivo**
- **`i_pdSwingLen` ELIMINADO** — se **fusionó con `i_majorLen`** (era redundante **y estaba
  descoordinado**: Visual/Strategy 1000, Context 50). **Neto −1 input, 0 nuevos.**
- `f_premiumDiscount` / `f_computeGradientLevels` **INTACTAS** ⇒ golden tests MQL5 vivos.
- **ADR-021** (ACEPTADA, defecto abierto) · **ADR-022** (ACEPTADA) · **SIN tag** (F1-GATE bloqueada).

## SIGUIENTE (S134)

1. **Calibrar `pdWindow` por TF.** Criterio: **ventana ≤ el mínimo de barras que sirve cualquier
   chart-TF**. **TENSIÓN MEDIDA:** ventana **corta** ⇒ **sin candidatos** (`pdLow`=na, gemelo de S131
   `minTouches`=2); **larga** ⇒ no determinista.
2. **Validación visual con el usuario: NADIE ha visto los 3 P/D dibujados** (el gate se pasó con un probe
   **truncado**, sin render).
3. **NO repetir** (11 hipótesis refutadas con medición): ancla (S128), cascada de mitades y mapeo nivel→TF
   (S130), toques y `poolTol` (S131), amplitud (S132), escala ×4, expansión, origen-de-**última**-pierna y
   3-ventanas-sobre-D1 (S133).
4. Pendientes de antes: fallback M2, IFVG por banda/lado, gate MB/BPR, `elig` excluye ZS_MITIGATED,
   `LEG_ANCH_TOL_ATR`, deudas S123, herencia MTF.

Ver [[Sesion-132]] · [[Sesion-131]] · [[Sesion-130]] · ADR-021 · ADR-022 ·
`docs/planes/GATE-fase1-segundo-extremo-S133.md`
