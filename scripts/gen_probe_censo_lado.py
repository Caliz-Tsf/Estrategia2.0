# -*- coding: utf-8 -*-
"""
S127 · Genera un PROBE que CENSA las zonas VIVAS por (concepto x lado x banda) a partir de
pine/SMC-Visual.pine SIN tocar el original.

Por que: el usuario pide definir "cuantos por concepto/familia/variante por lado". Esa decision
necesita saber QUE HAY, no que se dibuja. Hoy los conceptos mueren en sitios distintos:
  - OB/FVG/BRK/IDM -> band-pick, 2 slots por (concepto x lado x banda)  [disciplinados]
  - IFVG           -> solo f_densOK (en Operacion exige strength nivel 2) [sin lado ni cap]
  - BPR            -> solo bprCfg>=2 en Operacion (f_famOK(FAM_EST) es false) [sin lado ni cap]
  - MB/MITIGATION  -> promocion por confluencia SIN cap [inunda: las cajas 1.06-1.13]

Este probe NO cambia ningun gate: solo CUENTA. Distingue:
  - vivas   = state != ZS_INVALID and state != ZS_MITIGATED  (lo que el band-pick considera 'elig')
  - arriba / abajo / CONTIENE el precio  (el 3er caso es el BUG DE DISENO de S126: en el band-pick
    'above' y 'below' son ambos false -> la zona se cae del embudo sin que nadie lo note)
  - dentro de banda 1..i_profundidad  vs  fuera (banda 0 = invisible)

TRUNCADO EN "// === DIBUJO ===" (OBLIGATORIO, no es una optimizacion): el Visual esta pegado al
techo de tokens (S125 midio que +345 no cabian) -> un probe que anada un bucle + 11 plots ENCIMA
del Visual completo da CE10117 y no mide nada. El censo NO necesita dibujar: cuenta leyendo
SMC_zones, que puebla el CORE de deteccion. Todo lo que el probe usa (f_depthBand,
f_computeLegExtremes, el band-pick, i_profundidad, KIND_*/ZS_*) vive ANTES de ese marcador; lo que
se tira es solo render. Asi sobra headroom.

Marcador de identidad: probe_censo_marker = 127 (ver [[tv-lecturas-rancias-y-apply-en-espanol]] --
si este plot no aparece en data_get_study_values, estas leyendo un build VIEJO).

Uso:
  python scripts/gen_probe_censo_lado.py
"""
import sys, os, pathlib

SRC = pathlib.Path(__file__).resolve().parent.parent / "pine" / "SMC-Visual.pine"
# Probe desechable: fuera del repo (gotcha S124 #2).
OUT = pathlib.Path(os.environ.get("TEMP", ".")) / "PROBE-censo-lado-S127.pine"

s = SRC.read_text(encoding="utf-8")
orig_len = len(s)

# Guarda: los simbolos que usa el probe deben existir tal cual.
for needed in ("var float legExtHi = na", "f_depthBand(float level, float px) =>"):
    if s.count(needed) != 1:
        print(f"[FALLO] no se encontro exactamente 1 vez: {needed!r} (encontro {s.count(needed)})")
        sys.exit(1)

# Corta TODO el render (ver nota de cabecera: sin esto no cabe en tokens).
MARK = "// === DIBUJO ==="
if s.count(MARK) != 1:
    print(f"[FALLO] marcador de truncado no unico: {s.count(MARK)}")
    sys.exit(1)
cut = s.index(MARK)
lineas_antes = len(s.splitlines())
s = s[:cut]
print(f"[truncado] render eliminado en {MARK!r}: {lineas_antes} -> {len(s.splitlines())} lineas")

