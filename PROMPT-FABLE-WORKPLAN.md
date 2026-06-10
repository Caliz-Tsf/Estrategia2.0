# PROMPT MAESTRO — FABLE: Arquitecto del Bot SMC/ICT
> Instrucciones completas para que Fable genere el Workplan definitivo de Estrategia 2.0
> Versión: 1.0 | Fecha: 2026-06-10

---

## INSTRUCCIONES DE USO

Copia todo lo que está debajo de esta línea y pégalo en el chat de Fable (claude.ai o Cowork).
No necesitas adjuntar archivos — toda la información está incluida en el prompt.

---
---

# SISTEMA: QUIÉN ERES Y QUÉ DEBES HACER

Eres el mejor arquitecto de sistemas de trading algorítmico del mundo, con dominio experto en:

- **Smart Money Concepts (SMC) e ICT methodology** (Inner Circle Trader): BOS, CHoCH, MSS, Order Blocks, Fair Value Gaps, Liquidity Sweeps, Kill Zones, Premium/Discount, Inducement, Displacement, Power of Three, Wyckoff
- **Pine Script v6** para TradingView — indicadores de dos capas, multi-timeframe, scoring de confluencias
- **MQL5 para MetaTrader 5** — Expert Advisors modulares, gestión de riesgo, ejecución de órdenes
- **Diseño de sistemas multi-agente** con Claude Code: agentes especializados, MCPs, skills, workflows Archon
- **Arquitectura de software de trading**: separación de responsabilidades, modularidad, testing, ADRs

Tu misión es tomar toda la información del proyecto **Estrategia 2.0** que se detalla a continuación y:

1. **Entender profundamente** qué se ha planificado y por qué
2. **Evaluar críticamente** el plan actual — qué está bien, qué falta, qué puede mejorar
3. **Reestructurar y mejorar** el plan completo: fases, agentes, skills, MCPs, workflows, scripts
4. **Definir completamente** cada componente (no solo listarlo — diseñarlo de verdad)
5. **Generar el WORKPLAN MAESTRO v2.0 definitivo** con orden de ejecución preciso
6. **Justificar cada decisión arquitectural** con razonamiento técnico
7. **Proponer mejoras concretas** donde veas oportunidades que el plan original no contempló
8. **Crear o mejorar agentes** cuando la tarea lo requiera — incluyendo su prompt completo, modelo recomendado, herramientas, y casos de uso
9. **Ser exhaustivo**: este plan será la fuente de verdad para construir el bot completo

Cuando necesites crear subplanes o diseñar componentes complejos, llámate a ti mismo en modo "agente especializado" — por ejemplo: "Como agente SMC Architect, analizo la arquitectura de los 57 confluence inputs..." y responde desde ese rol antes de continuar.

---

# CONTEXTO COMPLETO DEL PROYECTO

## 1. QUÉ ESTAMOS CONSTRUYENDO

Un **bot de trading completo** basado en Smart Money Concepts (SMC) e ICT Methodology para el mercado Forex.

**Stack tecnológico:**
- **TradingView**: Dos indicadores Pine Script v6 (Capa 1 + Capa 2)
- **MetaTrader 5**: Expert Advisor MQL5 con 5 módulos
- **Claude Code + agentes**: Orquestación del desarrollo, validación, revisión
- **Antigravity IDE** (cuando disponible) o **Opus/Sonnet** (fallback): Escritura de código MQL5

**Par inicial**: EURUSD exclusivo hasta completar validación completa en Fase 3

**Multi-timeframe**:
- D1 → Contexto macro (Premium/Discount, bias institucional)
- H1 → Bias principal (CHoCH, BOS, OB, FVG activos) — timeframe de decisión
- M5 → Entrada de precisión (OB/FVG de precisión, Kill Zones)

**R:R mínimo**: 1:3 obligatorio, sin excepción. Trailing stop hacia extensión máxima calculable.

**Kill Zones**: London 08-10 GMT, NY 13-15 GMT (Tokyo 00-02 GMT secundaria)

---

## 2. ARQUITECTURA DE DOS CAPAS (Pine Script)

### Capa 1 — `SMC-Visualizer.pine`
Detecta, calcula y dibuja TODOS los conceptos SMC/ICT en D1, H1 y M5. Almacena estructuras en arrays con `maxSize` explícito. Es la fuente de datos para la Capa 2.

### Capa 2 — `SMC-Decision.pine`
Indicador separado que consume los arrays de la Capa 1 vía `request.security()`. Genera señales de entrada basadas en **57 confluencias con scoring ponderado**. Calcula SL/TP, lanza alertas para MT5.

**Por qué dos capas separadas:**
- Separación de responsabilidades: visualización vs decisión
- La Capa 1 puede actualizarse sin romper la lógica de decisión
- Mejor rendimiento (Pine Script tiene límites de recursos)
- Capa 2 puede ser probada con diferentes parámetros de scoring sin tocar la visualización
- Facilita la traducción a MQL5: los módulos MT5 siguen la misma separación

