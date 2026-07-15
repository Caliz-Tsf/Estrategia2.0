# Sesión 131 — 2026-07-15

## Título
FASE 1 · F1-GATE BLOQUEADA — LA REGLA DE POOLS MEDIDA: LOS TOQUES MIDEN CONGESTIÓN, EL USUARIO MARCA EXTREMOS

## Objetivo
Las 4 mediciones que S130 §9 dejó definidas antes de implementar la regla de pools.

## Estado del repo
- Rama `pine/sistema-completo`.
- `pine/` NO SE TOCÓ en toda la sesión.
- CORE SHA `752b4083a7db419d` (1866 líneas) INTACTO.
- core-sync OK ×3.
- pine_check 0/0 en los probes.
- SIN ADR. SIN tag. F1-GATE sigue BLOQUEADA.

## Completado

### Commits (1)
- `fd8f27b` chore(scripts): doc `docs/planes/DISENO-regla-de-pools-S131.md` + arnés `scripts/gen_probe_regla_pools.py` (ambos archivos nuevos)

### Tarea 0 — desambiguación previa (decisión del usuario, antes de escribir el probe)
La §9 de S130 decía "el siguiente pool" en dos sentidos incompatibles. El usuario eligió:
(a) el extremo de un TF es el pool MÁS LEJANO dentro del rango del TF superior;
(b) los pools de un TF son la UNIÓN de los heredados de D1 y los nativos.
Se hizo para no repetir el fallo de S129 (diseño ambiguo → los probes midieron la lectura equivocada).

### Tarea 1 — medición (probes v7/v9, markers 1310 y 1312, D1 OANDA:EURUSD, n=6283, los 3 cross-checks `P_xcheckCenso`/`P_xcheckUp`/`P_xcheckDown` en 0)
- P-P1 FALSA (era "la que decide"): la hipótesis letal (que `f_markPoolsSwept` + `f_prunePools` habrían matado los niveles que el usuario lee) es FALSA. Están VIVOS y clavados: `hitD1lo`=1 a 0.0 pips (0.95360), `hitH1lo`=2 a 7.5 pips, `hitH1hi`=1 a 3.6 pips (1.39937 vs su 1.39972). `nAliveAbove`=26, `maxAliveLvl`=1.60389, `minAliveLvl`=0.90275. Razón no prevista: el precio bajó de 1.39972 y NUNCA volvió, así que ese pool jamás fue barrido.
- P-P2 VERDE: `nAtCap`=5456, `maxSize`=80. El prune actúa.
- P-P3 VERDE en el número (`nAliveT3`=1, predicho <=2) pero su COROLARIO es FALSO: los niveles del usuario sí están en el set.
- P-P5 FALSA: `nNoPoolDown` = 1130/6283 = 18.0% (se predijo >30%).
- CENSO: 80 pools en el set, 38 vivos, 42 barridos, 26 vivos arriba y 12 abajo.

### Tarea 2 — corolario doctrinal (desbloquea el ADR parado desde S129)
"Min/max histórico" y "pool estructural (§2.3 strong high/low)" NO compiten. El extremo histórico es NECESARIAMENTE un pool vivo, porque nada lo superó nunca. `minAliveLvl`=0.90275 y `maxAliveLvl`=1.60389 son pools VIVOS. El ADR ya no tiene que elegir entre min/max y §2.3: era una falsa disyuntiva que costó S129 entera.

### Tarea 3 — HALLAZGO PRINCIPAL (gemelo exacto de S130)
`i_minTouches`=2 deja la regla SIN candidatos. Volcado de los 38 pools vivos (vía label + `data_get_pine_labels`): 37 tienen `touches`=1; el único con 3 es 1.51421, que no es ninguno de los del usuario. Como `f_farthestPool` exige `touches >= i_minTouches`: arriba solo pasa 1.51421 (medido `P_reglaUp`=1.51421 — el motor lo ancla ahí por ser el único candidato legal, no por criterio) y abajo NINGÚN pool vivo tiene 2 toques, así que el suelo sale `na` y NO HAY RANGO. Causa: `f_upsertPool` fusiona solo si `|Δlevel| <= i_poolTol × ATR`, con `i_poolTol`=0.1 y ATR D1 ~0.0055 = 5.5 pips → el clusterizado de pools está apagado por un input.

