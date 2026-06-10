# PLAN MAESTRO — Estrategia2.0
> Bot SMC/ICT para Forex EURUSD | TradingView Pine Script → MetaTrader 5 MQL5
> Generado: 2026-06-10 | Estado: PRE-EJECUCIÓN — solo planificación, nada ejecutado aún
> Par objetivo: EURUSD exclusivo hasta completar Fase 3 validada

---

## ARQUITECTURA DEL PROYECTO

```
D:\CODE\Estrategia2.0\     ← proyecto + vault Obsidian
D:\CODE\BOT\Bot\           ← EA MQL5 referencia (BotBase v3.0 — NO se migra código)
D:\obsidian\boveda MENTE\  ← vault personal (teoría SMC, cursos transcritos)
```

### Flujo de desarrollo por fases

```
FASE 0   → Entorno completo configurado
FASE 1   → Pine Script Capa 1: todos los conceptos SMC/ICT visualizados (Tier 1-3)
FASE 2   → Pine Script Capa 2: motor de decisión, 57 confluencias, scoring
FASE 3   → Validación TradingView: 500 velas H1 + paper trading 30 días
FASE 4   → EA MetaTrader 5: 5 módulos MQL5 + Expert Advisor
```

### Workflow de 3 agentes (regla permanente)

```
CLAUDE CODE    → Supervisión, arquitectura, revisión, Pine Script, TV MCP, agentes
ANTIGRAVITY    → SOLO escribe código MQL5 / PowerShell / JSON del EA
               → Claude Code revisa: integración correcta + cumple requisitos + errores
               → Loop revisión-corrección hasta aprobación de Claude Code
CLAUDE DESKTOP → SOLO verificación visual MT5 (compilación, Strategy Tester, screenshots EA)
               → Ya NO se usa para TradingView (TV MCP lo reemplaza)
```

### Multi-timeframe SMC/ICT
- **D1** → Contexto (Premium/Discount, bias macro)
- **H1** → Bias (CHoCH, BOS, OB, FVG activos)
- **M5** → Entrada (OB/FVG de precisión, Kill Zones)
- **R:R mínimo:** 1:3 sin excepción
- **Kill Zones:** London 08-10 GMT, NY 13-15 GMT

---

## PRE-FASE 0 — Preparación del entorno

> Ejecutar ANTES de comenzar cualquier desarrollo. Son mejoras y configuraciones base.

### BLOQUE A — Repositorios y herramientas

| ID | Tarea | Descripción | Herramienta |
|---|---|---|---|
| TV-MCP-01 | Sincronizar fork con upstream | Sync `Caliz-Tsf/tradingview-mcp-jackson` con `LewisWJackson/tradingview-mcp-jackson`. Incorporar: 3 tools faltantes (total 81), fix TV v2.14+, CLI `tv`, `rules.json` nativo. | `git fetch upstream && git merge upstream/main` |
| LAUNCH-01 | Mejorar launch-tv-agent.ps1 | Actualizar script en `scripts/launch-tv-agent.ps1`: fix para TV v2.14+, auto-cargar indicador SMC al arrancar, integrar `tv_health_check`, agregar `rules.json` con bias criteria SMC EURUSD. | PowerShell |
| ARCHON-01 | Reinstalar Archon v2 | Clonar `github.com/coleam00/Archon` en `Estrategia2.0/.archon/`. Crear `smc-sprint.yaml`. Migrar custom commands `maintainer-review-*` y `maintainer-standup`. | `git clone` |
| MEM-01 | Actualizar claude-mem | Actualizar de v12.1.5 → v13.4.1 (última estable). Verificar dashboard `http://localhost:37777`. | `npx claude-mem install` |

### BLOQUE B — MCPs

