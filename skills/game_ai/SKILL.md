# Skill: Inteligencia Artificial de Videojuegos (Game AI)

## 1. Propósito
Diseñar, implementar y mantener los sistemas de percepción, toma de decisiones, máquinas de estados (FSM) y navegación espacial (A*, steering) para NPCs y enemigos, garantizando presupuestos de tiempo de CPU acotados y escalabilidad para decenas de entidades simultáneas.

## 2. Contexto de aplicación
Aplica en `game/ai/`, `game/entities/enemies.py`, `game/entities/npc.py` y los catálogos de comportamiento en `game/data/enemies.json`.
No abarca el renderizado ni la aplicación física de colisiones (gestionada por `game/world/collision.py`).

## 3. Instrucciones
1. **Presupuesto por frame explícito**: Todo algoritmo de búsqueda de rutas (`A*`) debe recibir un parámetro `budget_ms` o cuota máxima de nodos explorados. Si se agota el presupuesto, devolver la mejor ruta parcial calculada o `None`.
2. **Caché y reutilización de rutas**: No recalcular caminos completos en cada fotograma. Cachear caminos calculados por tupla `(origen_tile, destino_tile)` o invalidar solo cuando el objetivo se desplace más de `N` tiles.
3. **Comportamientos dirigidos por datos (Data-Driven)**: Definir arquetipos de IA (patrulla, persecución melee, acosador a distancia, emboscada) en archivos JSON (`data/enemies.json`). El código de FSM procesa parámetros de datos, no clases hardcodeadas por nombre de enemigo.
4. **Separación de percepción y decisión**: Separar el chequeo de línea de visión (`has_line_of_sight`) y distancia euclidiana del cálculo de cinemática o steering.
5. **Actualización escalonada (Staggering)**: Para entidades alejadas del campo de visión del jugador, reducir la frecuencia de actualización de su IA (ej. actualizar 1 de cada 4 frames).

## 4. Buenas prácticas
- **Sin estado global mutable**: Las funciones de IA y FSM deben operar sobre el estado de la entidad y un contexto de simulación explícito.
- **Evitar asignaciones masivas en el bucle caliente**: Reutilizar estructuras de cola de prioridad (min-heap) y conjuntos de nodos visitados en A* en lugar de crear cientos de objetos temporales por segundo.
- **Steering simple antes de A* masivo**: Si hay línea de visión directa sin obstáculos sólidos, usar un vector de dirección directo con evitación simple de obstáculos en lugar de invocar el algoritmo de grafos.

## 5. Referencias técnicas
- `architecture/CONTRACTS.md`: Contratos para `ai.astar` y `ai.behavior`.
- Algoritmo A* canónico con heurística Manhattan o Chebyshev sobre cuadrícula ortogonal.
- Patrones de comportamiento en *Game Programming Patterns* (Robert Nystrom) - State & Behavior Trees.
- Referencia de tests: `tests/test_enemies.py`, `tests/test_enemy_catalog.py`.

## 6. Procedimientos
### Paso 1: Definición de la FSM dirigida por datos
```python
def update_enemy_behavior(enemy: Enemy, player_pos: Vec2, dt: float, tilemap: TileMap) -> EnemyIntent:
    dist = (player_pos - enemy.position).length()
    if dist < enemy.archetype.detection_range:
        if has_line_of_sight(tilemap, enemy.position, player_pos):
            return EnemyIntent(action="chase", target=player_pos)
    return EnemyIntent(action="idle")
```
### Paso 2: Ejecución de búsqueda de ruta con cuota
```python
path = astar.find_path(tilemap, start_tile, goal_tile, budget_ms=1.5)
if path:
    enemy.set_waypoints(path)
```
### Paso 3: Retorno de intenciones puras
Las entidades de IA devuelven un `EnemyIntent` con la dirección deseada o acción de ataque, sin mutar directamente el mundo ni el render.

## 7. Criterios de aceptación
- Simulación fluida con hasta 50 entidades activas en el mapa sin degradar los 60 FPS objetivo (frame time de IA < 3 ms global).
- Comportamientos completamente configurables desde `game/data/enemies.json`.
- Cero rutas que atraviesen tiles sólidos o generen atascos en bucles infinitos.
- Comportamiento reproducible ante una semilla de RNG fija.

## 8. Pruebas recomendadas
- `tests/test_enemies.py`: Pruebas de detección, alcance de ataque y transiciones de estado de enemigos.
- `tests/test_enemy_catalog.py`: Verificación de carga y validación de tipos y parámetros de IA en JSON.
- Pruebas unitarias de `A*` con laberintos predefinidos asegurando la ruta óptima y respeto de límites de tiempo.
