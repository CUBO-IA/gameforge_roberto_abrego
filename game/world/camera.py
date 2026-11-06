"""Cámara con seguimiento suave y límites de mapa."""

from __future__ import annotations

import math

from game.core.math2d import Vec2, clamp


class Camera:
    def __init__(self, viewport_width: int, viewport_height: int) -> None:
        if viewport_width <= 0 or viewport_height <= 0:
            raise ValueError("El viewport debe ser positivo.")
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height
        self.position = Vec2(viewport_width / 2, viewport_height / 2)

    @property
    def top_left(self) -> Vec2:
        return Vec2(
            self.position.x - self.viewport_width / 2,
            self.position.y - self.viewport_height / 2,
        )

    def snap_to(self, target: Vec2, map_width: int, map_height: int) -> None:
        self.position = self._clamped(target, map_width, map_height)

    def update(
        self,
        target: Vec2,
        dt: float,
        map_width: int,
        map_height: int,
        smoothing: float = 7.5,
    ) -> None:
        desired = self._clamped(target, map_width, map_height)
        # Interpolación exponencial estable para cualquier framerate.
        factor = 1.0 - math.exp(-max(0.0, smoothing) * max(0.0, dt))
        self.position = Vec2(
            self.position.x + (desired.x - self.position.x) * factor,
            self.position.y + (desired.y - self.position.y) * factor,
        )

    def _clamped(self, target: Vec2, map_width: int, map_height: int) -> Vec2:
        half_w = self.viewport_width / 2
        half_h = self.viewport_height / 2
        if map_width <= self.viewport_width:
            x = map_width / 2
        else:
            x = clamp(target.x, half_w, map_width - half_w)
        if map_height <= self.viewport_height:
            y = map_height / 2
        else:
            y = clamp(target.y, half_h, map_height - half_h)
        return Vec2(x, y)

    def world_to_screen(self, point: Vec2, shake: Vec2 | None = None) -> Vec2:
        offset = shake if shake is not None else Vec2()
        return Vec2(
            point.x - self.position.x + self.viewport_width / 2 + offset.x,
            point.y - self.position.y + self.viewport_height / 2 + offset.y,
        )

    def screen_to_world(self, point: Vec2, shake: Vec2 | None = None) -> Vec2:
        offset = shake if shake is not None else Vec2()
        return Vec2(
            point.x + self.position.x - self.viewport_width / 2 - offset.x,
            point.y + self.position.y - self.viewport_height / 2 - offset.y,
        )
