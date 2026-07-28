# CLAUDE.md — Estrategia 2.0

> **Este archivo es un MAPA, no doctrina. Techo: 40 líneas.** Dice qué documentos existen y
> cuándo ir a cada uno. El detalle vive en los documentos madre — **ve y léelos**.
> Si necesitas añadir una regla, va al documento que le corresponde, no aquí.

## El proyecto
Bot de trading **SMC/ICT** para Forex. Primero un sistema completo y validado en **TradingView
(Pine Script v6)**; después un **Expert Advisor 100% nativo en MQL5** que lo replica.
**Sin puente webhook** — el EA es autónomo. Idioma del proyecto: **español**, en todo.

## ⚠️ Leer SIEMPRE al arrancar, en este orden
| | Documento | Qué es |
|---|---|---|
| 1 | [memory/ESTADO-ACTUAL.md](memory/ESTADO-ACTUAL.md) | **Bloqueante.** Estado vivo: fase, tarea, cómo arrancar esta sesión. Rota, no acumula (techo 40 KB). |
| 2 | [docs/REGLAS-DURAS.md](docs/REGLAS-DURAS.md) | **Innegociable.** Las 8 reglas duras, la prohibición de referencias externas, la arquitectura que no se re-litiga, el workflow y el protocolo de sesión. |

**Frontera absoluta, sin excepción:** la única referencia externa permitida es LuxAlgo
(`pine/reference/LuxAlgo-SMC-base.pine`). **PROHIBIDO** leer o copiar `D:\CODE\BOT\Bot\` (EA
antiguo) o cualquier vault previo. El detalle y la única excepción, en `docs/REGLAS-DURAS.md`.

## Documentos madre — dónde está cada cosa
| Documento | Qué contiene | Cuándo ir |
|---|---|---|
| [WORKPLAN-MAESTRO-V2.md](WORKPLAN-MAESTRO-V2.md) + [docs/workplan/](docs/workplan/) | **Fuente de verdad del plan.** Fases, sprints, tareas con ID, gates. `PINE-PLAN.md` y `MQL5-PLAN.md` en la carpeta. | Al planificar, al cerrar una tarea, al mirar un gate. |
| [docs/reglas-smc-ict.md](docs/reglas-smc-ict.md) | **Fuente de verdad SMC.** Definiciones cuantificadas §0-§7. Si cambia ahí, cambia en todo el sistema. **Grande (~231 KB): entra por sección, no lo leas entero.** | Antes de implementar CUALQUIER concepto. Gate: sin regla cuantificada no se codifica. |
| [docs/adrs/](docs/adrs/README.md) | Decisiones de arquitectura ADR-001…027, con índice y huecos explicados. No se re-litigan. | Antes de proponer un cambio estructural. |
| [docs/reglas-dev.md](docs/reglas-dev.md) | Convenciones de código, naming, commits (Conventional Commits + ID de tarea). | Al escribir código o commitear. |
| [memory/sesiones/](memory/sesiones/) | Historial completo, un fichero por sesión. Aquí vive el pasado, **no** en ESTADO-ACTUAL. | Al buscar por qué se decidió algo, o qué se midió ya. |
| [docs/WORKFLOW-ARQUITECTURA.md](docs/WORKFLOW-ARQUITECTURA.md) | Quién hace qué: agentes internos, skills, reparto en Fase 4. | Al delegar o dudar de quién ejecuta. |
| [docs/TV-SMC-WORKFLOW.md](docs/TV-SMC-WORKFLOW.md) | Protocolo TradingView en 5 fases (startup → cierre). | En cualquier sesión que toque TV. |
| [docs/CONECTORES-MCP.md](docs/CONECTORES-MCP.md) | Conectores MCP montados (TV, MT5), config y cómo lanzarlos. | Al montar o diagnosticar herramientas. |
| [docs/planes/](docs/planes/) | Diseños, dossiers de Fable, esqueletos y mediciones puntuales. | Cuando un ADR o una sesión apunte a un plan concreto. |
| [pine/](pine/) · [scripts/](scripts/) | El código (`SMC-Visual`, `SMC-Strategy`, `SMC-Context`) y las herramientas (`check-core-sync.ps1`, `sync-obsidian.ps1`, tooling Pine). | Al implementar y al cerrar sesión. |

## Protocolo de sesión
Arranque `/smc-session-startup` · cierre `/smc-session-close`. Ambos detallados en
`docs/REGLAS-DURAS.md`. **Fase y siguiente paso exactos: siempre en `memory/ESTADO-ACTUAL.md`.**
