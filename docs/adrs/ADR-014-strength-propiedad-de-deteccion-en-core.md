# ADR-014 — `strength` es propiedad de DETECCIÓN (vive en el CORE), no un atributo de render

- **Fecha:** 2026-07-02 (Sesion-083)
- **Estado:** Aceptado.
- **Precisa (no contradice):** ADR-002 (pesos/umbrales congelados hasta Fase 3), ADR-009/ADR-010 (transporte MTF por buffer aplanado), ADR-013 (el scoring es aditivo + un multiplicador gradient). Fija DÓNDE vive el campo `strength`; no toca la calibración.
- **Tarea:** Paso 0 del Eje 2 "Fuerza" / orden visual — `docs/planes/ESQUELETO-FABLE-sistema-visual.md` §11.2 pasos 1–2 + `HANDOFF-OPUS-ULTRACODE-discriminacion-visual.md` §5. Decisión previa a tocar el CORE.

## Contexto

El sistema visual definitivo (esqueleto Fable) introduce un motor de **fuerza** (`strength ∈ [0,1]` por marca) que ordena el chart: alimenta la quantización a 3 niveles (`f_strengthLevel` → 0/1/2), la jerarquía visual {Primario/Secundario/Terciario} (§2.4) y el orden del top-N de tinta (§2.5).

