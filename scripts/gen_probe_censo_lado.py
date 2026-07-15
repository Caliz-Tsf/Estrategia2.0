# -*- coding: utf-8 -*-
"""
S127 · Genera un PROBE que CENSA las zonas de SMC_zones por (concepto x lado x estado x banda)
a partir de pine/SMC-Visual.pine SIN tocar el original.

Por que: el usuario pide decidir "cuantos por concepto/familia/variante por lado". Esa decision
necesita saber QUE HAY, no que se dibuja. Alternativa descartada: apagar conceptos uno por uno y
mirar -> S116 probo que ~40 recalculos sucesivos generan churn y dejan el estudio en estado roto
pegajoso; ademas cada apply crea instancia nueva y pierde el override de Densidad. El censo
numerico gana a la inspeccion visual (S123).

Hoy cada concepto muere en un sitio distinto (leido en codigo, S127):
  - OB/FVG/BRK/IDM -> band-pick, 2 slots por (concepto x lado x banda)   [disciplinados]
  - IFVG           -> solo f_densOK (en Operacion exige strength nivel 2) [sin lado ni cap]
  - BPR            -> solo bprCfg>=2 en Operacion (f_famOK(FAM_EST) es false) [sin lado ni cap]
  - MB/MITIGATION  -> promocion por confluencia SIN cap  [inunda, e IGNORA la banda]
Ademas 'elig' (L3371) excluye ZS_MITIGATED del band-pick -> una zona ya tocada deja de contar.

Este probe NO cambia ningun gate: solo CUENTA. Por concepto y lado distingue:
  - viva EN banda      (state != INVALID/MITIGATED, banda 1..i_profundidad) = lo que el embudo ve
  - viva FUERA de banda (banda 0) = existe y es invisible por regla de banda
  - mitigada EN banda  = la excluye 'elig'; si aqui hay numeros, el arreglo es dejarlas degradadas
  - contiene el precio = BUG DE DISENO S126: 'above' y 'below' son ambos false -> se cae del embudo

TRUNCADO EN "// === DIBUJO ===" (OBLIGATORIO, no es una optimizacion): el Visual esta pegado al
techo de tokens (S125 midio que +345 no cabian) -> un probe que anada bucle + plots ENCIMA del
Visual completo da CE10117 y no mide nada. El censo NO necesita dibujar: cuenta leyendo SMC_zones,
que puebla el CORE de deteccion. Todo lo que usa (f_depthBand, f_computeLegExtremes, el band-pick,
i_profundidad, KIND_*/ZS_*) vive ANTES del marcador; lo que se tira es solo render.
CONTRAPARTIDA: el chart queda EN BLANCO mientras el probe esta aplicado. Es esperado, no un fallo.

Marcador de identidad: probe_marker (ver [[tv-lecturas-rancias-y-apply-en-espanol]]) -- si no
aparece en data_get_study_values, la lectura es de un build VIEJO. El chart va 1-2 builds atras y
NO avisa; en S127 casi invierte la conclusion del fix de legext.

Uso:
  python scripts/gen_probe_censo_lado.py
"""
import sys, os, pathlib

SRC = pathlib.Path(__file__).resolve().parent.parent / "pine" / "SMC-Visual.pine"
# Probe desechable: fuera del repo (gotcha S124 #2).
OUT = pathlib.Path(os.environ.get("TEMP", ".")) / "PROBE-censo-lado-S127.pine"
MARKER = 130

# Los 9 tipos que viven en SMC_zones (verificado por los f_pushZoneV, S127).
# IPR queda fuera a proposito: es contexto, no entra a SMC_zones.
KINDS = [
    ("OB",   "KIND_OB"),
    ("FVG",  "KIND_FVG"),
    ("BRK",  "KIND_BREAKER"),
    ("IFVG", "KIND_IFVG"),
    ("BPR",  "KIND_BPR"),
    ("MB",   "KIND_MITIGATION"),
    ("OTE",  "KIND_OTE"),
    ("GP",   "KIND_GP"),
    ("VAC",  "KIND_VACUUM"),
]

s = SRC.read_text(encoding="utf-8")
orig_len = len(s)

# Guarda: los simbolos que usa el probe deben existir tal cual.
for needed in ("var float legExtHi = na", "f_depthBand(float level, float px) =>"):
    if s.count(needed) != 1:
        print(f"[FALLO] no se encontro exactamente 1 vez: {needed!r} (encontro {s.count(needed)})")
        sys.exit(1)
