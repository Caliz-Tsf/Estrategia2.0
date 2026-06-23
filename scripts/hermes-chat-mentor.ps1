<#
.SYNOPSIS
    Fase 4 del modulo Mentores -- Launcher para chatear con un mentor ya construido.

.DESCRIPTION
    Carga la skill mentor-<slug> y abre Hermes en su voz. Resuelve el modelo en este orden:
      1) parametro -Model explicito
      2) sidecar <SkillsDir>\mentor-<slug>\model.txt (override declarado en la ficha)
      3) default global: nvidia/nemotron-3-super-120b-a12b (NVIDIA NIM, gratis 40/min)
    Proveedor configurable con -Provider (default nvidia_nim). Otros mapeados HOY en config.yaml:
    google, zenmux, ollama. (Puter quedo obsoleto; ya no esta en la config.)
    Toolset terminal,file (file = recall del vault).

    Con -q hace una consulta one-shot (no interactivo, --yolo). Sin -q abre el chat interactivo.

    NOTA: archivo solo-ASCII (PS 5.1).

.PARAMETER Mentor
    Nombre/slug del mentor (el de la skill mentor-<slug>). Ej: "boxxocode".

.PARAMETER Model
    Override explicito del modelo Puter. Si se omite, ver orden de resolucion arriba.

.PARAMETER Question
    Pregunta one-shot. Alias -q. Si se omite, abre el chat interactivo.

.PARAMETER SkillsDir
    Carpeta de skills de Hermes. Default: %USERPROFILE%\.hermes\skills

.EXAMPLE
    powershell -File scripts/hermes-chat-mentor.ps1 -Mentor boxxocode -q "Cual es tu setup favorito?"

.EXAMPLE
    powershell -File scripts/hermes-chat-mentor.ps1 -Mentor boxxocode
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Mentor,

    [string]$Model,

    [Alias('q')]
    [string]$Question,

    [string]$Provider = 'nvidia_nim',

    [string]$SkillsDir = (Join-Path $env:USERPROFILE '.hermes\skills')
)

$ErrorActionPreference = 'Stop'

function Write-Step($m) { Write-Host "[..] $m" -ForegroundColor Cyan }
function Write-Ok($m)   { Write-Host "[OK] $m"  -ForegroundColor Green }
function Write-Bad($m)  { Write-Host "[X]  $m"  -ForegroundColor Red }

function Get-Slug([string]$text) {
    if (-not $text) { return 'mentor' }
    $s = $text.ToLowerInvariant() -replace '[^a-z0-9]+', '-' -replace '(^-+)|(-+$)', ''
    if (-not $s) { $s = 'mentor' }
    return $s
}

if (-not (Get-Command 'hermes' -ErrorAction SilentlyContinue)) {
    Write-Bad "Hermes no encontrado en PATH (pip install hermes-agent)."
    exit 1
}

$slug = Get-Slug $Mentor
$skillName = "mentor-$slug"
$skillDir  = Join-Path $SkillsDir $skillName
if (-not (Test-Path -LiteralPath (Join-Path $skillDir 'SKILL.md'))) {
    Write-Bad "No existe la skill '$skillName' en $skillDir. Corre build-personality.ps1 primero."
    exit 1
}

# --- Resolver modelo: -Model > sidecar model.txt > default ---
$defaultModel = 'nvidia/nemotron-3-super-120b-a12b'
$resolved = $null
$source = ''
if ($Model) {
    $resolved = $Model; $source = 'parametro -Model'
}
else {
    $sidecar = Join-Path $skillDir 'model.txt'
    if (Test-Path -LiteralPath $sidecar) {
        $v = (Get-Content -LiteralPath $sidecar -Raw -Encoding UTF8).Trim()
        if ($v) { $resolved = $v; $source = 'sidecar model.txt (ficha)' }
    }
}
if (-not $resolved) { $resolved = $defaultModel; $source = 'default global' }

Write-Step "Mentor : $Mentor (skill: $skillName)"
Write-Step "Modelo : $resolved  [$source]  via $Provider"
Write-Host ""

# --- Invocar Hermes ---
if ($Question) {
    & hermes chat -s $skillName -m $resolved --provider $Provider -t terminal,file -q $Question --yolo -Q
} else {
    & hermes chat -s $skillName -m $resolved --provider $Provider -t terminal,file
}
exit $LASTEXITCODE
