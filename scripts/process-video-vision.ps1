<#
.SYNOPSIS
    SCR-05 -- Pipeline de descripcion visual de video (canales mudos como
    Boxxocode) al vault Obsidian, via NVIDIA NIM cloud (gratis, sin tokens
    de Claude). Analogo a process-video.ps1 pero para video/frames en vez
    de audio/whisper.

.DESCRIPTION
    yt-dlp (descarga video completo) -> FFmpeg (detecta cambios de escena,
    extrae frames clave; si detecta muy pocos, cae a intervalo fijo) ->
    NVIDIA NIM (meta/llama-3.2-90b-vision-instruct, describe cada frame) ->
    .md con frontmatter al vault.

    Requiere NVIDIA_API_KEY en el entorno o en ~/.hermes/.env.

    NOTA: archivo solo-ASCII a proposito (PowerShell 5.1 + ANSI). El .md de
    salida si va en UTF-8 con acentos.

    Requisitos en PATH: yt-dlp, ffmpeg, python.

    Codigos de salida: 0 OK | 1 error.

.PARAMETER Url
    URL del video (yt-dlp).

.PARAMETER VaultRoot
    Raiz del vault del proyecto. Default: destino de Estrategia2.0.

.PARAMETER SubFolder
    Subcarpeta del vault donde cae el .md. Default: Teoria SMC.

.PARAMETER SceneThreshold
    Umbral de deteccion de cambio de escena de ffmpeg (0-1). Default 0.12.

.PARAMETER FallbackIntervalSec
    Si la deteccion de escena produce menos de MinScenes frames, se cae a
    extraer 1 frame cada N segundos. Default 15.

.PARAMETER MinScenes
    Minimo de frames por deteccion de escena antes de usar el fallback de
    intervalo fijo. Default 3.

.PARAMETER MaxFrames
    Tope de frames a describir (controla costo/tiempo). Default 20.

.PARAMETER MaxSeconds
    Si > 0, recorta la descarga a los primeros N segundos. Util para pruebas.

.PARAMETER WorkDir
    Carpeta temporal. Default: %TEMP%\smc-video-vision.

.PARAMETER KeepIntermediate
    Conserva video/frames intermedios (por defecto se borran).

.EXAMPLE
    powershell -File scripts/process-video-vision.ps1 -Url "https://www.youtube.com/shorts/XXXX"

.EXAMPLE
    # Prueba rapida: solo los primeros 30s
    powershell -File scripts/process-video-vision.ps1 -Url "https://youtu.be/XXXX" -MaxSeconds 30
#>
param(
    [Parameter(Mandatory = $true)]
    [string]$Url,

    [string]$VaultRoot = 'D:\obsidian\boveda MENTE\Mente',
    [string]$SubFolder = 'Teoria SMC',
    [double]$SceneThreshold = 0.12,
    [int]$FallbackIntervalSec = 15,
    [int]$MinScenes = 3,
    [int]$MaxFrames = 20,
    [int]$MaxSeconds = 0,
    [string]$WorkDir,
    [switch]$KeepIntermediate
)

$ErrorActionPreference = 'Stop'

function Write-Step($m) { Write-Host "[..] $m" -ForegroundColor Cyan }
function Write-Ok($m)   { Write-Host "[OK] $m"  -ForegroundColor Green }
function Write-Bad($m)  { Write-Host "[X]  $m"  -ForegroundColor Red }

# --- 0. Verificar herramientas ---
foreach ($t in @('yt-dlp', 'ffmpeg', 'ffprobe', 'python')) {
    if (-not (Get-Command $t -ErrorAction SilentlyContinue)) {
        Write-Bad "Falta '$t' en PATH."
        exit 1
    }
}
$describeScript = Join-Path $PSScriptRoot 'nvidia_vision_describe.py'
if (-not (Test-Path -LiteralPath $describeScript)) {
    Write-Bad "No existe scripts/nvidia_vision_describe.py."
    exit 1
}

# --- 0b. Resolver NVIDIA_API_KEY ---
$apiKey = $env:NVIDIA_API_KEY
if (-not $apiKey) {
    $envFile = Join-Path $env:USERPROFILE '.hermes\.env'
    if (Test-Path -LiteralPath $envFile) {
        $line = Get-Content -LiteralPath $envFile | Where-Object { $_ -match '^NVIDIA_API_KEY=' } | Select-Object -First 1
        if ($line) { $apiKey = $line -replace '^NVIDIA_API_KEY=', '' }
    }
}
if (-not $apiKey) {
    Write-Bad "No se encontro NVIDIA_API_KEY (ni en entorno ni en ~/.hermes/.env)."
    exit 1
}

