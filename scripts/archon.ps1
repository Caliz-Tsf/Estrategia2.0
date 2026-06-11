<#
.SYNOPSIS
    Wrapper para invocar el CLI de Archon contra ESTE proyecto.

.DESCRIPTION
    La app Archon vive en D:\CODE\Archon (repo externo, instalada con `bun install`).
    Este wrapper la ejecuta en modo dev (bun) y fija --cwd al proyecto, para correr
    workflows de Archon (p.ej. smc-sprint cuando WF-01 lo cree) sin escribir la ruta
    larga cada vez.

    IMPORTANTE: no ejecutar workflows que invoquen Claude DESDE DENTRO de una sesion
    de Claude Code (variable CLAUDECODE=1) — pueden colgarse (Archon issue #1067).
    Correr este wrapper desde una terminal normal.

.EXAMPLE
    pwsh scripts/archon.ps1 workflow list
    pwsh scripts/archon.ps1 doctor
    pwsh scripts/archon.ps1 workflow run smc-sprint "F1-S1.1-T02 swings"
#>
[CmdletBinding()]
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$ArchonArgs
)

$ErrorActionPreference = 'Stop'

$archonApp = 'D:\CODE\Archon'
$projectRoot = Split-Path -Parent $PSScriptRoot
if (-not $projectRoot) { $projectRoot = (Get-Location).Path }

if (-not (Test-Path -LiteralPath $archonApp)) {
    throw "No se encontro la app Archon en $archonApp. Clonar: git clone https://github.com/coleam00/Archon `"$archonApp`" && cd `"$archonApp`" && bun install"
}

# Binario de Claude para builds no-dev (en dev mode Archon resuelve via node_modules).
$claudeBin = Join-Path $env:USERPROFILE '.local\bin\claude.exe'
if (Test-Path -LiteralPath $claudeBin) { $env:CLAUDE_BIN_PATH = $claudeBin }

# Pasa el cwd del proyecto salvo que el usuario ya haya especificado --cwd.
$passArgs = @($ArchonArgs)
if ($passArgs -notcontains '--cwd') {
    $passArgs += @('--cwd', $projectRoot)
}

# Ejecutar DESDE el dir de la app (no usar `bun --cwd`: ese flag colisiona con el
# --cwd del propio CLI de Archon). Push/Pop garantiza volver al dir original.
Push-Location $archonApp
try {
    & bun run cli @passArgs
    $code = $LASTEXITCODE
} finally {
    Pop-Location
}
exit $code
