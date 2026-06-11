# reglas-dev.md — Reglas de desarrollo
> Estrategia 2.0 · Bot SMC/ICT · DOC-02 del WORKPLAN-MAESTRO-V2
> Convenciones obligatorias para Pine Script v6, MQL5, commits, branching y ADRs.
> La skill `smc-pine-develop` referencia este documento en su step `check-rule`.

Este documento define **cómo se escribe el código**, no qué hace (eso es [reglas-smc-ict.md](reglas-smc-ict.md)) ni en qué orden (eso es [WORKPLAN-MAESTRO-V2.md](../WORKPLAN-MAESTRO-V2.md) §3). Si una regla aquí choca con el plan, gana el plan y se corrige aquí.

---

## 0. PRINCIPIOS (orden de prioridad)

1. **Correcto antes que rápido.** Un concepto roto no avanza: compila 0/0 o no se commitea.
2. **Cuantificado antes que interpretado.** Todo umbral viene de [reglas-smc-ict.md](reglas-smc-ict.md). Si un número no está ahí, no se inventa en el código: se añade primero a la fuente de verdad.
3. **Anti-repaint por diseño, no por parche.** `[D-PINE-03]` Eventos solo en vela confirmada; `lookahead_off` siempre. No negociable.
4. **Un commit = un concepto verificado.** Nada de commits "WIP varios conceptos".
5. **El CORE es sagrado.** La sección `// === LIBRARY CORE ===` debe ser **byte-idéntica** en SMC-Visual y SMC-Strategy (lo vigila `check-core-sync.ps1`).
6. **Símbolo-agnóstico.** `[ADR-001]` Nada se hardcodea a EURUSD. Lo por-símbolo va como input/perfil.

---

## 1. PINE SCRIPT v6 — CONVENCIONES

### 1.1 Versión y declaración
- `//@version=6` obligatorio (no v5). `[D-PINE-02]`
- Visual: `indicator("SMC Engine — Visual", overlay=true, max_labels_count=500, max_lines_count=500, max_boxes_count=500)`.
- Strategy: `strategy("SMC Engine — Strategy", overlay=true, initial_capital=10000, default_qty_type=strategy.percent_of_equity, default_qty_value=1, commission_type=strategy.commission.cash_per_contract, process_orders_on_close=true)`. `[D-PINE-05]`
- Header de atribución LuxAlgo intacto en cualquier archivo que porte su algoritmo (CC BY-NC-SA). `[D-PINE-06]`

### 1.2 Naming

| Elemento | Convención | Ejemplo |
|---|---|---|
| Funciones de detección (librería/core) | `f_detect<Concepto>` / `f_<verbo><Cosa>` | `f_detectBOS`, `f_buildPools`, `f_computeSLTP` |
| Funciones de dibujo (solo Visual) | `f_draw<Concepto>` | `f_drawOB`, `f_drawKillZone` |
| UDTs | `SMC_<Nombre>` PascalCase tras prefijo | `SMC_Zone`, `SMC_Event`, `SMC_Swing`, `SMC_Pool`, `SMC_TFState` |
| Arrays globales | `SMC_<plural>` | `SMC_activeOBs`, `SMC_pools`, `SMC_swings` |
| Constantes enum `kind` | `KIND_<NOMBRE>` UPPER_SNAKE | `KIND_OB`, `KIND_FVG`, `KIND_CHOCH`, `KIND_SWEEP` |
| Inputs | `i_<grupo><Param>` camelCase | `i_swingLen`, `i_obShowMTF`, `i_emaLen200` |
| Pesos de scoring (input.float) | `w_<confluencia>` | `w_chochH1`, `w_sweepContra`, `w_obH1` |
| Variables locales | camelCase descriptivo, sin abreviaturas crípticas | `lastSwingHigh`, `mitigatedPct` |
| Snapshots MTF (tuples) | `<tf>_<campo>` | `d1_bias`, `h1_lastBOSPrice` |
| Booleans | prefijo `is`/`has`/`show` | `isConfirmed`, `hasSweep`, `showPanel` |

- **Prefijo `SMC_` en todo array global** (regla crítica de PINE-PLAN §2). Sin excepción.
- Nada de nombres de una letra salvo índices de loop (`i`, `j`).

### 1.3 Estructura del archivo (orden fijo de secciones)
Visual y Strategy siguen el mismo esqueleto; el CORE es idéntico en ambos.

```
1. //@version=6 + declaración + atribución
2. // === INPUTS ===            (agrupados: Estructura / OB / FVG / Liquidez / ICT / EMAs / MTF / KillZones / Panel / Estilo)
3. // === LIBRARY CORE ===      (UDTs + KIND_* + todas las f_detect*/f_compute*  — BYTE-IDÉNTICO en ambos archivos)
4. // === DETECCIÓN TF PROPIO === (llamadas a core sobre el chart actual)
5. // === MTF ===               (request.security snapshots D1/H1 — máx 2 en Strategy)
6. // === DIBUJO ===            (SOLO Visual: f_draw* + presupuesto de objetos)
7. // === SCORING ===           (SOLO Strategy: f_scoreConfluences → scoreLong/scoreShort)
8. // === ENTRADAS/SALIDAS ===  (SOLO Strategy: strategy.entry/exit + trailing)
9. // === PANEL ===             (tabla de estado)
10. // === ALERTAS ===
```

