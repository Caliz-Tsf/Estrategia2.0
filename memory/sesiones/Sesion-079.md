# Sesion-079 (2026-07-01)
> Módulo paralelo — Esqueleto Gradient Levels. Documento Marco Investigación + Especificación. NO toca Pine.

## Objetivo

Crear esqueleto de regla para familia Gradient Levels (T41-T44) basado en dossier S077 y codebase existente, cumpliendo convenciones del proyecto. Usuario instruyó "creas solamente el esqueleto" (no relleno completo de umbrales/casos EURUSD).

## Completado

### 1. Investigación de contexto codebase

Lectura exhaustiva:
- `docs/reglas-smc-ict.md` — formato de ficha §6.0, ejemplos §2.3/§5.10/§5.11/§6.3.x
- `pine/SMC-Library.pine` — UDTs, constantes `KIND_*` actuales (hasta 52)
- `WORKPLAN-MAESTRO-V2.md` §4.8 — catálogo 42 confluencias canónicas, candidatos #43-#51 asignados T26-T40
- `docs/planes/ESQUELETO-MITIGACION-conceptos.md` — patrones P1-P4 ciclo de vida conceptos
- `docs/planes/MATRIZ-conceptos-cobertura.md` — tabla de cobertura (NOTA: tabla "B1" citada por dossier S077 **NO existe físicamente** en archivo; es de S032 base NSL, 64 conceptos, no menciona gradient levels)

### 2. Análisis dossier S077

Lectura completa `docs/planes/DOSSIER-gradient-levels-para-ultracode.md`. Extracción:
- **Alcance núcleo:** T41 (grading quadrants/eighths) + T42 (confluencia exponencial) + T43 (FVG-válido-por-gradient)
- **Alcance diferible:** T44 (grading mecha REH/REL)
- **Reto central:** política determinista rango-fuente 3 niveles (Premium/Discount existente → suspension block diario → serie gaps apertura) + desempate objetivo: "test cuerpos-vs-nivel" (doctrina: cuerpos = order-flow institucional)
- **Doctrina verbatim:** trazas a madre-2026.md — grading january-12, confluencia exponencial february-11, FVG-válido february-11, jerarquía OB/parent march-13
- **8 preguntas diseño** del dossier a responder

### 3. Creación ESQUELETO-P4-gradient-levels.md

Entregable nuevo: `docs/planes/ESQUELETO-P4-gradient-levels.md` (commit `fa88f89`).

**§0 Alcance:**
- T41 (grading quadrants/eighths) — obligatorio
- T42 (confluencia exponencial) — obligatorio, BUT GOTCHA: mecanismo **multiplicador** post-hoc (NO aditivo puro)
- T43 (FVG-válido-por-gradient) — obligatorio
- T44 (grading mecha REH/REL) — diferible/opcional

**§1 Reto central resuelto:**
- Política rango-fuente: **3 niveles de prioridad con desempate objetivo**
  1. Premium/Discount EXISTENTE (SMC-Library.pine actuales)
  2. Suspension block DIARIO (newvo concepto)
  3. Serie gaps apertura EXISTENTE

- Desempate objetivo: cuerpos vs nivel (validación institucional)

**§2 Firmas CORE propuestas:**
- `KIND_GRADIENT = 53` (siguiente libre, tras KIND_SMT=52)
- UDT: `SMC_GradientGrid` (6 campos: levels, quadrant_index, eighths, premium_zone, discount_zone, source_level)
- 6 funciones CORE puras NUEVAS (todas `// TODO [impl]`, cero implementación):
  - `f_computeGradientLevels(...)` — calcula grid quadrants/eighths
  - `f_gradientZone(...)` — ubica precio en quadrant
  - `f_nearGradientLevel(...)` — nivel gradient más cercano
  - `f_bodyRespectsLevel(...)` — validación cuerpo-vs-nivel
  - `f_gradientConfluenceBonus(...)` — bonus confluencia exponencial
  - `f_selectGradientSource(...)` — resuelve política 3-niveles

