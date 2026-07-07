# CATÁLOGO — Imágenes de referencia de confluencias (lectura completa S098)

> **Qué es:** lectura íntegra, una por una, de las **48 imágenes únicas** subidas por el usuario a esta carpeta (2026-07-06/07, S098). Cada imagen fue analizada completa — desde el inicio del precio en el gráfico hasta el final — extrayendo estructura, conceptos que se cumplen y dónde se entra según su cumplimiento.
>
> **Para qué sirve:** es el **catálogo visual de razonamiento** que el enjambre (orquestador + agentes) y el EA usan como referencia de CÓMO pensar un gráfico. El esqueleto de Fase 4 ([ESQUELETO-FABLE-fase4-ea-mt5.md](../../docs/planes/ESQUELETO-FABLE-fase4-ea-mt5.md)) lo referencia desde los bloques E (debate), F (cuaderno) y G (bucle cognitivo).
>
> **⚠️ Regla de procedencia (dura):** son diagramas educativos de redes sociales (Facebook) — idealizados, sin ruido, sin los setups que fallan, y varios con R:R de marketing. Sirven como **referencia de RAZONAMIENTO y catálogo de variantes**, JAMÁS como fuente de reglas cuantificadas. La única fuente de umbrales y definiciones sigue siendo `docs/reglas-smc-ict.md` (§1–§7), bajo el gate `sprint16` (regla cuantificada + casos EURUSD reales antes de codificar).

---

## 1. Inventario

- **51 archivos** en la carpeta: 48 imágenes únicas + 1 README + **2 duplicados exactos** (`Screenshot_2026-06-23-19-07-06-533 (1).jpg` y `Screenshot_2026-06-23-19-12-24-896 (1).jpg` son copias byte-idénticas por nombre de sus originales — se anotan y se conservan, no se borran).
- Contenido: ~44 diagramas educativos SMC/ICT (mano alzada / whiteboard / render) + ~4 gráficos reales (EURUSD Weekly TradingView, XAUUSD 1H, GBPJPY 15m MMBM, EURNZD 60M).

## 2. La historia única que cuentan (síntesis)

Leídas las 48, **casi todas cuentan la misma historia en 4 actos** — que coincide exactamente con la tesis §7 del proyecto (leer-atrás → proyectar-adelante bajo confluencia):

1. **Contexto/acumulación** — el precio construye rango o tendencia y deja liquidez en extremos (equal highs/lows, stops, trendline liquidity).
2. **Manipulación** — sweep / liquidity grab / fakeout / Judas: se barre la liquidez (mecha grande, spike, falso breakout).
3. **Cambio de carácter** — CHoCH/MSS con desplazamiento que deja FVG y define el OB de origen.
4. **Retorno al origen y desplazamiento real** — el precio retrocede a la zona de origen (OB/FVG/OTE apilados = confluencia) y de ahí sale el swing hacia el draw opuesto (BSL/SSL/previous high-low).

**En el idioma del proyecto:** la zona de entrada de las imágenes es siempre `posRole=ORIGEN` (o GIRO) + `confDegree≥2` (familias apiladas en ±0.25×ATR) + `depthBand` profunda (retroceso a discount/premium extremo), con SL tras el extremo de la manipulación y TP en el draw proyectado. Los 3 primitivos §7.0 cuantifican lo que estas imágenes dibujan a mano.

## 3. Catálogo de modelos (16 modelos, 48 imágenes mapeadas)

Formato por modelo: **qué muestra · secuencia leer-atrás · gatillo de entrada · SL/TP · mapeo al proyecto** (familias §7.2: A1 Estructura 7.2.1–7, A2 OB 7.2.8–13, A3 FVG 7.2.14–20, A4 Liquidez 7.2.21–27, A5 P/D+Gradient 7.2.28–31, A6 Gaps 7.2.32–35, A7 Contexto 7.2.36–40; confluencias §4.8 del WORKPLAN).

