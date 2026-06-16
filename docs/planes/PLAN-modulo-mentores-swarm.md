# Plan — Módulo Mentores + Swarm  ·  v2 (corregido por Opus, Sesión-025)

> **v2 (2026-06-16):** revisión integral del plan por Opus (el handoff de
> [`HANDOFF-OPUS-MAX.md`](HANDOFF-OPUS-MAX.md)). Arquitectura raíz fijada en
> **[ADR-005](../adrs/ADR-005-enjambre-laboratorio-no-runtime-ea.md)**. Workflow canónico:
> [`../MODULO-MENTORES-WORKFLOW.md`](../MODULO-MENTORES-WORKFLOW.md). La v1 (Sesión-024) queda abajo en
> "Cambios respecto a v1". **Esta sesión NO ejecuta nada — solo deja el plan corregido.**

## Estado de lo construido (Sesión-024) — verificado contra la realidad
Los 5 scripts del pipeline existen y **hacen lo que el plan dice** (verificado contra `config.yaml` real):
`gemini-2.5-pro` (MAP) y `claude-sonnet-4-6` (REDUCE) están en Puter ✅ · `deepseek-v4-flash` existe (override
válido) ✅ · `mcp_servers: tradingview-desktop` `enabled` ✅ · `max_concurrent_children: 3` ✅ · sidecar
`model.txt` coherente entre `build-personality` y `hermes-chat-mentor` ✅. **Hermes real = 0.15.2.**

---

## PARTE A — Arquitectura (lo que más cambió) · [ADR-005]
**El enjambre es laboratorio + copiloto, NO runtime del EA.** Tres tiempos que no se mezclan:
Descubrimiento (enjambre, offline) → Validación (Strategy Tester IS/OOS, determinista) → Ejecución (EA MQL5
nativo). El EA **hereda** reglas cristalizadas; **no consulta** al enjambre. Único puente EA↔exterior en vivo:
**gate funcional determinista** (noticias/macro como veto binario con fail-safe; fuente **TBD**).
- **Modo Laboratorio:** enjambre opina sobre histórico/replay → propone y juzga confluencias (informe, no
  orden).
- **Modo Copiloto:** enjambre opina en vivo vía MCP TV para asistir **tu** decisión manual/paper en fase TV.
- Sin LLM, sin webhook, sin consulta al enjambre en el runtime del EA.

## PARTE B — Decisión de modelo (sin cambios)
Único `claude-sonnet-4-6`/Puter por defecto + override por mentor (`modelo:` → sidecar `model.txt`). Orden:
`-Model` → sidecar → default. Siempre `--provider puter`.

## PARTE C — Diseño del Swarm (corregido)
1. **3 capas de contexto por agente** (Knowledge / Expertise / Norms), corregidas para el proyecto:
   - Knowledge: Expertos → `reglas-smc-ict.md §`; Mentores → ficha; Funcionales → su fuente de datos.
   - Expertise: Mentores → ficha 3/7/8 (canal real); Expertos → criterio válido/inválido **alineado al Pine
     real**. Versionado por frontmatter.
   - Norms: **dominio** (por agente, en SKILL.md) + **riesgo** (GLOBAL, una fuente, **en código** Pine/EA, no
     por-mentor) + **validador determinista** en Orchestrator/Confluencia (descarta propuestas sin R:R≥1:3).
   - **No** se crea `/context/<mentor>/{knowledge,expertise,norms}.md` (fragmenta la verdad). Cada agente =
     skill de Hermes que **referencia** su grounding + Norms globales.
2. **Esquema de voto** (contrato I/O que faltaba): `{agente, direccion, postura, confianza, concepto,
   criterio, evidencia}`. El Supervisor de Confluencia consolida **determinista** y **no recalcula** el score
   §4.8 (capa cualitativa de revisión/veto, no un segundo score).
3. **Roster (4 familias):** Mentores · Expertos E1–E6 · Funcionales (Noticias, Order Flow, Tendencias-MTF) ·
   Control (Router, Supervisor de Confluencia, Orchestrator, Entrenador, **Escéptico** = ataca toda confluencia
   que backtestee bien, **independiente** del proponente). Flujo → **informe de confluencias
   +/–** (diario de laboratorio) y, en modo copiloto, → **tú decides**. **No** termina en MT5.
4. **MCP TV:** solo el Router toca TV (secuencial; una instancia CDP 9222). **Async:** no existe en 0.15.2;
   `delegate_task` síncrono para el broadcast.