**§3 Naturaleza de confluencia:**
- **T41 (grading quadrants/eighths):** herramienta/contexto, NO cuenta confluencia (como Standard Deviation §5.11)
- **T42 (confluencia exponencial):** candidata **#52** EN CATÁLOGO, BUT **mecanismo MULTIPLICADOR** (no aditivo):
  ```
  scoreDir_final = scoreDir_raw × (1 + gradientBonus)
  ```
  ⚠️ Esto CAMBIA el contrato de scoring: de aditivo-puro a aditivo+multiplicativo
  → **REQUIERE ADR NUEVO (candidato ADR-013)** ANTES de tocar `f_scoreConfluences` en Fase 2 (F2-T01)
  → Anotado en esqueleto §3
- **T43 (FVG-válido-por-gradient):** refinamiento FVG vía flag `gradedFvg` (patrón análogo `trueFvg`/`propulsion` existentes en `SMC_Zone`)

**§4-§5 Fichas regla canónicas + MTF:**
- 4 fichas de regla + 4 sub-fichas MTF — formato **exacto** reglas-smc-ict.md §6.0
- Ubicación futura: §5.16-§5.19 (reglas principales) + §6.3.36-§6.3.39 (MTF)
- Todos con slots `⏳ a cuantificar [impl]` / `⏳PENDIENTE-TVMCP`
- **CERO umbrales finales** — anotados como TO-DO para fase relleno
- **CERO casos EURUSD** — anotados como `[impl]` para extracción vía TV MCP (Sesion-080+)

**§6 Checklist procesal:**
- 7 pasos por concepto (ciclo canónico T01-T40):
  1. Especificar regla cuantificada (§5)
  2. Crear UDT + constantes (§2)
  3. Implementar funciones CORE puras
  4. Wiring Visual + Strategy
  5. Compilar 0/0 + core-sync
  6. Validar smc-validator-agent ≥90
  7. Commit + gate aprobado

