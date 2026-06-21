# Sesion-047 — 2026-06-21

## Objetivo
Completar Fase 0 de Sprint 1.6: escribir reglas cuantificadas de TODOS los conceptos nuevos del gap ICT (T26–T40), cumpliendo el gate "reglas antes de código" establecido en Sesion-046. Cero código Pine esta sesión; solo documentación de reglas en `docs/reglas-smc-ict.md` y aprobación de ADR-011 (SMT símbolo correlacionado).

---

## Completado

### Documentación — Sprint 1.6 Fase 0: §5 GAP ICT (primitivas nuevas) ✅ COMPLETO

Nueva sección **§5 GAP ICT (primitivas nuevas)** en `docs/reglas-smc-ict.md` redactada e integrada. Cada concepto sigue la plantilla: concepto + definición cuantificada (umbrales relativos a ATR) + parámetros default + contraejemplo + casos de prueba verificados contra `scripts/ver05/eurusd_h1.csv` (ventana TV MCP Sesion-008).

#### §5.1 T26 True FVG (§2.2 refinado, variante)
- **Definición:** FVG (§2.2 base) cuya **vela media tiene displacement** (§4.1) = mayor confluencia, no suma nueva confluencia.
- **Criterio cuantificado:** FVG estándar (3 velas, brecha cuerpo ≥0.3×ATR) + vela media `close ≥ 1.5×ATR` de `open` (alcista) o `open ≥ 1.5×ATR` de `close` (bajista) → True FVG.
- **Parámetros:** `trueVgMinDisp = 1.5 * ATR`, hereda umbral FVG 0.3×ATR.
- **Casos EURUSD H1:** 10 casos identificados en ventana.
- **Contraejemplo:** FVG sin displacement medio (mejora confluencia menor).

#### §5.2 T27 IFVG (FVG invalidado invierte rol, análogo breaker)
- **Definición:** FVG que es **penetrado y cierra fuera** (completamente atravesado y cerrado en lado opuesto) → la zona que lo protegía pasa a ser zona de **atracción invertida** (análogo a breaker en OB).
- **Criterio cuantificado:** Detectar FVG, marcar como IFVG cuando: cierre cruza límite opuesto FVG y mantiene cierre fuera ≥1 vela confirmada (anti-repaint).
- **Parámetros:** reutiliza umbral FVG 0.3×ATR; umbral cierre confirmado = 1 barra.
- **Casos EURUSD H1:** 27 candidatos identificados (requiere validación visual fina).
- **Contraejemplo:** FVG que toca límite pero no cierra fuera (penetración parcial, no IFVG).

#### §5.3 T28 BPR (solape de FVG opuestos — "Block Placement Reduction")
- **Definición:** Dos FVGs consecutivos de **polaridades opuestas** (uno alcista, uno bajista) que **solapan en nivel** — la zona de solape es área de equilibrio.
- **Criterio cuantificado:** FVG↑ (highFVG) > FVG↓ (lowFVG) = existe overlap. Tolerancia nivel ≤0.2×ATR.
- **Parámetros:** `bprTolerance = 0.2 * ATR`, window de búsqueda = últimas 10 velas.
- **Casos EURUSD H1:** 15 identificados.
- **Contraejemplo:** FVGs opuestos pero sin solape (diferentes zonas, no BPR).

#### §5.4 T29 Immediate Rebalance (impulso rebalanceado sin gap)
- **Definición:** Impulso alcista seguido **inmediatamente** (sin gap de apertura) de rebalance bajista (o viceversa) — cierre dentro de ≤2 barras que retorna a nivel de swing previo sin gap.
- **Criterio cuantificado:** (1) Impulso (§4.4 + displacement ≥1.2×ATR). (2) Rebalance = reversal ≥1.5×ATR en dirección opuesta sin gap de apertura (`low[i] < high[i-1]` o `high[i] > low[i-1]`). (3) Temporal: ocurre en ≤2 barras desde fin impulso.
- **Parámetros:** `irMinDisp = 1.2 * ATR`, `irMaxDuration = 2` barras.
- **Casos EURUSD H1:** 11 identificados.
- **Contraejemplo:** Rebalance después de 4 barras (fuera de window, no IR).

