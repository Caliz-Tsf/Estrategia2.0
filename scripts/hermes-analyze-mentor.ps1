<#
.SYNOPSIS
    Fase 2 del modulo Mentores -- Destila la ficha mental del mentor (map-reduce via Hermes/Puter).

.DESCRIPTION
    Lee las transcripciones .md de un mentor y produce ficha-mentor.md con los 8 campos
    (ver scripts/hermes-prompt-analisis-mentor.txt). Orientado a ARCHIVOS: las instrucciones
    a Hermes referencian RUTAS (el agente lee/escribe con el toolset `file`), nunca se pasa el
    texto completo por la linea de comandos -> evita el limite de longitud de Windows con
    transcripciones largas.

    Estrategia:
      MAP    (por video, modelo rapido): extrae notas parciales de los 8 campos -> parcial-N.md
      REDUCE (consolida, claude-sonnet-4-6): junta los parciales -> ficha-mentor.md
    Con -SinglePass (o un solo video) se omite el MAP y se hace un unico pase.

    NOTA: archivo solo-ASCII (PS 5.1 lee .ps1 como ANSI). La ficha de salida la escribe Hermes
    en UTF-8 (es contenido). Modelo SIEMPRE forzado a Puter (NIM/OR suspendidos).

    Codigos de salida: 0 OK | 1 error.

.PARAMETER MentorFolder
    Subcarpeta del mentor relativa al vault. Ej: "Mentores\boxxocode".

.PARAMETER VaultRoot
    Raiz del vault. Default: D:\obsidian\boveda MENTE\Mente

.PARAMETER MapModel
    Modelo Puter para el MAP (rapido). Default: gemini-2.5-pro.

.PARAMETER ReduceModel
    Modelo Puter para el REDUCE (sintesis). Default: claude-sonnet-4-6.

.PARAMETER SinglePass
    Fuerza un unico pase (sin MAP). Util cuando el curso entero cabe en contexto.

.PARAMETER Force
    Sobrescribe ficha-mentor.md si ya existe.

.EXAMPLE
    powershell -File scripts/hermes-analyze-mentor.ps1 -MentorFolder "Mentores\boxxocode"

.EXAMPLE
    powershell -File scripts/hermes-analyze-mentor.ps1 -MentorFolder "Mentores\Test" -SinglePass -Force
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$MentorFolder,

    [string]$VaultRoot   = 'D:\obsidian\boveda MENTE\Mente',
    [string]$MapModel    = 'gemini-2.5-pro',
    [string]$ReduceModel = 'claude-sonnet-4-6',
    [switch]$SinglePass,
    [switch]$Force
)

$ErrorActionPreference = 'Stop'

function Write-Step($m) { Write-Host "[..] $m" -ForegroundColor Cyan }
function Write-Ok($m)   { Write-Host "[OK] $m"  -ForegroundColor Green }
function Write-Bad($m)  { Write-Host "[X]  $m"  -ForegroundColor Red }

# Aplana un texto multilinea a una sola linea (CommandLineToArgvW fragmenta el multilinea).
function ConvertTo-Flat([string]$t) { return ($t -replace "`r`n", ' ' -replace "`n", ' ' -replace '\s{2,}', ' ').Trim() }

# Invoca Hermes con una instruccion (ya aplanada) forzando Puter. Devuelve el exit code.
function Invoke-Hermes([string]$flatPrompt, [string]$model) {
    & hermes chat -q $flatPrompt -t terminal,file --yolo -Q -m $model --provider puter
    return $LASTEXITCODE
}

# --- 0. Verificaciones ---
if (-not (Get-Command 'hermes' -ErrorAction SilentlyContinue)) {
    Write-Bad "Hermes no encontrado en PATH (pip install hermes-agent)."
    exit 1
}
$promptFile = Join-Path $PSScriptRoot 'hermes-prompt-analisis-mentor.txt'
if (-not (Test-Path -LiteralPath $promptFile)) {
    Write-Bad "Falta el prompt base: $promptFile"
    exit 1
}

$destDir = Join-Path $VaultRoot $MentorFolder
if (-not (Test-Path -LiteralPath $destDir)) {
    Write-Bad "La carpeta del mentor no existe: $destDir"
    exit 1
}

$fichaOut = Join-Path $destDir 'ficha-mentor.md'
if ((Test-Path -LiteralPath $fichaOut) -and -not $Force) {
    Write-Bad "Ya existe ficha-mentor.md. Usa -Force para sobrescribir: $fichaOut"
    exit 1
}

# Transcripciones: todos los .md salvo la ficha y el indice.
$videos = Get-ChildItem -LiteralPath $destDir -Filter '*.md' -File |
          Where-Object { $_.Name -ne 'ficha-mentor.md' -and $_.Name -ne 'Index.md' } |
          Sort-Object Name
