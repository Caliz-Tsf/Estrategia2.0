#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Lanza TradingView Desktop con CDP y prepara el agente en UN SOLO COMANDO.

.DESCRIPTION
    1. Verifica si agent-browser está instalado
    2. Detecta si TV Desktop ya corre con CDP en puerto 9222
    3. Si no: lanza TV con path dinámico (AppxPackage) + flag CDP
    4. Espera hasta 15s a que el endpoint CDP responda (poll cada 2s)
    5. Cambia al tab del chart automáticamente
    6. Toma snapshot inicial y confirma que el agente puede ver el chart
    7. Imprime: "TV Desktop listo. Chart: [URL] | Tab: [tN] | Elementos: [N]"

.EXAMPLE
    .\scripts\launch-tv-agent.ps1
#>

$ErrorActionPreference = 'Stop'
$ProgressPreference    = 'SilentlyContinue'
$TVPort = 9222

# ─── Colores de consola ─────────────────────────────────────────────
function Write-Ok   { param($msg) Write-Host "[OK]  $msg" -ForegroundColor Green  }
function Write-Info { param($msg) Write-Host "[..] $msg"  -ForegroundColor Cyan   }
function Write-Warn { param($msg) Write-Host "[!!] $msg"  -ForegroundColor Yellow }
function Write-Fail { param($msg) Write-Host "[XX] $msg"  -ForegroundColor Red    }

# ─── 1. Verificar agent-browser ─────────────────────────────────────
Write-Info "Verificando agent-browser..."
$abPath = Get-Command agent-browser -ErrorAction SilentlyContinue
if (-not $abPath) {
    Write-Fail "agent-browser no está instalado."
    Write-Fail "Instálalo con: npm install -g agent-browser"
    exit 1
}
Write-Ok "agent-browser encontrado: $($abPath.Source)"

# ─── 2. Verificar si CDP ya responde ────────────────────────────────
function Test-CDP {
    try {
        $null = Invoke-RestMethod "http://localhost:$TVPort/json" -ErrorAction Stop
        return $true
    } catch {
        return $false
    }
}

$cdpAlreadyUp = Test-CDP

# ─── 3. Si TV corre sin CDP: matar y relanzar ───────────────────────
if (-not $cdpAlreadyUp) {
    $tvProcess = Get-Process -Name "TradingView" -ErrorAction SilentlyContinue
    if ($tvProcess) {
        Write-Warn "TV Desktop esta abierto SIN CDP (puerto $TVPort no responde)."
        Write-Warn "Cerrando TradingView para relanzar con --remote-debugging-port=$TVPort ..."
        $tvProcess | Stop-Process -Force
        Start-Sleep -Seconds 3
        Write-Ok "TradingView cerrado."
    }
}

# ─── 4. Lanzar TV Desktop si es necesario ───────────────────────────
if (-not $cdpAlreadyUp) {
    Write-Info "TV Desktop no detectado en puerto $TVPort. Buscando instalacion..."

    $tvInstallPath = $null

    # Método 1: AppxPackage (Windows Store) — preferido, siempre actual
    $pkg = Get-AppxPackage -Name "*TradingView*" -ErrorAction SilentlyContinue
    if ($pkg -and $pkg.InstallLocation) {
        $candidate = Join-Path $pkg.InstallLocation "TradingView.exe"
        if (Test-Path $candidate) {
            $tvInstallPath = $candidate
            Write-Info "Encontrado via AppxPackage: $tvInstallPath"
        }
    }

    # Método 2: Rutas fijas de fallback
    if (-not $tvInstallPath) {
        $fallbacks = @(
            "C:\Program Files\TradingView\TradingView.exe",
            "C:\Program Files (x86)\TradingView\TradingView.exe",
            "$env:LOCALAPPDATA\TradingView\TradingView.exe",
            "$env:LOCALAPPDATA\Programs\TradingView\TradingView.exe"
        )
        foreach ($fb in $fallbacks) {
            if (Test-Path $fb) {
                $tvInstallPath = $fb
                Write-Warn "AppxPackage no encontrado. Usando fallback: $tvInstallPath"
                break
            }
        }
    }

    if (-not $tvInstallPath) {
        Write-Fail "No se encontro TradingView.exe en ninguna ubicacion conocida."
        Write-Fail "Abre TradingView Desktop manualmente con:"
        Write-Fail '  $p = (Get-AppxPackage *TradingView*).InstallLocation + "\TradingView.exe"'
        Write-Fail '  Start-Process $p -ArgumentList "--remote-debugging-port=9222"'
        exit 1
    }

    Write-Info "Lanzando TV Desktop con CDP puerto $TVPort..."
    Start-Process -FilePath $tvInstallPath -ArgumentList "--remote-debugging-port=$TVPort" -WindowStyle Normal

} else {
    Write-Ok "TV Desktop ya esta corriendo con CDP en puerto $TVPort."
}

