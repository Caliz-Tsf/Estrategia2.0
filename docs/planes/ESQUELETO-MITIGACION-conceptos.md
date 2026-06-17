# Esqueleto de implementación — Ciclo de vida / mitigación de todos los conceptos

> Sesión S028 · Fase 1 · rama `pine/sistema-completo`.
> **Qué es:** el *esqueleto* (estructura + firmas + contratos + puntos de integración) para añadir ciclo de vida / mitigación a cada concepto SMC, de modo que el gráfico deje de saturarse ("ruido sin mitigación"). Deriva de la decisión del usuario en `docs/planes/HANDOFF-OPUS-MAX-pools-mitigacion.md` (Opción A = mitigación completa + Propuesta B de display).
> **Qué NO es:** NO es código funcional. Cada cuerpo de función queda como `// TODO [impl]` con su contrato; **el implementador ("Opus Medio") escribe la lógica**. Este documento NO toca ningún `.pine` (para no romper *compila 0/0* ni el *core byte-idéntico*); es el plano que la siguiente IA integra.
> **Para quién:** la IA que implemente (referida aquí como **[impl]**). Léelo junto a `reglas-smc-ict.md` (fuente de verdad SMC) y `docs/workplan/PINE-PLAN.md` §2/§4/§5.

---

## 0. Reglas duras que el implementador DEBE respetar (innegociables)

Copiadas de `CLAUDE.md` — si el esqueleto y una regla chocan, manda la regla:

1. **Anti-repaint `[D-PINE-03]`.** Todo *evento* (incluido "pool barrido") se evalúa SOLO en `barstate.isconfirmed`. Nunca intra-vela. Las *zonas* pueden extenderse en vivo, pero su creación se confirma al cierre.
2. **Core byte-idéntico (regla #2).** Toda función nueva del núcleo va en la sección `// === LIBRARY CORE ===` **idéntica** en `SMC-Visual.pine` y `SMC-Strategy.pine`, y en versión `export` en `SMC-Library.pine`. Tras tocar el CORE → `scripts/check-core-sync.ps1` debe dar OK.
3. **Umbrales relativos a ATR (regla #3).** Nada de pips fijos. Toda tolerancia/umbral nuevo se expresa `× ATR(n)` y entra como `input`. Reusar `i_poolTol`, `i_eqThreshold`, etc.; no inventar constantes hardcodeadas.
4. **Funciones CORE puras.** Reciben datos por parámetro (precios, arrays), no leen series globales ni `request.security()`, no dibujan. Esto es lo que habilita los **golden tests MQL5 (ADR-002)**. El estado persistente (`var`) y el dibujo viven en el consumidor, NO en el CORE.
5. **Compila 0/0 (regla #7).** Un commit = un concepto verificado, 0 errores / 0 warnings en los 3 scripts. No commitear stubs que no compilen.
6. **Símbolo-agnóstico `[ADR-001]`** y **umbrales congelados hasta Fase 3 `[ADR-002]`.** El ruido residual tras mitigar (muchos pools con `0.1/2`) es **calibración Fase 3**, NO se "arregla" bajando umbrales aquí.

---

## 1. Mapa de archivos y secciones (dónde va cada pieza del esqueleto)

Las 3 piezas de cada concepto caen siempre en las mismas secciones canónicas:

| Pieza | `SMC-Library.pine` | `SMC-Visual.pine` | `SMC-Strategy.pine` |
|---|---|---|---|
| UDTs + constantes + funciones puras | sección raíz `export …` | `// === LIBRARY CORE ===` | `// === LIBRARY CORE ===` (idéntico a Visual) |
| Estado persistente (`var`) + wiring de detección | — | `// === DETECCIÓN TF PROPIO ===` | `// === DETECCIÓN TF PROPIO ===` (idéntico salvo lo visual) |
| Dibujo (`f_draw*` + repintado en `barstate.islast`) | — | `// === DIBUJO ===` | — (la Strategy no dibuja) |
| Lectura para scoring | — | — | `// === SCORING ===` |

**Convención de marca para el esqueleto:** al integrar, etiqueta cada bloque nuevo con el patrón y la tarea, p. ej. `// [P1 · T09b] …`, `// [P2 · T19] …`. Así el siguiente revisor localiza el ciclo de vida de un vistazo.

**Nomenclatura de estados (a añadir como constantes `KIND_*`-style en el CORE):** ver cada patrón. Reusar las existentes (`ZS_ACTIVE/PARTIAL/MITIGATED/INVALID`, `DIR_BULL/BEAR`) siempre que se pueda.

---

## 2. Los 4 patrones canónicos de ciclo de vida

Esqueletizar **una vez** y reutilizar. Cada concepto de §3 apunta a uno de estos.

### P1 — Nivel consumido por barrido  *(Pools BSL/SSL, IDM)*

**Idea.** Un *nivel* (precio único) es imán mientras NO ha sido barrido. Al barrerse (el precio cruza el nivel), se consume: deja de ser imán y pasa a historial (marcador de barrido — Propuesta B). Reemplaza el modelo "rebuild stateless cada vela" por **estado persistente**.

**Estado (campos a añadir al UDT del nivel — ver `SMC_Pool` en §3.A):**
```
    bool swept       = false   // ya existe: false = vivo (imán), true = consumido
    int  sweptBarTime = na     // NUEVO: ancla temporal del barrido (marcador Propuesta B)
    int  sweptBarIdx  = na     // NUEVO: ancla por índice (dibujo robusto a gaps de finde)
    int  barIdx       = na      // NUEVO si falta: barra de origen (hoy solo hay barTime)
```

**Firmas CORE (puras) — cuerpos `// TODO [impl]`:**
```
// f_mark<X>Swept: marca como barrido cada nivel VIVO cruzado en la barra actual.
// Contrato: muta los niveles in situ; BSL (dir==DIR_BULL) barrido si barHigh >= level;
// SSL (dir==DIR_BEAR) barrido si barLow <= level. Al barrer: swept:=true +
// sweptBarTime/sweptBarIdx. PURA (recibe high/low por parámetro) -> golden test MQL5.
// Llamar SOLO en barstate.isconfirmed (anti-repaint). Devuelve el array mutado (o el
// nº barridos en la barra, si el dibujo del marcador lo necesita — decidir al implementar).
f_markPoolsSwept(array<SMC_Pool> pools, float barHigh, float barLow, int barTime, int barIdx) =>
    // TODO [impl]: recorrer pools; saltar swept==true; aplicar la regla de cruce por lado.
    pools

// f_upsertPool: alta/merge INCREMENTAL de un candidato contra el set VIVO (reemplaza el
// rebuild de f_buildPools). Contrato: busca un pool vivo (swept==false) del mismo lado
// (isHigh) dentro de tolPrice; si existe -> merge (touches += weight; level = media corrida;
// barTime = max); si no -> alta nueva. La promoción a "visible" (touches >= minTouches) la
// decide el dibujo/scoring, no esta función. PURA -> golden test MQL5.
f_upsertPool(array<SMC_Pool> pools, bool isHigh, float level, int weight, int barTime, int barIdx, float tolPrice) =>
    // TODO [impl]: clustering incremental (reusar la lógica de proximidad de f_buildPools,
    // aplicada a UN candidato contra el set vivo, no a todo el histórico).
    pools
```

**Dibujo (Propuesta B, solo Visual):**
- Niveles `swept == false` → línea viva de `barTime` → barra actual (como hoy `f_drawPools`).
- Al pasar a `swept == true` → **terminar la línea en `sweptBarTime`** (no extender a la derecha) + dibujar **marcador**: `✗` + etiqueta `Sweep ↓` (BSL, rojo) / `Sweep ↑` (SSL, verde) anclada en `sweptBarTime`/`sweptBarIdx`. Opcional: *ghost* tenue unas velas y luego borrar.

**Nota MQL5 / golden tests.** El modelo persistente (merge incremental + marca) **reemplaza la pureza del rebuild** de `f_buildPools`. Documentar el cambio: el EA opera incremental/vivo, así que el persistente es **más fiel** al EA (ventaja, no deuda). Construir los golden tests sobre el estado vivo, no sobre el set reconstruido.

---

### P2 — Zona con máquina de 4 estados  *(Breaker, Mitigation block, OTE/Golden Pocket)*

**Idea.** Una *zona* (rango `[bottom, top]`) ya tiene ciclo de vida resuelto: la máquina `f_updateZoneMitigation` (ACTIVE→PARTIAL→MITIGATED→INVALID) que usan OB (T05) y FVG (T06). **No reinventar**: estos conceptos reutilizan `SMC_Zone` + esa máquina; cambian solo `kind` y de dónde nace la zona.

**Reutilización directa (sin código nuevo de mitigación):**
- **Breaker (T19, `KIND_BREAKER`):** nace de un OB que llega a `ZS_INVALID` → re-crear como zona `KIND_BREAKER` con `dir` invertido. La mitigación posterior usa la MISMA `f_updateZoneMitigation`.
- **Mitigation block (tier2, `KIND_MITIGATION`):** zona = high/low de la última vela contraria antes del impulso (sin sweep previo). Mitigación = misma máquina, sin cambios.

**Extensión necesaria — expiración por objetivo (solo OTE/GP):**
```
// f_expireOTE: la zona fib OTE/GP no se "mitiga" como un OB; CADUCA cuando el precio
// alcanza el objetivo del impulso (TP del swing origen) o cuando el swing origen se invalida.
// Contrato: si se cumple la condición de caducidad -> z.state := ZS_MITIGATED (o ZS_INVALID).
// Reusa SMC_Zone; añade el nivel objetivo como parámetro (no nuevo campo si se deriva del swing).
f_expireOTE(SMC_Zone z, float targetLevel, bool originInvalidated) =>
    // TODO [impl]: marcar caducidad; el dibujo deja de mostrarla igual que una zona mitigada.
    z
```
**Dibujo.** Idéntico patrón a OB/FVG (`f_drawOB`/`f_drawFVG`): color por `kind`, transparencia por `state`, no dibujar `ZS_INVALID`. Reusar el loop de repintado en `barstate.islast`.

---

### P3 — Nivel con cambio de rol, invalidable  *(Flip)*

**Idea.** Un nivel roto **por cierre limpio** queda "pendiente de retest"; si el precio lo retestea desde el otro lado y respeta → *flip* confirmado (soporte↔resistencia). Se invalida si una vela vuelve a cruzarlo limpio. Es un ciclo de vida de *nivel* (no zona, no barrido simple).

**Estado (constantes nuevas en CORE + UDT ligero o reuso de `SMC_Event`):**
```
// Estados del flip (definir al implementar T21):
//   LF_PENDING = 0   nivel roto por cierre, esperando retest desde el otro lado
//   LF_FLIPPED = 1   retesteado y respetado -> cambio de rol confirmado (KIND_FLIP)
//   LF_INVALID = 2   re-cruzado limpio -> el flip se anula (terminal)
// f_updateFlip: avanza el estado del nivel según el close de la barra. PURA.
f_updateFlip(/* nivel roto + dir + estado actual */) =>
    // TODO [impl]: PENDING -> FLIPPED si retest respeta; cualquier estado -> INVALID si re-cruce
    //              limpio. Anti-repaint: por CIERRE, en barstate.isconfirmed.
    na
```
**Nota.** Patrón menos crítico (1 nivel, baja densidad). Definir el contenedor (type propio mínimo vs `SMC_Event` + campo estado) al implementar T21. El "cierre limpio" lo distingue del sweep (mecha) — ver `reglas-smc-ict.md` §2.8.

---

### P4 — Eventos puntuales + "Present mode"  *(Sweep, Grab, MSS, Judas, Displacement, Rejection, False Breakout)*

**Idea.** Estos **NO mitigan** (son marcas históricas en una vela). Pero saturan igual si se dibujan todos. Solución = **límite de presentación** (PINE-PLAN §5 "presupuesto por concepto", y "Visual mínimo"): dibujar solo las últimas N ocurrencias / solo dentro de la ventana "presente".

**Mecanismo común (esqueleto de dibujo, solo Visual — no toca el CORE):**
```
// Convención de cuota por concepto: cada familia de eventos dibuja como máximo i_maxShow<X>
// marcas (las más recientes). Estado: arrays SMC_events / SMC_eqhl / SMC_eventsMajor ya existen.
// El loop de dibujo itera solo los últimos i_maxShow<X> elementos (o filtra por bar_index >=
// bar_index - i_presentBars). Input nuevo por familia: i_maxShowSweeps, i_maxShowMSS, ...
// TODO [impl]: helper de dibujo acotado, p. ej. f_drawLastN(array, n, drawFn) o un guard de
// índice en cada loop existente. NO almacenar de más: respetar MAX_EVENTS=100 / labels 500.
```
**Nota.** El marcador de barrido de los pools (P1, Propuesta B) **es** el evento visual del Sweep (T10): diseñar T10 (clasificación trampa: mecha que perfora + cierre de vuelta, peso direccional para el scoring §3.2) y el marcador de P1 **juntos**, para no duplicar el dibujo del barrido.

---

## 3. Tabla maestra concepto → patrón → integración

| Concepto | Tarea | Patrón | UDT / máquina | Función(es) nueva(s) CORE | Estado |
|---|---|---|---|---|---|
| **Pools BSL/SSL** | T09→T09b | **P1** | `SMC_Pool` (+campos swept*) | `f_markPoolsSwept`, `f_upsertPool` | refactor (este plan, §3.A) |
| Sweep / Grab | T10 | P4 (es el EVENTO que consume P1) | `SMC_Event` | `f_detectSweep`, `f_detectGrab` | marca `pool.swept` (usa P1) |
| Kill Zones | T11 | — (ventana de fondo) | — | `f_killZone` | sin ciclo de vida |
| MSS | T12 | P4 | `SMC_Event` | `f_detectMSS` | marca histórica |
| Displacement | T16 | P4 | `SMC_Event` | `f_detectDisplacement` | marca histórica |
| **IDM (inducement)** | T17 | **P1** | nivel (reusa lógica swept) | `f_detectIDM` (+marca swept del nivel interno) | §3.B |
| Judas | T18 | P4 | `SMC_Event` | `f_detectJudas` | marca histórica |
| **Breaker** | T19 | **P2** | `SMC_Zone` + `f_updateZoneMitigation` | `f_detectBreaker` (de OB invalidado) | §3.C |
| Rejection | T20 | P4 | `SMC_Event` | `f_detectRejection` | marca en la vela |
| **Flip** | T21 | **P3** | nivel + estados LF_* | `f_updateFlip` (+`f_detectFlip`) | §3.D |
| **OTE / Golden Pocket** | T22 | **P2 + expiración** | `SMC_Zone` + `f_expireOTE` | `f_detectOTE` | §3.E |
| EMAs | T23 | — (siempre vivo) | — | — | dinámico |
| False Breakout | T24 | P4 | `SMC_Event` | `f_detectFalseBreakout` | marca histórica |
| Impulsive/Corrective | T25 | — (clasificación) | — | — | estado |
| **Mitigation block** | tier2 | **P2** | `SMC_Zone` + `f_updateZoneMitigation` | `f_detectMitigationBlock` | reusa máquina |
| OB | T05 | P2 | `SMC_Zone` | (hecho) | ✅ `f_updateZoneMitigation` |
| FVG | T06 | P2 | `SMC_Zone` | (hecho) | ✅ misma máquina |

---

### 3.A — Pools (T09 → T09b): refactor a persistente con ciclo de vida  *(caso piloto de P1)*

Es el detonante del plan y el más detallado. **Hoy** (`SMC-Visual.pine` sección `// --- Pools de liquidez [T09] ---`, y gemelo en Strategy) se hace `array.clear(SMC_pools)` + rebuild completo cada vela relevante → imposible recordar `swept`. **Objetivo:** estado persistente.

**A.1 — UDT `SMC_Pool` (CORE: Library `export type` + Visual/Strategy idéntico).** Añadir los campos de P1:
```
type SMC_Pool
    float  level
    int    dir
    int    touches      = 1
    int    barTime
    bool   swept        = false
    string tf           = ""
    int    barIdx       = na    // NUEVO: barra de origen (anclaje dibujo)
    int    sweptBarTime = na    // NUEVO: ancla del marcador de barrido
    int    sweptBarIdx  = na    // NUEVO
```

**A.2 — CORE.** Añadir `f_markPoolsSwept` y `f_upsertPool` (firmas en §2-P1). **Mantener** `f_buildPools` por ahora (útil para el *seeding* inicial del histórico); marcar en su comentario que el set vivo ya no se reconstruye cada vela. Decidir al implementar si `f_buildPools` se retira tras el seeding o se conserva.

**A.3 — DETECCIÓN (Visual y Strategy, idéntico salvo dibujo).** Reemplazar el bloque `if … poolsDirty: array.clear + rebuild` por:
```
// [P1 · T09b] Pools persistentes. En barstate.isconfirmed:
//   1) al confirmarse un EQH/EQL o swing relevante -> f_upsertPool(candidato) contra SMC_pools vivo.
//   2) SIEMPRE -> f_markPoolsSwept(SMC_pools, high, low, time, bar_index) (marca barridos de la barra).
// NO array.clear. El set persiste entre velas. (Strategy: igual, sin el paso de dibujo.)
// TODO [impl]: wiring; respetar el orden upsert -> mark; anti-repaint en isconfirmed.
```

**A.4 — DIBUJO (solo Visual, Propuesta B).** En el loop de repintado (`if i_showPools and barstate.islast`):
- pools `swept==false` → línea viva + etiqueta `BSL/SSL ·N` (como hoy).
- pools `swept==true` → línea que **termina en `sweptBarTime`** + marcador `✗`/`Sweep ↑↓` en el barrido. (Opcional ghost configurable con `input`.)
```
// TODO [impl]: f_drawPoolSwept(p) -> ✗ + etiqueta direccional en sweptBar*. Añadir input
// i_showSweptPools (mostrar/ocultar historial de barridos).
```

**A.5 — Library.** Replicar `export` de `f_markPoolsSwept` / `f_upsertPool` y los campos nuevos del `export type SMC_Pool`.

**A.6 — Verificación específica** (de HANDOFF §Verificación): en EURUSD H1, tras el cruce de precio el pool desaparece como imán y queda su marcador; imanes vivos quedan segregados (BSL arriba / SSL abajo del precio); los 3 casos §3.1 (BSL ~1.16615, SSL ~1.15948, SSL ~1.15274) aparecen y luego se marcan barridos donde corresponde.

---

### 3.B — IDM / Inducement (T17, P1)

- **Qué consume:** un **swing low/high interno** (escala `internalLen`) cuya liquidez se barre ANTES de que el precio alcance el OB/FVG objetivo (`reglas-smc-ict.md` §3.6). Mismo mecanismo "nivel consumido por barrido" que los pools.
- **CORE:** `f_detectIDM(...)` puro → identifica el nivel interno inducement; reutiliza la marca `swept` del nivel (mismo helper/idea que `f_markPoolsSwept`, aplicado a swings internos). Confluencia #33 = "IDM barrido".
- **DETECCIÓN:** en `barstate.isconfirmed`, tras detectar el objetivo (OB/FVG), comprobar si el inducement intermedio fue barrido. Anti-repaint.
- **DIBUJO:** marca puntual en el barrido (mismo estilo Propuesta B). Sin zona.

### 3.C — Breaker (T19, P2)

- **Nace de:** un OB que `f_updateZoneMitigation` llevó a `ZS_INVALID` (`reglas-smc-ict.md` §2.6 / PINE-PLAN §122). Re-crear como `SMC_Zone` `KIND_BREAKER`, `dir` invertido.
- **CORE:** `f_detectBreaker(zInvalidatedOB)` → devuelve la zona breaker. La mitigación posterior = `f_updateZoneMitigation` **sin cambios**.
- **DETECCIÓN:** en el loop de mitigación existente, cuando una zona OB pasa a `ZS_INVALID`, generar el breaker y empujarlo a `SMC_zones`.
- **DIBUJO:** patrón `f_drawOB`/`f_drawFVG` con color propio de breaker.

### 3.D — Flip (T21, P3)

- **CORE:** estados `LF_PENDING/FLIPPED/INVALID` + `f_updateFlip` (firma en §2-P3). El nivel origen = swing/OB/EQHL roto por **cierre limpio**.
- **DETECCIÓN:** rastrear el nivel roto; avanzar estado en `barstate.isconfirmed`.
- **DIBUJO:** línea del nivel con estilo por estado (pendiente punteado / confirmado sólido / invalidado se omite).

### 3.E — OTE / Golden Pocket (T22, P2 + expiración)

- **CORE:** `f_detectOTE(swing)` → zona fib (61.8–79% = OTE `KIND_OTE`; 50–61.8% = GP `KIND_GP`, PINE-PLAN §125). `f_expireOTE` (firma en §2-P2) para la caducidad por objetivo/invalidación del swing.
- **DETECCIÓN:** tras BOS confirmado, crear la zona; cada barra, `f_updateZoneMitigation` + `f_expireOTE`.
- **DIBUJO:** zona fib como OB/FVG; al caducar, deja de dibujarse.

---

## 4. Checklist de integración (para [impl])

Orden recomendado (de mayor palanca a menor):

1. **T09b — Pools persistentes (P1)** primero: es la palanca grande contra el ruido y el caso piloto del patrón. Unificar con **T10 (Sweep)** porque el marcador de barrido = evento de sweep.
2. **T17 IDM (P1)** reutilizando el helper de marca de la familia P1.
3. **T19 Breaker + Mitigation block (P2)** — casi gratis: reutilizan `f_updateZoneMitigation`.
4. **T22 OTE/GP (P2+expiración)** y **T21 Flip (P3)**.
5. **P4 / Present mode** transversal: aplicarlo al dibujo de los eventos puntuales cuando se implementen (T10/T12/T16/T18/T20/T24), con cuota por concepto.

Por cada concepto, antes de commit:
- [ ] CORE byte-idéntico Visual/Strategy → `scripts/check-core-sync.ps1` = OK.
- [ ] `export` equivalente en `SMC-Library.pine`.
- [ ] `pine_set_source` + `pine_smart_compile` + `pine_get_errors` los 3 → **0/0**.
- [ ] Funciones CORE puras (sin series globales, sin dibujo) → preparado para golden test MQL5 (ADR-002).
- [ ] Anti-repaint: eventos/marcas solo en `barstate.isconfirmed`.
- [ ] Validación `smc-validator-agent` **≥90** contra `reglas-smc-ict.md`.
- [ ] ¿ADR? El cambio de pools stateless→persistente merece ADR ("Pools persistentes con ciclo de vida; reemplaza el rebuild de T09").

## 5. Documentos relacionados
- Decisión y display: `docs/planes/HANDOFF-OPUS-MAX-pools-mitigacion.md`.
- Spec SMC (fuente de verdad): `docs/reglas-smc-ict.md` §2.1 (mitigación de zona), §2.6 (breaker), §2.8 (flip/mitigation block), §3.1 (pools), §3.2 (sweep), §3.6 (IDM).
- Plan Pine: `docs/workplan/PINE-PLAN.md` §2 (UDTs/kind), §4 (detección), §5 (dibujo/presupuesto por concepto).
