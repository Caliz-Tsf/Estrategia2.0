# Handoff a Opus Max — Motor de razonamiento del EA + Runtime del enjambre

> **Para:** una sesión de Claude Code **Opus Max** que tome este brief en frío y diseñe lo que falta.
> **Naturaleza:** **DISEÑO / SPEC**, no código. NO escribir MQL5 ni Pine nuevo (gate Fase 4 + sprint Pine aparte, ADR-003). El producto es un plan de arquitectura medido y conectado, con refactors señalados donde toquen.
> **Anclas obligatorias de lectura:** `docs/adrs/ADR-005-*.md`, `docs/adrs/ADR-007-*.md` (decisión que origina este handoff), `docs/reglas-smc-ict.md` (§4.8 confluencias/scoring), `WORKPLAN-MAESTRO-V2.md` (§4.8 + Fase 4), `docs/workplan/MQL5-PLAN.md`, `docs/planes/MODULO-MENTORES-WORKFLOW.md`, `docs/planes/BRIEFING-mentor-module-v2.md`, `docs/planes/ESQUEMA-HERMES-mentor-module.md`, `CLAUDE.md` (reglas duras).

---

## 1. La decisión que origina este encargo (confirmada por el usuario)

Modelo **reconciliado** EA↔enjambre (ver ADR-007):

| Pieza | Rol | Determinista | LLM |
|---|---|---|---|
| **EA (Fase 4)** | Razona confluencias por **scoring que GENERALIZA** (combina confluencias similares-no-exactas según metodología + contexto de la zona en tiempo real donde puede actuar) | Sí | No |
| **Enjambre** | Laboratorio + copiloto **continuo en tiempo real**: descubre confluencias nuevas, las toma en vivo vía TV MCP, discute si una entrada se abre o no, **guarda las que cierran positivas en TV con autoría**, y hace **scoring/atribución de agentes** | No | Sí |
| **Validación** | Replay / Strategy Tester IS/OOS 70/30 → cristaliza pesos/reglas | Sí | No |
| **Puente vivo** | Solo gate funcional determinista (noticias/macro, veto binario, fail-safe) | Sí | No |

**Línea dura inamovible:** el EA **nunca** consulta al LLM en runtime (rompería el backtesting, MQL5 no hospeda LLM, latencia). El enjambre alimenta al EA **vía validación**, no en vivo.

**Mandato holístico del usuario (textual):** *"no es solo el EA; si hay que refactorizar en algún lado, se hace — todo debe quedar bien, medido y conectado para que funcione."* → el diseño debe trazar la **cadena completa** y proponer cambios **donde toquen, Pine incluido**, sin violar las reglas duras.

---

## 2. Qué YA está decidido/construido (no rehacer)

- **Arquitectura Pine:** 1 core compartido + Visual + Strategy; EA MQL5 nativo sin webhook. Reglas duras en `CLAUDE.md` (anti-repaint, core byte-idéntico, ATR-relativo, R:R≥1:3, scoring direccional 42 confluencias, 0/0, gates de fase).
- **Pine Fase 1 en curso:** T01–T09b/T10 implementados y validados (swings, BOS/CHoCH, OB, FVG, P/D, EQH/EQL, pools persistentes + sweep). El scoring direccional (Sprint 2.1) y la calibración (Fase 3 IS/OOS) son los que cristalizan pesos.
- **Módulo mentores (pipeline):** `process-channel.ps1`→`process-video.ps1`→`fw_transcribe.py` (ingesta) → `hermes-analyze-mentor.ps1` (ficha 9 campos) → `build-personality.ps1` (skill `mentor-<slug>`). Hermes con Gemini (gemini-2.5-flash/pro).
- **Hermes Workspace** expone cron (Trabajos), kanban (Tasks), swarm, conductor, operations, knowledge, skills, MCP, perfiles. `hermes cron/kanban/profile` existen (0.15.2). TV MCP = **single-instance** (CDP 9222): solo UN agente lee TV.
- **Decisión enjambre=laboratorio** (ADR-005) ampliada por ADR-007 (continuo + scoring de agentes).

