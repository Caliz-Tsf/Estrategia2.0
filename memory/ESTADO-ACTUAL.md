# ESTADO ACTUAL — Estrategia 2.0
> Actualizar al cierre de CADA sesión (lo hace smc-doc-updater vía /smc-session-close cuando existan).

## Estado
- **Fase actual:** **FASE 1 — DESBLOQUEADA ✅** (VER-09 aprobado, ADR-002 registrado). Siguiente: F1-S1.1-T01 (esqueleto 3 archivos Pine + UDTs + arrays acotados) vía `/smc-session-startup` + workflow `smc-sprint`.
- **Última tarea completada (Sesion-009):** **GATE VER-09 CERRADO — APROBADO POR FABLE.** Auditoría integral de Fase 0: reglas-smc-ict.md, DOC-01..07, MCPs/skills/agentes, workflows, scripts. Resolución de 3 decisiones de escasez (MSS swing ×1, Judas ×1, breaker retest): aceptados como composiciones de primitivos bien evidenciados; criterios de done convertidos en T12/T18/T19 de Fase 1. Umbrales congelados hasta calibración Fase 3 (anti-overfitting). MCP-06 (task-master) saltado definitivamente. Mejora: paridad Python↔Pine para golden tests. Correcciones aplicadas (C1–C5): alineación PINE-PLAN/WORKFLOWS/reglas-smc-ict.md. ADR-002 escrito y registrado. Tag `ver-09-aprobado` generado (supervisor). Handoff: `docs/VER-09-handoff-fable.md` + veredicto en sección final.
- **Última tarea completada (Sesion-008):** **VER-01..08 PASE COMPLETO.** VER-01 tv_health_check ✅ · VER-02 startup 1⚠️ ✅ · VER-03 morning_brief ✅ · VER-04 ✅ (S007) · **VER-05 ✅ reglas-smc-ict.md poblado con casos reales de EURUSD (24 conceptos, TV MCP) + aprobado por Freddy** — 3 notas de escasez (MSS swing ×1, Judas ×1, breaker retest) derivadas a Fable (VER-09) para decisión · VER-06 ✅ (SCR-03) · VER-07 ✅ git limpio · VER-08 ✅. Extractor reproducible en `scripts/ver05/` (detect*.py sobre eurusd_h1.csv/eurusd_m5.csv; H1 25-may→11-jun, M5 10–11-jun). Handoff: `docs/VER-09-handoff-fable.md`. tag `fase-0-completa`.
- **Sesion-007:** **GATE VER-04 SUPERADO** — verificación en frío de skills y agentes. Las 9 skills y los 8 agentes confirmados en disco Y en el registro del runtime al arrancar en frío (lo que falló en caliente en Sesion-006). Prueba real del Done de Bloque E ejecutada: `smc-code-explorer` respondió con anclas `archivo:línea` exactas sobre `pine/reference/LuxAlgo-SMC-base.pine` (swings :337-457, OB :507-540, FVG :634-649, BOS/CHoCH :551-612) y detectó por su cuenta el `lookahead_on` en :635 como riesgo de repaint vs D-PINE-03. Segundo agente `smc-architect` (opus) también operativo. Diagnóstico Sesion-006 confirmado: el registro de subagentes carga al arrancar la sesión, no en caliente. — *Sesion-006:* SKL-01..09 ✅ (commit 7bd74d3) + AGT-01..08 ✅ (commit 66ef51c). *Sesion-005:* code-review-graph, claude-mem, MCP-03 Archon, SCR-02 sync-obsidian.
- **Bloque C previo (Sesion-004):** MCP-01 ✅ 6 MCPs en `.mcp.json`. MCP-02 ✅ merge upstream fork TV MCP + `tv_health_check`. MCP-04 ✅ claude-mem. MCP-05 ✅ `rules.json` + `morning_brief`.
- **✅ VER-04 CERRADO (Sesion-007).** Verificación en frío superada (ver "Última tarea completada"). Despejada la prioridad #1 de Freddy.
- **✅ BLOQUE F COMPLETO (Sesion-007).** Los 5 ítems hechos y probados:
  - **WF-01** `.archon/workflows/smc-sprint.yaml` — adaptado al schema real de Archon v0.4.x (DAG `nodes`/`depends_on`/`loop`+`until`+`<promise>`; loop corrección implement↔validate in-node ×3; aprobación humana via `interactive`/`gate_message`). `archon validate workflows smc-sprint` = **ok** (discovery 20→21, 0 errores). commit b6c6c5c.
  - **SCR-01** `launch-tv-agent.ps1` — integrado byte-idéntico desde ubicación previa (pedido del usuario; es tooling, no sistema SMC). Lanza TV Desktop CDP 9222 + **agent-browser** (agente que navega el chart). Parsea sin errores. `auto-load SMC-Visual` queda para Fase 1 (no existe aún). commit c92bc40.
  - **SCR-02** `sync-obsidian.ps1` — ✅ ya estaba (Sesion-005).
  - **SCR-03** `check-core-sync.ps1` [NUEVO] — compara LIBRARY CORE Visual/Strategy por SHA-256. Probado: SKIP/OK/DIVERGENT(exit 1+diff). commit 768fde5.
  - **SCR-04** `process-video.ps1` — pipeline yt-dlp→FFmpeg→Whisper→.md al vault Teoria-SMC. Probado end-to-end con video real 19s. commit (este).
