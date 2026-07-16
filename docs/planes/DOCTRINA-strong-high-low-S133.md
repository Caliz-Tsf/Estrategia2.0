# DOCTRINA S133 — Cuantificar "strong high / strong low" (§2.3), y por qué el síntoma de S057 es medio doctrina

> **Estado: PROPUESTA DOCTRINAL.** No toca código. No descongela S021. Es el **paso 1 de Fable**, que nos
> saltamos en S133 al elegir "solo el probe".
> **Lo pide el usuario, literal (S133):** *"debes ayudarme a crear las zonas de premium y discount para
> cada TF pero obviamente que tenga que ver con la metodología SMC y SMC/ICT"*.

---

## 1. El giro que reordena 6 sesiones

> *"no es que sea por tiempo o quizás sí sea por tiempo pero más que nada **lo marco como referencia en
> dónde creo que quizás debiesen ir**... como estamos en una divisa bajista estamos con este error pero
> también sé que pasará así por ejemplo con uno que sea alcista **entonces debemos considerar para multi
> símbolo**"* — usuario, S133

**Sus niveles anotados NO son el oráculo.** Son una aproximación suya, sobre **un símbolo bajista**.
S128→S133 (6 sesiones) midieron hipótesis **contra sus líneas**. Ajustar a ellas es sobreajustar a
EURUSD-en-caída: viola **ADR-001** (símbolo-agnóstico) y **ADR-002** (anti-overfitting). Lo señaló él
antes que el supervisor.

**El oráculo correcto es la metodología SMC/ICT** (= `docs/reglas-smc-ict.md`, fuente de verdad del
proyecto). ⇒ **Se para de medir contra sus verdes.** Se cuantifica la doctrina y se valida en **≥2
símbolos de tendencia secular opuesta**.

---

## 2. El hueco, verificado

`docs/reglas-smc-ict.md` §2.3 (`:299-321`):

> *"Sea el rango `[L, H]` entre el **strong low** `L` y **strong high** `H` **vigentes** (los swings que
> delimitan el rango operativo actual)"* · tabla: *"rango | strong high / strong low vigentes | **se
> actualiza con la estructura**"*

**"Strong high/low" nunca se define** — es un término primitivo. Todo el motor P/D cuelga de esa palabra.
Y §5.11 (`:1218`) añade la única pista operativa: *"**Descarta** (citable): medir P/D sobre un rango ya
superado por estructura (el rango **se actualiza con cada nuevo strong high/low**)"*.

**Los casos de prueba de §2.3 no son oráculo independiente:** se generaron desde la Opción A ya
implementada (`decisiones-pd-rango.md`, tabla de validación al 5.º decimal) ⇒ validan la implementación
**contra sí misma**. (Hallazgo de Fable, verificado.)

---

## 3. La definición canónica (SMC/ICT), y lo que implica

**Strong / weak es RELATIVO AL BIAS, no al lado.** Doctrina ICT estándar, y es exactamente lo que LuxAlgo
codifica en su etiqueta (`LuxAlgo-SMC-base.pine:728/733`):

```
bias BAJISTA -> el high vigente es STRONG (defendido; el precio se alejó y rompió abajo)
             -> el low  vigente es WEAK   (liquidez pendiente de barrer)
bias ALCISTA -> el low  vigente es STRONG (defendido)
             -> el high vigente es WEAK   (será superado)
```

- **Strong low** := el mínimo cuya subida posterior **rompió estructura al alza**. Queda *protegido*.
- **Strong high** := el máximo cuya caída posterior **rompió estructura a la baja**.
- **Weak** := el opuesto. **Es liquidez: su destino es ser barrido.**

### 3bis. LA CONSECUENCIA QUE NADIE VIO EN 6 SESIONES

El síntoma que el usuario reporta desde **S057** — *"el rango P/D camina hacia el precio en tendencia
bajista"*, con el discount pegado al precio — **es, en el lado WEAK, la doctrina operando CORRECTAMENTE**.

En EURUSD bajista el **low es weak por definición**. Un weak low **debe** caminar: es liquidez que se
barre una y otra vez. Que el discount D1 esté pegado al precio en una caída **no es un bug del lado bajo**.

**El bug es que el lado STRONG también camina.** Hoy `f_resetTrailingHigh/Low` (`:1176-1186`) reancla
**ambos** lados con **cualquier** pivote (`:1641-1645`), sin mirar el bias. El strong high, que por
doctrina debe **permanecer hasta ser superado**, se sobrescribe con cada pivote nuevo.

⇒ **El fallo no es simétrico, y por eso ninguna palanca simétrica lo arregló** (escala S130/S132/S133×2,
amplitud S132, toques S131, tolerancia S131, ancla S128, expansión S133). **Todas trataban los dos lados
igual.** La doctrina no los trata igual.

