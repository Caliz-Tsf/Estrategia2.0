# Sesion-126 — 2026-07-14 — Verificación visual de bandas ciegas al lado + hallazgo del ancla de pierna sin piso

## Objetivo sesión
Arrancar por la verificación VISUAL (requisito del usuario en S125) del hallazgo "bandas ciegas al lado" en
D1 OANDA:EURUSD, antes de tocar nada.

## Resultado
F1-GATE SIGUE BLOQUEADA. CORE INTACTO (SHA `752b4083a7db419d`, 1866 líneas, core-sync OK ×3). `pine/` NO se
tocó. SIN ADR nuevo. SIN tag. **Commit único:** `68b7020` chore(scripts) — dos arneses de ablación
(`scripts/gen_probe_mbband.py`, `scripts/gen_probe_legext.py`), no tocan `pine/`.

La verificación visual confirmó el hallazgo de S125, pero además apareció un **hallazgo no buscado y más
grande**: el cálculo de los extremos de pierna sustituye su límite sin piso mínimo, y eso —no el band-pick—
explica por qué zonas cercanas anunciadas por el panel no se dibujan.

## Completado

### Hallazgo 1 — Bandas ciegas al lado: CONFIRMADO EN VIVO
Ya no es lectura de código. Censo D1 modo Operación, precio 1.14215, `total_labels` 74 (en modo "Todo" son
502):
- EQ (cap 2): 2 arriba (EQH 1.14, EQH 1.18) / 0 abajo (ninguna EQL). Ocultos EQ 60.
- Liquidez: 1 arriba (BSL ·3) / 0 abajo (ningún SSL). Ocultos Liq 30.
- Estructura (cap 3): CHoCH+ 1.15, BOS 1.14 ×2. Ocultos Est 339.

La prueba no depende del redondeo a 2 decimales de `data_get_pine_labels`, porque en EQ/Liq el lado va en el
NOMBRE (EQH/EQL, BSL/SSL).

**Control que aísla la causa:** los swings conservan ambos lados (12/12/12/12) y son los únicos que NO pasan
por `f_keepBestPerBand` (usan el top-N por tipo de S125).

**Método:** el modo importa. En "Todo" el recorte no corre (panel "Ocultos Est 0"); solo prueba algo en
Operación. Input Densidad = `in_118` (verificado contando los `input.` en orden).

### Hallazgo 2 — Asimetría entre familias (cierra la tarea "b")
Medido: 10 cajas = 7 MB + 1 OB + 1 BRK + 1 FVG.

Vías de dibujo en Operación:
- OB/FVG/BRK tienen band-pick (celda concepto×lado×banda, 2 slots) y además excluyen mitigadas.
- IDM tiene band-pick.
- MB y BPR se promocionan por confluencia (`mbCfg>=2` / `bprCfg>=2`) SIN cap de banda, lado ni cuota.
- IFVG y GP/OTE solo por `f_densOK`.
- Vacuum exige `f_famOK(FAM_EST)` → imposible en Operación.
- IPR exige `FAM_TODO`.

La familia disciplinada se autolimita; la indisciplinada inunda.

**Corrección registrada:** el band-pick de zonas NO es ciego al concepto ni al lado (sí lo es el de
estructura/EQ, `f_keepBestPerBand`). `f_confDegree` cuenta familias distintas con booleanos y excluye
mitigadas, por lo que los MB NO se auto-refuerzan (sospecha descartada).

### Hallazgo 3 — El gate de banda para MB/BPR: CABE y funciona, pero NO se implementó en pine/
A/B limpio (mismo estado de mercado, verificado porque ambos censos comparten NDOG y T.FVG·g 1.07):
original 75 labels con MB×7 → con gate 69 labels con MB×1. La diferencia son exactamente las 6 MB, nada más
cambió. Compila 0/0 y aplica sin CE10117.

No hay número de tokens: Pine solo reporta el conteo POR ENCIMA del techo (gotcha S121). Solo se sabe "cabe".

La predicción escrita antes de medir ("no cabrá") murió.

### Hallazgo 4 — EL PRINCIPAL, y no se buscaba: el ancla de pierna sustituye sin piso
Extremos de pierna, MEDIDOS con plots (`scripts/gen_probe_legext.py` vía `data_get_study_values`):

| Variable | Valor |
|---|---|
| `probe_close` | 1.14236 |
| `probe_legExtHi` | 1.14730 (coincide exactamente con "Pool cercano D1 1.14730 BSL" del panel) |
| `probe_legExtLo` | 1.13246 (coincide exactamente con pdLow) |
| `probe_pdHigh` | 1.20831 |
| `probe_pdLow` | 1.13246 |

