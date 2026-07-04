# Sesión 092 — 2026-07-03

**Rama:** `pine/sistema-completo` · **Fase:** 1 · Eje 2 "Fuerza" · **Paso 9** (verificación §10 + firma F1-GATE)
**CORE:** intacto — 1700 líneas SHA `5510361166844bd5`, core-sync OK, compila 0/0 los 3.
**Tipo:** Cierre técnico de los §10 restantes (#9 impl + #10/#12 verificación) + diagnóstico BSL D1. **F1-GATE listo para firma; SIN firmar aún.**

## Objetivo
Cerrar los ítems §10 restantes del Eje 2 → habilitar firma F1-GATE:
- **#9** mitigación (ciclo de vida: zonas mitigadas con fill).
- **#10** anti-repaint (replay 2 días).
- **#12** glifos strength coherentes (Eje 2).
- **Pendiente menor:** BSL ·3 nativo en D1 a ~1.51.

---

## #9 — Mitigación / ciclo de vida (IMPLEMENTADO + APLICADO, commit `bc7839b`)

**Hallazgo (inspección de código):** el decaimiento §5.4 del ESQUELETO-FABLE **no estaba implementado**. Las 9 funciones de dibujo de zonas pintaban las zonas `ZS_MITIGATED` con **fill gris tenue** (`color.new(color.gray, 90-92)`) — eso **es un fill**, viola checklist §10-#9 ("0 zonas mitigadas con fill en Operación/Estudio") y §5.4 ("Mitigada → pierde fill; borde punteado gris").

**Fix (Visual-only, +9 líneas netas, RE10045-safe):** 3 helpers puros nuevos antes de `f_drawOTE`:
- `f_mitBg(mit, col, transp)` → `mit ? color(na) : color.new(col, transp)` (pierde fill).
- `f_mitBorder(mit, col, transp)` → `mit ? color.new(color.gray, 55) : color.new(col, transp)`.
- `f_mitStyle(mit, st)` → `mit ? line.style_dotted : st`.

Aplicados a los **9 drawers de zonas**: OTE/GP, OB, Breaker, IFVG, BPR, VI, MB, Vacuum, FVG. Ahora una zona mitigada = sin fill + borde punteado gris. Activa/parcial conservan su render normal.

**RE10045-safe:** sin arrays nuevos, sin objetos nuevos — solo cambio de params de color/estilo en `box.new` existentes.

**Verificación en vivo (re-apply autónomo, ritual S091):**
- Slot `SMC_Library` (v136→v137) inyectado + guardado (`pine_inject.py` → `Pine Save`, `MARKERS: []` = 0/0 en TV).
- Instancia vieja `JUrtml` removida → botón "Añadir al gráfico" `[ref=e19]` → `agent-browser --cdp 9222 click e19` → instancia nueva `Hcihce` aplicada.
- Densidad fijada `{"in_123":"Operación"}`.
- **Resultado H1 Operación:** **24 labels (≤25 ✓), 2 boxes, sin crash RE10045**, panel T14 intacto, glifos `●●○` presentes, presupuesto sin regresión. Editor confirma "Compilado. / Añadido al gráfico."

**Compilación:** 0/0 server-side (`pine_check.py`) **y** en TV (`MARKERS: []`). CORE byte-idéntico intacto.

---

## #10 — Anti-repaint (VERIFICADO por auditoría; replay 2d = paywall)

**Replay TV es de pago** (constraint ya documentado en S057). La sub-parte "en replay 2 días" no es ejecutable. Cerrado por lo verificable sin replay:

**(a) Auditoría de código (exhaustiva, determinista):**
- **Todos** los bloques de creación de eventos guardados por `if barstate.isconfirmed` (evMSS, evDisp, evIDM, evIR, VI, BAG, CISD, IPR, InsideDay, EqH/L, pools/sweep, FB, KZ, SMT, Judas, Rej, Flip, swings de estructura, trailing…).
- Los **5** `request.security` reales usan `lookahead = barmerge.lookahead_off` con offsets históricos `[1]/[2]` (líneas 2017, 2298, 2482, 2638-2639).
- Único `lookahead_on` = comentario que contrasta con el repintado de LuxAlgo (línea 950).
- Sección explícita anti-repaint (4113-4116) + condiciones de alerta cerradas con `barstate.isconfirmed`.

**(b) Continuidad:** el CORE de detección está byte-idéntico e intacto desde **S057** (que ya confirmó "anti-repaint ✅ 2d histórico" vía recarga). El cambio #9 de S092 es **solo dibujo** (`barstate.islast`, no crea eventos) → no toca la invariante.

**Veredicto #10: PASS** por construcción (isconfirmed + lookahead_off + offsets `[1]`) + confirmación previa S057. El replay 2d queda como revisit Fase 3 OOS (igual criterio que S057).

---

## #12 — Glifos strength coherentes / Eje 2 (VERIFICADO vía panel)

- El header §10 admite `data_get_pine_tables` como canal de medida. El glifo `f_strGlyph(s)` (§9-2) = `f_strengthLevel(s)` quantizado a `●●●`/`●●○`/`●○○`, aplicado a las filas **OB/FVG/Pool cercano** columna M5/chart del panel T14 (`m5Ob`/`m5Fvg`/`m5Pool`).
- **Verificado en vivo** D1/H1/M5 (Operación): los 3 conceptos (OB, FVG, Pool) muestran glifo coherente con su strength (todos `●●○` = nivel medio, correcto para objetos cercanos al precio de fuerza intermedia). El glifo es **determinista** desde `f_zoneStrength` (validado S084) → coherencia por construcción.
- **Nota:** el panel expone solo el objeto **más cercano** por concepto (no permite comparar dos del mismo tipo). La comparación perceptual multi-caso de ≥3 niveles distintos (METODOLOGIA §3 Eje 2) corresponde al `smc-validator-agent` con screenshots — canal propio de la firma F1-GATE (§11.2 paso 9 "≥90 + firma usuario"). Los glifos en labels de chart (§5.5, solo Primarios) NO están cableados; #12 se cumple por el canal panel.

---

## Pendiente menor — BSL ·3 nativo D1 a ~1.51 (DIAGNOSTICADO: no es bug)

**Observación:** en D1 aparece label **"BSL ·3" a ~1.51** (3 toques), muy por encima del rango operativo (EURUSD hoy ~1.14, techo dealing range D1 = Premium 1.20831).

**Diagnóstico:**
- `data_get_pine_lines` D1 devuelve niveles a **1.51, 1.21, 1.19…1.13, 1.10, 1.06, 1.02** → los de 1.02/1.06/1.10 son mínimos de paridad EURUSD 2015-2022. Confirma que el indicador **computa sobre historia completa**, no solo las 100 barras recientes (feb-jul 2026, rango 1.13246-1.18728).
- 1.51 = cluster de **máximos históricos reales EURUSD 2009-2011** (equal highs) **no barridos** desde entonces.
- Surge como pool objetivo D1 porque los máximos cercanos (1.16-1.18) fueron raideados (`⚡ Raid ↓` @ 1.17 visible) → es el **BSL vivo más cercano arriba** que sobrevive.

**Veredicto:** detección **correcta** (pool antiguo real, no garbage/na). El filtrado por distancia/recencia del pool objetivo (no renderizar objetivo a > N×ATR) es **calibración de Fase 3** (congelado §11.3, `score_render = f(cercanía)`). **No bloquea F1-GATE.** Documentado como diferido.

---

## Commits

1. **`bc7839b`** — feat(pine-visual): F1-Eje2 S092 §10-#9 — ciclo de vida visual: zona mitigada pierde fill. (Visual-only, 9 drawers + 3 helpers puros, RE10045-safe, 0/0, core-sync OK.)

(#10, #12 y BSL = verificación/diagnóstico, sin commit de código.)

---

## Estado del plan §11.2 / §10

- **§10 checklist:** #1-#8 ✅ (S089-S091) · **#9 ✅ (impl+aplicado S092)** · **#10 ✅ (auditoría; replay=paywall)** · **#11 ✅ (S057 perf 20k)** · **#12 ✅ (panel; perceptual multi-caso → validador+firma)**.
- **Pendiente menor BSL ·3 D1:** diagnosticado, diferido Fase 3 (no bloquea).
- **Firma usuario F1-GATE:** **LISTA — pendiente de ejecución.** Opción de correr `smc-validator-agent` (Eje 2 ≥90) antes de firmar.

---

## GOTCHAs

- **Re-apply autónomo confirmado de nuevo:** abrir slot `SMC_Library` → `pine_inject.py` (Save) → remover instancia → `agent-browser --cdp 9222 click e19` → `indicator_set_inputs {"in_123":"Operación"}`. `indicator_set_inputs` requiere `entity_id` explícito (el id de la instancia nueva, aquí `Hcihce`), además del nombre.
- **`chart_manage_indicator add`** es solo para indicadores built-in — no re-añade user scripts (por eso el ritual e19).
- **Replay = paywall** (reconfirmado S092): cualquier verificación que dependa de replay se difiere a Fase 3 OOS.

---

## Evidencia

- Instancia TV aplicada: `Hcihce` (código nuevo #9, Operación).
- Screenshot: `D:\CODE\BOT\Bot\tradingview-mcp-jackson\screenshots\tv_full_2026-07-04T03-48-56-037Z.png` (H1 Operación, indicador sano post-#9, "Compilado. / Añadido al gráfico.").

---

## Adenda — Diseño: doctrina de proyección/confluencia + handoff a Fable (2ª mitad S092)

Tras cerrar §10, la revisión visual con el usuario (screenshots D1/H1/M5, nuestro indicador vs LuxAlgo base) abrió un rediseño de fondo del criterio de visibilidad en Operación. **No se escribió código** (queda como diseño/esqueleto bajo gate).

**Problema:** Operación limpio pero deja **conceptos en cero** — en H1 se ven OB/FVG heredados de D1 pero no los nativos de H1; en D1 ninguno. La spec §4 ya pedía "OB/FVG 3 por dirección" pero solo se implementó top-N para estructura/EQHL (S088); OB/FVG/IDM/Breaker quedaron con filtro puro de strength + ancla única.

**Principio rector que definió el usuario** (evolución del criterio):
1. Importancia = **relevancia estructural + confluencia**, NO fuerza×cercanía. Importa lo que está en **puntos de giro** y en el **origen del desplazamiento** (ruptura de estructura).
2. **"3 por lado" = mínimo de escenarios de proyección por profundidad** (cercano→retroceso corto · medio · origen/inducement inicial), con acceso opcional a 4.º/5.º más atrás. Son proyecciones; buscar confluencias = buscar patrones.
3. **No recortar draws lejanos** (fuera de Premium/Discount D1) si son objetivo de proyección bajo confluencia. El rango D1 es contexto, no tijera. (Corrige el "adiós al BSL 1.51" — puede ser draw válido.)
4. **Confluencia = métrica real de importancia** (conceptos apilados al mismo nivel).
5. Granularidad **por concepto Y por variación, caso por caso** (FVG≠trueFVG≠IFVG≠BPR). Ejemplos capturados: IFVG del origen del swing (antes del OB/LL) > IFVG de media; EQH en HH de giro > EQH neutro; sweep en el extremo que antecede el giro; FVG de desplazamiento > micro-internos.

**Alcance ampliado por el usuario:** el mismo modelo cognitivo (leer atrás + proyectar adelante bajo confluencia) debe unificar **visual + score + enjambre + agente decisor MT5**. El score debe pensar como **proyección verificable** (la proyección más exacta sube su score); cada agente del enjambre debe leer qué pasó atrás y proyectar adelante por concepto; el decisor MT5 tendrá un "cuaderno de confluencias"; el swarm debate y evoluciona por precisión de proyección.

**Entregables de esta adenda:**
- **`docs/planes/DOSSIER-FABLE-proyeccion-confluencia.md`** [NUEVO] — briefing completo a Fable (problemática, principio rector, inventario ~40 conceptos/variaciones, infraestructura Pine a reutilizar, 6 entregables A–F, restricciones, pregunta abierta §7: cómo hacer que la misma doctrina sea única fuente de verdad para render + score + cuaderno EA + debate del enjambre).
- **`docs/planes/ESQUELETO-FABLE-proyeccion-confluencia.md`** [NUEVO, entregado por Fable `claude-fable-5`, 345 líneas] — doctrina ordenada A–F. **Decisiones de diseño de Fable:** (1) **fuente única = 3 primitivos calculables** — `posRole` (GIRO/ORIGEN/INTERNO), `confDegree` (familias apiladas en ±tol×ATR = el mismo conteo de confluencias de zona §4.8 sin pesos), `depthBand` (banda 1–5 del retroceso); render+score+cuaderno EA+enjambre derivan de ellos sin re-implementar. (2) **2 fases** — A Visual-only (primitivos en Visual leyendo arrays CORE, SHA intacto) → B los promueve al CORE con ADR nuevo al abrir Fase 2 (mismas fórmulas, cero deuda). (3) `score_render_v2 = strength × wPos × (1+kConf·confDegree)` — la cercanía sale de la llave; profundidad vía `depthBand` (input `i_profundidad` default 3, max 5). Selección por celdas escalares concepto×lado×banda (≤40 ints, RE10045-safe, generaliza el ancla §2.3). (4) **guardián de draws** — `confDegree≥2` o pool alineado al bias = inmune al recorte (el BSL 1.51 vive); la confluencia además promociona familias de Estudio a Operación. (5) **exactitud de proyección = métrica darwiniana** (`0.4·dir + 0.4·nivel + 0.2·objetivo`) que calibra pesos Fase 3 y el score EMA del agente. Las 40 fichas §2 migran a `reglas-smc-ict.md §7` bajo gate sprint16 antes de codificar.
- Plan de trabajo vivo en `~/.claude/plans/la-primera-imagen-es-elegant-moler.md` (fuera del repo).

**Estado:** F1-GATE §10 sigue cerrado técnicamente; este rediseño es **trabajo NUEVO** (completa el top-N §4 diferido + lo extiende a proyección/confluencia/score/enjambre). **La firma F1-GATE queda supeditada a decidir si este rediseño entra antes de firmar o se firma el §10 actual y el rediseño va como sprint aparte** (decisión del usuario, próxima sesión, con el esqueleto de Fable en mano).

---

Ver [[Sesion-091]] · [[Sesion-090]] · [[re10045-arrays-y-agent-browser]] · [[eje2-paso5-ribbon-y-hallazgo-gate]].
