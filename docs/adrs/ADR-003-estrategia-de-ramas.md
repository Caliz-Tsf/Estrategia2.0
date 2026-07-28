# ADR-003 — Estrategia de ramas: dos ramas largas, una por gran etapa

- **Fecha:** 2026-06-11 (Sesion-010).
- **Estado:** **Aceptado** — decisión de Freddy. **Vigente y en uso desde entonces.**
- **Tarea:** apertura de la rama de trabajo Pine.
- **Relacionado:** `WORKPLAN-MAESTRO-V2.md` §FASE 4 (gate duro de entrada); [[ADR-002]] (gate VER-09).

> **Nota de procedencia (S147).** Este ADR se cita como decisión vigente en 8 documentos
> (`ADR-007`, `ADR-008`, `notas-revision-fable.md`, `BRIEFING-mentor-module-v2.md`,
> `ESQUELETO-P3`, `HANDOFF-OPUS-MAX-ea-razonamiento-y-enjambre.md`, `ESTADO-ACTUAL.md`,
> `Sesion-011.md`) pero **nunca tuvo fichero** — verificado con
> `git log --all --diff-filter=A`: no existe commit que lo haya añadido nunca. Sesion-010 fue
> la apertura de rama y **no dejó archivo de sesión propio** (anotado en `Sesion-011.md:49`).
> Este documento **no decide nada nuevo**: transcribe la decisión desde el texto que sobrevivió
> literal en `ESTADO-ACTUAL.md`. Todo lo que no consta ahí se marca como *no registrado*.

## Contexto

El proyecto tiene dos grandes etapas de construcción con lenguajes y herramientas distintas:
el sistema completo en **Pine Script v6** sobre TradingView (Fases 1-3) y el **EA nativo en
MQL5** sobre MT5 (Fase 4). Entre ambas hay un **gate duro**: Fable revisa y aprueba
explícitamente el sistema Pine completo antes de que se escriba una línea de MQL5
(`WORKPLAN-MAESTRO-V2.md` §FASE 4). `main` debe reflejar solo hitos aprobados.

## Decisión

**Dos ramas largas, una por gran etapa de desarrollo:**

1. **`pine/sistema-completo`** = TODO el Pine (Fases 1-3: los 25+ conceptos + Strategy +
   calibración). Los commits de cierre de sesión (ESTADO-ACTUAL, Sesion-NNN, ADRs) fluyen
   **en esta rama**; `main` permanece estable. Se fusiona a `main` **SOLO** tras pasar el
   GATE DURO de entrada a Fase 4: Fable revisa y aprueba explícitamente el sistema Pine
   completo.
2. **`mql5/ea-nativo`** (*nombre propuesto*) = Fase 4, el Expert Advisor MT5. Se crea **al
   cerrar la última sesión de Pine**, después de la aprobación de Fable, partiendo de `main`
   ya fusionado.
3. **Regla:** ningún MQL5 hasta cerrar la rama Pine + gate Fable. **Cada rama = una gran
   etapa; `main` = hitos aprobados.**

## Alternativas descartadas

**No registradas.** El texto que sobrevivió no consigna qué otras estrategias de ramas se
consideraron en Sesion-010. No se reconstruyen aquí.

## Consecuencias

- Todo el trabajo de Fases 1-3 vive fuera de `main`, que queda como referencia estable.
- El historial de `main` es legible como secuencia de hitos aprobados, no de sesiones.
- La fusión a `main` es un evento único y tardío: **el riesgo se concentra en ese merge**, a
  cambio de que `main` nunca contenga sistema sin aprobar.
- El nombre `mql5/ea-nativo` sigue siendo **propuesto**, no creado.

## Validación (medida en S147, 2026-07-28)

La decisión está en uso, no solo escrita:

- `main` → `3e437f2`, fechado **2026-06-11** (`docs(sesion-009): cierre — VER-09 ✅`): **no se
  ha movido desde el día de esta decisión**.
- `pine/sistema-completo` → **429 commits por delante de `main`**.
- La rama `mql5/ea-nativo` **no existe** — correcto: Fase 4 no ha arrancado y el gate de Fable
  no se ha pasado.

## Referencias

- `WORKPLAN-MAESTRO-V2.md` §FASE 4 — gate duro de entrada a Fase 4.
- `memory/ESTADO-ACTUAL.md` → *Decisiones vigentes* — fuente literal de esta transcripción.
- `memory/sesiones/Sesion-011.md:49` — nota de numeración: Sesion-010 = apertura de rama.
