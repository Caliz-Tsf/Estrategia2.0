<#
.SYNOPSIS
    Fase 1 del modulo Mentores -- Ingesta de un canal/playlist de YouTube al vault.

.DESCRIPTION
    Determinista, SIN LLM. Resuelve la lista de videos de un canal o playlist con
    yt-dlp (--flat-playlist) e itera scripts/process-video.ps1 por cada video,
    guardando los .md en  <Vault>\Mentores\<Mentor>\ . La inteligencia esta en
    faster-whisper (GPU), no en un modelo de lenguaje, por eso no se envuelve Hermes.

    Cada process-video.ps1 se invoca como PROCESO HIJO (powershell -File) para que
    su `exit` no aborte este script. Si un video falla, se loguea y se continua.
    Al final genera/actualiza un Index.md local con los .md de la carpeta del mentor.

    NOTA: archivo solo-ASCII a proposito (Windows PowerShell 5.1 lee .ps1 como ANSI;
    caracteres no-ASCII romperian el parseo). El Index.md de SALIDA va UTF-8 sin BOM.

    Requisitos en PATH: yt-dlp (y, via process-video.ps1: ffmpeg, python+faster-whisper).

    Codigos de salida: 0 = todos OK | 1 = error de setup o >=1 video fallido.

.PARAMETER ChannelUrl
    URL del canal o playlist. Para un canal completo usa la pestana de videos, p.ej.
    https://www.youtube.com/@Boxxocode/videos  (asi yt-dlp lista todos los uploads).

.PARAMETER Mentor
    Nombre/slug del mentor. Define la subcarpeta destino: Mentores\<Mentor>.

.PARAMETER Language
    Idioma forzado para whisper (ej: es, en). Default: es.

.PARAMETER Model
    Modelo whisper: tiny|base|small|medium|large. Default: small.

.PARAMETER MaxVideos
    Si > 0, procesa solo los primeros N videos de la lista (--playlist-end). Default: 0 (todos).

.PARAMETER MaxSeconds
    Si > 0, recorta cada video a los primeros N segundos (pasa a process-video.ps1).
    Util para una prueba rapida de todo el canal. Default: 0 (completo).

.PARAMETER PlaylistItems
    Rango/seleccion de items de la playlist al estilo yt-dlp (ej: "6-10", "1,3,5",
    "11-15"). Permite bajar por LOTES (de a 5, etc.) sin reprocesar lo ya bajado.
    Si se setea, tiene prioridad sobre -MaxVideos. Default: '' (toda la lista).

.PARAMETER VaultRoot
    Raiz del vault. Default: D:\obsidian\boveda MENTE\Mente

.EXAMPLE
    powershell -File scripts/process-channel.ps1 -ChannelUrl "https://www.youtube.com/@Boxxocode/videos" -Mentor "boxxocode" -MaxVideos 3

.EXAMPLE
    # Prueba rapida del pipeline completo: 2 videos, 20s cada uno
    powershell -File scripts/process-channel.ps1 -ChannelUrl "<playlist>" -Mentor "Test" -MaxVideos 2 -MaxSeconds 20 -Model tiny
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ChannelUrl,

    [Parameter(Mandatory = $true)]
    [string]$Mentor,

    [string]$Language = 'es',
    [ValidateSet('tiny', 'base', 'small', 'medium', 'large')]
    [string]$Model = 'small',
    [int]$MaxVideos = 0,
    [int]$MaxSeconds = 0,
    [string]$PlaylistItems = '',
    [string]$VaultRoot = 'D:\obsidian\boveda MENTE\Mente'
)

$ErrorActionPreference = 'Stop'

function Write-Step($m) { Write-Host "[..] $m" -ForegroundColor Cyan }
function Write-Ok($m)   { Write-Host "[OK] $m"  -ForegroundColor Green }
function Write-Bad($m)  { Write-Host "[X]  $m"  -ForegroundColor Red }

# --- 0. Verificar herramientas y scripts ---
if (-not (Get-Command 'yt-dlp' -ErrorAction SilentlyContinue)) {
    Write-Bad "Falta 'yt-dlp' en PATH."
    exit 1
}
$procVideo = Join-Path $PSScriptRoot 'process-video.ps1'
if (-not (Test-Path -LiteralPath $procVideo)) {
    Write-Bad "No existe scripts/process-video.ps1 junto a este script."
    exit 1
}

