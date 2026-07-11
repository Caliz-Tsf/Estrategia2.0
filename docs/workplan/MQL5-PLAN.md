# MQL5-PLAN — Diseño técnico del Expert Advisor MT5
> Anexo 6 del WORKPLAN-MAESTRO-V2.md | Estrategia 2.0 | 2026-06-10 · **REFRESCADO 2026-07-06 (S097)**
> Cubre el Paso 6 del PROMPT-FABLE. Nivel: diseño técnico — el código se escribe en Fase 4, SOLO tras validar Fase 3 en TradingView.
> **Decisión del usuario:** el EA es 100% nativo y autónomo en MQL5. NO existe puente webhook TV→MT5. El EA recalcula toda la detección y el scoring por sí mismo, con los pesos validados en Fase 3.

---

## 0. NOTA DE REFRESCO (2026-07-06, S097) — qué cambió desde 2026-06-10
Este documento se escribió antes de que el CORE Pine evolucionara. Sincronizado contra el CORE actual (**1952 líneas, SHA `d86bf37aacbd25cf`** — re-baseline S115 tras promover los extremos HTF; el SHA previo `5510361166844bd5` fue el CORE de 1700 líneas hasta S114). Cambios que los structs espejo DEBEN reflejar:
- **`strength` (ADR-014):** propiedad de DETECCIÓN (vive en el CORE byte-idéntico, no en Visual). Todo UDT de zona/evento/swing/pool la lleva. El EA la necesita para jerarquía y para alimentar el scoring. **Añadida abajo.**
- **KIND hasta 53:** el enum `KIND_*` creció (KIND_GRADIENT=53, breaker/flip/mitigation/rejection/IFVG/BPR, etc.). El struct `SMC_Zone.kind` ya es `int`, pero el enum espejo debe cubrir ≤53.
- **Gradient Levels (§5.16, KIND_GRADIENT=53):** grid de quadrants/eighths + `gradedFvg` (flag "FVG toca nivel del grid") + confluencia exponencial #52 (multiplicador, ADR-013). Nuevo subsistema a mapear.
- **Primitivos §7 (`posRole` / `confDegree` / `depthBand`):** capa de proyección/confluencia. **Hoy son Fase A Visual-only** (calculados en `SMC-Visual.pine`). **Fase B los promueve al CORE** con campos UDT nuevos + SHA nuevo + ADR. **Hasta que Fase B cierre, el EA los recalcula igual que el CORE** (son lectura pura de la detección existente). Reservados en los structs abajo como `[Fase B]`.
- **Extremos HTF (ADR-018, promovidos al CORE en S115):** además del transporte **nearest-N** (`f_computeTFState`, 89 campos, el que ya se mapea abajo), el CORE ahora emite un **2º contrato "farthest-important"** (`f_tfExtremes`, 51 campos = 3 escalares + 8 slots × 6) que da el **extremo IMPORTANTE por concepto/lado** más allá del Premium/Discount vigente (objetivos de liquidez / confluencias de contexto en ambas direcciones, §4.8). Es una **2ª `request.security` por HTF** en el consumidor (en Pine: Strategy D1+H1). El EA lo replica con un **2º struct espejo** (`SMC_TFExtremes`, abajo) y una 2ª pasada de detección por TF con selección farthest (no nearest). **Semántica clave:** `kind < 0` = extremo **traspasado/tomado** (mitigada / pool barrido / EQ cruzado) → contexto histórico, peso reducido; `kind == 0` = ranura vacía. Orden fijo de 8 slots: OB↑, OB↓, FVG↑, FVG↓, POOL↑, POOL↓, EQH↑, EQL↓. **Fuera de alcance v1:** MB/Breaker/BOS-CHoCH como extremos heredados (v2).
- **Enjambre + debate + cuaderno del EA:** el diseño 2026-06-10 no contemplaba el modelo de decisión del agente (proyección + debate darwiniano). Se especifica en el **DOSSIER-FABLE Fase 4** (`docs/planes/DOSSIER-FABLE-fase4-ea-mt5.md`) → Fable produce el esqueleto. **Este MQL5-PLAN cubre solo el EA determinista;** la capa cognitiva (enjambre) es aditiva y se ancla en Fase 3/4.

