# ESQUELETO — Sistema visual definitivo del indicador SMC/ICT (entregable Fable)

> **Sesión:** S083 · Fase 1 · rama `pine/sistema-completo` · Eje 2 "Fuerza" / orden visual (último eje del gate visual F1).
> **Qué es:** el **esqueleto completo del sistema visual** que pidió `DOSSIER-FABLE-sistema-visual.md` §3. Respuesta directa a la problemática (502 líneas + 502 labels, solapes, 0 jerarquía) y crítica formal al plan interno (Parte E del dossier / HANDOFF-ULTRACODE §5–§6).
> **Qué NO es:** NO es código. NO toca ningún `.pine`. Todo número es **candidato CONGELADO hasta Fase 3** (ADR-002). Cada decisión de cableado queda como slot `[impl]` — **Opus rellena/implementa** bajo los gates del proyecto (compila 0/0 → validador ≥90 → core-sync → commit por concepto).
> **Léelo junto a:** `DOSSIER-FABLE-sistema-visual.md` (problemática + inventario Parte C), `HANDOFF-OPUS-ULTRACODE-discriminacion-visual.md` §5–§6 (motor strength, base que este esqueleto conserva), `METODOLOGIA-VERIFICACION-VISUAL.md` (4 ejes + MTF), `docs/reglas-smc-ict.md` §6 (fichas de fuerza por concepto), ADR-010 (MTF anclado), ADR-012 (invalidación Q1–Q7).

---

## §0 — Veredicto sobre el plan interno (Parte E) — qué se conserva, qué se corrige

### §0.1 Se CONSERVA (no re-litigar al rellenar)

| Pieza del plan E | Veredicto |
|---|---|
| Motor `strength` en CORE (E.1): campo en `SMC_Zone`/`SMC_Event`/`SMC_Swing`/`SMC_Pool` + `f_zoneStrength`/`f_eventStrength` puras, solo al cierre, reusando `atr14` | ✅ **Correcto tal cual.** Los primitivos y pesos candidatos de E.1 son razonables como punto de partida. |
| Quantización `f_strengthLevel` a 3 niveles 0/1/2 (E.2) | ✅ Correcto. |
| `i_densidad` con 3 modos como filtro transversal ADICIONAL a los `i_show*` (E.4) | ✅ Correcto (con la matriz curada de §8, no "todo en Primario"). |
| Top-N por familia con `f_nearestN`/`f_nearestNPools` como presupuesto de tinta (E.4) | ✅ Correcto como mecanismo; se le añade un presupuesto GLOBAL (§6.5). |
| Terciario = oculto pero CONTADO en panel T14 (E.3) | ✅ Correcto; el contrato exacto está en §9. |

### §0.2 Se CORRIGE (los 8 huecos del plan E)

1. **La fuerza sola NO ordena el chart.** `strength` compara marcas *dentro* de una familia; no dice si un grid de fondo pesa más que un sweep. Falta la dimensión **CAPA (rol visual)**: fondo / marco / zona / evento / overlay (§2–§3). La jerarquía es **capa primero, fuerza después**.
2. **Hay conceptos que son Primarios por ROL, no por fuerza** (respuesta a pregunta E.5.1): las **anclas estructurales** (§2.3) se dibujan siempre, independiente del `strength` calculado. `f_visualLevel(sLevel, withinCap)` tal como está en E.3 ocultaría un ancla fuera de cap — el cap se aplica **después** de reservar las anclas.
3. **El alternado izquierda/derecha NO resuelve 10 labels al mismo precio.** Falta la **consolidación de etiquetas** (§6.2): un cluster de labels a ≤tol×ATR del mismo nivel se fusiona en UNA label combinada (`"OB·FVG·BPR (D1)"`). Es el arreglo principal del amontonamiento en 1.14.
4. **El choque Grid vs Kill Zones no es de z-order, es de FILLS.** Dos familias pintando área a chart completo se ensucian a cualquier z-order. Regla nueva: **"un solo fondo de área"** (§6.3) — el grid Gradient/PD posee el eje de PRECIO (líneas, sin fill grande); las Kill Zones poseen el eje de TIEMPO y se degradan a **tira/ribbon** (respuesta a E.5.2).
5. **Falta el contrato MTF de relevancia heredada** (el énfasis explícito del usuario): lo declarado importante en D1 **no puede desaparecer** en H1/M5, y lo importante de H1 no puede desaparecer en M5. Se codifica como **regla de herencia descendente obligatoria** (§7.1): el TF menor no puede silenciar lo que el TF mayor declaró Primario.
6. **Falta el presupuesto GLOBAL de tinta.** Top-N por familia × 12 familias sigue siendo ~60–120 objetos. Se añade tope global por modo con desalojo determinista (§6.5).
7. **Falta el decaimiento del ciclo de vida en lo visual.** `state` ya alimenta el strength, pero visualmente una zona mitigada debe **degradarse de forma** (pierde fill, queda borde) — no solo bajar de nivel (§5.4).
8. **El modo Operación necesita curación de FAMILIAS, no solo de niveles** (respuesta a E.5.3): mostrar las 12 familias "en Primario" sigue sucio. Operación usa una whitelist curada (§8.2).

### §0.3 Respuestas a las 6 preguntas abiertas (E.5) — decisiones de este esqueleto

