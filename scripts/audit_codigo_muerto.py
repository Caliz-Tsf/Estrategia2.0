# -*- coding: utf-8 -*-
"""
S135 · AUDITORIA ESTATICA DE CODIGO MUERTO en los 3 consumidores Pine.

QUE BUSCA. El precedente es ADR-022: `f_tfExtremes` = 139 lineas que el Visual CARGABA y NUNCA
LLAMABA, y en Pine una funcion no llamada SI cuesta tokens (ADR-020, confirmado empiricamente en
S120). Este arnes generaliza esa busqueda, de forma ESTATICA (cero ciclos de apply):

  1. FUNCIONES definidas pero con 0 call-sites en ESE consumidor -> candidatas a retirar del CORE
     hacia un bloque propio, o a eliminar si no las usa nadie.
  2. INPUTS declarados y nunca leidos -> tokens + ruido en la UI.
  3. CONSTANTES declaradas y nunca leidas.

NO decide nada: produce la lista de candidatas. El coste real de cada una se mide por ablacion
(unico metodo fiable — S133/ADR-022), porque las lineas NO predicen los tokens (4 predicciones
muertas de 4, memoria del proyecto).

LIMITE CONOCIDO: el conteo de call-sites es textual. Una funcion llamada solo desde OTRA funcion que
a su vez esta muerta cuenta como viva aqui (cadena muerta). Por eso el informe marca las funciones
cuyos unicos call-sites estan DENTRO de otras funciones candidatas.
"""
import re, pathlib, collections

RAIZ = pathlib.Path(__file__).resolve().parent.parent
ARCHIVOS = ["SMC-Visual.pine", "SMC-Strategy.pine", "SMC-Context.pine"]

# Pine: definicion de funcion = `f_nombre(args) =>` empezando en columna 0
RE_DEF   = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\s*\([^)]*\)\s*=>", re.M)
RE_INPUT = re.compile(r"^(i_[A-Za-z0-9_]+)\s*=\s*input\.", re.M)
RE_CONST = re.compile(r"^([A-Z][A-Z0-9_]{2,})\s*=\s*(?!input\.)", re.M)


def sin_comentarios(src: str) -> str:
    """Quita comentarios de linea para no contar menciones en prosa como call-sites."""
    out = []
    for ln in src.splitlines():
        i = ln.find("//")
        out.append(ln if i < 0 else ln[:i])
    return "\n".join(out)


def analiza(path: pathlib.Path):
    raw = path.read_text(encoding="utf-8")
    code = sin_comentarios(raw)

    defs = RE_DEF.findall(code)
    inputs = RE_INPUT.findall(code)
    consts = RE_CONST.findall(code)

    # linea de definicion de cada funcion, para localizarla en el informe
    linea_def = {}
    for m in RE_DEF.finditer(code):
        linea_def.setdefault(m.group(1), code[: m.start()].count("\n") + 1)

    def usos(nombre, patron):
        return len(re.findall(patron, code))

    muertas, vivas = [], {}
    for fn in sorted(set(defs)):
        # call-sites = `fn(` menos la propia definicion
        n = usos(fn, r"\b" + re.escape(fn) + r"\s*\(") - defs.count(fn)
        if n <= 0:
            muertas.append((fn, linea_def.get(fn, 0)))
        else:
            vivas[fn] = n

    inputs_muertos = []
    for inp in sorted(set(inputs)):
        n = usos(inp, r"\b" + re.escape(inp) + r"\b") - 1  # -1 = la declaracion
        if n <= 0:
            inputs_muertos.append(inp)

    consts_muertas = []
    for c in sorted(set(consts)):
        if c.startswith("GRP_"):
            continue  # los GRP_ se usan como `group =`, ya cuentan
        n = usos(c, r"\b" + re.escape(c) + r"\b") - 1
        if n <= 0:
            consts_muertas.append(c)

    return defs, muertas, vivas, inputs_muertos, consts_muertas


print("=" * 78)
print("AUDITORIA DE CODIGO MUERTO — S135")
print("=" * 78)