---

## 1. ARQUITECTURA — 6 MÓDULOS + EA

`[FIX]` Se añade un 6º módulo `SMC_Liquidity.mqh`: en el diseño original la liquidez (pools, sweeps, IDM, Judas) estaba mezclada dentro de Structures, pero es el subsistema más grande y con más estado propio — separado mejora el mapeo 1:1 con la librería Pine.

```
mt5/
├── Experts/
│   └── EA_SMC_ICT.mq5            ← orquestador: eventos MT5, órdenes, recovery
└── Include/SMC/
    ├── SMC_Types.mqh             ← [NUEVO] structs (espejo de los UDT Pine) + enums + constantes
    ├── SMC_Structures.mqh        ← swings, BOS, CHoCH, MSS, displacement, OB, FVG, breaker...
    ├── SMC_Liquidity.mqh         ← [NUEVO] EQH/EQL, pools, sweeps, grabs, Judas, IDM
    ├── SMC_MTF.mqh               ← snapshots D1/H1, Kill Zones, Premium/Discount, EMAs, session opens
    ├── SMC_Scoring.mqh           ← motor de confluencias direccional + pesos Fase 3
    ├── SMC_RiskManager.mqh       ← lotes, SL/TP, R:R 1:3, trailing estructural, límites de riesgo
    └── SMC_Display.mqh           ← panel visual MT5 (espejo del panel TV)
```

### Grafo de dependencias (acíclico — sin dependencias circulares)
```
SMC_Types.mqh  ←─ (todos dependen solo de Types y de los niveles inferiores)
   ↑
SMC_Structures.mqh ──┐
SMC_Liquidity.mqh ───┼──→ usados por → SMC_MTF.mqh ──→ SMC_Scoring.mqh ──→ EA
                     │                                   SMC_RiskManager.mqh ─→ EA
                     └────────────────────────────────→  SMC_Display.mqh ────→ EA
```
Regla: un módulo solo incluye módulos por debajo de él en el grafo. Display lee de todos pero ningún módulo lee de Display. RiskManager no conoce Scoring (recibe la señal ya formada del EA).

---

## 2. RESPONSABILIDADES E INTERFACES PÚBLICAS

### SMC_Types.mqh
Espejo exacto de los UDT Pine (PINE-PLAN §2):
```cpp
// [REFRESCO S097] + strength (ADR-014), gradedFvg/propulsion (§5.16/§5.18), y campos §7 [Fase B]
struct SMC_Zone   { double top, bottom; int dir; datetime barTime; int state; double mitigatedPct;
                    ENUM_TIMEFRAMES tf; int kind; double strength;            // ADR-014
                    bool gradedFvg; bool trueFvg; bool propulsion;            // §5.16/§5.18
                    int posRole; int confDegree; int depthBand; };            // §7 [Fase B: hoy recalculado, no persistido]
struct SMC_Event  { double price; int dir; datetime barTime; ENUM_TIMEFRAMES tf; int kind; double strength; };
struct SMC_Swing  { double price; datetime barTime; int kind; bool swept; double strength; };
struct SMC_Pool   { double level; int dir; int touches; datetime barTime; bool swept; ENUM_TIMEFRAMES tf; double strength; };
struct SMC_TFState{ int bias; SMC_Event lastBOS, lastCHoCH; double pdHigh, pdLow, pdEq;
                    double ema20, ema50, ema200; SMC_Zone nearestOB, nearestFVG;
                    double gradTop, gradBottom; int gradSrcKind; /*grid §5.16*/ };
// [ADR-018 · S115] 2º contrato del CORE: extremos "farthest-important" por HTF (f_tfExtremes, 51
// campos). 8 slots FIJOS: OB^ OBv FVG^ FVGv POOL^ POOLv EQH^ EQLv. kind<0 = traspasado/tomado.
struct SMC_ExtremeSlot { int kind; double top, bottom; int dir; datetime tA, tB; }; // kind==0 => vacío
struct SMC_TFExtremes  { double pdHigh, pdLow, atr14; SMC_ExtremeSlot slot[8]; };    // 3 escalares + 8×6
struct SMC_Signal { int dir; double score, entry, sl, tp1, tpExt; string confluences; datetime t; };
// enums KIND_* (≤53, incl. KIND_GRADIENT=53, KIND_BREAKER/FLIP/MITIGATION/REJECTION/IFVG/BPR),
//       STATE_* (ciclo de vida §5.4), POSROLE_{INTERNO=0,GIRO=1,ORIGEN=2}, + inputs compartidos
//       (umbrales de reglas-smc-ict.md como constantes input; wPos/kConf/tolConf/tolPos/bandas congelados)
```