### 3ter. Y esto ES el requisito multi-símbolo (ADR-001), gratis

Anclar al **bias** en vez de al **lado** es simétrico por construcción:

| símbolo | bias secular | lado STRONG (latcha) | lado WEAK (camina) |
|---|---|---|---|
| EURUSD (bajista) | BEAR | high | low ← el "error" que él ve |
| NAS100 (alcista) | BULL | low | high ← el error saldría **arriba** |

**Ya está medido:** S129 midió en NAS100USD el **patrón invertido** (`spreadHi`=0.0 / `spreadLo`=9410.9)
y lo anotó como *"el lado fósil cambia de bando según la tendencia secular del símbolo"* — se leyó como
un problema (*"hardcodear un lado viola ADR-001"*). **No es un problema: es la predicción de la doctrina.**
Nadie hardcodea un lado — lo elige el bias, que ya existe (`structTf.bias`, `chartState.bias`).

---

## 4. Parche propuesto para §2.3 (texto, para revisión del usuario)

> **Strong / weak.** El rango `[L, H]` tiene un lado **strong** (protegido) y uno **weak** (liquidez),
> determinados por el **bias estructural vigente** de la escala del rango — nunca por el lado:
> - **bias BAJISTA** → `H` es **strong high**; `L` es **weak low**.
> - **bias ALCISTA** → `L` es **strong low**; `H` es **weak high**.
>
> **Lado strong.** Se fija en el extremo de la pierna que rompió estructura y **permanece vigente hasta
> que el precio lo supera por cierre** (entonces deja de ser strong: el rango se re-ancla al siguiente
> strong de su escala). **No se reancla con pivotes** — solo la superación lo invalida.
>
> **Lado weak.** Trailing extreme: expande vela a vela con el precio (`f_updateTrailing`). Que camine hacia
> el precio **es correcto**: es liquidez pendiente. ⇒ `pct∈[0,1]` garantizado por construcción.
>
> **Escala.** El dealing range de cada TF usa el bias y la estructura **de su propia escala** ⇒ D1, H1 y M5
> pueden dar veredictos distintos simultáneamente (**rotación**, medida en S132: D1 discount 18% + H1
> premium 82% a la vez).

**Lo que este parche NO resuelve todavía y hay que decidir (§5):** cuál es "la escala" del strong de cada
TF, y de dónde sale el "bajo más bajo" grande de D1 (§3 de `DISENO-cascada-pivotes-S133.md`: es el pool #2,
edad 984, **no** el mínimo absoluto ⇒ **la ventana hay que declararla**).

---

## 5. Lo que falta decidir (y NO se puede medir contra sus verdes)

1. **La ventana de D1.** Único parámetro libre (ya concluido en S129). Su rango D1 excluye 2001. `pdLen`=1000
   acierta por coincidencia (el pool tiene edad 984 < 1000). **Declararla como input explícito.**
2. **La escala del strong por TF.** ¿El strong de H1 sale de la estructura nativa H1, o se hereda de D1 y se
   subdivide (§5.16 gradient levels, ADR-018)? Ambas existen ya en el código.
3. **Qué pasa cuando el strong es superado.** La doctrina dice "se re-ancla al siguiente strong de su
   escala". Cuál es "el siguiente" es exactamente la pregunta que S130 §9 dejó ambigua y que S131 tuvo que
   desambiguar a mano. **Aquí es donde hay que ser explícito antes de escribir una línea.**

---

## 6. Método a partir de aquí (cambia respecto a S128-S133)

- **Oráculo = la doctrina**, no las marcas del usuario. Sus niveles pasan a ser *sanity check* cualitativo.
- **Validación multi-símbolo OBLIGATORIA desde el primer probe**: ≥1 bajista (EURUSD) + ≥1 alcista
  (NAS100USD), y el criterio es que **el mismo código, sin ramas por símbolo**, ponga el latch en el lado
  que el bias dicta. Eso es P6 de Fable, ascendido de "última predicción" a **gate de entrada**.
- **Predicción escrita antes de medir** (norma S114/S132) y **frase literal del usuario citada** (norma S132).

---

## 7. Estado

- **S021 sigue congelada.** Este doc no implementa nada. Sin ADR (el ADR-021 lo escribiría el paso siguiente).
- **`pine/` intacto**, CORE SHA `752b4083a7db419d`, `pine_check` 0/0 ×4.
- **Sobrevive de Fable:** el hueco doctrinal (§2), "strong es relacional" (§3), y P7 (la mecánica
  event-driven **sí** difiere de A: 30-37%). **Muere de Fable:** "origen de la ÚLTIMA pierna" (§4bis de
  `MEDICION-relatch-estructural-S133.md`) — es demasiado local y re-fija el strong en cada evento, cuando la
  doctrina dice que **solo la superación lo invalida**.
