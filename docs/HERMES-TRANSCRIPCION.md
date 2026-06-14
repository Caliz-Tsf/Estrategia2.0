# Hermes — Workflow de Transcripción SMC
> Instrucciones paso a paso para que Hermes ejecute el pipeline de video-cursos.
> Referencia: `docs/VIDEO-CURSOS.md` · Script: `scripts/process-video.ps1`

---

## Cómo invocar Hermes para transcribir

### Opción A — Script wrapper (recomendado)

```powershell
# Un video
powershell -File scripts/hermes-transcribe.ps1 -Url "https://youtu.be/VIDEO_ID"

# Con modelo más preciso
powershell -File scripts/hermes-transcribe.ps1 -Url "https://youtu.be/VIDEO_ID" -Model medium

# Modo batch: archivo .txt con una URL por línea
powershell -File scripts/hermes-transcribe.ps1 -Batch "C:\Videos\lista.txt"
```

### Opción B — Hermes directo con prompt

```powershell
hermes chat -q "$(Get-Content scripts/hermes-prompt-transcripcion.txt -Raw)" -t terminal,file
```

---

## Sistema prompt para Hermes (`scripts/hermes-prompt-transcripcion.txt`)

> Este es el prompt que se inyecta en Hermes. Hermes lo lee y sabe exactamente qué hacer.

Ver archivo: `scripts/hermes-prompt-transcripcion.txt`

---

## Paso a paso que sigue Hermes

El agente Hermes ejecuta los siguientes pasos en orden cuando recibe una URL de video:

### Paso 0 — Verificación de herramientas

Hermes ejecuta en shell:
```powershell
where.exe yt-dlp
where.exe ffmpeg
where.exe whisper
```
Si alguno falla → reporta qué falta y se detiene. No procede sin las tres herramientas.

---

### Paso 1 — Leer metadatos sin descargar

```powershell
yt-dlp --no-warnings --skip-download --print "%(id)s|%(title)s|%(duration)s" <URL>
```

Hermes extrae:
- **ID** del video
- **Título** (para nominar el slug del .md)
- **Duración en segundos** (para elegir modelo: >600s → `small`; <120s → `tiny`)

---

### Paso 2 — Ejecutar el pipeline completo

```powershell
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-video.ps1" `
  -Url "<URL>" `
  -Model <modelo_elegido> `
  -Language es
```

Hermes espera la salida y verifica que la última línea contenga `process-video OK`.

Si hay error (exit code ≠ 0) → captura el mensaje `[X]` y reporta el fallo exacto.

---

### Paso 3 — Verificar la nota en Obsidian

```powershell
$vault = "D:\obsidian\boveda MENTE\Mente\Teoria SMC"
Get-ChildItem $vault -Name | Sort-Object LastWriteTime -Descending | Select-Object -First 3
```

Hermes confirma que existe un archivo .md nuevo con timestamp de hace <5 minutos.

Luego lee los primeros 30 líneas para confirmar que hay frontmatter y transcripción:
```powershell
Get-Content "<ruta_nota>.md" -TotalCount 30 -Encoding UTF8
```

---

### Paso 4 — Actualizar Index.md

Hermes agrega la fila del nuevo video a la tabla de transcripciones en:
`D:\obsidian\boveda MENTE\Mente\Teoria SMC\Index.md`

Formato de la nueva fila:
```
| [<titulo corto>](<slug>.md) | YouTube | <YYYY-MM-DD> | <modelo> |
```

Hermes localiza la línea `| (vacío o ultima fila)` de la tabla y agrega ENCIMA del `---` final.

---

### Paso 5 — Reporte final

Hermes imprime un resumen:

```
===========================
  TRANSCRIPCION COMPLETADA
===========================
Titulo   : <titulo completo del video>
URL      : <url>
Nota     : D:\obsidian\boveda MENTE\Mente\Teoria SMC\<slug>.md
Modelo   : <small|medium|tiny>
Duracion : <N> segundos
Chars    : <N> caracteres transcritos
Index    : actualizado
===========================
```

---

## Modo batch (múltiples videos)

Para procesar una playlist o lista de URLs, Hermes repite los pasos 1-5 por cada URL en orden:

```
# lista.txt — una URL por línea, líneas con # son comentarios
https://youtu.be/VIDEO1
https://youtu.be/VIDEO2
# este está pendiente
https://youtu.be/VIDEO3
```

Hermes lee el archivo, filtra comentarios y vacíos, y procesa secuencialmente con pausa de 3s entre videos para no saturar la API de YouTube.

---

## Manejo de errores

| Error | Causa probable | Acción de Hermes |
|-------|----------------|-----------------|
| `yt-dlp: ERROR: Video unavailable` | Video privado/borrado | Reporta y salta al siguiente (batch) |
| `ffmpeg: Conversion failed` | Audio corrupto | Intenta con `-Model tiny` como fallback |
| `Transcripcion vacia` | Audio sin habla | Crea nota igualmente con aviso `_(transcripcion vacia)_` |
| `El vault padre no existe` | Obsidian desconectado | Detiene e indica que hay que verificar la ruta |
| Timeout yt-dlp >120s | Video muy largo / red lenta | Reporta; sugiere usar `-MaxSeconds 300` para seccionar |

---

## Selección automática de modelo según duración

Hermes elige el modelo Whisper basado en la duración del video (leída en Paso 1):

| Duración | Modelo elegido | Razón |
|----------|---------------|-------|
| < 3 min | `tiny` | Rápido, suficiente para clips cortos |
| 3–20 min | `small` | Balance velocidad/precisión (default) |
| 20–60 min | `small` | Idem — el video se procesa en partes por Whisper |
| > 60 min | `medium` | Mejor precisión en audios largos con terminología técnica |

El usuario puede sobreescribir con `-Model <modelo>` en el wrapper script.

---

## Referencia rápida de comandos Hermes

```powershell
# Un video rápido
powershell -File scripts/hermes-transcribe.ps1 -Url "https://youtu.be/XXX"

# Forzar modelo
powershell -File scripts/hermes-transcribe.ps1 -Url "https://youtu.be/XXX" -Model medium

# Solo los primeros 5 minutos (preview antes de descargar todo)
powershell -File scripts/hermes-transcribe.ps1 -Url "https://youtu.be/XXX" -MaxSeconds 300

# Batch desde archivo de texto
powershell -File scripts/hermes-transcribe.ps1 -Batch "D:\Videos\playlist-smc.txt"

# Desde archivo local ya descargado
powershell -File scripts/hermes-transcribe.ps1 -InputFile "D:\Videos\curso-ict.mp4"
```