| # | Pregunta | Decisión |
|---|---|---|
| 1 | ¿Fuerza sola decide? | **No.** Capa (rol) → anclas → fuerza → cap, en ese orden (§2). |
| 2 | ¿Grid vs Kill Zones? | Ejes ortogonales: grid = precio (líneas), KZ = tiempo (ribbon). Regla "un solo fondo de área" (§6.3). Mismo pane; NO se saca a pane aparte (perdería la lectura precio-sobre-grid). |
| 3 | ¿Operación = todas las familias? | **No.** Whitelist curada de 7 familias (§8.2); el resto vive en panel/Estudio. |
| 4 | ¿Procedencia MTF? | Color = familia SIEMPRE; la procedencia va en **grosor + tag `(D1)`/`(H1)` + estilo de borde** (§7.2). Fusión heredado+nativo = un solo objeto con rótulo combinado. |
| 5 | ¿Sistema de color? | 4 dimensiones ortogonales: **hue = familia · dirección = glifo+tono · jerarquía = transparencia+grosor · procedencia = borde+tag** (§5). Prioridad al chocar: familia > jerarquía > dirección. |
| 6 | ¿Métricas de "chart legible"? | Checklist medible §10 (presupuesto global, ≤2 labels por franja 0.25×ATR, 0 fills solapados, 100% heredados con tag, panel cuenta 100% de lo oculto). |

---

## §1 — Principios de diseño (axiomas del sistema visual)

1. **El chart es un mapa, no un log.** Se dibuja lo que ayuda a decidir AHORA; el historial vive en el panel y en los arrays (la detección nunca se recorta — solo la tinta).
2. **Tinta proporcional a decisión.** Peso visual (opacidad, grosor, tamaño de label) ∝ relevancia operativa (capa + fuerza + cercanía + frescura).
3. **Un solo fondo de área.** Como máximo UNA familia pinta área grande simultáneamente; las demás familias de contexto son líneas o tiras (§6.3).
4. **Ejes ortogonales.** Conceptos de PRECIO (grid, niveles, zonas) no compiten con conceptos de TIEMPO (sesiones, macros): cada eje tiene su forma canónica y su franja del chart.
5. **La relevancia se hereda hacia abajo (MTF).** Lo Primario en D1 es visible en H1 y M5; lo Primario en H1 es visible en M5. El TF menor jamás silencia al mayor (§7.1).
6. **El color identifica QUÉ es.** Una familia = un hue, en todos los TF y todos los niveles. Dirección, fuerza y procedencia se expresan en otras dimensiones (§5).
7. **Todo lo oculto se cuenta.** Ninguna marca desaparece en silencio: cae al contador de su familia en el panel T14 (§9).
8. **Determinista y auditable.** Cada decisión de render (nivel, fusión, desalojo) sale de una regla reproducible con números — verificable por el validador (§10).

---

## §2 — Modelo de jerarquía: CAPA × NIVEL (la regla determinista)

### §2.1 Las dos dimensiones

- **CAPA (rol visual)** — a qué estrato del mapa pertenece la familia. Fija por familia (tabla §3). Decide z-order, forma canónica y contra quién compite por tinta.
- **NIVEL (Primario/Secundario/Terciario)** — cuánto grita una marca individual dentro de su capa. Derivado de `strength` + anclas + cap (§2.4).

### §2.2 Pipeline determinista de render (orden de evaluación por marca)

```
1. ¿Su familia está ON (i_show*) y visible en el modo actual (i_densidad, matriz §8)?  NO → panel
2. ¿Es ANCLA estructural (§2.3)?                                    SÍ → Primario (salta cap)
3. nivel_base = f_strengthLevel(strength)                           // 0/1/2 del CORE (E.2, se conserva)
4. ¿Dentro del top-N de su familia (f_nearestN, orden strength×cercanía §2.5)?  NO → Terciario
5. ¿Heredada MTF con nivel Primario en su TF origen?                SÍ → mínimo Secundario aquí (§7.1)
6. nivel_final = min(nivel_base, techo del modo §8)                 → render según §5
7. ¿Terciario? → NO se dibuja → +1 al contador de su familia en T14 (§9)
```

`[impl]` — cablear como `f_visualLevel(...)` v2 en **Visual, fuera del CORE** (el CORE solo aporta `strength`/`f_strengthLevel`). Firma candidata: `f_visualLevel(int sLevel, bool isAnchor, bool withinCap, int mtfFloor, int modeCeiling)`.

### §2.3 Anclas estructurales (Primarias SIEMPRE, independiente de strength)

Máximo **~8 objetos** de ancla simultáneos — son el "esqueleto del mapa":

| Ancla | Fuente (ya existe) | Tinta |
|---|---|---|
| Estructura dominante vigente (último BOS/CHoCH swing-50 que define el bias) | `i_showMajor` / eventos estructura | línea + label del evento |
| Dealing range activo: Premium/Discount + quadrants del grid seleccionado | `f_premiumDiscount` + `f_selectGradientSource` | líneas de nivel (§6.3) |
| Zona activa más cercana **por lado** (1 arriba + 1 abajo del precio, la de mayor strength) | `f_nearestN` sobre OB/FVG/Breaker | caja |
| Pool de liquidez objetivo del bias (el draw: BSL si bias alcista, SSL si bajista) | `SMC_Pool` + bias | línea + label |
| Kill Zone activa (solo la EN CURSO) | `f_killzone` | ribbon (§6.3) |

`[impl]` — decidir el tie-break exacto cuando hay 2 candidatos a "zona más cercana por lado" con strength igual (candidato: la más fresca). Las anclas NO consumen el top-N de su familia (se reservan aparte).

### §2.4 Niveles (se conserva E.3, con las correcciones §0.2-2/-5)

| Nivel | Cuándo | Render |
|---|---|---|
| **Primario** | ancla, o strength alta (≥0.66) dentro del cap | forma completa + label completa (§5) |
| **Secundario** | strength media (0.33–0.66) dentro del cap, o heredada MTF con piso (§7.1) | atenuado + label corta |
| **Terciario** | strength baja (<0.33), o fuera del cap, o familia fuera del modo | **no se dibuja** → contador T14 |

