# ESTADO ACTUAL — Estrategia 2.0
> Actualizar al cierre de CADA sesión (lo hace smc-doc-updater vía /smc-session-close cuando existan).

## Estado
- **Fase actual:** FASE 0 — EN CURSO
- **Última tarea completada:** **Bloques D y E completos** (Sesion-006). **SKL-01..09 ✅** 9 skills en `.claude/skills/<nombre>/SKILL.md` (copiadas tal cual de SKILLS.md, frontmatter válido, registradas como invocables; commit 7bd74d3). **AGT-01..08 ✅** 8 agentes en `.claude/agents/<nombre>.md` (copiados tal cual de AGENTES.md; 4 sonnet, 2 opus, 1 haiku; commit 66ef51c). ⚠️ Prueba de invocación en vivo de `smc-code-explorer` **diferida al reinicio de sesión** (el registro de subagentes se carga al arrancar, igual que las skills). — *Sesion-005 previa:* code-review-graph reconstruido, claude-mem dashboard 200, MCP-03 Archon instalado, SCR-02 sync-obsidian adelantado.
- **Bloque C previo (Sesion-004):** MCP-01 ✅ 6 MCPs en `.mcp.json`. MCP-02 ✅ merge upstream fork TV MCP + `tv_health_check`. MCP-04 ✅ claude-mem. MCP-05 ✅ `rules.json` + `morning_brief`.
- **SIGUIENTE PASO:** Bloque F (WF-01 smc-sprint.yaml + scripts restantes SCR-01/03/04; SCR-02 ya hecho) → VER-01..08 → gate VER-09 REVISIÓN-FABLE. (Bloques D y E ✅ hechos en Sesion-006.) **Pendiente al reiniciar sesión:** confirmar que las 9 skills y los 8 agentes aparecen listados/invocables (VER-04) y correr la prueba de smc-code-explorer.
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
- **GATE VER-09 REVISIÓN-FABLE (decisión usuario 2026-06-10):** al terminar TODO el Bloque F (toda la Fase 0), se entrega el paquete completo, estructurado e informado a Fable para que revise el sistema entero ANTES de escribir código Pine (Fase 1). Ningún código antes de pasar este gate. Registrado en WORKPLAN-MAESTRO-V2 §3 Fase 0.

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

*Última actualización: 2026-06-11 — Sesion-005: pendientes no-bloqueantes cerrados, Archon instalado, SCR-02 adelantado*
