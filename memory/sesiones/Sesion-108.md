# Sesion-108 — 2026-07-08 — Migración xloc.bar_time + BRIEF Herencia MTF

## Objetivo
Ejecutar la **Tarea #1 PRIORITARIA de S108** (solicitada usuario S107 al cierre): migrar los drawers de cajas de zona de `xloc.bar_index` con stopgap `f_xL` a ancla por tiempo `xloc.bar_time`, eliminando el clampeo falso de zonas >490 velas. Decisión de alcance usuario: SOLO ancla izquierda (Visual-only, sin tocar CORE); terminación en mitigación queda para Fase B.

## Completado — Tarea #1 (bar_time)

**1 commit Pine `04b67ca` (fix(pine-visual) bar_time)**

### Cambios Implementados
- **~17 sitios de dibujo migrados** en `pine/SMC-Visual.pine`:
  - Cajas OB, FVG, Breaker, IFVG, BPR, MB, Vacuum, OTE, IPR (todos los "core zones")
  - Labels centrados de cada concepto
  - Líneas CE (counterexample) del FVG
  - Patrón de cambio: `left = f_xL(z.barIdx), right = bar_index, xloc = xloc.bar_index` → `left = z.barTime, right = time, xloc = xloc.bar_time`

- **`f_xL(bi) = math.max(bi, bar_index-490)` ELIMINADO** — la función stopgap ya no se necesita

- **Nuevo helper global:** `int barMs = timeframe.in_seconds(timeframe.period) * 1000` para orígenes que no son la vela de creación:
  - FVG usa `z.barTime - barMs` (vela media del gap)
  - IPR usa `currentIpr.barTime - i_iprWindow * barMs` (ventana configurable)

- **Conservados 3 `xloc.bar_index` intencionales NO migrados:**
  - Label de pool en `bar_index+2` (L3679) — debe seguir pegado a barra viva
  - 3 líneas P/D `bar_index-1..bar_index` con `extend.left` (L4250-4252) — contexto vigente

### Compilación y Validación
- **Compila:** 0/0 server-side (pine_check.py)
- **Core-sync:** OK (SHA `5510361166844bd5` 1700 líneas, INTACTO)
- **Lookahead:** `lookahead_off` SIEMPRE (anti-repaint)

## Validación en Vivo

**Contexto:** OANDA:EURUSD H1, instancia MQVk7q, modo Operación, 2026-07-08

**Resultado Apply:**
- SIN CE10117 (token limit)
- SIN RE10026 (bar index limit)
- **error_count 0**
- 30 cajas dibujadas

**Distribución de x1 (borde izquierdo) — COMPROBADO bar_time funciona:**
- Zonas profundas/viejas (1.03–1.08): arrancan muy a la izquierda (x1=11-17 barras atrás)
- Zonas recientes (1.14–1.17): arrancan cerca de barra viva (x1=76-91 barras atrás)
- **ANTES con f_xL:** toda zona >490 barras compartía el mismo x1 clampea (visual falso)
- **AHORA:** cada caja ancla en su vela de origen sin límite de distancia

**Panel T14 (en vivo):**
```
D1  → Discount 12%
H1  → Equil 50%
M5  → Premium 64%
```

## Hallazgo y Discusión con Usuario (Pierna Alta Escasa)

**Observación usuario:** hacia arriba (D1 Premium 1.20831 / BSL-7/BSL-4/BSL-2) se ve casi solo un MB. Abajo hay más zonas.

**Diagnóstico técnico:**
1. Banda baja (1.14-1.16) SÍ está poblada ✓
2. Banda alta (1.17→premium) es escasa porque:
   - Esas zonas de oferta ESTÁN MITIGADAS
   - Dos gates las ocultan en Operación:
     - band-pick explícitamente excluye `z.state != ZS_MITIGATED` (L3126)
     - gate de densidad filtra por strength baja
3. NO es desalojo (panel "Ocultos" marca Desalojo 3 → MAX_ZONES_CHART=120 sin saturar)
4. **NO es bug del fix bar_time**

**Propuesta Parte A (Visual-only, NO implementada esta sesión):**
- Dejar entrar mitigadas al band-pick para poblar pierna alta como contexto gris degradado (§5.4)
- Observación: permite ver la frontera Premium histórica

## Idea Mayor del Usuario (Parte B — Documentada para Fable)

**Refinamiento de visión:** el usuario propone que el LTF (H1/M5) HEREDE las zonas/estructura IMPORTANTES del HTF (D1) **MÁS ALLÁ del Premium/Discount vigente**, en **AMBAS direcciones**, con **REVELADO PROGRESIVO**.