| ID | Tarea | Descripción |
|---|---|---|
| CTX-01 | Configurar context-mode | Agregar reglas en CLAUDE.md: qué NO comprimir (docs/reglas-smc-ict.md, PLAN-BOT-SMC-ICT.md, estado de fase actual). Usar en sesiones largas (>1h). |
| CRG-01 | Configurar code-review-graph | Limitar a 5 tools: `query_graph_tool`, `get_review_context_tool`, `detect_changes_tool`, `get_impact_radius_tool`, `semantic_search_nodes_tool`. Inicializar grafo en Estrategia2.0. |
| FIRE-01 | Configurar firecrawl | Usar `firecrawl_monitor` para Pine Script docs + MQL5 docs. Usar `firecrawl_agent` para research SMC/ICT (documentación LuxAlgo, artículos ICT). |
| TM-01 | Configurar task-master | Modelo: `claude-code/sonnet` (sin API key, usa Claude Pro plan). Ejecutar `task-master parse-prd PLAN-BOT-SMC-ICT.md` para generar backlog inicial. |
| MEM-02 | Configurar claude-mem | Crear `~/.claude-mem/settings.json`: modo `code`, puerto `37777`, context injection activado. |

### BLOQUE C — Obsidian y memoria

| ID | Tarea | Descripción |
|---|---|---|
| OBS-01 | Reset vault Obsidian | Borrar TODO el contenido interno de `D:\obsidian\boveda MENTE\`. Recrear estructura limpia: `Mente\Teoria SMC\` + `Mente\Estrategia2.0\`. |
| OBS-02 | Configurar .obsidian/ | Configurar `Estrategia2.0\.obsidian\` (el vault del proyecto): plugins Dataview (queries de ADRs/runs) + Git (backup automático de notas). |
| MEM-03 | Verificar MEM-03 en startup | Agregar `http://localhost:37777` al startup obligatorio para verificar que claude-mem está activo. |

---

## FASE 0 — Configuración base del proyecto

> Todo lo que debe existir ANTES de escribir la primera línea de Pine Script.
> Orden de ejecución: A → B → C → D → E → F

### A — Documentos base (fuentes de verdad)

| ID | Archivo a crear | Contenido |
|---|---|---|
| DOC-01 | `docs/reglas-smc-ict.md` | Fuente de verdad SMC/ICT: definiciones exactas de BOS, CHoCH, OB, FVG, EQH/EQL, Premium/Discount, Kill Zones, Liquidity Sweeps, MSS. Con ejemplos visuales en ASCII. |
| DOC-02 | `docs/reglas-dev.md` | Reglas de desarrollo: convenciones Pine Script v6, naming, estructura de código, commits, branching, cuándo crear ADR. |
| DOC-03 | `docs/WORKFLOW-ARQUITECTURA.md` | Workflow 3 agentes actualizado: Claude Code + Antigravity (con loop revisión) + Claude Desktop. |
| DOC-04 | `docs/TV-SMC-WORKFLOW.md` | Protocolo TradingView 5 fases: STARTUP → DESARROLLO → VALIDACIÓN VISUAL → BACKTESTING → CIERRE. |
| DOC-05 | `docs/pendientes-fase8.md` | Instalaciones pospuestas: TradingAgents + TA-Lib (Fase 8), Hermes API key + hermes init (Fase 8B), multica (Sprint 4+), GenericAgent (Sprint 3+). |
| DOC-06 | `docs/lecciones-estrategia-nueva.md` | ADR-001..006 históricos de Estrategia-Nueva con estado "HISTÓRICO". Decisiones que aplican al nuevo proyecto. |
| DOC-07 | `docs/referencia-botbase.md` | Algoritmos del BotBase v3.0 reutilizables en Fase 4: detección OB, FVG (dual-box + CE 50%), EQH/EQL. Los 175 golden tests como benchmark. |

### B — Configuración de entorno

