# DOSSIER PARA FABLE — Esqueleto completo Fase 4 → adelante (EA MQL5 + score + perfiles + enjambre + debate + cuaderno de decisión)

> **Handoff de Claude Code a Fable.** Objetivo: que Fable genere el **esqueleto COMPLETO de la Fase 4 hacia adelante** para el agente/EA de MT5 — no solo la traducción determinista Pine→MQL5, sino **toda la capa cognitiva**: cómo llega la información al EA, cómo el EA piensa y analiza el mercado en tiempo real, qué debe tener presente antes de entrar y en qué NO entrar, cómo proyecta a zonas y qué hace al llegar a ellas, cómo se integran el score, el score de los perfiles del enjambre, el debate de los agentes y el conocimiento SMC/ICT necesario para decidir.
>
> **REGLA DE ENTREGA (crítica):** entrega un **esqueleto separado, NO integrado al WORKPLAN-MAESTRO todavía.** Lo revisaremos aparte (es el "punto 3") y, una vez listo, decidiremos qué integrar. No toques `WORKPLAN-MAESTRO-V2.md` ni los planes vigentes; produce documentos nuevos.
>
> **NO implementar.** Solo el esqueleto ordenado con fichas `[impl]` (cuerpo vacío / TODO) y la secuencia bajo los gates del proyecto. El relleno viene después, con casos EURUSD reales y validación TV (gate `sprint16`).

---

## 0. CONTEXTO MÍNIMO DEL PROYECTO (para arrancar en frío)

