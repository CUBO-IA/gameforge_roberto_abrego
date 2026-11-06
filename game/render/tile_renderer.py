"""Pre-renderizado del mapa estático y adornos animados."""

from __future__ import annotations

import math

import pygame

from game.core.math2d import Vec2
from game.render import palette
from game.world.camera import Camera
from game.world.tilemap import TileMap
from game.world.tiles import TILE_DEFS, TileType


def _hash(col: int, row: int) -> int:
    value = (col * 73856093) ^ (row * 19349663) ^ 0x9E3779B9
    return value & 0xFFFFFFFF


class TileRenderer:
    def __init__(self, tilemap: TileMap) -> None:
        self.tilemap = tilemap
        self.surface = self._build(tilemap)
        self.water_tiles = [
            tilemap.tile_center(col, row)
            for col, row, tile in tilemap.iter_tiles()
            if tile == TileType.WATER
        ]
        self.lava_tiles = [
            tilemap.tile_center(col, row)
            for col, row, tile in tilemap.iter_tiles()
            if tile == TileType.LAVA
        ]

    def _build(self, tilemap: TileMap) -> pygame.Surface:
        size = tilemap.tile_size
        surface = pygame.Surface((tilemap.pixel_width, tilemap.pixel_height))
        surface.fill(palette.BACKGROUND_DEEP)
        for col, row, tile in tilemap.iter_tiles():
            rect = pygame.Rect(col * size, row * size, size, size)
            if tile == TileType.WALL:
                self._draw_wall(surface, tilemap, rect, col, row)
            elif tile == TileType.WATER:
                self._draw_water(surface, rect, col, row)
            elif tile == TileType.LAVA:
                self._draw_lava(surface, rect, col, row)
            else:
                self._draw_floor(surface, rect, col, row)
        return surface

    def _draw_floor(
        self, surface: pygame.Surface, rect: pygame.Rect, col: int, row: int
    ) -> None:
        value = _hash(col, row)
        base = palette.FLOOR if value % 3 else palette.FLOOR_ALT
        pygame.draw.rect(surface, base, rect)
        pygame.draw.line(surface, (29, 30, 44), rect.bottomleft, rect.bottomright)
        pygame.draw.line(surface, (29, 30, 44), rect.topright, rect.bottomright)
        if value % 11 == 0:
            offset_x = (value >> 8) % (rect.width - 8) + 4
            offset_y = (value >> 16) % (rect.height - 8) + 4
            pygame.draw.line(
                surface,
                (26, 27, 40),
                (rect.x + offset_x, rect.y + offset_y),
                (rect.x + offset_x + 6, rect.y + offset_y + 4),
                1,
            )
        if value % 17 == 0:
            pygame.draw.circle(
                surface,
                (58, 56, 76),
                (rect.x + value % rect.width, rect.y + (value >> 8) % rect.height),
                1,
            )

    def _draw_wall(
        self,
        surface: pygame.Surface,
        tilemap: TileMap,
        rect: pygame.Rect,
        col: int,
        row: int,
    ) -> None:
        open_below = not TILE_DEFS[tilemap.tile_at(col, row + 1)].solid
        open_above = not TILE_DEFS[tilemap.tile_at(col, row - 1)].solid
        value = _hash(col, row)
        pygame.draw.rect(surface, palette.WALL_FACE, rect)
        if open_below:
            top = rect.inflate(0, -rect.height // 3)
            top.y = rect.y
            pygame.draw.rect(surface, palette.WALL_TOP, top)
            pygame.draw.line(
                surface,
                palette.WALL_EDGE,
                (rect.left, top.bottom),
                (rect.right, top.bottom),
                2,
            )
            pygame.draw.line(
                surface, (115, 102, 142), rect.topleft, rect.topright, 1
            )
        elif open_above:
            pygame.draw.rect(
                surface,
                (44, 40, 62),
                pygame.Rect(rect.x, rect.y + rect.height // 2, rect.width, rect.height // 2),
            )
        if value % 5 == 0:
            x = rect.x + 5 + (value >> 7) % (rect.width - 10)
            y = rect.y + 6 + (value >> 13) % (rect.height - 12)
            pygame.draw.line(
                surface,
                (47, 43, 65),
                (x, y),
                (x + (value % 5) - 2, y + 8),
                1,
            )

    def _draw_water(
        self, surface: pygame.Surface, rect: pygame.Rect, col: int, row: int
    ) -> None:
        pygame.draw.rect(surface, palette.WATER, rect)
        value = _hash(col, row)
        for index in range(2):
            y = rect.y + 8 + index * 12 + (value >> (index * 5)) % 6
            pygame.draw.line(
                surface,
                palette.WATER_LIGHT,
                (rect.x + 6, y),
                (rect.x + rect.width - 8, y),
                2,
            )

    def _draw_lava(
        self, surface: pygame.Surface, rect: pygame.Rect, col: int, row: int
    ) -> None:
        pygame.draw.rect(surface, palette.LAVA, rect)
        value = _hash(col, row)
        pygame.draw.circle(
            surface,
            palette.LAVA_LIGHT,
            (rect.centerx, rect.centery),
            5 + value % 4,
        )
        pygame.draw.circle(
            surface,
            (255, 196, 90),
            (rect.centerx + 3, rect.centery - 2),
            2,
        )

    def draw_animated(
        self,
        target: pygame.Surface,
        camera: Camera,
        time: float,
        shake: Vec2,
    ) -> None:
        for tile in self.water_tiles:
            screen = camera.world_to_screen(tile, shake)
            if not (-20 <= screen.x <= camera.viewport_width + 20):
                continue
            if not (-20 <= screen.y <= camera.viewport_height + 20):
                continue
            phase = time * 1.7 + (tile.x + tile.y) * 0.011
            pygame.draw.arc(
                target,
                palette.WATER_LIGHT,
                pygame.Rect(int(screen.x) - 11, int(screen.y) - 4, 22, 10),
                phase % math.tau,
                (phase + 1.2) % math.tau,
                1,
            )
        for tile in self.lava_tiles:
            screen = camera.world_to_screen(tile, shake)
            if not (-20 <= screen.x <= camera.viewport_width + 20):
                continue
            if not (-20 <= screen.y <= camera.viewport_height + 20):
                continue
            pulse = 1.0 + 0.35 * math.sin(time * 3.0 + tile.x * 0.02)
            pygame.draw.circle(
                target,
                (255, 150, 60),
                (int(screen.x), int(screen.y)),
                int(3 * pulse),
            )
