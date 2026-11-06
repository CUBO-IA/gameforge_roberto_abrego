"""Iluminación 2D por máscara de oscuridad y luces radiales."""

from __future__ import annotations

import pygame

from game.core.math2d import Vec2
from game.world.camera import Camera


class Lighting:
    def __init__(self, size: tuple[int, int], ambient_alpha: int = 138) -> None:
        self.size = size
        self.ambient_alpha = ambient_alpha
        self._dark = pygame.Surface(size, pygame.SRCALPHA)
        self._mask = pygame.Surface(size, pygame.SRCALPHA)
        self._cache: dict[int, pygame.Surface] = {}
        self.vignette = self._build_vignette(size)

    def _radial(self, radius: int) -> pygame.Surface:
        radius = max(16, min(900, int(radius)))
        cached = self._cache.get(radius)
        if cached is not None:
            return cached
        surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        steps = 22
        for step in range(steps, 0, -1):
            fraction = step / steps
            alpha = int(255 * (1.0 - fraction) ** 1.6)
            pygame.draw.circle(
                surface,
                (0, 0, 0, alpha),
                (radius, radius),
                max(1, int(radius * fraction)),
            )
        self._cache[radius] = surface
        return surface

    def render(
        self,
        target: pygame.Surface,
        lights: list[tuple[Vec2, int, float]],
        camera: Camera,
        shake: Vec2,
    ) -> None:
        self._dark.fill((5, 6, 14, self.ambient_alpha))
        self._mask.fill((0, 0, 0, 0))
        for world_position, radius, strength in lights:
            screen = camera.world_to_screen(world_position, shake)
            radial = self._radial(int(radius))
            rect = radial.get_rect(center=(int(screen.x), int(screen.y)))
            if strength >= 0.99:
                self._mask.blit(radial, rect, special_flags=pygame.BLEND_RGBA_MAX)
            else:
                scaled = radial.copy()
                scaled.set_alpha(int(255 * max(0.0, min(1.0, strength))))
                self._mask.blit(scaled, rect, special_flags=pygame.BLEND_RGBA_MAX)
        self._dark.blit(self._mask, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
        target.blit(self._dark, (0, 0))
        target.blit(self.vignette, (0, 0))

    @staticmethod
    def _build_vignette(size: tuple[int, int]) -> pygame.Surface:
        tiny = pygame.Surface((64, 40), pygame.SRCALPHA)
        cx, cy = 31.5, 19.5
        maximum = (cx * cx + cy * cy) ** 0.5
        for y in range(40):
            for x in range(64):
                distance = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5 / maximum
                alpha = int(max(0.0, distance - 0.55) ** 1.4 * 230)
                tiny.set_at((x, y), (0, 0, 0, min(200, alpha)))
        return pygame.transform.smoothscale(tiny, size)