### §2.5 Orden dentro del cap top-N

Criterio de orden **candidato CONGELADO**: `score_render = strength × f(cercanía)` con `f = 1 − min(distAtr/6, 0.8)` — cercanía pondera pero no anula una zona fuerte algo lejana. `[impl]` — reusar `f_nearestN`/`f_nearestNPools` cambiando la llave de orden de "solo distancia" a este score (o añadir variante `f_strongestN`; decidir cuál rompe menos).

---

## §3 — Arquitectura de capas y z-order (fondo → frente)

| Capa | Rol | Familias (grupo real) | Forma canónica | z-order |
|---|---|---|---|---|
| **L0 Fondo temporal** | contexto de tiempo | Kill Zones, macros, RTH/ETH (`GRP_KZ`) | **ribbon** en borde superior/inferior + (opcional) bgcolor ultra-tenue SOLO en la KZ activa | 1 (atrás) |
| **L1 Marco de precio** | contexto de precio | Gradient grid + P/D + eq (`GRP_GRAD`, `GRP_PD`), OTE/StdDev (`GRP_OTE`), EMAs (`GRP_CTX` parcial) | líneas horizontales / curvas; **sin fill de área** (excepción: banda eq y golden pocket con fill ≥92 transp) | 2 |
| **L2 Zonas** | dónde reaccionar | OB/Breaker/MB/Vacuum (`GRP_OB`), FVG/IFVG/BPR/IR/VI/IPR (`GRP_FVG`), opening gaps (parte de `GRP_KZ`) | cajas con fill translúcido + borde | 3 |
| **L3 Liquidez y estructura** | qué se caza / qué se rompió | pools, EQH/EQL, sweeps, IDM, Judas, false breaks (`GRP_LIQ`, `GRP_EQHL`); swings, BOS/CHoCH/MSS, flips, CISD (`GRP_STRUCT`); displacement, rejections, legs, inside day (`GRP_CTX` resto) | líneas de nivel, tramos, marcas ▲/▼, labels de evento | 4 |
| **L4 Overlay informativo** | lectura | labels consolidadas (§6.2), panel T14 (`GRP_PANEL`) | tabla + labels | 5 (frente) |

`[impl]` — en Pine el z-order real se controla por ORDEN DE CREACIÓN + `display`/`force_overlay`; auditar el orden actual de los bloques de dibujo en `SMC-Visual.pine` (L3131+) y reordenarlos L0→L4. Documentar en comentario de sección qué capa es cada bloque.

---

## §4 — Política de curación por familia (12 fichas)

> Formato por ficha: capa · anclas · qué es P/S/T · top-N candidato (CONGELADO) · traspaso MTF · modo mínimo en que se dibuja (§8) · slots `[impl]`.
> "Panel" = cae al contador T14 (§9). Los `i_show*` existentes se conservan; esta política se aplica ENCIMA.

### F1 · Estructura (`GRP_STRUCT`) — capa L3
| Concepto | Primario | Secundario | Terciario/panel | Top-N cand. |
|---|---|---|---|---|
| BOS/CHoCH/MSS swing | el vigente (ancla §2.3) + los de strength alta | strength media, recientes | resto histórico | 4 eventos |
| BOS/CHoCH interno | nunca (solo Estudio+) | strength alta | resto | 2 |
| Swings HH/HL/LH/LL | — | los del tramo dominante vigente | resto (los rotula el panel de bias) | 6 labels |
| Flips / CISD | strength alta + fresco | strength media | resto | 2 c/u |
- **MTF:** BOS/CHoCH/MSS heredan SIEMPRE (evento de mapa); tag `(D1)`/`(H1)` obligatorio (§7.3-a). Swings NO bajan (ruido); flips/CISD bajan solo Primarios.
- **Modo mínimo:** Operación (BOS/CHoCH/MSS, flips-P) · Estudio (internos, swings, CISD-S).
- `[impl]` — el label del evento vigente lleva strength quantizado para el Eje 2 (p.ej. `"BOS ▲ ●●●"` o sufijo numérico corto; decidir glifo).

### F2 · Contexto / ICT (`GRP_CTX`) — capas L1 (EMAs) y L3 (resto)
| Concepto | Primario | Secundario | Terciario/panel | Top-N |
|---|---|---|---|---|
| EMAs 20/50/200 | — (las 3 líneas son contexto, siempre tenues si ON) | — | estado ⬆⬇ vive en panel | 3 líneas |
| Cruces/rebotes/stack | — | strength alta + fresco | resto → panel | 2 c/u |
| Displacement | el que valida el evento vigente (implícito en strength) | strength alta | resto | 2 |
| Rejections / legs / Inside Day | — | strength alta (rejection), leg vigente | resto | 2 / 1 / 1 |
- **MTF:** NO baja nada de esta familia (contexto se recalcula nativo por TF; el panel ya muestra EMA por TF).
- **Modo mínimo:** Estudio TODO (en Operación esta familia = solo panel; excepción: EMAs líneas si `i_showEMA`, sin marcas).
- `[impl]` — bajar la opacidad por defecto de las 3 EMAs (hoy compiten con las velas).

### F3 · Order Blocks (`GRP_OB`) — capa L2
| Concepto | Primario | Secundario | Terciario/panel | Top-N |
|---|---|---|---|---|
| OB | ancla por lado (§2.3) + strength alta activos | strength media o parcialmente mitigado | mitigados/lejanos | 3 por dirección |
| Breaker | strength alta + fresco | strength media | resto | 2 |
| Mitigation / Vacuum | — | strength alta | resto | 1 c/u |
- **Ciclo de vida (§5.4):** activa = fill+borde · parcial = fill al 50% del alfa · mitigada = SOLO borde punteado (y solo en Estudio+).
- **MTF:** OB/Breaker heredan si Primarios en origen (piso Secundario §7.1); Mitigation/Vacuum no bajan.
- **Modo mínimo:** Operación (OB-P, Breaker-P) · Estudio (resto).
- `[impl]` — flag `propulsion` eleva strength del OB base (ya decidido FIX P-05), y añade glifo `↑↑`/`↓↓` al label — NO caja aparte.