## PARTE D — Metodología de laboratorio (NUEVO)
El Strategy abre/cierra las entradas solo (es el backtester). Ciclo de una confluencia: hipótesis (agente) →
regla en `SMC-Strategy.pine` → backtest IS/OOS 70/30 → `smc-backtesting-analyst` juzga → Replay para casos
dudosos → entra/descarta. **Escalera:** backtest TV → replay → paper TV → [F4] EA en MT5 tester (+paridad) →
[F5] demo MT5 → real. **Diario** en `docs/laboratorio/`. **No** construir plataforma nueva: orquestar Hermes +
MCP TV + Strategy Tester + skills `smc-backtesting-analyst`/`smc-replay`/`smc-multi-scan`. MT5 (años de tick
data) entra en **Fase 4**.

## PARTE E — Pipeline de mentor unificado
Canónico = pipeline S024 (ficha → `mentor-<slug>`). **Rescatar** del V1 el campo **9. Conflictos con el
sistema 2.0** (cruza al mentor con `reglas-smc-ict.md` + scoring). **Archivar** las skills V1 (`consult-mentor`,
`mentor-extract-profile`, `mentor-transcribe`) — no borrar sin backup.

---

## Cambios respecto a v1 / Divergencias plan↔realidad resueltas
1. **Flujo terminaba en MT5** (enjambre dispara trades) → enjambre = laboratorio + copiloto; EA hereda reglas;
   gate funcional único puente. **[ADR-005]**
2. El prompt de Sonnet asumía **Hermes v0.11.0** → real **0.15.2** (el `0.11.0` venía del `/health`
   hardcodeado de `hermes-proxy.mjs`, engañoso).
3. Asumía **OpenRouter** → real **Puter/Sonnet** (OR suspendido). El `proxy.mjs` usa OR con key hardcodeada,
   pero es **puente de la UI del Workspace**, no la capa de decisión.
4. Listaba agentes inexistentes (**Harmonic Concept, ADT, Argentina-Confluencia**) → real **E1–E6 + mentores
   por canal + funcionales + control**.
5. Asumía **webhook** ("en construcción") → **sin webhook** (regla dura).
6. Ponía las Norms de riesgo en **`proxy.mjs`** → corregido: Norms en **Pine/EA** + validador en el
   Orchestrator. El proxy es puente de UI, capa equivocada.
7. Ponía Norms **por-mentor** → corregido: Norms de riesgo **globales** (una fuente); el mentor solo *sugiere*
   (Expertise).
8. **Faltaba el contrato I/O** entre agentes → añadido el **esquema de voto**.
9. **Faltaba alineación experto↔Pine** → el Expertise de E1–E6 se ata a la implementación real.
10. **Dos pipelines de mentor conviviendo** (V1 PERFIL-10 + S024 ficha-8) → unificar en S024 + rescatar campo
    9; archivar V1.
11. **Issues #5586/#11508** citados como evidencia de "no async" → **marcar para verificar** (números
    inverosímiles); el hecho técnico se sostiene por el código instalado.
12. **flag `--yolo` vs `-yolo`** y **toolset `file`/MCP en `hermes chat`** → confirmar en el E2E.

## Nota de seguridad (fuera de alcance — pendiente)
`D:\CODE\hermes\hermes-proxy.mjs:5` tiene una **API key de OpenRouter en texto plano**; `config.yaml` tiene la
JWT de Puter y una key de NIM en texto plano. Va contra "secretos solo por env var" (incidente previo SEC-01).
Rotar/mover a `.env` cuando se aborde (verificar antes si el `.mjs` está versionado en algún git).

---

## Verificación end-to-end (NO en esta sesión)
Ver [`../MODULO-MENTORES-WORKFLOW.md`](../MODULO-MENTORES-WORKFLOW.md) §Verificación. Primer mentor real
sugerido: `process-channel.ps1 -ChannelUrl "https://www.youtube.com/@Boxxocode/videos" -Mentor "boxxocode"
-MaxVideos 3`.

## Pine T08 EQH/EQL (FUERA de alcance — otra sesión)
Al abrir TV: confirmar 0/0 en los 3 scripts y re-guardar el slot por el cambio de etiqueta de S022. Concepto
en `reglas-smc-ict.md §2.4` (`f_detectEQHL`).

## Archivos de este plan
- ACTUALIZADOS: `docs/MODULO-MENTORES-WORKFLOW.md` (canónico), este plan.
- NUEVO: `docs/adrs/ADR-005-enjambre-laboratorio-no-runtime-ea.md`.
- SIN TOCAR: el CORE de Pine, los 5 scripts (el código ya construido es correcto; los cambios son de diseño/
  doc), los wheels nvidia-cu12.
- PRÓXIMA SESIÓN (al construir): añadir campo 9 a `hermes-prompt-analisis-mentor.txt`; archivar skills V1.