### M1 — BOS + FVG + OB (continuación) — el "Simple BOS Entry"
- **Imágenes:** `06-11-22-48-31`, `06-25-04-25-33` (repost), `07-01-13-44-41`, `07-03-03-34-13`, `07-05-01-19-41`.
- **Muestra:** tendencia alcista con BOS sucesivos; el impulso que rompe deja FVG y el OB es la última vela bajista antes del BOS; el precio retorna a FVG/OB y confirma; target = previous high / siguiente liquidez. Variante `07-05` añade sweep de BSL con 8:1.
- **Leer-atrás:** ¿hay tendencia con BOS? ¿el impulso dejó FVG medible? ¿dónde está el OB de origen?
- **Gatillo:** retorno a la zona FVG+OB (confluencia de 2 familias = confDegree≥2) + confirmación alcista.
- **SL/TP:** SL bajo el OB; TP en previous high / pool siguiente.
- **Mapeo:** A1 (BOS 7.2.x) + A2 (OB) + A3 (FVG); confluencias OB/FVG/estructura §4.8; R:R gate `minRR`.

### M2 — Sweep + MSS + FIB/OTE + OB (reversal en el origen) — el modelo "entrada en el origen"
- **Imágenes:** `06-11-23-00-14` (bearish, OTE 0.618–0.786, 6:1), `06-28-15-44-54`, `06-28-20-48-46`, `07-03-03-34-55`, `07-05-09-29-17` (textbook: BOS→trendline liquidity→OTE+FVG→BSL).
- **Muestra:** sweep de liquidez (protected high/low) → MSS/structure shift → retorno al OB/FVG en la zona OTE del retroceso → desplazamiento al draw opuesto.
- **Leer-atrás:** ¿qué liquidez se tomó? ¿hubo desplazamiento con MSS? ¿dónde queda el origen (OB+FVG+OTE)?
- **Gatillo:** precio entra a la zona OTE 0.618–0.786 con OB/FVG apilados (confDegree≥2, posRole=ORIGEN).
- **SL/TP:** SL tras el extremo del sweep; TP en la liquidez opuesta (4R–6R en los diagramas).
- **Mapeo:** A4 (sweep 7.2.2x) + A1 (MSS) + A2/A3 (OB/FVG) + OTE (§ reglas OTE/GP del CORE); es el **modelo canónico del esqueleto §7-G** (captura del swing completo).

### M3 — Smart Money Entry: BOS + IND(inducement) + OB + QM
- **Imágenes:** `06-11-23-00-40` (whiteboard, 4RR con MSS).
- **Muestra:** BOS alcista → inducement (IDM) → OB profundo → QM (quasimodo) entry tras MSS.
- **Gatillo:** mitigación del OB tras barrer el IDM; confirmación con MSS.
- **Mapeo:** A2 (OB) + IDM (7.2.x familia estructura/liquidez; en el sistema IDM ya está en Operación desde Fase A A-5) + estructura A1.

### M4 — Sweep + IDM + OB de extremo (SMC "for beginners")
- **Imágenes:** `06-11-23-02-12`, `06-26-03-19-05` (VIP setup: diagrama + chart real).
- **Muestra:** secuencia BOS…BOS → sweep del high → MSS/CHoCH → IDM → entrada en OB de extremo; SL sobre el OB; targets en los lows ($$$).
- **Leer-atrás:** "cuando el mercado está en uptrend y no hay BOS, espera MSS y CHoCH; el rango entre BOS y CHoCH define FVG y OB como Entry Area".
- **Mapeo:** A1 (CHoCH/MSS/BOS) + A2 (OB extremo) + A4 (sweep, IDM). Nota: la promoción confDegree≥2 del sistema (Fase A A-5) refleja exactamente este filtro.

### M5 — Venta tras liquidity grab en zona de venta (sell setup confirmation)
- **Imágenes:** `06-19-23-15-23` (spike enorme sobre liquidity area, RISK=50 pips REWARD=150, R:R 1:3 explícito), `06-29-14-43-08` (selling zone + sweep, R/R 1:3, TP escalonado).
- **Muestra:** downtrend → zona de venta con muchos stops arriba → HUGE SPIKE toma los stops → entrada short → TP1/TP2/TP3 (1R/2R/3R).
- **Gatillo:** vela de rechazo tras el grab en la zona marcada (paciencia para validación).
- **Mapeo:** A4 (pool/sweep) + A2 (zona de oferta/OB) + doctrina TP escalonado (esqueleto §7-G paso 7). **Estas 2 imágenes muestran el 1:3 del proyecto tal cual.**

