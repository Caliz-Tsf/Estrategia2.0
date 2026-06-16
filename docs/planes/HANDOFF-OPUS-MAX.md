# Handoff a Opus Max — Revisión del plan del Módulo Mentores + Swarm

> Pega este prompt en una **nueva sesión de Claude Code (modelo Opus)** abierta sobre este repo
> (`D:\CODE\Estrategia2.0`). Así tiene acceso a los agentes/skills que debe invocar.

---

Eres Claude Opus revisando un plan de arquitectura del proyecto **Estrategia 2.0** (bot SMC/ICT). Trabajas
en Claude Code sobre este repo, así que tienes acceso a sus agentes y skills — **úsalos**.

**Propósito / finalidad del workflow a revisar:** construir el *Módulo Mentores* de Hermes —un pipeline que
transcribe canales de YouTube de mentores/estrategas y los convierte en agentes-skill con personalidad— y
diseñar el *Swarm* de agentes (mentores + 6 expertos-concepto SMC + funcionales + control) que en Fase 5
opinarán en paralelo sobre las señales del Pine y votarán confluencia antes de decidir una entrada. El plan a
revisar es `docs/planes/PLAN-modulo-mentores-swarm.md` y su materialización está en
`docs/MODULO-MENTORES-WORKFLOW.md` + los scripts `scripts/process-channel.ps1`,
`scripts/hermes-analyze-mentor.ps1`, `scripts/build-personality.ps1`, `scripts/hermes-chat-mentor.ps1`,
`scripts/hermes-prompt-analisis-mentor.txt`.

**Tu tarea:**
1. Lee el plan y TODAS las dependencias listadas abajo.
2. Evalúa si es correcto y viable: ¿cumple las reglas duras de `CLAUDE.md` (anti-repaint, ATR-relativo,
   R:R≥1:3, símbolo-agnóstico, referencias externas permitidas)? ¿es viable en el Hermes real (0.15.2,
   Puter/Sonnet, `delegate_task` síncrono, MCP TV de una sola instancia)? ¿los scripts ya escritos hacen lo
   que el plan dice?
3. Di explícitamente **qué cambiarías y dónde hay divergencias** entre lo que el plan asume y lo que de
   verdad existe en config/código.
4. **Reconstruye o corrige el plan completo.**

**Invoca nuestros agentes/skills** según lo necesites: `smc-architect` (decisiones de arquitectura/ADR),
`planner` o el agente `Plan`/`architect` (rediseño), las skills `plan-eng-review` / `autoplan` /
`writing-plans` (revisión y estructura de plan), `smc-code-explorer` (rastrear scripts/config). No asumas:
verifica contra los archivos.

**Entregable:** el plan corregido + una lista de cambios aplicados + las divergencias detectadas (plan vs
realidad) con su resolución.

---

## Dependencias a leer (rutas exactas)

**En el repo:**
- Plan: `docs/planes/PLAN-modulo-mentores-swarm.md`
- Workflow ejecutado: `docs/MODULO-MENTORES-WORKFLOW.md`
- Scripts nuevos: `scripts/process-channel.ps1`, `scripts/hermes-analyze-mentor.ps1`,
  `scripts/hermes-prompt-analisis-mentor.txt`, `scripts/build-personality.ps1`, `scripts/hermes-chat-mentor.ps1`
- Scripts base reutilizados: `scripts/process-video.ps1`, `scripts/fw_transcribe.py`,
  `scripts/hermes-transcribe.ps1`, `scripts/hermes-prompt-transcripcion.txt`
- Reglas duras/arquitectura: `CLAUDE.md` · SMC (24 conceptos): `docs/reglas-smc-ict.md`
- Plan maestro: `WORKPLAN-MAESTRO-V2.md` + `docs/workplan/`
- Estado: `memory/ESTADO-ACTUAL.md` · Doc mentores V1 (histórico): `docs/MODULO-MENTORES-V1.md`

**Fuera del repo (rutas absolutas):**
- Plan S023 original: `C:\Users\Fredd\.claude\plans\c-users-fredd-downloads-modulo-mentores-streamed-ullman.md`
- Hermes config (providers/modelos/`mcp_servers`/`delegation`): `C:\Users\Fredd\.hermes\config.yaml`
- Guía de modelos: `C:\Users\Fredd\.hermes\MODELO-GUIA.md`
- Skill de referencia: `C:\Users\Fredd\.hermes\skills\mentor-extract-profile\SKILL.md`
- Paquete instalado (verificar delegación): `C:\Users\Fredd\AppData\Roaming\Python\Python314\site-packages\tools\delegate_tool.py`

**Memorias** (se autocargan vía `MEMORY.md`): `mentores-modulo-plan`, `hermes-puter-provider`,
`hermes-workspace-setup`, `hermes-modelos-locales-pendiente`, `doc-updater-no-debe-tocar-git`.

## Decisiones ya tomadas (no re-litigar salvo que encuentres un error de fondo)
- Modelo de mentores: **único `claude-sonnet-4-6`/Puter por defecto + override por mentor** (sidecar `model.txt`).
- Swarm: **solo diseño** esta fase; construcción en Fase 5 (requiere mentores reales primero).
- Personalidad = **skill de Hermes por mentor** (no el bloque `personalities:`, que está vacío).
- Broadcast del swarm con `delegate_task` (síncrono); no esperar la feature async (#5586).
