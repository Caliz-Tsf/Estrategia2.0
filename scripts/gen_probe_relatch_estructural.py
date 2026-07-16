# -*- coding: utf-8 -*-
"""
S133 · PROBE v12 — RELATCH ESTRUCTURAL AL ORIGEN DE LA PIERNA (esqueleto de Fable, en sombra).

QUE MIDE. El esqueleto de RESPUESTA-FABLE-premium-discount-S132.md §3: cambiar QUIEN dispara el
reanclaje del dealing range —de "cualquier pivote de f_detectSwings(pdLen)" (:1641-1645 / :2261-2264,
la Opcion A) a "el evento estructural BOS/CHoCH que ya se calcula" (:1649 / :2276)— y a QUE NIVEL se
reancla: del pivote al ORIGEN DE LA PIERNA que rompio.

  Opcion A (vigente):  reset al nivel del pivote pdLen, en cada pivote confirmado.
  Esqueleto (sombra):  reset al min(low)/max(high) acumulado desde el evento anterior,
                       solo en la barra de un BOS/CHoCH. Expansion (f_updateTrailing) INTACTA
                       en ambos lados -> pct en [0,1] conservado por construccion.

EN SOMBRA: no sustituye nada, corre en PARALELO y emite ambos veredictos. `pine/` NO se toca.
La decision S021 (Opcion A, reconfirmada S057/S091) NO esta descongelada: este probe la informa.

ORDEN (importante). El bloque P/D (:2261-2265) corre ANTES que la estructura (:2276). Este probe va
al FINAL del archivo -> ve el evStructSwing de ESTA barra, que es el orden que el esqueleto necesita
(estructura -> relatch). Si se implementa de verdad, hay que mover el P/D despues de la estructura
(o el relatch usaria el evento de la barra anterior). Anotado como coste de implementacion.

PREDICCIONES (de §7 de Fable, escritas ANTES de medir — van 24 vivas de 44).
Este probe mide las del chart-TF, que deciden 3 de los 4 criterios de abandono:

  P1  D1 EURUSD hoy (bias bajista): el strongHigh latcheado cae a <= 1.0 x ATR_D1 de 1.23697
      (el rojo de Freddy). FALSA si cae en otro sitio (p.ej. se queda en 1.20831 o salta a 1.60389).
  P2  D1 EURUSD hoy: el suelo es el trailing low de la pierna actual (~1.141) => pct < 20%
      (discount profundo). FALSA si sale equilibrium/premium, o si reaparece 1.13246 como ancla.
  P4  Frecuencia de relatch = frecuencia de BOS/CHoCH: nRelatch > 0 y << nPiv(pdLen).
      FALSA si nRelatch = 0 (degenero en Opcion C / min-max de ventana, hipotesis #3 muerta en S129).
      *** CRITERIO DE ABANDONO de Fable: P4 = 0 -> la propuesta se retira. ***
  P7  Diferencia real vs Opcion A: el veredicto P/D cambia en >= 15% de las barras confirmadas.
      (S128 mato la variante pivote con 3.2%.)
      *** CRITERIO DE ABANDONO de Fable: P7 < 5% -> la propuesta se retira. ***
      *** CRITERIO DE ABANDONO de Fable: P1 y P2 fallan AMBAS -> la propuesta se retira. ***

  P3 (rotacion entre TF), P5 (los 9 niveles anotados) y P6 (NAS100) NO se miden aqui: necesitan
  tocar f_computeTFState (los 3 estados MTF) y otro simbolo. Segundo probe SI este pasa el gate.

RESULTADO corrida `swing` (marker 1330, D1 OANDA:EURUSD, n=6284, anti-humo limpio):
  P1 ❌ FALSA   sHi=1.16445 -> 12.8 x ATR de 1.23697 (umbral 1.0). Muy falsa, no marginal.
  P2 ❌ FALSA   pctL=0.46202 (equilibrium, no discount profundo) y sLo=1.13246 = REAPARECE el ancla
                que la propia prediccion marcaba como senal de fallo.
  P4 ~ MITAD    nRelatch=301 (>0 ✔) pero nPiv=78 -> ratio 3.86x: el relatch es MAS frecuente que los
                pivotes, no "<<" como predijo. El "<<" es falso.
  P7 ✅ VERDE   nDisagree/nBars = 1896/6284 = 30.2% (>=15%; muy por encima del 5% de abandono).
  Anti-humo OK: lastRelHiT = 2026-06-17 = el "BOS 17-06" del panel que Fable mando cruzar.
                nSeed=2, nOutRange=0 (invariante pct en [0,1] conservado), P_marker=1330 fresco.
  => P1 ∧ P2 ambas falsas = criterio de abandono de Fable. PERO ver el diagnostico de escala arriba.

PREDICCIONES corrida `major` (escritas ANTES de medir, S133):
  P-R1  nRelatch(major) < nPiv(78), y por tanto << 301 de la corrida swing. FALSA si >= 78.
        (Facil, casi mecanica: se declara facil para no inflar el marcador.)
  P-R2  ampL(major) > 758 pips (el rango de la Opcion A doctrinal con pdLen=50, medido en S130/S132).
        FALSA si sale <= 758. Es la prueba de que la escala 50 compra un rango NO local.
  P-R3  *** LA QUE DECIDE *** sHi(major) cae a <= 1.0 x ATR_D1 de 1.23697 (la P1 de Fable con la
        escala corregida). FALSA si cae a mas de 1 ATR. Si esta falla tambien, el abandono de la
        propuesta ya no es cuestion de parametrizacion: "origen de pierna" no es lo que Freddy marca.
  P-R4  P7 se mantiene >= 15% con la escala 50. FALSA si cae por debajo (seria el suelo de S128).

ANTI-HUMO (leccion S128: contadores con guard `not na()` miden humo):
  - P_nBars: denominador explicito.
  - P_nRelatchHi / P_nRelatchLo: por lado separado (no un total que oculte un lado muerto).
  - P_nPiv: pivotes pdLen contados en la misma pasada -> P4 compara peras con peras.
  - P_lastRelHiT / P_lastRelLoT: fecha del ultimo relatch por lado -> DEBE coincidir con los eventos
    del panel (BOS 17-06, CHoCH 14-05 en D1). Si el probe relatcha en fechas que el panel no reconoce,
    el probe mide otra cosa.
  - P_nSeed: cuantas veces se sembro un lado desde na (delata el arranque).
  - P_nOutRange: el invariante pct en [0,1]; debe salir 0.

GOTCHAS a respetar al leer (memoria del proyecto):
  - data_get_study_values sigue el CROSSHAIR -> mover el raton al borde derecho antes de leer.
  - Verificar P_marker = 1330; builds rancios conviven con frescos (S127/S129).
  - El numero real de tokens esta en pine_get_console, NO en pine_get_errors (CE10117 a 79 tokens).
  - Apply real = inject (guarda) + Ctrl+Enter (guarda) + Ctrl+Enter (aplica). Ojo al modal
    "¿Desea guardar...?" que bloquea el 2.º Ctrl+Enter EN SILENCIO (S131).
  - TV solo deja 2 indicadores: remover el viejo con chart_manage_indicator.

LA ESCALA DEL EVENTO ES UN PARAMETRO LIBRE (hallazgo de la corrida `swing`, S133).
Fable §2 especifica "un BOS/CHoCH alcista de escala `swingLen`" (=i_swingLen=5). MEDIDO: eso da
301 relatches en 6284 barras (3.86x MAS que los 78 pivotes de escala 50) -> rango LOCAL de 319 pips
-> P1 y P2 falsas. Es el bug de S021 reencarnado (decisiones-pd-rango.md :36-41: "alimento los
trailing extremes con los swings estructurales swingLen=5 -> rango local ~60 pips"). El dealing
range de LuxAlgo/§2.3 es de escala DOMINANTE 50 (getCurrentStructure(50), ref :782), y el proyecto
ya la tiene viva: `structMajor`/`evStructMajor` (i_majorLen=50, T07B, :2290-2292).
Por eso este arnes parametriza la escala en vez de hardcodearla:

  python scripts/gen_probe_relatch_estructural.py swing   -> evStructSwing (escala 5)  · marker 1330
  python scripts/gen_probe_relatch_estructural.py major   -> evStructMajor (escala 50) · marker 1331
"""
import sys, os, pathlib

