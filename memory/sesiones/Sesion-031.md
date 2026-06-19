# Sesion-031 — 2026-06-19

**Rama:** pine/sistema-completo · **Estado Pine:** INTACTO (core-sync OK SHA 8967d31bdbb7ed13, 592 líneas, idéntico Sesion-030)

## Objetivo
Integración de 6 herramientas/repos externos evaluadas por el usuario; config operativa Hermes (ZenMux + NVIDIA Nemotron); handoff ampliado a Opus Max para ponderación del workplan.

## Completado (NO sprint Pine)

### 1. Investigación de 6 herramientas (verificación independiente)
Tareas: (a) investigar encaje en arquitectura Pine + enjambre Hermes; (b) integrar en handoff Opus Max; (c) dejar insertos en operación.

**Veredicto tabla resume-solapa** en `docs/planes/HANDOFF-OPUS-MAX-ea-razonamiento-y-enjambre.md` §9:

| Herramienta | Repo | Encaje | Solapa-con | Veredicto | Acción |
|---|---|---|---|---|---|
| Open Second Brain | itechmeat/open-second-brain | §8 Obsidian | tradememory-protocol/gbrain | DIRECTO; elegir UNO | Adopción no-urgente (Fase 5) |
| Oh My Hermes | witt3rd/oh-my-hermes | §3.B discusión | TradingAgents | DIRECTO; roster Control/Escéptico ADR-005 | Adopción Fase 4 (diseño doc S030+) |
| Headroom | chopratejas/headroom | compresión MCP | compression nativo Hermes | Media-baja; apenas útil | Fallback solo si llena límite |
| Ponytail | DietrichGebert/ponytail | skill YAGNI | reglas-dev.md + #7 | Media-baja; YAGNI | Fase 4 (MQL5) posible |
| CallMeBot | zenmux.ai + API | alertas WhatsApp/Telegram | EA canal vivo | Alta pero tardía | Fase 4-5; noticias/gate |
| ZenMux | zenmux.ai | gateway OpenAI | Puter + NVIDIA redundancia | Redundancia proveedor | Instalado + config; plan requerido |

**Hallazgo crítico:** conteos de estrellas circulantes (Headroom "30k", Ponytail "33k", O2B "6") NO son fiables; verificación independiente necesaria.

### 2. ZenMux + NVIDIA Nemotron en Hermes
**Config en `~/.hermes` (NO git):**

- **Backup:** `config.yaml.bak-S031` (snapshot pre-cambios).
- **Proveedores añadidos:**
  - `zenmux` (base_url https://zenmux.ai/api/v1, key sk-mg-v1-*, 3 modelos free z-ai/glm-5.2-free, moonshotai/kimi-k2.7-code-free, stepfun/step-3.7-flash-free) [⚠️ requiere plan de uso en cuenta]
  - `nvidia_nim` (base_url https://integrate.api.nvidia.com/v1, key MISMA nvapi que auxiliary.vision, nvidia/nemotron-3-super-120b-a12b) [✅ OPERATIVO]
- **Start-script:** `~/.hermes/start-hermes.ps1` selector ampliado:
  - [1] Gemini primario (existente)
  - [2] Puter (fallback)
  - [3] ZenMux modelo 1 (z-ai/glm-5.2-free)
  - [4] ZenMux modelo 2 (moonshotai/kimi-k2.7-code-free)
  - [5] ZenMux modelo 3 (stepfun/step-3.7-flash-free)
  - [6] NVIDIA Nemotron (super-120b)
- **Verificación real:** `curl -H "Authorization: Bearer $env:NVIDIA_API_KEY" https://integrate.api.nvidia.com/v1/models` → HTTP 200 OK; Nemotron presente. ZenMux `/models` → HTTP 200 OK (configuración correcta).
- **Estado:** Nemotron ✅ OPERATIVO (HTTP 200, sin créditos, free tier). ZenMux ✅ config OK pero ❌ HTTP 403 access_denied en uso (necesita plan de usuario: Builder ~$20/mes o Pay-As-You-Go con saldo). Decisión = dejar instalado, usuario decide.

### 3. Documentación Hermes actualizada
- **`~/.hermes/MODELO-GUIA.md`** reescrita (estaba obsoleta "Puter primario", hoy Gemini único):
  - Canónica: Gemini primario + NVIDIA Nemotron operativo (Fase 4+)
  - Config keys en .env vars (deuda Fase 5)
  - Fallbacks: Puter (HTTP 402 frec.), ZenMux (plan requerido)

### 4. Integración en handoff Opus Max
**`docs/planes/HANDOFF-OPUS-MAX-ea-razonamiento-y-enjambre.md` §9** (NUEVO):
- Tabla 6 herramientas (ver arriba)
- Decisión: Opus Max elige set **mínimo coherente**
- Repos enjambre (2.A) + repos Fase 4-5 (2.B) solapan → deduplicación automática handoff
- No instalar a ciegas; Opus Max pondera integración

## Bloqueos
**Ninguno para el proyecto.** ZenMux requiere acción de cuenta del usuario (activar plan de uso); decisión = pendiente del usuario, no bloquea.

## ADRs
**Ninguno.** No hubo decisión arquitectural (config operativa + research; integración a cargo de Opus Max).

## Gates
**Ninguno completado.** Investigación finaliza aquí; integración = sesión próxima (tras ajustes Opus Max).

## Decisiones pendientes
- ZenMux: usuario elige si activar plan de uso (Builder $20/mes o PAYG con saldo)
- Integración de solapas (Open Second Brain vs tradememory, Oh My Hermes vs TradingAgents) = Opus Max
- Rotar keys texto plano config.yaml → env vars (deuda Fase 5)

## Próxima
- **Sesión mentores (sin cambios):** E2E curso NSL comandos 5-en-5; Opus Max integra handoff §9
- **Sprint Pine (sin cambios):** validación formal ≥90 de T09b/T10 por Opus Medio (esqueleto S028)
- **Generación COMANDOS:** docs 5-en-5 para 6 playlists NSL extras + ICT (postergada de S030)

## Notas
- **Índice Hermes/MODELO-GUIA.md:** consultar antes de arrancar cualquier sesión que use LLM
- **Keys en texto plano:** config.yaml + ~/.hermes/* — rotar a env vars post-Fase 3 (deuda anotada)
- **Nemotron 120B:** modelo más potente disponible gratis (NVIDIA free tier); útil Fase 4 (MQL5 complex)
- **ZenMux gratis:** modelos son rate-limited dentro de plan, no gratis sin setup (error común)
- **Chair decisión:** usuario baja; CLI comando exacto disponible si activar ZenMux

---

**Commit:** 4cc98af (2026-06-19)  
**Core Pine:** SHA 8967d31bdbb7ed13 (592 líneas, INTACTO)  
**check-core-sync:** OK ✅
