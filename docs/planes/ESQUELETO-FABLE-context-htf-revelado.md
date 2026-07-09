# ESQUELETO-FABLE — SMC-Context.pine: herencia pierna HTF + revelado al romper

> Estrategia 2.0 · Fase 1 (Pine Visual) · S109 (2026-07-08) · autor: **Fable** (Claude Fable 5)
> **Ejecutor: Opus (Claude Code), en frío.** Fable diseña; Opus rellena y ejecuta. Este documento es
> autocontenido: con él + el repo, una sesión nueva ejecuta todo sin contexto previo.
> Veredicto y justificación de diseño: [RESPUESTA-FABLE-herencia-pierna-htf.md](RESPUESTA-FABLE-herencia-pierna-htf.md)
> Brief origen: [BRIEF-FABLE-herencia-pierna-htf-revelado.md](BRIEF-FABLE-herencia-pierna-htf-revelado.md) · ADR-016 · CLAUDE.md.

---

## §0. PROTOCOLO DE RELLENO (Opus, leer ANTES de tocar nada)

### §0.1 Lectura obligatoria al arrancar
1. `memory/ESTADO-ACTUAL.md` (bloqueante) · rama `pine/sistema-completo` limpia (bloqueante).
2. Este documento COMPLETO + la RESPUESTA-FABLE enlazada arriba (veredicto: por qué Context y no Visual).
3. Reglas duras de `CLAUDE.md` — en especial: anti-repaint, CORE byte-idéntico, RE10045-safe,
   ATR-relativo, símbolo-agnóstico, un commit = un concepto, **jamás** referenciar `D:\CODE\BOT\Bot\`.

### §0.2 Reglas de ejecución de ESTE esqueleto
- **Orden estricto A0 → A2/A3 → (A1 opcional) → B → C → D → E → F.** Ningún paso de feature (C+)
  antes del verde del probe (A2/A3). Si un gate falla → parar, documentar, consultar al usuario.
- **Cada `[OPUS]` es un punto de verificación o relleno**: verificar contra el código real antes de asumir.
  Los números de línea citados son del HEAD de S108/S109 (commit `0520274`); si el archivo cambió,
  re-localizar por contenido, no por número.
- **Ritual apply TV (memorizar, aplica a TODO el documento):**
  `python scripts/pine_inject.py <archivo>` → **Ctrl+Enter** (o botón PLAY junto al NOMBRE del script;
  NO "Añadir al gráfico" para re-aplicar) → esperar **18–25 s** → `pine_get_errors`.
  GOTCHAS: `pine_check.py` NO cuenta tokens (falso-0 para CE10117; solo el apply valida);
  el "0 errores" inmediato tras Save es falso; tras cambiar TF/símbolo esperar 8–10 s + poll
  `data_get_pine_tables` hasta `study_count>0`; si CDP 9222 se cae → `tv_launch`.
- **`pine_inject.py` inyecta al tab ACTIVO del editor** y su click de fallback puede guardar el slot
  vinculado. Para scripts de probe: SIEMPRE `pine_new` (indicator) primero → tab sin slot → inyectar ahí.
  Para el Context de producción: el usuario crea el slot `SMC_Context` A MANO (el MCP no crea slots
  nombrados) → `pine_open("SMC_Context")` → inyectar.
- Idioma español; commits Conventional + ID (`feat(pine-context): F1-CTX-...`); compila 0/0 o no se commitea.

### §0.3 Contexto mínimo (qué es esto)
El LTF (H1/M5) debe heredar del HTF (D1) las zonas/estructura IMPORTANTES **más allá del
Premium/Discount vigente**, en ambas direcciones, **reveladas solo cuando el precio rompe la frontera**
del rango HTF (draw-on-liquidity: "si allá arriba hay un EQH que desplazó el precio hasta aquí,
necesitamos saberlo"). El transporte actual (`f_nearestN`, CORE) solo emite lo cercano al precio →
los extremos no viajan. Bloqueador real: `SMC-Visual.pine` está pegado al techo CE10117 (~100 256
tokens compilados) → la feature vive en un **tercer consumidor visual `pine/SMC-Context.pine`** con el
mismo LIBRARY CORE byte-idéntico (presupuesto de tokens Y memoria frescos, por-script) y una
**2ª `request.security` por HTF** con función de extremos FUERA del CORE (patrón `f_m5Light` L2722;
la nota L2769 del Visual ya anticipaba la 2ª llamada). CORE SHA `5510361166844bd5` NO se toca.

---

## PASO A0 — Sanity (5 min, sin cambios)
1. `tv_health_check` → CDP OK, chart OANDA:EURUSD.
2. `chart_get_state` → `SMC Engine — Visual` aplicado (instancia viva).
3. `python scripts/pine_check.py pine/SMC-Visual.pine` → 0/0 (baseline).
4. `powershell -File scripts/check-core-sync.ps1` → CORE_SYNC=OK.
- **Gate A0:** los 4 verdes. Si no → arreglar entorno antes de seguir.

## PASO A2/A3 — Probe OOM de la 2ª llamada + convivencia (SIN tocar el slot Visual)

**Qué mide:** ¿aguanta TV un script con el motor completo D1+H1 (proxy exacto del futuro Context)
corriendo EN PARALELO con el Visual ya aplicado? El dummy de `f_tfExtremes` es el propio
`f_computeTFState` (mismo motor, mismo perfil de memoria).

**Pre-validado por Fable (S109):** el generador de abajo produce un script de **1715 líneas que ya
compiló 0/0 server-side**. Falta SOLO el apply vivo (la parte que valida OOM/CE10117).

1. Generar el probe (guardar el generador como `scripts/gen_probe_context.py` o correr inline;
   escribe a un scratchpad, NO a `pine/`, NO se commitea el .pine):

```python
# gen_probe_context.py — genera PROBE-context-oom.pine desde el HEAD del Visual
src = open("pine/SMC-Visual.pine", encoding="utf-8").read().splitlines()
# CORE = seccion '// === LIBRARY CORE ===' (L143) hasta ANTES de '// === DETECCIÓN TF PROPIO ===' (L1843)
# [OPUS] verificar con grep que los marcadores siguen en 143/1843; si no, localizar por marcador.
core = src[142:1842]

