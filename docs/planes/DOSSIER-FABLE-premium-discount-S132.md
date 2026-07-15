# DOSSIER FABLE — El Premium/Discount no cuadra: 5 sesiones, 6 hipótesis muertas, y una línea de código

> **Para:** Fable · **De:** Claude Code (supervisor) + Freddy (usuario/trader)
> **Fecha:** 2026-07-15 (Sesión 132) · **Estado del proyecto:** Fase 1, F1-GATE **BLOQUEADA**
> **Entregable pedido:** ver §9. **Solo el ESQUELETO de la solución.** No código.

---

## 0. Cómo leer esto (y qué NO hacer)

Este dossier es **autocontenido a propósito**: no necesitas historial de sesiones. Pero necesitas
**verificar por tu cuenta**, no confiar en él. Razón dura: **este proyecto acaba de perder una sesión
entera midiendo una premisa que un documento anterior se inventó y atribuyó al usuario** (§6). Si algo
aquí no lo puedes trazar a una línea de código, a una regla citada de la doctrina, o a un número
medido, **trátalo como sospechoso**.

**Lo que se te pide es un esqueleto de solución, no una implementación.** Y con justificación: *por
qué esa solución, qué resuelve exactamente, qué NO resuelve, y qué cuesta.*

---

## 1. Qué es el sistema (mínimo indispensable)

Bot de trading **SMC/ICT** para Forex. Primero un sistema completo y validado en **TradingView
(Pine Script v6)**; después un EA en MQL5 que lo replica. Arquitectura: **1 core de detección + 2
consumidores** (+1 auxiliar):

- `pine/SMC-Visual.pine` — `indicator`, dibuja + panel.
- `pine/SMC-Strategy.pine` — `strategy`, scoring + entradas.
- `pine/SMC-Context.pine` — `indicator` auxiliar (ADR-017), hereda extremos HTF.
- La sección `// === LIBRARY CORE ===` (L154–~L2019 de Visual) es **byte-idéntica en los 3**.
  SHA actual: **`752b4083a7db419d`** (1866 líneas). Tocarla ⇒ re-baseline ×3 + contrato MQL5 + **ADR**.

**Fuentes de verdad** (léelas, no me creas):
- **Doctrina SMC:** `docs/reglas-smc-ict.md` — definiciones cuantificadas. **§2.3** es el corazón de
  este dossier. También **§6.3.5** y **§5.16**.
- Plan: `WORKPLAN-MAESTRO-V2.md`, `docs/workplan/PINE-PLAN.md`.
- Reglas duras: `CLAUDE.md`.
- Referencia externa **única permitida**: `pine/reference/LuxAlgo-SMC-base.pine` (CC BY-NC-SA).
  **Prohibido** referenciar cualquier otro proyecto/EA previo.

---

## 2. El síntoma, en palabras del usuario (cita literal, sin interpretar)

> *"cuestionamiento de dónde están marcándose en este minuto en el indicador los premium y discount de
> cada temporalidad y no dan, todo lo que he dicho es observación"*

Y al ver el resultado del ajuste que probamos hoy:

> *"pero es que dime algo, ¿cómo eso va a estar bien si arriba del premium hay otros altos más altos
> los cuales provienen de la caída? y ¿cómo va a ser ese el discount si el precio viene de dos swings
> alcistas al rebotar? […] se supone que el premium y discount se marcan de pivotes consumidos, o sea
> si el precio cayó hasta 0.95… y sabiendo que hay otros bajos más bajos abajo, ¿por qué 1.132… sería
> el discount? […] el discount debiese ser el bajo antes del swing, y aquí está en el bajo que se está
> creando junto a la caída, no en el swing posterior al iniciar el swing"*

**Traducción operativa:** el ancla del rango debería ser **el origen de la pierna** (el mínimo desde
el que el precio se fue y rompió estructura), no un mínimo de pullback que se está formando *dentro*
del movimiento actual.

---

## 3. La evidencia visual

En el repo (capturadas hoy, EURUSD OANDA, `i_pdSwingLen`=1000, todo apagado salvo P/D + panel):

