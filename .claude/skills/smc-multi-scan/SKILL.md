---
name: smc-multi-scan
description: Escanea el estado SMC de múltiples pares Forex. BLOQUEADA hasta que la Fase 3 esté completada y validada en EURUSD - verificar memory/ESTADO-ACTUAL.md antes de ejecutar.
---

# Multi-scan SMC

## Guard obligatorio
1. Leer memory/ESTADO-ACTUAL.md. Si Fase 3 no está marcada COMPLETADA →
   responder: "Bloqueada: el sistema solo está validado en EURUSD (fase actual:
   <X>). Expansión multi-par es posterior a Fase 3." y DETENER.

## Protocolo (post-Fase 3)
1. Watchlist: GBPUSD, USDJPY, AUDUSD, USDCAD (orden de prueba definido en plan).
2. Por par: cargar SMC-Visual H1 → leer panel → registrar bias, confluencias
   activas, Kill Zone.
3. Salida: tabla comparativa por par + diferencias de comportamiento observadas
   vs EURUSD (volatilidad de detecciones, densidad de señales) → input para
   decidir ajustes de parámetros por par.