def fields(p):
    scal = [f"{p}_bias",f"{p}_bosP",f"{p}_bosD",f"{p}_bosT",f"{p}_chP",f"{p}_chD",f"{p}_chT",
            f"{p}_mssP",f"{p}_mssD",f"{p}_mssT",f"{p}_pdH",f"{p}_pdL",f"{p}_pdM",
            f"{p}_e20",f"{p}_e50",f"{p}_e200",f"{p}_atr"]
    slots = []
    for s in range(12):
        slots += [f"{p}_k{s}",f"{p}_t{s}",f"{p}_b{s}",f"{p}_d{s}",f"{p}_ta{s}",f"{p}_tb{s}"]
    return scal + slots

# Literales = defaults de los inputs del Visual (swingLen 5, pdSwingLen 50, disp 1.5, body 0.70,
# eqlLen 3, eqThr 0.1, obVol 2.0, obMitClose false, fvgThr 0.25, poolTol 0.1, minTouches 2,
# caps OB2/FVG2/Pool2/Sweep2/EQ2/BOS1/CHoCH1)
ARGS = "5, 50, 1.5, 0.70, 3, 0.1, 2.0, false, 0.25, 0.1, 2, 2, 2, 2, 2, 2, 1, 1"
def call(p, tf):
    return (f'[{", ".join(fields(p))}] = request.security(syminfo.tickerid, "{tf}", '
            f'f_computeTFState({ARGS}), lookahead = barmerge.lookahead_off)')

hdr = ["// PROBE-A2A3 · S109 — de-riesgo OOM 2a llamada MTF. NO producto, NO commit.",
       "//@version=6", 'indicator("PROBE Context OOM", overlay = true)', ""]
