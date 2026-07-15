# Sesión 130 — 2026-07-15

## Título
FASE 1 · F1-GATE BLOQUEADA — EL RANGO VA DE POOL A POOL; Y NO ERA EL ANCLA, ERA LA ESCALA

## Objetivo
Decisión del usuario al arrancar (respuesta a la §3 ambigua de S128/S129): de las 4 opciones planteadas eligió "ventana declarada en D1 + herencia". Al explicarle que la herencia pura congela el veredicto en H1/M5, el usuario planteó el requisito real: el rango D1 es contexto, no señal; si el precio tardó 18 meses en llegar al discount de D1 el veredicto dura años y no es operable; los TF menores necesitan un P/D que rote.

## Estado del repo
- Rama `pine/sistema-completo`.
- CORE SHA `752b4083a7db419d` (1866 líneas) INTACTO.
- core-sync OK ×3.
- pine_check 0/0 en Visual y Strategy.
- SIN ADR. SIN tag. F1-GATE sigue BLOQUEADA.

## Completado

### Commits (3)
- `364d63d` chore(scripts): diseño + probe de la cascada P/D anidada (solo docs+scripts)
- `500dffa` chore(scripts): P-G1 refutada, 5 símbolos (solo docs+scripts)
- `61dcc36` fix(pine-pd): i_pdSwingLen 50 -> 1000 (toca `pine/SMC-Visual.pine` L95 y `pine/SMC-Strategy.pine` L35, ambos FUERA del CORE que empieza en L146)

### Archivos nuevos
- `docs/planes/DISENO-cascada-pd-anidada-S130.md`
- `scripts/gen_probe_cascada_pd.py`
- `scripts/gen_probe_ratio_tf.py`

### Tarea 1 — cascada P/D anidada (probe v5, marker 1301, D1 OANDA:EURUSD n=6283)
Regla medida: Lk+1 = la mitad de Lk donde vive el precio.
- P-G1 (la que decidía) VERDE en su momento: L1 = [0.90275, 1.25332] = 3505.675 pips vs 3780 leídos por el usuario en H1 = 7.3% de error; niveles desplazados 1190 y 1464 pips.
- LA CASCADA ROTA (medido): pctL0 = 0.344 (DISCOUNT de D1) y pctL1 = 0.689 (PREMIUM del nivel 1) simultáneamente. Contraste: Opción A vigente pctA = 0.155 congelado.
- P-G4 VIVA: flapping monótono nFlip1=36 / nFlip3=390 / nFlip5=1536 (L5 salta cada ~4 velas) = el modo de fallo.
- P-G2 (nNestViol=0) y las amplitudes de P-G5 (L2 1752.84 / L3 876.42 / L4 438.21 / L5 219.10 / L6 109.55) salieron verdes pero son TAUTOLÓGICAS (por construcción).
- Identidad binaria verificada por otra vía: pctL1 = 2 × pctL0 exacto. errBin NO medido (es local, queda na en la barra viva).
- Hallazgo NO predicho: pct NO se conserva en [0,1] INTRABARRA en niveles bajos (pctL5 = 1.02 en la vela viva); sobre confirmadas nOutRange = 0.

### Tarea 2 — discriminación de P-G1 (probe v6, marker 1302, 5 símbolos, D1 n≈5623-6284 / H1 n≈9036-9537)
ratio ampH1/ampD1: EURUSD 0.272 · GBPUSD 0.164 · USDJPY 0.263 · AUDUSD 0.235 · NAS100USD 0.485
- P-H2 (la que decidía) FALSA: recorrido 0.321 > 0.20 → los ratios NO se agrupan → no existe constante "H1 = tal fracción de D1" → P-G1 REFUTADA, el 7.3% fue CASUALIDAD.
- P-H3 FALSA: NAS100USD 0.485 cae en 0.5 ± 0.05.
- P-H4 FALSA CON EL SIGNO INVERTIDO: se predijo NAS100 el ratio más BAJO, salió el más ALTO.
- P-H1 VIVA pero fácil: 0.2717 vs 0.27 (aritmética sobre un número ya medido en S129; el 1905.2 salió idéntico por otra vía → valida el método).

### Tarea 3 — HALLAZGO PRINCIPAL: no era el ancla, era la escala
S128 y S129 gastaron 2 sesiones discutiendo cambiar el ancla (Opción B/C), romper el SHA, la paridad LuxAlgo y rederivar §2.3. No hacía falta: con `i_pdSwingLen=50` se le pedía a D1 el rango de 50 velas (~2.5 meses).

Barrido MEDIDO en vivo del input, sin tocar código:
- 50 → [1.13246, 1.20831] 758 pips, Discount 15%
- 150 → [1.01779, 1.20831] 1905 pips, Premium 66%
- 400 → [0.95360, 1.23496] 2814 pips
- 1000 → [0.95360, 1.60389] 6503 pips, Discount 29% ← el rango del usuario

CLAVE: [0.95360, 1.60389] NO es el min/max de la ventana ([0.90275, 1.60389]): el suelo difiere 508 pips → 0.95360 es un PIVOTE real de 2022 → sigue siendo estructural (§2.3) y Opción A (paridad LuxAlgo intacta). Con 758 pips el rango D1 era MENOR que el nativo de H1 (1905) → de ahí la falsa "jerarquía invertida" de S128.

