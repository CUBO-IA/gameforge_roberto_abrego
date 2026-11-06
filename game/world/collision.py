"""Colisión círculo-tile y resolución por ejes.

El juego es top-down sin rotaciones físicas: un resolvedor por ejes con
subdivisión del desplazamiento es suficiente, determinista y barato. Se evita
Pymunk porque no aporta valor frente a colisiones tile-based (ver ADR-002).
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from game.core.math2d import Vec2, clamp
from game.world.tilemap import TileMap


@dataclass(frozen=True, slots=True)
class CollisionResult:
    position: Vec2
    hit_x: bool = False
    hit_y: bool = False


def circle_hits_solid(tilemap: TileMap, position: Vec2, radius: float) -> bool:
    if radius <= 0:
        return tilemap.is_solid_at(position.x, position.y)
    size = tilemap.tile_size
    left = math.floor((position.x - radius) / size)
    right = math.floor((position.x + radius) / size)
    top = math.floor((position.y - radius) / size)
    bottom = math.floor((position.y + radius) / size)
    limit = radius * radius - 1e-9
    for row in range(top, bottom + 1):
        for col in range(left, right + 1):
            if not tilemap.is_solid_tile(col, row):
                continue
            nearest_x = clamp(position.x, col * size, (col + 1) * size)
            nearest_y = clamp(position.y, row * size, (row + 1) * size)
            dx = position.x - nearest_x
            dy = position.y - nearest_y
            if dx * dx + dy * dy < limit:
                return True
    return False


def move_circle(
    tilemap: TileMap,
    start: Vec2,
    radius: float,
    delta: Vec2,
    max_step: float = 4.0,
) -> CollisionResult:
    """Mueve un círculo resolviendo colisión por ejes.

    El desplazamiento se subdivide para no atravesar tiles finos a alta
    velocidad. Si el movimiento completo falla se prueba X y después Y, lo que
    produce deslizamiento natural contra paredes.
    """
    if max_step <= 0:
        raise ValueError("max_step debe ser positivo.")
    position = start.copy()
    distance = delta.length()
    if distance <= 1e-9:
        return CollisionResult(position)

    steps = max(1, math.ceil(distance / max_step))
    step = delta / steps
    hit_x = False
    hit_y = False
    for _ in range(steps):
        candidate = position + step
        if not circle_hits_solid(tilemap, candidate, radius):
            position = candidate
            continue
        moved = False
        candidate_x = Vec2(position.x + step.x, position.y)
        if abs(step.x) > 1e-9 and not circle_hits_solid(tilemap, candidate_x, radius):
            position = candidate_x
            moved = True
        else:
            hit_x = hit_x or abs(step.x) > 1e-9
        candidate_y = Vec2(position.x, position.y + step.y)
        if abs(step.y) > 1e-9 and not circle_hits_solid(tilemap, candidate_y, radius):
            position = candidate_y
            moved = True
        else:
            hit_y = hit_y or abs(step.y) > 1e-9
        if not moved:
            break
    return CollisionResult(position, hit_x=hit_x, hit_y=hit_y)


def has_line_of_sight(
    tilemap: TileMap,
    start: Vec2,
    end: Vec2,
    step: float = 6.0,
) -> bool:
    delta = end - start
    distance = delta.length()
    if distance <= 1e-9:
        return not tilemap.is_solid_at(start.x, start.y)
    if step <= 0:
        raise ValueError("step debe ser positivo.")
    samples = max(1, math.ceil(distance / step))
    for index in range(samples + 1):
        point = start + delta * (index / samples)
        if tilemap.is_solid_at(point.x, point.y):
            return False
    return True
