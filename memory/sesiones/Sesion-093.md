# Sesion-093 (2026-07-04)

## Objetivo
Resolver el fork abierto en Sesion-092 (punto F) respecto al rediseño arquitectónico de Fable: decidir si la Fase A (rediseño visual) entra ANTES de firmar F1-GATE o después. Escribir la doctrina de los 3 primitivos cuantificados (`posRole` / `confDegree` / `depthBand`) y las 40 fichas de confluencia como nueva sección §7 de `reglas-smc-ict.md`, bajo gate [[sprint16-gate-reglas-antes-de-codigo]].

## Completado

### Tarea 1: Aclaración doctrina con el usuario
**Resultado:** RESUELTO. El usuario confirmó:
1. El rediseño (Fase A Visual-only) entra **ANTES** de firmar F1-GATE, no después.
2. El §10 (checklist #1-#12) está cerrado técnicamente (S089-S092) sin necesidad de código nuevo.
3. La firma F1-GATE espera a que A-7 cierre la parte visual del rediseño.

**Aclaración doctrina clave:** §7 es capa ADITIVA sobre §1–§6. NO reescribe la detección (§1–§5 intacta) ni el grading (§6 intacto). Es una lectura nueva de la detección existente a través de 3 primitivos, con llave de orden de render que reemplaza score-render antiguo. Moduladores/lecturas mantienen el estatus de "strength" (ADR-014 §3, 42 confluencias sin infla).

### Tarea 2: Escribir §7 "CAPA DE PROYECCIÓN / CONFLUENCIA"
**Commit:** `6dea79f` (doc-only, CORE INTACTO 1700 líneas SHA `5510361166844bd5`)

**Entregable:** `docs/reglas-smc-ict.md §7` (NUEVA, 488 líneas) — capa de proyección/confluencia.

**Estructura §7:**

#### §7.0 — Primitivos cuantificados
- **`posRole`** (3 estados):
  - 0 = INTERNO (tolPos = 0.5×ATR, posLookfwd = 20, desempate = más cercano en barra actual)
  - 1 = GIRO (zona de transición entre interno y origen)
  - 2 = ORIGEN (desempate GANA si hay conflicto, marca máxima relevancia estructural)
  
- **`confDegree`** (1..3, saturación):
  - tolConf = 0.25×ATR = labelClusterTol (distancia máxima entre etiquetas para contar cluster)
  - 7 familias de confluencias cuentan sus instancias
  - ≥2 clusters = promoción (visible siempre, confDegree=2 mínimo de draws "inteligentes")
  - 1 = aislado / 2 = pareado / 3 = triple (saturado)
  
- **`depthBand`** (1..5):
  - Cortes 0.33, 0.66, 1.0 sobre dealing range vigente
  - "3 por lado = mínimo no cap" (band 3 = centro, 2 arriba, 2 abajo + opcionales 4/5)
  - Input `i_profundidad` (3→5, default 3, activa bandas 4/5 visuales)

**Candidatos CONGELADOS:** ADR-002 (todos estos primitivos son candidatos finalizados, no para Fase 3).

#### §7.1 — Llave visual + Guardián de draws
**Fórmula render:**
```
score_render_v2 = strength × wPos(posRole) × (1 + kConf × min(confDegree, 3))
```

**Pesos:**
- wPos: ORIGEN=1.0, GIRO=0.9, INTERNO=0.35
- kConf = 0.25 (multiplicador de confianza)

**Guardián de draws:**
- Una instancia con confDegree≥2 O pool alineado al bias del indicador = **INMUNE al recorte** por distancia/frescura
- Esto mantiene vivo el BSL·3 D1 ~1.51 (pool cluster, no descartable)
- P/D es **contexto de razonamiento**, JAMÁS se recorta por orden del guardián

#### §7.2 — 40 Fichas (7.2.1–7.2.40) en 7 familias A1–A7
**Familia A1 – Estructura (fichas 1–7)**
- 7.2.1 Breaking Of Structure (BOS)
- 7.2.2 Change of Character (ChoCH)
- 7.2.3 Equal High / Equal Low (EQH/EQL)
- 7.2.4 Higher High / Lower Low (HH/LL)
- 7.2.5 Range Reset / Equilibrium
- 7.2.6 Swing Highs/Lows (validación cuerpos)
- 7.2.7 Session Anchors (apertura sesión, vela #1)

**Familia A2 – Order Blocks (fichas 8–13)**
- 7.2.8 OB Bullish (formación, edad, validación breaker)
- 7.2.9 OB Bearish (formación, edad, validación breaker)
- 7.2.10 OB Parent vs Propulsion (jerarquía)
- 7.2.11 OB Mitigación (BS/MI reconfiguración)
- 7.2.12 OB Premium/Discount (contexto P/D)
- 7.2.13 Sweep Confirmation (vela cruza low, cierra fuera)

**Familia A3 – FVG (fichas 14–20)**
- 7.2.14 Fair Value Gap (definición, 3 cuerpos)
- 7.2.15 TrueFVG (FVG inmitigado, sin precio tocando)
- 7.2.16 InvertedFVG (inversión de roles, precio regresa)
- 7.2.17 FVG Mitigación (llenado, cierre, reapertura)
- 7.2.18 FVG Gradient (validación contra grid, T43)
- 7.2.19 FVG Reclaimed (precio cruza, cierra fuera)
- 7.2.20 Breaker Pools (FVG roto en nueva dirección)

**Familia A4 – Liquidez (fichas 21–27)**
- 7.2.21 Pools (acumulaciones, objetivos)
- 7.2.22 Supply/Demand Zones (contexto P/D)
- 7.2.23 Kill Zones (sesión actual, ribbon KZ)
- 7.2.24 Relative Depth (bandas 1-5 del rango)
- 7.2.25 Wicks (roce, respeto a nivel)
- 7.2.26 Volume Profile (VWAP, volúmenes)
- 7.2.27 Liquidation Levels (matriz riesgo)

**Familia A5 – P/D+Gradient (fichas 28–31)**
- 7.2.28 Premium Zone (arriba EQ+eighths)
- 7.2.29 Discount Zone (abajo EQ+eighths)
- 7.2.30 Gradient Levels (T41, eighths del ORG)
- 7.2.31 Gradient Confluence (T42, multiplicador exponencial)

**Familia A6 – Gaps apertura (fichas 32–35)**
- 7.2.32 Opening Range (30min RTH/ETH)
- 7.2.33 Opening Gap (discontinuidad precio)
- 7.2.34 Gap Projection (proyección desplazamiento)
- 7.2.35 Gap Mitigation (reacción, objetivos)

**Familia A7 – Contexto (fichas 36–40)**
- 7.2.36 MTF Bias (procedencia multitimeframe, herencia correcta)
- 7.2.37 Session Type (RTH/ETH, macro, sesión)
- 7.2.38 Time Distortion (TF switch para revelar ineficiencia)
- 7.2.39 Probability Gate (one-sided vs two-sided, riesgo)
- 7.2.40 Narrative (orden de raids, cierre de día)

**Cada ficha contiene:**
- Lee-atrás (sección que cita su regla base §1–§6)
- posRole requerido {0,1,2}
- confDegree objetivo {1,2,3}
- depthBand preferida {1..5}
- Proyección + outcome verificable (§4.3 del plan de validación)
- MTF/modo mínimo (H1 / Operación, etc.)
- **[Extracción TV…]** — placeholder para casos reales EURUSD (PENDIENTE)
- Nota: cada ficha cita su regla base, NO reescribe

## Pendiente pre-código (gate sprint16)

### Punto 1: Pasada TV concentrada — ~10 casos EURUSD por familia
Para cada familia A1–A7, extraer niveles reales EURUSD H1:
- **Depthband 1/2/3:** niveles arriba y abajo del precio actual
- **ConfDegree≥2 clusters:** ≥2 instancias (OB+FVG+pool) dentro de ±0.25×ATR
- **ConfDegree=1 contraejemplo:** instancia aislada sin pareja
- **Bandas 4/5:** 2 rangos históricos previos para validación opcional

Marcar los casos extraídos en las fichas respectivas (reemplazar `[Extracción TV…]`).

### Punto 2: Aprobación usuario por familia
Tras completar punto 1, usuario confirma cada familia A1–A7 como VALIDADA (gate lo exige).

## Commits realizados
- **`6dea79f`** — docs(reglas): S093 — §7 "CAPA DE PROYECCIÓN / CONFLUENCIA" completa (488 líneas, 3 primitivos + 40 fichas + llave render v2 + guardián draws). Doc-only, CORE INTACTO.

## CORE status
- **SHA:** `5510361166844bd5` (1700 líneas)
- **Compilación:** 0 errores / 0 warnings (todos 3 scripts: Library, Visual, Strategy)
- **core-sync.ps1:** OK

## Bloques / Decisiones

**Bloqueante:**
- Nada (sesión de doctrina completa, 0 código Pine).

**Decisión registrada:**
- [[Sesion-093]]: Rediseño Fase A entra **ANTES** de firmar F1-GATE (resuelve fork S092 punto F).

## Siguiente sesión (S094)

**Orden estricto:**
1. **Pasada TV concentrada:** extraer ~10 casos EURUSD por familia (7 familias A1–A7), niveles reales depthBand 1/2/3, confDegree≥2 clusters + contraejemplo confDegree=1.
2. **Aprobación usuario:** confirmar cada familia.
3. **Arranque Fase A — pasos A-1…A-7** en `SMC-Visual.pine` (nada en CORE):
   - A-1: f_depthBand + i_profundidad
   - A-2: f_posRole
   - A-3: f_confDegree
   - A-4: f_renderScoreV2 + selección OB/FVG
   - A-5: Breaker + IDM + promoción
   - A-6: guardián draws + reserva desalojo §6.5
   - A-7: estructura/EQ re-llaveados + bandas 4/5

**Meta:** A-7 cierra la parte visual → **firma F1-GATE**.

**Fase B** (promover primitivos al CORE) abre **Fase 2** con ADR nuevo.

## Notas

- El usuario indicó explícitamente: "Cerrar doctrina aquí; S094 continúa con punto 2 + arranque A-1."
- No hay checkboxes de WORKPLAN que marcar (§7 es doctrina, no tarea T-numerada).
- No hay ADR nuevas generadas en esta sesión (ADR-014 ya existe desde S083; primitivos congelados en ADR-002).
- 0 código Pine tocado: documentación pura.
