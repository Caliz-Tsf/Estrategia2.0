# Sesión 018 — Corrección de coherencia documental T06 (FVG §2.2)

> Fecha: 2026-06-13 · Fase 1 Sprint 1.2 · Claude Code (Opus 4.8) + Freddy
> Registro de QUÉ se hizo, POR QUÉ, CON QUÉ FINALIDAD y QUÉ SE DECIDIÓ.
> **ESTADO: correcciones documentales aplicadas y verificadas. Sin tocar código Pine. Sin nuevo concepto.**

## Objetivo de la sesión
Resolver los errores documentales que quedaron de Sesion-017 (T06 FVG) **antes** de avanzar a T07,
con la condición del usuario: verificar/calcular todo bien para que no afecte al plan ni a la
metodología ni contradiga cosas que no son. El git lo maneja el usuario.

## Qué se hizo y por qué

### 1. Error 1 — Contraejemplo §2.2 incorrecto (el que estaba anotado)
**Problema:** `reglas-smc-ict.md §2.2` rotulaba el caso 06-03 06:00 como "sub-umbral, se descarta"
con "0.26×ATR" — contradictorio: 0.26 ≥ 0.25 ⇒ PASA el filtro, no se descarta. El contraejemplo
existe para ilustrar la **rama del descarte por tamaño** (importa para la paridad MQL5, golden tests
ADR-002), y ese caso no la ilustraba.

**Verificación (misma metodología que la spec — detector `scripts/ver05/` sobre `eurusd_h1.csv`,
ATR14 Wilder):**
- Caso 06-03 06:00 (idx152): gap [1.16224, 1.16244] = 0.00020 = **0.255×ATR** (ATR 0.000784,
  umbral 0.000196) → **PASA**. Luego `close 1.16164 < bottom 1.16224` → **INVALIDA** (estado 3).
- Escaneo de sub-umbral (`_scan_sub.py`, nuevo): **33 gaps < 0.25×ATR** en la ventana 25-may→11-jun.
  Mejor contraejemplo real: **06-04 11:00 (idx181)** gap alcista [1.16284, 1.16304] = **0.209×ATR**,
  CE 1.16294 → descartado de verdad por el filtro.

**Corrección aplicada en `reglas-smc-ict.md §2.2`:**
- Contraejemplo de umbral reemplazado por el sub-umbral real 06-04 11:00 (0.209×ATR).
- Caso 06-03 06:00 reubicado como **ejemplo de invalidación** (pasa umbral, muere por close<bottom).
  No se pierde el caso; queda correctamente atribuido a la máquina de mitigación.

### 2. Error 2 — Aritmética rota en el relato de Sesion-017.md
**Problema:** el desarrollo intermedio de los 3 casos canónicos confundía `high/low` de la vela [0]
con `low[0]`/`high[2]` (p.ej. caso 1 calculaba CE 1.16288 y declaraba "EXACTO" el 1.16318; caso 3
alcista escribía "NO CUMPLE l0>h2" y lo tapaba). Los valores FINALES siempre fueron correctos y
coinciden con `validaciones.md`; solo el relato estaba mal escrito (la sesión corrió con Haiku 4.5).

**Corrección:** reescritos los 3 casos con los números correctos (verificados contra el CSV):
- FVG baj 06-01 14:00 (idx112): high[0]=1.16184, low[2]=1.16452 → [1.16184,1.16452] CE 1.16318.
- FVG baj 06-05 13:00 (idx207): high[0]=1.15998, low[2]=1.16345 → [1.15998,1.16345] CE 1.16172.
- FVG alc 05-29 15:00 (idx89): low[0]=1.16673, high[2]=1.16532 → [1.16532,1.16673] CE 1.16602.

### 3. Reconciliaciones de coherencia
- **Tercer número erróneo cazado:** los docs decían `close 1.16082` para el caso 06-03; el cierre
  real de idx152 es **1.16164** (1.16082 era de idx156, 06-03 10:00). Corregido en todos los docs.
- **Atribución del −5:** unificada a `MAX_ZONES=50` (caso 3 no visible en chart) — fuente autoritativa
  `validaciones.md`. El relato de Sesion-017 lo atribuía por error al contraejemplo; corregido.
- Notas "pendiente Sesion-018" marcadas ✅ resueltas en `ESTADO-ACTUAL.md`, `Sesion-017.md` y
  `validaciones.md`.

## Decisiones registradas
1. **El código Pine no se tocó** — siempre fue correcto. T06 sigue válido (95/100), gate intacto.
2. **Contraejemplos extraídos de datos reales**, nunca inventados (regla del proyecto). Verificador
   reproducible `scripts/ver05/_scan_sub.py` queda como herramienta junto a `detect.py`.
3. Workflow de transcripción/"mente de los mentores" (Hermes + claude-video-vision): **diferido a
   conversación dedicada** por decisión del usuario. No es parte del sprint Pine.

## Estado al cierre
- **Fase:** FASE 1 Sprint 1.2 — T05 OB ✅ · T06 FVG ✅ (validado, doc coherente).
- **Rama:** `pine/sistema-completo`.
- **Core sync:** OK (342 líneas, SHA `16f5e945af5f27c7`) — Pine intacto.
- **Working tree (para commit del usuario):**
  - M `docs/reglas-smc-ict.md` (§2.2 contraejemplo + invalidación)
  - M `docs/sprint-runs/validaciones.md` (nota T06 reconciliada)
  - M `memory/ESTADO-ACTUAL.md` (notas resueltas)
  - M `memory/sesiones/Sesion-017.md` (aritmética + atribución −5)
  - ?? `scripts/ver05/_scan_sub.py` (verificador sub-umbral)
- **Siguiente tarea:** **T07 Premium/Discount** (Sprint 1.2, PINE-PLAN §7).

## Links
- `docs/reglas-smc-ict.md` §2.2 — definición FVG + contraejemplo corregido.
- `docs/sprint-runs/validaciones.md` — detalle T06 reconciliado.
- `scripts/ver05/_scan_sub.py` — escaneo de FVG sub-umbral (33 en la ventana).
- [[Sesion-017]] — T06 FVG (origen de los errores corregidos aquí).
