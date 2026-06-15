# Sesión 021 — 2026-06-14

## Objetivo
F1-S1.2-T07 — Premium/Discount/Equilibrium (Sprint 1.2, PINE-PLAN §7).

## Arranque
- ESTADO-ACTUAL ✅ (T06 cerrado, siguiente T07) · git limpio, rama `pine/sistema-completo` ✅
- TV MCP: lanzado vía `tv_launch` (CDP 9222) ✅, EURUSD H1.
- Plan confirmado: ciclo del concepto + documentar las 2 opciones de rango (petición del usuario).

## Trabajo

### Implementación T07 (opción A — trailing extremes de LuxAlgo)
- **Decisión del usuario:** opción **A** (trailing extremes de LuxAlgo) vs **B** (último strong
  high/low por BOS/CHoCH). Documentada en `docs/decisiones-pd-rango.md` (A vs B + por qué A:
  paridad LuxAlgo + portabilidad MQL5 con estado plano).
- **CORE byte-idéntico** (Visual/Strategy) + export en Library: `type SMC_Trailing`,
  `f_resetTrailingHigh/Low`, `f_updateTrailing`, `f_premiumDiscount` (→ `[zona, pct]`),
  constantes `PD_DISCOUNT/PD_EQUILIBRIUM/PD_PREMIUM`.
- **Visual:** wiring + dibujo en **líneas** (premium roja / discount verde / eq punteada gris) +
  fila de panel + inputs grupo `Premium/Discount`. **Strategy:** wiring + label, input en `Scoring`.
- **Swing P/D dedicado `i_pdSwingLen=50`** (= `swingsLengthInput` de LuxAlgo) separado del
  `swingLen=5` estructural → rango DOMINANTE.

### Bugs encontrados y corregidos (3)
1. **Panel >100%:** el `pct` superaba 100% en la barra viva porque el snapshot se congelaba en
   `isconfirmed` mientras `close` era vivo. Fix: `f_updateTrailing` corre CADA barra (expansión en
   vivo, como LuxAlgo `updateTrailingExtremes`); el snapshot de scoring sigue solo en `isconfirmed`.
2. **Rango local en vez de dominante** (lo detectó el usuario comparando con LuxAlgo: discount debía
   estar ~1.15000 en el LL del 8-jun): los trailing extremes se anclaban con `swingLen=5`. Fix:
   swing P/D dedicado de **50**. Tras el fix los niveles coinciden EXACTO con §2.3.
3. **Líneas P/D "volando":** usaban un ancla compartida. Fix: cada línea se ancla en su propio
   extremo vía `topTime`/`bottomTime` (cf. LuxAlgo `lastTopTime`/`lastBottomTime`).
- Cambio de **cajas → líneas** por preferencia del usuario (menos ruido visual).

### Gates
- Compila **0/0** los 3 en TV (EURUSD H1; Visual reinyectado y recompilado tras cada fix).
- `check-core-sync.ps1` **OK** — 415 líneas, SHA `24c3a4a28fcf74c3` (el CORE no cambió con los
  ajustes de dibujo/escala, todos en DETECCIÓN/INPUTS/DIBUJO).
- **Validación 97/100** (`docs/sprint-runs/validaciones.md`): 4 niveles §2.3 exactos al 5º decimal
  (Premium 1.16859 / EQ 1.15928 / Discount 1.14997 / banda [1.15835,1.16021]) + paridad visual con
  LuxAlgo en el mismo chart. Clasificación verificada numéricamente (panel "Premium NN%").
- **Commit ddd8cc5** `feat(pine-core): F1-S1.2-T07 ...`.

## Pendiente abierto (Sesion-022 — sesión DEDICADA)
- **Estructura BOS/CHoCH de escala GRANDE (swing=50).** Nuestro `swingLen=5` ≈ interno de LuxAlgo;
  falta la capa de swing grande (LuxAlgo usa 50). Por eso no se ven los BOS/CHoCH grandes.
- Ejemplos del usuario (LuxAlgo, EURUSD H1) y opciones B/C en `docs/pendiente-estructura-swing-grande.md`.
- Reglas: planear con opus-max/smc-architect (+ skills/agentes/MCP/workflow que hagan falta), NO
  romper T01–T07, ciclo y validación igual que todo stask, actualizar los 3 docs si cambia la def.

## Estado de herramientas
- TV MCP ✅ (compilación + lectura de tablas/labels/screenshots vía MCP).
- check-core-sync ✅.

## Siguiente
Sesion-022 (dedicada): estructura swing grande. Luego T08 EQH/EQL.
