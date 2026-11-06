"""Resolución del ataque cuerpo a cuerpo del jugador.

Sistema puro de simulación: muta a los enemigos alcanzados y los devuelve.
"""

from __future__ import annotations

import math

from game.core.math2d import Vec2, clamp
from game.entities.enemies import Enemy
from game.entities.player import AttackSpec


def attack_hits_enemy(
    origin: Vec2,
    direction: Vec2,
    attack_range: float,
    arc_degrees: float,
    enemy: Enemy,
) -> bool:
    if not enemy.alive:
        return False
    delta = enemy.position - origin
    distance = delta.length()
    if distance > attack_range + enemy.radius:
        return False
    if distance <= 1e-6:
        return True
    angle = abs(math.atan2(delta.y, delta.x) - math.atan2(direction.y, direction.x))
    angle = abs((angle + math.pi) % (2 * math.pi) - math.pi)
    return angle <= math.radians(clamp(arc_degrees, 0.0, 360.0) / 2.0)


def resolve_player_attack(spec: AttackSpec, enemies: list[Enemy]) -> list[Enemy]:
    """Aplica daño en arco y devuelve los enemigos alcanzados."""
    hit: list[Enemy] = []
    for enemy in enemies:
        if attack_hits_enemy(
            spec.origin, spec.direction, spec.range, spec.arc_degrees, enemy
        ):
            enemy.take_damage(spec.damage, spec.origin, spec.knockback)
            hit.append(enemy)
    return hit
