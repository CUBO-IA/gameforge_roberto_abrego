# Directiva de integración multiagente (04_INTEGRATION.md)

## Flujo de trabajo estándar
1. **Asignación**: El DIRECTOR define y aprueba la tarea en `tasks/BOARD.md`, especificando ID, responsable y archivos permitidos según `architecture/OWNERSHIP.md`.
2. **Aislamiento**: El especialista crea una rama de trabajo `task/T-XXX-descripcion` a partir de `main` actualizado.
3. **Desarrollo**: El especialista implementa la funcionalidad exclusivamente dentro de su ámbito de archivos asignado.
4. **Verificación local**: El especialista ejecuta `tools/verify.py` y genera el informe de entrega en `tasks/reports/T-XXX.md`. Mueve la tarea a `ENTREGADA`.
5. **Auditoría e integración**: QA/INTEGRADOR revisa el diff, comprueba el cumplimiento de contratos de interfaces, ejecuta la suite de regresión y realiza el merge en `main`.
6. **Aprobación de cierre**: El DIRECTOR revisa el informe final de QA y marca la tarea como `VERIFICADA`.

## Prohibiciones estrictas
- Prohibido hacer merge en `main` si `tools/verify.py` reporta fallos en lint, pruebas o benchmarks.
- Prohibida la autoaprobación: ningún agente puede aprobar o integrar su propio código en tareas críticas o cambios de contratos.
- Prohibido editar archivos compartidos (`architecture/CONTRACTS.md`, `game/core/config.py`, `game/data/config.json`) sin una propuesta previa aprobada por el DIRECTOR.
- Prohibido resolver conflictos de fusión sobreescribiendo o eliminando silenciosamente el trabajo de otros agentes.
- Prohibido dejar placeholders (`pass`, `TODO`, `NotImplementedError`) en rutas de código funcionales.

## Estructura del informe de entrega (`tasks/reports/T-XXX.md`)
- ID de tarea, fecha y agente responsable.
- Objetivo y justificación técnica.
- Archivos creados, modificados o eliminados.
- Contratos de interfaces afectados o añadidos.
- Dependencias introducidas y justificación de licencia.
- Resultados textuales de `tools/verify.py` (lint, pytest, benchmarks).
- Riesgos identificados y próximos pasos recomendados.
