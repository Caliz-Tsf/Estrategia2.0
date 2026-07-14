# -*- coding: utf-8 -*-
"""
S125 · Genera el PROBE de la Opcion 1 (cap top-N POR TIPO en los swings) a partir de
pine/SMC-Visual.pine SIN tocar el original.

Problema que ataca: el etiquetado de swings se filtra con un UMBRAL DE AMPLITUD
(sw.strength >= i_swingDomAtr). Los HH/LL (extremos de impulso) tienen mas amplitud que
los HL/LH (pullbacks) -> el umbral los mata de forma asimetrica: HH 31 / LL 19 / HL 11 /
LH 4 (censo S123/S124). Eso ROMPE la alternancia H-L-H-L que era la clave del rediseno
leg-based de S117.

Fix: el RANGO decide QUIEN se dibuja (top-N por tipo), la AMPLITUD decide QUE TAN FUERTE
se ve (i_swingDomAtr se queda dentro de f_pushSwingLabel para la transparencia dom/menor).

Objetivo del probe: MEDIR tokens (CE10117 solo aparece al aplicar en el chart; pine_check
NO cuenta tokens -- S107/S124). Dos variantes, porque el coste no se predice (S124):

  (por defecto)  variante A "fuerza"  -> top-N por tipo por STRENGTH (helper nuevo + array.sort)
  recency        variante B "reciente"-> ultimos N por tipo (pasada hacia atras, SIN funcion nueva)

Ambas comparten el input nuevo i_swingTopN, declarado AL FINAL de los inputs a proposito:
anadirlo arriba correria todos los in_N (gotcha [[tv-input-ids-se-corren]]).
"""
import sys, os, pathlib

SRC = pathlib.Path(__file__).resolve().parent.parent / "pine" / "SMC-Visual.pine"
# El probe es desechable: fuera del repo (gotcha S124 #2).
FLAGS = set(sys.argv[1:])
VARIANT = "recency" if "recency" in FLAGS else "strength"
SIN65 = "sin65" in FLAGS
SOLO65 = "solo65" in FLAGS  # solo la remocion, sin la Opcion 1: mide el ahorro
OUT = pathlib.Path(os.environ.get("TEMP", ".")) / (
    f"PROBE-swingtopn-{'solo65' if SOLO65 else VARIANT + ('-sin65' if SIN65 else '')}-S125.pine"
)

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


# --- E0: REMOCION de la §6.5 (token muerto: recorta DESPUES de crear, y Pine ya desalojo en el
# label.new -- S123 Hallazgo 4). S124 la midio "gratis o mejor". Aqui se mide cuanto FINANCIA.
if SIN65 or SOLO65:
    OLD_CAPF = """// f_capLbls: recorta un array de labels (con sus lineas 1:1) al budget restante borrando las MAS VIEJAS
// (array.shift) hasta que gCount + size <= cap. Devuelve [nuevoGCount, cortadas]. Solo actua cuando el
// presupuesto aprieta (Operacion/M5); en Estudio+/Todo el cap holgado deja el while inactivo.
f_capLbls(array<label> lbls, array<line> lns, int gCount, int cap) =>
    int cut = 0
    while array.size(lbls) > 0 and gCount + array.size(lbls) > cap
        label.delete(array.shift(lbls))
        if array.size(lns) > 0
            line.delete(array.shift(lns))
        cut += 1
    [gCount + array.size(lbls), cut]
f_capLblsOnly(array<label> lbls, int gCount, int cap) =>
    int cut = 0
    while array.size(lbls) > 0 and gCount + array.size(lbls) > cap
        label.delete(array.shift(lbls))
        cut += 1
    [gCount + array.size(lbls), cut]
"""
    sub("E0a borrar f_capLbls/f_capLblsOnly", OLD_CAPF, "")

    OLD_EVCAP = """int eventCap = math.max(0, budgetLbl - mtfReserve - FRAME_RESERVE)                                          // labels que quedan para eventos nativos L3
int gEvtLbl = 0                                                                                             // contador de labels de eventos nativos ya emitidos (orden de dibujo)
int gEvtCut = 0                                                                                             // §10-#8: desalojados -> panel T14 (nada desaparece en silencio)
"""
    sub("E0b borrar eventCap/gEvtLbl/gEvtCut", OLD_EVCAP, "")

    idx65 = s.find("// --- §6.5 · DESALOJO DETERMINISTA de eventos nativos L3")
    end65 = s.find("    gEvtCut := c1 + c2 + c3 + c4 + c5")
    if idx65 < 0 or end65 < 0:
        print("[FALLO] E0c: no se localizo el bloque §6.5")
        sys.exit(1)
    end65 = s.find("\n", end65) + 1
    s = s[:idx65] + s[end65:]
    applied.append("E0c borrar bloque §6.5 (desalojo post-hoc)")

    OLD_PAN = ' + (gEvtCut > 0 ? " · Desalojo " + str.tostring(gEvtCut) : "")'
    sub("E0d quitar gEvtCut del panel", OLD_PAN, "")

if SOLO65:
    OUT.write_text(s, encoding="utf-8")
    print("Variante: SOLO remocion §6.5 (sin Opcion 1)")
    for a in applied:
        print("  OK  " + a)
    print(f"\nPROBE -> {OUT}")
    print(f"bytes : {orig_len} -> {len(s)}  (delta {len(s)-orig_len:+d})")
    sys.exit(0)

