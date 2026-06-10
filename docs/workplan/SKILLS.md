# SKILLS — Diseño completo de las skills del proyecto
> Anexo 3 del WORKPLAN-MAESTRO-V2.md | Estrategia 2.0 | 2026-06-10
> Cubre el Paso 3 del PROMPT-FABLE. Cada skill se crea en `.claude/skills/<nombre>/SKILL.md` durante Fase 0 (tareas SKL-XX del workplan). El contenido SKILL.md está completo y listo para copiar.

**Correcciones aplicadas:**
- `[FIX]` `smc-validator` y `smc-backtesting-analyst` quedan como skills-protocolo: definen pasos y formato; la ejecución pesada la hace el agente correspondiente (AGT-01/AGT-02). Sin duplicación.
- `[FIX]` `smc-replay` reposicionada: ya no es el método principal de backtesting (eso es el Strategy Tester) — es la herramienta de validación VISUAL de conceptos y de estudio de señales individuales.
- `[FIX]` Protocolos de startup/cierre con tolerancia a fallos: cada paso reporta OK/FALLO y el protocolo continúa; solo los pasos marcados BLOQUEANTE detienen.

---

## SKL-01 · smc-pine-develop
**Tipo**: code-generation | **Cuándo se usa**: cualquier implementación o modificación de código Pine del proyecto.

`.claude/skills/smc-pine-develop/SKILL.md`:
```markdown
---
name: smc-pine-develop
description: Desarrolla código Pine Script v6 del sistema SMC siguiendo el protocolo del proyecto - reglas SMC, naming, compilación 0 errores, validación y commit. Usar para implementar o modificar cualquier concepto en pine/.
---

# Desarrollo Pine Script SMC

## Antes de escribir código
1. Lee la definición cuantificada del concepto en docs/reglas-smc-ict.md.
   Si no existe o no tiene umbrales numéricos → DETENTE: primero se completa la
   regla (con aprobación del usuario), después se codifica.
2. Lee la sección correspondiente de docs/workplan/PINE-PLAN.md (firma de la
   función, UDT que usa, sprint al que pertenece).
3. Verifica con grep si ya existe código relacionado (no dupliques funciones).

## Reglas de código (de docs/reglas-dev.md)
- Pine v6. Un concepto = una función `f_detect<Concepto>()` — sin lógica inline.
- Prefijo SMC_ en arrays globales. Todo array acotado: tras push, shift si supera MAX.
- Eventos solo con barstate.isconfirmed. request.security siempre lookahead_off.
- Comentario por función: propósito + parámetros + retorno.
- La sección LIBRARY CORE de SMC-Visual.pine y SMC-Strategy.pine es IDÉNTICA:
  si editas el core en uno, replica el cambio exacto en el otro y corre
  scripts/check-core-sync.ps1.
- No romper las 16 alertas heredadas del base LuxAlgo.

## Ciclo por cambio
1. Implementar → 2. Compilar vía TV MCP (0 errores y 0 warnings; si no se
   resuelve al primer intento → agente pine-build-resolver) → 3. Screenshot
   EURUSD en TF relevante → 4. Validar con /smc-validator → 5. Si RECHAZADO,
   corregir y volver a 2 → 6. Commit individual:
   `feat(pine): <concepto> — <qué detecta>` o `fix(pine): ...`

## Salida esperada
Código compilando + validación APROBADA + commit. Nunca dejar un concepto a medias
entre Visual y Strategy.
```

---

## SKL-02 · smc-chart-analysis
**Tipo**: research | **Cuándo se usa**: leer el estado SMC actual del chart EURUSD (confluencias activas, bias, zonas) — para sesiones de validación o decisión.

`.claude/skills/smc-chart-analysis/SKILL.md`:
```markdown
---
name: smc-chart-analysis
description: Lee el estado SMC actual de EURUSD desde TradingView - bias por TF, confluencias activas, zonas Premium/Discount, Kill Zone vigente. Usar para análisis de mercado o verificación del panel.
---

# Análisis de chart SMC EURUSD

## Protocolo
1. TV MCP: verificar salud (tv_health_check). Si falla → reportar y detener.
2. Cargar EURUSD con el indicador SMC-Visual en H1. Screenshot.
3. Leer el panel de estado: bias D1/H1/M5, último BOS/CHoCH/MSS por TF, OB/FVG
   activos más cercanos, pool más cercano, sweep reciente, Kill Zone, EMAs, P/D.
4. Repetir screenshot en M5 si la sesión es de entrada (Kill Zone activa).
5. Contrastar lo que muestra el panel con lo visible en el chart — discrepancia
   = bug de panel, reportar como hallazgo.

## Formato de salida
# Análisis EURUSD — <fecha hora GMT>
| Dato | D1 | H1 | M5 |  (bias, estructura, zonas, liquidez)
**Lectura SMC:** <2-4 frases: dónde está el precio respecto a la liquidez y zonas,
qué confluencias están activas en cada dirección>
**Kill Zone:** <activa/próxima>
NOTA: esto es lectura del indicador, NO recomendación de operar.
```

