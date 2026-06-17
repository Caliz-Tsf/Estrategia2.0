# Sesion-027 — 2026-06-17
> Cierre de sesión: F1-S1.3-T09 Pools de Liquidez (f_buildPools) **BUILD COMPLETO, VALIDADO (core-sync), COMMITEADO**

## Objetivo
Implementar T09 — Pools de Liquidez (Buyer Support Levels / Seller Supply Levels) en el CORE compartido Pine (Visual + Strategy). Clusterizar EQH/EQL (T08) + swings NO barridos para construir niveles de liquidez. Inicia Sprint 1.3 (Liquidez).

## Completado
✅ **F1-S1.3-T09 — BUILD COMPLETO**

### CORE (byte-idéntico Visual/Strategy, export en Library)
- **Función pura `f_buildPools(SMC_eqhl[], SMC_Swing[], float tolPrice, int minTouches) → SMC_Pool[]`**
  - Clusteriza EQH/EQL (array `SMC_eqhl` de T08) + swings NO barridos en niveles de liquidez.
  - Cada EQH/EQL aporta **2 touches** (doble techo/suelo, confirmado por T08).
  - Cada swing NO barrido (campo `swept=false`) aporta **1 touch**.
  - **Lado highs → BSL** (Buyer Support Level, dir `+1`).
  - **Lado lows → SSL** (Seller Supply Level, dir `−1`).
  - **Algoritmo clustering voraz:**
    1. Extrae todos los niveles (EQH/EQL + swings) en arrays separados (highs/lows).
    2. Ordena por precio (`array.sort_indices`).
    3. Agrupa niveles mientras `|nivel−media_cluster| <= tolPrice`.
    4. Cluster completo con `touches >= minTouches` → `SMC_Pool(level=promedio, touches=suma, barTime=más_reciente, swept=false)`.
  - **UDT:** `SMC_Pool` con campos `float level`, `int touches`, `int barTime`, `bool swept`.
  - **Inputs:**
    - `i_poolTol = 0.1 × ATR14` (tolerancia de clustering, predeterminado).
    - `i_minTouches = 2` (mínimo de touches para crear pool, reglas-smc-ict §3.1, congelado Fase 3 ADR-002).
  - **Array global:** `SMC_pools[]` (máx 50 pools por lado, BSL + SSL).
  - **Diseño PROPIO:** LuxAlgo no tiene clusterización de pools. Esta es la extensión del bot para liquidez (parte de Fase 1 Blueprint).

### Visual
- **Función `f_drawPools(SMC_pools[], bool showBSL, bool showSSL, color cBSL, color cSSL, string label)`**
  - **BSL (Buyer Support):** líneas **dashed naranja** horizontal, ancladas en `xloc.price` (level).
  - **SSL (Seller Supply):** líneas **dashed aqua** horizontal, ancladas en `xloc.price`.
  - **Etiquetas:** formato `"BSL ·2"` / `"SSL ·3"` (nombre + punto + número de touches), posicionadas a la derecha de la línea.
- **Grupo input:** `GRP_LIQ` con toggles `i_showPools`, `i_poolTol`, `i_minTouches`.
- **Panel:** nueva fila "Pools" mostrando contador total (BSL + SSL) en ventana visible.
- **Compila 0/0 en TV (EURUSD H1).**

### Strategy
- **Wiring detección:** idéntico a Visual (llamadas a `f_buildPools` en ambos contextos).
- **Array `SMC_pools`** poblado para uso en scoring (Sprint 2.1 — entrada/SL/TP sobre imanes de liquidez).
- **Flag `poolsDirty`** señala recálculo en cada vela (reusable para optimizaciones posteriores).
- **Sin dibujo** — la estrategia pasa datos al array; Visual dibuja.
- **Compila 0/0.**

### Verificaciones
- **check-core-sync.ps1:** OK. LIBRARY CORE = 503 líneas. SHA `2949a931757b9900` (Visual/Strategy idénticos).
- **Compila TV:** 0 errores / 0 warnings los 3 scripts (Visual, Strategy, Library import).
- **Validación formal ≥90:** **PENDIENTE.** El build compila y funciona visualmente (pools se generan, niveles/touches coherentes con §3.1). Validación exhaustiva de casos canónicos y contraejemplos (reglas-smc-ict §3.1) → diferido a Opus Max junto con mitigación.

### Bug Encontrado y Corregido (misma sesión)
**Descarte accidental de BSL en volcado de pools:**
- El código original usaba `f_pushPool` (FIFO con cap `MAX_POOLS=50`) para ambos BSL y SSL.
- Durante la reconstrucción de pools cada vela, los BSL se construían ANTES que los SSL.
- Resultado: los pools BSL se descartaban (desplazados del FIFO), solo sobrevivían ~2 BSL de ~60 SSL.
- **Impacto:** hubiera roto los sweeps de compra (T10) al inicio.
- **Fix:** cambio a volcado completo `array.push` sin cap. Todos los pools persisten en memoria.
- **Verificación visual:** balance BSL/SSL coherente en el chart.

## Decision CLAVE de la Sesion — Ciclo de Vida de Pools (DIFERIDO a Opus Max)

### Problema observado (usuario)
El gráfico se satura: se dibujan **TODOS** los pools, incluyendo los que el precio ya cruzó. Causa: T09 solo construye (campo `swept` siempre `false`) y reconstruye el set desde cero cada vela.