---

## 3. INDICADOR BASE — LuxAlgo Smart Money Concepts

El proyecto parte de un indicador existente `Smart Money Concepts [LuxAlgo]` en Pine Script v5 que ya implementa:

✅ BOS/CHoCH (internos y swing) con filtro de confluencias
✅ Order Blocks (internos y swing, con mitigación por close o high/low)
✅ Fair Value Gaps (con soporte MTF via `request.security()`)
✅ Equal Highs/Lows con sensibilidad configurable
✅ Premium/Discount/Equilibrium zones
✅ Strong/Weak Highs & Lows
✅ Niveles diarios/semanales/mensuales
✅ 16 alertas configuradas
✅ Panel visual configurable

**Lo que FALTA en el indicador base (a agregar en Capa 1):**

TIER 1 (primer sprint — críticos):
- FVG Mitigation tracking explícito (parcial en base)
- Liquidity Pools (zonas de stops acumulados sobre EQH/bajo EQL)
- Liquidity Sweeps (precio toca pool, cierra de vuelta — false breakout + wick)
- Kill Zones (ventanas horarias London/NY/Tokyo)
- HTF Structure alignment completo (extender MTF a BOS/CHoCH/OB en todos los TFs)

TIER 2 (segundo sprint):
- Market Structure Shift (MSS)
- Impulsive/Corrective Move detection
- Judas Swing (spike falso que captura stops)
- Displacement (vela expansiva post-consolidación)
- Breaker Block (OB roto que invierte rol)
- Rejection Block (candle de rechazo con wick largo)
- Mitigation Block (OB/FVG parcialmente mitigado)
- Role Reversal/Flip (resistencia → soporte tras ruptura limpia)
- Inducement (IDM — trampa de liquidez menor)
- OTE — Optimal Trade Entry (zona 61.8-79% retracement)
- Golden Pocket (Fibonacci 50-61.8%)
- EMA 20 / 50 / 200 con cruces y rebotes

TIER 3 (tercer sprint — evaluar aporte):
- Liquidity Grab, Liquidity Void, False Breakout, Raid, Spring/Shakeout
- Wyckoff Accumulation/Distribution (fases A-E)
- Power of Three / AMD
- Compression/Squeeze, Inside Bar, Engulfing, Volume Surge
- Session Opens (W/M/Q)

---

## 4. SISTEMA DE 57 CONFLUENCIAS (Capa 2)

El motor de scoring evalúa estas 57 confluencias. Los pesos se definen DESPUÉS de la validación visual en Fase 3 — aquí solo se establece la arquitectura.

**Estructura de mercado (8):**
1. CHoCH H1 swing confirmado en dirección de entrada
2. BOS H1 swing confirmado en dirección de entrada
3. CHoCH M5 confirmado
4. BOS M5 confirmado
5. MSS (Market Structure Shift) detectado
6. Secuencia HH/HL o LL/LH confirmada
7. Impulsive move detectado previo
8. Corrective move detectado (retroceso esperado)

**Liquidez (10):**
9. Liquidity Pool activo en dirección
10. Liquidity Sweep ejecutado (pool barrido antes de entrada)
11. Liquidity Grab detectado
12. Equal Highs barridos
13. Equal Lows barridos
14. Judas Swing detectado
15. Spring/Shakeout detectado
16. False Breakout detectado
17. Raid detectado
18. (reservado)

**Imbalances y bloques (11):**
18. FVG H1 activo (precio retrocede hacia él)
19. OB H1 activo
20. FVG M5 activo (como trigger de entrada)
21. OB M5 activo
22. FVG D1 activo (confluencia macro)
23. OB D1 activo
24. Breaker Block en dirección
25. Rejection Block en nivel
26. Mitigation Block detectado
27. Role Reversal confirmado
28. FVG mitigado recientemente

**Premium/Discount/Fibonacci (7):**
29. OTE activo (61.8-79%)
30. Golden Pocket activo (50-61.8%)
31. Precio en Discount Zone H1 (para longs)
32. Precio en Premium Zone H1 (para shorts)
33. Precio en Discount Zone D1
34. Precio en Premium Zone D1
35. Precio en Equilibrium (potencial chop — resta/neutraliza)

**ICT específico (7):**
36. Displacement previo al setup
37. Inducement (IDM) detectado previo
38. Kill Zone activa (London/NY/Tokyo)
39. Power of Three fase identificada (A/M/D)
40. Wyckoff phase identificada
41. Session open relevante activo (W/M/Q)
42. Evento D1 transferido activo en mismo sentido

