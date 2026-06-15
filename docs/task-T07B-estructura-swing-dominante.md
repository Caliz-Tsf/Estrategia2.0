# TASK F1-S1.2-T07B — Estructura BOS/CHoCH DOMINANTE (swing length 50)

> **Tipo:** sesión dedicada (Sesion-022). **Estado:** ✅ COMPLETADO E IMPLEMENTADO (Sesion-022, 2026-06-15). Compila 0/0, core-sync OK mismo SHA, validación visual con LuxAlgo (3 casos presentes, sin regresión T01–T07), aprobado por Freddy. Ver ADR-004 + Sesion-022. Pendiente Fase 3: bias dominante en scoring.
> **Origen:** `docs/pendiente-estructura-swing-grande.md` (hallazgo del usuario en Sesion-021).
> **Regla de oro de este task:** **NO romper nada de T01–T07.** Solo se AÑADE una capa;
> no se modifica detección ya validada (swings 5, interno 3, OB, FVG, P/D).
> **Brief autocontenido:** cualquier IA debe poder implementar esto leyendo solo este
> documento + los 4 archivos que referencia. No re-litigar la arquitectura ya decidida abajo.

---

## 0. TL;DR para el implementador

1. Hoy el sistema dibuja BOS/CHoCH a `swingLen=5` (estructura local) e interno `=3`. **Falta
   por completo la estructura GRANDE de LuxAlgo (`length=50`)** — los movimientos
   estructurales que el usuario ve en LuxAlgo y NO en nuestro Pine.
2. **Decisión arquitectónica tomada: Opción C (capa aditiva).** Se añade una **tercera
   escala** de estructura (`i_majorLen=50`) reutilizando el CORE existente **sin modificarlo**.
   No se re-escala T02–T06 (eso sería Opción B, descartada — ver §2).
3. El CORE (`SMC_Structure`, `f_detectStructure`, `f_setStructureHigh/Low`, `f_detectSwings`)
   **ya es escala-agnóstico**: acepta cualquier instancia y cualquier longitud. Por eso esta
   capa se integra **sin tocar el bloque `// === LIBRARY CORE ===`** → `check-core-sync` sigue
   OK trivialmente y T01–T07 quedan byte-intactos.
4. Trabajo neto = **inputs nuevos + 1 var de estado + ~10 líneas de wiring (idénticas en Visual
   y Strategy) + 1 función de dibujo (solo Visual) + docs + validación.**

---

## 1. Contexto y problema (resumen)

Mapa de escalas — **esto es lo que hay que entender antes de tocar nada:**

| Capa | LuxAlgo (referencia) | Nuestro Pine HOY | Tras este task |
|---|---|---|---|
| **Dominante / swing grande** | `getCurrentStructure(50)` — "Swing Structure" (ref `LuxAlgo-SMC-base.pine` :95 input=50, :782) | **NO EXISTE** ❌ | `structMajor` (`i_majorLen=50`) ✅ |
| **Swing / mayor** | `getCurrentStructure(5, internal=true)` — "Internal Structure" (:783) | `structSwing` (`i_swingLen=5`) | sin cambios |
| **Interno fino** | — | `structInternal` (`i_internalLen=3`) | sin cambios |
| **Rango P/D (dealing range)** | `trailing` sobre swing 50 (:782, :430-454) | `trailing` (`i_pdSwingLen=50`) — T07 | sin cambios |

**Diagnóstico:** nuestro `swingLen=5` equivale al **interno** de LuxAlgo. La capa de swing
GRANDE (50) **nunca se implementó para la estructura** (solo se usó esa longitud para el rango
P/D en T07). Por eso en el chart solo se ven BOS/CHoCH pequeños y densos, no los movimientos
estructurales grandes.

**Coherencia que esto resuelve:** hoy P/D usa swing 50 pero la ESTRUCTURA usa 5. LuxAlgo usa 50
para ambos. Este task cierra esa inconsistencia añadiendo la estructura a escala 50, **sin**
quitarle al sistema la granularidad local (5/3) que ya está validada y que sirve para el gatillo
de entrada.