- **SIGUIENTE PASO (Sesion-010):** **F1-S1.1-T01 — ESQUELETO DE 3 ARCHIVOS PINE** (SMC-Library.pine, SMC-Visual.pine, SMC-Strategy.pine) + UDTs + arrays acotados. Workflow: `/smc-session-startup` → `smc-sprint` (Archon) → ciclo implement↔validate ×3 (agentes smc-pine-develop + smc-validator-agent). Ningún gate de fase se salta (regla 8).
- **Commits:** Bloque A 5970a10 · Tier 1 414fa1b · Tier 2 3a17b79 · §3+ADR-001 429de10 · §4 f2b9b57 · Sesion-002 (DOC-02/03/04/07 + gate VER-09 + eliminación DOC-06).
- **PLAN ACORDADO (Sesion-001):** adelantar TODO lo informativo (escribir/investigar/corregir/desglosar conceptos y estructuras) ANTES del gráfico. Freddy quiere validar todos los conceptos/reglas con Fable antes de la fase visual.
- **Docs informativos (Sesion-002) ✅ COMPLETOS:** DOC-02 reglas-dev.md · DOC-03 WORKFLOW-ARQUITECTURA.md · DOC-04 TV-SMC-WORKFLOW.md · DOC-07 CLAUDE.md. **DOC-06 ELIMINADO** (proyecto nuevo, sin BotBase ni Estrategia-Nueva; única ref externa = LuxAlgo SMC — ver [[proyecto-nuevo-solo-luxalgo]]).
- **DIFERIDO (necesita gráfico):** pasada TradingView MCP para poblar casos ⏳PENDIENTE-TVMCP de reglas-smc-ict.md + aprobación final (gate VER-05). Se hace cuando todo lo informativo esté escrito y validado con Fable.
- ~~PENDIENTE workplan: aplicar cambios de ADR-001~~ ✅ APLICADO en Sesion-003 (§4.8, F2-T02, DOC-07 desc., PINE-PLAN §3.4/§6, MQL5-PLAN).

## Bloqueos
- Ninguno. (SEC-01 resuelto: usuario confirmó keys viejas revocadas; nuevas en .env/.mcp.json gitignored.)

## Decisiones de esta sesión (DOC-01)
- Umbrales SIEMPRE relativos a ATR(14), nunca pips fijos.
- swingLen=5 / internalLen=3 (ajustable en pruebas Fase 3).
- BOS/CHoCH por CIERRE, no mecha. Modelo bias = structure high/low (extensor vs protector).
- MSS = CHoCH de nivel swing + displacement (≥1.5×ATR, cuerpo ≥70%) — lo distingue del CHoCH simple en el scoring.
- Storage keys: .mcp.json + .env (ambos gitignored), sin migrar a env vars de Windows.
- **ADR-001 — Bot MULTI-SÍMBOLO, sin filtro horario duro.** Kill Zone = confluencia ponderada + sessionProfile configurable (FX-London-NY/FX-Asia/None), no bloqueo. Guardián universal = filtro de spread. Pesos del scoring por símbolo. Valida EURUSD primero, cada símbolo nuevo = Fase 5 abreviada. Umbrales ATR-relativo = base de portabilidad.