if (-not $videos -or $videos.Count -eq 0) {
    Write-Bad "No hay transcripciones .md en $destDir (corre process-channel.ps1 primero)."
    exit 1
}
$videos = @($videos)
Write-Ok "Transcripciones encontradas: $($videos.Count)"

$useMap = (-not $SinglePass) -and ($videos.Count -gt 1)

if ($useMap) {
    # --- 1. MAP: notas parciales por video ---
    $tmpDir = Join-Path $env:TEMP "mentor-analisis-$($MentorFolder -replace '[^\w]', '_')"
    if (Test-Path -LiteralPath $tmpDir) { Remove-Item -LiteralPath $tmpDir -Recurse -Force }
    New-Item -ItemType Directory -Path $tmpDir -Force | Out-Null

    $n = 0
    $parciales = @()
    foreach ($v in $videos) {
        $n++
        $parcial = Join-Path $tmpDir ("parcial-{0:D3}.md" -f $n)
        Write-Step "MAP [$n/$($videos.Count)] $($v.Name) -> $(Split-Path $parcial -Leaf)"
        $instr = ConvertTo-Flat @"
Sigue al pie de la letra las instrucciones del archivo de sistema '$promptFile'.
Lee la transcripcion en '$($v.FullName)'.
Extrae NOTAS PARCIALES de los 8 campos a partir SOLO de esa transcripcion (es un video; no esperes
que cubra todos los campos). Escribe el resultado en '$parcial' con las 8 secciones '## '.
No inventes; usa '[no cubierto en el material]' donde falte. No imprimas la ficha en el chat, solo escribe el archivo.
"@
        $ec = Invoke-Hermes $instr $MapModel
        if ($ec -ne 0 -or -not (Test-Path -LiteralPath $parcial)) {
            Write-Bad "MAP fallo en $($v.Name) (exit $ec). Se aborta para no producir una ficha incompleta."
            exit 1
        }
        $parciales += $parcial
    }

    # --- 2. REDUCE: consolidar parciales -> ficha ---
    Write-Step "REDUCE: consolidando $($parciales.Count) parciales con $ReduceModel..."
    $listaParciales = ($parciales | ForEach-Object { "'$_'" }) -join ', '
    $instrR = ConvertTo-Flat @"
Sigue al pie de la letra las instrucciones del archivo de sistema '$promptFile'.
Te paso notas parciales de varios videos del mismo mentor en estos archivos: $listaParciales.
Leelos todos y CONSOLIDA una unica ficha final con las 8 secciones '## ', detectando los PATRONES
que se repiten entre videos y fusionando sin duplicar. Conserva las citas textuales literales.
No inventes; usa '[no cubierto en el material]' donde nada lo cubra.
Escribe la ficha final en '$fichaOut'. No la imprimas en el chat, solo escribe el archivo.
"@
    $ec = Invoke-Hermes $instrR $ReduceModel
}
else {
    # --- Un solo pase ---
    Write-Step "Pase unico (sin MAP) con $ReduceModel sobre $($videos.Count) transcripcion(es)..."
    $listaVideos = ($videos | ForEach-Object { "'$($_.FullName)'" }) -join ', '
    $instrS = ConvertTo-Flat @"
Sigue al pie de la letra las instrucciones del archivo de sistema '$promptFile'.
Lee TODAS estas transcripciones del mismo mentor: $listaVideos.
Destila una unica ficha final con las 8 secciones '## ', detectando los PATRONES que se repiten.
Conserva las citas textuales literales. No inventes; usa '[no cubierto en el material]' donde falte.
Escribe la ficha final en '$fichaOut'. No la imprimas en el chat, solo escribe el archivo.
"@
    $ec = Invoke-Hermes $instrS $ReduceModel
}

# --- 3. Verificar la ficha ---
if ($ec -ne 0 -or -not (Test-Path -LiteralPath $fichaOut)) {
    Write-Bad "No se genero la ficha (exit $ec): $fichaOut"
    exit 1
}
$fichaText = Get-Content -LiteralPath $fichaOut -Raw -Encoding UTF8
$secciones = ([regex]::Matches($fichaText, '(?m)^##\s')).Count

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "  hermes-analyze-mentor OK" -ForegroundColor Green
Write-Host "  Mentor       : $MentorFolder" -ForegroundColor Green
Write-Host "  Transcripts  : $($videos.Count) | Estrategia: $(if ($useMap) { 'map-reduce' } else { 'single-pass' })" -ForegroundColor Green
Write-Host "  Ficha        : $fichaOut" -ForegroundColor Green
Write-Host "  Secciones ## : $secciones (esperadas 8)" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
if ($secciones -lt 8) {
    Write-Host "[!] La ficha tiene menos de 8 secciones. Revisa el contenido y reejecuta con -Force si hace falta." -ForegroundColor Yellow
}
exit 0