- Cada concepto con **toggle on/off** en inputs; si está off, se salta detección Y dibujo. `[FIX P-06]`
- Una `f_draw<Concepto>` por concepto, cada una con su propio array de objetos y su cuota (borra el más viejo al exceder). Presupuesto de objetos por tipo en PINE-PLAN §5.

### 1.4 Reglas de la librería/core `[restricciones duras Pine]`
1. El core **no dibuja** (nada de label/line/box/table dentro de `f_detect*`). El dibujo vive solo en Visual.
2. El core **no llama `request.security()`**. Los datos MTF se obtienen en el consumidor y se pasan **como parámetros**.
3. Las funciones del core **no leen globales mutables** del consumidor: reciben todo su estado por parámetro (arrays de UDT por referencia OK).
4. Funciones **puras respecto a su entrada**: misma entrada → misma salida. Facilita los golden tests de paridad con MQL5 (Fase 4).

### 1.5 Anti-repaint `[D-PINE-03 — INNEGOCIABLE]`
- Todo **evento** (BOS, CHoCH, MSS, sweep, displacement, grab, Judas…) se confirma SOLO con `barstate.isconfirmed`. Nunca intra-vela.
- Las **zonas** (OB, FVG, breaker…) pueden extenderse en vivo, pero su **creación** se confirma al cierre.
- `request.security(..., lookahead = barmerge.lookahead_off)` SIEMPRE.
- Prohibido usar el futuro: nada de `[-n]`, ni `security` con `lookahead_on`.
- Cada concepto pasa el **test anti-repaint** (PINE-PLAN §10.5): señales en tiempo real (paper 2 días) idénticas a las históricas en las mismas velas.

### 1.6 Performance `[FIX P-08]`
- Arrays con tamaño acotado: tras cada `array.push`, si `array.size(a) > MAX_X` → `array.shift(a)`. Límites default: zonas 50/TF, eventos 100/TF, swings 100/TF.
- Máx 2 `request.security` en Strategy (D1, H1); Visual hasta 4. Muy por debajo del límite de 40.
- Modo `Present` (default): dibujar solo las últimas N barras (input, default 500).
- Objetivo: cargar 20k barras M5 sin "Calculation takes too long".
- Loops acotados; nada de recorrer arrays completos en cada vela si se puede mantener estado incremental.

### 1.7 Prohibiciones
- ❌ Hardcodear umbrales en pips fijos → siempre múltiplos de ATR. `[reglas-smc-ict §0]`
- ❌ Hardcodear EURUSD, sesiones GMT fijas sin DST, o cualquier constante por-símbolo. `[ADR-001, P-25]`
- ❌ Números mágicos sin input ni constante nombrada.
- ❌ Divergencia entre el CORE de Visual y Strategy.
- ❌ Commitear con warnings de compilación.

---

## 2. MQL5 — CONVENCIONES (Fase 4, resumen)
> Detalle completo en [MQL5-PLAN.md](workplan/MQL5-PLAN.md). Aquí solo lo transversal.

- Arquitectura modular: `SMC_Structures.mqh` · `SMC_Liquidity.mqh` · `SMC_MTF.mqh` · `SMC_Scoring.mqh` · `SMC_RiskManager.mqh` · `SMC_Display.mqh` + `EA_SMC_ICT.mq5`.
- **Traducción función a función** desde la librería Pine (que es la spec), con **golden tests de paridad**. La arquitectura del EA sí es nativa (OnTick, gestión de órdenes, riesgo). `[R-13]`
- Naming: clases/structs `S<Nombre>`, métodos PascalCase, miembros `m_<nombre>`, constantes `INP_`/`#define UPPER`.
- Targets de performance propios del EA: < 50 ms/tick · < 100 MB RAM · paridad de detección con el Pine validado (golden tests 100% verdes).
- Cero operaciones intra-vela: el EA opera **velas cerradas** (coincide con anti-repaint de TV).

---

## 3. COMMITS

### 3.1 Formato (Conventional Commits + ID de tarea)
```
<tipo>(<ámbito>): <ID-tarea> <resumen imperativo en presente>

[cuerpo opcional: qué y por qué, no cómo]
```
- **Tipos:** `feat` · `fix` · `docs` · `refactor` · `test` · `chore` · `perf`.
- **Ámbito:** la fase o módulo — `fase-0`, `pine-core`, `visual`, `strategy`, `mql5`, `scripts`, `docs`.
- **ID-tarea:** el del workplan (`DOC-02`, `F1-S1.1-T03`, `VER-09`…). Hace rastreable cada commit contra el plan.

