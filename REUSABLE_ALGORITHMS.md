# GAMEFORGE 2D — CATÁLOGO DE ALGORITMOS REUTILIZABLES

**Documento:** `REUSABLE_ALGORITHMS.md`  
**Rol:** Arquitecto Principal de GameForge 2D  
**Fecha:** 2026-11-06  
**Estado:** ESPECIFICACIÓN ALGORÍTMICA OFICIAL  
**Origen:** Algoritmos extraídos, analizados y sintetizados a partir de la investigación de los 12 repositorios clave.

---

## 1. Índice de Algoritmos Optimizados

| ID | Algoritmo | Repositorio de Inspiración | Complejidad Temporal | Complejidad Espacial | Aplicación en GameForge 2D |
|---|---|---|:---:|:---:|---|
| **ALG-01** | **Validación Topológica BFS y Flood Fill** | Procedural generation / TCOD | $O(V + E)$ | $O(V)$ | Verificación determinista de mazmorras transitables |
| **ALG-02** | **A\* con Cuota de CPU y Caché LRU** | python-tcod / A* nativo | $O(K \log K)$ acotado | $O(K)$ | Navegación inteligente de enemigos sin tirones |
| **ALG-03** | **Partición Espacial por Spatial Hash** | Pymunk (BBTree / Hash) | $O(N)$ amortizado | $O(C + N)$ | Separación de entidades y culling visual $O(1)$ |
| **ALG-04** | **Resolución Anti-Tunneling Círculo vs. Tiles** | Custom engine / Pymunk | $O(S)$ por entidad | $O(1)$ | Colisión física y dashes a alta velocidad |
| **ALG-05** | **Máscara de Decaimiento Radial para Terrenos** | opensimplex-island-generator | $O(W \times H)$ | $O(W \times H)$ | Cavernas subterráneas orgánicas e islas |
| **ALG-06** | **Matriz de Biomas Whittaker (Cleanroom)** | Procedural-Maps | $O(W \times H)$ | $O(W \times H)$ | Clasificación de terrenos por elevación y humedad |
| **ALG-07** | **Mapas de Distancia Dijkstra (Swarm AI)** | python-tcod | $O(V + E)$ único | $O(W \times H)$ | Persecución de hordas de enemigos a coste $O(1)$ |
| **ALG-08** | **Elevación 2.5D, Sombras y $Y$-Sorting** | pygame-topdownengine | $O(N \log N)$ | $O(N)$ | Salto de obstáculos y profundidad visual |
| **ALG-09** | **FSM Dirigida por Datos y Generación de Intenciones** | py_trees / Esper / Catalog | $O(1)$ por entidad | $O(1)$ | Inteligencia desacoplada de la simulación |

---

## 2. Especificación Detallada de Algoritmos

---

### ALG-01: Validación Topológica BFS y Flood Fill
- **Problema que resuelve:** Los generadores procedurales de mazmorras pueden crear salas aisladas o cofres bloqueados por muros si los corredores se interrumpen.
- **Solución algorítmica:** Una búsqueda en anchura (Breadth-First Search) que parte desde el punto de spawn del jugador y explora únicamente celdas transitables (no sólidas). Tras recorrer el componente conexo, se verifica que el altar, la hoguera y el 100% de los cofres hayan sido visitados. Si falta alguno, el mapa se descarta y se regenera con una semilla derivada.

```python
from collections import deque
from typing import Set, Tuple, List

def validate_dungeon_connectivity(
    walkable_grid: List[List[bool]], 
    spawn: Tuple[int, int], 
    critical_points: List[Tuple[int, int]]
) -> bool:
    """Verifica en O(V + E) que todos los puntos críticos son alcanzables desde el spawn."""
    width = len(walkable_grid[0])
    height = len(walkable_grid)
    
    if not walkable_grid[spawn[1]][spawn[0]]:
        return False
        
    queue = deque([spawn])
    visited: Set[Tuple[int, int]] = {spawn}
    
    while queue:
        cx, cy = queue.popleft()
        for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < width and 0 <= ny < height:
                if walkable_grid[ny][nx] and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append((nx, ny))
                    
    return all(pt in visited for pt in critical_points)
```

- **Garantía contractual:** Ningún mapa injugable o con progreso bloqueado llega a la escena de juego.

---

### ALG-02: A\* con Cuota de CPU (Budgeting) y Caché LRU
- **Problema que resuelve:** Invocar el algoritmo A* tradicional para decenas de enemigos simultáneamente en Python puede consumir más de 15 ms por fotograma, provocando caídas de FPS.
- **Solución algorítmica:**
  1. **Cuota máxima de tiempo:** Se fija un límite estricto de reloj (`budget_ms <= 1.5 ms`). Si se alcanza la cuota, la función interrumpe la expansión y devuelve la mejor ruta parcial calculada hasta el nodo con menor heurística $h$.
  2. **Caché LRU parametrizada:** Dado que varios enemigos persiguen frecuentemente al mismo jugador en el mismo piso, el cálculo se memoriza bajo la clave `(floor_id, start_tile, goal_tile)`.