### F4 · Fair Value Gaps (`GRP_FVG`) — capa L2
| Concepto | Primario | Secundario | Terciario/panel | Top-N |
|---|---|---|---|---|
| FVG (+CE) | strength alta activos cerca | strength media | mitigados/micro | 3 por dirección |
| IFVG / BPR | strength alta | strength media | resto | 2 / 1 |
| IR / VI / IPR | — (micro-conceptos) | strength alta | resto → panel | 1 c/u |
- **CE (línea 50%):** SOLO en FVG Primarios (en Secundarios ensucia).
- **trueFvg/gradedFvg:** elevan strength del FVG base + sufijo de label existente (`·g`); sin tinta propia.
- **MTF:** FVG/IFVG/BPR heredan si Primarios; IR/VI/IPR nunca bajan.
- **Modo mínimo:** Operación (FVG-P, IFVG-P) · Estudio (BPR, IR) · Todo (VI, IPR).

### F5 · Premium/Discount (`GRP_PD`) — capa L1
- P/D/eq del rango dominante = **ancla** (parte del marco §2.3). Solo líneas + banda eq tenue; labels `Premium`/`Discount`/`EQ` en el margen derecho (precio en label, no línea adicional).
- **MTF:** el P/D de D1 puede mostrarse en TF menores SOLO como 3 líneas rotuladas `(D1)` — nunca dos bandas eq simultáneas (regla "un solo fondo").
- **Modo mínimo:** Operación.
- `[impl]` — unificar el dibujo P/D con el grid Gradient (§F6): P/D son los niveles 0/0.5/1 del mismo grid; hoy conviven dos bloques de dibujo → deduplicar tinta (ya salta 0/0.5/1 en el grid; verificar que no queden labels dobles).

### F6 · Gradient Levels (`GRP_GRAD`) — capa L1 (el que más solapa hoy)
| Elemento | Primario | Secundario | Terciario/panel |
|---|---|---|---|
| Quadrants LQ/EQ/UQ + P/D del grid seleccionado | ancla (líneas sólidas finas) | — | — |
| Eighths 1/8–7/8 | — | solo Estudio+ (punteadas, más tenues) | — |
| Grids P3 (gaps) | — | solo el más reciente, Estudio+ | resto → panel |
| Ghosts (grids archivados) | — | — | solo Todo, gris tenue |
- **Labels del grid:** SOLO en el margen derecho (extremo del chart), fuente mínima, sin caja de fondo. JAMÁS labels de grid en medio del chart.
- **MTF:** el grid es global-por-símbolo (rango-fuente H1/D1); en M5 se ve el MISMO grid (herencia implícita) — no se recalcula un grid M5.
- **Modo mínimo:** Operación (quadrants) · Estudio (eighths, P3) · Todo (ghosts).
- `[impl]` — es la familia que rompe el solape con KZ: verificar que ningún elemento del grid use fill de área grande (hoy la banda del grid pinta encima del sombreado KZ — quitar el fill o bajarlo a ≥95 transp).

### F7 · Equal Highs/Lows (`GRP_EQHL`) — capa L3
- Primario: el cluster EQH/EQL **no barrido más cercano por lado** (es liquidez objetivo). Secundario: strength media cerca. Panel: el resto (¡hoy hay 100 en H1! — el contador T14 ya existe).
- Top-N cand.: **2 por lado**. Tramo toque-a-toque punteado + UNA label (`EQH ·3` con nº de toques).
- **MTF:** heredan si Primarios en origen, con cuadre fino diferido (§7.3-b).
- **Modo mínimo:** Operación (Primarios) · Estudio (Secundarios).

### F8 · Liquidez (`GRP_LIQ`) — capa L3
| Concepto | Primario | Secundario | Terciario/panel | Top-N |
|---|---|---|---|---|
| Pools BSL/SSL | pool objetivo del bias (ancla) + strength alta | strength media | barridos/lejanos | 2 por lado |
| Sweeps | el último por lado si fresco | strength alta recientes | histórico | 2 |
| IDM / Judas / False Break | — | strength alta + fresco | resto | 1 c/u |
- **Pools barridos (`i_showSwept`):** solo Estudio+ (historial no es decisión).
- **MTF:** pools/sweeps heredan si Primarios; IDM/Judas/FalseBreak no bajan (micro-timing del TF propio).
- **Modo mínimo:** Operación (pools-P, sweep último) · Estudio (resto).

### F9 · Kill Zones / Sesiones (`GRP_KZ`) — capa L0 (+ opening gaps en L2)
- **Cambio de forma (la corrección grande §0.2-4):** el sombreado full-height desaparece del modo Operación. La KZ se rinde como **ribbon** (tira delgada en el borde del chart, coloreada por sesión) + estado en panel. En Estudio puede añadirse bgcolor ultra-tenue (≥92 transp) SOLO en la KZ activa. Macros intradía: ticks sobre el ribbon, solo Estudio+.
- **Opening gaps NWOG/NDOG/NYMO:** son ZONAS (capa L2, mismo tratamiento que F4; strength decide). BAG/Breakaway solo Estudio.
- **MTF:** los gaps D1 heredan como zonas si Primarios; el ribbon es del TF activo.
- **Modo mínimo:** Operación (ribbon + gaps-P) · Estudio (bgcolor activa, macros) · Todo (RTH/ETH).
- `[impl]` — el ribbon: candidatos `box.new` delgado anclado arriba (precio máximo visible) o tabla de celdas; elegir el que no tape precio (evaluar `force_overlay`/posición). Definir altura ≈ 0.5×ATR visual o px fijos.