---

## 2. Decisión arquitectónica (paso 0 — ratificar con `smc-architect`, NO re-litigar)

**ELEGIDA: Opción C — añadir 3.ª capa de swing dominante (50), aditiva.**

### Por qué C y no B

- **(B) Re-escalar `swingLen 5→50`, `internalLen 3→5`** (alinear nombres a LuxAlgo) se
  **DESCARTA** porque:
  1. Invalida toda la spec `reglas-smc-ict.md` §1.1–§1.5 (swings, HH/HL/LH/LL, BOS, CHoCH, MSS)
     y §2.1 (OB depende de las rupturas de estructura): **TODOS** los casos de prueba fechados
     están construidos a escala 5. Cambiar la base re-abre y re-valida T02–T06.
  2. Contradice **ADR-002** (umbrales/escala congelados hasta calibración de Fase 3) y la regla
     dura #8 (no se ajusta un criterio ya validado).
  3. Pierde la estructura LOCAL (5/3), que es deseable como gatillo fino de entrada en ICT
     (HTF da contexto, LTF da entrada). Colapsar a una sola escala (50) destruye esa
     granularidad. La spec **siempre** quiso múltiples escalas (§1.3: "se evalúa en ambas").
  - El error real de origen no fue tener 5/3, sino **no haber añadido la capa 50**. C lo corrige
    sin desmontar lo bueno.
- **(C) Añadir capa dominante (50)** se **ELIGE** porque:
  1. Es **puramente aditiva**: el CORE no cambia (ver §4), `check-core-sync` queda OK, T01–T07
    intactos. Cumple el mandato "sin tocar nada más de lo creado".
  2. Refleja la realidad SMC: 3 escalas = **contexto dominante (50) / estructura (5) / liquidez
    interna (3)**. Es lo que tiene un sistema serio.
  3. Coherente con T07, que ya usa 50 para el rango dominante: ahora la ESTRUCTURA también tiene
    su capa 50, alineada con el rango.
- **(A) Statu quo** (no mostrar la estructura grande): descartada por el usuario.

### El único punto de diseño abierto: ¿la capa 50 manda el *bias*?

Hoy el bias headline (`chartState.bias`, vía `f_updateTFState(chartState, evStructSwing)`, T04)
lo fija la escala swing(5). **En este task NO se cambia eso** (tocarlo modifica T04, validado, y
el scoring tiene pesos congelados hasta Fase 3, ADR-002). La capa dominante se **DETECTA y
DIBUJA**; su papel en el bias/scoring es **decisión explícita de Fase 3** (Sprint 2.1 +
calibración). Así el task queda 100% aditivo. Ver §6 (nota Fase 3).

> **Acción del implementador:** abrir con `smc-architect` (opus) para **ratificar** C (no
> re-decidir) y confirmar el alcance IN/OUT de §3. Si `smc-architect` propusiera cambiar el
> bias ahora, eso es scope nuevo → ADR aparte, no entra en este task.

---

## 3. Alcance — qué SÍ y qué NO

### SÍ (entra en este task)
- Nuevo input `i_majorLen` (default **50**) + inputs de dibujo de la capa dominante.
- Nueva instancia de estado `var SMC_Structure structMajor = SMC_Structure.new()` (consumer-side).
- Wiring de detección de la capa dominante (pivotes 50 → set structure → detect ruptura → push
  evento), **idéntico en Visual y Strategy** (sección DETECCIÓN, no es el CORE hash-checked, pero
  debe quedar lógicamente igual en ambos).
- Dibujo prominente de la estructura dominante (solo Visual): líneas + etiquetas BOS/CHoCH
  grandes, estilo distinto del swing/interno.
- (Opcional, nice-to-have) etiquetas HH/HL/LH/LL a escala 50 (`i_showMajorSwings`).
- (Opcional) fila de panel "Bias dominante (50)".
- Actualización de los 3 documentos + ADR (§7).
- Validación ≥90 con `smc-validator-agent` contra los casos del usuario (§8).

