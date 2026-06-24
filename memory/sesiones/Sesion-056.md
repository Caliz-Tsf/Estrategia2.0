# Sesion-056 — Población de la capa de discriminación/verificación visual (reglas §6.3)
**Fecha:** 2026-06-23  
**Objetivo:** Completar la especificación de la capa de discriminación/verificación visual graduada — rellenar §6.3 de `docs/reglas-smc-ict.md` (35 sub-bloques nuevos de conceptos con plantilla §6.0) + especificar §5 y §6 del HANDOFF Opus.  
**Resultado:** ✅ **COMPLETADO**

---

## Qué se entregó

### 1. **docs/reglas-smc-ict.md §6.3 — POBLADO**
- **35 sub-bloques nuevos** (`6.3.1` a `6.3.35`) de conceptos de la capa discriminación, utilizando plantilla §6.0 (variante·fuerza·invalidación·visual·MTF).
- **Citación exclusiva de primitivos del inventario §6.1** (9 primitivos: BOS/CHoCH, OB, FVG, EQH/EQL, Sweep, Pool, Premium/Discount, Liquidez).
- **Sumados a los 5 ejemplos completados en §6.2 (sesión anterior):** OB COMPLETO + 4 slots rellenables (FVG, EMA-cruce, Rejection, MSS) = **40 conceptos en total**.
- **Refinamientos `[FIX P-05]` sin sub-bloque propio:**
  - True FVG: elevado `strength` del concepto FVG base (§5.1, ya en S053).
  - Propulsion: elevado `strength` del concepto Pool base (§5.8).
  - Macros: herramienta auxiliar, NOT confluencia de scoring.
  - Volume Imbalance: herramienta auxiliar, NOT confluencia.
  - Std Dev: herramienta SL/TP, NOT confluencia de scoring.
- **Marginalia:** SMT requiere GBPUSD (ADR-011); RTH/ETH N/A en FX.
- **Líneas documento:** 1062 → 1362 líneas (incremento +300).
- **Encabezado §6:** marcado `POBLADO (Sesion-056)`.

### 2. **docs/planes/HANDOFF-OPUS-ULTRACODE-discriminacion-visual.md — §5 y §6 ESPECIFICADOS**
**Paso 3 del plan (ejecución) — especificación lista para implementación Opus/Claude:**

#### §5 — Motor `strength` Pine (UDTs + funciones puras + tabla de pesos)
- **Campos UDTs nuevos:** `SMC_Zone.strength`, `SMC_Event.strength`, `SMC_Swing.strength`, `SMC_Pool.strength`.
- **Funciones puras:**
  - `f_zoneStrength(zone: SMC_Zone) → float 0..1`
  - `f_eventStrength(event: SMC_Event) → float 0..1`
  - `f_strengthLevel(strength: float) → int 0/1/2` (cuantización: débil/normal/fuerte).
  - `f_mtfWeight(tf: string) → float` (D1=1.0, H1=0.7, M5=0.5).
- **Tabla candidata de pesos (CONGELADA hasta Fase 3):**
  - Por primitivo (BOS/CHoCH, OB, FVG, EQH/EQL, Sweep, Pool): ponderación según cuerpo%, distancia ATR, displacement, mitigación, contexto MTF.
  - Ejemplo: OB[cuerpo%] × ATR[proximidad] × sweep[0.8|1.0] = fuerza.
- **Lógica de MTF:** una zona del HTF (D1) que se repite exacta en TF inferior (H1) = elevada confianza; si diverge = ambigüedad → baja fuerza.
- **Exposición:** para visual (§6 siguiente) y para futuro scoring (Fase 3).

#### §6 — Jerarquía visual (master input `i_densidad`, `f_visualLevel`, z-order, cap top-N)
- **Input maestro `i_densidad`:**
  - `"Operación"` (solo Primario ↑ + Segundario gatillos actuales) = 3-5 marcas por gráfico.
  - `"Estudio"` (Primario + Secundario + Terciario contexto) = 12-20 marcas.
  - `"Todo"` (todos los conceptos, raw, sin jerarquización) = 35+ marcas.
- **Función `f_visualLevel(concept, tf_context) → int 1/2/3`:**
  - Primario: concepto+TF que gatilla entrada (BOS/CHoCH ruptura → sweep → liquidación en vela media actual).
  - Secundario: contexto inmediato (OB/FVG en H1 si M5 está dentro; EQH/EQL que confirma bias).
  - Terciario: frame MTF más grande (D1 estructura dominante, para diagnóstico).
- **Z-order antisolape:**
  - Nivel 1 (inferior): líneas estructura (BOS/CHoCH/Equilibrio).
  - Nivel 2 (medio): cajas (OB/FVG/Pools).
  - Nivel 3 (superior): marcas puntuales (Sweep ▲▼, IDM, eventos).
