# Sesion-112 — VALIDACIÓN + PARTE A (F1-CTX-04/05 frontera+pools gris)
**Fecha:** 2026-07-10  
**Objetivo:** Continuar tareas pendientes de S111 (Test 2 break-side, Parte A mitigadas gris, Tarea #3 calibración, Fase B, firma F1-GATE). Plan elegido: **validación + Parte A, difiriendo Fase B**.  
**Estado:** ✅ FASE A CONTEXTO COMPLETADA. F1-GATE BLOQUEADA (sin firmar — aprobación humana pendiente). CORE 1700 líneas SHA `5510361166844bd5` byte-idéntico, compila 0/0 los 3, core-sync ×3 OK.

## Completado

### F1-CTX-04 — Frontera mitigada gris (Parte A) — commit `32445ae`
**Concepto:** cuando un lado no tiene OB/FVG viva dentro del alcance de `i_kExt`, revelar la MITIGADA más lejana como frontera gris degradada (contexto visual, fallback puro, jamás oculta una viva).

- **Diseño clave:** `f_farthestZone(type, side, inclMit=false)` → busca en array (orden: ACTIVA/PARCIAL > MITIGADA) y retorna la más lejana del lado + **emite `kind` con signo NEGATIVO cuando mitiga** (ej. `kind = -KIND_OB`) → **NO crece la tuple**, reusa los k-fields ya emitidos (protege headroom CE10117).
- **Nuevo parámetro `inclMit`:** si true, incluye mitigadas; si false, solo vivas (default inclusión en la búsqueda).
- **Dibujo gris (fallback):**
  - Color: `rgb(120,120,120)` (constante `CTX_MIT`), fill/borde más transparentes que vivas.
  - Tag " mit" para distinguir en etiqueta.
  - Caja (OB/FVG) con estilo degradado.
- **Toggle nuevo `i_ctxMitigated`:** input `in_5`, default **false** (OFF). Activa/desactiva la visualización de mitigadas como frontera gris.
- **Alcance:** solo OB/FVG (cajas). POOL y EQ no necesitan fallback gris (traspaso diferente).
- **Validación viva (EURUSD M5, OANDA):**
  - Baseline (capa OFF): sin cambios respecto a S111 → regresión OK ✅
  - Con capa ON (i_ctxMitigated=true): apareció caja gris H1 OB▼ 1.14 (bgColor 0x12787878 = rgb(120,120,120) transp~93%, borde 0x59787878) donde no había viva → **additivo, no reemplaza vivas, solo propone frontera** ✅

### F1-CTX-05 — Pools barridos gris (traspaso liquidez) — commit `e029f81`
**Concepto:** análogo directo a F1-CTX-04 para pools. Cuando no hay pool VIVO en ese lado dentro del alcance, revelar el BARRIDO (swept) más lejano como frontera gris (liquidez tomada/traspasada).

- **Nuevo helper `f_farthestPool(side, inclSwept=false)`:** busca en array pools (orden: VIVO > BARRIDO) → retorna más lejano + **emite `-KIND_POOL` cuando barrido** → reusa k-fields, sin crecimiento tuple.
- **Nuevo parámetro `inclSwept`:** si true, incluye barridos en búsqueda (4º parámetro +4º retorno `swept`).
- **Dibujo gris (fallback):**
  - Línea gris `CTX_MIT` (mismo color familia que F1-CTX-04).
  - Sufijo " x" en etiqueta para marcar "traspasado".
  - Nivel ±0.3×ATR del soporte/resistencia (patrón Visual existente).
- **Reutilización toggle:** mismo `i_ctxMitigated` (label generalizado a "traspasadas (mit + barridas)"). Ambas familias ON/OFF juntas.
- **Verificación técnica:**
  - CORE `f_prunePools` (L1387) **evicta swept solo al exceder cap** → pools barridos persisten en array → fallback alcanzable (no código muerto).
  - Compila 0/0, core-sync OK.
- **Validación:** path de dibujo gris probado (mismo mecanismo F1-CTX-04 línea L###). Captura directa de un pool-barrido-gris NO surgió con estado mercado disponible (requiere lado con SOLO pools barridos dentro bound; probado EURUSD/NAS100 con kExt estrecho, siempre había pool vivo que ganaba preferencia) — mismo límite observabilidad que break-al-romper, no hueco de código. Validado por paridad estructural + alcanzabilidad + 0/0 ✅

### Test 2 break-side — REPRODUCIBLE
**Hallazgo:** el break-side genuino reportado en S111 fue diferido por "no reproducible sin replay". En S112 reproducido en **NAS100USD (no EURUSD)**:

- **Condiciones:** precio superó rango dominante D1 (break genuino). Chart M5 con i_pdSwingLen corto (sensible). i_ctxAlways=false (normal).
- **Observación:** reveal_bits=4 (H1▲OB solamente, no D1 suprimido), H1▲OB 29975–30143 (box 17) dibujado, H1▲EQH 30588 (label) dibujado, **SOLO lado roto**, sin reveal espurio.
- **Ruta real validada:** lógica `close>pdHigh` ejecutada sin i_ctxAlways forzado, sin replay, sin pago TV → **"reveal-al-romper no reproducible" CERRADO: sí es reproducible en símbolos cuyo precio rompió rango D1** ✅
- **Nota:** EURUSD S111 seguía dentro rango dominante (precio 1.14193 < 1.20831 PDHigh) → lógicamente sin ruptura → correcto SIN reveal.

### Tarea #3 (Calibración i_kLeg / MAX_ZONES_CHART) — VALIDADA
**Hallazgo:** defaults de S106/S107 funcionan bien sin saturación de memoria ni exceso de desalojo.

- **Panel T14 EURUSD H1 (Operación):** "Ocultos: Est 0 · EQ 0 · Liq 0 · Ref 0 · Desalojo 32"
  - Nada importante oculto (todos Ocultos=0 significa band-pick cubrió bien).
  - "Desalojo 32" = cuenta acumulada de expulsiones del cap 120, NO saturación actual.
- **Decisión:** mantener i_kLeg=3.0 / MAX_ZONES_CHART=120 sin cambios. Defaults validados ✅

## Notas técnicas

### Discusión de diseño — Visión usuario & arquitectura TV
Usuario, viendo población hacia atrás del Visual, pidió que "importantes de cada TF que luego se traspasarán" reciban tratamiento gris/traspaso. Aterrizaje:

- **Visual YA selecciona por importancia** (`band-pick` top-3/celda, `f_isBandPick`).
- **Visual EXCLUYE mitigadas** en SMC-Visual.pine:3126 (`state != ZS_MITIGATED`).
- **Tratamiento gris/traspaso** se pone en **CONTEXT** (no Visual) porque:
  - Visual pegado a techo tokens CE10117 (headroom ≈ cero desde S107).
  - Meterlo en Visual obligaría recorte, rompería validación.
  - CORE inmutable (core-sync ×3 no tolera cambios).
- **Arquitectura TV reafirmada:** 2 Pines permanentes (Visual+Context) apilados, 1 CORE + 2 consumidores.
  - Indicadores NO se comunican en TV (límite plataforma).
  - Unificación real = Fase 4 (EA MQL5, un solo programa nativo).
  - NO se reorganiza fuente Visual (reorganizar ≠ reduce tokens; solo BORRAR statements reduce).

### CORE & Core-sync
- **CORE 1700 líneas SHA `5510361166844bd5` INTACTO.** Compila 0/0 los 3 (Visual/Strategy/Context), core-sync OK ×3.
- F1-CTX-04/05 reutilizan k-fields existentes (no crecimiento tuple).

### Sin ADR nuevo
Ambas características (F1-CTX-04 y F1-CTX-05) caen bajo **ADR-017 (Context consumidor auxiliar visual, Fase A, reversible; no toca Visual/Strategy/SHA).** ADR-017 ya escrito S110.

### Sin gate/tag
Progreso Visual-only auxiliar, no es gate de fase.

## Estado F1-GATE
**Sigue BLOQUEADA.** Pasos B/C/D/E/F Context + Parte A (F1-CTX-04/05) ✅. CORE intacto, core-sync OK ×3. **Pendiente:** aprobación humana (firma de Fable o usuario).

## Pendiente S113
Usuario comprometió orden S113:

1. **(a) PRIMERO al iniciar:** **EQ-tomado-gris** (F1-CTX-06 nueva). Mostrar EQH/EQL recién barridos/cruzados en gris un tiempo (liquidez tomada) en lugar de esfumarse. Requiere rastrear evento "cruzado" del EQ (buffer evK/evL hoy NO marca) → extensión no trivial. Después completar c/d.
2. **(b) Fase B promoción CORE:** tuple único `nearest+farthest` (31+31 campos → 62 en vez de 51), Strategy consume, re-baseline SHA `5510361166844bd5` → nuevo SHA, ADR nuevo Fase B.
3. **(c) Firma F1-GATE:** aprobación humana Fable/usuario. Gate no firmado aún.
4. **(d) Tarea #3 validada:** i_kLeg=3.0, MAX_ZONES_CHART=120 defaults confirmados sin cambios.

**Fuera alcance v1 Contexto:** MB/Breaker/BOS-CHoCH extremos heredados (v2 posible si Usuario pide).

## Commits
- **`32445ae`** — feat(pine-context): F1-CTX-04 frontera mitigada gris (Parte A)
- **`e029f81`** — feat(pine-context): F1-CTX-05 pools barridos gris (traspaso liquidez)

---
**Enlaza con:** [[Sesion-111]], [[Sesion-110]], `docs/planes/ESQUELETO-FABLE-context-htf-revelado.md`, `docs/adrs/ADR-017-consumidor-visual-auxiliar-context.md`, `docs/planes/swing-ideal-vision-usuario.md`
