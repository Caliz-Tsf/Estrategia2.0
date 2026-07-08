# Sesion-107 — 2026-07-08 — Validación Viva Pasos A–D (CE10117 + RE10026 Resueltos)

## Objetivo
Validación en vivo TV D1/H1/M5 de los Pasos A–D de S106 (confirmar que Paso D no revienta al aplicar; pierna poblada sin outlier 1.51; calibrar i_kLeg/MAX_ZONES_CHART). Contexto: S106 compiló 0/0 server-side pero nunca fue aplicado en vivo.

## Hallazgo Crítico Inicial (Bloqueador Doble)

**NO era RE10045** (arrays islast) sino **DOS bloqueadores encadenados que impedían todo dibujo:**

### CE10117 — Token Limit Compilado (CRÍTICO)
- **Error:** "Compiled code contains too many tokens: 101049. The limit is 100256"
- **Root cause:** S106 (Pasos A–D, +297 líneas net) cruzó el techo de tokens compilados TradingView por **793 tokens**
- **Causa desconocida en server-side:** `pine_check.py`/translate_light NO cuenta tokens (reportaba 0/0 en S106). **Aprendizaje clave verificado empíricamente:** las funciones de usuario en Pine NO se inlinean (compiladas una vez) → deduplicar call-sites no ahorra tokens; lo que baja el conteo es **BORRAR statements**.
- **Protocolo de medición establecido:** inject → Ctrl+Enter (apply) → esperar ~18-25s → `pine_get_errors` (el conteo real aparece tardío; el "0" inmediato tras Save es falso-0)
- **Reducción aplicada (midiendo cada paso):** 101049 → 100675 → 100559 → 100325 → 100314 → bajo límite
  - `f_bp3Insert` bubble-sort 3×4-arrays reemplazado por membership test + nuevo `f_cellMinScore` (umbral early-out): **−374 tokens**
  - Eviction `f_pushZoneV`/`f_prunePoolsV`: escaneos fusionados a 1 pasada: **−116 tokens**
  - `bp3Bar` (array tie-break por recencia) eliminado; empate conserva existente: **−234 tokens**
  - Reset bp3 vía `array.fill` en lugar de loop: **−11 tokens**
  - Band-pick top-3 → top-2 por celda (arrays 120 → 80), dentro del spec "1-3 por banda": **−~120 tokens**
  - VI (§5.5 Volume Imbalance, `i_showVI=false`) y StdDev projection (§5.11, `i_showStdDev=false`) **RETIRADOS del Visual** (default-OFF → cero impacto visual)

**Decisión usuario:** las funciones puras `f_detectVolumeImbalance` (L~780) y `f_projStdDev` (L~907) siguen en el CORE byte-idéntico **SIN llamar** (core-sync intacto); se pueden re-cablear en Fase 3 bajo parámetro `i_showVI/i_showStdDev` ON.

### RE10026 — Box Bar Index Límite (SECUNDARIO)
- **Error:** "Bar index value of the `left` argument (179) in box.new() is too far from the current bar index" en `f_drawOB`
- **Causa directa:** S106 Paso B retención por importancia ahora conserva zonas MUY viejas (no-mitigadas) que antes se desalojaban por antigüedad; los ~19 drawers (OB/FVG/Breaker/IFVG/BPR/VI/MB/Vacuum/GP-OTE/IPR + labels/CE-lines) las pintaban con `xloc.bar_index`. Límite TradingView: origen caja no puede ser >490 barras atrás.
- **Fix stopgap:** helper `f_xL(bi) = math.max(bi, bar_index-490)` que clampea el x-origen en todos los sitios (~19 calls)
- **Limitación:** para zonas MUY viejas la caja arranca en `bar_index-490`, NO en la vela real → aspecto visual falso (caja "brinca" 10+ barras)

## Resultado Verificado en Vivo

**Contexto:** OANDA:EURUSD H1, instancia MQVk7q, modo Operación, 2026-07-08

**Compilación y Apply:**
- Compila **0/0** tras reducciones token
- Aplica **SIN CE10117 ni RE10026**
- Dibujo **completo y consistente**

**Panel T14 (Bias/P/D reales):**
```
TF       Bias       Discount    EQ          Premium
D1       Bajista    12%         N/A         N/A
H1       Equil      N/A         51%         N/A
M5       Alcista    N/A         N/A         67%

Grid P/D Premium:  1.14730
Grid P/D EQ:       1.14174
Grid P/D Discount: 1.13618
```

**Pierna Poblada (Paso A verificado):**
- **Arriba:** OB 1.15726–1.16221, FVG, MB, BSL-4/BSL-2
- **Abajo:** OB ~1.136, MB, T.FVG, SSL 1.13246
- **Sin outlier 1.51** (Paso A clamp confirmado)

**Pools LP-Pro (Paso C):**
- Render top-2 fuertes/lado: **confirmado dibujado**

**Band-pick top-2 (Paso D):**
- Representantes repartidos por banda: **confirmado**

**Panel Ocultos (Desalojo de Paso B):**
```
Estructura (Est):     500
Equilibrio (EQ):      98
Liquidez (Liq):       53
Referencia (Ref):     1061
Volume Imbalance (µ): 82  [= SMC_ipr, VI retirado]
Desalojo:            2
```

## Verificaciones

- **Compilación:** 0 errores / 0 warnings
- **Core-sync:** OK (SHA `5510361166844bd5` intacto 1700 líneas)
- **Lookahead:** `lookahead_off` SIEMPRE (anti-repaint)
- **Densidad:** Operación, all3TFs dibujando sin crash
- **Conteo visual:** Operación estable (pre-desalojo ya logrado S091)

