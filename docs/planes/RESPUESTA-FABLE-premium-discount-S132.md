# RESPUESTA FABLE — Premium/Discount: el esqueleto del ancla estructural (y quién tiene que descongelarla)

> **De:** Fable · **Para:** Freddy + Claude Code (supervisor)
> **Fecha:** 2026-07-15 · **Responde a:** `DOSSIER-FABLE-premium-discount-S132.md`
> **Verificado de primera mano:** `pine/SMC-Visual.pine:1635-1645`, `:1176-1198`, `:1200-1214`, `:433-477`;
> `pine/reference/LuxAlgo-SMC-base.pine:404-457`, `:707-733`; `docs/reglas-smc-ict.md` §2.3/§5.16/§6.3.5;
> `docs/decisiones-pd-rango.md` completo. No me creí ninguna línea del dossier sin leer la fuente.

---

## 1. Diagnóstico propio

**Confirmo el mecanismo de §5 del dossier, con una corrección de framing que cambia la gobernanza.**

Verificado: `:1641-1645` reancla `trailTf` con **cualquier** pivote de `f_detectSwings(pdLen)` (`:1635`),
y `f_resetTrailingHigh/Low` (`:1176-1186`) **sobrescribe** el extremo sin preguntar qué hizo ese pivote.
La estructura BOS/CHoCH ya vive dos líneas antes (`structTf`, `:1638-1640`, evaluada en `:1649`) y el
P/D no la consume. Todo cierto. El patrón existe en **4 call-sites**: `:1642/:1644` y `:1925/:1927`
(ambos EN el CORE) + `:2262/:2264` y `:2951/:2953` (consumidor).

**La corrección:** esto **no es un bug ni una desviación del código**. Es un **port fiel de LuxAlgo**.
Verificado en la referencia:

- LuxAlgo `getCurrentStructure(size)` (`:409-457`): al inicio de cada pierna nueva (`startOfNewLeg`),
  resetea `trailing.bottom`/`trailing.top` al pivote — **cualquier pivote de escala 50**, exactamente
  como nuestro `:1641-1645`.
- LuxAlgo "Strong High"/"Strong Low" (`:728`, `:733`): es **una etiqueta de texto** decidida por el bias
  (`swingTrend.bias == BEARISH ? 'Strong High' : 'Weak High'`). **El ancla nunca mira el bias.**
  LuxAlgo jamás calculó un rango anclado en strong high/low; solo lo rotula a posteriori.

Y por eso la contradicción real es **doctrina vs implementación**, y ya tiene nombre y expediente en el
proyecto: es la **Opción A vs Opción B** de `docs/decisiones-pd-rango.md` (S021). La prosa de §2.3 quedó
escrita en modo B ("rango entre el último strong high y strong low… se actualiza con la estructura");
la implementación y los casos de prueba del 5.º decimal se generaron en modo A. Desde entonces la
doctrina promete una cosa y el motor calcula otra, y cada vez que Freddy mira el chart con ojos ICT ve
la prosa y recibe LuxAlgo. Tres observaciones independientes del mismo síntoma (S057, S091, S132) —
y sus palabras de S091 **son la Opción B literal**:

> *"anclar el Discount al bajo más bajo del swing; que D1 quede lejos mientras el precio no rompa ese
> bajo, y así por temporalidad"* (S091, `decisiones-pd-rango.md`)

**Consecuencia de gobernanza (nadie la puede saltar):** mi esqueleto revierte una decisión que Freddy
tomó en S021 y reconfirmó 2 veces, congelada hasta Fase 3. **Solo Freddy puede descongelarla.** Lo que
sí cambió — y es la evidencia nueva que justifica reabrirla ahora y no en Fase 3:

1. **La razón #1 de S021 ("paridad con la referencia única") perdió su base:** LuxAlgo no computa lo
   que §2.3 promete; su "Strong" es cosmético. Mantener A no preserva una semántica de LuxAlgo — solo
   preserva su atajo.
2. **La variante barata de B ya se midió muerta** (S128, hipótesis #1: pivote `structMajor`, 3.2%,
   n=6283). La única B que queda en pie es la event-driven, que es otra mecánica (ver §4).