| ID | Archivo a crear | Contenido |
|---|---|---|
| CFG-01 | `.mcp.json` | 6 MCPs: tradingview (local Node.js), firecrawl-mcp (npx), task-master-ai (npx, claude-code/sonnet), tavily-mcp (npx), context-mode (global), code-review-graph (global, 5 tools). |
| CFG-02 | `rules.json` | Config morning_brief: watchlist EURUSD, criteria bullish/bearish/neutral H1 (CHoCH, BOS, FVG, OB, EMA200), risk rules (Kill Zones, R:R 1:3), timeframes D/60/5. |
| CFG-03 | `CLAUDE.md` | Principios Karpathy + reglas SMC + contexto del proyecto. Incluir: qué NO comprimir (context-mode), workflow 3 agentes, convenciones de código, startup/cierre obligatorio. |
| CFG-04 | `memory/ESTADO-ACTUAL.md` | Estado inicial: Fase 0 en progreso. Template para actualizar al cierre de cada sesión. |

### C — Skills custom SMC (9 skills)

Instalar en `Estrategia2.0\.claude\skills\`:

| ID | Skill | Basada en | Adiciones SMC |
|---|---|---|---|
| SKL-01 | `smc-pine-develop` | `pine-develop` (TV MCP) | Validación contra reglas-smc-ict.md, compilación con 0 errores/warnings, nomenclatura SMC |
| SKL-02 | `smc-chart-analysis` | `chart-analysis` (TV MCP) | Lectura de confluencias activas EURUSD, bias H1, zonas Premium/Discount |
| SKL-03 | `smc-replay` | `replay-practice` (TV MCP) | Protocolo de backtesting manual: fecha → señal → registro → siguiente |
| SKL-04 | `smc-multi-scan` | `multi-symbol-scan` (TV MCP) | Solo EURUSD (bloqueado hasta Fase 3) — template para expansión futura |
| SKL-05 | `smc-validator` | Nueva | Verifica conceptos SMC contra reglas-smc-ict.md. Input: screenshot. Output: score por confluencia. |
| SKL-06 | `smc-backtesting-analyst` | Nueva | Analiza runs de backtesting: win rate, R:R promedio, distribución por Kill Zone, por fase de mercado. |
| SKL-07 | `mql5-translator` | Nueva | Traduce lógica Pine Script → MQL5 siguiendo arquitectura modular (5 módulos). Usa docs/reglas-dev.md. |
| SKL-08 | `smc-session-startup` | Nueva | Ejecuta protocolo startup: ESTADO-ACTUAL → latent-briefing → git branch → autoplan → tv_health_check → crg:build → morning_brief. |
| SKL-09 | `smc-session-close` | Nueva | Ejecuta protocolo cierre: checkpoint → commits pendientes → actualizar ESTADO-ACTUAL → ADR si aplica → sync-obsidian.ps1. |

### D — Agentes custom SMC (7 agentes)

Instalar en `Estrategia2.0\.claude\agents\`:

| ID | Agente | Modelo | Propósito |
|---|---|---|---|
| AGT-01 | `smc-validator-agent` | Sonnet | Valida implementaciones Pine Script contra reglas-smc-ict.md. Inspecciona screenshots. Score por concepto. |
| AGT-02 | `smc-backtesting-analyst-agent` | Sonnet | Analiza JSON de runs. Detecta patrones de pérdida. Sugiere ajustes al scoring de confluencias. |
| AGT-03 | `mql5-translator-agent` | Opus | Traduce Pine Script validado → MQL5 modular. Alta complejidad. Usa Opus por precisión. |
| AGT-04 | `smc-architect` | Opus | Decisiones de arquitectura del indicador y EA. ADRs. Diseño de los 57 confluence inputs. |
| AGT-05 | `mql5-reviewer` | Sonnet | Revisión de código MQL5: performance (<50ms/tick), memory (<100MB), ICT accuracy (>94%). |
| AGT-06 | `smc-code-explorer` | Sonnet | Exploración del codebase Pine Script y MQL5. AST analysis via code-review-graph. |
| AGT-07 | `smc-doc-updater` | Sonnet | Mantiene docs/reglas-smc-ict.md, ADRs y memory/ESTADO-ACTUAL.md actualizados tras cada sesión. |

### E — Archon v2 workflows

| ID | Workflow | Cuándo usar |
|---|---|---|
| WF-01 | `smc-sprint.yaml` (custom) | Ciclo SMC: spec → implement loop → validate → approve → commit. Para todo Fase 1 y Fase 2. |
| WF-02 | `archon-piv-loop` | Plan-Implement-Validate con aprobación humana. Principal workflow de desarrollo. |
| WF-03 | `archon-refactor-safely` | Refactoring entre Tiers (Fase 1) sin romper lo existente. |
| WF-04 | `archon-test-loop-dag` | Loop hasta que 175 golden tests pasen. Fase 4. |
| WF-05 | `archon-validate-pr` | Antes de cada merge en el repo del EA. Fase 4. |
| WF-06 | `archon-architect` | Sweep arquitectural del EA antes de traducir Pine→MQL5. Inicio Fase 4. |
| WF-07 | `archon-feature-development` | Implementar un feature completo desde plan hasta PR. Fases 1 y 4. |

### F — Scripts

| ID | Script | Descripción |
|---|---|---|
| SCR-01 | `scripts/launch-tv-agent.ps1` | Mejorado (LAUNCH-01): TV v2.14+ fix, auto-load indicador SMC, tv_health_check, rules.json integrado. |
| SCR-02 | `scripts/sync-obsidian.ps1` | Copia `memory/Sesión-X.md` + `docs/adrs/` nuevos → `D:\obsidian\boveda MENTE\Mente\Estrategia2.0\`. |
| SCR-03 | `scripts/process-video.ps1` | Pipeline: YouTube URL → yt-dlp → FFmpeg → Whisper → .md → `D:\obsidian\boveda MENTE\Mente\Teoria SMC\`. |

---

## PROTOCOLO DE SESIÓN (permanente desde Fase 0)

### Startup obligatorio

```
1. memory/ESTADO-ACTUAL.md       → leer estado del proyecto
2. /latent-briefing              → comprimir si sesión >1h desde última
3. git branch                    → verificar rama activa
4. /autoplan                     → plan automático de la sesión
5. tv_health_check               → verificar TradingView + MCP (81 tools)
6. code-review-graph build       → actualizar grafo del código
7. http://localhost:37777        → verificar claude-mem activo
8. morning_brief                 → bias SMC EURUSD del día (si sesión de validación)
```

### Cierre obligatorio

```
AUTOMÁTICO (claude-mem):
  → Comprime observaciones técnicas de la sesión → SQLite local

