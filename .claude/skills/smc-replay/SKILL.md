---
name: smc-replay
description: Protocolo de replay en TradingView para validar conceptos SMC visualmente en fechas históricas concretas y estudiar señales individuales. Complementa (no reemplaza) al Strategy Tester.
---

# Replay SMC — validación visual

## Modo A — Validar un concepto (Fase 1)
1. Tomar del docs/reglas-smc-ict.md los casos de prueba del concepto (fechas).
2. TV MCP replay → ir a la fecha, avanzar vela a vela hasta el evento.
3. Verificar: el indicador marca el evento al confirmarse la vela correcta
   (ni antes = repaint, ni después), precio y etiqueta correctos.
4. Registrar en docs/sprint-runs/replay-<concepto>-<fecha>.md:
   caso, esperado, observado, veredicto.

## Modo B — Estudiar señales de la Strategy (Fase 3)
1. Elegir N señales del Strategy Tester (mezcla de wins y losses).
2. Replay a cada señal: ¿las confluencias listadas en la señal son visualmente
   reales? ¿el SL/TP quedó donde la regla dice?
3. Registrar cada una en el log de validación:
   {fecha, dir, score, confluencias, sl, tp1, tpExt, resultado, ¿confluencias
   visualmente correctas?, notas}
4. Las discrepancias señal↔visual son BUGS (la Strategy y el Visual comparten
   core — divergencia = core desincronizado o error de scoring). Reportarlas.

## Regla
Avanzar siempre con vela confirmada. Lo que se ve en replay debe ser idéntico a
lo que el indicador habría mostrado en vivo (test anti-repaint).
