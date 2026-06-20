# Sesion-038 — 2026-06-20
**Tipo:** Sesión de DISEÑO / planificación (entrega del encargo de Opus Max). NO sprint Pine. CORE INTACTO, core-sync OK MISMO SHA `2de06be3a3eb1321` (644 líneas, T12 MSS de Sesion-036). No se tocó ningún .pine.

## Objetivo
Ejecutar el encargo del handoff `HANDOFF-OPUS-MAX-mapa-mtf-confluencias.md` (S037): producir el **esqueleto integrado P3** (mapa MTF rico + motor confluencia→entrada), **unificar el workplan** con las nuevas integraciones, y **reconciliar ADR-005/007**. El usuario aportó de nuevo las 5 imágenes de setups SMC para anclar la visión "marca todo lo que pasa → decide en qué zona entrar".

## Completado
**NINGUNA TAREA PINE IMPLEMENTADA.** Entrega documental que desbloquea Sprint 1.4. 4 archivos:

1. **`docs/planes/ESQUELETO-P3-mapa-mtf-confluencias.md` [NUEVO]** — el plano principal:
   - **§2 Mapa MTF rico:** 2 planos (TF propio rico local / HTF reducido vía security). **Presupuesto de `security` calculado:** `total ≈ 24 + 28·N` por llamada → **N_htf ≈ 3/lado** es el cap (N=3→108 ✅, N=4→136 ❌ sobre ~127). Contrato `f_computeTFState`/`f_tfSnapshot` (CORE byte-idéntico, estado interno por-contexto R-P3-1). UDT `SMC_TFState` a ampliar. `f_nearestN` pura nueva en CORE (generaliza `f_pNearZone`/`f_pNearPool` que devuelven UNO y son de presentación). Cascada D1→{H1,M5}, H1→{M5} + dibujo diferenciado + inputs densidad GRP_MTF.
   - **§3 Motor confluencia→entrada (el "fondo de todo"):** las 5 imágenes destiladas a UNA gramática canónica `①contexto(BOS/MSS/CHoCH)→②liquidez(grab/sweep/IDM)→③POI(OB/FVG en disc/prem)→④trigger→⑤SL→⑥target(R:R≥1:3)`. Dos capas: (a) confluencias atómicas §4.8 (scoreLong/Short) + (b) **setups/secuencias** nuevas (NO recalculan el score). Pieza nueva: **`f_selectEntryPOI`** — el selector de zona de entrada que premia el solapamiento multi-TF (la anidación EN cascada ES la confluencia de calidad). Catálogo de setups S-01..S-05 como fichas (NO recetas hardcodeadas). Puente offline §3.6.
   - **§4 Carriles** Pine/EA vs Hermes/Enjambre + 4 puntos de integración (I-1..I-4; único puente vivo = gate noticias I-4).
   - **§5 Workplan unificado** + orden paso a paso (11 pasos) + gates. **§6 riesgos** (R-1 spike, R-2 límite tuple, R-3 objetos dibujo).

2. **`docs/adrs/ADR-008-mapa-mtf-confluencias-pared-dura.md` [NUEVO]** — reconcilia ADR-005/007: (1) pared dura EA↔laboratorio-en-vivo; (2) "operar" del enjambre = **entradas DEMO + notificación** (no reales); (3) puente EA←enjambre **offline** (cristalización por IS/OOS); (4) mapa MTF + motor confluencia→entrada = arquitectura **adelantada de Fase 4** (`SMC_MTF.mqh`). Incluye el protocolo de escalada del spike y el gate pre-testeo.

3. **`docs/workplan/PINE-PLAN.md` [EDIT]** — Sprint 1.4 desdoblado **T13a** (núcleo) / **T13b** (rico) + gate del spike + nota de la capa confluencia→entrada + los 2 gates duros. Pointer a P3.

4. **`WORKPLAN-MAESTRO-V2.md` [EDIT]** — §4.8 nota de la capa (b) setups sobre las atómicas, sin tocar la numeración (42 + #43–#51).

### Decisiones del usuario capturadas en S038 (van a P3 + ADR-008)
- **Protocolo de fallo del spike test (R-P3-1):** ✅ si pasa → se continúa el plan; ❌ si falla / hay problemas → **DETENER, NO improvisar workaround, avisar a Freddy** con diagnóstico para que **escale a Opus ultracode (Opus Max)** y se decida el rediseño del transporte MTF. (P3 §5.3/§5.4/§6)
- **★ GATE PRE-TESTEO DE SETUPS:** el testeo de setups del enjambre (replay+demo → IS/OOS) **NO arranca** hasta que estén COMPLETOS **(A) el Pine** (todos los conceptos integrados + motor confluencia→entrada en Strategy) **Y (B) el enjambre** (perfiles + archivos/knowledge + skills + MCP + workflow + loop, no el piloto). Construcción paralela permitida; testeo no antes del gate. (P3 §5.3, ADR-008)

## Commits
- `docs(planes): ESQUELETO-P3 mapa MTF rico + motor confluencias + ADR-008 + workplan unificado` (este cierre).

## Pendiente
**Sprint 1.4 SIGUE EN PAUSA hasta que el usuario apruebe P3 + ADR-008.** Próximo paso técnico = **spike test R-P3-1** (sesión Pine corta) antes de T13b. Orden completo en `ESQUELETO-P3 §5.4`.

1. Aprobación humana de P3 + ADR-008.
2. Spike test R-P3-1 (request.security + estado var interno no contamina chart). Si falla → escalar a Opus ultracode.
3. T13a → T13b → T14 → T15 → gate Fase 1.
4. Completar Pine (Sprint 1.5/1.6 + Fase 2 motor) ‖ construir enjambre completo (P2).
5. Gate pre-testeo → testeo setups → IS/OOS Fase 3 → gate Fable → Fase 4 EA.

## Bloqueos
Ninguno nuevo.

## ADRs escritos en sesión
**ADR-008** (mapa MTF + confluencias + pared dura). Reconcilia/precisa ADR-005/007 sin contradecirlos.

## Gates completados
Ninguno (los 2 gates nuevos quedan DEFINIDOS, no superados).

## Notas
- 4 archivos tocados; **0 .pine**; core-sync mismo SHA `2de06be3a3eb1321`.
- P3 NO duplica P1/P2: los referencia. Cubre el hueco que ninguno cubría (substrato espacial MTF + capa de decisión confluencia→entrada).
- Hallazgo decision-grade: el "mapa rico N=10/lado en TODO" NO cabe por `security` (presupuesto ~127); la riqueza completa vive en el TF propio (local), el HTF va capado a N_htf≈3.
- Ver [[Sesion-037]] (handoff origen) · [[estrategia2-arquitectura-v2]].
