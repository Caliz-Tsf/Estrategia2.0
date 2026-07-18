# -*- coding: utf-8 -*-
"""
S135 · ABLACION DEL CORE — cuanto cuestan REALMENTE los 3 grupos que la auditoria estatica marco.

EL PROBLEMA DE MEDICION. El conteo de tokens de TradingView SOLO ES VISIBLE POR ENCIMA DEL TECHO
(gotcha S121): si ablacionas un bloque bajas del limite y TV no dice nada -> medirias a ciegas.

LA SALIDA: LASTRE. Se anade un bloque de relleno que mantiene el script POR ENCIMA del techo en las
DOS lecturas. Ambas son visibles => la resta es exacta y no hace falta calibrar el lastre:

    coste(B) = tokens(V + lastre) - tokens(V + lastre - B)          [modo QUITAR]
    coste(B) = tokens(V + lastre + copia(B)) - tokens(V + lastre)   [modo DUPLICAR]

El modo DUPLICAR existe porque los 36 detectores SI los usa el Visual (no se pueden quitar sin
romper la compilacion), pero su coste es el mismo alla donde vivan -> se mide duplicandolos con el
nombre prefijado. Es lo que hace falta para saber cuanto liberaria Context al soltarlos.

POR QUE EL VISUAL Y NO CONTEXT: el Visual ya esta A <=6 TOKENS DEL TECHO (medido en S135: 100262
fallo, el revertido pasa) => basta un lastre pequeno para cruzarlo. Context esta ~50k por debajo y
necesitaria un lastre enorme, con riesgo de topar otros limites de Pine.

PREDICCIONES (escritas ANTES de medir — norma S114/S132):

  P1  *** LA QUE DECIDE *** coste(36 detectores) >= 15000 tokens.
      FALSA si < 5000 => soltarlos NO libera espacio suficiente en Context para recibir familias de
      dibujo => la via "reestructurar el CORE para hacer sitio" no sirve y hay que replantear.

  P2  coste(3 f_farthest*) < 1500 tokens. Son 3 selectores en ~113 lineas (:1814-:1926).
      FALSA si > 3000 => las lineas enganan aun mas de lo que ya sabemos.

  P3  coste(3 f_farthest*) > 6 tokens ⇒ retirarlos del Visual PAGA el fix de pdMid que falto por 6.
      Es la prediccion directamente accionable. FALSA solo si son ~0 (imposible salvo tree-shaking).

  P4  El Visual sin los 3 f_farthest* compila y aplica 0/0 (no los llama: la auditoria dio 0
      call-sites). FALSA si rompe => la auditoria estatica tiene un falso negativo y hay que
      revisarla antes de seguir.

ANTI-HUMO:
  - El script imprime cuantas lineas quita/anade realmente. Si quita 0, la ablacion NO OCURRIO y
    cualquier delta seria ruido.
  - Verificar SIEMPRE en pine_get_console que la lectura es de ESTE build (timestamp), no rancia.
"""
import re, sys, os, pathlib

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SRC = RAIZ / "pine" / "SMC-Visual.pine"

# los 3 que el Visual carga y NUNCA llama (auditoria estatica S135)
GRUPO_FARTHEST = ["f_farthestZone", "f_farthestPool", "f_farthestEvent"]

# los 36 que usan Visual+Strategy pero NO Context => lo que Context liberaria
GRUPO_DETECTORES = [
    "f_classifyLeg", "f_classifyOpenGap", "f_classifySweep", "f_classifySwing",
    "f_computeGradientLevels", "f_computeTFState", "f_detectBPR", "f_detectBreaker",
    "f_detectCISD", "f_detectFalseBreak", "f_detectIDM", "f_detectIFVG", "f_detectIPR",
    "f_detectImmediateRebalance", "f_detectInsideDay", "f_detectJudas", "f_detectOTE",
    "f_detectRejection", "f_detectSMT", "f_detectVacuumBlock", "f_emaCrossDir", "f_emaState",
    "f_expireOTE", "f_isPropulsion", "f_killZone", "f_macroActive", "f_nearGradientLevel",
    "f_poolStrength", "f_premiumDiscount", "f_pushEvent", "f_pushSwing",
    "f_selectGradientSource", "f_sessionType", "f_smtPivots", "f_updateFlip", "f_wickNearLevel",
]


def bloque_funcion(lineas, nombre):
    """Devuelve (ini, fin) 0-based del bloque de una funcion Pine: la linea `nombre(...) =>`
    mas todas las siguientes indentadas o en blanco."""
    pat = re.compile(r"^" + re.escape(nombre) + r"\s*\([^)]*\)\s*=>")
    for i, ln in enumerate(lineas):
        if pat.match(ln):
            j = i + 1
            while j < len(lineas) and (lineas[j].strip() == "" or lineas[j][:1] in (" ", "\t")):
                j += 1
            # no arrastrar las lineas en blanco finales
            while j > i + 1 and lineas[j - 1].strip() == "":
                j -= 1
            return i, j
    return None


