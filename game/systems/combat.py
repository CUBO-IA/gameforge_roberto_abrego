"""Resolución del ataque cuerpo a cuerpo del jugador."""

from __future__ import annotations

from game.entities.enemies import Enemy, attack_hits_enemy
from game.entities.player import AttackSpec


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
