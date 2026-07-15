# -*- coding: utf-8 -*-
"""
S129 · PROBE v2 — ¿el rango de C1 lo decide el MERCADO o lo decide DONDE EMPIEZA LA VENTANA?

DE DONDE SALE ESTA PREGUNTA. El probe v1 (gen_probe_rango_pegajoso.py) midio C1 en D1/H1/M5 y P-C3
salio verde (alcance 1.13246 -> 0.95360). Pero dos contadores delataron algo no predicho:
    H1: nLoViol = 0   -> el low 1.01779 NUNCA fue violado
    M5: nHiViol = 0   -> el high nunca fue violado
Un extremo que nunca se viola no lo fijo el mercado: es el PRIMER pivote de la ventana disponible.
Y la ventana la fija TV, no el simbolo: D1 6283 barras (~24 anos), H1 9535 (~1.1 anos), M5 6426 (~22 dias).
=> Sospecha: la "auto-escala por temporalidad" del diseno (§3) seria en parte un ARTEFACTO de la
   profundidad de historia por TF. Si es cierto, C1 no es simbolo-agnostico (ADR-001) y el ADR no se
   sostiene tal como esta escrito.

EL EXPERIMENTO. Cuatro sombras de C1 IDENTICAS salvo en DONDE SE SIEMBRAN: al 0%, 25%, 50% y 75% de la
historia disponible. Misma regla, mismo i_pdSwingLen, mismo latch. Es un test de convergencia:
    - Si las 4 convergen al mismo [cHi, cLo] -> la semilla SE LAVA: las violaciones mandan, C1 es robusto
      y el hallazgo de v1 era solo el efecto de ventanas cortas en H1/M5.
    - Si divergen -> la semilla MANDA: C1 mide el borde de la ventana, no la estructura. C1 tal como esta
      disenada no sirve, y P-C3 verde seria un acierto por accidente (la ventana de D1 casualmente empieza
      donde da la respuesta que el usuario espera).

PREDICCION (escrita ANTES de medir, norma del proyecto — van 4 vivas de 12):
  P-S1  En D1 las 4 sombras DIVERGEN: al menos una difiere de la sembrada al 0% en > 500 pips.
        Razon: el low 0.95360 es de 2022; una sombra sembrada al 75% (~2020+) no puede "ver" 2008 para el
        high, y una sembrada despues de 2022 no puede anclar en 0.95360 salvo que el precio lo re-viole
        (no lo hizo: nLoViol solo cuenta 128 barras, todas en el tramo antiguo).
        FALSA si convergen (<= 500 pips de spread entre las 4).
  P-S2  La divergencia es ASIMETRICA: mayor por ARRIBA (el high de 2008 es inalcanzable para semillas
        tardias) que por abajo. FALSA si el spread de cLo >= el de cHi.

ANTI-HUMO (leccion S128 v3 + v1): P_sSeeded* cuenta las siembras de cada sombra por separado; si alguno
es != 2, esa sombra no arranco y su lectura es humo, no evidencia. P_nBars es el denominador explicito.

TRUNCADO en "// === DIBUJO ===" (CE10117: el Visual esta a ~79 tokens del techo). Chart en blanco: esperado.
Verificar SIEMPRE P_marker=1292 (identidad del build) y console "Compilado."+"Anadido al grafico".

Uso:
  python scripts/gen_probe_rango_pegajoso_semilla.py
"""
import sys, os, pathlib

SRC = pathlib.Path(__file__).resolve().parent.parent / "pine" / "SMC-Visual.pine"
OUT = pathlib.Path(os.environ.get("TEMP", ".")) / "PROBE-rango-semilla-S129.pine"
MARKER = 1292

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

# Cuatro sombras: 0%, 25%, 50%, 75% de la historia. last_bar_index es constante en toda la serie.
SHADOWS = [("0", 0.00), ("25", 0.25), ("50", 0.50), ("75", 0.75)]

decl, logic, plots = [], [], []
for tag, frac in SHADOWS:
    decl.append(f"""var float cHi{tag}   = na
var float cLo{tag}   = na
var bool  cHiP{tag}  = false
var bool  cLoP{tag}  = false
var int   cSd{tag}   = 0""")
    logic.append(f"""    // --- sombra sembrada al {int(frac*100)}% de la historia ---
    if bar_index >= math.floor(last_bar_index * {frac})
        if na(cHi{tag}) and not na(pdSwingHigh)
            cHi{tag} := pdSwingHigh
            cSd{tag} += 1
        if na(cLo{tag}) and not na(pdSwingLow)
            cLo{tag} := pdSwingLow
            cSd{tag} += 1
        if not na(cHi{tag}) and close > cHi{tag}
            cHiP{tag} := true
        if not na(cLo{tag}) and close < cLo{tag}
            cLoP{tag} := true
        if cHiP{tag} and not na(pdSwingHigh)
            cHi{tag}  := pdSwingHigh
            cHiP{tag} := false
        if cLoP{tag} and not na(pdSwingLow)
            cLo{tag}  := pdSwingLow
            cLoP{tag} := false""")
    plots.append(f"""plot(cHi{tag}, "P_cHi_{tag}")
plot(cLo{tag}, "P_cLo_{tag}")
plot(cSd{tag}, "P_sSeeded_{tag}")""")

PROBE = "\n\n// --- [S129 · PROBE v2: convergencia de C1 segun la semilla] solo lee, no cambia nada.\n"
PROBE += "\n".join(decl) + "\nvar int nBars = 0\n\nif barstate.isconfirmed\n    nBars += 1\n"
PROBE += "\n".join(logic) + "\n\n"
PROBE += "\n".join(plots) + "\n"
PROBE += f"""plot(nBars, "P_nBars")
// Spread entre sombras: 0 => la semilla se lava (C1 robusto); grande => la semilla manda (C1 mide la ventana).
plot((math.max(nz(cHi0,-1e9), nz(cHi25,-1e9), nz(cHi50,-1e9), nz(cHi75,-1e9)) - math.min(nz(cHi0,1e9), nz(cHi25,1e9), nz(cHi50,1e9), nz(cHi75,1e9))) / syminfo.mintick / 10, "P_spreadHi_pips")
plot((math.max(nz(cLo0,-1e9), nz(cLo25,-1e9), nz(cLo50,-1e9), nz(cLo75,-1e9)) - math.min(nz(cLo0,1e9), nz(cLo25,1e9), nz(cLo50,1e9), nz(cLo75,1e9))) / syminfo.mintick / 10, "P_spreadLo_pips")
plot(last_bar_index, "P_lastBarIdx")
plot(close, "P_close")
plot({MARKER}, "P_marker")
"""

s = s + PROBE
OUT.write_text(s, encoding="utf-8")
print(f"Variante: convergencia de C1 por semilla (4 sombras 0/25/50/75%; marker={MARKER})")
print(f"\nPROBE -> {OUT}")
print(f"lineas: {lineas_antes} -> {len(s.splitlines())}")
print(f"bytes : {orig_len} -> {len(s)}  (delta {len(s)-orig_len:+d})")
