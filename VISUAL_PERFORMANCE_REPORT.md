# Informe de rendimiento visual — baseline pendiente

**Fecha:** 2026-11-07. **Resultado de medición:** no disponible.

## Procedimiento intentado

`python tools/visual_benchmark.py --label mission008-baseline --frames 60`

Resultado real: salida con código 1; `ModuleNotFoundError: No module named 'pygame'`. No se generaron capturas ni JSON de benchmark. No se asignan FPS, memoria, carga ni cantidad visual efectiva sin medir.

También falló el preflight Graphify: `python tools/graph_ops.py query ...` y `affected ...` importan `tools.graph_memory`, que no existe en el entorno/repo disponible (`ModuleNotFoundError`).

## Infraestructura existente

`tools/visual_benchmark.py` implementa escena headless, semilla fija, frames deterministas, medición de carga, frame time p50/p95/máximo, FPS equivalente, tracemalloc y capturas PNG. Está listo para producir línea base cuando pygame-ce esté instalado. Incluye un ataque real para capturar efectos. La medición de memoria Python no equivale al RSS total del proceso o memoria GPU.

`TileRenderer` cachea una superficie estática. `Lighting` retiene máscaras/superficies. `draw_attack_arc` construye superficie de ventana cuando el ataque está activo. No se midió el coste de estos puntos.

## Repetición requerida

En el mismo equipo/entorno con pygame-ce y dependencias del proyecto:

1. Ejecutar 180+ frames con `--seed 20261107`, guardar baseline actual y capturas.
2. Integrar un cambio visual acotado y repetir igual hardware, semilla y frames.
3. Comparar carga, p50/p95/max, FPS equivalente, memoria Python y capturas reales.
4. Investigar p95 de frame superior a 16.67 ms y registrar resolución, sistema, SDL y configuración.

No se afirma aceptación de 60 FPS ni rendimiento en CPU/GPU integrada hasta completar esa medición.
