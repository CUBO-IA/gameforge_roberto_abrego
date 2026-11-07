"""Vector 2D y utilidades numéricas sin dependencia de pygame."""

from __future__ import annotations

import math
from collections.abc import Iterator
from dataclasses import dataclass


@dataclass(slots=True)
class Vec2:
    x: float = 0.0
    y: float = 0.0

    def __add__(self, other: Vec2) -> Vec2:
        return Vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Vec2) -> Vec2:
        return Vec2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> Vec2:
        return Vec2(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar: float) -> Vec2:
        return self * scalar

    def __truediv__(self, scalar: float) -> Vec2:
        if scalar == 0:
            raise ZeroDivisionError("No se puede dividir un Vec2 por cero.")
        return Vec2(self.x / scalar, self.y / scalar)

    def __neg__(self) -> Vec2:
        return Vec2(-self.x, -self.y)

    def __iter__(self) -> Iterator[float]:
        yield self.x
        yield self.y

    def copy(self) -> Vec2:
        return Vec2(self.x, self.y)

    def length_squared(self) -> float:
        return self.x * self.x + self.y * self.y

    def length(self) -> float:
        return math.hypot(self.x, self.y)

    def normalized(self) -> Vec2:
        length = self.length()
        if length <= 1e-12:
            return Vec2()
        return Vec2(self.x / length, self.y / length)

    def clamped(self, max_length: float) -> Vec2:
        if max_length <= 0:
            return Vec2()
        length = self.length()
        if length <= max_length or length <= 1e-12:
            return self.copy()
        return self * (max_length / length)

    def dot(self, other: Vec2) -> float:
        return self.x * other.x + self.y * other.y

    def angle(self) -> float:
        return math.atan2(self.y, self.x)

    def distance_to(self, other: Vec2) -> float:
        return math.hypot(self.x - other.x, self.y - other.y)

    def distance_squared_to(self, other: Vec2) -> float:
        dx = self.x - other.x
        dy = self.y - other.y
        return dx * dx + dy * dy

    def as_tuple(self) -> tuple[float, float]:
        return self.x, self.y

    @classmethod
    def from_angle(cls, angle: float, length: float = 1.0) -> Vec2:
        return cls(math.cos(angle) * length, math.sin(angle) * length)


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * clamp(t, 0.0, 1.0)


def normalize_angle(angle: float) -> float:
    """Devuelve un ángulo en el rango [-pi, pi]."""
    return (angle + math.pi) % (2.0 * math.pi) - math.pi


def angle_difference(a: float, b: float) -> float:
    """Diferencia angular absoluta mínima entre dos ángulos."""
    return abs(normalize_angle(a - b))


def circles_overlap(a: Vec2, radius_a: float, b: Vec2, radius_b: float) -> bool:
    return a.distance_squared_to(b) < (radius_a + radius_b) ** 2