### Tarea 4 — barrido de `i_poolTol` (vía `indicator_set_inputs` sobre la instancia del chart; el default del repo sigue en 0.1)
- 0.1 → 38 pools vivos, 1 con touches>=2 (1.51421)
- 0.3 → 34 pools, 3 con touches>=2 (aparecen 1.25753 y 0.97175)
- 0.5 (=maxval del input) → 34 pools, 3 con touches>=2, IDÉNTICO a 0.3 (satura)

En todo el barrido los 5 niveles del usuario siguen a 1 toque.

CONCLUSIÓN: los toques miden CONGESTIÓN y el usuario marca EXTREMOS — propiedades opuestas; un máximo histórico no puede tener 2 toques porque si los tuviera no sería el máximo. Vía de la fuerza-por-toques REFUTADA, la opción barata queda CERRADA.

### Tarea 5 — reglas aritméticas descartadas contra los números del usuario
Lectura suya D1 [0.90494, 1.60063] / H1 [1.02108, 1.39437], precio 1.14660:
- (a) escala fija ×4 — encoger un rango por ambos lados CONSERVA el pct: D1 34.7% vs H1 33.6%, así que H1 no aporta información distinta de D1 y un escalado simétrico nunca compra rotación.
- (b) ventana `close ± X` — con la X que alcanza 1.39437 arriba (2478 pips) abajo llega a 0.90180, y cogería 0.95364, no su 1.02108.
- (c) escala por ATR — el ratio ATR D1/H1 es ~4.9 pero el ratio de sus rangos es 1.86.

## Lo que queda en pie (única vía viva, para S132)
LA AMPLITUD DEL SWING (en ATR). Entre 1.02108 y el precio hay 6 pools vivos (1.036, 1.0733, 1.10654, 1.12105, 1.13246, 1.1473) que el usuario NO considera pisos; no los descarta por toques ni por edad, sino porque son swings pequeños. `SMC_Pool` guarda level/dir/touches/barTime/swept/barIdx pero NO la amplitud del swing que lo creó. Es la única propiedad que su ojo usa y el motor no registra. Ya existe para swings (`i_swingDomAtr`=8×ATR, S125) y es adimensional → multi-símbolo (ADR-001). Añadirla toca el CORE → rompe el SHA → re-baseline ×3 → contrato MQL5 → ADR obligatorio, pero ahora con evidencia medida. MEDIR ANTES de tocar el CORE (norma S114), con predicción escrita antes.

## Gotchas nuevos
- El 2.º Ctrl+Enter puede abrir el modal "¿Desea guardar este script antes de añadirlo?" y el apply se queda BLOQUEADO EN SILENCIO (marker rancio sin aviso); hay que pulsar Guardar; la consola lo delata porque muestra "Compilando..." sin el "Añadido al gráfico".
- `data_get_pine_labels` NO sigue el crosshair → es el canal correcto para censos de N filas; `data_get_study_values` SÍ lo sigue y devolvió `nPools`=0 con el crosshair en una barra intermedia.
- `i_poolTol` tiene maxval=0.5 en el input → 1.0 no es alcanzable sin tocar código.
- Mapeo de inputs verificado contando `input.` en orden: `i_poolTol`=in_81, `i_minTouches`=in_82 (coherente con `i_pdSwingLen`=in_69 e `i_densidad`=in_118 ya conocidos).

## Predicciones
18 vivas de 37 (P-P2, P-P3, P-P6 nuevas verdes; P-P1 y P-P5 falsas; P-P4 declarada tautológica ANTES de medir y por eso no cuenta).

## Pendiente / Siguiente (S132)
1. Medir si etiquetar pools por amplitud de swing en ATR hace emerger los 5 niveles del usuario y NO los 6 intermedios que descarta.
2. El fallback (M2) sigue sin resolver — el 18% medido salió con el gate roto, hay que re-medirlo cuando el gate de anclaje funcione.
3. NO repetir: cascada de mitades, mapeo nivel→TF (S130), fuerza-por-toques ni barrer `i_poolTol` (S131), los cuatro refutados con medición.
4. Pendientes abiertas de antes: IFVG por banda/lado, gate MB/BPR, `elig` excluye ZS_MITIGATED en Visual, calibrar `LEG_ANCH_TOL_ATR`, deudas S123 #2/#3/#4, herencia MTF.

## Enlaces
[[Sesion-131]] · [[Sesion-130]] · [[Sesion-129]] · [[Sesion-128]]