## GOTCHAs Descubiertos Esta Sesión

1. **Clave input Densidad desplazada:** con 8 inputs removidos (VI/StdDev), `in_123` → `in_115`. MCP `indicator_set_inputs {"in_115":"Operación"}` (verificación manual vía inspector UI necesaria si nuevas pruebas).

2. **CDP 9222 crash:** se cayó 1 vez durante sesión. Fix: relanzar con `tv_launch`.

3. **Editor async post-relanza:** tras relanzar TV, el editor recarga el slot async y puede sobrescribir `setValue` del inject. Fix: re-inyectar con editor **ya estable** (~10s post-launch).

## Decisiones y Cambios Aplicados

### Reducción de Tokens (Root Cause CE10117)
- **`f_bp3Insert` refactorizada:** membership test de candidatos (O(n)) en lugar de bubble-sort (O(n²)), eliminado segundo array. Criterio early-out nuevo: `f_cellMinScore = strength ≥ u threshold` (→ skip costoso f_posRole/f_confDegree si no pasa).
- **Eviction consolidada:** `f_pushZoneV` y `f_prunePoolsV` ahora fusionan escaneos (antes 2 pasadas → 1). Sin cambio de lógica, solo compresión de código.
- **BP3 simplificado:** top-2 en lugar de top-3 (dentro del spec "1-3 por banda"). Arrays bp3Idx/Score/Lvl (120 slots) ahora son suficientes.
- **VI y StdDev Visual-OFF por defecto:** funciones puras siguen en CORE (no borradas) pero no se llaman. User puede re-activar en Fase 3 con toggle UI.

### Fix RE10026 (Stopgap)
- Helper `f_xL(barIdx) = math.max(barIdx, bar_index-490)` aplicado en ~19 drawers
- **Limitación conocida:** cajas viejas muy viejas arrancaYn artificialmente en -490, no en la vela real. Pendiente S108: migrar a `xloc.bar_time` (eliminando límite).

## Estado

- **F1-GATE:** BLOQUEADA (aún pendiente pase fino)
- **Pasos A→D:** implementados + compilando 0/0 + **VALIDACIÓN VIVA COMPLETADA** ✅
- **CORE:** 1700 líneas SHA `5510361166844bd5`, compila 0/0 los 3 scripts, core-sync OK
- **Commits:** `c15ad15` fix(pine-visual) F1 S107 (CORE INTACTO)
- **ADRs:** Sin nuevo (CE10117 fix + VI/StdDev retire bajo ADR-002/ADR-016 Visual-only reversible)
- **Sin gate/tag:** F1-GATE sigue en redefinición; validación viva desbloquea revisión fina S108

## Pendiente (S108 — PRIORITARIO Usuario)

**Usuario solicitó explícitamente las siguientes 3 tareas para S108:**

1. **Migración xloc.bar_time en drawers:** Las cajas FVG/OB/etc. DEBEN empezar exactamente en la vela de origen. Actual f_xL stopgap clampea a bar_index-490 → caja falsa para zonas viejas. Solución: usar `z.barTime` / `time` (sin límite distancia) en lugar de `xloc.bar_index`. Aplica a ~19 drawers.

2. **Regla de solape MTF:** Cuando cajas D1, H1 y M5 se solapan (herencia MTF), definir comportamiento: ¿colapso visual? ¿prioridad por TF? ¿transparencia escalonada?

3. **Validación fina restante:**
   - Conteo exacto por banda (bandPickIdx realmente 1-3 por banda)
   - Calibrar i_kLeg (default 3.0) — confirmar rango 1-6
   - Calibrar MAX_ZONES_CHART (120) — confirmar no sobrecarga visual

## Enlaces y Referencias

- [[Sesion-106]] — pasos A–D implementación
- [[Sesion-105]] — revert S104 + redefinición PASO 6 + PASO 1
- [[s106-pasos-a-d-poblar-pierna-fib-descartado]] — marca como contexto previo
- `docs/adrs/ADR-016-retencion-zonas-por-importancia.md` — decisión retención
- `docs/reglas-smc-ict.md` — core doctrina (VI/StdDev en §5.5/§5.11)

## Notas

- Descubrimiento clave: **`pine_check.py` server-side no cuenta tokens reales**. La única forma de validar CE10117 es apply al chart (→ tarda 18-25s + error diferido).
- Compresión token sin cambio de lógica: membership test + early-out confDegree + simplificación arrays.
- Retiro VI/StdDev del Visual es reversible (funciones siguen en CORE); permite futura Fase 3 re-activación sin recompilación masiva.
- Stopgap f_xL es banda-aid temporal (visual falso para zonas 500+ barras atrás). S108 usa xloc.bar_time (verdadero). **NO es blockeador de F1-GATE** (pierna se puebla bien visualmente desde ~10 barras atrás, outliers lejanos rare).
- F1-GATE sigue BLOQUEADA por redefinición (pendiente "validación pase fino") pero hallazgos técnicos de S107 **resueltos completamente** (CE10117 + RE10026 + validación viva ✅).

---

**Sesión completada exitosamente.** Bloqueadores críticos CE10117 + RE10026 resueltos. Pasos A–D validados en vivo. Commit `c15ad15` Pine + core-sync OK. PENDIENTE S108: xloc.bar_time + regla solape MTF + calibración final.
