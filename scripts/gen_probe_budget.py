# -*- coding: utf-8 -*-
"""
S124 · Genera el PROBE de la Opcion 2 (presupuesto explicito de labels por importancia)
a partir de pine/SMC-Visual.pine SIN tocar el original.

Objetivo del probe: MEDIR tokens (CE10117 solo aparece al aplicar en el chart).
Ver docs/planes/DISENO-presupuesto-labels-S124.md
"""
import sys, os, pathlib

SRC = pathlib.Path(__file__).resolve().parent.parent / "pine" / "SMC-Visual.pine"
# El probe es desechable: fuera del repo (igual que gen_probe_faseB.py / gen_probe_context.py).
OUT = pathlib.Path(os.environ.get("TEMP", ".")) / "PROBE-budget-S124.pine"

# Ablacion: flags en argv para aislar el coste en tokens de cada pieza.
#   nogates   -> solo las REMOCIONES (borra §6.5 + f_capLbls*), sin los 3 gates at-creation
#   nozgate   -> todo menos el gate de f_zLbl
#   noevgate  -> todo menos el gate de f_evLbl
#   noswgate  -> todo menos el gate de f_pushSwingLabel
#   nocap     -> lblCap simple (sin la reserva medida por array.size)
FLAGS = set(sys.argv[1:])
def on(name):
    return name not in FLAGS and "nogates" not in FLAGS if name.endswith("gate") else name not in FLAGS

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

# --- E1+E2: borrar f_capLbls/f_capLblsOnly (token muerto, S123 H4) y reubicar
# las declaraciones de las familias HISTORICAS aqui (deben existir antes de f_zLbl/f_evLbl).
OLD_CAP = """// f_capLbls: recorta un array de labels (con sus lineas 1:1) al budget restante borrando las MAS VIEJAS
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
NEW_CAP = """// [S124 · presupuesto explicito] f_capLbls/f_capLblsOnly ELIMINADAS: recortaban DESPUES de crear, y el
// desalojo de Pine ocurre en el label.new (S123 Hallazgo 4) -> no podian funcionar. El cobro pasa a ser
// AT-CREATION dentro de f_evLbl/f_zLbl/f_pushSwingLabel. Las familias HISTORICAS (estructura, EQH/EQL) se
// declaran AQUI (antes que f_zLbl/f_evLbl) porque su tamano real es la RESERVA del presupuesto.
var array<line>  SMC_structLines  = array.new<line>()
var array<label> SMC_structLabels = array.new<label>()
var array<float> SMC_structLevels = array.new<float>()                                                      // §3.5-f [A-7]: nivel paralelo para el recorte por banda
var array<line>  SMC_eqLines  = array.new<line>()
var array<label> SMC_eqLabels = array.new<label>()
var array<float> SMC_eqLevels = array.new<float>()                                                          // §3.5-f [A-7]: nivel paralelo para el recorte por banda
"""
sub("E1+E2 borrar f_capLbls* + reubicar declaraciones historicas", OLD_CAP, NEW_CAP)

# --- E3: eventCap/gEvtLbl/gEvtCut -> lblCap + lblSpent (reserva MEDIDA, no adivinada)
OLD_BUD = """int eventCap = math.max(0, budgetLbl - mtfReserve - FRAME_RESERVE)                                          // labels que quedan para eventos nativos L3
int gEvtLbl = 0                                                                                             // contador de labels de eventos nativos ya emitidos (orden de dibujo)
int gEvtCut = 0                                                                                             // §10-#8: desalojados -> panel T14 (nada desaparece en silencio)
"""
NEW_BUD = """// [S124] Techo REAL = min(lo que el usuario quiere ver, lo que la plataforma permite). Las familias
// historicas (estructura/EQ) se crean en el recorrido historico = son las MAS VIEJAS y Pine las desaloja
// primero; su tamano ya se conoce aqui, asi que se RESERVA leyendolo (no estimando). El resto de familias
// (islast) gasta lo que queda, en ORDEN DE DIBUJO = orden de importancia.
int lblCap = math.max(0, math.min(budgetLbl, 500 - array.size(SMC_structLabels) - array.size(SMC_eqLabels) - FRAME_RESERVE - mtfReserve))
var array<int> lblSpent = array.new<int>(1, 0)                                                              // cobro at-creation; array<int> de 1 (Pine no muta un global escalar en funcion) = RE10045-safe
"""
sub("E3 eventCap -> lblCap + lblSpent", OLD_BUD, NEW_BUD)

# --- E5: gate en f_zLbl
OLD_ZLBL = """f_zLbl(int x, float y, string txt, color tc) =>
    label.new(x, y, txt, style = label.style_label_center, color = color.new(color.gray, 100), textcolor = tc, size = size.small, xloc = xloc.bar_time)