tail = ["", "// === PROBE · 2 security calls D1/H1 con motor completo ===",
        call("d1", "D"), call("h1", "60"),
        'plot(d1_pdH, "d1 pdHigh", color = color.new(color.blue, 60))',
        'plot(h1_pdH, "h1 pdHigh", color = color.new(color.orange, 60))',
        'plotchar(d1_bias + h1_bias + d1_k0 + h1_k0 + d1_d0 + h1_d0, "chk_int", "", location.top)',
        'plotchar(d1_t0 + h1_t0 + d1_b0 + h1_b0 + d1_atr + h1_atr, "chk_f", "", location.top)']
open(OUT, "w", encoding="utf-8", newline="\n").write("\n".join(hdr + core + tail) + "\n")
```

2. `python scripts/pine_check.py <probe>` → esperar 0/0 (ya validado; si falla, el CORE se movió).
3. **⚠️ HALLAZGO S109 (verificado vivo):** `pine_new` NO da un tab sin slot en esta build — el editor
   sigue vinculado a `SMC_Library`, y `pine_inject`+Ctrl+Enter/Save **sobrescriben el slot del Visual**
   (el probe reemplaza al Visual, mismo entity_id). Recuperable re-inyectando `pine/SMC-Visual.pine` en
   `SMC_Library` + save + apply, pero INVALIDA el método de este paso para A3.
   - **A2 (probe SOLO) sí es medible así** y quedó VERDE (0 err, sin CE10117/OOM): aplicar el probe
     (sobrescribe Visual temporalmente), leer `pine_get_errors`, luego RESTAURAR el Visual.
   - **A3 (convivencia) REQUIERE el slot `SMC_Context` ya creado** (Paso B.5). Por eso el orden real es:
     A0 → A2 (probe solo, restaurar Visual) → **B.5 (usuario crea slot)** → A3 (inyectar probe en
     `SMC_Context`, con Visual vivo, leer ambos) → resto de B → C…  El resto de gates no cambia.
4. Leer resultado con el Visual TODAVÍA aplicado (A3 — solo posible con el slot SMC_Context):
   - `chart_get_state` → debe listar `SMC Engine — Visual` + `PROBE Context OOM`.
   - Verificar que el panel T14 del Visual sigue vivo (`data_get_pine_tables`, study_filter="Visual").
   - `capture_screenshot` de evidencia.
5. Limpieza: quitar el study PROBE del chart (`chart_manage_indicator` remove con su entity_id).

**Tabla de decisión (Gate A2/A3):**
| Resultado | Lectura | Acción |
|---|---|---|
| Aplica sin error, Visual vivo | Verde total | Seguir a B |
| "Internal server study error" / memoria | El motor duplicado D1+H1 no cabe ni solo | Recortar motor de extremos: quitar `obBuf*` (volumen) y buffer eventos del dummy → re-probe. Si sigue: **degradar alcance v1 a solo pools+EQ** (motor mínimo) y re-probe |
| Aplica solo, pero con Visual da error/lag severo | Convivencia falla | Documentar; opción: Context solo-bajo-demanda (usuario lo activa al operar) — consultar usuario |
| CE10117 en el probe | Improbable (probe ≈ CORE+poco) | Anotar el número reportado = techo real del CORE solo; replantear con Fable |

## PASO A1 (OPCIONAL) — Medir headroom de tokens del Visual
Solo sirve para **descartar formalmente la Ruta 2** (implementar dentro del Visual). Si el usuario ya
aceptó Ruta 1, puede saltarse. ⚠️ Toca temporalmente el slot Visual — hacer con calma y RESTAURAR.

1. Generar `Visual+padding`: HEAD + bloque final de N statements únicos:
   `__padSum += ta.sma(close, K)` (K = 7..7+N−1, `var float __padSum = 0.0` arriba, un solo
   `plot(__padSum, display = display.none)` al final). Únicos para evitar fusión de subexpresiones.
2. N=400 → inyectar al tab del Visual → Ctrl+Enter → 25 s → `pine_get_errors` → si CE10117, anotar
   total **T1** ("contains too many tokens: T1").
3. N=200 → ídem → **T2** (si no desborda, probar N=300).
4. `unit=(T1−T2)/(N1−N2)` · `tokens_HEAD = T1 − 400×unit` · `headroom = 100256 − tokens_HEAD`.
5. **RESTAURAR:** inyectar HEAD limpio → Ctrl+Enter → 25 s → 0 errores + panel T14 vivo. NO terminar
   la sesión sin este paso.
- **Registro:** anotar `tokens_HEAD` y `headroom` en la Sesion-NNN. Esperado: headroom < 1k →
  Ruta 2 formalmente muerta.

## PASO B — Decisión + ADR-017 + tooling (doc-only, 1 commit)
1. Presentar al usuario los números de A → confirmación de Ruta 1 (tercer consumidor).
2. Escribir `docs/adrs/ADR-017-consumidor-visual-auxiliar-context.md`:
   - **Contexto:** CE10117 en Visual + extremos HTF no viajan (nearest-N, ADR-009/010).
   - **Decisión:** 3er consumidor `pine/SMC-Context.pine` (indicator overlay, solo dibuja, sin
     `strategy.*`, sin alertas) con LIBRARY CORE byte-idéntico; 2ª security call por HTF con
     `f_tfExtremes` fuera del CORE.
   - **Alternativas descartadas:** (a) dentro del Visual → CE10117; (b) ensanchar tuple del CORE →
     SHA+Strategy+ADR+OOM acoplado → queda como **Fase B** junto a la promoción ADR-016.
   - **Consecuencias:** check-core-sync ×3; slot TV manual; motor D1/H1 corre 2× en el chart;
     reversible (borrar archivo + revertir ADR). Estado: Aceptada — Fase A.
3. Extender `scripts/check-core-sync.ps1`: añadir `[string]$ContextPath` (default
   `pine/SMC-Context.pine`); si existe, extraer su bloque CORE y exigir hash == Visual. Si NO existe
   → comportamiento actual intacto (no romper Fase 0/CI). `[OPUS]` mantener solo-ASCII (PS 5.1).
4. Nota en `CLAUDE.md` (sección Arquitectura, 1 línea: consumidor visual auxiliar opcional, ADR-017)
   y en `docs/workplan/PINE-PLAN.md`.
5. **Slot TV `SMC_Context`** — MÉTODO VERIFICADO S109 (Opus puede casi todo, 1 clic del usuario):
   abrir el editor Pine (`ui_click` data-name `pine-dialog-button`) → clic en el desplegable del
   NOMBRE del script → menú → **"Hacer una copia…"** → sale diálogo pidiendo nombre → escribir
   `SMC_Context` → Guardar. (El único paso manual real es teclear el nombre en el diálogo modal;
   todo lo demás es `ui_evaluate`/`ui_click`.) Luego `pine_open("SMC_Context")` → inyectar ahí.
   Crea el slot como COPIA del Visual sin tocar `SMC_Library`.
- **Gate B:** ADR commiteado, sync-script extendido y verde con 2 archivos, slot existente.

## PASO C — `pine/SMC-Context.pine` v1: esqueleto + `f_tfExtremes` (1-2 commits)

### C.1 Layout del archivo (crear)
```pine
// © Estrategia 2.0 — SMC Engine (Context HTF). Porta algoritmos del indicador
// "Smart Money Concepts [LuxAlgo]" (CC BY-NC-SA 4.0, © LuxAlgo) — atribucion
// obligatoria [D-PINE-06]. https://creativecommons.org/licenses/by-nc-sa/4.0/
//@version=6
indicator("SMC Engine — Context (HTF)", overlay = true, max_labels_count = 100, max_lines_count = 100, max_boxes_count = 100)