| Archivo | Qué muestra |
|---|---|
| `docs/planes/evidencia-S132/S132-D1-pd-motor.png` | Chart D1. El motor etiqueta `Premium 1.60389` · `EQ 1.27874` · `Discount 0.95360`. |
| `docs/planes/evidencia-S132/S132-H1-pd-motor.png` | Chart H1. El motor etiqueta `Premium 1.18492` · `EQ 1.15869` · `Discount 1.13246`, y al fondo `D1: Discount 0.95360` heredado. |

**Freddy te entregará además sus propias capturas anotadas** (líneas verdes y rojas dibujadas a mano
por él). En ellas verás: verdes en **1.10640 / 1.07408 / 1.01814** (y en otra, **0.95751 / 1.02182**),
rojas en **1.23697 / 1.39834 / 1.49539 / 1.60180**. Son los pivotes que él considera estructurales y
que el motor ignora o sobrescribe. **Pídeselas si no las tienes: son parte del planteamiento.**

---

## 4. Lo que dice la DOCTRINA (`docs/reglas-smc-ict.md`) — citas literales

**§2.3 Premium / Discount / Equilibrium** (`f_premiumDiscount`):

> *"El **dealing range** (rango de negociación entre el último **strong high** y **strong low**)
> dividido en zonas de valor."*
> *"Sea el rango `[L, H]` entre el **strong low** `L` y **strong high** `H` vigentes (los swings que
> delimitan el rango operativo actual)"*

Y su tabla de parámetros:

> `| rango | strong high / strong low vigentes | **se actualiza con la estructura**. |`

**§6.3.5:**

> *"EL relevante = el rango **dominante** activo (`majorLen`). **Descarta** (citable): medir P/D sobre
> **un rango ya superado por estructura** (el rango se actualiza con cada nuevo strong high/low)."*

**§5.16 (P1):**

> *"P1 — Dealing range Premium/Discount (§2.3, `f_premiumDiscount`). Rango-fuente por defecto siempre
> que haya un dealing range vigente (strong high ↔ strong low, escala **`pdSwingLen=50`**)."*

**§2.3 (MTF)** y **§5.16 (grids anidados)** — esto importa para el punto 3 de §7:

> *"**MTF.** Transferible como **bandas del HTF heredadas** a M5 (el dealing range D1/H1 colorea el
> fondo de M5); el `eq` HTF es un nivel ancla por `bar_time` del rango."*
> *"los gradient levels de un rango-fuente HTF son **globales** (mismos en todo TF), **no se recomputan
> por TF**"*

---

## 5. LA CAUSA RAÍZ (hallazgo de S132 — verifícala tú mismo)

`pine/SMC-Visual.pine:1641-1645`, dentro de `f_computeTFState` (**está en el LIBRARY CORE**):

```pine
if barstate.isconfirmed and not na(pdH)
    f_resetTrailingHigh(trailTf, pdH, bar_index - pdLen, time[pdLen])
if barstate.isconfirmed and not na(pdL)
    f_resetTrailingLow(trailTf, pdL, bar_index - pdLen, time[pdLen])
f_updateTrailing(trailTf, high, low, time)
```

Donde `[pdH, pdL] = f_detectSwings(pdLen)` (:1635) = **pivote simétrico estricto**: `high[len]` mayor
que las `len` velas a cada lado. Y `f_resetTrailingHigh/Low` (:1176-1186) **sobrescribe** el extremo.

### El hueco, en una frase

> **El código ancla el rango en CUALQUIER pivote confirmado de escala `pdLen`.
> La doctrina §2.3 exige anclarlo en el STRONG high/low.
> Ningún valor de `pdLen` convierte un pivote débil en fuerte.**

Un **strong low** (doctrina) es el mínimo cuyo rally **rompió estructura** — está protegido/defendido.
Un mínimo de pullback que no originó nada es **débil**. El código no distingue: reancla en los dos.