if (-not $WorkDir) { $WorkDir = Join-Path $env:TEMP 'smc-video-vision' }
if (-not (Test-Path -LiteralPath $WorkDir)) { New-Item -ItemType Directory -Path $WorkDir -Force | Out-Null }
$framesDir = Join-Path $WorkDir 'frames'
if (Test-Path -LiteralPath $framesDir) { Remove-Item -LiteralPath $framesDir -Recurse -Force }
New-Item -ItemType Directory -Path $framesDir -Force | Out-Null

function Get-Slug([string]$text) {
    if (-not $text) { return 'video' }
    $s = $text.ToLowerInvariant()
    $s = $s -replace '[aaaaaa]', 'a' -replace '[eeee]', 'e' -replace '[iiii]', 'i' `
            -replace '[ooooo]', 'o' -replace '[uuuu]', 'u' -replace 'n', 'n'
    $s = $s -replace '[^a-z0-9]+', '-' -replace '(^-+)|(-+$)', ''
    if ($s.Length -gt 80) { $s = $s.Substring(0, 80).TrimEnd('-') }
    if (-not $s) { $s = 'video' }
    return $s
}

# --- 1. Metadatos ---
Write-Step "Leyendo metadatos con yt-dlp..."
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

# --- 2. Descargar video completo (no solo audio) ---
$videoPath = Join-Path $WorkDir "$slug.mp4"
# 137=1080p primero: frames mas nitidos para que NVIDIA NIM lea texto en pantalla
# (parametros, codigo, valores). Cae a 720p/480p/360p y por ultimo al 18 progresivo.
$ytArgs = @('-f', '137/136/135/134/18/best',
            '--no-warnings', '-o', $videoPath, $Url)
if ($MaxSeconds -gt 0) {
    $ytArgs = @('--download-sections', "*0-$MaxSeconds") + $ytArgs
    Write-Step "Descargando video (primeros $MaxSeconds s)..."
} else {
    Write-Step "Descargando video completo..."
}
& yt-dlp @ytArgs
if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $videoPath)) {
    Write-Bad "Fallo la descarga de video con yt-dlp."
    exit 1
}
Write-Ok "Video: $videoPath"

# --- 3. Extraer frames por cambio de escena ---
# NOTA: se usa Start-Process (redirige stderr a nivel de SO) en vez de
# "ffmpeg ... 2> archivo" -- con $ErrorActionPreference='Stop', PowerShell 5.1
# convierte cada linea de stderr de ffmpeg (banner de version, logs normales)
# en un NativeCommandError fatal aunque ffmpeg no haya fallado.
Write-Step "Detectando cambios de escena (umbral=$SceneThreshold)..."
$sceneLog = Join-Path $WorkDir 'scene.log'
$framePattern = Join-Path $framesDir 'frame_%03d.jpg'
$ffArgsScene = @('-i', $videoPath, '-vf', "select='gt(scene,$SceneThreshold)',showinfo", '-vsync', 'vfr', $framePattern, '-y')
$proc = Start-Process -FilePath 'ffmpeg' -ArgumentList $ffArgsScene -NoNewWindow -Wait -RedirectStandardError $sceneLog -PassThru
if ($proc.ExitCode -ne 0) {
    Write-Bad "ffmpeg fallo en la deteccion de escena (exit $($proc.ExitCode)). Ver $sceneLog"
    exit 1
}
$frameFiles = Get-ChildItem -LiteralPath $framesDir -Filter 'frame_*.jpg' | Sort-Object Name

$timestamps = @()
if ($frameFiles.Count -ge $MinScenes) {
    Write-Ok "Deteccion de escena: $($frameFiles.Count) frames."
    $logContent = Get-Content -LiteralPath $sceneLog -Raw
    $matches = [regex]::Matches($logContent, 'pts_time:(?<t>[\d\.]+)')
    foreach ($m in $matches) { $timestamps += [double]$m.Groups['t'].Value }
}
else {
    Write-Step "Deteccion de escena insuficiente ($($frameFiles.Count) frames) -> fallback cada $FallbackIntervalSec s."
    Get-ChildItem -LiteralPath $framesDir -Filter 'frame_*.jpg' | Remove-Item -Force
    $totalDur = [double]$durationSec
    if (-not $totalDur -or $totalDur -le 0) { $totalDur = 60 }
    if ($MaxSeconds -gt 0 -and $MaxSeconds -lt $totalDur) { $totalDur = $MaxSeconds }
    $t = 2.0
    $idx = 1
    while ($t -lt $totalDur -and $idx -le $MaxFrames) {
        $outFrame = Join-Path $framesDir ("frame_{0:D3}.jpg" -f $idx)
        & ffmpeg -ss $t -i $videoPath -frames:v 1 $outFrame -y -loglevel error
        if (Test-Path -LiteralPath $outFrame) {
            $timestamps += $t
            $idx++
        }
        $t += $FallbackIntervalSec
    }
    $frameFiles = Get-ChildItem -LiteralPath $framesDir -Filter 'frame_*.jpg' | Sort-Object Name
    Write-Ok "Fallback: $($frameFiles.Count) frames."
}

if ($frameFiles.Count -eq 0) {
    Write-Bad "No se pudo extraer ningun frame."
    exit 1
}

# Tope de frames (si la deteccion de escena dio demasiados, hacer subsampling uniforme)
if ($frameFiles.Count -gt $MaxFrames) {
    Write-Step "Recortando de $($frameFiles.Count) a $MaxFrames frames (muestreo uniforme)..."
    $step = [Math]::Ceiling($frameFiles.Count / $MaxFrames)
    $keepFiles = @(); $keepTimestamps = @()
    for ($i = 0; $i -lt $frameFiles.Count; $i += $step) {
        $keepFiles += $frameFiles[$i]
        if ($i -lt $timestamps.Count) { $keepTimestamps += $timestamps[$i] } else { $keepTimestamps += $null }
    }
    # renombrar a secuencia limpia para que el script de python las recorra en orden
    $tmpDir = Join-Path $WorkDir 'frames_kept'
    if (Test-Path -LiteralPath $tmpDir) { Remove-Item -LiteralPath $tmpDir -Recurse -Force }
    New-Item -ItemType Directory -Path $tmpDir -Force | Out-Null
    $newIdx = 1
    foreach ($f in $keepFiles) {
        Copy-Item -LiteralPath $f.FullName -Destination (Join-Path $tmpDir ("frame_{0:D3}.jpg" -f $newIdx))
        $newIdx++
    }
    Remove-Item -LiteralPath $framesDir -Recurse -Force
    Rename-Item -LiteralPath $tmpDir -NewName 'frames'
    $framesDir = Join-Path $WorkDir 'frames'
    $frameFiles = Get-ChildItem -LiteralPath $framesDir -Filter 'frame_*.jpg' | Sort-Object Name
    $timestamps = $keepTimestamps
}

# Escribir timestamps legibles (mm:ss) para que el script de python los use
$tsLines = $timestamps | ForEach-Object {
    if ($_ -ne $null) {
        $ts = [TimeSpan]::FromSeconds([double]$_)
        '{0:mm}:{0:ss}' -f $ts
    } else { '' }
}
$utf8NoBomTs = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText((Join-Path $framesDir 'frames_timestamps.txt'), ($tsLines -join "`n"), $utf8NoBomTs)

# --- 4. Describir frames via NVIDIA NIM ---
Write-Step "Describiendo $($frameFiles.Count) frames via NVIDIA NIM (puede tardar)..."
$resultsJson = Join-Path $WorkDir 'descriptions.json'
& python $describeScript $framesDir $apiKey $resultsJson
if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $resultsJson)) {
    Write-Bad "Fallo la descripcion de frames via NVIDIA NIM."
    exit 1
}
$descriptions = Get-Content -LiteralPath $resultsJson -Raw -Encoding UTF8 | ConvertFrom-Json
Write-Ok "Frames descritos: $($descriptions.Count)"

