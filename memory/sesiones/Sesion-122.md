# Sesion-122 — Eventos curados + nudo confluencia cercano precio (2026-07-14)

## Objetivo
Afinar el amontonamiento de eventos cerca del precio (la regla "band-pick siempre rotula" compite con el anti-solape) y, en segundo término, proseguir la matriz de auditoría visual F1.

## Lo que pasó (hallazgos centrales)

### HALLAZGO 1 — la premisa de S122 estaba mal dirigida
1. **Bypass band-pick secundario:** La regla "el importante SIEMPRE rotula" genera ≤2 picks/celda → ~16 labels conflictivos. Es SECUNDARIO; no se tocó.
2. **Causa REAL encontrada:** Solo 9 familias ZONA (OB, FVG, Breaker, IFVG, BPR, MB, Vacuum, OTE, IPR) pasaban por `f_zLbl`/`f_ySlot` con anti-solape. Las ~16 familias EVENTO (ID, Rej, Stack, ×EMA, FLP, CISD, SMT, Judas, Leg, Bag, Sweep, Disp) dibujaban con `label.new()` **crudo, SIN anti-solape**. La curación S120/S121 nunca llegó a eventos.

### HALLAZGO 2 (CRÍTICO) — el coste de tokens está EN LOS CALL-SITES, no en el cuerpo
**Medición viva en CE10117 (solo legible SOBRE techo 100256):**
- `if f_evSlotOK(x,y)` por call-site ×15 = **+991 tokens (~60 tokens/sitio)**
- `f_evLbl` con anti-solape DENTRO ×19 call-sites = **+41 tokens**
- Cuantizadores `evXq`/`evYq` precomputados + 1 `str.tostring` = **CABE sin CE10117**

**Conclusión:** El "headroom" de S121 fue un MITO. S121 apenas cruzó la línea; B+H ≈ 100344 vs. 100256. La regla es:
- **Migrar una familia a un helper existente ≈ ~6 tokens (insignificante).**
- **Meter lógica DENTRO de un helper existente ≈ GRATIS (el compilador optimiza el call).**
- **REGLA NUEVA:** Todo feature nuevo en Visual entra por un helper existente o paga su refactor.

### SOLUCIÓN IMPLEMENTADA (commit `778d661`)
Helper `f_evLbl(x, y, st, txt, bg, transp, tc)` creado junto a `f_zBox`/`f_zLbl` (~L3510 SMC-Visual.pine):
- **19 call-sites migramos** de `label.new(...)` directo a `f_evLbl(...)` (render byte-idéntico).
- **Anti-solape DENTRO del helper:** ranura 2D (3 velas × 0.5×ATR en eje X).
  - Zona horizontal (OB/FVG): si dos ocupan la misma vela, se descartan por Y.
  - Evento = punto en X (una vela) → solo colisiona si OTRO evento está en AMBOS ejes cercanos (no dedup solo-Y porque borraría eventos legítimos separados en el tiempo).
- **Acumulador COMPARTIDO entre familias:** `array<string>` de tamaño 1 (RE10045-safe; Pine pasa arrays por referencia).
- **Prioridad por orden de dibujo:** familia que dibuja primero elige ranura; luego NO se reasigna.
- **Devolución:** Devuelve `na` si la ranura está tomada → la label NO se crea → **libera presupuesto del tope `max_labels_count=500`** (antes ~501 labels intentadas desalojaban las VIEJAS = aquellas con mayor señal histórica).

## Validación en vivo y resultado honesto

**Compilación:** 0/0 server-side. Core-sync OK ×3. SHA CORE `752b4083a7db419d` intacto (1866 líneas).

**Resultado:**
- ✅ **Eventos curados:** CORR/×EMA/IDM/FLIP repartidos en la pierna histórica, ahora legibles (no ilegibles apilados).
- ✅ **Arquitectura de tokens desbloqueada:** Podemos añadir features sin tocar el CORE si las metemos dentro de helpers.
- ❌ **El cúmulo CERCA DEL PRECIO sigue.** La validación a mitad de sesión fue lectura floja (comparó zona media, no zona cercana al precio actual). Usuario lo detectó con captura: el amontonamiento OB+FVG·g+T.FVG·g+IFVG en píxeles sobre el precio actual aún es denso.

