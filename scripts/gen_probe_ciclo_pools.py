# -*- coding: utf-8 -*-
"""
S146 · PROBE — ciclo de vida de los pools: se CREAN al avanzar la tendencia?

LA FRASE DEL USUARIO (S145, literal — NORMA S132: ninguna medicion arranca sin citarla):
  "si el precio llegase a caer y romper esos bajos y no los tenemos calculados seria perdida igual"
  y el fondo: "cuando el swing termine y el precio gire, el indicador tendra que ir creando los
  SSL/BSL que la pierna completada va dejando".

EL HECHO MEDIDO QUE LO DISPARA (S145, D1 EURUSD, re-medido hoy con data_get_pine_labels):
  36 etiquetas del Visual = 1 sola de la familia POOL ("BSL ·3" en 1.51) + 35 de la escalera DOL
  (23 OH + 12 OL + 1 resumen). CERO SSL de pool. S144 registraba 4 pools vivos.

LO QUE EL CODIGO YA DICE (lectura estatica, ANTES de medir):
  - f_upsertPool (:1399) se llama en CADA swing confirmado y en cada EQH/EQL (:2685-2691) => los
    pools SI se dan de alta. "No crea pools" seria falso.
  - Pero un swing suelto entra con touches = 1, y el DIBUJO exige touches >= i_minTouches (:3943,
    :3959) con i_minTouches = input.int(2, minval = 2) (:115) => un extremo de 1 toque NO se puede
    dibujar NI SIQUIERA bajando el input. Es exactamente S131: "los toques miden congestion, el
    usuario marca extremos".
  - f_markPoolsSwept (:1425) marca barrido en cuanto high/low cruza el nivel. En bajista sostenida
    todo SSL nace y es perforado por la continuacion => 0 SSL vivos es lo CORRECTO por §3.1.
  => Hipotesis: los pools se crean y siguen vivos; lo que falla es que son INVISIBLES por el gate de
     toques. Distinto de "no se crean" y distinto de "mueren en la misma pierna". Hay que medir cual.

PREDICCIONES (escritas ANTES de medir — memoria: ~8 predicciones muertas por no escribirlas):
  P1 (LA QUE DECIDE) P_nAliveT1 >= 8 y P_nAliveT2 <= 2. Los pools existen; el gate los oculta.
  P2  P_nAliveBelowT1 >= 3. "CERO SSL" es cero SSL DIBUJABLES, no cero SSL vivos.
  P3  P_pctNoDrawSSL > 50%. Mas de la mitad de la historia sin objetivo SSL dibujable.
  P4  P_medLife (proxy: P_sumAge/P_nSweepEv) > i_swingLen. La sospecha "nace y muere barrido en la
      misma pierna" es FALSA: viven, solo que nunca llegan a 2 toques.
  P5  P_nBornSSL > 100 sobre la historia D1. La creacion no es el problema.
  Contra-prediccion util: si P_nBornSSL fuese ~0, la causa seria la DETECCION (newSwingLow), no el
  gate — y el fix seria otro completamente.

ANTI-HUMO (S128/S129/S130/S139):
  - Los contadores de ciclo corren sobre TODA la historia confirmada (P_nBars de denominador). Solo
    el censo final se lee en islast, y se declara como tal.
  - Cross-checks aritmeticos: P_xcheckCenso (alive+swept-total) y P_xcheckT (T1+T2-alive) deben ser 0.
  - Descompuesto POR LADO (S128: el bug de legExtHi/Lo se delato por lado).
  - P_marker nuevo por build: unico distintivo fresco/rancio.
  - Alta vs merge se miden por DELTA DE TAMANO alrededor de la llamada: no toca f_upsertPool ni el
    CORE, y no depende de re-implementar su criterio de match (que seria medir mi copia, no el suyo).

TRUNCADO en "// === DIBUJO ===" (CE10117 — el Visual completo + probe no cabe).

Uso:
  python scripts/gen_probe_ciclo_pools.py
"""
import sys, os, pathlib

