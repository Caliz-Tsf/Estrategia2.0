# ADR-024 — Reparto del dibujo entre Visual y Context: el eje es **heredado vs nativo**, y la unidad de reparto es el **call-site**, no el bloque de dibujo

- **Fecha:** 2026-07-20 (Sesion-139)
- **Estado:** 🔴 **PREMISA CENTRAL REFUTADA (S139, mismo día) — NO EJECUTAR SIN REDISEÑO.**

> ## 🔴 El "corte limpio" NO existe — el panel también consume la GEOMETRÍA
>
> Este ADR afirma como hallazgo central que *"Panel T14 (columnas D1/H1) → **solo los 17 escalares**"*.
> **Es falso.** Se verificó `:4782-4836` (Bias/BOS/CHoCH/MSS/P-D/EMAs) y se dio la lista por cerrada
> **sin mirar las filas de arriba y de abajo**. Cinco filas del panel se alimentan del buffer de
> geometría heredada:
>
> | Fila del panel | Consume | Línea |
> |---|---|---|
> | `OB cercano` | `f_bufZoneCell(d1Kind, d1Top, d1Bot, KIND_OB)` | `:4811` |
> | `FVG cercano` | `f_bufZoneCell(d1Kind, …)` | `:4817` |
> | `Pool cercano` | `f_bufNear(d1Kind, …)` | `:4756` |
> | `Último Sweep` | `f_bufNear(d1Kind, …)` | `:4758` |
> | `EQ H/L` | `f_bufCountEQ(d1Kind)` | `:4841` |
>
> **Comprobado ejecutando el paso 2:** al sustituir las llamadas por `f_m5Light`, `f_computeTFState`
> queda sin call-site — pero el archivo **no compila**, porque `d1Kind`/`d1Top`/`d1Bot` quedan sin
> definir en el panel. Revertido (`git checkout`), árbol limpio en `9d41479`.
>
> **La evidencia estaba a la vista desde la primera captura de la sesión** (el panel mostraba
> `OB cercano [1.15726, 1.16221]`, `Pool cercano 1.13246 SSL`, `EQ H/L 4` — cifras que solo pueden
> salir de la geometría). No se conectó.
>
> **Qué sobrevive del ADR:** el eje `heredado vs nativo`, el principio de que la unidad de reparto es
> el **call-site** (no el bloque de dibujo), y la §Frontera dura. **Qué cae:** que exista un corte
> barato que deje el panel intacto.
>
> **Opciones para el rediseño** (ninguna medida todavía):
> 1. Mover al Context también esas 5 filas ⇒ el panel queda partido en dos indicadores. Choca con
>    ADR-023 y con la identidad del Visual.
> 2. Aceptar perder esas 5 filas en las columnas D1/H1 (mostrarían "—"). Pérdida funcional real.
> 3. **Reducir el número de RANURAS del transporte** (hoy 12: `k0..k11` ⇒ 89 identificadores por
>    llamada × 2 llamadas). Es un **dial**, no cirugía: no cambia arquitectura, conserva panel y mapa,
>    y recorta muchos identificadores. **No medido — candidato más barato a probar primero.**
- **Precisa (no contradice):** **ADR-017** (el Context ya es el consumidor de lo heredado — esto lo
  lleva a su conclusión), **ADR-018/ADR-022** (el CORE sigue byte-idéntico ×3), **ADR-023** (el panel
  se lee desde el TF más bajo — el panel **no se mueve**).
- **Bloquea/desbloquea:** desbloquea la **matriz concepto × TF × {nativo, heredado}** de la F1-GATE,
  que hoy no cabe: verificar familias pide espacio de dibujo en un Visual con **21-39 tokens libres**
  (S138).

---

## Contexto

### 1. El techo es real y está medido