Con len=1000 los 3 TF rotan y alternan: D1 Discount 29% / H1 Discount 19% / M5 Premium 68%.

Predicción de Claude ("crecerá pero no lo suficiente; a esa escala ya no es un pivote sino el min/max de todo") MURIÓ EN SUS DOS MITADES.

### Tarea 4 — la regla correcta (modelo del usuario, doc §9): el rango va de pool a pool
El escalón lo pone la ESTRUCTURA (pool/pivote), no la aritmética. La cascada de mitades era la versión mala de esto.

Cómo se destapó: el usuario marcó el suelo de H1 en 1.01854 = el `SSL -3` (pool sell-side de 3 toques que dibuja el propio sistema) y el techo en 1.39972 — en S128 había dicho 1.39970. CLAVADO, no aproximado: leía POOLS con precisión mientras se medían pivotes de lookback y mitades.

Y 1.39972 está POR ENCIMA del techo del feed H1 (1.20831) → ese pool VIVE EN D1 → la liquidez no pertenece a una temporalidad → herencia de pools. Explica por qué ninguna medición nativa de H1 podía coincidir con él jamás.

La regla:
1. El rango de cada TF va de pool/pivote a pool/pivote a su escala; H1 busca el SIGUIENTE pivote/pool DENTRO del rango de D1, M5 dentro del de H1 → el anidamiento sale solo.
2. El rango NO se mueve porque aparezca un pivote nuevo: se mueve cuando el precio CONSUME el extremo → salta al siguiente pool.
3. Cascada de rupturas: se come el premium de M5 → salta; se come el de H1 → salta; puede que nunca llegue al de D1, pero llega a un pool donde retrocede y ese pool es el nuevo premium de H1.

Explica el fracaso de la Opción C (S129): la idea era correcta (el extremo se queda hasta ser violado); el fallo fue que al violarse reanclaba a un pivote de `i_pdSwingLen` (arbitrario) en vez de al siguiente pool. Error de implementación, no del usuario.

## Lo que queda sin resolver
H1 y M5 siguen con la regla vieja. H1 quedó en [1.13246, 1.18492] (525 pips, 41 días) — anidado dentro de D1 y rotando, pero NO donde debe estar según el criterio de pools del usuario.

## Gotchas nuevos
- `i_pdSwingLen >= ~4000` revienta con RE10008 (max_bars_back) → techo entre 1000 y 4000, sin calibrar. Con 4000 el estudio deja de dibujar del todo.
- El mismo `i_pdSwingLen` va a los 3 `request.security` (D/60/5) → en H1 son 41 días y en M5 3.5 días. `f_computeTFState(swingLen, pdLen, ...)` YA recibe el `pdLen` como parámetro y los call-sites (:2970/:2971/:2976) están FUERA del CORE → un len por TF costaría 2 inputs, sin ADR.
- Mapeo de inputs verificado contando `input.` en orden: `i_pdSwingLen` = in_69, `i_densidad` = in_118 (coincide con la memoria previa → valida el mapeo).
- `indicator_set_inputs` puede provocar que el chart revierta al layout guardado (volvió de H1 a D1 solo).
- `pine_inject.py` falla en silencio si el editor Pine no está abierto: hay que llamar `pine_open` ANTES (tras relanzar TV el inject "guardó" pero la versión del slot no subió).
- El panel ya muestra P/D por TF: `f_pdCell(d1State.pdHigh, d1State.pdLow)` :4862, `h1State` :4863, `m5State` :4873. `request.security` a TF menores NO está roto (los eventos por TF tienen escalas de tiempo coherentes: BOS D1 17-06, H1 13-07, M5 15-07).
- El error de runtime del estudio NO sale en `pine_get_console` (que lee el editor): se lee del atributo `title` del icono de la barra del estudio ("Error de ejecución: RE10008").
- RECONFIRMADO: apply real = `pine_inject` (guarda) + 1er Ctrl+Enter (guarda) + 2º Ctrl+Enter (aplica, "Compilado." + "Añadido al gráfico"). Cada apply crea instancia NUEVA → remover la vieja con `chart_manage_indicator`.

## Predicciones
Van 15 vivas de 32.

## Pendiente / Siguiente (S131) — orden sugerido
1. La regla de pools (doc §9). MEDIR antes de implementar: (a) qué fuerza mínima debe tener un pool para anclar un extremo; (b) qué pasa cuando NO hay pool a un lado (= el censo de S127 midió el lado de abajo vacío); (c) si el anidamiento D1⊇H1⊇M5 se sostiene; (d) qué pools se heredan y cuáles no.
2. Un `i_pdSwingLen` por TF (2 inputs, fuera del CORE) si la regla de pools no lo sustituye.
3. NO volver a proponer la cascada de mitades ni "medir el mapeo nivel→TF": ambos REFUTADOS en esta sesión.
4. Pendientes de F1-GATE que siguen abiertas: IFVG por banda/lado, gate de banda MB/BPR, `elig` excluye ZS_MITIGATED del band-pick en Visual, calibrar `LEG_ANCH_TOL_ATR`, deudas S123 #2/#3/#4, auditoría de herencia MTF.

## Enlaces
[[Sesion-130]] · [[Sesion-129]] · [[Sesion-128]] · [[Sesion-127]]
