"""Búsqueda de caminos A* sobre la cuadrícula ortogonal de TileMap.

Garantías:
- Respeta una cuota máxima de tiempo de CPU por consulta (budget_ms).
- Devuelve la mejor ruta parcial alcanzada si se agota el presupuesto.
- Utiliza una caché LRU acotada para consultas frecuentes.
- Totalmente desacoplado de Pygame o efectos visuales.
"""

from __future__ import annotations

import heapq
import math
import time
from collections import OrderedDict

from game.core.math2d import Vec2
from game.world.tilemap import TileMap

# Vecinos ortogonales (derecha, abajo, izquierda, arriba)
_ORTHOGONAL_NEIGHBORS: tuple[tuple[int, int], ...] = (
    (1, 0),
    (0, 1),
    (-1, 0),
    (0, -1),
)

_CACHE_MAX_SIZE = 128
_PATH_CACHE: OrderedDict[tuple[int, int, int, int, int], list[Vec2] | None] = OrderedDict()


def clear_path_cache() -> None:
    """Limpia la caché de rutas (útil al cambiar de planta o mapa)."""
    _PATH_CACHE.clear()


def find_path(
    tilemap: TileMap,
    start: Vec2,
    goal: Vec2,
    budget_ms: float = 1.5,
) -> list[Vec2] | None:
    """Encuentra una ruta de start a goal sorteando tiles sólidos.

    Retorna una lista de puntos en el mundo (Vec2) o None si no hay ruta accesible.
    """
    ts = tilemap.tile_size
    start_c = math.floor(start.x / ts)
    start_r = math.floor(start.y / ts)
    goal_c = math.floor(goal.x / ts)
    goal_r = math.floor(goal.y / ts)

    if not tilemap.in_bounds(start_c, start_r):
        return None
    if not tilemap.in_bounds(goal_c, goal_r):
        return None

    # Si el objetivo es un muro sólido, no es navegable directamente.
    if tilemap.is_solid_tile(goal_c, goal_r):
        return None

    # Si start y goal están en el mismo tile, ruta directa.
    if start_c == goal_c and start_r == goal_r:
        return [goal]

    # Comprobar caché LRU
    cache_key = (id(tilemap), start_c, start_r, goal_c, goal_r)
    if cache_key in _PATH_CACHE:
        cached = _PATH_CACHE[cache_key]
        _PATH_CACHE.move_to_end(cache_key)
        if cached is None:
            return None
        # Devolver una copia para prevenir mutaciones externas
        return list(cached)

    deadline = time.perf_counter() + (budget_ms / 1000.0)

    # Heurística Manhattan
    def h(c: int, r: int) -> float:
        return float(abs(c - goal_c) + abs(r - goal_r))

    counter = 0
    start_h = h(start_c, start_r)
    # Priority Queue: (f_score, h_score, tie_breaker, col, row)
    open_set: list[tuple[float, float, int, int, int]] = [(start_h, start_h, counter, start_c, start_r)]
    came_from: dict[tuple[int, int], tuple[int, int]] = {}
    g_score: dict[tuple[int, int], float] = {(start_c, start_r): 0.0}

    best_node = (start_c, start_r)
    best_h = start_h
    reached_goal = False

    while open_set:
        # Control del presupuesto de tiempo cada 32 nodos explorados
        if counter % 32 == 0 and time.perf_counter() >= deadline:
            break

        _, current_h, _, curr_c, curr_r = heapq.heappop(open_set)

        if curr_c == goal_c and curr_r == goal_r:
            reached_goal = True
            best_node = (curr_c, curr_r)
            break

        if current_h < best_h:
            best_h = current_h
            best_node = (curr_c, curr_r)

        current_g = g_score[(curr_c, curr_r)]

        for dc, dr in _ORTHOGONAL_NEIGHBORS:
            next_c = curr_c + dc
            next_r = curr_r + dr

            if not tilemap.in_bounds(next_c, next_r):
                continue
            if tilemap.is_solid_tile(next_c, next_r):
                continue

            tentative_g = current_g + 1.0
            neighbor = (next_c, next_r)

            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                g_score[neighbor] = tentative_g
                counter += 1
                neighbor_h = h(next_c, next_r)
                f_score = tentative_g + neighbor_h
                heapq.heappush(open_set, (f_score, neighbor_h, counter, next_c, next_r))
                came_from[neighbor] = (curr_c, curr_r)

    # Si no se alcanzó la celda objetivo, no existe ruta completa
    if not reached_goal:
        _cache_result(cache_key, None)
        return None

    path_cells: list[tuple[int, int]] = []
    curr = best_node
    while curr in came_from:
        path_cells.append(curr)
        curr = came_from[curr]
    path_cells.reverse()

    if not path_cells:
        _cache_result(cache_key, None)
        return None

    # Convertir celdas de cuadrícula a coordenadas Vec2 en el centro de cada tile
    path: list[Vec2] = [tilemap.tile_center(c, r) for c, r in path_cells]
    # Si alcanzamos la celda objetivo, el último punto apunta con precisión al objetivo exacto
    if reached_goal:
        path[-1] = goal

    _cache_result(cache_key, path)
    return list(path)


def _cache_result(key: tuple[int, int, int, int, int], result: list[Vec2] | None) -> None:
    if len(_PATH_CACHE) >= _CACHE_MAX_SIZE:
        _PATH_CACHE.popitem(last=False)
    _PATH_CACHE[key] = list(result) if result is not None else None