**Diagnosis del cúmulo cercano:**
- Apilamiento = **ZONAS de distintas familias** (OB, FVG·g, T.FVG·g, IFVG) al mismo nivel de precio → **familias distintas = acumuladores independientes** → cada familia elige su ranura → 3-4 nombres se pisan en píxeles.
- Sumado: bypass band-pick ("el importante SIEMPRE rotula") añade más presión.
- Ranura X calibrada para **vista cercana** (3 velas). A **zoom amplio**, dos ID a 5-6 velas no colisionan por la regla pero sí en píxeles en pantalla.

## Nudo de diseño (S123)

**EL APILAMIENTO CERCANO AL PRECIO NO ES RUIDO — ES CONFLUENCIA.**

Lo que el sistema busca marcar: múltiples conceptos importantes convergiendo al mismo nivel. El usuario QUIERE verlo.

**Deduplicar más fuerte sería EQUIVOCADO** (ocultaría señal legítima).

**Opciones a evaluar con la matriz:**
1. Etiqueta fusionada ("OB·FVG·IFVG").
2. Marcador de grado de confluencia (✱ o número de familias).
3. Sacar el nombre fuera de la banda de precio.
4. Aceptar densidad + resolver en Fase 3 (post-gate).

## Mapa de variantes auditado (todos los conceptos, S122)

Inventario completo de ZONA + EVENTO + variantes y su criterio de dedup:

**ZONA (9 tipos, 8 familias de colores):**
- OB: `OB` / `OB⇈` (propulsión = mayor peso)
- FVG: `FVG` / `T.FVG` × `·g` (4 combinaciones: FVG bruto, FVG intradiario, etc.)
- Breaker: `BRK ↑` / `BRK ↓` (**DIRECCIÓN es clave: ceder oculta sesgo**)
- **OTE / GP: `OTE` / `GP` — SIN anti-solape ⚠️** (no pasan por f_zLbl, usan f_densOK)
- IFVG, BPR, MB, Vacuum: sin variantes internas.

**EVENTO (ahora comparten `evSeen`, compiten entre familias):**
- **Sweep:** 3 conceptos distintos: `⚡Raid` / `⇧Spring` / `✗Sweep` (con dirección ↑↓ cada uno)
- **Leg:** `IMP` / `CORR` (con dirección)
- **EMA cross:** `×{timeframe}` (varía por TF)
- **Open gaps:** 3 conceptos: `NWOG` / `NDOG` / `NYMO` (con `BAG` adicional)
- **Otros:** IDM, Rej, CISD, SMT, Judas, Disp, FB (dirección ↑↓ cuando aplica)

**Criterio de dedup:**
- **OK ceder el nombre** si la variante es redundante (ej: dos nombres idénticos para el mismo concepto).
- **NO ceder si la variante porta la señal** (ej: "Raid" vs "Spring" vs "Sweep" son 3 tácticas distintas; dirección del Breaker cambia interpretación).

## GOTCHAs nuevos (técnicos)

1. **`in_115` NO es densidad; es `i_smtSymbol` (GBPUSD).** Escribirle "Operación" → TV lo resuelve como ticker → toast "Símbolo incorrecto" → estudio muere (parece caída TV). **Densidad real = `in_118`.** Mapa inputs actuales: in_115 i_smtSymbol · in_117 i_maxShowSMT · in_118 i_densidad · in_119 i_profundidad · in_120 i_kLeg · in_121 i_swingMinorLabels.

2. **`pine_get_errors` lee marcadores del EDITOR (Monaco) y devuelve 0 aunque el estudio esté muerto.** Error vivo se saca via CDP clickeando "Pine Save" y buscando en DOM "too many tokens" / `[title]` con CE10117. Los mensajes ACUMULAN en console → comparar contra vistos previos para detectar nuevo.

