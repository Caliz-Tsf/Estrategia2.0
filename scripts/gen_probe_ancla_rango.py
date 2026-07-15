# -*- coding: utf-8 -*-
"""
S128 · Genera un PROBE que mide la pendiente #1 (el ancla del dealing range, Opcion A vs B),
sin tocar pine/SMC-Visual.pine. Diseno + predicciones: docs/planes/DISENO-ancla-dealing-range-S128.md

CONTEXTO. La Opcion A (trailing extremes de LuxAlgo) fue elegida en S021 y RE-CONFIRMADA por el
usuario en S057 y S091, con el cambio a B congelado hasta Fase 3 (anti-overfitting, ADR-002). Lo
unico que reabre el tema es el hallazgo de S127: el trailing que solo EXPANDE hace que el archivo
(pdPrev1/2) sea SIEMPRE anidado -> las bandas 4/5 son incapaces por construccion.

HALLAZGO DE LECTURA S128 (esto es lo que el probe va a intentar refutar):
  (a) structMajor (i_majorLen=50) YA ES el ancla de la Opcion B, y esta a la MISMA escala que
      i_pdSwingLen=50. A y B solo difieren en "expande vs no expande" entre reanclajes.
  (b) f_computeLegExtremes fase 1 (L3149-3152) ya toma la UNION mas-lejana de {pdHigh/pdLow,
      structMajor, HTF} -> el ALCANCE VIVO no depende del ancla del P/D. Cambiar A->B no lo puede
      ensanchar; en el estado de S127 (structMajor_low 1.14110 > pdLow 1.13246) incluso lo ENCOGE.
  => Si (b) es cierto, la premisa de la pendiente #1 ("el ancla define la geometria de la que
     depende el alcance") es FALSA, y lo unico que A->B puede arreglar es EL ARCHIVO (bandas 4/5).

MIDE (contadores sobre historia confirmada, no un punto suelto — el hueco de S057/S091):
  P1  P_nDisagree/P_nBars ... veredicto P/D de A vs B. Prediccion: desacuerdo < 20%.
  P2  P_nBnarrowLo vs P_nBwiderLo ... B mas estrecho por abajo. Prediccion: narrow >> wider.
  P3  P_legExtLo_id = legExtLo - min(pdLow, structMajor.lowLevel). Prediccion: 0 (identidad de la
      union) salvo clamp/snap.
  P4  LA DE LA CASA. Misma regla de rotacion (borde > 0.5xATR, copiada de L3093-3102) aplicada a
      los DOS anclajes:
        P_nA_arch_out ....... barras con archivo de A NO anidado. Prediccion: 0 (S127).
        P_nB_arch_out ....... barras con archivo de B NO anidado. Prediccion: > 0.
        P_nB_arch_belowLeg .. LA ACCIONABLE: archivo de B por DEBAJO del alcance vivo (legExtLo)
                              -> terreno nuevo que la banda 4/5 cubriria y hoy es invisible.
      Si sale 0/0 -> la Opcion B no compra nada y el re-baseline del CORE no se justifica.

TRUNCADO en "// === DIBUJO ===" (obligatorio: el Visual esta a ~79 tokens del techo, medido en el
console S127 -> anadir plots encima del Visual completo da CE10117). El chart queda EN BLANCO
mientras el probe esta aplicado: es esperado.

VERIFICAR SIEMPRE con pine_get_console que aparece "Compilado." + "Anadido al grafico"; si solo dice
"guardado", el apply NO ocurrio y cualquier lectura es de un build viejo (gotcha S127 #2: el chart va
1-2 builds por detras y data_get_study_values NO avisa). P_marker=128 es el control de identidad.

Uso:
  python scripts/gen_probe_ancla_rango.py
"""
import sys, os, pathlib

SRC = pathlib.Path(__file__).resolve().parent.parent / "pine" / "SMC-Visual.pine"
OUT = pathlib.Path(os.environ.get("TEMP", ".")) / "PROBE-ancla-rango-S128.pine"
MARKER = 1283

s = SRC.read_text(encoding="utf-8")
orig_len = len(s)

# Anclas de existencia: si el Visual se refactoriza, el probe falla RUIDOSO en vez de medir humo.
for needed in ("var SMC_Structure structMajor = SMC_Structure.new()",
               "var float legExtHi = na",
               "var float pdPrev1Hi = na",
               "f_premiumDiscount(float price, float top, float bottom, float eqLo, float eqHi) =>"):
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

