# MT5 esqueleto: timing y agenda

**Resumen decisiones sobre cuándo materializar el esqueleto MT5 en código.**

## S096 — Decisión diferida

El usuario pidió evaluar una "brief para Fable" sobre el esqueleto MT5 ("bot completo").

**Conclusión S096:** El "bot completo para rellenar" es PREMATURO.

**Razones:**
- Scoring Fase 2 no existe (apenas esbozado en reglas-smc-ict.md)
- Primitivos §7 son Fase A (Visual-only) → Fase B los promueve al CORE (UDT + SHA)
- `MQL5-PLAN.md` estaba stale (structs sin `strength`, KIND<53, campos §7 sin marcar)

**Sí es viable AHORA sin desperdicio:**
- Materializar solo módulos de **DETECCIÓN** (`SMC_Types.mqh`, `SMC_Structures.mqh`, `SMC_Liquidity.mqh`, `SMC_MTF.mqh`, etc.)
- Andamio compilable con `// TODO` en Scoring/Cuaderno/§7
- Refrescado contra CORE actual (1700 líneas SHA `5510361166844bd5`)
- Tabla de equivalencias Pine→MQL5

## S097 — Arquitectura documentada

Se creó `DOSSIER-FABLE-fase4-ea-mt5.md` con diseño completo:

- Bloque A: capa determinista EA
- Bloque B: percepción/cómo llega info
- Bloque C: score direccional
- Bloque D: score-de-perfiles darwiniano
- Bloque E: debate enjambre
- Bloque F: cuaderno confluencias + qué/cuándo NO entrar + proyección
- Bloque G: bucle cognitivo tiempo real (8 pasos)
- Bloque H: roadmap Fase 4.1–4.3, Fase 5

Se refrescó `MQL5-PLAN.md` contra CORE actual:
- Structs con `strength` (ADR-014)
- KIND≤53 (KIND_GRADIENT=53)
- Campos §7 `posRole`/`confDegree`/`depthBand` marcados [Fase B]
- Mapeo Pine→MQL5 para gradient levels, strength, §7, #52

## Secuencia recomendada

**Materializar esqueleto MT5 en código: DESPUÉS Fase 2 (scoring).**

**Razones:**
1. Fase 2 define los inputs (42 confluencias, weights)
2. Scoring es el corazón — sin él, re-work masivo post-Fase2
3. Fase 3 (calibración) ajusta pesos → cambios en structs
4. Arrancar ahora = 2–3 re-factors

**Antes de Fase 2 (AHORA viable):**
- Diseño arquitectónico (DOSSIER: hecho ✅)
- Módulos DETECCIÓN compilables (andamio: no hecho aún)
- Tabla equivalencias (refresco: hecho ✅)

**Regla dura:**
- Jamás referenciar EA viejo `D:\CODE\BOT\Bot\`
- Construir 100% desde CORE Pine + MQL5-PLAN

## Status

- DOSSIER-FABLE-fase4-ea-mt5.md: ✅ LISTO PARA ENTREGA A FABLE
- MQL5-PLAN.md refresco: ✅ ACTUALIZADO contra S097 CORE
- Andamio DETECCIÓN modules (MQL5): ⬜ DIFERIDO post-Fase2
- Esqueleto MT5 completo en código: ⬜ DIFERIDO post-Fase2
