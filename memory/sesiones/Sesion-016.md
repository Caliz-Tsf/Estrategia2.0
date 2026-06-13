# Sesión 016 — F1-S1.2-T05 Order Blocks cierre y validación (COMPLETO ✅)
> Fecha: 2026-06-12 · Fase 1 Sprint 1.2 · Claude Code (Haiku 4.5) + Freddy
> Registro de QUÉ se hizo, POR QUÉ, CON QUÉ FINALIDAD y QUÉ SE DECIDIÓ.
> **ESTADO FINAL: T05 COMPLETADO, VALIDADO 97/100, COMMITEADO (698b9dd).**

## Objetivo de la sesión
Cerrar **F1-S1.2-T05 (Order Blocks + mitigación)** — el trabajo quedó WIP en Sesion-015 con código compilable pero sin validación formal ni commit. Esta sesión completa los 3 pasos finales: (1) diagnóstico del supuesto "bug de asimetría", (2) validación numérica ≥90, (3) commit + doc update.

## Qué se hizo y por qué

### 1. Bug "asimetría OB" — INVESTIGADO Y DESCARTADO
**Contexto:** Sesion-015 reportó asimetría visual en el chart: "varios OB bajistas pero solo ~1 alcista". La hipótesis era sesgo en la detección o el dibujo.

**Diagnóstico en Sesion-016:**
- Freddy aclaró que la versión vieja del indicador aún estaba cargada en el chart de TradingView. Al refrescar con la versión actual (archivos locales = fuente de verdad), la detección aparece simétrica.
- **Verificación en código (Sesion-015):** `obOrigin` usa `highBarIdx` y `lowBarIdx` en espejo (BULL busca mínimo, BEAR busca máximo); `f_detectOB` tiene ramas BULL/BEAR estructuralmente idénticas; `f_updateZoneMitigation` es simétrico.
- **Verificación en runtime (Sesion-016):** 10 cajas OB vivas (8 bajistas, 2 alcistas) reflejan el downtrend vigente, no sesgo de detección. Las zonas no dibujadas son las invalidadas/mitigadas (estado = 3 o 2), que no se redibujan — comportamiento correcto.
- **Conclusión:** NO hay bug. La asimetría visual es artefacto de versión antiguo cargado en memoria de TV. **Sin cambios de código.**

### 2. Validación numérica §2.1 — EJECUTADA CON `smc-validator-agent`
**3 casos canónicos de reglas-smc-ict.md §2.1, verificados EXACTO vs OHLC real:**
- ✓ OB bajista **2026-06-01 12:00 (vela 1.16506/1.16452)** → detector: `[1.16452, 1.16506]` ← EXACTO
- ✓ OB bajista **2026-06-05 11:00 (vela 1.16420/1.16345)** → detector: `[1.16345, 1.16420]` ← EXACTO
- ✓ OB alcista **2026-06-08 08:00 (vela 1.15235/1.15079)** → detector: `[1.15079, 1.15235]` ← EXACTO

**Score total:** 97/100 (aprobado).
- −3 observación no bloqueante: si el pivote roto está a >MAX_BARBUF(500) barras atrás (~21 días en H1), `f_detectOB` devuelve `na` sin aviso en el panel. Limitación documentada en header función (ADR-002 §5, límite de la arquitectura ~300 velas de Fase 0). Riesgo bajo: en operación real (M5 entry, H1 detección) no se da; en backtest/análisis histórico con replay sí. **Nota para Fase 3:** observar si sale en play largo.

**Evidencia:** score registrado en `docs/sprint-runs/validaciones.md` + screenshots/t05_ob_eurusd_h1.png ya en Sesion-015.

### 3. Commit 698b9dd — REALIZADO
```
git -C D:\CODE\Estrategia2.0 log --oneline -1
698b9dd feat(pine-core): F1-S1.2-T05 Order Blocks + mitigacion
```
Incluye:
- `pine/SMC-Library.pine` — export `f_detectOB` + `f_updateZoneMitigation` + `const int MAX_BARBUF = 500`
- `pine/SMC-Visual.pine` — inputs GRP_OB, CORE idéntico, wiring buffers/detección/dibujo `f_drawOB`, panel "OB T05"
- `pine/SMC-Strategy.pine` — inputs GRP_OB, CORE idéntico, wiring OB (sin dibujo), label "OB T05"
- `docs/sprint-runs/validaciones.md` — score 97/100, 3 casos §2.1
- `screenshots/t05_ob_eurusd_h1.png` — evidencia visual (10 cajas OB)
- Nota MAX_BARBUF en headers (para paridad MQL5 ADR-002)

