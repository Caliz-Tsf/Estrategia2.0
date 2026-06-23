# Sesion-052 — 2026-06-23

> **Módulo PARALELO (Hermes / enjambre), NO Pine.** Core intacto, ningún `.pine` tocado, core-sync OK (verificado: 1517 líneas SHA `80fad14dd8d03758`). La validación visual del set completo (Sesion-049, F1-GATE) **sigue pendiente**. Continuación directa de `[[Sesion-051]]`.

## Objetivo
1. Resolver el "NEEDS SETUP" de NSL en el Workspace y dejarlo operativo en el Conductor.
2. Documentar el protocolo de razonamiento del agente (cómo decide el enjambre ESPERAR/ENTRAR/DESCARTAR), candidato a ADR.

---

## Completado

### A. NSL OPERATIVO EN WORKSPACE

#### Diagnóstico
El Workspace (hermes-workspace, puerto 3000) mostraba NSL en `/operations` con cartel **"NEEDS SETUP — CLICK TO CONFIGURE"**. Causa raíz: **profile incompleto**. La función `use-operations.ts:594` marca `needsSetup = !agent.model` al listar perfiles.

#### Análisis del profile
- **~/.hermes/profiles/mentor-no-soy-liquidez/** contenía solo `track-record.md` (metadatos).
- **NO había `config.yaml` propio** en el profile → la aplicación no encontraba `model:` ni `provider:`.
- Los profiles NO heredan el bloque `providers:` del config raíz global (`~/.hermes/config.yaml`) cuando se invocan con `hermes -p mentor-no-soy-liquidez`. Intento de usar `--provider puter` fallaba ("Unknown provider 'puter'" — Puter HTTP 402 desde hace sesiones).

#### Soluciones aplicadas (en ~/.hermes, fuera de git)

**Fix 1: Profile autocontenido**
1. Copiar config raíz global a `~/.hermes/profiles/mentor-no-soy-liquidez/config.yaml`.
2. Editar modelo y provider en ese config local:
   - `model.default: nvidia/nemotron-3-super-120b-a12b` (razonamiento + gratis 40/min + español).
   - `provider: nvidia_nim` (confirma NVIDIA Nim, gratis hasta 40 requests/min).
3. Validación: `hermes -p mentor-no-soy-liquidez -z "Tú y liquidez"` → responde en español, voz NSL, rechaza estrategias basadas en EMAs, suelta su muletilla **"Si tú no ves la liquidez, tú eres la liquidez"** ✅.

**Fix 2: Skills visible**
1. Copiar `SKILL.md` a `~/.hermes/profiles/mentor-no-soy-liquidez/skills/mentor-no-soy-liquidez/SKILL.md`.
2. El Workspace ahora ve `Skills: 1` (antes mostraba `Skills: 0`, perfil vacío).

#### Coherencia documental (actualizado)
- **SKILL.md:** línea de modelo cambió de `hermes-3:8b (Ollama obsoleto)` + `puter` → `nvidia_nim` + `nemotron-3-super-120b` (lo actual).
- **~/.hermes/swarm.yaml:** entrada `mentor-no-soy-liquidez:` cambió de `model: gemini-2.5-flash` (fallback Jarvis) → `model: nvidia/nemotron-3-super-120b-a12b` (permanente).

#### Estado final
- **Workspace (localhost:3000):** `/operations` muestra NSL sin "NEEDS SETUP" (model field poblado).
- **Conductor:** aún NO aparece en la lista (el usuario debe refrescar la UI en el navegador).
- **CLI E2E:** `hermes -p mentor-no-soy-liquidez` funciona ✅.
- **Cambios en ~/.hermes:** NO se commiten a git (son configuración local del usuario).

---

### B. PROTOCOLO DE RAZONAMIENTO DEL AGENTE — ADR-012 ACEPTADO

#### Contexto
El enjambre requiere una **estrategia compartida** para que cada agente mentor (y funcionales como el Escéptico, Router) razone sus decisiones de forma **determinista y verificable**. NO es por mentor (Expertise es flexible); SÍ es el contrato de salida del razonamiento (cómo **justifica** su voto).

#### Componentes definidos

**1. Snapshot DETERMINISTA del mercado**
- Fuente: **indicador Pine vía MCP TV** (no especulación local).
- Contenido multi-TF (D1/H1/M5):
  - Estructura de swings (altos/bajos, BOS, CHoCH).
  - Bias direccional (arriba/abajo).
  - Premium/Discount actual.
  - Pools sin barrer (liquidez acumulada).
  - OBs y FVGs abiertos (niveles esperados).
  - Eventos críticos de la vela (cierre, sweep, liquidación).
- Método de lectura:
  - `data_get_pine_labels` (panel T14: "Bias Long", "Sweep ▼", etc.).
  - `data_get_pine_boxes` (OB/FVG zonas como {high, low}).
  - `data_get_pine_lines` (pools, EQH/EQL).
  - `quote_get` (precio actual + OHLC).
  - `data_get_ohlcv` (barras históricas para validación).

**2. Cadena de 7 preguntas (discretas, verificables)**
Cada agente aplica este árbol de decisión:

1. **Q1: ¿La zona importa?**
   - ¿Hay OB/FVG activo? ¿Hay pool sin barrer? ¿El premium/discount está al extremo?
   - Si NO → DESCARTAR (no hay setup).
   - Si SÍ → Q2.

2. **Q2: Draw on liquidity (dirección + intención)**
   - ¿El precio está liquidando a un lado (alcista/bajista)?
   - ¿Hay rechazo en la zona rival?
   - Decide: UP / DOWN / UNDEFINED.
   - Si UNDEFINED → Q3 con cautela.

3. **Q3: ¿Rompió la estructura?**
   - ¿Hay BOS (Break of Structure) confirmado por cierre?
   - ¿Hay CHoCH (Change of Character) con retest + rutura?
   - ¿MSS (Multiple Structure Shift) visible?
   - Si NO → ESPERAR (estructura no rota).
   - Si SÍ → Q4.

4. **Q4: ¿Ya liquidaron a los tempranos?**
   - ¿Hay sweep (cierre en zona, retest, liquidación)?
   - ¿El precio rechazó la OB rival?
   - Si NO → ESPERAR (puede ser trap).
   - Si SÍ → Q5.

5. **Q5: ¿Qué confluencias presentes/faltantes?**
   - Mapeo contra §ref = 42 confluencias (WORKPLAN §4.8).
   - Mínimo esperado (sin especificar aún): 3 confluencias.
   - Si NO alcanza → ESPERAR o DESCARTAR.
   - Si SÍ → Q6.

6. **Q6: R:R ≥ 1:3 calculable?**
   - Entrada = precio actual o zona esperada.
   - SL = bajo de la OB rival (o breach de estructura).
   - TP = múltiplo de SL (1:3 mínimo).
   - Si ratio < 1:3 → DESCARTAR (regla §0.10 dura).
   - Si ratio ≥ 1:3 → Q7.

7. **Q7: Sesión + gate de noticias**
   - ¿Estamos en kill-zone configurable (Londres/NY/Tokyo)?
   - ¿Hay noticia de alto impacto en calendario?
   - Si se incumple gate → DESCARTAR.
   - Si OK → ENTRAR.

**3. Contrato de salida (YAML/JSON)**
```yaml
decision: ESPERAR | ENTRAR | DESCARTAR
razonamiento:
  q1: <respuesta corta>
  q2: <UP/DOWN/UNDEFINED>
  q3: <SÍ/NO + detalle>
  q4: <SÍ/NO + detalle>
  q5: <confluencias encontradas + faltantes>
  q6: <SÍ/NO + ratio resultado>
  q7: <gate OK/NO>

# Si ENTRAR o ESPERAR:
proyeccion:
  gatillo: <condición que espera>
  invalida: <condición que anula>
  objetivo_precio: <nivel TP esperado>

# Si ENTRAR:
q6_rr:
  entrada: <precio>
  sl: <precio>
  tp: <precio>
  ratio: <número ≥ 3.0>
```

#### Relaciones arquitecturales
- **ADR-005 (Laboratorio/Copiloto):** el protocolo es *modo copiloto* — razonamiento + proyección. El mentor es *laboratorio* — propone ideas (Expertise flexible, R:R 1:2 aceptado para aprendizaje). El **validador de Norms** (Orchestrator) filtra: `if ratio < 1:3: mark(rejected, reason="R:R < 1:3"); return`. El mentor no recalcula, el validador lo descarta transparentemente.
- **ADR-007 (EA razona confluencias):** el EA MQL5 replicará esta cadena; las 7 preguntas → scoring determinista.
- **ADR-012 ↔ Snapshot + Kanban:** el Vigía calcula el snapshot (MCP TV) y lo vuelca en el Kanban (JSON/tabla). Los agentes lo leen, corren Q1–Q7, escriben su voto (YAML) + razonamiento. El Orchestrator agrega votos y aplica Norms.

#### Implementación marcada como abierta (NO bloquea)
- `[impl]` K de proximidad del Vigía (cada cuántas velas recalcula snapshot).
- `[impl]` Dónde se calculan SL/TP en Q6 (en CORE Pine o en Vigía).
- `[impl]` Validación de YAML vs Kanban_show (JSON en DB vs texto en UI).
- `[impl]` Normalización de huso (Vigía local vs agentes en cloud).
- `[impl]` Re-evaluador de gatillos en tiempo real (cada vela, el Vigía revisa `proyeccion.gatillo`).

#### Documentación commiteada
- **docs/planes/PROTOCOLO-razonamiento-agente.md:** referencia viva (actualizable sin ADR si cambio es menor).
- **docs/adrs/ADR-012-protocolo-razonamiento-agente.md:** decisión formal, ACEPTADA (Freddy 2026-06-23).
- **Commit: `244bf23`** — `docs(enjambre): S052 — ADR-012 protocolo de razonamiento del agente`.

---

## Verificación
- **Workspace/NSL:** profile autocontenido + skills visible. Responde en español, voz NSL, muletilla confirmada ✅.
- **ADR-012:** documento redactado, decisión ACEPTADA, relaciones claras (↔ ADR-005/007) ✅.
- **Commit:** `244bf23` (coherente, referencia ADR-012) ✅.
- **Core:** intacto, core-sync OK (1517 líneas SHA `80fad14dd8d03758`) ✅.
- **Git:** el commit solo toca `docs/` (sin cambios a `.pine` ni runtime) ✅.

---

## Commits de Sesion-052
1. **244bf23** — `docs(enjambre): S052 — ADR-012 protocolo de razonamiento del agente`

---

## PENDIENTE — próxima sesión arranca con UNA de estas dos opciones

### Opción 1: Continuar enjambre (recomendado si NSL refrescado)
1. **Verificar NSL operativo** en Conductor (localhost:3000 refrescado).
2. **Instanciar 2º mentor real** → bajar otro curso (ICT raíz o Boxxocode). Re-destilar ficha + SKILL.
3. **Piloto E2E mínimo:** Vigía (loop 15m) + Kanban (JSON) + 2 mentores + Orchestrator → 1 entrada de diario sobre EURUSD.
4. **Aplicar ADR-012:** snapshot en Kanban, Q1–Q7 en mentor, voto + razonamiento.
5. **Medir:** RPD (requests/día), ruido, aciertos, cobertura.

### Opción 2: Retomar validación Pine (crítico para progresión)
- **Sesion-049 (F1-GATE):** validación visual 1-a-1 aislada de los 40+ conceptos.
- **Método:** MCP apaga TODOS los `i_show*`, enciende solo 1 concepto, scroll a casos §de reglas-smc-ict.md, screenshot, smc-validator-agent ≥90.
- **Gate:** ≥90 + anti-repaint (2 días EURUSD histórico) + performance 20k barras → desbloquea Fase 2 (scoring).

### Heredado (sigue pendiente, NO bloquea)
- Playlists NSL extra (6 totales) + bajar ICT (5 esenciales) → enriquecer conocimiento/expertise.
- CallMeBot + open-second-brain (gate §4.3) + Expertos E1–E6 (Funcionales/Control).
- Jarvis voz (wake-word fix "Jarvis", openWakeWord custom o Porcupine).
- Live-test MCP TV + browser_navigate.

---

## Resumen
Sesión paralela de enjambre. **NSL OPERATIVO** en Workspace tras diagnosticar y reparar profile incompleto: config.yaml autocontenido + skills cargadas. Modelo elegido: nvidia_nim nemotron-3-super-120b (razonamiento + gratis). COHERENCIA documental (SKILL.md + swarm.yaml) actualizada. **ADR-012 PROTOCOLO DE RAZONAMIENTO ACEPTADO:** snapshot determinista (Pine via MCP), 7 preguntas Q1–Q7 discretas, contrato YAML de salida, validador de Norms filtra R:R < 1:3. Relaciones: ↔ ADR-005 (laboratorio/copiloto) y ADR-007 (EA). Docs commiteados. Core Pine intacto. Próxima: refrescar NSL + 2º mentor + piloto E2E, **O** validación Pine (F1-GATE, crítica).

---

*Sesion-052 = módulo paralelo enjambre. NSL operativo + ADR-012 aceptado. Siguiente: piloto E2E o validación Pine F1-GATE. Validación Pine (049) sigue pendiente.*
