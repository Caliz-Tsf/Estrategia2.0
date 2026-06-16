<#
.SYNOPSIS
    Fase 3 del modulo Mentores -- Genera una skill de Hermes 'mentor-<slug>' desde la ficha.

.DESCRIPTION
    Lee ficha-mentor.md (8 secciones '## ') y construye una skill de Hermes en
    <SkillsDir>\mentor-<slug>\SKILL.md (frontmatter name/description + cuerpo con la ficha
    embebida + reglas de comportamiento + ruta del vault para recall on-demand).

    Override de modelo: si la ficha trae un frontmatter YAML con 'modelo: <id>', se escribe
    en <SkillsDir>\mentor-<slug>\model.txt (sidecar que lee hermes-chat-mentor.ps1). Si no,
    el mentor usa el default global (claude-sonnet-4-6 / Puter).

    NOTA: archivo solo-ASCII (PS 5.1). El SKILL.md de salida va UTF-8 sin BOM (embebe la ficha
    con acentos).

    Codigos de salida: 0 OK | 1 error.

.PARAMETER MentorFolder
    Subcarpeta del mentor relativa al vault. Ej: "Mentores\boxxocode".

.PARAMETER VaultRoot
    Raiz del vault. Default: D:\obsidian\boveda MENTE\Mente

.PARAMETER SkillsDir
    Carpeta de skills de Hermes. Default: %USERPROFILE%\.hermes\skills

.PARAMETER Force
    Sobrescribe la skill si ya existe.

.EXAMPLE
    powershell -File scripts/build-personality.ps1 -MentorFolder "Mentores\boxxocode"
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$MentorFolder,

    [string]$VaultRoot = 'D:\obsidian\boveda MENTE\Mente',
    [string]$SkillsDir = (Join-Path $env:USERPROFILE '.hermes\skills'),
    [switch]$Force
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

# --- 0. Localizar la ficha ---
$destDir  = Join-Path $VaultRoot $MentorFolder
$fichaPath = Join-Path $destDir 'ficha-mentor.md'
if (-not (Test-Path -LiteralPath $fichaPath)) {
    Write-Bad "No existe ficha-mentor.md (corre hermes-analyze-mentor.ps1 primero): $fichaPath"
    exit 1
}
$ficha = Get-Content -LiteralPath $fichaPath -Raw -Encoding UTF8

# Nombre/slug del mentor = ultimo segmento de MentorFolder.
$mentorName = Split-Path $MentorFolder -Leaf
$slug = Get-Slug $mentorName
$skillName = "mentor-$slug"

# --- 1. Override de modelo: frontmatter 'modelo:' de la ficha (opcional) ---
$modelOverride = ''
if ($ficha -match '(?ms)\A---\s*(.*?)\s*---') {
    $fm = $Matches[1]
    if ($fm -match '(?m)^\s*modelo\s*:\s*(\S+)\s*$') { $modelOverride = $Matches[1].Trim() }
}

# --- 2. Crear carpeta de la skill ---
$skillDir = Join-Path $SkillsDir $skillName
if ((Test-Path -LiteralPath $skillDir) -and -not $Force) {
    Write-Bad "La skill ya existe (usa -Force): $skillDir"
    exit 1
}
if (-not (Test-Path -LiteralPath $skillDir)) { New-Item -ItemType Directory -Path $skillDir -Force | Out-Null }

# --- 3. Construir SKILL.md ---
$modelLine = if ($modelOverride) { "Modelo preferido declarado en la ficha: ``$modelOverride`` (lo aplica hermes-chat-mentor.ps1)." } else { "Modelo: el default global (claude-sonnet-4-6 / Puter)." }

$skillBody = @"
---
name: $skillName
description: Encarna al mentor $mentorName. Responde SIEMPRE en su voz y metodologia (SMC/ICT/estrategia) segun su ficha; no inventa fuera de su dominio. Cargar con -s $skillName.
---

# Mentor: $mentorName

Eres **$mentorName**. Adoptas su identidad, voz, vocabulario, metodologia y mentalidad tal como
quedaron destiladas en la ficha de abajo. Mantienes la personalidad coherente en toda la conversacion.

## Reglas de comportamiento (duras)

1. **Habla como el mentor.** Usa su vocabulario, muletillas, frases ancla y tono (seccion "Voz").
2. **No salgas de tu dominio.** Si te preguntan algo ajeno a su metodologia/temas, dilo con su estilo
   ("eso no es lo mio / no es lo que yo enseno") y NO inventes una respuesta fuera de su mundo.
3. **No inventes reglas ni numeros.** Si una regla, umbral o cita no esta en la ficha ni en tus
   transcripciones, di que no lo cubriste. Cero invencion.
4. **Recall on-demand.** Para citar un detalle concreto, puedes leer tus transcripciones originales en
   la carpeta del vault (toolset ``file``): ``$destDir``. Cita textual = literal.
5. **Eres una voz de consulta, no la fuente de verdad del sistema.** Tus ideas (sobre todo si eres un
   mentor de estrategias) son SUGERENCIAS: el sistema las valida despues contra sus reglas duras
   (R:R>=1:3, umbrales ATR-relativos, anti-repaint) y los expertos-concepto.

$modelLine

---

## FICHA DEL MENTOR

$ficha
"@

$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText((Join-Path $skillDir 'SKILL.md'), $skillBody, $utf8NoBom)

# --- 4. Sidecar de modelo (si hay override) ---
if ($modelOverride) {
    [System.IO.File]::WriteAllText((Join-Path $skillDir 'model.txt'), $modelOverride, $utf8NoBom)
}

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "  build-personality OK" -ForegroundColor Green
Write-Host "  Skill   : $skillName" -ForegroundColor Green
Write-Host "  Carpeta : $skillDir" -ForegroundColor Green
Write-Host "  Modelo  : $(if ($modelOverride) { "$modelOverride (override de la ficha)" } else { 'default claude-sonnet-4-6 / Puter' })" -ForegroundColor Green
Write-Host "  Vault   : $destDir (recall on-demand)" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "  Cargar con:  hermes chat -s $skillName -t terminal,file --provider puter" -ForegroundColor DarkGray
exit 0
