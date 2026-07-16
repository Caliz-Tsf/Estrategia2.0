# ADR-021 — El dealing range es el **2.º extremo estructural** por temporalidad

- **Fecha:** 2026-07-15 (Sesion-133)
- **Estado:** **ACEPTADA — IMPLEMENTADA, con un DEFECTO ABIERTO que bloquea la firma** (ver abajo).
  Descongelada por el usuario en S133; gate pasado en sombra
  (`docs/planes/GATE-fase1-segundo-extremo-S133.md`) **antes** de tocar código.

> ## 🛑 DEFECTO ABIERTO (S133, medido EN VIVO tras implementar): `pdWindow` es OBLIGATORIA
>
> **El panel da `M5 Discount 21%` con el chart en H1 y `M5 Premium 90%` con el chart en M5.** Mismo TF,
> dos veredictos. (El 90% es el correcto: coincide con el probe del gate, `pct`=0.929.)
>
> **Causa:** `request.security("5", f_m5Light(...))` desde un chart H1 recibe **mucha más historia M5**
> que un chart M5 nativo (5253 barras) ⇒ más strong acumulados ⇒ **el 2.º extremo se va más lejos** ⇒
> el rango se ensancha.
>
> **Lo que esto refuta:** que `pdWindow` fuera **opcional** (§2.3.2, decidido en esta misma sesión). Sin
> ventana, el 2.º extremo depende de **cuánta historia sirva el bróker/TV**, no de la estructura ⇒
> **no es determinista** (regla dura #1) y el "M5" deja de ser M5. **La ventana no es el remedio del
> fósil secular: es lo que define la escala.**
>
> **Lo que NO refuta:** la regla en sí. D1 (34%) y H1 (74%) cuadran **exactos** con el gate en sombra, el
> techo no camina (3 re-fijaciones vs 41), y la cascada rota. **El defecto es de acotación, no de diseño.**
>
> **Pendiente:** calibrar `pdWindow` por TF y re-verificar que el veredicto de cada TF **no dependa del
> chart-TF**. Hasta entonces **no se firma F1-GATE**.
- **Supersede:** [`docs/decisiones-pd-rango.md`](../decisiones-pd-rango.md) (Opción A, S021, reconfirmada
  en S057 y S091). Aquel doc queda como **registro histórico**.
- **Precisa (no contradice):** regla dura #2 (CORE byte-idéntico — **se mantiene**), #1 (anti-repaint —
  **se mantiene**, ver Consecuencias), #4/ADR-001 (símbolo-agnóstico — **se refuerza**: esta regla lo
  cumple *por construcción*, sin ramas). ADR-002 (anti-overfitting): **el oráculo es la doctrina, no las
  marcas del usuario** (ver Contexto). ADR-018 (extremos HTF al CORE) intacta.
- **Cambia la doctrina:** [`reglas-smc-ict.md`](../reglas-smc-ict.md) §2.3.1 y §2.3.2 (nuevas).

---

## Contexto

**El síntoma, abierto desde S057:** el rango P/D *"camina hacia el precio"* en tendencia bajista — el
discount de D1 queda pegado al precio y el premium se sobrescribe con cada pivote nuevo. El usuario lo
reportó **tres veces** (S057, S091, S132).

**Ocho sesiones, ocho palancas, ocho refutaciones medidas:** ancla (S128, 3.2%), escala ×4 (S130 `pdLen`,
S132 amplitud, S133 escalas de evento ×2), toques (S131), tolerancia (S131), expansión (S133),
origen-de-la-última-pierna (S133, 4 configuraciones).

**Por qué fallaron todas — dos causas, ambas halladas en S133:**

1. **El fallo NO es simétrico, y las ocho palancas trataban los dos lados igual.** En SMC/ICT
   `strong`/`weak` depende del **bias**, no del lado. En bajista el low es **weak** = liquidez, y un weak
   low **debe** caminar. **La mitad del síntoma era la doctrina operando bien.** El bug real: hoy
   `f_resetTrailingHigh/Low` (`:1176-1186`) reancla **ambos** lados con **cualquier** pivote (`:1641-1645`)
   **sin mirar el bias** — también el strong, que por doctrina debe permanecer hasta ser superado.
2. **Se medía contra las marcas del usuario, no contra la doctrina.** Él aclaró en S133 que sus niveles
   anotados son *"referencia en dónde creo que quizás debiesen ir"*, tomados sobre **un símbolo bajista**.
   Ajustar a ellos era sobreajustar a EURUSD-en-caída — **viola ADR-001 y ADR-002**, y lo señaló él antes
   que el supervisor.

**El hueco de fondo, verificado:** §2.3 usaba **"strong high/low" sin definir** — término primitivo del que
colgaba todo el motor P/D. Y sus casos de prueba al 5.º decimal **se generaron desde la Opción A ya
implementada** ⇒ **validaban el código contra sí mismo**. (Hallazgo de Fable, confirmado leyendo la fuente.)

