# ADR-022 — `EXTREMES CORE`: un 2.º bloque byte-idéntico para Strategy + Context

> ## 🔴 PREMISA CUESTIONADA POR MEDICIÓN — leer antes de actuar sobre este ADR *(S135, 2026-07-18)*
>
> Este ADR se apoya en **"en Pine una función no-llamada SÍ cuenta tokens"** (heredado de ADR-020).
> En S135 se midió **lo contrario**, tres veces y con el mismo número exacto (107986): las funciones
> sin call-site **cuestan 0 tokens** — Pine las tree-shakea por completo.
>
> **La paradoja abierta es justo este ADR:** si el código muerto cuesta cero, **¿por qué retirar
> `f_tfExtremes` (139 líneas que el Visual no llamaba) resolvió el `CE10117` en S133?** No se ha
> re-medido. Hipótesis sin comprobar: que sí tuviera un call-site en Visual, o que la retirada
> coincidiera con otro cambio.
>
> **NO SE REVOCA:** el bloque `EXTREMES CORE` existe, está verificado por `check-core-sync` y
> funciona. Lo que está en duda es **la explicación de por qué funcionó**, no el hecho.
> Entregado a Fable: `docs/planes/DOSSIER-FABLE-capacidad-y-codigo-muerto-S135.md` §2.1 y §4.

- **Fecha:** 2026-07-15 (Sesion-133)
- **Estado:** **ACEPTADA** — ejecutada. Decisión del usuario en S133 entre 4 opciones.
- **Precisa (no contradice):** **ADR-018** (`f_tfExtremes` sigue siendo lógica compartida y de una sola
  fuente — cambia *dónde* vive, no *qué* es). **ADR-020** (extiende su regla; ver §Decisión).
  **Regla dura #2** (CORE byte-idéntico) — **se mantiene, y se refuerza** con un 2.º bloque verificado.
- **Desbloquea:** **ADR-021** (el 2.º extremo estructural), que no podía aplicar en vivo por `CE10117`.

---

## Contexto

Implementar ADR-021 llevó al Visual a **`CE10117`: `too many tokens: 100952. The limit is 100256`**
(+696). El Visual ya rozaba el techo desde S120 (ADR-020) y el tracker del 2.º extremo lo cruzó.

**Un intento fallido primero, y su lección.** Se refactorizaron las 4 copias del bloque a un UDT
(`SMC_PdRange` + 3 funciones). **Ahorro medido: CERO** (100952 antes y después). La memoria del proyecto
ya lo sabía y se ignoró: *"S125: helper+sort 100615 vs inline 100601 → distan 14: lo caro es TOCAR el
bloque, no la FORMA"*. ⇒ **En Pine, refactorizar no ahorra tokens. Solo retirar código los ahorra.**
(El refactor se conservó igualmente: no compra tokens, pero elimina 4 copias que había que mantener a
mano. Commit `aee69a7`.)

**La causa, aislada por ABLACIÓN MEDIDA** (no deducida): `f_tfExtremes` = **139 líneas que el Visual
carga y NUNCA llama**. Sus call-sites reales están en `SMC-Strategy.pine:2699/:2700` y
`SMC-Context.pine:1901/:1902`; en Visual, **ninguno**. Vive en el `LIBRARY CORE` solo por la regla
byte-idéntica (ADR-018). Y **en Pine una función no-llamada SÍ cuenta tokens** (ADR-020, confirmado
empíricamente en S120). Se retiraron **solo** esas 139 líneas del Visual y se inyectó en vivo →
**"Compilado." + "Añadido al gráfico." SIN error**. Mismo archivo salvo eso ⇒ **causa aislada**.

---

## Decisión

**`f_tfExtremes` sale del `LIBRARY CORE` (en los 3) y pasa a un bloque nuevo
`// === EXTREMES CORE ===`, byte-idéntico entre `SMC-Strategy.pine` y `SMC-Context.pine`.**
El Visual **no lo tiene**.

**Regla que precisa (extiende ADR-020).** ADR-020 sentó: *"una función que **un solo** consumidor usa no
pertenece al CORE compartido; el CORE es para lógica que ≥2 consumidores comparten"*. `f_tfExtremes` la
comparten **2 de 3** ⇒ por la **letra** iría al CORE; por el **espíritu**, no: **el CORE no debe cargar a
quien no la usa**. Se resuelve sin romper ninguna de las dos:

> **El CORE compartido contiene lo que usan TODOS los consumidores. La lógica que comparte un
> SUBCONJUNTO de consumidores vive en su propio bloque byte-idéntico, verificado igual que el CORE.**

Así, ADR-020 (funciones de-un-consumidor → locales) y esta ADR (funciones de-un-subconjunto → bloque
propio) son el mismo principio a distintas cardinalidades.

**`check-core-sync.ps1` extendido** — sin esto quedaban **2 copias sincronizadas a mano**, que es
exactamente el fallo que la regla dura #2 existe para prevenir:

- `Get-CoreBlock` generalizada a `Get-Block(path, patrón)`.
- Verifica `EXTREMES CORE` byte-idéntico entre Strategy y Context; **error** si está en uno y no en el otro.
- **GUARDRAIL:** **error si `SMC-Visual.pine` vuelve a contener `f_tfExtremes` o el bloque** — que es la
  razón de existir del split. Sin este guard, un `git merge` descuidado reintroduce el CE10117 en silencio.

---

## Consecuencias

| Partida | Efecto |
|---|---|
| **LIBRARY CORE** | **1915 → 1776 líneas** — **por debajo del baseline original (1866)**. SHA re-baselined `d8a412b910c78b36` → **`9559a0d7fe58b213`**. |
| **EXTREMES CORE** | 148 líneas · SHA `5f851d87e5fda720` · Strategy + Context. |
| **Regla dura #2** | **Se mantiene y se refuerza**: ahora hay **dos** bloques verificados en vez de uno, y un guardrail nuevo. |
| **ADR-018** | **Intacta en lo esencial.** Promovió `f_tfExtremes` a lógica compartida de una sola fuente; sigue siéndolo. Solo cambia el bloque en el que vive, porque el Visual nunca fue su consumidor. |
| **MQL5 (Fase 4)** | Sin impacto en paridad: `f_tfExtremes` sigue siendo una sola fuente. Su golden test vive con el motor de extremos (Strategy/Context), no con el CORE de todos. |
| **Headroom** | El Visual baja del techo ⇒ **desbloquea ADR-021** y deja margen para los conceptos siguientes. |
| **Reversible** | `git revert` de `f91a2bd`. El bloque está íntegro en Strategy/Context. |

**Verificado:** `pine_check` **0/0 ×3** · `check-core-sync` **OK** en ambos bloques.

**PENDIENTE (no verificado al cerrar la ADR):**
1. **El número de tokens del Visual final en vivo.** La ablación demostró que sin `f_tfExtremes` compila
   **y** aplica, pero el Visual completo no llegó a aplicarse: tras varios ciclos la UI de TV dejó el
   editor en un script *"Sin nombre"* y hay que reabrir el slot. **Es la única verificación que falta.**
2. **Validación visual con el usuario:** nadie ha visto los 3 P/D dibujados. El gate de ADR-021 se pasó
   con un probe **truncado en `// === DIBUJO ===`**, sin render.

---

## Alternativas descartadas

| Alternativa | Por qué cae |
|---|---|
| **Fuera del CORE, copia suelta en cada uno** (lo que ADR-020 hizo con `f_detectVolumeImbalance`) | Válido para **1** consumidor; con **2** deja 2 copias sin vigilar ⇒ divergen a la primera edición. El bloque verificado cuesta ~30 líneas de script y elimina el riesgo. |
| **Otra dieta, no tocar ADR-018** | Habría que encontrar ~700 tokens en otro sitio **y** el Visual seguiría cargando 139 líneas muertas ⇒ el techo vuelve con el siguiente concepto. Trata el síntoma. |
| **Revertir ADR-021** | Tirar una regla que pasó su gate (anida, rota, clava el suelo de H1 a 0.3 pips) por un problema de presupuesto **resuelto y medido**. |
| **Reducir comentarios** | **No cuentan tokens** en Pine (ADR-020) ⇒ cero efecto. |
| **Refactorizar (UDT/helpers)** | **Medido: 0 tokens.** La forma no cambia el coste (S125, y esta sesión otra vez). |

---

## ANEXO S136 — resuelto el pendiente 1, y la premisa de tokens era falsa

**Pendiente 1 de esta ADR ("el número de tokens del Visual final en vivo") — RESUELTO y medido:**

- `Visual(HEAD) + lastre(300)` = **107986** (referencia S135, medida ×3)
- `Visual(HEAD) + lastre(300) + fix-slim de pdMid` = **108031** (S136, 00:45:09)
- ⇒ `coste(fix-slim)` = **45 tokens** ⇒ **`base_V` = 100217** y **headroom real del Visual = 39
  tokens** (límite 100256).

Legitimidad de la resta verificada antes de medir: `git log 42207ea..HEAD -- pine/SMC-Visual.pine`
**vacío** ⇒ el Visual no cambió desde la medición de referencia.

⇒ El *"el fix de `pdMid` falla por 6"* era **numéricamente correcto pero por la razón equivocada**
(lo había señalado la auditoría de Fable, §3): no es que el fix cueste 6 — **cuesta 45 y solo hay 39
libres**. Para que quepa hay que liberar **≥6 tokens de código que se EJECUTA**.

**La premisa de tokens de esta ADR era falsa.** La alternativa descartada *"el Visual seguiría
cargando 139 líneas muertas ⇒ el techo vuelve"* asumía que el muerto costaba ~700 tokens. **Medido
en S136: costaba CERO** (ver ANEXO S136 de ADR-020, `ΔT = 142` sobre `aee69a7` vs `f91a2bd`).

**NO se revoca la ADR.** El bloque `EXTREMES CORE` se queda: **dos copias verificadas son mejores
que tres aunque los tokens no lo exijan**. Lo que cae es la justificación por presupuesto, no la
arquitectura.