3. **El mandato de S132:** *"si tienes mejoras o ideas mejores para hacer este cálculo bien,
   implementémosla, pero que sea LA solución"*. Eso es una invitación explícita a reabrir, citada como
   exige la norma de §6 del dossier.

---

## 2. Revisión de la doctrina

**¿Qué es un strong high/low en la metodología?** Es **relacional, no local**: un strong low es el
mínimo cuya subida posterior **rompió estructura** (quedó "protegido/defendido"); un strong high, el
máximo cuya caída rompió estructura. No es una propiedad del pivote (amplitud, toques, simetría) sino
de **lo que la pierna nacida en él hizo después**. Esto, dicho de paso, explica de un plumazo por qué
murieron las hipótesis 6, 7 y 9 del dossier: buscaban "strong" como propiedad local del nivel, y esa
propiedad no existe.

**¿Cómo lo determina LuxAlgo?** No lo determina (verificado, §1): etiqueta los trailing extremes según
el bias. El rango de LuxAlgo es "último pivote high ↔ último pivote low, expandido por precio".

**¿Está bien cuantificada nuestra §2.3?** **No — tiene un hueco real.** "Strong high/low vigentes"
aparece como término primitivo sin definición cuantificada en todo el documento (verificado por
búsqueda). Además sus casos de prueba **no son un oráculo independiente**: se generaron desde la
Opción A ya implementada (`decisiones-pd-rango.md`, tabla de validación), así que "validan" la
implementación contra sí misma. La tabla de §2.3 dice "se actualiza con la estructura" y el código se
actualiza con pivotes: la fila es hoy falsa.

**Parche doctrinal propuesto (§2.3, antes de tocar código):**

- **Strong low** := el mínimo de la pierna cuya subida rompió por cierre el swing high estructural
  vigente (= en la barra de un BOS/CHoCH **alcista** de escala `swingLen`, el `min(low)` acumulado
  desde el evento alcista anterior). Se fija en la barra de la ruptura — todo dato pasado, anti-repaint
  [D-PINE-03] — y permanece vigente hasta el **siguiente evento alcista** (que lo sustituye por el
  origen de la nueva pierna).
- **Strong high** := simétrico, con eventos bajistas.
- **Lado weak** := el opuesto al último evento; es el **trailing extreme** (expansión vela a vela,
  `f_updateTrailing` intacto). Si el precio supera un lado, la expansión lo sigue ⇒ `pct∈[0,1]`
  garantizado por construcción, como hoy.
- Los casos de prueba fechados de §2.3 se **regeneran** tras la implementación (los actuales quedan
  como registro de la Opción A).

---

## 3. El esqueleto

**Idea en una frase: no se toca el clasificador ni la expansión; solo se cambia QUIÉN dispara el
reanclaje — de "cualquier pivote pdLen" a "el evento estructural que ya se calcula tres líneas más
abajo" — y el nivel al que se reancla — del pivote al origen de la pierna que rompió.**

| # | Componente | Qué hace | Dónde vive |
|---|---|---|---|
| C1 | **Tracker de origen de pierna** | 2 floats + 2 times por TF-state: `runMin` = `min(low)` desde el último evento alcista; `runMax` = `max(high)` desde el último evento bajista. Se actualizan cada barra confirmada. | **CORE** (junto a `SMC_Trailing` o campos nuevos en él) |
| C2 | **Relatch por evento** | En el bloque donde ya existe `ev = f_detectStructure(...)` (`:1649`): si `ev` alcista → `f_resetTrailingLow(runMin…)` y reset del tracker; si bajista → `f_resetTrailingHigh(runMax…)`. **Se eliminan** `:1641-1645` y la llamada `f_detectSwings(pdLen)` (`:1635`). | **CORE** ×2 (`f_computeTFState` y su gemela en `:1895+`) |
| C3 | **Expansión intacta** | `f_updateTrailing` no se toca. El lado weak trailea; `pct∈[0,1]` se conserva. | CORE (sin cambio) |
| C4 | **Espejo en consumidores** | Mismos 2 cambios en `:2262/:2264` (chart-TF, con dibujo) y `:2951/:2953` (M5 light). | Visual (fuera de CORE) |
| C5 | **Input retirado** | `i_pdSwingLen` queda sin uso ⇒ se elimina. **Neto: −1 input, 0 inputs nuevos.** Cuidado con el corrimiento de `in_N` (gotcha conocido). | Visual/Strategy/Context |
| C6 | **Docs** | Parche §2.3 (§2 de este doc) + §5.16 P1 (borrar "escala `pdSwingLen=50`") + **ADR-021** que supersede `decisiones-pd-rango.md` + desviación LuxAlgo documentada en header (precedente: la NB de `:1162-1165`). | docs/ |

