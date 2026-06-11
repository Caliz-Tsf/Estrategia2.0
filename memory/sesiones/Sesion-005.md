# Sesión 005 — Cierre de pendientes no-bloqueantes del Bloque C + SCR-02 adelantado
> Fecha: 2026-06-11 · Fase 0 · Claude Code (Opus 4.8) + Freddy
> Registro de QUÉ se hizo, POR QUÉ, CON QUÉ FINALIDAD y QUÉ SE DECIDIÓ.
> **NOTA PARA FABLE:** esta sesión cierra los ⚠️ que quedaron abiertos en Sesion-004 (Bloque C) ANTES de entrar al Bloque D. El cambio más relevante a revisar es el de **Archon (MCP-03)**, que resultó ser una herramienta distinta a la que el workplan asumía.

## Objetivo de la sesión
Cerrar los pendientes no-bloqueantes anotados al final del Bloque C, para no arrastrarlos al Bloque D:
1. code-review-graph — reconstruir el grafo (estaba con 0 tools / 0 nodos).
2. MCP-03 Archon — instalar (estaba diferido por "requiere Docker").
3. MCP-06 task-master parse — decidir si se ejecuta.
4. claude-mem dashboard — confirmar que responde.
5. SCR-02 sync-obsidian.ps1 — **adelantarlo del Bloque F** (pedido de Freddy: empezar a respaldar en Obsidian ya).

## Qué se hizo y por qué

### 1. code-review-graph ✅ (reconstruido, pero su valor real es limitado)
- Binario `code-review-graph 2.3.2` OK en PATH. `build` corre limpio (FTS reconstruido), repo registrado como alias `estrategia2`, `serve` (MCP stdio) arranca bien.
- **El grafo queda en 0 nodos POR NATURALEZA, no por error:** el repo solo tiene 21 .md + 1 .pine + .gitignore. code-review-graph **no parsea Pine** (esto es exactamente el riesgo **P-12** del workplan) y el markdown no es código.
- **Implicación honesta para Fable:** la utilidad de esta herramienta en este proyecto es marginal — el sistema se escribe en Pine (no soportado) y luego MQL5. Confirmamos que el explorador usará Grep/Read como vía principal (ya previsto en P-12). Los tools del MCP deberían registrar al reiniciar la sesión; no es bloqueante para nada.

### 2. claude-mem dashboard ✅
- Responde HTTP 200 en `localhost:37777`. `~/.claude-mem/` con db + corpora + logs. Pendiente cerrado.

### 3. MCP-03 Archon ✅ INSTALADO — ⚠️ CAMBIÓ DE ARQUITECTURA (revisar)
- **Hallazgo:** Docker NO está instalado en el sistema, y al investigar los requisitos reales descubrimos que **el Archon actual ya no necesita Docker**. Más aún: **no es la herramienta que el workplan (Fable, 2026-06-10) describía.**
  - Workplan asumía: sistema tipo RAG/knowledge-base con Docker, "18 workflows default".
  - Archon real (coleam00/Archon **v0.4.1**): **"Remote Agentic Coding Platform"** — Bun + TypeScript + SQLite, controla asistentes de código (Claude Code SDK / Codex SDK) remotamente vía Slack/Telegram/GitHub, con un **motor de workflows DAG** (approval gates, loops, nodos prompt/bash/script/command).
- **Por qué SÍ sirve igual:** sus 20 workflows default incluyen `archon-architect` y `archon-validate-pr` — **exactamente los que el workplan referencia** (F4-T00 "archon-architect sweep", §4.4 "archon-validate-pr"). O sea, la pieza que necesitamos (motor de workflows DAG para `smc-sprint`) está y encaja. Solo la suposición de Docker estaba obsoleta.
- **Cómo quedó instalado:**
  - App clonada en **`D:\CODE\Archon`** (FUERA del repo). Inicialmente la cloné por error en `.archon/` dentro del proyecto y la moví, porque en el modelo real de Archon el `.archon/` del proyecto es para **tus propios** workflows/commands/config (ahí irá `smc-sprint.yaml` en WF-01).
  - `bun install` OK (2578 paquetes). `bun run cli doctor` → **All checks passed** (SQLite reachable, 20 workflows + 36 commands). Sin Docker. Slack/Telegram NO configurados (no se necesitan para correr workflows en local).
  - Binario Claude en `C:\Users\Fredd\.local\bin\claude.exe`; en dev mode el SDK resuelve vía node_modules.