**EMAs — todas las combinaciones (15):**
43. EMA 200: precio por encima (bias alcista)
44. EMA 200: precio por debajo (bias bajista)
45. EMA 50: precio por encima
46. EMA 50: precio por debajo
47. EMA 20: precio por encima
48. EMA 20: precio por debajo
49. Cruce EMA 20×50 (golden/death)
50. Cruce EMA 50×200 (golden/death)
51. Cruce EMA 20×200
52. Rebote EMA 200
53. Rebote EMA 50
54. Rebote EMA 20
55. Las 3 EMAs alineadas en misma dirección (tendencia fuerte)
56. Confluencia EMA + OB en mismo nivel
57. Confluencia EMA + FVG en mismo nivel

**Lógica de señal:**
```
SI score >= threshold:
  → Señal LONG o SHORT
  → SL: debajo/encima del OB o swing más reciente que justifica la entrada
  → TP1: SL × 3 (R:R mínimo 1:3)
  → TP_ext: siguiente OB/FVG/swing no mitigado en TF mayor
  → Alerta TradingView con detalle completo → webhook → MT5
```

---

## 5. EL PLAN MAESTRO ACTUAL (FASE 0)

### Por qué creamos este plan así — Justificación

El plan maestro fue construido respondiendo estas preguntas fundamentales:

**¿Por qué SMC + ICT juntos?**
SMC (Smart Money Concepts) da el marco estructural: dónde está el dinero institucional, cómo se mueven los precios en relación a liquidez. ICT (Inner Circle Trader) complementa con herramientas de timing preciso: Kill Zones, Power of Three, Displacement, Inducement. Juntos forman el sistema más completo de análisis de mercado basado en flujo institucional.

**¿Por qué EURUSD como único par inicial?**
Es el par más líquido, el que mejor responde a conceptos SMC, con spreads bajos y datos históricos abundantes. Validar en un solo par antes de expandir evita el error común de diversificar prematuramente sin tener una base sólida.

**¿Por qué Pine Script primero, MT5 después?**
TradingView permite backtesting visual rápido sin escribir código de ejecución. Validar la lógica visualmente antes de automatizarla reduce el riesgo de desarrollar un EA defectuoso. El Pine Script se convierte en la spec exacta del EA.

**¿Por qué dos capas separadas en Pine Script?**
Separación de responsabilidades. La Capa 1 (visualización) puede evolucionar independientemente de la Capa 2 (decisión). Esto facilita mantener, actualizar y traducir a MQL5. Además, TradingView tiene límites de recursos que hacen recomendable separar la lógica pesada de visualización del motor de decisión.

**¿Por qué 57 confluencias?**
Más confluencias activas = mayor probabilidad de que el movimiento sea institucional y no ruido. El sistema de scoring permite que cada trader configure los pesos según su estilo, pero la arquitectura captura TODO lo que puede ser relevante.

**¿Por qué el workflow de 3 agentes?**
- Claude Code es el supervisor y arquitecto: mantiene coherencia, revisa integraciones, hace el Pine Script con TV MCP
- Antigravity IDE (o Opus/Sonnet como fallback): especializado en escritura de código MQL5, aislado para evitar contaminación con el resto del proyecto
- Claude Desktop (o computer use): verificación visual de MT5, compilación, Strategy Tester — cosas que requieren ver la UI de MT5

**¿Por qué R:R mínimo 1:3?**
Con un win rate del 40% y R:R 1:3 ya eres rentable. Esto da margen de error amplio para el sistema y evita operar setups de bajo potencial que consumen capital sin justificación estadística.

**¿Por qué solo Kill Zones London y NY?**
Son las sesiones de mayor volumen y liquidez en Forex. Los movimientos institucionales más significativos ocurren en estas ventanas. Operar fuera de ellas aumenta el ruido y reduce la calidad de las señales SMC.

### Arquitectura del entorno (Fase 0)

**MCPs configurados en `.mcp.json`:**
```json
{
  "tradingview": { 
    "command": "node",
    "args": ["D:\\CODE\\BOT\\Bot\\tradingview-mcp-jackson\\src\\server.js"],
    "nota": "Fork de LewisWJackson/tradingview-mcp-jackson — 81 tools para operar TradingView desde Claude Code. Permite: crear/editar Pine Script, publicar indicadores, hacer backtesting, tomar screenshots de charts, morning_brief con bias EURUSD"
  },
  "firecrawl-mcp": { 
    "nota": "Web scraping para Pine Script docs, MQL5 docs, artículos ICT/SMC, LuxAlgo documentation"
  },
  "task-master-ai": { 
    "nota": "Gestión de backlog del proyecto — parsea PLAN-BOT-SMC-ICT.md para generar tareas automáticamente"
  },
  "tavily-mcp": { 
    "nota": "Búsqueda web para research de conceptos SMC/ICT y documentación técnica"
  },
  "context-mode": { 
    "nota": "Evita comprimir documentos críticos en sesiones largas (>1h) — mantiene reglas-smc-ict.md y el plan siempre en contexto"
  },
  "code-review-graph": { 
    "nota": "Grafo semántico del codebase — permite hacer impact analysis antes de modificar código"
  }
}
```

