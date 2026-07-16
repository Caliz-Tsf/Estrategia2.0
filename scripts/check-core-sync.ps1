<#
.SYNOPSIS
    Verifica que la seccion "// === LIBRARY CORE ===" sea BYTE-IDENTICA en
    SMC-Visual.pine, SMC-Strategy.pine y (si existe) SMC-Context.pine
    (regla dura #2 del proyecto; tercer consumidor = ADR-017).

.DESCRIPTION
    Extrae de cada archivo el bloque desde la linea marcador
    "// === LIBRARY CORE ===" (inclusive) hasta el siguiente encabezado de
    seccion "// === ... ===" (exclusive), normaliza fin de linea a LF y compara
    por hash SHA-256. Si divergen, imprime el diff linea a linea y sale con
    codigo 1. Si coinciden, sale con 0.

    El tercer consumidor SMC-Context.pine (ADR-017) es OPCIONAL: si el archivo
    existe, su bloque CORE debe tener el mismo SHA que el Visual; si NO existe,
    el comportamiento es el mismo de siempre (solo Visual vs Strategy) para no
    romper Fase 0/CI.

    Corre en cada commit de codigo Pine (Fases 1-2) y en el cierre de sesion.
    Tolera que los archivos Pine aun no existan (Fase 0): si AMBOS faltan, no
    hay core que verificar -> exit 0 informativo.

    NOTA: archivo solo-ASCII a proposito. Windows PowerShell 5.1 lee .ps1 como
    ANSI (no UTF-8 sin BOM), por lo que caracteres no-ASCII romperian el parseo.

    Codigos de salida:
      0 = core identico (o aun no hay archivos Pine que verificar)
      1 = core DIVERGENTE (Visual != Strategy)  -> ARREGLAR antes de commitear
      2 = error de uso (falta un solo archivo, o falta el marcador LIBRARY CORE)

.PARAMETER VisualPath
    Ruta a SMC-Visual.pine. Default: pine/SMC-Visual.pine

.PARAMETER StrategyPath
    Ruta a SMC-Strategy.pine. Default: pine/SMC-Strategy.pine

.PARAMETER ContextPath
    Ruta al tercer consumidor SMC-Context.pine (ADR-017). Default:
    pine/SMC-Context.pine. Opcional: si el archivo no existe, se ignora.

.PARAMETER Quiet
    Solo codigo de salida y una linea de resumen (para hooks/CI).

.EXAMPLE
    powershell -File scripts/check-core-sync.ps1

.EXAMPLE
    powershell -File scripts/check-core-sync.ps1 -VisualPath a.pine -StrategyPath b.pine
#>
[CmdletBinding()]
param(
    [string]$VisualPath,
    [string]$StrategyPath,
    [string]$ContextPath,
    [switch]$Quiet
)

$ErrorActionPreference = 'Stop'

# Resolver rutas por defecto en el cuerpo (no en el param default: $PSScriptRoot
# se evalua vacio en defaults de param() bajo Windows PowerShell 5.1).
$scriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
$projectRoot = Split-Path -Parent $scriptDir
if (-not $VisualPath)   { $VisualPath   = Join-Path $projectRoot 'pine/SMC-Visual.pine' }
if (-not $StrategyPath) { $StrategyPath = Join-Path $projectRoot 'pine/SMC-Strategy.pine' }
if (-not $ContextPath)  { $ContextPath  = Join-Path $projectRoot 'pine/SMC-Context.pine' }

# Regex del marcador de inicio y de cualquier encabezado de seccion.
$startRe    = '^\s*//\s*===\s*LIBRARY\s+CORE\s*===\s*$'
$sectionRe  = '^\s*//\s*===\s*.+?\s*===\s*$'
# [ADR-022] 2.º bloque byte-identico, SOLO Strategy + Context (el Visual no debe cargarlo).
$extremesRe = '^\s*//\s*===\s*EXTREMES\s+CORE\s*===\s*$'

function Write-Info($msg) { if (-not $Quiet) { Write-Host $msg } }

# Extrae un bloque delimitado por su marcador de inicio hasta el siguiente header de seccion.
# Devuelve $null si no encuentra el marcador de inicio.
function Get-Block([string]$path, [string]$startPattern) {
    $lines = [System.IO.File]::ReadAllLines($path)
    $startIdx = -1
    for ($i = 0; $i -lt $lines.Count; $i++) {
        if ($lines[$i] -match $startPattern) { $startIdx = $i; break }
    }
    if ($startIdx -lt 0) { return $null }

    $endIdx = $lines.Count  # por defecto hasta EOF
    for ($j = $startIdx + 1; $j -lt $lines.Count; $j++) {
        if ($lines[$j] -match $sectionRe) { $endIdx = $j; break }
    }
    # Bloque = desde el marcador (incl.) hasta el siguiente header (excl.)
    return $lines[$startIdx..($endIdx - 1)]
}

function Get-CoreBlock([string]$path) { Get-Block $path $startRe }

function Get-Sha256([string]$text) {
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        $bytes = [System.Text.Encoding]::UTF8.GetBytes($text)
        return -join ($sha.ComputeHash($bytes) | ForEach-Object { $_.ToString('x2') })
    } finally { $sha.Dispose() }
}

