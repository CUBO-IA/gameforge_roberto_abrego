"""Fondos procedurales compartidos."""

from __future__ import annotations

import math

import pygame

from game.core.math2d import lerp


def vertical_gradient(
    size: tuple[int, int],
    top: tuple[int, int, int],
    bottom: tuple[int, int, int],
) -> pygame.Surface:
    width, height = size
    strip = pygame.Surface((1, max(2, height)))
    for y in range(strip.get_height()):
        t = y / (strip.get_height() - 1)
        strip.set_at(
            (0, y),
            (
                int(lerp(top[0], bottom[0], t)),
                int(lerp(top[1], bottom[1], t)),
                int(lerp(top[2], bottom[2], t)),
            ),
        )
    return pygame.transform.scale(strip, size)


def forge_glow(
    size: tuple[int, int], center: tuple[int, int], radius: int, color: tuple[int, int, int]
) -> pygame.Surface:
    surface = pygame.Surface(size, pygame.SRCALPHA)
    steps = 18
    for index in range(steps, 0, -1):
        fraction = index / steps
        alpha = int(70 * (1.0 - fraction) ** 2)
        pygame.draw.circle(
            surface,
            (color[0], color[1], color[2], alpha),
            center,
            int(radius * fraction),
        )
    return surface


def draw_anvil(surface: pygame.Surface, x: int, y: int, scale: float = 1.0) -> None:
    color = (42, 36, 48)
    highlight = (72, 60, 78)
    width = int(150 * scale)
    top = pygame.Rect(0, 0, width, int(20 * scale))
    top.midtop = (x, y)
    pygame.draw.rect(surface, color, top)
    pygame.draw.rect(surface, highlight, pygame.Rect(top.x, top.y, top.width, 4))
    horn = [
        (top.right, top.y),
        (top.right + int(32 * scale), top.y + int(10 * scale)),
        (top.right, top.y + int(18 * scale)),
    ]
    pygame.draw.polygon(surface, color, horn)
    waist = pygame.Rect(0, 0, int(46 * scale), int(26 * scale))
    waist.midtop = (x, top.bottom)
    pygame.draw.rect(surface, color, waist)
    base = pygame.Rect(0, 0, int(90 * scale), int(16 * scale))
    base.midtop = (x, waist.bottom)
    pygame.draw.rect(surface, color, base)
    pygame.draw.rect(surface, highlight, pygame.Rect(base.x, base.y, base.width, 3))


def draw_title_forge(
    surface: pygame.Surface, center: tuple[int, int], time: float
) -> None:
    pulse = 1.0 + 0.05 * math.sin(time * 2.2)
    glow = forge_glow(surface.get_size(), center, int(260 * pulse), (255, 120, 48))
    surface.blit(glow, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
