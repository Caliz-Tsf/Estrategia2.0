# PINE-PLAN — Plan técnico de implementación Pine Script v6
> Anexo 5 del WORKPLAN-MAESTRO-V2.md | Estrategia 2.0 | 2026-06-10
> Cubre el Paso 5 del PROMPT-FABLE: arquitectura, orden de implementación, comunicación entre módulos, panel, alertas, testing y performance.

---

## 1. ARQUITECTURA: 1 LIBRERÍA + 2 CONSUMIDORES

`[FIX: #1 demolición]` La arquitectura original de "dos indicadores comunicados por arrays + request.security()" es técnicamente imposible: `request.security()` no puede leer arrays de otro indicador, y `input.source()` solo transfiere series float (máx. 10 fuentes externas). La arquitectura correcta:

```
pine/
├── SMC-Library.pine      ← LIBRERÍA v6: toda la detección SMC/ICT (funciones puras + UDTs)
├── SMC-Visual.pine       ← INDICATOR: importa librería, dibuja todo, panel de estado, alertas
├── SMC-Strategy.pine     ← STRATEGY: importa librería, scoring direccional, strategy.entry/exit
└── reference/
    └── LuxAlgo-SMC-base.pine  ← indicador LuxAlgo v5 original (solo referencia, NO se edita)
```

**Por qué esta separación:**
- La librería es el "cerebro" único: una sola implementación de cada concepto → cero divergencia entre lo que se ve (Visual) y lo que se opera (Strategy).
- `SMC-Strategy.pine` como `strategy()` da **Strategy Tester gratis**: win rate, profit factor, drawdown, lista de trades exportable — elimina el 90% del backtesting manual.
- La librería es la **spec exacta** para la traducción a MQL5: cada función exportada mapea 1:1 a una función de un módulo `.mqh`.
- El peso computacional se reparte: Visual carga el dibujo (se puede apagar por secciones), Strategy carga el scoring (sin dibujo pesado).

**Limitaciones de las libraries Pine (restricciones de diseño obligatorias):**
1. Una library NO puede dibujar (label/line/box/table) → todo dibujo vive en SMC-Visual.
2. Una library NO puede llamar `request.security()` → los datos MTF se obtienen en el consumidor y se pasan como **parámetros** a las funciones de la librería.
3. Las funciones exportadas no pueden depender de variables globales mutables del consumidor → cada función recibe todo su estado como parámetros (arrays de UDTs pasados por referencia están permitidos).
4. Publicación: la librería debe publicarse en TradingView (privada/invite-only es válido) para poder importarla. Alternativa durante desarrollo: mantener las funciones en una sección `// === LIBRARY CORE ===` copiada idéntica en ambos consumidores, y migrar a library formal al estabilizar (ver §8, decisión D-PINE-01).

---

## 2. TIPOS DE DATOS (UDTs exportados por la librería)

```pinescript
//@version=6
// library("SMC_Library", overlay = true)

// Zona con extensión espacial (OB, FVG, Breaker, Rejection, OTE, Premium/Discount...)
export type SMC_Zone
    float  top          // borde superior
    float  bottom       // borde inferior
    int    dir          // +1 alcista / -1 bajista
    int    barIdx       // bar_index de creación
    int    barTime      // time de creación (ms)
    int    state        // 0=activa, 1=parcialmente mitigada, 2=mitigada, 3=invalidada
    float  mitigatedPct // 0.0–1.0 cuánto se ha rellenado
    string tf           // "D" | "60" | "5"
    int    kind         // enum interno: KIND_OB, KIND_FVG, KIND_BREAKER, KIND_REJECTION, KIND_MITIGATION, KIND_OTE, KIND_GP

// Evento puntual (BOS, CHoCH, MSS, Sweep, Judas, Displacement, IDM, EMA cross/bounce...)
export type SMC_Event
    float  price        // nivel del evento
    int    dir          // +1 / -1
    int    barIdx
    int    barTime
    string tf
    int    kind         // KIND_BOS, KIND_CHOCH, KIND_MSS, KIND_SWEEP, KIND_GRAB, KIND_JUDAS,
                        // KIND_DISPLACEMENT, KIND_IDM, KIND_EMACROSS, KIND_EMABOUNCE, KIND_FLIP...

// Punto de swing estructural
export type SMC_Swing
    float  price
    int    barIdx
    int    barTime
    int    kind         // KIND_HH, KIND_HL, KIND_LH, KIND_LL
    bool   swept        // si su liquidez ya fue barrida

// Pool de liquidez (EQH/EQL clusterizados)
export type SMC_Pool
    float  level
    int    dir          // +1 = BSL (sobre highs) / -1 = SSL (bajo lows)
    int    touches      // número de toques que lo confirman
    int    barTime
    bool   swept
    string tf

// Snapshot de estado por timeframe (lo que devuelve cada request.security)
export type SMC_TFState
    int    bias                  // +1 / -1 / 0
    float  lastBOSPrice
    int    lastBOSDir
    int    lastBOSTime
    float  lastCHoCHPrice
    int    lastCHoCHDir
    int    lastCHoCHTime
    float  pdHigh                // rango Premium/Discount: high del rango
    float  pdLow
    float  ema20
    float  ema50
    float  ema200
    // ... (campos planos: request.security solo transporta tipos simples y tuples;
    //      los UDT NO cruzan contextos de security → ver §4)
```

