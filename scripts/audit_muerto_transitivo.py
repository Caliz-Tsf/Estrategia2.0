# -*- coding: utf-8 -*-
"""
S135 · AUDITORIA RIGUROSA DE CODIGO MUERTO — cierre transitivo + cruce de los 3 consumidores.

QUE MEJORA respecto de audit_codigo_muerto.py:
  1. CIERRE TRANSITIVO: una funcion cuyos unicos call-sites estan dentro de funciones ya muertas
     TAMBIEN esta muerta. Se itera hasta punto fijo. La version anterior no lo hacia y por eso
     subestimaba.
  2. CRUCE DE LOS 3: la regla dura #2 exige que el LIBRARY CORE sea BYTE-IDENTICO en Visual,
     Strategy y Context. => Solo es BORRABLE lo que esta muerto en LOS TRES. Lo que vive en
     alguno NO se puede borrar de los otros sin romper la identidad; ese caso es una
     RELOCALIZACION (ADR-020/ADR-022), no un borrado, y requiere ADR.
  3. Distingue simbolos dentro y fuera del CORE.

SE ANALIZA sobre el codigo SIN COMENTARIOS y SIN STRINGS: una mencion en prosa o dentro de un
literal no es un uso. (La version anterior no quitaba strings -> podia dar falsos vivos.)

SALIDA: dos listas separadas y explicitas
  [BORRABLE]  muerto en los 3 -> se puede eliminar conservando la identidad byte a byte.
  [RELOCALIZABLE] vivo en alguno -> NO se toca aqui; es material de ADR.
"""
import re, pathlib, collections

RAIZ = pathlib.Path(__file__).resolve().parent.parent
ARCHIVOS = ["SMC-Visual.pine", "SMC-Strategy.pine", "SMC-Context.pine"]

RE_DEF = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\s*\([^)]*\)\s*=>", re.M)
RE_INPUT = re.compile(r"^(i_[A-Za-z0-9_]+)\s*=\s*input\.", re.M)
RE_CONST = re.compile(r"^([A-Z][A-Z0-9_]{2,})\s*=\s*(?!input\.)", re.M)


def limpia(src: str) -> str:
    """Quita comentarios de linea Y literales de string: ni la prosa ni el texto de una etiqueta
    cuentan como uso de un simbolo."""
    out = []
    for ln in src.splitlines():
        i, en_str, q = -1, False, ""
        res = []
        j = 0
        while j < len(ln):
            c = ln[j]
            if en_str:
                if c == q:
                    en_str = False
                res.append(" ")
            elif c in "\"'":
                en_str, q = True, c
                res.append(" ")
            elif c == "/" and j + 1 < len(ln) and ln[j + 1] == "/":
                break
            else:
                res.append(c)
            j += 1
        out.append("".join(res))
    return "\n".join(out)


def bloques(code):
    """nombre -> (ini, fin) de cada definicion de funcion, en lineas 0-based."""
    lineas = code.splitlines()
    res = {}
    for i, ln in enumerate(lineas):
        m = RE_DEF.match(ln)
        if m:
            j = i + 1
            while j < len(lineas) and (lineas[j].strip() == "" or lineas[j][:1] in (" ", "\t")):
                j += 1
            res[m.group(1)] = (i, j)
    return res, lineas


def muertas_transitivas(code):
    """Itera hasta punto fijo: en cada pasada marca las funciones sin call-site FUERA de las ya
    marcadas como muertas."""
    defs, lineas = bloques(code)
    muertas = set()
    while True:
        vivas_lineas = []
        rangos_muertos = set()
        for fn in muertas:
            ini, fin = defs[fn]
            rangos_muertos.update(range(ini, fin))
        for k, ln in enumerate(lineas):
            if k not in rangos_muertos:
                vivas_lineas.append(ln)
        cuerpo_vivo = "\n".join(vivas_lineas)

        nuevas = set()
        for fn, (ini, fin) in defs.items():
            if fn in muertas:
                continue
            # call-sites en el codigo VIVO, descontando la propia linea de definicion
            n = len(re.findall(r"\b" + re.escape(fn) + r"\s*\(", cuerpo_vivo)) - 1
            if n <= 0:
                nuevas.add(fn)
        if not nuevas:
            return muertas, defs
        muertas |= nuevas


