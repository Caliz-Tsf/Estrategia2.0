# Sesion-060 — Módulo Mentores (continuación) + Bugfix Pipeline Visión
**Fecha:** 2026-06-25 (continuación Sesion-059)  
**Tipo:** Infraestructura (módulo mentores + tooling visión), **NO Pine/MQL5**  
**Rama:** `pine/sistema-completo` (sin cambios, core intacto)

---

## Objetivo
Cierre formal de la sesión anterior (Sesion-059) y registro del commit adicional descubierto post-sesión que implementa el bugfix de colisión de WorkDir en el pipeline de visión boxxocode.

---

## Completado

### 1. Bugfix pipeline visión boxxocode (commit 35efc33)
**Problema raíz (HALLAZGO POST-SESION-059):** `process-channel.ps1` lanza múltiples instancias de `process-video-vision.ps1` en paralelo. Ambas descargan frames a `%TEMP%\smc-video-vision\frames` y cada script **borra y recrea la carpeta al arrancar**. Resultado: video A baja frames 001-200, el script de A borra la carpeta, video B intenta leer sus frames pero ya están borrados → `FileNotFoundError` en `nvidia_vision_describe.py`.

**Fix implementado:**
- **WorkDir único por PID:** `smc-video-vision\frames` → `smc-video-vision\frames-$PID` (e.g., `frames-12345`).
- **`nvidia_vision_describe.py` refactorizado:** degradación frame-por-frame si uno falla (log de error, se salta, continúa) en vez de tumbar el video entero.
- **Limpieza al terminar:** cada proceso limpia su carpeta `frames-$PID` sin afectar a otros.

**Verificación:** descarga paralela de 3 videos boxxocode cortos sin colisión; cada línea del .md final contiene el resumen del video.

**Commit:** `35efc33` · 2026-06-25 (post-cierre S059)

### 2. Mentor ICT — 2022 Mentorship, LOTE 1 COMPLETO (TRABAJO PRINCIPAL DE ESTA SESIÓN)
Leídos densos **intro + episodios 2-13** (arco fundacional canónico, ~600k chars) y destilados a
`D:\obsidian\boveda MENTE\Mente\Mentores\ict\knowledge\2022-mentorship.md` (10 secciones). Contenido:
- **Modelo canónico:** bias → barrido de liquidez (stop hunt) → displacement/MSS → FVG → entrada limit → targets IRL/ERL.
- **Conceptos cuantificados:** FVG 3-velas (bordes exactos), Order Block real ("change in state of delivery" / serie de velas + imbalance), premium/discount 50%, **Power Three** (acum/manip/distrib) + **Judas Swing**, **Opening Range projection**, measured move ×2, **breaker** (mitad inferior de la vela).
- **Market structure:** nesting STH/ITH/LTH (Larry Williams) + interpretación avanzada (ITH/ITL = key levels formados al rebalancear, no violar = invalidación); **institutional order flow** (up-close = resistencia en bajista / down-close = soporte en alcista).
- **Operativa:** kill zones NY (Asia 7-9pm, Londres 2-5am, NY 7-10am, no-trade 12-1, tarde 1:30, MOC 3:40-4), top-down 15m→1m, riesgo 1.25-1.5% alumno, pyramiding mayor-primero, neutral/"I don't know", meta 20%/mes, fib -1/-1.5 std para targets.
- **Tensiones con Estrategia 2.0 (anotadas para la ficha):** R:R por parciales (~3.5:1 en ejemplos, NO 1:3 fijo) y filtro horario fuerte (vs ADR-001 sin filtro horario).

### 3. Contexto previo (Sesion-059, no nuevo esta sesión)
- Corpus ICT: 202/203 transcripciones bajadas (falta Lecture #14, age-gate).
- `knowledge/madre-2026.md` iteración 1 (4 lectures 2026) — ya existía desde S059.
- Detalle inter-sesión vivo en memoria Claude: `ict-mentor-madre-build.md`.

---

## Discrepancia hallada y registrada

**NOTA CRÍTICA:** El resumen oral recibido para cierre de Sesion-059 informó **2 commits:**
```
4094839 fix(mentores): descarga audio-only para evitar streams truncados de ICT
bdbd36c feat(mentores): pipeline de vision NVIDIA para canales mudos (boxxocode)
```

**REALIDAD (git log):** 3 commits después de Sesion-059:
```
35efc33 fix(mentores): aislar WorkDir por PID en pipeline de vision (evita colision de frames)
bdbd36c feat(mentores): pipeline de vision NVIDIA para canales mudos (boxxocode)
4094839 fix(mentores): descarga audio-only para evitar streams truncados de ICT
```

El commit `35efc33` (bugfix colisión) fue implementado POST-SESION-059 pero ANTES del cierre documentado. Esta sesion (060) registra **ambos hallazgos**: (a) el resumen oral reflejado como Sesion-059.md existente, (b) el commit real 35efc33 aquí capturado para no perderlo.

---

## Commits confirmados (Sesion-060 = Cierre formal)

```
35efc33 fix(mentores): aislar WorkDir por PID en pipeline de vision (evita colision de frames)
```

(Los 2 de Sesion-059 ya están registrados en su documento.)

---

## Estado del código Pine/Core

**INTACTO.** No hubo cambios al sistema SMC/ICT.
- CORE: 1517 líneas, SHA `80fad14dd8d03758`, compila 0/0 los 3.
- core-sync: OK.
- **F1-GATE:** pendiente firma usuario (abierto desde Sesion-057).

---

## Decisiones

- **Paralización determinista:** bugfix PID aisla ejecuciones; cada proceso ahora accede a su `frames-$PID` sin interferencia.
- **Degradación robusta:** `nvidia_vision_describe.py` continúa si un frame falla (nota error por frame).

---

## Sin ADR, sin gate, sin tag

- Bugfix infraestructura, no arquitectura de sistema.
- Mentores = laboratorio paralelo, no componente crítico de Fase 1-2.

---

## Notas

- **Sesion-060 = sesión de cierre formal** de la actividad paralela mentores iniciada en Sesion-059.
- **Corpus completo:** 202/203 lectures bajadas, accesible para densificación MAP→REDUCE en sesiones posteriores.
- **Siguiente:** usuario elige Opción A (Paso 4 motor strength) O Opción B (Fase 2 motor decisión) para Sesion-061+. Enjambre (mentor ICT) continúa paralelo.

---

## Refs

- [[Sesion-059]] — sesión principal (mentores + visión + madre iniciada).
- `memory/ict-mentor-madre-build.md` — tracking construcción MAP/REDUCE.
- `scripts/process-video-vision.ps1` (línea: WorkDir unique per PID).
- `scripts/nvidia_vision_describe.py` (degradación frame-por-frame).