**Agentes definidos (7):**

| ID | Agente | Modelo | Propósito |
|----|--------|--------|-----------|
| AGT-01 | `smc-validator-agent` | Sonnet | Valida implementaciones Pine Script contra reglas-smc-ict.md. Inspecciona screenshots. Score por concepto. |
| AGT-02 | `smc-backtesting-analyst-agent` | Sonnet | Analiza JSON de runs de backtesting. Detecta patrones de pérdida. Sugiere ajustes al scoring. |
| AGT-03 | `mql5-translator-agent` | Opus | Traduce Pine Script validado → MQL5 modular. Alta complejidad, usa Opus por precisión. |
| AGT-04 | `smc-architect` | Opus | Decisiones de arquitectura del indicador y EA. ADRs. Diseño de los 57 confluence inputs. |
| AGT-05 | `mql5-reviewer` | Sonnet | Revisión código MQL5: performance <50ms/tick, memory <100MB, ICT accuracy >94%. |
| AGT-06 | `smc-code-explorer` | Sonnet | Exploración del codebase Pine/MQL5. AST analysis via code-review-graph. |
| AGT-07 | `smc-doc-updater` | Sonnet | Mantiene reglas-smc-ict.md, ADRs y ESTADO-ACTUAL.md actualizados tras cada sesión. |

**Skills definidas (9 custom):**

| ID | Skill | Propósito |
|----|-------|-----------|
| SKL-01 | `smc-pine-develop` | Desarrolla Pine Script con validación contra reglas SMC, 0 errores/warnings |
| SKL-02 | `smc-chart-analysis` | Lee confluencias activas EURUSD, bias H1, zonas Premium/Discount |
| SKL-03 | `smc-replay` | Backtesting manual: fecha → señal → registro → siguiente |
| SKL-04 | `smc-multi-scan` | Solo EURUSD hasta Fase 3, template para expansión futura |
| SKL-05 | `smc-validator` | Verifica conceptos SMC contra reglas. Input: screenshot. Output: score por confluencia. |
| SKL-06 | `smc-backtesting-analyst` | Analiza runs: win rate, R:R promedio, distribución por Kill Zone |
| SKL-07 | `mql5-translator` | Traduce lógica Pine Script → MQL5 arquitectura modular (5 módulos) |
| SKL-08 | `smc-session-startup` | Ejecuta protocolo startup: ESTADO-ACTUAL → briefing → git branch → tv_health_check → morning_brief |
| SKL-09 | `smc-session-close` | Ejecuta protocolo cierre: checkpoint → commits → ESTADO-ACTUAL → ADR si aplica → sync-obsidian |

**Workflows Archon v2 (7):**

| ID | Workflow | Cuándo usar |
|----|----------|-------------|
| WF-01 | `smc-sprint.yaml` | Ciclo SMC: spec → implement loop → validate → approve → commit. Fases 1 y 2. |
| WF-02 | `archon-piv-loop` | Plan-Implement-Validate con aprobación humana. Workflow principal. |
| WF-03 | `archon-refactor-safely` | Refactoring entre Tiers sin romper lo existente. |
| WF-04 | `archon-test-loop-dag` | Loop hasta que 175 golden tests pasen. Fase 4. |
| WF-05 | `archon-validate-pr` | Antes de cada merge en el repo del EA. Fase 4. |
| WF-06 | `archon-architect` | Sweep arquitectural del EA antes de traducir Pine→MQL5. |
| WF-07 | `archon-feature-development` | Implementar feature completo desde plan hasta PR. |

**Estructura de directorios objetivo:**
```
D:\CODE\Estrategia2.0\
├── .claude/
│   ├── agents/          ← 7 agentes custom SMC
│   └── skills/          ← 9 skills SMC + skills base
├── .archon/
│   └── workflows/
│       ├── defaults/    ← 18 workflows Archon oficiales
│       └── smc-sprint.yaml
├── pine/
│   ├── SMC-Visualizer.pine     ← CAPA 1 (nueva — basada en LuxAlgo)
│   ├── SMC-Decision.pine       ← CAPA 2 (nueva)
│   └── reference/
│       └── LuxAlgo-SMC-base.pine  ← indicador base de referencia
├── mt5/
│   ├── Experts/EA_SMC_ICT.mq5
│   └── Include/
│       ├── SMC_Structures.mqh
│       ├── SMC_MTF.mqh
│       ├── SMC_Scoring.mqh
│       ├── SMC_RiskManager.mqh
│       └── SMC_Display.mqh
├── docs/
│   ├── adrs/
│   ├── sprint-runs/
│   ├── reglas-smc-ict.md     ← FUENTE DE VERDAD SMC
│   ├── reglas-dev.md
│   ├── WORKFLOW-ARQUITECTURA.md
│   └── TV-SMC-WORKFLOW.md
├── scripts/
│   ├── launch-tv-agent.ps1
│   ├── sync-obsidian.ps1
│   └── process-video.ps1
├── memory/
│   └── ESTADO-ACTUAL.md
├── .mcp.json
├── CLAUDE.md
└── rules.json
```

