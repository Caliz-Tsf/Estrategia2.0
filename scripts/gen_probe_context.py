#!/usr/bin/env python
# gen_probe_context.py — S109 · ESQUELETO-FABLE-context-htf-revelado.md Paso A2/A3.
# Genera PROBE-context-oom.pine desde el HEAD de pine/SMC-Visual.pine: CORE verbatim
# (seccion // === LIBRARY CORE ===) + 2 request.security D1/H1 con motor completo
# (dummy de f_tfExtremes = f_computeTFState, mismo perfil de memoria) + plots checksum.
# El .pine generado NO se commitea (es probe de de-riesgo, se aplica en tab sin slot).
# Validado por Fable S109: el output (1715 lineas) compila 0/0 server-side.
# Uso: python scripts/gen_probe_context.py [salida.pine]
import sys, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "pine", "SMC-Visual.pine")
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "PROBE-context-oom.pine")

src = open(SRC, encoding="utf-8").read().splitlines()

# Localizar CORE por MARCADOR (no por numero de linea): desde '// === LIBRARY CORE ==='
# (inclusive) hasta el siguiente encabezado '// === ... ===' (exclusive).
sec = re.compile(r"^\s*//\s*===\s*.+?\s*===\s*$")
start = next(i for i, l in enumerate(src) if re.match(r"^\s*//\s*===\s*LIBRARY\s+CORE\s*===\s*$", l))
end = next((j for j in range(start + 1, len(src)) if sec.match(src[j])), len(src))
core = src[start:end]

def fields(p):
    scal = [f"{p}_bias", f"{p}_bosP", f"{p}_bosD", f"{p}_bosT", f"{p}_chP", f"{p}_chD", f"{p}_chT",
            f"{p}_mssP", f"{p}_mssD", f"{p}_mssT", f"{p}_pdH", f"{p}_pdL", f"{p}_pdM",
            f"{p}_e20", f"{p}_e50", f"{p}_e200", f"{p}_atr"]
    slots = []
    for s in range(12):
        slots += [f"{p}_k{s}", f"{p}_t{s}", f"{p}_b{s}", f"{p}_d{s}", f"{p}_ta{s}", f"{p}_tb{s}"]
    return scal + slots

# Literales = defaults de los inputs del Visual (swingLen 5, pdSwingLen 50, disp 1.5, body 0.70,
# eqlLen 3, eqThr 0.1, obVol 2.0, obMitClose false, fvgThr 0.25, poolTol 0.1, minTouches 2,
# caps OB2/FVG2/Pool2/Sweep2/EQ2/BOS1/CHoCH1).
ARGS = "5, 50, 1.5, 0.70, 3, 0.1, 2.0, false, 0.25, 0.1, 2, 2, 2, 2, 2, 2, 1, 1"

def call(p, tf):
    return (f'[{", ".join(fields(p))}] = request.security(syminfo.tickerid, "{tf}", '
            f"f_computeTFState({ARGS}), lookahead = barmerge.lookahead_off)")

hdr = ["// PROBE-A2A3 · Estrategia 2.0 · S109 — de-riesgo OOM 2a llamada MTF. NO producto, NO commit.",
       "//@version=6", 'indicator("PROBE Context OOM", overlay = true)', ""]
tail = ["", "// === PROBE · 2 security calls D1/H1 con motor completo (proxy de SMC-Context) ===",
        call("d1", "D"), call("h1", "60"),
        'plot(d1_pdH, "d1 pdHigh", color = color.new(color.blue, 60))',
        'plot(h1_pdH, "h1 pdHigh", color = color.new(color.orange, 60))',
        'plotchar(d1_bias + h1_bias + d1_k0 + h1_k0 + d1_d0 + h1_d0, "chk_int", "", location.top)',
        'plotchar(d1_t0 + h1_t0 + d1_b0 + h1_b0 + d1_atr + h1_atr, "chk_f", "", location.top)']

out = "\n".join(hdr + core + tail) + "\n"
open(OUT, "w", encoding="utf-8", newline="\n").write(out)
print(f"OK: {out.count(chr(10))} lineas -> {OUT}")
print("Siguiente: python scripts/pine_check.py <salida> (esperar 0/0), luego pine_new + inject + Ctrl+Enter.")