### M6 — Doctrina estructural: CHoCH vs BOS
- **Imágenes:** `06-23-19-07-06` (+ duplicado `(1)`), `07-04-02-47-26` (major/minor CHoCH + fake breakout).
- **Muestra:** definición operativa — CHoCH = ruptura del swing en dirección OPUESTA (posible reversal); BOS = ruptura en la MISMA dirección (continuación). HH/HL/LH/LL etiquetados; HTF POI arriba y abajo; FVG en las rupturas; major CHoCH (reversal HTF) vs minor CHoCH (shift corto plazo).
- **Mapeo:** doctrina base A1 — ya cuantificada en `reglas-smc-ict.md` §1 (detección BOS/CHoCH del CORE). Sirve como material de entrenamiento del orquestador para NARRAR la estructura.

### M7 — Setup institucional: CHoCH + FVG + OB → buy side liquidity
- **Imágenes:** `06-23-19-12-24` (+ duplicado `(1)`).
- **Muestra:** BOS bajista → CHoCH alcista → doble FVG + OB como zona de demanda → objetivo buy side liquidity en 2 niveles.
- **Mapeo:** A1+A2+A3+A4; proyección a draws escalonados (depthBand: draw cercano → medio → origen).

### M8 — MSS + OB entry hacia la liquidez opuesta (modelo general LTF)
- **Imágenes:** `06-25-15-18-44` (HFT institutional entry, 1:5RR, SSL barrida → BOS ×2 → OB entry), `06-28-03-43-25` (BOS→BSL con OB+SSL+POI), `06-28-20-49-22` (US100 3m: sweep de sell stops → CHoCH → discount range → IFVG+OB = entry), `06-29-19-42-29` (whiteboard con niveles reales 0.58xxx: BSL→MSS→FVGs→SS→OB), `07-03-22-48-55` (best ICT model: OB + LQ sweep + LTF CHoCH → SSL), `07-05-21-24-32` (bearish: sweep → BOS → OB → trendline break → entry).
- **Muestra:** el modelo general en timeframe de ejecución: liquidez tomada → shift → entrada en OB/FVG del origen → correr hacia la liquidez opuesta.
- **Mapeo:** es M2 aplicado en LTF (M5 del sistema = timing/confirmación). El orquestador usa D1=bias, H1=estructura, M5=este modelo.

### M9 — OB Trap (la trampa y la entrada real)
- **Imágenes:** `06-26-03-07-04` (XAUUSD: 30-min OB arriba, OB TRAP abajo — "price breaks a level to trap traders before reversing", RRI 6), `06-28-15-57-31` (ORDER BLOCK TRAP → CH → IDM → OB real → entry 1.6RR).
- **Muestra:** el primer OB "obvio" es trampa (lo barren); la entrada válida es el OB superior/origen tras el internal structure break en LTF.
- **Leer-atrás:** distinguir OB mitigado/trampa vs OB de origen con confluencia — en el sistema: OB aislado (confDegree=1) vs OB apilado (≥2) + posRole.
- **Mapeo:** A2 + doctrina "en qué NO entrar" (esqueleto §6-F): OB sin confluencia ni posición estructural = trampa candidata.

### M10 — Fakeout (dónde NO entrar y dónde sí)
- **Imágenes:** `06-27-00-29-58` ("How to trade fakeout": breakout falso de resistencia → risky entry area vs safe entry area tras reingreso).
- **Muestra:** la ruptura con mecha que vuelve al rango = fake out; entrada segura = tras confirmar el reingreso, no en el breakout.
- **Mapeo:** A4 (sweep de resistencia = grab) + doctrina NO-entrar (perseguir breakouts sin confluencia). Conecta con "no chase price, follow smart money footprints" (M14).

### M11 — Breaker / Break Block reversal
- **Imágenes:** `06-27-00-30-54` ("2 most powerful momentum reversal patterns": bearish/bullish break block con fases agonist→antagonist→trade, entry en el retest del block, stop al otro lado, initial TP al extremo), `06-28-03-43-19` ("Breaker Block Trade": sharp downward impulse → structural break → institutional breaker zone = entry, demand pool abajo, profit target area arriba).
- **Muestra:** la zona rota (OB fallido) se convierte en breaker; la entrada es el retest desde el lado opuesto.
- **Mapeo:** Breaker ya existe en el CORE (band-pick Fase A A-5); ficha §7.2.x familia A2; promoción por confDegree.

