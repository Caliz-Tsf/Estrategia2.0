# Sesion-053 — 2026-06-23

> **Módulo INTEGRACIÓN (TradingView MCP Desktop + MetaTrader 5 MCP). NO Pine.** Core intacto, ningún `.pine` tocado, core-sync OK (verificado: 1517 líneas SHA `80fad14dd8d03758`). La validación visual del set completo (Sesion-049, F1-GATE) **sigue pendiente**. Continuación directa de `[[Sesion-052]]`.

## Objetivo
1. Conectar el MCP de TradingView Desktop (con su agente browser/CDP) al conector de Claude Desktop.
2. Conectar el MCP de MetaTrader 5 al conector de Claude Desktop.
3. Verificar que ambos funcionen E2E (TV chart, MT5 account, operaciones).

---

## Completado

### A. INSTALACIÓN DEL MCP DE MT5

**Paquete instalado:**
```
pip install metatrader-mcp-server==0.5.1
```

**Detalles:**
- Proveedor: `ariadng/metatrader-mcp-server` (repositorio GitHub).
- Versión: **0.5.1**.
- MetaTrader 5: **5.0.5735** (instalado localmente).
- Rueda compatible: `cp314` (Python 3.14 compatible — proyecto usa Python 3.13.0, pero el wheel es forward-compatible).
- Función: expone `metatrader-mcp-server.exe` como comando ejecutable (wrapper Python).

**Verificación:**
```bash
metatrader-mcp-server --help
# Response: MCP server para MetaTrader 5 con operaciones CRUD + datos de cuenta
```

---

### B. MONTAJE DE AMBOS MCP EN CLAUDE DESKTOP CONFIG

**Ubicación REAL del config (GOTCHA CLAVE):**

Claude Desktop en Microsoft Store (MSIX) **NO utiliza** `C:\Users\<user>\AppData\Roaming\Claude\claude_desktop_config.json` como se documentaba en tutoriales genéricos. Esa ruta cae bajo virtualización MSIX (invisible en el Explorador). **El config REAL está en:**

```
C:\Users\Fredd\AppData\Local\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\claude_desktop_config.json
```

**Cómo acceder:**
- **Atajo:** Claude Desktop → Configuración → Desarrollador → "Editar configuración" — abre VS Code con el archivo correcto.
- **Alternativa manual:** abrir ruta anterior en el Explorador (copiar/pegar en barra de direcciones).

**Config final (fragmento):**

```json
{
  "mcpServers": {
    "tradingview": {
      "command": "node.exe",
      "args": ["D:\\CODE\\BOT\\Bot\\tradingview-mcp-jackson\\server.js"]
    },
    "metatrader": {
      "command": "metatrader-mcp-server.exe",
      "args": [
        "--account", "4529532",
        "--password", "Freddy123456!",
        "--server", "ForexClub-Demo"
      ]
    }
  }
}
```

**Notas:**
- **tradingview:** sin args de credencial (se engancha directo a TV Desktop por CDP puerto 9222).
- **metatrader:** cuenta DEMO ForexClub (balance $50k, leverage 1000, USD). Password en texto plano (DEMO = riesgo bajo; migrar a variable de entorno si pasa a cuenta real).

**Reinicio obligatorio:**
Tras editar, cerrar Claude Desktop completamente (Alt+F4) y relanzar para que Lee el config.

---

### C. VERIFICACIÓN EN VIVO DE CONECTORES

**Estado en interfaz de Conectores:**

1. **tradingview:** ✅ Verde, operativo
2. **metatrader:** ✅ Verde, operativo

**Pruebas funcionales:**

#### Conector MetaTrader 5
```
Tool: mcp__metatrader__get_account_info
Response:
- balance: $50,000
- equity: $50,000
- free_margin: $50,000
- leverage: 1000
```

```
Tool: mcp__metatrader__get_symbol_price
Symbol: EURUSD
Response:
- bid: 1.13819
- ask: 1.13864
- time: 2026-06-23 14:32:15 UTC
```

#### Conector TradingView
```
Tool: mcp__tradingview__tv_launch
Response:
- PID: 12032
- CDP port: 9222
- Binary: TradingView.Desktop_3.2.0
- Status: running
```

```
Tool: mcp__tradingview__chart_get_state
Response:
- symbol: OANDA:EURUSD
- timeframe: 1H
- type: candlestick
- indicators: ["SMC Engine — Visual", "Smart Money Concepts [LuxAlgo]"]
```

---

### D. DIAGNÓSTICO Y FIX DEL SCRIPT LAUNCH-TV-AGENT

**Script afectado:** `scripts/launch-tv-agent.ps1`

**Problema:** fallaba al ejecutarse desde cwd ≠ `D:\CODE\Estrategia2.0`, error de rutas relativas (`.\ server.js` no encontraba el módulo).

**Solución aplicada:**
- Cambiar todas las rutas de `scripts/launch-tv-agent.ps1` a absolutas.
- Ejemplo anterior: `.\server.js` → `D:\CODE\BOT\Bot\tradingview-mcp-jackson\server.js`.

**Invocación correcta:**
```powershell
powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\launch-tv-agent.ps1"
```

**Estado de herramientas:**
- **agent-browser:** v0.26.0 instalado global (`npm list -g agent-browser`).
- **ExecutionPolicy:** CurrentUser = RemoteSigned (no era problema de permisos).

---

### E. DOCUMENTACIÓN CREADA

**Archivo nuevo:** `docs/CONECTORES-MCP.md`

