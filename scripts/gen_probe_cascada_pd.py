# -*- coding: utf-8 -*-
"""
S130 · PROBE v5 — cascada premium/discount ANIDADA desde D1 (mitades recursivas).

QUE MIDE. El diseno de S130 (docs/planes/DISENO-cascada-pd-anidada-S130.md):
  L0 = [min, max] de la ventana (= Opcion C literal, ya medida en S129: [0.90275, 1.60389])
  Lk+1 = la MITAD de Lk donde vive el precio:  close >= mid ? [mid, hi] : [lo, mid]
Cada nivel tiene su propio premium/discount, quieto en su tramo, que SALTA al tramo contiguo
cuando el precio se lo come. Requisito del usuario (S130): el macro D1 no rota => no es operable;
los TF menores necesitan un veredicto propio que SI rote.

LA CONSECUENCIA (escrita antes de medir, §3 del diseno). La cascada de mitades ES la expansion
BINARIA de pct: el veredicto del nivel k es el k-esimo bit de pct en base 2. Por tanto los niveles
NO tienen contenido estructural (son cortes aritmeticos, no swings de H1/M5) y el flapping alrededor
de cada 'mid' es el modo de fallo. P-G5 verifica la identidad binaria de forma independiente
(reconstruye pct desde los bits y lo compara con el pct directo).

PREDICCIONES (escritas ANTES de medir — van 9 vivas de 21; detalle en el doc §4):
  P-G1  (LA QUE DECIDE) L1 = [0.90275, 1.25332], amp ~3505.7 pips. La lectura H1 del usuario
        ([1.02175, 1.39970] = 3780 pips) coincide en AMPLITUD (<10%) pero NO en niveles (>1000 pips).
  P-G2  Anidamiento Lk+1 subconjunto de Lk en el 100% de las barras -> nNestViol = 0.
  P-G3  pct en [0,1] en TODOS los niveles -> nOutRange = 0.
  P-G4  Flapping monotono creciente hacia abajo: nFlip1 < nFlip3 < nFlip5.
  P-G5  Amplitudes = mitades exactas (L2 1752.9 / L3 876.4 / L4 438.2 / L5 219.1 / L6 109.6 pips);
        M5 (100-300 pips) cae en L5 o L6. Y errBin ~ 0 (identidad binaria).

ANTI-HUMO (S128/S129): P_nBars denominador explicito; P_tSeeded delata el arranque; contadores por
nivel separados; nada se lee en islast; P_close de control (data_get_study_values sigue el CROSSHAIR
-> mover el raton al borde derecho antes de leer); P_marker por build (unico distintivo fresco/rancio).
TRUNCADO en "// === DIBUJO ===" (CE10117 — el Visual completo + probe no cabe).

Uso:
  python scripts/gen_probe_cascada_pd.py
"""
import sys, os, pathlib

SRC = pathlib.Path(__file__).resolve().parent.parent / "pine" / "SMC-Visual.pine"
OUT = pathlib.Path(os.environ.get("TEMP", ".")) / "PROBE-cascada-pd-S130.pine"
MARKER = 1301
NIVELES = 6

s = SRC.read_text(encoding="utf-8")

