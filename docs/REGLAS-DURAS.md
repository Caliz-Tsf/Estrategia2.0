# REGLAS DURAS — Estrategia 2.0

> **Doctrina operativa del proyecto.** Extraído verbatim de `CLAUDE.md` en S147, cuando
> `CLAUDE.md` se redujo a mapa de ≤40 líneas. **Nada de este texto se reescribió.**
> Esto NO se re-litiga: si algo debe cambiar, se escribe un ADR en `docs/adrs/`.
> **Léelo al arrancar, junto con `memory/ESTADO-ACTUAL.md`.**

## ⚠️ Referencias externas (regla absoluta)
- **La ÚNICA referencia externa permitida es el indicador SMC de LuxAlgo** (`pine/reference/LuxAlgo-SMC-base.pine`). De ahí se portan algoritmos base (swings, OB, FVG, EQH/EQL, Premium/Discount) v5→v6.
- Este es un **proyecto nuevo desde cero**. **PROHIBIDO** leer, copiar o referenciar `D:\CODE\BOT\Bot\` (EA antiguo) o cualquier vault/proyecto previo (`Estrategia-Nueva`). No existen para este proyecto.
- **Única excepción:** el fork del TV MCP vive físicamente en `D:\CODE\BOT\Bot\tradingview-mcp-jackson\` — es **herramienta**, no referencia de código. Ejecutarlo/actualizarlo (MCP-02) está permitido; lo prohibido es usar el código del EA antiguo como fuente del sistema.
- **Vault Obsidian — precisión:** lo prohibido es **leer `Mente/Estrategia-Nueva/`** (proyecto previo) como fuente. El vault en sí NO está prohibido: `D:\obsidian\boveda MENTE\Mente\Estrategia2.0\` es el **destino de respaldo** del proyecto (SCR-02 `sync-obsidian.ps1` copia ahí sesiones y ADRs — escritura, no lectura de referencia). La limpieza del vault viejo es manual del usuario con backup previo `[P-21/OBS-01]`.
- Licencia LuxAlgo CC BY-NC-SA: uso personal OK, atribución en headers, **no** publicar derivado comercial.

## Arquitectura (no re-litigar)
**1 core de detección + 2 consumidores** `[FIX: comunicación entre indicadores es imposible en TV]`:
- Sección `// === LIBRARY CORE ===` byte-idéntica en los consumidores — toda la detección como funciones puras + UDTs. No dibuja, no llama `request.security()`. (`pine/SMC-Library.pine` se eliminó en S136: sin consumidores y rancio; la library se regenerará desde el CORE al cerrar Fase 2 — D-PINE-01b.)
- `pine/SMC-Visual.pine` (`indicator`) — dibujo + panel de estado + alertas.
- `pine/SMC-Strategy.pine` (`strategy`) — scoring direccional + entradas/SL/TP → **Strategy Tester** da el backtesting masivo.
- **Fase 4:** el EA MQL5 traduce el core función a función (módulos `SMC_*.mqh` + `EA_SMC_ICT.mq5`), con golden tests de paridad construidos desde TradingView.
- **Consumidor auxiliar opcional** `[ADR-017]`: `pine/SMC-Context.pine` (`indicator`, solo dibuja) — hereda extremos HTF y los revela al romper la frontera. Mismo LIBRARY CORE byte-idéntico (check-core-sync ×3) + 2ª `request.security` con `f_tfExtremes` **fuera** del CORE. No toca Visual/Strategy/SHA. Reversible.

Detalle: [docs/workplan/PINE-PLAN.md](docs/workplan/PINE-PLAN.md) · [docs/workplan/MQL5-PLAN.md](docs/workplan/MQL5-PLAN.md).

## Reglas duras (innegociables)
1. **Anti-repaint.** `[D-PINE-03]` Eventos solo en `barstate.isconfirmed`; `request.security(..., lookahead = barmerge.lookahead_off)` SIEMPRE. Nada del futuro.
2. **Core sincronizado.** La sección LIBRARY CORE de Visual, Strategy y —si existe— `SMC-Context.pine` (ADR-017) es **byte-idéntica**. Tras tocarla → `scripts/check-core-sync.ps1` (verifica los 3).
3. **Umbrales relativos a ATR**, nunca pips fijos. Cada concepto declara qué ATR usa.
4. **Símbolo-agnóstico.** `[ADR-001]` Nada se hardcodea a EURUSD. Lo por-símbolo va como input/perfil (pip, spread, sessionProfile, pesos). Validación primero en EURUSD (gate Fase 3); cada par nuevo repite Fase 3 abreviada (Fase 5).
5. **R:R mínimo 1:3** sin excepción. Si no es calculable → no hay señal (no hay "casi señal").
6. **Scoring direccional** (scoreLong/scoreShort), nunca score absoluto. 42 confluencias canónicas (workplan §4.8).
7. **Compila 0 errores / 0 warnings** o no se commitea. Un commit = un concepto verificado.
8. **Ningún gate de fase se salta.** Si un gate falla → se retrocede con diagnóstico, no se ajusta el criterio.

## Workflow (resumen)
- **Quién hace qué:** [docs/WORKFLOW-ARQUITECTURA.md](docs/WORKFLOW-ARQUITECTURA.md). Claude Code es supervisor permanente; 8 agentes internos + 9 skills; en Fase 4 se suma el trío Claude Code / Antigravity (escribe MQL5) / Claude Desktop (verifica visual MT5).
- **Protocolo TradingView:** [docs/TV-SMC-WORKFLOW.md](docs/TV-SMC-WORKFLOW.md) — 5 fases (startup → desarrollo → validación visual → backtesting → cierre).
- **Ciclo por concepto (Fases 1-2):** check-rule → spec → implement (`smc-pine-develop`) → compile 0/0 → validate ≥90 (`smc-validator-agent`) → approve humano → check-core-sync → commit.
- **Gate VER-09 REVISIÓN-FABLE:** al terminar toda la Fase 0 (Bloque F), se entrega el sistema completo a Fable para revisión integral **antes de escribir una línea de Pine**. Ningún código antes de ese gate.

## Protocolo de sesión
- **Startup** (`/smc-session-startup`): ESTADO-ACTUAL [bloqueante] → git [bloqueante] → tv_health_check [si sesión TV] → claude-mem/context [⚠️ y seguir] → morning_brief [solo Fase 3] → plan confirmado.
- **Cierre** (`/smc-session-close`): commits coherentes → check-core-sync → resumen → `smc-doc-updater` (ESTADO-ACTUAL + Sesion-NNN + checkboxes) → ADR si aplica → git tag si gate → sync-obsidian.
- **Degradación elegante:** el único MCP crítico es el **TV MCP**. Todo lo demás (Archon, claude-mem, context-mode, code-review-graph, task-master, firecrawl/tavily) degrada con ⚠️ y se sigue. Los gates dependen de criterios medibles, no de herramientas.

## Convenciones operativas
- **Idioma: español** en toda comunicación, documentación, commits y comentarios.
- **Commits:** Conventional Commits + ID de tarea — `feat(pine-core): F1-S1.1-T03 detección BOS+CHoCH`. Detalle en reglas-dev §3.
- **Secretos:** API keys SOLO por variable de entorno; `.env`/`*.local.json` en `.gitignore`. Nunca en git.
- **No comprimir en sesiones largas (context-mode):** `docs/reglas-smc-ict.md`, `WORKPLAN-MAESTRO-V2.md`, `memory/ESTADO-ACTUAL.md`, la fase/estado actual y estas reglas duras.