```python
import heapq
import time
from typing import Dict, List, Optional, Tuple

def find_path_budgeted(
    is_walkable_fn,
    start: Tuple[int, int],
    goal: Tuple[int, int],
    budget_ms: float = 1.5
) -> Optional[List[Tuple[int, int]]]:
    if start == goal:
        return [start]
        
    t_start = time.perf_counter()
    frontier: List[Tuple[float, float, int, int]] = []
    heapq.heappush(frontier, (0.0, 0.0, start[0], start[1]))
    
    came_from: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {start: None}
    cost_so_far: Dict[Tuple[int, int], float] = {start: 0.0}
    best_node = start
    best_h = abs(start[0] - goal[0]) + abs(start[1] - goal[1])
    
    while frontier:
        # Control estricto de presupuesto por fotograma
        if (time.perf_counter() - t_start) * 1000.0 >= budget_ms:
            break  # Devolver mejor ruta parcial disponible
            
        _, _, cx, cy = heapq.heappop(frontier)
        current = (cx, cy)
        
        if current == goal:
            best_node = current
            break
            
        for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            nx, ny = cx + dx, cy + dy
            neighbor = (nx, ny)
            if not is_walkable_fn(nx, ny):
                continue
                
            new_cost = cost_so_far[current] + 1.0
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                h = abs(nx - goal[0]) + abs(ny - goal[1])
                if h < best_h:
                    best_h = h
                    best_node = neighbor
                heapq.heappush(frontier, (new_cost + h, h, nx, ny))
                came_from[neighbor] = current
                
    # Reconstrucción de la ruta
    path = []
    curr: Optional[Tuple[int, int]] = best_node
    while curr is not None:
        path.append(curr)
        curr = came_from.get(curr)
    path.reverse()
    return path if len(path) > 1 else None
```

---

### ALG-03: Partición Espacial por Spatial Hash
- **Problema que resuelve:** Comprobar la colisión y separación entre $N$ enemigos requiere $O(N^2)$ comparaciones de distancia. Para 100 enemigos son 10.000 operaciones por frame.
- **Solución algorítmica:** Se divide el mundo en una cuadrícula virtual de tamaño de celda $S = 64$ píxeles. Cada entidad se registra en la celda correspondiente a su centro en $O(1)$. Para resolver separaciones, cada enemigo solo consulta su propia celda y las 8 celdas adyacentes.

$$\text{cell\_x} = \lfloor x / S \rfloor, \quad \text{cell\_y} = \lfloor y / S \rfloor$$

- **Complejidad:** $O(N)$ tiempo total de actualización y $O(1)$ vecinos por entidad en densidad controlada.
- **Implementación en el proyecto:** Módulo `game/world/spatial.py`.

---

### ALG-04: Resolución Anti-Tunneling Círculo vs. Tiles Sólidos
- **Problema que resuelve:** Cuando una entidad se desplaza a gran velocidad (por ejemplo, durante la esquiva rápida o *dash* a 400 px/s con $dt = 0.05$ s, $\Delta = 20$ px), el desplazamiento directo puede hacer que atraviese muros delgados de 16 o 32 píxeles (efecto túnel o *tunneling*).
- **Solución algorítmica:** Subdivisión adaptativa de pasos. Si la longitud del vector de desplazamiento $|\Delta| > \text{max\_step}$ (fijado en 4.0 píxeles), el vector se fragmenta en $S = \lceil |\Delta| / \text{max\_step} \rceil$ micro-pasos. En cada micro-paso, el movimiento se resuelve primero en el eje X y luego en el eje Y de forma desacoplada, deslizando suavemente la entidad por las paredes.

```python
def move_circle_anti_tunneling(
    tilemap, 
    start: Vec2, 
    radius: float, 
    delta: Vec2, 
    max_step: float = 4.0
) -> Vec2:
    dist = delta.length()
    if dist == 0.0:
        return start
        
    steps = max(1, int(dist / max_step) + 1)
    step_delta = delta / steps
    current = start
    
    for _ in range(steps):
        # Resolver eje X
        next_x = Vec2(current.x + step_delta.x, current.y)
        if not tilemap.intersects_circle(next_x, radius):
            current = next_x
            
        # Resolver eje Y
        next_y = Vec2(current.x, current.y + step_delta.y)
        if not tilemap.intersects_circle(next_y, radius):
            current = next_y
            
    return current
```

---

### ALG-05: Máscara de Decaimiento Radial para Terrenos Orgánicos
- **Problema que resuelve:** Generar cavernas subterráneas o islas flotantes utilizando funciones de ruido continuo que garanticen matemáticamente que los bordes del mapa son muros sólidos infranqueables sin generar cortes rectilíneos artificiales.
- **Inspiración:** `opensimplex-island-generator`.
- **Fórmula de la Máscara:** Para un mapa de ancho $W$ y alto $H$ con centro en $(c_x, c_y)$:

$$n_x = \frac{2x - W}{W}, \quad n_y = \frac{2y - H}{H}$$
$$d = \sqrt{n_x^2 + n_y^2}$$
$$\text{Falloff}(d) = \max\left(0.0, 1.0 - d^2\right)$$
$$\text{ValorFinal}(x, y) = \text{Ruido}(x, y) \times \text{Falloff}(d)$$

- Si $\text{ValorFinal}(x, y) < \text{Umbral}$, el tile se marca como `WALL`; si es mayor o igual, se marca como `FLOOR`.
- **Resultado:** Cavernas con bordes orgánicos circulares o elípticos perfectamente cerradas en los extremos del mapa.

---

### ALG-06: Matriz de Biomas Whittaker (Implementación Cleanroom)
- **Problema que resuelve:** Generar variedad ambiental en exteriores o mazmorras profundas sin incurrir en violaciones de copyright del repositorio sin licencia `Procedural-Maps`.
- **Solución algorítmica:** Creación de dos mapas de ruido ortogonales e independientes (elevación $E \in [0, 1]$ y humedad $M \in [0, 1]$) y clasificación mediante una tabla de decisión discreta:

| Elevación ($E$) | Humedad Baja ($M < 0.35$) | Humedad Media ($0.35 \le M < 0.70$) | Humedad Alta ($M \ge 0.70$) |
|---|---|---|---|
| **Alta ($E \ge 0.75$)** | Pico Rocoso | Alta Montaña / Templo | Picos Glaciares / Nieve |
| **Media ($0.30 \le E < 0.75$)**| Páramo Árido | Bosque Templado / Pradera | Pantano / Bosque Húmedo |
| **Baja ($E < 0.30$)** | Grieta de Lava | Río / Laguna Subterránea | Foso Abisal / Agua Profunda |

- **Ventaja legal:** Código 100% original, determinista y parametrizable en JSON.

---

### ALG-07: Mapas de Distancia Dijkstra para Comportamiento de Enjambre (Swarm AI)
- **Problema que resuelve:** En escenarios con 50 o 100 enemigos persiguiendo al jugador a la vez, ejecutar 100 búsquedas A* individuales por frame colapsa la CPU.
- **Inspiración:** `python-tcod`.
- **Solución algorítmica:** Cálculo de un mapa de calor o campo de distancias (Distance Field) con una única pasada BFS partiendo de la posición del jugador hacia todo el mapa transitable. Cada enemigo consulta simplemente a cuál de sus celdas vecinas corresponde el menor valor de distancia:
  - Coste de cálculo global: $O(V + E)$ una sola vez por frame (o cada varios frames si el jugador no se ha movido más de un tile).
  - Coste por enemigo: $O(1)$ (comprobación de 4 o 8 vecinos inmediatos).
  - Permite guiar a **más de 1.000 enemigos** simultáneos sin pérdida de rendimiento.

---

### ALG-08: Elevación 2.5D, Sombras Elípticas y $Y$-Sorting
- **Problema que resuelve:** Resolver la profundidad visual y la superposición de sprites en perspectiva top-down, y permitir saltar sobre obstáculos o trampas en el suelo.
- **Inspiración:** `pygame-topdownengine`.
- **Mecánica Z-Axis:**
  - La entidad mantiene posición física $(x, y)$ y altura vertical $z \ge 0$.
  - Si salta, $v_z = v_{\text{salto}}$ y en cada tick $z = \max(0.0, z + v_z dt - \frac{1}{2} g dt^2)$.
  - Mientras $z > 0$, la entidad no colisiona con trampas a ras de suelo (`hazard_damage`).
- **Renderizado Desacoplado:**
  - Sombra: Se dibuja en $(x, y)$ con radio menor y mayor transparencia cuanto mayor sea $z$.
  - Sprite: Se dibuja con offset visual en $(x, y - z)$.
- **$Y$-Sorting:** Antes de dibujar, se ordenan las entidades visibles en cámara por su base inferior:
  $$\text{sort\_key} = y + \text{height}$$
  Garantiza que las entidades más adelantadas tapen correctamente a las que se encuentran detrás.

---

### ALG-09: FSM Dirigida por Datos y Generación Pura de Intenciones
- **Problema que resuelve:** La arquitectura tradicional acopla la IA a la mutación inmediata del mundo, dificultando el testing y generando condiciones de carrera o inconsistencias en los fotogramas.
- **Solución algorítmica:** La entidad nunca muta el mundo ni crea proyectiles directamente. Su método `update()` evalúa su estado interno (FSM: `IDLE`, `CHASE`, `ATTACK`, `WANDER`, `FLEE`) y devuelve un objeto inmutable `EnemyIntent`:

```python
@dataclass(frozen=True)
class EnemyIntent:
    entity_id: str
    move_vector: Vec2
    dash_requested: bool = False
    attack_action: Optional[str] = None
    target_position: Optional[Vec2] = None
```

- La capa de simulación pura (`game/sim/combat.py`) recibe todas las intenciones de forma atómica y las procesa en orden secuencial determinista, facilitando las pruebas unitarias puras y la reproducción de partidas guardadas.