### SMC_Structures.mqh  *(mapea f_detectSwings, f_classifySwing, f_detectBOS/CHoCH/MSS, f_detectDisplacement, f_isImpulsive, f_detectOB, f_detectFVG, f_updateZoneMitigation, f_detectBreaker/Rejection/Flip, f_detectOTE)*
```cpp
class CSMCStructures {
public:
   bool   Init(ENUM_TIMEFRAMES tf, int maxZones, int maxEvents);
   void   OnNewBar(const MqlRates &rates[]);     // recalcula TODO el TF con la vela cerrada
   int    GetBias();
   bool   GetLastEvent(int kind, SMC_Event &out);
   int    GetActiveZones(int kind, SMC_Zone &out[]);   // copia filtrada
   bool   GetNearestZone(int kind, double price, SMC_Zone &out);
};
```

### SMC_Liquidity.mqh  *(mapea f_detectEQHL, f_buildPools, f_detectSweep, f_detectGrab, f_detectJudas, f_detectIDM, f_detectFalseBreakout)*
```cpp
class CSMCLiquidity {
public:
   bool   Init(ENUM_TIMEFRAMES tf, CSMCStructures *structs);  // lee swings de Structures
   void   OnNewBar(const MqlRates &rates[], bool inKillZone);
   int    GetActivePools(SMC_Pool &out[]);
   bool   GetLastEvent(int kind, SMC_Event &out);              // sweep/grab/judas/idm/fbo
};
```

### SMC_MTF.mqh  *(mapea f_premiumDiscount, f_killZone, f_sessionOpens, f_emaState + el rol de los snapshots request.security)*
```cpp
class CSMCMTF {
public:
   bool   Init();                                  // crea CSMCStructures+CSMCLiquidity internos para D1 y H1
   void   OnNewBar();                              // detecta nuevas velas D1/H1 cerradas y actualiza snapshots
   bool   GetTFState(ENUM_TIMEFRAMES tf, SMC_TFState &out);
   bool   InKillZone(string &zoneName);            // según input sessionProfile (FX-London-NY/FX-Asia/None) [ADR-001]; hora local de mercado con DST → convertir desde hora del broker. NO es guard: alimenta la confluencia #34
   double GetSessionOpen(int which);               // W / M / Q
};
```

### SMC_Scoring.mqh  *(mapea f_scoreConfluences — pesos = los validados en Fase 3, como inputs del EA)*
```cpp
class CSMCScoring {
public:
   bool   Init(const double &weights[], double threshold);
   // recibe TODO el estado, devuelve señal si la hay (sin efectos secundarios):
   bool   Evaluate(const SMC_TFState &d1, const SMC_TFState &h1,
                   CSMCStructures *chartS, CSMCLiquidity *chartL,
                   bool inKZ, SMC_Signal &out);
   string GetActiveConfluences();                  // para log/panel/journal
};
```

### SMC_RiskManager.mqh  *(mapea f_computeSLTP + todo lo que Pine no hace: lotes, ejecución de riesgo real)*
```cpp
class CSMCRisk {
public:
   bool   Init(double riskPctPerTrade, double maxDailyLossPct, int maxOpenPositions);
   bool   ComputeSLTP(const SMC_Signal &sig, double &sl, double &tp1, double &tpExt); // R:R>=3 o false
   double ComputeLots(double entry, double sl);    // % riesgo / distancia SL, normalizado a VOLUME_STEP
   bool   RiskBudgetOK();                          // pérdida diaria, posiciones abiertas, equity stop
   void   UpdateTrailing(ulong ticket, CSMCStructures *chartS);  // SL → último HL/LH confirmado ± buffer
};
```