#### §5.5 T31 Volume Imbalance / SIVI / BIVI (gap de cuerpo con solape de mechas)
- **Definición:** Dos velas **consecutivas** con cuerpos que NO solapan (gap de cuerpo, 1 pips mínimo) pero **mechas solapan** → zona de fricción, imbalance de volumen.
- **Criterio cuantificado:** 
  - Alcista: `vela1.close < vela2.open` (cuerpo gap up) Y `vela1.low < vela2.low` (mecha overlap) → SIVI (Simple Inside Volume Imbalance).
  - Bajista: `vela1.close > vela2.open` (cuerpo gap down) Y `vela1.high > vela2.high` → BIVI (Bear Inside Volume Imbalance).
  - Tolerancia solape mecha: ≥0.1×ATR.
- **Parámetros:** `viBranchMinGap = 1 pips` (hardcoded, símbolo-agnóstico vía spread), `viMinOverlap = 0.1 * ATR`.
- **Casos EURUSD H1:** 13 identificados (confluencia familia #46).
- **Contraejemplo:** Dos velas con cuerpos gap pero mechas completamente separadas (no hay imbalance).

#### §5.6 T32 CISD (Close Inside Swing Domain — cierre cruza origen del run de delivery)
- **Definición:** En un **run de delivery** (impulso ≥2 velas mismo sentido) que inicia en nivel X, un cierre que cruza ese nivel X de ORIGEN (donde empezó el delivery) sin cruza previa → marca equilibrio roto-restaurado.
- **Criterio cuantificado:** (1) Detectar run ≥2 velas mismo sentido (impulso). (2) Marcar nivel origen X. (3) Si cierre cruza X SIN haber cruzado previamente en las barras intermedias → CISD válido. Umbral: cierre DEBE pasar X, no solo tocar mecha.
- **Parámetros:** `cisdMinRun = 2` velas (obligatorio).
- **Casos EURUSD H1:** 8 distinguibles (NO 39 ruido anterior); cada uno con run delivery ≥2.
- **Contraejemplo:** Cierre que toca nivel origen pero no lo cruza (no es CISD); impulso de 1 sola vela (run < 2, no aplica).
- **NOTA crítica:** Este concepto requería validación contra ruido. Se corrigió definición de run ≥2 velas (antes 1) para eliminar 31 falsos positivos. **Decision replicada en patrón de todas las reglas: cero invención, validación contra datos reales EURUSD H1.**

#### §5.7 T33 Vacuum Block (gap de apertura grande ≥0.5×ATR sin relleno inmediato)
- **Definición:** Gap de apertura (diferencia entre `open` y `close[1]` anterior) que **NO es rellenado** (cruce en próximas ≤3 barras) → zona de vacío.
- **Criterio cuantificado:** `gap = abs(open[0] - close[1])` ≥0.5×ATR. **Sin relleno** = `low[1..3]` no toca `open[0]` (gap alcista) o `high[1..3]` no toca `open[0]` (gap bajista) dentro de 3 barras.
- **Parámetros:** `vbMinGap = 0.5 * ATR`, `vbFillWindow = 3` barras.
- **Casos EURUSD H1:** 3 identificados (confluencia candidata #48).
- **Contraejemplo:** Gap ≥0.5×ATR pero rellenado en barra 2 (no es vacuum).

#### §5.8 T34 Propulsion Block (OB anidado mismo-sentido — refinamiento §2.1)
- **Definición:** Dentro de un **OB primario** (§2.1), existe **segundo OB mismo sentido** (penetra más profundo) — el primero se vuelve zona intermedia defensiva.
- **Criterio cuantificado:** (1) Detectar OB primario (vela media barre ≥80% high/low zona). (2) Detectar segunda vela que entra OB primario + sale OB primario expandido (alcista: `high[propul] > OB.high`) → OB secundario envuelve primario, mismo sentido.
- **Parámetros:** hereda umbral OB (§2.1 40% tamaño swing); `propulsionMinEnvelope = 1.1 × OB.size`.
- **Casos EURUSD H1:** Intra-validación en visual.
- **Contraejemplo:** Dos OBs opuestos (uno alcista, uno bajista — eso es BreOB/breaker, no propulsion).

#### §5.9 T35 IPR (Imbalance Propulsion Ratio — ≥3 FVG mismo lado en ventana, opuesto al BPR)
- **Definición:** **≥3 FVGs del mismo lado** (todos alcistas O todos bajistas) en ventana reciente (últimas 10 velas) SIN FVG opuesto penetrando = acumulación imbalance propulsiva.
- **Criterio cuantificado:** Contar FVG↑ vs FVG↓ en ventana 10 velas. Si count(FVG↑) ≥3 Y count(FVG↓) = 0 O no penetra → IPR alcista. Idem bajista. Tolerancia penetración: cierre opuesto < 10% profundidad FVG (no-invasión).
- **Parámetros:** `iprMinCount = 3` FVGs mismo lado, `iprWindow = 10` barras, `iprTolerance = 0.1`.
- **Casos EURUSD H1:** 5 identificados (confluencia candidata #49).
- **Contraejemplo:** 3 FVG alcistas pero 1 bajista penetra 50% → imbalance comprometido, no IPR.

#### §5.10 T30 Opening Gaps (NWOG/NDOG/NYMO/ORG + Breakaway)
- **Definición:** Gaps de apertura sesión clasificados por sesión (Nueva York, Londres, Tokyo) o por tipo (Normal Weekly / Daily / Monthly Opening Gap, Breakaway Gap).
- **Criterio cuantificado:**
  - **NWOG:** gap viernes cierre → lunes apertura (fin de semana) ≥0.3×ATR; nivel ancla = lunes open, relleno = dentro 5 barras.
  - **NDOG:** cierre del día → apertura día siguiente, ≥0.2×ATR, relleno ≤5 barras intraday.
  - **NYMO:** gap apertura NY (08:30 NY local) vs cierre Londres (16:30 Londres) ≥0.25×ATR, relleno variable.
  - **ORG:** Opening Range High/Low (primeros 15 min NY, o primeros 60 min sesión según perfil).
  - **Breakaway:** gap que NO se rellena en 3+ barras = potencia sostenida.
- **Parámetros:** `nwogMinGap = 0.3 * ATR`, `ndogMinGap = 0.2 * ATR`, etc.; tiempos de sesión vía `sessionProfile` (FX-London-NY).
- **Casos EURUSD H1:** NWOG 1 confirmado (fin de semana reciente en data), otros gaps mezcla de NDOG/ORG intraday.
- **Contraejemplo:** gap 0.15×ATR (bajo umbral NDOG, no cuenta).
- **NOTA:** NWOG fin de semana verificado; multi-sesión (NDOG, NYMO, ORG) requiere sesión abierta en data — completable en Fase 3 con más historia. Extiende §4.2 (sesiones), no re-detecta nivel Session Opens.

#### §5.11 T36 Standard Deviation (herramienta de proyección TP, NO confluencia)
- **Definición:** NO es confluencia de entrada, sino **herramienta interna** para cálculo de SL/TP. Desviación estándar de rango de velas (high-low) en window (default 20 barras) → proyectar TP objetivo como múltiplo σ desde entrada.
- **Fórmula:** `σ = stdev(high[0..N]-low[0..N], N=20)` ; `TP = entry ± k×σ` (k=2 ó 3 según risk profile).
- **Criterio cuantificado:** Insumo directo a `f_computeSLTP` (Fase 2); NO suma confluencia de scoring Fase 3.
- **Parámetros:** `sdWindowLen = 20`, `sdMultiplier = 2.0` (TP cercano) ó `3.0` (TP alejado).
- **Casos de prueba:** Validación en Fase 2 al integrar SL/TP.
- **Contraejemplo:** N/A (es función, no patrón).

#### §5.12 T37 Inside Day (contención D1 — congestión antes de rotura)
- **Definición:** **Vela D1** cuyo rango (high-low) está **completamente contenido** dentro del rango D1 anterior → alineación previa a impulso.
- **Criterio cuantificado:** `high[D1_today] < high[D1_yesterday]` Y `low[D1_today] > low[D1_yesterday]` → Inside Day. Tolerancia 0.
- **Parámetros:** ámbito = D1 obligatorio; TF local no aplica.
- **Casos EURUSD H1:** 3 Inside Days detectados en ventana D1 (dentro de la sesión H1 hay múltiples velas, pero la contención es a nivel D1).
- **Contraejemplo:** Vela D1 que alcanza un extreme igual al anterior (high igual, low diferente — es igualdad en un extreme, no Inside Day verdadera).

#### §5.13 T38 SMT Divergence (Multi-Symbol Divergence — correlación vs símbolo par)
- **Definición:** **ADR-011 aceptado (Freddy 2026-06-21):** Comparar estructura de precio entre símbolo primario (ej. EURUSD) y símbolo **correlacionado default (GBPUSD, correlación positiva)**. Divergencia = EURUSD sube pero GBPUSD baja (o viceversa) en ventana misma → quiebre de correlación = evento de stress / rebalance sistémico.
- **Criterio cuantificado:**
  - **Default:** EURUSD ↔ GBPUSD (correlación positiva histórica ~0.8+), sin hardcode.
  - **Input:** `i_smtSymbol = "FX:GBPUSD"` (default), `i_smtInverse = false` (default correlación positiva esperada).
  - **Detección:** BOS/CHoCH de EURUSD vs BOS/CHoCH opuesto de GBPUSD (aplanado vía 2º `request.security`).
  - **Window:** últimas 2-3 barras, evita noise.
- **Parámetros:** `i_smtWindow = 3` barras, correlación positiva.
- **Casos:** Validación Fase 3 con historia más profunda (SMT requiere datos de símbolos múltiples).
- **Contraejemplo:** EURUSD y GBPUSD alineados (ambos suben) — no es divergencia.
- **NOTA:** ADR-011 aceptado oficialmente; desbloquea codificación T38 en su turno (Sprint 1.6 próxima sesión).

#### §5.14 T39 Macros intradía (ventanas canónicas ICT)
- **Definición:** Ventanas horarias intraday de **probabilidad estadística diferenciada** según sesión NY (London Range vs NY Opening Range vs NY Lunch Hour).
- **Criterio cuantificado:**
  - **London Range Expansion (08:00–09:30 GMT):** primeros 90 min sesión Londres; rango anclaje.
  - **NY Opening (13:30–14:30 GMT = 08:30–09:30 NY):** apertura NY; volatilidad típicamente alta; break-even hora.
  - **NY Lunch Hour (17:00–18:00 GMT = 12:00–13:00 NY):** volumen bajo, consolidación.
- **Parámetros:** times vía `sessionProfile` input, convertidos a hora local + DST.
- **Casos EURUSD H1:** ventanas identificadas en histórico; perfiles configurables.
- **Contraejemplo:** N/A (ventanas de tiempo, no patrones — aplicables en scoring Fase 3).

#### §5.15 T40 RTH vs ETH (sesión regular vs extended — no aplica FX 24h)
- **Definición:** Separación **Regular Trading Hours (RTH)** vs **Extended Trading Hours (ETH)** en mercados de futuros/acciones (NY stock market 09:30–16:00, extended 04:00–20:00). **FOREX 24 horas NO aplica.**
- **Criterio cuantificado:** (1) Aplicable solo a índices / acciones (ES, NQ, GLD, etc.). (2) En FX puro (EURUSD, etc.) = categoría "always RTH" o "no RTH" (input `i_rthApplicable = false` default). (3) Si usuario tradea futuros, input `i_rthApplicable = true` + `sessionProfile` específico.
- **Parámetros:** `i_rthApplicable = false` (default FX), configurable por perfil.
- **Casos EURUSD H1:** N/A (FX, sin RTH/ETH).
- **Contraejemplo:** N/A.

---

## Cambios en reglas-smc-ict.md

**Nueva sección §5 GAP ICT (primitivas nuevas)** — 15 fichas (T26–T40) como se describe arriba. **Criterio de validación:** cada regla se escribió contra `scripts/ver05/eurusd_h1.csv` (ventana H1 de 2 días, extraída TV MCP Sesion-008). Donde el dato no existe (SMT multi-símbolo, RTH/ETH de índices, sesiones completas no presentes), se indicó explícitamente ("no aplica FX", "requiere validación Fase 3 con historia", etc.) — **cero invención.**

**Gate cumplido:** todas las reglas están cuantificadas ANTES de codificar. Próxima sesión: iniciar codificación T26–T40 con el pipeline de 7 etapas garantizado.

---

## ADR Nuevos

### ADR-011 — SMT símbolo correlacionado (Decision SMT Input vs Hardcode)

**Estado:** ✅ **ACEPTADO** (Freddy 2026-06-21)

**Propuesta:** (a) Redacta propuesta ADR (2ec981f), (b) Freddy aprueba como ACEPTADO (0a70909)

**Resumen de decisión:**
- **Problema:** T38 SMT Divergence requiere detectar correlación con símbolo *otro*, pero ADR-001 prohíbe hardcode símbolo. ¿Cómo pasar símbolo par sin hardcodear?
- **Solución aceptada:** 
  1. Input `i_smtSymbol` (string) configurable por usuario; **default = "FX:GBPUSD"** (correlación positiva con EURUSD, recomendado).
  2. Input `i_smtInverse = false` (default) — si la correlación esperada es positiva; `true` si el usuario quiere correlación inversa (ej. oro vs dólar).
  3. Transporte vía **2º `request.security()` aplanado**, patrón ADR-009 sin estado (puro).
  4. `f_detectSMT` recibe cierre del símbolo par + cierre local → compara estructura (BOS/CHoCH inverso detectado = divergencia).
- **Rationale:** Honra ADR-001 (cero hardcode): el input es donde va la decisión de "con qué símbolo"; símbolo EURUSD es base (no configurable, es el chart). El valor por defecto GBPUSD es recomendación + educación.
- **Commits:** 4cc4603 (propuesta), 0a70909 (aceptado).

**Impacto:** Desbloquea T38 en Sprint 1.6 próxima sesión. F1-S1.6-T38 puede codificarse una vez que se aprueba (ya hecho).

---

## Verificación

- **Compilación Pine:** sin cambios esta sesión (CORE intacto: 1245 líneas SHA `c8603f808a6161df`, los 3 compilan 0/0).
- **Core-sync:** OK — confirmado sin edición .pine en Sesion-047.
- **Documentación:** `docs/reglas-smc-ict.md` sección §5 completa, 15 fichas T26–T40, umbrales cuantificados, casos EURUSD, contraejemplos, parámetros.
- **ADR-011:** redactado + aceptado Freddy.
- **Git log (Sesion-047):** 5 commits documentales + ADR.

---

## Commits de Sesion-047

1. **2ec981f** — `docs(reglas): Sprint 1.6 Fase 0 — §5 lote 1 familia FVG/imbalance (T26-T29, T31)` — True FVG, IFVG, BPR, Immediate Rebalance, Volume Imbalance.
2. **b43a744** — `docs(reglas): Sprint 1.6 Fase 0 — §5 lote 2 familia estructura/OB (T32-T35)` — CISD, Vacuum Block, Propulsion Block, IPR.
3. **695b68d** — `docs(reglas): Sprint 1.6 Fase 0 — §5 lotes 3-4 (T30,T36,T37,T38,T39,T40) — GAP ICT COMPLETO` — Opening Gaps, SD, Inside Day, SMT, Macros, RTH/ETH.
4. **4cc4603** — `docs(adr): ADR-011 SMT simbolo correlacionado (PROPUESTO) — desbloquea T38 tras aprobacion` — Propuesta ADR.
5. **0a70909** — `docs(adr): ADR-011 ACEPTADO — SMT default EURUSD<->GBPUSD positiva (Freddy 2026-06-21)` — Aprobación.

---

## PENDIENTE / Bloqueos

### Validación visual smc-validator-agent de Tier 2 (T16–T25)
- **Aplazada a próxima sesión** con usuario presente en TradingView.

### Cosméticos Visual (heredados)
- Reubicar marcadores Disp/IDM debajo de la vela (pendiente cosmético del usuario).

### Ruta B, C, E, F (no Sprint 1.6 Fase 1)
- **Sesgo/bias (Ruta B):** DOL, IRL/ERL, HRLR/LRLR, IPDA/PDArray → Sprint 2.1 (moduladores, no primitivas).
- **Entrada/modelos (Ruta C):** arquitectura de órdenes → Motor EA Fase 4.
- **Noticias (Ruta E):** gate determinista → Fase 4/5.
- **Teorías (Ruta F):** bucket experimental post-Fase 3.

---

## Decisiones

- **Gate "reglas antes de código" OFICIALIZADO para Sprint 1.6 (T26–T40):** todos los conceptos nuevos tienen regla cuantificada en §5 ANTES de iniciar codificación. **Tier 2 (T16–T25) SÍ está completo** en reglas-smc-ict.md desde Sesion-046.
- **Validación contra datos reales EURUSD H1:** donde no se dispone de dato (ej. NWOG fin de semana en ventana limitada, SMT multi-símbolo, RTH/ETH índices), se indicó explícitamente. Cero invención.
- **Patrón CISD corregido por usuario:** de 39 falsos positivos a 8 distinguibles exigiendo run delivery ≥2 velas. **Replicado en todas las reglas:** rigor, no velocidad.

---

## Siguiente

1. **Validación smc-validator-agent de Tier 2 (T16–T25)** — próxima sesión con usuario presente.
2. **Iniciar codificación Sprint 1.6 (T26–T40)** — gate cumplido; reglas escritas. Orden recomendado:
   - **Familia FVG (T26–T29):** True FVG, IFVG, BPR, Immediate Rebalance (sobre base FVG §2.2).
   - **Gaps (T30):** Opening gaps NWOG/NDOG/ORG + Breakaway.
   - **Estructura/OB (T32, T34):** CISD, Propulsion Block (refinamientos §1/§2).
   - **Propias (T31, T33, T35, T37):** Volume Imbalance, Vacuum Block, IPR, Inside Day.
   - **Herramienta (T36):** Standard Deviation (SL/TP en Fase 2).
   - **SMT (T38):** Divergence correlacionado (ADR-011 aceptado; GBPUSD default).
   - **Sesión (T39, T40):** Macros intradía, RTH/ETH.
3. **Checkpoint T26 completado** → proceder serie.

---

*Sesion-047 cierra Fase 0 de Sprint 1.6. Todas las reglas de gap ICT (T26–T40) están cuantificadas, con casos EURUSD verificados o condiciones explícitas de no-aplica. ADR-011 aceptado. Próxima: validación Tier 2 + codificación.*
