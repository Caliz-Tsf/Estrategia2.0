# Video Cursos SMC — Pipeline de Transcripción
> SCR-04 del WORKPLAN-MAESTRO-V2.md | Estrategia 2.0 | Rescatado de Estrategia-Nueva S29-S30

Sistema completo para descargar videos de YouTube de teoría SMC/ICT, transcribirlos con Whisper y guardar la nota estructurada en Obsidian (`Teoria SMC/`).

---

## Stack instalado globalmente

| Herramienta | Versión | Uso |
|-------------|---------|-----|
| **yt-dlp** | 2026.03.17 | Descarga video/audio de YouTube (y 1000+ sitios) |
| **FFmpeg** | 8.1 | Extrae y normaliza audio a WAV 16 kHz mono |
| **Whisper** (openai-whisper) | 20250625 | Transcripción local offline, multidioma |
| **claude-video-vision** MCP | 1.2.1 | MCP alternativo: extrae frames + audio y los envía a Claude para análisis visual |

Todos los binarios están en PATH. No se requiere conexión a ninguna API para el pipeline base (Whisper corre localmente).

---

## Flujo principal (pipeline base)

```
URL de YouTube
  → yt-dlp     (descarga solo el audio en MP3)
  → FFmpeg     (normaliza a WAV 16 kHz mono — formato óptimo para Whisper)
  → Whisper    (transcribe → .txt en $TEMP\smc-video\)
  → PowerShell (genera .md con frontmatter YAML)
  → Obsidian   D:\obsidian\boveda MENTE\Mente\Teoria SMC\<slug>.md
```

### Script

```
scripts/process-video.ps1
```

### Parámetros

| Parámetro | Default | Descripción |
|-----------|---------|-------------|
| `-Url` | (obligatorio con -Url) | URL de YouTube/cualquier sitio compatible con yt-dlp |
| `-InputFile` | — | Alternativa: ruta a un archivo de audio/video local ya descargado |
| `-VaultRoot` | `D:\obsidian\boveda MENTE\Mente` | Raíz del vault Obsidian |
| `-SubFolder` | `Teoria SMC` | Subcarpeta dentro del vault |
| `-Model` | `small` | Modelo Whisper: `tiny` (rápido) / `base` / `small` / `medium` / `large` (preciso) |
| `-Language` | auto | Forzar idioma: `es`, `en`, etc. Si se omite, Whisper autodetecta |
| `-MaxSeconds` | 0 (completo) | Recortar a los primeros N segundos — útil para tests rápidos |
| `-KeepIntermediate` | false | Conservar los archivos WAV/TXT temporales después de procesar |

---

## Ejemplos de uso

### Transcribir un video completo en español
```powershell
powershell -File scripts/process-video.ps1 `
  -Url "https://www.youtube.com/watch?v=XXXX" `
  -Language es
```

### Test rápido de 20 segundos con modelo mínimo
```powershell
powershell -File scripts/process-video.ps1 `
  -Url "https://www.youtube.com/shorts/XXXX" `
  -Model tiny -MaxSeconds 20
```

### Desde archivo local ya descargado
```powershell
powershell -File scripts/process-video.ps1 `
  -InputFile "C:\Videos\curso-smc.mp4" `
  -Model small -Language es
```

### Playlist en lote (loop manual)
```powershell
$urls = @(
  "https://youtu.be/VIDEO1",
  "https://youtu.be/VIDEO2"
)
foreach ($url in $urls) {
  powershell -File scripts/process-video.ps1 -Url $url -Language es -Model small
  Start-Sleep -Seconds 5
}
```

---

## Salida — formato .md generado

```markdown
---
title: "Nombre del video"
source: https://youtu.be/XXXX
fuente_tipo: youtube
modelo_whisper: small
idioma: es
duracion_seg: 1200
procesado: 2026-06-13
tags: [teoria-smc, transcripcion]
---

# Nombre del video

> Fuente: https://youtu.be/XXXX
> Transcrito con Whisper (small) el 2026-06-13.

[Transcripción completa del video aquí...]
```

---

## Destino en Obsidian

```
D:\obsidian\boveda MENTE\Mente\
└── Teoria SMC\
    ├── Index.md          ← índice manual de cursos
    ├── SMC-Short-Video.md ← primer test (del proyecto Estrategia-Nueva)
    └── <slug-del-video>.md ← cada transcripción nueva aquí
```

El slug se genera automáticamente desde el título del video (lowercase ASCII, guiones, máx 80 chars).

---

## MCP alternativo: claude-video-vision

Para análisis VISUAL del video (no solo transcripción de audio), el MCP `claude-video-vision` v1.2.1 está configurado en el settings.json global y disponible en toda sesión Claude Code.

**Configuración actual** (`~/.claude/settings.json`):
```json
"claude-video-vision": {
  "command": "npx",
  "args": ["-y", "claude-video-vision@latest"]
}
```

El MCP extrae frames via FFmpeg y procesa audio via múltiples backends (Whisper, etc.) para que Claude pueda **ver y entender** el video. Útil para:
- Analizar diagramas de chart en videos
- Extraer información visual de slides
- Análisis combinado audio+visual

**Nota:** El pipeline `process-video.ps1` (Whisper puro) es suficiente para el caso principal de cursos con narración. El MCP añade capacidad visual cuando el video tiene gráficos relevantes.

---

## Modelos Whisper — guía de elección

| Modelo | Velocidad | Precisión | Uso recomendado |
|--------|-----------|-----------|-----------------|
| `tiny` | Muy rápido | Básica | Tests de pipeline, snippets <30s |
| `base` | Rápido | Aceptable | Videos cortos en inglés |
| `small` | Moderado | Buena | **Default** — cursos en español |
| `medium` | Lento | Muy buena | Cuando small comete errores |
| `large` | Muy lento | Óptima | Calidad máxima, audio difícil |

Para cursos de trading en español: `-Model small -Language es` es el balance óptimo.

---

## Requisitos verificados (2026-06-13)

```
yt-dlp  : 2026.03.17       ✅
ffmpeg  : 8.1 (gyan.dev)   ✅  (C:\ffmpeg\ffmpeg.exe + WinGet)
whisper : 20250625          ✅  (openai-whisper, Python 3.14)
claude-video-vision : 1.2.1 ✅  (npm global + MCP configurado)
Obsidian vault : D:\obsidian\boveda MENTE\Mente\Teoria SMC\  ✅
```

---

## Historial

| Evento | Fecha | Detalle |
|--------|-------|---------|
| Sistema creado | 2026-05-02 | Estrategia-Nueva S29-S30: instalación + test con YouTube Short |
| Portado a Estrategia2.0 | 2026-06-07 | SCR-04 en WORKPLAN, script process-video.ps1 |
| Fix VaultRoot | 2026-06-13 | Corregido default: `Estrategia2.0/Teoria-SMC` → `Mente/Teoria SMC` |