### NO (fuera de alcance — NO tocar)
- ❌ El bloque `// === LIBRARY CORE ===` (ninguna línea). Se REUTILIZAN sus funciones tal cual.
- ❌ `structSwing` (5), `structInternal` (3), su detección, su dibujo, sus inputs.
- ❌ `chartState.bias` / `f_updateTFState` / T04 (el bias headline no cambia).
- ❌ Order Blocks (T05): el OB se detecta de `evStructSwing` (escala 5). La capa dominante **NO**
  alimenta el pipeline de OB. (OB de escala dominante = task futuro, no este.)
- ❌ FVG (T06), Premium/Discount (T07): no se tocan.
- ❌ `SMC_TFState` (es CORE; añadirle un campo cambiaría el CORE). Si se quiere registrar el bias
  dominante, va en una var consumer-side, no en el UDT del CORE.
- ❌ MTF / `request.security` (eso es T13, Sprint 1.4).

---

## 4. Diseño técnico (preciso, listo para copiar)

> Archivos: `pine/SMC-Visual.pine` (indicator) y `pine/SMC-Strategy.pine` (strategy).
> El CORE (`pine/SMC-Library.pine` + bloque `// === LIBRARY CORE ===` en ambos consumidores)
> **NO se modifica**. Verificado: `SMC_Structure`, `f_setStructureHigh/Low`, `f_detectStructure`
> y `f_detectSwings` son escala-agnósticos (operan sobre la instancia/longitud que reciban).

### 4.1 Inputs (sección `// === INPUTS ===`, ambos consumidores)

```pine
// Estructura DOMINANTE (swing grande = LuxAlgo getCurrentStructure(50), ref :782).
// NUESTRO swingLen=5 ≈ interno de LuxAlgo; esta capa es la que faltaba [T07B].
i_majorLen     = input.int(50, "Swing dominante (estructura grande)", minval = 10, group = GRP_STRUCT)
```
En **Visual** además (dibujo):
```pine
i_showMajor       = input.bool(true,  "Mostrar estructura dominante (50)", group = GRP_STRUCT)
i_showMajorSwings = input.bool(false, "Mostrar HH/HL/LH/LL dominantes",     group = GRP_STRUCT) // opcional
```
> Nota: `i_majorLen` coincide hoy con `i_pdSwingLen=50` (T07) **a propósito** (ambos = swing
> dominante de LuxAlgo). Se mantienen **inputs separados** para no acoplar la calibración del
> rango P/D con la de la estructura (cambiar uno no debe mover el otro). No reutilizar la
> variable del otro.

### 4.2 Estado (sección `// === DETECCIÓN TF PROPIO ===`, ambos consumidores)

Junto a `structSwing` / `structInternal` (Visual ~:474):
```pine
var SMC_Structure structMajor = SMC_Structure.new()
```
Array dedicado para sus eventos (NO mezclar con `SMC_events`, que lo consume el OB/otros):
```pine
var array<SMC_Event> SMC_eventsMajor = array.new<SMC_Event>()
```

### 4.3 Wiring de detección (ambos consumidores, byte-igual entre sí)