### SMC_Display.mqh
```cpp
class CSMCDisplay {
public:
   bool   Init(int corner);
   void   Update(const SMC_TFState &d1, const SMC_TFState &h1, /*chart state*/,
                 double scoreL, double scoreS, string kz);      // espejo del panel TV
   void   ShowSignal(const SMC_Signal &sig);                    // flecha + líneas SL/TP en chart
};
```

### EA_SMC_ICT.mq5 — orquestador
```cpp
// Inputs: pesos (grupo por categoría — perfil POR SÍMBOLO [ADR-001]), threshold, riesgo (%/trade, % diario máx),
//         sessionProfile (FX-London-NY/FX-Asia/None), maxSpread, magic, símbolo de validación, modo (live/demo/test)
int OnInit():    valida símbolo == el del perfil cargado (EURUSD hasta expansión Fase 5 [ADR-001]) → Init de los 6 módulos
                 → RECOVERY: escanear posiciones abiertas con nuestro magic y re-adoptarlas
void OnTick():
   1. if (!isNewBar(PERIOD_CURRENT)) { gestionar trailing intra-vela si hay posición; return; }
   2. mtf.OnNewBar()                       // snapshots D1/H1 si cerraron vela
   3. chartStructures.OnNewBar(rates)      // detección en el TF del chart (M5)
   4. chartLiquidity.OnNewBar(rates, inKZ)
   5. display.Update(...)
   6. if (spreadActual > maxSpread || !risk.RiskBudgetOK() || hayPosicion()) return;   // KZ NO bloquea [ADR-001]; su estado entra al scoring como confluencia #34
   7. if (scoring.Evaluate(...) == señal):
        risk.ComputeSLTP → risk.ComputeLots → OrderSend (verificar retcode,
        reintentos con backoff) → journal CSV → display.ShowSignal
void OnTrade():  registrar fills/cierres en journal (docs/sprint-runs/mt5-journal.csv)
void OnDeinit(): liberar objetos del display
```

**Flujo por tick:** `tick → ¿vela nueva? —no→ trailing y salir | —sí→ MTF → Structures → Liquidity → Display → guards (spread, riesgo, posición) → Scoring → Risk → OrderSend`. `[ADR-001]`
Todo el trabajo pesado ocurre solo en vela nueva (en M5: una vez cada 5 min) → el target <50ms/tick es holgado; el tick promedio hace solo el guard isNewBar + trailing (µs).

---

## 3. MAPEO PINE → MQL5 (tabla de traducción de Fase 4)

