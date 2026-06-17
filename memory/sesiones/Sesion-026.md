# Sesion-026 — 2026-06-16
> Cierre de sesión: F1-S1.2-T08 Equal Highs/Equal Lows (EQH/EQL) **COMPLETADO, VALIDADO, COMMITEADO**

## Objetivo
Implementar T08 — Equal Highs / Equal Lows (EQH/EQL) en el CORE compartido Pine (Visual + Strategy). Porta la detección de LuxAlgo (@DrawEqualHighLow, §2.4).

## Completado
✅ **F1-S1.2-T08 — COMPLETO**

### CORE (byte-idéntico Visual/Strategy, export en Library)
- **Función pura `f_detectEQHL(bool isHigh, float curPrice, int curBarIdx, int curBarTime, float prevPrice, float threshold) → SMC_Event`**
  - EQH (Equal High): comparación PIVOTE RECIÉN CONFIRMADO vs PIVOTE PREVIO MISMO TIPO (estado plano `prevEqHigh`). Si `|curPrice − prevPrice| <= threshold`, genera `SMC_Event` con `kind=KIND_EQH=44` (dirección `DIR_BEAR=−1` por ser EQH = presión alcista = reverso bajista).
  - EQL (Equal Low): lógica idéntica, `kind=KIND_EQL=45` (`DIR_BULL=+1`).
  - El pivote previo **SIEMPRE AVANZA** en el seguimiento (cf. algoritmo de LuxAlgo `getCurrentStructure` :419-448), no se queda estancado.
  - Anti-repaint: evaluación en `barstate.isconfirmed`; pivote anclado a `bar_index - i_eqlLength`.
- **Escalas separadas:** `i_eqlLength=3` (pivotes EQH/EQL) vs `swingLen=5` (estructura core) vs `i_pdSwingLen=50` (rango dominante P/D). La configuración por defecto de LuxAlgo (`equalHighsLowsLengthInput`) es 3 → portable.
- **Umbral:** `i_eqThreshold=0.1 × ATR14` (configurable). Ejemplo: umbral 0.009×ATR ≈ coincidencia dentro de 1 pip en EURUSD.
- **Array dedicado:** `SMC_eqhl` (máx 100 eventos). Separado de `SMC_events` (OB/FVG) → no contamina pooling de liquidez.
- **Conteo en panel:** nueva fila mostrando cantidad de EQH/EQL en ventana visible.

### Visual
- **Función `f_drawEQHL(SMC_eqhl[], i_showEQHL, i_eqThreshold, i_eqlLength)`**
  - Línea AZUL PUNTEADA conectando los dos pivotes "iguales" (ambos EQH y EQL en azul; opción usuario separada no requerida, diseño consistente).
  - Etiquetas **centradas por `bar_index`** midpoint de los dos pivotes:
    - EQH: etiqueta "EQH" por ENCIMA de la línea (posición `label.style_label_down` para dirección alcista dominante).
    - EQL: etiqueta "EQL" por DEBAJO de la línea (posición `label.style_label_up`).
  - Líneas ancladas en `xloc.bar_time` (ambos pivotes), etiquetas en `xloc.bar_index` (midpoint, sin gap de finde).
- **Grupo input:** `GRP_EQHL` con toggles `i_showEQHL`, `i_eqThreshold`, `i_eqlLength`.
- **Panel:** nueva fila "EQ H/L" mostrando conteo actual.
- **Compila 0/0 en TV (EURUSD H1).**

### Strategy
- **Wiring detección** idéntico a Visual (llamadas a `f_detectEQHL` en ambos contextos).
- **Array `SMC_eqhl`** poblado para uso en pools de liquidez (Sprint 2.1 — clustering EQH/EQL).
- **Etiqueta panel actualizada** a T08 + conteo EQH/EQL.
- **Sin dibujo** — la estrategia pasa puntos al array; Visual dibuja.
- **Compila 0/0.**

### Verificaciones
- **check-core-sync.ps1:** OK. LIBRARY CORE = 437 líneas. SHA `2c6b47b73fda01ff` (Visual/Strategy idénticos).
- **Compila TV:** 0 errores / 0 warnings los 3 scripts (Visual, Strategy, Library import).
- **smc-validator-agent:** **97/100 APROBADO** (3 puntos pendientes ajuste menor comentario).
  - Casos canónicos §2.4: **3/3 exactos**
    - EQH 2026-05-27 12:00 ≈ 2026-05-28 16:00 @~1.166 (diferencia 0.009×ATR14, umbral 0.1×ATR) ✅
    - EQL 2026-06-03 14:00 ≈ 06-03 22:00 @~1.159 (0.036×ATR) ✅
    - EQL 2026-06-08 18:00 ≈ 06-09 00:00 @~1.153 (0.086×ATR) ✅
  - Contraejemplo §2.4: 05-29 15:00 vs 05-28 16:00 (~1.7×ATR) **NO unidos** ✅ (correctamente rechazado).
  - −3 validador: comentario stale en `f_drawEQHL` (menciona "rojo/teal" para EQH/EQL vs implementación "azul" real). Corregido en sesión → repo=TV sin re-commit Pine.

