# Sesion-124 — 2026-07-14 — Presupuesto Explícito Labels (Opción 2): Diseñado, Medido y Rechazado

## Objetivo sesión
Diseñar Opción 2 (presupuesto explícito por importancia, deuda S123 #7) — **medir ANTES de escribir**. Si cabe: ejecutar + resolver varios pendientes. Si no cabe: conocer los tokens necesarios + caer a plan B (Opción 1, cap top-N por tipo en swings). Norma proyecto desde S114: "diseño + probe primero, código después".

## Resultado
**La Opción 2 NO CABE.** Faltan 194 tokens. **NADA se escribió en pine/** (probe vivió en scratchpad; slot TV restaurado a versión repo). RECHAZADA + documentada.

## Completado

### DISEÑO (entregable: `docs/planes/DISEÑO-presupuesto-labels-S124.md`, commit `d179f1f`)
Tres piezas de la solución:

1. **Reserva MEDIDA, no adivinada:** `lblCap = min(budgetLbl, 500 − size(SMC_structLabels) − size(SMC_eqLabels) − FRAME_RESERVE − mtfReserve)`. Binds los presupuestos (25/60/150 por modo) al espacio real disponible.

2. **Contador cobrado AT-CREATION** (obligado por S123 Hallazgo 4: cap post-hoc inútil). En 3 helpers bottleneck: `f_evLbl` (20 call-sites), `f_zLbl` (9), `f_pushSwingLabel` (1). Acumulador `array<int>` tamaño 1 (truco S122: Pine muta arrays por ref, no escalares).

3. **Política de importancia = ORDEN DE DIBUJO** (ya documentada). Regalo: S117 puso swings al final; con cobro at-creation eso significa CEDEN primero → correcto (L3).

### Hallazgos de lectura de código (antes de medir)
- **El presupuesto EXISTE y es CORRECTO:** `budgetLbl` L3462 declara 25/60/150. "Todo"=150 **no es casualidad:** 500 − 342 (estructura) − 8 (FRAME_RESERVE) ≈ 150. **Lo que NUNCA existió es el COBRO:** `eventCap` solo cargado en 5 familias §6.5, mientras swings/zonas/IR y ~15 familias evento crean gratis. **Eso es el ×3.3** de S123.

- **Obstáculo de orden:** `lblCap` necesita existir ANTES de definir `f_zLbl` (L3518) y `f_evLbl` (L3547), pero `SMC_structLabels` se declara L3693 y `SMC_eqLabels` L3818. Requiere relocalización pura (neutral en tokens).

### MEDICIÓN (lo único que vale)
Protocolo realizado:

**Casos medidos en vivo OANDA:EURUSD D1 "Todo" (saturado):**

| Variante | Tokens | Veredicto |
|----------|--------|-----------|
| Diseño completo (3 gates) | 100450 | ❌ +194 sobre 100256 |
| Solo remociones (§6.5 afuera, sin gates) | ≤100256 | ✅ cabe |
| Gates f_evLbl + f_pushSwingLabel (sin zonas) | ≤100256 | ✅ cabe |
| Solo gate f_evLbl | ≤100256 | ✅ cabe |

**CONCLUSIÓN de ablación:** gate en `f_zLbl` (zonas) cuesta ~194 tokens ÉL SOLO. Mismo gate es asequible en f_evLbl y f_pushSwingLabel.

### Dos hipótesis propias muertas contra la medición
1. **Predije: rediseño LIBERARÍA tokens** (borrar §6.5 inútil, financiaba gates). Aritmética de sentencias decía "claramente negativo". **Realidad: +194.** Conclusión: aritmética de sentencias NO predice tokens Pine.

2. **Supuse: coste POR CALL-SITE** (referenciar un global nuevo en helper llamado desde N sitios). **Ablación lo desmienta:** f_evLbl 20 call-sites CABE; f_zLbl 9 NO. Conclusión: coste no es por call-site.

**SOSPECHA VIVA (sin medir aparte, NO doctrina):** `f_zLbl` era una función de UNA SOLA EXPRESIÓN hasta que se metió una rama (if + local + return). Pine podría inlinear/compilar distinto funciones de una sola expresión; romper esa forma es lo que se paga. Esto **matiza gotcha S122** ("meter lógica en helper existente ≈ gratis"): no es gratis si el helper era de una sola expresión.

### Intento de salvar el diseño (también medido, también NO)
Variante de 2 gates (sin cobrar zonas) CABE y COBRA de verdad: panel T14 mostró `Presup 88/88` (saturado, VISIBLE en vez de morir en silencio → cumple §10-#8 S123). **PERO censo numérico dio `total_labels = 501`:** las ~96 labels de zona, al no pagar, devuelven total al tope y estructura se sigue desalojando. → **EL GATE DE ZONAS NO ES OPCIONAL. Los tres gates necesarios y los tres no caben.**

### Hallazgo que cambia prioridades
`lblCap = 88` en D1/"Todo" ⇒ estructura + EQ ≈ 404/500 slots. La estructura histórica es **MAYOR que los ~342 estimados** S123. Ningún reparto de presupuesto arregla eso: no hay sitio para lo demás. La **deuda #5 (estructura vieja) NO es fleco, es PARTIDA PRINCIPAL.** Perseguir headroom para gobernar presupuesto de 88 es optimizar migajas.

**CAVEAT descubierto:** `array.size(SMC_structLabels)` cuenta labels CREADAS, Pine ya desalojó algunas (siguen en array aunque muertas) → una vez saturado, reserva se AUTO-INFLA. `lblCap` solo fiable POR DEBAJO del tope.

### Lo que queda probado y capitalizable
1. §6.5 (f_capLbls/f_capLblsOnly) es **TOKEN MUERTO** (S123 H4) y quitarla es gratis o mejor → financiación real disponible.
2. Presupuesto **SE PUEDE cobrar at-creation y se ve panel** (`Presup 88/88`).
3. Coste **CONCENTRADO en una sola función** (f_zLbl) → atacable.

## GOTCHAS S124
1. **`pine_check` 0/0 NO significa nada para tokens:** solo apply mide (~20-25s tard). Reconfirma S107.
2. **Generador probe debe escribir FUERA repo** (%TEMP%): al meterlo a scripts/ ensució el repo. (Relocado con `run_in_background`, recuperado.)
3. **Inyectar SMC_Library sobrescribe Visual**, pero recuperable: pine/SMC-Visual.pine fuente verdad. Restaurar siempre.
4. **`data_get_pine_labels` con `limit:1` devuelve 50 muestras**, pero da `total_labels` correcto.
5. **Esperar ~45s POST apply + re-poll `data_get_pine_tables`** hasta `study_count>0` (render atrasa compilación).

## Commits S124
- `29df099` chore(scripts): F1-S124 arnés ablación `gen_probe_budget.py` (flags nogates/nozgate/noevgate/noswgate; .pine→%TEMP%, fuera repo)
- `d179f1f` docs(planes): F1-S124 diseño Opción 2 — MEDIDO y RECHAZADO (faltan 194 tokens)

## CORE
- **SHA `752b4083a7db419d`** (1866 líneas)
- core-sync OK ×3
- pine_check 0/0
- **NUNCA se tocó pine/** — probe en scratchpad, slot restaurado repo

## Estado
- **F1-GATE BLOQUEADA**
- SIN ADR (es diseño rechazado; candidato ADR-021 si aparecen los 194 tokens)
- SIN tag
- Rama `pine/sistema-completo`
- Working tree limpio

## Tareas S125 (ordenadas prioridad — DECISIÓN PENDIENTE)
**¿Opción 1 primero (barato, acerca firma) o atacar primero causa real (recorte estructura)?**

1. **Opción 1 — cap top-N POR TIPO en swings (~2 tokens)** [plan B inmediato]. Arregla esqueleto desbalanceado (HH 31 / LL 19 / HL 11 / LH 4) → rompe alternancia H-L de S117. Recalibrar i_swingDomAtr (hoy 8.0 provisional fd54448).

2. **Recorte estructura histórica (deuda #5)** — la causa real (404/500). `f_drawStructure` recorrido histórico → labels viejos caen por edad. Requiere repintar islast (arrays datos) o cap at-creation en histórico.

3. **Los 194 tokens:** (a) gate zonas SIN romper forma una-expr de f_zLbl; (b) cobrar zonas en entry f_isBandPick (elige qué dibuja); (c) atacar estructura; (d) dieta estilo S121 (refactor feature-preserving).

4. **Verificar sospecha** "Pine inlinea distinto funciones una-expr". Si cierta: doctrina proyecto valiosa, matiza gotcha S122.

5. **Aplicar remociones §6.5** probadas gratis → abrir headroom. OJO: hoy es lo único que recorta EQ/pools/sweep/flip/gaps (aunque tarde) → verificar antes commitear.

6. **Resolver caveat reserva:** `array.size` cuenta muertas cuando saturado → se auto-infla.

7. Deuda S123 #2: meter EQ + estructura en `f_evLbl` (anti-solape).

8. Deuda S123 #3: zoom calibración ranura X.

9. Deuda S123 #4: nudo confluencia (CONFLUENCIA real que usuario QUIERE).

10. Deuda S123 #5: estructura vieja (pre-2016).

11. Deuda S123 #6: herencia H1/M5 auditoría → firma F1-GATE.

## Enlaces
- [[Sesion-123]]
- [[Sesion-122]]
- [[Sesion-121]]
- docs/planes/DISEÑO-presupuesto-labels-S124.md