"""
NEW_ZLBL = """f_zLbl(int x, float y, string txt, color tc) =>
    label lz = na
    if array.get(lblSpent, 0) < lblCap
        array.set(lblSpent, 0, array.get(lblSpent, 0) + 1)
        lz := label.new(x, y, txt, style = label.style_label_center, color = color.new(color.gray, 100), textcolor = tc, size = size.small, xloc = xloc.bar_time)
    lz
"""
if on("nozgate"):
    sub("E5 gate f_zLbl", OLD_ZLBL, NEW_ZLBL)

# --- E6: gate en f_evLbl (se acopla al if del anti-solape 2D ya existente)
OLD_EVLBL = """    if k == "" or not str.contains(array.get(evSeen, 0), k)
        array.set(evSeen, 0, array.get(evSeen, 0) + k)
        lb := label.new(x, y, txt, style = st, color = color.new(bg, transp), textcolor = tc, size = size.tiny, xloc = xloc.bar_time)
"""
NEW_EVLBL = """    if (k == "" or not str.contains(array.get(evSeen, 0), k)) and array.get(lblSpent, 0) < lblCap
        array.set(evSeen, 0, array.get(evSeen, 0) + k)
        array.set(lblSpent, 0, array.get(lblSpent, 0) + 1)
        lb := label.new(x, y, txt, style = st, color = color.new(bg, transp), textcolor = tc, size = size.tiny, xloc = xloc.bar_time)
"""
if on("noevgate"):
    sub("E6 gate f_evLbl", OLD_EVLBL, NEW_EVLBL)

# --- E8: reset por pasada (junto al reset de evSeen, antes de todos los drawers de islast)
OLD_RST = """if barstate.islast
    array.set(evSeen, 0, "")
"""
NEW_RST = """if barstate.islast
    array.set(evSeen, 0, "")
    array.set(lblSpent, 0, 0)
"""
sub("E8 reset lblSpent", OLD_RST, NEW_RST)

# --- E4a: quitar declaraciones originales de estructura (ya reubicadas arriba). Ancla = STRUCT_OP_CAP.
OLD_DECL_ST = """int STRUCT_OP_CAP = 3
var array<line>  SMC_structLines  = array.new<line>()
var array<label> SMC_structLabels = array.new<label>()
var array<float> SMC_structLevels = array.new<float>()                                                      // §3.5-f [A-7]: nivel paralelo para el recorte por banda
var int hidStruct = 0"""
NEW_DECL_ST = """int STRUCT_OP_CAP = 3
var int hidStruct = 0"""
sub("E4a quitar decls originales de estructura", OLD_DECL_ST, NEW_DECL_ST)

# --- E4b: quitar declaraciones originales de EQ (ya reubicadas)
OLD_DECL_EQ = """var array<line>  SMC_eqLines  = array.new<line>()
var array<label> SMC_eqLabels = array.new<label>()
var array<float> SMC_eqLevels = array.new<float>()                                                          // §3.5-f [A-7]: nivel paralelo para el recorte por banda
var int hidEq = 0"""
NEW_DECL_EQ = """var int hidEq = 0"""
sub("E4b quitar decls duplicadas de EQ", OLD_DECL_EQ, NEW_DECL_EQ)

# --- E9: borrar el bloque §6.5 (desalojo post-hoc, inutil por S123 H4)
OLD_65 = """// --- §6.5 · DESALOJO DETERMINISTA de eventos nativos L3 [Eje2 · Paso 6 · S090] ---
// Punto unico: todas las familias nativas discrecionales ya estan construidas + top-N'd; la capa MTF
// (mandatoria §7.1) aun NO dibuja. Se recorta el excedente de labels al presupuesto restante (eventCap =
// budget - reservaMTF - marco). PRIORIDAD de conservacion: EQHL > pools > sweep > flip > gaps; dentro de
// cada familia caen primero las MAS VIEJAS. En M5 (doble MTF) eventCap≈0 -> el ruido nativo cede a la
// herencia; en H1 (una MTF) sobra sitio para ~8 nativos; en D1 (sin MTF) se conservan todos. Sin arrays
// nuevos. Los desalojados se cuentan (gEvtCut) y afloran en la fila "Ocultos" del panel T14 (§10-#8).
if barstate.islast
    [g1, c1] = f_capLbls(SMC_eqLabels, SMC_eqLines, gEvtLbl, eventCap)
    gEvtLbl := g1
    [g2, c2] = f_capLblsOnly(SMC_poolLabels, gEvtLbl, eventCap)
    gEvtLbl := g2
    [g3, c3] = f_capLblsOnly(SMC_sweepLabels, gEvtLbl, eventCap)
    gEvtLbl := g3
    [g4, c4] = f_capLbls(SMC_flipLabels, SMC_flipLines, gEvtLbl, eventCap)
    gEvtLbl := g4
    [g5, c5] = f_capLbls(SMC_ogLabels, SMC_ogLines, gEvtLbl, eventCap)
    gEvtLbl := g5
    gEvtCut := c1 + c2 + c3 + c4 + c5