**Esto explica las dos objeciones del usuario a la vez:**
- El techo 1.20831 no "ganó" a 1.23697/1.39834/1.49539/1.60180: los **sobrescribió** al reanclar.
- El suelo 1.13246 es un mínimo **débil** creado dentro de la caída actual; el origen de la pierna
  (su 1.02182) fue sobrescrito.

**Ironía cruel:** el material ya existe. Dos líneas ANTES, en `:1638-1640`, el mismo bucle llama a
`f_setStructureHigh/Low` — la estructura BOS/CHoCH **ya está detectada y viva en `structTf`**. El P/D
simplemente **no la usa**: corre un detector de pivotes en paralelo e ignora la estructura.

---

## 6. AVISO CRÍTICO DE MÉTODO — lee esto antes de proponer nada

Este proyecto ha fallado **tres veces seguidas por la misma causa: no volver a la observación literal
del usuario.**

1. **S129** — el diseño de S128 era ambiguo en un punto (§3); los probes midieron la lectura
   equivocada. Sesión perdida.
2. **S130** — se discutió durante 3 sesiones cambiar el ancla (romper el SHA, rederivar §2.3). La
   causa era un input mal puesto. Lección escrita: *"preguntar QUÉ MIRA el usuario, y barrer los
   inputs ANTES de proponer arquitectura"*.
3. **S132 (hoy)** — el doc `DISENO-regla-de-pools-S131.md` §3bis.4 **afirmó** que el usuario
   "descartaba" 6 niveles por ser *"swings pequeños"*. **El usuario nunca dijo eso.** Preguntado:
   *"yo no descarto nada, todo lo que he dicho es observación"*. Se midió la amplitud de swing en 5
   escalas contra ese contraste ficticio. Y al enseñar sus dibujos resultó ser **exactamente al
   revés**: sus marcas (1.10640 / 1.07408 / 1.01814) **SON** esos pools (1.10654 / 1.0733 / 1.01779,
   a 1.4–7.8 pips) y él sostiene que **deberían ser los discount de las TF menores**.

> **Norma nueva del proyecto: ninguna medición ni diseño arranca sin citar la frase literal del
> usuario que lo motiva.** Si tu esqueleto se apoya en "el usuario quiere X", cita dónde lo dijo.

---

## 7. Las hipótesis YA REFUTADAS con medición — no las re-propongas

Si tu esqueleto reintroduce alguna de estas, será rechazado. Cada una costó ≥1 sesión.

| # | Hipótesis | Cómo murió | Sesión |
|---|---|---|---|
| 1 | Opción B: ancla estructural (`structMajor`) | Mueve el veredicto solo **3.2%** (n=6283) y **no puede** ensanchar el alcance (`structMajor.lowLevel < pdLow` en **0 de 6283**). | S128 |
| 2 | "Bandas 4/5 incapaces por construcción" | **Falsa**: están dormidas, no muertas (10.8% de los casos). | S128 |
| 3 | Opción C: rango pegajoso hasta violación | Con la expansión conservada, `close > top` es **imposible** ⇒ la violación **nunca** se dispara ⇒ C literal **= el máx/mín de la ventana**. `nHiReset=nLoReset=0` en 6283 barras. | S129 |
| 4 | Cascada de mitades (cada nivel = mitad del anterior) | Medida **rota**: flapping monótono (L5 salta cada ~4 velas). | S130 |
| 5 | Mapeo nivel→TF (H1 = fracción constante de D1) | **Refutada con 5 símbolos**: ratio 0.164…0.485, recorrido 0.321. El acierto previo fue **casualidad**. | S130 |
| 6 | Fuerza por toques (`i_minTouches`) | **37 de 38** pools vivos tienen 1 toque. Los toques miden **congestión**; los extremos son lo contrario (un máximo histórico no puede tener 2 toques). | S131 |
| 7 | Barrer `i_poolTol` (0.1 / 0.3 / 0.5=maxval) | **Satura** en 0.3. Los niveles del usuario siguen a 1 toque en todo el barrido. | S131 |
| 8 | Reglas aritméticas (escala ×4, ventana `close±X`, escala por ATR) | Las tres descartadas contra sus números. Un escalado simétrico **conserva el pct** ⇒ nunca compra rotación. | S131 |
| 9 | **Amplitud del swing como propiedad del pool** | **Refutada en 5 escalas.** Ver tabla abajo. | **S132** |

