# Sesión 116 — 2026-07-11

**Rama:** `pine/sistema-completo` · **Fase:** 1 (F1-GATE BLOQUEADA) · **CORE:** SHA `d86bf37aacbd25cf` intacto (1952 líneas, core-sync OK ×3)
**Commits:** `a7c07ab` feat(pine-visual) filtro por rol swings · `964557e` docs(planes) rúbrica curación · **Sin tag.**

## Objetivo
Retomar S116: recuperar estado limpio (slots TV desincronizados por funnel), resolver el "Internal server error", y arrancar la auditoría visual concepto-por-concepto desde D1.

## Lo hecho

### 1. Recuperación limpia de slots (retoma S116)
- El estudio con "Internal server error" era **estado roto pegajoso por churn** (sobrevive relanzar app); removido + re-aplicado fresco lo revive.
- **DESCUBRIMIENTO CLAVE:** en TV Desktop un estudio aplicado **rastrea su slot EN VIVO, no es snapshot** — re-guardar el slot muta la instancia (código+título). Corrige el supuesto de S116-previo ("add to chart = instancia fresca"). Ver [[tv-estudios-rastrean-slot-en-vivo]].
- Estado limpio: `SMC_Library`=Visual repo (v169), `SMC_Context`=Context repo (v19); estudios `RqQuYW`=Visual, `zirOQD`=Context, **slots distintos**.
- Conmutación fiable de slot = abrir dropdown + **click nativo MCP** (`ui_mouse_click`); los clicks sintéticos CDP no registran en los menús de TV.

### 2. Test all-off determinista (paso 3 S116)
Apagar TODOS los conceptos dejando solo pivotes en D1, **en un solo cambio en bloque**, **NO reproduce** el error. Conclusión: era churn (≈40 recálculos sucesivos si se apaga uno por uno), no efecto determinista. Una vez roto, solo re-apply fresco lo revive.

### 3. Evaluación de 2 skills de diseño
- **Emil Kowalski** (`github.com/emilkowalski/skills`) y **checklist de Gemini**: ambas **UI web animada** (CSS/JS/springs/easing). ~90% no aplica al Pine estático (solo color+transp+estilo línea+tamaño label).
- Lo útil (jerarquía peso+color, dim-to-focus, encoding consistente, anti-overlap islast, GC) **ya lo hacíamos**. Rechazada la regla Gemini "3 colores + opacidad" (ilegible para 40 conceptos; lo correcto es hue-por-familia + canal secundario).
- **NO instalar**; reservar para artifacts web / UI del EA Fase 4. Ver [[emil-skills-diseño-web-fase4]].

### 4. Rúbrica de curación visual (`docs/planes/rubrica-curacion-visual.md`)
5 principios estáticos + jerarquía L1/L2/L3 (solid/dashed/dotted + peso) + regla de encoding **invariante al origen**. **Colisión de paleta detectada:** pools nativo rojo/verde (`COL_BSL/SSL`) vs heredado violeta (`CTX_LIQ`, SMC-Context L2159) = mismo concepto, 2 colores; violeta sobrecargado (eventos-liq Visual vs pools+EQ Context). Ver [[rubrica-curacion-y-colision-paleta]].

### 5. Filtro por rol en swings (F1-D1-B) — commit `a7c07ab`
Swings HH/HL/LH/LL reescritos a **repintado-en-islast** (patrón sweeps, `xloc.bar_time`, RE10045/RE10026-safe) con input `i_swingRoleOnly` (default ON): dibuja solo el pivote **con rol SMC** = coincide con pool (liquidez, incl. barrida) O borde de zona OB/FVG (precio ≤ 0.15·ATR). `f_drawSwing` eliminado. **Visual-only, CORE intacto.** pine_check 0/0, core-sync OK. Validado vivo D1 EURUSD (A/B on/off): elimina pivotes viejos/sin-rol, deja dominante + pivotes con liquidez real.

### 6. Hallazgo: la pierna no puebla hacia atrás
Los swings solo aparecen recientes: `MAX_SWINGS=100` FIFO (bota el más viejo) + el rol necesita pool/zona VIVA (podados a 50). La estructura dominante BOS+/CHoCH+ sí llega atrás (pivotes escala-50 raros, sin cap). Coherente con curación, pero el usuario **quiere ver la pierna completa** → PENDIENTE.

### 7. Concepto aclarado (herencia MTF)
Pivotes D1 ≠ H1 ≠ M5 (distinta escala; fractal = el patrón se repite, los puntos NO coinciden). "Reusar D1 en M5" **ya existe** = la herencia MTF (`f_computeTFState` + `request.security` + extremos promovidos S115). En M5 se ve: nativos + heredados D1/H1. El transporte es acotado (nearest-12 + extremos), no la pierna completa (límite OOM S104-S108).

## Pendiente S117
- **(a) "Poblar la pierna hacia atrás"** (elección usuario): retención Visual-side de swings por importancia = **"ADR-016 para swings"**. `SMC_Swing`/`MAX_SWINGS`/`f_pushSwing` están DENTRO del CORE byte-idéntico → **NO tocar**; crear capa chart-level FUERA del CORE (como `MAX_ZONES_CHART`/`f_pushZoneV` de zonas) + flag `hadRole` **pegajoso** (una vez que el pivote tuvo pool/zona, se recuerda aunque se poden) + subir cap. **Requiere mini-ADR.**
- (b) Afinar cluster reciente (opcional; colapso agresivo arriesga ocultar pivotes reales).
- (c) Resolver colisión de paleta pools nativo/heredado (hue=concepto, origen=canal secundario).
- (d) Continuar la matriz de auditoría: OB/FVG nativos D1 → luego H1/M5 con herencia.

F1-GATE sigue BLOQUEADA. Ver [[Sesion-115]] · [[Sesion-114]].
