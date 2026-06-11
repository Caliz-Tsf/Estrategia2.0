<#
.SYNOPSIS
    SCR-04 -- Pipeline de transcripcion de video de teoria SMC al vault Obsidian.

.DESCRIPTION
    yt-dlp (descarga audio) -> FFmpeg (normaliza a WAV 16kHz mono) ->
    Whisper (transcribe) -> .md con frontmatter al vault Teoria-SMC.

    Acepta una URL (YouTube/etc, via yt-dlp) o un archivo local (-InputFile).
    Escritura: solo hacia el vault. No lee proyectos previos (ver CLAUDE.md).

    NOTA: archivo solo-ASCII a proposito. Windows PowerShell 5.1 lee .ps1 como
    ANSI; caracteres no-ASCII romperian el parseo. El .md de SALIDA si va en
    UTF-8 con acentos (es contenido, no codigo).

    Requisitos en PATH: yt-dlp, ffmpeg, whisper (openai-whisper).

    Codigos de salida: 0 OK | 1 error.

.PARAMETER Url
    URL del video (yt-dlp). Excluyente con -InputFile.

.PARAMETER InputFile
    Ruta a un archivo de audio/video local ya descargado. Excluyente con -Url.

.PARAMETER VaultRoot
    Raiz del vault del proyecto. Default: destino de Estrategia2.0.

.PARAMETER SubFolder
    Subcarpeta del vault donde cae el .md. Default: Teoria-SMC.

.PARAMETER Model
    Modelo Whisper: tiny|base|small|medium|large. Default: small.

.PARAMETER Language
    Idioma forzado (ej: es, en). Si se omite, Whisper autodetecta.

.PARAMETER MaxSeconds
    Si > 0, recorta a los primeros N segundos (yt-dlp --download-sections o
    ffmpeg -t). Util para pruebas rapidas. Default: 0 (completo).

.PARAMETER WorkDir
    Carpeta temporal para audio/wav/txt. Default: %TEMP%\smc-video.

.PARAMETER KeepIntermediate
    Conserva audio/wav/txt intermedios (por defecto se borran).

.EXAMPLE
    powershell -File scripts/process-video.ps1 -Url "https://youtu.be/XXXX" -Language es

.EXAMPLE
    # Prueba rapida: primeros 20s con el modelo tiny
    powershell -File scripts/process-video.ps1 -Url "https://youtu.be/XXXX" -Model tiny -MaxSeconds 20
#>
[CmdletBinding(DefaultParameterSetName = 'Url')]
param(
    [Parameter(ParameterSetName = 'Url', Mandatory = $true)]
    [string]$Url,

    [Parameter(ParameterSetName = 'File', Mandatory = $true)]
    [string]$InputFile,

    [string]$VaultRoot = 'D:\obsidian\boveda MENTE\Mente\Estrategia2.0',
    [string]$SubFolder = 'Teoria-SMC',
    [ValidateSet('tiny', 'base', 'small', 'medium', 'large')]
    [string]$Model = 'small',
    [string]$Language,
    [int]$MaxSeconds = 0,
    [string]$WorkDir,
    [switch]$KeepIntermediate
)

$ErrorActionPreference = 'Stop'

function Write-Step($m) { Write-Host "[..] $m" -ForegroundColor Cyan }
function Write-Ok($m)   { Write-Host "[OK] $m"  -ForegroundColor Green }
function Write-Bad($m)  { Write-Host "[X]  $m"  -ForegroundColor Red }

# --- 0. Verificar herramientas ---
$tools = @('yt-dlp', 'ffmpeg', 'whisper')
# yt-dlp solo es necesario si se usa -Url
if ($PSCmdlet.ParameterSetName -eq 'File') { $tools = @('ffmpeg', 'whisper') }
foreach ($t in $tools) {
    if (-not (Get-Command $t -ErrorAction SilentlyContinue)) {
        Write-Bad "Falta '$t' en PATH. Requisitos: yt-dlp, ffmpeg, whisper (openai-whisper)."
        exit 1
    }
}

if (-not $WorkDir) { $WorkDir = Join-Path $env:TEMP 'smc-video' }
if (-not (Test-Path -LiteralPath $WorkDir)) { New-Item -ItemType Directory -Path $WorkDir -Force | Out-Null }

