"""Proyectiles enemigos simples."""

from __future__ import annotations

from dataclasses import dataclass

from game.core.math2d import Vec2
from game.world.tilemap import TileMap


@dataclass(slots=True)
class Projectile:
    position: Vec2
    velocity: Vec2
    radius: float
    damage: float
    ttl: float = 4.0
    color: tuple[int, int, int] = (150, 120, 255)
    alive: bool = True
    trail_timer: float = 0.0

    def update(self, dt: float, tilemap: TileMap) -> None:
        if not self.alive or dt <= 0:
            return
        self.ttl -= dt
        if self.ttl <= 0:
            self.alive = False
            return
        self.position = self.position + self.velocity * dt
        if tilemap.is_solid_at(self.position.x, self.position.y):
            self.alive = False


@dataclass(frozen=True, slots=True)
class ProjectileSpec:
    origin: Vec2
    direction: Vec2
    speed: float
    damage: float
    radius: float = 7.0
