# MQL5-PLAN — Diseño técnico del Expert Advisor MT5
> Anexo 6 del WORKPLAN-MAESTRO-V2.md | Estrategia 2.0 | 2026-06-10
> Cubre el Paso 6 del PROMPT-FABLE. Nivel: diseño técnico — el código se escribe en Fase 4, SOLO tras validar Fase 3 en TradingView.
> **Decisión del usuario:** el EA es 100% nativo y autónomo en MQL5. NO existe puente webhook TV→MT5. El EA recalcula toda la detección y el scoring por sí mismo, con los pesos validados en Fase 3.

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
struct SMC_Zone   { double top, bottom; int dir; datetime barTime; int state; double mitigatedPct; ENUM_TIMEFRAMES tf; int kind; };
struct SMC_Event  { double price; int dir; datetime barTime; ENUM_TIMEFRAMES tf; int kind; };
struct SMC_Swing  { double price; datetime barTime; int kind; bool swept; };
struct SMC_Pool   { double level; int dir; int touches; datetime barTime; bool swept; ENUM_TIMEFRAMES tf; };
struct SMC_TFState{ int bias; SMC_Event lastBOS, lastCHoCH; double pdHigh, pdLow; double ema20, ema50, ema200; SMC_Zone nearestOB, nearestFVG; /*...*/ };
struct SMC_Signal { int dir; double score, entry, sl, tp1, tpExt; string confluences; datetime t; };
// enums KIND_*, STATE_*, + inputs compartidos (umbrales de reglas-smc-ict.md como constantes input)
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
