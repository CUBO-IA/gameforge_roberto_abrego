# Directiva de arquitectura

## Capas propuestas
- `game/core`: configuración, ciclo de vida, eventos y reloj.
- `game/platform`: integración con Pygame CE.
- `game/input`: acciones abstractas y mapeo de teclas.
- `game/world`: mapa, tiles, escenas y cámara.
- `game/entities`: jugador, NPC y entidades.
- `game/systems`: interacción, inventario, combate, misiones.
- `game/persistence`: serialización, guardado y migraciones.
- `game/ui`: HUD, menús y pantallas.
- `game/assets`: carga y caché de recursos.
- `tests`: pruebas unitarias e integración.

No crear todos los directorios vacíos desde el inicio. Crear módulos cuando exista una necesidad real.

## Reglas
- La lógica de dominio no debe depender directamente de Pygame cuando pueda evitarse.
- El renderizador recibe estado y dibuja; no decide reglas de negocio.
- La entrada se traduce a acciones, no se consulta teclado desde cada entidad.
- Persistir datos versionados; validar datos al cargar.
- Recursos compartidos se cargan mediante un gestor/caché.
- El bucle principal no realiza I/O bloqueante.
- El tiempo de simulación debe ser controlable en pruebas.

## Dependencias
Pygame CE es la dependencia principal. Pymunk solo se añade si los requisitos de física lo justifican. Tiled/LDtk pueden utilizarse como editores externos; el juego debe definir claramente el formato de importación.