`headroom(Visual) ∈ [21, 39] tokens` sobre un límite de 100256 (S138, bracket sin modelo). No es una
estimación: `Visual(HEAD)` aplica y `Visual+fix-slim` = 100262. Cualquier trabajo de la F1-GATE que
añada dibujo al Visual **no compila**. El reparto no es higiene: está en el camino crítico.

### 2. Lo único que ahorra es retirar código **que se ejecuta**

S135/S137, medido ×3: Pine hace **tree-shaking** — una función sin call-site cuesta **0 tokens**.
Corolario que este ADR explota:

> El `LIBRARY CORE` es byte-idéntico en los 3 consumidores, pero **lo que cada consumidor
> ejecuta no lo es**. El mismo CORE pesa distinto en Visual, Strategy y Context.
> **La variable de reparto es el conjunto de call-sites, no el texto del CORE.**

Esto es lo que hace el reparto compatible con la **regla dura #2** sin tocarla: no se mueve una línea
del CORE. Se mueve **quién lo llama**.

### 3. El instrumento tiene ruido conocido

`docs/reglas-dev.md` §1.6c: intercepto ±1246, restas ±18 ⇒ **solo sirve para señales > 100 tokens**.
Este ADR está diseñado para producir una señal muy por encima de ese ruido (§Consecuencias), y su
verificación es un **apply real**, no una extrapolación.

---

## El hallazgo que define el corte

El Visual pide a D1 y H1 la tuple completa de `f_computeTFState` (`:2887-2888`): **17 escalares + 12
ranuras × 6 campos de geometría**. Sus tres consumidores están **ya separados** en el código:

| Consumidor | Qué consume | Dónde |
|---|---|---|
| Panel T14 (columnas D1/H1) | solo los **17 escalares** | `SMC-Visual.pine:4782-4836` |
| `f_depthBand` (bandas de profundidad) | solo `pdHigh`/`pdLow` | `SMC-Visual.pine:3071-3079` |
| **Mapa MTF** (`f_drawMTFState` + `f_drawMTFZones`) | solo la **geometría** | `SMC-Visual.pine:4579-4583` |

Y **la función ligera ya existe**: `f_m5Light` (`:2844`) devuelve exactamente esos 17 escalares, con el
mismo orden de campos, y es **espejo fiel de ADR-021** — usa `f_pdRelatch` / `f_pdTop` / `f_pdBottom`,
el mismo dealing range del 2.º extremo. Hoy ya se ejecuta en el Visual (columna M5, `:2893`), así que
la función **ya está viva**: añadirle call-sites cuesta solo los call-sites.

⇒ **El corte no pasa por el bloque de dibujo. Pasa por la llamada.** Mover solo `f_drawMTFZones` no
ahorraría casi nada: `f_computeTFState` seguiría ejecutándose para alimentar el panel. Mover la
**llamada** es lo que apaga la función entera.

---

## Decisión

**El eje del reparto es `heredado` vs `nativo`, no la familia ni la capa de dibujo.**

1. **El Visual conserva todo lo NATIVO del chart-TF** — L0/L1/L2/L3, swings, gradient levels, panel,
   alertas. Es el consumidor del TF que el usuario está mirando.
2. **El Context recibe todo lo HEREDADO de HTF** — es lo que ADR-017 ya declara que es. En concreto,
   se le trasladan:
   - las dos `request.security(..., f_computeTFState(...))` de D1 y H1 (`Visual:2887-2888`),
   - los 12 `array.from` del buffer genérico (`Visual:2897-2908`),
   - `f_drawMTFState` y `f_drawMTFZones` (`Visual:4466-~4590`).
3. **El Visual sustituye esas dos llamadas por `f_m5Light("D","60")`.** El panel y `f_depthBand`
   quedan **funcionalmente idénticos** (mismos 17 campos, misma semántica ADR-021). ADR-023 intacto:
   el panel no se mueve ni cambia de forma.
4. **El `LIBRARY CORE` no se toca.** `check-core-sync` ×3 debe seguir dando el SHA `9559a0d7fe58b213`.
   Si el SHA cambia, la ejecución está mal hecha y se revierte.
