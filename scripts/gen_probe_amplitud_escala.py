# -*- coding: utf-8 -*-
"""
S132 · PROBE v11 — la amplitud del swing, BARRIDO DE ESCALA.

POR QUE EXISTE ESTE PROBE (auto-correccion de v10). v10 midio la amplitud de llegada contra el pivote
anterior de f_detectSwings(i_swingLen) con i_swingLen=5 — un zigzag de 5 barras. P-A1 salio FALSA
(min(A)=3.41 < max(B)=4.80, solape robusto al artefacto del primer pivote). PERO la lectura correcta
NO es "la via esta muerta": max(amp) de todo el set = 6.07 mientras i_swingDomAtr = 8.0 => NINGUN pool
alcanza el umbral de "swing dominante" ya existente => v10 y ese umbral no hablan de lo mismo. La
maquina de la que sale el 8.0 (:2232-2251) usa i_swingStructLen=20, no i_swingLen=5.
Mismo fallo que S129 (probe midiendo la lectura equivocada) y S130 (no era el ancla, era la ESCALA).

QUE MIDE. En vez de otro viaje de ida y vuelta: TODAS las escalas a la vez. Replica la maquina
leg-based de :2232-2251 para L in {5, 10, 20, 50, 100} con registro PROPIO y SIN CAP. Por que propio
y no SMC_majorSwingsV: ese array es FIFO con i_swingMaxKeep=350 (:2129) => pudo desalojar los tramos
de 2014 y dejar SIN MATCH los pools viejos (el pool mas viejo tiene edad 6276 barras).

PREDICCIONES (escritas ANTES de medir — doc §5bis):
  P-A6  (LA QUE DECIDE) Existe alguna L in {10,20,50,100} con P_margen_L > 0 (separacion limpia
        min(amp_A) > max(amp_B)). Si NINGUNA separa => la amplitud no es la propiedad => VIA MUERTA.
  P-A7  La L que separa es >= 20, y en L=20 P_maxAmp_20 alcanza el entorno de i_swingDomAtr=8.0
        => confirma el diagnostico de desajuste de escala de v10.
  P-A8  P_maxAmp_L crece monotonamente con L.

ANTI-HUMO (S128 midio humo; v10 lo atrapo con nAmpCeroPiv):
  - P_nPiv_L por escala: si es 0, esa escala no registro nada y sus lecturas son basura.
  - P_nAmpCeroPiv_L: el fallback 0.0 (na(prev) o ATR<=0). Debe ser 1 por escala (el primer pivote).
  - P_nHitA_L / P_nHitB_L: cobertura del contraste. Si nHitA < 4 la comparacion esta incompleta.
    OJO: 1.60063 del grupo A NO casa con el pool 1.60389 (32.6 pips > TOL_GRP=30) => se AMPLIA
    TOL_GRP a 40 pips para que los 5 de A entren. Documentado, no silencioso.
  - EXCLUSION DEL ARTEFACTO: el primer pivote de la historia tiene amp=0.0 por no tener anterior.
    v10 lo conto y contamino minAmpA. Aqui amp<=0 se EXCLUYE del min/max (bAmp > 0.0), y se cuenta
    aparte en P_nExcl_L.
  - P_marker = 1321, nuevo por build (S127/S129/S130/S131).
  - data_get_pine_labels NO sigue el crosshair; data_get_study_values SI (raton al borde derecho).
TRUNCADO en "// === DIBUJO ===" (CE10117).

Uso:
  python scripts/gen_probe_amplitud_escala.py
"""
import sys, os, pathlib

SRC = pathlib.Path(__file__).resolve().parent.parent / "pine" / "SMC-Visual.pine"
OUT = pathlib.Path(os.environ.get("TEMP", ".")) / "PROBE-amplitud-escala-S132.pine"
MARKER = 1321

ESCALAS = [5, 10, 20, 50, 100]

GRUPO_A = [0.90494, 0.95360, 1.02108, 1.39972, 1.60063]
GRUPO_B = [1.036, 1.0733, 1.10654, 1.12105, 1.13246, 1.1473]
TOL_GRP = 0.0040   # 40 pips: v10 con 30 dejo fuera 1.60063 (pool real 1.60389, a 32.6 pips).

s = SRC.read_text(encoding="utf-8")

for needed in ("float sAtr14        = ta.atr(14)",
               "f_prunePoolsV(SMC_pools, MAX_POOLS_CHART)",
               "float ampH = na(legPrev) or sAtr14 <= 0 ? 0.0 : math.abs(legPh - legPrev) / sAtr14"):
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

lit_a = ", ".join(str(x) for x in GRUPO_A)
lit_b = ", ".join(str(x) for x in GRUPO_B)

# --- Maquina leg-based replicada por escala (copia literal de :2232-2251, con registro sin cap).
maquinas = []
for L in ESCALAS:
    maquinas.append(f"""
// escala L={L}
var array<float> lv{L} = array.new_float()
var array<float> am{L} = array.new_float()
var float pv{L} = na
var int   st{L} = 0
var int   np{L} = 0
var int   nz{L} = 0
float hiN{L} = ta.highest({L})
float loN{L} = ta.lowest({L})
if barstate.isconfirmed
    int pr{L} = st{L}
    if high[{L}] > hiN{L}
        st{L} := 0
    else if low[{L}] < loN{L}
        st{L} := 1
    if st{L} != pr{L} and st{L} == 0
        float p{L} = high[{L}]
        float a{L} = na(pv{L}) or sAtr14 <= 0 ? 0.0 : math.abs(p{L} - pv{L}) / sAtr14
        if a{L} == 0.0
            nz{L} += 1
        array.push(lv{L}, p{L})
        array.push(am{L}, a{L})
        pv{L} := p{L}
        np{L} += 1
    if st{L} != pr{L} and st{L} == 1
        float q{L} = low[{L}]
        float b{L} = na(pv{L}) or sAtr14 <= 0 ? 0.0 : math.abs(q{L} - pv{L}) / sAtr14
        if b{L} == 0.0
            nz{L} += 1
        array.push(lv{L}, q{L})
        array.push(am{L}, b{L})
        pv{L} := q{L}
        np{L} += 1""")

