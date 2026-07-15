# -*- coding: utf-8 -*-
"""
S131 · PROBE v7 — la regla de pools: que pool ancla el rango de cada temporalidad.

QUE MIDE. docs/planes/DISENO-regla-de-pools-S131.md. La regla (desambiguada por el usuario en S131):
el extremo de un TF = el pool MAS LEJANO del precio, con fuerza suficiente, DENTRO del rango del TF
superior. Eso es literalmente f_farthestPool(src, px, up, minT, bound, inclSwept) — ya en el CORE
(:1816). Lo unico que cambia vs. lo implementado es el BOUND: hoy es close +- kExt*rango (:2001,
distancia aritmetica); la regla dice que el bound de H1 ES el rango de D1.

LA CONSECUENCIA (escrita antes de medir, §2 del diseno). f_markPoolsSwept (:1389) marca swept TODO
pool revisitado por el precio; f_prunePools (:1425) borra PRIMERO el barrido mas antiguo al desbordar
MAX_POOLS=50 (:231); f_farthestPool PREFIERE VIVOS. Los niveles que el usuario LEE (techo H1 1.39972,
suelo SSL-3 1.01854, suelo D1 0.95360) son de 2014-2022 y el precio los cruzo muchas veces => estarian
swept y probablemente ya borrados => la regla no tendria a que anclar. HIPOTESIS DE LECTURA, no hecho.

PREDICCIONES (escritas ANTES de medir — van 15 vivas de 32; detalle en el doc §3):
  P-P1  (LA QUE DECIDE) Ninguno de 0.95360 / 1.01854 / 1.39972 sobrevive VIVO en el set en la ultima
        barra: P_nAliveAbove <= 3 y P_maxAliveLvl < 1.39972. (P_hit* = 0 para los tres.)
  P-P2  El set DESBORDA el cap: P_nAtCap > 0 y P_maxSize == MAX_POOLS_CHART (80). El prune actua.
  P-P3  La fuerza no discrimina: P_nAliveT3 <= 2 en todo el set. Corolario: el SSL-3 que el usuario ve
        viene del CHART (cap 80 + f_prunePoolsV por importancia, :2089), NO del transporte que
        alimenta f_tfExtremes (cap 50 + f_prunePools por antiguedad) => miran DOS SETS DISTINTOS.
  P-P4  TAUTOLOGICA POR CONSTRUCCION — se declara ANTES de medir y NO cuenta como prediccion viva:
        con bound = rango D1 el anidamiento D1 ⊇ H1 ⊇ M5 sale forzado por el bound. Lo que si
        discrimina es el fallback (P-P5).
  P-P5  El fallback es la mitad del sistema, no un detalle: P_nNoPoolDown / P_nBars > 30%.

ANTI-HUMO (S128/S129/S130):
  - NADA se lee en islast salvo el censo final (que es explicitamente un censo de estado final);
    todos los contadores corren sobre TODA la historia confirmada, con P_nBars como denominador.
  - Contadores DESCOMPUESTOS POR LADO (S128: el bug de legExtHi/Lo se delato por lado).
  - Cross-check aritmetico: P_nAlive + P_nSwept debe == P_nPools (si no, el censo miente).
  - P_close de control (data_get_study_values SIGUE EL CROSSHAIR -> raton al borde derecho).
  - P_marker = 1310, nuevo por build: unico distintivo fresco/rancio (S129/S130).
TRUNCADO en "// === DIBUJO ===" (CE10117 — el Visual completo + probe no cabe).

Uso:
  python scripts/gen_probe_regla_pools.py
"""
import sys, os, pathlib

SRC = pathlib.Path(__file__).resolve().parent.parent / "pine" / "SMC-Visual.pine"
OUT = pathlib.Path(os.environ.get("TEMP", ".")) / "PROBE-regla-pools-S131.pine"
MARKER = 1312

# Los tres niveles que el usuario LEE a ojo (S128/S130). Se buscan en el set con tolerancia.
NIV_USUARIO = [("D1lo", 0.95360), ("H1lo", 1.01854), ("H1hi", 1.39972)]
TOL_HIT = 0.0030   # 30 pips: generoso a proposito — si NI ASI hay hit, P-P1 es solida.

s = SRC.read_text(encoding="utf-8")

