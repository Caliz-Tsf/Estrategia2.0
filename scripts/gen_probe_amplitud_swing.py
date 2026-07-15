# -*- coding: utf-8 -*-
"""
S132 · PROBE v10 — la amplitud del swing como propiedad del pool.

QUE MIDE. docs/planes/DISENO-amplitud-de-swing-S132.md. S131 refuto con medicion las cuatro vias
baratas (toques, barrido de i_poolTol, escala fija, ventana close+-X, escala por ATR). Queda UNA
propiedad que el ojo del usuario usa y el motor no registra: la AMPLITUD DEL SWING que creo el pool.

EL HALLAZGO QUE ABARATA ESTO (S132): la amplitud YA se calcula en :2246
    ampH = math.abs(legPh - legPrev) / sAtr14
en la maquina leg-based de S117 (L2232-2251, FUERA del CORE). Lo que falta NO es calcularla: es que
SMC_Pool (:266) la RECUERDE — f_upsertPool (:1363) recibe solo 'level'. Por eso la MEDICION cabe
entera fuera del CORE; solo el FIX (si sale verde) rompe el SHA.

DEFINICION DECLARADA ANTES DE MEDIR (leccion S129 §3 — el diseno ambiguo hizo medir la lectura
equivocada durante una sesion entera). "Amplitud del swing que creo el pool" es ambigua entre:
  (a) AMPLITUD DE LLEGADA — |level - pivote anterior| / ATR: cuanto recorrio el precio para LLEGAR.
      ES LA QUE MIDE ESTE PROBE (la misma formula de :2246).
  (b) amplitud de salida — cuanto se alejo DESPUES. Necesita el pivote siguiente => no disponible en
      el upsert => descartada (ademas huele a lookahead).

PREDICCIONES (escritas ANTES de medir — van 18 vivas de 37; detalle en el doc §5):
  P-A1  (LA QUE DECIDE) Existe umbral T que separa A de B SIN SOLAPE: P_minAmpA > P_maxAmpB
        => P_margen > 0. Cualquier solape mata la via entera.
  P-A2  El margen es holgado, no marginal: P_minAmpA >= 1.5 * P_maxAmpB => P_ratio >= 1.5.
  P-A3  T cae en el entorno de i_swingDomAtr=8.0 (rango 4-15) => no hace falta input nuevo.
  P-A4  Los 5 de A quedan en el top-8 del set ordenado por amplitud desc => P_rankMaxA <= 8.
  P-A5  La amplitud NO es proxy de los toques: de los 3 pools con touches>=2 (1.51421, 1.25753,
        0.97175), ninguno entra en el top-5 por amplitud => P_nT2enTop5 == 0.

ANTI-HUMO (S128: el arnes v2 midio HUMO — legExtHi/Lo solo se poblaban en islast => contadores 0
triviales; se delato por aritmetica):
  - P_nAmpCero / P_nSinMatch: :2246 devuelve 0.0 como FALLBACK SILENCIOSO cuando na(legPrev) o
    ATR<=0. Si las amplitudes salen todas 0, este probe mide humo y hay que saberlo SIN dudar.
  - P_nPoolsDump debe == P_nAlive (si no, el volcado miente).
  - P_nHitA / P_nHitB: cuantos de los 5+6 niveles esperados se encontraron REALMENTE en el set.
    Si P_nHitA < 5, el contraste A-vs-B esta incompleto y P-A1 NO es concluyente.
  - P_marker = 1320, nuevo por build: unico distintivo fresco/rancio (S127/S129/S130/S131).
  - data_get_pine_labels NO sigue el crosshair (canal correcto para censos de N filas — gotcha S131);
    data_get_study_values SI lo sigue.
TRUNCADO en "// === DIBUJO ===" (CE10117 — el Visual completo + probe no cabe).

Uso:
  python scripts/gen_probe_amplitud_swing.py
"""
import sys, os, pathlib

SRC = pathlib.Path(__file__).resolve().parent.parent / "pine" / "SMC-Visual.pine"
OUT = pathlib.Path(os.environ.get("TEMP", ".")) / "PROBE-amplitud-swing-S132.pine"
MARKER = 1320

# Los dos grupos a separar (niveles MEDIDOS en S131, set D1 con i_poolTol=0.1, precio 1.14660).
GRUPO_A = [0.90494, 0.95360, 1.02108, 1.39972, 1.60063]                  # los que el usuario SI marca
GRUPO_B = [1.036, 1.0733, 1.10654, 1.12105, 1.13246, 1.1473]             # los que descarta
TOL_GRP = 0.0030   # 30 pips: misma tolerancia generosa que S131 (si no hay hit ni asi, es solido).

s = SRC.read_text(encoding="utf-8")