## Decisiones vigentes (no re-litigar)
- Arquitectura Pine: 1 core compartido + SMC-Visual.pine (indicator) + SMC-Strategy.pine (strategy → Strategy Tester).
- EA MT5 100% nativo, SIN webhook.
- 42 confluencias direccionales; pesos en Fase 3 con split IS/OOS 70/30.
- Solo EURUSD hasta gate de Fase 3. R:R mínimo 1:3. Anti-repaint obligatorio.
- Fuente de verdad del plan: WORKPLAN-MAESTRO-V2.md + docs/workplan/*.
- **ADR-002 — VER-09 APROBADO (2026-06-11, Sesion-009).** MSS swing / Judas / Breaker aceptados como composiciones de primitivos evidenciados; criterios de done convertidos en T12/T18/T19 (Fase 1). Umbrales CONGELADOS hasta calibración Fase 3 (anti-overfitting). MCP-06 saltado. Paridad Python↔Pine anotada en Fase 1. Ningún código antes del gate (completado). Límite ~300 velas documentado; validación visual sin límite (chart_scroll_to_date/replay/screenshots).

## Cómo arrancar la próxima sesión
1. Leer este archivo + WORKPLAN-MAESTRO-V2.md Sección 3 (Fase 0).
2. Confirmar SEC-01 hecho por el usuario.
3. Ejecutar Fase 0 en orden: Bloque A → B → C → D → E → F → VER-01..08.

## Notas de herramientas (Sesion-005)
- **TV MCP:** lanzar SIEMPRE por `mcp__tradingview__tv_launch` (CDP 9222), nunca manual. Fork en `D:\CODE\BOT\Bot\tradingview-mcp-jackson` +4 ahead de origin (merge upstream sin pushear).
- **rules.json** (morning_brief) vive en la raíz del repo-herramienta TV MCP. Config EURUSD/H1/SMC. Si merges de upstream lo tocan, re-aplicar.
- **code-review-graph** v2.3.2: binario OK, repo registrado como `estrategia2`, `serve` arranca. Grafo vacío *por naturaleza* (P-12: no parsea Pine; el resto es .md). Útil de verdad desde Fase 1 SOLO si se le da código en lenguaje soportado — Pine NO lo es, así que su valor real es limitado. Los tools del MCP deberían registrar al reiniciar la sesión.
- **Archon (MCP-03) ✅ INSTALADO — OJO: cambió de arquitectura.** El Archon real (v0.4.1) NO es el RAG/Docker que asumía el workplan: es una **"Remote Agentic Coding Platform"** (Bun+SQLite, controla Claude Code/Codex vía Slack/Telegram/GitHub) con **motor de workflows DAG** (lo que sí usamos para `smc-sprint`). App clonada en `D:\CODE\Archon` (NO dentro del repo). `bun run cli doctor` = All checks passed; 20 workflows default visibles (archon-architect, archon-validate-pr, etc. — coinciden con refs del workplan). Sin Docker, sin Slack/Telegram (no se necesitan). Invocar con `scripts/archon.ps1 <args>` desde el proyecto. ⚠️ NO correr workflows que invoquen Claude dentro de una sesión Claude Code (CLAUDECODE=1 → cuelgue, issue #1067) — usar terminal normal. Ver [[estrategia2-archon-remote-agent-platform]].
- **task-master (MCP-06):** **OPCIONAL — se puede saltar sin perder nada** (decisión usuario Sesion-005). No es pieza del sistema (el WORKPLAN ya es el backlog; teoría→indicador corre sobre reglas-smc-ict.md + smc-sprint/Archon + smc-validator-agent). Si se hiciera, es en VER-09 y **a criterio de Fable** decidir si vale la pena (probablemente no). CLI disponible (0.43.1).
- **SCR-02 sync-obsidian.ps1** ✅: copia incremental (por hash) de `memory/sesiones/`, `docs/adrs/`, `memory/ESTADO-ACTUAL.md` → `D:\obsidian\boveda MENTE\Mente\Estrategia2.0\`. `-DryRun` para simular. Idempotente. Adelantado del Bloque F.

*Última actualización: 2026-06-11 — Sesion-009: **VER-09 CERRADO — APROBADO.** ADR-002 aplicado, Fase 1 DESBLOQUEADA. Siguiente: F1-S1.1-T01 (esqueleto Pine).*