5. **La fusión de dibujo heredado NO se hace aquí.** El mapa MTF se traslada al Context **tal cual**,
   sin rediseñar sus reglas de solape. Ver §Frontera dura.

---

## Frontera dura — este ADR MUEVE maquinaria, no DECIDE la herencia

*(Instrucción del usuario, S139. Restringe el alcance de este ADR.)*

**La herencia se decide después de que todos los conceptos estén verificados en su TF propio y
nativo.** Recién entonces se decide *cuáles* se heredan y *por qué*, y luego se revisa cada uno **en
cada TF al que se herede**. ⇒ La matriz `concepto × TF × nativo` es el **prerrequisito**, no un
trabajo paralelo.

Consecuencia sobre este ADR — y es lo que lo salva, no lo que lo estorba:

- Mover la maquinaria de herencia **fuera del Visual** es exactamente lo que libera espacio para
  verificar los nativos. El reparto **sirve a** ese orden en vez de adelantarse a él.
- Pero el traslado debe ser **verbatim**: mismas reglas, mismo dibujo, mismo comportamiento. **No se
  fija qué se hereda ni cómo se resuelve el solape heredado.** Eso queda para después de los nativos.
- ⇒ **La ejecución para en el paso 4.** Los pasos 5-6 de la versión inicial (fusionar con las reglas
  de solape del Context) quedan **fuera de este ADR**.

**Y el solape que de verdad duele no es el que este ADR tocaría.** No es zona-contra-zona del mismo
rango (colapso >70%, 0.3·ATR): es el **anidamiento** — se hereda p. ej. un **OB de H1** y **dentro**
caen otros OB/FVG más **sus etiquetas**. **La familia de etiquetas es la que más ruido hace.** El
criterio actual mide pares comparables y **no ve el caso contenedor ⊃ contenido**. Es un problema
propio, y se ataca cuando toque la curación de lo heredado — no ahora, y no como un ajuste de
porcentaje.

### Predicción pre-registrada (escribir ANTES de medir, norma del proyecto)

- **P1:** `f_computeTFState` deja de tener call-site en el Visual ⇒ el tree-shaking la retira ⇒
  el ahorro es de **cientos de tokens**, no de decenas. *Falsable:* si el ahorro medido es < 100, la
  premisa del tree-shaking por call-site está mal entendida y el ADR se retira.
- **P2:** el panel sigue dando **D1 34% · H1 33% · M5 56%** en el mismo chart y misma fecha (oráculo
  conocido de S134/S138). *Falsable:* cualquier otro número ⇒ `f_m5Light` no es espejo fiel y la
  sustitución del punto 3 es inválida.
- **P3:** `data_get_pine_lines` sigue devolviendo el P/D de D1 (1.51441 / 1.23400 / 0.95360) — ahora
  dibujado por el Context. *Falsable:* si desaparecen, el traslado perdió el dibujo.

Verificación = **apply real** con lectura de `pine_get_console` ("Compilado." + "Añadido al gráfico.")
y `data_get_study_values` fresco. `pine_check` 0/0 **no valida** (S135).

---

## Alternativas descartadas

- **Reparto por familia** (OB/FVG al Visual, liquidez al Context). Descartada: rompe la lectura de
  confluencia — el usuario mira el cúmulo cerca del precio, que es confluencia real y **quiere verlo
  junto** (S120). Además obliga a duplicar el sistema de solape por familia.
- **Reparto por capa de dibujo** (L0/L1 al Visual, L2/L3 al Context). Descartada: L2/L3 es el 60% del
  dibujo nativo y es justo lo que la F1-GATE tiene que verificar en el TF propio.
- **Mover solo el bloque de dibujo MTF, dejando las `request.security` en el Visual.** Descartada por
  el hallazgo de §El corte: no apaga `f_computeTFState`, ahorra poco, y deja el transporte huérfano.
