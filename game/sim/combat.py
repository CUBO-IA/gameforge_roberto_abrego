"""Resolución del ataque cuerpo a cuerpo del jugador.

Sistema puro de simulación: muta a los enemigos alcanzados y los devuelve.
"""

from __future__ import annotations

import math

from game.core.math2d import Vec2, clamp
from game.entities.enemies import Enemy
from game.entities.player import AttackSpec
from game.world.spatial import SpatialHash


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


def resolve_player_attack(
    spec: AttackSpec,
    enemies: list[Enemy],
    spatial_grid: SpatialHash[Enemy] | None = None,
) -> list[Enemy]:
    """Aplica daño en arco y devuelve los enemigos alcanzados.

    Usa SpatialHash para filtrar candidatos si la lista de enemigos es grande.
    """
    if spatial_grid is not None:
        candidates = spatial_grid.query_radius(spec.origin, spec.range + 32.0)
    elif len(enemies) > 20:
        grid: SpatialHash[Enemy] = SpatialHash(cell_size=64.0)
        for enemy in enemies:
            if enemy.alive:
                grid.insert(enemy, enemy.position, enemy.radius)
        candidates = grid.query_radius(spec.origin, spec.range + 32.0)
    else:
        candidates = enemies

    hit: list[Enemy] = []
    for enemy in candidates:
        if attack_hits_enemy(
            spec.origin, spec.direction, spec.range, spec.arc_degrees, enemy
        ):
            enemy.take_damage(spec.damage, spec.origin, spec.knockback)
            hit.append(enemy)
    return hit
