"""Engagement de enemigos y proyectiles contra el jugador.

Sistemas puros que encapsulan el bucle de amenazas: actualización de
enemigos, disparos, contacto y colisión de proyectiles. Devuelven datos
(p Specs, daños) que la escena convierte en presentación.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from game.ai.dijkstra import DijkstraMap
from game.core.math2d import Vec2, circles_overlap
from game.entities.enemies import Enemy, separate_enemies
from game.entities.player import Player
from game.entities.projectiles import Projectile, ProjectileSpec
from game.world.tilemap import TileMap

SWARM_THRESHOLD: int = 6


@dataclass(slots=True)
class EngagementEvents:
    """Intenciones y daños producidos en un frame por los enemigos."""

    projectiles: list[ProjectileSpec] = field(default_factory=list)
    touch_damage: list[float] = field(default_factory=list)


def update_enemies(
    enemies: list[Enemy],
    dt: float,
    player: Player,
    tilemap: TileMap,
    rng,
    frame_counter: int = 0,
    dijkstra_map: DijkstraMap | None = None,
) -> EngagementEvents:
    """Actualiza a los enemigos aplicando staggering para entidades distantes.

    Si se proporciona ``dijkstra_map`` y la cantidad de enemigos vivos supera
    ``SWARM_THRESHOLD``, se calcula el campo de distancias una sola vez en el frame
    para que todos los enemigos enjambre naveguen en O(1).
    """
    events = EngagementEvents()
    active_dijkstra: DijkstraMap | None = None
    alive_count = sum(1 for e in enemies if e.alive)

    if dijkstra_map is not None and alive_count >= SWARM_THRESHOLD:
        ts = tilemap.tile_size
        p_col = math.floor(player.position.x / ts)
        p_row = math.floor(player.position.y / ts)
        if tilemap.in_bounds(p_col, p_row):
            dijkstra_map.compute(p_col, p_row)
            active_dijkstra = dijkstra_map

    for index, enemy in enumerate(enemies):
        if not enemy.alive:
            continue
        dist_sq = (enemy.position - player.position).length_squared()
        # Staggering: si el enemigo está muy lejos (> 750 px), actualizar 1 de cada 3 frames
        if dist_sq > 562500.0:  # 750^2
            if (index + frame_counter) % 3 != 0:
                continue
            effective_dt = dt * 3.0
        else:
            effective_dt = dt

        intent = enemy.update(
            effective_dt,
            player.position,
            player.radius,
            tilemap,
            rng,
            dijkstra_map=active_dijkstra,
        )
        if intent.projectile is not None:
            events.projectiles.append(intent.projectile)
        if (
            circles_overlap(
                enemy.position, enemy.radius, player.position, player.radius
            )
            and enemy.touch_cooldown <= 0.0
        ):
            enemy.touch_cooldown = 0.8
            if player.take_damage(enemy.stats.touch_damage, enemy.position):
                events.touch_damage.append(enemy.stats.touch_damage)
    separate_enemies(enemies, tilemap)
    return events


def spawn_projectile(spec: ProjectileSpec) -> Projectile:
    """Materializa la intención de disparo de un enemigo."""
    return Projectile(
        position=spec.origin,
        velocity=spec.direction * spec.speed,
        radius=spec.radius,
        damage=spec.damage,
    )


def move_projectiles(
    projectiles: list[Projectile], dt: float, tilemap: TileMap
) -> list[Projectile]:
    """Avanza los proyectiles y elimina los muertos; devuelve los vivos."""
    alive: list[Projectile] = []
    for projectile in projectiles:
        projectile.update(dt, tilemap)
        if projectile.alive:
            alive.append(projectile)
    return alive


def projectile_hits_player(projectile: Projectile, player: Player) -> bool:
    return circles_overlap(
        projectile.position, projectile.radius, player.position, player.radius
    )


def nearest_enemy_position(enemies: list[Enemy]) -> Vec2 | None:
    """Posición de un enemigo vivo (utilidad para pruebas y depuración)."""
    for enemy in enemies:
        if enemy.alive:
            return enemy.position
    return None