# --- 5. Construir .md y escribir al vault ---
$destDir = Join-Path $VaultRoot $SubFolder
$vaultParent = Split-Path -Parent $VaultRoot
if (-not (Test-Path -LiteralPath $vaultParent)) {
    Write-Bad "El vault padre no existe: $vaultParent"
    exit 1
}
if (-not (Test-Path -LiteralPath $destDir)) { New-Item -ItemType Directory -Path $destDir -Force | Out-Null }

$mdPath = Join-Path $destDir "$slug-vision.md"
$nowIso = (Get-Date).ToString('yyyy-MM-dd')
$titleEsc = $title -replace '"', "'"

$sections = foreach ($d in $descriptions) {
    $label = if ($d.timestamp) { "## Frame $($d.timestamp)" } else { "## Frame $($d.frame)" }
    "$label`n`n$($d.description)`n"
}
$body = ($sections -join "`n")

$md = @"
---
title: "$titleEsc"
source: $Url
fuente_tipo: youtube-vision
modelo_vision: meta/llama-3.2-90b-vision-instruct
duracion_seg: $durationSec
frames_descritos: $($descriptions.Count)
procesado: $nowIso
tags: [teoria-smc, vision, boxxocode]
---

# $title (descripcion visual)

> Fuente: $Url
> Frames descritos con NVIDIA NIM ($($descriptions.Count) frames) el $nowIso.
> Pipeline visual (sin audio) -- canal mudo.

$body
"@

$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($mdPath, $md, $utf8NoBom)
Write-Ok "Nota creada: $mdPath"

# --- 6. Limpieza ---
if (-not $KeepIntermediate) {
    Remove-Item -LiteralPath $videoPath -Force -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath $framesDir -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath $resultsJson -Force -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath $sceneLog -Force -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "  process-video-vision OK" -ForegroundColor Green
Write-Host "  Titulo : $title" -ForegroundColor Green
Write-Host "  Nota   : $mdPath" -ForegroundColor Green
Write-Host "  Frames : $($descriptions.Count)" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
exit 0
