# -*- coding: utf-8 -*-
"""
S126 · Genera el PROBE del GATE DE BANDA para la promocion por confluencia (MB/BPR)
a partir de pine/SMC-Visual.pine SIN tocar el original.

Problema que ataca (medido vivo S126, D1 Operacion, precio 1.14215):
las 10 cajas dibujadas son 7 MB + 1 OB + 1 BRK + 1 FVG. Las MB inundan porque su via
de dibujo es `... or mbCfg >= 2` (L4425): promocion por CONFLUENCIA **sin gate de banda,
sin lado y sin cuota**. OB/FVG, las unicas con band-pick, se autolimitan a 2 por celda.
La familia disciplinada se autolimita; la indisciplinada inunda.

El absurdo que lo prueba: f_confDegree (L3217) cuenta FAMILIAS VIVAS distintas y excluye
mitigadas -> un MB con mbCfg>=2 en 1.37 significa que ahi hay 2 familias vivas confluyendo
QUE NO SE DIBUJAN (1.37 cae fuera de banda: i_kLeg=3.0 recorta el extremo a ~1.3697).
Se dibuja el testigo de la confluencia y no los que la forman.

Fix: exigir que la promocion por confluencia caiga DENTRO del alcance de banda
(1..i_profundidad), el mismo alcance que ya respetan OB/FVG/BRK via band-pick.
NO toca el band-pick, NO toca la exclusion de mitigadas (ese es el otro hilo).

Objetivo del probe: MEDIR tokens. CE10117 solo aparece al APLICAR en el chart;
pine_check NO cuenta tokens (S107/S124). Y el conteo solo es legible POR ENCIMA del
techo (gotcha S121) -> si cabe, no hay numero: solo "cabe".

Variantes (el coste no se predice -- 4 predicciones muertas de 4):
  (por defecto)  helper  -> f_inBand nueva + 2 call-sites (MB, BPR)
  inline         -> misma condicion incrustada en los 2 call-sites, SIN funcion nueva
  mbonly         -> helper + 1 call-site (solo MB). Aisla el coste de tocar UN bloque.

Uso:
  python scripts/gen_probe_mbband.py            # helper, MB+BPR
  python scripts/gen_probe_mbband.py inline
  python scripts/gen_probe_mbband.py mbonly
"""
import sys, os, pathlib

SRC = pathlib.Path(__file__).resolve().parent.parent / "pine" / "SMC-Visual.pine"
FLAGS = set(sys.argv[1:])
INLINE = "inline" in FLAGS
MBONLY = "mbonly" in FLAGS
VARIANT = "inline" if INLINE else ("mbonly" if MBONLY else "helper")
# El probe es desechable: fuera del repo (gotcha S124 #2).
OUT = pathlib.Path(os.environ.get("TEMP", ".")) / f"PROBE-mbband-{VARIANT}-S126.pine"

s = SRC.read_text(encoding="utf-8")
orig_len = len(s)
applied = []


def sub(tag, old, new, count=1):
    global s
    n = s.count(old)
    if n != count:
        print(f"[FALLO] {tag}: esperaba {count} ocurrencia(s), encontro {n}")
        sys.exit(1)
    s = s.replace(old, new, count)
    applied.append(tag)


# Condicion inline equivalente al helper (misma semantica, sin funcion).
# Replica la logica de f_isBandPick L3322-3331: lado por posicion vs close, nivel = borde
# encarado al precio, banda 1..i_profundidad.
INLINE_MB = ("(mbCfg >= 2 and f_depthBand(z.bottom > close ? z.bottom : z.top, close) >= 1"
             " and f_depthBand(z.bottom > close ? z.bottom : z.top, close) <= i_profundidad)")
INLINE_BPR = ("(bprCfg >= 2 and f_depthBand(z.bottom > close ? z.bottom : z.top, close) >= 1"
              " and f_depthBand(z.bottom > close ? z.bottom : z.top, close) <= i_profundidad)")

# --- E1: helper f_inBand (variantes helper / mbonly)
if not INLINE:
    ANCHOR = "// f_updateLegExtremes §7 [S106 Paso A]"
    if s.count(ANCHOR) != 1:
        print(f"[FALLO] E1: ancla f_updateLegExtremes encontrada {s.count(ANCHOR)} veces")
        sys.exit(1)
    HELPER = """// f_inBand [S126]: ¿el borde de la zona encarado al precio cae dentro del alcance de banda
// (1..i_profundidad)? Mismo criterio de lado/nivel que f_isBandPick (L3322) pero SIN cuota: aqui
// no se elige representante, solo se acota el ALCANCE de la promocion por confluencia (MB/BPR),
// que hoy dibuja fuera de la pierna. PURA, Visual-only.
f_inBand(float top, float bottom) =>
    bool above = bottom > close
    bool ok = false
    if above or top < close
        int band = f_depthBand(above ? bottom : top, close)
        ok := band >= 1 and band <= i_profundidad
    ok

"""
    s = s.replace(ANCHOR, HELPER + ANCHOR, 1)
    applied.append("E1 helper f_inBand")

# --- E2: gate en la promocion por confluencia de MB (L4425)
sub("E2 gate de banda en MB",
    "or mbCfg >= 2",
    "or (mbCfg >= 2 and f_inBand(z.top, z.bottom))" if not INLINE else "or " + INLINE_MB)

# --- E3: gate en la promocion por confluencia de BPR (L4359) -- omitido en mbonly
if not MBONLY:
    sub("E3 gate de banda en BPR",
        "or bprCfg >= 2",
        "or (bprCfg >= 2 and f_inBand(z.top, z.bottom))" if not INLINE else "or " + INLINE_BPR)

OUT.write_text(s, encoding="utf-8")
print(f"Variante: {VARIANT}")
print("Ediciones aplicadas:")
for a in applied:
    print("  OK  " + a)
print(f"\nPROBE -> {OUT}")
print(f"lineas: {len(SRC.read_text(encoding='utf-8').splitlines())} -> {len(s.splitlines())}")
print(f"bytes : {orig_len} -> {len(s)}  (delta {len(s)-orig_len:+d})")