**Detalle de (9)** — barrido de sensibilidad de tramo L, contraste entre los niveles del usuario (A) y
los otros (B) — *nota: el contraste A/B resultó ser ficticio (§6), pero la refutación de la amplitud
como propiedad discriminante es válida en sí misma*:

| L | `min(amp_A)` | `max(amp_B)` | margen | `max(amp)` global |
|---|---|---|---|---|
| 5 | 3.06 | 4.80 | −1.74 | 6.07 |
| 10 | 2.70 | 6.21 | −3.51 | 9.10 |
| 20 | 4.08 | 7.55 | −3.48 | 13.48 |
| 50 | 3.30 | 22.46 | −19.16 | 25.78 |
| 100 | 10.47 | 15.54 | −5.06 | 42.61 |

Ninguna escala separa. Anti-humo limpio (`nHitA`=5 en las 5, `nAmpCeroPiv`=1, `nPiv`
740/409/204/86/38). Arneses: `scripts/gen_probe_amplitud_swing.py`, `scripts/gen_probe_amplitud_escala.py`.

---

## 8. Lo MEDIDO hoy sobre el parámetro (cero código, `indicator_set_inputs`)

`i_pdSwingLen` **no es un lookback**: es la **sensibilidad del pivote** (va a `f_detectSwings(pdLen)`).
El repo lo tiene hoy en **1000** (commit `61dcc36`, S130). La doctrina §5.16 dice **50**.

| TF | `pdLen`=1000 (repo hoy) | `pdLen`=50 (doctrina §5.16) |
|---|---|---|
| D1 | Discount 30% · `[0.95360, 1.60389]` = 6503 pips | **Discount 18%** · `[1.13246, 1.20831]` = 758 pips |
| H1 | Discount 27% · `[1.13246, 1.18492]` = 525 pips | **Premium 82%** ← **se invierte** |
| M5 | Premium 88% | **Premium 76%** |

**Tres lecturas de esto, y las tres importan:**

1. **El fix de S130 (50→1000) es doctrinalmente incorrecto.** Con 1000, "un swing necesita 1000 barras
   a cada lado" ⇒ casi ningún pivote califica ⇒ el reanclaje **casi nunca se dispara** ⇒ solo actúa
   `f_updateTrailing` (que solo expande) ⇒ el rango tiende a los extremos casi globales. Cuadró con el
   ojo del usuario en D1 **porque el bug estaba apagado**, no porque el ancla fuera estructural. Y es
   justo el "rango ya superado por estructura" que §6.3.5 manda **descartar**.
2. **Con la escala doctrinal (50) aparece la ROTACIÓN:** D1 Discount 18% **y** H1 Premium 82%
   *simultáneamente* = barato en el rango grande, caro en el pequeño. Con 1000 era imposible (30% vs
   27%: **decir lo mismo en las 3 TF es no decir nada**). Esto es lo que S130 perseguía con la
   "cascada de mitades" (que midió rota) y **sale solo** con la escala correcta.
3. **Pero 50 produce exactamente la queja del usuario** (§2): reancla en pivotes débiles ⇒ el discount
   cae en 1.13246 en vez del origen de la pierna (1.02182). **Ni 50 ni 1000. El parámetro es la
   palanca equivocada.**

### La tensión que hay que resolver conceptualmente (no con un número)

El usuario lee D1 como **6503 pips**; el dealing range doctrinal de D1 es **758 pips**. **Hipótesis
del supervisor (NO confirmada, cuestiónala):** son **dos objetos distintos** — su 6503 no es el
*dealing range*, es el **contexto macro**; el dealing range es la estructura dominante vigente, que
se actualiza y por eso es operable. Precedente del mismo patrón: en S130 se concluyó que su lectura de
H1 (3780 pips) y el H1 nativo (1905) eran objetos distintos, porque su techo H1 (1.39972) es de 2014
≈ 75.000 barras H1 y **TradingView solo entrega 9.535** ⇒ no es obtenible nativamente en H1 ⇒ tiene
que heredarse de D1.

