# Sesion-127 — 2026-07-14 — El ancla de pierna SNAPEA a liquidez (fix) + las bandas 4/5 son incapaces por construcción

## Objetivo sesión
Arreglar el bloqueante real de F1-GATE dejado por S126: el ancla de pierna sustituía el extremo sin piso
mínimo. Además, censar zonas por (concepto × lado × banda) y revisar el ancla del dealing range.

## Resultado
F1-GATE SIGUE BLOQUEADA. CORE INTACTO (SHA `752b4083a7db419d`, 1866 líneas, core-sync OK ×3). `pine_check`
0/0. Rama `pine/sistema-completo`. SIN ADR nuevo. SIN tag.

## Commits (4)
- `35d6cf2` fix(pine-visual): F1-S127 el ancla de pierna SNAPEA a liquidez, no la sustituye
- `0e2d61a` chore(scripts): F1-S127 arnés de censo de zonas por (concepto x lado x banda)
- `db63811` chore(scripts): F1-S127 censo extendido a los 9 conceptos de SMC_zones + diagnóstico
- `4c4ae26` chore(scripts): F1-S127 arnés de bandas 4/5 + ancla del dealing range

## Completado

### Tarea 1 — Fix del ancla de pierna (pendiente #1 de S126, bloqueante real)
Bug: la fase 3 de `f_computeLegExtremes` hacía `hi := anchHi` de forma incondicional y sin piso.

Hallazgo de diseño clave: la búsqueda del ancla está acotada a `[px, hi]`, así que el ancla SOLO puede
ENCOGER la pierna, nunca extenderla. Eso descarta tanto el arreglo "que solo extienda" (sería código muerto)
como el de "piso mínimo" (pondría el extremo en un precio arbitrario, exactamente el "en el aire" que el
ancla busca evitar).

Fix elegido: SNAP por tolerancia. Nueva constante `LEG_ANCH_TOL_ATR = 1.0` (PROVISIONAL, sin calibrar). El
ancla solo vale si el pool cae a <= `LEG_ANCH_TOL_ATR × ATR` del extremo bruto. Si `atr14` es `na`, la
tolerancia es `na`, la comparación da `false` y se conserva el extremo bruto (fallback seguro).

`f_computeLegExtremes` vive fuera del LIBRARY CORE y solo existe en SMC-Visual.pine: el fix es Visual-only,
no rompe el SHA. Sin ADR (precedente S118/S125: Visual-only bajo ADR-016/ADR-002).

**A/B MEDIDO en vivo** (D1 OANDA:EURUSD, misma sesión de mercado):
- `LEG_ANCH_TOL_ATR = 1e9` (= comportamiento de S126) → `legExtHi` = 1.14730 (bug reproducido).
- `LEG_ANCH_TOL_ATR = 1.0` (fix) → `legExtHi` = 1.20831 (extremo legítimo).

El pool estaba a 11.0×ATR del extremo bruto (0.06101 / `probe_atr14` 0.00555) → rechazado con margen amplio.
`probe_tol` = 0.00555 no-na, así que la comparación SÍ se evaluó (se descartó la sospecha de que el fix
funcionara por accidente, anulando la fase 3 entera).

**Efecto:** la pierna arriba pasó de 49 a 653 pips (de ~6% a ~86% del rango). El censo de Operación D1 pasó
de 10 a 16 cajas. El OB [1.15726, 1.16221] y el FVG [1.15283, 1.15748] que anunciaba el panel desde S126 YA
DIBUJAN. El lado bajo no cambió (`legExtLo = pdLow`, no tenía pool que lo amputara).

Predicción escrita ANTES de medir: se cumplió exacta — primera predicción viva de la serie (van 1 de 8).

### Tarea 2 — Censo medido por (concepto × lado × estado)
Arnés `scripts/gen_probe_censo_lado.py`. D1 OANDA:EURUSD, modo Operación, precio 1.14399 (Discount 14%),
marker 129 verificado. Columnas: viva_arriba / viva_abajo / fuera_arriba / fuera_abajo / mitig_arriba /
mitig_abajo:

| Concepto | viva↑ | viva↓ | fuera↑ | fuera↓ | mitig↑ | mitig↓ |
|---|---|---|---|---|---|---|
| OB | 3 | 0 | 13 | 5 | 1 | 0 |
| FVG | 3 | 0 | 15 | 11 | 0 | 0 |
| BRK | 1 | 0 | 10 | 1 | 0 | 0 |
| IFVG | 3 | 0 | 4 | 3 | 2 | 0 |
| BPR | 0 | 0 | 0 | 0 | 0 | 0 |
| MB | 1 | 1 | 7 | 5 | 0 | 0 |
| OTE | 1 | 0 | 0 | 0 | 0 | 0 |
| GP | 1 | 0 | 0 | 0 | 0 | 0 |
| VAC | 0 | 0 | 0 | 0 | 1 | 0 |

Zonas que contienen el precio: 0 (el bug de diseño detectado en S126 no muerde en este estado).

**REFUTA la hipótesis del cap** (era de Claude, no del usuario): los BRK no los esconde el cap de 2 — solo
hay 1 vivo arriba, 0 abajo. Subir el cap no habría dibujado nada. Tampoco es por mitigadas (`mit_abajo` = 0
en todo el censo).

**Dónde muere cada concepto** (leído en código, no observado en pantalla):
- OB/FVG/BRK/IDM → band-pick de 2 slots por (concepto×lado×banda); `elig` excluye ZS_INVALID y
  ZS_MITIGATED.
- IFVG → solo pasa por `f_densOK` (en Operación exige strength nivel 2), sin banda, lado ni cap: 3 vivos
  arriba y ninguno dibuja.
- BPR → `(f_famOK(FAM_EST) and f_densOK(...)) or bprCfg>=2`; en Operación `f_famOK(FAM_EST)` es false.
- MB → se promociona por confluencia sin cap e IGNORANDO la banda.

El usuario CONFIRMÓ que el concepto que echa en falta es IFVG (no BPR).

### Tarea 3 — Hallazgo principal: las bandas 4/5 son INCAPACES POR CONSTRUCCIÓN
Arnés `scripts/gen_probe_bandas45.py`. MEDIDO (marker 145, close 1.14336):
- `pdPrev1Hi/Lo` = 1.20831 / 1.13757
- `pdPrev2Hi/Lo` = 1.20831 / 1.14110
- `pdHigh/pdLow` = 1.20831 / 1.13246
- `structMajor_high/low` = 1.20831 / 1.14110
- `legExtHi/Lo` = 1.20831 / 1.13246

La sospecha "pdPrev está na → el código está dormido" es FALSA: sí se puebla.

Los dos rangos archivados están ANIDADOS DENTRO del rango actual → `f_depthBand` solo da banda 4/5 si el
nivel cae dentro de esos rangos archivados → todo lo que cubren ya era banda 1-3, y lo que está bajo
`pdLow` sigue en banda 0.

Es ESTRUCTURAL: la rotación archiva fotos de `pdHigh`/`pdLow`, que entre reanclajes SOLO expanden (trailing
extremes) → una foto vieja de un rango que solo crece es SIEMPRE un subconjunto del rango actual.
`i_profundidad` 4/5 NO PUEDE funcionar nunca tal como está implementado.

**Consecuencia:** hoy no existe mecanismo alguno para ver por debajo de `pdLow`. Ni caps, ni gates, ni
`i_profundidad`. El requisito del usuario ("del alto más alto al bajo más bajo, 2-3 conceptos por lado con
todas sus variantes") no es alcanzable sin rediseño. El censo midió que ahí abajo hay 5 OB + 11 FVG + 1 BRK
+ 3 IFVG vivos e invisibles.

### Tarea 4 — Hueco doctrina/implementación en el dealing range (duda del usuario, registrada desde S102
como "Opción B ancla estructural", diferida a Fase 3)
- Doctrina §2.3: rango = [strong low, strong high] "vigentes", "se actualiza con la estructura".
- Implementación: reancla SOLO al confirmarse un swing de escala `i_pdSwingLen` (default 50); el resto del
  tiempo `f_updateTrailing` solo EXPANDE, nunca contrae.