# --- Resolucion de existencia de archivos ---
$hasV = Test-Path -LiteralPath $VisualPath
$hasS = Test-Path -LiteralPath $StrategyPath
$hasC = Test-Path -LiteralPath $ContextPath

if (-not $hasV -and -not $hasS) {
    Write-Info "[i] Ni SMC-Visual.pine ni SMC-Strategy.pine existen aun (Fase 0)."
    Write-Info "    No hay LIBRARY CORE que verificar. OK."
    Write-Host "CORE_SYNC=SKIP (sin archivos Pine)"
    exit 0
}
if ($hasV -xor $hasS) {
    $missing = if ($hasV) { $StrategyPath } else { $VisualPath }
    Write-Host "[X] ERROR: solo uno de los dos archivos Pine existe. Falta: $missing" -ForegroundColor Red
    Write-Host "CORE_SYNC=ERROR (falta un archivo)"
    exit 2
}

# --- Extraccion de los bloques ---
$coreV = Get-CoreBlock $VisualPath
$coreS = Get-CoreBlock $StrategyPath

if ($null -eq $coreV) {
    Write-Host "[X] ERROR: marcador '// === LIBRARY CORE ===' no encontrado en $VisualPath" -ForegroundColor Red
    Write-Host "CORE_SYNC=ERROR (sin marcador en Visual)"
    exit 2
}
if ($null -eq $coreS) {
    Write-Host "[X] ERROR: marcador '// === LIBRARY CORE ===' no encontrado en $StrategyPath" -ForegroundColor Red
    Write-Host "CORE_SYNC=ERROR (sin marcador en Strategy)"
    exit 2
}

# Normaliza a LF para comparar contenido (no falsos positivos por CRLF/LF).
$textV = ($coreV -join "`n")
$textS = ($coreS -join "`n")
$hashV = Get-Sha256 $textV
$hashS = Get-Sha256 $textS

