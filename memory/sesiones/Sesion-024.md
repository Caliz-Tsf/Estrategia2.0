# Sesión 024 — 2026-06-16

> Sesión de **Hermes / módulo mentores** (NO sprint Pine). El core Pine no se tocó; check-core-sync OK,
> MISMO SHA 24c3a4a28fcf74c3 (415 líneas).

## Objetivo
Construir el módulo mentores (los 5 scripts del pipeline rediseñado en S023), decidir el modelo de los
mentores, diseñar el grupo de agentes (swarm) + restricciones, y dejar un handoff para que Opus Max revise
el plan.

## Hecho

### 1. Los 5 scripts del pipeline transcripción→personalidad
- `scripts/process-channel.ps1` — **Fase 1 (ingesta, sin LLM).** Resuelve la lista del canal/playlist con
  `yt-dlp --flat-playlist --print %(id)s` e itera `process-video.ps1 -SubFolder "Mentores\<slug>"` como
  proceso hijo (su `exit` no aborta el padre). Continúa si un video falla; genera/actualiza `Index.md`.
- `scripts/hermes-analyze-mentor.ps1` + `scripts/hermes-prompt-analisis-mentor.txt` — **Fase 2 (análisis
  map-reduce).** Los 8 campos de la ficha en el prompt. **Orientado a archivos:** la instrucción a Hermes
  referencia RUTAS (lee/escribe con el toolset `file`), nunca pasa el texto por la línea de comandos → evita
  el límite de longitud de Windows con transcripciones largas. MAP por video (`gemini-2.5-pro`/Puter) →
  REDUCE (`claude-sonnet-4-6`/Puter) → `ficha-mentor.md`. `-SinglePass` para 1 pase; `-Force` sobrescribe.
- `scripts/build-personality.ps1` — **Fase 3 (personalidad).** Lee la ficha → genera la skill de Hermes
  `mentor-<slug>` en `~/.hermes/skills/` (`SKILL.md` con reglas de rol + ruta del vault para recall) +
  sidecar `model.txt` si la ficha trae `modelo:` en el frontmatter.
- `scripts/hermes-chat-mentor.ps1` — **Fase 4 (launcher).** Resuelve modelo (`-Model` > sidecar `model.txt`
  > default `claude-sonnet-4-6`) y abre `hermes chat -s mentor-<slug> --provider puter -t terminal,file`
  (`-q` para one-shot).
- Los 4 `.ps1` pasan el parser de PowerShell 5.1 (verificado con `Parser::ParseFile`). Solo-ASCII.

### 2. Decisión de modelo
**Único `claude-sonnet-4-6`/Puter por defecto + override opcional por mentor.** La fidelidad la da la
ficha/skill, no el modelo. Override = `modelo:` en el frontmatter de la ficha → `build-personality.ps1` lo
copia a `model.txt` → el launcher lo aplica. (No se usa el bloque `personalities:`, que está vacío.)

### 3. Diseño del Swarm (solo propuesta + diagrama; construcción = Fase 5)
- `docs/MODULO-MENTORES-WORKFLOW.md` (doc canónico, reemplaza a V1): 4 fases + tabla de scripts + roster del
  swarm + principio de restricciones + diagrama mermaid.
- **4 familias:** Mentores (sub-tipos SMC y *estrategia*, p.ej. `mentor-boxxocode` del canal `@Boxxocode` —
  aporta ideas de estrategias como *sugerencias* que pasan por las reglas duras + expertos antes de
  adoptarse) · Expertos-concepto **E1–E6** (agrupan los 24 conceptos de `reglas-smc-ict.md`: E1 Estructura,
  E2 Order Blocks, E3 Imbalance/FVG, E4 Premium/Discount&OTE, E5 Liquidez, E6 Tiempo&Sesiones) · Funcionales
  (Noticias, Order Flow, Tendencias-MTF/Macro) · Control (Router, Supervisor de Confluencia, Orchestrator,
  Entrenador). Flujo: Pine/TV → Router (broadcast) → opinadores → Confluencia (42 confluencias §4.8) →
  Orchestrator (R:R≥1:3 + filtros) → MT5; Entrenador = loop offline.
- **MCP TV:** Hermes ya tiene `mcp_servers: tradingview-desktop`. Los agentes pueden manejar TV **secuencial**
  (uno por uno); **NO en paralelo** (una sola instancia CDP 9222 → se pisan). Recomendado: solo el Router
  toca TV y reparte el contexto.
- **Delegación async:** verificado en el código instalado — **hermes-agent 0.15.2 NO trae
  `delegate_task_async`/`async_delegation`** (issue #5586 abierto; #11508 confirma que `delegate_task`
  bloquea al padre). `delegate_task` corre hijos en paralelo (`max_concurrent_children: 3`) pero bloquea al
  padre. **Recomendación:** usar `delegate_task` síncrono para el broadcast ("junta y decide");
  `terminal(background=True, notify_on_complete=True)`/`cron` para tareas largas; no esperar async.

### 4. Handoff a Opus Max
- `docs/planes/PLAN-modulo-mentores-swarm.md` (plan versionado) + `docs/planes/HANDOFF-OPUS-MAX.md` (prompt
  para una nueva sesión de Claude Code Opus sobre este repo: leer dependencias, evaluar contra CLAUDE.md y el
  Hermes real, señalar divergencias y reconstruir/corregir el plan invocando `smc-architect`/`planner`/
  `plan-eng-review`/`autoplan`).

## Commit
- **5cc00f4** `feat(mentores): pipeline 5 scripts + diseno swarm + handoff Opus Max (S024)` — 8 archivos, 975
  inserciones, en `pine/sistema-completo`. (Los archivos de `~/.hermes/` no son del repo.)

## Pendiente próxima sesión (mentores)
Correr el pipeline end-to-end con un canal real (Boxxocode `-MaxVideos 3`) y verificar que Hermes escribe la
ficha vía toolset `file` + que el toolset MCP carga en `hermes chat`.

## Pine
Intacto. **Siguiente: F1-S1.2-T08 EQH/EQL.** Recordar de S022: re-lanzar TV al inicio, confirmar 0/0 en los 3
scripts y re-guardar el slot por el cambio de estilo de etiqueta (la conexión CDP se cayó tras esa inyección).

## Nota fija
Los wheels `nvidia-cublas-cu12` + `nvidia-cudnn-cu12` (~1.2 GB) habilitan la GPU de transcripción — no
borrarlos.