### F10 · OTE / Golden Pocket (`GRP_OTE`) — capa L1
- Se dibuja SOLO cuando hay pierna activa alineada al bias (ya condicionado): golden pocket con fill tenue + 3 líneas fib. StdDev projections: solo Estudio+ (herramienta, no confluencia).
- **MTF:** no baja (se recalcula por TF); si el OTE D1 está activo y el precio dentro, el panel lo indica.
- **Modo mínimo:** Operación (OTE activo) · Estudio (StdDev).

### F11 · Mapa MTF (`GRP_MTF`) — transversal (usa la capa de su concepto)
- No es familia visual propia: cada objeto heredado se rinde en la capa de su familia con el estilo de procedencia (§7.2). Los caps 0–10 por concepto (ADR-010) se conservan como límite de TRANSPORTE; el nivel visual se decide aquí (§2).
- **Modo mínimo:** sigue al concepto heredado.

### F12 · Panel T14 (`GRP_PANEL`) — capa L4
- Siempre visible en los 3 modos (es el desagüe del sistema). Contrato ampliado en §9.

---

## §5 — Sistema de color y estilo

### §5.1 Las 4 dimensiones ortogonales (prioridad al chocar: familia > jerarquía > dirección > procedencia)

| Dimensión | Se expresa con | NUNCA con |
|---|---|---|
| **Familia** (qué es) | **hue** fijo (paleta §5.2) | forma |
| **Dirección** (alcista/bajista/neutro) | glifo ▲/▼/• en label + variante tonal del hue (claro=alcista / oscuro=bajista) | hue distinto |
| **Jerarquía** (P/S/T) | transparencia + grosor + longitud de label (§5.3) | hue |
| **Procedencia MTF** | grosor de borde + estilo + tag `(D1)`/`(H1)` (§7.2) | hue |

> Excepción única: **estructura (L3)** mantiene el binomio clásico teal/rojo por dirección (BOS alcista teal, bajista rojo) — es el lenguaje nativo del trader y la familia se identifica por la FORMA (línea de tramo + label de evento). Las ZONAS y el resto siguen hue-por-familia.

### §5.2 Paleta maestra (8 hues máx + 2 neutros — candidata CONGELADA)

| Hue | Familias | Candidato |
|---|---|---|
| Azul | OB / Breaker / MB / Vacuum | `#2962FF` |
| Naranja | FVG / IFVG / BPR / IR / VI / IPR / opening gaps | `#FF9800` |
| Violeta | Liquidez: pools, sweeps, IDM, Judas, EQH/EQL | `#9C27B0` |
| Teal / Rojo | Estructura alcista / bajista (BOS/CHoCH/MSS, swings, flips) | `#089981` / `#F23645` |
| Gris-azul | Marco: grid Gradient + P/D + eq | `#787B86` (quadrants) / `#5D606B` (eighths) |
| Ámbar tenue | OTE / Golden Pocket | `#D4AF37` |
| Por sesión | KZ ribbon: London / NY / Asia | `#4CAF50` / `#E91E63` / `#3F51B5` |
| Gris puro | ghosts, mitigado, neutro | `#9598A1` |

`[impl]` — centralizar la paleta en UNA sección de constantes `COL_*` al inicio de Visual (hoy los colores están dispersos por bloque). Cualquier dibujo referencia la constante — es el prerequisito para poder recalibrar en Fase 3 sin tocar 40 bloques.

### §5.3 Matriz de render por nivel (candidata CONGELADA)

| Atributo | Primario | Secundario | Terciario |
|---|---|---|---|
| Fill de zona (transp) | 82 | 92 | no se dibuja |
| Borde de zona | sólido, grosor por TF (§7.2) | punteado 1px | — |
| Línea de nivel | sólida 2px | punteada 1px | — |
| Label | texto completo + glifo + strength (`"OB ▲ (D1) ●●●"`) | abreviatura sola (`"OB"`) | — |
| Tamaño label | `size.small` | `size.tiny` | — |

### §5.4 Ciclo de vida visual (decaimiento — corrección §0.2-7)

| `state` | Render (multiplica a §5.3) |
|---|---|
| Activa | 100% del alfa de su nivel |
| Parcialmente mitigada | fill al 50% del alfa; borde igual |
| Mitigada / invalidada | pierde fill; borde punteado gris; solo visible en Estudio+ |
| Breaker (rol invertido) | cambia al hue de su nueva familia (azul) + label `BRK` — no conserva el color del OB original |

### §5.5 Tipografía y abreviaturas canónicas de labels

- Longitud máxima: **Primario ≤ 16 chars · Secundario ≤ 6 chars** (sin contar tag TF).
- Abreviaturas canónicas (una sola por concepto — tabla completa `[impl]` a partir de las existentes): `OB · BRK · MB · VAC · FVG · IFVG · BPR · IR · VI · IPR · BOS · CHoCH · MSS · FLIP · CISD · IDM · JUD · SWP · FB · EQH · EQL · BSL · SSL · NWOG · NDOG · NYMO · BAG · OTE · ID`.
- Glifos de dirección: `▲`/`▼`/`•`. Glifo de strength (solo Primarios): `●●●`/`●●○`/`●○○` — es la lectura del Eje 2 vía `data_get_pine_labels`.
- `[impl]` — precio en el label SOLO para anclas de liquidez (pool objetivo, EQ); el resto no repite el precio (el eje ya lo da).

