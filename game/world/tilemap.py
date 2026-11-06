"""Representación de un mapa de tiles.

Solo contiene datos y consultas. El renderizado vive en ``game.render``.
"""

from __future__ import annotations

import math
from collections.abc import Iterator

from game.core.math2d import Vec2
from game.world.tiles import TILE_DEFS, TileType


class TileMap:
    def __init__(
        self,
        width: int,
        height: int,
        tile_size: int,
        tiles: list[list[TileType | int]],
    ) -> None:
        if width <= 0 or height <= 0:
            raise ValueError("El mapa debe tener dimensiones positivas.")
        if tile_size <= 0:
            raise ValueError("El tamaño de tile debe ser positivo.")
        if len(tiles) != height or any(len(row) != width for row in tiles):
            raise ValueError("La matriz de tiles no coincide con width/height.")
        self.width = width
        self.height = height
        self.tile_size = tile_size
        self._tiles: list[list[TileType]] = [
            [tile if isinstance(tile, TileType) else TileType(tile) for tile in row]
            for row in tiles
        ]

    @classmethod
    def filled(cls, width: int, height: int, tile_size: int, tile: TileType) -> "TileMap":
        return cls(width, height, tile_size, [[tile for _ in range(width)] for _ in range(height)])

    @property
    def pixel_width(self) -> int:
        return self.width * self.tile_size

    @property
    def pixel_height(self) -> int:
        return self.height * self.tile_size

    def in_bounds(self, col: int, row: int) -> bool:
        return 0 <= col < self.width and 0 <= row < self.height

    def tile_at(self, col: int, row: int) -> TileType:
        if not self.in_bounds(col, row):
            return TileType.WALL
        return self._tiles[row][col]

    def tile_at_pixel(self, x: float, y: float) -> TileType:
        col = math.floor(x / self.tile_size)
        row = math.floor(y / self.tile_size)
        return self.tile_at(col, row)

    def set_tile(self, col: int, row: int, tile: TileType) -> None:
        if not self.in_bounds(col, row):
            raise IndexError(f"Tile fuera del mapa: ({col}, {row})")
        self._tiles[row][col] = tile

    def is_solid_tile(self, col: int, row: int) -> bool:
        return TILE_DEFS[self.tile_at(col, row)].solid

    def is_solid_at(self, x: float, y: float) -> bool:
        return TILE_DEFS[self.tile_at_pixel(x, y)].solid

    def speed_multiplier_at(self, x: float, y: float) -> float:
        return TILE_DEFS[self.tile_at_pixel(x, y)].speed_multiplier

    def hazard_damage_at(self, x: float, y: float) -> float:
        return TILE_DEFS[self.tile_at_pixel(x, y)].damage_per_second

    def iter_tiles(self) -> Iterator[tuple[int, int, TileType]]:
        for row, values in enumerate(self._tiles):
            for col, tile in enumerate(values):
                yield col, row, tile

    def tile_center(self, col: int, row: int) -> Vec2:
        half = self.tile_size / 2
        return Vec2(col * self.tile_size + half, row * self.tile_size + half)
