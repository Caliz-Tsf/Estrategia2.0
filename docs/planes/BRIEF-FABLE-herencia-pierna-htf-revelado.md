# BRIEF-FABLE — Herencia de la pierna COMPLETA del HTF al LTF + revelado progresivo al romper

> Estrategia 2.0 · Fase 1 (Pine Visual) · S108 (2026-07-08) · autor: Claude Code (Opus 4.8)
> Para: **Fable** (revisión de diseño). Objetivo: que el LTF (H1/M5) herede las zonas/estructura
> IMPORTANTES del HTF (D1→H1→M5) **más allá del Premium/Discount vigente del HTF**, en **AMBAS
> direcciones**, y las **revele progresivamente cuando el precio rompe la frontera del rango del HTF**.
> Antecedentes obligatorios: [BRIEF-FABLE-retencion-zonas-pierna.md](BRIEF-FABLE-retencion-zonas-pierna.md)
> · [RESPUESTA-FABLE-retencion-zonas.md](RESPUESTA-FABLE-retencion-zonas.md) · ADR-016 · CLAUDE.md (reglas duras).

## 0. Petición explícita a Fable
1. **Analiza la viabilidad** de la idea (sección 1), en especial el **riesgo OOM** del transporte MTF
   (sección 4) — es la restricción que ya nos mató dos sesiones (S104/S105).
2. Si es viable, **genera un ESQUELETO** (pasos A–F, estilo tus entregas previas) **respetando la línea
   del WORKPLAN** y las reglas duras. Debe distinguir claramente qué es **Visual-only** vs qué toca el
   **LIBRARY CORE byte-idéntico** (rompe SHA → Strategy + ADR).
3. Si algo del plan debe cambiar, **dilo y proponlo** — lo ajustamos, pero **seguimos la línea del plan**
   (no re-litigar arquitectura: 1 core + Visual + Strategy; anti-repaint; ATR-relativo; símbolo-agnóstico).
4. **Empieza el esqueleto por un de-riesgo de OOM** (probe incremental) ANTES de la feature completa.

## 1. La idea del usuario (visión validada, S108)
El sistema debe dar **contexto de proyección de swing** completo: el LTF necesita "ver" hacia dónde
puede ir el precio si rompe el rango del HTF, en **ambos sentidos**.

- **Estado normal:** H1 muestra el contexto hasta el **Premium/Discount de D1** (fronteras del rango D1).
  Esto YA existe (líneas `D1: Premium 1.20831` / `D1: Discount 1.13246` heredadas a H1).
- **Al romper la frontera:** si el precio **rompe el Premium D1** (o el Discount D1), se **activan/revelan
  en H1 las zonas que están MÁS ALLÁ de esa frontera** (las que en el chart D1 sí se ven), hasta el
  siguiente pivote importante (p. ej. un BSL histórico tipo "BSL-3" que precede al verdadero inicio del
  swing real de D1). Revelado progresivo = chart limpio dentro del rango, contexto cuando se vuelve relevante.
- **Todos los conceptos + estructura importantes:** no solo OB/FVG/MB, también **EQH/EQL, pools SSL/BSL,
  BOS/CHoCH**. Ejemplo clave del usuario: *"si allá arriba hay un EQH que hizo que se desplace el precio
  hasta aquí, necesitamos saberlo"* — ese EQH es el **draw-on-liquidity / objetivo** del próximo swing.
- **Ambas direcciones, simétrico:** arriba del Premium D1 **y** abajo del Discount D1. "Información
  complementaria importante por si vuelve a romper los máximos o mínimos de cada temporalidad."
- **Cascada:** D1→H1 y también D1/H1→M5 (herencia de dos capas ya existente).