---

## 3. Lo que FALTA diseñar (el encargo)

### 3.A — Motor de razonamiento del EA (lo central, Fase 4 — spec, no código)
Diseñar **cómo el EA "razona" confluencias de forma determinista y generalizable**:
- Cómo el **scoring direccional** (scoreLong/scoreShort, 42 confluencias §4.8) **generaliza**: dispara con confluencia *suficiente* aunque no sea la combinación exacta (umbral, pesos, no exact-match). Definir el modelo de combinación (suma ponderada, gating por contexto, mínimos por familia, etc.) y cómo se **mide** (qué hace que una confluencia "similar" cuente).
- **Contexto de zona en tiempo real:** cómo el EA pondera "lo que está pasando ahora en la zona donde puede actuar" (mitigación viva, sweep reciente, premium/discount, sesión) sin repaint y sin LLM.
- **Trazabilidad EA↔Pine:** mapeo función-a-función Pine→MQL5 (golden tests, ADR-002) para que el EA ejecute exactamente lo validado. Señalar si el scoring actual de Pine necesita **refactor** para soportar la generalización (p.ej. exponer scores parciales por familia, normalización ATR, umbrales configurables) — **aquí es donde "tocar Pine si hace falta"**.
- **R:R≥1:3** y gestión (SL/TP) como parte del razonamiento, no add-on.

### 3.B — Runtime del enjambre (construible ya; es Hermes, no Pine/EA)
Diseñar el **loop continuo** del enjambre como laboratorio:
- **Vigía/cron** que toma confluencias en vivo vía TV MCP (solo este agente toca TV) y abre eventos en kanban.
- **Protocolo de discusión** (rondas 1/2 + síntesis) con voto **estructurado** (contrato I/O): sesgo, nivel, invalidación, confianza, confluencias citadas (ancladas a `reglas-smc-ict.md`).
- **Regla de registro:** al cerrar **positiva en TV** (replay/seguimiento), guardar la confluencia + **autoría** (qué agente la propuso) en `docs/laboratorio/`.
- **Scoring/atribución de agentes:** track record por mentor (acierto/fallo, R), cómo se **combinan votos** (ponderar por track record), y cómo eso retroalimenta qué confluencias se priorizan para validar.
- Restricciones: TV MCP single-instance; cuota free-tier Gemini (intervalo de cron, gating de "accionable"); persistencia (cron+kanban, no `delegate_task`).

### 3.C — Traza de la cadena completa + refactors
Producir un **diagrama y una tabla de extremo a extremo**: enjambre (descubre) → diario laboratorio → validación IS/OOS → cristalización de pesos → Pine scoring → EA MQL5. En cada eslabón: qué existe, qué falta, **qué refactor se necesita** para que quede "medido y conectado". Marcar explícitamente cualquier cambio en Pine/core y cómo respeta core-sync, anti-repaint y ADR-002 (umbrales congelados hasta Fase 3).