SRC = pathlib.Path(__file__).resolve().parent.parent / "pine" / "SMC-Visual.pine"
OUT = pathlib.Path(os.environ.get("TEMP", ".")) / "PROBE-ciclo-pools-S146.pine"
MARKER = 1460

s = SRC.read_text(encoding="utf-8")

# --- Anclas: si el CORE cambio, fallar RUIDOSO en vez de medir humo.
BLOQUE = """SMC_Event evSweepAlert = na
if barstate.isconfirmed
    if newSwingHigh
        f_upsertPool(SMC_pools, true,  swingHigh, 1, time[i_swingLen], bar_index - i_swingLen, i_poolTol * atr14)
    if newSwingLow
        f_upsertPool(SMC_pools, false, swingLow,  1, time[i_swingLen], bar_index - i_swingLen, i_poolTol * atr14)
    if not na(evEqHigh)
        f_upsertPool(SMC_pools, true,  evEqHigh.price, 2, evEqHigh.barTime, evEqHigh.barIdx, i_poolTol * atr14)
    if not na(evEqLow)
        f_upsertPool(SMC_pools, false, evEqLow.price,  2, evEqLow.barTime, evEqLow.barIdx, i_poolTol * atr14)
    f_markPoolsSwept(SMC_pools, high, low, time, bar_index)
"""
if s.count(BLOQUE) != 1:
    print(f"[FALLO] el bloque upsert->mark no aparece exactamente 1 vez (encontro {s.count(BLOQUE)})")
    sys.exit(1)

# M1 (alta vs merge) + M2 (edad al ser barrido) instrumentados EN SITIO, sin tocar el CORE.
BLOQUE_NUEVO = """var int nBornBSL   = 0
var int nBornSSL   = 0
var int nMergeBSL  = 0
var int nMergeSSL  = 0
var int nSweepEv   = 0
var int nSweepBSL  = 0
var int nSweepSSL  = 0
var int sumAge     = 0
var int nDieSameLeg = 0
var int maxAge     = 0
SMC_Event evSweepAlert = na
if barstate.isconfirmed
    if newSwingHigh
        int pb0 = array.size(SMC_pools)
        f_upsertPool(SMC_pools, true,  swingHigh, 1, time[i_swingLen], bar_index - i_swingLen, i_poolTol * atr14)
        if array.size(SMC_pools) > pb0
            nBornBSL += 1
        else
            nMergeBSL += 1
    if newSwingLow
        int pb1 = array.size(SMC_pools)
        f_upsertPool(SMC_pools, false, swingLow,  1, time[i_swingLen], bar_index - i_swingLen, i_poolTol * atr14)
        if array.size(SMC_pools) > pb1
            nBornSSL += 1
        else
            nMergeSSL += 1
    if not na(evEqHigh)
        int pb2 = array.size(SMC_pools)
        f_upsertPool(SMC_pools, true,  evEqHigh.price, 2, evEqHigh.barTime, evEqHigh.barIdx, i_poolTol * atr14)
        if array.size(SMC_pools) > pb2
            nBornBSL += 1
        else
            nMergeBSL += 1
    if not na(evEqLow)
        int pb3 = array.size(SMC_pools)
        f_upsertPool(SMC_pools, false, evEqLow.price,  2, evEqLow.barTime, evEqLow.barIdx, i_poolTol * atr14)
        if array.size(SMC_pools) > pb3
            nBornSSL += 1
        else
            nMergeSSL += 1
    f_markPoolsSwept(SMC_pools, high, low, time, bar_index)
    // M2: edad al morir. p.barIdx = ultimo refuerzo (en un pool de 1 toque == su nacimiento).
    // Se mide EN EL INSTANTE del barrido: un censo final estaria sesgado por el prune (cap 80).
    if array.size(SMC_pools) > 0
        for si = 0 to array.size(SMC_pools) - 1
            SMC_Pool sp = array.get(SMC_pools, si)
            if sp.swept and sp.sweptBarIdx == bar_index
                int spAge = bar_index - sp.barIdx
                nSweepEv += 1
                sumAge   += spAge
                if spAge > maxAge
                    maxAge := spAge
                if spAge <= i_swingLen
                    nDieSameLeg += 1
                if sp.dir == DIR_BULL
                    nSweepBSL += 1
                else
                    nSweepSSL += 1
"""
s = s.replace(BLOQUE, BLOQUE_NUEVO)

