# Sesión 002 — Bloque B: documentos informativos + giro a proyecto limpio
> Fecha: 2026-06-10 · Fase 0 · Claude Code (Opus 4.8) + Freddy
> Registro de QUÉ se hizo, POR QUÉ, CON QUÉ FINALIDAD y QUÉ SE DECIDIÓ.

## Objetivo de la sesión
Continuar el plan acordado en Sesion-001: escribir TODO lo informativo (documentos sin gráfico) antes de la fase visual, para validarlo con Fable. Antes de empezar, Freddy preguntó por qué aún no se instalan agentes/skills/workflows.

## Aclaración de inicio — ¿en qué fase quedaron los agentes/skills?
Se explicó que **no cambiaron de fase**: siguen siendo Fase 0, bloques D (skills), E (agentes), F (workflows). Van **después** de los documentos a propósito (decisión R-11/P-14): el `smc-validator-agent` consume DOC-01 (reglas cuantificadas) como su spec; crearlos antes sería cáscaras vacías. Orden real: DOC-01 ✅ → resto de docs → Bloque C MCPs → D skills → E agentes → F workflows → gate.

## Qué se hizo, por qué y con qué finalidad

### Documentos informativos del Bloque B
| Doc | Archivo | Por qué / finalidad |
|---|---|---|
| **DOC-02** | `docs/reglas-dev.md` | Convenciones de cómo se escribe el código (Pine v6 naming/estructura/anti-repaint/performance, MQL5, commits, branching, cuándo ADR, ciclo por concepto). La skill `smc-pine-develop` lo referencia en su step check-rule. |
| **DOC-03** | `docs/WORKFLOW-ARQUITECTURA.md` | Quién ejecuta qué: los 2 niveles de orquestación (trío externo de Fase 4 + 8 agentes/9 skills internos), regla "workflows orquestan, agentes ejecutan, skills definen protocolo", degradación elegante. |
| **DOC-04** | `docs/TV-SMC-WORKFLOW.md` | Protocolo de trabajo contra TradingView en 5 fases (startup→desarrollo→validación visual→backtesting→cierre) con tools MCP por fase. |
| **DOC-07** | `CLAUDE.md` | Contexto + reglas duras + protocolo de sesión + qué no comprimir. <150 líneas. Incluye la regla absoluta de referencia externa única (LuxAlgo). |

### Gate de revisión-Fable (VER-09) — petición de Freddy
Se registró un **gate nuevo VER-09 REVISIÓN-FABLE** en el workplan §3 (Fase 0) y en ESTADO-ACTUAL: al terminar todo el Bloque F, se entrega el sistema completo y estructurado a Fable para revisión integral **antes de escribir una línea de Pine**. Ningún código antes de pasar el gate.

## Decisión importante — proyecto NUEVO, solo LuxAlgo
**Freddy frenó la lectura del BotBase y del proyecto anterior.** Instrucción explícita: *"este proyecto es único y no se debe tocar nada de la carpeta bot; la única referencia es el indicador de trading SMC de LuxAlgo, y esto debe quedar claro."*

**Por qué se borró DOC-06:** estaba definido como leer dos fuentes externas — el EA `D:\CODE\BOT\Bot\` (BotBase v3.0) y el vault `Estrategia-Nueva` — para extraer ADRs históricos y algoritmos "reutilizables". Como Estrategia2.0 es un proyecto desde cero cuya única referencia externa es el indicador LuxAlgo, DOC-06 dejó de tener sentido. Se verificó que **eliminarlo no rompe la lógica del plan**: los golden tests de Fase 4 NO dependían del BotBase (se construyen frescos desde TradingView); el BotBase solo aparecía como *namedrop* de formato y de targets de performance.

**Acciones de limpieza:**
- DOC-06 eliminado del workplan (Bloque B) con explicación in situ + **nota dedicada para Fable** en el gate VER-09.
- Limpiados los 3 *namedrops* residuales de "BotBase v3.0 / 175 golden tests" en WORKPLAN-MAESTRO-V2 (§5), WORKFLOWS.md (WF-04) y reglas-dev.md (§2).
- Regla absoluta escrita en CLAUDE.md ("Referencias externas") + memoria persistente `proyecto-nuevo-solo-luxalgo.md`.

## Decisiones tomadas (no re-litigar)
1. **Única referencia externa = indicador LuxAlgo SMC.** Prohibido leer/referenciar `D:\CODE\BOT\Bot\` y el vault `Estrategia-Nueva`.
2. **DOC-06 eliminado** definitivamente — no recrearlo.
3. **Golden tests de Fase 4 = set propio** construido desde TradingView, no heredado.
4. **Gate VER-09:** revisión integral de Fable antes de cualquier código Pine.

## Pendientes abiertos
- Heredados de Sesion-001: aplicar ADR-001 al workplan (§4.8/F2-T02/PINE-PLAN/MQL5-PLAN); poblar casos ⏳PENDIENTE-TVMCP; aprobación final de reglas-smc-ict.md.
- Siguiente paso del plan: validar lo informativo con Fable; luego Bloque C (MCPs) → D (skills) → E (agentes) → F (workflows) → gate VER-09.

## Cierre
DOC-02/03/04/07 creados · gate VER-09 registrado · DOC-06 eliminado + BotBase scrubbed · ESTADO-ACTUAL y memoria actualizados. Commit de la sesión hecho.