def simbolos_muertos(code, patron, muertas_fn, defs):
    """Constantes / inputs sin uso en el codigo vivo (excluyendo cuerpos de funciones muertas)."""
    lineas = code.splitlines()
    rangos = set()
    for fn in muertas_fn:
        ini, fin = defs[fn]
        rangos.update(range(ini, fin))
    vivo = "\n".join(ln for k, ln in enumerate(lineas) if k not in rangos)
    fuera = []
    for s in sorted(set(patron.findall(code))):
        if s.startswith("GRP_"):
            continue
        if len(re.findall(r"\b" + re.escape(s) + r"\b", vivo)) - 1 <= 0:
            fuera.append(s)
    return fuera


print("=" * 78)
print("AUDITORIA TRANSITIVA — S135")
print("=" * 78)

datos = {}
for nombre in ARCHIVOS:
    p = RAIZ / "pine" / nombre
    code = limpia(p.read_text(encoding="utf-8"))
    muertas, defs = muertas_transitivas(code)
    consts = simbolos_muertos(code, RE_CONST, muertas, defs)
    inputs = simbolos_muertos(code, RE_INPUT, muertas, defs)
    datos[nombre] = dict(defs=set(defs), muertas=muertas, consts=consts, inputs=inputs)
    print(f"\n### {nombre}")
    print(f"    funciones: {len(defs)}  |  muertas (transitivo): {len(muertas)}")
    print(f"    constantes sin uso: {len(consts)}  |  inputs sin uso: {len(inputs)}")

# --- que es BORRABLE de verdad: muerto en LOS TRES ---
todas_fn = set().union(*[d["defs"] for d in datos.values()])
print("\n" + "=" * 78)
print("[BORRABLE] muerto en LOS 3 => se elimina conservando la identidad byte a byte")
print("=" * 78)
borrables_fn = []
for fn in sorted(todas_fn):
    presente = [n for n, d in datos.items() if fn in d["defs"]]
    viva_en = [n for n in presente if fn not in datos[n]["muertas"]]
    if presente and not viva_en:
        borrables_fn.append(fn)
        print(f"    funcion   {fn:<30} (definida en {len(presente)} archivos, viva en 0)")
if not borrables_fn:
    print("    (ninguna funcion esta muerta en los 3)")

todas_c = set().union(*[set(d["consts"]) for d in datos.values()])
borrables_c = []
for c in sorted(todas_c):
    presente = [n for n, d in datos.items() if re.search(r"^" + re.escape(c) + r"\s*=", limpia((RAIZ / "pine" / n).read_text(encoding="utf-8")), re.M)]
    muerta_en = [n for n, d in datos.items() if c in d["consts"]]
    if presente and set(presente) == set(muerta_en):
        borrables_c.append(c)
        print(f"    constante {c:<30} (definida en {len(presente)}, sin uso en todas)")

todas_i = set().union(*[set(d["inputs"]) for d in datos.values()])
for i in sorted(todas_i):
    print(f"    input     {i:<30} (sin uso donde se declara)")

print("\n" + "=" * 78)
print("[RELOCALIZABLE] vivo en alguno => NO se borra: romperia la regla dura #2.")
print("Es material de ADR (patron ADR-020/ADR-022), no una limpieza.")
print("=" * 78)
for fn in sorted(todas_fn):
    presente = [n for n, d in datos.items() if fn in d["defs"]]
    viva_en = [n for n in presente if fn not in datos[n]["muertas"]]
    if viva_en and len(viva_en) < len(presente):
        muerta_en = [n.replace("SMC-", "").replace(".pine", "") for n in presente if n not in viva_en]
        print(f"    {fn:<30} viva en {len(viva_en)}/{len(presente)}  |  muerta (y cargada) en: {', '.join(muerta_en)}")

print(f"\nRESUMEN: {len(borrables_fn)} funciones + {len(borrables_c)} constantes borrables sin tocar la identidad del CORE.")