### Regla documental
§3.1 de reglas-smc-ict dice: *"Solo los niveles NO barridos son imanes de liquidez"*.

### Solución requerida
**MITIGACIÓN:** pools PERSISTENTES que se marcan barridos cuando el precio cruza su nivel y desaparecen del dibujo.
- **Propuesta A (descartada):** desaparecer en silencio.
- **Propuesta B (elegida por el usuario):** marcar barrido (fecha/hora/contexto), mostrar un marcador visual (p.ej., "✓" o línea atenuada), no desaparecer.

### Scope: unificación con T10 (Sweeps)
- T10 detecta cuando un pool es "swept" (precio lo cruza).
- El diseño de persistencia + sweep + marcador requiere:
  1. Cambiar `f_buildPools` de **stateless (reconstruye cada vela) → persistente** (arrays que persisten entre velas, se actualizan, no se reemplazan).
  2. Lógica de sweep en T10: cuando `close` traspasa `pool.level`, marcar `pool.swept = true` + registrar `pool.sweptTime`.
  3. Lógica de dibujo: pools vivos (swept=false) se dibujan normales; pools barridos (swept=true) se dibujan con marcador (Propuesta B).
  4. Limpieza: pools barridos desaparecen después de N velas (configurable).

### Handoff escrito
Documento: **`docs/planes/HANDOFF-OPUS-MAX-pools-mitigacion.md`** (este archivo, si no existe, se genera ahora).

Contiene:
1. Especificación del refactor (persistencia, swept, Propuesta B).
2. **REVISION INTEGRAL DE MITIGACION** de TODOS los conceptos restantes:
   - Cuáles necesitan ciclo de vida (Pools T09, IDM T17, Breaker T19, Flip T21, OTE/GP T22).
   - Cuáles NO (Sweep/Grab T10, KillZones T11, MSS T12, Displacement T13, Judas T14, Rejection T18, EMAs T15, FalseBreakout T16, Impulsive/Corrective T20).
   - Agrupados en 4 patrones P1–P4.
3. Plan de acción Opus Max: refactor T09, unificar T10, implementar mitigación completa.

### Modelo mental corregido (usuario observó)
**BSL (Buyer Support Level):** barrer arriba = vender (presión vendedora, opuesto a "soporte para compra").
**SSL (Seller Supply Level):** barrer abajo = comprar (presión compradora, opuesto a "resistencia para venta").

Los "colores mezclados arriba y abajo" del usuario NO son un bug de nomenclatura aparte = mismo síntoma que la saturación (sin mitigación, no se ve el patrón).

## Notas Fase 3 (no bloquean)
- **Ruido elevado (calibración):** defaults `i_poolTol=0.1 / i_minTouches=2` generan **muchos pools** (~60+ en EURUSD H1 ventana típica). Número bruto fiel a la densidad de EQH/EQL (T08, ruido conocido). La **mitigación (pendiente)** es la palanca grande disponible: con ciclo de vida, solo pools VIVOS (no barridos) se dibujan, dramáticamente menos ruido.
- **Calibración IS/OOS:** Fase 3 determinará si los defaults son suficientes o necesitan ajuste.

## Operativo TV MCP
- **Verificación:** EURUSD H1, 3 scripts compilados sin errores.
- **Visual confirmado:** pools se generan con niveles y touches coherentes a §3.1.
- **Slot SMC_Library guardado** (export CORE para importación posterior).

## Commits
- **139e1c1** `feat(pine-core): F1-S1.3-T09 pools de liquidez (f_buildPools) [build]` (2026-06-17)
  - Core: `f_buildPools`, UDT `SMC_Pool`, arrays `SMC_pools`, inputs `i_poolTol`/`i_minTouches`.
  - Visual/Strategy: wiring detección + `f_drawPools`.
  - Bug fix: volcado FIFO → array.push (sin cap).
  - check-core-sync: OK, 503 líneas, SHA `2949a931757b9900`.

## Pendiente (próxima sesion — Opus Max)
### Refactor y validación de T09 + T10 (unificados)
1. **Diseño persistente:** cambiar `f_buildPools` stateless → persistente.
2. **T10 Sweeps:** detectar cuando `close` traspasa `pool.level`, marcar `pool.swept = true`.
3. **Dibujo mejorado:** Propuesta B (marcador visual en pools barridos).
4. **Limpieza:** pools barridos desaparecen tras N velas.
5. **Revisión integral:** mitigación de concepto completo T09–T10 según patterns P1–P4.
6. **Validación formal ≥90** de T09 completo (casos §3.1 + contraejemplos).

**Handoff:** leer `docs/planes/HANDOFF-OPUS-MAX-pools-mitigacion.md`.

## Notas técnicas / educación
- **Clustering voraz:** algoritmo simple y determinista, apto para MQL5 (sin STL C++17).
- **Diseño PROPIO:** LuxAlgo no comercializa pools; esta es una extensión original.
- **Portabilidad:** `i_poolTol` / `i_minTouches` como inputs → multi-símbolo Fase 5.
- **UDT SMC_Pool:** simple (4 campos) → paridad MQL5 trivial (struct en .mqh).

---

*Sesion-027: Cierre 2026-06-17 · T09 BUILD ✅ · core-sync OK · bug fix (FIFO→push) · decision mitigación diferida Opus Max · handoff escrito · validación ≥90 pendiente · siguiente Sprint 1.3 continúa con T10 (Opus Max) · commit 139e1c1*
