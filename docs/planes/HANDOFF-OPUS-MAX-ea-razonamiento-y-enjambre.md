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

---

## 4. Restricciones y reglas duras (no negociables)
- Sin MQL5/Pine nuevo en este handoff (solo diseño). Nada de código antes del gate Fase 4.
- Anti-repaint `[D-PINE-03]`; core byte-idéntico (core-sync); ATR-relativo; R:R≥1:3; 0/0; ningún gate se salta.
- Umbrales/pesos **congelados hasta Fase 3** (ADR-002): el diseño no "ajusta" umbrales, define la *mecánica*.
- El EA no consulta LLM en runtime (ADR-005/007). Único puente vivo = gate determinista.
- Símbolo-agnóstico (ADR-001): validar en EURUSD primero.

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