### 3.D — Integración del GAP de conceptos al Pine master plan (decisión del usuario)
Los mentores ICT enseñan ~25-30 conceptos que **NO están** en `reglas-smc-ict.md`. **Decisión del usuario:** integrarlos al plan maestro de Pine por el **MISMO proceso que todos** (no atajos), porque **Pine y el EA deben verlos, identificarlos y calcularlos como confluencias**. Insumo completo: **`docs/planes/MATRIZ-conceptos-cobertura.md`** (inventario have/falta/variante + clasificación por tipo).
- **Revisar** `WORKPLAN-MAESTRO-V2.md` §4.8 (42 confluencias) + `docs/workplan/PINE-PLAN.md` + `reglas-smc-ict.md` y decidir, por cada concepto faltante, **cuál es:**
  - **primitiva nueva de detección** (Vacuum/Propulsion Block, Volume Imbalance/SIVI/BIVI, Immediate Rebalance, BPR, CISD, Breakaway Gap, IPR, Standard Deviation, IFVG/True FVG como variantes propias, niveles-gap de apertura NWOG/NDOG/ORG, SMT≈requiere símbolo correlacionado) → entra por el pipeline estándar (spec cuantificada → `f_detect*` puro → 0/0 + core-sync → validación ≥90 → confluencia §4.8 + golden test MQL5);
  - **sesgo/contexto** (Draw on Liquidity, IRL/ERL, HRLR/LRLR, IPDA, PDArray Matrix) → alimenta el bias/scoring, no es zona;
  - **modelo de entrada / composición** (IOFED, ICT Entry Model 2022, Low Hanging Fruit, Unicorn, MMXM, Silver Bullet, Power of 3) → **NO es primitiva**; vive en el **motor de razonamiento del EA** (§3.A) como combinación de primitivas + timing;
  - **tiempo/macro** (NY Lunch/Midnight/ORG macros, RTH/ETH) → extiende §3.4 Kill Zones;
  - **noticias** (NFP) → el **gate determinista** de ADR-005, no confluencia;
  - **teoría propia a escrutar** (Gray Pool, Event Horizon, Price Delivery Continuum, Early Buyer/Seller) → validar valor real vs reempaque (campo 9).
- **Entregar:** un plan de cómo se amplían las confluencias y los sprints de Fase 1 para absorber el gap **sin romper** el scoring ya validado ni la congelación ADR-002 (se define mecánica; pesos en Fase 3). El EA generaliza sobre el set ampliado.

### 3.E — PILOTO: UN agente de referencia completo ("No soy liquidez") + entorno Hermes
**Norte del usuario:** se baja TODO "No soy liquidez" y se usa **SOLO este mentor como ejemplo** para **rediseñar todo lo que se hará en el enjambre (cron, task/kanban, swarm, workspace, etc.)**. El objetivo es dejar **UN agente construido de punta a punta** —con todo lo que necesita y todo lo que le solicita al workspace— de modo que **los demás mentores se clonen/ajusten de esa plantilla** según la función que cada uno cumpla.
- Diseñar (estructura/ingeniería) el **entorno completo del agente piloto**: su perfil/skill, sus carpetas de knowledge, qué herramientas de Hermes usa (cron, kanban, file, MCP TV), qué le pide al workspace, cómo entra al loop continuo del enjambre, cómo emite su voto y cómo registra en el diario de laboratorio.
- Producirlo como **plantilla parametrizable** (el resto de mentores = misma estructura, distinta ficha/knowledge/función). Entregar los **documentos de creación del entorno** (qué crear en Hermes y en el repo).
- **Insumo:** el curso completo de "No soy liquidez" (ficha 9 campos + knowledge por tema) más sus playlists extra y el canal ICT (fuente raíz de los conceptos).

---

## 4. Restricciones y reglas duras (no negociables)
- Sin MQL5/Pine nuevo en este handoff (solo diseño). Nada de código antes del gate Fase 4.
- Anti-repaint `[D-PINE-03]`; core byte-idéntico (core-sync); ATR-relativo; R:R≥1:3; 0/0; ningún gate se salta.
- Umbrales/pesos **congelados hasta Fase 3** (ADR-002): el diseño no "ajusta" umbrales, define la *mecánica*.
- El EA no consulta LLM en runtime (ADR-005/007). Único puente vivo = gate determinista.
- Símbolo-agnóstico (ADR-001): validar en EURUSD primero.
- **NO duplicar lo existente:** Opus Max no recrea ni altera conceptos/objetos ya creados ni los que ya están en `reglas-smc-ict.md`/el Pine validado (T01–T10). Solo **construye sobre ellos** o añade lo que falta (el gap §3.D). Antes de proponer un concepto, verificar que no exista ya (matriz).
- **Fuera del alcance de Opus Max:** la generación de los **documentos de comandos de descarga** (listas por playlist, lotes de 5) la hace **Claude Code en la sesión siguiente**, NO Opus Max. Este handoff es estructura/ingeniería, no operación de descarga.