- **Qué es:** bot de trading **SMC/ICT** para Forex. Primero un sistema completo y validado en **TradingView (Pine Script v6)**; después un **Expert Advisor 100% nativo en MQL5** que replica el sistema validado. **Sin puente webhook** — el EA es autónomo: recalcula toda la detección y el scoring por sí mismo con los pesos validados en Fase 3.
- **Arquitectura Pine:** **1 core de detección** (sección `LIBRARY CORE`, byte-idéntica en `SMC-Visual.pine` y `SMC-Strategy.pine`) + 2 consumidores (Visual dibuja; Strategy hace scoring/entradas). El EA traduce el core **función a función**.
- **Estado actual (2026-07-06, S097):** Fase 1, F1-GATE del rediseño visual completado (Fase A A-1…A-7 implementada). CORE **1700 líneas, SHA `5510361166844bd5`**. Falta firmar F1-GATE, luego Fase 2 (scoring) → Fase 3 (validación EURUSD + paper) → **Fase 4 (EA MT5)**.
- **Reglas duras (innegociables):** anti-repaint (`barstate.isconfirmed` + `lookahead_off`); core byte-idéntico (`scripts/check-core-sync.ps1`); **umbrales relativos a ATR**, nunca pips fijos; **símbolo-agnóstico** (nada hardcodeado a EURUSD; lo por-símbolo va como perfil/input, ADR-001); **R:R mínimo 1:3** sin excepción (si no es calculable, no hay señal); **scoring direccional** (scoreLong/scoreShort, 42 confluencias canónicas §4.8); compila 0/0; ningún gate se salta.
- **Prohibición absoluta:** **JAMÁS** referenciar, leer o copiar el EA viejo en `D:\CODE\BOT\Bot\` ni ningún proyecto previo (`Estrategia-Nueva`). La única referencia externa permitida es el indicador LuxAlgo SMC. El esqueleto MT5 se construye **exclusivamente** desde el CORE Pine + `MQL5-PLAN.md`.

### Documentos que Fable DEBE leer antes de empezar
- `docs/workplan/MQL5-PLAN.md` — **diseño técnico del EA determinista** (6 módulos + EA, structs espejo, mapeo Pine→MQL5, golden tests, gates Fase 4). **Recién refrescado (S097)** contra el CORE actual: structs ya incluyen `strength`, `gradedFvg`, KIND≤53 y los campos §7. **Base determinista sobre la que Fable construye la capa cognitiva.**
- `docs/reglas-smc-ict.md` — **fuente de verdad SMC** con definiciones cuantificadas. Contiene §1–§6 (detección + grading), **§7 (capa de proyección/confluencia: primitivos `posRole`/`confDegree`/`depthBand` + 40 fichas 7.2.1–7.2.40)**, y las 42 confluencias.
- `docs/planes/DOSSIER-FABLE-proyeccion-confluencia.md` + `docs/planes/ESQUELETO-FABLE-proyeccion-confluencia.md` — la **doctrina de proyección** ya ordenada (leer-atrás → proyectar-adelante bajo confluencia). **Es la semilla del modelo de pensamiento que el EA y el enjambre deben heredar.**
- `docs/planes/ESQUELETO-FABLE-sistema-visual.md` — jerarquía visual, §8.2 matriz modo×familia, §10 checklist.
- `WORKPLAN-MAESTRO-V2.md §4.8` — catálogo de las 42 confluencias (+ candidatos #43–#52).
- Doctrina ICT destilada (en el vault): `Mentores/ict/knowledge/madre-2026.md` y `ficha-mentor.md` — el cuerpo de conocimiento SMC/ICT que el agente decisor debe "tener presente".
- ADRs relevantes: **ADR-001** (multi-símbolo, sin filtro horario), **ADR-013** (#52 gradient = multiplicador), **ADR-014** (`strength` es detección, vive en el CORE), y el protocolo de razonamiento del agente (ADR-012 si existe; si no, Fable lo propone).

---

## 1. LA TESIS RECTORA (el idioma común que TODO debe hablar)

Toda la inteligencia del sistema — el render Pine, el score direccional, el cuaderno del EA y el debate del enjambre — debe hablar **un único idioma**:

> **La importancia NO es "fuerza × cercanía al precio". Es RELEVANCIA ESTRUCTURAL + CONFLUENCIA, leída como PROYECCIÓN.**
>
> Un analista mira **hacia atrás** (contexto: dónde se tomó liquidez, dónde se rompió estructura, cuál es el rango/premium-discount) y **hacia adelante** (proyección: a dónde va el precio = *draw on liquidity*, y dónde REACCIONARÁ = origen del desplazamiento, bajo confluencia). El score de una zona ES su calidad como **proyección verificable**: `backward-read → forward-projection → outcome`.

Los 3 primitivos §7 ya cuantifican esto (congelados ADR-002):
- **`posRole` {0=INTERNO, 1=GIRO, 2=ORIGEN}** — posición estructural (tolPos=0.5×ATR; desempate ORIGEN gana).
- **`confDegree` {1..3}** — grado de confluencia = cuántas familias se apilan en ±tolConf(0.25×ATR); **≥2 = promoción**.
- **`depthBand` {1..5}** — profundidad del retroceso en el dealing range (cortes 0.33/0.66/1.0; bandas 4/5 = rangos previos).
- **Llave de render/score v2:** `score = strength × wPos(posRole) × (1 + kConf·min(confDegree,3))` con wPos {ORIGEN 1.0 / GIRO 0.9 / INTERNO 0.35}, kConf 0.25.

**El EA y cada agente del enjambre deben razonar con estos mismos primitivos.** Ése es el hilo que Fable debe mantener sin duplicar: una sola doctrina alimentando (1) render, (2) score, (3) cuaderno EA, (4) debate del enjambre.

---

## 2. QUÉ PEDIMOS A FABLE — ENTREGABLES DEL ESQUELETO

Fable debe producir un esqueleto integral (fichas `[impl]` + secuencia bajo gates) que cubra los bloques **A–H**. Para cada bloque: qué es, cómo mapea al CORE Pine existente, qué estructuras de datos/funciones nuevas requiere, y en qué fase/gate se rellena. **Sin implementar.**

### A. Capa determinista del EA (consolidar lo que ya está en MQL5-PLAN)
Confirmar/afinar los **6 módulos + EA** de `MQL5-PLAN.md` (`SMC_Types`, `SMC_Structures`, `SMC_Liquidity`, `SMC_MTF`, `SMC_Scoring`, `SMC_RiskManager`, `SMC_Display`, `EA_SMC_ICT.mq5`). Verificar que los structs espejo refrescados (con `strength`, `gradedFvg`, KIND≤53, campos §7) son suficientes. Señalar cualquier gap del mapeo Pine→MQL5 tras la evolución del CORE (gradient §5.16, ciclo de vida §5.4, primitivos §7). Este bloque es la **base**; los bloques B–H son la capa cognitiva **encima**.

### B. Cómo LLEGA la información al EA (la percepción)
Definir el **flujo de datos** que el EA construye en cada vela nueva antes de pensar: snapshots MTF (D1/H1/M5), detección propia recalculada, estado de premium/discount, gradient grid, Kill Zones (como confluencia, no guard — ADR-001), pools/draws vivos y objetivos. El resultado es un **"estado de mercado" estructurado** = el input del razonamiento. Especificar qué se persiste entre velas y qué se recomputa. El EA NO recibe señales de fuera; **percibe** el mercado él mismo.

### C. El SCORE direccional (une visual ↔ Fase 2 ↔ EA)
Cómo la "importancia visual" ES el mismo score de confluencia direccional (scoreLong/scoreShort, nunca absoluto). Un nivel donde se apilan conceptos en el punto estructural correcto (posRole giro/origen) suma score; el gradient #52 es **multiplicador** (ADR-013). La **precisión de la proyección** (¿el precio reaccionó donde se proyectó?) retroalimenta el score → pensar el score como **proyección verificable**, no peso estático. Definir la función de score que el EA usa en vivo y cómo hereda los pesos validados en Fase 3 (`scoring-weights-final.md`) como inputs por-perfil.

### D. El "SCORE DE LOS PERFILES" (los mentores / agentes del enjambre)
El enjambre tiene **perfiles** (mentores destilados: NSL/no-soy-liquidez, ICT-madre, Wyckoff, etc.), cada uno con su doctrina y su **track-record**. Definir:
- Cómo cada **perfil** produce **su propio score/proyección** para el mismo estado de mercado (su lectura de las confluencias según su doctrina).
- Cómo se pondera el aporte de cada perfil por su **track-record** (score darwiniano: el perfil cuya proyección se cumple con más exactitud sube su peso).
- Cómo estos scores-por-perfil se combinan (o **no** se promedian) con el score determinista del sistema. Regla del enjambre: **confluencia, no consenso**; diversidad no-SMC bienvenida; **olas de 3** con concurrencia dura ≤3.
- El choque conocido: NSL opera R:R 1:2 vs la regla dura del sistema 1:3 → cómo se reconcilia (el sistema manda el gate 1:3; el perfil aporta lectura, no override del gate).

### E. El DEBATE de los agentes (mecanismo)
Cómo el enjambre **debate**: cada agente entrega **su proyección** (dónde reaccionará el precio, a qué draw apunta, con qué confluencia, en qué zona NO entrar). Definir:
- El **protocolo de lectura+proyección común** (encaja con ADR-012): por cada concepto, leer *qué pasó atrás* (contexto estructural) + proyectar *hacia adelante* (escenarios) bajo confluencia. Todos hablan el mismo idioma §7.
- Cómo se mide **"exactitud de proyección"** contra el outcome real → selección darwiniana por precisión.
- Cómo el debate produce una **decisión o abstención** (no forzar consenso; la confluencia de proyecciones independientes es la señal).
- La sala de debate es **espejo/entrega, nunca bus** (el motor es determinista/Kanban); definir dónde vive el enjambre respecto al EA (laboratorio + copiloto de decisión, NO runtime dentro del EA en vivo salvo que se decida explícitamente — ADR-005: el EA hereda reglas cristalizadas, el enjambre calibra/valida).

### F. El CUADERNO DE CONFLUENCIAS del agente decisor MT5 (el conocimiento)
El agente decisor tendrá un **"cuaderno"**: todo el conocimiento SMC/ICT necesario para que, en tiempo real, tenga presentes **todas las confluencias, variantes y doctrina** para decidir. Definir su **formato** y cómo consume las doctrinas B/C/D. Debe cubrir:
- **Las 42 confluencias + sus variantes por concepto** (una FVG normal ≠ trueFVG ≠ IFVG ≠ BPR aunque sean la misma familia; el cuaderno distingue caso por caso, con la doctrina de cuál importa según posRole/confDegree/depthBand — ver §7.2.1–7.2.40).
- **Qué tener presente ANTES de entrar:** contexto (premium/discount, bias MTF, dónde se tomó liquidez), confluencia mínima (confDegree≥2), R:R 1:3 calculable, Kill Zone/timing, spread/riesgo OK.
- **En qué NO entrar:** confluencia insuficiente, media-tendencia (posRole=INTERNO), R:R<3, contra el draw dominante, en equilibrium/chop, cuando la proyección no es calculable ("no hay casi-señal").
- **El punto clave del usuario:** el agente TENDRÁ el conocimiento de las confluencias, **pero no todas se dan exactas** → debe **tomar decisiones, proyectar a zonas, y saber qué hacer al llegar a esas zonas** (¿reacción esperada? ¿confirmación intra-zona? ¿invalidación? ¿trailing hacia el siguiente draw?). Definir ese **protocolo de "qué hago cuando el precio llega a la zona proyectada"** (confirmación / entrada / invalidación / re-proyección al siguiente draw).

### G. Cómo el EA PIENSA y ANALIZA el mercado en tiempo real (el bucle de decisión)
El bucle cognitivo completo, tick a tick / vela a vela:
1. **Percibe** (bloque B) → estado de mercado estructurado.
2. **Lee atrás** → contexto estructural (rango, liquidez tomada, estructura vigente CHoCH/MSS, dominante).
3. **Proyecta adelante** → escenarios por profundidad (depthBand): draw más cercano, medio, y origen/inducement; identifica dónde REACCIONARÁ bajo confluencia.
4. **Puntúa** (bloques C/D) → score direccional + aporte de perfiles + (opcional) debate del enjambre.
5. **Decide con gates** (bloque F "en qué NO entrar" + R:R 1:3 + riesgo/spread).
6. **Al llegar a la zona proyectada** → confirma / entra / invalida / re-proyecta.
7. **Gestiona** → SL/TP estructural, trailing hacia el siguiente draw no mitigado, salida.
8. **Aprende** → outcome vs proyección retroalimenta el score de perfiles (bloque D/E).
Definir cada paso como ficha `[impl]` mapeada a módulos MQL5 y/o a la capa de enjambre.

### H. Fases posteriores (Fase 4 → adelante)
Esqueleto de la secuencia **desde Fase 4 en adelante**: Fase 4 (EA + golden tests + Strategy Tester + 60d demo + 30d live lote mínimo), Fase 5 (expansión multi-símbolo, Fase 3 abreviada por par — ADR-001), y el rol del enjambre en producción (calibración continua vs runtime). Gates de cada fase con criterios medibles. **No inventar fases nuevas sin justificar; anclar a la estructura del WORKPLAN pero SIN integrarlo ahí.**

---

## 3. INFRAESTRUCTURA EXISTENTE A REUTILIZAR (no reinventar)
- **CORE Pine (1700 líneas, SHA `5510361166844bd5`):** toda la detección §1–§6 + primitivos §7 (Fase A). Fuente de verdad de la traducción MQL5.
- **`MQL5-PLAN.md` refrescado:** 6 módulos + EA + structs espejo (con `strength`/`gradedFvg`/KIND≤53/§7) + mapeo Pine→MQL5 + golden tests + gates Fase 4.
- **Primitivos §7 (`posRole`/`confDegree`/`depthBand`) + llave `score_render_v2`** — ya cuantificados y congelados (ADR-002). El EA los recalcula (Fase B los promoverá al CORE).
- **42 confluencias §4.8** + candidatos #43–#52 (incl. #52 gradient multiplicador ADR-013).
- **Enjambre ya existente:** perfiles/mentores destilados (NSL construido y verificado E2E; ICT-madre; roster ESQUELETO-P2 §2.10/§3.1), regla de olas-de-3, darwiniano por score, Hermes como runtime de agentes. **Filosofía: confluencia no consenso, ADR-005 (enjambre = laboratorio + copiloto, no runtime EA).**
- **Doctrina de proyección ya ordenada:** `ESQUELETO-FABLE-proyeccion-confluencia.md` (bloques A–F de proyección). El EA/enjambre heredan de ahí.

---

## 4. RESTRICCIONES QUE EL ESQUELETO DEBE RESPETAR
- **CORE byte-idéntico** (SHA `5510361166844bd5`); la traducción MQL5 preserva semántica función a función; los golden tests son la prueba de paridad (fuente = sistema TV validado, fin Fase 3).
- **Anti-repaint** (solo vela cerrada, `shift≥1`); **símbolo-agnóstico** (todo ×ATR, lo por-símbolo en perfil — ADR-001); **R:R ≥1:3** sin excepción; **no inflar las 42 confluencias**; números congelados en Fase 3 (defaults razonables antes); un commit = un concepto verificado; **ningún gate se salta**.
- **Kill Zone NO es guard** — entra al scoring como confluencia #34 (ADR-001).
- El esqueleto se rellena luego bajo el gate **`sprint16`** (regla cuantificada + casos EURUSD reales antes de codificar).
- **PROHIBIDO** referenciar el EA viejo `D:\CODE\BOT\Bot\` o cualquier proyecto previo.
- **Entrega SEPARADA:** no integrar al WORKPLAN; producir documentos nuevos que revisaremos aparte.

---

## 5. FORMATO DE ENTREGA PEDIDO A FABLE
1. **Un documento esqueleto** (o varios enlazados) `ESQUELETO-FABLE-fase4-ea-mt5.md`, con los bloques A–H, cada uno con: descripción · mapeo al CORE/MQL5-PLAN · estructuras/funciones nuevas como fichas `[impl]` (cuerpo TODO) · fase/gate de relleno.
2. **Marcadores:** `[SUPOSICIÓN: …]` para cada supuesto, `[NUEVO: …]` para lo que no estaba, `[✓ MANTENER: …]` para lo correcto del diseño 2026-06-10, `[CONTRADICCIÓN: …]` + resolución si algo choca.
3. **Diagramas en texto** (ASCII/Mermaid): (a) flujo de percepción→decisión del EA; (b) arquitectura del enjambre + debate + cómo su output llega al EA; (c) cómo la doctrina única §7 alimenta render/score/cuaderno/debate sin duplicarse; (d) secuencia de fases 4→adelante con gates.
4. **La pregunta abierta a resolver:** ¿cómo estructurar esto para que la **misma doctrina** (leer-atrás + proyectar-adelante bajo confluencia, cuantificada en los primitivos §7) sea la **única fuente de verdad** que alimente sin duplicarse: (1) el render Pine, (2) el score direccional, (3) el cuaderno del EA, y (4) el protocolo de debate del enjambre — y cómo el "score de perfiles" darwiniano se integra sin romper los gates deterministas (R:R 1:3, confDegree≥2)?

---

*Dossier generado por: Claude Code (Estrategia 2.0) — Sesion-097, 2026-07-06*
*Para: Fable (arquitecto). Contexto adicional en los documentos listados en §0. NO integrar al workplan; entrega separada para revisión.*