**Ejemplos:**
```
docs(fase-0): DOC-02 reglas-dev — convenciones Pine v6, commits, branching
feat(pine-core): F1-S1.1-T03 detección BOS+CHoCH swing e interno
fix(visual): F1-S1.2-T05 OB no se mitigaba por close en MTF
perf(strategy): F2-T01 acotar array de eventos a 100/TF
```

### 3.2 Reglas
- **Un commit = un concepto verificado** (compila 0/0 + validado ≥90 si aplica). No mezclar conceptos.
- Mensaje en español, imperativo, presente.
- Nada de secretos en el commit (los vigila `.gitignore`; keys solo por env var). `[FIX P-07]`
- Antes de commitear código Pine: `check-core-sync.ps1` debe pasar.
- Co-autoría de Claude al final del mensaje cuando aplique.

---

## 4. BRANCHING

| Rama | Uso |
|---|---|
| `main` | Estado estable y verificado. Cada gate de fase deja un tag aquí. |
| `fase-N/<sprint-o-tarea>` | Trabajo de un sprint/tarea concreta. Ej.: `fase-1/s1.1-fundacion`, `fase-2/scoring`. |
| `fix/<descripcion>` | Correcciones puntuales fuera de un sprint. |

- Mientras dura la Fase 0 (documentos) se trabaja directo sobre `main` con commits atómicos por DOC (no requiere ramas — no hay código que romper).
- Desde Fase 1 (código Pine): rama por sprint, merge a `main` al pasar el gate parcial del sprint.
- **Tags de gate:** `fase-1-completa`, `fase-2-completa`, `fase-3-completa` (más los sub-gates A-D de Fase 4). Un tag = un gate del workplan pasado.
- Regla absoluta del plan: **ningún gate se salta.** Si un gate falla → se retrocede, no se ajusta el criterio. `[§4.2 workplan]`

---

## 5. CUÁNDO CREAR UN ADR
> ADRs en `docs/adrs/ADR-NNN-<slug>.md`. Los escribe `smc-architect` (Opus). Histórico: ADR-001 ya existe (multi-símbolo).

Se crea un ADR cuando una decisión:
1. **Cambia la arquitectura** (estructura de archivos, comunicación entre módulos, contrato de datos). Ej.: migrar el core copiado → library publicada (D-PINE-01).
2. **Es difícil de revertir** o costosa de cambiar después (elección de broker, formato de golden tests, esquema de scoring).
3. **Afecta a varias fases** o a la portabilidad multi-símbolo.
4. **Contradice o supera una decisión previa** (entonces el nuevo ADR marca al anterior como *superseded*).
5. **Resuelve una "pregunta abierta"** del workplan §5 (threshold de score, qué Tier 3 probar, broker Fase 4).

**No** requieren ADR: ajustes de parámetros dentro de rangos ya definidos, fixes de bugs, cambios de naming, decisiones reversibles en minutos. Esas van en el commit y, si son relevantes inter-sesión, en `memory/ESTADO-ACTUAL.md`.

**Formato ADR:** Contexto → Decisión → Alternativas consideradas → Consecuencias → Estado (`Propuesto`/`Aceptado`/`Superseded por ADR-NNN`). Numeración secuencial.

---

## 6. CICLO DE DESARROLLO POR CONCEPTO (Fases 1-2)
> El workflow `smc-sprint` (ver [WORKFLOWS.md](workplan/WORKFLOWS.md)) automatiza este ciclo. Skill principal: `smc-pine-develop`.

```
1. check-rule   → confirmar que el concepto está cuantificado en reglas-smc-ict.md (si no → parar, definir primero)
2. implement    → escribir en el CORE/Visual/Strategy según corresponda (skill smc-pine-develop)
3. compile      → TV MCP pine_smart_compile → 0 errores / 0 warnings (si falla → agente pine-build-resolver)
4. validate     → screenshot EURUSD + skill smc-validator → score ≥90 contra reglas-smc-ict.md (agente smc-validator-agent)
5. core-sync    → check-core-sync.ps1 (si tocó el CORE)
6. approve       → aprobación humana (Freddy)
7. commit       → un commit atómico con ID de tarea
```
- Nunca avanzar al siguiente concepto con el actual roto o sin validar.
- Si validate < 90 → corregir y repetir desde el paso que falló (no acumular deuda).

---

## 7. DOCUMENTACIÓN Y MEMORIA
- **Fuente de verdad SMC:** [reglas-smc-ict.md](reglas-smc-ict.md). Si una definición cambia ahí, cambia en todo el sistema.
- **Estado inter-sesión:** `memory/ESTADO-ACTUAL.md` (lo actualiza `smc-doc-updater` en cada cierre).
- **Sesiones numeradas:** `memory/sesiones/Sesion-NNN.md`.
- **Checkboxes del workplan:** los marca `smc-doc-updater` al completar cada tarea.
- Comentarios en el código: explican el **por qué** (la regla que implementan, con referencia `[reglas-smc-ict §X]`), no el qué obvio.

---

*DOC-02 · Estrategia 2.0 · 2026-06-10 — referenciado por skill smc-pine-develop (step check-rule)*