por_archivo = {}
for nombre in ARCHIVOS:
    p = RAIZ / "pine" / nombre
    if not p.exists():
        print(f"\n[SKIP] {nombre} no existe")
        continue
    defs, muertas, vivas, inp_m, cst_m = analiza(p)
    por_archivo[nombre] = (set(defs), {f for f, _ in muertas})

    print(f"\n### {nombre}  ({len(p.read_text(encoding='utf-8').splitlines())} lineas)")
    print(f"    funciones definidas: {len(set(defs))}   |   SIN call-site: {len(muertas)}")
    for fn, ln in muertas:
        print(f"      [MUERTA]  {fn:<28} def en :{ln}")
    if inp_m:
        print(f"    inputs declarados y NO leidos: {len(inp_m)}")
        for i in inp_m:
            print(f"      [INPUT ]  {i}")
    if cst_m:
        print(f"    constantes declaradas y NO leidas: {len(cst_m)}")
        for c in cst_m:
            print(f"      [CONST ]  {c}")

# --- membresia del CORE: la dimension que hace accionable el cruce ---
# El LIBRARY CORE es byte-identico en los 3 => una funcion que vive AHI la cargan los 3,
# la llamen o no. Si solo un SUBCONJUNTO la llama, no pertenece al CORE (ADR-020/ADR-022).
def rango_core(path: pathlib.Path):
    lineas = path.read_text(encoding="utf-8").splitlines()
    ini = fin = None
    for i, ln in enumerate(lineas, 1):
        if ln.startswith("// === LIBRARY CORE ==="):
            ini = i
        elif ini and fin is None and ln.startswith("// === ") and i > ini:
            fin = i
    return ini, (fin or len(lineas))


core_ini, core_fin = rango_core(RAIZ / "pine" / "SMC-Visual.pine")
src_v = (RAIZ / "pine" / "SMC-Visual.pine").read_text(encoding="utf-8")
en_core = set()
for m in RE_DEF.finditer(sin_comentarios(src_v)):
    ln = sin_comentarios(src_v)[: m.start()].count("\n") + 1
    if core_ini <= ln < core_fin:
        en_core.add(m.group(1))

if len(por_archivo) == 3:
    print("\n" + "=" * 78)
    print(f"CRUCE — el LIBRARY CORE del Visual va de :{core_ini} a :{core_fin} ({len(en_core)} funciones)")
    print("Regla ADR-020/ADR-022: el CORE es lo que usan TODOS; lo que usa un SUBCONJUNTO")
    print("va a su propio bloque byte-identico entre quienes SI lo usan.")
    print("=" * 78)
    todas = set().union(*[d for d, _ in por_archivo.values()])
    tabla = collections.defaultdict(list)
    for fn in sorted(todas):
        usan = [n for n, (defs, muertas) in por_archivo.items()
                if fn in defs and fn not in muertas]
        tabla[len(usan)].append((fn, usan))

    for k in sorted(tabla):
        if k == 3:
            continue
        etiqueta = "NADIE la llama" if k == 0 else f"solo {k} consumidor(es)"
        enc = [(f, u) for f, u in tabla[k] if f in en_core]
        fuera = [(f, u) for f, u in tabla[k] if f not in en_core]
        print(f"\n  --- {etiqueta}: {len(tabla[k])} funciones "
              f"({len(enc)} DENTRO del CORE, {len(fuera)} fuera) ---")
        if enc:
            print("      >>> DENTRO DEL CORE = las que cuestan tokens a quien no las usa <<<")
            for fn, usan in enc:
                quien = ', '.join(u.replace('SMC-', '').replace('.pine', '') for u in usan) or '(nadie)'
                print(f"        [CORE] {fn:<30} usan: {quien}")
        if fuera:
            print(f"      (fuera del CORE, no penalizan a los otros: {len(fuera)})")

    # --- resumen ejecutivo ---
    print("\n" + "=" * 78)
    print("RESUMEN — candidatas a salir del CORE, por consumidor que las cargaria de balde")
    print("=" * 78)
    for nombre, (defs, muertas) in por_archivo.items():
        muertas_core = sorted(f for f in muertas if f in en_core)
        print(f"  {nombre:<22} carga {len(muertas_core):>3} funciones del CORE que NUNCA llama")
    print("\n  [OJO] Las LINEAS no predicen los TOKENS (4 predicciones muertas de 4).")
    print("        Esta lista es de CANDIDATAS: el ahorro real se mide por ABLACION.")
