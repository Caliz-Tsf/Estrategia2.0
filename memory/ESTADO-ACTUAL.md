# ESTADO ACTUAL — Estrategia 2.0
> Actualizar al cierre de CADA sesión (lo hace smc-doc-updater vía /smc-session-close cuando existan).

## Estado
- **Fase actual:** FASE 0 — EN CURSO
- **Última tarea completada:** **Bloque C (MCPs) cerrado** (Sesion-004). MCP-01 ✅ 6 MCPs en `.mcp.json` (code-review-graph ⚠️ no registró tools, no-bloqueante). MCP-02 ✅ merge upstream del fork TV MCP + `tv_health_check` OK. MCP-04 ✅ claude-mem instalado. MCP-05 ✅ `rules.json` EURUSD + `morning_brief` OK. MCP-03 (Archon) y MCP-06 (task-master parse) ⏳ DIFERIDOS (no-bloqueante/opcional).
- **SIGUIENTE PASO:** Bloque D (skills SKL-01..09) → E (agentes AGT-01..08) → F (workflows) → VER-01..08 → gate VER-09 REVISIÓN-FABLE.
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

## Notas de herramientas (Sesion-004)
- **TV MCP:** lanzar SIEMPRE por `mcp__tradingview__tv_launch` (CDP 9222), nunca manual. Fork en `D:\CODE\BOT\Bot\tradingview-mcp-jackson` ahora +4 ahead de origin (merge upstream sin pushear).
- **rules.json** (morning_brief) vive en la raíz del repo-herramienta TV MCP (de ahí lo lee por defecto). Config EURUSD/H1/SMC. Si futuros merges de upstream lo tocan, re-aplicar.
- **code-review-graph** ⚠️: binario OK pero no registró tools; grafo con 0 nodos (sin código aún). Reintentar/construir grafo en Fase 1.
- **Archon (MCP-03)** y **task-master parse (MCP-06)** diferidos — retomar en Bloque F si se necesitan.

*Última actualización: 2026-06-11 — Sesion-004: Bloque C (MCPs) cerrado*