**Contenido:** ≤40 líneas con:
- Descripción de cada MCP (TV, MT5).
- Ubicación del config Claude Desktop REAL.
- Instrucciones de instalación (pip, npm).
- Ejemplo de config JSON.
- Verificación de estado (colores verdes en interfaz).
- Gotchas (MSIX, paths absolutos, reinicio).

**Link añadido:** CLAUDE.md lista de fuentes de verdad ahora incluye:
```markdown
- **MCPs conectados:** [docs/CONECTORES-MCP.md](docs/CONECTORES-MCP.md).
```

**Commit:** `2ec4be1` — `docs(conectores): S053 — TV+MT5 como conectores MCP en Claude Desktop`.

---

## Verificación
- **MCP TV:** instalado en fork D:\CODE\BOT\Bot\tradingview-mcp-jackson, lanzable vía MCP ✅.
- **MCP MT5:** instalado vía pip (metatrader-mcp-server 0.5.1), ejecutable ✅.
- **Config Claude Desktop:** ambos conectores registrados en la ruta REAL (MSIX LocalCache), con credenciales (Demo), operativos ✅.
- **Verificación E2E:** get_account_info (MT5) + chart_get_state (TV) + quote_get (EURUSD real) ✅.
- **Documentación:** docs/CONECTORES-MCP.md creado, CLAUDE.md actualizado ✅.
- **Commit:** `2ec4be1` coherente ✅.
- **Core:** intacto, core-sync OK (1517 líneas SHA `80fad14dd8d03758`) ✅.

---

## Commits de Sesion-053
1. **2ec4be1** — `docs(conectores): S053 — TV+MT5 como conectores MCP en Claude Desktop`

---

## SIGUIENTE SESIÓN — ACUERDO EXPLÍCITO

### Plan: Corrida semi-autónoma de validación visual del set completo Pine

**Objetivo:** retomar y completar **Sesion-049 (F1-GATE)** con los MCPs ya conectados.

**Flujo e2e que Claude ejecuta autónomamente:**
1. **Para cada concepto T01–T40 (40 conceptos totales):**
   - MCP: apagar TODOS los `i_show*` en Visual.
   - MCP: encender SOLO `i_showX` del concepto en turno (aislar sin ocultar detección).
   - MCP: `chart_scroll_to_date` → navegar a los casos ✓ y ✗ documentados en `docs/reglas-smc-ict.md` §T.
   - MCP: `capture_screenshot` → salvar evidence por concepto.
   - MCP: `data_get_pine_lines/labels/boxes` + `quote_get` + `data_get_ohlcv` → extraer valores numéricos del indicator.
   - Validador: correr `smc-validator-agent` con los datos capturados → score por concepto.
   - Registrar: PASS ≥90 o FAIL < 90 con diagnóstico.

2. **Agregación final:**
   - Score GLOBAL = media ponderada Tier 1 (T01–T15) + Tier 2 (T16–T25) + Tier 3 (T26–T40).
   - Gate F1: GLOBAL ≥90 + **anti-repaint verificado (2 días EURUSD histórico)** + **performance 20k barras** → PASA.
   - Si algún concepto < 90 → reportar con retroceso planificado (no ajusta criterio, regla dura 8).

3. **El usuario:**
   - Observa el flujo ejecutándose (screenshots progresivos).
   - **Firma de aprobación por concepto o lote:** "Aprobado T01–T05" / "T13a rechazado, retroceso necesario" (NO se salta gate).
   - Firma final de gate: "Gate F1-GATE APROBADO" desbloquea Sprint 2.1 (scoring).

**Preparación para la próxima sesión:**
- Tener EURUSD H1 cargado en TradingView Desktop.
- Plan de ejecución: `docs/sprint-runs/PLAN-VALIDACION-Sesion-049.md` ya existe (creado S048), contiene la lista ordenada de 40 conceptos + orden de TF (§).
- MCPs operativos: TV + MT5 ya están. Agent-browser disponible. Script launch-tv-agent.ps1 ruta corregida.

---

## PENDIENTE — crítico para progresión
- **Validación visual F1-GATE (Sesion-049):** 40 conceptos 1-a-1 aislados, scores ≥90, anti-repaint, perf 20k → desbloquea Fase 2.
- **Heredado enjambre:** 2º mentor, piloto E2E (Vigía+kanban+2mentores+orquestador), playlists NSL, CallMeBot, open-second-brain.

---

## Resumen
Sesión de **INTEGRACIÓN: TV + MT5 como conectores MCP en Claude Desktop.** MCP MT5 instalado (pip metatrader-mcp-server 0.5.1, cuenta DEMO ForexClub $50k). Ambos MCPs conectados en claude_desktop_config.json — GOTCHA CLAVE descubierto: archivo config REAL está en `AppData\Local\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\` (MSIX virtualización), no en AppData\Roaming. Verificación E2E: MT5 get_account_info (balance $50k) + TV chart_get_state (EURUSD 1H) + quote_get (bid/ask reales). Script `launch-tv-agent.ps1` fix: rutas absolutas. Documentación: `docs/CONECTORES-MCP.md` creado (≤40 líneas), CLAUDE.md enlace añadido. **Acuerdo crítico:** próxima sesión = corrida semi-autónoma de validación visual F1-GATE (40 conceptos, MCP apaga/enciende i_show*, extraer datos, smc-validator-agent ≥90, firma usuario, anti-repaint+perf gate). Core Pine intacto. Commit `2ec4be1`.

---

*Sesion-053 = integración MCPs. TV+MT5 operativos. Próxima: validación visual F1-GATE semi-autónoma con MCPs. Validación Pine (049) NOW READY TO START.*
