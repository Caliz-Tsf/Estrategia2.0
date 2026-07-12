# Sesion-118 — Resolución colisión encoding swings ⇄ BOS/CHoCH (2026-07-12)

## Objetivo
Resolver **colisión de encoding** entre la capa de swings (HH/HL/LH/LL, estructura leg-based S117) y la estructura BOS/CHoCH (Visual L1) en el gráfico D1 operacional. Método: diferenciar por **nivel L1/L2/L3** (jerarquía visual, no por hue). Dirección elegida: "solo los pivotes más fuertes; fuertes en Operación, resto en Estudio".

## Diagnóstico (verificado vivo OANDA:EURUSD D1, ambas capas ON)

**TRES problemas superpuestos:**

1. **Colisión de hue:** swings y BOS/CHoCH comparten teal/rojo por dirección (mismo hue = misma familia, correcto per rúbrica §2) pero SIN canal secundario → texto pegado visual ("HHBOS +"/"BOS +LH").

2. **Jerarquía invertida:** swing dominante gritaba (`size.small`, transp 25) y la estructura swing L2 susurraba (mismo tamaño pero menos contraste). Estructura BOS/CHoCH (L1) perdía énfasis.

3. **COLISIÓN DE PRESUPUESTO (hallazgo crítico):** swings solos = ~493 labels con `i_swingMaxKeep=350`; estructura BOS/CHoCH = ~289; juntos = 782 ≫ tope `max_labels_count=500` de Pine. Al encender ambos, la **estructura DESAPARECÍA** (los swings, dibujados al final, se comían el presupuesto). Un concepto ocupaba ~70% del budget.

## Solución implementada

**Commit:** `5374746` (Visual-only, pine/SMC-Visual.pine)  
**Core:** Byte-idéntico INTACTO, SHA `d86bf37aacbd25cf`  
**Compilación:** 0/0  
**Core-sync ×3:** OK

### Cambios específicos

1. **`f_pushSwingLabel` refactorizada:**
   - Swings demotados a **NIVEL L3** (rúbrica §2bis) — `size.tiny` SIEMPRE (antes dominante usaba `size.small` = choque con estructura swing L2 también small).
   - Transparencia: dominante 45 / menor 75 (antes invertida).
   - Hue: teal/rojo SIN cambios (`COL_BULL`/`COL_BEAR`).
   - **Nueva firma con parámetro `atr`:** offset vertical 0.3×ATR hacia afuera para despegar el tag del BOS/CHoCH (anti-solape §2ter).

2. **Draw loop de swings (solo ETIQUETADO dominantes):**
   - Array `SMC_majorSwingsV` (retención FIFO `i_swingMaxKeep`) queda INTACTO → historia profunda S117 preservada.
   - **Se recorta SOLO el DIBUJO** (etiquetado), no datos.
   - Gate DOMINANTES ⇒ visible en TODOS modos (Operación + Estudio), etiqueta `size.tiny` tenue.
   - Gate MENORES ⇒ `i_swingMinorLabels and f_famOK(FAM_EST)` (solo Estudio, con toggle).

3. **Nuevo input `i_swingMinorLabels`** (bool, default false, GRP_STRUCT):
   - Declarado al FINAL del bloque de inputs (in_121) a propósito: no desplaza índices in_N existentes.
   - `i_densidad` sigue in_118, `i_kLeg` in_120.
   - Revela swings menores tenues solo en Estudio+.

4. **Default `i_swingDomAtr` actualizado: 1.5 → 4.0**
   - Calibrado vivo en D1: umbral 1.5×ATR era demasiado bajo (casi toda pierna leg-based supera 1.5×ATR).
   - 4.0 da set limpio de giros mayores (filtra ruido de pierna).

5. **Estructura BOS/CHoCH sin cambios:**
   - Ya tenía L1/L2/L3 por escala (SC_MAJOR/SC_SWING/SC_INTERNAL en `f_drawStructure`).
   - Queda como capa fuerte por contraste.

## Validación viva (D1/H1/M5, Operación)

- **Apply:** 0/0 sin CE10117/RE10045/OOM.
- **Labels:** confirmados `size: "tiny"`, alpha 0x8C = transp 45 (dominante).
- **Colisión resuelta en 3 TFs:** swings tenues de fondo, estructura BOS/CHoCH destaca, sin gluing.
- **Hallazgo de fondo:** `strength=amplitud÷ATR` discrimina poco en TFs bajos (H1/M5 casi todas las piernas >4×ATR → 350 retenidos casi todos pasan umbral, pero por L3 tenue quedan como fondo aceptable). Si se quiere thinning fino en H1/M5, la palanca sería `i_swingMaxKeep` o ventana visible (fuera alcance de esta colisión).

## GOTCHAs de la sesión

1. **Guardar slot (Pine Save) NO actualiza instancia aplicada:**
   - La instancia se queda pinneada al bytecode viejo.
   - Fix: REMOVER la instancia y RE-AÑADIR fresca vía botón ▶/Añadir al gráfico del editor.
   - Reiniciar TV solo NO bastó: reaplica misma instancia.
   - Nueva instancia = `gRWnMq`.

2. **Render lag real tras `indicator_set_inputs`:**
   - Esperar ~15-35s y re-consultar `data_get_pine_labels` (puede cachear).

3. **Mapa de inputs Visual (referencia):**
   - in_5=`i_showMajor`
   - in_6=`i_showSwings`
   - in_7=`i_swingStructLen`
   - in_8=`i_swingMaxKeep`
   - in_9=`i_swingDomAtr` (default ahora 4.0)
   - in_10=`i_showStruct`
   - in_118=`i_densidad`
   - in_120=`i_kLeg`
   - in_121=`i_swingMinorLabels` (nuevo)

## Estado post-sesión

- **F1-GATE:** BLOQUEADA (sin cambios).
- **ADR:** Sin nuevo (Visual-only bajo ADR-016/ADR-019 existentes).
- **Git tag:** Sin nuevo.
- **Commits:** Único `5374746`.

## Pendiente S119

**Continuar matriz de auditoría concepto×variante×TF×{nativo,heredado}:**
- Siguientes celdas: OB/FVG nativos D1 (tras esta colisión resuelta).
- Luego herencia MTF H1/M5.
- Opcional: afinar densidad swings en H1/M5 si molesta (`i_swingMaxKeep`/ventana).

**Firma F1-GATE:** sigue pendiente hasta cerrar toda la matriz.

## Referencias
- [[Sesion-117]] — estructura swings leg-based + dim-to-focus
- [[rubrica-curacion-y-colision-paleta]] — reglas de jerarquía L1/L2/L3
- Commit `5374746` — código Visual-only