PROBE = """

// --- [S127 · PROBE censo por lado] cuenta zonas VIVAS por concepto/lado/banda. NO cambia gates.
// Responde: cuantas hay REALMENTE arriba y abajo de cada concepto, cuantas caen en banda 0
// (invisibles) y cuantas CONTIENEN el precio (se caen del band-pick sin avisar, bug S126).
int pBrkA = 0
int pBrkB = 0
int pBrkC = 0
int pIfvA = 0
int pIfvB = 0
int pBprA = 0
int pBprB = 0
int pMbA  = 0
int pMbB  = 0
int pBand0 = 0
// MITIGADAS en banda: 'elig' (L3371) las excluye del band-pick. Si abajo hay BRK mitigados, el
// arreglo es dejarlas entrar degradadas (Parte A de S108, hecha en Context y nunca en Visual);
// si son 0, es que NO EXISTEN y ningun cap/gate lo arregla.
int pBrkMitA = 0
int pBrkMitB = 0
int pIfvMitA = 0
int pIfvMitB = 0
int pBprMitA = 0
int pBprMitB = 0
if barstate.islast and array.size(SMC_zones) > 0
    float qPx = close
    for i = 0 to array.size(SMC_zones) - 1
        SMC_Zone z = array.get(SMC_zones, i)
        bool viva = z.state != ZS_INVALID and z.state != ZS_MITIGATED
        if z.state == ZS_MITIGATED
            bool abM = z.bottom > qPx
            bool beM = z.top < qPx
            float lvM = abM ? z.bottom : z.top
            int bdM = f_depthBand(lvM, qPx)
            bool enBandaM = bdM >= 1 and bdM <= i_profundidad
            if z.kind == KIND_BREAKER
                pBrkMitA += abM and enBandaM ? 1 : 0
                pBrkMitB += beM and enBandaM ? 1 : 0
            if z.kind == KIND_IFVG
                pIfvMitA += abM and enBandaM ? 1 : 0
                pIfvMitB += beM and enBandaM ? 1 : 0
            if z.kind == KIND_BPR
                pBprMitA += abM and enBandaM ? 1 : 0
                pBprMitB += beM and enBandaM ? 1 : 0
        if viva
            bool ab = z.bottom > qPx
            bool be = z.top < qPx
            float lv = ab ? z.bottom : z.top
            int bd = f_depthBand(lv, qPx)
            bool enBanda = bd >= 1 and bd <= i_profundidad
            if (ab or be) and not enBanda
                pBand0 += 1
            if z.kind == KIND_BREAKER
                pBrkA += ab and enBanda ? 1 : 0
                pBrkB += be and enBanda ? 1 : 0
                pBrkC += not ab and not be ? 1 : 0
            if z.kind == KIND_IFVG
                pIfvA += ab and enBanda ? 1 : 0
                pIfvB += be and enBanda ? 1 : 0
            if z.kind == KIND_BPR
                pBprA += ab and enBanda ? 1 : 0
                pBprB += be and enBanda ? 1 : 0
            if z.kind == KIND_MITIGATION
                pMbA += ab and enBanda ? 1 : 0
                pMbB += be and enBanda ? 1 : 0
plot(pBrkA,  "probe_BRK_arriba",  color = color.new(color.aqua, 0))
plot(pBrkB,  "probe_BRK_abajo",   color = color.new(color.aqua, 0))
plot(pBrkC,  "probe_BRK_contiene_px", color = color.new(color.red, 0))
plot(pIfvA,  "probe_IFVG_arriba", color = color.new(color.orange, 0))
plot(pIfvB,  "probe_IFVG_abajo",  color = color.new(color.orange, 0))
plot(pBprA,  "probe_BPR_arriba",  color = color.new(color.yellow, 0))
plot(pBprB,  "probe_BPR_abajo",   color = color.new(color.yellow, 0))
plot(pMbA,   "probe_MB_arriba",   color = color.new(color.green, 0))
plot(pMbB,   "probe_MB_abajo",    color = color.new(color.green, 0))
plot(pBand0, "probe_fuera_de_banda", color = color.new(color.gray, 0))
plot(pBrkMitA, "probe_BRKmit_arriba", color = color.new(color.blue, 0))
plot(pBrkMitB, "probe_BRKmit_abajo",  color = color.new(color.blue, 0))
plot(pIfvMitA, "probe_IFVGmit_arriba", color = color.new(color.purple, 0))
plot(pIfvMitB, "probe_IFVGmit_abajo",  color = color.new(color.purple, 0))
plot(pBprMitA, "probe_BPRmit_arriba", color = color.new(color.olive, 0))
plot(pBprMitB, "probe_BPRmit_abajo",  color = color.new(color.olive, 0))
plot(128,    "probe_censo_marker", color = color.new(color.white, 0))
"""

s = s + PROBE

OUT.write_text(s, encoding="utf-8")
print("Variante: censo por lado (17 plots: vivas + mitigadas; marker=128)")
print(f"\nPROBE -> {OUT}")
print(f"lineas: {len(SRC.read_text(encoding='utf-8').splitlines())} -> {len(s.splitlines())}")
print(f"bytes : {orig_len} -> {len(s)}  (delta {len(s)-orig_len:+d})")
