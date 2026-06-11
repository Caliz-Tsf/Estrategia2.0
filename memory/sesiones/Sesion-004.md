# Sesión 004 — Bloque C: MCPs y herramientas
> Fecha: 2026-06-11 · Fase 0 · Claude Code (Opus 4.8) + Freddy
> Registro de QUÉ se hizo, POR QUÉ, CON QUÉ FINALIDAD y QUÉ SE DECIDIÓ.
> ⚠️ **RECONSTRUIDA en Sesion-005 (2026-06-11).** No se escribió un Sesion-004.md al cierre de aquella sesión; este archivo se reconstruye a partir de las anotaciones "Sesion-004" del WORKPLAN-MAESTRO-V2 (MCP-01..06) y de ESTADO-ACTUAL. Los hechos son fieles; el nivel de detalle de relato es menor que en una sesión escrita en vivo.

## Objetivo de la sesión
Ejecutar el **Bloque C** de la Fase 0: configurar los 6 MCPs y herramientas (MCP-01..06), dejando anotado como ⚠️ no-bloqueante lo que no registrara o se difiriera. Premisa de diseño: el único MCP crítico es el TV MCP; todo lo demás degrada con ⚠️ y se sigue.

## Qué se hizo y por qué

### MCP-01 ✅ — `.mcp.json` con los 6 MCPs
- Creado `.mcp.json` con: tradingview (Node local, ruta verificada), firecrawl-mcp (npx + env var), task-master-ai (npx, claude-code/sonnet), tavily-mcp (npx + env var), context-mode, code-review-graph.
- **Secretos:** keys SOLO por variable de entorno; `.mcp.json` y `.env` quedan gitignored (`[FIX: P-07]`). No se migró a env vars de Windows — se quedan en `.env`/`.mcp.json` locales.
- En sesión cargaron tradingview, firecrawl, task-master, tavily, context-mode.
- ⚠️ **code-review-graph** no registró tools (binario OK en PATH, grafo creado con 0 nodos — sin código aún). No-bloqueante; se anotó para revisar más adelante. *(Resuelto en Sesion-005: el grafo queda vacío por naturaleza — no parsea Pine, P-12.)*

### MCP-02 ✅ — Sync fork TV MCP con upstream
- `git fetch upstream && git merge` en `D:\CODE\BOT\Bot\tradingview-mcp-jackson`. Merge de `upstream/main` (3 commits: validación de paths/dates, gitignore .env, subscribe banner) limpio. Fork quedó +4 ahead de origin (sin pushear).
- `tv_launch` + `tv_health_check` OK (CDP 9222), 81 tools.
- **Decisión/convención:** TradingView Desktop se lanza SIEMPRE por el MCP (`tv_launch`), nunca manual. (Ver [[preferencia-lanzar-tv-por-mcp]].)
- Nota: la excepción a la prohibición de `D:\CODE\BOT\Bot\` para el fork del TV MCP ya se había documentado en CLAUDE.md en Sesion-003 — es herramienta, no referencia de código.

### MCP-03 ⏳ DIFERIDO — Archon
- Se difirió por considerarse pesado y "requiere docker". No-bloqueante: el workplan contempla ejecutar los workflows manualmente si Archon no está. *(Retomado e instalado en Sesion-005, donde se descubrió que Archon cambió de arquitectura y ya no usa Docker — ver Sesion-005 §3 y [[estrategia2-archon-remote-agent-platform]].)*

### MCP-04 ✅ — claude-mem
- `npx claude-mem install`. `~/.claude-mem/` existe (db + corpora + logs). Verificación del dashboard quedó pendiente del usuario (no-bloqueante). *(Confirmado HTTP 200 en puerto 37777 en Sesion-005.)*

### MCP-05 ✅ — `rules.json` (morning_brief)
- `rules.json` reescrito: watchlist `FX:EURUSD`, TF 60 (H1), bias por ESTRUCTURA + premium/discount, R:R 1:3, alineado con ADR-001 (multi-símbolo, sin filtro horario duro).
- `morning_brief` devuelve quote + indicadores de EURUSD H1.
- **Ubicación:** `rules.json` vive en la raíz del repo-herramienta del TV MCP (de ahí lo lee `morning_brief` por defecto). Si futuros merges de upstream lo tocan, re-aplicar.

### MCP-06 ⏳ DIFERIDO — task-master parse
- Diferido como opcional: el workplan sigue siendo la fuente de verdad y un backlog paralelo podría divergir. *(En Sesion-005, decisión de Freddy: se ejecuta en el gate VER-09, tras la revisión de Fable, sobre el workplan ya validado.)*

## Decisiones de la sesión
- Storage de keys: `.mcp.json` + `.env`, ambos gitignored; sin migrar a env vars de Windows.
- TV se lanza siempre por el MCP (`tv_launch`).
- SEC-01 confirmado: el usuario revocó las keys viejas; las nuevas viven en `.env`/`.mcp.json` gitignored. Sin bloqueos de seguridad.
- Degradación elegante confirmada en la práctica: code-review-graph (⚠️), Archon y task-master diferidos no bloquearon el cierre del bloque.

## Cierre
Bloque C cerrado: 4 de 6 MCPs verificados (MCP-01/02/04/05), 2 diferidos no-bloqueantes (MCP-03 Archon, MCP-06 task-master), 1 ⚠️ anotado (code-review-graph sin tools). Commit `0ec79ae` — "cierre Bloque C — MCPs configurados y verificados". Siguiente: Bloque D (skills). *(Antes del Bloque D, Sesion-005 cerró los pendientes no-bloqueantes que quedaron aquí.)*
