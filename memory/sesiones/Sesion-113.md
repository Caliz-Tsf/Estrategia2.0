# Sesion-113 — 2026-07-10

**Cierre de sesión 113. Objetivo: F1-CTX-06 EQ-tomado-gris — Opción (a) S112 comprometida.**

## Resumen ejecución

**F1-CTX-06 EQ-TOMADO-GRIS (COMPLETADA — commit `d8a50ff`)**

Objetivo: mostrar EQH/EQL barridos/cruzados en gris un tiempo (liquidez tomada) en lugar de que se esfumen. Pieza no-trivial pendiente de S112 que requería rastrear el estado "cruzado" del evento EQ.

### Solución sin flag intrínseco

EQH está **TOMADO** cuando el precio ya lo cruzó por arriba (`lvl <= px`) → vive del lado OPUESTO, exactamente como:
- Mitigada de zonas (CTX-04, S112)
- Barrido de pools (CTX-05, S112)

EQL simétrico: `lvl >= px`.

### Cambios principales

**`f_farthestEvent(type,side,boundTaken,inclTaken)` (FUERA CORE, ~L1811 SMC-Context.pine):**
- 5º retorno nuevo: `taken` (bool)
- Lógica: prefiere EQ VIVO (en reposo) del lado
- Si no hay vivo e `inclTaken=true`, cae al TOMADO más lejano dentro `boundTaken` (bound del lado contrario)
- Fallback puro: jamás oculta EQ vivo por mostrar tomado

**Emit `kind` NEGATIVO cuando tomado:**
- NO crece tuple (reutiliza k-field, protege CE10117)
- Patrón idéntico CTX-04/05

**Dibujo:**
- YA manejaba `kd < 0` en slots línea EQ (s≥6, ~L2138)
- Gris CTX_MIT rgb(120,120,120) + sufijo " x"
- Solo actualización comentario ("EQ nunca negativo" era falso ahora)

**Reutiliza toggle:**
- `i_ctxMitigated` (input in_5)
- Label generalizado: "Mostrar traspasadas (frontera gris: mit + barridas + EQ tomadas)"
- SIN input nuevo

## Validación

**Compilación:**
- Compila 0/0 server-side (pine_check.py) ✅
- Core-sync OK ×3 (SHA `5510361166844bd5` CORE byte-idéntico; f_farthestEvent/f_tfExtremes viven fuera CORE) ✅

**Vivo en TradingView:**
- OANDA:EURUSD M5/H1 + NAS100USD
- Aplica 0 errores toggle OFF y ON
- Sin CE10117/OOM/RE ✅

**Chequeo corrección clave:**
- Precio 1.1415
- H1 EQH marginalmente sobre precio → clasificados VIVOS (violeta CTX_LIQ), NO gris espurio
- Detección tomado sin falsos positivos sobre vivos cercanos ✅

**Captura directa gris-traspaso (S112 no había logrado):**
- "D1 ▲ BSL x" renderizó gris vivo
- textColor 4286085240 = 0xFF787878 = rgb(120,120,120) = CTX_MIT
- línea color 0x40787878
- Rama dibujo `kd<0` probada por identidad ✅

**Captura "EQH x" gris:**
- Depende timing mercado (precio sobre EQH más lejano sin vivo arriba)
- Misma clase diferida/paridad que S112 aceptó para swept-gris
- No reproducible en sesión (esperado por mercado)

## GOTCHAs descubiertos

1. **`data_get_pine_labels`/`data_get_pine_lines` redondean precio ~2 decimales** → inservibles para juzgar vivo-vs-tomado
   - Fix: usar `verbose:true` + decodificar textColor ARGB (gris = 0x..787878) + `quote_get` para precio exacto

2. **CDP 9222 se cayó 1×** durante validación
   - Fix: relanzar con `tv_launch`

3. **Inject sobrescribe slot ABIERTO en el editor**
   - Precaución: verificar header con `pine_get_source[:400]` antes inyectar (evitar clobber SMC_Library/Visual)

4. **Mapa inputs Context (in_N 0-indexed):**
   - in_0 = extOn
   - in_1 = ctxAlways
   - in_2 = kExt
   - in_3 = extMinStrength
   - in_4 = revealHyst
   - in_5 = ctxMitigated
   - in_6 = swingLen
   - in_7 = pdSwingLen

## Estado

**F1-GATE BLOQUEADA** (aprobación humana pendiente)

**Capa gris-traspaso Context COMPLETA** en todas las familias:
- OB/FVG mitigadas ✅
- Pools barridos ✅
- EQ tomados ✅

**Sin ADR nuevo:** F1-CTX-06 cae bajo ADR-017 Fase A (escrito S110)

**Sin gate/tag nuevo**

## Commits

- `d8a50ff` feat(pine-context): F1-CTX-06 EQ tomado gris (liquidez cruzada)

## Pendiente S114

1. **(a) Fase B promoción CORE:** tuple único nearest+farthest ~62 campos, ADR nuevo, rompe SHA `5510361166844bd5`, Strategy consume, riesgo OOM histórico
2. **(b) Firma F1-GATE:** aprobación humana
3. Fuera alcance v1: MB/Breaker/BOS-CHoCH extremos heredados

**Usuario confirmó:** cerrar S113 aquí, continuar Fase B + firma F1-GATE en S114.

## Referencias

- [[Sesion-112]] — Opción (a) comprometida, F1-CTX-04/05 completadas
- [[Sesion-111]] — Pasos E/F dibujo Context HTF
- [[Sesion-110]] — Pasos B/C/D Context HTF (ADR-017 + SMC-Context.pine + revelado)
- docs/adrs/ADR-017-consumidor-visual-auxiliar-context.md

---
**Cierre:** Capa gris-traspaso Context 100% completa. CORE byte-idéntico. Listo para Fase B.