**Y la razón #1 de S021 se cayó.** Aquel doc eligió A por *"paridad con la única referencia externa
permitida"*. **Verificado en la referencia:** el `"Strong High"/"Strong Low"` de LuxAlgo es **una etiqueta
de texto** decidida por el bias **después** de calcular el rango
(`pine/reference/LuxAlgo-SMC-base.pine:728`, `:733`); **su ancla nunca mira el bias** (`:409-457`).
**LuxAlgo jamás calculó un rango anclado en strong high/low.** Mantener A no preservaba una semántica —
preservaba **su atajo**. Las razones #2 (portabilidad MQL5) y #3 (determinismo) siguen en pie y **esta
decisión las respeta** (estado plano de 6 floats; `f_premiumDiscount` intacta).

---

## Decisión

**El dealing range de cada TF es `[2.º strong low, 2.º strong high]` de la escala de ese TF.**
Doctrina completa en `reglas-smc-ict.md` §2.3.1/§2.3.2. En resumen:

1. **`strong` es RELACIONAL** — no una propiedad local del nivel (ni toques, ni amplitud, ni antigüedad:
   las tres refutadas con medición en S131/S132). **Strong low** := el mínimo de la pierna cuya subida
   **rompió estructura** (BOS/CHoCH). Se fija en la barra de la ruptura, con `min/max` de barras pasadas.
2. **El 1.er extremo (`histLow`/`histHigh`) se marca aparte y NO entra en el rango.** Es el arranque del
   feed o un evento único de hace décadas: cierto, pero **no operable**.
3. **El 2.º extremo ES el rango.** Da un rango *"no tan lejos"* (palabras del usuario) y sigue siendo
   **estructural**, no aritmético.
