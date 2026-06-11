---
name: smc-chart-analysis
description: Lee el estado SMC actual de EURUSD desde TradingView - bias por TF, confluencias activas, zonas Premium/Discount, Kill Zone vigente. Usar para análisis de mercado o verificación del panel.
---

# Análisis de chart SMC EURUSD

## Protocolo
1. TV MCP: verificar salud (tv_health_check). Si falla → reportar y detener.
2. Cargar EURUSD con el indicador SMC-Visual en H1. Screenshot.
3. Leer el panel de estado: bias D1/H1/M5, último BOS/CHoCH/MSS por TF, OB/FVG
   activos más cercanos, pool más cercano, sweep reciente, Kill Zone, EMAs, P/D.
4. Repetir screenshot en M5 si la sesión es de entrada (Kill Zone activa).
5. Contrastar lo que muestra el panel con lo visible en el chart — discrepancia
   = bug de panel, reportar como hallazgo.

## Formato de salida
# Análisis EURUSD — <fecha hora GMT>
| Dato | D1 | H1 | M5 |  (bias, estructura, zonas, liquidez)
**Lectura SMC:** <2-4 frases: dónde está el precio respecto a la liquidez y zonas,
qué confluencias están activas en cada dirección>
**Kill Zone:** <activa/próxima>
NOTA: esto es lectura del indicador, NO recomendación de operar.