# --- Contraste A vs B por escala, en islast.
contrastes = []
for L in ESCALAS:
    contrastes.append(f"""
float minA{L} = 1e9
float maxB{L} = -1.0
float maxAll{L} = -1.0
int   hitA{L} = 0
int   hitB{L} = 0
int   nEx{L}  = 0
if barstate.islast
    int nP{L} = array.size(SMC_pools)
    if nP{L} > 0
        for i = 0 to nP{L} - 1
            SMC_Pool p = array.get(SMC_pools, i)
            if not p.swept
                float bs = 1e9
                float ba = -1.0
                if array.size(lv{L}) > 0
                    for j = 0 to array.size(lv{L}) - 1
                        float d = math.abs(array.get(lv{L}, j) - p.level)
                        if d < bs
                            bs := d
                            ba := array.get(am{L}, j)
                if bs > {TOL_GRP}
                    ba := -1.0
                // EXCLUSION del artefacto: amp <= 0 no es una medida, es el fallback de :2246.
                if ba <= 0.0
                    nEx{L} += 1
                else
                    if ba > maxAll{L}
                        maxAll{L} := ba
                    bool eA = false
                    bool eB = false
                    for k = 0 to array.size(gA) - 1
                        if math.abs(p.level - array.get(gA, k)) <= {TOL_GRP}
                            eA := true
                    for k = 0 to array.size(gB) - 1
                        if math.abs(p.level - array.get(gB, k)) <= {TOL_GRP}
                            eB := true
                    if eA
                        hitA{L} += 1
                        if ba < minA{L}
                            minA{L} := ba
                    if eB
                        hitB{L} += 1
                        if ba > maxB{L}
                            maxB{L} := ba""")

plots = []
for L in ESCALAS:
    plots.append(f"""plot(np{L},   "P_nPiv_{L}")
plot(nz{L},   "P_nAmpCeroPiv_{L}")
plot(nEx{L},  "P_nExcl_{L}")
plot(hitA{L}, "P_nHitA_{L}")
plot(hitB{L}, "P_nHitB_{L}")
plot(minA{L}, "P_minAmpA_{L}")
plot(maxB{L}, "P_maxAmpB_{L}")
plot(minA{L} - maxB{L}, "P_margen_{L}")
plot(maxAll{L}, "P_maxAmp_{L}")""")

maq = "\n".join(maquinas)
con = "\n".join(contrastes)
plt = "\n".join(plots)

# Volcado: una fila por pool vivo con la amplitud en CADA escala.
cols = " + \"|\" + ".join(f'str.tostring(d{L}, "#.##")' for L in ESCALAS)
calcs = "\n".join(f"""                float s{L} = 1e9
                float d{L} = -1.0
                if array.size(lv{L}) > 0
                    for j = 0 to array.size(lv{L}) - 1
                        float e = math.abs(array.get(lv{L}, j) - p.level)
                        if e < s{L}
                            s{L} := e
                            d{L} := array.get(am{L}, j)
                if s{L} > {TOL_GRP}
                    d{L} := -1.0""" for L in ESCALAS)

PROBE = f"""

// --- [S132 · PROBE v11: amplitud del swing — BARRIDO DE ESCALA]
// Replica de la maquina leg-based (:2232-2251) para L in {ESCALAS}, registro propio SIN cap.
// NO se toca el CORE: registros paralelos de solo lectura sobre high/low.
array<float> gA = array.from({lit_a})
array<float> gB = array.from({lit_b})
{maq}
{con}

plot({MARKER}, "P_marker")
plot(close,    "P_close")
{plt}

// --- VOLCADO: pools VIVOS con su amplitud en CADA escala.
// RE10045: NADA de array.push en islast -> string acumulador.
if barstate.islast
    string dump = "POOL|grupo|amp{'|amp'.join(str(x) for x in ESCALAS)}\\n"
    if array.size(SMC_pools) > 0
        for i = 0 to array.size(SMC_pools) - 1
            SMC_Pool p = array.get(SMC_pools, i)
            if not p.swept
{calcs}
                string g = "-"
                for k = 0 to array.size(gA) - 1
                    if math.abs(p.level - array.get(gA, k)) <= {TOL_GRP}
                        g := "A"
                for k = 0 to array.size(gB) - 1
                    if math.abs(p.level - array.get(gB, k)) <= {TOL_GRP}
                        g := "B"
                if g != "-"
                    dump += str.tostring(p.level, "#.#####") + "|" + g + "|" + {cols} + "\\n"
    label.new(bar_index, close, dump, style = label.style_label_left, textcolor = color.white, size = size.small)
"""

s = s + PROBE
OUT.write_text(s, encoding="utf-8")
print(f"Variante: amplitud por ESCALA {ESCALAS} — contraste A vs B (marker={MARKER})")
print(f"grupo A ({len(GRUPO_A)}): {GRUPO_A}")
print(f"grupo B ({len(GRUPO_B)}): {GRUPO_B}")
print(f"tolerancia: {TOL_GRP} ({TOL_GRP*10000:.0f} pips) — ampliada desde 30: 1.60063 no casaba con 1.60389")
print(f"\nPROBE -> {OUT}")
print(f"lineas: {lineas_antes} -> {len(s.splitlines())}")
