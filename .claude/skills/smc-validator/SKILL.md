---
name: smc-validator
description: Protocolo de validación de un concepto SMC implementado - delega la auditoría al agente smc-validator-agent y gestiona el resultado. Usar tras implementar o modificar cualquier concepto.
---

# Validación de concepto SMC

1. Identificar el concepto y el archivo Pine afectado.
2. Tomar screenshots frescos (TV MCP) en los casos de prueba de
   docs/reglas-smc-ict.md para ese concepto.
3. Invocar al agente `smc-validator-agent` con: concepto + archivo + screenshots.
4. Procesar el veredicto:
   - APROBADO (≥90) → registrar score en docs/sprint-runs/validaciones.md y
     continuar el ciclo (commit).
   - RECHAZADO → aplicar las correcciones exactas del reporte → recompilar →
     volver a 2. Máximo 3 iteraciones; a la 4ª, escalar al usuario con el
     historial de intentos (algo está mal en la regla o en el enfoque).
   - REGLA INCOMPLETA → detener y completar docs/reglas-smc-ict.md con el
     usuario antes de seguir.