### M12 — IFVG (inverse FVG)
- **Imágenes:** `06-27-00-31-56` ("IFVG? not good enough" — 4H FVG + buyside liquidity como contexto), `07-04-02-40-46` ("How to trade IFVG", 5 pasos numerados: 1 sweep de liquidez, 2 retorno al rango, 3 FVG violado se vuelve IFVG, 4 entrada en el retest del IFVG, 5 target = DOL/SSL o liquidez más cercana).
- **Muestra:** el FVG que falla invierte su rol; la entrada es el retest desde el otro lado tras el sweep.
- **Mapeo:** IFVG ya es variante A3 del sistema (FVG≠trueFVG≠IFVG≠BPR — cuaderno §6-F las distingue caso por caso); la validación de 2 pasadas + body está en la doctrina madre-2026 (inversion-FVG Triple A).

### M13 — Double Top/Bottom + MSS + FVG
- **Imágenes:** `06-28-03-49-15` ("Double Top Analysis": M-shape, neckline, retest, structure break→retest→pattern), `06-28-15-49-04` (liquidity sweep + double top at FVG → BOS → risk/reward), `07-05-01-07-31` ("Double Top Reversal": neckline como soporte clave, SL sobre los tops, target medido), `07-05-01-22-15` ("Double Bottom + MSS + FVG": identificar DB liquidity grab → esperar MSS → entrar en FVG pullback → target previous high, SL bajo FVG/low. Lección literal: "Structural shifts confirm a trade idea, not just patterns").
- **Muestra:** el patrón clásico SOLO vale con confirmación estructural (MSS) y zona (FVG) — no el dibujo por sí mismo.
- **Mapeo:** EQH/EQL del CORE (equal highs/lows = pool A4) + MSS (A1) + FVG (A3). La lección de la imagen ES la regla del sistema: patrón sin estructura no es señal.

### M14 — Checklist "smart money activo" + contexto
- **Imágenes:** `06-28-03-50-23` ("10 signs smart money is active": displacement, sweep antes del move, BOS, FVG, OB reaction, high volume, EQH/EQL targeted, rejection wicks, break+retest, continuación tras pullback; ejemplo integrado con RR 1:3 — "don't chase price"), `07-03-22-51-37` ("Consolidation area": rechazos múltiples arriba/abajo, breakout con presión bajista masiva, retest).
- **Muestra:** lista de evidencias de participación institucional + el patrón consolidación→breakout→retest.
- **Mapeo:** son las confluencias §4.8 en versión narrativa; consolidación/equilibrium = zona NO-entrar (chop) hasta breakout+retest confirmado.

### M15 — AMD: Accumulation → Manipulation → Distribution
- **Imágenes:** `06-28-03-52-14` y `06-28-03-52-22` (el ciclo completo: acumulación en rango con SSL abajo, manipulación con MS_FU (false uptick) sobre BSL, MSS confirma el shift, FVG de reacción, distribución con -OB y SIBI hasta sellside liquidity).
- **Muestra:** el mapa completo de la campaña del market maker — el "por qué" detrás de M2/M8.
- **Mapeo:** es la narrativa maestra del orquestador (leer en qué fase del ciclo estamos = paso 2 del bucle cognitivo §7-G). Kill Zones/sesiones (A7) le dan el timing.

### M16 — Gráficos reales (la prueba de fuego)
- **Imágenes:** `06-28-04-00-32` (EURUSD Weekly real: BOS históricos, OB semanal abajo [1.105–1.125], FVG y proyección bajista dibujada, 26/6/2026), `07-04-00-18-21` (XAUUSD 1H real: BOS alcista fuerte → pullback a premium demand zone con proyección en zigzag hacia 4160), `06-28-15-54-52` (GBPJPY 15m NY session: market maker buy model — SMT con EURJPY, breakaway gap, propulsion block, BPR, HTF PDA daily BISI, rel equal highs → buy side), `07-04-03-27-07` (EURNZD 60M + whiteboard 1H BOS+FVG+OB mitigation 4RR).
- **Muestra:** el mercado real es más sucio que los diagramas — estructura anidada, zonas solapadas, ruido. **Por eso los umbrales son ×ATR y la validación es contra outcome real.**
- **Mapeo:** este es el formato de captura que el orquestador entregará al debate (D1/H1/M5 con todo dibujado por el indicador Visual).

