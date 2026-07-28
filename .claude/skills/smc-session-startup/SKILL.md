---
name: smc-session-startup
description: Protocolo de arranque de sesión del proyecto Estrategia 2.0 - estado, rama, salud de herramientas, plan de sesión. Ejecutar al inicio de cada sesión de trabajo.
---

# Startup de sesión

Ejecutar en orden. Cada paso reporta ✅/⚠️/❌. Solo los BLOQUEANTES detienen.

1. [BLOQUEANTE] Leer memory/ESTADO-ACTUAL.md → fase, sprint, siguiente tarea,
   bloqueos. Si no existe → algo está muy mal: reconstruirlo desde git log antes
   de seguir.
   - **Chequeo de tamaño ANTES de leer** (`wc -c memory/ESTADO-ACTUAL.md`):
     techo **40 KB**. Entre 40 KB y 256 KB → ⚠️ avisar al usuario: `smc-doc-updater`
     dejó de rotar. **Por encima de 256 KB el tool `Read` NO puede abrirlo** y el
     arranque se haría a ciegas → ❌ BLOQUEANTE: podar (REGLA ABSOLUTA 3 de
     `smc-doc-updater`) antes de seguir. Pasó de verdad de S140 a S146 (291 KB).
   - **Chequeo de frescura:** el título de «Cómo arrancar la próxima sesión» debe
     nombrar la sesión que empieza AHORA. Si nombra una sesión vieja, la sección se
     apiló en vez de reemplazarse → no fiarse de ella, reconstruir el plan con el
     usuario. Estuvo congelada en S090 durante 56 sesiones.
2. git status + git branch → working tree limpio y rama correcta
   (fase-N/<sprint>). Sucio → preguntar al usuario antes de tocar nada.
3. [Solo si la sesión toca TradingView] tv_health_check del TV MCP.
   ❌ → las tareas TV se posponen; las de docs/código local pueden seguir.
4. [Opcional] claude-mem dashboard (http://localhost:37777) y context-mode
   activos. ❌ → ⚠️ y continuar (no son bloqueantes).
5. [Solo sesiones de validación Fase 3] morning_brief con rules.json → bias
   EURUSD del día.
6. Proponer el plan de la sesión: la "siguiente tarea" de ESTADO-ACTUAL.md +
   tiempo estimado + qué agentes/skills se usarán. Confirmar con el usuario.

## Salida
Resumen de arranque: estado de los 6 checks + plan de sesión confirmado.
