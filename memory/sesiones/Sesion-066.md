# Sesion-066 — Mentor ICT OTE Pattern Recognition (20/20) COMPLETO

**Fecha:** 2026-06-29  
**Objetivo:** MENTOR ICT (madre) — OTE Pattern Recognition lectura íntegra cerrada al 100%. Alcance usuario AMPLIADO: no "muestra densa", leer TODOS los capítulos íntegros como se hizo con NSL. Decisión operativa: **un curso por sesión**.

## Completado

### Tarea Principal: OTE Pattern Recognition (20/20) ✅
- **Leídos COMPLETOS los 16 volúmenes que faltaban** (vol 04–19). Antes solo había muestra de 01/02/03/20.
- **Hallazgo clave:** la afirmación previa "el modelo se agota en Vol 01, los demás no aportan reglas" era **FALSA**. Los ejemplos 04–19 traen matices operables que la muestra dejaba fuera → valida la decisión del usuario de leer todo íntegro.
- **Refinamientos nuevos identificados en 04–19:**
  - Nivel **−1.5 std dev** en la escala de scaling (peldaño regular, ausente de la 1ª destilación; Vols 10/11/13/17/19).
  - **Regla LEADER 80/20:** override del colapso en −2 cuando el bias del diario sostiene objetivo mayor (gap por llenar, equal highs/lows lejanos). Vols 16/17/18.
  - **Mercado SIN tendencia:** OTE operable solo con volatilidad intradía, sin bias diario (Vol 04, breaker + Judas + proyectar la vela = market efficiency paradigm).
  - **Gap como imán / draw-on-liquidity + bias por llenado de gap** (Vol 16, crudo): la dirección de llenado del gap = modelo de bias para el día siguiente.
  - **Shallow run / unfinished business** (Vol 09): sweep parcial deja liquidez pendiente; dos shallow runs = primed para el movimiento grande. Que el precio ya pasara el PDH/PDL NO anula la entrada NY.
  - **Selección de price-leg por displacement + volumen-en-cuerpos** = la "signature" (Vol 13/14): elegir el swing con displacement limpio y volumen en cuerpos (no mechas), no el high más alto. Sin indicadores en el chart.
  - **Sobreventa/sobrecompra irrelevante** (Vol 13): el mercado busca liquidez por extendido que parezca; equal lows = "candyland".
  - **Filosofía de parciales "págate a ti mismo"** (Vol 15): analogía de la semana laboral; market-order en ganancia > esperar target no entregado.
  - **62% = low-hanging-fruit** (Vol 14): usar 62% por defecto, no estirar al 70.5/79 (riesgo de perder fill / spread).
  - **Trade CONTRA el retail = ~90% del edge** (Vol 04/06/07/16/19): tomar la vista opuesta a la opinión obvia del retail (S/R clásico, doji/pinbar, equal highs como "stops protegidos") = donde está la liquidez objetivo.
  - **Bonos del Tesoro (Vol 18):** el MEJOR mercado para stops ultra-cortos (4–6 ticks) por sus movimientos limpios; "le gana a forex/índices/cripto".

### Documentación Actualizada
**Archivo:** `D:\obsidian\boveda MENTE\Mente\Mentores\ict\knowledge\ote.md` (VAULT, fuera de git)
- Header de cobertura: corregido a **20/20 vols leídos íntegros**; corrección explícita de la afirmación errónea previa.
- **§5 NUEVA** "Conceptos y refinamientos nuevos de los ejemplos 04–19" con los 11 matices de arriba.
- **Paso 5 (escalado):** escala completa old high/low (≈1:1) → −0.5 → −1 → **−1.5** → −2, + regla del LEADER 80/20.
- Sección de tensiones/notas: **candidatos Pine nuevos** añadidos bajo gobernanza [[sprint16-gate-reglas-antes-de-codigo]]:
  - shallow-run (sub-regla de sweep/pools, refina Q2/Q4 de [[ADR-012]])
  - signature (selección de price-leg por displacement + volumen → tag de fuerza, Eje 2)
  - gap-as-bias (solapa T30 Opening Gaps; el matiz es el gap como imán direccional/bias)
  - equal lows/highs "candyland" como objetivo de liquidez de alta calidad
  - regla leader 80/20 = gestión TP (Fase 4 / EA), no detección

### Estado Pine (Paralelo)
- **CORE INTACTO:** 1517 líneas, SHA `80fad14dd8d03758`, compila 0/0 los 3 (SMC-Library, SMC-Visual, SMC-Strategy).
- **core-sync.ps1:** OK — ninguna divergencia.
- **0 commits Pine en esta sesión** — módulo mentores es paralelo.
- Commits anteriores mentores vigentes: `a960feb` (yt-dlp android + reintentos) + `35efc33` (visión WorkDir/PID) + `4094839` (audio fix) + `bdbd36c` (visión NVIDIA).

## Siguientes Tareas

### Barrido Íntegro de Cursos — Un Curso por Sesión
**Decisión usuario:** leer TODO íntegro (revocada la "muestra densa"). Secuencia:
1. **✅ 2022 Mentorship:** 41 episodios (S062).
2. **✅ MMP (Market Maker Primer):** 24 vols (S063).
3. **✅ OTE Pattern Recognition:** 20 vols (S066 — HOY).
4. **Sesion-067 PRÓXIMA:** **2024 Mentorship — ~46 archivos** (era NQ/index futures + tape-reading, 100–270KB c/u).
5. **Luego:** 2026 madre (67 lecciones — aún solo iteración 1 = 4 de 67).

### Post-Lectura Íntegra — REDUCE + Refresh Agente
Una vez completado el barrido (S067 + 2026):
- **REDUCE nuevo:** `ficha-mentor.md` v2 integrando 2026+2022+MMP+OTE+2024 (la actual es PROVISIONAL).
- **Refresh 4 piezas del agente ICT** (perfil Hermes / swarm.yaml / skill `mentor-ict` / track-record + E2E): los SKILL.md incrustan la ficha → regenerar con la ficha definitiva.

## Bloqueos
Ninguno.

## ADRs Nuevos
Ninguno (módulo mentores, no arquitectura Pine).

## Notas
- Conflicto R:R: OTE relativiza el ratio ("1:1 vale por frecuencia") vs la regla dura 1:3 del proyecto — OTE es laboratorio/copiloto per ADR-005, no recalcula en Norms. NO adoptar el 1:1.
- Pipeline boxxocode sin muro anti-bot (S061 `a960feb`).

## Commits Sesion-066
Cierre documental (ESTADO-ACTUAL + Sesion-066 + track-record-ict). Ningún commit Pine.

## Pendiente Usuario
Ninguno formal. Próxima sesión = S067 iniciar 2024 Mentorship (~46 archivos).
