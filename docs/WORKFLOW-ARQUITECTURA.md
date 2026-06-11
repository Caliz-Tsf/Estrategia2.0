# WORKFLOW-ARQUITECTURA.md — Orquestación de agentes y workflow de desarrollo
> Estrategia 2.0 · Bot SMC/ICT · DOC-03 del WORKPLAN-MAESTRO-V2
> Quién hace qué: el workflow de 3 agentes externos (Fase 4) + la orquestación de los 8 agentes y 9 skills internos.

Este documento responde "**quién ejecuta cada cosa y en qué orden**". El contenido de cada agente está en [AGENTES.md](workplan/AGENTES.md); el de cada skill en [SKILLS.md](workplan/SKILLS.md); el de cada workflow en [WORKFLOWS.md](workplan/WORKFLOWS.md). Aquí se ata todo.

---

## 1. DOS NIVELES DE ORQUESTACIÓN

El proyecto tiene dos planos de colaboración que no hay que confundir:

| Nivel | Quiénes | Cuándo |
|---|---|---|
| **A · Agentes externos (3)** | Claude Code · Antigravity · Claude Desktop | Solo **Fase 4** (construcción del EA MQL5). |
| **B · Agentes/skills internos** | Los 8 subagentes (`.claude/agents/`) + 9 skills (`.claude/skills/`) que invoca Claude Code | **Todas las fases** (0-4). |

En ambos planos, **Claude Code es el supervisor permanente**: dirige, integra outputs y aprueba. Los agentes nunca se invocan entre sí; el supervisor encadena. `[AGENTES.md §orquestación]`

---

## 2. NIVEL A — WORKFLOW DE 3 AGENTES (Fase 4) `[regla permanente]`

```
[USUARIO / Freddy] ── dirige ──┐
                               ▼
┌──────────────────── CLAUDE CODE (supervisor) ────────────────────┐
│ Arquitectura · revisión · Pine Script · TV MCP · subagentes      │
│ Es el ÚNICO que aprueba. Orquesta a los otros dos.               │
└───────────┬───────────────────────────────────┬─────────────────┘
            │ spec + código MQL5 a escribir       │ verificación visual
            ▼                                     ▼
   ANTIGRAVITY (IDE)                      CLAUDE DESKTOP
   SOLO escribe código MQL5 /            SOLO verificación visual MT5:
   PowerShell / JSON del EA              compilación en MetaEditor,
            │                            Strategy Tester, screenshots EA
            │ código                              │ resultado visual
            └────────► CLAUDE CODE revisa ◄───────┘
                       (integración correcta + cumple requisitos +
                        sin errores) → loop revisión-corrección
                        hasta APROBACIÓN de Claude Code
```

**Reglas del Nivel A:**
- **Claude Code** — supervisión, arquitectura, revisión, Pine Script, TV MCP, subagentes. Decide y aprueba.
- **Antigravity** — SOLO escribe código MQL5/PowerShell/JSON del EA. No decide arquitectura. Recibe spec del `mql5-translator-agent` (vía Claude Code) y la implementa.
- **Claude Desktop** — SOLO verificación visual en MT5 (compilación, Strategy Tester, screenshots del EA corriendo). Ya **NO** se usa para TradingView — el TV MCP lo reemplazó.
- El **loop** es: Antigravity escribe → Claude Code (con `mql5-reviewer`) revisa → correcciones → repite hasta que Claude Code apruebe. Máx 3 vueltas sin progreso → escala a `smc-architect`. `[WF-04 / AGENTES.md AGT-05]`

> Este nivel está **inactivo hasta Fase 4**. En Fases 0-3 todo el trabajo lo hace Claude Code con sus subagentes internos.

---

## 3. NIVEL B — AGENTES Y SKILLS INTERNOS (todas las fases)

### 3.1 Mapa de agentes `[AGENTES.md]`

```
[CLAUDE CODE — supervisor permanente]
   │ usa skills (protocolos) y decide invocaciones
   ├─→ smc-architect            · opus   · F0-4 · decisiones/ADRs/inicio de fase
   ├─→ smc-code-explorer        · sonnet · F1-4 · preguntas de código + impact analysis
   ├─→ pine-build-resolver      · sonnet · F1-3 · compilación Pine fallida (TV MCP)
   ├─→ smc-validator-agent      · sonnet · F1-4 · valida concepto vs reglas (screenshots)
   ├─→ smc-backtesting-analyst-agent · sonnet · F3-4 · analiza CSV de runs → pesos
   ├─→ smc-doc-updater          · haiku  · F0-4 · cierre de sesión (estado + sesión)
   └── FASE 4 ───────────────────────────────────────────────
       ├─→ mql5-translator-agent · opus   · F4 · spec + código + golden tests
       └─→ mql5-reviewer         · sonnet · F4 · review MQL5 antes de cada merge
```

### 3.2 Regla de oro de orquestación
> **Los workflows orquestan · los agentes ejecutan · las skills definen protocolos.** `[WORKFLOWS.md §regla general]`

