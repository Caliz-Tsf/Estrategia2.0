# Sesion-098 — 2026-07-06
> Cierre: Esqueleto Fable Fase 4 EA MT5 entregado + catálogo de imágenes confluencias

## Resumen ejecutivo
**Entrega: ESQUELETO-FABLE-fase4-ea-mt5.md (separada del workplan, pendiente revisión usuario "punto 3") + catálogo de 48 imágenes confluencias con mapeo a familias §7.2 + plantillas swarm/EA.**

Respuesta de Fable (Claude Code) al DOSSIER-FABLE-fase4-ea-mt5.md de S097. Usuario proporcionó 48 imágenes de referencia confluencias SMC/ICT + clarificaciones doctrinales adicionales; todas incorporadas ANTES de redactar. CORE Pine intacto 1700 líneas SHA `5510361166844bd5`, compila 0/0, core-sync OK. **1 commit doc-only: `8c08849`.**

---

## Entregables

### 1. ESQUELETO-FABLE-fase4-ea-mt5.md (NUEVO)
**Ubicación:** `docs/planes/ESQUELETO-FABLE-fase4-ea-mt5.md`

**Estructura (8 bloques A–H + anexos):**

#### Protocolo de relleno (§0.1–§0.3)
- §0.1: **Protocolo para IA en frío** — cómo rellenar el esqueleto sin contexto previo (lectura de 5 fuentes: reglas-smc-ict.md §7, DOSSIER S097, este ESQUELETO, imágenes catálogo, filas congeladas ADR-002/ADR-014).
- §0.2: **Contexto en frío** — síntesis DOSSIER S097 (propósito: definir capa cognitiva/decisional EA, integración enjambre→EA).
- §0.3: **Respuesta a pregunta abierta** (del DOSSIER): doctrina unificadora = reglas-smc-ict.md §7 es fuente única; 3 compiladores (Pine→MQL5, visuales, reglas), 2 capas (gates determinista capa 1 / ponderación darwiniana capa 2; el darwiniano NUNCA anula gates).

#### Bloque A — Capa determinista EA
- **A-1:** Módulo SMC_Cognition.mqh (arquitectura entrada/procesamiento/salida, anti-repaint, árbol de decisión gates).
- **A-2:** Persistencia (estado vela a vela, no reset al cambio TF, snapshots vivos para TV vivo-validación).
- **A-3:** Golden tests (paritoria Pine→MQL5, casos EURUSD §7.2 emparejados).

#### Bloque B — Percepción (MarketState)
- **B-1:** Capas percepción: D1 (bias macro/contexto), H1 (estructura/soporte), M5 (timing/entrada).
- **B-2:** Pipeline por vela (lectura D1/H1/M5 en orden, cumulativa, sin retroactivos).
- **B-3:** InfoRequest (módulo solicitud de datos: noticias, calendario, spread, riesgo país) — **A SOLICITUD del EA** (no confluencia, veto de riesgo).

#### Bloque C — Score direccional
- **C-1:** ComputeDirectionalScore (espera Fase 2; hoy stub).
- **C-2:** Exactitud de proyección acumula evidencia (métrica: cuántos ticks hacia TP antes de girar).
- **C-3:** Pesos por confluencia NO se cambian vivo (solo orden ADR, no cambio durante sesión).

#### Bloque D — Score de perfiles (darwiniano)
- **D-1:** Formato lectura perfiles (mentor ICT, Wyckoff, Chart Fanatic, NSL).
- **D-2:** Métrica exactitud (derivada de §7.2: posRole×confDegree×depthBand cuantificados).
- **D-3:** Confluencia = NO consenso; voto por accuracy (mejor razonador gana, no mayoría).
- **CONTRADICCIÓN RESUELTA:** NSL pitch 1:2 vs regla dura #5 1:3 → **gate minRR (default 3.0) es mandatario** (usuario puede bajar a 1:2 bajo orden + ADR-015, pero default respeta regla).

#### Bloque E — Debate enjambre (ORQUESTADOR)
- **E-1:** Protocolo 7 pasos (captura D1/H1/M5 → narración → ronda olas-de-3 → registro → decisión → validación diferida → cristalización).
- **E-2:** CRISTALIZADAS.md como **única frontera** enjambre→EA (nunca en caliente; EA lee documento al inicio sesión + sobre demanda).

#### Bloque F — Cuaderno del decisor
- **F-1:** Formato compilado (ejecutable, no prosa).
- **F-2:** Checklist pre-entrada (7 preguntas obligatorias).
- **F-3:** Lista NO-entrar (contra-patrón, fractales bajistas, sesión cerrada).
- **F-4:** Máquina de estados zona (APPROACHING → TESTING → CONFIRMED → INVALIDATED / EXPIRED; ramas agresiva vs confirmada).
- **F-5:** Canónico "entrada en origen": sweep→MSS→retorno confDegree≥2, posRole=ORIGEN→desplazamiento; swing completo vía TP1≥minRR + trailing/re-proyección.

