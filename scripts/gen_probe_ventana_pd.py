# -*- coding: utf-8 -*-
"""
S133 · PROBE v15 — BARRIDO DE LA VENTANA del 2.º extremo (§2.3.2). Elige el default de `pdWindow`.

POR QUE. El gate de la Fase 1 paso, pero al releer NAS100 con datos frescos (el usuario mando una captura
que no cuadraba) aparecio el limite: en D1 con ~24 anos de feed, el 2.º extremo del lado que el precio
nunca vuelve a visitar SE FOSILIZA en el arranque -> pdLow=1021.1 (de 2001) -> premium 95.8% clavado ->
NO OPERABLE. H1 no lo sufre SOLO porque su feed llega 1.5 anos atras => la ventana ya actuaba de hecho,
sin declararse. Decision del usuario (S133): VENTANA DECLARADA POR INPUT.

3 VENTANAS A LA VEZ, un solo apply (patron del barrido de S132): 500 / 1000 / 2000 velas del TF.

METODO. Los strong lows/highs se acumulan con su bar_index en arrays (son POCOS: 23 y 18 en 6284 barras
de EURUSD D1). min1/min2 por ventana = escaneo de los que caen dentro. ~30 elementos x 3 ventanas = barato.
El array.push va en barras CONFIRMADAS, no en islast (el RE10045 conocido es de islast).

PREDICCIONES (escritas ANTES de medir. Acumulado S133: 8 vivas de 17):
  P-V1  NAS100 D1 con W=1000: pdLow SUBE de 1021.1 a un nivel reciente (> 10000) => el rango se hace
        operable (pct deja de estar clavado en 0.958). FALSA si sigue < 10000.
  P-V2  EURUSD D1 con W=1000: pdLow SIGUE siendo 0.95360 +-20 pips => la ventana no rompe lo que ya
        funcionaba. FALSA si cambia. *** OJO: es JUSTO — ese pool tiene edad 984 y la ventana es 1000:
        16 velas de margen. Si sale verde, hay que decir que es FRAGIL, no celebrarlo. ***
  P-V3  *** LA QUE DECIDE *** Existe UNA ventana (de las 3) que cumple P-V1 y P-V2 A LA VEZ.
        FALSA si ninguna las cumple juntas => la ventana no puede ser un default unico y habria que
        declararla por simbolo (lo cual roza ADR-001: seria un perfil por-simbolo, no una rama).
  P-V4  EURUSD D1 con W=500: pdLow YA NO es 0.95360 (edad 984 > 500 => sale de la ventana).
        FALSA si sigue saliendo 0.95360 => el escaneo por ventana no esta filtrando (anti-humo del arnes).

ANTI-HUMO: P_nSlAll/P_nShAll = cuantos strong se acumularon en total (si 0, todo lo demas es humo);
P_nSlW* = cuantos caen DENTRO de cada ventana (si nSlW500 == nSlAll, la ventana no filtra -> arnes roto);
volcado por label en islast (data_get_pine_labels NO sigue el crosshair — el gotcha que ya invalido una
lectura de NAS100 en esta misma sesion); P_marker.

Uso:
  python scripts/gen_probe_ventana_pd.py
"""
import sys, os, pathlib

SRC = pathlib.Path(__file__).resolve().parent.parent / "pine" / "SMC-Visual.pine"
OUT = pathlib.Path(os.environ.get("TEMP", ".")) / "PROBE-ventana-pd-S133.pine"
MARKER = 1350
VENTANAS = (500, 1000, 2000)

s = SRC.read_text(encoding="utf-8")

NEEDED = (
    "evStructMajor := f_detectStructure(structMajor, bar_index, time, true, true)",
    "f_premiumDiscount(float price, float top, float bottom, float eqLo, float eqHi) =>",
    "var SMC_Trailing trailing = SMC_Trailing.new()",
)
for needed in NEEDED:
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

