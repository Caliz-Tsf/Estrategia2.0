# Sesion-037 — 2026-06-20
**Tipo:** Sesión de DISEÑO / planificación. NO sprint Pine. CORE INTACTO, core-sync OK MISMO SHA `2de06be3a3eb1321` (644 líneas, T12 MSS de Sesion-036). No se tocó ningún .pine.

## Objetivo
Arrancar implementación Sprint 1.4 T13 MTF (request.security D1/H1). En el camino, el usuario AMPLIÓ la visión más allá de un T13 técnico aislado.

## Completado
**NINGUNA TAREA PINE IMPLEMENTADA.** La sesión fue exclusivamente de **DISEÑO + HANDOFF** para que Opus Max (Claude Code Opus) integre la visión MTF/confluencias/enjambre en el workplan maestro.

### Decisiones + hallazgos capturados

1. **Decisión de diseño MTF — top-down clásico + mapa rico:**
   - El chart es la base "rica"; D1/H1 son fotos hacia arriba. 
   - El usuario NO quiere foto plana mínima: quiere un **MAPA MTF RICO** — los últimos ~10 de CADA concepto cerca del precio, SEPARADOS por dirección (alcistas/bajistas), con densidad configurable (input 0–10 por concepto, por dirección, por TF).
   - Anidación en CASCADA: D1→{H1,M5}, H1→{M5} (las zonas/estructuras nativas de H1 también se ven en M5).
   - Dibujo MTF diferenciado (transp 85, punteado, prefijo "D1:"/"H1:").

2. **Hallazgo técnico central (explorado con 2 agentes Explore):**
   - La cadena de detección está suelta en DETECCIÓN (SMC-Visual.pine ~697-960 / SMC-Strategy.pine ~678-904) con estado var global.
   - Para correrla en D1/H1 dentro de `request.security` hay que ENCAPSULARLA en una función (`f_computeTFState`) con todo su estado interno.
   - `request.security` solo transporta NÚMEROS, no objetos/arrays → el mapa HTF se trae APLANADO (tope fijo, ~127 valores/llamada).
   - Es un refactor del corazón pero es justo lo que Fase 4 (SMC_MTF.mqh) necesita.
   - **Helpers reutilizables ya existen:** `f_pNearZone` (Visual:1232), `f_pNearPool` (:1245), `f_pLastEvent` (:1229), `f_updateZoneMitigation` (Library:327), UDT SMC_TFState (Library:113, hay que ampliarla).
   - Sección MTF es stub vacío (Visual:962-963, Strategy:906-907).
   - Se sugirió **T13 escalonado** (T13a núcleo / T13b enriquecido).

3. **Motor de confluencias — validación con usuario:**
   - El usuario aportó 5 imágenes de setups SMC/ICT (Sell Setup, Simple BOS Entry, Smart Money Entry BOS+IND+OB+QM+MSS, SMC for Beginners, Institutional Notes).
   - Estas son **secuencias de confluencias** que disparan entrada R:R≥1:3.
   - Foco del EA+enjambre = buscar/testear esas confluencias y entregarlas validadas al EA.
   - Sigue siendo **scoring direccional ponderado** (regla #6), NO recetas hardcodeadas.

4. **Correcciones a ADR-005/007 (para reconciliar después):**
   - El enjambre **OPERA EN VIVO** (replay + en vivo vía MCP, discute en vivo) PERO "operar" = registrar **ENTRADAS DEMO en TradingView** para testear (NO operaciones reales) + notificación WhatsApp/CallMeBot.
   - Pared dura EA↔laboratorio-en-vivo (no se comunican en runtime).
   - Puente EA←enjambre **OFFLINE** (confluencias testeadas → calibración Fase 3 → EA).

## Commits
**NINGUNO — sesión documental únicamente.** Git status limpio; no se tocaron .pine ni otros archivos codigo.

## Pendiente
**Sprint 1.4 (T13/T14/T15) queda en PAUSA hasta que Opus Max entregue el esqueleto integrado + workplan unificado.**

1. **Opus Max debe producir:**
   - Análisis completo del handoff.
   - Esqueleto integrado `ESQUELETO-P3-mapa-mtf-confluencias.md` que Claude Code rellene.
   - **Workplan maestro UNIFICADO** (WORKPLAN-MAESTESTRPO-V2.md reescrito) siguiendo TODAS las reglas/políticas existentes.
   - Separación clara de carriles Pine/EA vs Hermes/Enjambre con puntos de integración marcados.
   - Reconciliación de ADR-005/007 (enjambre en vivo vs EA offline).

2. **Próxima sesión Claude Code (Opus Max):** lanzar con el handoff `docs/planes/HANDOFF-OPUS-MAX-mapa-mtf-confluencias.md` + directiva de producir el esqueleto integrado + workplan unificado.

3. **Tareas Pine T13/T14/T15 NO marcadas como completadas** (no se implementaron).

## Bloqueos
Ninguno nuevo.

## ADRs escritos en sesión
Ninguno (se delegó la reconciliación a Opus Max).

## Gates completados
Ninguno.

## Notas
- **ENTREGABLE ÚNICO de la sesión:** documento de handoff `docs/planes/HANDOFF-OPUS-MAX-mapa-mtf-confluencias.md` (NUEVO).
- Decisión del usuario: **NO lanzar Opus Max automático** — usuario lo hace en sesión aparte, dedicada a Opus Code.
- El usuario proporcionó 5 imágenes de setups reales como referencia para las confluencias — se guardaron en el contexto del handoff para que Opus Max las vea.
- Acuerdo de diseño: el user quiere que Opus Max NO solo rellene el esqueleto técnico Pine, sino que reconcilie TODO (arquitectura, workplan, ADRs, split Pine/EA/Hermes/Enjambre, confluencias, gate Fase 3).

