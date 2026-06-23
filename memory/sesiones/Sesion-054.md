# Sesion-054 — 2026-06-23

> **Módulo PLANIFICACIÓN + DISEÑO (módulo de verificación visual / discriminación).** NO Pine, core intacto, core-sync OK (1517 líneas SHA `80fad14dd8d03758`). Sesión paralela a Pine; validación visual F1-GATE (Sesion-049) replantea con rigor adicional. Continuación directa de `[[Sesion-053]]`.

## Objetivo
Diseñar una nueva capa de **calidad/discriminación** del sistema SMC que ataca el problema real observado: el Pine detecta todo (40+ conceptos) pero nada está jerarquizado — no se sabe cuál OB/FVG importa, cuáles marcas son fuertes vs ruido, ni cuáles están externamente invalidadas aunque cumplan la regla. Resultado: gráfico ilegible (3 IFVG, 2 T.FVG, OB, MB, BRK, Stack, Rej, IDM, CORR, EMAs y cajas solapadas en una vista). Diseño aprobado por Freddy 2026-06-23.

---

## Completado

### A. DIAGNÓSTICO DEL PROBLEMA — Columna vertebral del diseño

**Ciclo detectar → decidir:**
1. **Detectar** (marca todo) → Pine actualmente lo hace (reglas cuantificadas en reglas-smc-ict.md).
2. **Graduar** (fuerza 0–1) → FALTA. Necesario para discriminar OB/FVG fuerte vs ruido, mecha sin nivel, BOS rango normal.
3. **Contextualizar** (confluencia/secuencia) → FALTA. Necesario para invalidación externa (1er rebote no/2º sí) vía cadena ADR-012.
4. **Decidir** → Scoring + entrada/SL/TP.

**Problema mapeo:**
- (1) Variante equivocada de un concepto → **regla de desempate** (dentro del concepto).
- (2) Válido pero débil/ruido → **score de fuerza** (reuso cuerpo%, ×ATR, displacement, mitigado, sweep, distancia).
- (3) Regla cumplida pero externamente invalidada → **contexto/secuencia** vía cadena ADR-012, NO se hardcodea "no marcar".

### B. DECISIONES DE FREDDY — Fijan el diseño

**Capa de calidad HÍBRIDA:**
- Pine añade tag de fuerza **barato** por marca (reusa cuerpo%, ×ATR, displacement, mitigado, sweep, distancia).
- Grading completo aguas abajo: scoring Fase 3 + ADR-012 (enjambre).

**Verificación MTF DESCENDENTE (D1→H1→M5):**
- Cada TF detecta conceptos propios + heredados del TF mayor.
- Solo marcan los que REALMENTE valen (alta fuerza + alineados al bias).
- **Prueba de visibilidad cruzada:** un FVG D1 importante en su rango debe verse en H1 y M5 en las mismas coordenadas por bar_time.

**Casa de criterios (EXTENDER reglas-smc-ict.md):**
- Sub-bloque por concepto: Variante correcta / Fuerza 0–1 / Invalidación externa / Visual jerarquía.

**Arreglo de errores de dibujo MTF:**
- Entra al alcance el REPAIR documentado en `docs/sprint-runs/revision-T13b-mtf-dibujo-nativo.md` §2 + pendientes S042:
  - EQH/EQL que no caen donde se formaron → anclar tA→tB por bar_time.
  - OB/FVG dibujados como línea, no caja vela-a-vela.
  - Conteo de velas al bajar de TF (bar_time vs bar_index).
  - Tag de TF faltante en BOS/CHoCH fusionados.

### C. REPARTO DE ROLES (corrección clave de Freddy)

- **Opus Ultracode:** genera SOLO indicaciones + esqueleto (refina plantilla/metodología, ve qué falta para medir cada concepto, entrega plan de ejecución). **NO rellena los 40+ conceptos.**
- **Claude (yo):** hace el RELLENADO completo de los 40+ conceptos en reglas-smc-ict.md + ejecuta verificación.

> **Citado:** "Opus genera el plan, nosotros lo ejecutamos."

### D. ENTREGABLES DEL PLAN (pendientes crear — próxima sesión de ejecución)

1. **`docs/METODOLOGIA-VERIFICACION-VISUAL.md` (nuevo)**
   - Metodología graduada (supersede validación binaria Sesion-049).
   - Eje MTF descendente (D1→H1→M5).
   - Spec de jerarquía visual (3 niveles relevancia→visual, presupuesto de tinta top-N, decaimiento, perfiles densidad i_densidad, anti-solape).
   - Bloque arreglo errores de dibujo.

2. **Edición `docs/reglas-smc-ict.md` — plantilla + ejemplos**
   - Plantilla del sub-bloque.
   - 5 ejemplos trabajados (cobertura 3 fallos):
     - OB §2.1 (variante correcta).
     - FVG/variantes §2.2/5.1/5.2 (fuerza).
     - Cruce EMA §4.3 #40 (contexto).
     - Rejection §2.7 (invalidación).
     - MSS §1.5 (composite).