// === INPUTS ===
GRP_CTX = "Contexto HTF (revelado)"
i_extOn          = input.bool(true,  "Capa de contexto HTF activa",            group = GRP_CTX)
i_ctxAlways      = input.bool(false, "Mostrar siempre (Estudio) vs al romper", group = GRP_CTX)
i_kExt           = input.float(6.0,  "Alcance extremos (x rango dominante HTF)", minval = 2.0, maxval = 12.0, step = 0.5, group = GRP_CTX)
i_extMinStrength = input.float(0.5,  "Importancia minima zona extrema (0-1)",  minval = 0.0, maxval = 1.0, step = 0.05, group = GRP_CTX)
i_revealHyst     = input.float(1.0,  "Histeresis re-ocultado (x ATR HTF)",     minval = 0.25, maxval = 3.0, step = 0.25, group = GRP_CTX)
// [OPUS] + inputs de deteccion NECESARIOS para f_tfExtremes con MISMOS defaults que el Visual
// (i_swingLen 5, i_pdSwingLen 50, i_mssDispFactor 1.5, i_mssBodyPct 0.70, i_eqlLength 3,
//  i_eqThreshold 0.1, i_obHighVolFactor 2.0, i_obMitClose false, i_fvgThreshold 0.25,
//  i_poolTol 0.1, i_minTouches 2) — copiar las lineas de input del Visual tal cual.

