# MODULO-MENTORES-V1 — Personalidades indexadas en Estrategia 2.0
> ⚠ **PARCIALMENTE OBSOLETO (Sesion-023).** Los modelos citados aquí (nemotron-550b/49b vía
> `critical_analysis`/`personality_agent`) quedaron suspendidos: NIM/OR están caídos, el primario es ahora
> **Puter / claude-sonnet-4-6** (ver `~/.hermes/MODELO-GUIA.md`). El mecanismo de carga de personalidad
> (PERFIL en system_prompt / `personality_agent`) también se revisó: la dirección nueva es **una skill de
> Hermes por mentor** generada con `skill-creator`. El workflow definitivo de las 4 fases se está
> rediseñando en la próxima sesión (ver memoria `mentores-modulo-plan` y el plan de Sesion-023). Lo de abajo
> queda como histórico/inventario.
>
> Documentacion del modulo de mentores. NO reemplaza al WORKPLAN-MAESTRO-V2.md
> ni toca codigo Pine/MQL5. Es un modulo paralelo que aprende de las
> transcripciones y crea perfiles consultables desde Hermes.

## Que es

Un modulo del proyecto Estrategia 2.0 que:
1. Transcribe videos de canales SMC/ICT usando `scripts/process-video.ps1` (ya operativo, no se toca).
2. Procesa cada transcripcion para armar un PERFIL estructurado del mentor.
3. Permite invocar la "voz" de cada mentor desde cualquier chat de Hermes.
4. Compara posturas de varios mentores sobre un mismo tema.
5. Audita coherencia contra el sistema Pine/MQL5 (la "tabla de conflictos").

## Estado al cierre

