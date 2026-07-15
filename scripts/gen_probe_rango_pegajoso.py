# -*- coding: utf-8 -*-
"""
S129 · Genera un PROBE que mide la Opcion C1 (dealing range PEGAJOSO por temporalidad) en SOMBRA,
sin tocar pine/SMC-Visual.pine. Diseno + predicciones: docs/planes/DISENO-opcion-C-rango-pegajoso-S128.md §7

QUE ES C1. Hoy (Opcion A = trailingExtremes de LuxAlgo) el rango REANCLA en CADA pivote confirmado de
escala i_pdSwingLen (L2253-2256) y entre reanclajes solo EXPANDE (f_updateTrailing). C1 dice: el extremo
SE QUEDA y solo reancla cuando es VIOLADO (close mas alla). Mismo i_pdSwingLen=50, CERO parametros nuevos.
Lo unico que cambia es CUANDO se llama al reset.

EL LATCH (detalle de implementacion que el diseno §3 no fija y hay que dejar explicito). f_detectSwings
es ta.pivothigh/low -> devuelve na SALVO en la barra en que el pivote confirma (latencia len velas). Asi
que "al ser violado, reancla a un nuevo pivote de escala pdSwingLen" no puede ser instantaneo: en la barra
de la violacion no hay pivote nuevo disponible. Se resuelve con un latch: la violacion marca PENDIENTE, y
el proximo pivote confirmado de ese lado ancla y limpia el flag. Consecuencia buscada: durante un breakout
sostenido el extremo persigue cada nuevo swing; cuando el precio deja de hacer extremos nuevos, el ultimo
swing se queda clavado. Es lo que reproduce [0.9536, 1.60554] en D1.

MIDE (contadores sobre historia confirmada — el hueco de S057/S091 y el humo de S128):
  P-C1  P_cHi / P_cLo ......... convergencia de C1 en D1. Prediccion: ~[0.9536, 1.60554] (+-1 pivote de 50).
  P-C2  P_ampC (pips) ......... amplitud de C1. Se compara CORRIENDO ESTE MISMO PROBE EN D1/H1/M5 y leyendo
                                P_ampC en cada uno -> NO hace falta request.security (el Visual esta a ~79
                                tokens del techo; 2 securities extra darian CE10117). Prediccion: D1>H1>M5.
  P-C3  P_reachLo_C .......... LA QUE DECIDE. Proxy de alcance con la MISMA identidad medida en S128
                                (P3 = 0): reach == min(rangoLow, structMajor.lowLevel). Con A da 1.13246;
                                con C1 se predice ~0.95-1.02. Si no baja, C no compra el requisito del usuario.
  P-C5  P_nHiReanch / P_nLoReanch ... reanclajes de C1 en D1. Prediccion: <= 5 en ~6283 barras.
        P_nHiViol / P_nLoViol ...... barras EN violacion (denominador del latch; delata churn).

ANTI-HUMO (leccion S128 v3: el arnes medio 0 TRIVIALMENTE porque legExtHi/Lo solo se pueblan en islast ->
en toda la historia son na -> los guards "not na()" nunca pasaban). Aqui:
  - NADA se lee de legExtHi/Lo. El alcance se mide con el proxy computable en toda la historia (P3 de S128).
  - Contadores DESCOMPUESTOS por lado (nunca un OR que mezcle arriba y abajo).
  - P_nBars es el denominador explicito -> todo contador es verificable por aritmetica.
  - P_cSeeded delata el arranque: si es 0, cHi/cLo nunca se sembraron y TODA lectura es humo.

TRUNCADO en "// === DIBUJO ===" (obligatorio: CE10117, medido en console S127 -> 100335 vs limite 100256).
El chart queda EN BLANCO mientras el probe esta aplicado: es esperado.

VERIFICAR SIEMPRE con pine_get_console que aparece "Compilado." + "Anadido al grafico"; si solo dice
"guardado", el apply NO ocurrio y la lectura es de un build viejo (gotcha S127 #2 / S128 #4: el chart va
1-2 builds por detras y data_get_study_values NO avisa; devuelve TODAS las instancias). P_marker=129 es
el control de identidad por build.

GOTCHA S128 #2: TV solo deja 2 indicadores encendidos; cada Ctrl+Enter crea instancia NUEVA -> el cupo se
llena y el apply deja de aterrizar EN SILENCIO. Quitar instancias viejas antes de re-aplicar.

Uso:
  python scripts/gen_probe_rango_pegajoso.py
"""
import sys, os, pathlib