---

## §6 — Antisolape (las 5 reglas)

### §6.1 Alternancia de lado (se conserva de E.4)
Labels de nivel alternan `style_label_left`/`style_label_right` según el lado del precio y paridad del índice del nivel. `[impl]` — extender el patrón ya usado en MTF a todas las familias L1/L3.

### §6.2 Consolidación de etiquetas (la regla NUEVA principal)
- **Cluster:** labels cuyo precio-ancla cae dentro de `labelClusterTol×ATR` (cand. **0.25**) entre sí forman un cluster.
- **Fusión:** cada cluster rinde UNA label combinada: conceptos ordenados por capa (L2→L3), separados por `·`, tag TF del mayor: `"OB·FVG·BPR (D1) ▲"`. El precio-ancla de la fusión = el del concepto de mayor strength.
- **Tope por franja:** máx **2 labels** por franja de `0.25×ATR` (la métrica del checklist §10). Si tras fusionar quedan >2, las de menor strength pierden el label (la forma queda).
- `[impl]` — implementar como pasada de post-proceso en Visual sobre un array de "labels pendientes" antes de crearlas (recolectar → clusterizar → emitir). Es la pieza de más trabajo del esqueleto; hacerla genérica (todas las familias la usan).

### §6.3 "Un solo fondo de área" (resuelve Grid vs KZ)
- El **eje de precio** lo posee L1: grid + P/D como LÍNEAS (fill solo banda eq y golden pocket, transp ≥92).
- El **eje de tiempo** lo posee L0: KZ como RIBBON (§F9); bgcolor de área solo en Estudio+ y solo la KZ activa.
- Prohibido: dos fills de área grande de familias distintas visibles a la vez en modo Operación. El checklist lo mide (§10-4).

### §6.4 Z-order por capas
Orden de creación de objetos = L0 → L1 → L2 → L3 → L4 (§3). Dentro de una capa: Secundarios antes que Primarios (los fuertes quedan encima).

### §6.5 Presupuesto GLOBAL de tinta (corrección §0.2-6 — candidato CONGELADO)

| Modo | Objetos totales máx (líneas+cajas+marcas) | Labels máx |
|---|---|---|
| Operación | **60** | **25** |
| Estudio | 150 | 60 |
| Todo | 400 | 150 |

Desalojo determinista si se excede: Terciarios ya no dibujan; luego Secundarios de menor `score_render` (§2.5), familia por familia en orden inverso de capa (L3 primero, L0 último). Las anclas jamás se desalojan. `[impl]` — contador global de objetos emitidos por barra de render; cortar al llegar al tope e incrementar contadores T14.

---

## §7 — Traspasos MTF (D1 → H1 → M5) — el contrato completo

> **Regla madre (pedido explícito del usuario):** *lo importante que sucede en D1 SE VE en H1 y M5; lo importante que sucede en H1 SE VE en M5.* La cadena es descendente y transitiva. El TF activo puede tener su chart limpio, pero NUNCA a costa de silenciar un Primario de un TF mayor.

### §7.1 Regla de herencia descendente obligatoria

1. **Qué baja:** toda marca **Primaria en su TF origen** (ancla o strength alta dentro de cap) de una familia heredable (tabla §7.4). Los caps de transporte 0–10 (ADR-010) se ordenan por `score_render` — bajan las N más fuertes, no las N más cercanas a secas.
2. **Piso de nivel:** una heredada que era Primaria en origen entra al TF destino con **piso Secundario** — puede subir a Primaria (si además es ancla local) pero NUNCA caer a Terciaria mientras su origen la tenga Primaria y esté dentro del cap de transporte.
3. **Qué NO baja:** Secundarios y Terciarios del TF origen (el TF menor ya tiene su propio ruido); familias no-heredables (§7.4).
4. **Transitividad:** en M5 se ven los Primarios de D1 **y** los de H1. Si el mismo objeto existe en ambos (el OB D1 contiene al H1), se fusionan (§7.3-a) y gana el tag del TF MAYOR.
5. **Anti-repaint:** la herencia usa los buffers aplanados ADR-010 con `lookahead_off`; el nivel heredado se fija al cierre de la vela del TF origen.

### §7.2 Estilo de procedencia (cómo se VE de qué TF viene)

| Origen | Grosor borde/línea | Estilo | Tag |
|---|---|---|---|
| D1 heredado | 3px | sólido | `(D1)` obligatorio |
| H1 heredado (en M5) | 2px | sólido | `(H1)` obligatorio |
| Nativo del TF activo | 1px | según nivel §5.3 | sin tag |
| Fusionado nativo+heredado | el del TF mayor | sólido | combinado `(D1·H1)` / `(H1·M5)` |

El **hue no cambia** con la procedencia (principio §1-6). `[impl]` — pasar el `tf` de origen (ya viaja en los buffers/`SMC_Event.tf`) al bloque de dibujo y mapear a grosor+tag.

### §7.3 Los 3 pendientes diferidos ENTRAN a este esqueleto (dejan de diferirse)

- **(a) Tag TF en BOS/CHoCH fusionados** — resuelto por §7.2 (rótulo combinado). Arreglo puntual ya especificado en HANDOFF §6.3-a; se implementa junto con esta capa.
- **(b) Cuadre fino EQH/EQL HTF↔LTF** — anclar al `pool.level` HTF literal + `xloc.bar_time`; tolerancia de fusión `poolTol×ATR` del LTF (HANDOFF §6.3-b).
- **(c) Exactitud vela-a-vela OB/FVG heredados** — anclar al `SMC_Zone.barTime` exacto; FVG a la vela media real (HANDOFF §6.3-c).
- `[impl]` — un commit por pendiente, con su criterio de verificación del HANDOFF.

