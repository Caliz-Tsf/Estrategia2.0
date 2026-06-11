# TV-SMC-WORKFLOW.md — Protocolo de trabajo en TradingView
> Estrategia 2.0 · Bot SMC/ICT · DOC-04 del WORKPLAN-MAESTRO-V2
> Las 5 fases de una sesión que toca TradingView: STARTUP → DESARROLLO → VALIDACIÓN VISUAL → BACKTESTING → CIERRE.

Este documento describe **cómo se trabaja contra TradingView vía el TV MCP** dentro de una sesión. No reemplaza al protocolo de sesión general ([DOC-03](WORKFLOW-ARQUITECTURA.md) §6); lo especializa para el trabajo en el chart. Herramienta base: **TradingView MCP** (único MCP crítico del proyecto). Lanzador: `scripts/launch-tv-agent.ps1` (SCR-01).

---

## VISIÓN GENERAL

```
┌──────────┐   ┌────────────┐   ┌──────────────────┐   ┌─────────────┐   ┌────────┐
│ 1 STARTUP│ → │ 2 DESARROLLO│ → │ 3 VALID. VISUAL  │ → │4 BACKTESTING│ → │5 CIERRE│
│ salud TV │   │ implementar │   │ concepto vs regla│   │ Strategy    │   │ commits│
│ + chart  │   │ Pine + comp.│   │ (screenshots)    │   │ Tester +CSV │   │ + estado│
└──────────┘   └────────────┘   └──────────────────┘   └─────────────┘   └────────┘
   SKL-08      SKL-01            SKL-05→AGT-01           SKL-03/SKL-06      SKL-09
              (pine-build-      (smc-validator-agent)   (smc-backtesting-  (smc-doc-
               resolver si      smc-replay modo A        analyst-agent)     updater)
               falla compilar)
```

No todas las sesiones pasan por las 5 fases:
- **Sesión de desarrollo (Fase 1-2):** 1 → 2 → 3 → 5 (el backtesting masivo es de Fase 3).
- **Sesión de validación/calibración (Fase 3):** 1 → 4 → 3(modo B) → 5.
- **Sesión de análisis de mercado:** 1 → (smc-chart-analysis) → 5.

---

## FASE 1 — STARTUP (preparar TradingView)
**Skill:** `smc-session-startup` (SKL-08). **Objetivo:** tener TV operativo y el chart en su sitio antes de tocar nada.

1. Arranque general de sesión (ESTADO-ACTUAL + git) — pasos BLOQUEANTES de DOC-03 §6.
2. **`tv_health_check`** del TV MCP. ❌ → las tareas TV se posponen; las de docs/código local pueden seguir. **Es el único check que bloquea el trabajo TV.**
3. Lanzar/verificar TradingView con `scripts/launch-tv-agent.ps1`: fix TV v2.14+, auto-load de `SMC-Visual`, tv_health_check integrado.
4. **`chart_set_symbol` EURUSD** + **`chart_set_timeframe`** al TF de la tarea (H1 por defecto; M5 si es trabajo de entrada; D1 para contexto).
5. Confirmar que el indicador `SMC-Visual` está cargado (`chart_get_state` → lista de indicadores).
6. [Solo Fase 3] `morning_brief` con `rules.json` → bias EURUSD del día.

**Salida:** TV sano, EURUSD cargado en el TF correcto, indicador visible.

---

## FASE 2 — DESARROLLO (implementar Pine)
**Skill:** `smc-pine-develop` (SKL-01). **Objetivo:** un concepto implementado y compilando 0/0.

1. **check-rule:** leer la definición cuantificada del concepto en [reglas-smc-ict.md](reglas-smc-ict.md). Si no existe o no tiene umbrales → DETENER y completar la regla con el usuario primero.
2. Implementar en la sección **LIBRARY CORE** (idéntica en `SMC-Visual.pine` y `SMC-Strategy.pine`) siguiendo [reglas-dev.md](reglas-dev.md): `f_detect<Concepto>`, prefijo `SMC_`, arrays acotados, `barstate.isconfirmed`, `lookahead_off`.
3. Añadir dibujo en Visual (`f_draw<Concepto>` con su cuota de objetos) + fila de panel si aplica.
4. **Compilar vía TV MCP** (`pine_smart_compile` / `pine_get_errors`): objetivo **0 errores / 0 warnings**.
   - Si no se resuelve al primer intento → agente **`pine-build-resolver`** (AGT-08), que arregla con el diff mínimo sin tocar la lógica SMC.
5. Si se tocó el CORE → `scripts/check-core-sync.ps1` (Visual == Strategy).

**Salida:** código compilando 0/0, core sincronizado. (Aún sin validar visualmente → Fase 3.)

---

## FASE 3 — VALIDACIÓN VISUAL (concepto vs regla)
**Skills:** `smc-validator` (SKL-05) → agente `smc-validator-agent` (AGT-01); `smc-replay` (SKL-03) modo A. **Objetivo:** score ≥90 contra la regla, con evidencia visual.