MANUAL (smc-session-close skill):
1. /checkpoint                   → guardar estado de sesión
2. git add -A && git commit      → commits pendientes
3. memory/ESTADO-ACTUAL.md       → actualizar estado
4. Si ADR → docs/adrs/ADR-X.md  → documentar decisión arquitectural
5. Si run → docs/sprint-runs/    → guardar JSON resultado
6. /freeze (si fase completa)    → snapshot estable
7. sync-obsidian.ps1             → sincronizar Sesión-X.md al vault personal
```

---

## ESTRUCTURA DE DIRECTORIOS OBJETIVO (fin de Fase 0)

```
D:\CODE\Estrategia2.0\
│
├── .claude/
│   ├── agents/                        ← 7 agentes custom SMC
│   │   ├── smc-validator-agent.md
│   │   ├── smc-backtesting-analyst-agent.md
│   │   ├── mql5-translator-agent.md
│   │   ├── smc-architect.md
│   │   ├── mql5-reviewer.md
│   │   ├── smc-code-explorer.md
│   │   └── smc-doc-updater.md
│   └── skills/                        ← 9 skills SMC + 39 de GitHub
│       ├── smc-pine-develop/
│       ├── smc-chart-analysis/
│       ├── smc-replay/
│       ├── smc-multi-scan/
│       ├── smc-validator/
│       ├── smc-backtesting-analyst/
│       ├── mql5-translator/
│       ├── smc-session-startup/
│       └── smc-session-close/
│
├── .obsidian/                         ← vault Obsidian del proyecto (configurar Dataview + Git plugin)
├── .mcp.json                          ← 6 MCPs configurados
│
├── .archon/
│   ├── config.yaml
│   ├── workflows/
│   │   ├── defaults/                  ← 18 YAML Archon oficiales
│   │   └── smc-sprint.yaml           ← workflow custom SMC
│   └── commands/defaults/             ← maintainer-review-* commands
│
├── .context-mode/                     ← context-mode v1.0.111+
├── .code-review-graph/graph.db        ← grafo de código (inicializar en Fase 0)
│
├── pine/
│   ├── SMC-ICT-Indicator.pine        ← BASE: archivo LuxAlgo existente → evoluciona Capa 1 + Capa 2
│   └── reference/
│       ├── LuxAlgo-SMC-Historical.pine
│       └── LuxAlgo-SMC-Flow.pine
│
├── mt5/                               ← vacío hasta Fase 4
│   ├── Experts/EA_SMC_ICT.mq5
│   └── Include/
│       ├── SMC_Structures.mqh
│       ├── SMC_MTF.mqh
│       ├── SMC_Scoring.mqh
│       ├── SMC_RiskManager.mqh
│       └── SMC_Display.mqh
│
├── docs/
│   ├── adrs/                          ← ADR-001..006 históricos + nuevos desde Fase 0
│   ├── sprint-runs/                   ← JSON runs Fase 3
│   ├── reglas-smc-ict.md             ← FUENTE DE VERDAD SMC (DOC-01)
│   ├── reglas-dev.md                  ← reglas de desarrollo (DOC-02)
│   ├── WORKFLOW-ARQUITECTURA.md       ← workflow 3 agentes (DOC-03)
│   ├── TV-SMC-WORKFLOW.md             ← protocolo TV 5 fases (DOC-04)
│   ├── pendientes-fase8.md            ← instalaciones pospuestas (DOC-05)
│   ├── lecciones-estrategia-nueva.md  ← ADRs históricos (DOC-06)
│   └── referencia-botbase.md          ← lógica reutilizable BotBase v3.0 (DOC-07)
│
├── scripts/
│   ├── launch-tv-agent.ps1            ← mejorado (SCR-01)
│   ├── sync-obsidian.ps1              ← sync al vault personal (SCR-02)
│   └── process-video.ps1              ← pipeline transcripción videos SMC (SCR-03)
│
├── memory/
│   └── ESTADO-ACTUAL.md               ← estado inter-sesión (actualizar en cada cierre)
│
├── CLAUDE.md                          ← Karpathy + reglas SMC + contexto proyecto (CFG-03)
├── PLAN-BOT-SMC-ICT.md               ← plan de desarrollo por fases (ya existe)
├── PLAN-MAESTRO-FASE0.md             ← este documento
└── rules.json                         ← config morning_brief SMC EURUSD (CFG-02)
```

---

## CHECKLIST COMPLETO — ORDEN DE EJECUCIÓN

### PRE-FASE 0 (ejecutar antes de abrir el proyecto en Claude Code)

- [ ] **OBS-01** — Reset vault Obsidian: borrar contenido de `D:\obsidian\boveda MENTE\`, recrear `Mente\Teoria SMC\` + `Mente\Estrategia2.0\`
- [ ] **MEM-01** — Actualizar claude-mem: `npx claude-mem install` (v12.1.5 → v13.4.1)
- [ ] **TV-MCP-01** — Sync fork tradingview-mcp-jackson con upstream (81 tools, TV v2.14+ fix)
- [ ] **ARCHON-01** — Reinstalar Archon v2: clonar en `.archon/`, verificar 18 workflows default

### FASE 0 — Bloque A: Documentos base

- [ ] **DOC-01** — Crear `docs/reglas-smc-ict.md` (fuente de verdad SMC)
- [ ] **DOC-02** — Crear `docs/reglas-dev.md` (reglas de desarrollo)
- [ ] **DOC-03** — Crear `docs/WORKFLOW-ARQUITECTURA.md`
- [ ] **DOC-04** — Crear `docs/TV-SMC-WORKFLOW.md`
- [ ] **DOC-05** — Crear `docs/pendientes-fase8.md`
- [ ] **DOC-06** — Crear `docs/lecciones-estrategia-nueva.md`
- [ ] **DOC-07** — Crear `docs/referencia-botbase.md`

### FASE 0 — Bloque B: Configuración

- [ ] **CFG-01** — Crear `.mcp.json` (6 MCPs)
- [ ] **CFG-02** — Crear `rules.json` (morning_brief SMC EURUSD)
- [ ] **CFG-03** — Crear `CLAUDE.md` (Karpathy + reglas SMC)
- [ ] **CFG-04** — Crear `memory/ESTADO-ACTUAL.md`
- [ ] **MEM-02** — Configurar `~/.claude-mem/settings.json`
- [ ] **OBS-02** — Configurar `.obsidian/` (Dataview + Git plugin)
- [ ] **CTX-01** — Agregar reglas context-mode en CLAUDE.md
- [ ] **CRG-01** — Configurar code-review-graph (5 tools) + inicializar grafo
- [ ] **TM-01** — Configurar task-master (claude-code/sonnet) + parse-prd
- [ ] **FIRE-01** — Configurar firecrawl (monitor Pine/MQL5 docs)

### FASE 0 — Bloque C: Skills (9 custom)

- [ ] **SKL-01** — Crear skill `smc-pine-develop`
- [ ] **SKL-02** — Crear skill `smc-chart-analysis`
- [ ] **SKL-03** — Crear skill `smc-replay`
- [ ] **SKL-04** — Crear skill `smc-multi-scan`
- [ ] **SKL-05** — Crear skill `smc-validator`
- [ ] **SKL-06** — Crear skill `smc-backtesting-analyst`
- [ ] **SKL-07** — Crear skill `mql5-translator`
- [ ] **SKL-08** — Crear skill `smc-session-startup`
- [ ] **SKL-09** — Crear skill `smc-session-close`
- [ ] **SKL-10** — Instalar 39 skills de GitHub (obra/superpowers + addyosmani/agent-skills)

### FASE 0 — Bloque D: Agentes (7 custom)

- [ ] **AGT-01** — Crear agente `smc-validator-agent`
- [ ] **AGT-02** — Crear agente `smc-backtesting-analyst-agent`
- [ ] **AGT-03** — Crear agente `mql5-translator-agent` (Opus)
- [ ] **AGT-04** — Crear agente `smc-architect` (Opus)
- [ ] **AGT-05** — Crear agente `mql5-reviewer`
- [ ] **AGT-06** — Crear agente `smc-code-explorer`
- [ ] **AGT-07** — Crear agente `smc-doc-updater`

### FASE 0 — Bloque E: Archon workflows

- [ ] **WF-01** — Crear `smc-sprint.yaml`
- [ ] **WF-02** — Verificar y activar custom commands `maintainer-review-*`

### FASE 0 — Bloque F: Scripts

- [ ] **SCR-01** — Crear/mejorar `scripts/launch-tv-agent.ps1` (LAUNCH-01)
- [ ] **SCR-02** — Crear `scripts/sync-obsidian.ps1`
- [ ] **SCR-03** — Crear `scripts/process-video.ps1`

### FASE 0 — Verificación final

- [ ] **VER-01** — Ejecutar `tv_health_check` → verificar 81 tools activos
- [ ] **VER-02** — Ejecutar skill `smc-session-startup` → verificar startup completo sin errores
- [ ] **VER-03** — Ejecutar `morning_brief` con `rules.json` → verificar output EURUSD H1
- [ ] **VER-04** — Verificar `http://localhost:37777` → claude-mem activo
- [ ] **VER-05** — Verificar code-review-graph con `query_graph_tool` → grafo inicializado
- [ ] **VER-06** — Abrir `D:\CODE\Estrategia2.0\` en Obsidian → vault funcional, notas visibles
- [ ] **VER-07** — `git status` limpio → todo commiteado

---

## FASES DE DESARROLLO (resumen — detalle en PLAN-BOT-SMC-ICT.md)

### FASE 1 — Pine Script Capa 1 (visualización completa)

Base: `pine/SMC-ICT-Indicator.pine` (archivo LuxAlgo existente)
Workflow: `smc-sprint.yaml` + `archon-piv-loop`
Herramientas: TV MCP + smc-pine-develop + smc-validator-agent + smc-chart-analysis

**Tier 1 — Estructura de mercado:**
- BOS (Break of Structure) alcista y bajista
- CHoCH (Change of Character) interno y swing
- MSS (Market Structure Shift)

**Tier 2 — Zonas de liquidez:**
- Order Blocks (OB) alcistas y bajistas — base: algoritmo LuxAlgo
- Fair Value Gaps (FVG) con equilibrium 50% (CE)
- Liquidity Sweeps (BSL/SSL)
- Equal Highs/Lows (EQH/EQL)

**Tier 3 — Contexto multi-timeframe:**
- Premium/Discount zones D1
- Bias H1 (integración D1 → H1)
- Kill Zones M5 (London + NY)
- EMA 200 H1

### FASE 2 — Pine Script Capa 2 (motor de decisión)

- 57 confluence inputs con scoring ponderado
- Señal de entrada cuando score ≥ umbral (definir en Fase 3)
- Panel de estado en tiempo real (tabla Pine)
- Sistema de alertas (TradingView alerts vía `alert_create`)

### FASE 3 — Validación TradingView

- 500 velas H1 EURUSD backtesting visual con `smc-replay`
- 30 días paper trading
- Criterios de éxito: win rate ≥ X%, R:R promedio ≥ 1:3, max drawdown ≤ Y%
- Score mínimo definitivo para señales
- Análisis con `smc-backtesting-analyst-agent`
- Runs guardados en `docs/sprint-runs/` (JSON)

### FASE 4 — MetaTrader 5 Expert Advisor

Arquitectura modular (5 módulos + EA principal):

| Módulo | Responsabilidad |
|---|---|
| `SMC_Structures.mqh` | Detección BOS/CHoCH/MSS en tiempo real |
| `SMC_MTF.mqh` | Análisis multi-timeframe D1+H1+M5 |
| `SMC_Scoring.mqh` | Motor de 57 confluencias y scoring |
| `SMC_RiskManager.mqh` | Gestión de riesgo, SL/TP, trailing stop |
| `SMC_Display.mqh` | Panel visual en MT5 |
| `EA_SMC_ICT.mq5` | Expert Advisor principal (orquesta módulos) |

Targets de performance (heredados de BotBase v3.0):
- < 50ms por tick
- < 100MB RAM
- > 94% ICT accuracy
- 175/175 golden tests verde

Flujo de traducción: `mql5-translator-agent` (Opus) → Antigravity escribe → Claude Code revisa → compilar en MetaEditor → Claude Desktop verifica visual en MT5

---

## POSPUESTO — No instalar hasta la fase indicada

| Herramienta | Fase | Instalación |
|---|---|---|
| TradingAgents (Python) | Fase 8 (Live Trading) | `pip install tradingagents` |
| TA-Lib Python | Fase 8 | `pip install TA-Lib` |
| Hermes API key | Fase 8B | `ANTHROPIC_API_KEY` en `~/.hermes/.env` + `hermes init` |
| multica v0.2.25 | Sprint 4+ | `npm install -g multica` |
| GenericAgent | Sprint 3+ | `~/.claude/GenericAgent/` (ya clonado) |

> **Nota Hermes:** Activar solo DESPUÉS de reconstruir base de conocimiento SMC con transcripciones de videos via `process-video.ps1`. Sin contenido indexado, Hermes no tiene nada que consultar.

---

## MCPs CONFIGURADOS EN .mcp.json

```json
{
  "mcpServers": {
    "tradingview": {
      "command": "C:\\Program Files\\nodejs\\node.exe",
      "args": ["D:\\CODE\\BOT\\Bot\\tradingview-mcp-jackson\\src\\server.js"],
      "cwd": "D:\\CODE\\BOT\\Bot\\tradingview-mcp-jackson"
    },
    "firecrawl-mcp": {
      "command": "npx",
      "args": ["-y", "firecrawl-mcp"],
      "env": {
        "FIRECRAWL_API_KEY": "fc-b474081cd20c43f5ad084896c2c406dd",
        "FIRECRAWL_RETRY_MAX_ATTEMPTS": "5",
        "FIRECRAWL_CREDIT_WARNING_THRESHOLD": "2000",
        "FIRECRAWL_CREDIT_CRITICAL_THRESHOLD": "500"
      }
    },
    "task-master-ai": {
      "command": "npx",
      "args": ["-y", "task-master-ai"],
      "env": { "TASK_MASTER_TOOLS": "standard" }
    },
    "tavily-mcp": {
      "command": "npx",
      "args": ["-y", "tavily-mcp@latest"],
      "env": { "TAVILY_API_KEY": "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" }
    },
    "context-mode": { "command": "context-mode" },
    "code-review-graph": {
      "command": "code-review-graph",
      "args": ["serve", "--tools", "query_graph_tool,get_review_context_tool,detect_changes_tool,get_impact_radius_tool,semantic_search_nodes_tool"],
      "env": { "PYTHONUTF8": "1" }
    }
  }
}
```

## rules.json (morning_brief SMC EURUSD)

```json
{
  "watchlist": ["EURUSD"],
  "bias_criteria": {
    "bullish": [
      "CHoCH alcista confirmado en H1",
      "BOS alcista en H1",
      "Precio en Discount Zone H1",
      "FVG alcista H1 activo no mitigado",
      "OB alcista H1 activo",
      "Liquidity Sweep bajista previo",
      "Precio sobre EMA 200 H1"
    ],
    "bearish": [
      "CHoCH bajista confirmado en H1",
      "BOS bajista en H1",
      "Precio en Premium Zone H1",
      "FVG bajista H1 activo no mitigado",
      "OB bajista H1 activo",
      "Liquidity Sweep alcista previo",
      "Precio bajo EMA 200 H1"
    ],
    "neutral": [
      "Precio en Equilibrium H1",
      "Sin CHoCH ni BOS reciente",
      "EMAs en compresión"
    ]
  },
  "risk_rules": [
    "No entrar fuera de Kill Zone (London 08-10 GMT, NY 13-15 GMT)",
    "Score mínimo requerido: definir al completar Fase 3",
    "R:R mínimo 1:3 obligatorio — sin excepción",
    "Solo EURUSD hasta completar Fase 3 validada",
    "SL siempre debajo/encima del OB o swing que justifica la entrada"
  ],
  "timeframes": {
    "context": "D",
    "bias": "60",
    "entry": "5"
  }
}
```

---

*Documento compilado: 2026-06-10*
*Próximo paso: Ejecutar checklist PRE-FASE 0, luego iniciar Fase 0 Bloque A*
