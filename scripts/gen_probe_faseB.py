#!/usr/bin/env python
# gen_probe_faseB.py - S114 - GATE B (probe de token/OOM antes de romper el SHA).
# Simula un SMC-Strategy.pine POST-Fase-B: CORE de Strategy (verbatim, marcador
# // === LIBRARY CORE ===) + las funciones de extremos que Fase B promueve
# (f_farthestZone/Pool/Event + f_tfExtremes, extraidas de SMC-Context.pine) +
# 4 request.security en UN solo script: 2 nearest (f_computeTFState D1/H1, como hoy)
# + 2 extremos (f_tfExtremes D1/H1, lo nuevo). Plots de checksum para probar que los
# 4 tuples pueblan. Aisla el unico riesgo nuevo de B2: 4 securities en un Strategy.
#
# El .pine generado NO se commitea (probe de de-riesgo; se aplica en tab sin slot).
# Criterio de paso: pine_check 0/0 + apply en TV sin CE10117 ni OOM + checksums no-na.
# Uso: python scripts/gen_probe_faseB.py [salida.pine]
import sys, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_CORE = os.path.join(ROOT, "pine", "SMC-Strategy.pine")   # CORE real de Strategy
SRC_EXT  = os.path.join(ROOT, "pine", "SMC-Context.pine")    # funciones de extremos a promover
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "PROBE-faseB-oom.pine")

sec = re.compile(r"^\s*//\s*===\s*.+?\s*===\s*$")

def extract(path, start_re, count_headers=1):
    """Devuelve el bloque desde la 1a linea que casa start_re (inclusive) hasta la
    (count_headers)-esima cabecera '// === ... ===' posterior (exclusive)."""
    lines = open(path, encoding="utf-8").read().splitlines()
    start = next(i for i, l in enumerate(lines) if re.match(start_re, l))
    seen, end = 0, len(lines)
    for j in range(start + 1, len(lines)):
        if sec.match(lines[j]):
            seen += 1
            if seen == count_headers:
                end = j
                break
    return lines[start:end]

# 1) CORE de Strategy (marcador a marcador)
core = extract(SRC_CORE, r"^\s*//\s*===\s*LIBRARY\s+CORE\s*===\s*$")

# 2) Funciones de extremos desde Context: seccion "=== EXTREMOS HTF (fuera del CORE) ==="
#    hasta la cabecera "=== CALL-SITES ...". Contiene f_farthestZone/Pool/Event + f_tfExtremes.
ext = extract(SRC_EXT, r"^\s*//\s*===\s*EXTREMOS\s+HTF.*===\s*$")

# --- nearest-N (f_computeTFState): 89 campos ---
def near_fields(p):
    scal = [f"{p}_bias", f"{p}_bosP", f"{p}_bosD", f"{p}_bosT", f"{p}_chP", f"{p}_chD", f"{p}_chT",
            f"{p}_mssP", f"{p}_mssD", f"{p}_mssT", f"{p}_pdH", f"{p}_pdL", f"{p}_pdM",
            f"{p}_e20", f"{p}_e50", f"{p}_e200", f"{p}_atr"]
    slots = []
    for s in range(12):
        slots += [f"{p}_k{s}", f"{p}_t{s}", f"{p}_b{s}", f"{p}_d{s}", f"{p}_ta{s}", f"{p}_tb{s}"]
    return scal + slots

# defaults Strategy (mismos que Visual): caps OB2/FVG2/Pool2/Sweep2/EQ2/BOS1/CHoCH1
NEAR_ARGS = "5, 50, 1.5, 0.70, 3, 0.1, 2.0, false, 0.25, 0.1, 2, 2, 2, 2, 2, 2, 1, 1"

def near_call(p, tf):
    return (f'[{", ".join(near_fields(p))}] = request.security(syminfo.tickerid, "{tf}", '
            f"f_computeTFState({NEAR_ARGS}), lookahead = barmerge.lookahead_off)")

# --- extremos (f_tfExtremes): 51 campos = 3 escalares + 8 slots x 6 ---
def ext_fields(p):
    out = [f"{p}_pdH", f"{p}_pdL", f"{p}_atr"]
    for s in range(8):
        out += [f"{p}_ek{s}", f"{p}_et{s}", f"{p}_eb{s}", f"{p}_ed{s}", f"{p}_ea{s}", f"{p}_etb{s}"]
    return out

# defaults Context: kExt 6.0, extMinStrength 0.5, ctxMitigated false
EXT_ARGS = "5, 50, 1.5, 0.70, 3, 0.1, 2.0, false, 0.25, 0.1, 2, 6.0, 0.5, false"

def ext_call(p, tf):
    return (f'[{", ".join(ext_fields(p))}] = request.security(syminfo.tickerid, "{tf}", '
            f"f_tfExtremes({EXT_ARGS}), lookahead = barmerge.lookahead_off)")

hdr = ["// PROBE-faseB · Estrategia 2.0 · S114 — GATE B: 4 request.security (2 nearest + 2 extremos)",
       "// en un solo Strategy. NO producto, NO commit. Aisla token/OOM de la promocion Fase B.",
       "//@version=6", 'indicator("PROBE FaseB OOM", overlay = true)', ""]

tail = ["", "// === PROBE · 4 security calls: 2 nearest (hoy) + 2 extremos (Fase B) ===",
        near_call("d1", "D"), near_call("h1", "60"),
        ext_call("xd1", "D"), ext_call("xh1", "60"),
        "",
        'plot(d1_pdH, "d1 pdHigh", color = color.new(color.blue, 60))',
        'plot(xd1_pdH, "xd1 pdHigh", color = color.new(color.teal, 60))',
        '// checksum nearest (89x2) — debe ser no-na si el nearest viaja',
        'plotchar(d1_bias + h1_bias + d1_k0 + h1_k0 + d1_t0 + h1_t0, "chk_near", "", location.top)',
        '// checksum extremos (51x2) — debe ser no-na si los extremos viajan',
        'plotchar(xd1_ek0 + xh1_ek0 + xd1_et0 + xh1_et0 + xd1_atr + xh1_atr, "chk_ext", "", location.bottom)']

out = "\n".join(hdr + core + [""] + ext + tail) + "\n"
open(OUT, "w", encoding="utf-8", newline="\n").write(out)
n = out.count("\n")
print(f"OK: {n} lineas -> {OUT}")
print("Nearest fields/call: 89 | Extremos fields/call: 51 | 4 securities (2+2).")
print("Siguiente: python scripts/pine_check.py <salida> (esperar 0/0), luego pine_inject + Ctrl+Enter en tab sin slot; esperar ~20s; pine_get_errors (CE10117 solo aparece en apply).")
