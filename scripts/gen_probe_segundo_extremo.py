# -*- coding: utf-8 -*-
"""
S133 · PROBE v14 — EL 2.º EXTREMO ESTRUCTURAL (§2.3.2), EN SOMBRA. **ES EL GATE DE LA FASE 1.**

QUE MIDE. La regla que el usuario cerro en S133 y que quedo escrita en reglas-smc-ict.md §2.3.1/§2.3.2
(commit a0ae5e4), ANTES de tocar el CORE:

  strong low  := el minimo de la pierna cuya subida rompio estructura (BOS/CHoCH alcista). §2.3.1
  histLow     := el strong low MAS BAJO      -> se marca aparte, NO entra en el rango
  pdLow       := el 2.º strong low mas bajo  -> ES el suelo del dealing range
  (simetrico arriba con eventos bajistas)

  fallback en cascada (garantiza pct en [0,1], requisito literal del usuario):
    close >= pdLow            -> suelo = pdLow      (caso normal)
    histLow <= close < pdLow  -> suelo = histLow    (franja historica: el rango SE ESTIRA)
    close <  histLow          -> suelo = trailing   (rompio el historico: expande hasta el pivote nuevo)

DIFERENCIA CON EL ESQUELETO DE FABLE (refutado en S133, 4 configuraciones): el tomaba EL ULTIMO strong
high -> cada evento lo re-fijaba mas abajo -> caminaba hacia el precio (9-13x ATR de error). Aqui se toma
EL 2.º MAS ALTO DE TODOS -> no camina, no hay nada que lo re-fije. Se conserva su principio ("strong es
relacional"), se corrige la operacionalizacion.

POR QUE ES BARATO: no hace falta ordenar nada (la exploracion reporto que NO existe ordenacion por nivel
en el codigo, solo por distancia). Mantener el 1.º y el 2.º es O(1) por evento, con 4 floats y una
comparacion. Sin arrays, sin array.sort, sin array.push en islast (evita el RE10045 conocido).

EN SOMBRA: corre en PARALELO al rango vigente, no sustituye nada. `pine/` NO se toca. La decision S021
NO esta descongelada: este probe la informa.

PREDICCIONES (escritas ANTES de medir — norma S114/S132. Acumulado del proyecto ~33 de 63):

  P1  histLow (min1) de EURUSD D1 = 0.90275 +-10 pips (el minimo absoluto, medido en S129 y S133).
      FALSA si cae en otro sitio. [Facil: es un cross-check del arnes, no discrimina. Declarada facil
      de antemano para no inflar el marcador.]
  P2  pdLow (min2) de EURUSD D1 = 0.95360 +-20 pips (el 2.º pool mas bajo, edad 984, medido en S133).
      FALSA si cae en otro sitio. Es la prediccion que dice si "2.º extremo" == lo que el usuario lee.
  P3  *** LA QUE DECIDE *** pdHigh (max2) NO CAMINA: nRelatchMax2 << 41 (el nRelatch del esqueleto de
      Fable en escala 50, medido en S133). Concretamente: nRelatchMax2 <= 10 en 6284 barras.
      FALSA si se re-fija con frecuencia similar => mismo defecto que Fable => *** ABANDONO ***
  P4  pct en [0,1] en el 100% de las barras (nOutRange = 0), INCLUIDA la franja historica.
      FALSA si nOutRange > 0 => el fallback en cascada no cubre => *** ABANDONO ***
  P5  ADR-001 / multi-simbolo: en NAS100USD (alcista secular) el lado que queda congelado es el LOW,
      sin tocar una linea de codigo. Se mide con P_biasLatch (= structSwing.bias).
      FALSA si hay que hardcodear lado o simbolo => *** ABANDONO ***
  P6  El veredicto P/D difiere de la Opcion A vigente en >= 15% de las barras.
      FALSA si < 5% => no compra nada (el suelo que mato la Opcion B en S128 fue 3.2%).

ABANDONO PRE-COMPROMETIDO: P3 falsa, o P4 > 0, o P5 exige asimetria.

ANTI-HUMO (leccion S128: contadores con guard `not na()` miden humo):
  - P_nBars: denominador explicito.
  - P_nStrongLo / P_nStrongHi: cuantos strong se acumularon por lado (si un lado sale 0, el otro no vale).
  - P_nRelatchMin2 / P_nRelatchMax2: cuantas veces cambio CADA 2.º extremo (P3 se lee aqui).
  - P_nCase2Lo / P_nCase3Lo: cuantas barras cayeron en cada rama del fallback (si case2/case3 = 0, P4 es
    trivialmente verde y NO prueba nada -> hay que decirlo).
  - P_lastEvT: fecha del ultimo evento -> cruzar con el panel (BOS 17-06 / CHoCH 14-05 en D1).
  - P_marker (1340/1341) fresco verificado en CADA lectura.

GOTCHAS (memoria del proyecto — uno casi arruina S133):
  - El modal "¿Desea guardar este script antes de anadirlo?" bloquea el apply EN SILENCIO -> el marker
    sale RANCIO y se reportan los numeros de la corrida anterior. Cerrar con ui_click(text="Guardar").
  - Confirmar en pine_get_console: "Compilado." + "Anadido al grafico." (no basta "guardado").
  - Aplicar crea instancia NUEVA y TV solo deja 2 -> remover la vieja con chart_manage_indicator.
  - Las instancias viejas arrastran overrides de inputs de sesiones previas.
  - data_get_study_values sigue el CROSSHAIR; data_get_pine_labels no.
  - El numero real de tokens esta en pine_get_console, NO en pine_get_errors.

Uso:
  python scripts/gen_probe_segundo_extremo.py          # escala dominante 50 (evStructMajor) · marker 1340
  python scripts/gen_probe_segundo_extremo.py swing    # escala 5 (evStructSwing)            · marker 1341
"""
import sys, os, pathlib

