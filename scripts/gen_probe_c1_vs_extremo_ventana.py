# -*- coding: utf-8 -*-
"""
S129 · PROBE v3 — ¿es C1 ("pegajoso hasta ser violado") lo mismo que "el EXTREMO DE LA VENTANA"?

DE DONDE SALE LA HIPOTESIS. El probe v2 (gen_probe_rango_pegajoso_semilla.py) sembro C1 en 4 puntos de
la historia y cada sombra devolvio el maximo de SU ventana, y los tres valores cuadran con tres techos
historicos reales de EURUSD:
    semilla 0%/25% -> 1.60195 (techo de 2008)
    semilla 50%    -> 1.39937 (techo de 2014)
    semilla 75%    -> 1.23496 (techo de 2021)
=> Sospecha: "se queda hasta que lo violen" no seria una regla nueva, sino una forma INDIRECTA de decir
   "el extremo de la ventana disponible" (un extremo solo se mueve cuando el precio lo supera).
   Si es cierto, el ADR se simplifica muchisimo: el concepto pasa a ser "el extremo de la ventana"
   (trivial de razonar y de portar a MQL5, Fase 4) y la regla deja de depender del LATCH, que es la
   pieza mas fragil de C1.

QUE COMPARA. Barra a barra, sobre historia confirmada:
    cHi/cLo ......... C1 con latch (identico al del probe v1).
    runMaxHi/runMinLo  maximo/minimo CORRIDO de los pivotes confirmados de escala i_pdSwingLen.
                       Monotono por construccion: runMax nunca baja, runMin nunca sube.

PREDICCIONES (escritas ANTES de medir — van 6 vivas de 14):
  P-E1  Coinciden en la GRAN MAYORIA de barras: nAgreeHi/nBars > 90% y nAgreeLo/nBars > 90%.
        FALSA si <= 90%. Es la hipotesis de equivalencia.
  P-E2  LA DIAGNOSTICA (de quien es la culpa de los 36 pips de 2008: cHi=1.60195 vs lectura 1.60554).
        Prediccion: runMaxHi termina en ~1.60554 => SI confirmo un pivote en el pico y el LATCH lo
        desecho al adoptar uno posterior mas bajo => la culpa es del LATCH, y quitarlo MEJORA el ancla.
        FALSA si runMaxHi termina en 1.60195 => ningun pivote confirmo en el pico (pivote estricto) =>
        la culpa es de f_detectSwings y el latch es inocente.
  P-E3  cHi PUEDE BAJAR (nHiDown > 0), cosa que el extremo-de-la-ventana no puede hacer nunca.
        Es el mecanismo exacto por el que P-E1 no seria 100%. FALSA si nHiDown == 0.

POR QUE PUEDEN DIFERIR (el latch no es monotono): tras una violacion el latch adopta el PROXIMO pivote
de ese lado SEA CUAL SEA su nivel — y como los pivotes confirman con 50 barras de latencia, si el precio
ya retrocedio ese pivote puede ser MAS BAJO que el extremo que acaba de ser violado => cHi BAJA.

ANTI-HUMO (leccion S128 v3): P_cSeeded/P_rSeeded delatan el arranque de cada mecanismo por separado;
si son 0 la lectura es humo. P_nBars es el denominador explicito -> todo ratio es verificable a mano.
Contadores DESCOMPUESTOS por lado (nunca un OR que mezcle arriba y abajo).

TRUNCADO en "// === DIBUJO ===" (CE10117). Chart en blanco: esperado. Verificar P_marker=1293 y
console "Compilado."+"Anadido al grafico" (si solo dice "guardado", el apply NO ocurrio).

Uso:
  python scripts/gen_probe_c1_vs_extremo_ventana.py
"""
import sys, os, pathlib

SRC = pathlib.Path(__file__).resolve().parent.parent / "pine" / "SMC-Visual.pine"
OUT = pathlib.Path(os.environ.get("TEMP", ".")) / "PROBE-c1-vs-ventana-S129.pine"
MARKER = 1293

s = SRC.read_text(encoding="utf-8")
orig_len = len(s)

for needed in ("[pdSwingHigh, pdSwingLow] = f_detectSwings(i_pdSwingLen)",):
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

