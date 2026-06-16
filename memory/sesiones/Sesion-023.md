# Sesión 023 — 2026-06-15

> Sesión de **Hermes / módulo mentores** (NO sprint Pine). El core Pine no se tocó; check-core-sync intacto.

## Objetivo
Revisar los scripts de transcripción de Hermes, activar GPU de verdad, y rediseñar el workflow del módulo
mentores a partir del PDF `modulo-mentores-plan-completo.md.pdf` que el usuario preparó con Sonnet.

## Hecho

### 1. GPU CUDA — RESUELTA
- **Diagnóstico:** faster-whisper caía a CPU **en silencio**. `fw_transcribe.py` ya defaulteaba a
  `cuda/float16`, pero CTranslate2 4.8.0 (compilado contra CUDA 12) busca `cublas64_12.dll` / `cudnn64_9.dll`
  y en la máquina solo había **CUDA Toolkit 13.3** (que trae `_13`, no `_12`). NIM/torch no aportan esas DLLs.
- **Fix:** `pip install nvidia-cublas-cu12 nvidia-cudnn-cu12` (wheels cu12, conviven con el toolkit 13) +
  parche `_register_cuda_dll_dirs()` en `fw_transcribe.py` que registra las carpetas `nvidia/*/bin` vía
  `os.add_dll_directory()` antes de importar `faster_whisper`.
- **Verificado:** transcribe en `cuda (float16)` sin fallback. Benchmark ~3.5x vs CPU (RTX 3070 8GB).
- Corregidos los mensajes hardcodeados "CPU int8" en `process-video.ps1` (líneas 176, 247).
- Archivos: `scripts/fw_transcribe.py`, `scripts/process-video.ps1`.

### 2. Módulo mentores — workflow REDISEÑADO (construcción diferida)
- Revisado el PDF. Verificado el estado real contra `~/.hermes/config.yaml` + `hermes chat/--help`.
- **Correcciones a los supuestos de Sonnet:** (a) no existe `hermes chat --personality`; (b) `personalities:`
  está vacío `{}` y ningún comando lo lee; (c) NIM y OpenRouter suspendidos (api_key vacía) → primario
  **Puter/claude-sonnet-4-6**; (d) `hermes memory` no indexa por carpeta; (e) GPU es RTX 3070 (no 3060).
- **Decisiones (Opus):** personalidad = **skill por mentor** (`-s`, generada con `skill-creator`); Fase 2 =
  **map-reduce con Claude Sonnet/Puter** (descartado minimax: lento + sin tokens); Fase 1 =
  `process-channel.ps1` directo sin Hermes.
- Diagrama renderizado en el chat. Workflow completo + scripts a crear en el plan:
  `C:\Users\Fredd\.claude\plans\c-users-fredd-downloads-modulo-mentores-streamed-ullman.md`.
- **DIFERIDO a próxima sesión** (decisión del usuario): construir los 5 scripts; decidir **un modelo por
  mentor vs el mismo para todos**; diseñar el **grupo de agentes + restricciones** (supervisor/entrenador,
  expertos por concepto, etc.). Ver memoria `mentores-modulo-plan`.

### 3. Listado de modelos actualizado al nuevo (Puter primario)
- **Reescrita `~/.hermes/MODELO-GUIA.md`** (listado canónico): Puter primario (claude-sonnet-4-6 default,
  deepseek-v4-flash, gemini-2.5-pro, glm-5, deepseek-r1) + Ollama local; NIM/OR marcados SUSPENDIDOS con
  instrucciones de reactivación; modelo recomendado por tarea.
- Banner de obsolescencia parcial en `docs/MODULO-MENTORES-V1.md`.
- `scripts/hermes-transcribe.ps1`: default `-HermesModel` NIM→`claude-sonnet-4-6` y `--provider` nim→puter.
- `~/.hermes/skills/mentor-extract-profile/SKILL.md`: refs viejas (minimax/nemotron) → Puter.

## Commits
- (A) fix GPU CUDA: `scripts/fw_transcribe.py` + `scripts/process-video.ps1`.
- (B) docs/listado modelos: `docs/MODULO-MENTORES-V1.md`, `scripts/hermes-transcribe.ps1`,
  `memory/ESTADO-ACTUAL.md`, `memory/sesiones/Sesion-023.md`, `docs/HERMES-INVESTIGACION-S022.md` (pendiente
  de S022). (Los docs de `~/.hermes/` no son del repo, no se commitean.)

## Pine
Intacto. **Siguiente: F1-S1.2-T08 EQH/EQL.** Recordar de S022: re-lanzar TV al inicio y confirmar 0/0 +
re-guardar el slot tras el último cambio de estilo de etiqueta (la conexión CDP se cayó tras esa inyección).
