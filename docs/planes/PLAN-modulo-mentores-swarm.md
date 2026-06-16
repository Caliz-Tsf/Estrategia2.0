# Plan — Módulo Mentores (5 scripts) + Diseño del Swarm de agentes

> Plan aprobado en Sesión-024 (2026-06-16). Copia versionada del plan de trabajo
> (`~/.claude/plans/opus-ayudame-con-las-happy-codd.md`). Handoff de revisión:
> [`HANDOFF-OPUS-MAX.md`](HANDOFF-OPUS-MAX.md). Workflow ejecutado:
> [`../MODULO-MENTORES-WORKFLOW.md`](../MODULO-MENTORES-WORKFLOW.md).

## Contexto
El usuario cerró la S023 dejando tres tareas para la siguiente sesión, ya decididas en esta planificación:

1. **Construir el módulo mentores** (los 5 scripts del pipeline transcripción→personalidad) según el
   workflow rediseñado en S023. Hermes + workspace ya están operativos (Claude Sonnet 4.6 vía Puter;
   faster-whisper en GPU RTX 3070). Ver memoria `[[mentores-modulo-plan]]`, `[[hermes-puter-provider]]`,
   `[[hermes-workspace-setup]]`.
2. **Decidir el modelo de los mentores** → DECIDIDO: **único `claude-sonnet-4-6` (Puter) por defecto, con
   override opcional por mentor**. La fidelidad de la personalidad la da la ficha/skill, no el modelo.
3. **Diseñar el grupo de agentes (swarm) + restricciones** → DECIDIDO: **solo propuesta + diagrama** esta
   sesión (roles, funciones, conexiones, restricciones). Construirlos es Fase 5 (requiere mentores reales
   primero). Entregable = doc + diagrama renderizado.

Aparte (NO en este alcance, va DESPUÉS y casi seguro en otra sesión): **Pine T08 EQH/EQL** — al abrir TV
confirmar 0/0 y re-guardar el slot por el cambio de estilo de etiqueta de S022.

> Nota fija: los wheels `nvidia-cublas-cu12` + `nvidia-cudnn-cu12` (~1.2 GB) habilitan la GPU de
> transcripción — **no tocarlos**.

---

## PARTE A — Decisión de modelo (cómo se implementa el override)
- **Default global:** `claude-sonnet-4-6 --provider puter` para TODOS los mentores (consistente, barato,
  visión+código). No se confía en el routing de `task_profiles` porque su cadena prioriza NIM/OR (caídos).
- **Override por mentor (opcional):** la `ficha-mentor.md` puede declarar en su frontmatter `modelo: <id>`
  (ej. `deepseek-v4-flash` para uno simple). Mecánica:
  - `build-personality.ps1` copia ese valor a un sidecar `model.txt` dentro de la skill.
  - `hermes-chat-mentor.ps1` resuelve el modelo en este orden: parámetro `-Model` explícito → `model.txt`
    de la skill → default `claude-sonnet-4-6`. Siempre `--provider puter`.
- Esto da "único por defecto" + "selector manual" sin bloque `personalities:` (que está vacío y no se lee).

---

## PARTE B — Construir los 5 scripts + doc (Fases 1-4)
Patrón común a respetar (copiar de `scripts/hermes-transcribe.ps1`): `$ErrorActionPreference='Stop'`,
helpers `Write-Step/Ok/Bad`, archivo **solo-ASCII** (PS 5.1 lee .ps1 como ANSI; el `.md`/`.txt` de salida sí
va UTF-8 sin BOM), aplanado del prompt antes de `hermes chat`, invocar con `--yolo -Q -m <modelo>
--provider puter`. Modelo siempre forzado a Puter.

- **B0. Doc** → `docs/MODULO-MENTORES-WORKFLOW.md` (4 fases + diagrama del swarm + tabla de scripts).
- **B1. Fase 1 — Ingesta** → `scripts/process-channel.ps1` (determinista, sin LLM): `yt-dlp
  --flat-playlist` → itera `process-video.ps1 -SubFolder "Mentores\<n>"`. Genera `Index.md`.
- **B2. Fase 2 — Análisis (map-reduce)** → `scripts/hermes-analyze-mentor.ps1` +
  `scripts/hermes-prompt-analisis-mentor.txt` (8 campos). MAP (gemini/deepseek) → REDUCE (Sonnet) →
  `ficha-mentor.md`. **Orientado a archivos** (Hermes lee/escribe rutas con el toolset `file`) para evitar el
  límite de longitud de comando con transcripciones largas.
- **B3. Fase 3 — Personalidad** → `scripts/build-personality.ps1`: ficha → skill `mentor-<slug>`
  (`SKILL.md` + reglas de rol + ruta del vault + sidecar `model.txt` si hay override).
- **B4. Fase 4 — Uso** → `scripts/hermes-chat-mentor.ps1`: resuelve modelo y abre
  `hermes chat -s mentor-<slug> --provider puter -t terminal,file`.
- **B5. Limpieza** → `hermes-transcribe.ps1` default Puter (ya hecho en S023).

---