**§7 Respuestas a 8 preguntas diseño del dossier:**
- P1 ¿Cómo priorizar rango-fuente? → Política 3-niveles + desempate cuerpos
- P2 ¿Multiplicador o aditivo? → Multiplicador (ADR-013 pendiente)
- P3 ¿FVG-válido cómo se valida? → Toca gradient level (doctrina feb-11)
- P4 ¿Gradient levels mecha? → T44 diferible
- P5 ¿Índices sólo o en rules? → Índice-only T42 candidato #52
- P6 ¿Escala octavos o cuartos? → Eighths (finer-grain doctrina)
- P7 ¿Pre-UB o post-UB? → Pre (candidato #52 confluencia, no entry)
- P8 ¿Distintos pares diferente grid? → SÍ (symbol-agnóstico ADR-001, grid = pares por ATR histórico)

**§8 Verificación restricciones duras:**
- ✅ Anti-repaint: funciones puras, sin state futuro
- ✅ Core byte-idéntico: UDT + KIND + funciones AISLADAS (sin tocar `f_scoreConfluences` hasta ADR-013)
- ✅ Funciones puras: sin estado mutable, sin llamadas request.security() internas
- ✅ Símbolo-agnóstico: grid relativo a ATR histórico, no hardcoded
- ✅ Sin duplicar: KIND_GRADIENT único, UDT SGradientGrid único
- ✅ Sin inflar confluencias: T41 = contexto (0 confluencias), T42 = 1 confluencia (#52), T43 = refinamiento (0 nuevas)
- ✅ Pesos congelados Fase 3: weight T42 = 1.0 + multiplicador (exacto, no optimizable Fase 3)

**§9 Integración pendiente (deliberadamente NO ejecutada, por instrucción usuario):**
- (a) Añadir familia a `MATRIZ-conceptos-cobertura.md` — **NOTA:** tabla "B1" que dossier S077 citaba como existente NO está en archivo (es de S032 NSL base, 64 conceptos); anotado como pendiente
- (b) Añadir T41-T44 a `docs/workplan/PINE-PLAN.md` §7
- (c) Nota expansión WORKPLAN-MAESTRO-V2.md §4.8 (candidato #52)
- (d) Escribir ADR-013 cuando se cierre wiring T42 (FUTURO, no antes de relleno)
- (e) Actualización ESTADO-ACTUAL.md (que estás haciendo)

## Verificación

`scripts/check-core-sync.ps1` → **OK**
- CORE 1517 líneas SHA `80fad14dd8d03758` (sin cambios, ningún `.pine` tocado esta sesión)
- Compila 0/0 los 3 archivos
- core-sync OK

**NO hubo cambios Pine.** Módulo paralelo esqueleto.

## Commits de sesión

1. **`fa88f89`** `docs(planes): S079 esqueleto Gradient Levels (T41-T44) resuelve dossier S077`

## Pendiente para próxima sesión

**S080 — USUARIO ELIGE:**

**OPCIÓN A — Retomar pendientes S077 infraestructura/enjambre PRIMERO:**
1. Reiniciar Claude Desktop → verificar 8 MCP responden
2. Reiniciar Hermes gateway → verificar 4 MCP + env propagado
3. openWakeWord: `start-voice.ps1 -DryRun`, grabar clips, entrenar verifier
4. BOXXO descarga: gate indicators 1-5, validar pipeline
5. Enjambre: 6 tareas S074 (si usuario prioriza)

**DESPUÉS (S080+):** Claude Code inicia relleno Gradient Levels bajo gate [[sprint16-gate-reglas-antes-de-codigo]]
- Extracción casos EURUSD vía TV MCP
- Cuantificación umbrales reglas
- Poblado completo §5.16-§5.19 + §6.3.36-§6.3.39
- Implementación T41-T44 (después de reglas cuantificadas)

**OPCIÓN B — Empezar relleno Gradient Levels AHORA:**
- S080 arranca extracción EURUSD (casos, umbrales, reglas) vía TV MCP
- Relleno esqueleto completo
- Implementación T41-T44

## Decisiones

- **NO decisiones arquitecturales nuevas.** Sesión = esqueleto + especificación.
- **Candidato ADR-013:** mecanismo multiplicador confluencia T42 (FUTURO, no ahora; anotado para cuando se cierre wiring real).
- **NO se tocó dossier S077:** entregable anterior; usuario decide siguiente paso.

## Bloqueos

Ninguno. Esqueleto especificado, listo para relleno (S080+).

## Notas

- **Módulo PARALELO:** 0 commits Pine. CORE INTACTO (1517 líneas SHA `80fad14dd8d03758`, compila 0/0 los 3, core-sync OK).

- **Convención cumplida:** esqueleto sigue plantilla ESQUELETO-P1/P2/P3/MITIGACION (fichas regla canónicas + checklist procesales + verificación restricciones).

- **Hallazgo documental:** tabla "B1" MATRIZ-conceptos-cobertura que dossier S077 citaba como existente NO está. Base actual = S032 (NSL 64 conceptos), no menciona gradient levels. Anotado como pendiente (no bloquea esqueleto).

- **Ruta relleno:** S080+ Claude Code inicia extracción EURUSD bajo gate [[sprint16-gate-reglas-antes-de-codigo]] (precedente = T01-T40). Reglas cuantificadas ANTES de código; casos verificados EURUSD.

- **Próxima sesión:** Usuario elige entre (a) retomar infraestructura S077 primero, O (b) iniciar relleno esqueleto ahora. Instrucciones en ESTADO-ACTUAL.md §Cómo-arrancar.

---

Cerrada por: Claude Code (Haiku 4.5)
Fecha: 2026-07-01 22:45 UTC
Módulo: Paralelo (no-Pine)
Estatus: ESQUELETO ENTREGADO, RELLENO DIFERIDO A S080+