4. **Fallback en cascada** (garantiza `pct∈[0,1]`, requisito literal del usuario *"el precio siempre está
   por dentro"*): `close >= pdLow` → `pdLow` · `histLow <= close < pdLow` → `histLow` (el rango se estira)
   · `close < histLow` → trailing (expande hasta que se confirme el pivote nuevo). Simétrico arriba.
5. **`pdWindow` es OPCIONAL y por-TF** — solo para el fósil en símbolos seculares (ver Consecuencias).
   **La regla base no la necesita.**

**Se elimina:** el reanclaje por pivote (`:1641-1645`), la llamada `f_detectSwings(pdLen)` (`:1635`) y el
input `i_pdSwingLen`. **Neto: −1 input, 0 nuevos.**

**Implementación — O(1), sin arrays:** mantener el 1.º y el 2.º extremo **no requiere ordenar** (la
exploración confirmó que no existe ordenación por nivel en el código: todo el sorting es por distancia).
Bastan **6 floats por TF** (`runMin, runMax, min1, min2, max1, max2`) y una comparación por evento. Sin
`array.sort`, sin `array.push` (evita el RE10045 conocido).

---

## Evidencia (medida en sombra ANTES de implementar — `pine/` intacto)

**La cascada, EURUSD, 3 TF nativas, cero parámetros** (probe marker 1351):

| TF | rango | `pct` | veredicto |
|---|---|---|---|
| **D1** | [0.95360, 1.51441] | 0.344 | **DISCOUNT** |
| **H1** | [1.02105, 1.19188] | 0.733 | **PREMIUM** |
| **M5** | [1.13335, 1.14730] | 0.929 | **PREMIUM extremo** |

**ANIDA** (D1 ⊃ H1 ⊃ M5, verificado) y **ROTA** (3 veredictos simultáneos distintos) — el requisito
literal del usuario, **sin código por-TF ni un solo input nuevo**.

| Predicción (escrita antes) | Resultado |
|---|---|
| El techo **no camina** | ✅ **3** re-fijaciones en 6284 barras, contra **41** del esqueleto de Fable ⇒ **muere el síntoma de S057** |
| `pct∈[0,1]` siempre | ✅ **0** fuera de rango, en ambos símbolos — y **no trivial**: el fallback se ejerció en 773 (EURUSD) y 4432 (NAS100) barras |
| `pdLow` EURUSD = 0.95360 | ✅ **exacto** |
| **ADR-001** multi-símbolo | ✅ mismo código, **0 ramas**; el bias sale solo y el strong se congela en el lado que dicta |
| Desacuerdo vs A ≥15% | ❌ **5.8% (D1) / 12.3% (H1)** — ver Consecuencias |

**Sanity check contra las lecturas del usuario (NO oráculo — ADR-002):** su suelo de **H1 = 1.02108** vs el
2.º strong low nativo de H1 = **1.02105** ⇒ **0.3 pips**. **S132 midió "1100 pips de error"** en ese mismo
suelo con la Opción A. **Nada se calibró contra sus marcas.**

**El fallback verificado en vivo por el usuario** (captura de NAS100 D1): `close`=29532 rompió
`histHigh`=26288 ⇒ **el rango pasó a `[1021.1, 30773.2]`** — el techo subió al nuevo alto más alto, con el
precio dentro. Es su frase, ejecutándose.

---

## Alternativas descartadas (todas con medición, no por opinión)

| Alternativa | Por qué cae |
|---|---|
| **Mantener Opción A** | Su razón #1 (paridad LuxAlgo) resultó **cosmética** (ver Contexto). Y no arregla el síntoma de S057. |
| **Opción B** (S021/S128) | **Medida muerta en S128**: mueve el veredicto solo **3.2%** (n=6283) — ancla en pivotes de otra escala: **misma mecánica que A**. |
| **Opción C** pegajosa (S129) | Con la expansión conservada, `close > top` es **imposible** ⇒ la violación nunca dispara ⇒ degeneró en **min/max de ventana** (`nReset`=0). |
| **Esqueleto de Fable** — relatch al origen de **la última** pierna (S133) | **Refutado en 4 configuraciones** (escala {5,50} × lectura {L1,L2}): re-fija el techo en **cada** evento ⇒ **reproduce el "camina hacia el precio"** que venía a corregir (9-13×ATR de error). Su principio (*"strong es relacional"*) **sobrevive y se usa aquí**; lo que cae es operacionalizarlo como *"la última pierna"*. |
| **3 ventanas sobre D1** (S133) | Anida y rota, pero cuesta **3 inputs** y el mapeo ventana→TF sería **una definición nuestra, no un hecho** — el error que S130 ya cometió con el mapeo nivel→TF (resultó **casualidad**). Y **reintroduce el fallo de S131**: ventana corta ⇒ 1 solo strong dentro ⇒ **sin candidatos** (`pdLow`=`na`). |
| **Toques / amplitud / tolerancia** | S131 y S132: buscaban la fuerza **EN** el nivel. **Strong es relacional** — esa propiedad no existe ahí. |

---

## Consecuencias

**Coste asumido:**

- **CORE roto** ⇒ SHA `752b4083a7db419d` re-baselined · `check-core-sync.ps1` ×3 · tuple de
  `f_computeTFState` **89 → 91** escalares (emite `histLow`/`histHigh`) ⇒ ajustar los desempaquetados de
  `:2980-2999`.
- **Contrato MQL5:** la semántica de `SMC_Trailing` cambia ⇒ los golden tests **del rango** se rederivan.
  **Es el momento más barato posible: Fase 4 no ha escrito una línea.** `f_premiumDiscount` (`:1208`)
  queda **intacta** ⇒ **sus golden tests sobreviven**.
- **Paridad LuxAlgo:** desviación **deliberada y documentada** (precedente: la NB de `:1162-1165`). La
  expansión (`f_updateTrailing`) se conserva ⇒ paridad parcial. La atribución CC BY-NC-SA no cambia.
- **Casos de prueba de §2.3:** se invalidan (eran hijos de la Opción A, no un oráculo) ⇒ **se regeneran**
  fechados tras implementar. Ya marcados como no-oráculo en la doctrina.
- **`f_computeLegExtremes` (`:3154`)** parte de `chartState.pdHigh/pdLow` ⇒ el alcance de bandas/zonas se
  moverá. Puede **mejorar** la geometría del censo S127 (banda de abajo vacía) — **se mide, no se promete**.

**Anti-repaint [D-PINE-03]: sin riesgo nuevo.** El latch usa `min/max` de barras pasadas, fijado en la
barra **confirmada** de la ruptura. Nada mira adelante.

**Tokens:** se retiran 1 `f_detectSwings`, 4 resets y 1 input; se añade el tracker. **Neto desconocido y
NO se predice: se mide por ablación** con `pine_get_console` (norma del proyecto — 4/4 predicciones de
tokens muertas). El diseño al menos **retira** código, cosa que ninguna propuesta previa hacía.

**Límite conocido y aceptado — el fósil secular.** En un símbolo de tendencia secular fuerte, el 2.º
extremo del lado que el precio **nunca vuelve a visitar** se ancla en el arranque del feed: NAS100 D1 da
`pdLow`=1021.1 (de 2001) ⇒ **premium 95.8% permanente**. **H1 no lo sufre** (feed de 1.5 años):
`[19013, 30722]`, y rota (12.3% de desacuerdo). **Decisión: se acepta.** El usuario ya estableció que
**D1 es contexto, no señal**, y un D1 que dice "premium extremo" en máximos de 24 años **está diciendo la
verdad**. `pdWindow` queda disponible como remedio **opcional y por-TF** si algún día molesta —
**nunca menor que la ventana que contiene ≥2 strong del lado**.

**Sobre el desacuerdo de solo 5.8% en D1 (predicción fallida):** el rango nuevo **comparte suelo** con la
Opción A vigente y solo cambia el techo ⇒ los veredictos coinciden casi siempre. **La métrica era la
equivocada:** el % de desacuerdo era el listón correcto para la Opción B (misma mecánica que A); aquí lo
que se compra es **la estabilidad del strong**, que ese % no mide. En H1 sube a **12.3%**.

**Nota histórica:** `i_pdSwingLen`=1000 (S130) acertaba el rango D1 de EURUSD **actuando como ventana de
facto, sin saberlo** — no era una escala de pivote. Ver `decisiones-pd-rango.md` nota S133(b), que además
corrige el veredicto erróneo de S132 sobre ese fix.