MARK = "// === DIBUJO ==="
if s.count(MARK) != 1:
    print(f"[FALLO] marcador de truncado no unico: {s.count(MARK)}")
    sys.exit(1)
lineas_antes = len(s.splitlines())
s = s[:s.index(MARK)]
print(f"[truncado] render eliminado en {MARK!r}: {lineas_antes} -> {len(s.splitlines())} lineas")

PROBE = f"""

// --- [S146 · PROBE: ciclo de vida de los pools]
// M3: hay OBJETIVO DIBUJABLE por lado, barra a barra? "Dibujable" = vivo + touches >= i_minTouches
// + del lado correcto respecto a close (es la condicion exacta de :3943/:3959). aliveT1 cuenta los
// que existen pero el gate esconde: la diferencia entre ambos ES el defecto, si lo hay.
var int nBarsP      = 0
var int nNoDrawSSL  = 0
var int nNoDrawBSL  = 0
var int nNoAliveSSL = 0
var int nNoAliveBSL = 0
if barstate.isconfirmed
    nBarsP += 1
    int dS = 0
    int dB = 0
    int aS = 0
    int aB = 0
    if array.size(SMC_pools) > 0
        for mi = 0 to array.size(SMC_pools) - 1
            SMC_Pool mp = array.get(SMC_pools, mi)
            if not mp.swept
                if mp.dir == DIR_BEAR and mp.level <= close
                    aS += 1
                    if mp.touches >= i_minTouches
                        dS += 1
                if mp.dir == DIR_BULL and mp.level >= close
                    aB += 1
                    if mp.touches >= i_minTouches
                        dB += 1
    if dS == 0
        nNoDrawSSL += 1
    if dB == 0
        nNoDrawBSL += 1
    if aS == 0
        nNoAliveSSL += 1
    if aB == 0
        nNoAliveBSL += 1

// --- CENSO del set en la ULTIMA barra (estado final; explicitamente en islast).
int   nPools         = 0
int   nAlive         = 0
int   nSwept         = 0
int   nAliveT1       = 0
int   nAliveT2       = 0
int   nAliveT3       = 0
int   nAliveBelowT1  = 0
int   nAliveBelowT2  = 0
int   nAliveAboveT1  = 0
int   nAliveAboveT2  = 0
float maxAliveLvl    = na
float minAliveLvl    = na
if barstate.islast
    nPools := array.size(SMC_pools)
    if nPools > 0
        for i = 0 to nPools - 1
            SMC_Pool p = array.get(SMC_pools, i)
            if p.swept
                nSwept += 1
            else
                nAlive += 1
                if p.touches == 1
                    nAliveT1 += 1
                if p.touches >= 2
                    nAliveT2 += 1
                if p.touches >= 3
                    nAliveT3 += 1
                if p.dir == DIR_BEAR and p.level <= close
                    if p.touches == 1
                        nAliveBelowT1 += 1
                    else
                        nAliveBelowT2 += 1
                    if na(minAliveLvl) or p.level < minAliveLvl
                        minAliveLvl := p.level
                if p.dir == DIR_BULL and p.level >= close
                    if p.touches == 1
                        nAliveAboveT1 += 1
                    else
                        nAliveAboveT2 += 1
                    if na(maxAliveLvl) or p.level > maxAliveLvl
                        maxAliveLvl := p.level

plot(nBarsP,   "P_nBars")
plot({MARKER},  "P_marker")
plot(close,    "P_close")

// M1 — ALTA vs MERGE. P5: si P_nBornSSL es alto, la creacion NO es el problema.
plot(nBornBSL,  "P_nBornBSL")
plot(nBornSSL,  "P_nBornSSL")
plot(nMergeBSL, "P_nMergeBSL")
plot(nMergeSSL, "P_nMergeSSL")

// M2 — VIDA. P4: edad media al morir vs i_swingLen. nDieSameLeg = barridos en <= swingLen velas.
plot(nSweepEv,    "P_nSweepEv")
plot(nSweepBSL,   "P_nSweepBSL")
plot(nSweepSSL,   "P_nSweepSSL")
plot(sumAge,      "P_sumAge")
plot(nSweepEv > 0 ? sumAge / nSweepEv : na, "P_avgLife")
plot(nDieSameLeg, "P_nDieSameLeg")
plot(maxAge,      "P_maxAge")

// M3 — OBJETIVO DISPONIBLE. P3: pct de barras sin SSL dibujable.
plot(nNoDrawSSL,  "P_nNoDrawSSL")
plot(nNoDrawBSL,  "P_nNoDrawBSL")
plot(nNoAliveSSL, "P_nNoAliveSSL")
plot(nNoAliveBSL, "P_nNoAliveBSL")
plot(nBarsP > 0 ? math.round(100.0 * nNoDrawSSL  / nBarsP) : na, "P_pctNoDrawSSL")
plot(nBarsP > 0 ? math.round(100.0 * nNoDrawBSL  / nBarsP) : na, "P_pctNoDrawBSL")
plot(nBarsP > 0 ? math.round(100.0 * nNoAliveSSL / nBarsP) : na, "P_pctNoAliveSSL")

// M4 — CENSO FINAL. P1/P2: T1 (existe, invisible) vs T2 (dibujable).
plot(nPools,        "P_nPools")
plot(nAlive,        "P_nAlive")
plot(nSwept,        "P_nSwept")
plot(nAlive + nSwept - nPools, "P_xcheckCenso")
plot(nAliveT1,      "P_nAliveT1")
plot(nAliveT2,      "P_nAliveT2")
plot(nAliveT3,      "P_nAliveT3")
plot(nAliveT1 + nAliveT2 - nAlive, "P_xcheckT")
plot(nAliveBelowT1, "P_nAliveBelowT1")
plot(nAliveBelowT2, "P_nAliveBelowT2")
plot(nAliveAboveT1, "P_nAliveAboveT1")
plot(nAliveAboveT2, "P_nAliveAboveT2")
plot(minAliveLvl,   "P_minAliveLvl")
plot(maxAliveLvl,   "P_maxAliveLvl")

// Control: el gate vigente, para que el censo se lea contra su umbral real.
plot(i_minTouches, "P_minTouches")
plot(i_swingLen,   "P_swingLen")

// --- VOLCADO: pools VIVOS uno a uno (nivel|toques|lado|edad_velas).
// RE10045: NADA de array.push en islast -> string acumulador.
if barstate.islast
    string dump = "POOLS VIVOS (nivel|toques|lado|edad)\\n"
    if array.size(SMC_pools) > 0
        for i = 0 to array.size(SMC_pools) - 1
            SMC_Pool p = array.get(SMC_pools, i)
            if not p.swept
                dump += str.tostring(p.level, "#.#####") + "|" + str.tostring(p.touches) + "|" + (p.dir == DIR_BULL ? "BSL" : "SSL") + "|" + str.tostring(bar_index - p.barIdx) + "\\n"
    label.new(bar_index, close, dump, style = label.style_label_left, textcolor = color.white, size = size.small)
"""

s = s + PROBE
OUT.write_text(s, encoding="utf-8")
print(f"Variante: ciclo de vida de pools — alta/merge + edad al barrido + objetivo dibujable (marker={MARKER})")
print(f"\nPROBE -> {OUT}")
print(f"lineas: {lineas_antes} -> {len(s.splitlines())}")