def quitar(lineas, nombres):
    fuera, quitadas = set(), 0
    for n in nombres:
        r = bloque_funcion(lineas, n)
        if r is None:
            print(f"  [AVISO] no se encontro {n} — NO se quita")
            continue
        ini, fin = r
        fuera.update(range(ini, fin))
        quitadas += 1
    nuevas = [ln for k, ln in enumerate(lineas) if k not in fuera]
    print(f"  quitadas {quitadas}/{len(nombres)} funciones = {len(lineas) - len(nuevas)} lineas")
    return nuevas, len(lineas) - len(nuevas)


def copiar_renombradas(lineas, nombres):
    """Extrae los bloques y los re-emite con prefijo zz_ (las llamadas internas siguen apuntando
    a los originales: no altera la semantica del build, solo suma tokens)."""
    out, copiadas = [], 0
    for n in nombres:
        r = bloque_funcion(lineas, n)
        if r is None:
            print(f"  [AVISO] no se encontro {n} — NO se copia")
            continue
        ini, fin = r
        bloque = lineas[ini:fin]
        bloque[0] = re.sub(r"^" + re.escape(n), "zz_" + n, bloque[0])
        out.extend(bloque)
        out.append("")
        copiadas += 1
    print(f"  copiadas {copiadas}/{len(nombres)} funciones = {len(out)} lineas")
    return out, len(out)


def lastre(n_unidades):
    """Relleno de coste desconocido pero CONSTANTE entre builds: no hace falta calibrarlo,
    solo estar presente igual en las dos lecturas que se restan.

    ⚠️ INTENTO 1 FALLIDO (S135): la version previa declaraba `var float zzbal_i` y le asignaba,
    pero NUNCA leia el resultado => PINE LO ELIMINO ENTERO POR TREE-SHAKING (misma leccion que
    S121: 'Pine tree-shakea lo no usado'). El build salio por DEBAJO del techo y la medicion no
    ocurrio: `Compilando... -> guardado` SIN numero de tokens.

    INTENTO 2 FALLIDO (S135): con el plot ya contaba, pero 300 sentencias en el cuerpo principal
    dispararon otro limite distinto: "The main body of the script is too long. Try wrapping code
    in functions". El propio mensaje da el remedio.

    FIX (intento 3): el lastre vive DENTRO de una funcion (cuerpo principal corto) y su resultado
    alimenta un plot (no se puede tree-shakear). Las dos trampas cubiertas a la vez."""
    ls = ["", "// --- [S135 · LASTRE de ablacion: empuja sobre el techo para que el numero sea VISIBLE] ---",
          "// DOS trampas medidas y cubiertas: (1) sin el plot, Pine tree-shakea el lastre entero;",
          "// (2) en el cuerpo principal revienta 'main body too long' => va dentro de una funcion.",
          "zz_lastre(float c, float o) =>",
          "    float acc = 0.0"]
    for i in range(n_unidades):
        ls.append(f"    acc := acc + c * {1.0 + i * 0.001} - o * {0.5 + i * 0.001}")
    ls.append("    acc")
    ls.append('plot(zz_lastre(close, open), "zzbal", display = display.none)')
    return ls


MODOS = ("base", "sin-farthest", "con-copia36")
modo = sys.argv[1] if len(sys.argv) > 1 else ""
n_lastre = int(sys.argv[2]) if len(sys.argv) > 2 else 300

if modo not in MODOS:
    print(f"uso: python {pathlib.Path(__file__).name} <{'|'.join(MODOS)}> [n_lastre]")
    print("\n  base          V + lastre                      -> T1")
    print("  sin-farthest  V + lastre - 3 f_farthest*       -> T2   coste = T1 - T2")
    print("  con-copia36   V + lastre + copia de los 36     -> T3   coste = T3 - T1")
    sys.exit(1)

lineas = SRC.read_text(encoding="utf-8").splitlines()
print(f"[origen] {SRC.name}: {len(lineas)} lineas   |   modo={modo}   lastre={n_lastre} unidades")

extra = []
if modo == "sin-farthest":
    lineas, _ = quitar(lineas, GRUPO_FARTHEST)
elif modo == "con-copia36":
    extra, _ = copiar_renombradas(lineas, GRUPO_DETECTORES)

salida = lineas + lastre(n_lastre) + extra
OUT = pathlib.Path(os.environ.get("TEMP", ".")) / f"ABL-{modo}-S135.pine"
OUT.write_text("\n".join(salida) + "\n", encoding="utf-8")
print(f"[salida] {OUT}  ({len(salida)} lineas)")
print("\nAplicar en TV y leer el numero en pine_get_console (debe estar POR ENCIMA de 100256).")