for _, k in KINDS:
    if f"\n{k} " not in s and f"\n{k}  " not in s and f"{k} =" not in s:
        print(f"[FALLO] constante no encontrada: {k}")
        sys.exit(1)

# Corta TODO el render (ver nota de cabecera: sin esto no cabe en tokens).
MARK = "// === DIBUJO ==="
if s.count(MARK) != 1:
    print(f"[FALLO] marcador de truncado no unico: {s.count(MARK)}")
    sys.exit(1)
lineas_antes = len(s.splitlines())
s = s[:s.index(MARK)]
print(f"[truncado] render eliminado en {MARK!r}: {lineas_antes} -> {len(s.splitlines())} lineas")

# --- construccion del probe ---
decls, branches, plots = [], [], []
for tag, kind in KINDS:
    for suf in ("vA", "vB", "fA", "fB", "mA", "mB"):
        decls.append(f"int p{tag}{suf} = 0")
    branches.append(
f"""            if z.kind == {kind}
                p{tag}vA += viva and ab and enBanda ? 1 : 0
                p{tag}vB += viva and be and enBanda ? 1 : 0
                p{tag}fA += viva and ab and not enBanda ? 1 : 0
                p{tag}fB += viva and be and not enBanda ? 1 : 0
                p{tag}mA += mit and ab and enBanda ? 1 : 0
                p{tag}mB += mit and be and enBanda ? 1 : 0""")
    plots.append(f'plot(p{tag}vA, "{tag}_viva_arriba")')
    plots.append(f'plot(p{tag}vB, "{tag}_viva_abajo")')
    plots.append(f'plot(p{tag}fA, "{tag}_fuera_arriba")')
    plots.append(f'plot(p{tag}fB, "{tag}_fuera_abajo")')
    plots.append(f'plot(p{tag}mA, "{tag}_mitig_arriba")')
    plots.append(f'plot(p{tag}mB, "{tag}_mitig_abajo")')

PROBE = "\n\n// --- [S127 · PROBE censo por lado] NO cambia gates: solo cuenta SMC_zones.\n"
PROBE += "\n".join(decls) + "\n"
PROBE += "int pContiene = 0\n"
PROBE += """if barstate.islast and array.size(SMC_zones) > 0
    float qPx = close
    for i = 0 to array.size(SMC_zones) - 1
        SMC_Zone z = array.get(SMC_zones, i)
        bool viva = z.state != ZS_INVALID and z.state != ZS_MITIGATED
        bool mit  = z.state == ZS_MITIGATED
        if viva or mit
            bool ab = z.bottom > qPx
            bool be = z.top < qPx
            float lv = ab ? z.bottom : z.top
            int bd = f_depthBand(lv, qPx)
            bool enBanda = bd >= 1 and bd <= i_profundidad
            pContiene += not ab and not be ? 1 : 0
"""
PROBE += "\n".join(branches) + "\n"
PROBE += "\n".join(plots) + "\n"
PROBE += 'plot(pContiene, "ZZ_contienen_precio")\n'
# Por que las bandas 4/5 no activan: f_depthBand las exige con pdPrev1/pdPrev2 no-na, y esos
# escalares SOLO se pueblan al ROTAR el rango (borde >0.5xATR). Si son na, i_profundidad>=4 no
# hace nada. Ploteamos tambien el input para PROBAR que el override entro (no suponerlo).
PROBE += 'plot(i_profundidad, "ZZ_input_profundidad")\n'
PROBE += 'plot(pdPrev1Hi, "ZZ_pdPrev1Hi")\n'
PROBE += 'plot(pdPrev1Lo, "ZZ_pdPrev1Lo")\n'
PROBE += 'plot(pdPrev2Hi, "ZZ_pdPrev2Hi")\n'
PROBE += 'plot(legExtHi, "ZZ_legExtHi")\n'
PROBE += 'plot(legExtLo, "ZZ_legExtLo")\n'
PROBE += f'plot({MARKER}, "ZZ_marker")\n'

s = s + PROBE

OUT.write_text(s, encoding="utf-8")
print(f"Variante: censo {len(KINDS)} conceptos x lado x estado ({len(plots)+2} plots; marker={MARKER})")
print(f"\nPROBE -> {OUT}")
print(f"lineas: {lineas_antes} -> {len(s.splitlines())}")
print(f"bytes : {orig_len} -> {len(s)}  (delta {len(s)-orig_len:+d})")
