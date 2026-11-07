"""Jugador: movimiento, dash, ataque y salud. Sin pygame."""

from __future__ import annotations

import math
from dataclasses import dataclass

from game.core.config import PlayerConfig
from game.core.math2d import Vec2
from game.world.collision import move_circle
from game.world.tilemap import TileMap


@dataclass(frozen=True, slots=True)
class AttackSpec:
    origin: Vec2
    direction: Vec2
    range: float
    arc_degrees: float
    damage: float
    knockback: float


class Player:
    def __init__(self, position: Vec2, config: PlayerConfig) -> None:
        self.config = config
        self.position = position.copy()
        self.radius = config.radius
        self.health = config.max_health
        self.facing = Vec2(0, 1)
        self.attack_cooldown = 0.0
        self.attack_anim = 0.0
        self.dash_cooldown = 0.0
        self.dash_time = 0.0
        self.invulnerability = 0.0
        self.knockback = Vec2()
        self.pending_attack: AttackSpec | None = None
        self.dash_started = False
        self.damage_flash = 0.0
        self._dash_direction = Vec2(0, 1)
        self.z = 0.0
        self.vz = 0.0
        self.gravity = 520.0
        self.jump_speed = 190.0
        self.jump_started = False
        self.ceiling_z: float | None = None
        self.ceiling_hit = False
        self.anim_player: object = None

    @property
    def max_health(self) -> float:
        return self.config.max_health

    @property
    def alive(self) -> bool:
        return self.health > 0.0

    @property
    def is_dashing(self) -> bool:
        return self.dash_time > 0.0

    @property
    def is_jumping(self) -> bool:
        return self.z > 0.0

    def update(
        self,
        dt: float,
        move: Vec2,
        aim: Vec2,
        dash: bool,
        attack: bool,
        tilemap: TileMap,
        jump: bool = False,
        ceiling_z: float | None = None,
    ) -> None:
        if dt <= 0 or not self.alive:
            return
        self.pending_attack = None
        self.dash_started = False
        self.jump_started = False
        self.ceiling_hit = False

        self.attack_cooldown = max(0.0, self.attack_cooldown - dt)
        self.attack_anim = max(0.0, self.attack_anim - dt)
        self.dash_cooldown = max(0.0, self.dash_cooldown - dt)
        self.invulnerability = max(0.0, self.invulnerability - dt)
        self.damage_flash = max(0.0, self.damage_flash - dt)

        # Mecánica 2.5D: elevación, salto vertical y colisión contra techos
        effective_ceiling = ceiling_z if ceiling_z is not None else self.ceiling_z

        if jump and self.z <= 0.0 and not self.is_dashing:
            if effective_ceiling is None or effective_ceiling > 4.0:
                self.vz = self.jump_speed
                self.jump_started = True

        if self.z > 0.0 or self.vz > 0.0:
            self.z += self.vz * dt
            self.vz -= self.gravity * dt

            # Colisión con techo: frena y empuja hacia abajo
            if effective_ceiling is not None and self.z >= effective_ceiling:
                self.z = effective_ceiling
                self.ceiling_hit = True
                if self.vz > 0.0:
                    self.vz = -50.0

            if self.z <= 0.0:
                self.z = 0.0
                self.vz = 0.0

        move = move.clamped(1.0)
        if aim.length_squared() > 1e-6:
            self.facing = aim.normalized()

        if dash and self.dash_cooldown <= 0.0 and self.dash_time <= 0.0:
            self.dash_time = self.config.dash_duration
            self.dash_cooldown = self.config.dash_cooldown
            self.invulnerability = max(
                self.invulnerability, self.config.dash_duration + 0.06
            )
            self._dash_direction = move if move.length_squared() > 1e-6 else self.facing
            self.dash_started = True

        if attack and self.attack_cooldown <= 0.0:
            self.attack_cooldown = self.config.attack_cooldown
            self.attack_anim = 0.22
            self.pending_attack = self.build_attack()

        if self.is_dashing:
            self.dash_time = max(0.0, self.dash_time - dt)
            delta = self._dash_direction * (self.config.dash_speed * dt)
        else:
            speed = self.config.speed * tilemap.speed_multiplier_at(
                self.position.x, self.position.y
            )
            delta = move * (speed * dt)

        delta = delta + self.knockback * dt
        self.knockback = self.knockback * math.exp(-9.0 * dt)
        result = move_circle(
            tilemap, self.position, self.radius, delta, max_step=max(2.0, self.radius / 2)
        )
        self.position = result.position

        hazard = tilemap.hazard_damage_at(self.position.x, self.position.y)
        if hazard > 0.0 and not self.is_dashing and self.z <= 0.0:
            self.health = max(0.0, self.health - hazard * dt)
            self.damage_flash = 0.15

    def build_attack(self) -> AttackSpec:
        return AttackSpec(
            origin=self.position.copy(),
            direction=self.facing.copy(),
            range=self.config.attack_range,
            arc_degrees=self.config.attack_arc,
            damage=self.config.attack_damage,
            knockback=210.0,
        )

    def take_damage(self, amount: float, source: Vec2 | None = None) -> bool:
        if amount <= 0 or not self.alive or self.invulnerability > 0.0:
            return False
        self.health = max(0.0, self.health - amount)
        self.invulnerability = self.config.invulnerability
        self.damage_flash = 0.25
        if source is not None:
            direction = (self.position - source).normalized()
            if direction.length_squared() <= 1e-9:
                direction = Vec2(1, 0)
            self.knockback = direction * 230.0
        return True

    def heal(self, amount: float) -> float:
        if amount <= 0 or not self.alive:
            return 0.0
        before = self.health
        self.health = min(self.max_health, self.health + amount)
        return self.health - before