### §7.4 Tabla de heredabilidad por familia (resumen normativo de las fichas §4)

| Familia | ¿Baja D1→H1→M5? | Qué baja | Nota |
|---|---|---|---|
| Estructura BOS/CHoCH/MSS | ✅ SÍ | todos los Primarios | tag obligatorio; fusión §7.3-a |
| Swings / internos | ❌ | — | ruido en LTF |
| OB / Breaker | ✅ SÍ | Primarios | exactitud §7.3-c |
| MB / Vacuum | ❌ | — | micro del TF propio |
| FVG / IFVG / BPR | ✅ SÍ | Primarios | exactitud §7.3-c |
| IR / VI / IPR | ❌ | — | micro |
| P/D + Gradient grid | ✅ implícito | el grid/P/D dominante ES global | §F5/§F6; solo líneas, un solo fondo |
| EQH/EQL | ✅ SÍ | Primarios | cuadre §7.3-b |
| Pools / Sweeps | ✅ SÍ | pool objetivo + Primarios | ya funciona (ADR-010) |
| IDM / Judas / False Break | ❌ | — | timing del TF propio |
| Kill Zones / macros | ❌ (ribbon local) | gaps de apertura SÍ (zonas) | §F9 |
| OTE / StdDev | ❌ | — | panel indica OTE D1 activo |
| EMAs / contexto | ❌ | — | panel ya da EMA por TF |

### §7.5 Verificación del eje MTF (amarra con METODOLOGIA §4)
Prueba de visibilidad cruzada por familia heredable: marcar el objeto Primario en D1 → confirmar presencia en H1 y M5 en el mismo `bar_time`+nivel con tag correcto → confirmar que un Primario H1 aparece en M5. Criterio: **100% de los Primarios de TF mayor visibles en los TF menores** dentro del rango visible (checklist §10-6).

---

## §8 — Modos de densidad (matriz curada)

### §8.1 El input (se conserva E.4)
`i_densidad = input.string("Operación", options=["Operación","Estudio","Todo"])` — filtro transversal ADICIONAL a los `i_show*`. `[impl]` — grupo propio `GRP_DENS` primero en la lista de inputs (es el control maestro del usuario).

### §8.2 Matriz modo × familia (la curación — corrección §0.2-8)

| Familia | Operación | Estudio | Todo |
|---|---|---|---|
| F1 Estructura | P (BOS/CHoCH/MSS, flips-P) | +S +internos +CISD | +T |
| F2 Contexto | solo EMAs líneas + panel | +S (cruces, rejections, legs, ID) | +T |
| F3 OB | P | +S +mitigadas (borde) | +T |
| F4 FVG | P (FVG/IFVG) | +S +BPR +IR | +T (VI, IPR) |
| F5 P/D | ancla | igual | igual |
| F6 Gradient | quadrants | +eighths +P3 | +ghosts |
| F7 EQH/EQL | P | +S | +T |
| F8 Liquidez | pool objetivo + sweep último | +S +barridos | +T |
| F9 KZ | ribbon + gaps-P | +bgcolor activa +macros | +RTH/ETH |
| F10 OTE | OTE activo | +StdDev | igual |
| F11 MTF | Primarios heredados (siempre) | igual | igual |
| F12 Panel | ON | ON | ON |

> **Los heredados MTF se ven en los 3 modos** — la regla madre §7 no se negocia ni en Operación (son precisamente "lo que importa").

`[impl]` — cablear como `and f_visualLevel(...) >= umbralModo` + whitelist de familia por modo (mapa constante, no 40 ifs sueltos).

---

## §9 — Contrato con el panel T14 (el desagüe)

1. **Fila nueva "Ocultos"** (o columna compacta): contador por familia de marcas Terciarias/desalojadas: `OB 4 · FVG 7 · EQ 96 · Liq 12` — el usuario sabe cuánto hay detrás del chart limpio. `[impl]` — decidir si fila única concatenada o sección plegable del panel (limitación `table`: fila única concatenada probablemente).
2. **Strength en las filas existentes:** las filas "OB cercano / FVG cercano / Pool cercano" añaden el glifo de strength (`●●○`) del objeto que muestran — misma lectura que el label (Eje 2 verificable por `data_get_pine_tables`).
3. **Modo activo visible:** celda con `i_densidad` actual (`Op/Est/Todo`) — las capturas de validación siempre declaran su modo.
4. Todo lo demás del panel T14 se conserva tal cual (columnas D1 | H1 | TF activo — ya cumple el rol MTF).

---

## §10 — Checklist de verificación visual (criterios medibles del "quedó bien")

> Se mide con `draw_list`/`data_get_pine_labels`/`data_get_pine_lines`/`data_get_pine_boxes` + `capture_screenshot` + `data_get_pine_tables`, en OANDA:EURUSD, D1/H1/M5, modo declarado. Umbral global: TODOS los ítems PASS → Eje 2 cerrado (con METODOLOGIA §8).

