# Registro de validaciones — smc-validator-agent

> Score por concepto contra `docs/reglas-smc-ict.md`. Gate de aprobación ≥90.
> Lo genera el ciclo de `smc-validator` (skill) en cada tarea de implementación.

| Fecha | Tarea | Concepto | Archivo | Score | Veredicto | Notas |
|---|---|---|---|---|---|---|
| 2026-06-11 | F1-S1.1-T02 | Swing High/Low (`f_detectSwings`) + clasificación HH/HL/LH/LL (`f_classifySwing`) | SMC-Visual.pine | **97/100** | ✅ APROBADO | §1.1/§1.2. 4 casos canónicos confirmados vs OHLCV real (1.16494, 1.16859, 1.14997, secuencia giro 06-08 LL→HH→HL→HH) + contraejemplo. Única observación menor no bloqueante: edge case pivote high+low en mismo bar (imposible con swingLen=5 en H1). Sin correcciones requeridas. |
| 2026-06-12 | F1-S1.1-T03 | BOS (`f_detectBOS`) + CHoCH + modelo de bias estructural (`SMC_Structure`, `f_setStructureHigh/Low`, `f_detectStructure`) | SMC-Visual.pine | **97/100** | ✅ APROBADO | §1.3/§1.4 + modelo de bias. 12/12 eventos swing del oráculo `ver05/detect.py` presentes; 4 casos canónicos confirmados (CHoCH baj 06-01 13:00 [MSS], BOS baj 06-05 12:00, CHoCH alc 05-27 06:00, CHoCH alc 05-29 14:00) + contraejemplo wick-no-BOS 05-27 12:00 (high 1.16615 supera nivel pero close 1.16440 no rompe → correctamente ausente). Ruptura por cierre estricto, anti-repaint, distinción BOS/CHoCH por bias, escala swing+interna separadas. Sin correcciones requeridas. |

## Detalle F1-S1.1-T02 (2026-06-11)

- **Evidencia:** `screenshots/t02-swings-eurusd-h1.png` (overview, 100 swings cap), `t02-val-jun08-secuencia.png` (giro 06-08), `t02-val-may27-29-highs.png` (highs 27-29 may).
- **Checklist OK:** detección pivote simétrico estricto (`ta.pivothigh/low(5,5)` = def. §1.1), anti-repaint (`barstate.isconfirmed and not na`), anclaje en vela t (`bar_index-len`, `time[len]`), clasificación contra swing previo del mismo tipo, manejo de empates (hereda kind → candidato EQH/EQL), colores/posición labels (teal HH/HL arriba, rojo LH/LL abajo).
- **CORE sync:** OK (137 líneas, SHA `81cc892d`). Compila 0/0 en Visual, Strategy y Library.

## Detalle F1-S1.1-T03 (2026-06-12)

- **Evidencia:** `screenshots/t03-bos-choch-direccional.png` (ventana completa 05-26→06-12, etiquetas direccionales), `t03-zoom-0601-0608-mss-bos.png` (zoom cadena bajista CHoCH→BOS×3 + giro alcista CHoCH→BOS).
- **Desglose de puntuación:** ruptura por cierre estricto 25/25 · distinción BOS/CHoCH por bias 25/25 · anti-repaint 15/15 · 12/12 eventos oráculo presentes 19/20 · contraejemplo wick correctamente ausente 10/10 · core sync 3/5. (−3: lectura de precios exactos vía screenshot, no coordenadas numéricas; core sync verifica el bloque CORE no el archivo completo — comportamiento correcto.)
- **Checklist OK:** `close > highLevel`/`close < lowLevel` estricto (no mecha), `tag = bias==BEAR?CHoCH:BOS`, flag `crossed` anti-redisparo, `structSwing`/`structInternal` separados (ruptura interna no voltea bias swing §1.4), guard nivel-distinto interno (LuxAlgo `extraCondition`), `barstate.isconfirmed`, dibujo direccional (alcista teal arriba / bajista rojo debajo, etiqueta centrada pivote→ruptura).
- **Paridad ver05 (ADR-002):** `f_detectStructure` equivalente línea-a-línea a `run_structure` del oráculo (`close>nivel` + `topBroken/btmBroken` ↔ flag `crossed` + `bias`).
- **CORE sync:** OK (207 líneas, SHA `a742779738bee0f2`). Compila 0/0 en Visual, Strategy y Library.