**Regla crítica de naming:** todo array global usa prefijo `SMC_` (`SMC_activeOBs`, `SMC_pools`, ...). Todos los arrays se crean con tamaño controlado manualmente: tras cada push, `if array.size(a) > MAX_X` → `array.shift(a)`. Límites por defecto: zonas 50/TF, eventos 100/TF, swings 100/TF.

---

## 3. CATÁLOGO DE FUNCIONES DE LA LIBRERÍA

Cada función es pura respecto a su entrada (recibe series/arrays, devuelve detecciones). Firma → módulo MQL5 destino (Fase 4).

### 3.1 Estructura (→ SMC_Structures.mqh)
| Función | Firma (resumida) | Detecta |
|---|---|---|
| `f_detectSwings` | `(len) → SMC_Swing` nuevo o na | Swing H/L con `len` barras de confirmación a cada lado (default 5 swing / 3 interno) |
| `f_classifySwing` | `(swing, prevSwings[]) → kind` | HH/HL/LH/LL según swing previo del mismo tipo |
| `f_detectBOS` | `(close, swings[], bias) → SMC_Event` | Cierre más allá del último swing en dirección del bias |
| `f_detectCHoCH` | `(close, swings[], bias) → SMC_Event` | Cierre más allá del último swing CONTRA el bias |
| `f_detectMSS` | `(swings[]) → SMC_Event` | Secuencia HH+HL → LH+LL confirmada (o inversa) — requiere CHoCH + nuevo swing confirmado |
| `f_detectDisplacement` | `(atr, factor) → SMC_Event` | Vela con rango ≥ `factor`×ATR14 (default 1.5) y cuerpo ≥70% del rango, tras ≥3 velas de rango < ATR |
| `f_isImpulsive` | `(events[]) → bool` | ≥2 BOS consecutivos misma dirección sin CHoCH intermedio |

### 3.2 Zonas (→ SMC_Structures.mqh)
| Función | Detecta |
|---|---|
| `f_detectOB` | Última vela contraria antes del impulso que genera BOS/CHoCH (algoritmo LuxAlgo: vela de origen filtrada por ATR o rango medio acumulado). Crea `SMC_Zone` KIND_OB |
| `f_detectFVG` | Gap entre high[2] y low[0] (alcista) o low[2] y high[0] (bajista), tamaño ≥ % ATR configurable (default 25% ATR14). Incluye nivel CE (50%) |
| `f_updateZoneMitigation` | Para cada zona activa: si precio penetra → actualizar `mitigatedPct` y `state`. Mitigación por `close` o `high/low` (configurable, igual que LuxAlgo) |
| `f_detectBreaker` | OB con `state`=invalidada (precio cerró a través) → re-crear como KIND_BREAKER con `dir` invertido |
| `f_detectRejection` | Vela con wick ≥ 2× cuerpo tocando zona/nivel clave → KIND_REJECTION |
| `f_detectFlip` | Nivel roto con cierre limpio y luego retesteado desde el otro lado → KIND_FLIP |
| `f_detectOTE` | Tras impulso confirmado (BOS), zona fib 61.8–79% del swing → KIND_OTE; 50–61.8% → KIND_GP |