# Anclas que el probe necesita que existan tal cual (si el CORE cambio, fallar RUIDOSO, no medir humo).
for needed in ("f_farthestPool(array<SMC_Pool> src, float px, bool up, int minT, float bound, bool inclSwept) =>",
               "f_prunePoolsV(SMC_pools, MAX_POOLS_CHART)",
               "chartState.pdHigh := trailing.top"):
    if s.count(needed) != 1:
        print(f"[FALLO] no se encontro exactamente 1 vez: {needed!r} (encontro {s.count(needed)})")
        sys.exit(1)

MARK = "// === DIBUJO ==="
if s.count(MARK) != 1:
    print(f"[FALLO] marcador de truncado no unico: {s.count(MARK)}")
    sys.exit(1)
lineas_antes = len(s.splitlines())
s = s[:s.index(MARK)]
print(f"[truncado] render eliminado en {MARK!r}: {lineas_antes} -> {len(s.splitlines())} lineas")

hits_decl = "\n".join(
    f"var int nHit{n} = 0\nvar float dMin{n} = 1e9" for n, _ in NIV_USUARIO
)
# OJO indentacion: esto va DENTRO del "for i = 0 to nPools - 1" (cuerpo a 12 espacios). A 8 caeria
# fuera del bucle y 'p' no existiria -> "Undeclared identifier" (pasado en S131, atrapado por pine_check).
hits_scan = "\n".join(
    f"""            float d{n} = math.abs(p.level - {lvl})
            if d{n} < dMin{n}
                dMin{n} := d{n}
            if d{n} <= {TOL_HIT} and not p.swept
                nHit{n} += 1""" for n, lvl in NIV_USUARIO
)
hits_plot = "\n".join(
    f'plot(nHit{n}, "P_hit{n}")\nplot(dMin{n}, "P_dMin{n}")' for n, _ in NIV_USUARIO
)