---

## SKL-03 · smc-replay
**Tipo**: validation | **Cuándo se usa**: validación visual de conceptos en datos históricos y estudio cualitativo de señales individuales (Fase 1 y Fase 3). NO es el backtesting estadístico (eso lo hace el Strategy Tester).

`.claude/skills/smc-replay/SKILL.md`:
```markdown
---
name: smc-replay
description: Protocolo de replay en TradingView para validar conceptos SMC visualmente en fechas históricas concretas y estudiar señales individuales. Complementa (no reemplaza) al Strategy Tester.
---

# Replay SMC — validación visual

## Modo A — Validar un concepto (Fase 1)
1. Tomar del docs/reglas-smc-ict.md los casos de prueba del concepto (fechas).
2. TV MCP replay → ir a la fecha, avanzar vela a vela hasta el evento.
3. Verificar: el indicador marca el evento al confirmarse la vela correcta
   (ni antes = repaint, ni después), precio y etiqueta correctos.
4. Registrar en docs/sprint-runs/replay-<concepto>-<fecha>.md:
   caso, esperado, observado, veredicto.

## Modo B — Estudiar señales de la Strategy (Fase 3)
1. Elegir N señales del Strategy Tester (mezcla de wins y losses).
2. Replay a cada señal: ¿las confluencias listadas en la señal son visualmente
   reales? ¿el SL/TP quedó donde la regla dice?
3. Registrar cada una en el log de validación:
   {fecha, dir, score, confluencias, sl, tp1, tpExt, resultado, ¿confluencias
   visualmente correctas?, notas}
4. Las discrepancias señal↔visual son BUGS (la Strategy y el Visual comparten
   core — divergencia = core desincronizado o error de scoring). Reportarlas.

## Regla
Avanzar siempre con vela confirmada. Lo que se ve en replay debe ser idéntico a
lo que el indicador habría mostrado en vivo (test anti-repaint).
```

---

## SKL-04 · smc-multi-scan
**Tipo**: research | **Cuándo se usa**: BLOQUEADA hasta completar Fase 3 en EURUSD. Después: escanear el estado SMC de la watchlist de expansión.

`.claude/skills/smc-multi-scan/SKILL.md`:
```markdown
---
name: smc-multi-scan
description: Escanea el estado SMC de múltiples pares Forex. BLOQUEADA hasta que la Fase 3 esté completada y validada en EURUSD - verificar memory/ESTADO-ACTUAL.md antes de ejecutar.
---

# Multi-scan SMC

## Guard obligatorio
1. Leer memory/ESTADO-ACTUAL.md. Si Fase 3 no está marcada COMPLETADA →
   responder: "Bloqueada: el sistema solo está validado en EURUSD (fase actual:
   <X>). Expansión multi-par es posterior a Fase 3." y DETENER.

## Protocolo (post-Fase 3)
1. Watchlist: GBPUSD, USDJPY, AUDUSD, USDCAD (orden de prueba definido en plan).
2. Por par: cargar SMC-Visual H1 → leer panel → registrar bias, confluencias
   activas, Kill Zone.
3. Salida: tabla comparativa por par + diferencias de comportamiento observadas
   vs EURUSD (volatilidad de detecciones, densidad de señales) → input para
   decidir ajustes de parámetros por par.
```

---

## SKL-05 · smc-validator
**Tipo**: validation (protocolo) | **Cuándo se usa**: paso 4 del ciclo smc-pine-develop, y a demanda.