// === LIBRARY CORE ===
// [OPUS] COPIAR VERBATIM la seccion completa del Visual (L143 marcador incluido → L1842).
// Tras copiar: powershell -File scripts/check-core-sync.ps1  → mismo SHA 5510361166844bd5.

// === EXTREMOS HTF (fuera del CORE) ===   ← C.2/C.3
// [OPUS] ANTES de escribir C.2/C.3: verificar por grep que existen con nombre EXACTO
//   ZS_MITIGATED, KIND_OB, KIND_FVG, KIND_POOL, KIND_EQH, KIND_EQL y MTF_K en el CORE.
//   Si alguno difiere, el snippet no compila. (SMC_Zone.bottom / SMC_Pool.level ya verificados.)
// [OPUS] slots: el probe A2/A3 emite 12 slots/HTF (= MTF_K del Visual, peor-caso de memoria);
//   f_tfExtremes de PRODUCCION emite 8 conceptos x6 (§X). Son distintos a proposito: no unificar.
// === REVELADO AL ROMPER ===              ← Paso D
// === DIBUJO CONTEXTO ===                 ← Paso E
```

### C.2 Selectores farthest-important (fuera del CORE; puros, RE10045-safe)
```pine
// f_farthestZone: la zona 'kind' NO mitigada mas LEJANA de px en el lado 'up', con
// strength >= minStr, sin salirse de 'bound' (= px ± kExt*rango, calculado por el llamador).
// Devuelve [top, bottom, dir, tA] (nas si no hay). Espejo conceptual de f_nearestN.
f_farthestZone(array<SMC_Zone> src, int kind, float px, bool up, float minStr, float bound) =>
    float bTop = na
    float bBot = na
    int   bDir = 0
    int   bTA  = int(na)
    float bDist = -1.0
    if array.size(src) > 0
        for i = 0 to array.size(src) - 1
            SMC_Zone z = array.get(src, i)
            float mid = (z.top + z.bottom) / 2.0
            bool side = up ? mid > px : mid < px
            bool inB  = up ? mid <= bound : mid >= bound
            if z.kind == kind and z.state < ZS_MITIGATED and z.strength >= minStr and side and inB
                float d = math.abs(mid - px)
                if d > bDist
                    bDist := d
                    bTop  := z.top
                    bBot  := z.bottom   // campo del UDT es 'bottom' (SMC_Zone L228), NO 'bot'
                    bDir  := z.dir
                    bTA   := z.barTime
    [bTop, bBot, bDir, bTA]

