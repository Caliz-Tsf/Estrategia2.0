# PENDIENTE — Estructura BOS/CHoCH de escala GRANDE (swing 50)

> Abierto en Sesion-021 (2026-06-14) por hallazgo del usuario comparando con LuxAlgo.
> **Tarea de SESIÓN DEDICADA y específica.** No mezclar con otra tarea. **No debe
> romper nada de T01–T07 ya validado.** Revisar con `opus-max` (arquitecto) y planear
> usando las herramientas que haga falta (skill/agente/MCP/workflow) ANTES de tocar código.

## El problema

Nuestra estructura BOS/CHoCH (T03/T04) corre solo a **`swingLen=5`** (swing) +
**`internalLen=3`** (interno). LuxAlgo dibuja la estructura GRANDE con
**`swingsLengthInput=50`** (`getCurrentStructure(50, false)`, ref
`pine/reference/LuxAlgo-SMC-base.pine` :95, :782) y la fina con **5**
(`getCurrentStructure(5, false, true)`, :783).

Es decir: nuestro "swing=5" equivale al **interno** de LuxAlgo, y **nos falta por
completo la capa de swing GRANDE (50)**. Por eso en el chart solo se ven BOS/CHoCH
pequeños y densos, y NO los movimientos estructurales grandes que sí marca LuxAlgo.

Es el mismo tipo de desajuste de escala que se corrigió en T07 para Premium/Discount
(que ahora usa su propio `i_pdSwingLen=50`), pero aquí en la **estructura**, y afecta
tareas ya validadas (T02–T06) → por eso requiere sesión dedicada.

## Ejemplos del usuario (LuxAlgo, EURUSD H1) — lo que NO se ve en nuestro Pine

1. **CHoCH bajista** en ~**1.17225** — inicia jue **07-may-2026 16:00**, se termina de
   formar mié **13-may-2026 01:00**.
2. **BOS bajista** en ~**1.15762** — inicia jue **21-may-2026 09:00**, se termina de
   formar vie **05-jun-2026 09:00**.
3. **CHoCH** en ~**1.15777** — inicia mar **09-jun-2026 09:00**, termina jue
   **11-jun-2026 15:00**.

Comportamiento observado de las líneas premium/discount de LuxAlgo (ya replicado en
T07): la línea sigue el precio y **no se marca una nueva hasta que el precio rompe ese
LL o HH**, y no se marca otra hasta el próximo HH/LL.

## Opciones a evaluar (para el arquitecto)

- **(B) Alinear estructura a LuxAlgo:** `swingLen=5→50`, `internalLen=3→5`. Re-valida
  T02–T06 (swings, BOS/CHoCH, bias, OB, FVG) porque cambia la escala base. Es lo más
  coherente con la referencia única y con T07 (que ya usa 50 para P/D).
- **(C) Añadir 3.ª capa de swing GRANDE (50)** sobre swing=5 + interno=3. No re-abre lo
  validado, pero conviven 3 escalas (más código, más objetos, definir cuál manda el bias).
- **(A) Dejar swing=5** (statu quo) — nuestro sistema más granular a propósito; se
  descarta mostrar la estructura grande. (El usuario NO quiere esto: quiere ver la
  estructura grande como LuxAlgo.)

> Nota de coherencia: hoy P/D usa swing 50 pero la estructura usa 5. LuxAlgo usa 50 para
> AMBOS. Esa inconsistencia es justo lo que esta tarea debe resolver.

## Reglas del proceso (igual que todo stask)

1. **Planear primero** con `opus-max`/`smc-architect` (y skill/agente/MCP/workflow que
   convenga). Decidir B vs C con criterio de no romper lo validado.
2. Si cambia la definición → actualizar los **3 documentos** que apliquen:
   `docs/reglas-smc-ict.md` (§1.1–§1.4 escalas), `WORKPLAN-MAESTRO-V2.md` /
   `docs/workplan/PINE-PLAN.md`, y `memory/ESTADO-ACTUAL.md`.
3. Ciclo por concepto: check-rule → spec → implement → compile 0/0 → check-core-sync →
   validar ≥90 (smc-validator-agent) → aprobación humana → commit. Re-validar cada tarea
   afectada con las mismas reglas.
4. ADR si cambia una decisión estructural (escala de swing es decisión de DOC-01).
