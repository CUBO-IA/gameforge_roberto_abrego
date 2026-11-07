# Calidad, seguridad y rendimiento (03_QUALITY_AND_SECURITY.md)

## Seguridad y robustez
- Validar minuciosamente los archivos de guardado JSON antes de deserializarlos en objetos de dominio.
- No ejecutar código arbitrario contenido en archivos de datos (prohibido `eval`, `pickle` no seguro, o deserialización refleja).
- Establecer límites estrictos de memoria: limitar tamaños máximos de mapas, número de salas y capacidad de inventario.
- Manejar todas las rutas de archivos de forma canónica mediante `pathlib.Path`.
- Cero secretos, tokens o claves de API en el repositorio.
- Registrar formalmente la procedencia y licencia de cada asset externo en `assets/README.md`.
- Mantener pruebas continuas para deserialización de partidas con datos corruptos, incompletos o de versiones anteriores.

## Umbrales y control de rendimiento
- **Regla de oro**: Medir antes de optimizar; justificar cualquier cambio de rendimiento mediante métricas comparativas objetivas.
- **Presupuesto de 60 FPS**: Tiempo de fotograma total inferior a 16.67 ms.
  - La simulación pura (`game/sim/`) debe mantenerse con un tiempo p95 < 2.0 ms.
  - La búsqueda de rutas (A*) debe operar con cuota estricta de tiempo de CPU (`budget_ms <= 1.5 ms`).
- **Generación procedural**: Tiempo de generación p95 < 10.0 ms para mapas de 64x48 tiles.
- **Consumo de memoria**: Evitar asignaciones masivas de objetos volátiles en el bucle caliente para prevenir pausas del Garbage Collector.

## Criterios mínimos de aceptación (DoD)
- Arranque y cierre limpios sin fugas de recursos ni errores de SDL.
- 100% de la suite de pruebas automatizadas en verde (`pytest -q`).
- 0 errores o advertencias en el análisis estático (`ruff check .`).
- Benchmark de simulación dentro del umbral de rendimiento fijado.
- Compatibilidad absoluta con ejecución en modo headless (`--headless`).