# --- E1: input nuevo i_swingTopN, AL FINAL de los inputs (no corre los in_N existentes)
OLD_IN = 'i_swingMinorLabels = input.bool(false, "Swings: etiquetar menores (solo Estudio+)", group = GRP_STRUCT, tooltip = "Off (default) = solo pivotes dominantes (anclas), esqueleto limpio. On = anade los menores tenues en Estudio+. Con i_swingMaxKeep alto + modo Todo puede acercarse al tope de 500 labels de Pine.")'
# el fuente real lleva acentos; se localiza por prefijo estable
PREFIX_IN = "i_swingMinorLabels = input.bool(false,"
idx = s.find(PREFIX_IN)
if idx < 0:
    print("[FALLO] E1: no se encontro la declaracion de i_swingMinorLabels")
    sys.exit(1)
end = s.find("\n", idx)
NEW_IN = (
    s[idx:end]
    + '\ni_swingTopN = input.int(12, "Swings: max. por tipo (HH/HL/LH/LL)", minval = 1, maxval = 60, group = GRP_STRUCT, tooltip = "Cuantos pivotes de CADA tipo se etiquetan. Reemplaza el umbral de amplitud como criterio de QUIEN se dibuja: el umbral mataba HL/LH (pullbacks, poca amplitud) y dejaba solo HH/LL -> se rompia la alternancia H-L. i_swingDomAtr sigue decidiendo la INTENSIDAD del tag, no su existencia.")'
)
s = s[:idx] + NEW_IN + s[end:]
applied.append("E1 input i_swingTopN (al final, no corre in_N)")

# --- E2: el bucle de dibujo pasa de umbral de amplitud a cap top-N por tipo
OLD_LOOP = """    int nMj = array.size(SMC_majorSwingsV)
    if nMj > 0
        for i = 0 to nMj - 1
            SMC_Swing sw = array.get(SMC_majorSwingsV, i)
            bool domSw = sw.strength >= i_swingDomAtr
            bool showSw = domSw or (i_swingMinorLabels and f_famOK(FAM_EST))
            if showSw
                f_pushSwingLabel(SMC_majorSwingLabels, sw, i_swingDomAtr, sAtr14)
"""

NEW_LOOP_STRENGTH = """    int nMj = array.size(SMC_majorSwingsV)
    array<float> swThr = array.new<float>(4, 0.0)
    for k = 0 to 3
        array.set(swThr, k, f_swThr(SMC_majorSwingsV, KIND_HH + k, i_swingTopN))
    if nMj > 0
        for i = 0 to nMj - 1
            SMC_Swing sw = array.get(SMC_majorSwingsV, i)
            int ki = sw.kind - KIND_HH
            bool domSw = ki >= 0 and ki < 4 and sw.strength > array.get(swThr, ki)
            bool showSw = domSw or (i_swingMinorLabels and f_famOK(FAM_EST))
            if showSw
                f_pushSwingLabel(SMC_majorSwingLabels, sw, i_swingDomAtr, sAtr14)
"""

NEW_LOOP_RECENCY = """    int nMj = array.size(SMC_majorSwingsV)
    array<int> swCnt = array.new<int>(4, 0)
    array<int> swCut = array.new<int>(4, 0)
    if nMj > 0
        for i = nMj - 1 to 0
            int kb = array.get(SMC_majorSwingsV, i).kind - KIND_HH
            if kb >= 0 and kb < 4
                array.set(swCnt, kb, array.get(swCnt, kb) + 1)
                if array.get(swCnt, kb) == i_swingTopN
                    array.set(swCut, kb, i)
        for i = 0 to nMj - 1
            SMC_Swing sw = array.get(SMC_majorSwingsV, i)
            int ki = sw.kind - KIND_HH
            bool domSw = ki >= 0 and ki < 4 and i >= array.get(swCut, ki)
            bool showSw = domSw or (i_swingMinorLabels and f_famOK(FAM_EST))
            if showSw
                f_pushSwingLabel(SMC_majorSwingLabels, sw, i_swingDomAtr, sAtr14)
"""

sub("E2 bucle: umbral -> top-N por tipo (" + VARIANT + ")",
    OLD_LOOP,
    NEW_LOOP_STRENGTH if VARIANT == "strength" else NEW_LOOP_RECENCY)

# --- E3: helper del umbral por tipo (SOLO variante A)
if VARIANT == "strength":
    ANCHOR = "var array<label> SMC_majorSwingLabels = array.new<label>()"
    HELPER = """// f_swThr [S125 · Opcion 1]: umbral de corte del top-N por TIPO. Junta las amplitudes de los swings
// de ese kind, las ordena desc y devuelve la (n+1)-esima -> comparar con > deja pasar como mucho n.
// Devuelve 0.0 si hay n o menos (pasan todos). PURA, Visual-only, corre 4x por pasada en islast.
f_swThr(array<SMC_Swing> a, int kind, int n) =>
    array<float> ss = array.new<float>()
    for sw in a
        if sw.kind == kind
            array.push(ss, sw.strength)
    array.sort(ss, order.descending)
    array.size(ss) > n ? array.get(ss, n) : 0.0

"""
    sub("E3 helper f_swThr", ANCHOR, HELPER + ANCHOR)

OUT.write_text(s, encoding="utf-8")
print(f"Variante: {VARIANT}")
print("Ediciones aplicadas:")
for a in applied:
    print("  OK  " + a)
print(f"\nPROBE -> {OUT}")
print(f"lineas: {len(SRC.read_text(encoding='utf-8').splitlines())} -> {len(s.splitlines())}")
print(f"bytes : {orig_len} -> {len(s)}  (delta {len(s)-orig_len:+d})")