La pregunta de arquitectura, planteada en la revisión del esqueleto (concern #1): **¿el campo `strength` y sus funciones de cálculo (`f_zoneStrength`/`f_eventStrength`/`f_strengthLevel`) van en el `=== LIBRARY CORE ===` byte-idéntico (que Strategy también carga), o en `SMC-Visual.pine` fuera del CORE?**

El dilema es real por la regla dura #2 (core byte-idéntico) y por P-05 (no acoplar cosas al CORE que solo sirven a un consumidor):
- Si `strength` es **puramente visual** → meterlo en el CORE infla el CORE de Strategy sin razón, obliga a `check-core-sync` + SHA nuevo por un campo que Strategy nunca lee, y arriesga el tipo de acoplamiento que P-05 penaliza.
- Si `strength` es una propiedad de **detección** (calidad intrínseca de la marca, derivada de primitivos ya en el CORE) → los DOS consumidores la necesitan y pertenece al CORE.

## Decisión

**`strength` es una propiedad de DETECCIÓN. Vive en el `=== LIBRARY CORE ===` byte-idéntico, junto a los UDTs y funciones puras.** El *nivel visual* {Primario/Secundario/Terciario} sí es de render y vive en Visual (`f_visualLevel`), pero el `strength ∈ [0,1]` y su quantización `f_strengthLevel` a 0/1/2 son CORE.

### 1. Justificación: `strength` tiene DOS consumidores, uno es Strategy
- **Consumidor visual (Fase 1, ahora):** `SMC-Visual.pine` mapea `strength` → nivel visual → tinta.
- **Consumidor de scoring (Fase 3):** el HANDOFF §5.3 y su restricción #4 ya declaran que "el 0–1 fino lo consume el scoring; el 0/1/2 alimenta la jerarquía visual" y que "la capa de fuerza alimenta el peso". La calidad de una zona (frescura, displacement, cuerpo%, sweep previo, alineación con bias) es exactamente el insumo que el scoring direccional de Fase 3 usará para modular pesos. `SMC-Strategy.pine` ES consumidor.
- Un campo que ambos consumidores leen, calculado a partir de primitivos que ya viven en el CORE (`f_detectDisplacement`, `SMC_Zone.state`, `f_detectSweep`), es por definición parte del CORE. No es acoplamiento P-05: es cohesión.

### 2. Qué va al CORE y qué NO (frontera exacta)
| Pieza | Ubicación | Razón |
|---|---|---|
| Campo `float strength` en `SMC_Zone`/`SMC_Event`/`SMC_Swing`/`SMC_Pool` | **CORE** | propiedad de detección; ambos consumidores |
| `f_zoneStrength` / `f_eventStrength` (puras, al cierre, reusan `atr14`) | **CORE** | cálculo de la propiedad |
| `f_strengthLevel(s) → 0/1/2` | **CORE** | quantización estable; la usan Visual (jerarquía) y el transporte MTF |
| `f_visualLevel(sLevel, isAnchor, withinCap, mtfFloor, modeCeiling)` | **Visual** | decisión de RENDER (anclas, cap, modo) — no la necesita Strategy |
| Constantes `COL_*`, `i_densidad`, consolidación de labels, ribbon, z-order | **Visual** | 100% render |

### 3. `strength` NO es una confluencia nueva (P-05 / regla #6 intactas)
`strength` modula la CALIDAD de una marca; no es un voto que se suma al catálogo §4.8. Los flags de refinamiento (`trueFvg`, `propulsion`, `gradedFvg`) elevan el `strength` del concepto base — NO crean confluencia nueva (consistente con la decisión FIX P-05 ya tomada en S048/S080). El conteo de 42 confluencias no cambia.

### 4. Transporte MTF por el buffer existente (ADR-009/010 intactos)
El `strength` viaja quantizado (0/1/2) en el buffer de evento/zona que ADR-010 ya aplana para MTF — empaquetado junto al `dir` (`dir·3 + level` cabe en un int, o campo extra si el aplanado lo permite; decisión `[impl]` al cablear). No requiere un 7º campo dedicado ni tocar `SMC_TFState`.

### 5. Valores congelados hasta Fase 3 (ADR-002 intacto)
Los pesos por primitivo (0.30 displacement, 0.20 state, etc. — HANDOFF §5.2) y los umbrales de quantización (0.33/0.66) son candidatos CONGELADOS. La FORMA (suma ponderada normalizada + quantización de 3 niveles) se fija aquí; los NÚMEROS entran por IS/OOS.

## Alternativas descartadas

- **`strength` en Visual, fuera del CORE:** descartada — obligaría a re-implementar el mismo cálculo en Strategy cuando Fase 3 cablee la modulación de pesos (dos implementaciones divergentes del mismo concepto = el problema que el CORE compartido existe para evitar), y rompería el golden-test 1:1 de Fase 4 (el EA necesita `strength` como función pura verificable).
- **`strength` como confluencia #53 aditiva:** descartada — contradice P-05 y la regla #6; `strength` es un modulador de calidad, no un voto.
- **Campo separado por consumidor (un `strength` visual + otro de scoring):** descartada — misma cantidad, dos nombres = divergencia garantizada. Un solo `strength ∈ [0,1]`; cada consumidor lo interpreta (Visual quantiza, scoring usa el fino).

## Consecuencias

- **Pasos 1–2 del §11.2 tocan el CORE** → `check-core-sync.ps1` + SHA nuevo documentado por commit (esperado, no es regresión). Del paso 3 en adelante todo vive en Visual y NO toca core-sync.
- **Fase 3 hereda `strength` listo** para modular pesos — F2/F3 no re-litigan de dónde sale la calidad de una marca.
- **Fase 4 (MQL5):** `f_zoneStrength`/`f_eventStrength`/`f_strengthLevel` se traducen 1:1 como funciones puras con golden tests directos (mismo patrón que `f_gradientConfluenceBonus` en ADR-013).
- **Nota de implementación ligada (no es parte de este ADR, se decide al cablear §2.5):** el orden del top-N por `strength × cercanía` se implementa como variante nueva `f_strongestN`, NO mutando `f_nearestN` (que quedó validado en S057 con orden por distancia) — para no regresar lo aprobado.
- **Nota de verificación ligada:** al reescribir el render de 40 conceptos (pasos 3–8), el paso 9 debe re-confirmar los Ejes 0/1/3 (presencia/variante/invalidación) además del Eje 2, no vaya el overhaul a ocultar algo que el Eje 0 necesitaba.

## Referencias

- Esqueleto: `docs/planes/ESQUELETO-FABLE-sistema-visual.md` §0.1 (motor strength conservado), §2.4, §11.2 (pasos 1–2 CORE), §11.1 D-2.
- Spec del motor: `docs/planes/HANDOFF-OPUS-ULTRACODE-discriminacion-visual.md` §5 (campos, funciones, pesos, quantización, transporte MTF).
- ADRs base: ADR-002 (congelación), ADR-009/ADR-010 (transporte MTF), ADR-013 (scoring aditivo + multiplicador; strength distinto del bonus gradient).
- Reglas duras: `CLAUDE.md` #2 (core byte-idéntico), #3–#4 (ATR-relativo/símbolo-agnóstico), #6 (scoring direccional), P-05 (no inflar confluencias).
