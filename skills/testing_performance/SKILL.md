# Skill: Pruebas Automatizadas y Medición de Rendimiento (Testing & Performance)

## 1. Propósito
Establecer la metodología de pruebas automatizadas, control de regresiones y perfilado continuo de rendimiento (frame time, memoria RAM, tiempos de carga) para validar objetivamente cada cambio de código sin depender de impresiones subjetivas o afirmaciones no fundamentadas.

## 2. Contexto de aplicación
Aplica en `tests/`, `benchmark/`, `tools/verify.py` y en el flujo de trabajo de todos los agentes (especialmente QA/INTEGRADOR y antes de entregar cualquier tarea en `tasks/BOARD.md`).

## 3. Instrucciones
1. **Regla de oro: Medir antes de optimizar**: Ningún agente tiene autorización para introducir complejidad arquitectónica o micro-optimizaciones sin un benchmark que demuestre el cuello de botella previo y posterior.
2. **Puerta única de verificación**: La suite oficial es `tools/verify.py` (ejecutable con `python tools/verify.py` o `uv run --extra dev python tools/verify.py`). Toda entrega debe reportar:
   - Lint con `ruff check .` (0 errores).
   - Suite completa de `pytest` (100% passed).
   - Benchmark de simulación dentro del umbral acordado.
3. **Métricas obligatorias de rendimiento**:
   - Frame time de simulación: medir p50, media, p95 y máximo en milisegundos.
   - Presupuesto de 60 FPS = 16.67 ms total (simulación pura debe consumir < 2.0 ms en p95).
   - Tiempo de generación procedural: p95 < 10 ms para 64x48.
4. **Uso de `tracemalloc`**: Para tareas que afecten a la carga de mapas o gestión de entidades, perfilar las asignaciones de memoria y verificar la ausencia de fugas (memory leaks) entre cambios de escena.
5. **Determinismo en pruebas**: Fijar siempre la semilla aleatoria en los tests que involucren generación o IA para garantizar que los fallos sean 100% reproducibles.

## 4. Buenas prácticas
- **Separar pruebas unitarias de pruebas con display**: Las pruebas de lógica deben ejecutarse sin abrir ventanas mediante mocks o los drivers dummy de SDL (`SDL_VIDEODRIVER=dummy`).
- **Pruebas de regresión obligatorias**: Cuando se corrija un defecto o bug, añadir un test específico que reproduzca el error antes del arreglo y confirme la solución tras el arreglo.
- **Informar honestamente**: Si una prueba no pudo ejecutarse en el entorno del agente, declararlo explícitamente en el informe de entrega de la tarea; nunca inventar resultados.

## 5. Referencias técnicas
- `benchmark/METRICS.md`: Rúbrica de evaluación y parámetros de referencia.
- `benchmark/bench_simulation.py` y `benchmark/bench_generation.py`.
- `tools/verify.py`: Script de validación integral.
- Documentación oficial de `pytest` y módulo estándar `tracemalloc`.

## 6. Procedimientos
### Paso 1: Ejecución de verificación integral
```bash
python tools/verify.py
```
### Paso 2: Perfilado de memoria con tracemalloc
```python
import tracemalloc

tracemalloc.start()
# Ejecutar simulación o generación de 1000 frames
current, peak = tracemalloc.get_traced_memory()
tracemalloc.stop()
print(f"Pico de RAM: {peak / 1024 / 1024:.2f} MB")
```
### Paso 3: Estructuración de un test de regresión
```python
def test_regression_bug_description():
    # 1. Arrange con estado específico del bug
    # 2. Act ejecutando el método conflictivo
    # 3. Assert verificando que no ocurre la excepción o estado anómalo
```

## 7. Criterios de aceptación
- `tools/verify.py` termina con código de salida 0.
- Cero advertencias críticas o errores no gestionados en la suite de pruebas.
- Ninguna prueba tarda más de 5 segundos de forma individual.
- Tiempos de simulación p95 claramente documentados en el informe de entrega.

## 8. Pruebas recomendadas
- `tests/test_headless_app.py`: Smoke test del ciclo principal sin interfaz gráfica.
- `tests/test_sim.py`: Verificación de consistencia del modelo cinemático y combate.
- Ejecución de `benchmark/bench_simulation.py` con variación de carga (24, 50, 100 entidades).
