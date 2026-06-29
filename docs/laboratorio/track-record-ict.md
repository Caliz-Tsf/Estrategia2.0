# Track record — mentor-ict (ICT / Michael J. Huddleston)

> Registro de desempeño del agente ICT en el enjambre (laboratorio + copiloto, ADR-005/007).
> **Árbitro del resultado = la acción del precio en TradingView** (replay/seguimiento, reglas de salida deterministas). Ni el enjambre ni el agente se autoadjudican el resultado.
> Se puebla desde el runtime (§2.6 de `ESQUELETO-P2-hermes-enjambre.md`). Vacío hasta el primer evento real.

## Estado del agente
- **Creado:** Sesion-065 (2026-06-28). Perfil Hermes ✅ · Skill `mentor-ict` ✅ · ficha 10 campos (9 + "Lo que opinan sus compañeros") ✅ · entrada `swarm.yaml` ✅ · E2E ✅.
- **Rol:** **madre/raíz del enjambre** — define el léxico canónico ICT que el validador de Norms usa como vara. NSL ([[no-soy-liquidez]]) se declara su estudiante explícito.
- **Fuente:** REDUCE de 5 cursos destilados (`Mentores/ict/knowledge/`): 2022 Mentorship (intro+ep2-41, canónica completa) + Market Maker Primer (24/24) + OTE Pattern Recognition (Vol 01-20) + 2024 Mentorship (muestra densa conceptual) + 2026 lectures (iteración 1, 4 de 67). Enriquecimiento opcional pendiente: tape-reading 2026 + missed-entries/decoupled 2024.
- **Modelo:** `nvidia/nemotron-3-super-120b-a12b` (nvidia_nim, razonamiento, gratis 40/min). Perfil autocontenido en `~/.hermes/profiles/mentor-ict/`.
- **Aviso de Norm:** ICT **relativiza el R:R fijo** (gestiona por parciales/liquidez IRL→ERL; en la serie OTE llega a "forget R:R, 1:1 vale por frecuencia") — el validador determinista del Orchestrator descarta toda propuesta sin R:R≥1:3 calculable ANTES de mostrarla (regla dura `CLAUDE.md`). Misma tensión que arrastra NSL.
- **Candidatos que aporta para el set ampliado (ADR-012, validar contra TV antes de ascender):** HRLR/LRLR como régimen, time distortion (anti-chop), displacement obligatorio off PD array (gate), CE+cuadrantes con "stay open", FPFVG, ORG+regla 70%, Event Horizon, large-range-day filter. Detalle y estado-vs-Pine en `Mentores/ict/knowledge/2024.md` §"Vocabulario nuevo vs Pine". Gobernanza: regla cuantificada en `reglas-smc-ict.md` ANTES de codificar ([[sprint16-gate-reglas-antes-de-codigo]]).

## Log (JSONL/CSV — se anexa por el runtime)
| fecha | símbolo | TF | dirección | confianza | confluencia (§ref) | resultado | R | fuente |
|---|---|---|---|---|---|---|---|---|
| — | — | — | — | — | — | — | — | — |

## Hit-rate por confluencia (se calcula con muestra suficiente)
_(pendiente de datos)_
