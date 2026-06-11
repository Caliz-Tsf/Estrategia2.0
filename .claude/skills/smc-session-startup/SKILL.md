---
name: smc-session-startup
description: Protocolo de arranque de sesión del proyecto Estrategia 2.0 - estado, rama, salud de herramientas, plan de sesión. Ejecutar al inicio de cada sesión de trabajo.
---

# Startup de sesión

Ejecutar en orden. Cada paso reporta ✅/⚠️/❌. Solo los BLOQUEANTES detienen.

1. [BLOQUEANTE] Leer memory/ESTADO-ACTUAL.md → fase, sprint, siguiente tarea,
   bloqueos. Si no existe → algo está muy mal: reconstruirlo desde git log antes
   de seguir.
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
