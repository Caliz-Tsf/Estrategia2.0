# Sesión 025 — 2026-06-16

> Sesión de **revisión del plan del Módulo Mentores / Swarm** (NO sprint Pine; NO se ejecutó nada del
> pipeline). El core Pine no se tocó; check-core-sync OK, MISMO SHA 24c3a4a28fcf74c3 (415 líneas).
> Es la ejecución del handoff `docs/planes/HANDOFF-OPUS-MAX.md` por Opus en este repo.

## Objetivo
Revisar, corregir y mejorar el plan del módulo mentores + el diseño del swarm. Resolver la arquitectura
enjambre↔EA. Integrar el modelo de 3 capas (Knowledge/Expertise/Norms) que el usuario discutió con Sonnet.
Dejar el plan corregido y cerrar. **Sin ejecutar el pipeline.**

## Hecho

### 1. Auditoría plan↔realidad (verificada contra config/código real)
- Hermes real = **0.15.2** (no 0.11.0). `gemini-2.5-pro`/`claude-sonnet-4-6`/`deepseek-v4-flash` en Puter ✅.
  `mcp_servers: tradingview-desktop` enabled ✅. `max_concurrent_children: 3` ✅. Los 5 scripts hacen lo que
  el plan dice.
- **Hallazgo: dos pipelines de mentor conviviendo** — V1 (`consult-mentor` + `mentor-extract-profile` +
  `mentor-transcribe`, PERFIL 10 secciones, con "Conflictos con Strategy 2.0") y S024 (ficha 8 campos →
  `mentor-<slug>`). Decisión del usuario: **unificar en S024 + rescatar el campo "Conflictos con el sistema"**
  (nuevo campo 9 de la ficha); archivar V1.
- **Nota seguridad:** `hermes-proxy.mjs:5` con OR API key en texto plano + keys en `config.yaml` → pendiente
  rotar/mover a env.
- **A verificar en E2E:** flag `--yolo` vs `-yolo`; toolset `file`/MCP en `hermes chat`; issues #5586/#11508.

### 2. Arquitectura enjambre↔EA — ADR-005 (decisión raíz)
El usuario quería que los expertos opinaran en vivo para validar la entrada del EA. Se resolvió: **el enjambre
es laboratorio + copiloto, NO runtime del EA.** Tres tiempos: Descubrimiento (enjambre, offline) → Validación
(Strategy Tester IS/OOS, determinista) → Ejecución (EA MQL5 nativo). El EA hereda reglas cristalizadas; no
consulta al enjambre. Único puente en vivo = **gate funcional determinista** (noticias/macro, veto binario,
fail-safe; fuente TBD). Modo Copiloto da el "tiempo real" — pero su consumidor es el HUMANO en fase TV, no el
EA. Razones (en el ADR): rompe validez del backtest, fragilidad/latencia (Puter+1 TV CDP), TV≠MT5.

### 3. Las 3 capas (Knowledge/Expertise/Norms) integradas y corregidas
Idea buena de Sonnet, corregida: Knowledge = `reglas-smc-ict.md`/ficha; Expertise alineado al Pine real; Norms
de **riesgo GLOBALES y en código** (no por-mentor, no en `proxy.mjs`) + validador determinista en el
Orchestrator. **No** se crea el árbol `/context/<mentor>/...` (fragmenta la verdad); cada agente = skill que
referencia su grounding. El prompt de Sonnet partía de premisas de otro proyecto (v0.11.0, OpenRouter,
webhook, agentes Harmonic/ADT/Argentina inexistentes) — documentado en el plan.

### 4. Esquema de voto + metodología de laboratorio (NUEVO)
- **Esquema de voto** (contrato I/O que faltaba): `{agente, direccion, postura, confianza, concepto, criterio,
  evidencia}`; consolidación determinista que **no recalcula** el score §4.8.
- **Metodología de laboratorio:** el Strategy abre las entradas solo; los agentes proponen/juzgan. Ciclo:
  hipótesis → regla Pine → backtest IS/OOS → analista → replay. **Escalera:** backtest TV → replay → paper TV
  → [F4] EA en MT5 tester (+paridad) → [F5] demo MT5 → real. Diario en `docs/laboratorio/`. No construir
  plataforma nueva. MT5 (años) entra en F4.

## Archivos
- NUEVO: `docs/adrs/ADR-005-enjambre-laboratorio-no-runtime-ea.md`.
- REESCRITO: `docs/MODULO-MENTORES-WORKFLOW.md` (canónico, +arquitectura +3 capas +voto +laboratorio +campo 9).
- REESCRITO: `docs/planes/PLAN-modulo-mentores-swarm.md` → v2 + lista de 12 divergencias resueltas.
- Estado: `memory/ESTADO-ACTUAL.md`, este registro, memoria `[[mentores-modulo-plan]]`.
- **NO TOCADO:** CORE de Pine, los 5 scripts (el código es correcto; los cambios son de diseño/doc).

## Pendiente próxima sesión (mentores, al construir)
Añadir el campo 9 "Conflictos con el sistema" a `scripts/hermes-prompt-analisis-mentor.txt`; archivar skills
V1; correr el pipeline E2E con Boxxocode (`-MaxVideos 3`) y verificar toolset `file`/MCP + flag `--yolo`.

## Pine
Intacto. **Siguiente: F1-S1.2-T08 EQH/EQL.** Recordar de S022: re-lanzar TV, confirmar 0/0 en los 3 scripts,
re-guardar el slot por el cambio de estilo de etiqueta.

## Nota fija
Los wheels `nvidia-cublas-cu12` + `nvidia-cudnn-cu12` (~1.2 GB) habilitan la GPU de transcripción — no borrar.
