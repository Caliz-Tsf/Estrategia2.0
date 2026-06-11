<#
.SYNOPSIS
    SCR-02 — Respalda sesiones y ADRs del proyecto en el vault Obsidian.

.DESCRIPTION
    Copia incrementalmente los archivos nuevos o modificados desde el repo
    Estrategia2.0 hacia el vault de respaldo en Obsidian. Solo ESCRITURA hacia
    el vault — nunca lee de Estrategia-Nueva (proyecto previo, prohibido como
    referencia; ver CLAUDE.md). Compara por hash de contenido: solo copia lo que
    realmente cambió.

    Fuentes (CLAUDE.md / WORKPLAN §SCR-02):
      - memory/sesiones/   -> <vault>/sesiones/
      - docs/adrs/         -> <vault>/adrs/
      - memory/ESTADO-ACTUAL.md -> <vault>/ESTADO-ACTUAL.md  (estado inter-sesión)

.PARAMETER DryRun
    No copia nada; solo reporta qué se copiaría. Es el modo del criterio de
    "done" de SCR-02.

.PARAMETER VaultRoot
    Carpeta destino en el vault. Default: el destino del proyecto.

.EXAMPLE
    pwsh scripts/sync-obsidian.ps1 -DryRun
    pwsh scripts/sync-obsidian.ps1
#>
[CmdletBinding()]
param(
    [switch]$DryRun,
    [string]$RepoRoot,
    [string]$VaultRoot = 'D:\obsidian\boveda MENTE\Mente\Estrategia2.0'
)

$ErrorActionPreference = 'Stop'

# Resolver la raíz del repo de forma robusta (el script vive en <repo>\scripts\).
if (-not $RepoRoot) {
    $scriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
    $RepoRoot = Split-Path -Parent $scriptDir
}

# Mapa fuente -> subcarpeta destino. Carpetas se copian recursivas (*.md);
# archivos sueltos se copian tal cual.
$jobs = @(
    @{ Source = Join-Path $RepoRoot 'memory\sesiones';     Dest = Join-Path $VaultRoot 'sesiones'; Kind = 'dir' }
    @{ Source = Join-Path $RepoRoot 'docs\adrs';           Dest = Join-Path $VaultRoot 'adrs';     Kind = 'dir' }
    @{ Source = Join-Path $RepoRoot 'memory\ESTADO-ACTUAL.md'; Dest = $VaultRoot;                  Kind = 'file' }
)

function Get-FileHashSafe([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path)) { return $null }
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash
}

$mode = if ($DryRun) { 'DRY-RUN' } else { 'SYNC' }
Write-Host "=== sync-obsidian.ps1 [$mode] ===" -ForegroundColor Cyan
Write-Host "Repo : $RepoRoot"
Write-Host "Vault: $VaultRoot"
Write-Host ""

# El vault padre debe existir (es disco físico); la carpeta del proyecto la creamos.
$vaultParent = Split-Path -Parent $VaultRoot
if (-not (Test-Path -LiteralPath $vaultParent)) {
    throw "El vault padre no existe: $vaultParent. ¿Disco/ruta correcta?"
}

$copied = 0; $skipped = 0; $missing = 0

foreach ($job in $jobs) {
    if (-not (Test-Path -LiteralPath $job.Source)) {
        Write-Host "  [skip] fuente no existe: $($job.Source)" -ForegroundColor DarkYellow
        $missing++
        continue
    }

    # Resolver pares (origen, destino)
    $pairs = @()
    if ($job.Kind -eq 'dir') {
        Get-ChildItem -LiteralPath $job.Source -Filter '*.md' -File -Recurse | ForEach-Object {
            $rel = $_.FullName.Substring($job.Source.Length).TrimStart('\')
            $pairs += @{ Src = $_.FullName; Dst = (Join-Path $job.Dest $rel) }
        }
    } else {
        $name = Split-Path -Leaf $job.Source
        $pairs += @{ Src = $job.Source; Dst = (Join-Path $job.Dest $name) }
    }

    foreach ($p in $pairs) {
        $srcHash = Get-FileHashSafe $p.Src
        $dstHash = Get-FileHashSafe $p.Dst
        $relName = Split-Path -Leaf $p.Dst

        if ($srcHash -eq $dstHash) {
            Write-Host "  [=]    $relName (sin cambios)" -ForegroundColor DarkGray
            $skipped++
            continue
        }

        $verb = if ($null -eq $dstHash) { 'NEW ' } else { 'UPD ' }
        Write-Host "  [$verb] $relName" -ForegroundColor Green

        if (-not $DryRun) {
            $dstDir = Split-Path -Parent $p.Dst
            if (-not (Test-Path -LiteralPath $dstDir)) {
                New-Item -ItemType Directory -Path $dstDir -Force | Out-Null
            }
            Copy-Item -LiteralPath $p.Src -Destination $p.Dst -Force
        }
        $copied++
    }
}

Write-Host ""
Write-Host "Resumen: $copied a copiar/copiados | $skipped sin cambios | $missing fuentes ausentes" -ForegroundColor Cyan
if ($DryRun) {
    Write-Host "(dry-run: no se escribio nada)" -ForegroundColor Yellow
}