# ─── 4. Esperar hasta 15s a que CDP responda ────────────────────────
Write-Info "Esperando endpoint CDP http://localhost:$TVPort/json ..."

$maxWait  = 15
$interval = 2
$elapsed  = 0
$cdpReady = $false

while ($elapsed -le $maxWait) {
    if (Test-CDP) {
        $cdpReady = $true
        break
    }
    if ($elapsed -lt $maxWait) {
        Write-Warn "CDP no responde aun. Reintentando en ${interval}s... ($elapsed/${maxWait}s)"
        Start-Sleep -Seconds $interval
    }
    $elapsed += $interval
}

if (-not $cdpReady) {
    Write-Fail "CDP no respondio en ${maxWait}s. Verifica que TV Desktop este abierto."
    Write-Fail "Puedes lanzarlo manualmente con --remote-debugging-port=9222"
    exit 1
}

Write-Ok "CDP listo en http://localhost:$TVPort/json"

# ─── 5. Detectar tab del chart ──────────────────────────────────────
Write-Info "Buscando tab del chart de TradingView..."

$tabListRaw = & agent-browser --cdp $TVPort tab list 2>&1
$chartLine  = $tabListRaw | Where-Object { $_ -match 'tradingview\.com/chart' } | Select-Object -First 1

if (-not $chartLine) {
    Write-Warn "No se encontro tab con tradingview.com/chart. Tabs disponibles:"
    $tabListRaw | ForEach-Object { Write-Host "  $_" }
    Write-Fail "Navega al chart en TV Desktop y vuelve a ejecutar el script."
    exit 1
}

# Extraer ID de tab: "[t8]" → "t8"
if ($chartLine -match '\[t(\d+)\]') {
    $tabId  = "t$($Matches[1])"
    $tabNum = $Matches[1]
} else {
    Write-Fail "No se pudo extraer el ID del tab del chart: $chartLine"
    exit 1
}

# Extraer URL del chart
$chartUrl = if ($chartLine -match 'https://[^\s]+') { $Matches[0] } else { "URL desconocida" }

Write-Info "Tab del chart encontrado: [$tabId] | $chartUrl"

# ─── 6. Cambiar al tab del chart ────────────────────────────────────
Write-Info "Cambiando al tab [$tabId]..."
$null = & agent-browser --cdp $TVPort tab $tabId 2>&1

# ─── 7. Snapshot inicial ────────────────────────────────────────────
Write-Info "Tomando snapshot inicial del chart..."
$snapshot = & agent-browser --cdp $TVPort snapshot -i 2>&1

# Contar elementos interactivos (lineas con [ref=eN])
$refCount = ($snapshot | Select-String -Pattern '\[ref=e\d+\]').Count

# Detectar símbolo activo
$symbolLine = $snapshot | Where-Object { $_ -match 'button "([A-Z]{3,6})"' -and $_ -match 'ref=e' } | Select-Object -First 1
$activeSymbol = if ($symbolLine -match 'button "([A-Z]{3,6})"') { $Matches[1] } else { "DESCONOCIDO" }

# Detectar timeframe activo
$tfLine = $snapshot | Where-Object { $_ -match 'checked=true' -and $_ -match 'radio' } | Select-Object -First 1
$activeTF = if ($tfLine -match 'radio "([^"]+)"') { $Matches[1] } else { "DESCONOCIDO" }

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "  TV Desktop listo." -ForegroundColor Green
Write-Host "  Chart activo : $chartUrl" -ForegroundColor Green
Write-Host "  Tab          : [$tabId]" -ForegroundColor Green
Write-Host "  Simbolo      : $activeSymbol" -ForegroundColor Green
Write-Host "  Timeframe    : $activeTF" -ForegroundColor Green
Write-Host "  Elementos    : $refCount elementos interactivos" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
Write-Host ""
Write-Ok "Agente listo. Puedes usar agent-browser --cdp $TVPort <comando>"
