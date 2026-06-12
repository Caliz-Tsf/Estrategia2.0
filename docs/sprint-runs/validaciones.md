# Registro de validaciones — smc-validator-agent

> Score por concepto contra `docs/reglas-smc-ict.md`. Gate de aprobación ≥90.
> Lo genera el ciclo de `smc-validator` (skill) en cada tarea de implementación.

| Fecha | Tarea | Concepto | Archivo | Score | Veredicto | Notas |
|---|---|---|---|---|---|---|
| 2026-06-11 | F1-S1.1-T02 | Swing High/Low (`f_detectSwings`) + clasificación HH/HL/LH/LL (`f_classifySwing`) | SMC-Visual.pine | **97/100** | ✅ APROBADO | §1.1/§1.2. 4 casos canónicos confirmados vs OHLCV real (1.16494, 1.16859, 1.14997, secuencia giro 06-08 LL→HH→HL→HH) + contraejemplo. Única observación menor no bloqueante: edge case pivote high+low en mismo bar (imposible con swingLen=5 en H1). Sin correcciones requeridas. |

## Detalle F1-S1.1-T02 (2026-06-11)

- **Evidencia:** `screenshots/t02-swings-eurusd-h1.png` (overview, 100 swings cap), `t02-val-jun08-secuencia.png` (giro 06-08), `t02-val-may27-29-highs.png` (highs 27-29 may).
- **Checklist OK:** detección pivote simétrico estricto (`ta.pivothigh/low(5,5)` = def. §1.1), anti-repaint (`barstate.isconfirmed and not na`), anclaje en vela t (`bar_index-len`, `time[len]`), clasificación contra swing previo del mismo tipo, manejo de empates (hereda kind → candidato EQH/EQL), colores/posición labels (teal HH/HL arriba, rojo LH/LL abajo).
- **CORE sync:** OK (137 líneas, SHA `81cc892d`). Compila 0/0 en Visual, Strategy y Library.
