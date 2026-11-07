"""Partición espacial basada en Spatial Hashing.

Permite consultas de proximidad y colisión en O(1) amortizado, evitando
el coste O(n²) en separación de entidades, ataques y culling de renderizado.
Sin dependencias de Pygame ni estado global mutable.
"""

from __future__ import annotations

import math
from collections import defaultdict
from collections.abc import Iterable
from typing import Generic, TypeVar

from game.core.math2d import Vec2

T = TypeVar("T")


class SpatialHash(Generic[T]):
    """Estructura de partición espacial bidimensional uniforme."""

    def __init__(self, cell_size: float = 64.0) -> None:
        if cell_size <= 0:
            raise ValueError("El tamaño de celda debe ser positivo.")
        self.cell_size = float(cell_size)
        self._buckets: dict[tuple[int, int], list[T]] = defaultdict(list)
        self._items: dict[int, tuple[T, Vec2, float]] = {}

    def clear(self) -> None:
        """Limpia todos los buckets y elementos registrados."""
        self._buckets.clear()
        self._items.clear()

    def _cell_coords(self, x: float, y: float) -> tuple[int, int]:
        return math.floor(x / self.cell_size), math.floor(y / self.cell_size)

    def insert(self, item: T, position: Vec2, radius: float = 0.0) -> None:
        """Inserta un elemento en los buckets espaciales que solapa."""
        r = max(0.0, radius)
        self._items[id(item)] = (item, position, r)

        min_col, min_row = self._cell_coords(position.x - r, position.y - r)
        max_col, max_row = self._cell_coords(position.x + r, position.y + r)

        for col in range(min_col, max_col + 1):
            for row in range(min_row, max_row + 1):
                self._buckets[(col, row)].append(item)

    def insert_all(self, items: Iterable[tuple[T, Vec2, float]]) -> None:
        """Inserta múltiples elementos a la vez."""
        for item, pos, radius in items:
            self.insert(item, pos, radius)

    def query_radius(self, center: Vec2, radius: float) -> list[T]:
        """Devuelve los elementos cuyos radios solapen con el círculo (center, radius)."""
        r = max(0.0, radius)
        min_col, min_row = self._cell_coords(center.x - r, center.y - r)
        max_col, max_row = self._cell_coords(center.x + r, center.y + r)

        candidates: set[int] = set()
        result: list[T] = []

        for col in range(min_col, max_col + 1):
            for row in range(min_row, max_row + 1):
                bucket = self._buckets.get((col, row))
                if bucket:
                    for item in bucket:
                        item_id = id(item)
                        if item_id in candidates:
                            continue
                        candidates.add(item_id)
                        _, pos, item_r = self._items[item_id]
                        max_dist = r + item_r
                        if (pos - center).length_squared() <= max_dist * max_dist:
                            result.append(item)
        return result

    def query_rect(self, x: float, y: float, width: float, height: float) -> list[T]:
        """Devuelve los elementos que intersectan con el rectángulo AABB."""
        min_col, min_row = self._cell_coords(x, y)
        max_col, max_row = self._cell_coords(x + width, y + height)

        candidates: set[int] = set()
        result: list[T] = []

        for col in range(min_col, max_col + 1):
            for row in range(min_row, max_row + 1):
                bucket = self._buckets.get((col, row))
                if bucket:
                    for item in bucket:
                        item_id = id(item)
                        if item_id in candidates:
                            continue
                        candidates.add(item_id)
                        _, pos, item_r = self._items[item_id]
                        # Comprobar si el círculo del elemento solapa el AABB
                        closest_x = max(x, min(pos.x, x + width))
                        closest_y = max(y, min(pos.y, y + height))
                        dx = pos.x - closest_x
                        dy = pos.y - closest_y
                        if dx * dx + dy * dy <= item_r * item_r:
                            result.append(item)
        return result

    def query_pairs(self) -> list[tuple[T, T]]:
        """Devuelve pares únicos de elementos que comparten al menos un bucket."""
        pairs: set[tuple[int, int]] = set()
        result: list[tuple[T, T]] = []

        for bucket in self._buckets.values():
            n = len(bucket)
            if n < 2:
                continue
            for i in range(n):
                first = bucket[i]
                id_first = id(first)
                for j in range(i + 1, n):
                    second = bucket[j]
                    id_second = id(second)
                    pair_key = (min(id_first, id_second), max(id_first, id_second))
                    if pair_key not in pairs:
                        pairs.add(pair_key)
                        result.append((first, second))
        return result