- **Cap top-N:** si `i_densidad="Operación"`, limita dibujable por TF a ~5 Primarios más activos (memoria última N velas).
- **Diagnóstico diferido de 3 arreglos MTF** (notas follow-up, NO bloquean):
  1. **Tag TF en BOS/CHoCH FUSIONADOS:** hoy BOS/CHoCH nativos + HTF se solapan sin distinguir origen. Solución: etiqueta `(D1)/(H1)` en los HTF, ausente en los nativos. Impacto visual: claridad cuándo vino la ruptura. Complejidad: extra label.
  2. **Cuadre fino EQH/EQL:** líneas punteadas azules entre velas pivote-a-pivote. Hoy cálculo de pivotes (high 5 barras atrás/adelante) puede fallar en vela 1 de la historia. Solución: guardia (≥5 barras disponibles antes de dibujar). Impacto: legibilidad +10%. Complejidad: baja.
  3. **Exactitud vela-a-vela OB/FVG:** hoy caja cubre "approximately" la zona válida. Precisión: vela CIERRE (open+close, no high/low) debe estar DENTRO OB body-range, y FVG MITAD DE VELA debe estar DENTRO FVG zone. Hoy: visual correcto, números off ~0.3 pips. Solución: refinar `top/bottom` con vela real OHLC vs rango Bid/Ask histórico. Impacto: 0 visual (ya se ve bien), valor numérico interno +5%. Complejidad: media (refactor f_computeTFState vela-a-vela).
- **Orden de implementación (§6.4):** 4 commits secuenciales:
  1. Commit A: UDTs + función strength base (Sin cambios visual).
  2. Commit B: `i_densidad` input + `f_visualLevel` + wiring Visual.
  3. Commit C: Z-order + cap top-N (Visual refinado).
  4. Commit D: 3 arreglos MTF diferidos (Fase 2+ cuando se integren resultados de D1 contexto validado).

### 3. **Commit**
- **bc9902f** — `docs(discriminacion): S056 — §6.3 poblado (35 conceptos) + spec strength/visual Pine`
  - Files: `docs/reglas-smc-ict.md`, `docs/planes/HANDOFF-OPUS-ULTRACODE-discriminacion-visual.md`.
  - Líneas: +422/-42 (neto +380).

---

## Estado de gates y decisiones

### F1-GATE (ampliado)
- **Status:** ABIERTO — requiere Paso 4 (implementación Pine) + validación visual graduada 4 ejes ≥90%.
- **Ejes a validar (orden):**
  - **Eje 0 (presencia/F1-GATE):** concepto existe y se dibuja correctamente → cumple el test "¿tá ahí?".
  - **Eje 1 (variante):** se detectó la variante correcta (no confundir OB con FVG, etc.) → cumple metodología §1.
  - **Eje 2 (fuerza):** strength score refleja realidad visual (débil=ruido, fuerte=confluencia real) → **REQUIERE CÓDIGO Paso 4** implementado.
  - **Eje 3 (invalidación):** cuando regla dice "invalida", el Pine DEJA DE MOSTRAR → cumple metodología §3.
  - **MTF descendente:** D1 contexto visible → H1 bias → M5 gatillo, sin duplicados → cumple MTF §2.

### Validación visual (próxima sesión)
- **Paso 4 (pendiente):** implementar en Pine el tag `strength` (toca CORE byte-idéntico) + jerarquía visual + 3 arreglos MTF (plan §6.4, ordenado en 4 commits).
- **Paso 5 (próxima sesión S057+):** ejecutar validación visual 1-a-1 sobre cada concepto.
  - Ejes 0/1/3 validables con Pine ACTUAL.
  - **Eje 2 (fuerza) BLOQUEADO en Paso 5 hasta que Paso 4 esté hecho** — sin código de `strength`, no hay scoring que validar.

### Decisión de la próxima sesión (usuario)
- **Opción A:** Arrancar Paso 4 implementación (Pine dev sprint 1.6 refinamiento) → requiere Opus + Loop compilación 0/0.
- **Opción B:** Ejecutar validación visual sobre Ejes 0/1/3 (Eje 2 deferred) con Pine actual → S057 + smc-validator-agent.
- **Ambas son correctas** (no son excluyentes, pero no paralelo); se alternan según urgencia.

---

## Estado del CORE

- **SHA-256:** `80fad14dd8d03758` — 1517 líneas, intacto desde S048.
- **Compilación:** 0 errores / 0 warnings (SMC-Visual.pine, SMC-Strategy.pine, SMC-Library.pine).
- **check-core-sync:** OK — ninguna divergencia entre Visual y Strategy.
- **Cambios sesión:** 0 (documentación solamente).

---

## Bloques

- **Ninguno.** Especificación lista, paso 4 requiere Opus (no bloqueante para sesión siguiente).

---

## Pendientes (Sesión 057+)

| Número | Descripción | Ejecutor | Prioridad |
|--------|-------------|----------|-----------|
| Paso 4 | Implementar strength + jerarquía visual + 3 arreglos MTF en Pine | Opus/Claude Loop | Alta |
| Paso 5 | Validación visual 1-a-1 de 40 conceptos (Ejes 0/1/3 ahora, Eje 2 post-Paso 4) | smc-validator-agent + usuario | Alta |
| NSL-2 | 2º mentor del enjambre | Opus/skill-builder | Paralela |
| Sesion-049 | F1-GATE visual (pendiente desde S049) | smc-validator-agent | Crítica (diferida) |

---

## Notas finales

- **Cambio documental sin implementación:** esta sesión fue especificación pura. CORE intacto, 0 toques Pine.
- **Metodología unificada:** §6 ahora una única capa (discriminación), no dos capas paralelas A/B. Plan S054 fusionaba caminos; S056 confirma la arquitectura.
- **Gotcha resuelto:** los "5 errores MTF" mencionados en S042 ya estaban cerrados antes de esta sesión; el plan S054 los mapeó a 3 arreglos diferidos legítimos (no bloquean F1-GATE).
- **Conflicto R:R:** NSL 1:2 vs sistema 1:3 será manejado por ADR-012 (validador de Norms descarta antes de mostrar en Conductor); NSL sigue siendo laboratorio/copiloto.

Ver [[Sesion-056]].