## PARTE C — Diseño del Swarm (solo propuesta + diagrama)
**Principio de restricción:** cada agente tiene dominio estricto; el `system_prompt` prohíbe responder fuera
de él. Grounding: mentores → transcripciones; expertos-concepto → `docs/reglas-smc-ict.md`; funcionales →
fuentes web/datos; control → solo meta.

**Expertos-concepto (24 conceptos de reglas-smc-ict.md en 6 dominios):**
E1 Estructura (§1.1-1.6) · E2 Order Blocks (§2.1, 2.6, 2.7, 2.8) · E3 Imbalance/FVG (§2.2, §4.1) ·
E4 Premium/Discount & OTE (§2.3, §2.5) · E5 Liquidez (§2.4, §3.1, 3.2, 3.3, 3.5, 3.6, 3.7) ·
E6 Tiempo & Sesiones (§3.4, §4.2, §4.3).

**Roster (4 familias):** Mentores (SMC + estrategia, p.ej. `mentor-boxxocode`) · Expertos-concepto E1–E6 ·
Funcionales (Noticias, Order Flow, Tendencias-MTF/Macro) · Control (Router, Supervisor de Confluencia,
Orchestrator, Entrenador). Flujo: Pine/TV → Router (broadcast) → opinadores → Confluencia (42 confluencias
§4.8) → Orchestrator (R:R≥1:3 + filtros) → MT5. Entrenador = loop offline que refina mentores.

**C.2 MCP TV:** Hermes ya tiene `mcp_servers: tradingview-desktop`. Los agentes pueden manejar TV
**secuencialmente** (uno por uno); **NO en paralelo** (una sola instancia CDP 9222 → se pisan). Recomendado:
solo el Router toca TV y reparte el contexto.

**C.3 Delegación async:** hermes-agent **0.15.2 NO** trae `delegate_task_async`/`async_delegation` (issue
[#5586](https://github.com/NousResearch/hermes-agent/issues/5586) abierto;
[#11508](https://github.com/NousResearch/hermes-agent/issues/11508) confirma el bloqueo). `delegate_task`
corre hijos en paralelo (hasta `max_concurrent_children: 3`) pero bloquea al padre. Estables:
`terminal(background=True, notify_on_complete=True)` y `cron`. **Recomendación:** usar `delegate_task` para el
broadcast ("junta y decide"); `terminal background`/`cron` para tareas largas; no esperar async.

---

## PARTE D — Pine T08 EQH/EQL (FUERA de alcance hoy)
Va después, casi seguro en otra sesión. Al abrir TV: confirmar 0/0 en los 3 scripts y re-guardar el slot por
el cambio de etiqueta de S022. Concepto en `reglas-smc-ict.md §2.4` (`f_detectEQHL`).

---

## PARTE E — Cierre + Handoff a Opus Max
Versionar el plan en `docs/planes/` (este archivo), crear `docs/planes/HANDOFF-OPUS-MAX.md`, commit+push en
`pine/sistema-completo`, entregar URLs de GitHub, cierre con `/smc-session-close`. El handoff instruye a Opus
Max (nueva sesión de Claude Code sobre este repo) a revisar/reconstruir el plan invocando los agentes/skills
(`smc-architect`, `planner`, `plan-eng-review`, `autoplan`).

---

## Verificación end-to-end
1. `process-channel.ps1 -ChannelUrl <playlist> -Mentor "Test" -MaxVideos 2` → `.md` + `Index.md`.
2. `hermes-analyze-mentor.ps1 -MentorFolder "Mentores\Test"` → `ficha-mentor.md` (8 secciones `##`).
3. `build-personality.ps1 -MentorFolder "Mentores\Test"` → skill `mentor-test` en `~/.hermes/skills/`.
4. `hermes-chat-mentor.ps1 -Mentor test -q "<pregunta>"` → responde en voz/metodología, cita transcripciones,
   rechaza lo de fuera de dominio.
5. Override: `modelo: deepseek-v4-flash` en una ficha → el launcher lo usa.
6. Confirmar Puter/Sonnet + transcripción por GPU.
7. Primer mentor real (opcional): `process-channel.ps1 -ChannelUrl "https://www.youtube.com/@Boxxocode/videos"
   -Mentor "boxxocode" -MaxVideos 3` → ingesta + ficha + skill; clasificar su contenido.

## Archivos
- NUEVOS (B-C): `docs/MODULO-MENTORES-WORKFLOW.md`, `scripts/process-channel.ps1`,
  `scripts/hermes-prompt-analisis-mentor.txt`, `scripts/hermes-analyze-mentor.ps1`,
  `scripts/build-personality.ps1`, `scripts/hermes-chat-mentor.ps1`.
- NUEVOS (E): `docs/planes/PLAN-modulo-mentores-swarm.md`, `docs/planes/HANDOFF-OPUS-MAX.md`.
- REUTILIZA: `scripts/process-video.ps1`, `scripts/fw_transcribe.py`, `scripts/hermes-transcribe.ps1`,
  `~/.hermes/skills/mentor-extract-profile/SKILL.md`, `docs/reglas-smc-ict.md`.
- NO TOCAR: el CORE de Pine, los wheels nvidia-cu12.
