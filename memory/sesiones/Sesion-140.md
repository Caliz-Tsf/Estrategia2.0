# Sesión 140 — 2026-07-20

## Objetivo con el que arrancó
Terminar las variantes de la familia OB en su TF nativo (D1 EURUSD) + revisar su
comportamiento entre sí. Regla de orden vigente (S139): verificar concepto × TF nativo
ANTES de herencias.

## Rama
`pine/sistema-completo`

## Qué se tocó
CORE intacto todo el tiempo: LIBRARY CORE SHA `9559a0d7fe58b213` (1776 líneas), EXTREMES
CORE SHA `5f851d87e5fda720` (148 líneas). check-core-sync OK ×3. Sin tag (F1-GATE sigue sin
firmar). Todos los cambios en la capa de dibujo del Visual (`pine/SMC-Visual.pine`), fuera
del CORE.

## Commits (4)
- `590a209` feat(pine-visual) — atenuado de Breaker por antigüedad — paridad con OB.
- `9cd99ce` feat(pine-visual) — atenuado de Mitigation Block por antigüedad — paridad
  OB/Breaker.
- `2735d4b` feat(pine-visual) — atenuado de Vacuum por antigüedad — familia de bloques
  completa.
- `b8654b4` feat(pine-visual) — curación de labels de la familia OB — anti-solape
  cross-family + atenuado de labels por edad.

## Método
Vistas AISLADAS por concepto vía `indicator_set_inputs` (apagar todos los toggles menos
uno), censo con `data_get_pine_boxes`/`data_get_pine_labels`, screenshot, y al final vista
COMBINADA de la familia. Densidad en "Todo" para censo completo.

## Breaker (§2.6)
13 vivos (11 BRK↓ resistencia, 2 BRK↑ soporte). Render OK (borde punteado, familia color,
label BRK↑/↓). Defecto: viejos cruzaban el gráfico (`f_drawBreaker` no tenía el atenuado
por edad de S139). FIX: helper nuevo `f_ageDim` (DRY, reusable) aplicado a `f_drawBreaker`.

**Gotcha medido:** el censo inicial con TODO encendido dio "0 breakers" (falso) — artefacto
del censo mixto (OB tapaba la lista de boxes/labels); el aislamiento reveló los 13.

## Mitigation Block (§2.8 #24)
14 vivos. Render OK (borde punteado + label MB). Mismo defecto de antigüedad. FIX:
`f_ageDim` en `f_drawMB`.

**Observación del usuario + respuesta:** asimetría 5 MB soporte fuertes abajo vs 1
resistencia fuerte arriba. Es coherente, NO bug: "fuerte" = reciente (age-dim) y el precio
reciente clusteró soportes abajo; el bias D1 es bajista; no se fuerza simetría por lado
(doctrina strong/weak sigue al BIAS, no al lado — S133). El instinto del usuario apunta al
defecto real ya anotado en S139: age sola es discriminador tosco, falta reactivación por
relevancia/proximidad.

## Vacuum (§5.7)
Solo 1 vivo en D1 (VAC@1.18, reciente) — raros en D1 Forex (gaps de apertura ≥factor×ATR).
Render OK. FIX aplicado por PARIDAD (`f_ageDim` en el dibujo inline del Vacuum) aunque en
D1 no cambia nada visible; su valor es en TFs bajos (M5/M15) donde los vacuums se acumulan.

## Propulsion (§5.8)
3 vivos (label OB⇈). Ya revisado, marca correcta, sin cambios.

## Comportamiento entre sí (vista combinada OB+Breaker+MB+Vacuum)
Los CUADROS apilados = confluencia real y deseable (se conserva). Pero los NOMBRES se
pisaban ENTRE familias: el anti-solape S120 (`f_ySlot`) llevaba la cuenta de ranuras-Y POR
FAMILIA separada (`obSeenY`/`brkSeenY`/`mbSeenY`/`vacSeenY`) → cada familia creía la ranura
libre. Casos confirmados por el usuario con zoom: OB+MB co-ubicados, OB (tocado no
mitigado)+VAC, versión alcista.

**FIX 1:** acumulador `blockSeenY` COMPARTIDO top-level (resetea cada barra, prioridad de
orden de dibujo OB>Breaker>MB>Vacuum: el 1.º conserva el nombre, el resto cede, el cuadro
sigue). Elimina las 4 declaraciones locales. SOLO la familia OB (la familia FVG — FVG/IFVG/
BPR — mantiene sus SeenY aparte).

**FIX 2:** el usuario notó que arriba los labels viejos seguían brillando sobre cajas
fantasma y con scatter izquierda/derecha (label X = punto medio temporal de cada zona). Se
eligió (opción del usuario) ATENUAR LOS LABELS POR EDAD: `color.new(txt, min(f_ageDim(barIdx)*2, 85))`
en los 4 push de label → el texto viejo recede como su caja. Completa el dim-to-focus (antes
solo la caja se atenuaba). El scatter persiste pero apagado.

## Verificación
Cada fix: pine_check server-side 0/0, compilado en TV sin CE10117 (confirma headroom tras
ADR-024 de S139), check-core-sync OK. Verificado en vivo con screenshots.

## Demostración del filtro de fuerza (a pregunta del usuario)
Se cambió a `i_densidad = Operación` para mostrar que el gráfico se limpia a solo
Primario/anclas (fila "Ocultos" del panel: Est 0 · EQ 62 · Liq 30 · Ref 1058 · μ 106 =
~1058 refs ocultas). Confirmado que la familia OB pasa por el filtro `f_densOK`
(Operación/Estudio/Todo) + band-pick/ancla siempre destacan. Al cierre se restauró a "Todo"
+ todos los conceptos + Context visible.

## Estado de la familia OB
COMPLETA — todas las variantes revisadas concepto × TF nativo (D1) + comportamiento entre
sí. Los 4 bloques atenúan por antigüedad de forma consistente (helper `f_ageDim`
compartido); labels curados cross-family.

## Defectos abiertos heredados de S139 (siguen vivos)
- El atenuado por edad no se reactiva por relevancia — un bloque viejo que se vuelve el
  próximo objetivo sigue apagado; falta combinar edad con alcance/proximidad, cubriendo
  OB/Breaker/MB juntos.
- El umbral en barras no es equivalente entre TFs (2000 barras en M5 ≈ 1 semana, en D1 ≈ 8
  años); se revisa en fase de herencias.

## Defecto menor nuevo
El scatter horizontal de labels (X = punto medio temporal) persiste, atenuado pero
presente — opción "columna fija a la derecha" queda como alternativa futura si molesta.

## Orden acordado para la próxima sesión (S141)
Plan explícito del usuario: SOLO la familia FVG y sus variantes (FVG, CE, IFVG §5.2, BPR
§5.3, IR §5.4, IPR §5.9), mismo método:
1. Revisar cada FVG/variante en su TF nativo.
2. Comparación ENTRE variantes de FVG.
3. LUEGO comparación FVG vs OB (con las variantes de ambas familias juntas).
4. Al final, revisión en modo Operación.

## Fase
Sigue FASE 1, F1-GATE ABIERTA.

## Referencias
[[Sesion-139]].