**Lo que NO cambia:** `f_premiumDiscount` (pura, byte-idéntica — sus golden tests MQL5 de clasificación
sobreviven), gradient levels §5.16 (consumen `[bottom, top]` sin saber de dónde vino), la herencia
HTF/Context (capa macro, ADR-017/018), la interfaz `chartState.pdHigh/pdLow` hacia Strategy y el
contrato del tuple MTF (mismos escalares, misma posición).

**Efecto colateral a vigilar (no a diseñar todavía):** `f_computeLegExtremes` (`:3154`) parte de
`chartState.pdHigh/pdLow` ⇒ el alcance de bandas/zonas se moverá con el rango nuevo. Puede *mejorar* la
geometría del censo S127 (el suelo en el origen de la pierna ensancha la banda de abajo, la que estaba
vacía), pero se mide en el probe, no se promete.

**Orden de construcción:**

0. **Gate humano:** Freddy descongela (o no) la decisión S021 con este doc delante. Sin esto no hay paso 1.
1. Parche doctrinal §2.3 (solo docs).
2. **Probe en sombra** (patrón `gen_probe_*.py`): latch en paralelo, sin sustituir; predicciones de §7
   escritas antes. `pine/` no se toca.
3. Gate de medición contra los criterios de abandono de §7.
4. ADR-021 + decisión registrada.
5. Implementación CORE + **ablación de tokens medida** + `check-core-sync.ps1` ×3 + re-baseline SHA.
6. Regenerar casos fechados §2.3; retirar `i_pdSwingLen`; validación visual con Freddy.

---

## 4. Por qué ESTA solución (y no las otras)