### 3.3 Liquidez (→ SMC_Liquidity.mqh — `[NUEVO]` módulo 6, ver MQL5-PLAN)
| Función | Detecta |
|---|---|
| `f_detectEQHL` | Equal highs/lows: 2+ swings con diferencia < threshold×ATR (algoritmo LuxAlgo) |
| `f_buildPools` | Clusteriza EQH/EQL + swings no barridos en `SMC_Pool` (nivel = promedio, touches = #confirmaciones) |
| `f_detectSweep` | Precio supera pool intra-vela pero CIERRA de vuelta dentro del rango → sweep ejecutado, `pool.swept := true` |
| `f_detectGrab` | Wick toca el nivel sin cierre más allá (subset de sweep, sin requerir pool) |
| `f_detectJudas` | Sweep en la primera mitad de una Kill Zone seguido de displacement contrario en ≤ N velas (default 6 en M5) |
| `f_detectIDM` | Pullback menor (liquidez interna) barrido ANTES de que el precio alcance el OB/FVG objetivo |
| `f_detectFalseBreakout` | Cierre más allá del nivel + reversión con cierre de vuelta en ≤2 velas |

### 3.4 Contexto (→ SMC_MTF.mqh)
| Función | Detecta |
|---|---|
| `f_premiumDiscount` | Rango entre último strong high y strong low → Premium (>50%), Discount (<50%), Equilibrium (45–55%) |
| `f_killZone` | `f_killZone(time, sessionProfile)` → qué sesión está activa (o ninguna) + si es la primera mitad de la ventana (para Judas). Ventanas en **hora local de mercado con DST** vía `time(timeframe.period, session, timezone)`: London 07:00–10:00 `Europe/London` · NY AM 08:00–11:00 `America/New_York` · Tokyo 09:00–11:00 `Asia/Tokyo`. Perfiles: `FX-London-NY` / `FX-Asia` / `None` `[ADR-001, P-25; def. en reglas-smc-ict §3.4]` |
| `f_sessionOpens` | Apertura semanal/mensual/trimestral como niveles |
| `f_emaState` | EMAs 20/50/200: posición del precio, cruces (20×50, 50×200, 20×200), rebotes (toque + cierre de vuelta con wick), alineación de las 3 |

### 3.5 Scoring (→ SMC_Scoring.mqh) — usado solo por SMC-Strategy
| Función | Hace |
|---|---|
| `f_scoreConfluences` | Recibe todos los arrays + estados MTF + tabla de pesos → devuelve `(scoreLong, scoreShort, activeList)` |
| `f_computeSLTP` | SL = extremo del OB/swing que justifica la entrada ± buffer (0.1×ATR); TP1 = entrada + 3×riesgo; TPext = siguiente zona/swing no mitigado en TF mayor. Si TPext < TP1 → **no hay señal** (R:R 1:3 incalculable) |

---

## 4. COMUNICACIÓN MTF — D1 → H1 → M5

`[FIX: #6]` Restricción dura: los UDTs y arrays **no cruzan** `request.security()`. Solo tipos simples y tuples (máx ~127 valores). Diseño:

1. **El script corre en el TF del chart (M5 para operar; cualquier TF para visualizar).**
2. **Una sola llamada `request.security` por TF superior**, devolviendo un tuple plano con el snapshot `SMC_TFState` descompuesto (~20 floats/ints):

```pinescript
// En el CONSUMIDOR (Visual y Strategy), nunca en la librería:
f_tfSnapshot() =>
    // ejecuta la detección de la librería en el contexto del TF solicitado
    [bias, bosP, bosD, bosT, chochP, chochD, chochT, pdHigh, pdLow,
     ema20, ema50, ema200, obTop, obBot, obDir, fvgTop, fvgBot, fvgDir,
     sweepRecent, dispRecent]

[d1_bias, d1_bosP, ...] = request.security(syminfo.tickerid, "D",  f_tfSnapshot(), lookahead = barmerge.lookahead_off)
[h1_bias, h1_bosP, ...] = request.security(syminfo.tickerid, "60", f_tfSnapshot(), lookahead = barmerge.lookahead_off)
```

3. **Solo se transfiere la zona/evento MÁS RELEVANTE de cada tipo por TF** (el OB activo más cercano, el FVG activo más cercano, el último BOS/CHoCH/sweep/displacement). Justificación: para el scoring solo importa lo que está cerca del precio actual; la visualización completa del TF mayor se ve cambiando el chart a ese TF. Esto mantiene el tuple pequeño y el indicador rápido.
4. `lookahead_off` SIEMPRE + detecciones evaluadas con `barstate.isconfirmed` → **cero repaint** en señales (las zonas pueden extenderse en vivo, pero los eventos solo se confirman al cierre de vela).
5. Presupuesto: 2 llamadas security (D1, H1) en Strategy; Visual añade máx. 2 más para niveles D/W/M → muy por debajo del límite de 40.

---

## 5. SMC-Visual.pine — ESPECIFICACIÓN

**Declaración:** `indicator("SMC Engine — Visual", overlay=true, max_labels_count=500, max_lines_count=500, max_boxes_count=500)`

**Secciones del código (en orden):**
1. INPUTS — grupos: Estructura / Order Blocks / FVG / Liquidez / ICT / EMAs / MTF / Kill Zones / Panel / Estilo. **Cada concepto tiene toggle on/off** (`[FIX: #6]` el usuario apaga lo que no usa → el código de detección Y dibujo de ese concepto se salta por completo).
2. LIBRARY CORE — import de la librería (o sección copiada, ver D-PINE-01).
3. DETECCIÓN TF PROPIO — llamadas a funciones de librería sobre el chart actual.
4. MTF — los 2 `request.security` snapshots.
5. DIBUJO — una función `f_draw<Concepto>()` por concepto. Elementos del TF mayor: fondo semitransparente (transp 85), borde punteado, etiqueta prefijada `"D1: "` / `"H1: "`.
6. PANEL DE ESTADO — tabla.
7. ALERTAS.

**Presupuesto de objetos (`[FIX: #6]`):** TradingView limita a 500 labels/lines/boxes por tipo. Asignación: OBs 60 boxes, FVGs 60, Breaker/Rejection/Flip 30, zonas MTF 20, Premium/Discount 6, Kill Zones 15 (background), estructura (BOS/CHoCH/MSS) 80 lines+labels, sweeps/pools 50, EMAs 3 plots (no consumen objetos), reserva 100. Implementación: cada `f_draw` mantiene su propio array de objetos y borra el más viejo al superar su cuota (patrón LuxAlgo existente). Modo `Present` (default): solo dibuja estructuras de las últimas `N` barras (input, default 500).

**Panel de estado** (tabla, posición configurable, default top-right). Cada celda: `precio | fecha hora GMT`:

| Concepto | D1 | H1 | M5/chart |
|---|---|---|---|
| Bias | ▲/▼/— | ▲/▼/— | ▲/▼/— |
| Último BOS | precio · dd-MM HH:mm | … | … |
| Último CHoCH | … | … | … |
| Último MSS | … | … | … |
| OB activo más cercano | rango | … | … |
| FVG activo más cercano | rango | … | … |
| Pool más cercano | nivel (BSL/SSL) | … | … |
| Último Sweep | nivel · hora | … | … |
| Displacement reciente | sí/no · hora | … | … |
| Kill Zone | — | activa/próxima | activa/próxima |
| EMA 20/50/200 | ⬆⬆⬆ / mixto | … | … |
| Premium/Discount | P/D/EQ + % | … | … |

Filas con toggle individual (panel compacto vs completo). Colores: verde/rojo/gris según dirección.

**Alertas:** se preservan las 16 del LuxAlgo base `[✓ MANTENER]` + nuevas: Sweep ejecutado (por TF), Kill Zone abierta, Judas detectado, MSS confirmado, precio entra a OB/FVG H1. Todas via `alertcondition()` con mensaje plantilla: `"{{ticker}} | <concepto> <dir> @ {{close}} | TF=<tf> | {{timenow}}"`.

---

## 6. SMC-Strategy.pine — ESPECIFICACIÓN

**Declaración:** `strategy("SMC Engine — Strategy", overlay=true, initial_capital=10000, default_qty_type=strategy.percent_of_equity, default_qty_value=1, commission_type=strategy.commission.cash_per_contract, process_orders_on_close=true)`
(commission/slippage configurados con valores realistas de EURUSD: spread ~0.8 pips → modelar como slippage 1 tick + comisión)

**Scoring direccional (`[FIX: #4]`):** cada confluencia activa suma su peso a `scoreLong` O a `scoreShort` (nunca "score absoluto"). Las ~50 confluencias rediseñadas y agrupadas (lista completa y pesos default en WORKPLAN-MAESTRO-V2 §4.8):

- **Estructura (8):** CHoCH H1 / BOS H1 / CHoCH chart / BOS chart / MSS / secuencia HH-HL o LL-LH / impulso previo / corrección en curso — cada una direccional.
- **Liquidez (8):** pool objetivo en dirección / sweep contrario ejecutado / grab / EQH-EQL barridos / Judas / false breakout / spring / raid.
- **Zonas (10):** precio EN OB H1 / EN FVG H1 / EN OB chart / EN FVG chart / OB-FVG D1 cercano alineado / breaker / rejection / mitigation block / flip / FVG-CE tocado.
- **Premium-Discount-Fib (5):** OTE / Golden Pocket / Discount H1 (long) o Premium H1 (short) / Discount-Premium D1 / Equilibrium → **resta** 50% del peso (zona de chop).
- **ICT (5):** displacement previo / IDM barrido / Kill Zone activa / evento D1 alineado / session open como nivel cercano.
- **EMAs (6, colapsadas de las 15 originales):** precio vs EMA200 (direccional, 1 sola confluencia) / precio vs EMA50 / precio vs EMA20 / cruce reciente alineado (cualquier par, ≤20 velas) / rebote en EMA alineado / 3 EMAs alineadas. `[FIX: #4 — elimina el doble conteo de pares mutuamente excluyentes]`

**Pesos como inputs:** `input.float` por confluencia, agrupados, default 1.0 (peso plano hasta Fase 3). `input.int scoreThreshold` (default: a calibrar). Esto permite **optimizar pesos y threshold con el optimizador del Strategy Tester** sobre el periodo in-sample.

**Lógica de entrada (solo en vela confirmada):**
```
si scoreLong ≥ threshold y scoreLong > scoreShort y spread ≤ maxSpread:   // [ADR-001] KZ no es precondición
    [sl, tp1, tpExt, ok] = f_computeSLTP(...)
    si ok:  // R:R 1:3 calculable
        strategy.entry("L", strategy.long, alert_message = jsonDetalle)
        strategy.exit("L-tp1", from_entry="L", stop=sl, limit=tp1, qty_percent=50)
        strategy.exit("L-ext", from_entry="L", stop=sl, limit=tpExt)
(espejo para short)
```
**Trailing estructural:** mientras la posición esté abierta, al confirmarse un nuevo HL (long) / LH (short) en el chart TF → mover stop de "L-ext" a ese swing ± buffer.
**Filtros duros (no-score):** spread ≤ `maxSpread` (input, guardián universal de liquidez `[ADR-001]`) · R:R ≥ 3 calculable · sin posición abierta del mismo lado. La Kill Zone NO filtra: aporta como confluencia #34 ponderada; inputs `sessionProfile` (FX-London-NY/FX-Asia/None) y `maxSpread` en el grupo Sesiones/Filtros.

**Visual mínimo:** label de entrada con `LONG 14.5pts [CHoCH-H1, Sweep, OB-H1, OTE, KZ-LDN]`, líneas SL (rojo) / TP1 (verde) / TPext (verde punteado). Registro: el Strategy Tester ya guarda cada trade con fecha/precio/resultado → exportable a CSV para el `smc-backtesting-analyst`. Adicionalmente, tabla "últimas 20 señales" opcional.

---

## 7. ORDEN DE IMPLEMENTACIÓN (Sprints de Fase 1 y 2)

Protocolo por concepto: **implementar → compilar 0 errores/0 warnings → screenshot en EURUSD H1 → validar con `smc-validator` contra reglas-smc-ict.md → corregir → commit individual**. Nunca avanzar con un concepto roto.

**Sprint 1.1 — Fundación (todo lo demás depende de esto):**
1. Esqueleto de los 3 archivos + UDTs + naming + arrays con límite
2. Swings + clasificación HH/HL/LH/LL (migrar de LuxAlgo v5 → v6)
3. BOS + CHoCH (swing e interno)
4. Bias por TF

**Sprint 1.2 — Zonas core:**
5. Order Blocks + mitigación (portar algoritmo LuxAlgo)
6. FVG + CE 50% + tracking de mitigación explícito `[FIX: gap del plan original]`
7. Premium/Discount/Equilibrium
8. EQH/EQL

**Sprint 1.3 — Liquidez (corazón SMC):**
9. Pools (clustering EQH/EQL + swings)
10. Sweeps + Grabs
11. Kill Zones (background + estado)
12. MSS

**Sprint 1.4 — MTF + panel:**
13. Snapshots D1/H1 vía security + dibujo diferenciado de zonas/eventos MTF
14. Panel de estado completo
15. Alertas (16 base + nuevas)
→ **Gate Fase 1:** validación visual completa con smc-validator-agent, score ≥ 90% por concepto Tier 1.

**Sprint 1.5 — Tier 2:**
16. Displacement → 17. IDM → 18. Judas → 19. Breaker → 20. Rejection → 21. Flip → 22. OTE + Golden Pocket → 23. EMAs (estado, cruces, rebotes) → 24. False Breakout → 25. Impulsive/Corrective

**Sprint 2.1 — Strategy:** scoring direccional + filtros duros + entrada/SL/TP/trailing + alert_message JSON
**Sprint 2.2 — Calibración técnica:** verificar en Strategy Tester que ejecuta trades correctamente (sin pesos optimizados aún), registro y export CSV.

Tier 3 (Wyckoff, PO3, Volume Surge, etc.): **pospuesto a post-Fase 3** como experimentos individuales — solo se integra lo que demuestre mejorar expectancy out-of-sample.

---

## 8. DECISIONES TÉCNICAS REGISTRADAS

| ID | Decisión | Justificación |
|---|---|---|
| D-PINE-01 | Durante desarrollo, el "core" vive como sección idéntica copiada en Visual y Strategy; se migra a library publicada al cerrar Fase 2 | Publicar/actualizar una library en cada iteración añade fricción (cada cambio requiere republicar y re-importar versión). El diff de la sección core se verifica con script en cada commit (`scripts/check-core-sync.ps1` `[NUEVO]`) |
| D-PINE-02 | Pine v6 (no v5) | Tipos UDT mejorados, `request.security` más estricto y predecible, métodos sobre arrays. La migración del código LuxAlgo v5 es parte del Sprint 1.1 |
| D-PINE-03 | Eventos solo en `barstate.isconfirmed`; `lookahead_off` siempre | Cero repaint — condición indispensable para que el backtest sea creíble y para que MQL5 (que opera velas cerradas) coincida con TV |
| D-PINE-04 | Del TF mayor solo se transfiere el elemento más relevante por tipo | Tuples de security son limitados; el scoring solo necesita lo cercano al precio |
| D-PINE-05 | Strategy con comisión+slippage realistas desde el día 1 | Un backtest sin costes es ficción; con R:R 1:3 y SL ajustados, el spread es material en M5 |
| D-PINE-06 | LuxAlgo CC BY-NC-SA: uso personal OK; NO publicar derivado con fines comerciales; mantener atribución en header | Cumplimiento de licencia |

## 9. QUÉ SE REUTILIZA DEL LuxAlgo BASE

`[✓ MANTENER]` Algoritmos a portar (v5→v6, hacia funciones de librería): detección de swings con leg(), estructura interna vs swing, Order Blocks con filtro ATR/rango acumulado, mitigación por close o high/low, FVG con threshold, EQH/EQL con sensibilidad, Premium/Discount basado en trailing extremes, patrón de gestión de objetos (borrar el más viejo).
**Se reescribe:** todo el sistema de inputs (reagrupado), el dibujo (presupuesto por concepto), MTF (snapshots consolidados en vez de security por concepto), y se añade todo lo que el base no tiene (pools, sweeps, KZ, MSS, displacement, IDM, Judas, OTE, EMAs, breaker...).

## 10. TESTING Y VALIDACIÓN POR CONCEPTO

1. **Compilación:** TV MCP `pine-develop` → 0 errores, 0 warnings.
2. **Test visual dirigido:** para cada concepto, identificar manualmente 3 ocurrencias históricas claras en EURUSD (ej.: sweep del 2026-03-12 08:30) y verificar que el indicador las marca — y que NO marca falsos obvios.
3. **Validación formal:** skill `smc-validator` con screenshot → score por concepto contra reglas-smc-ict.md (≥90% para aprobar).
4. **Test de performance:** cargar en chart M5 con 20k barras → sin error "calculation takes too long"; si falla → revisar presupuesto/loops.
5. **Test anti-repaint:** comparar señales en tiempo real (paper de 2 días) vs históricas en mismas velas → deben ser idénticas.
