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
},
"claude-video-vision": {                  // npm -g claude-video-vision (Jordan Vasconcelos), v1.2.1
  "command": "C:\\Program Files\\nodejs\\node.exe",
  "args": ["C:\\Users\\Fredd\\AppData\\Roaming\\npm\\node_modules\\claude-video-vision\\dist\\index.js"]
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

## Conector `claude-video-vision` (S058)
Agregado para resolver el problema de Boxxocode: ese canal (toolbox EA/MT5) no habla nunca —
son screencasts mudos con música de fondo, el pipeline whisper de `process-channel.ps1` no tiene
nada que transcribir. `claude-video-vision` (npm global, `jordanrendric/claude-video-vision`)
extrae frames vía ffmpeg y los describe con Claude mismo (`frame_describer_model: "sonnet"`,
sin API key extra) — permite leer pantalla (código fxDreema, configuración de EA Builder,
parámetros de backtest) en vez de depender del audio.

**Backends evaluados** (solo importa la transcripción de audio; los frames siempre los describe
Claude): `local` = whisper.cpp/whisper Python, 100% local y gratis. `openai`/`gemini` = APIs reales
en la nube, requieren `OPENAI_API_KEY`/`GEMINI_API_KEY` — **no aceptan endpoint propio**, por lo
que los modelos locales del enjambre (hermes3, MiMo vía Ollama) no sirven como backend aunque
expongan API compatible con OpenAI. Recomendado: `backend: "local"` (default de fábrica, cero costo).

**Estado:** agregado a `mcpServers` en `claude_desktop_config.json`. Pendiente:
1. Reiniciar Claude Desktop completo (icono bandeja → Salir → reabrir) para que cargue el servidor.
2. Primera vez, correr `video-configure`/`video-setup` para fijar `backend: "local"`.
3. Tras eso, reintentar `COMANDOS-boxxocode.md` ya con visión de frames disponible.

**Tool MCP alternativa evaluada (no agregada):** `agent-browser` (vercel-labs, ya instalado global
para `tv_launch`/CDP) también puede correr como servidor MCP (`agent-browser mcp`) y daría
screenshots anotados con refs clickeables — útil como respaldo de navegación/scraping general,
pero no aporta nada nuevo para TV (ahí manda el conector dedicado `tv_launch`). Queda como opción
futura, no urgente.

## Pendientes (S058)
1. **MT5 se abre solo al abrir Claude Desktop — investigar.** Hoy el terminal de MetaTrader 5
   se lanza automáticamente cada vez que se abre Claude Desktop, junto con la app, en vez de
   abrirse solo cuando Claude invoca una tool del conector `metatrader`. Sospecha: Claude
   Desktop arranca **todos** los `mcpServers` configurados (stdio) al iniciar la app —no es
   lazy por tool-call—, y `metatrader-mcp-server.exe` probablemente abre la terminal MT5 como
   efecto secundario de inicializar la conexión Python `MetaTrader5` ya en su arranque (no al
   primer `get_account_info`). Falta confirmar leyendo el código/comportamiento de
   `metatrader-mcp-server` (paquete `ariadng`) y decidir si se puede diferir el lanzamiento de
   la terminal hasta el primer request real.