- **Adelgazar más el Visual (dieta).** Agotada: S120/S125/S133 ⇒ refactorizar no ahorra, y las ramas
  muertas ya se están rascando de una en una (S138 financió `pdMid` con **una** rama inalcanzable).

---

## Consecuencias

### A favor

- El ahorro esperado desbloquea la F1-GATE: espacio para verificar familias en el Visual.
- El Context pasa a ser lo que ADR-017 dijo que era — **todo** lo heredado en un sitio, con un solo
  sistema de solape MTF. Hoy está partido entre dos scripts con dos reglas distintas.
- Paridad Fase 4: el EA MQL5 no tiene el artefacto de `request.security` ni el límite de tokens. Un
  corte por `heredado vs nativo` **traduce a MQL5 como un módulo**; un corte por familia o por capa
  no traduce a nada.

### En contra — **la restricción de 2 slots, sin disfraz**

El plan **gratuito de TradingView admite 2 indicadores por chart**. Tras este reparto, el sistema
visual completo **exige los dos**: Visual (nativo) + Context (heredado). Consecuencias que hay que
aceptar explícitamente:

1. **En Fase 3 (Strategy Tester) hay que soltar uno.** La Strategy ocupa slot. El backtesting se hará
   con Strategy + uno de los dos, no con los tres. Esto ya era cierto, pero el reparto lo convierte
   en estructural: hoy el Visual solo se puede leer **completo** con el Context al lado.
2. **El orden de apilado pasa a ser funcional, no cosmético.** El Context debe ir **bajo** el Visual
   (regla ya declarada en `Context:~1995`). Si el usuario los apila al revés, lo heredado tapa lo
   nativo. Es una instrucción de operación, como ADR-023.
3. **Esto es un techo, no una solución.** El reparto compra espacio **una vez**. Cuando el Context se
   acerque a su propio techo (~83k ± 3k libres hoy, S138) no hay tercer slot gratuito. La salida
   entonces es plan de pago o retirar dibujo, y conviene decirlo ahora y no descubrirlo en Fase 3.

### Riesgos

- **`f_m5Light` podría no ser espejo perfecto** para D1/H1 en algún campo que el panel muestre. P2 es
  exactamente el test de esto, y tiene oráculo numérico conocido.
- **Duplicación de P/D heredado** entre el mapa MTF entrante y los extremos que el Context ya dibuja.
  Debe resolverse en el punto 5, no dejarse para "se ve en pantalla".
- **El Context sube de coste** (ejecutará `f_computeTFState` ×2 + el dibujo). Tiene margen holgado,
  pero el margen es **una extrapolación** (±1,2k sobre 83k = 1,5%, tolerable) y **solo se confirma al
  aplicar**. El compilador dice sí o no; no hay que medirlo antes.

---

## Ejecución (sesión siguiente, no ahora)

Orden obligatorio — cada paso con apply real antes del siguiente:

1. Medir `base_V` de referencia con `Visual(HEAD)` (apply real, marcador nuevo por build).
2. Sustituir las 2 llamadas por `f_m5Light` **sin tocar el dibujo MTF todavía** → medir. Aquí debe
   aparecer P1 (el tree-shaking de `f_computeTFState`), porque el mapa MTF queda sin datos y sin
   call-site útil. *Esta es la medición que decide el ADR.*
3. Verificar P2 (panel 34/33/56) antes de mover nada al Context.
4. Trasladar transporte + dibujo al Context **verbatim** (sin fusionar reglas de solape, §Frontera
   dura) → apply real, P3.
5. `scripts/check-core-sync.ps1` ×3 (SHA `9559a0d7fe58b213` intacto) → commit. **Aquí termina el ADR.**
   La curación de lo heredado (anidamiento, etiquetas) es trabajo posterior a la matriz de nativos.

Si el paso 2 no produce la señal de P1, **se detiene y se revierte**: el ADR se apoya en esa premisa
y no se ajusta el criterio para salvarlo (regla dura #8).