### Trabajo visual adicional (mismo commit 0b63eda)
**Ajustes de dibujo pedidos por el usuario (iterados en vivo):**
- **Fix T07B BOS/CHoCH etiquetas dominantes (swing 50, pendiente de S022):** re-compilado código del repo que ya tenía la corrección (etiqueta ALCISTA con `style_label_down` = encima; BAJISTA con `style_label_up` = debajo). Confirmado en chart por usuario.
- **Colores (ajuste visual, solo dibujo):**
  - EQH/EQL → **AZUL** (ambos, sin distinción rojo/teal).
  - OB alcista → **verde oscuro** `color.rgb(0,100,0)` semitransparente.
  - OB bajista → **rojo oscuro** `color.rgb(120,20,20)` semitransparente (distinto del teal/rojo de estructura).
  - FVG sin cambios (lima alcista / naranja bajista).
  - Nombres de zonas (OB, FVG) → **centrados** en la caja (`label.style_label_center` midpoint H/V), antes colgaban a la izquierda.
- **Jerarquía visual final:**
  - Estructura swing (5) → teal/rojo (línea 2px).
  - Estructura dominante (50) → teal/rojo (línea 3px, apenas visible para evitar ruido).
  - OBs → verde oscuro / rojo oscuro cajas.
  - FVGs → lima / naranja cajas.
  - EQH/EQL → azul líneas punteadas.
  - P/D/EQ → líneas roja/verde/gris (trailing).

## Notas operativas / Decisiones Fase 3
- **Ruido EQH/EQL elevado (anotado, NO bloquea):** escala length=3 con umbral 0.1×ATR genera MUCHOS eventos. Array `SMC_eqhl` alcanza el cap MAX_EVENTS=100; chart toca límite 500 labels (max_labels_count). Es fiel al comportamiento de LuxAlgo default (razón por la que su modo "Present" solo muestra el evento más reciente). Calibración del ruido y decisión sobre densidad aceptable = tarea de Fase 3 (backtesting IS/OOS); posibles mitidas: (1) separar arrays por TF → varias límites; (2) subir caps; (3) modo "solo último evento" si el ruido estorba visualmente.
- **EQH/EQL → pools de liquidez (próxima tarea):** en Sprint 2.1, `f_buildPools()` clusterizará los eventos de `SMC_eqhl` (junto con swings no barridos) para crear niveles de liquidez. En T08 solo se detecta, almacena y dibuja.

## Operativo TV MCP
- **Cambio de estudio en compilación:** al invocar `pine_smart_compile` sobre Strategy/Library, el estudio del chart cambió temporalmente a esos scripts (comportamiento esperado). Al terminar validaciones, se inyectó + guardó el Visual nuevamente para dejarlo como estudio correcto en el chart.
- **Confirmación:** estudio actual = "SMC Engine — Visual" + tab "SMC_Library" visible. Chart mostrando los 3 casos canónicos + ajustes visuales aprobados.

## Commits
- **0b63eda** `feat(pine): F1-S1.2-T08 deteccion EQH/EQL (f_detectEQHL) + ajustes visuales` (2026-06-16)
  - Core: `f_detectEQHL`, `KIND_EQH=44`, `KIND_EQL=45`, array `SMC_eqhl`, estados planos `prevEqHigh`/`prevEqLow`.
  - Visual/Strategy: wiring detección + `f_drawEQHL`.
  - Ajustes visuales: colores OB/EQH/EQL, posición etiquetas (centradas), T07B BOS/CHoCH fix.
  - check-core-sync: OK, 437 líneas, SHA `2c6b47b73fda01ff`.

## Pendiente (próxima tarea)
**T09 — siguiente concepto del sprint 1.2 (consultar PINE-PLAN §7 / WORKPLAN para orden exacto).**
Candidatos según el orden:
- **OTE / Golden Pocket** (§2.5 reglas-smc-ict) — zonas fib tras impulso.
- O el siguiente elemento de la lista de estructura/liquidez/contexto del workplan.

**Nota:** el doc-updater debe consultar PINE-PLAN y WORKPLAN-MAESTRO-V2.md §3 para determinar el concepto exacto de T09 (NO asumir aquí; será determinado al actualizar checkboxes).

## Notas técnicas / educación
- **Anti-repaint garantizado:** `barstate.isconfirmed` guard en detección. Pivote confirmado en t−N (no en vivo).
- **Portabilidad:** escala 3 con ATR relativo (factor 0.1) = fácilmente portable a otros símbolos (MQL5, otros pares en Fase 5).
- **Paridad LuxAlgo:** el algoritmo de "pivote previo siempre avanza" viene de LuxAlgo `:419-448` (getCurrentStructure), traducido fielmente.
- **Límites:** MAX_EVENTS=100 está documentado; posible ajuste Fase 3 si el ruido no es aceptable. Decisión de calibración = criterio Freddy con Strategy Tester OOS (validación real del sistema, no asunción).

---

*Sesion-026: Cierre 2026-06-16 · T08 COMPLETO ✅ · check-core-sync OK · validación 97/100 ✅ · commit 0b63eda · ajustes visuales aprobados · siguiente T09*
