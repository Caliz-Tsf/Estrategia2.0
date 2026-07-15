# -*- coding: utf-8 -*-
"""
S126 · Genera un PROBE que EXPONE legExtHi / legExtLo (extremos de pierna) a partir de
pine/SMC-Visual.pine SIN tocar el original.

Por que: en S126 el gate de banda (gen_probe_mbband.py) elimino MB a 1.17 y 1.09, que estan
a ~3 y ~5 pips del precio (1.1423) y deberian caer en banda 1. La unica explicacion es que la
VENTANA DE BANDAS sea minuscula. Reconstruyendo desde que sobrevivio (1.13) y que murio
(1.09/1.17/1.27/1.34/1.37) se INFIERE legExtHi~1.152 y legExtLo~1.10 -- muy lejos del clamp
de i_kLeg=3.0, que daria px +- 3*0.07585 = [0.915, 1.370].

Hipotesis: no manda el CLAMP, manda el ANCLAJE de f_computeLegExtremes al pool fuerte mas
lejano DENTRO del clamp (engancha LQ 1.15142 / BSL 1.14730) -> colapsa el alcance hacia
arriba a ~10 pips -> casi todo cae en banda 0 -> invisible para band-pick Y para el gate.

Esto se INFIRIO, no se midio. Este probe lo MIDE: plotea los dos extremos y se leen con
data_get_study_values. Si se confirma, el bloqueante real es el anclaje, no i_kLeg.

Los plots van al FINAL del fichero: legExtHi/legExtLo son globales (`var float`, ~L3106-3107)
asignadas en el bloque islast (~L3345), que corre ANTES del final -> el plot ve el valor ya
actualizado en la barra viva.

Uso:
  python scripts/gen_probe_legext.py
"""
import sys, os, pathlib

SRC = pathlib.Path(__file__).resolve().parent.parent / "pine" / "SMC-Visual.pine"
# El probe es desechable: fuera del repo (gotcha S124 #2).
OUT = pathlib.Path(os.environ.get("TEMP", ".")) / "PROBE-legext-S126.pine"

s = SRC.read_text(encoding="utf-8")
orig_len = len(s)

# Guardas: las globales deben existir tal cual antes de plotearlas.
for needed in ("var float legExtHi = na", "var float legExtLo = na"):
    if s.count(needed) != 1:
        print(f"[FALLO] no se encontro exactamente 1 vez: {needed!r} (encontro {s.count(needed)})")
        sys.exit(1)

PLOTS = """

// --- [S126 · PROBE legext] expone los extremos de pierna para medirlos con data_get_study_values.
// NO forma parte del Visual: solo vive en el probe. Mide la hipotesis "el anclaje al pool colapsa
// la ventana de bandas" (inferida del A/B del gate MB: murieron 1.09 y 1.17, sobrevivio 1.13).
plot(legExtHi, "probe_legExtHi", color = color.new(color.aqua, 0))
plot(legExtLo, "probe_legExtLo", color = color.new(color.fuchsia, 0))
// referencias para interpretar: el clamp teorico y el precio.
plot(close, "probe_close", color = color.new(color.gray, 0))
plot(chartState.pdHigh, "probe_pdHigh", color = color.new(color.lime, 0))
plot(chartState.pdLow, "probe_pdLow", color = color.new(color.red, 0))
"""

s = s + PLOTS

OUT.write_text(s, encoding="utf-8")
print("Variante: legext (5 plots de diagnostico al final)")
print(f"\nPROBE -> {OUT}")
print(f"lineas: {len(SRC.read_text(encoding='utf-8').splitlines())} -> {len(s.splitlines())}")
print(f"bytes : {orig_len} -> {len(s)}  (delta {len(s)-orig_len:+d})")
