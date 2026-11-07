# Skill: Informes de Control de Calidad y Regresión (QA Reporting)

## 1. Propósito
Estandarizar el proceso de auditoría, generación de informes de calidad, clasificación de severidad de defectos, reporte de métricas de benchmark y verificación formal de tareas completadas para garantizar que ningún cambio de código introduzca regresiones o degrade la estabilidad del juego.

## 2. Contexto de aplicación
Se aplica en `tasks/reports/`, `prompts/02_qa_agent.md`, revisiones de integración y tareas de validación ejecutadas por el rol QA/INTEGRADOR.

## 3. Instrucciones
1. **Estructura estricta del informe de tarea (`tasks/reports/T-XXX.md`)**:
   - Identificador de la tarea y agente responsable.
   - Resumen ejecutivo de cambios entregados.
   - Lista detallada de archivos modificados, creados o eliminados.
   - Comandos ejecutados y resultados reales con captura de texto (pytest, ruff, benchmarks).
   - Matriz de riesgos residuales o trabajo pendiente.
2. **Clasificación estándar de severidad de defectos**:
   - **CRÍTICO / BLOQUEANTE**: Crash del juego, fallo en la carga de partida, pérdida de datos, o violación de contratos de arquitectura. Impide el merge inmediatamente.
   - **ALTO**: Funcionalidad principal rota o fallo de regresión en pruebas existentes.
   - **MEDIO**: Comportamiento anómalo no crítico, degradación de FPS que no rompe el presupuesto p95, o falta de validación de datos.
   - **BAJO**: Problema cosmético menor, advertencia de linter no bloqueante o desalineación visual no funcional.
3. **Reproducibilidad obligatoria**: Todo defecto reportado debe incluir pasos mínimos para reproducirlo, semilla utilizada (si aplica) y archivo de log asociado.
4. **Prohibición estricta de autoaprobación**: El agente que implementa el código jamás puede emitir el informe de verificación final como QA; la verificación corresponde a QA/INTEGRADOR o DIRECTOR.

## 4. Buenas prácticas
- **Honestidad documental absoluta**: Informar con total transparencia qué pruebas se ejecutaron y qué pruebas no pudieron ser completadas debido a limitaciones del entorno.
- **Evidencia factual comprobable**: Incluir tiempos exactos de benchmark, número de tests pasados y hash de commit evaluado.
- **Pruebas en frío**: Probar la aplicación en un entorno limpio sin dependencias residuales o archivos generados fuera de control.

## 5. Referencias técnicas
- `prompts/02_qa_agent.md`: Prompt de rol del agente de aseguramiento de calidad.
- `benchmark/METRICS.md`: Rúbrica de evaluación objetiva de agentes.
- `tools/verify.py`: Herramienta estándar de comprobación.

## 6. Procedimientos
### Paso 1: Ejecución de la batería de pruebas
```bash
python tools/verify.py
python -m game --headless --frames 60
python benchmark/bench_generation.py
```
### Paso 2: Redacción del informe de aseguramiento de calidad
```markdown
# Informe de QA — Tarea T-XXX
**Estado:** APROBADA / RECHAZADA
**Commit evaluado:** [hash]
**Resultado de pruebas:** 132/132 passed
**Lint (ruff):** 0 errores
**Benchmark Simulación:** p50: 0.39 ms, p95: 0.69 ms (presupuesto 16.67 ms)
**Veredicto:** Aprobado para integración en main.
```
### Paso 3: Actualización del estado en el tablero
Mover la tarea a `VERIFICADA` si se cumplen todos los criterios, o a `EN CURSO` con hallazgos para corrección por el especialista.

## 7. Criterios de aceptación
- Todos los informes de QA son archivados en `tasks/reports/` con formato uniforme.
- Cero tareas integradas sin informe de verificación firmado.
- Tiempo de respuesta de auditoría ágil y reproducible.

## 8. Pruebas recomendadas
- Verificación cruzada de cobertura de tests unitarios y de integración.
- Ejecución de pruebas de estrés con duraciones prolongadas (smoke test de 1000 frames).