3. **Post-`pine_save` esperar 30-60s.** El estudio tarda renderizar. Leer errores antes da FALSO VERDE.

4. **`total_labels` de `data_get_pine_labels` pinchado en 500.** Inútil para medir dedup; validar visualmente.

5. **`pine_check.py` da CLEAN_0_0 aunque no quepa.** No cuenta tokens. Confirma S107.

6. **`updated_inputs: {}` vacío = falla silenciosa.** Las `in_N` se reindexan al añadir/quitar inputs. Mapear SIEMPRE contando `input.` en orden del fuente.

## Alcance atrás — caps que gobiernan "hasta dónde se marca"

**Anti-solape NO es lo que gobierna.** Lo gobiernan:
- **Eventos:** últimos 10-20 por familia (`i_maxShow*`)
- **Zonas:** `MAX_ZONES_CHART=120` COMPARTIDO entre 8 tipos (~15 slots/tipo, sospechoso principal de falta poblamiento pierna)
- **Pools:** `MAX_POOLS_CHART=80`
- **Swings:** `i_swingMaxKeep=350` (solo dominantes ≥ `i_swingDomAtr=4.0×ATR` se etiquetan, historial preservado)
- **Bandas:** `i_profundidad=3`
- **Extremo pierna:** `i_kLeg=3.0`

**Efecto colateral positivo:** Al no crear labels condenadas (ranura tomada → `label.new` ni se llamará), se libera presupuesto del tope 500 → sobrevive más historia.

## CORE y estado técnico

- **SHA CORE:** `752b4083a7db419d` (1866 líneas, INTACTO)
- **core-sync OK ×3:** SMC-Visual, SMC-Strategy, SMC-Context
- **pine_check:** 0/0
- **SIN ADR nuevo:** F1-CTX-06 bajo ADR-017 Fase A (ya S110), f_evLbl bajo ADR-016/ADR-002 (Visual-only, reversible)
- **SIN git tag**
- **F1-GATE BLOQUEADA** (redefinida: decisión sobre nudo confluencia pendiente)

## PENDIENTE S123 (próxima sesión)

1. **Matriz medida en D1:** familia × concepto × variante → hasta qué fecha/precio llega, cuántas instancias sobreviven, qué cap las corta.
2. **Diagnóstico de `MAX_ZONES_CHART=120` compartido** entre 8 tipos (¿por qué solo ~15/tipo? ¿Desalojo excesivo?).
3. **Resolver nudo confluencia + variantes:**
   - OB⇈ vs OB (propulsión sí/no)
   - T.FVG vs FVG (intradiario)
   - Breaker dirección (sesgo real)
   - OTE/GP sin dedup
   - Sweep: Raid vs Spring vs Sweep (3 tácticas)
4. **Calibrar ranura X:** 3 velas sirve para zoom cercano; en amplio da falso (píxeles se superponen). ¿Escalar por zoom?
5. **H1 y M5:** herencia MTF (nativos + heredados D1/H1) + validación matriz.
6. **Firma F1-GATE:** recién después que pase matriz.

## Notas

- Validación mid-sesión fue lectura floja (comparó zona media vs. cúmulo cercano). Usuario proporcionó captura.
- El desalojo de labels > 500 es un hallazgo: el tope está mordiendo y desalojando las viejas (de más señal). Anti-solape + acumulador compartido ayudan, pero MAX_ZONES_CHART=120 es sospechoso (distinta estrategia de desalojo por importancia vs. antigüedad).
- Arquitectura de tokens ahora CLARA: call-sites dominan; lógica dentro helpers es gratis; refactor paga todos los features nuevos. Se desbloqueó el camino.

Ver [[Sesion-121]] · [[Sesion-120]] · docs/adrs/ADR-016-retencion-zonas-por-importancia.md · docs/adrs/ADR-017-consumidor-visual-auxiliar-context.md