ESCALA = (sys.argv[1] if len(sys.argv) > 1 else "major").lower()
if ESCALA not in ("major", "swing"):
    print(f"[FALLO] escala desconocida: {ESCALA!r} (usar: major | swing)")
    sys.exit(1)
EV     = "evStructMajor" if ESCALA == "major" else "evStructSwing"
MARKER = 1340 if ESCALA == "major" else 1341

SRC = pathlib.Path(__file__).resolve().parent.parent / "pine" / "SMC-Visual.pine"
OUT = pathlib.Path(os.environ.get("TEMP", ".")) / f"PROBE-segundo-extremo-{ESCALA}-S133.pine"

s = SRC.read_text(encoding="utf-8")

NEEDED = (
    "evStructSwing := f_detectStructure(structSwing, bar_index, time, true, true)",   # :2276 escala 5
    "evStructMajor := f_detectStructure(structMajor, bar_index, time, true, true)",   # :2292 escala 50
    "f_premiumDiscount(float price, float top, float bottom, float eqLo, float eqHi) =>",
    "var SMC_Trailing trailing = SMC_Trailing.new()",                                 # :2198 la Opcion A
    "float sAtr14        = ta.atr(14)",                                               # :2151
)
for needed in NEEDED:
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

// --- [S133 · PROBE v14: EL 2.º EXTREMO ESTRUCTURAL (§2.3.2) — EN SOMBRA]
var float rMin  = na    // min(low)  desde el ultimo evento alcista -> candidato a strong low
var float rMax  = na    // max(high) desde el ultimo evento bajista -> candidato a strong high
var float min1  = na    // histLow : el strong low MAS BAJO
var float min2  = na    // pdLow   : el 2.º strong low mas bajo
var float max1  = na    // histHigh
var float max2  = na    // pdHigh
var int nStrongLo = 0
var int nStrongHi = 0
var int nRelatchMin2 = 0
var int nRelatchMax2 = 0
var int nBars     = 0
var int nOutRange = 0
var int nDisagree = 0
var int nCase1Lo  = 0   // close >= pdLow            (caso normal)
var int nCase2Lo  = 0   // histLow <= close < pdLow  (franja historica: el rango se estira)
var int nCase3Lo  = 0   // close < histLow           (rompio el historico: trailing)
var int nCase2Hi  = 0
var int nCase3Hi  = 0
var int lastEvT   = na