| Función Pine (core) | Módulo MQL5 | Método | Notas de traducción |
|---|---|---|---|
| f_detectSwings / f_classifySwing | SMC_Structures | OnNewBar interno | índices: ArraySetAsSeries(true) |
| f_detectBOS / f_detectCHoCH / f_detectMSS | SMC_Structures | OnNewBar interno | solo vela cerrada (shift≥1) |
| f_detectOB / f_detectFVG / f_updateZoneMitigation | SMC_Structures | OnNewBar interno | ta.atr → implementar EMA-Wilder exacta, validar numéricamente vs TV |
| f_detectBreaker / Rejection / Flip / OTE | SMC_Structures | OnNewBar interno | |
| f_detectEQHL / f_buildPools / f_detectSweep / Grab / Judas / IDM / FalseBreakout | SMC_Liquidity | OnNewBar interno | |
| f_premiumDiscount / f_killZone / f_sessionOpens / f_emaState | SMC_MTF | OnNewBar/getters | KZ: sessionProfile + hora local de mercado con DST [ADR-001]; convertir hora broker→GMT con TimeGMT(); ta.ema → seed SMA + alpha 2/(n+1), NO iMA directo sin validar |
| snapshots request.security("D"/"60") | SMC_MTF | CopyRates(PERIOD_D1/H1) | usar solo velas cerradas (shift 1); la vela diaria del broker puede abrir a otra hora que TV → documentar offset del broker elegido |
| f_computeGradientLevels / f_gradientZone / f_nearGradientLevel / f_selectGradientSource | SMC_MTF (grid) + SMC_Structures (gradedFvg) | OnNewBar interno | §5.16 KIND_GRADIENT=53; grid P1/P2/P3, ghost/persistencia; gradedFvg = CE del FVG dentro de gradTol×ATR de un nivel |
| f_zoneStrength / f_eventStrength / f_strengthLevel | todos los detectores | interno, al crear cada instancia | ADR-014; pesos de strength congelados (HANDOFF §5.2); alimenta jerarquía y scoring |
| f_posRole / f_confDegree / f_depthBand (§7) | SMC_Scoring (lectura pura) | interno | **[Fase B]** hoy Visual-only; el EA los recalcula sobre la detección; wPos/kConf/tolConf/tolPos/bandas congelados (ADR-002) |
| f_gradientConfluenceBonus (#52, multiplicador) | SMC_Scoring | Evaluate | ADR-013: `scoreDir_final = scoreDir_raw × (1+bonus)`; wiring en Fase 2, calibración Fase 3 |
| f_scoreConfluences | SMC_Scoring | Evaluate | pesos = inputs, default = scoring-weights-final.md de Fase 3 |
| f_computeSLTP | SMC_RiskManager | ComputeSLTP | + normalización tick size / stops level del broker |
| panel (tabla Pine) | SMC_Display | Update | objetos OBJ_LABEL / Canvas |
| — (no existe en Pine) | SMC_RiskManager | ComputeLots, RiskBudgetOK, UpdateTrailing | nuevo: riesgo real |
| — (no existe en Pine) | EA | OnInit recovery, OrderSend retry, journal | nuevo: ejecución real |

**Golden tests:** por cada fila de las secciones de detección, ≥5 tests con OHLC reales de EURUSD extraídos de TV y la detección esperada (evento+precio+tiempo). Criterio: 0 diferencias en eventos, ±1 tick en niveles. El runner es un Script MT5 (`mt5/Scripts/SMC_RunGoldenTests.mq5`) que carga casos desde CSV en `mt5/tests/golden/`.

---

## 4. PIPELINE DE DESARROLLO FASE 4 (workflow 3 agentes)

```
Por cada módulo (orden: Types → Structures → Liquidity → MTF → Scoring → Risk → Display → EA):
1. mql5-translator-agent (Opus)  → spec + código + golden tests   [skill mql5-translator]
2. Antigravity IDE (si disponible) u Opus/Sonnet → escribe/completa el código
3. mql5-reviewer (Sonnet)        → review; loop hasta APROBADO (máx 3, luego smc-architect)
4. Claude Code                   → integra, compila MetaEditor CLI: 0 errors / 0 warnings
5. Golden tests                  → workflow archon-test-loop-dag hasta verde
6. Claude Desktop (computer use) → verificación visual MT5: panel, Strategy Tester, objetos chart
7. Commit + archon-validate-pr antes de merge
```

### Validación de Fase 4 (gates secuenciales)
1. **Golden tests**: todos los módulos de detección verdes (paridad con Pine).
2. **Strategy Tester MT5**: ≥2 años EURUSD, modo "Every tick based on real ticks". Criterio: métricas comparables a las de TV Fase 3 (PF dentro de ±20%, mismo orden de magnitud de trades). Si difieren mucho → investigar dato por dato (suele ser: horario del broker, spread real, vela D1 distinta).
3. **Forward demo**: ≥60 días en cuenta demo. Criterio: expectancy > 0 y comportamiento = backtest.
4. **Live lote mínimo**: 0.01 lotes, ≥30 días. Solo entonces escalar capital gradualmente.

### Riesgos específicos Pine↔MQL5 (anticipados — Paso 8 del prompt)
- **Datos distintos**: TV (consolidado) vs broker (su propio feed). Las detecciones pueden diferir legítimamente en velas límite. Mitigación: golden tests usan datos del broker exportados, no de TV, para los gates 2-4; la paridad exacta solo se exige sobre datos idénticos.
- **Vela D1**: TV corta a las 17:00 NY; muchos brokers también, otros no. Elegir broker con D1 17:00 NY o ajustar.
- **ATR/EMA seeds**: implementaciones propias validadas numéricamente (no confiar en iATR/iMA ciegamente).
- **Spread y stops level**: SL de M5 pueden quedar bajo el stops level del broker → RiskManager lo verifica y descarta la señal (y lo registra).