La pierna visible mide 49 pips arriba y 99 abajo, con un rango vigente de 758 pips: el 6% del rango. Bandas
arriba: 1→1.14399, 2→1.14562, 3→1.14730. Todo lo que supere 1.14730 cae en banda 0 = invisible.

**Causa** (`f_computeLegExtremes`, fase 3 "ancla a liquidez", L3175): `hi := anchHi` sustituye
INCONDICIONALMENTE y sin suelo mínimo. La fase 1 fija `hi = pdHigh = 1.20831`; la fase 2 no recorta (clamp
`i_kLeg=3.0` = 1.36991); la fase 3 encuentra que el único pool vivo fuerte dentro de `[px, hi]` es el BSL
1.14730 (el BSL ·3 de 1.51 queda excluido por `p.level <= hi`) y reemplaza 1.20831 por 1.14730.

No es "ancla al más cercano": el bucle sí busca el más lejano dentro de `[px, hi]`, como dice su comentario.
El fallo es sustituir sin piso.

**Asimetría entre lados:** el lado con pool cercano se amputa; el lado sin pool conserva su alcance (por eso
`legExtLo` quedó en `pdLow`). Un solo pool cercano borra un lado entero → incumple el "3 por lado".

**Consecuencia:** explica, mejor que la exclusión de mitigadas, que el FVG cercano [1.15283, 1.15748] y el
OB cercano [1.15726, 1.16221] no dibujen pese a anunciarlos el panel (ambos caen por encima de 1.14730).

**Corolario:** `i_kLeg` es IRRELEVANTE — su clamp nunca actúa. Calibrarlo (tarea #4 pendiente desde
S106/S112) era un callejón sin salida.

La predicción escrita antes de medir (legExtHi≈1.152, legExtLo≈1.10) murió. Van 6 predicciones muertas de 6.

## Gotchas de método nuevos

1. `scripts/pine_inject.py` y `pine_smart_compile` solo hacen "Pine Save" y NO aplican, porque sus
   selectores buscan el botón "Update on chart" en inglés y este TradingView está en español. Guardar NO
   compila. Hay que enfocar Monaco por JS y mandar Ctrl+Enter, y verificar SIEMPRE que la versión del slot
   subió en `pine_list_scripts` antes de creerse una medición. Además, Ctrl+Enter puede crear una instancia
   NUEVA del estudio (`vf6tZu` → `khC0d1`), que arranca con los inputs por defecto y pierde los overrides.
2. `data_get_study_values` lee la leyenda, que sigue al crosshair; para fiarse de un valor hay que comprobar
   que un plot de control (`close`) coincide con el precio real.

## Bug de diseño detectado (no implementado)
En el gate propuesto (y que arrastra también `f_isBandPick`): las zonas que CONTIENEN el precio se
rechazan, porque "above" y "below" son ambos false.

## Nota sobre el tope de 500 labels
El tope de 500 labels de Pine NO aplica en Operación (74 labels). El "`total_labels` 502 ≥ 500" de
S123-S125 es un problema del modo "Todo"; la matriz de auditoría F1 se hace en Operación. El límite real
para estos arreglos es el techo de tokens CE10117 (100256).

## Commits S126
- `68b7020` chore(scripts): F1-S126 arneses de ablación del gate de banda y de los extremos de pierna
  (`gen_probe_mbband.py`, `gen_probe_legext.py`). No tocan `pine/`.

## CORE
- **SHA `752b4083a7db419d`** (1866 líneas) — INTACTO
- core-sync OK ×3 (verificado al cierre)
- `pine/` no se tocó esta sesión → no se re-compiló el repo. Los `pine_check 0/0` de esta sesión son de los
  PROBES (`PROBE-mbband-helper-S126`, `PROBE-legext-S126`), no del Visual del repo.

## Estado
- **F1-GATE BLOQUEADA**
- SIN ADR nuevo
- SIN tag
- Rama `pine/sistema-completo`

## Pendiente S127 (orden sugerido)
1. Arreglar el suelo del anclaje en `f_computeLegExtremes` (cambio de diseño → probablemente ADR). Es el
   bloqueante real de F1-GATE.
2. Política N por (banda × lado) en `f_keepBestPerBand` (estructura/EQ).
3. Implementar el gate de banda de MB/BPR (ya medido: cabe).
4. Zonas que contienen el precio (`f_isBandPick` y el gate).
5. Exclusión de mitigadas del band-pick (elig): Parte A de S108, hecha en Context desde S112/S113 y nunca en
   Visual.
6. Recorte de estructura en Estudio/"Todo".
7. Deudas S123 #2/#3/#4 y auditoría de herencia MTF.

BAJA: `i_kLeg` (tarea #4 histórica) queda DESCARTADA como callejón.

## Enlaces
[[Sesion-125]] · [[Sesion-124]] · [[Sesion-123]] · [[Sesion-122]]