3. **`docs/planes/HANDOFF-OPUS-ULTRACODE-discriminacion-visual.md` (nuevo)**
   - Brief para Opus Ultracode: esqueleto + indicaciones (no rellenar 40).
   - Include: tag de fuerza Pine, jerarquía visual implementable, plan de ejecución.
   - Restricciones duras (core byte-idéntico, anti-repaint, ATR-relativo, no recalcular §4.8).

### E. REUTILIZACIÓN IDENTIFICADA (no inventar)

- `f_nearestN` → zonas no mitigadas más cercanas → top-N tinta.
- `SMC_Zone` + flags (mitigado/state/trueFvg/propulsion) → base del campo strength.
- `f_detectDisplacement` → primitivo de fuerza ya existente.
- Panel T14 → destino de lo no dibujado.
- ~43 toggles `i_show*` agrupados → base perfiles densidad.
- Cadena ADR-012 Q1–Q7 → capa Contextualizar/invalidación.

### F. DECISIONES DOCUMENTALES

**Plan completo guardado en:** `C:\Users\Fredd\.claude\plans\hola-claude-mira-quiero-dapper-conway.md` (fuera del repo, usuario).

**Bloqueos nuevos:** ninguno.

**ADRs nuevos:** ninguno. (Plan se apoya en ADR-010 dibujo MTF + ADR-012 razonamiento.)

**Relación:** Este plan da el rigor que faltaba a la validación F1-GATE (S049) y al snapshot determinista de ADR-012 (que depende de que el indicador marque SOLO lo que importa).

---

## Verificación
- **Plan manuscrito:** aprobado por Freddy, documento capturado en memory usuario ✅.
- **Ciclo detect→graduar→contextualizar→decidir:** diseñado, mecánismos diferenciados (no mezclar) ✅.
- **MTF descendente:** D1→H1→M5 con prueba visibilidad cruzada ✅.
- **Entregables:** 3 documentos especificados (plantilla, ejemplos, handoff Opus) ✅.
- **Reutilización:** 6+ funciones/estructuras identificadas, no inventar ✅.
- **Roles:** Opus = plan, Claude = ejecución — confirmado ✅.
- **Core:** intacto, core-sync OK (1517 líneas SHA `80fad14dd8d03758`) ✅.
- **Commits:** ninguno. (Sesión diseño, NO código.) ✅.

---

## Commits de Sesion-054
*Ninguno.* (Sesión de planificación + diseño. Validación Pine y enjambre siguen pendientes.)

---

## SIGUIENTE SESIÓN — Plan de ejecución

**Opción A (recomendada):** Ejecutar el diseño → crear los 3 entregables (METODOLOGIA-VERIFICACION-VISUAL.md + ejemplos en reglas-smc-ict.md + HANDOFF-OPUS).

**Opción B (paralela):** Retomar validación visual F1-GATE (Sesion-049, semi-autónoma MCP) en paralelo.

**Opción C (paralela):** Continuar enjambre (2º mentor, piloto E2E ADR-012).

---

## Pendiente — crítico para progresión
- **Validación visual F1-GATE (Sesion-049):** 40 conceptos 1-a-1 aislados, scores ≥90, anti-repaint, perf 20k → desbloquea Fase 2.
- **Diseño visual/discriminación:** crear 3 entregables, handoff Opus Ultracode, rellenado 40+ conceptos reglas-smc-ict.md.
- **Heredado enjambre:** 2º mentor, piloto E2E (Vigía+kanban+2mentores+orquestador), playlists NSL, CallMeBot, open-second-brain.

---

## Resumen
Sesión de **PLANIFICACIÓN + DISEÑO: módulo de verificación visual y discriminación de calidad.** Diagnóstico: Pine detecta todo pero nada está jerarquizado (gráfico ilegible). Solución: ciclo Detectar → **Graduar** (fuerza 0–1) → **Contextualizar** (confluencia/secuencia/invalidación) → Decidir. Tres mecanismos distintos: (1) variante equivocada = regla desempate; (2) válido pero débil = score fuerza; (3) externamente invalidado = ADR-012. **Decisión Freddy = HÍBRIDA:** Pine tags fuerza barato, grading completo aguas abajo (scoring + ADR-012). Verificación MTF obligatoria D1→H1→M5. **Reparto roles:** Opus Ultracode genera plan+esqueleto (NO rellena 40), Claude ejecuta rellenado+verificación. **Entregables 3:** (a) `METODOLOGIA-VERIFICACION-VISUAL.md` (nueva, supersede S049, MTF descendente), (b) `reglas-smc-ict.md` ampliada (plantilla + 5 ejemplos cobertura 3 fallos), (c) `HANDOFF-OPUS-ULTRACODE.md` (brief, no rellenar). Core intacto. Próxima: ejecutar diseño → crear entregables. Validación F1-GATE y enjambre siguen pendientes.

---

*Sesion-054 = planificación visual y discriminación. Plan aprobado por Freddy. No hay commits (diseño, no código). Próxima: crear 3 entregables + handoff Opus.*