# --- Normalizar nombre del mentor a un slug ASCII para la subcarpeta ---
function Get-Slug([string]$text) {
    if (-not $text) { return 'mentor' }
    $s = $text.ToLowerInvariant()
    $s = $s -replace '[^a-z0-9]+', '-' -replace '(^-+)|(-+$)', ''
    if (-not $s) { $s = 'mentor' }
    return $s
}
$mentorSlug = Get-Slug $Mentor
$subFolder  = "Mentores\$mentorSlug"
$destDir    = Join-Path $VaultRoot $subFolder

Write-Step "Canal  : $ChannelUrl"
Write-Step "Mentor : $Mentor (slug: $mentorSlug)"
Write-Step "Destino: $destDir"

# --- 1. Resolver la lista de IDs de video (sin descargar) ---
Write-Step "Resolviendo lista de videos con yt-dlp (--flat-playlist)..."
$ytArgs = @('--flat-playlist', '--no-warnings', '--print', '%(id)s')
if ($PlaylistItems) {
    # Lote explicito (ej. "6-10"): prioridad sobre -MaxVideos.
    $ytArgs = @('--playlist-items', $PlaylistItems) + $ytArgs
} elseif ($MaxVideos -gt 0) {
    $ytArgs = @('--playlist-end', "$MaxVideos") + $ytArgs
}
$ytArgs += $ChannelUrl

$ids = & yt-dlp @ytArgs 2>&1 | Where-Object { $_ -and ($_ -match '^[\w-]{6,}$') } | ForEach-Object { $_.Trim() }
if ($LASTEXITCODE -ne 0 -or -not $ids -or $ids.Count -eq 0) {
    Write-Bad "yt-dlp no devolvio IDs de video. Revisa la URL (para un canal usa .../@nombre/videos)."
    exit 1
}
$ids = @($ids)
Write-Ok "Videos a procesar: $($ids.Count)"

# --- 2. Iterar process-video.ps1 por cada video (proceso hijo) ---
$okCount = 0
$failCount = 0
$failed = @()
$i = 0
foreach ($vid in $ids) {
    $i++
    $vurl = "https://www.youtube.com/watch?v=$vid"
    Write-Host ""
    Write-Step "[$i/$($ids.Count)] $vurl"

    $argList = @(
        '-ExecutionPolicy', 'Bypass', '-File', $procVideo,
        '-Url', $vurl,
        '-SubFolder', $subFolder,
        '-Model', $Model,
        '-Language', $Language
    )
    if ($MaxSeconds -gt 0) { $argList += @('-MaxSeconds', "$MaxSeconds") }

    & powershell @argList
    if ($LASTEXITCODE -eq 0) {
        $okCount++
    } else {
        $failCount++
        $failed += $vurl
        Write-Bad "Video fallido (exit $LASTEXITCODE): $vurl -- se continua con el siguiente."
    }
}

# --- 3. Generar/actualizar Index.md local (sin LLM) ---
if (Test-Path -LiteralPath $destDir) {
    $notes = Get-ChildItem -LiteralPath $destDir -Filter '*.md' -File |
             Where-Object { $_.Name -ne 'Index.md' -and $_.Name -ne 'ficha-mentor.md' } |
             Sort-Object Name
    $nowIso = (Get-Date).ToString('yyyy-MM-dd')
    $rows = foreach ($n in $notes) {
        $name = [System.IO.Path]::GetFileNameWithoutExtension($n.Name)
        "| [$name]($($n.Name)) | $($n.LastWriteTime.ToString('yyyy-MM-dd')) |"
    }
    $indexMd = @"
# Indice de transcripciones -- $Mentor

> Carpeta de ingesta del mentor. Generado por process-channel.ps1 el $nowIso.
> $($notes.Count) transcripcion(es).

| Nota | Procesado |
|------|-----------|
$($rows -join "`n")
"@
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText((Join-Path $destDir 'Index.md'), $indexMd, $utf8NoBom)
    Write-Ok "Index.md actualizado ($($notes.Count) notas)."
} else {
    Write-Bad "La carpeta destino no existe (ningun video se proceso con exito): $destDir"
}

# --- 4. Reporte final ---
Write-Host ""
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "  process-channel  --  $Mentor" -ForegroundColor Green
Write-Host "  Total : $($ids.Count) | OK: $okCount | Fallidos: $failCount" -ForegroundColor Green
if ($failCount -gt 0) {
    Write-Host "  Fallidos:" -ForegroundColor Yellow
    $failed | ForEach-Object { Write-Host "    - $_" -ForegroundColor Yellow }
}
Write-Host "  Carpeta: $destDir" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green

if ($failCount -gt 0) { exit 1 }
exit 0