// f_farthestPool: idem para pools NO barridos con touches >= minT.
// [OPUS] verificar campos SMC_Pool (level/dir/swept/barTime/touches) en el UDT del CORE.
// f_farthestEvent: idem sobre los arrays evK/evL/evD/evTA/evTB para KIND_EQH/KIND_EQL
// (los EQ son liquidez per se: sin filtro de strength, solo lado+bound).
```

### C.3 `f_tfExtremes` (fuera del CORE; patrón f_m5Light)
```pine
// f_tfExtremes: MISMA cadena de deteccion que f_computeTFState (reutiliza los detectores puros
// del CORE con estado var interno propio) pero la EMISION cambia: en vez de nearest-N, emite
// el extremo importante por concepto por lado. Tuple compacto 3 escalares + 8 slots x 6 = 51.
// CONTRATO (orden exacto): [ pdHigh, pdLow, atr14,
//   OB↑{k,t,b,d,tA,tB}, OB↓, FVG↑, FVG↓, POOL↑, POOL↓, EQ↑, EQ↓ ]   (kind=0 ranura vacia, ADR-010)
f_tfExtremes(int swingLen, int pdLen, float dispFactor, float bodyPct, int eqlLength, float eqThreshold, float obHighVolFactor, bool obMitClose, float fvgThreshold, float poolTol, int minTouches, float kExt, float minStr) =>
    // [OPUS] (1) COPIAR el cuerpo de deteccion de f_computeTFState VERBATIM: desde
    //   'var SMC_TFState st = SMC_TFState.new()' hasta 'f_prunePools(poolsTf, MAX_POOLS)'
    //   inclusive + las 5 asignaciones st.pdMid/ema20/ema50/ema200/atr14 (Visual L1687–1790).
    //   NO tocar nada de ese bloque (es la garantia de paridad de deteccion).
    // (2) SELECCION NUEVA (sustituye el bloque nearest-N L1791–1828):
    float rango  = na(st.pdHigh) or na(st.pdLow) ? na : st.pdHigh - st.pdLow
    float hiB    = na(rango) ? na : close + kExt * rango
    float loB    = na(rango) ? na : close - kExt * rango
    [obUt, obUb, obUd, obUa] = f_farthestZone(zonesTf, KIND_OB,  close, true,  minStr, hiB)
    [obDt, obDb, obDd, obDa] = f_farthestZone(zonesTf, KIND_OB,  close, false, minStr, loB)
    [fvUt, fvUb, fvUd, fvUa] = f_farthestZone(zonesTf, KIND_FVG, close, true,  minStr, hiB)
    [fvDt, fvDb, fvDd, fvDa] = f_farthestZone(zonesTf, KIND_FVG, close, false, minStr, loB)
    // [OPUS] pools y EQ analogos (f_farthestPool / f_farthestEvent)
    // (3) RETURN plano 51 campos; ranura vacia => kind 0 + nas (convencion ADR-010):
    //   kind emitido = KIND_OB/KIND_FVG/KIND_POOL/KIND_EQH|EQL si hay objeto, 0 si na(top).
    [ st.pdHigh, st.pdLow, st.atr14, /* ...48 campos de slots... */ ]

// Call-sites (globales, junto a los del... — en Context son LOS UNICOS):
// [ctxD1_pdH, ctxD1_pdL, ctxD1_atr, ...48] = request.security(syminfo.tickerid, "D",
//     f_tfExtremes(i_swingLen, i_pdSwingLen, ..., i_kExt, i_extMinStrength), lookahead = barmerge.lookahead_off)
// [ctxH1_...] = request.security(syminfo.tickerid, "60", f_tfExtremes(...), lookahead = barmerge.lookahead_off)
// [OPUS] en chart D1, la llamada "60" hereda hacia abajo — replicar la logica de TF-condicional del
// Visual si existe (si el chart ES D1, el contexto H1 no aplica; verificar como lo gatea el Visual).
```
- **Alcance v1 = OB/FVG/POOL/EQ** (lo que el transporte ya modela). MB/Breaker/BOS-CHoCH lejanos = v2
  solo si el probe A2 dio holgura (el pivote importante que precede al swing ES pool/EQ → v1 ya cubre
  el draw-on-liquidity).
- Anti-repaint: la cadena copiada ya gatea en `barstate.isconfirmed`; llamador `lookahead_off`. Nada nuevo.
- **Commit C:** `feat(pine-context): F1-CTX-01 esqueleto Context + f_tfExtremes (extremos HTF)` —
  compila 0/0 (pine_check + apply vivo), check-core-sync ×3 verde.

## PASO D — Revelado al romper (máquina de frontera, en Context)
```pine
// === REVELADO AL ROMPER ===
// DORMANT ⇄ REVEALED por HTF y por lado, con histeresis (sin ella, un close pegado a la
// frontera hace parpadear las 8 cajas en cada vela). SOLO close CONFIRMADO (regla dura #1).
var bool revD1Up = false
var bool revD1Dn = false
if barstate.isconfirmed and not na(ctxD1_pdH) and not na(ctxD1_atr)
    float hyst = i_revealHyst * ctxD1_atr
    revD1Up := revD1Up ? close > ctxD1_pdH - hyst : close > ctxD1_pdH
    revD1Dn := revD1Dn ? close < ctxD1_pdL + hyst : close < ctxD1_pdL