ESCALA = (sys.argv[1] if len(sys.argv) > 1 else "swing").lower()
if ESCALA not in ("swing", "major"):
    print(f"[FALLO] escala desconocida: {ESCALA!r} (usar: swing | major)")
    sys.exit(1)
EV     = "evStructSwing" if ESCALA == "swing" else "evStructMajor"
MARKER = 1330 if ESCALA == "swing" else 1331

SRC = pathlib.Path(__file__).resolve().parent.parent / "pine" / "SMC-Visual.pine"
OUT = pathlib.Path(os.environ.get("TEMP", ".")) / f"PROBE-relatch-{ESCALA}-S133.pine"

s = SRC.read_text(encoding="utf-8")

# --- Guards de identidad: si el archivo cambio, el probe NO debe correr a ciegas.
NEEDED = (
    "[pdSwingHigh, pdSwingLow] = f_detectSwings(i_pdSwingLen)",     # :2199 pivotes escala P/D
    "evStructSwing := f_detectStructure(structSwing, bar_index, time, true, true)",  # :2276 escala 5
    "evStructMajor := f_detectStructure(structMajor, bar_index, time, true, true)",  # :2292 escala 50
    "f_premiumDiscount(float price, float top, float bottom, float eqLo, float eqHi) =>",
    "var SMC_Trailing trailing = SMC_Trailing.new()",               # :2198 la Opcion A vigente
    "float sAtr14        = ta.atr(14)",                             # :2151 ATR del chart
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

// --- [S133 · PROBE v12: RELATCH ESTRUCTURAL al origen de la pierna — EN SOMBRA]
// Esqueleto Fable §3. C1 = tracker de origen de pierna; C2 = relatch por evento; C3 = expansion intacta.
var float rMin      = na   // C1: min(low) acumulado desde el ultimo evento ALCISTA  -> futuro strong low
var float rMax      = na   // C1: max(high) acumulado desde el ultimo evento BAJISTA -> futuro strong high
var float sHi       = na   // rango en sombra: lado alto
var float sLo       = na   // rango en sombra: lado bajo
var int   nRelatchHi = 0
var int   nRelatchLo = 0
var int   nPiv       = 0
var int   nBars      = 0
var int   nSeed      = 0
var int   nOutRange  = 0
var int   nDisagree  = 0   // P7: veredicto latch != veredicto A
var int   lastRelHiT = na
var int   lastRelLoT = na

float pdEqLo = 0.5 - i_pdEqBand / 100.0
float pdEqHi = 0.5 + i_pdEqBand / 100.0

if barstate.isconfirmed
    nBars += 1
    // Anti-humo P4: los pivotes de escala P/D contados en la MISMA pasada (denominador de "<< nPiv").
    if not na(pdSwingHigh)
        nPiv += 1
    if not na(pdSwingLow)
        nPiv += 1

    // C1 — trackers de origen de pierna. Se actualizan CADA barra confirmada, con datos pasados.
    rMin := na(rMin) ? low  : math.min(rMin, low)
    rMax := na(rMax) ? high : math.max(rMax, high)

    // C2 — RELATCH POR EVENTO. Unico disparador: el BOS/CHoCH que ya se calcula ({EV}).
    // Alcista -> el strong LOW es el origen de la pierna que rompio (min acumulado). Simetrico bajista.
    // Anti-repaint [D-PINE-03]: min/max de barras pasadas, fijado en la barra confirmada de la ruptura.
    if not na({EV}) and ({EV}.kind == KIND_BOS or {EV}.kind == KIND_CHOCH)
        if {EV}.dir == DIR_BULL
            sLo        := rMin
            rMin       := low          // el tracker reinicia: la nueva pierna nace aqui
            nRelatchLo += 1
            lastRelLoT := time
        else
            sHi        := rMax
            rMax       := high
            nRelatchHi += 1
            lastRelHiT := time

    // C3 — EXPANSION INTACTA (f_updateTrailing tal cual, ambos lados). Orden reset->expand como :2261-2265.
    // Es lo que garantiza pct en [0,1]: si el precio supera un lado, el rango lo sigue.
    if na(sHi)
        nSeed += 1
    if na(sHi) or high > sHi
        sHi := high
    if na(sLo)
        nSeed += 1
    if na(sLo) or low < sLo
        sLo := low

    // P7 — desacuerdo de VEREDICTO (no de nivel) contra la Opcion A vigente, barra a barra.
    [zLh, pLh] = f_premiumDiscount(close, sHi, sLo, pdEqLo, pdEqHi)
    [zAh, pAh] = f_premiumDiscount(close, chartState.pdHigh, chartState.pdLow, pdEqLo, pdEqHi)
    if not na(zLh) and not na(zAh) and zLh != zAh
        nDisagree += 1
    // Invariante pct en [0,1].
    if not na(pLh) and (pLh < 0 or pLh > 1)
        nOutRange += 1

[zL, pctL] = f_premiumDiscount(close, sHi, sLo, pdEqLo, pdEqHi)
[zA, pctA] = f_premiumDiscount(close, chartState.pdHigh, chartState.pdLow, pdEqLo, pdEqHi)

// --- Lecturas. P1/P2 son de la barra viva; P4/P7 son contadores sobre historia.
plot(nBars,        "P_nBars")
plot(sHi,          "P_sHi")           // P1: el strong high latcheado  (esperado ~1.23697 +- 1 ATR)
plot(sLo,          "P_sLo")           // P2: el suelo                  (esperado ~1.141)
plot(pctL,         "P_pctL")          // P2: esperado < 0.20
plot(pctA,         "P_pctA")          // el vigente, para contraste
plot(chartState.pdHigh, "P_pdHighA")
plot(chartState.pdLow,  "P_pdLowA")
plot(nRelatchHi,   "P_nRelatchHi")    // P4: > 0 y << nPiv
plot(nRelatchLo,   "P_nRelatchLo")    // P4: > 0 y << nPiv
plot(nPiv,         "P_nPiv")          // P4: denominador
plot(nDisagree,    "P_nDisagree")     // P7: / nBars >= 0.15 pasa; < 0.05 = abandono
plot(nSeed,        "P_nSeed")         // anti-humo: siembras desde na
plot(nOutRange,    "P_nOutRange")     // invariante: debe ser 0
plot(lastRelHiT,   "P_lastRelHiT")    // anti-humo: cruzar con el panel (BOS 17-06 / CHoCH 14-05)
plot(lastRelLoT,   "P_lastRelLoT")
plot(sAtr14,       "P_atr14")         // P1: la tolerancia 1.0 x ATR
plot((sHi - sLo) / syminfo.mintick / 10, "P_ampL")  // amplitud del rango en sombra (pips)
plot(close,        "P_close")
plot({MARKER},     "P_marker")
"""

s = s + PROBE
OUT.write_text(s, encoding="utf-8")
print(f"Variante: RELATCH ESTRUCTURAL al origen de pierna, EN SOMBRA (Fable §3) · escala={ESCALA} ({EV})")
print(f"Mide: P1 (sHi ~ 1.23697), P2 (pctL < 0.20), P4 (nRelatch > 0), P7 (nDisagree/nBars >= 0.15)")
print(f"Abandono si: P4=0, o P7<5%, o P1 y P2 fallan ambas")
print(f"\nPROBE -> {OUT}   (marker={MARKER})")
print(f"lineas: {lineas_antes} -> {len(s.splitlines())}")
