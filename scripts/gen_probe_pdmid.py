# -*- coding: utf-8 -*-
"""
S135 · PROBE v15 — VERIFICACION EN VIVO DEL FIX DE `chartState.pdMid` (commit 5094d2a)

QUE VERIFICA. El bloque chart-TF (:2193-2199) asignaba pdLow/pdHigh pero NUNCA pdMid, que quedaba en
su default `na` (:296). Las lecturas de :2745/:2746 (f_wickNearLevel, Rejection §2.7) recibian ese `na`
=> el nivel EQ nunca participaba en la confluencia de mecha. Muerto desde el Sprint 1.5 (5bc4828).

El fix anade la asignacion. Este probe mide DOS cosas, en el MISMO punto del script (no al final:
las zonas/pools cambian de estado mas abajo y una lectura al final no seria apples-to-apples):

  (a) que pdMid ya NO es `na` y vale exactamente (pdHigh + pdLow)/2
  (b) A/B REAL: f_wickNearLevel con pdMid (fix) vs con `na` (el bug), contando en cuantas barras
      DIFIEREN. Esto mide el impacto del fallo silencioso, no solo que la variable este poblada.

OJO AL CORTOCIRCUITO (leido en :951-975): f_wickNearLevel comprueba zonas -> pools -> EQH/EQL -> P/D
-> EMAs, con `break`. El nivel EQ es la 4.ª comprobacion => solo puede cambiar el resultado cuando
NINGUN otro nivel esta cerca. El impacto esperado es por tanto BAJO, y eso es justo lo que P3 fija.

PREDICCIONES (escritas ANTES de medir — norma S114/S132):

  P1  pdMid NO es `na` en la ultima barra y vale (pdHigh + pdLow)/2 al 5.º decimal.
      FALSA si sale `na` => el fix no aplica donde se creia.
      [FACIL: es un cross-check del arnes, no discrimina. Declarada facil de antemano.]

  P2  *** LA QUE DECIDE *** nDiffLow + nDiffHigh > 0 en la historia del TF.
      FALSA si es 0 => pdMid SIEMPRE queda tapado por otro nivel => el fallo silencioso era
      INOCUO y el fix no compra nada. Seria un hallazgo honesto y hay que reportarlo como tal.

  P3  El impacto es BAJO: (nDiffLow + nDiffHigh) / nBars < 5%.
      FALSA si > 15% => mi modelo del cortocircuito esta mal y el EQ pesa mucho mas de lo previsto.

  P4  nRejDiff >= 1: al menos UNA rejection real (evRej no-na) cambia de veredicto por el fix.
      FALSA si 0 => pdMid difiere en el ancla pero nunca en una barra que ademas cumpla la
      geometria de rechazo => el fix es correcto pero inerte en la practica.

ANTI-HUMO (leccion S128: contadores con guard `not na()` miden humo):
  - P_nBars: denominador explicito.
  - P_nMidNa: en cuantas barras confirmadas pdMid seguia `na` (debe ser 0 tras el fix; si sale
    igual a nBars, el fix NO esta en el build que se esta leyendo => marker rancio).
  - P_nRejTotal: cuantas rejections detecta en total (si es 0, P4 es trivial y no prueba nada).
  - P_marker fresco verificado en CADA lectura (gotcha S129/S133: lecturas rancias sin avisar).

GOTCHAS aplicados (memoria del proyecto):
  - Volcado por `label` en `islast`: data_get_study_values SIGUE EL CROSSHAIR (casi arruina S133).
  - pine_inject.py solo GUARDA (y su clic busca botones en INGLES; el TV esta en ESPANOL) =>
    el apply real es remove + inject + clic en PLAY + confirmar "Anadido al grafico" en consola.
  - Leer desde chart M5 (ADR-023): es el TF donde la Rejection importa para la Strategy.
"""
import os, pathlib, sys

MARKER = 1350
SRC = pathlib.Path(__file__).resolve().parent.parent / "pine" / "SMC-Visual.pine"
OUT = pathlib.Path(os.environ.get("TEMP", ".")) / f"PROBE-pdmid-S135.pine"

s = SRC.read_text(encoding="utf-8")

# --- anclas: deben existir exactamente 1 vez, si no el probe midio otra cosa ---
ANCLA_VAR = "var array<SMC_Event> SMC_rejections = array.new<SMC_Event>()"
ANCLA_REJ = "    evRej := f_detectRejection(open, high, low, close, i_rejWickFactor, rejNearLow, rejNearHigh, bar_index, time)"
ANCLA_FIX = "    chartState.pdMid  := na(chartState.pdHigh) or na(chartState.pdLow) ? na : (chartState.pdHigh + chartState.pdLow) / 2.0"