---

## 6. FASES DE DESARROLLO

### FASE 0 — Configuración base
Crear todos los documentos fuente, configurar MCPs, crear los 7 agentes y 9 skills, configurar Archon workflows, scripts de startup/cierre.

### FASE 1 — `SMC-Visualizer.pine` (Capa 1)
Implementar todos los Tiers 1+2 (críticos + importantes) del indicador de visualización. Panel de estado con precio/fecha/hora por concepto y timeframe. Arrays SMC_ con maxSize para consumo de Capa 2.

### FASE 2 — `SMC-Decision.pine` (Capa 2)
Motor de 57 confluencias con scoring, generación de señal LONG/SHORT, SL/TP calculados, alertas para webhook MT5, registro histórico de señales.

### FASE 3 — Validación TradingView
- 500 velas H1 EURUSD backtesting visual con `smc-replay`
- 30 días paper trading
- Criterios de avance: win rate ≥55% (min 50 señales), R:R promedio ≥2.0
- Definición de pesos de scoring basada en estadística de señales

### FASE 4 — MetaTrader 5 EA
Reimplementación en MQL5 de 5 módulos + EA principal. No traducción directa — reimplementación siguiendo la arquitectura validada. Pipeline: Fase 3 spec → `mql5-translator-agent` (Opus) → Antigravity/Sonnet escribe → Claude Code revisa → MetaEditor compila → Claude Desktop verifica visual.

Targets de performance heredados de BotBase v3.0:
- <50ms por tick
- <100MB RAM
- >94% ICT accuracy
- 175/175 golden tests verde

---

## 7. NOTAS IMPORTANTES SOBRE EL WORKFLOW DE AGENTES

**Workflow flexible** (no inamovible):
- Antigravity IDE escribe MQL5 cuando tiene tokens disponibles
- **Cuando Antigravity no está disponible**: Opus o Sonnet asumen la escritura de código MQL5
- Claude Code siempre supervisa, revisa integración y aprueba
- Claude Desktop (computer use) para verificación visual de MT5 cuando sea necesario

**Protocolo de revisión de código MQL5:**
```
1. mql5-translator-agent (Opus) → genera spec + estructura de código
2. Antigravity/Sonnet/Opus → implementa el código
3. Claude Code → revisa: integración correcta + cumple requisitos + 0 errores
4. Loop revisión-corrección hasta aprobación
5. Compilar en MetaEditor → verificar 0 errors, 0 warnings
6. Claude Desktop → verificar visual en MT5 (Strategy Tester, panel)
```

---

# TU MISIÓN — INSTRUCCIONES PARA FABLE

Con toda la información anterior, debes hacer lo siguiente **en este orden**:

## PASO 1: Destrucción total del plan actual → Reconstrucción desde cero

Este paso tiene DOS fases obligatorias. No puedes pasar al Paso 2 sin completar ambas.

### FASE 1A — DESTRUCCIÓN: Demoler el plan con brutalidad técnica

Actúa como un auditor implacable. Tu trabajo es encontrar TODO lo que está mal, incompleto, mal pensado, contradictorio, ambiguo o directamente equivocado. No hay lugar para cortesía — si algo falla, dilo directo.

Destruye el plan respondiendo cada una de estas preguntas sin filtro:

**Sobre la arquitectura general:**
- ¿El flujo de fases tiene sentido o hay dependencias mal ordenadas?
- ¿La separación en dos capas Pine Script crea problemas técnicos que el plan no contempla?
- ¿El plan de 4 fases cubre todos los riesgos reales de un bot de trading en producción?
- ¿Hay pasos que son imposibles o imprácticamente difíciles de ejecutar tal como están descritos?

**Sobre los agentes:**
- ¿Algún agente tiene responsabilidades que se superponen con otro? ¿Cuál es redundante?
- ¿Hay tareas críticas del proyecto que ningún agente cubre?
- ¿Los modelos asignados (Opus/Sonnet) son los correctos para cada responsabilidad?
- ¿Los agentes actuales pueden realmente ejecutar lo que se les pide sin MCPs o contexto que no tienen?

**Sobre las skills:**
- ¿Alguna skill está mal definida o es demasiado vaga para ser implementable?
- ¿Hay skills que se solapan con lo que ya hacen los MCPs o agentes?
- ¿El protocolo de startup/cierre de sesión es realista o tiene pasos que fallarán?

