# Sesion-028 — 2026-06-17

> Cierre de sesión: **Esqueleto de implementación de la mitigación / ciclo de vida** de todos los conceptos SMC (documento, sin tocar Pine). NO sprint Pine — el CORE queda intacto.

## Objetivo
A partir del encargo del usuario y del `docs/planes/HANDOFF-OPUS-MAX-pools-mitigacion.md` (decisión: Opción A mitigación completa + Propuesta B de display), producir **solo el esqueleto/estructura de implementación** de la mitigación para que la integre otra IA ("Opus Medio"). El usuario fue explícito: *yo dejo el esqueleto, Opus Medio escribe el código.*

## Completado
✅ **Documento `docs/planes/ESQUELETO-MITIGACION-conceptos.md`** (esqueleto accionable, no código funcional).

Contiene:
- **§0 Reglas duras** que el implementador debe respetar (anti-repaint, core byte-idéntico + check-core-sync, ATR-relativo, funciones CORE puras para golden tests MQL5, compila 0/0, umbrales congelados Fase 3).
- **§1 Mapa archivo×sección:** dónde cae cada pieza (CORE en Library/Visual/Strategy, DETECCIÓN, DIBUJO solo Visual, SCORING solo Strategy) + convención de marca `// [P#·T##]`.
- **§2 Los 4 patrones canónicos** (esqueletizar una vez, reutilizar):
  - **P1 Nivel-consumido-por-barrido** (Pools, IDM): campos `swept`/`sweptBarTime`/`sweptBarIdx`, firmas `f_markPoolsSwept` + `f_upsertPool` (merge incremental que reemplaza el rebuild stateless), dibujo Propuesta B.
  - **P2 Zona-máquina-4-estados** (Breaker, Mitigation block, OTE/GP): reutiliza `SMC_Zone` + `f_updateZoneMitigation` ya existentes; OTE/GP añade `f_expireOTE` (caducidad por objetivo).
  - **P3 Nivel-rol-invalidable** (Flip): estados `LF_PENDING/FLIPPED/INVALID` + `f_updateFlip`.
  - **P4 Eventos puntuales + Present mode** (Sweep, Grab, MSS, Judas, Displacement, Rejection, False Breakout): no mitigan, pero límite de presentación / cuota por concepto (PINE-PLAN §5).
- **§3 Tabla maestra concepto→patrón→tarea→función** + fichas de integración por concepto (3.A Pools T09b como caso piloto detallado; 3.B IDM T17; 3.C Breaker T19; 3.D Flip T21; 3.E OTE/GP T22).
- **§4 Checklist de integración** (orden por palanca: T09b+T10 primero; verificación core-sync/compila/validador≥90/ADR).
- **§5 Documentos relacionados.**

Todas las firmas se entregan con cuerpo `// TODO [impl]` y su contrato (entradas/salidas/qué muta/pureza), **sin lógica escrita** → división de trabajo respetada.

## Decisión de enfoque (esqueleto = documento, NO stubs en los .pine)
Se entregó como documento y NO se insertó Pine no-funcional en `SMC-Visual/Strategy/Library.pine` porque:
1. Stubs que no compilan violarían la **regla dura #7** (compila 0/0 o no se commitea).
2. Comentarios/firmas en el CORE romperían el **SHA byte-idéntico** (regla #2) y obligarían a re-sincronizar — eso es trabajo de implementación, no de esqueleto.
3. El propio encargo dice *"para que lo pueda integrar cualquier IA luego"* → la integración en los `.pine` es el paso posterior (Opus Medio), no este.

## Verificaciones
- **check-core-sync.ps1:** OK — 503 líneas, SHA `2949a931757b9900` (idéntico a S027 → confirma que NO se tocó el CORE).
- **Pine intacto:** los 3 scripts sin cambios; no hubo recompilación (no era necesaria).
- `git status`: único cambio = el documento nuevo (+ docs de cierre).

## Pendiente (próxima sesión — Opus Medio implementa)
1. **T09b — Pools persistentes (P1)** unificado con **T10 (Sweep)**: el marcador de barrido = evento de sweep.
2. **T17 IDM (P1)**, **T19 Breaker + Mitigation block (P2)**, **T22 OTE/GP (P2+expiración)**, **T21 Flip (P3)**.
3. **P4 / Present mode** transversal al dibujar los eventos puntuales.
4. Por concepto: core-sync OK → compila 0/0 → `smc-validator-agent` ≥90 → (ADR para pools persistentes).

**Insumos:** `docs/planes/ESQUELETO-MITIGACION-conceptos.md` (este esqueleto) + `docs/planes/HANDOFF-OPUS-MAX-pools-mitigacion.md` (decisión/display) + `docs/reglas-smc-ict.md` §2/§3.

## Git
- Rama `pine/sistema-completo`. Commit de cierre local (docs). **Sin push** (preferencia del usuario; el supervisor maneja git, no se sube sin pedirlo). Sin tag (no se cerró gate). Sin sync-obsidian salvo que el usuario lo pida.

---

*Sesion-028: Cierre 2026-06-17 · esqueleto de mitigación (4 patrones P1–P4 + fichas por concepto) escrito en `docs/planes/ESQUELETO-MITIGACION-conceptos.md` · Pine INTACTO (core-sync OK mismo SHA 2949a931757b9900) · entregado como documento por reglas duras #2/#7 · siguiente: Opus Medio implementa.*