### 4. Acuerdo importante con el usuario: Caso de uso MTF (T13)
**Contexto:** Freddy mencionó que sería útil "ver un par de OB de demanda más abajo" (HTF) para anticipar dónde podría rebotar el precio.

**Decisión:** **NO resolver debilitando la invalidación §2.1 (validada/congelada VER-09)**, sino con **OB de mayor temporalidad (MTF)**. Esto ya está planificado en **Sprint 1.4 / T13** (`request.security D1/H4→H1`, PINE-PLAN §7).

**Caso de uso explícito a validar en T13:** "demanda HTF visible debajo del precio como objetivo de rebote, pocas zonas, sin sobrecarga visual."

**Nota adicional:** OBs internos (basados en `structInternal`, reusan `f_detectOB`) añadirían densidad pero con riesgo de sobrecarga visual. Queda anotado para la tarea del siguiente sprint de liquidez (Sprint 1.3 o decisión Fase 3). **Criterio de Fase 3:** mejoría demostrableOut-of-sample antes de integrar.

### 5. Higiene TV — NO ALCANZABLE por MCP, DEJADO COMO TODO COSMÉTICO
**Contexto (Sesion-015):** Al guardar los scripts en TradingView via `pine_save` del MCP TV, la plataforma los guardó todos con el nombre anterior ("SMC_Library" de sesión previa), no con sus nombres propios (SMC-Visual, SMC-Strategy, SMC-Library).

**Intento en Sesion-015:** se probó `chart_save_indicator` del MCP — no creó slots nombrados (TV Desktop no expone esa API al MCP).

**Solución definitiva:** Save As manual en la UI de TradingView (Ctrl+S → Save Script As → nombre). **Documentado como TODO menor, sin bloqueo técnico.**

## Decisiones registradas
1. **Asimetría OB descartada** — artefacto de versión antigua; código correcto.
2. **Validación formal aprobada 97/100** — 3 casos exactos, 1 obs. no bloqueante (límite MAX_BARBUF).
3. **Caso de uso HTF MTF** — derivado a T13; no debilitar §2.1.
4. **OBs internos** — anotado para sprint siguiente con criterio Fase 3 (mejoría OOS).
5. **Higiene TV** — TODO manual menor.

## Estado al cierre
- **Fase:** FASE 1 Sprint 1.2 — **T05 ORDER BLOCKS ✅ COMPLETADO**.
- **Rama:** `pine/sistema-completo` (desarrollo Pine).
- **Working tree:** LIMPIO (T05 commiteado 698b9dd).
- **Core sync:** OK (316 líneas, SHA `0945389f2725fefb`).
- **Validación:** 97/100 (aprobado).
- **Siguiente tarea:** T06 (FVG + CE 50% + mitigación explícita — Sprint 1.2, PINE-PLAN §7).

## Cambios en archivos (commiteados en 698b9dd)
- `pine/SMC-Visual.pine` — inputs GRP_OB, CORE + f_detectOB/f_updateZoneMitigation/MAX_BARBUF, wiring, f_drawOB, panel.
- `pine/SMC-Strategy.pine` — inputs GRP_OB, CORE idéntico, wiring OB.
- `pine/SMC-Library.pine` — exports f_detectOB, f_updateZoneMitigation, MAX_BARBUF.
- `docs/sprint-runs/validaciones.md` — score T05: 97/100, 3 casos §2.1.
- `screenshots/t05_ob_eurusd_h1.png` — evidencia (10 cajas OB).

## Notas para Fase 3 y después
- **MAX_BARBUF limitación (≤~21 días H1):** observar en play largo de backtest/validación si alguna detección falla por antiguedad. Riesgo bajo en operación (H1 + M5) pero a tener en mente.
- **Caso de uso T13:** demanda HTF es un valor potencial a evaluar en Fase 3 — si MTF mejora expectancy OOS vs baseline, integrar; si no, quedó documentado como exploration.
- **OBs internos:** Sprint siguiente; Fase 3 decide si entra según lift OOS (regla R-08 WORKPLAN).

## Links
- [[Sesion-015]] — trabajo WIP previo (implementación + 2 bugs resueltos RE10045 + footgun for 0 to -1).
- `docs/sprint-runs/validaciones.md` — score y casos.
- `docs/reglas-smc-ict.md` §2.1 — definición OB + mitigación.
- PINE-PLAN §7 — orden de sprints.