1. Tomar **screenshots frescos** (TV MCP `capture_screenshot`) en los **casos de prueba** que la regla del concepto lista en reglas-smc-ict.md (fechas-hora GMT concretas).
2. Para casos históricos: **`smc-replay` modo A** — `replay_start` → ir a la fecha → `replay_step` vela a vela hasta el evento. Verificar que el indicador lo marca **al confirmarse la vela correcta** (ni antes = repaint, ni después).
3. Invocar **`smc-validator-agent`** con: concepto + archivo Pine + screenshots. Devuelve score 0-100 con aciertos/fallos por coordenada precio-tiempo.
4. Procesar veredicto:
   - **APROBADO (≥90)** → registrar en `docs/sprint-runs/validaciones.md` → continuar a commit (Fase 5).
   - **RECHAZADO** → aplicar las correcciones exactas → recompilar (volver a Fase 2) → revalidar. Máx 3 iteraciones; a la 4ª, escalar al usuario.
   - **REGLA INCOMPLETA** → detener y completar reglas-smc-ict.md con el usuario.

**Anti-repaint (innegociable):** lo que se ve en replay debe ser idéntico a lo que el indicador mostraría en vivo en esas mismas velas. `[D-PINE-03]`

**Salida:** concepto APROBADO ≥90 con evidencia, o lista de correcciones.

---

## FASE 4 — BACKTESTING (solo Fase 3 del proyecto)
**Skills:** `smc-backtesting-analyst` (SKL-06) → agente `smc-backtesting-analyst-agent` (AGT-02); `smc-replay` modo B. **Objetivo:** estadística honesta del sistema y propuesta de pesos sin overfitting.

> Esto NO es replay manual señal a señal. El backtesting masivo lo hace el **Strategy Tester nativo** porque `SMC-Strategy.pine` es un `strategy()`. `[FIX P-02]`

1. Correr el **Strategy Tester** sobre el máximo histórico disponible de EURUSD (M5/H1).
2. Exportar la lista de trades a `docs/sprint-runs/run-NNN-trades.csv` (TV MCP `data_get_trades` / `data_get_strategy_results`). Columnas: fecha, dir, score, confluencias, SL, TP, resultado, R alcanzado.
3. Confirmar el **corte IS/OOS** vigente (en `docs/scoring-weights-vN.md`; default 70% cronológico IS). **El corte se fija ANTES de mirar resultados.** `[FIX P-03]`
4. Invocar **`smc-backtesting-analyst-agent`** con CSV + pesos vigentes + corte → lift por confluencia (solo muestra ≥20), patrones de pérdida, propuesta de pesos vN+1, **degradación IS→OOS honesta**.
5. Procesar veredicto:
   - **PROMOVER PESOS** → `docs/scoring-weights-vN+1.md` + actualizar inputs default en `SMC-Strategy.pine` + commit.
   - **MÁS DATOS** → registrar qué falta, extender periodo.
   - **RED FLAG OVERFITTING** → NO tocar pesos; sesión de simplificación con el usuario.
6. **`smc-replay` modo B:** revisar 30-50 señales (mezcla wins/losses) → ¿las confluencias listadas son visualmente reales? ¿SL/TP donde la regla dice? Discrepancia señal↔visual = BUG (core desincronizado o error de scoring).

**Regla:** los pesos NUNCA se editan a mano sin pasar por este protocolo. Nunca se optimiza sobre OOS.

**Salida:** reporte estadístico + pesos versionados (o red flag).

---

## FASE 5 — CIERRE
**Skill:** `smc-session-close` (SKL-09) → agente `smc-doc-updater` (AGT-07). **Objetivo:** dejar el proyecto en estado retomable.

1. `git status` → commits coherentes por concepto (nunca mega-commit "wip"); verificar con `git log` que todo lo de hoy está commiteado.
2. `scripts/check-core-sync.ps1` → si Visual y Strategy divergen, **ARREGLAR antes de cerrar**.
3. Resumen de sesión con IDs del workplan (completado / a medias / bloqueos).
4. Invocar **`smc-doc-updater`** → actualiza `memory/ESTADO-ACTUAL.md` + `memory/sesiones/Sesion-NNN.md` + checkboxes del workplan.
5. ¿Decisión arquitectural sin ADR? → invocar `smc-architect` AHORA (no se acumulan).
6. ¿Gate de fase completado? → tag git (`fase-N-completa`).
7. `scripts/sync-obsidian.ps1` → copiar sesión + ADRs nuevos al vault personal. ❌ → ⚠️ y cerrar igualmente.

**Salida:** commits ✅ · core sync ✅ · estado actualizado ✅ · obsidian ✅/⚠️.

---

## HERRAMIENTAS TV MCP MÁS USADAS POR FASE

| Fase | Tools TV MCP típicos |
|---|---|
| STARTUP | `tv_health_check` · `chart_set_symbol` · `chart_set_timeframe` · `chart_get_state` · `morning_brief` |
| DESARROLLO | `pine_set_source` · `pine_smart_compile` · `pine_get_errors` · `pine_get_console` |
| VALID. VISUAL | `capture_screenshot` · `replay_start/step/stop` · `chart_scroll_to_date` · `data_get_pine_labels/boxes/lines` |
| BACKTESTING | `data_get_strategy_results` · `data_get_trades` · `data_get_equity` |
| CIERRE | (git + scripts locales; sin TV salvo screenshot final) |

---

## DEGRADACIÓN
Si el TV MCP cae a mitad de sesión: el trabajo TV se detiene, pero documentación, diseño de reglas y revisión de código local continúan. Ningún gate de fase depende de que TV esté arriba en un momento dado — depende de los criterios medibles del workplan §2. `[R-10]`

---

*DOC-04 · Estrategia 2.0 · 2026-06-10 — referencia: SKILLS.md, AGENTES.md, DOC-03, instrucciones del TV MCP*