for needed in ("f_premiumDiscount(float price, float top, float bottom, float eqLo, float eqHi) =>",
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

PROBE = f"""

// --- [S130 · PROBE v5: cascada P/D anidada — mitades recursivas desde el macro D1]
// L0 = min/max de la ventana (Opcion C literal, S129). Lk+1 = mitad de Lk donde vive el precio.
var float tHi     = na
var float tLo     = na
var int   tSeeded = 0
var int   nBars   = 0

// Estado por nivel: bordes, lado previo (para flapping) y contadores.
var float[] cLo      = array.new_float({NIVELES} + 1, na)
var float[] cHi      = array.new_float({NIVELES} + 1, na)
var int[]   prevSide = array.new_int({NIVELES} + 1, -1)
var int[]   nFlip    = array.new_int({NIVELES} + 1, 0)
var int[]   nNestV   = array.new_int({NIVELES} + 1, 0)
var int[]   nOutR    = array.new_int({NIVELES} + 1, 0)

float pdEqLo = 0.5 - i_pdEqBand / 100.0
float pdEqHi = 0.5 + i_pdEqBand / 100.0
float errBin = na

if barstate.isconfirmed
    nBars += 1
    // (1) L0 — el macro: min/max de la ventana. Identico a la Opcion C literal medida en S129.
    if na(tHi)
        tSeeded += 1
    if na(tHi) or high > tHi
        tHi := high
    if na(tLo)
        tSeeded += 1
    if na(tLo) or low < tLo
        tLo := low
    array.set(cLo, 0, tLo)
    array.set(cHi, 0, tHi)

    // (2) La cascada: cada nivel = la mitad del anterior donde vive el precio.
    float accBin = 0.0
    float accW   = 0.5
    for k = 0 to {NIVELES} - 1
        float lo = array.get(cLo, k)
        float hi = array.get(cHi, k)
        if not na(lo) and not na(hi) and hi > lo
            float mid  = (lo + hi) / 2.0
            bool  up   = close >= mid
            float nlo  = up ? mid : lo
            float nhi  = up ? hi  : mid
            array.set(cLo, k + 1, nlo)
            array.set(cHi, k + 1, nhi)
            // P-G2: anidamiento. Debe ser subconjunto estricto del padre, siempre.
            if nlo < lo or nhi > hi
                array.set(nNestV, k + 1, array.get(nNestV, k + 1) + 1)
            // P-G4: flapping — cuantas veces este nivel cambia de tramo.
            int side = up ? 1 : 0
            if array.get(prevSide, k + 1) != -1 and array.get(prevSide, k + 1) != side
                array.set(nFlip, k + 1, array.get(nFlip, k + 1) + 1)
            array.set(prevSide, k + 1, side)
            // P-G3: el invariante pct en [0,1] en cada nivel.
            if nhi > nlo
                float p = (close - nlo) / (nhi - nlo)
                if p < 0 or p > 1
                    array.set(nOutR, k + 1, array.get(nOutR, k + 1) + 1)
            // P-G5: identidad binaria — el veredicto del nivel k ES el bit k de pct.
            accBin += up ? accW : 0.0
            accW   := accW / 2.0
    // errBin: |pct reconstruido desde los bits - pct directo|. Debe ser < 2^-{NIVELES}.
    if not na(tHi) and not na(tLo) and tHi > tLo
        errBin := math.abs(accBin - (close - tLo) / (tHi - tLo))

f_amp(float hi, float lo) => (hi - lo) / syminfo.mintick / 10

[zL0, pctL0] = f_premiumDiscount(close, array.get(cHi, 0), array.get(cLo, 0), pdEqLo, pdEqHi)
[zL1, pctL1] = f_premiumDiscount(close, array.get(cHi, 1), array.get(cLo, 1), pdEqLo, pdEqHi)
[zL5, pctL5] = f_premiumDiscount(close, array.get(cHi, 5), array.get(cLo, 5), pdEqLo, pdEqHi)
[zA,  pctA ] = f_premiumDiscount(close, chartState.pdHigh, chartState.pdLow, pdEqLo, pdEqHi)

plot(nBars,   "P_nBars")
plot(tSeeded, "P_tSeeded")
plot(errBin,  "P_errBin")
plot(close,   "P_close")
plot({MARKER}, "P_marker")

// L0 = macro (control: debe reproducir la medida de S129).
plot(array.get(cLo, 0), "P_L0lo")
plot(array.get(cHi, 0), "P_L0hi")
plot(f_amp(array.get(cHi, 0), array.get(cLo, 0)), "P_L0amp")
plot(pctL0, "P_pctL0")

// L1 = el candidato a H1 (P-G1, la que decide).
plot(array.get(cLo, 1), "P_L1lo")
plot(array.get(cHi, 1), "P_L1hi")
plot(f_amp(array.get(cHi, 1), array.get(cLo, 1)), "P_L1amp")
plot(pctL1, "P_pctL1")
plot(zL1,   "P_zL1")

// Amplitudes de la cascada (P-G5: mitades exactas; M5 deberia caer en L5/L6).
plot(f_amp(array.get(cHi, 2), array.get(cLo, 2)), "P_L2amp")
plot(f_amp(array.get(cHi, 3), array.get(cLo, 3)), "P_L3amp")
plot(f_amp(array.get(cHi, 4), array.get(cLo, 4)), "P_L4amp")
plot(f_amp(array.get(cHi, 5), array.get(cLo, 5)), "P_L5amp")
plot(f_amp(array.get(cHi, 6), array.get(cLo, 6)), "P_L6amp")

// L5 = el candidato a M5.
plot(array.get(cLo, 5), "P_L5lo")
plot(array.get(cHi, 5), "P_L5hi")
plot(pctL5, "P_pctL5")

// P-G4: flapping por nivel (debe crecer hacia abajo).
plot(array.get(nFlip, 1), "P_nFlip1")
plot(array.get(nFlip, 3), "P_nFlip3")
plot(array.get(nFlip, 5), "P_nFlip5")

// P-G2 / P-G3: violaciones. Todas deben ser 0.
plot(array.get(nNestV, 1) + array.get(nNestV, 3) + array.get(nNestV, 5), "P_nNestViol")
plot(array.get(nOutR, 1) + array.get(nOutR, 3) + array.get(nOutR, 5), "P_nOutRange")

// Control: la Opcion A vigente, para contraste.
plot(pctA, "P_pctA")
"""

s = s + PROBE
OUT.write_text(s, encoding="utf-8")
print(f"Variante: cascada P/D anidada, {NIVELES} niveles (marker={MARKER})")
print(f"\nPROBE -> {OUT}")
print(f"lineas: {lineas_antes} -> {len(s.splitlines())}")