**Sobre los MCPs:**
- ¿Los 6 MCPs cubren realmente todas las necesidades del proyecto?
- ¿Hay MCPs faltantes críticos para este tipo de sistema?
- ¿El TV MCP de 81 tools es suficiente para todo el trabajo en TradingView que el plan requiere?

**Sobre Pine Script:**
- ¿Los 57 confluencias tienen problemas de rendimiento que harán el indicador inutilizable en TradingView?
- ¿El sistema de arrays SMC_ con `request.security()` entre Capa 1 y Capa 2 tiene limitaciones técnicas que el plan ignora?
- ¿El Tier 3 de conceptos (Wyckoff, Power of Three, etc.) es implementable en Pine Script v6 de manera confiable?

**Sobre MQL5/MT5:**
- ¿La arquitectura de 5 módulos tiene dependencias circulares o problemas de inicialización?
- ¿Los targets de performance (<50ms/tick, <100MB) son realistas para la complejidad del sistema?
- ¿El proceso de traducción Pine→MQL5 está subvalorado en complejidad?

**Sobre el workflow de agentes:**
- ¿El loop de revisión Claude Code → Antigravity/Sonnet es eficiente o creará cuellos de botella?
- ¿Hay riesgos de consistencia cuando Antigravity no está disponible y Sonnet/Opus toman su lugar?

**Errores, gaps y contradicciones que debes buscar activamente:**
- Pasos que asumen herramientas instaladas que no están configuradas
- Documentos referenciados que no existen aún
- Flujos donde la salida de un paso no coincide con la entrada esperada del siguiente
- Estimaciones de tiempo que son completamente irreales
- Conceptos SMC/ICT que están definidos de forma incorrecta o incompleta
- Cualquier cosa que, si se ejecuta tal como está, producirá un resultado diferente al esperado

Al final de esta fase, produce un **REPORTE DE DEMOLICIÓN** con:
- Lista numerada de todos los problemas encontrados (sin límite — mejor más que menos)
- Clasificados por severidad: 🔴 CRÍTICO (bloquea el proyecto) | 🟡 IMPORTANTE (degradará resultados) | 🟢 MENOR (optimizable)
- Para cada problema: descripción exacta + por qué es un problema + qué consecuencia tiene si no se corrige

---

### FASE 1B — RECONSTRUCCIÓN: Construir el nuevo plan desde los cimientos

Con el Reporte de Demolición en mano, ahora construyes el plan correcto. Cada problema crítico y importante del reporte debe quedar resuelto en el nuevo plan.

Para esta reconstrucción:

- **Parte desde cero conceptualmente** — el plan anterior es solo referencia, no la base
- **Mantén lo que funciona** (márcalo con `[✓ MANTENER]`) — no destruyas por destruir
- **Resuelve cada problema** del reporte de demolición explícitamente (márcalo con `[FIX: problema #N]`)
- **Propón componentes nuevos** cuando la demolición reveló gaps (márcalo con `[NUEVO]`)
- **Justifica cada decisión arquitectural** — especialmente donde cambias algo del plan original

La reconstrucción debe producir:
1. Nueva arquitectura general del proyecto (diagrama en texto)
2. Nuevo flujo de fases con dependencias claras
3. Lista revisada de agentes (pueden ser más, menos o los mismos con responsabilidades corregidas)
4. Lista revisada de skills
5. Lista revisada de MCPs
6. Nuevos workflows si los actuales eran defectuosos

**Esta reconstrucción es el nuevo plan base sobre el cual ejecutarás los Pasos 2 al 8.**

## PASO 2: Rediseño de agentes (modo agente especializado)

Para cada uno de los 7 agentes actuales, y para cualquier agente nuevo que propongas, genera:

```markdown
### [NOMBRE DEL AGENTE]
**Modelo**: [claude-opus-4-8 | claude-sonnet-4-6 | claude-haiku-4-5]
**Cuándo se activa**: [condición específica]
**Responsabilidades exactas**:
  - [lista detallada]
**Herramientas / MCPs que usa**:
  - [lista]
**Input esperado**:
  - [qué recibe como input]
**Output esperado**:
  - [qué produce como output]
**Prompt completo del agente**:
  [El system prompt completo que define el comportamiento del agente]
**Criterio de éxito**:
  - [cómo saber que el agente funcionó correctamente]
```

## PASO 3: Rediseño de skills

Para cada una de las 9 skills actuales, y para skills nuevas que propongas, genera:

```markdown
### [NOMBRE DE LA SKILL]
**Tipo**: [output-format | research | code-generation | validation | protocol]
**Cuándo se usa**: [trigger específico]
**Pasos de ejecución**:
  1. [paso detallado]
  2. ...
**Herramientas que invoca**:
  - [lista de tools/MCPs/agentes]
**Output**:
  - [formato exacto del resultado]
**Ejemplo de invocación**:
  `/smc-session-startup` → [qué hace exactamente]
```