| # | Criterio | Métrica PASS |
|---|---|---|
| 1 | Presupuesto global | modo Operación: ≤60 objetos + ≤25 labels visibles (hoy: 502+502) |
| 2 | Franja de precio | ≤2 labels por franja de 0.25×ATR en todo el rango visible |
| 3 | Consolidación | 0 clusters de ≥3 labels sin fusionar al mismo nivel (±0.25×ATR) |
| 4 | Un solo fondo | 0 pares de fills de área grande solapados en Operación (grid vs KZ resuelto) |
| 5 | Jerarquía legible | en 3 capturas (D1/H1/M5), los 3 objetos de mayor strength son los 3 más salientes (juicio validador + orden por `data_get_pine_labels`) |
| 6 | Herencia MTF | 100% de Primarios D1 visibles en H1 y M5; 100% de Primarios H1 visibles en M5; mismo `bar_time`+nivel |
| 7 | Procedencia | 100% de objetos heredados con tag `(D1)`/`(H1)`; fusionados con tag combinado |
| 8 | Panel-desagüe | suma(dibujados + contados en panel) = total detectado por familia (nada desaparece en silencio) |
| 9 | Ciclo de vida | 0 zonas mitigadas con fill en Operación/Estudio |
| 10 | Anti-repaint | niveles/labels idénticos tras recarga y en replay 2 días (marca creada solo en `isconfirmed`) |
| 11 | Performance | carga 20k barras sin timeout; sin `max_labels/lines/boxes` excedidos |
| 12 | Strength coherente (Eje 2) | por concepto: en ≥3 casos, el orden del glifo `●` coincide con el orden perceptual (METODOLOGIA §3 Eje 2) |

---

## §11 — Restricciones + orden de implementación

### §11.1 Cumplimiento de las restricciones duras (Parte D del dossier)

| Restricción | Cómo la cumple este esqueleto |
|---|---|
| D-1 anti-repaint | strength al cierre (E.1 conservado); herencia con `lookahead_off`; §10-10 lo verifica |
| D-2 core byte-idéntico | SOLO §E.1/E.2 (strength) tocan CORE → `check-core-sync` + SHA; TODO §2–§9 vive en Visual |
| D-3 funciones puras | `f_zoneStrength`/`f_eventStrength`/`f_strengthLevel` puras; `f_visualLevel` v2 en Visual |
| D-4 símbolo-agnóstico | toda tolerancia en ×ATR (`labelClusterTol`, franjas, `score_render`); 0 pips fijos |
| D-5 no inflar confluencias | trueFvg/propulsion/gradedFvg = strength del base + sufijo (fichas F3/F4) |
| D-6 congelados Fase 3 | TODOS los números aquí marcados candidatos (pesos E.1, umbrales 0.33/0.66, transparencias, presupuestos, top-N, paleta) |
| D-7 compila 0/0 | orden de commits §11.2, uno por pieza verificada |
| D-8 reutilizar | `f_nearestN`/`f_nearestNPools`, `state`/`mitigatedPct`/flags, `f_detectDisplacement`, panel T14, `i_show*`, ADR-012, buffers ADR-010 |
| D-9 pendientes MTF | integrados y resueltos en §7.3 (dejan de ser diferidos) |

### §11.2 Orden de implementación (para Opus — un commit por paso, ciclo completo del proyecto)

| Paso | Pieza | Toca | Gate | Estado |
|---|---|---|---|---|
| ✅ 1 | Campos `strength` en UDTs (E.1/HANDOFF §5.1) | CORE | 0/0 ×3 + core-sync + SHA | S083 `0b1ffba` |
| ✅ 2 | `f_zoneStrength`/`f_eventStrength`/`f_strengthLevel` + cálculo en sitios de creación | CORE | ídem | S084 `0f1a485` |
| ✅ 3 | Constantes `COL_*` centralizadas (§5.2) + matriz de render §5.3/§5.4 aplicada por familia | Visual | 0/0 Visual | S084 `042e1e2` |
| ✅ 4 | `i_densidad` + `f_visualLevel` v2 (anclas §2.3 + pisos MTF) + matriz §8.2 | Visual | 0/0 | S085 `c2410ca` |
| ✅ 5 | Reordenar bloques de dibujo a capas L0→L4 (§3) + KZ→ribbon + grid sin fill (§6.3) | Visual | 0/0 + checklist #4 | S087 `9be569a`,`6cc4a84` |
| 🔶 6 | Consolidación de labels (§6.2) + alternancia + presupuesto global (§6.5) | Visual | 0/0 + checklist #1–3 | S088 §8.2✅+top-N✅ (`469f197`/`1959583`/`3ce3c84`); §6.2 consolidación pendiente |
| ⬜ 7 | Estilo de procedencia MTF (§7.2) + pisos de herencia (§7.1) + 3 pendientes (§7.3, un commit c/u) | Visual | 0/0 + checklist #6–7 | S089 PENDIENTE (12 MTF heredados = excedente budget) |
| ✅ 8 | Panel T14: fila Ocultos + glifos strength + modo (§9) | Visual | 0/0 + checklist #8 | S088 Ocultos+modo✅ (`2507ec7`); glifos strength §9-2 ✅ (`f_strGlyph` en OB/FVG/Pool cercano col M5) |
| 🔶 9 | Pasada de verificación completa §10 + Eje 2 (METODOLOGIA §3/§7) por concepto | — | ≥90 + firma usuario → **cierra el gate visual F1** | §10 #1-#12 ✅ (S089-S092): #9 impl+aplicado (`bc7839b`), #10 auditoría (replay=paywall), #12 panel; BSL·3 D1 diferido F3. **Falta: firma usuario** (opción validador Eje 2 ≥90 antes) |

### §11.3 Congelados explícitos (recordatorio ADR-002)
Pesos E.1 · umbrales 0.33/0.66 · `labelClusterTol=0.25` · franja 0.25×ATR · presupuestos 60/25–150/60–400/150 · top-N por familia (§4) · transparencias 82/92 · grosores 1/2/3px · paleta §5.2 · `score_render` f(cercanía). Se calibran en Fase 3 (IS/OOS); aquí solo estructura + defaults razonables.

---

*Fin del esqueleto. Siguiente paso (NO en este documento): Opus rellena los `[impl]` siguiendo §11.2, bajo los gates del proyecto. La verificación final es §10 + METODOLOGIA-VERIFICACION-VISUAL §8 (F1-GATE ampliado, Eje 2).*
