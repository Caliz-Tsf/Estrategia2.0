# -*- coding: utf-8 -*-
"""
S133 · PROBE v13 — LA CASCADA DE PIVOTES DEL USUARIO: ¿sus verdes son pools contables desde abajo?

LA FRASE LITERAL QUE MOTIVA ESTA MEDICION (norma S132: ninguna medicion arranca sin citarla):

  "el precio en este caso siempre esta por dentro, pero vuelvo y digo, en algun minuto puede salir del
   rango de los altos mas altos y de los bajos mas bajos y este debe quedarse con los premium o discount
   hasta que genere de nuevo un bajo mas bajo o un alto mas alto y ahi se quedaria la etiqueta de D1,
   luego un par de pivotes mas arriba el discount de h1 y un par de pivotes mas arriba el discount de m5
   o es algo asi lo que pienso debes ayudarme a disenar esto. No se si esta bien el salto o que se expanda
   pero se supone que si sale del premium de las 3 temporalidades se expande hasta el nuevo alto mas alto
   y asi como explique con lo del bajo mas bajo"                                        (S133, 2026-07-15)

LO QUE ESA FRASE RESUELVE (y no hay que volver a preguntar):
  1. NO ES SALTO, ES EXPANSION PURA. "se expande hasta el nuevo alto mas alto". El "salta al siguiente
     pool" de S130 lo interpreto el supervisor; el usuario nunca dijo saltar. Hipotesis del supervisor
     MUERTA por su propia frase.
  2. pct en [0,1] SE CONSERVA. "el precio siempre esta por dentro" => el invariante NO se toca.
  3. EL EXTREMO NO SE REANCLA en pivotes. "debe quedarse... hasta que genere de nuevo un bajo mas bajo".
  => (1)+(2)+(3) = f_updateTrailing SIN f_resetTrailing = lo que YA HACE i_pdSwingLen=1000 hoy.
     S130 lo midio: [0.95360, 1.60389] = su lectura EXACTA de D1.
     S132 llamo a eso "doctrinalmente incorrecto / rango fosil que §6.3.5 prohibe" -> ESE RAZONAMIENTO
     ES ERRONEO: §6.3.5 prohibe medir sobre un rango YA SUPERADO por estructura, y un rango que solo
     expande NUNCA esta superado (contiene el precio por construccion). Anotado para el ADR.

LO QUE LA FRASE NO RESUELVE (y es lo unico que mide este probe): "UN PAR DE PIVOTES MAS ARRIBA".
  - cuantos es "un par"? (2? 3? constante?)
  - pivotes de que escala? (SMC_pools se puebla de f_detectSwings(i_swingLen=5), :2687-2689)
  - se cuentan desde el discount de D1 hacia arriba, saltando pools intermedios?

SUS 9 NIVELES ANOTADOS (de las capturas de §3 del dossier S132):
  verdes (discount): 1.10640 · 1.07408 · 1.01814 · 0.95751 · 1.02182
  rojos  (premium):  1.23697 · 1.39834 · 1.49539 · 1.60180
Todos los verdes estan BAJO el precio (~1.147) => son los candidatos a la cascada de discounts.

PREDICCIONES (escritas ANTES de medir — acumulado del proyecto ~28 de 52):
  P-C1  Sus 5 verdes coinciden con pools VIVOS a <= 10 pips. (FACIL: S131/S132 ya midieron 3 de ellos a
        1.4/7.8/3.5 pips. Se declara facil para no inflar el marcador; sirve de anti-humo del volcado.)
  P-C2  *** LA QUE DECIDE *** El espaciado entre sus verdes CONSECUTIVOS, contado en numero de pools
        vivos intermedios, es CONSTANTE +-1. FALSA si varia mas de +-1 entre pares consecutivos.
        Si es constante => "un par de pivotes" se cuantifica y la cascada es implementable como regla.
        Si varia => sus verdes NO son "cada N pools" y la cascada necesita otro criterio (o su ojo usa
        algo que el motor no registra, como en S131 con la amplitud).
  P-C3  El pool vivo MAS BAJO coincide con chartState.pdLow (=0.95360 con pdLen=1000) a <= 10 pips
        => el "bajo mas bajo" de su D1 ES un pool del propio sistema. FALSA si difiere.
        (Ojo: S129 midio que el minimo ABSOLUTO del feed es 0.90275, 508 pips mas abajo => si P-C3 sale
        verde, su "bajo mas bajo" es ESTRUCTURAL (un swing low), no el low absoluto de una vela.)

ANTI-HUMO: P_nAliveDown (denominador), P_marker (1333), volcado con edad y toques para cruzar con S131
(que midio 12 pools vivos abajo). El orden se hace en PYTHON, no en Pine (evita array.push en islast ->
RE10045, gotcha conocido). data_get_pine_labels NO sigue el crosshair (canal correcto para censos).

Uso:
  python scripts/gen_probe_cascada_pivotes.py
"""
import sys, os, pathlib

SRC = pathlib.Path(__file__).resolve().parent.parent / "pine" / "SMC-Visual.pine"
OUT = pathlib.Path(os.environ.get("TEMP", ".")) / "PROBE-cascada-pivotes-S133.pine"
MARKER = 1333

s = SRC.read_text(encoding="utf-8")

NEEDED = (
    "var array<SMC_Pool>  SMC_pools  = array.new<SMC_Pool>()",
    "f_premiumDiscount(float price, float top, float bottom, float eqLo, float eqHi) =>",
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

// --- [S133 · PROBE v13: la cascada de pivotes — volcado de pools vivos BAJO el precio]
var int nAliveDown = 0
var int nAliveUp   = 0

if barstate.islast
    nAliveDown := 0
    nAliveUp   := 0
    string dump = "POOLS VIVOS BAJO PRECIO (nivel|toques|edad_velas)\\n"
    if array.size(SMC_pools) > 0
        for i = 0 to array.size(SMC_pools) - 1
            SMC_Pool p = array.get(SMC_pools, i)
            if not p.swept
                if p.level < close
                    nAliveDown += 1
                    dump += str.tostring(p.level, "#.#####") + "|" + str.tostring(p.touches) + "|" + str.tostring(bar_index - p.barIdx) + "\\n"
                else
                    nAliveUp += 1
    label.new(bar_index, close, dump, style = label.style_label_left, textcolor = color.white, size = size.small)

plot(nAliveDown,        "P_nAliveDown")   // anti-humo: S131 midio 12 vivos abajo
plot(nAliveUp,          "P_nAliveUp")     // anti-humo: S131 midio 26 vivos arriba
plot(chartState.pdLow,  "P_pdLow")        // P-C3: el "bajo mas bajo" del motor (0.95360 con pdLen=1000)
plot(chartState.pdHigh, "P_pdHigh")
plot(close,             "P_close")
plot({MARKER},          "P_marker")
"""

s = s + PROBE
OUT.write_text(s, encoding="utf-8")
print("Variante: cascada de pivotes — volcado de pools vivos bajo el precio (orden y analisis en Python)")
print(f"\nPROBE -> {OUT}   (marker={MARKER})")
print(f"lineas: {lineas_antes} -> {len(s.splitlines())}")