PROBE = f"""

// --- [S128 · PROBE ancla del dealing range: A (trailing) vs B (estructural)] solo lee, no cambia nada.
// Sombra de la Opcion B: MISMA regla de rotacion que L3093-3102, pero alimentada por structMajor
// (= el ancla de la Opcion B, i_majorLen=50) en vez de chartState.pdHigh/pdLow (= Opcion A).
var float bPrev1Hi = na
var float bPrev1Lo = na
var float bLastHi  = na
var float bLastLo  = na
// Contadores (denominador + P1/P2/P4). Solo isconfirmed -> anti-repaint, determinista.
var int nBars          = 0
var int nDisagree      = 0
var int nBnarrowLo     = 0
var int nBwiderLo      = 0
var int nAArchOut      = 0
var int nBArchOut      = 0
var int nBArchBelowLeg = 0
var int nAArchAboveHi   = 0
var int nAArchBelowLeg  = 0
var int nAArch2BelowLeg = 0

float pdEqLo = 0.5 - i_pdEqBand / 100.0
float pdEqHi = 0.5 + i_pdEqBand / 100.0
[zA, pctA] = f_premiumDiscount(close, chartState.pdHigh, chartState.pdLow, pdEqLo, pdEqHi)
[zB, pctB] = f_premiumDiscount(close, structMajor.highLevel, structMajor.lowLevel, pdEqLo, pdEqHi)

if barstate.isconfirmed and not na(structMajor.highLevel) and not na(structMajor.lowLevel) and not na(chartState.atr14) and chartState.atr14 > 0
    bool bRot = na(bLastHi) or math.abs(structMajor.highLevel - bLastHi) > 0.5 * chartState.atr14 or math.abs(structMajor.lowLevel - bLastLo) > 0.5 * chartState.atr14
    if bRot
        if not na(bLastHi)
            bPrev1Hi := bLastHi
            bPrev1Lo := bLastLo
        bLastHi := structMajor.highLevel
        bLastLo := structMajor.lowLevel

if barstate.isconfirmed
    nBars += 1
    // P1: ¿discrepan A y B en el veredicto premium/discount/equilibrium?
    if not na(zA) and not na(zB) and zA != zB
        nDisagree += 1
    // P2: ¿B es mas estrecho por abajo que A? (si lo es, B a secas RECORTA el alcance)
    if not na(structMajor.lowLevel) and not na(chartState.pdLow)
        if structMajor.lowLevel > chartState.pdLow
            nBnarrowLo += 1
        else if structMajor.lowLevel < chartState.pdLow
            nBwiderLo += 1
    // P4: archivo NO anidado = la foto previa se sale del rango vigente => la banda 4/5 cubre terreno nuevo.
    // DECOMPUESTO POR LADO [S128 v2]: la v1 mezclaba ambos lados con un OR y no permitia saber si el
    // 19% no-anidado de A venia de ARRIBA (irrelevante) o de ABAJO (= la pendiente #2). Sin decomponer,
    // el contador no decide nada.
    if not na(pdPrev1Lo) and not na(chartState.pdLow) and not na(pdPrev1Hi) and not na(chartState.pdHigh)
        if pdPrev1Lo < chartState.pdLow or pdPrev1Hi > chartState.pdHigh
            nAArchOut += 1
        if pdPrev1Hi > chartState.pdHigh
            nAArchAboveHi += 1
    if not na(bPrev1Lo) and not na(structMajor.lowLevel) and not na(bPrev1Hi) and not na(structMajor.highLevel)
        if bPrev1Lo < structMajor.lowLevel or bPrev1Hi > structMajor.highLevel
            nBArchOut += 1
    // LAS ACCIONABLES: archivo por DEBAJO del alcance vivo -> es EXACTAMENTE lo que la banda 4 necesita
    // para cubrir terreno nuevo (f_depthBand solo mira pdPrev cuando band==0 = fuera del alcance).
    //
    // [S128 v3 · CORRECCION] La v2 comparaba contra legExtLo y media HUMO: f_updateLegExtremes solo puebla
    // legExtHi/Lo en islast (1x/vela, ultima barra) -> en TODA la historia legExtLo es na -> el guard
    // "not na(legExtLo)" nunca pasaba y los tres contadores daban 0 TRIVIALMENTE, no por evidencia.
    // Se delataba solo: nA_arch_out=1221 con nA_arch_aboveHi=541 implica >=680 barras con archivo por
    // debajo, incompatible con el 0. Proxy correcto, computable en toda la historia y con la MISMA
    // semantica: legExtLo == min(pdLow, structMajor.lowLevel) (identidad P3 medida = 0).
    float reachLo = math.min(nz(chartState.pdLow, 1e9), nz(structMajor.lowLevel, 1e9))
    if not na(pdPrev1Lo) and reachLo < 1e9 and pdPrev1Lo < reachLo
        nAArchBelowLeg += 1
    if not na(pdPrev2Lo) and reachLo < 1e9 and pdPrev2Lo < reachLo
        nAArch2BelowLeg += 1
    if not na(bPrev1Lo) and reachLo < 1e9 and bPrev1Lo < reachLo
        nBArchBelowLeg += 1

plot(nBars, "P_nBars")
plot(nDisagree, "P_nDisagree")
plot(nBnarrowLo, "P_nBnarrowLo")
plot(nBwiderLo, "P_nBwiderLo")
plot(nAArchOut, "P_nA_arch_out")
plot(nBArchOut, "P_nB_arch_out")
plot(nBArchBelowLeg, "P_nB_arch_belowLeg")
plot(nAArchAboveHi, "P_nA_arch_aboveHi")
plot(nAArchBelowLeg, "P_nA_arch_belowLeg")
plot(nAArch2BelowLeg, "P_nA_arch2_belowLeg")
// P3: identidad de la union (0 => legExtLo == min(pdLow, structMajor.lowLevel), salvo clamp/snap).
plot(legExtLo - math.min(nz(chartState.pdLow, 1e9), nz(structMajor.lowLevel, 1e9)), "P_legExtLo_id")
plot(pctA, "P_pctA")
plot(pctB, "P_pctB")
plot(chartState.pdHigh, "P_pdHigh")
plot(chartState.pdLow, "P_pdLow")
plot(structMajor.highLevel, "P_structMajor_high")
plot(structMajor.lowLevel, "P_structMajor_low")
plot(legExtLo, "P_legExtLo")
plot(bPrev1Lo, "P_bPrev1Lo")
plot(close, "P_close")
plot({MARKER}, "P_marker")
"""

s = s + PROBE
OUT.write_text(s, encoding="utf-8")
print(f"Variante: ancla del rango A vs B (18 plots; marker={MARKER})")
print(f"\nPROBE -> {OUT}")
print(f"lineas: {lineas_antes} -> {len(s.splitlines())}")
print(f"bytes : {orig_len} -> {len(s)}  (delta {len(s)-orig_len:+d})")
