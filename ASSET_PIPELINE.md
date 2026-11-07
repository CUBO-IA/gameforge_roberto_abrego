# Pipeline de producción e integración de assets

## Estado local comprobado

Hay imágenes en `assets/sprites/` y `assets/hub_catalog/`, manifiestos gf-anim-v1, metadatos de procedencia, `assets/hub_index.json`, la CLI y módulos de `tools/asset_hub/` para escaneo, validación, búsqueda, previsualización, SQLite y exportación. `game/render/animation.py` carga manifiestos y recorta fotogramas. `TileRenderer` pre-renderiza un mapa estático con primitivas.

## Flujo previsto

1. Buscar primero en `assets/hub_index.json`/Asset Hub; registrar criterios y clips requeridos. Evitar búsquedas externas si el catálogo resuelve la necesidad.
2. Si falta recurso, investigar la página original y guardar autor, URL, licencia SPDX, atribución, restricciones, resolución, formato y modificaciones. No descargar paquetes completos sin necesidad.
3. Mantener originales externos inmutables en zona de origen; adaptar/exportar a rutas de juego separadas. Documentar cambios y hashes.
4. Validar geometría, transparencia, dimensiones, manifiesto y licencia con `tools/asset_hub/`; detectar hashes repetidos antes de indexar.
5. Escribir el manifiesto gf-anim-v1: atlas, rectángulos, pivotes, duración, loop, prioridad, sockets y eventos. Probar clips/frames con `load_animation_manifest`.
6. Integrar únicamente en `game/render/` y `game/scenes/` siguiendo propiedad PRESENTACIÓN. Conservar entidades y colisiones puras. Cargar superficies al entrar a escena, no por frame.
7. Validar con pruebas existentes, captura real headless y comparación antes/después a igual semilla. Registrar carga, p50/p95 frame time y memoria con `tools/visual_benchmark.py`.
8. Actualizar índice/licencias y reporte. No declarar finalizado un recurso que solo sea ejemplo de catálogo.

## Categorías y entregas

- Personajes/enemigos: atlas, manifiesto, licencia, pivotes, clips reales usados y prueba de orientación.
- Terreno: tileset/atlas, mapeo de TileType→tile visual, reglas de bordes/autotile, variantes de suelo y preservación de colisión.
- Decoración/interactivos: origen, tamaño de colisión visual y capas de profundidad.
- VFX/UI: superficies reutilizables, límites de resolución, contraste y estado visual.

No se propone una dependencia runtime. Pygame CE y JSON existentes bastan para integrar spritesheets; herramientas offline se justifican por tarea y no se importan desde `game/`.
