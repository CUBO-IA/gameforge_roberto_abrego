# Skill: Generación Procedural de Niveles (Procedural Generation)

## 1. Propósito
Diseñar, generar y validar mazmorras, cuevas y mapas 2D reproducibles a partir de semillas pseudoaleatorias, garantizando que el espacio generado sea siempre jugable, completamente navegable entre objetivos clave (sin salas aisladas ni callejones bloqueados) y cumpla con presupuestos estrictos de tiempo de carga.

## 2. Contexto de aplicación
Se aplica en `game/world/generation.py`, `game/world/tilemap.py` y los benchmarks asociados (`benchmark/bench_generation.py`).
Controla la colocación de salas, pasillos, puntos de aparición del jugador, cofres, enemigos, altares y escaleras/transiciones de piso.

## 3. Instrucciones
1. **Determinismo por semilla**: `generate_dungeon(seed, floor, config)` debe producir la misma configuración exacta de tiles y entidades para la misma terna de entrada.
2. **Validación topológica obligatoria (BFS/Flood Fill)**: Todo mapa generado debe verificarse inmediatamente tras la creación de pasillos. Es un requisito estricto que:
   - El punto de aparición del jugador (`spawn`) tenga ruta hacia el altar/salida (`stairs`).
   - Todos los cofres interactuables y puntos de interés sean accesibles desde el `spawn`.
   - Si la validación falla, descartar el intento y reintentar con una variación determinista de semilla hasta agotar `attempts`.
3. **Escalado con la profundidad (`floor`)**: La cantidad de enemigos, densidad de salas y tipos de peligro deben calcularse mediante fórmulas puras dependientes del piso (`floor`).
4. **Presupuesto de generación**: La generación de una planta de 64x48 o 128x96 debe completarse en menos de 10 ms (p95) en CPUs estándar.
5. **Separación de generación y visuales**: La generación genera una representación lógica (`TileMap`, `Room`, `Vec2`). No carga imágenes ni genera texturas.

## 4. Buenas prácticas
- **RNG aislado**: Instanciar siempre un generador `random.Random(seed)` local en la función; nunca alterar el generador global `random.seed()`.
- **Salas con padding**: Aplicar separación mínima entre salas rectangulares (`overlaps_padded`) para evitar que se fusionen de forma amorfa y garantizar muros sólidos perimetrales.
- **Corredores en L deterministas**: Conectar centros de salas mediante corredores ortogonales horizontales y verticales controlados.
- **Identificadores estables**: Generar identificadores únicos y deterministas para cofres (`chest_{idx}`) y enemigos (`e_{floor}_{room}_{idx}`) para permitir la persistencia fiel del estado.

## 5. Referencias técnicas
- `architecture/CONTRACTS.md`: Contrato de `game.world.generation.generate_dungeon`.
- Artículos canónicos de RogueBasin: "Basic BSP Dungeon Generation", "Connecting Rooms with Corridors".
- Tutorial de mapas y Flood Fill en `python-tcod`.
- Benchmark de referencia: `benchmark/bench_generation.py`.

## 6. Procedimientos
### Paso 1: Inicialización con semilla y matriz sólida
```python
rng = random.Random(seed)
tilemap = TileMap.filled(width, height, tile_size, TileType.WALL)
```
### Paso 2: Ubicación de salas no solapadas
```python
rooms: list[Room] = []
for _ in range(attempts):
    room = Room(x, y, w, h)
    if not any(r.overlaps_padded(room, padding=2) for r in rooms):
        rooms.append(room)
        carve_room(tilemap, room)
```
### Paso 3: Conexión ortogonal de centros
```python
for i in range(len(rooms) - 1):
    connect_centers(tilemap, rooms[i].center, rooms[i+1].center, rng)
```
### Paso 4: Validación BFS de conectividad
```python
reachable = flood_fill(tilemap, spawn_point)
if not all(p in reachable for p in critical_points):
    raise GenerationError("Mapa desconectado")
```

## 7. Criterios de aceptación
- 100% de los mapas generados son navegables desde el spawn hasta el objetivo.
- Cero muros perimetrales abiertos (el borde del mapa siempre es sólido).
- Tiempo de generación medido: p95 < 10 ms para mapas estándar (64x48) verificado en benchmark.
- Idempotencia: el guardado de la semilla y piso regenera exactamente el mismo layout.

## 8. Pruebas recomendadas
- `tests/test_generation.py`: Pruebas de conectividad BFS, distribución de salas, número de cofres y determinismo ante 50 semillas distintas.
- `benchmark/bench_generation.py`: Verificación de distribución de tiempos (p50, p95, max) y estabilidad de memoria.