- Una **skill** es el procedimiento (pasos + formato de salida). Ej.: `smc-validator` define *cómo* validar.
- Un **agente** ejecuta ese procedimiento en contexto aislado. Ej.: `smc-validator-agent` *hace* la validación.
- Un **workflow** encadena steps con loops y gates de aprobación. Ej.: `smc-sprint` encadena check-rule → implement → validate → approve → commit.

Esto resuelve el solapamiento del plan original (skill vs agente hacían lo mismo). `[FIX P-11]`

### 3.3 Mapa de invocación de skills `[workplan §4.10]`

```
[inicio sesión] ─ /smc-session-startup ─ ESTADO-ACTUAL · git · tv_health_check · morning_brief
[desarrollo] ──── /smc-pine-develop ──── ciclo regla→código→compila(→pine-build-resolver)
                                          →/smc-validator(→smc-validator-agent)→commit
[análisis] ────── /smc-chart-analysis ── TV MCP screenshots → tabla estado + lectura SMC
[validación] ──── /smc-replay ────────── modo A (conceptos) · modo B (señales) → sprint-runs/
[fase 3] ──────── /smc-backtesting-analyst ─ CSV → smc-backtesting-analyst-agent → pesos vN+1
[fase 4] ──────── /mql5-translator ───── pipeline 7 pasos → smc-architect + mql5-reviewer + golden tests
[post fase 3] ─── /smc-multi-scan ────── GUARD de fase → 4 pares
[fin sesión] ──── /smc-session-close ─── commits · core-sync · smc-doc-updater · obsidian
```

---

## 4. WORKFLOW DE DESARROLLO POR FASE

### 4.1 Fases 1-2 (por concepto) — workflow `smc-sprint`
```
/smc-session-startup
  → smc-sprint:
      check-rule   (¿cuantificado en reglas-smc-ict.md? si no → write-rule con smc-architect + aprobación)
      → spec       (smc-architect: firma f_detect, UDT, arrays, impacto Visual/Strategy)
      → implement  (skill smc-pine-develop; compila 0/0, si atasca → pine-build-resolver)
      → validate   (smc-validator-agent: screenshots → score ≥90; RECHAZADO ×3 → humano)
      → approve    (humano: score + screenshot + diff)
      → check-core-sync.ps1
      → commit     (atómico, ID de tarea)
/smc-session-close
```

### 4.2 Fase 3 (por iteración)
```
/smc-session-startup
  → run Strategy Tester → export CSV
  → skill smc-backtesting-analyst (smc-backtesting-analyst-agent: lift → pesos vN+1, solo IS)
  → aplicar pesos SOLO si veredicto = PROMOVER
  → replay modo B (muestra cualitativa)
/smc-session-close
```

### 4.3 Fase 4 (por módulo) — Nivel A activo
```
/smc-session-startup
  → skill mql5-translator (pipeline 7 pasos):
      spec (mql5-translator-agent) → Antigravity escribe →
      mql5-reviewer revisa → compilar (Claude Desktop) →
      golden tests verdes → verificación visual (Claude Desktop) → commit
  → archon-validate-pr antes del merge
/smc-session-close
```

---

## 5. DEGRADACIÓN ELEGANTE (tolerancia a fallos) `[FIX P-13, R-10]`

El stack tiene muchas piezas (6 MCPs + Archon + claude-mem). **Ninguna salvo el TV MCP es crítica en runtime.**

- **Único crítico:** TV MCP (para sesiones de desarrollo/validación en TradingView).
- **Degradan con ⚠️ y se sigue:** Archon (→ workflows ejecutados manualmente por Claude Code siguiendo los steps), claude-mem, context-mode, code-review-graph (→ el explorador usa Grep/Read), task-master, firecrawl/tavily.
- **Startup:** solo 2 pasos bloqueantes (ESTADO-ACTUAL + git). El resto degrada. `[workplan §4.9]`
- **Gates de fase:** dependen de criterios medibles del workplan §2, **nunca** de que una herramienta funcione.

---

## 6. PROTOCOLO DE SESIÓN (resumen — detalle en cada skill)

```
STARTUP (/smc-session-startup)                 CIERRE (/smc-session-close)
1 ESTADO-ACTUAL.md      [BLOQUEANTE]           1 commits coherentes pendientes
2 git status/branch     [BLOQUEANTE]           2 check-core-sync.ps1 [ARREGLAR si falla]
3 tv_health_check       [solo sesiones TV]     3 resumen de sesión (IDs workplan)
4 claude-mem/context    [⚠️ y seguir]          4 → smc-doc-updater: ESTADO-ACTUAL + Sesion-NNN + checkboxes
5 morning_brief         [solo Fase 3]          5 ¿decisión sin ADR? → smc-architect ahora
6 plan de sesión        [confirmar usuario]    6 ¿gate de fase? → git tag
                                               7 sync-obsidian.ps1 [⚠️ y cerrar]
```

---

*DOC-03 · Estrategia 2.0 · 2026-06-10 — referencia: AGENTES.md, SKILLS.md, WORKFLOWS.md, workplan §4.3-4.10*