- **Cómo se ejecuta (aclaración a Freddy):** Archon LANZA Claude por su cuenta (no hace falta otra IA). Se invoca desde una **terminal normal** con el wrapper `scripts/archon.ps1 <args>` (ej. `scripts/archon.ps1 workflow run smc-sprint "..."`).
- **⚠️ Trampa #1067:** NO correr workflows que invoquen Claude *desde dentro* de una sesión Claude Code (`CLAUDECODE=1`) — se cuelgan por anidamiento Claude-dentro-de-Claude. Usar terminal normal.

### 4. MCP-06 task-master → MOVIDO A VER-09 (decisión de Freddy)
- Estaba diferido por riesgo de **backlog divergente** del workplan (fuente de verdad viva).
- **Decisión de Freddy:** no generar el backlog ahora. Se ejecuta DENTRO del gate **VER-09 REVISIÓN-FABLE**: una vez construido todo (skills + agentes + MCPs + workflows de Bloques D/E/F) y que **Fable revise** que está bien creado, se corre `task-master parse-prd` sobre el workplan **ya validado** para producir el plan de escritura concreto de Fase 1. Así el backlog nace de una fuente aprobada y no diverge. CLI disponible (0.43.1).

### 5. SCR-02 sync-obsidian.ps1 ✅ (adelantado del Bloque F)
- Creado `scripts/sync-obsidian.ps1`: copia **incremental por hash SHA-256** de `memory/sesiones/` + `docs/adrs/` + `memory/ESTADO-ACTUAL.md` → vault `D:\obsidian\boveda MENTE\Mente\Estrategia2.0\`. Flag `-DryRun` simula; idempotente (re-run = 0 cambios).
- Dry-run correcto Y sync real ejecutado. El vault de respaldo ya está vivo (carpeta creada, 6 archivos). Recordatorio: lo prohibido es LEER `Estrategia-Nueva/`; escribir en `Estrategia2.0/` es el destino legítimo (CLAUDE.md).

## Cambios en archivos (este commit)
- `scripts/sync-obsidian.ps1` **(nuevo)** — SCR-02.
- `scripts/archon.ps1` **(nuevo)** — wrapper para invocar Archon contra el proyecto desde terminal normal.
- `.gitignore` — `.archon/` ya NO se ignora entero (la app vive fuera); solo `.archon/state/`, `.archon/artifacts/`, `.archon/*.local.yaml`, para que los workflows propios (WF-01) sean rastreables.
- `WORKPLAN-MAESTRO-V2.md` — MCP-03 ✅ (con nota de cambio de arquitectura), SCR-02 ✅, MCP-06 → VER-09.
- `memory/ESTADO-ACTUAL.md` — Sesion-005, notas de herramientas actualizadas.
- Memoria de Claude: `estrategia2-archon-remote-agent-platform.md` (índice MEMORY.md).

## Pendientes abiertos (sin cambios)
- Poblar casos ⏳PENDIENTE-TVMCP de reglas-smc-ict.md + aprobación final (gate VER-05) — necesita gráfico.
- **Siguiente paso: Bloque D (skills SKL-01..09 desde SKILLS.md).** Luego E (agentes) → F (WF-01 smc-sprint + SCR-01/03/04) → VER-01..08 → VER-09 (incluye el task-master del punto 4).

## Cierre
Los 5 pendientes no-bloqueantes quedaron resueltos o decididos. Nada queda colgando del Bloque C. El único punto que Fable debe mirar con atención es Archon: es una herramienta distinta a la planeada pero contiene lo que necesitamos (motor de workflows DAG); WF-01 deberá escribir `smc-sprint.yaml` contra el schema real de Archon v0.4.1, no contra el supuesto del plan original.