**Arquitectura tentativa del supervisor (3 capas) — es una PROPUESTA, tu esqueleto puede tumbarla:**
1. **Contexto macro** (el 6503 del usuario) → consumidor Context (ADR-017) + herencia §5.16/ADR-018.
2. **Dealing range operable por TF** → doctrinal §2.3, anclado en **strong** high/low, rotando.
3. **Cascada de pivotes anidados del usuario** (D1 ⊇ H1 ⊇ M5, cada TF anclando en un pivote más
   cercano al precio) → **extiende** §2.3 MTF ⇒ requiere ADR propio.

⚠️ Ojo con (3): el usuario **matizó** que no es literalmente "el siguiente pivote":

> *"no necesariamente tiene que ser el siguiente pivote, porque por ejemplo en el caso del premium el
> siguiente pivote desde el premium de D1 hacia abajo sería uno de temporalidad súper lejana y quizás
> el precio nunca vuelva a llegar ahí; en el mismo caso de los mercados alcistas quizás nunca vuelvan
> a su bajo más bajo. Entonces aquí es donde tú me tienes que ayudar a parametrizar dónde estará el
> discount de D1 bien, el de H1 y el de M5, y que queden en un rango que sea **operable**"*

Es decir: **la operabilidad es requisito, no adorno**. Y §6.3.5 ya lo respalda por doctrina (prohíbe
el rango fósil). Su frase de cierre:

> *"lo que siempre he dicho es lo que veo y me causa ruido; si tienes mejoras o ideas mejores para
> hacer este cálculo bien, implementémosla, pero que sea LA solución"*

---

## 9. QUÉ SE TE PIDE (entregable)

**Solo el ESQUELETO de la solución.** No escribas Pine. No implementes. Estructura pedida:

1. **Diagnóstico propio.** ¿Confirmas la causa raíz de §5 (ancla en pivote cualquiera vs strong
   high/low de §2.3)? Si no, ¿cuál es y con qué evidencia? **Verifica `:1641-1645` tú mismo.**
2. **Revisión de la doctrina SMC.** Lee `docs/reglas-smc-ict.md` (§2.3, §6.3.5, §5.16, §2.x
   estructura/BOS/CHoCH) y `pine/reference/LuxAlgo-SMC-base.pine`. **¿Qué es exactamente un strong
   high/low en la metodología, y cómo lo determina LuxAlgo?** ¿Nuestra §2.3 está bien cuantificada o
   tiene un hueco? Si la doctrina está mal escrita, dilo: se corrige la doctrina, no el código.
3. **El esqueleto.** Qué componentes, qué entra/sale de cada uno, dónde vive cada uno
   (**CORE vs Visual-only** — esto decide si hay ADR), y en qué orden se construye.
4. **Por qué ESA solución.** Qué alternativas consideraste y por qué las descartaste. Si alguna es de
   la tabla §7, di por qué esta vez sí (con evidencia nueva).
5. **Qué resuelve exactamente, y qué NO.** Sé explícito con lo que queda fuera. En particular: ¿resuelve
   los 3 TF o solo D1? ¿Resuelve la rotación (§8.2)? ¿Y la tensión macro-vs-dealing-range (§8)?
6. **Coste.** ¿Toca el CORE? ⇒ rompe SHA `752b4083a7db419d`, re-baseline ×3, contrato MQL5, **ADR
   obligatorio**. ¿Rompe la paridad LuxAlgo? ¿Invalida los casos de prueba de §2.3 (validados al 5.º
   decimal)? ¿Cuántos inputs nuevos? (menos es mejor: cada input es superficie de calibración).
7. **Cómo se MIDE antes de implementar.** Norma dura del proyecto: **se mide en sombra, con las
   predicciones escritas ANTES**, y `pine/` no se toca hasta que la medición decida. Dinos qué medir,
   con qué predicción falsable, y **qué resultado te haría abandonar tu propia propuesta**.

