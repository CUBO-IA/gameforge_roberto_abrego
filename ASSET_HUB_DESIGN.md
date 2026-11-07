# Diseño del GameForge Asset Hub

## Estado

El Hub ya está implementado parcialmente en `tools/asset_hub/`: CLI, SQLite, escáner, esquema de catálogo JSON, consulta por tipo/tamaño/clips, hashes, validación, vista previa y exportador. Pruebas asociadas existen en `tests/test_asset_hub.py`. `assets/hub_index.json` declara ocho entradas y `assets/.hub/asset_hub.db` es índice local.

## Fuente de consulta para agentes

Consultar el índice y la CLI existente antes de crear o buscar assets. La base SQLite sirve para búsqueda local; el índice JSON se puede revisar y versionar. Registrar actualización de ambos de forma reproducible para evitar diferencias.

## Campos mínimos por asset

ID estable, categoría, tags/estilo, rutas relativas, dimensiones, modo/alpha, tamaño de frame y layout, hash SHA-256, hash perceptual cuando esté disponible, clips/direcciones, ancla, compatibilidad, autor, URL/repositorio, SPDX, atribución, modificaciones y estado de validación.

## Brechas y siguientes pasos

- Completar entradas para los atlas propios slime/wisp/brute y verificar hashes frente a los archivos reales.
- Alinear `assets/README.md`, `hub_index.json` y `assets/.hub/asset_hub.db`; el README contradice la existencia actual de binarios.
- Tratar `has_paperdoll_layers`, `tilemap_ready` y claims de compatibilidad como datos que deben validarse, no inferirse por nombre.
- Añadir detección de dimensiones/hash en verificación automatizada y un reporte de licencias sin duplicar lógica del Hub.
- La búsqueda por similitud no reemplaza inspección de duplicados ni validación visual humana.

## Seguridad y arquitectura

El Hub es tooling de desarrollo; `game/` no debe importar SQLite, CLI ni escáner. Las rutas se validan antes de importar/exportar. La inspección se limita a formatos de imagen/datos conocidos; no ejecutar contenido de assets. No introducir servicio externo ni dependencia runtime.