Reutiliza EXACTAMENTE el patrón de `structSwing` pero con `i_majorLen`. Insertar junto al cómputo
de pivotes (Visual ~:488, donde ya está `f_detectSwings` para 5/3/PD):
```pine
// Pivotes de escala DOMINANTE (50). Mismo guard anti-repaint que swing/interno.
// Latencia inherente = i_majorLen velas (≈2 días en H1): el pivote pertenece a la
// vela t = bar_index - i_majorLen y NO existe hasta su cierre [§1.1]. Es correcto.
[majorHigh, majorLow] = f_detectSwings(i_majorLen)
newMajorHigh = barstate.isconfirmed and not na(majorHigh)
newMajorLow  = barstate.isconfirmed and not na(majorLow)
if newMajorHigh
    f_setStructureHigh(structMajor, majorHigh, bar_index - i_majorLen, time[i_majorLen])
if newMajorLow
    f_setStructureLow(structMajor, majorLow, bar_index - i_majorLen, time[i_majorLen])
```
Detección de ruptura (junto al bloque `if barstate.isconfirmed` que llama a `f_detectStructure`,
Visual ~:527). La capa dominante es la mayor → guards `true, true` (no necesita dedupe contra una
escala superior):
```pine
SMC_Event evStructMajor = na
if barstate.isconfirmed
    evStructMajor := f_detectStructure(structMajor, bar_index, time, true, true)
    if not na(evStructMajor)
        f_pushEvent(SMC_eventsMajor, evStructMajor, MAX_EVENTS)
    // NO se llama f_updateTFState con evStructMajor: el bias headline NO cambia (ver §2).
```
> **Verificación obligatoria:** este bloque debe quedar **idéntico** en Visual y Strategy
> (lógica de detección compartida). El dibujo (§4.4) es SOLO Visual.

### 4.4 Dibujo (SOLO Visual, sección `// === DIBUJO ===`)

Nueva función prominente (NO modificar la `f_drawStructure` existente de T03). Usa
`xloc.bar_time` para anclar por tiempo (robusto en spans largos — mismo motivo que el fix de
"líneas volando" de T07; los ejemplos del usuario abarcan hasta 15 días):
```pine
// f_drawStructureMajor: estructura dominante (50). Más gruesa y con etiqueta grande que
// el swing(5)/interno(3) para distinguir la capa. Color propio (azul alcista / naranja
// bajista) para no confundir con teal/rojo del swing. Anclaje por bar_time (spans largos).
f_drawStructureMajor(int pivotTime, float level, int breakTime, int kind, int dir) =>
    col = dir == DIR_BULL ? color.new(#2962FF, 0) : color.new(#FF6D00, 0)
    txt = kind == KIND_CHOCH ? "CHoCH ▣" : "BOS ▣"
    line.new(pivotTime, level, breakTime, level, xloc = xloc.bar_time, color = col, style = line.style_solid, width = 3)
    label.new(breakTime, level, txt, xloc = xloc.bar_time, style = dir == DIR_BULL ? label.style_label_down : label.style_label_up, color = color.new(col, 80), textcolor = col, size = size.normal)
```
Llamada (junto a las llamadas de dibujo de estructura, Visual ~:620). Usa el pivote roto correcto
(`highTime` si la ruptura fue alcista, `lowTime` si bajista):
```pine
if i_showMajor and not na(evStructMajor)
    int pivotT = evStructMajor.dir == DIR_BULL ? structMajor.highTime : structMajor.lowTime
    f_drawStructureMajor(pivotT, evStructMajor.price, evStructMajor.barTime, evStructMajor.kind, evStructMajor.dir)
```
> `SMC_Structure` guarda `highTime`/`lowTime` y `SMC_Event` guarda `barTime` (verificado en el
> CORE) → todas las coordenadas de tiempo están disponibles, sin necesidad de almacenar nada nuevo.

(Opcional `i_showMajorSwings`: dibujar HH/HL/LH/LL a escala 50 con `f_classifySwing` sobre un
array dedicado `SMC_swingsMajor` y la `f_drawSwing` existente con tamaño mayor. Nice-to-have, no
bloqueante para el DoD.)

### 4.5 Panel (opcional, Visual `// === PANEL ===`)
Añadir fila "Bias dom. (50): ↑/↓/–" leyendo `structMajor.bias`. No bloqueante.

---

## 5. Por qué esto NO rompe T01–T07 (checklist de seguridad)

- **CORE byte-idéntico:** no se edita ninguna línea entre `// === LIBRARY CORE ===` y el siguiente
  header `// === ... ===`. `scripts/check-core-sync.ps1` compara SOLO ese bloque → seguirá OK con
  el MISMO SHA actual (415 líneas, `24c3a4a28fcf74c3`). Confirmarlo tras implementar.
- **Detección existente intacta:** `structSwing`, `structInternal`, `trailing` y sus llamadas no
  se tocan. Solo se AÑADEN líneas nuevas.