---

## 10. Restricciones innegociables (`CLAUDE.md`)

1. **Anti-repaint.** Eventos solo en `barstate.isconfirmed`; `request.security(..., lookahead_off)`
   siempre. Nada del futuro. (Ojo: "el origen de la pierna" es tentador de calcular mirando adelante —
   **no se puede**.)
2. **Core sincronizado** byte-idéntico ×3. Tocarlo ⇒ `scripts/check-core-sync.ps1` + ADR.
3. **Umbrales relativos a ATR**, nunca pips fijos. Cada concepto declara qué ATR usa.
4. **Símbolo-agnóstico** (ADR-001). Nada hardcodeado a EURUSD. Validación en EURUSD, pero el diseño
   debe sobrevivir a NAS100 (donde, medido en S129, **el patrón se invierte**: el lado fósil cambia de
   bando según la tendencia secular del símbolo — hardcodear un lado viola ADR-001).
5. **R:R mínimo 1:3.** Si no es calculable ⇒ no hay señal.
6. **Scoring direccional** (scoreLong/scoreShort), nunca absoluto.
7. **Compila 0 errores / 0 warnings** o no se commitea.
8. **Presupuesto de tokens Pine:** el script está **al borde del límite** (CE10117: límite 100256,
   se llegó a medir 100335). Todo lo que añadas compite por ese presupuesto. **Los tokens no se
   predicen, se miden** (4 predicciones muertas de 4).
9. **Licencia LuxAlgo CC BY-NC-SA:** atribución obligatoria en headers, no publicar derivado comercial.

---

## 11. Dónde está todo

| Qué | Dónde |
|---|---|
| **Doctrina SMC (§2.3, §6.3.5, §5.16)** | `docs/reglas-smc-ict.md` |
| Reglas duras del proyecto | `CLAUDE.md` |
| Código: la causa raíz | `pine/SMC-Visual.pine:1641-1645` (y `:1176-1191`, `:1635`, `:1638-1640`) |
| Código: el P/D | `f_premiumDiscount` en `pine/SMC-Visual.pine:1200-1206` |
| **Este análisis, completo** | `docs/planes/DISENO-amplitud-de-swing-S132.md` (§5bis, §5ter, §5quater, §7bis) |
| Capturas del motor | `docs/planes/evidencia-S132/S132-D1-pd-motor.png`, `S132-H1-pd-motor.png` |
| Capturas anotadas del usuario | **Freddy te las entrega** (§3) |
| Historia del ancla | `DISENO-ancla-dealing-range-S128.md`, `DISENO-opcion-C-rango-pegajoso-S128.md` |
| Historia de la escala | `DISENO-cascada-pd-anidada-S130.md` |
| Historia de los pools | `DISENO-regla-de-pools-S131.md` (⚠️ §3bis.4 **contiene la premisa fabricada**, marcada) |
| Decisiones previas P/D | `docs/decisiones-pd-rango.md` (la Opción B fue descartada por el usuario en S021 y **reconfirmada 2 veces**) |
| Arneses de medición | `scripts/gen_probe_*.py` (patrón: generan un probe en sombra desde el Visual) |
| Verificación del core | `scripts/check-core-sync.ps1` |

---

## 12. Resumen en 5 líneas

1. El P/D de las 3 temporalidades **no cuadra** con lo que el usuario ve, y lleva 5 sesiones sin resolverse.
2. **Causa raíz (S132):** el código ancla el rango en **cualquier pivote** (`:1641-1645`); la doctrina
   §2.3 exige **strong high/low**. Ningún valor del parámetro arregla eso.
3. La estructura que hace falta **ya está detectada** dos líneas antes (`:1638-1640`) — el P/D no la usa.
4. **6 hipótesis alternativas están muertas con medición** (§7). No las repitas.
5. Se pide **esqueleto + porqué + qué resuelve + coste + cómo medirlo antes de tocar código**. Y que
   **cites al usuario literalmente** en cualquier requisito que le atribuyas (§6).
