# Conectores MCP en Claude Desktop
> Cómo quedaron montados TradingView y MetaTrader 5 como conectores de Escritorio. S053.

## Dónde vive el config (gotcha)
Claude Desktop es la **versión del Microsoft Store (MSIX)**, paquete `Claude_pzs8sxrjxfjjc`.
Su `claude_desktop_config.json` **NO** está en `AppData\Roaming\Claude` (no aparece en el Explorador
por la virtualización MSIX), sino en:
```
C:\Users\Fredd\AppData\Local\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\claude_desktop_config.json
```
Atajo para abrirlo: en la app → **Configuración → Desarrollador → Editar configuración**.
Tras editar → **reiniciar Claude Desktop completo** (clic derecho icono bandeja → Salir) para recargar.

## Bloque `mcpServers`
```jsonc
"tradingview": {                          // sin credenciales — se engancha al TV Desktop por CDP 9222
  "command": "C:\\Program Files\\nodejs\\node.exe",
  "args": ["D:\\CODE\\BOT\\Bot\\tradingview-mcp-jackson\\src\\server.js"],
  "cwd":  "D:\\CODE\\BOT\\Bot\\tradingview-mcp-jackson"
},
"metatrader": {                           // pip install metatrader-mcp-server (paquete ariadng)
  "command": "C:\\Users\\Fredd\\AppData\\Roaming\\Python\\Python314\\Scripts\\metatrader-mcp-server.exe",
  "args": ["--login","<CUENTA>","--password","<PASS>","--server","<SERVIDOR>","--transport","stdio"]
}
```
Cuenta actual = **demo ForexClub** ($50k, leverage 1000). Password en texto plano → si algún día es
cuenta real, migrar a variable de entorno.

## Cómo lanzarlos
- **TradingView** necesita CDP activo. Vía MCP: herramienta `tv_launch` (lo levanta solo).
  Vía script: `powershell -ExecutionPolicy Bypass -File "D:\CODE\Estrategia2.0\scripts\launch-tv-agent.ps1"`
  (usar ruta absoluta; el `.\` solo funciona parado en `D:\CODE\Estrategia2.0`). agent-browser ya global.
- **MetaTrader 5**: tener la terminal abierta + *Herramientas → Opciones → Asesores Expertos →
  Permitir trading algorítmico*. El puente abre sesión con login/password/server.

## Verificación rápida
- TV: `tv_health_check` / `chart_get_state` → debe devolver símbolo + estudios.
- MT5: `get_account_info` / `get_symbol_price EURUSD` → balance y bid/ask en vivo.
