# -*- coding: utf-8 -*-
"""
S130 · PROBE v6 — ¿el rango de un TF es la MITAD del de su TF padre? (discrimina P-G1)

POR QUE. S130 midio que el nivel 1 de la cascada de mitades (3505.7 pips) reproduce la lectura a ojo
del usuario en H1 (3780) con 7.3% de error -> P-G1 verde. PERO es n=1: amplitud coincidente con
niveles desplazados >1200 pips no distingue "el ojo leia la mitad de D1" de una casualidad.

EL AGUJERO DEL TEST OBVIO. No se puede repetir en otro simbolo comparando contra el H1 NATIVO: S129
midio que el H1 nativo NO reproduce la lectura del usuario (1905 vs 3780) — necesitaria ~75.000 barras
y TV da 9.535. Comparar contra el nativo mide OTRA cosa. La referencia de P-G1 es el OJO del usuario y
solo existe para EURUSD.

LO QUE ESTE PROBE SI PUEDE FALSAR. La afirmacion estructural que sostiene el mapeo "nivel 1 = H1":
que el rango de H1 sea SISTEMATICAMENTE ~la mitad del de D1. Si el ratio se agrupa entre simbolos, el
mapeo nivel->TF tiene base (aunque la constante no sea 0.5); si sale disperso, es arbitrario.

LIMITACION HONESTA (no ocultar al leer los numeros). El ratio ampH1/ampD1 depende de CUANTA HISTORIA
da TV en cada TF (~6283 barras D1 = 24 años vs ~9535 barras H1 = ~1.5 años), no solo del mercado. Es
mitad artefacto del feed. Vale como test de "que nivel corresponde a H1 EN LA PRACTICA" — que es lo
que el sistema real veria —, NO como ley de mercado.

PREDICCIONES (escritas ANTES de medir — van 14 vivas de 26):
  P-H1  EURUSD: ratio ampH1/ampD1 ~ 0.27 (de S129: 1905.2 / 7011.35 = 0.2718; en H1 el extremo nunca
        se violo -> latch == literal). FALSA si difiere > 0.05.
  P-H2  (LA QUE DECIDE) El ratio se AGRUPA entre los 5 simbolos: desviacion max-min <= 0.20.
        FALSA si el rango de ratios supera 0.20 -> el mapeo nivel->TF seria arbitrario.
  P-H3  NINGUN simbolo da ratio ~0.5 => el nivel 1 NO es H1; el candidato correcto es el NIVEL 2
        (0.25). FALSA si algun simbolo cae en 0.5 +/- 0.05.
  P-H4  NAS100USD (tendencia secular fuerte, el caso adverso de S129) es el OUTLIER: su ratio sera el
        mas BAJO de los 5 (su D1 abarca varios multiplos, su H1 no). FALSA si no es el minimo.

METODO. Un solo apply; despues se cambia symbol/TF con chart_set_symbol / chart_set_timeframe y el
estudio RECALCULA SOLO (no hace falta re-aplicar). 5 simbolos x 2 TFs = 10 lecturas rapidas.
Unidades: se reporta hi/lo crudos + amp RELATIVA ((hi-lo)/lo) para que NAS100 y USDJPY sean
comparables con EURUSD (los "pips" no son comparables entre clases de activo).

ANTI-HUMO (S128/S129): P_nBars denominador explicito; P_close de control (data_get_study_values sigue
el CROSSHAIR); P_marker por build (unico distintivo fresco/rancio); nada se lee en islast.
TRUNCADO en "// === DIBUJO ===" (CE10117).

Uso:
  python scripts/gen_probe_ratio_tf.py
"""
import sys, os, pathlib

SRC = pathlib.Path(__file__).resolve().parent.parent / "pine" / "SMC-Visual.pine"
OUT = pathlib.Path(os.environ.get("TEMP", ".")) / "PROBE-ratio-tf-S130.pine"
MARKER = 1302

s = SRC.read_text(encoding="utf-8")

MARK = "// === DIBUJO ==="
if s.count(MARK) != 1:
    print(f"[FALLO] marcador de truncado no unico: {s.count(MARK)}")
    sys.exit(1)
lineas_antes = len(s.splitlines())
s = s[:s.index(MARK)]
print(f"[truncado] render eliminado en {MARK!r}: {lineas_antes} -> {len(s.splitlines())} lineas")

PROBE = f"""

// --- [S130 · PROBE v6: rango de la ventana del TF del chart — para el ratio ampH1/ampD1]
// Deliberadamente MINIMO: solo el min/max de la ventana (= Opcion C literal, L0) del TF que este
// puesto en el chart. Se cambia symbol/TF por fuera y el estudio recalcula solo.
var float wHi   = na
var float wLo   = na
var int   nBars = 0

if barstate.isconfirmed
    nBars += 1
    if na(wHi) or high > wHi
        wHi := high
    if na(wLo) or low < wLo
        wLo := low

// amp RELATIVA: adimensional -> comparable entre EURUSD / USDJPY / NAS100USD.
float ampRel = na(wHi) or na(wLo) or wLo <= 0 ? na : (wHi - wLo) / wLo
// L1 = la mitad donde vive el precio (el candidato a H1 segun el diseno de S130).
float wMid   = na(wHi) or na(wLo) ? na : (wHi + wLo) / 2.0
float l1lo   = na(wMid) ? na : (close >= wMid ? wMid : wLo)
float l1hi   = na(wMid) ? na : (close >= wMid ? wHi  : wMid)

plot(nBars,    "P_nBars")
plot(close,    "P_close")
plot({MARKER}, "P_marker")
plot(wHi,      "P_wHi")
plot(wLo,      "P_wLo")
plot(ampRel,   "P_ampRel")
plot(l1lo,     "P_L1lo")
plot(l1hi,     "P_L1hi")
"""

s = s + PROBE
OUT.write_text(s, encoding="utf-8")
print(f"Variante: rango de ventana por TF del chart (marker={MARKER})")
print(f"\nPROBE -> {OUT}")
print(f"lineas: {lineas_antes} -> {len(s.splitlines())}")