## PASO 4: Diseño de los workflows Archon

Para cada workflow (actuales y nuevos que propongas), genera el YAML completo:

```yaml
# smc-sprint.yaml
name: smc-sprint
description: "Ciclo SMC completo: spec → implement → validate → approve → commit"
steps:
  - name: spec
    agent: smc-architect
    prompt: "..."
    output: spec.md
  - name: implement
    agent: [agente apropiado]
    ...
```

## PASO 5: Plan de implementación detallado de las DOS CAPAS Pine Script

Genera un plan técnico detallado para implementar `SMC-Visualizer.pine` y `SMC-Decision.pine`:

- Estructura completa del código (funciones, variables, arrays)
- Orden de implementación de los conceptos (qué primero, qué después)
- Cómo se comunican las dos capas (arrays, `request.security()`, naming conventions)
- Panel de estado: estructura exacta de la tabla
- Sistema de alertas: mensajes y condiciones
- Testing: cómo validar cada concepto antes de agregar el siguiente
- Gestión de performance: cómo evitar el límite de 500 labels/lines/boxes de Pine Script

## PASO 6: Plan técnico del EA MetaTrader 5

Genera el diseño técnico completo de los 5 módulos MQL5:

Para cada módulo (`SMC_Structures.mqh`, `SMC_MTF.mqh`, `SMC_Scoring.mqh`, `SMC_RiskManager.mqh`, `SMC_Display.mqh`, `EA_SMC_ICT.mq5`):
- Responsabilidades exactas
- Interfaces públicas (funciones expuestas a otros módulos)
- Estructuras de datos clave
- Cómo mapea a la Capa 1 y Capa 2 de Pine Script

## PASO 7: WORKPLAN MAESTRO v2.0

Genera el plan de ejecución definitivo con:

```
FASE 0: Configuración (estimado: X días)
  ├── PRE-FASE 0: Herramientas externas (manual)
  │   ├── [ID] Tarea — descripción — herramienta — criterio de completitud
  │   └── ...
  ├── BLOQUE A: Documentos base
  ├── BLOQUE B: MCPs y config
  ├── BLOQUE C: Skills (con orden de creación)
  ├── BLOQUE D: Agentes (con orden de creación)
  ├── BLOQUE E: Workflows
  ├── BLOQUE F: Scripts
  └── VERIFICACIÓN: checklist de 7 puntos

FASE 1: SMC-Visualizer.pine (estimado: X días)
  ├── Sprint 1: Tier 1 conceptos
  ├── Sprint 2: Tier 2 conceptos
  ├── Sprint 3: Tier 3 + Panel de estado
  └── Sprint 4: MTF completo + testing

FASE 2: SMC-Decision.pine (estimado: X días)
  ├── ...

FASE 3: Validación (estimado: X días)
  ├── ...

FASE 4: MetaTrader 5 EA (estimado: X días)
  ├── ...
```

## PASO 8: Mejoras y propuestas adicionales

Propone cualquier mejora que el plan original no contempló:
- ¿Falta algún MCP relevante para este tipo de proyecto?
- ¿Hay conceptos SMC/ICT importantes que no están en los Tiers?
- ¿El sistema de scoring de 57 confluencias puede mejorarse arquitecturalmente?
- ¿Hay riesgos de performance en Pine Script no contemplados?
- ¿La traducción Pine→MQL5 tiene trampas técnicas que debemos anticipar?
- ¿Cómo manejar la gestión de estado entre sesiones de Claude Code?
- ¿Qué pasa cuando un concepto SMC en MT5 se comporta diferente al Pine Script?

---

## PASO 9: Diagramas completos del sistema

Genera diagramas en texto (ASCII / Mermaid) para visualizar el proyecto completo. Usa el formato que sea más claro para cada caso. Crea tantos sub-diagramas como sean necesarios — **no comprimas en uno solo lo que necesita varios**.

### 9.1 — Diagrama maestro: visión general del bot completo

Un diagrama que muestre de un vistazo todo el sistema: desde el análisis de mercado hasta la ejecución de órdenes en MT5. Debe mostrar cómo fluyen los datos a través de TradingView → señal → MT5 → orden ejecutada.

```
Ejemplo de forma (no el contenido real):
Mercado EURUSD → [Capa 1: SMC-Visualizer] → arrays SMC_ → [Capa 2: SMC-Decision] → señal + alerta → webhook → [EA MT5] → orden
```

### 9.2 — Diagrama de fases del proyecto

Diagrama de línea de tiempo con las 4 fases (0→4), sus dependencias, criterios de entrada/salida de cada fase, y los hitos clave. Debe mostrar claramente que no se puede avanzar a la siguiente fase sin cumplir los criterios de la anterior.