# Anclas que el probe necesita tal cual. Si el CORE/Visual cambio -> fallar RUIDOSO, no medir humo.
for needed in ("[swingHigh, swingLow] = f_detectSwings(i_swingLen)",
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

# Los grupos como arrays Pine: se recorren en islast para clasificar cada pool vivo.
lit_a = ", ".join(str(x) for x in GRUPO_A)
lit_b = ", ".join(str(x) for x in GRUPO_B)

PROBE = f"""

// --- [S132 · PROBE v10: la amplitud del swing como propiedad del pool]
// Registro SOMBRA de (nivel de pivote -> amplitud de llegada en ATR). Misma formula que :2246, pero
// sobre los MISMOS pivotes que alimentan los pools (f_detectSwings(i_swingLen), :2164) — no sobre la
// maquina leg-based de :2232, que usa otra sensibilidad (i_swingStructLen) y otro set.
// NO se toca el CORE: esto es un registro paralelo, de solo lectura sobre swingHigh/swingLow.
var array<float> pvLvl = array.new_float()
var array<float> pvAmp = array.new_float()
var float prevPiv = na
var int   nPiv     = 0
var int   nAmpCeroPiv = 0

if barstate.isconfirmed
    // Anti-repaint: swingHigh/swingLow ya vienen desplazados i_swingLen barras (pivote confirmado).
    if not na(swingHigh)
        float aH = na(prevPiv) or atr14 <= 0 ? 0.0 : math.abs(swingHigh - prevPiv) / atr14
        if aH == 0.0
            nAmpCeroPiv += 1
        array.push(pvLvl, swingHigh)
        array.push(pvAmp, aH)
        prevPiv := swingHigh
        nPiv += 1
    if not na(swingLow)
        float aL = na(prevPiv) or atr14 <= 0 ? 0.0 : math.abs(swingLow - prevPiv) / atr14
        if aL == 0.0
            nAmpCeroPiv += 1
        array.push(pvLvl, swingLow)
        array.push(pvAmp, aL)
        prevPiv := swingLow
        nPiv += 1

// --- CENSO + CONTRASTE A vs B en la ultima barra (estado final, explicitamente en islast).
int   nAlive     = 0
int   nPoolsDump = 0
int   nSinMatch  = 0    // pools vivos sin pivote asociado (EQH/EQL entran con weight 2, no son swings)
int   nAmpCero   = 0    // ANTI-HUMO: si esto == nAlive, el probe mide humo
int   nHitA      = 0
int   nHitB      = 0
float minAmpA    = 1e9
float maxAmpB    = -1.0
int   rankMaxA   = -1   // peor ranking (por amplitud desc) entre los de A -> P-A4
int   nT2enTop5  = 0    // P-A5: pools con touches>=2 dentro del top-5 por amplitud

if barstate.islast
    array<float> gA = array.from({lit_a})
    array<float> gB = array.from({lit_b})
    int nP = array.size(SMC_pools)
    // 1a pasada: amplitud de cada pool vivo (match al pivote mas cercano) + min/max por grupo.
    array<float> aLvl = array.new_float()
    array<float> aAmp = array.new_float()
    array<int>   aTch = array.new_int()
    if nP > 0
        for i = 0 to nP - 1
            SMC_Pool p = array.get(SMC_pools, i)
            if not p.swept
                nAlive += 1
                // match: el pivote registrado mas cercano al nivel del pool.
                float best  = 1e9
                float bAmp  = -1.0
                if array.size(pvLvl) > 0
                    for j = 0 to array.size(pvLvl) - 1
                        float d = math.abs(array.get(pvLvl, j) - p.level)
                        if d < best
                            best := d
                            bAmp := array.get(pvAmp, j)
                if best > {TOL_GRP}
                    nSinMatch += 1
                    bAmp := -1.0
                if bAmp == 0.0
                    nAmpCero += 1
                array.push(aLvl, p.level)
                array.push(aAmp, bAmp)
                array.push(aTch, p.touches)
                // clasificacion A / B por tolerancia.
                bool esA = false
                bool esB = false
                for k = 0 to array.size(gA) - 1
                    if math.abs(p.level - array.get(gA, k)) <= {TOL_GRP}
                        esA := true
                for k = 0 to array.size(gB) - 1
                    if math.abs(p.level - array.get(gB, k)) <= {TOL_GRP}
                        esB := true
                if esA and bAmp >= 0.0
                    nHitA += 1
                    if bAmp < minAmpA
                        minAmpA := bAmp
                if esB and bAmp >= 0.0
                    nHitB += 1
                    if bAmp > maxAmpB
                        maxAmpB := bAmp
    nPoolsDump := array.size(aLvl)
    // 2a pasada: ranking por amplitud desc. rank de un pool = cuantos lo superan + 1.
    if nPoolsDump > 0
        for i = 0 to nPoolsDump - 1
            float ai = array.get(aAmp, i)
            int   rk = 1
            for j = 0 to nPoolsDump - 1
                if array.get(aAmp, j) > ai
                    rk += 1
            float li = array.get(aLvl, i)
            bool esA2 = false
            for k = 0 to array.size(gA) - 1
                if math.abs(li - array.get(gA, k)) <= {TOL_GRP}
                    esA2 := true
            if esA2 and rk > rankMaxA
                rankMaxA := rk
            if rk <= 5 and array.get(aTch, i) >= 2
                nT2enTop5 += 1

plot(nBarsProbe_dummy_unused_guard_0, "P_guard") == na ? na : na
"""

# El guard de arriba es un error deliberado si se cuela: se elimina. (defensivo — nunca debe salir)
PROBE = PROBE.replace('plot(nBarsProbe_dummy_unused_guard_0, "P_guard") == na ? na : na\n', "")

PROBE += f"""
plot({MARKER}, "P_marker")
plot(close,    "P_close")

// ANTI-HUMO — leer ESTOS PRIMERO. Si P_nAmpCero == P_nAlive, el probe mide humo (fallback 0.0 de
// :2246 con na(legPrev)/ATR<=0) y NINGUNA otra lectura vale.
plot(nPiv,        "P_nPiv")
plot(nAmpCeroPiv, "P_nAmpCeroPiv")
plot(nAmpCero,    "P_nAmpCero")
plot(nSinMatch,   "P_nSinMatch")
plot(nAlive,      "P_nAlive")
plot(nPoolsDump,  "P_nPoolsDump")
plot(nPoolsDump - nAlive, "P_xcheckDump")

// Cobertura del contraste: si P_nHitA < 5, A-vs-B esta INCOMPLETO y P-A1 no es concluyente.
plot(nHitA, "P_nHitA")
plot(nHitB, "P_nHitB")

// P-A1 (LA QUE DECIDE): P_margen > 0 <=> existe umbral T que separa A de B sin solape.
plot(minAmpA, "P_minAmpA")
plot(maxAmpB, "P_maxAmpB")
plot(minAmpA - maxAmpB, "P_margen")
// P-A2: holgura. >= 1.5 predicho.
plot(maxAmpB > 0 ? minAmpA / maxAmpB : na, "P_ratio")
// P-A3: T en el entorno de i_swingDomAtr=8.0 (rango 4-15 predicho). T = punto medio del hueco.
plot((minAmpA + maxAmpB) / 2, "P_Tmedio")
plot(i_swingDomAtr, "P_swingDomAtr")
// P-A4: peor ranking por amplitud entre los de A. <= 8 predicho.
plot(rankMaxA, "P_rankMaxA")
// P-A5: pools con touches>=2 en el top-5 por amplitud. 0 predicho.
plot(nT2enTop5, "P_nT2enTop5")

// --- VOLCADO: pools VIVOS uno a uno (nivel | toques | amplitud_ATR | edad_velas | grupo).
// Por que un label y no plots: son ~38 filas, no caben en plots. Se lee con data_get_pine_labels.
// RE10045: NADA de array.push en islast (revienta el limite de recursos) -> string acumulador.
if barstate.islast
    array<float> gA2 = array.from({lit_a})
    array<float> gB2 = array.from({lit_b})
    string dump = "POOLS VIVOS (nivel|toques|ampATR|edad|grupo)\\n"
    if array.size(SMC_pools) > 0
        for i = 0 to array.size(SMC_pools) - 1
            SMC_Pool p = array.get(SMC_pools, i)
            if not p.swept
                float best = 1e9
                float bAmp = -1.0
                if array.size(pvLvl) > 0
                    for j = 0 to array.size(pvLvl) - 1
                        float d = math.abs(array.get(pvLvl, j) - p.level)
                        if d < best
                            best := d
                            bAmp := array.get(pvAmp, j)
                if best > {TOL_GRP}
                    bAmp := -1.0
                string g = "-"
                for k = 0 to array.size(gA2) - 1
                    if math.abs(p.level - array.get(gA2, k)) <= {TOL_GRP}
                        g := "A"
                for k = 0 to array.size(gB2) - 1
                    if math.abs(p.level - array.get(gB2, k)) <= {TOL_GRP}
                        g := "B"
                dump += str.tostring(p.level, "#.#####") + "|" + str.tostring(p.touches) + "|" + str.tostring(bAmp, "#.##") + "|" + str.tostring(bar_index - p.barIdx) + "|" + g + "\\n"
    label.new(bar_index, close, dump, style = label.style_label_left, textcolor = color.white, size = size.small)
"""

s = s + PROBE
OUT.write_text(s, encoding="utf-8")
print(f"Variante: amplitud de swing por pool — contraste A vs B (marker={MARKER})")
print(f"grupo A (usuario, {len(GRUPO_A)}): {GRUPO_A}")
print(f"grupo B (descartados, {len(GRUPO_B)}): {GRUPO_B}")
print(f"tolerancia de clasificacion: {TOL_GRP} ({TOL_GRP*10000:.0f} pips)")
print(f"\nPROBE -> {OUT}")
print(f"lineas: {lineas_antes} -> {len(s.splitlines())}")