`.claude/skills/smc-validator/SKILL.md`:
```markdown
---
name: smc-validator
description: Protocolo de validación de un concepto SMC implementado - delega la auditoría al agente smc-validator-agent y gestiona el resultado. Usar tras implementar o modificar cualquier concepto.
---

# Validación de concepto SMC

1. Identificar el concepto y el archivo Pine afectado.
2. Tomar screenshots frescos (TV MCP) en los casos de prueba de
   docs/reglas-smc-ict.md para ese concepto.
3. Invocar al agente `smc-validator-agent` con: concepto + archivo + screenshots.
4. Procesar el veredicto:
   - APROBADO (≥90) → registrar score en docs/sprint-runs/validaciones.md y
     continuar el ciclo (commit).
   - RECHAZADO → aplicar las correcciones exactas del reporte → recompilar →
     volver a 2. Máximo 3 iteraciones; a la 4ª, escalar al usuario con el
     historial de intentos (algo está mal en la regla o en el enfoque).
   - REGLA INCOMPLETA → detener y completar docs/reglas-smc-ict.md con el
     usuario antes de seguir.
```

---

## SKL-06 · smc-backtesting-analyst
**Tipo**: validation (protocolo) | **Cuándo se usa**: Fase 3 — tras cada run del Strategy Tester o lote de paper trades.

`.claude/skills/smc-backtesting-analyst/SKILL.md`:
```markdown
---
name: smc-backtesting-analyst
description: Protocolo de análisis de un run de backtesting - exporta trades del Strategy Tester, delega la estadística al agente smc-backtesting-analyst-agent y gestiona la propuesta de pesos. Usar en Fase 3.
---

# Análisis de run de backtesting

1. Exportar la lista de trades del Strategy Tester (TV MCP) a
   docs/sprint-runs/run-NNN-trades.csv. Verificar columnas: fecha, dir, score,
   confluencias, SL, TP, resultado, R alcanzado.
2. Confirmar el corte IS/OOS vigente (está en docs/scoring-weights-vN.md;
   default: IS = primeros 70% cronológicos).
3. Invocar `smc-backtesting-analyst-agent` con: CSV + pesos vigentes + corte.
4. Procesar veredicto:
   - PROMOVER PESOS → crear docs/scoring-weights-vN+1.md (tabla completa +
     threshold + evidencia), actualizar los inputs default en SMC-Strategy.pine,
     commit `feat(scoring): pesos vN+1`.
   - MÁS DATOS → registrar qué falta y extender el periodo de test.
   - RED FLAG OVERFITTING → NO tocar pesos; sesión con el usuario para
     simplificar el sistema (menos confluencias, threshold más simple).
5. Los pesos NUNCA se editan a mano sin pasar por este protocolo.
```

---

## SKL-07 · mql5-translator
**Tipo**: code-generation (protocolo) | **Cuándo se usa**: Fase 4 — pipeline de traducción de cada función del core.

`.claude/skills/mql5-translator/SKILL.md`:
```markdown
---
name: mql5-translator
description: Protocolo del pipeline de traducción Pine→MQL5 por función - spec, escritura, revisión, compilación, golden test. Solo Fase 4.
---

# Pipeline de traducción Pine→MQL5 (por función)

GUARD: memory/ESTADO-ACTUAL.md debe marcar Fase 4. Si no → detener.

1. SPEC+CÓDIGO: invocar `mql5-translator-agent` con la función Pine + entrada del
   mapeo (docs/workplan/MQL5-PLAN.md §3) → produce código + equivalencias + tests.
2. ESCRITURA ALTERNATIVA: si Antigravity IDE está disponible y se prefiere,
   entregarle la spec del paso 1 y que escriba él; el código resultante sigue
   el mismo pipeline.
3. REVISIÓN: invocar `mql5-reviewer` con el código + spec. Loop hasta APROBADO
   (máx 3 iteraciones, luego escalar a smc-architect).
4. COMPILAR: MetaEditor vía línea de comandos
   ("metaeditor64.exe /compile:<ruta> /log") → 0 errors, 0 warnings.
5. GOLDEN TESTS: ejecutar el script de tests del módulo con los casos del
   translator → todos verdes. Un test rojo = la traducción difiere de Pine:
   volver a 1 con el caso fallido como evidencia.
6. VERIFICACIÓN VISUAL (si el cambio afecta al panel/display): Claude Desktop
   con computer use sobre MT5.
7. Commit: `feat(mql5): <módulo>::<función> traducida + N golden tests`.
```

---

## SKL-08 · smc-session-startup
**Tipo**: protocol | **Cuándo se usa**: al inicio de cada sesión de trabajo del proyecto.

