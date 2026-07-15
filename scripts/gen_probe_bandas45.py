# -*- coding: utf-8 -*-
"""
S127 · Genera un PROBE que mide DOS preguntas abiertas a la vez, sin tocar pine/SMC-Visual.pine:

(1) ¿Estan MUERTAS las bandas 4/5? En S127 subir i_profundidad 3 -> 5 no cambio NADA en el censo,
    pero no se pudo verificar que el override entrara. f_depthBand (L3124-3127) asigna banda 4/5
    SOLO si pdPrev1Hi/pdPrev2Hi no son na, y esos escalares solo se pueblan cuando el rango ROTA
    (borde > 0.5xATR, L3093-3102). Si son na -> las bandas 4/5 son CODIGO DORMIDO y ningun cap ni
    gate hara visible lo que hay bajo pdLow. Se plotea i_profundidad para PROBAR que el override
    entro (no suponerlo).

(2) ¿El dealing range esta mal anclado? (duda del usuario, registrada desde S102 como "Opcion B
    ancla estructural", diferida a Fase 3). Doctrina §2.3: el rango es [strong low, strong high]
    "vigentes" y "se actualiza con la estructura". Implementacion (L2253-2259): reancla SOLO al
    confirmarse un swing de escala i_pdSwingLen(50) y el resto del tiempo f_updateTrailing solo
    EXPANDE (trailing extremes de LuxAlgo, nunca contrae). Ploteamos el rango junto al swing
    dominante (structMajor) para ver cuanto se separan: si structMajor ya giro bajista y el rango
    sigue anclado al tramo alcista viejo, el hueco doctrina/implementacion es medible.

Ambas preguntas deciden lo mismo: si el lado de ABAJO puede verse. El censo midio que abajo hay
5 OB + 11 FVG + 1 BRK + 3 IFVG VIVOS pero fuera de banda (bajo pdLow).

TRUNCADO en "// === DIBUJO ===" (obligatorio: el Visual esta a ~79 tokens del techo, medido en el
console S127 -> anadir plots encima del Visual completo da CE10117). El chart queda EN BLANCO
mientras el probe esta aplicado: es esperado.

VERIFICAR SIEMPRE con pine_get_console que aparece "Compilado." + "Añadido al gráfico"; si solo
dice "guardado", el apply NO ocurrio y cualquier lectura es de un build viejo.

Uso:
  python scripts/gen_probe_bandas45.py
"""
import sys, os, pathlib

SRC = pathlib.Path(__file__).resolve().parent.parent / "pine" / "SMC-Visual.pine"
OUT = pathlib.Path(os.environ.get("TEMP", ".")) / "PROBE-bandas45-S127.pine"
MARKER = 145

s = SRC.read_text(encoding="utf-8")
orig_len = len(s)

for needed in ("var float pdPrev1Hi = na", "var SMC_Structure structMajor = SMC_Structure.new()",
               "var float legExtHi = na"):
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

// --- [S127 · PROBE bandas 4/5 + ancla del rango] solo lee, no cambia nada.
// (1) bandas 4/5: si pdPrev1/pdPrev2 son na -> codigo dormido, i_profundidad>=4 no hace nada.
plot(i_profundidad, "P_input_profundidad")
plot(pdPrev1Hi, "P_pdPrev1Hi")
plot(pdPrev1Lo, "P_pdPrev1Lo")
plot(pdPrev2Hi, "P_pdPrev2Hi")
plot(pdPrev2Lo, "P_pdPrev2Lo")
// (2) ancla del rango vs estructura dominante: cuanto se separa el dealing range del swing vivo.
plot(chartState.pdHigh, "P_pdHigh")
plot(chartState.pdLow, "P_pdLow")
plot(structMajor.highLevel, "P_structMajor_high")
plot(structMajor.lowLevel, "P_structMajor_low")
plot(legExtHi, "P_legExtHi")
plot(legExtLo, "P_legExtLo")
plot(close, "P_close")
plot({MARKER}, "P_marker")
"""

s = s + PROBE
OUT.write_text(s, encoding="utf-8")
print(f"Variante: bandas45 + ancla del rango (13 plots; marker={MARKER})")
print(f"\nPROBE -> {OUT}")
print(f"lineas: {lineas_antes} -> {len(s.splitlines())}")
print(f"bytes : {orig_len} -> {len(s)}  (delta {len(s)-orig_len:+d})")