| Pieza | Ubicacion | Estado |
|---|---|---|
| Dependencias transcripcion (`yt-dlp`, `ffmpeg`, `faster-whisper`) | PATH del sistema + `scripts/fw_transcribe.py` | OK (Sesion-019/020, GPU CUDA activa) |
| `scripts/process-video.ps1` | `D:\CODE\Estrategia2.0\scripts\` | OK (operativo, no modificar) |
| Vault destino transcripciones crudas | `D:\obsidian\boveda MENTE\Mente\Teoria SMC\` | OK |
| Carpeta modulo mentores (vault) | `D:\obsidian\boveda MENTE\Mente\Estrategia2.0\Mentores\` | creada en esta sesion |
| Template PERFIL | `Mentores/Template-PERFIL.mentor.md` | creado |
| Espejo Hermes por mentor | `~/.hermes/memoria/<slug>/PERFIL.md` | creado para `ict` |
| Skill `consult-mentor` (Workspace) | `~/.hermes/skills/consult-mentor/SKILL.md` | creado |
| MCP `claude-video-vision` (vision+audio) | `~/.hermes/config.yaml` (mcp_servers) | PENDIENTE — agregar manualmente (ver regla MCP-VISION al final) |

> Este modulo NO toca: `pine/`, `scripts/process-video.ps1`, `WORKPLAN-MAESTRO-V2.md`,
> `.claude/agents/*-smc-*`, ni `.claude/skills/smc-*`.

## MCP de video-vision (lo que faltaba del workspace)

Paquete npm: `claude-video-vision@1.2.1` (instalado globalmente desde la Sesion-007 area).
Binario: `C:\Users\Fredd\AppData\Roaming\npm\node_modules\claude-video-vision\dist\index.js`
Ruta npm-global: `C:\Users\Fredd\AppData\Roaming\npm`

Tools que expone (6):
- `video_watch` — extraer frames de un video por timestamps
- `video_info` — metadata del video (duracion, fps, codec)
- `video_setup` — configurar directorios de trabajo
- `video_configure` — ajustar backend (whisper local vs Gemini)
- `video_analyze` — analisis multimodal (frames + audio)
- `video_detail` — detalle de frames especificos

Variables de entorno opcionales:
- `GEMINI_API_KEY` / `GOOGLE_API_KEY` — si queres usar Gemini como backend de vision (mas rico que ffmpeg+whisper).
- Sin esas keys: cae automaticamente al backend local (ffmpeg + whisper local).

**REGLA:** el archivo `~/.hermes/config.yaml` esta protegido contra escritura automatica.
Claude debe agregar la siguiente entrada a mano bajo la seccion `mcp_servers:`:

```yaml
  # Vision+audio multimodal de videos. v1.2.1 ya instalada globalmente via npm.
  # Backend Gemini opcional (GEMINI_API_KEY) si se quiere vision real de frames.
  # Sin keys: cae al backend local ffmpeg+whisper.
  claude-video-vision:
    command: claude-video-vision
    args: []
    enabled: true
```

## Flujo end-to-end "agregar un mentor"

```
[1] USUARIO: "agrega al mentor ICT"  (o da un canal)
        |
        v
[2] skill `mentor-transcribe` (Workspace):
      -1 usuario pega URLs (o el script lista el canal con yt-dlp)
      -2 invoca:  powershell.exe -File D:\CODE\Estrategia2.0\scripts\process-video.ps1 `
                    -Url "<URL>" -Model medium -Language es
      -3 valida que .md se genero en Teoria SMC/
        |
        v
[3] skill `mentor-extract-profile`:
      - lee .md de vault
      - opcionalmente invoca mcp__claude-video-vision__video_analyze
        sobre frames clave del video (para captar visual del chart que muestra)
      - invoca un LLM (nemotron-550b segun MODELO-GUIA.md,
        perfil critical_analysis) para llenar el PERFIL
      - escribe Mentores/<slug>.PERFIL.md (con copia mirror en
        ~/.hermes/memoria/<slug>/PERFIL.md)
        |
        v
[4] al terminar, en cualquier chat de Hermes:
      "/consult-mentor ict, ¿que harias en este trade?"
      o  "como mentoria @smartrisk, que confluencia priorizar?"
      --> cautela: skill `consult-mentor` carga el PERFIL en system prompt
          y responde como el mentor con citas textuales
```

## Inventario de canales inicial

> Pendiente que el usuario complete con la lista corta que quiere arrancar.
> Recomendado: arranca con 2-3 mentores maximo (ej: ICT, uno de metodologia
> conservadora como Smart Risk, y uno mas agresivo como todotrader).

| # | Mentor (slug) | Canal YouTube | Videos indexados | PERFIL armado | Estado |
|---|---|---|---|---|---|
| 1 | ict | TBD | 0 | NO | DRAFT |
| 2 | TBD | TBD | 0 | NO | pendiente |

## Agentes del modulo

| Agente | Modelo | Funcion | Estado |
|---|---|---|---|
| `mentor-ict` | `personality_agent` (nemotron-49b tras leer PERFIL) | Voz del mentor ICT | FABRICA, falta PERFIL |
| `mentor-<slug>` | idem | voz del mentor N | FABRICA |
| `mentor-coordinator` | sonnet/orquestador | Lee N PERFILES + trade/noticia -> devuelve tabla comparativa de posturas + discrepancias + cita | spec listo, falta SPEC.md |
| `smc-architect` (ya existe) | opus | Arbitro final de conflictos mentor vs sistema Pine | EXISTE, agregar nota "consulta mentores antes de ADRs" |

## Skills del modulo (Workspace)

| Skill | Path | Estado |
|---|---|---|
| `consult-mentor` | `~/.hermes/skills/consult-mentor/SKILL.md` | CREADA |
| `mentor-transcribe` (spec) | orquestacion de process-video.ps1 desde chat | por crear |
| `mentor-extract-profile` (spec) | transcripcion -> PERFIL.md usando vision+audio MCP y LLM critical_analysis | por crear |

## Workflows pendientes (Conductor de Hermes, no Archon del proyecto)

| Workflow | Disparador | Pasos | Estado |
|---|---|---|---|
| `add-mentor` | manual (vos lo disparas) | URL -> process-video.ps1 -> extract-profile -> guardar PERFIL | spec, no implementado |
| `update-mentor` | manual o por Operation programada | detecta .md nuevos en Teoria SMC para un mentor existente -> re-extrae -> mergea con backup | pendiente |
| `multi-mentor-bias` | Operation diaria (Operation Programada de Workspace) | lee chart EURUSD / trade / noticia -> consulta N mentores -> tabla consolidada | pendiente |
| `mentor-audit-discrepancy` | manual | toma un PERFIL y un concepto del sistema Pine -> smc-architect juzga conflicto | pendiente |

## Comparacion contra el WORKPLAN-MAESTRO-V2.md

Esto es un modulo PARALELO al bot SMC/ICT, no una fase nueva del workplan:
- No agrega trabajo al bot Pine.
- No agrega tareas a las fases 0-4.
- No requiere ADR nuevo.
- Si algun dia interfiere (ej: contradicciones con la Pine), smc-architect abre ADR.

## Decisiones tomadas en esta sesion

1. PERFIL.md vive en el vault Obsidian (`D:\obsidian\boveda MENTE\Mente\Estrategia2.0\Mentores\`)
   como fuente de verdad; espejo en `~/.hermes/memoria/<slug>/` para carga rapida del system prompt.
2. Skill `consult-mentor` en `~/.hermes/skills/` (Workspace) — NO en `.claude/skills/`
   porque `.claude/skills/` esta reservado al sistema SMC del workplan.
3. MCP `claude-video-vision` queda en Workspace, NO en el `.mcp.json` del proyecto
   Estrategia2.0 (regla del usuario: modificaciones sensibles las hace Claude).
4. Nombres en espanol para archivos `.md` y frontmatter human-readable.
   Nombres tecnicos (slug, mcp, skill) en ingles siguiendo convencion del proyecto.
