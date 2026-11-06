"""Enemigos con máquinas de estado ligeras.

La IA no conoce pygame ni la escena: recibe posición del jugador y el mapa, y
devuelve intenciones (por ejemplo, disparar). La escena materializa esas
intenciones en proyectiles y aplica daño de contacto.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field

from game.core.config import EnemyStats
from game.core.math2d import Vec2, clamp
from game.entities.projectiles import ProjectileSpec
from game.world.collision import has_line_of_sight, move_circle
from game.world.tilemap import TileMap

ENEMY_NAMES = {
    "slime": "Cieno",
    "wisp": "Fuego fatuo",
    "brute": "Bruto de escoria",
}


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
        return ENEMY_NAMES.get(self.kind, self.kind)

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
        if self.kind == "wisp":
            intent = self._update_wisp(
                dt, direction, distance, tilemap, rng, player_position
            )
        elif self.kind == "brute":
            self._update_brute(dt, direction, distance, tilemap)
        else:
            self._update_slime(dt, direction, distance, player_radius, tilemap)

        self.knockback = self.knockback * math.exp(-10.0 * dt)
        return intent

    def _move(self, tilemap: TileMap, delta: Vec2) -> None:
        if delta.length_squared() <= 1e-9:
            return
        result = move_circle(
            tilemap, self.position, self.radius, delta, max_step=max(2.0, self.radius / 2)
        )
        self.position = result.position

    def _update_slime(
        self,
        dt: float,
        direction: Vec2,
        distance: float,
        player_radius: float,
        tilemap: TileMap,
    ) -> None:
        desired = self.radius + player_radius - 2.0
        if distance > desired:
            wobble = 1.0 + 0.16 * math.sin(self.anim_time * 6.0)
            step = direction * (self.stats.speed * wobble * dt)
            step = step + self.knockback * dt
            self._move(tilemap, step)
        else:
            self._move(tilemap, self.knockback * dt)

    def _update_wisp(
        self,
        dt: float,
        direction: Vec2,
        distance: float,
        tilemap: TileMap,
        rng: random.Random,
        player_position: Vec2,
    ) -> EnemyIntent:
        intent = EnemyIntent()
        has_sight = has_line_of_sight(tilemap, self.position, player_position)
        if distance > 250.0:
            move_direction = direction
        elif distance < 140.0:
            move_direction = -direction
        else:
            perpendicular = Vec2(-direction.y, direction.x)
            move_direction = perpendicular * self._strafe_sign
        if has_sight and distance <= self.stats.attack_range:
            if self.shoot_cooldown <= 0.0:
                self.shoot_cooldown = self.stats.shoot_cooldown
                if distance > 1e-6:
                    intent.projectile = ProjectileSpec(
                        origin=self.position + direction * (self.radius + 4.0),
                        direction=direction,
                        speed=self.stats.projectile_speed,
                        damage=self.stats.touch_damage + 4.0,
                    )
        step = move_direction * (self.stats.speed * 0.55 * dt) + self.knockback * dt
        self._move(tilemap, step)
        return intent

    def _update_brute(
        self, dt: float, direction: Vec2, distance: float, tilemap: TileMap
    ) -> None:
        speed = self.stats.speed
        if self.state == "chase":
            if (
                distance <= self.stats.attack_range
                and self.charge_cooldown <= 0.0
                and distance > 30.0
            ):
                self.state = "windup"
                self.state_timer = 0.55
                self._charge_direction = direction
            else:
                step = direction * (speed * dt) + self.knockback * dt
                self._move(tilemap, step)
        elif self.state == "windup":
            if self.state_timer <= 0.0:
                self.state = "charge"
                self.state_timer = 0.42
        elif self.state == "charge":
            step = self._charge_direction * (speed * 4.0 * dt) + self.knockback * dt
            self._move(tilemap, step)
            if self.state_timer <= 0.0:
                self.state = "recover"
                self.state_timer = 0.7
        elif self.state == "recover":
            if self.state_timer <= 0.0:
                self.state = "chase"
                self.charge_cooldown = 2.4
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