float pdEqLo = 0.5 - i_pdEqBand / 100.0
float pdEqHi = 0.5 + i_pdEqBand / 100.0

if barstate.isconfirmed
    nBars += 1
    // §2.3.1 — trackers del origen de pierna (min/max de barras PASADAS -> anti-repaint [D-PINE-03]).
    rMin := na(rMin) ? low  : math.min(rMin, low)
    rMax := na(rMax) ? high : math.max(rMax, high)

    // §2.3.1 — un strong low nace SOLO cuando la pierna que empezo en el ROMPIO ESTRUCTURA.
    if not na({EV}) and ({EV}.kind == KIND_BOS or {EV}.kind == KIND_CHOCH)
        lastEvT := time
        if {EV}.dir == DIR_BULL
            float sl = rMin
            nStrongLo += 1
            rMin := low                         // la nueva pierna nace aqui
            // O(1): mantener los DOS mas bajos. Sin arrays, sin sort (evita RE10045).
            if na(min1) or sl < min1
                if not na(min1)
                    min2 := min1
                    nRelatchMin2 += 1
                min1 := sl
            else if na(min2) or sl < min2
                min2 := sl
                nRelatchMin2 += 1
        else
            float sh = rMax
            nStrongHi += 1
            rMax := high
            if na(max1) or sh > max1
                if not na(max1)
                    max2 := max1
                    nRelatchMax2 += 1
                max1 := sh
            else if na(max2) or sh > max2
                max2 := sh
                nRelatchMax2 += 1

    if not na(min2)
        if close >= min2
            nCase1Lo += 1
        else if close >= min1
            nCase2Lo += 1
        else
            nCase3Lo += 1
    if not na(max2)
        if close > max2 and close <= max1
            nCase2Hi += 1
        else if close > max1
            nCase3Hi += 1

    // §2.3.2 fallback, version local para los contadores historicos de esta barra confirmada.
    float sLoI = na(min2) ? trailing.bottom : close >= min2 ? min2 : close >= min1 ? min1 : trailing.bottom
    float sHiI = na(max2) ? trailing.top    : close <= max2 ? max2 : close <= max1 ? max1 : trailing.top
    // P6 — desacuerdo de VEREDICTO contra la Opcion A vigente, barra a barra.
    [zNh, pNh] = f_premiumDiscount(close, sHiI, sLoI, pdEqLo, pdEqHi)
    [zAh, pAh] = f_premiumDiscount(close, chartState.pdHigh, chartState.pdLow, pdEqLo, pdEqHi)
    if not na(zNh) and not na(zAh) and zNh != zAh
        nDisagree += 1
    // P4 — el invariante.
    if not na(pNh) and (pNh < 0 or pNh > 1)
        nOutRange += 1

// §2.3.2 — el rango VIGENTE, recalculado CADA barra (incluida la VIVA). min1/min2/max1/max2 son `var`
// y persisten. OJO: esto tiene que vivir FUERA del `if barstate.isconfirmed` — si no, en la barra viva
// saldria `na` y el volcado de islast (el unico canal que no sigue el crosshair) no mostraria nada.
float sLo = na(min2) ? trailing.bottom : close >= min2 ? min2 : close >= min1 ? min1 : trailing.bottom
float sHi = na(max2) ? trailing.top    : close <= max2 ? max2 : close <= max1 ? max1 : trailing.top

[zN, pctN] = f_premiumDiscount(close, sHi, sLo, pdEqLo, pdEqHi)
[zA, pctA] = f_premiumDiscount(close, chartState.pdHigh, chartState.pdLow, pdEqLo, pdEqHi)