// [OPUS] idem revH1Up/revH1Dn con ctxH1_*. Visibilidad efectiva:
bool showD1Up = i_extOn and (i_ctxAlways or revD1Up)
bool showD1Dn = i_extOn and (i_ctxAlways or revD1Dn)
```
- Cascada M5: en chart M5 aplican las 4 flags (D1 y H1); en chart H1 solo las D1; en chart D1 el
  contexto es nativo (Context puede no dibujar nada en D1 — decidir con el usuario en F).
- **Commit D:** `feat(pine-context): F1-CTX-02 revelado al romper (maquina de frontera + histeresis)`.

## PASO E — Dibujo contexto + presupuesto de tinta
**PRERREQUISITO: Tarea #2 de S108 (regla de solape MTF)** debe estar decidida — el contexto apila
capas D1 sobre H1 sobre nativas. Si no está: pararse y resolverla con el usuario ANTES (propuesta
mínima de Fable para desbloquear: heredado-lejano SIEMPRE detrás, transparencia escalonada
nativo < H1 < D1, y si dos cajas solapan >70% del rango de la menor → solo la del TF mayor).

- Slots de dibujo **FIJOS** (RE10045-safe): `var box`/`var label` persistentes, máx **8 boxes + 8
  labels por HTF**; en `barstate.islast` se actualizan con `box.set_*` (o delete+new acotado), jamás
  `array.push` creciente.
- Estilo §5.4 contexto: hue de familia (COL_OB/COL_FVG/COL_LIQ del Visual — copiar las constantes
  necesarias, viven FUERA del CORE), transparencia alta (≥90 fill), borde punteado
  (`line.style_dotted`), tag `D1▲ OB` / `D1▼ SSL` / `D1▲ EQH`.
- Anclaje `xloc.bar_time` con `left = tA` del slot (patrón S108); GOTCHA FVG: tA = vela MEDIA del
  gap (convención T13c) → dibujar `left = tA - barMs` NO aplica aquí (tA ya es la vela correcta del
  HTF; `[OPUS]` replicar exactamente lo que hace `f_drawMTFZones` L4261+ del Visual, que ya resuelve esto).
- Pools/EQ = `line.new` horizontal desde tA + label; zonas = `box.new`.
- Presupuesto: en régimen normal (sin ruptura, `i_ctxAlways=false`) la capa añade **0 tinta**.
  Revelada: ≤16 objetos por HTF (8 boxes/lines + 8 labels). El Context es un script separado — tiene
  su PROPIO límite max_*_count=100 y no compite con el presupuesto ≤25/≤60 del Visual; aún así,
  respetar la regla de solape para no ensuciar.
- **Commit E:** `feat(pine-context): F1-CTX-03 dibujo contexto revelado (estilo §5.4)`.

## PASO F — Validación viva + cierre
Ritual completo (§0.2). Chart OANDA:EURUSD. Matriz mínima:
1. **H1, precio dentro del rango D1, `i_ctxAlways=false`** → 0 objetos de contexto (screenshot).
2. **Ruptura histórica:** `chart_scroll_to_date` a un tramo donde el precio rompió el Premium o
   Discount de D1 (p. ej. tendencias 2024-2025 EURUSD; `[OPUS]` localizar con data_get_ohlcv D1
   summary). Verificar: extremos revelados correctos, y SIN parpadeo en las velas de re-test de la
   frontera (histéresis) — avanzar unas velas con el chart y re-mirar.
3. **`i_ctxAlways=true`** → contexto siempre visible en gris/degradado.
4. **M5** → cascada D1+H1 correcta (4 flags).
5. **Convivencia**: Visual aplicado a la vez, panel T14 intacto, sin errores de estudio, lag aceptable.
6. **Sin CE10117 / RE10026 / RE10045 / OOM** en el apply del Context (18–25 s + `pine_get_errors`).
7. `check-core-sync.ps1` ×3 verde; `pine_check.py` 0/0 los DOS archivos tocados.
- Cierre: Sesion-NNN + ESTADO-ACTUAL vía `smc-doc-updater`; sin tag (no es gate de fase).
- **Si algo de la matriz falla** → diagnóstico documentado; NO ajustar el criterio (regla dura #8).

---

## §X. Congelados propuestos (ADR-002-style; calibrables por input, jamás hardcode)
| Parámetro | Default | Rango | Notas |
|---|---|---|---|
| `i_extOn` | true | bool | kill-switch de toda la capa |
| `i_ctxAlways` | false | bool | Estudio (true) vs Operación (false, solo revelado) |
| `i_kExt` | 6.0 | 2–12 | alcance del extremo en rangos del swing dominante HTF |
| `i_extMinStrength` | 0.5 | 0–1 | importancia mínima zona extrema |
| `i_revealHyst` | 1.0 | 0.25–3 | histéresis re-ocultado × ATR(HTF) |
| Slots extremos | 8 fijos ×6 campos | — | + 3 escalares = tuple de 51/HTF |
| Objetos dibujo | ≤16/HTF revelado | — | slots fijos RE10045-safe |

## §Y. Fuera de alcance v1 (anotado, no olvidado)
- MB/Breaker/BOS-CHoCH extremos → v2 (si A2 dio holgura) o Fase B.
- Promoción de extremos al CORE (tuple único nearest+farthest, Strategy consume para scoring) →
  **Fase B** junto a ADR-016; requiere re-baseline SHA + ADR nuevo.
- **Parte A (mitigadas gris §5.4):** implementarla EN el Context (no en el Visual, protege headroom
  CE10117) — puede ser F1-CTX-04 tras cerrar F.
- Tarea #3 S108 (calibración i_kLeg / MAX_ZONES_CHART) — ortogonal, en paralelo cuando se quiera.

## §Z. Registro de ejecución (rellena Opus)
| Paso | Estado | Evidencia / números | Commit |
|---|---|---|---|
| A0 | ✅ | S109: TV+CDP OK, Visual vivo, Visual 0/0, CORE_SYNC=OK | — |
| A2 | ✅ | S109: probe 1712L compila 0/0 server-side; apply VIVO 0 err, sin CE10117/OOM. Visual restaurado (slot v168, T14 vivo). Convivencia A3 pendiente de slot SMC_Context | — |
| A3 | ✅ | S109: probe en slot SMC_Context aplicado JUNTO al Visual (3 estudios: PROBE gphnPd + Visual MQVk7q + LuxAlgo). 0 err, sin OOM/CE10117; T14 vivo; probe emite d1_pdH=1.20831/h1_pdH=1.14730/chk no-na. VERDE TOTAL → seguir a B. Probe removido del chart, slot SMC_Context conservado (v2, contiene probe; se reemplaza en C) | — |
| A1 (opc) | ☐ | tokens_HEAD= · headroom= | — |
| B | ✅ | S110: ADR-017 escrito; check-core-sync.ps1 +`$ContextPath` opcional (verde con 2 archivos SHA `5510361166844bd5`; probado 3-vías OK/DIVERGENT con Context sintético); notas CLAUDE.md (Arquitectura + regla dura #2) y PINE-PLAN.md; slot SMC_Context existe (c098abf3, S109) | (commit S110) |
| C | ✅ | S110: `pine/SMC-Context.pine` generado (CORE verbatim L143-1842 + `f_tfExtremes`/`f_farthestZone`/`f_farthestPool`/`f_farthestEvent`). check-core-sync ×3 verde (SHA `5510361166844bd5`). pine_check 0/0. **Apply VIVO** (slot SMC_Context id 9rxgph) 22s sin CE10117/OOM, JUNTO al Visual (MQVk7q)+LuxAlgo. Emite real: ctxD1_pdH=1.20831, ctxH1_pdH=1.14730, chk_kind=89 (slots pobladas). Debug plots temporales (se reemplazan en E) | (commit S110) |
| D | ☐ | | |
| E | ☐ | | |
| F | ☐ | matriz 1-7 | |