### M17 — Order Block Strategy HTF + estructura institucional
- **Imágenes:** `07-01-13-43-49` ("Order Block Strategy" 1H/1D: BOS → ChoCh → retorno al OB/Demand zone profundo), `07-04-02-46-09` ("Institutional market structure & OB": BOS ×2, liquidity grab al OB inferior, bullish harami como confirmación de vela en la zona).
- **Muestra:** el mismo modelo en HTF; el patrón de vela (harami/rechazo) como confirmación intra-zona.
- **Mapeo:** A2 en D1/H1 (el sistema hereda zonas MTF); "confirmación intra-zona" = protocolo al llegar a la zona (esqueleto §6-F).

### M18 — Doctrina R:R por tipo de setup
- **Imágenes:** `06-28-20-50-45` ("FVG & price ratios": 1:3 para bearish reversal setup / 1:2 para bullish continuation con FVG filled + nivel 0.5–0.6).
- **Muestra:** el R:R esperable depende del tipo de setup (reversal desde origen rinde más que continuación).
- **Mapeo:** alimenta el gate paramétrico `minRR` (esqueleto §9): default 1:3; los datos del laboratorio dirán qué familias de setups sostienen múltiplos mayores.

### M19 — Trendline liquidity + breakout/retest
- **Imágenes:** `07-03-22-46-35` (soportes 1-2-3 + trendline breakout → retest → entry con OB debajo), `07-05-09-29-17` (comparte con M2: la trendline acumula liquidez $$$ que se barre antes del move).
- **Muestra:** las trendlines son liquidez (stops acumulados), no soportes mágicos; el sistema las lee como pools dinámicos.
- **Mapeo:** A4 (trendline liquidity como pool); el sweep de trendline es manipulación (acto 2 del ciclo).

## 4. El razonamiento tipo destilado (plantilla de narración del orquestador)

Ésta es la plantilla de lectura que sale de las 48 imágenes + el ejemplo del usuario, y que el orquestador del enjambre usará para abrir cada debate (bloque E del esqueleto). **Siempre en este orden, siempre citando datos del CORE, nunca inventando niveles:**

1. **¿Dónde estamos?** — símbolo, TF, precio actual, posición en el dealing range (premium/discount/EQ, depthBand), sesión/Kill Zone activa.
2. **¿Qué pasó atrás?** (leer-atrás, del pasado al presente): "se generó un swing en X → CHoCH en Y → BOS en Z → retroceso en curso → el precio está entrando a [zona] (OB+FVG, banda 2, GIRO)". Liquidez ya tomada vs pools vivos. Fase del ciclo AMD.
3. **¿Qué hay adelante?** (proyección): draws vivos por profundidad — cercano / medio / origen-inducement. Dónde debería REACCIONAR el precio y con qué confluencia (posRole/confDegree/depthBand de cada zona candidata).
4. **Escenarios accionables** (el ejemplo del usuario, formalizado): "si el precio mitiga el FVG y confirma → entrada A; si barre el FVG pero rebota en el OB de abajo → entrada B; si pierde el OB → invalida y esperamos CHoCH de TF mayor / re-proyectamos al siguiente draw".
5. **Ronda de agentes:** cada perfil responde con SU proyección (dirección, zona exacta, confluencias que ve, invalidación, R:R estimado vs `minRR`) o su abstención con motivo. Uno esperará confirmación, otro entrará directo — **eso es el debate**; la confluencia de proyecciones independientes es la señal, no el consenso.
6. **Registro y validación:** todo queda en `confluencias/swarm/` (plantilla TEMPLATE-debate.md); horas/días después el orquestador valida contra TV vivo qué se cumplió y actualiza el score darwiniano de cada agente por exactitud de proyección.

## 5. Reglas de uso de este catálogo

- Los modelos M1–M19 son **variantes de razonamiento**, no señales: ninguno dispara nada por sí mismo. Disparan los gates deterministas del sistema (confDegree≥2, posRole, R:R≥minRR calculable, invalidación definida).
- Cuando un agente cite un modelo ("esto es un M2"), debe citar también **qué ficha §7.2.x del sistema lo respalda y con qué números** (niveles reales, ATR, tolerancias).
- Las imágenes idealizadas NO se usan para calibrar umbrales. Los gráficos reales (M16) sí pueden usarse como casos de estudio adicionales.
- Este catálogo se amplía: nuevas imágenes del usuario se agregan a la carpeta y se catalogan aquí (modelo existente o nuevo M-n).

---

*Catálogo generado por Claude Code (Fable) — S098, 2026-07-06. Lectura íntegra de las 48 imágenes confirmada antes de escribir el esqueleto (regla del usuario).*