- Medido: `structMajor_low` = 1.14110 pero `pdLow` = 1.13246 → el rango se expandió POR DEBAJO del suelo
  estructural.
- NO RESUELTO: ambos anclajes coinciden en que el precio está en discount (3.4% del swing dominante / 14.4%
  del rango) → el anclaje no explica por sí solo la objeción del usuario ("no creo que sea discount porque
  el precio viene de swing alcista → consolidación → manipulación → rompiendo bajista").

## Gotchas de método nuevos

1. `mcp__tradingview__pine_get_console` SÍ muestra el CE10117 con número exacto: "Compiled code contains too
   many tokens: 100335. The limit is 100256" (Visual + probe sin truncar se pasa por 79). Es el primer
   número real del Visual en 5 sesiones. `pine_get_errors` NO lo ve: lee markers de Monaco (compilación), no
   errores de runtime del estudio — devolvía `error_count` 0 con el estudio en rojo y sin emitir valores.
2. El chart va 1-2 builds POR DETRÁS y `data_get_study_values` devuelve lecturas RANCIAS sin avisar. Casi
   invierte la conclusión del fix (se leyó la ablación como si no cambiara nada). Antídoto: añadir un plot
   NUEVO por build como marcador de identidad; `pine_list_scripts` no basta. Apply real: 60-90s, no 35.
3. Un probe que añada código ENCIMA del Visual completo NO CABE (CE10117). Solución: truncar el render en
   "// === DIBUJO ===" (libera ~1600 líneas / ~115KB); el censo no necesita dibujar. Contrapartida: el chart
   queda EN BLANCO mientras el probe está aplicado (esperado, no un fallo).
4. Ctrl+Enter crea instancia nueva y pierde los overrides de inputs (hay que re-aplicar Densidad `in_118`
   tras cada apply). Verificado: `in_118` = `i_densidad`, `in_119` = `i_profundidad`.
5. El editor recarga el slot encima de la inyección si TV se acaba de relanzar → verificar el contenido del
   editor antes de aplicar.

## Commits S127
- `35d6cf2` fix(pine-visual): F1-S127 el ancla de pierna SNAPEA a liquidez, no la sustituye
- `0e2d61a` chore(scripts): F1-S127 arnés de censo de zonas por (concepto x lado x banda)
- `db63811` chore(scripts): F1-S127 censo extendido a los 9 conceptos de SMC_zones + diagnóstico
- `4c4ae26` chore(scripts): F1-S127 arnés de bandas 4/5 + ancla del dealing range

## CORE
- **SHA `752b4083a7db419d`** (1866 líneas) — INTACTO
- core-sync OK ×3
- `pine_check` 0/0

## Estado
- **F1-GATE BLOQUEADA**
- SIN ADR nuevo
- SIN tag
- Rama `pine/sistema-completo`

## Pendiente S128 (orden recomendado, el orden importa)
1. El ancla del dealing range (Opción B estructural) — define la geometría de la que depende todo lo demás;
   arreglar el alcance antes que esto arriesga construir sobre un rango equivocado. Requiere ADR.
2. El alcance bajo `pdLow` (bandas 4/5 rotas por construcción) — bloquea el requisito literal del usuario.
   Requiere rediseño + ADR.
3. IFVG: darle disciplina por banda/lado (hoy solo `f_densOK`; 3 vivos arriba sin dibujar).
4. MB/BPR: gate de banda (ya medido en S126 que cabe; MB hoy ignora la banda por completo).
5. Calibrar `LEG_ANCH_TOL_ATR` (provisional en 1.0; el A/B de S127 no discrimina su valor porque el pool
   estaba a 11×ATR).
6. `elig` excluye ZS_MITIGATED del band-pick en Visual (Parte A de S108, hecha en Context desde S112/S113).
7. Deudas S123 #2/#3/#4 y auditoría de herencia MTF.
8. DESCARTADO definitivamente: calibrar `i_kLeg` (su clamp nunca actúa).

## Enlaces
[[Sesion-126]] · [[Sesion-125]] · [[Sesion-124]] · [[Sesion-123]]