**Ejemplo:**
- H1 muestra hasta el Premium D1
- Al romperse esa frontera, se activan las zonas pasadas al premium (hasta un pivote histórico tipo BSL-3 ~1.50)
- Para TODOS los conceptos + estructura (incluido EQH que originó desplazamiento)
- Objetivo: draw-on-liquidity / proyección del swing

**Diagnóstico técnico (BLOQUEADOR OOM potencial):**
- Transporte MTF actual emite solo los K objetos MÁS CERCANOS AL PRECIO (`f_nearestN`/`f_computeTFState`, CORE byte-idéntico L1566/L1686)
- Las zonas D1 lejanas NO viajan a H1
- Revelado-al-romper es Visual-only barato; los DATOS lejanos requieren cambiar CORE:
  - Rompe SHA `5510361166844bd5`
  - Requiere campos nuevos UDT SMC_Zone
  - Strategy necesita actualización
  - Sensibilidad OOM (historia S104/S105)

**Decisión sesión:** NO se implementa Parte B esta sesión. Se documentó íntegramente para Fable.

## Entregable Doc (commit `a2751d5`)

**Archivo:** `docs/planes/BRIEF-FABLE-herencia-pierna-htf-revelado.md`

Contiene:
- Brief para revisión de Fable
- Contrato del transporte MTF actual
- Diagnóstico nearest-N
- Restricción OOM
- Petición de esqueleto respetando WORKPLAN
- Estrategia de-riesgo OOM primero

**Nota:** usuario lo pasará a Fable para revisión/sesión posterior.

## GOTCHAs Esta Sesión

1. **Inputs desplazados:** al quitar los 8 inputs en S107, la clave de Densidad pasó de `in_123` a `in_115` (verificado)
2. **El fix bar_time es el fix DEFINITIVO de RE10026** (f_xL era stopgap temporal)

## Estado Final

- **F1-GATE:** BLOQUEADA (redefinida, pendiente "pase fino")
- **Tarea #1 S108:** ✅ COMPLETADA + VALIDADA EN VIVO
- **Tarea #2 (regla solape MTF):** PENDIENTE
- **Tarea #3 (calibración i_kLeg/MAX_ZONES):** PENDIENTE
- **CORE:** 1700 líneas SHA `5510361166844bd5`, compila 0/0 los 3, core-sync OK
- **Commits:** 
  - `04b67ca` fix(pine-visual) bar_time (TAREA #1)
  - `a2751d5` docs(planes) BRIEF-FABLE (idea mayor documentada)
- **ADRs:** Sin nuevo (bar_time = refactor Visual-only bajo ADR-016/ADR-002; Parte B tendrá su ADR cuando se implemente)

## Pendiente (S109)

1. **Recibir/leer respuesta+esqueleto de Fable** al BRIEF herencia-pierna-htf-revelado.md
2. **Parte A (Visual-only):** mitigadas-como-contexto en band-pick (opcional demora a S109+)
3. **Tareas #2/#3 originales:**
   - Regla de solape MTF cuando D1/H1/M5 se sobreponen
   - Calibrar i_kLeg=3.0 (rango 1-6)
   - MAX_ZONES_CHART=120 (confirmar no sobrecarga)
   - Conteo exacto por banda

## Enlaces y Referencias

- [[Sesion-107]] — bloqueadores CE10117 + RE10026 resueltos
- [[Sesion-106]] — pasos A–D implementación
- [[Sesion-105]] — redefinición PASO 6
- `docs/adrs/ADR-016-retencion-zonas-por-importancia.md`
- `docs/planes/BRIEF-FABLE-herencia-pierna-htf-revelado.md` — nuevo brief

## Notas

- El fix bar_time es robusto: cada zona ancla en su timestamp de creación, sin límites artificiales
- Parte A (mitigadas) y Parte B (herencia+revelado) son extensiones independientes del fix bar_time
- La decisión de usuario de SOLO ancla izquierda (no terminación) es pragmática (Fase B requiere CORE-change, riesgo OOM)
- Stopgap f_xL fue banda-aid efectiva (permitió validación viva S107); bar_time elimina necesidad

---

**Sesión completada exitosamente.** Tarea #1 bar_time migración COMPLETA + VALIDADA VIVO. Commit `04b67ca` Pine + core-sync OK. Idea mayor documentada para Fable (`a2751d5`). F1-GATE sigue bloqueada por redefinición pero hallazgos técnicos resueltos. PENDIENTE S109: Fable respuesta + Partes A/B + Tareas #2/#3.