**El principio unificador que dejaron 9 hipótesis muertas:** "strong" no es una propiedad local del
nivel — es lo que su pierna rompió después. Toda hipótesis que buscó la fuerza EN el nivel (toques #6,
tolerancia #7, amplitud #9) murió; toda la que buscó la escala EN un número (pdLen S130/S132, aritmética
#8, cascada #4, mapeo #5) murió. La única información que distingue 1.02182 de 1.13246 es que del
primero salió la ruptura y del segundo no — y esa información vive en `structTf`, ya calculada, gratis.

Contra la tabla §7 del dossier, una por una donde aplica:

- **#1 (Opción B vía `structMajor`, muerta S128):** aquella anclaba en los **niveles de pivote** de otra
  escala — pivot-driven, mecánica idéntica a A, por eso movió 3.2%. La mía es **event-driven con
  latch del origen**: el ancla solo cambia en BOS/CHoCH y se fija al extremo acumulado de la pierna, no
  al pivote. La evidencia nueva es doble: el propio 3.2% de S128 (demuestra que cambiar de pivote no es
  cambiar de mecánica) y el hallazgo LuxAlgo de §1 (la paridad que protegía a A es cosmética).
- **#3 (Opción C pegajosa, muerta S129):** esperaba la violación del **extremo del rango**, imposible con
  expansión conservada (`nReset=0`). La mía dispara con **eventos estructurales interiores al rango**,
  que demostradamente ocurren (el panel de hoy lista BOS 17-06, CHoCH 14-05, MSS 22-01 solo en D1). La
  frecuencia de relatch es medible y su cero es criterio de abandono (§7).
- **#4/#5/#8:** aritmética sin estructura; no las reintroduzco.
- **Alternativa "corregir la doctrina para que diga lo que hace el código":** legítima en abstracto
  (§9.2 del dossier la permite), rechazada aquí porque TODO lo demás está del mismo lado: la prosa de
  §2.3, su propia tabla ("se actualiza con la estructura"), §6.3.5 (prohíbe el rango superado por
  estructura), y la observación literal del usuario en 3 sesiones distintas. El código es el único
  elemento desalineado, y su única defensa era una paridad que resultó ser una etiqueta.

---

## 5. Qué resuelve exactamente — y qué NO

**Resuelve:**

- **Las dos objeciones literales de §2 del dossier, por el mismo mecanismo:** el discount deja de ser el
  pullback en formación (1.13246) y pasa al origen de la pierna; el premium deja de sobrescribirse con
  cada pivote nuevo (los 1.23697/1.39834/… ya no "pierden" contra 1.20831 — el vigente es el origen de
  la pierna bajista que rompió estructura).
- **Los 3 TF a la vez:** el cambio es en `f_computeTFState` (CORE compartido) ⇒ D1, H1 y M5 reciben cada
  uno su dealing range estructural nativo sin código por-TF.
- **La rotación (§8.2 del dossier):** cada TF ancla su propia pierna ⇒ veredictos distintos simultáneos
  son posibles por construcción. Se **mide** en el probe (P3), no se promete.
- **El rango fósil (§6.3.5):** el relatch por estructura es exactamente "se actualiza con cada nuevo
  strong high/low". Elimina la no-operabilidad del fix S130 (`pdLen=1000`).

**NO resuelve:**

- **La tensión macro (6503 pips) vs dealing range:** son objetos distintos (coincido con la hipótesis
  del supervisor en §8 del dossier). El contexto macro ya tiene su vía — Context/herencia (ADR-017/018).
  Este esqueleto no la toca ni la necesita.
- **La cascada anidada parametrizada de Freddy** (*"ayudarme a parametrizar dónde estará el discount de
  D1, el de H1 y el de M5, y que queden en un rango que sea operable"*, §8 del dossier): mi respuesta
  tentativa es que **la pierna nativa por TF ES esa cascada** (D1 ⊇ H1 ⊇ M5 la mayor parte del tiempo,
  y cada una ancla más cerca del precio). Pero si sus verdes anotados (1.10640/1.07408/1.01814) NO
  coinciden con orígenes de pierna de ninguna TF nativa, entonces su cascada es una **capa 3 con ADR
  propio** que este esqueleto no cubre. El probe lo decide (P5), no yo.
- **Nada de pools/EQ/OB/bandas:** cualquier mejora ahí es efecto colateral a medir, no objetivo.

---

## 6. Coste

| Partida | Coste |
|---|---|
| **CORE** | SÍ se toca (2 de los 4 call-sites + tracker). ⇒ SHA `752b4083a7db419d` roto, re-baseline ×3, `check-core-sync.ps1`, **ADR-021 obligatorio**. |
| **Decisión de usuario** | Revierte S021/S057/S091 (congelada a Fase 3). **Gate humano previo a todo.** |
| **Contrato MQL5** | La semántica de `SMC_Trailing` cambia ⇒ golden tests del rango se rederivan. **Es el momento más barato posible:** Fase 4 no ha escrito una línea. `f_premiumDiscount` (la función pura) queda intacta. |
| **Paridad LuxAlgo** | Desviación **deliberada y documentada** (precedente NB `:1162-1165`). La expansión (`f_updateTrailing`) se conserva = paridad parcial; la atribución CC BY-NC-SA no cambia. |
| **Casos §2.3 (5.º decimal)** | Se invalidan — eran hijos de la Opción A, no un oráculo. Se regeneran fechados tras implementar. |
| **Inputs** | **Neto −1** (`i_pdSwingLen` desaparece; cuidar corrimiento `in_N`). Cero inputs nuevos = cero superficie de calibración nueva. |
| **Tokens Pine** | Se retiran 1 llamada `f_detectSwings` + 4 resets; se añade tracker + relatch ×4. **Neto desconocido y NO se predice: se mide por ablación** (norma del proyecto, 4/4 predicciones muertas), con `pine_get_console` como fuente del número real. El diseño al menos *retira* código, cosa que ninguna propuesta previa hacía. |
| **Anti-repaint** | Sin riesgo nuevo: el latch usa `min/max` de barras pasadas fijado en la barra confirmada de la ruptura. Nada mira adelante. |

---

## 7. Cómo se MIDE antes de implementar (predicciones escritas AQUÍ, antes del probe)

**Arnés:** probe en sombra (patrón `gen_probe_*.py`) que computa el rango latcheado EN PARALELO al
actual (no sustituye) y emite ambos a tabla/plots. EURUSD D1/H1/M5, luego NAS100 (P6). Vigilar
`pine_get_console` (borde de tokens) y marcador de identidad de build (gotcha S127).

| # | Predicción falsable | Falla si… |
|---|---|---|
| P1 | En D1 hoy (bias bajista), el `strongHigh` latcheado cae a **≤1.0×ATR_D1 de 1.23697** (el rojo de Freddy). | Cae en otro sitio (p.ej. se queda en 1.20831 o salta a 1.60389). |
| P2 | En D1 hoy, el suelo es el trailing low de la pierna actual (~1.141) ⇒ **pct < 20% (discount profundo)** — y el veredicto ya no depende de ningún input de escala P/D (el input no existe). | pct sale equilibrium/premium, o reaparece 1.13246 como ancla. |
| P3 | **Rotación:** en el histórico H1+M5 (n≥5000 barras c/u), el % de barras con veredictos NO idénticos entre las 3 TF es **materialmente > 0** (con `pdLen=1000` era ≈0: "decir lo mismo en las 3 TF es no decir nada"). | Las 3 TF coinciden >95% del tiempo. |
| P4 | **Frecuencia de relatch** = frecuencia de BOS/CHoCH: **> 0 y ≪ nº de pivotes(50)**. | `nRelatch = 0` (degeneró en Opción C / min-max de ventana, hipótesis #3). |
| P5 | **Niveles del usuario:** de sus 7 niveles anotados (verdes 1.10640/1.07408/1.01814/0.95751/1.02182, rojos 1.23697/1.39834/1.49539/1.60180 — capturas de §3 del dossier), **al menos los extremos de pierna de D1 y H1 actuales coinciden con alguno a ≤1.0×ATR de su TF**. Los que no coincidan con NINGUNA TF quedan asignados a capa macro o capa 3 (dato, no fallo). | Ningún nivel suyo coincide con ningún latch de ninguna TF (>2×ATR todos) ⇒ mi definición de "origen" no es la suya. |
| P6 | **ADR-001 (NAS100):** el latch funciona simétrico sin tocar nada (strong low vigente en tendencia secular alcista, strong high en las caídas). | Hay que hardcodear un lado o un símbolo. |
| P7 | **Diferencia real vs Opción A:** el veredicto P/D cambia en **≥15% de las barras** (S128 mató la variante pivote con 3.2%; si esta no supera con claridad ese suelo, no compra nada). | Cambia en <5% de las barras. |

**Criterio de abandono de mi propia propuesta (global, pre-comprometido):** la abandono si
**P4 = 0**, o si **P7 < 5%**, o si **P1 y P2 fallan ambas**, o si **P6 exige asimetría**. Si falla solo
P5, la propuesta sobrevive como capa 2 pero la cascada del usuario exige la capa 3 con ADR propio —
y eso se le dice, no se le disimula.

**Anti-humo:** contar `nRelatch` por lado y por TF, y verificar que los latches históricos del probe
coinciden con los eventos del panel (BOS 17-06, CHoCH 14-05 en D1) — si el probe relatcha en fechas que
el panel no reconoce, el probe mide otra cosa (lección S128: contadores con guard `not na()` miden humo).

---

## Resumen en 5 líneas

1. La causa raíz de §5 es real y la verifiqué — pero **no es un bug: es la Opción A** (S021, reconfirmada
   ×2), un port fiel de LuxAlgo cuyo "Strong" resultó ser **una etiqueta, no un ancla**.
2. La doctrina §2.3 tiene el hueco: "strong high/low" sin cuantificar y casos de prueba generados desde
   la propia Opción A. Se parchea la doctrina ANTES que el código (§2).
3. Esqueleto: **relatch por evento estructural al origen de la pierna** (`runMin/runMax` + los eventos
   que ya existen en `:1649`), expansión intacta, `f_premiumDiscount` intacta, **−1 input**, 4 call-sites.
4. "Strong" es **relacional** (lo que la pierna rompió), no local — por eso murieron toques, amplitud y
   tolerancia, y por eso ni 50 ni 1000 podían arreglarlo.
5. Nada se implementa sin: (0) Freddy descongelando S021, (1) parche doctrinal, (2) probe en sombra
   contra las 7 predicciones de §7 con abandono pre-comprometido.