# Sanitiza un texto a un slug ASCII apto para nombre de archivo.
function Get-Slug([string]$text) {
    if (-not $text) { return 'video' }
    $s = $text.ToLowerInvariant()
    # quitar acentos comunes
    $s = $s -replace '[aaaaaa]', 'a' -replace '[eeee]', 'e' -replace '[iiii]', 'i' `
            -replace '[ooooo]', 'o' -replace '[uuuu]', 'u' -replace 'n', 'n'
    $s = $s -replace '[^a-z0-9]+', '-' -replace '(^-+)|(-+$)', ''
    if ($s.Length -gt 80) { $s = $s.Substring(0, 80).TrimEnd('-') }
    if (-not $s) { $s = 'video' }
    return $s
}

# --- 1. Resolver metadatos y obtener audio ---
$title = $null; $sourceUrl = $null; $durationSec = $null; $sourceKind = $null
$audioPath = $null

if ($PSCmdlet.ParameterSetName -eq 'Url') {
    $sourceKind = 'youtube'
    $sourceUrl = $Url
    Write-Step "Leyendo metadatos con yt-dlp..."
    # id|title|duration  (separador | improbable en estos campos)
    $meta = & yt-dlp --no-warnings --skip-download --print "%(id)s|%(title)s|%(duration)s" $Url 2>&1
    if ($LASTEXITCODE -ne 0 -or -not $meta) {
        Write-Bad "yt-dlp no pudo leer el video: $meta"
        exit 1
    }
    $parts = ($meta | Select-Object -Last 1) -split '\|', 3
    $vid = $parts[0]
    $title = if ($parts.Count -ge 2 -and $parts[1]) { $parts[1] } else { $vid }
    $durationSec = if ($parts.Count -ge 3) { $parts[2] } else { '' }
    Write-Ok "Video: $title ($vid) | dur=$durationSec s"

    $slug = Get-Slug $title
    $audioPath = Join-Path $WorkDir "$slug.mp3"

    $ytArgs = @('-x', '--audio-format', 'mp3', '--audio-quality', '0',
                '--no-warnings', '-o', $audioPath, $Url)
    if ($MaxSeconds -gt 0) {
        $ytArgs = @('--download-sections', "*0-$MaxSeconds") + $ytArgs
        Write-Step "Descargando audio (primeros $MaxSeconds s)..."
    } else {
        Write-Step "Descargando audio completo..."
    }
    & yt-dlp @ytArgs
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $audioPath)) {
        Write-Bad "Fallo la descarga de audio con yt-dlp."
        exit 1
    }
    Write-Ok "Audio: $audioPath"
}
else {
    $sourceKind = 'local'
    if (-not (Test-Path -LiteralPath $InputFile)) {
        Write-Bad "No existe el archivo de entrada: $InputFile"
        exit 1
    }
    $sourceUrl = (Resolve-Path -LiteralPath $InputFile).Path
    $title = [System.IO.Path]::GetFileNameWithoutExtension($InputFile)
    $slug = Get-Slug $title
    $audioPath = $sourceUrl
    Write-Ok "Entrada local: $audioPath"
}

# --- 2. FFmpeg: normalizar a WAV 16kHz mono ---
$wavPath = Join-Path $WorkDir "$slug.wav"
Write-Step "Normalizando audio con ffmpeg (16kHz mono WAV)..."
$ffArgs = @('-y', '-i', $audioPath, '-ar', '16000', '-ac', '1', '-c:a', 'pcm_s16le')
if ($MaxSeconds -gt 0 -and $sourceKind -eq 'local') { $ffArgs += @('-t', "$MaxSeconds") }
$ffArgs += $wavPath
& ffmpeg @ffArgs -loglevel error
if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $wavPath)) {
    Write-Bad "ffmpeg no pudo normalizar el audio."
    exit 1
}
Write-Ok "WAV: $wavPath"

# --- 3. Whisper: transcribir ---
Write-Step "Transcribiendo con Whisper (modelo=$Model)... (puede tardar)"
$wArgs = @($wavPath, '--model', $Model, '--output_format', 'txt',
           '--output_dir', $WorkDir, '--fp16', 'False', '--verbose', 'False')
if ($Language) { $wArgs += @('--language', $Language) }
& whisper @wArgs
$txtPath = Join-Path $WorkDir "$slug.txt"
if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $txtPath)) {
    Write-Bad "Whisper no genero la transcripcion ($txtPath)."
    exit 1
}
$transcriptRaw = Get-Content -LiteralPath $txtPath -Raw -Encoding UTF8
$transcript = if ($transcriptRaw) { $transcriptRaw.Trim() } else { '' }
if (-not $transcript) {
    Write-Host "[!] Transcripcion vacia (audio sin habla detectable). Se crea la nota igualmente." -ForegroundColor Yellow
    $transcript = '_(transcripcion vacia: el audio no contenia habla detectable)_'
}
Write-Ok "Transcripcion: $($transcript.Length) caracteres"

# --- 4. Construir .md y escribir al vault ---
$destDir = Join-Path $VaultRoot $SubFolder
$vaultParent = Split-Path -Parent $VaultRoot
if (-not (Test-Path -LiteralPath $vaultParent)) {
    Write-Bad "El vault padre no existe: $vaultParent"
    exit 1
}
if (-not (Test-Path -LiteralPath $destDir)) { New-Item -ItemType Directory -Path $destDir -Force | Out-Null }

$mdPath = Join-Path $destDir "$slug.md"
$nowIso = (Get-Date).ToString('yyyy-MM-dd')
$langLabel = if ($Language) { $Language } else { 'auto' }
$titleEsc = $title -replace '"', "'"

$md = @"
---
title: "$titleEsc"
source: $sourceUrl
fuente_tipo: $sourceKind
modelo_whisper: $Model
idioma: $langLabel
duracion_seg: $durationSec
procesado: $nowIso
tags: [teoria-smc, transcripcion]
---

# $title

> Fuente: $sourceUrl
> Transcrito con Whisper ($Model) el $nowIso.

$transcript
"@

$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($mdPath, $md, $utf8NoBom)
Write-Ok "Nota creada: $mdPath"

# --- 5. Limpieza ---
if (-not $KeepIntermediate) {
    foreach ($f in @($wavPath, $txtPath)) {
        if (Test-Path -LiteralPath $f) { Remove-Item -LiteralPath $f -Force -ErrorAction SilentlyContinue }
    }
    # el mp3 descargado solo se borra si lo creamos nosotros (modo Url)
    if ($sourceKind -eq 'youtube' -and (Test-Path -LiteralPath $audioPath)) {
        Remove-Item -LiteralPath $audioPath -Force -ErrorAction SilentlyContinue
    }
}

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "  process-video OK" -ForegroundColor Green
Write-Host "  Titulo : $title" -ForegroundColor Green
Write-Host "  Nota   : $mdPath" -ForegroundColor Green
Write-Host "  Modelo : $Model | Idioma: $langLabel" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
exit 0