for ancla in (ANCLA_VAR, ANCLA_REJ, ANCLA_FIX):
    if s.count(ancla) != 1:
        print(f"[FALLO] ancla no unica ({s.count(ancla)}x): {ancla!r}")
        sys.exit(1)
print("[OK] 3 anclas unicas — incluida la linea del fix (si falta, el repo no tiene el commit 5094d2a)")

MARK = "// === DIBUJO ==="
if s.count(MARK) != 1:
    print(f"[FALLO] marcador de truncado no unico: {s.count(MARK)}")
    sys.exit(1)

# --- contadores, justo antes del bloque de Rejection ---
CONTADORES = """// --- [S135 · PROBE v15: A/B del fix de pdMid] ---
var int P_nBars     = 0
var int P_nMidNa    = 0
var int P_nDiffLow  = 0
var int P_nDiffHigh = 0
var int P_nRejTotal = 0
var int P_nRejDiff  = 0
""" + ANCLA_VAR
s = s.replace(ANCLA_VAR, CONTADORES)

# --- A/B en el MISMO punto: mismo tol, mismos arrays, mismo estado ---
AB = ANCLA_REJ + """
    // [S135 · PROBE v15] variante BUG: identica salvo que pdMid entra como `na` (el default de :296)
    bool bugNearLow  = f_wickNearLevel(low,  SMC_zones, SMC_pools, SMC_eqhl, chartState.pdHigh, chartState.pdLow, na, emaFast, emaMid, emaSlow, rejTol)
    bool bugNearHigh = f_wickNearLevel(high, SMC_zones, SMC_pools, SMC_eqhl, chartState.pdHigh, chartState.pdLow, na, emaFast, emaMid, emaSlow, rejTol)
    SMC_Event bugRej = f_detectRejection(open, high, low, close, i_rejWickFactor, bugNearLow, bugNearHigh, bar_index, time)
    P_nBars     += 1
    P_nMidNa    += na(chartState.pdMid) ? 1 : 0
    P_nDiffLow  += rejNearLow  != bugNearLow  ? 1 : 0
    P_nDiffHigh += rejNearHigh != bugNearHigh ? 1 : 0
    P_nRejTotal += na(evRej) ? 0 : 1
    P_nRejDiff  += na(evRej) != na(bugRej) ? 1 : 0"""
s = s.replace(ANCLA_REJ, AB)

# --- truncar el render (ahorra tokens: el CE10117 no tiene headroom) ---
lineas_antes = len(s.splitlines())
s = s[:s.index(MARK)]
print(f"[truncado] render eliminado en {MARK!r}: {lineas_antes} -> {len(s.splitlines())} lineas")

VOLCADO = f"""

// --- [S135 · PROBE v15] VOLCADO EN islast POR LABEL.
// data_get_study_values SIGUE EL CROSSHAIR y devuelve la barra equivocada (gotcha S133, casi
// arruina la sesion). data_get_pine_labels NO lo sigue => es el canal fiable para el veredicto.
if barstate.islast
    float midEsperado = na(chartState.pdHigh) or na(chartState.pdLow) ? na : (chartState.pdHigh + chartState.pdLow) / 2.0
    string d = "== PROBE {MARKER} · pdMid · " + syminfo.ticker + " " + timeframe.period + " ==\\n"
    d += "pdHigh=" + str.tostring(chartState.pdHigh, "#.#####") + "  pdLow=" + str.tostring(chartState.pdLow, "#.#####") + "\\n"
    d += "pdMid ="  + str.tostring(chartState.pdMid, "#.#####") + "  esperado=" + str.tostring(midEsperado, "#.#####") + "   <-- P1\\n"
    d += "nBars=" + str.tostring(P_nBars) + "  nMidNa=" + str.tostring(P_nMidNa) + "  (nMidNa>0 => el fix no esta en este build)\\n"
    d += "nDiffLow=" + str.tostring(P_nDiffLow) + "  nDiffHigh=" + str.tostring(P_nDiffHigh) + "   <-- P2: suma > 0 ?\\n"
    d += "impacto=" + str.tostring(P_nBars == 0 ? na : (P_nDiffLow + P_nDiffHigh) * 100.0 / P_nBars, "#.##") + "%   <-- P3: < 5 ?\\n"
    d += "nRejTotal=" + str.tostring(P_nRejTotal) + "  nRejDiff=" + str.tostring(P_nRejDiff) + "   <-- P4: >= 1 ?"
    label.new(bar_index, close, d, style = label.style_label_left, textcolor = color.white, size = size.small)
"""

s = s + VOLCADO
OUT.write_text(s, encoding="utf-8")
print(f"\nPROBE -> {OUT}   (marker={MARKER})")
print("P1: pdMid == esperado, no na  |  *** P2 (LA QUE DECIDE): nDiffLow+nDiffHigh > 0 ***")
print("P3: impacto < 5%  |  P4: nRejDiff >= 1")