"""
NEW_65 = """// --- §6.5 · PRESUPUESTO AT-CREATION [S124 · sustituye el desalojo post-hoc S090] ---
// El bloque de desalojo que vivia aqui borraba labels DESPUES de crearlas; para entonces Pine ya habia
// desalojado las mas viejas en el propio label.new (S123 Hallazgo 4) -> no hacia nada. El cobro vive ahora
// en f_evLbl/f_zLbl/f_pushSwingLabel (at-creation, contador lblSpent, techo lblCap).
// ORDEN DE DIBUJO = ORDEN DE IMPORTANCIA: quien dibuja antes se queda el slot; el ultimo cede. NO reordenar
// las secciones de dibujo sin entender que se estan reordenando PRIORIDADES (los swings van al final = L3).
"""
sub("E9 borrar §6.5 post-hoc", OLD_65, NEW_65)

# --- E7: gate en f_pushSwingLabel
OLD_SW = """    float yAdj = isHigh ? sw.price + atr * 0.3 : sw.price - atr * 0.3
    array.push(arr, label.new(sw.barTime, yAdj, txt, style = isHigh ? label.style_label_down : label.style_label_up, color = color.new(color.gray, 100), textcolor = color.new(col, dom ? 45 : 75), size = size.tiny, xloc = xloc.bar_time))
"""
NEW_SW = """    float yAdj = isHigh ? sw.price + atr * 0.3 : sw.price - atr * 0.3
    if array.get(lblSpent, 0) < lblCap
        array.set(lblSpent, 0, array.get(lblSpent, 0) + 1)
        array.push(arr, label.new(sw.barTime, yAdj, txt, style = isHigh ? label.style_label_down : label.style_label_up, color = color.new(color.gray, 100), textcolor = color.new(col, dom ? 45 : 75), size = size.tiny, xloc = xloc.bar_time))
"""
if on("noswgate"):
    sub("E7 gate f_pushSwingLabel", OLD_SW, NEW_SW)

# --- E10: panel T14 "Desalojo" -> "Presup consumido/techo" (§10-#8: nada en silencio)
OLD_PAN = """(gEvtCut > 0 ? " · Desalojo " + str.tostring(gEvtCut) : "")"""
NEW_PAN = """" · Presup " + str.tostring(array.get(lblSpent, 0)) + "/" + str.tostring(lblCap)"""
sub("E10 panel Desalojo -> Presup", OLD_PAN, NEW_PAN)

OUT.write_text(s, encoding="utf-8")
print("Ediciones aplicadas:")
for a in applied:
    print("  OK  " + a)
print(f"\nPROBE -> {OUT}")
print(f"lineas: {len(SRC.read_text(encoding='utf-8').splitlines())} -> {len(s.splitlines())}")
print(f"bytes : {orig_len} -> {len(s)}  (delta {len(s)-orig_len:+d})")
# sanity: no deben quedar referencias a lo eliminado
for dead in ("f_capLbls", "f_capLblsOnly", "eventCap", "gEvtLbl", "gEvtCut"):
    n = s.count(dead)
    print(f"  residuo '{dead}': {n}")