#### Bloque G — Bucle cognitivo (8 pasos)
- Tabla: paso → módulo MQL5 → ficha reglas (§7.2.X).
- Nota transversal: anti-repaint en CADA paso (no solo entrada).

#### Bloque H — Fases (4→adelante)
- **F4-LAB:** Laboratorio enjambre paralelo pre-Fase4 (no depende Pine/MQL5; requiere roster probado 1:1 según ESQUELETO-P2 §2).
- **F4.0:** Esqueleto código POST-Fase 2 (módulos CORE vacíos + estructura compilable).
- **F4.1:** Cognitiva (relleno bloques A–G).
- **F4.2:** Traducción F4-GOLD (validación paritoria contra TV).
- **F4.3:** Tester MT5 + 60d demo vivo (F4-DEMO gate).
- **F4.4:** 30d live (F4-LIVE gate).
- **F5:** Multi-símbolo (Fase 3 repetida por símbolo, sin saltar gates).

#### Anexos (§9–§12)
- **§9:** Gate minRR (regla #5, parametrizable, default 3.0).
- **§10:** 4 diagramas Mermaid (decisión EA, flujo datos, máquina estados, ciclo cognitivo).
- **§11:** Tabla cumplimiento 8 restricciones duras (anti-repaint, core byte-idéntico, puro, agnóstico, sin duplica, 42 sin infla, pesos congelados, R:R≥minRR).
- **§12:** Congelados (ADR-002, ADR-014 + nuevos si aplica), parámetros a cuantificar (k, wPos, tolXXX), resumen marcadores.

---

### 2. Catálogo de imágenes confluencias
**Ubicación:** `confluencias/imagenes-referencia/`

**Contenido:**
- **48 imágenes** (de usuario; 2 anotadas como duplicados).
- **CATALOGO.md** (NUEVO):
  - 16 modelos M1–M19 (idealizados, hand-drawn).
  - Mapeo a familias §7.2 (40 fichas, 7 familias A1–A7).
  - Modelos cubiertos:
    - BOS + FVG + OB primario (entrada).
    - Sweep + MSS + OTE + OB "entrada en origen" (swing completo).
    - QM (Quick Move).
    - Sweep + IDM + perfil.
    - Liquidity grab (sell liquidity, buy liquidity).
    - CHoCH vs BOS (diferencias).
    - Breaker.
    - Fakeout / reversal giro.
    - IFVG (inversa).
    - AMD (acceleration/mispricing).
    - Doble top/bottom + MSS mitigación.
    - OB trap / falso breakout.
    - Mitigation block (confDegree≥2).
    - Trendline liquidity + rejection.
    - R:R por tipo de entrada (1:3, 1:5).
  - **§4 Plantilla narración orquestador** (6 pasos):
    1. Contexto D1 (bias, estructuras previas).
    2. Estructura H1 (rango, giro, focos).
    3. Timing M5 (candidatos entrada, zonas críticas).
    4. Narracion (cuento = lógica inteligible).
    5. Evidencia (cuáles fichas §7.2 se aplican, cuáles no, por qué).
    6. Conclusión (entrada SÍ/NO, si NO: abstención).
    - **Ejemplo:** formalización del razonamiento usuario de S098 (desglome paso-a-paso).

**Regla de procedencia:** imágenes = REFERENCIA DE RAZONAMIENTO (visualización intuitiva de la lógica §7.2), **JAMÁS fuente de umbrales** (gate sprint16 intacto: umbrales viven solo en reglas-smc-ict.md).

---

### 3. Plantillas swarm + EA
**Ubicación:** `confluencias/swarm/` + `confluencias/ea/`

#### confluencias/swarm/
- **README.md:** Rol orquestador, protocolo debate 7 pasos, qué lee EA (CRISTALIZADAS.md).
- **TEMPLATE-debate.md:** Plantilla relleno sesión swarm:
  - Cabecera (fecha, símbolo, TF, bias D1/H1).
  - Narración (6 pasos plantilla CATALOGO).
  - Ronda olas-de-3 (opiniones de 3 agentes mentores).
  - Decisión (mayoritaria por accuracy, veto minRR).
  - Validación diferida (vs TV VIVO después 1h/4h).
  - Score darwiniano (exactitud proyección).
  - Cristalización (documento CRISTALIZADAS.md).

#### confluencias/ea/
- **README.md:** Cuaderno decisor, máquina estados, checklist pre-entrada.
- **TEMPLATE-operacion.md:** Plantilla operación concretada:
  - 7 preguntas obligatorias (precio, zona, R:R, posRole, confDegree, horizonte, riesgo).
  - Abstención (si falta dato, si riesgo > umbral, si mercado cerrado).
  - Seguimiento (TP1, trailing, TP final, cierre + "cuánto swing dejado en mesa").

---

## Decisiones del usuario S098 (registradas en esqueleto, no tocan docs vigentes)

1. **minRR parametrizable, default 3.0:**
   - Regla dura #5 (R:R ≥ 1:3) queda **INTACTA**.
   - Usuario puede cambiar valor a 1:2 (lab) o 1:5 (conservador) vía orden explícita + ADR-015.
   - **ADR-015 PROPUESTO** ("minRR parametrizado"), **NO escrito en S098** (se redacta cuando usuario ordene cambio).
   - Meta largo plazo: swing completo vía trailing, no subiendo minRR.

2. **Orquestador toma D1/H1/M5 como capas percepción:**
   - D1 = bias macro (qué dirección es más probable).
   - H1 = estructura (dónde están los swings, nodos).
   - M5 = timing (cuándo entrar, zona operacional).
   - Debate abierto en las 3 temporalidades.
   - TV vivo valida qué se cumplió (nunca replay TV, es de pago; replay solo MT5).

3. **Enjambre→EA frontera única es CRISTALIZADAS.md:**
   - Documento generado sesión de debate enjambre.
   - EA lo lee al inicio sesión + sobre demanda (consultas "¿entro en zona X?" → busca precedente cristalizado).
   - **Nunca en caliente** (enjambre no toca EA en vivo).

4. **EA puede solicitar información:**
   - Noticias, datos económicos, spread/volatilidad, riesgo país.
   - Propuesta usuario: InfoRequest vía calendario MT5 + query API (OANDA, Reuters, etc.).
   - Implementación diferida F4.1 (hoy stub en esqueleto A-B3).

---

## Pendientes (sin cambio respecto S097)

1. **Revisión usuario del esqueleto ("punto 3"):**
   - Usuario revisar ESQUELETO-FABLE-fase4-ea-mt5.md + CATALOGO.md + plantillas.
   - Decisión: qué se integra workplan, qué se rechaza, qué se modifica.

2. **Validación viva Fase A (TV):**
   - Familia-por-familia D1/H1/M5 (apagar resto → todo encendido).
   - Checklist §10 (#1-#3 densidad, #8 ocultos, ≤25/60).
   - Firma F1-GATE (usuario).

3. **F4-LAB (laboratorio enjambre):**
   - Puede arrancar cuando usuario quiera (paralelo a Pine/MQL5).
   - Requiere roster de 3+ mentores probados 1:1 (ESQUELETO-P2 §2).
   - No bloquea nada del workplan.

---

## Cambios a reglas/arquitectura

**NINGUNO.** Todas las decisiones quedan en el esqueleto (documentación separada del workplan). Regla dura #5 intacta. Arquitectura 2 capas (gates + darwiniano) confirmada por doctrina.

**ADR pendiente:** ADR-015 "minRR parametrizado" (solo propuesto, no escrito; requiere orden usuario).

---

## Commits

- **`8c08849` (2026-07-06):** `docs(fase4): S098 ESQUELETO-FABLE-fase4-ea-mt5 + catalogo imagenes confluencias + plantillas swarm/EA`
  - ESQUELETO-FABLE-fase4-ea-mt5.md (8 bloques + anexos).
  - confluencias/imagenes-referencia/CATALOGO.md (16 modelos, plantilla narración).
  - confluencias/swarm/TEMPLATE-debate.md + README.md.
  - confluencias/ea/TEMPLATE-operacion.md + README.md.
  - +628 líneas, 57 archivos.
  - CORE INTACTO 1700 líneas SHA `5510361166844bd5`, core-sync OK.

---

## Notas técnicas

1. **Métrica exactitud (scoring darwiniano):** derivada de §7.2 — proyección: posRole×confDegree×depthBand cuantificados. Score = `(ticks al TP antes de giro) / (ticks esperados segun R:R)`.

2. **CRISTALIZADAS.md estructura:** documento de texto plano (lectura EA, no JSON). Líneas: `[FECHA] [SÍMBOLO] [TF] [NARRACIÓN] [DECISIÓN] [ACCURACY]`. EA busca por timestamp/símbolo/TF más reciente.

3. **Anti-repaint en bucle cognitivo:** cada paso (E1–E8) solo en barstate.isconfirmed. Validación diferida = medición post-cierre barra (nunca intra-barra).

4. **Diagramas Mermaid (§10):** máquina estados 5-nodos + flujo datos 4-capas + ciclo cognitivo tabla 8×3. Exportables a PNG para reportes TV/MT5.

---

## Sin toque TV, sin gate de fase

- TV no lanzado (S098 = documentación pura).
- Sin gate de Fase completado (F1-GATE aún pendiente firma usuario).
- CORE Pine intacto, compila 0/0, core-sync OK.

---

Ver [[Sesion-097]] (DOSSIER origen) · [[Sesion-098]] (cierre).