- **OB/FVG/P-D intactos:** el OB lee `evStructSwing` (no `evStructMajor`); FVG y P/D no dependen de
  la nueva capa. Sin efectos colaterales.
- **`SMC_events` sin contención:** los eventos dominantes van a `SMC_eventsMajor` (array nuevo), no
  al `SMC_events` compartido.
- **Anti-repaint:** toda la detección bajo `barstate.isconfirmed`; pivote 50 anclado a
  `t = bar_index - i_majorLen`. Cero futuro [D-PINE-03].

---

## 6. Notas de diseño y Fase 3

- **Bias dominante (deferido a Fase 3):** una vez exista esta capa, evaluar **con datos OOS** si el
  bias del scoring debe venir de la escala 50 (contexto) en vez de la 5, o de una combinación
  (50 = contexto/gate, 5 = gatillo). Es una decisión de calibración (Sprint 2.1 + Fase 3), NO de
  este task. Registrar como pendiente en ESTADO-ACTUAL.
- **P/D revisitable (relación con T07):** con la estructura dominante ya disponible, la Opción B de
  T07 (anclar el dealing range a los *strong high/low* de la estructura dominante, en vez de
  trailing extremes crudos) se vuelve natural y más estable. Mantener como nota de Fase 3 en
  `docs/decisiones-pd-rango.md` (ya contemplada ahí).
- **Latencia visible:** la estructura 50 confirma 50 velas tarde y su ruptura puede tardar días
  (coincide con "inicia… se termina de formar…" de los ejemplos del usuario). Es anti-repaint
  correcto, no un bug.

---

## 7. Cambios documentales requeridos (los 3 docs + ADR)