### 9.3 — Diagrama de arquitectura de agentes

Muestra todos los agentes, qué herramientas/MCPs usa cada uno, cuándo se activan, y cómo interactúan entre sí. Si un agente llama a otro agente, que se vea el flujo. Si un agente usa un MCP específico, que se vea la conexión.

```
Ejemplo:
[Claude Code — supervisor]
    │ activa
    ├──→ [smc-architect (Opus)] — usa: code-review-graph, firecrawl
    ├──→ [smc-validator-agent (Sonnet)] — usa: TV MCP, reglas-smc-ict.md
    └──→ [mql5-translator-agent (Opus)] — usa: firecrawl (MQL5 docs)
              │ produce spec
              └──→ [Antigravity / Sonnet] — escribe código
                        │ output
                        └──→ [Claude Code — revisa] → loop hasta aprobación
```

### 9.4 — Diagrama de flujo de desarrollo de cada fase

Un sub-diagrama por fase (Fase 1, 2, 3, 4) que muestre el ciclo de trabajo interno: qué skill se invoca, qué agente actúa, qué workflow orquesta, cuál es el criterio de validación, y cómo se hace el commit/cierre. Deben ser lo suficientemente detallados para que un desarrollador los siga paso a paso.

### 9.5 — Diagrama de los workflows Archon

Para cada workflow relevante (`smc-sprint`, `archon-piv-loop`, `archon-test-loop-dag`), un diagrama de flujo que muestre cada step, las decisiones (aprobación humana, test pass/fail), y los loops de corrección.

```
Ejemplo smc-sprint:
[spec] → [implement] → [validate] ──→ ¿aprobado? ──SI──→ [commit]
                           ↑                │
                           └────────────NO──┘ (loop revisión)
```

### 9.6 — Diagrama de las dos capas Pine Script

Muestra la arquitectura interna de `SMC-Visualizer.pine` y `SMC-Decision.pine`:
- Qué módulos/funciones tiene cada capa
- Qué arrays produce la Capa 1 y cuáles consume la Capa 2
- Cómo fluye la información via `request.security()`
- Cómo se genera la señal y cómo se transforma en alerta para MT5

### 9.7 — Diagrama de la arquitectura MQL5 (5 módulos + EA)

Muestra la estructura interna del Expert Advisor:
- Los 5 módulos `.mqh` y sus dependencias entre sí
- Cuál módulo llama a cuál
- El flujo de ejecución en cada tick: qué módulo se ejecuta primero, en qué orden
- Cómo el EA principal (`EA_SMC_ICT.mq5`) orquesta los módulos
- El flujo completo desde "llega un nuevo tick" hasta "se ejecuta o no una orden"

### 9.8 — Diagrama de las 57 confluencias (scoring visual)

Un diagrama que muestre las 57 confluencias agrupadas por categoría, con su peso relativo conceptual (antes de la validación estadística), y cómo se suman para llegar al threshold de señal. Puede ser un árbol o una tabla visual que muestre la lógica de scoring.

### 9.9 — Diagrama del protocolo de sesión

El flujo exacto de startup y cierre de sesión de Claude Code:
- Startup: cada paso, qué herramienta invoca, qué verifica, en qué orden
- Cierre: cada paso, qué guarda, qué sincroniza, condiciones especiales (si hubo ADR, si fase completada, etc.)

### 9.10 — Diagrama de skills: mapa de invocación

Un mapa que muestre cuándo y desde dónde se invoca cada skill, qué herramientas internas usa, y qué produce. Útil para entender el ecosistema de skills sin leer cada una individualmente.

```
Ejemplo:
[Inicio de sesión]
    └──→ /smc-session-startup
              ├── Lee: memory/ESTADO-ACTUAL.md
              ├── Invoca: /latent-briefing (si >1h)
              ├── Ejecuta: git branch
              ├── Llama MCP: tv_health_check
              └── Llama MCP: morning_brief (rules.json)
```

---

# FORMATO DE ENTREGA

Tu respuesta debe estar estructurada en secciones claramente marcadas. Prioriza precisión técnica sobre brevedad — este documento será la guía de construcción real del bot.

Si necesitas hacer suposiciones, márcalas explícitamente con `[SUPOSICIÓN: ...]`.

Si encuentras contradicciones en el plan original, señálalas con `[CONTRADICCIÓN: ...]` y propón resolución.

Si propones algo nuevo que no estaba en el plan original, márcalo con `[NUEVO: ...]`.

Si algo del plan original es correcto y no debe cambiar, confírmalo con `[✓ MANTENER: ...]`.

---

*Prompt generado por: Estrategia 2.0 — Freddy Hernández*
*Fecha: 2026-06-10*
*Contexto: Todo el contenido de D:\CODE\Estrategia2.0\ está incluido en este prompt*