SRC = pathlib.Path(__file__).resolve().parent.parent / "pine" / "SMC-Visual.pine"
OUT = pathlib.Path(os.environ.get("TEMP", ".")) / "PROBE-rango-pegajoso-S129.pine"
MARKER = 129

s = SRC.read_text(encoding="utf-8")
orig_len = len(s)

# Anclas de existencia: si el Visual se refactoriza, el probe falla RUIDOSO en vez de medir humo.
for needed in ("[pdSwingHigh, pdSwingLow] = f_detectSwings(i_pdSwingLen)",
               "var SMC_Structure structMajor = SMC_Structure.new()",
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

// --- [S129 · PROBE Opcion C1: dealing range pegajoso] solo lee, no cambia nada.
// Sombra de C1 sobre el chart-TF, en paralelo al trailing vigente (Opcion A) que sigue intacto.
var float cHi      = na
var float cLo      = na
var bool  cHiPend  = false
var bool  cLoPend  = false
var int   cSeeded  = 0

var int nBars      = 0
var int nHiViol    = 0
var int nLoViol    = 0
var int nHiReanch  = 0
var int nLoReanch  = 0

float pdEqLo = 0.5 - i_pdEqBand / 100.0
float pdEqHi = 0.5 + i_pdEqBand / 100.0

if barstate.isconfirmed
    nBars += 1
    // Siembra: primer pivote de escala i_pdSwingLen de cada lado. Sin esto todo es na (P_cSeeded lo delata).
    if na(cHi) and not na(pdSwingHigh)
        cHi     := pdSwingHigh
        cSeeded += 1
    if na(cLo) and not na(pdSwingLow)
        cLo     := pdSwingLow
        cSeeded += 1
    // Violacion: close mas alla del extremo -> marca PENDIENTE (no puede reanclar aqui: no hay pivote aun).
    if not na(cHi) and close > cHi
        cHiPend := true
        nHiViol += 1
    if not na(cLo) and close < cLo
        cLoPend := true
        nLoViol += 1
    // Reanclaje: solo mientras esta pendiente Y confirma un pivote nuevo de ese lado.
    if cHiPend and not na(pdSwingHigh)
        cHi       := pdSwingHigh
        cHiPend   := false
        nHiReanch += 1
    if cLoPend and not na(pdSwingLow)
        cLo       := pdSwingLow
        cLoPend   := false
        nLoReanch += 1

// P-C3: proxy de alcance, MISMA identidad que S128 midio = 0 (reach == min(rangoLow, structMajor.lowLevel)).
// Computable en TODA la historia (a diferencia de legExtLo, que solo vive en islast -> el humo de S128 v3).
float reachLoA = math.min(nz(chartState.pdLow, 1e9), nz(structMajor.lowLevel, 1e9))
float reachLoC = math.min(nz(cLo, 1e9), nz(structMajor.lowLevel, 1e9))

[zA, pctA] = f_premiumDiscount(close, chartState.pdHigh, chartState.pdLow, pdEqLo, pdEqHi)
[zC, pctC] = f_premiumDiscount(close, cHi, cLo, pdEqLo, pdEqHi)

plot(nBars,     "P_nBars")
plot(cSeeded,   "P_cSeeded")
plot(cHi,       "P_cHi")
plot(cLo,       "P_cLo")
plot(nHiViol,   "P_nHiViol")
plot(nLoViol,   "P_nLoViol")
plot(nHiReanch, "P_nHiReanch")
plot(nLoReanch, "P_nLoReanch")
// P-C2: amplitud de C1 en pips. Se compara leyendo este plot en D1, H1 y M5 (sin request.security).
plot((cHi - cLo) / syminfo.mintick / 10, "P_ampC")
plot((chartState.pdHigh - chartState.pdLow) / syminfo.mintick / 10, "P_ampA")
plot(reachLoC,  "P_reachLo_C")
plot(reachLoA,  "P_reachLo_A")
plot(pctA,      "P_pctA")
plot(pctC,      "P_pctC")
plot(chartState.pdHigh, "P_pdHigh")
plot(chartState.pdLow,  "P_pdLow")
plot(structMajor.lowLevel, "P_structMajor_low")
plot(close,     "P_close")
plot({MARKER},  "P_marker")
"""

s = s + PROBE
OUT.write_text(s, encoding="utf-8")
print(f"Variante: Opcion C1 rango pegajoso en sombra (20 plots; marker={MARKER})")
print(f"\nPROBE -> {OUT}")
print(f"lineas: {lineas_antes} -> {len(s.splitlines())}")
print(f"bytes : {orig_len} -> {len(s)}  (delta {len(s)-orig_len:+d})")