`.claude/skills/smc-session-startup/SKILL.md`:
```markdown
---
name: smc-session-startup
description: Protocolo de arranque de sesión del proyecto Estrategia 2.0 - estado, rama, salud de herramientas, plan de sesión. Ejecutar al inicio de cada sesión de trabajo.
---

# Startup de sesión

Ejecutar en orden. Cada paso reporta ✅/⚠️/❌. Solo los BLOQUEANTES detienen.

1. [BLOQUEANTE] Leer memory/ESTADO-ACTUAL.md → fase, sprint, siguiente tarea,
   bloqueos. Si no existe → algo está muy mal: reconstruirlo desde git log antes
   de seguir.
2. git status + git branch → working tree limpio y rama correcta
   (fase-N/<sprint>). Sucio → preguntar al usuario antes de tocar nada.
3. [Solo si la sesión toca TradingView] tv_health_check del TV MCP.
   ❌ → las tareas TV se posponen; las de docs/código local pueden seguir.
4. [Opcional] claude-mem dashboard (http://localhost:37777) y context-mode
   activos. ❌ → ⚠️ y continuar (no son bloqueantes).
5. [Solo sesiones de validación Fase 3] morning_brief con rules.json → bias
   EURUSD del día.
6. Proponer el plan de la sesión: la "siguiente tarea" de ESTADO-ACTUAL.md +
   tiempo estimado + qué agentes/skills se usarán. Confirmar con el usuario.

## Salida
Resumen de arranque: estado de los 6 checks + plan de sesión confirmado.
```

---

## SKL-09 · smc-session-close
**Tipo**: protocol | **Cuándo se usa**: al cerrar cada sesión de trabajo.

`.claude/skills/smc-session-close/SKILL.md`:
```markdown
---
name: smc-session-close
description: Protocolo de cierre de sesión - commits, actualización de estado vía smc-doc-updater, ADRs pendientes, sync a Obsidian. Ejecutar antes de terminar cada sesión de trabajo.
---

# Cierre de sesión

1. git status → si hay cambios sin commitear, agruparlos en commits coherentes
   (nunca un mega-commit "wip"). Verificar con git log que todo lo de hoy
   está commiteado.
2. Verificar sincronía del core: scripts/check-core-sync.ps1 → si Visual y
   Strategy divergen, ARREGLAR antes de cerrar (es la deuda más cara).
3. Redactar resumen de sesión (qué se completó con IDs del workplan, qué quedó
   a medias, bloqueos nuevos).
4. Invocar agente `smc-doc-updater` con el resumen → actualiza
   memory/ESTADO-ACTUAL.md + memory/sesiones/Sesion-NNN.md + checkboxes.
5. Si hubo decisión arquitectural sin ADR → invocar smc-architect para
   escribirla AHORA (no se acumulan).
6. Si se completó una fase/gate → tag git (`fase-N-completa`) y nota en
   ESTADO-ACTUAL.
7. scripts/sync-obsidian.ps1 → copiar sesión + ADRs nuevos al vault personal.
   ❌ → ⚠️ reportar y cerrar igualmente.

## Salida
Confirmación: commits ✅ · core sync ✅ · estado actualizado ✅ · obsidian ✅/⚠️
```

---

## TABLA RESUMEN E INVOCACIÓN

| ID | Skill | Tipo | Ejemplo de invocación |
|----|-------|------|----------------------|
| SKL-01 | smc-pine-develop | code-generation | "implementa la detección de sweeps" → aplica el ciclo completo |
| SKL-02 | smc-chart-analysis | research | "/smc-chart-analysis" → tabla de estado EURUSD + lectura SMC |
| SKL-03 | smc-replay | validation | "valida los sweeps en replay" → modo A sobre casos de prueba |
| SKL-04 | smc-multi-scan | research | "/smc-multi-scan" → guard de fase; post-F3 escanea 4 pares |
| SKL-05 | smc-validator | validation | invocada por SKL-01 paso 4; delega en AGT-01 |
| SKL-06 | smc-backtesting-analyst | validation | "analiza el run 3" → export CSV + AGT-02 + gestión de pesos |
| SKL-07 | mql5-translator | code-generation | "traduce f_detectOB" → pipeline 7 pasos (Fase 4) |
| SKL-08 | smc-session-startup | protocol | "/smc-session-startup" al abrir sesión |
| SKL-09 | smc-session-close | protocol | "/smc-session-close" al cerrar sesión |

**Mapa de dependencias:** SKL-01 → invoca SKL-05 → invoca AGT-01 · SKL-06 → AGT-02 · SKL-07 → AGT-04 + AGT-05 · SKL-09 → AGT-07 (+AGT-03 si ADR pendiente) · SKL-08/09 usan scripts SCR-01..03.