plot(nBars,        "P_nBars")
plot(min1,         "P_histLow")        // P1: esperado 0.90275 en EURUSD D1
plot(min2,         "P_pdLow")          // P2: esperado 0.95360
plot(max1,         "P_histHigh")
plot(max2,         "P_pdHigh")
plot(pctN,         "P_pctN")
plot(pctA,         "P_pctA")
plot(nRelatchMin2, "P_nRelatchMin2")
plot(nRelatchMax2, "P_nRelatchMax2")   // *** P3, LA QUE DECIDE: <= 10 (Fable dio 41) ***
plot(nStrongLo,    "P_nStrongLo")      // anti-humo: si un lado sale 0, el otro no vale
plot(nStrongHi,    "P_nStrongHi")
plot(nOutRange,    "P_nOutRange")      // *** P4: debe ser 0 ***
plot(nDisagree,    "P_nDisagree")      // P6: / nBars >= 0.15
plot(nCase1Lo,     "P_nCase1Lo")
plot(nCase2Lo,     "P_nCase2Lo")       // anti-humo de P4: si case2+case3 = 0, P4 es TRIVIAL y no prueba
plot(nCase3Lo,     "P_nCase3Lo")
plot(nCase2Hi,     "P_nCase2Hi")
plot(nCase3Hi,     "P_nCase3Hi")
plot(structSwing.bias, "P_biasSwing")  // P5: -1 bear / +1 bull -> que lado deberia estar congelado
plot(structMajor.bias, "P_biasMajor")
plot(lastEvT,      "P_lastEvT")        // anti-humo: cruzar con el panel (BOS 17-06 / CHoCH 14-05)
plot(sAtr14,       "P_atr14")
plot((sHi - sLo) / syminfo.mintick / 10, "P_ampN")
plot(close,        "P_close")
plot({MARKER},     "P_marker")

// --- VOLCADO EN islast. POR QUE: data_get_study_values sigue el CROSSHAIR y devolvio la barra
// EQUIVOCADA en NAS100 (close=22688 con el chart en 29536) -> los valores no eran del presente.
// data_get_pine_labels NO sigue el crosshair (gotcha S131) -> este es el canal fiable para el veredicto.
if barstate.islast
    string d = "== PROBE {MARKER} · " + syminfo.ticker + " " + timeframe.period + " ==\\n"
    d += "close=" + str.tostring(close, "#.#####") + " bias=" + str.tostring(structSwing.bias) + "\\n"
    d += "histLow="  + str.tostring(min1, "#.#####") + "  pdLow="  + str.tostring(min2, "#.#####") + "\\n"
    d += "histHigh=" + str.tostring(max1, "#.#####") + "  pdHigh=" + str.tostring(max2, "#.#####") + "\\n"
    d += "RANGO USADO=[" + str.tostring(sLo, "#.#####") + ", " + str.tostring(sHi, "#.#####") + "]\\n"
    d += "pctN=" + str.tostring(pctN, "#.####") + "  pctA=" + str.tostring(pctA, "#.####") + "\\n"
    d += "nBars=" + str.tostring(nBars) + " nOutRange=" + str.tostring(nOutRange) + "\\n"
    d += "relatch min2=" + str.tostring(nRelatchMin2) + " max2=" + str.tostring(nRelatchMax2) + "\\n"
    d += "strong lo=" + str.tostring(nStrongLo) + " hi=" + str.tostring(nStrongHi) + "\\n"
    d += "caseLo 1/2/3=" + str.tostring(nCase1Lo) + "/" + str.tostring(nCase2Lo) + "/" + str.tostring(nCase3Lo) + "\\n"
    d += "caseHi 2/3=" + str.tostring(nCase2Hi) + "/" + str.tostring(nCase3Hi) + "\\n"
    d += "nDisagree=" + str.tostring(nDisagree)
    label.new(bar_index, close, d, style = label.style_label_left, textcolor = color.white, size = size.small)
"""

s = s + PROBE
OUT.write_text(s, encoding="utf-8")
print(f"Variante: 2.º EXTREMO ESTRUCTURAL §2.3.2, EN SOMBRA · escala={ESCALA} ({EV})")
print("P3 (LA QUE DECIDE): P_nRelatchMax2 <= 10   |   P4: P_nOutRange = 0   |   P5: NAS100 sin tocar codigo")
print(f"\nPROBE -> {OUT}   (marker={MARKER})")
print(f"lineas: {lineas_antes} -> {len(s.splitlines())}")
