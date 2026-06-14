# Sesión 019 — Pipeline transcripción Hermes: faster-whisper + fixes CLI

> Fecha: 2026-06-14 · Hermes / SCR-04 · Claude Code (Sonnet 4.6) + Freddy
> Sesión dedicada al pipeline de transcripción de videos de mentores (fuera del sprint Pine).
> **ESTADO: pipeline funcional end-to-end. Video 29 min transcrito en 22.7 min.**

## Objetivo de la sesión
Continuar desde la sesión anterior (contexto comprimido): el pipeline de transcripción corría
openai-whisper en CPU y tardaba 40+ minutos para un video de 29 min. El usuario detuvo la
ejecución y aprobó instalar faster-whisper para acelerar.

## Qué se hizo y por qué

### 1. Cambio de modelo en Hermes config
`C:\Users\Fredd\.hermes\config.yaml`:
- `model.default` / `active_model`: `minimaxai/minimax-m3` → `nvidia/nemotron-3-ultra-550b-a55b:free`
- `model.provider` / `active_provider`: `nvidia_nim` → `openrouter`
- `terminal.timeout`: 180 → 3600 (para runs largos de Whisper)

**Diseño:** workspace usa el modelo más inteligente (nemotron-3-ultra-550b vía OpenRouter gratis);
CLI de transcripción usa llama-3.3-nemotron-super-49b-v1 vía NIM (rápido, 1.02s latencia).

### 2. Instalación de faster-whisper
```
pip install faster-whisper
```
Instala: `ctranslate2-4.8.0`, `faster-whisper-1.2.1`, `onnxruntime-1.26.0`.

**Por qué:** openai-whisper usa PyTorch `2.11.0+cpu` — no detecta la RTX 3070.
faster-whisper usa CTranslate2 con su propio backend CUDA.

**Resultado CUDA:** `cublas64_12.dll` no disponible (driver CUDA OK pero CUDA Toolkit 12 no
instalado). El fallback a CPU int8 funciona y es 4-8x más rápido que openai-whisper CPU.

### 3. Nuevo script fw_transcribe.py
`scripts/fw_transcribe.py` — wrapper Python para faster-whisper:
- Carga modelo en CPU int8 por default (CUDA disponible como opción `--device cuda`)
- Fallback automático a CPU si CUDA falla (cublas DLL runtime error durante transcripción)
- Fuerza `sys.stdout` a UTF-8 (evita UnicodeEncodeError cp1252 con caracteres españoles)
- Salida: `<output_dir>/<stem>.txt` con la transcripción completa

### 4. Actualización de process-video.ps1
`scripts/process-video.ps1`:
- Verifica `python` en PATH en vez de `whisper`
- Verifica existencia de `fw_transcribe.py`
- Llama `python fw_transcribe.py` en vez de `whisper` CLI
- Mensajes actualizados ("faster-whisper CPU int8")

### 5. Fixes en hermes-transcribe.ps1
- Eliminada línea bogus `& $pythonExe $callerScript` que había quedado de un borrador previo

### 6. Actualización del prompt base
`scripts/hermes-prompt-transcripcion.txt`:
- Paso 0 verifica `python` en vez de `whisper`
- Nota explícita: "NO usar `whisper` CLI"

## Resultado del test completo
```
Video : Mentoria Ep. 1 - ORDER BLOCKS (29 min, 1740s)
URL   : https://www.youtube.com/watch?v=_Wz4gpZsTiQ
Modelo: medium (faster-whisper CPU int8)
Chars : 21,787 caracteres
Tiempo: 22.7 minutos (vs 40+ con openai-whisper)
Nota  : D:\obsidian\boveda MENTE\Mente\Teoria SMC\mentoria-ep-1-order-blocks-...md
Exit  : 0
```

## Workflow de transcripción (estado actual)

Hermes recibe la URL y ejecuta 5 pasos:

**Paso 0** — `where.exe yt-dlp && where.exe ffmpeg && where.exe python`

**Paso 1** — `yt-dlp --skip-download --print "%(id)s|%(title)s|%(duration)s" <URL>`
Selección automática: `<180s→tiny`, `<1200s→small`, `≥1200s→medium`

**Paso 2** — Un solo comando, Hermes espera que termine:
```
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-video.ps1" -Url "<URL>" -Model <modelo> -Language es
```
Internamente: yt-dlp → ffmpeg (WAV 16kHz mono) → python fw_transcribe.py → .md en vault.

**Paso 3** — Verificar nota en Obsidian (Get-ChildItem + Get-Content primeras 25 líneas)

**Paso 4** — Actualizar Index.md (nueva fila en tabla)

**Paso 5** — Reporte `TRANSCRIPCION COMPLETADA`

**Invocación desde PowerShell:**
```powershell
powershell -File scripts/hermes-transcribe.ps1 -Url "https://youtu.be/XXXX"
```

**Invocación directa desde bash (skill mentor-transcribe):**
```bash
PROMPT=$(cat scripts/hermes-prompt-transcripcion.txt | tr '\n' ' ' | tr -s ' ')
FULL="$PROMPT === TAREA ACTUAL === Transcribir el siguiente video: URL: <URL>. Empieza con el Paso 0 y sigue los 5 pasos en orden."
hermes chat -q "$FULL" -t terminal,file --yolo -Q
```

## Flags obligatorios hermes chat
| Flag | Por qué |
|---|---|
| `--yolo` | Sin esto hermes espera aprobación de yt-dlp/ffmpeg/python → timeout |
| `-Q` | Suprime banner y spinner |
| `-t terminal,file` | Toolsets mínimos |
| `-q "<prompt_flat>"` | Prompt en una sola línea (Windows fragmente multilinea por espacios) |

## Commits de esta sesión
- `190738e` feat(hermes): faster-whisper CPU int8 reemplaza openai-whisper en pipeline
  - `scripts/fw_transcribe.py` (nuevo)
  - `scripts/process-video.ps1` (actualizado)
  - `scripts/hermes-transcribe.ps1` (fix linea bogus)
  - `scripts/hermes-prompt-transcripcion.txt` (actualizado)

## Limitaciones conocidas
- **GPU no activa:** `cublas64_12.dll` ausente. Para activar GPU: instalar CUDA Toolkit 12.
  Con GPU el tiempo bajaría a ~2-3 min para un video de 29 min.
- **Modelo large/large-v3:** no probado. Para mayor precisión en español podría valer la pena.

## Próximos pasos (Hermes/mentores)
- Transcribir más videos del mismo canal u otros mentores SMC.
- Cuando haya suficientes transcripciones, activar `mentor-extract-profile` para crear
  perfiles de cada mentor.

## Estado del sprint Pine (sin cambios esta sesión)
- **Rama:** `pine/sistema-completo`
- **Siguiente tarea Pine:** T07 Premium/Discount (Sprint 1.2)
- **Core sync:** OK (342 líneas, SHA `16f5e945af5f27c7`) — Pine intacto

## Links
- `scripts/fw_transcribe.py` — wrapper faster-whisper
- `scripts/process-video.ps1` — pipeline completo
- `scripts/hermes-prompt-transcripcion.txt` — prompt base para Hermes
- `C:\Users\Fredd\.hermes\skills\mentor-transcribe\SKILL.md` — skill con pitfalls documentados
- [[Sesion-018]] — sesión previa (corrección documental T06)