Justificación SMC/ICT (correcta): sin el imán de liquidez del HTF más allá del rango vigente no se puede
proyectar el objetivo del siguiente swing ni distinguir continuación de reversión. Encaja con §7 (capa de
proyección) y con el requisito firme "objetivos de liquidez en ambas direcciones" (S102 punto #6).

## 2. Estado a hoy (S108, en vivo EURUSD, indicador `SMC Engine — Visual`)
- **Fix bar_time (S108) ya validado y commiteado:** las cajas nativas se anclan por `xloc.bar_time` desde
  `z.barTime` (vela de origen real). En **D1** esto deja ver zonas históricas altas (MB ~1.36/1.34,
  T.FVG-g ~1.30, MB ~1.26, T.FVG ~1.20) y bajas, cada una en su vela real. **BSL-3 ~1.50** aparece como
  pool histórico en D1.
- **En H1**, el precio (~1.1417) está en **Discount profundo** de D1 (rango D1 [1.13246, 1.20831]).
- **Herencia actual D1→H1:** H1 recibe `D1: Premium 1.20831`, `D1: Discount 1.13246`, y las zonas D1
  **cercanas al precio** (D1: OB [1.15726,1.16221], D1: FVG [1.15283,1.15748], D1: BSL, D1: SSL, etc.).
  **NO** recibe las zonas D1 altas (1.20–1.50): quedan solo en el chart D1.

## 3. Diagnóstico técnico — por qué H1 NO ve la pierna alta de D1
El transporte MTF emite, por concepto, **solo los K objetos MÁS CERCANOS AL PRECIO** del HTF, no los
extremos lejanos.

- **Contrato del transporte** (`pine/SMC-Visual.pine` L2761–2764, y `f_computeTFState` L1686, **CORE**):
  tuple plano por HTF = **17 escalares + 12 slots × 6 campos** `{kind,top,bottom,dir,tA,tB}` (89 campos),
  vía `request.security(sym, "D"|"60", f_computeTFState(...), lookahead_off)`. Dos HTF (D1, H1) = 2 calls.
- **Selección = nearest-N a `close` del HTF** (`f_nearestN` L1566 / `f_nearestNPools` L1594 /
  `f_nearestNEvents` L1637, **todas en el CORE byte-idéntico**), con caps por concepto (inputs
  `i_mtfCapOB/FVG/Pool/Sweep/EQ/BOS/CHoCH`) que llenan los 12 slots compartidos.
- **Consecuencia:** las zonas D1 a 1.20–1.50 no están entre las más cercanas al precio (1.14) → **nunca
  viajan** en el tuple → H1 no puede dibujarlas (Visual no tiene esos datos; solo dibuja lo transportado
  vía `f_drawMTFZones` L4261+).

### 3.1 Las dos piezas de la solución (costes MUY distintos)
- **Revelado-al-romper = Visual-only, barato.** H1 puede calcular `close > d1State.pdHigh` (o `<
  d1State.pdLow`) y usar eso como gate para dibujar las zonas lejanas. Máquina de estados de frontera
  (DORMANT más allá del borde → ACTIVE al romper). NO toca CORE.
- **Los DATOS lejanos = cambio en el LIBRARY CORE.** Para que el tuple lleve los extremos importantes de
  cada concepto (OB/FVG/MB/Breaker/EQH/EQL/pools/BOS/CHoCH) hay que cambiar la SELECCIÓN en `f_nearestN`
  y familia (nearest-N → nearest-N **+ farthest-important-por-lado**), y probablemente **agrandar el
  buffer de 12 slots**. Eso rompe CORE-INTACTO (SHA `5510361166844bd5`), obliga a sincronizar
  `SMC-Strategy.pine` + ADR, y **crece el tuple de `request.security`**.

## 4. Restricción crítica: OOM (leer con cuidado)
- **Historia:** S104/S105 murieron porque correr la geometría M5 completa vía `request.security` +
  `calc_bars_count` revienta el límite server-side de TV a cualquier ventana. El transporte de **tuple
  fijo** (89 campos) NO fue la causa del OOM — es el camino que hoy funciona.
- **Pero** agrandar el tuple (más slots por concepto, y ahora "extremo por lado" para varios conceptos)
  casi **duplica** los campos transportados por 2 security calls. No sabemos el headroom. **Hay que
  medirlo empíricamente ANTES de diseñar la feature completa** (probe incremental: +1/+2 slots, aplicar
  al chart, esperar 18–25s, `pine_get_errors`; recordar CE10117 = límite de tokens solo se valida en
  apply, no en `pine_check` server-side).
- **Acotar "qué tan arriba":** BSL-3 ~1.50 es muy histórico. El selector de extremos debe filtrar por
  **importancia** (strength/estructural dentro del swing DOMINANTE del propio HTF), no cada zona histórica,
  o el transporte y el clutter explotan. Sugerencia: 1 extremo "fuerte" por concepto por lado, además del
  nearest.

## 5. Reglas duras a respetar (no negociables)
1. **Anti-repaint:** eventos en `barstate.isconfirmed`; `request.security(..., lookahead_off)` SIEMPRE.
2. **CORE byte-idéntico:** si tocas `f_nearestN`/`f_computeTFState`/UDT, va a Visual **y** Strategy;
   `scripts/check-core-sync.ps1` debe pasar; nuevo SHA; **ADR obligatorio**.
3. **RE10045-safe:** nada de `array.push` que crezca sin cota en funciones que corren en `islast` de un
   script grande. Slots FIJOS (como el band-pick top-2 actual, arrays de tamaño fijo).
4. **Presupuesto de tinta:** Operación ≤25 labels / ≤60 objetos; Estudio ≤60; el revelado-al-romper
   ayuda (solo dibuja fuera de rango cuando rompe) pero debe respetar §6.5 (desalojo determinista).
5. **ATR-relativo**, **símbolo-agnóstico** (nada hardcodeado a EURUSD; caps/tolerancias por input/perfil).
6. **Un commit = un concepto verificado; compila 0/0.**

## 6. Datos técnicos de referencia (para el esqueleto)
- Transporte: `f_computeTFState` L1686 (CORE); call-sites D1/H1 L2761–2762 (Visual, caps por input).
  `MTF_K = 12` slots compartidos; caps `i_mtfCap*`.
- Selección nearest: `f_nearestN` L1566, `f_nearestNPools` L1594, `f_nearestNEvents` L1637 (CORE).
- Dibujo heredado: `f_drawMTFZones` L4261+ (Visual); ya ancla por `xloc.bar_time` (tA/tB).
- Fronteras heredadas: `d1State.pdHigh/pdLow`, `h1State.pdHigh/pdLow` (escalares, ya transportados).
- Pierna/bandas: `f_depthBand` (§7), extremo de pierna Paso A (input `i_kLeg` default 3.0), retención
  `MAX_ZONES_CHART = 120` + `f_pushZoneV` (ADR-016; en vivo "Desalojo 3" → cap NO saturado).
- Nota S102 punto #5: la herencia D1→H1→M5 está garantizada a nivel de escalares TFState (L2570).
- **Parte A complementaria (Visual-only, decidida en S108, aún no implementada):** dejar entrar las
  zonas **mitigadas** al band-pick (hoy excluidas en L3126 `z.state != ZS_MITIGATED`) para que la pierna
  alta del **propio TF** (y de D1 nativo) se pueble con "contexto de origen" en gris degradado (§5.4).
  Es independiente de este brief pero relacionada (misma visión "pierna poblada").

## 7. Pregunta abierta para Fable
¿El "extremo importante por concepto por lado" debe transportarse como **slots extra fijos** en el mismo
tuple (más simple, más OOM), o conviene una **segunda `request.security` por HTF** dedicada a extremos
(la nota L1674 menciona una "2a llamada/TF preparada, no activada")? Recomienda la opción con mejor
relación headroom-OOM / simplicidad, y cómo medir el headroom antes de comprometer el diseño.
