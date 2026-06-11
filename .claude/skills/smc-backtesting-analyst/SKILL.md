---
name: smc-backtesting-analyst
description: Protocolo de análisis de un run de backtesting - exporta trades del Strategy Tester, delega la estadística al agente smc-backtesting-analyst-agent y gestiona la propuesta de pesos. Usar en Fase 3.
---

# Análisis de run de backtesting

1. Exportar la lista de trades del Strategy Tester (TV MCP) a
   docs/sprint-runs/run-NNN-trades.csv. Verificar columnas: fecha, dir, score,
   confluencias, SL, TP, resultado, R alcanzado.
2. Confirmar el corte IS/OOS vigente (está en docs/scoring-weights-vN.md;
   default: IS = primeros 70% cronológicos).
3. Invocar `smc-backtesting-analyst-agent` con: CSV + pesos vigentes + corte.
4. Procesar veredicto:
   - PROMOVER PESOS → crear docs/scoring-weights-vN+1.md (tabla completa +
     threshold + evidencia), actualizar los inputs default en SMC-Strategy.pine,
     commit `feat(scoring): pesos vN+1`.
   - MÁS DATOS → registrar qué falta y extender el periodo de test.
   - RED FLAG OVERFITTING → NO tocar pesos; sesión con el usuario para
     simplificar el sistema (menos confluencias, threshold más simple).
5. Los pesos NUNCA se editan a mano sin pasar por este protocolo.
