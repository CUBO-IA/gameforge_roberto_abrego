"""Mapa de distancias Dijkstra para movimiento de hordas (Swarm AI).

Algoritmo ALG-07 inspirado en python-tcod: implementación clean-room de campo de
distancias BFS sobre la cuadrícula ortogonal de TileMap. Permite calcular la
dirección óptima de cada enemigo en O(1) tras un preprocesamiento O(W×H).

Sin dependencias de Pygame. Totalmente desacoplado de renderizado.
"""

from __future__ import annotations

import math
from collections import deque

from game.core.math2d import Vec2
from game.world.tilemap import TileMap

# Vecinos ortogonales (derecha, abajo, izquierda, arriba)
_NEIGHBORS: tuple[tuple[int, int], ...] = ((1, 0), (0, 1), (-1, 0), (0, -1))

# Valor centinela que indica celda inalcanzable
UNREACHABLE: int = 0x7FFF_FFFF


class DijkstraMap:
    """Campo de distancias BFS desde una o varias fuentes en un TileMap.

    Uso típico:
        dmap = DijkstraMap(tilemap)
        dmap.compute(player_tile_col, player_tile_row)
        direction = dmap.best_neighbor(enemy_col, enemy_row)
    """

    __slots__ = ("_tilemap", "_width", "_height", "_dist")

    def __init__(self, tilemap: TileMap) -> None:
        self._tilemap = tilemap
        self._width = tilemap.width
        self._height = tilemap.height
        # Inicializar con UNREACHABLE
        self._dist: list[list[int]] = [
            [UNREACHABLE] * self._width for _ in range(self._height)
        ]

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    def distance_at(self, col: int, row: int) -> int:
        """Devuelve la distancia Manhattan mínima desde (col, row) a la fuente más cercana."""
        if 0 <= col < self._width and 0 <= row < self._height:
            return self._dist[row][col]
        return UNREACHABLE

    def compute(self, source_col: int, source_row: int) -> None:
        """Recalcula el campo de distancias BFS desde una única fuente.

        Solo propaga por tiles no sólidos. Complejidad O(W×H).
        """
        self.compute_multi([(source_col, source_row)])

    def compute_multi(self, sources: list[tuple[int, int]]) -> None:
        """Recalcula el campo de distancias BFS desde múltiples fuentes simultáneas.

        Útil para que enemigos converjan hacia cualquiera de varios objetivos.
        """
        w, h = self._width, self._height
        tilemap = self._tilemap
        dist = self._dist

        # Resetear
        for row in range(h):
            for col in range(w):
                dist[row][col] = UNREACHABLE

        queue: deque[tuple[int, int]] = deque()

        for sc, sr in sources:
            if 0 <= sc < w and 0 <= sr < h and not tilemap.is_solid_tile(sc, sr):
                dist[sr][sc] = 0
                queue.append((sc, sr))

        while queue:
            cx, cy = queue.popleft()
            next_d = dist[cy][cx] + 1
            for dx, dy in _NEIGHBORS:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < w and 0 <= ny < h:
                    if dist[ny][nx] > next_d and not tilemap.is_solid_tile(nx, ny):
                        dist[ny][nx] = next_d
                        queue.append((nx, ny))

    def best_neighbor(self, col: int, row: int) -> tuple[int, int] | None:
        """Devuelve el vecino ortogonal con menor distancia a la fuente.

        Retorna (delta_col, delta_row) o None si no hay vecino válido
        (la celda actual es UNREACHABLE o está rodeada de muros).
        Coste O(1) por consulta.
        """
        if not (0 <= col < self._width and 0 <= row < self._height):
            return None
        if self._dist[row][col] == UNREACHABLE:
            return None

        best_d = self._dist[row][col]
        best_dir: tuple[int, int] | None = None

        for dx, dy in _NEIGHBORS:
            nx, ny = col + dx, row + dy
            if 0 <= nx < self._width and 0 <= ny < self._height:
                d = self._dist[ny][nx]
                if d < best_d:
                    best_d = d
                    best_dir = (dx, dy)

        return best_dir

    def direction_toward_source(
        self, world_x: float, world_y: float
    ) -> Vec2 | None:
        """Devuelve un vector unitario de dirección desde (world_x, world_y) hacia la fuente.

        Conveniencia para integrar con el sistema de movimiento de entidades.
        Retorna None si la posición es inalcanzable.
        """
        ts = self._tilemap.tile_size
        col = math.floor(world_x / ts)
        row = math.floor(world_y / ts)
        neighbor = self.best_neighbor(col, row)
        if neighbor is None:
            return None
        dx, dy = neighbor
        length = math.sqrt(dx * dx + dy * dy)
        if length == 0:
            return None
        return Vec2(dx / length, dy / length)