PROBE = f"""

// --- [S131 · PROBE v7: la regla de pools — que pool ancla el rango de cada TF]
// La regla (usuario, S131): extremo = pool MAS LEJANO con fuerza >= minT, DENTRO del rango del TF
// superior. En el chart D1 el "TF superior" es el propio rango D1 => bound = chartState.pdHigh/pdLow.
var int nBars    = 0
var int nAtCap   = 0     // P-P2: barras con el set al tope (el prune esta actuando)
var int maxSize  = 0
var int nNoPoolUp   = 0  // P-P5 / M2: barras SIN pool vivo dentro del bound, por LADO (S128: por lado)
var int nNoPoolDown = 0
var int nSideUpOK   = 0
var int nSideDownOK = 0

if barstate.isconfirmed
    nBars += 1
    int sz = array.size(SMC_pools)
    if sz > maxSize
        maxSize := sz
    if sz >= MAX_POOLS_CHART
        nAtCap += 1
    // M2 sobre TODA la historia: la regla nueva, en sombra, con bound = rango D1 vigente.
    [luU, ldU, ltU, lsU] = f_farthestPool(SMC_pools, close, true,  i_minTouches, chartState.pdHigh, false)
    [luD, ldD, ltD, lsD] = f_farthestPool(SMC_pools, close, false, i_minTouches, chartState.pdLow,  false)
    if na(luU)
        nNoPoolUp += 1
    else
        nSideUpOK += 1
    if na(luD)
        nNoPoolDown += 1
    else
        nSideDownOK += 1

// --- CENSO del set en la ultima barra (estado final, explicitamente en islast).
int   nPools      = 0
int   nAlive      = 0
int   nSwept      = 0
int   nAliveAbove = 0
int   nAliveBelow = 0
int   nAliveT1    = 0
int   nAliveT2    = 0
int   nAliveT3    = 0
int   nAliveT4    = 0
float maxAliveLvl = na
float minAliveLvl = na
// M1 cerrada: la regla NUEVA evaluada en sombra en la ultima barra (bound = rango D1 vigente).
// Si el pool mas lejano arriba dentro del bound ES el propio pdHigh, el "anidamiento" es DEGENERADO:
// el TF inferior hereda el extremo del superior en vez de anclar uno propio.
[rgU, rgUd, rgUt, rgUs] = f_farthestPool(SMC_pools, close, true,  i_minTouches, chartState.pdHigh, false)
[rgD, rgDd, rgDt, rgDs] = f_farthestPool(SMC_pools, close, false, i_minTouches, chartState.pdLow,  false)
{hits_decl}

if barstate.islast
    nPools := array.size(SMC_pools)
    if nPools > 0
        for i = 0 to nPools - 1
            SMC_Pool p = array.get(SMC_pools, i)
            if p.swept
                nSwept += 1
            else
                nAlive += 1
                // M1: histograma de fuerza. i_minTouches (default 2) es el gate vigente de anclaje.
                if p.touches == 1
                    nAliveT1 += 1
                if p.touches >= 2
                    nAliveT2 += 1
                if p.touches >= 3
                    nAliveT3 += 1
                if p.touches >= 4
                    nAliveT4 += 1
                if p.level > close
                    nAliveAbove += 1
                    if na(maxAliveLvl) or p.level > maxAliveLvl
                        maxAliveLvl := p.level
                else
                    nAliveBelow += 1
                    if na(minAliveLvl) or p.level < minAliveLvl
                        minAliveLvl := p.level
{hits_scan}

plot(nBars,   "P_nBars")
plot({MARKER}, "P_marker")
plot(close,   "P_close")

// P-P2: el prune actua?
plot(nAtCap,  "P_nAtCap")
plot(maxSize, "P_maxSize")

// P-P1 / P-P3: el censo del set. Cross-check: nAlive + nSwept debe == nPools.
plot(nPools,      "P_nPools")
plot(nAlive,      "P_nAlive")
plot(nSwept,      "P_nSwept")
plot(nAlive + nSwept - nPools, "P_xcheckCenso")
plot(nAliveAbove, "P_nAliveAbove")
plot(nAliveBelow, "P_nAliveBelow")
// M1: el histograma de fuerza. Cross-check: nAliveT1 + nAliveT2 debe == nAlive (toques >= 1 siempre).
plot(nAliveT1,    "P_nAliveT1")
plot(nAliveT2,    "P_nAliveT2")
plot(nAliveT3,    "P_nAliveT3")
plot(nAliveT4,    "P_nAliveT4")
plot(nAliveT1 + nAliveT2 - nAlive, "P_xcheckT")

// M1 cerrada: la regla NUEVA en sombra. Si P_reglaUp == P_pdHigh, el anidamiento es DEGENERADO.
plot(rgU, "P_reglaUp")
plot(rgD, "P_reglaDown")
plot(rgU - chartState.pdHigh, "P_degenUp")
plot(rgD - chartState.pdLow,  "P_degenDown")
plot(maxAliveLvl, "P_maxAliveLvl")
plot(minAliveLvl, "P_minAliveLvl")

// P-P1: los tres niveles que el usuario LEE. nHit* = pools VIVOS a <= {TOL_HIT} del nivel;
// dMin* = a que distancia quedo el pool mas cercano (delata "cerca pero no").
{hits_plot}

// --- VOLCADO: los pools VIVOS uno a uno (nivel | toques | antiguedad en velas).
// Por que un label y no plots: son ~38 filas, no caben en plots. Se lee con data_get_pine_labels.
// RE10045: NADA de array.push en islast (revienta el limite de recursos) -> string acumulador.
if barstate.islast
    string dump = "POOLS VIVOS (nivel|toques|edad_velas)\\n"
    if array.size(SMC_pools) > 0
        for i = 0 to array.size(SMC_pools) - 1
            SMC_Pool p = array.get(SMC_pools, i)
            if not p.swept
                dump += str.tostring(p.level, "#.#####") + "|" + str.tostring(p.touches) + "|" + str.tostring(bar_index - p.barIdx) + "\\n"
    label.new(bar_index, close, dump, style = label.style_label_left, textcolor = color.white, size = size.small)

// P-P5 / M2: el fallback, por lado. Cross-check: nNoPoolUp + nSideUpOK debe == nBars.
plot(nNoPoolUp,   "P_nNoPoolUp")
plot(nNoPoolDown, "P_nNoPoolDown")
plot(nNoPoolUp + nSideUpOK - nBars,     "P_xcheckUp")
plot(nNoPoolDown + nSideDownOK - nBars, "P_xcheckDown")

// Control: el bound vigente de la regla, para contraste.
plot(chartState.pdHigh, "P_pdHigh")
plot(chartState.pdLow,  "P_pdLow")
"""

s = s + PROBE
OUT.write_text(s, encoding="utf-8")
print(f"Variante: regla de pools — censo + cap + fallback por lado (marker={MARKER})")
print(f"niveles del usuario buscados (tol={TOL_HIT}): {[n for n, _ in NIV_USUARIO]}")
print(f"\nPROBE -> {OUT}")
print(f"lineas: {lineas_antes} -> {len(s.splitlines())}")