if ($hashV -eq $hashS) {
    Write-Info "[OK] LIBRARY CORE identico en Visual y Strategy."
    Write-Info ("     Lineas: {0} | SHA-256: {1}" -f $coreV.Count, $hashV.Substring(0, 16))

    # --- Verificacion opcional del tercer consumidor Context (ADR-017) ---
    if ($hasC) {
        $coreC = Get-CoreBlock $ContextPath
        if ($null -eq $coreC) {
            Write-Host "[X] ERROR: marcador '// === LIBRARY CORE ===' no encontrado en $ContextPath" -ForegroundColor Red
            Write-Host "CORE_SYNC=ERROR (sin marcador en Context)"
            exit 2
        }
        $textC = ($coreC -join "`n")
        $hashC = Get-Sha256 $textC
        if ($hashC -ne $hashV) {
            Write-Host "[X] LIBRARY CORE DIVERGENTE entre Visual y Context." -ForegroundColor Red
            Write-Host ("    Visual:  {0}  ({1} lineas, SHA {2})" -f $VisualPath, $coreV.Count, $hashV.Substring(0, 16))
            Write-Host ("    Context: {0}  ({1} lineas, SHA {2})" -f $ContextPath, $coreC.Count, $hashC.Substring(0, 16))
            if (-not $Quiet) {
                Write-Host ""
                Write-Host "    --- Diferencias (V = solo Visual, C = solo Context) ---"
                $diffC = Compare-Object -ReferenceObject $coreV -DifferenceObject $coreC -CaseSensitive
                foreach ($d in $diffC) {
                    $tag = if ($d.SideIndicator -eq '<=') { 'V' } else { 'C' }
                    Write-Host ("    [{0}] {1}" -f $tag, $d.InputObject)
                }
            }
            Write-Host ""
            Write-Host "CORE_SYNC=DIVERGENT -- ARREGLAR antes de commitear (regla dura #2, ADR-017)."
            exit 1
        }
        Write-Info "[OK] LIBRARY CORE identico tambien en Context (3 consumidores)."

        # --- EXTREMES CORE (ADR-022): 2.º bloque byte-identico, solo Strategy + Context ---
        # f_tfExtremes NO vive en el LIBRARY CORE porque Visual no la llama nunca y en Pine una
        # funcion no-llamada SI cuenta tokens (ADR-020) -> sus 139 lineas cruzaban al Visual sobre
        # el techo CE10117 (medido S133). Pero la comparten 2 consumidores => necesita la MISMA
        # garantia de single-source-of-truth que el CORE. Sin este check quedarian 2 copias a mano.
        $extS = Get-Block $StrategyPath $extremesRe
        $extC = Get-Block $ContextPath  $extremesRe
        if ($null -eq $extS -and $null -eq $extC) {
            Write-Info "[i] Sin bloque EXTREMES CORE en Strategy/Context (nada que verificar)."
        } elseif ($null -eq $extS -or $null -eq $extC) {
            $falta = if ($null -eq $extS) { $StrategyPath } else { $ContextPath }
            Write-Host "[X] ERROR: EXTREMES CORE existe en uno pero no en el otro. Falta en: $falta" -ForegroundColor Red
            Write-Host "CORE_SYNC=ERROR (EXTREMES CORE incompleto)"
            exit 2
        } else {
            $hashES = Get-Sha256 ($extS -join "`n")
            $hashEC = Get-Sha256 ($extC -join "`n")
            if ($hashES -ne $hashEC) {
                Write-Host "[X] EXTREMES CORE DIVERGENTE entre Strategy y Context." -ForegroundColor Red
                Write-Host ("    Strategy: {0} lineas, SHA {1}" -f $extS.Count, $hashES.Substring(0, 16))
                Write-Host ("    Context:  {0} lineas, SHA {1}" -f $extC.Count, $hashEC.Substring(0, 16))
                if (-not $Quiet) {
                    Write-Host ""
                    Write-Host "    --- Diferencias (S = solo Strategy, C = solo Context) ---"
                    foreach ($d in (Compare-Object -ReferenceObject $extS -DifferenceObject $extC -CaseSensitive)) {
                        $tag = if ($d.SideIndicator -eq '<=') { 'S' } else { 'C' }
                        Write-Host ("    [{0}] {1}" -f $tag, $d.InputObject)
                    }
                }
                Write-Host ""
                Write-Host "CORE_SYNC=DIVERGENT -- ARREGLAR antes de commitear (ADR-022)."
                exit 1
            }
            Write-Info ("[OK] EXTREMES CORE identico en Strategy y Context (ADR-022).")
            Write-Info ("     Lineas: {0} | SHA-256: {1}" -f $extS.Count, $hashES.Substring(0, 16))
            # Guardrail: el Visual NO debe cargarlo (es la razon de existir del bloque).
            if ((Get-Block $VisualPath $extremesRe) -or ([System.IO.File]::ReadAllText($VisualPath) -match 'f_tfExtremes\(')) {
                Write-Host "[X] ERROR: SMC-Visual.pine contiene f_tfExtremes / EXTREMES CORE." -ForegroundColor Red
                Write-Host "    Ese bloque existe precisamente para que el Visual NO lo cargue (CE10117, ADR-022)."
                Write-Host "CORE_SYNC=ERROR (Visual carga EXTREMES CORE)"
                exit 2
            }
        }

        Write-Host "CORE_SYNC=OK"
        exit 0
    }

    Write-Host "CORE_SYNC=OK"
    exit 0
}

# --- Divergencia: mostrar diff linea a linea ---
Write-Host "[X] LIBRARY CORE DIVERGENTE entre Visual y Strategy." -ForegroundColor Red
Write-Host ("    Visual:   {0}  ({1} lineas, SHA {2})" -f $VisualPath, $coreV.Count, $hashV.Substring(0, 16))
Write-Host ("    Strategy: {0}  ({1} lineas, SHA {2})" -f $StrategyPath, $coreS.Count, $hashS.Substring(0, 16))
if (-not $Quiet) {
    Write-Host ""
    Write-Host "    --- Diferencias (V = solo Visual, S = solo Strategy) ---"
    $diff = Compare-Object -ReferenceObject $coreV -DifferenceObject $coreS -CaseSensitive
    foreach ($d in $diff) {
        $tag = if ($d.SideIndicator -eq '<=') { 'V' } else { 'S' }
        Write-Host ("    [{0}] {1}" -f $tag, $d.InputObject)
    }
}
Write-Host ""
Write-Host "CORE_SYNC=DIVERGENT -- ARREGLAR antes de commitear (regla dura #2)."
exit 1