1. **`docs/reglas-smc-ict.md`**
   - §1.1: añadir la **tercera escala** a la tabla de parámetros — `majorLen` (default **50**,
     "estructura dominante / swing grande = LuxAlgo swing structure"). Aclarar el mapeo: nuestro
     `swingLen=5` ≈ interno de LuxAlgo; `majorLen=50` = swing de LuxAlgo.
   - §1.3 / §1.4: nota de que BOS/CHoCH se evalúan también en la escala dominante (extender "se
     evalúa en ambas escalas" → tres escalas) y que la dominante **no** voltea por sí sola el bias
     headline hasta decisión de Fase 3.
   - Casos de prueba: incorporar los 3 del usuario (§8) como ocurrencias fechadas de la escala
     dominante.
2. **`WORKPLAN-MAESTRO-V2.md` / `docs/workplan/PINE-PLAN.md`**
   - Insertar el task en Sprint 1.2 como ítem "7B" (o 4B de Sprint 1.1, criterio del
     implementador): "Estructura BOS/CHoCH dominante (swing 50)". Marcar dependencia: después de
     T07, antes de T08 (EQH/EQL).
3. **`memory/ESTADO-ACTUAL.md`**
   - Actualizar estado tras completar; registrar el pendiente "bias dominante → Fase 3".
4. **ADR nuevo** (`docs/adrs/ADR-00X-escala-estructura-dominante.md`): la escala de swing es una
   decisión DOC-01. Documentar: problema, Opción C elegida vs B descartada, que es aditiva, y el
   pendiente de bias para Fase 3. Tag de git si aplica al cerrar.

---

## 8. Casos de prueba / criterios de validación (EURUSD H1, LuxAlgo)

Del usuario (lo que LuxAlgo marca y hoy NO se ve en nuestro Pine). El indicador debe reproducir
estas rupturas de escala dominante (nivel al pip, fecha de inicio = pivote roto, fecha de cierre =
vela de ruptura confirmada):

1. **CHoCH bajista ~1.17225** — inicia jue **2026-05-07 16:00**, se forma mié **2026-05-13 01:00**.
2. **BOS bajista ~1.15762** — inicia jue **2026-05-21 09:00**, se forma vie **2026-06-05 09:00**.
3. **CHoCH ~1.15777** — inicia mar **2026-06-09 09:00**, se forma jue **2026-06-11 15:00**.

**Comportamiento esperado** (como las líneas P/D de T07): la estructura sigue el precio y no marca
una nueva ruptura hasta que el precio rompe ese LL/HH; no aparece otra hasta el próximo HH/LL.

**Validación:** `smc-validator-agent` con screenshot del chart EURUSD H1, indicador dominante
activo, comparado contra LuxAlgo en el mismo chart. **Score ≥ 90.** Confirmar que los 3 casos
aparecen con su nivel/dirección/tipo correctos y que NO cambió ningún dibujo de T01–T07.

---

## 9. Ciclo de trabajo (protocolo por concepto)

1. **Plan:** ratificar Opción C con `smc-architect`; confirmar IN/OUT (§3). (No re-litigar.)
2. **check-rule:** actualizar `reglas-smc-ict.md` §1.1/§1.3/§1.4 + casos (§7.1) ANTES de codear.
3. **Implement:** inputs (§4.1) → estado (§4.2) → wiring detección byte-igual V/S (§4.3) → dibujo
   Visual (§4.4). Inyectar en TV y compilar.
4. **Compile 0/0** en los 3 archivos (Visual, Strategy, Library) — regla dura #7.
5. **check-core-sync:** `powershell -File scripts/check-core-sync.ps1` → debe seguir **OK con el
   mismo SHA** (no debió cambiar el CORE). Si cambia el SHA, algo se metió en el CORE por error →
   revertir esa parte.
6. **Validate ≥90:** `smc-validator-agent` con los 3 casos (§8) + verificación de no-regresión de
   T01–T07 (mismos dibujos previos presentes).
7. **Aprobación humana** (Freddy).
8. **Docs:** completar §7 (3 docs + ADR).
9. **Commit** Conventional + ID: `feat(pine-core): F1-S1.2-T07B estructura BOS/CHoCH dominante (swing 50)`.
10. **Cierre** vía `/smc-session-close` (ESTADO-ACTUAL + Sesion-022 + checkbox + sync-obsidian).

---

## 10. Definition of Done

- [ ] Opción C ratificada con `smc-architect` (sin scope nuevo).
- [ ] `reglas-smc-ict.md` §1.1/§1.3/§1.4 + 3 casos actualizados.
- [ ] Inputs + `structMajor` + `SMC_eventsMajor` + wiring detección (idéntico en Visual y Strategy).
- [ ] `f_drawStructureMajor` en Visual; capa visible y distinguible de swing/interno.
- [ ] Compila **0 errores / 0 warnings** en Visual, Strategy y Library.
- [ ] `check-core-sync` = **OK, mismo SHA** que antes del task (CORE intacto).
- [ ] Los 3 casos del usuario reproducidos vs LuxAlgo; `smc-validator-agent` ≥ 90.
- [ ] **No-regresión:** swings(5)/interno(3)/OB/FVG/P-D dibujan exactamente igual que antes.
- [ ] PINE-PLAN/WORKPLAN + ESTADO-ACTUAL actualizados; ADR escrito.
- [ ] Pendiente "bias dominante → Fase 3" registrado.
- [ ] Commit + cierre de sesión.

---

### Referencias
- Origen: `docs/pendiente-estructura-swing-grande.md`
- Spec: `docs/reglas-smc-ict.md` §1.1–§1.4
- CORE reutilizado (NO tocar): `pine/SMC-Library.pine` :184-238 (`SMC_Structure`,
  `f_setStructure*`, `f_detectStructure`), :144-145 (`f_detectSwings`)
- Patrón a copiar (wiring): `pine/SMC-Visual.pine` :459-535 (structSwing/structInternal)
- Referencia LuxAlgo: `pine/reference/LuxAlgo-SMC-base.pine` :409 (`getCurrentStructure`),
  :551-612 (`displayStructure`), :782-783 (llamadas 50 y 5)
- Decisión P/D relacionada: `docs/decisiones-pd-rango.md`
- ADR de escala: ADR-002 (congelación), nuevo ADR-00X (esta capa)