## 5. Entregables esperados de Opus Max
1. **Spec del motor de razonamiento del EA** (§3.A) con el modelo de generalización medible y el mapeo Pine→MQL5.
2. **Diseño del runtime del enjambre** (§3.B): cron/kanban, contrato de voto, regla de registro, scoring de agentes.
3. **Traza end-to-end + lista de refactors** (§3.C), Pine incluido, con justificación contra reglas duras.
4. **Riesgos, preguntas abiertas y plan de construcción por fases** (qué se puede pilotar ya vs qué espera a Fase 4).
5. Usar agentes internos: `smc-architect` (decisiones de arquitectura/ADR), `planner`/`plan-eng-review`, `smc-backtesting-analyst-agent` (anti-overfitting), `smc-code-explorer` (trazas Pine).

## 6. Insumos de conocimiento (mentores) que alimentan esto
- **Mentores SMC** (No soy liquidez ✅, Profittrading, TJ Trading, Fedex): metodología/confluencias → grounding del scoring y de qué confluencias buscar.
- **Boxxocode** (experto estrategias/automatización-EA): backtesting, money management, construcción de EAs → insumo directo del **motor del EA** y Fase 4.
- Cada mentor = 1 agente con **varias carpetas de knowledge** (`knowledge/<slug>/<tema>.md`). Ver `ESQUEMA-HERMES-mentor-module.md` §3.

## 7. Adopciones del ecosistema (revisión de `LLMQuant/awesome-trading-agents`)
Evaluar (no adoptar a ciegas) estos proyectos open-source para acelerar el diseño:
- **`MobiusQuant/OpenMobius-skill`** — skill de **conocimiento ICT/SMC compatible con Hermes** (knowledge cards, datos, indicadores, gráficos). Candidato directo para (a) **grounding de los mentores** y (b) **acelerar el cierre del gap de conceptos** (§3.D). Revisar qué conceptos cubre vs nuestra matriz.
- **`mnemox-ai/tradememory-protocol`** — **Memory MCP** que registra razonamiento de decisión + resultado + evidencia de revisión (17 tools). Candidato a **sustrato del diario de laboratorio + scoring/atribución de agentes** (§3.B) en vez de construirlo desde cero.
- **`TauricResearch/TradingAgents`** (paper arXiv 2412.20138) — framework de **debate** (analistas + bull/bear + trader + riesgo + PM). Referencia para el **protocolo de rondas 1/2** y la estructura de prompts/roles.
- **`flash131307/multi-agent-investment`** y **`FinStep-AI/ContestTrade`** — "LLM propone, **capa determinista decide**" y "agentes **compiten** antes de elegir": **precedente directo de ADR-007** (enjambre cualitativo + scoring determinista; combinación de votos).
- **MT5 (Fase 4):** `ariadng/metatrader-mcp-server`, `Qoyyuum/mcp-metatrader5-server` (solo-lectura para laboratorio; la escritura la hace el EA nativo). **TV alterno de referencia:** `atilaahmettaner/tradingview-mcp`.

## 8. Arquitectura de conocimiento / almacenamiento (optimización de peso)
Con mentores de 100+ videos, las transcripciones pesan. Diseñar así:
- **Fuente única en Obsidian**, sin duplicar a `~/.hermes/knowledge/`. El agente lee **on-demand** (toolset `file`/grep o MCP de memoria), no copia.
- **El agente NO carga las transcripciones crudas** (millones de tokens). Su grounding = **síntesis compacta** (`ficha-mentor.md` + 1 resumen por tema). Las crudas = archivo/respaldo (comprimible tras sintetizar).
- **Recuperación (RAG):** vía `tradememory-protocol`/`gbrain` o búsqueda por archivo. Definir el contrato de recuperación (qué se carga, cuándo).
