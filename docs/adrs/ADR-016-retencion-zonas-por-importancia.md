# ADR-016 — Retención de zonas del chart por IMPORTANCIA (desalojo tier+strength), no por antigüedad

- **Fecha:** 2026-07-08 (Sesion-106)
- **Estado:** Aceptada — **Fase A** como wrapper Visual-only (`f_pushZoneV` en `SMC-Visual.pine`, fuera del CORE); **Fase B** promueve el mecanismo al CORE (`f_pushZone` v2 parametrizada + réplica en Strategy + re-baseline SHA + `MQL5-PLAN §3`).
- **Precisa (no contradice):** ADR-002 (parámetros congelados hasta Fase 3 — `MAX_ZONES_CHART`/`K_LEG` son candidatos a calibrar, no valores validados), ADR-009/010 (transporte MTF por buffer aplanado — intacto), ADR-014 (`strength` es propiedad de detección del CORE — aquí se **consume** como llave de desalojo, no se recalcula). No toca la calibración del scoring.
- **Tarea:** S106 Paso B del rediseño "poblar la pierna" (`docs/planes/RESPUESTA-FABLE-retencion-zonas.md`, Q1/Q2). Root-cause diagnosticado en S105.

## Contexto

El objetivo redefinido de la Fase A (S105, `docs/planes/swing-ideal-vision-usuario.md`) es **poblar la pierna completa del swing en ambas direcciones** con conceptos importantes NO mitigados (OB/FVG/Breaker/…), no reducir a ≤25 labels. Al validar en vivo faltaban cajas arriba de la pierna Y abajo del objetivo.

**Root-cause (S105):** el cap `MAX_ZONES = 50` (CORE, L225) lo comparten ~9 tipos de zona; y `f_pushZone` (CORE, L356) desaloja por **pura antigüedad** (`array.shift` del más viejo). Al llenarse, expulsaba zonas **NO mitigadas** viejas de ambos lados de la pierna — justo las que debían poblarla. Mismo patrón en pools (`MAX_POOLS=50`/`f_prunePools`, tratado en Paso C).

**Hallazgo que habilita Fase A sin tocar el CORE:** el `=== LIBRARY CORE ===` byte-idéntico termina en L1850. Los call-sites del chart (`f_pushZone(SMC_zones, …)` L2101+, 10 sitios) están **fuera** de esa sección, y `f_pushZone` ya recibe `maxN` por parámetro. → se puede introducir un wrapper Visual-only y subir el cap **solo en el chart**, sin tocar el transporte (`f_computeTFState` sigue a 50 → cero riesgo OOM server-side, `[[s105-revert-s104-y-diseno-fable-poblar-pierna]]`) y sin romper el SHA `5510361166844bd5`.

## Decisión

**El chart retiene zonas con un cap propio y un desalojo por importancia; el CORE y su transporte no cambian en Fase A.**

### 1. Cap separado por call-site
- **Transporte (CORE, `f_computeTFState`):** `MAX_ZONES = 50` — INTACTO. Es lo que corre vía `request.security` a otro TF; subirlo revienta el límite server-side (lección S104, HEAD muerto). 
- **Chart (`SMC-Visual.pine`, fuera del CORE):** `MAX_ZONES_CHART = 120`. Cubre poblar la pierna arriba y abajo con ~9 tipos.

### 2. Llave de desalojo = tier (`z.state`) + `strength`, nunca `score_render_v2`
`score_render_v2` (§7.1) es caro y está reservado a la pasada `islast`. El desalojo corre en cada push, así que usa dos campos ya materializados por el CORE (ADR-014): el estado y el `strength`. Orden de expulsión:

1. `ZS_INVALID` más viejo (marcador terminal, prescindible).
2. `ZS_MITIGATED` más viejo (ya cumplió su función).
3. La de **menor `strength`** entre `ZS_ACTIVE`/`ZS_PARTIAL`.
4. *Fallback anti-loop:* la más vieja (solo si todo está protegido).

### 3. Guarda de extremos por lado (anti-vaciado)
Nunca se expulsa la `ZS_ACTIVE` de **mayor `top`** ni la de **menor `bottom`** — son el techo y el origen de la pierna. Garantiza que cada lado conserva siempre un representante aunque el set esté saturado de instancias fuertes en el centro.

### 4. Frontera exacta (qué cambió en Fase A)
| Pieza | Ubicación | Cambio |
|---|---|---|
| `f_pushZone` / `f_prunePools` (definiciones) | CORE | **sin cambio** (byte-idéntico, SHA intacto) |
| `MAX_ZONES = 50` (transporte) | CORE | **sin cambio** |
| `MAX_ZONES_CHART = 120` | Visual | nuevo |
| `f_pushZoneV` (wrapper desalojo por importancia + guarda extremos) | Visual | nuevo |
| 10 call-sites del chart (`SMC_zones`/`SMC_vi`/`SMC_ipr`) | Visual | `f_pushZone`→`f_pushZoneV`, `MAX_ZONES`→`MAX_ZONES_CHART` |

## Consecuencias

- **Positivas:** la pierna se puebla en ambas direcciones sin OOM; el CORE y su SHA quedan intactos; el desalojo es determinista y auditable.
- **Deuda asumida (Riesgo #1 de Fable):** divergencia Visual/Strategy en retención durante Fase A — aceptada porque Strategy **aún no puntúa**. Se cierra en **Fase B** promoviendo `f_pushZoneV` al CORE (v2 de `f_pushZone` parametrizada por política de desalojo), replicando a Strategy, re-baseline del SHA y actualizando `MQL5-PLAN §3` (`SMC_Zones.mqh`).
- **Calibración (ADR-002):** `MAX_ZONES_CHART=120` y el umbral de "pool fuerte" (`touches≥2 ∨ strength≥0.5`, Paso A) son candidatos, no validados. Se revisan con datos reales EURUSD D1/H1 (y XAUJPY) antes de congelar.
- **Presupuesto de tinta:** subir el cap de retención NO sube la tinta dibujada — el band-pick top-3 (Paso D) + la fila "Ocultos"/desalojo §6.5 siguen acotando cuántas se dibujan. Retener ≠ dibujar.
