"""Enemigos con máquinas de estado ligeras.

La IA no conoce pygame ni la escena: recibe posición del jugador y el mapa, y
devuelve intenciones (por ejemplo, disparar). La escena materializa esas
intenciones en proyectiles y aplica daño de contacto.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field

from game.ai.astar import find_path
from game.core.config import EnemyStats
from game.core.math2d import Vec2
from game.entities.enemy_catalog import EnemyDefinition, definition_for
from game.entities.projectiles import ProjectileSpec
from game.world.collision import has_line_of_sight, move_circle
from game.world.tilemap import TileMap


@dataclass(slots=True)
class EnemyIntent:
    projectile: ProjectileSpec | None = None


@dataclass(slots=True)
class Enemy:
    id: str
    kind: str
    position: Vec2
    stats: EnemyStats
    health: float = field(default=0.0)
    state: str = "chase"
    state_timer: float = 0.0
    shoot_cooldown: float = 0.0
    touch_cooldown: float = 0.0
    charge_cooldown: float = 0.0
    hit_flash: float = 0.0
    anim_time: float = 0.0
    knockback: Vec2 = field(default_factory=Vec2)
    _charge_direction: Vec2 = field(default_factory=Vec2)
    _strafe_sign: float = 1.0

    def __post_init__(self) -> None:
        if self.health <= 0:
            self.health = self.stats.health
        # Hash de Python está aleatorizado por proceso; usar la suma de
        # caracteres mantiene el comportamiento reproducible.
        self._strafe_sign = 1.0 if sum(map(ord, self.id)) % 2 == 0 else -1.0

    @property
    def radius(self) -> float:
        return self.stats.radius

    @property
    def alive(self) -> bool:
        return self.health > 0.0

    @property
    def name(self) -> str:
        return definition_for(self.kind).name

    def update(
        self,
        dt: float,
        player_position: Vec2,
        player_radius: float,
        tilemap: TileMap,
        rng: random.Random,
    ) -> EnemyIntent:
        if dt <= 0 or not self.alive:
            return EnemyIntent()
        self.anim_time += dt
        self.hit_flash = max(0.0, self.hit_flash - dt)
        self.shoot_cooldown = max(0.0, self.shoot_cooldown - dt)
        self.touch_cooldown = max(0.0, self.touch_cooldown - dt)
        self.charge_cooldown = max(0.0, self.charge_cooldown - dt)
        self.state_timer = max(0.0, self.state_timer - dt)

        to_player = player_position - self.position
        distance = to_player.length()
        direction = to_player.normalized() if distance > 1e-6 else Vec2()

        intent = EnemyIntent()
        definition = definition_for(self.kind)
        if definition.behavior == "ranged":
            intent = self._update_ranged(
                definition, dt, direction, distance, tilemap, player_position
            )
        elif definition.behavior == "charger":
            self._update_charger(definition, dt, direction, distance, tilemap)
        else:
            self._update_melee(
                definition, dt, direction, distance, player_radius, tilemap, player_position
            )

        self.knockback = self.knockback * math.exp(-10.0 * dt)
        return intent

    def _move(self, tilemap: TileMap, delta: Vec2) -> None:
        if delta.length_squared() <= 1e-9:
            return
        result = move_circle(
            tilemap, self.position, self.radius, delta, max_step=max(2.0, self.radius / 2)
        )
        self.position = result.position

    def _update_melee(
        self,
        definition: EnemyDefinition,
        dt: float,
        direction: Vec2,
        distance: float,
        player_radius: float,
        tilemap: TileMap,
        player_position: Vec2,
    ) -> None:
        desired = self.radius + player_radius - 2.0
        if distance > desired:
            move_dir = direction
            if distance > 40.0 and not has_line_of_sight(tilemap, self.position, player_position):
                path = find_path(tilemap, self.position, player_position, budget_ms=1.0)
                if path and len(path) > 0:
                    diff = path[0] - self.position
                    if diff.length_squared() > 1e-4:
                        move_dir = diff.normalized()

            wobble = 1.0 + definition.param("wobble_amplitude") * math.sin(
                self.anim_time * definition.param("wobble_frequency")
            )
            step = move_dir * (self.stats.speed * wobble * dt)
            step = step + self.knockback * dt
            self._move(tilemap, step)
        else:
            self._move(tilemap, self.knockback * dt)

    def _update_ranged(
        self,
        definition: EnemyDefinition,
        dt: float,
        direction: Vec2,
        distance: float,
        tilemap: TileMap,
        player_position: Vec2,
    ) -> EnemyIntent:
        intent = EnemyIntent()
        has_sight = has_line_of_sight(tilemap, self.position, player_position)
        far = definition.param("far_distance")
        near = definition.param("near_distance")
        if distance > far:
            move_direction = direction
        elif distance < near:
            move_direction = -direction
        else:
            perpendicular = Vec2(-direction.y, direction.x)
            move_direction = perpendicular * self._strafe_sign
        if has_sight and distance <= self.stats.attack_range:
            if self.shoot_cooldown <= 0.0:
                self.shoot_cooldown = self.stats.shoot_cooldown
                if distance > 1e-6:
                    intent.projectile = ProjectileSpec(
                        origin=self.position
                        + direction * (self.radius + definition.param("origin_offset")),
                        direction=direction,
                        speed=self.stats.projectile_speed,
                        damage=self.stats.touch_damage + definition.param("projectile_bonus"),
                    )
        step = move_direction * (self.stats.speed * definition.param("move_scale") * dt)
        step = step + self.knockback * dt
        self._move(tilemap, step)
        return intent

    def _update_charger(
        self,
        definition: EnemyDefinition,
        dt: float,
        direction: Vec2,
        distance: float,
        tilemap: TileMap,
    ) -> None:
        speed = self.stats.speed
        if self.state == "chase":
            if (
                distance <= self.stats.attack_range
                and self.charge_cooldown <= 0.0
                and distance > definition.param("min_charge_distance")
            ):
                self.state = "windup"
                self.state_timer = definition.param("windup_time")
                self._charge_direction = direction
            else:
                step = direction * (speed * dt) + self.knockback * dt
                self._move(tilemap, step)
        elif self.state == "windup":
            if self.state_timer <= 0.0:
                self.state = "charge"
                self.state_timer = definition.param("charge_time")
        elif self.state == "charge":
            step = self._charge_direction * (
                speed * definition.param("charge_speed_scale") * dt
            )
            step = step + self.knockback * dt
            self._move(tilemap, step)
            if self.state_timer <= 0.0:
                self.state = "recover"
                self.state_timer = definition.param("recover_time")
        elif self.state == "recover":
            if self.state_timer <= 0.0:
                self.state = "chase"
                self.charge_cooldown = definition.param("charge_cooldown")
            self._move(tilemap, self.knockback * dt)

    def take_damage(
        self, amount: float, source: Vec2 | None = None, knockback_force: float = 0.0
    ) -> bool:
        if amount <= 0 or not self.alive:
            return False
        self.health = max(0.0, self.health - amount)
        self.hit_flash = 0.16
        if source is not None and knockback_force > 0:
            direction = (self.position - source).normalized()
            if direction.length_squared() <= 1e-9:
                direction = Vec2(1, 0)
            self.knockback = direction * knockback_force
        return True


def separate_enemies(enemies: list[Enemy], tilemap: TileMap) -> None:
    """Evita que los enemigos se apilen, empujándolos suavemente."""
    for index, first in enumerate(enemies):
        if not first.alive:
            continue
        for second in enemies[index + 1 :]:
            if not second.alive:
                continue
            delta = second.position - first.position
            minimum = first.radius + second.radius - 2.0
            distance = delta.length()
            if distance >= minimum or distance <= 1e-6:
                continue
            push = delta.normalized() * ((minimum - distance) * 0.5)
            first._move(tilemap, -push)
            second._move(tilemap, push)