# Un bloque de lectura por ventana. min1/min2/max1/max2 por escaneo de los strong DENTRO de la ventana.
bloques = []
for W in VENTANAS:
    bloques.append(f"""
    // --- ventana {W}
    float lo1_{W} = na
    float lo2_{W} = na
    int   nlo_{W} = 0
    if array.size(slLvl) > 0
        for i = 0 to array.size(slLvl) - 1
            if bar_index - array.get(slBar, i) <= {W}
                nlo_{W} += 1
                float v = array.get(slLvl, i)
                if na(lo1_{W}) or v < lo1_{W}
                    lo2_{W} := lo1_{W}
                    lo1_{W} := v
                else if na(lo2_{W}) or v < lo2_{W}
                    lo2_{W} := v
    float hi1_{W} = na
    float hi2_{W} = na
    int   nhi_{W} = 0
    if array.size(shLvl) > 0
        for i = 0 to array.size(shLvl) - 1
            if bar_index - array.get(shBar, i) <= {W}
                nhi_{W} += 1
                float v = array.get(shLvl, i)
                if na(hi1_{W}) or v > hi1_{W}
                    hi2_{W} := hi1_{W}
                    hi1_{W} := v
                else if na(hi2_{W}) or v > hi2_{W}
                    hi2_{W} := v
    float sLo_{W} = na(lo2_{W}) ? trailing.bottom : close >= lo2_{W} ? lo2_{W} : close >= lo1_{W} ? lo1_{W} : trailing.bottom
    float sHi_{W} = na(hi2_{W}) ? trailing.top    : close <= hi2_{W} ? hi2_{W} : close <= hi1_{W} ? hi1_{W} : trailing.top
    [z_{W}, pct_{W}] = f_premiumDiscount(close, sHi_{W}, sLo_{W}, pdEqLo, pdEqHi)
    d += "W={W}: nLo=" + str.tostring(nlo_{W}) + " nHi=" + str.tostring(nhi_{W}) + "  histLo=" + str.tostring(lo1_{W}, "#.#####") + " pdLo=" + str.tostring(lo2_{W}, "#.#####") + "  histHi=" + str.tostring(hi1_{W}, "#.#####") + " pdHi=" + str.tostring(hi2_{W}, "#.#####") + "\\n"
    d += "      RANGO=[" + str.tostring(sLo_{W}, "#.#####") + ", " + str.tostring(sHi_{W}, "#.#####") + "]  pct=" + str.tostring(pct_{W}, "#.####") + "\\n"
""")

PROBE = f"""

// --- [S133 · PROBE v15: BARRIDO DE LA VENTANA del 2.º extremo — EN SOMBRA]
var array<float> slLvl = array.new<float>()   // strong lows  (nivel)
var array<int>   slBar = array.new<int>()     // strong lows  (bar_index del origen de la pierna)
var array<float> shLvl = array.new<float>()
var array<int>   shBar = array.new<int>()
var float rMin = na
var float rMax = na
var int   rMinBar = na
var int   rMaxBar = na

float pdEqLo = 0.5 - i_pdEqBand / 100.0
float pdEqHi = 0.5 + i_pdEqBand / 100.0

if barstate.isconfirmed
    // §2.3.1 — trackers del origen de pierna (guardan tambien la barra, para la ventana).
    if na(rMin) or low < rMin
        rMin    := low
        rMinBar := bar_index
    if na(rMax) or high > rMax
        rMax    := high
        rMaxBar := bar_index
    // §2.3.1 — un strong nace SOLO cuando la pierna que empezo en el rompio estructura.
    if not na(evStructMajor) and (evStructMajor.kind == KIND_BOS or evStructMajor.kind == KIND_CHOCH)
        if evStructMajor.dir == DIR_BULL
            array.push(slLvl, rMin)
            array.push(slBar, rMinBar)
            rMin    := low
            rMinBar := bar_index
        else
            array.push(shLvl, rMax)
            array.push(shBar, rMaxBar)
            rMax    := high
            rMaxBar := bar_index

// --- VOLCADO. data_get_pine_labels NO sigue el crosshair (el gotcha que ya invalido una lectura
// de NAS100 en esta misma sesion). Este es el canal fiable para el veredicto.
if barstate.islast
    string d = "== PROBE {MARKER} · " + syminfo.ticker + " " + timeframe.period + " ==\\n"
    d += "close=" + str.tostring(close, "#.#####") + "  nBars=" + str.tostring(bar_index) + "\\n"
    d += "strong acumulados: lo=" + str.tostring(array.size(slLvl)) + " hi=" + str.tostring(array.size(shLvl)) + "\\n"
{"".join(bloques)}
    label.new(bar_index, close, d, style = label.style_label_left, textcolor = color.white, size = size.small)

plot(array.size(slLvl), "P_nSlAll")
plot(array.size(shLvl), "P_nShAll")
plot(close,   "P_close")
plot({MARKER}, "P_marker")
"""

s = s + PROBE
OUT.write_text(s, encoding="utf-8")
print(f"Variante: BARRIDO DE VENTANA {VENTANAS} del 2.º extremo, EN SOMBRA")
print("P-V3 (LA QUE DECIDE): existe UNA ventana que hace NAS100 operable Y conserva 0.95360 en EURUSD")
print(f"\nPROBE -> {OUT}   (marker={MARKER})")
print(f"lineas: {lineas_antes} -> {len(s.splitlines())}")