// --- [S129 · PROBE v3: C1 (latch) vs extremo de la ventana (running max/min)] solo lee, no cambia nada.
// Mecanismo A: C1 con latch (identico al probe v1).
var float cHi     = na
var float cLo     = na
var bool  cHiPend = false
var bool  cLoPend = false
var int   cSeeded = 0
// Mecanismo B: extremo corrido de los pivotes confirmados. Monotono por construccion.
var float runMaxHi = na
var float runMinLo = na
var int   rSeeded  = 0

var int nBars     = 0
var int nAgreeHi  = 0
var int nAgreeLo  = 0
var int nHiDown   = 0
var int nLoUp     = 0
var int nPivHi    = 0
var int nPivLo    = 0
var float maxDifHi = 0.0
var float maxDifLo = 0.0

if barstate.isconfirmed
    nBars += 1
    // --- A: C1 con latch ---
    if na(cHi) and not na(pdSwingHigh)
        cHi     := pdSwingHigh
        cSeeded += 1
    if na(cLo) and not na(pdSwingLow)
        cLo     := pdSwingLow
        cSeeded += 1
    if not na(cHi) and close > cHi
        cHiPend := true
    if not na(cLo) and close < cLo
        cLoPend := true
    if cHiPend and not na(pdSwingHigh)
        float prevHi = cHi
        cHi     := pdSwingHigh
        cHiPend := false
        // P-E3: el latch puede BAJAR el extremo (el running max no puede). Es el mecanismo de la divergencia.
        if not na(prevHi) and pdSwingHigh < prevHi
            nHiDown += 1
    if cLoPend and not na(pdSwingLow)
        float prevLo = cLo
        cLo     := pdSwingLow
        cLoPend := false
        if not na(prevLo) and pdSwingLow > prevLo
            nLoUp += 1
    // --- B: extremo de la ventana ---
    if not na(pdSwingHigh)
        if na(runMaxHi)
            rSeeded += 1
        runMaxHi := na(runMaxHi) ? pdSwingHigh : math.max(runMaxHi, pdSwingHigh)
        nPivHi   += 1
    if not na(pdSwingLow)
        if na(runMinLo)
            rSeeded += 1
        runMinLo := na(runMinLo) ? pdSwingLow : math.min(runMinLo, pdSwingLow)
        nPivLo   += 1
    // --- P-E1: acuerdo barra a barra (tolerancia 1 tick para no medir ruido de float) ---
    if not na(cHi) and not na(runMaxHi)
        if math.abs(cHi - runMaxHi) <= syminfo.mintick
            nAgreeHi += 1
        maxDifHi := math.max(maxDifHi, math.abs(cHi - runMaxHi))
    if not na(cLo) and not na(runMinLo)
        if math.abs(cLo - runMinLo) <= syminfo.mintick
            nAgreeLo += 1
        maxDifLo := math.max(maxDifLo, math.abs(cLo - runMinLo))

plot(nBars,    "P_nBars")
plot(cSeeded,  "P_cSeeded")
plot(rSeeded,  "P_rSeeded")
plot(cHi,      "P_cHi")
plot(cLo,      "P_cLo")
plot(runMaxHi, "P_runMaxHi")
plot(runMinLo, "P_runMinLo")
plot(nAgreeHi, "P_nAgreeHi")
plot(nAgreeLo, "P_nAgreeLo")
plot(nHiDown,  "P_nHiDown")
plot(nLoUp,    "P_nLoUp")
plot(nPivHi,   "P_nPivHi")
plot(nPivLo,   "P_nPivLo")
plot(maxDifHi / syminfo.mintick / 10, "P_maxDifHi_pips")
plot(maxDifLo / syminfo.mintick / 10, "P_maxDifLo_pips")
plot(close,    "P_close")
plot({MARKER}, "P_marker")
"""

s = s + PROBE
OUT.write_text(s, encoding="utf-8")
print(f"Variante: C1 (latch) vs extremo de la ventana (15 plots; marker={MARKER})")
print(f"\nPROBE -> {OUT}")
print(f"lineas: {lineas_antes} -> {len(s.splitlines())}")
print(f"bytes : {orig_len} -> {len(s)}  (delta {len(s)-orig_len:+d})")
