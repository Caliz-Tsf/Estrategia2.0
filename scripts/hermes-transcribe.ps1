<#
.SYNOPSIS
    Wrapper que invoca Hermes para transcribir un video SMC y guardarlo en Obsidian.

.DESCRIPTION
    Construye el prompt de contexto (hermes-prompt-transcripcion.txt) con la URL
    o archivo indicado, luego lanza Hermes con ese prompt y el toolset bash.

    Hermes sigue los 5 pasos del workflow:
      0. Verificar herramientas (yt-dlp, ffmpeg, whisper)
      1. Leer metadatos (sin descargar)
      2. Ejecutar process-video.ps1
      3. Verificar nota en Obsidian
      4. Actualizar Index.md
      5. Reporte final

    Para batch: un .txt con una URL por linea (# = comentario).

.PARAMETER Url
    URL de YouTube (o cualquier sitio compatible con yt-dlp).

.PARAMETER InputFile
    Ruta a archivo de audio/video local ya descargado.

.PARAMETER Batch
    Ruta a un .txt con multiples URLs, una por linea.

.PARAMETER Model
    Fuerza un modelo Whisper: tiny|base|small|medium|large.
    Si se omite, Hermes elige segun la duracion del video.

.PARAMETER MaxSeconds
    Si > 0, recorta el video a los primeros N segundos (util para tests).

.PARAMETER HermesModel
    Modelo de Hermes a usar. Default: usa el modelo default configurado en config.yaml.

.EXAMPLE
    powershell -File scripts/hermes-transcribe.ps1 -Url "https://youtu.be/XXXX"

.EXAMPLE
    powershell -File scripts/hermes-transcribe.ps1 -Url "https://youtu.be/XXXX" -Model medium

.EXAMPLE
    powershell -File scripts/hermes-transcribe.ps1 -Batch "D:\Videos\playlist-smc.txt"

.EXAMPLE
    powershell -File scripts/hermes-transcribe.ps1 -InputFile "D:\Videos\curso-ict.mp4"
#>
[CmdletBinding(DefaultParameterSetName = 'Url')]
param(
    [Parameter(ParameterSetName = 'Url', Mandatory = $true)]
    [string]$Url,

    [Parameter(ParameterSetName = 'File', Mandatory = $true)]
    [string]$InputFile,

    [Parameter(ParameterSetName = 'Batch', Mandatory = $true)]
    [string]$Batch,

    [ValidateSet('tiny', 'base', 'small', 'medium', 'large')]
    [string]$Model,

    [int]$MaxSeconds = 0,

    [string]$HermesModel = 'nvidia/llama-3.3-nemotron-super-49b-v1'
)

$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$PromptFile  = Join-Path $PSScriptRoot 'hermes-prompt-transcripcion.txt'

function Write-Step($m) { Write-Host "[..] $m" -ForegroundColor Cyan }
function Write-Ok($m)   { Write-Host "[OK] $m"  -ForegroundColor Green }
function Write-Bad($m)  { Write-Host "[X]  $m"  -ForegroundColor Red }

# --- Verificar Hermes disponible ---
if (-not (Get-Command 'hermes' -ErrorAction SilentlyContinue)) {
    Write-Bad "Hermes no encontrado en PATH. Instala con: pip install hermes-agent==0.15.1"
    exit 1
}

# --- Verificar que el prompt base existe ---
if (-not (Test-Path -LiteralPath $PromptFile)) {
    Write-Bad "Prompt base no encontrado: $PromptFile"
    exit 1
}

$basePrompt = Get-Content -LiteralPath $PromptFile -Raw -Encoding UTF8

# --- Construir la instruccion especifica segun modo ---
$taskSection = ''

switch ($PSCmdlet.ParameterSetName) {

    'Url' {
        $modelHint = if ($Model) { "El usuario eligio el modelo: $Model. Usa ese modelo en el Paso 2 (ignorar seleccion automatica por duracion)." } else { '' }
        $maxHint   = if ($MaxSeconds -gt 0) { "Agrega el parametro -MaxSeconds $MaxSeconds al comando del Paso 2." } else { '' }
        $taskSection = @"

=== TAREA ACTUAL ===

Transcribir el siguiente video:
URL: $Url
$modelHint
$maxHint

Empieza con el Paso 0 (verificar herramientas) y sigue los 5 pasos en orden.
"@
    }

    'File' {
        if (-not (Test-Path -LiteralPath $InputFile)) {
            Write-Bad "Archivo no encontrado: $InputFile"
            exit 1
        }
        $modelVal = if ($Model) { $Model } else { 'small' }
        $taskSection = @"

=== TAREA ACTUAL ===

Transcribir el siguiente archivo local (ya descargado, no necesitas yt-dlp):
Archivo: $InputFile
Modelo: $modelVal

En el Paso 2, usa el parametro -InputFile en vez de -Url:
  powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\process-video.ps1" -InputFile "$InputFile" -Model $modelVal -Language es

Empieza con el Paso 0 (verificar ffmpeg y whisper solamente) y sigue los pasos 1-5.
El Paso 1 (metadatos yt-dlp) se omite para archivos locales; usa el nombre del archivo como titulo.
"@
    }

    'Batch' {
        if (-not (Test-Path -LiteralPath $Batch)) {
            Write-Bad "Archivo de batch no encontrado: $Batch"
            exit 1
        }
        $urls = Get-Content -LiteralPath $Batch -Encoding UTF8 |
                Where-Object { $_ -and $_ -notmatch '^\s*#' } |
                ForEach-Object { $_.Trim() }
        if ($urls.Count -eq 0) {
            Write-Bad "El archivo de batch esta vacio o solo tiene comentarios."
            exit 1
        }
        $urlList = ($urls | ForEach-Object { "  - $_" }) -join "`n"
        $modelHint = if ($Model) { "Usa el modelo $Model para todos los videos (ignora la seleccion automatica)." } else { '' }
        $taskSection = @"

=== TAREA ACTUAL: BATCH ===

Procesar la siguiente lista de $($urls.Count) video(s) en orden:
$urlList

$modelHint

Para cada URL: ejecuta los 5 pasos completos antes de pasar a la siguiente.
Si una URL falla: loguea el error y continua con la siguiente. No abortes el batch.
Al final: muestra resumen (exitosas / fallidas / lista de fallidas).
"@
    }
}

# --- Ensamblar y aplanar prompt (fix: CommandLineToArgvW fragmenta multilinea) ---
$fullPrompt = $basePrompt + " " + ($taskSection -replace "`r`n"," " -replace "`n"," " -replace "\s{2,}"," ")
$flatPrompt  = $fullPrompt -replace "`r`n"," " -replace "`n"," " -replace "\s{2,}"," "

Write-Step "Invocando Hermes para transcripcion..."
Write-Host "  Modo    : $($PSCmdlet.ParameterSetName)" -ForegroundColor DarkGray
if ($Url)       { Write-Host "  URL     : $Url" -ForegroundColor DarkGray }
if ($InputFile) { Write-Host "  Archivo : $InputFile" -ForegroundColor DarkGray }
if ($Batch)     { Write-Host "  Batch   : $Batch ($($urls.Count) URLs)" -ForegroundColor DarkGray }
if ($Model)     { Write-Host "  Modelo  : $Model (forzado)" -ForegroundColor DarkGray }
Write-Host "  Modelo  : $HermesModel (hermes)" -ForegroundColor DarkGray
Write-Host ""

# Invocar hermes chat con prompt aplanado + --yolo (evita timeout por aprobacion de hooks)
& hermes chat -q $flatPrompt -t terminal,file --yolo -Q -m $HermesModel --provider nvidia_nim
$exit = $LASTEXITCODE

if ($exit -eq 0) {
    Write-Host ""
    Write-Ok "Hermes termino correctamente (exit 0)."
} else {
    Write-Host ""
    Write-Bad "Hermes termino con exit $exit. Revisa el output anterior."
}
exit $exit
