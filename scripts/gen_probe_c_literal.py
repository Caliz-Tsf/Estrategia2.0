# -*- coding: utf-8 -*-
"""
S129 · PROBE v4 — la Opcion C LITERAL (conservando f_updateTrailing), vs la variante que se midio antes.

POR QUE ESTE PROBE. El diseno de S128 (§3) se CONTRADICE:
  - su pseudocodigo dice "strongHigh: se queda"                    -> SIN expansion
  - su texto dice "Lo unico que cambia es CUANDO se llama al reset" -> f_updateTrailing SE CONSERVA
Los probes v1/v2/v3 implementaron la PRIMERA lectura (sticky sobre pivotes + latch). Esta mide la SEGUNDA.

LA CONSECUENCIA (a verificar, no a asumir). Si la expansion se conserva, entonces top >= high >= close
por construccion => "close > top" es IMPOSIBLE => la violacion NUNCA se dispara => el lado alto no
reancla jamas => top = MAXIMO ABSOLUTO de la ventana. Idem bottom = minimo absoluto. Es decir: la
Opcion C literal no es "pegajoso hasta ser violado" sino, simplemente, EL EXTREMO DE LA VENTANA sobre
precios crudos — sin latch, sin semilla, y con i_pdSwingLen VOLVIENDOSE IRRELEVANTE (el reset no corre).

PREDICCIONES (escritas ANTES de medir — van 7 vivas de 18):
  P-F1  D1 EURUSD: tHi/tLo = [0.95360, 1.60554] EXACTO = las lineas del usuario (la variante con latch
        daba 1.60195, 36 pips corta). FALSA si difiere > 1 pip.
  P-F2  nHiReset = 0 y nLoReset = 0 en toda la historia => la violacion no se dispara nunca =>
        i_pdSwingLen es IRRELEVANTE para el rango. FALSA si algun reset > 0.
  P-F3  pct SIEMPRE en [0,1] (el invariante que la variante con latch rompia: pctC=1.1 en NAS100USD).
        Se mide con nOutOfRange sobre historia confirmada. FALSA si nOutOfRange > 0.

ANTI-HUMO: P_nBars denominador explicito; P_tSeeded delata el arranque; contadores por lado separados.
TRUNCADO en "// === DIBUJO ===" (CE10117). Verificar P_marker=1294 y que P_close ~= precio real
(gotcha S126: data_get_study_values sigue el CROSSHAIR -> mover el raton al borde derecho antes de leer).

Uso:
  python scripts/gen_probe_c_literal.py
"""
import sys, os, pathlib

SRC = pathlib.Path(__file__).resolve().parent.parent / "pine" / "SMC-Visual.pine"
OUT = pathlib.Path(os.environ.get("TEMP", ".")) / "PROBE-c-literal-S129.pine"
MARKER = 1294

s = SRC.read_text(encoding="utf-8")
orig_len = len(s)

for needed in ("[pdSwingHigh, pdSwingLow] = f_detectSwings(i_pdSwingLen)",
               "f_premiumDiscount(float price, float top, float bottom, float eqLo, float eqHi) =>"):
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

PROBE = f"""

// --- [S129 · PROBE v4: Opcion C LITERAL — reset solo tras violacion + expansion CONSERVADA]
var float tHi      = na
var float tLo      = na
var int   tSeeded  = 0
var int   nHiReset = 0
var int   nLoReset = 0
var int   nBars    = 0
var int   nOutOfRange = 0

float pdEqLo = 0.5 - i_pdEqBand / 100.0
float pdEqHi = 0.5 + i_pdEqBand / 100.0

if barstate.isconfirmed
    nBars += 1
    // (1) RESET solo tras violacion — el unico cambio que el diseno §3 dice hacer sobre la Opcion A.
    if not na(tHi) and close > tHi and not na(pdSwingHigh)
        tHi      := pdSwingHigh
        nHiReset += 1
    if not na(tLo) and close < tLo and not na(pdSwingLow)
        tLo      := pdSwingLow
        nLoReset += 1
    // (2) EXPANSION — f_updateTrailing tal cual (LuxAlgo updateTrailingExtremes), CONSERVADA.
    if na(tHi)
        tSeeded += 1
    if na(tHi) or high > tHi
        tHi := high
    if na(tLo)
        tSeeded += 1
    if na(tLo) or low < tLo
        tLo := low
    // (3) P-F3: el invariante pct en [0,1].
    if not na(tHi) and not na(tLo) and tHi > tLo
        float p = (close - tLo) / (tHi - tLo)
        if p < 0 or p > 1
            nOutOfRange += 1

[zC, pctC] = f_premiumDiscount(close, tHi, tLo, pdEqLo, pdEqHi)
[zA, pctA] = f_premiumDiscount(close, chartState.pdHigh, chartState.pdLow, pdEqLo, pdEqHi)

plot(nBars,       "P_nBars")
plot(tSeeded,     "P_tSeeded")
plot(tHi,         "P_tHi")
plot(tLo,         "P_tLo")
plot(nHiReset,    "P_nHiReset")
plot(nLoReset,    "P_nLoReset")
plot(nOutOfRange, "P_nOutOfRange")
plot(pctC,        "P_pctC")
plot(pctA,        "P_pctA")
plot((tHi - tLo) / syminfo.mintick / 10, "P_ampC")
plot(chartState.pdHigh, "P_pdHigh")
plot(chartState.pdLow,  "P_pdLow")
plot(close,       "P_close")
plot({MARKER},    "P_marker")
"""

s = s + PROBE
OUT.write_text(s, encoding="utf-8")
print(f"Variante: Opcion C LITERAL (expansion conservada; marker={MARKER})")
print(f"\nPROBE -> {OUT}")
print(f"lineas: {lineas_antes} -> {len(s.splitlines())}")
