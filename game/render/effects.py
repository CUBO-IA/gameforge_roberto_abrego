"""Partículas, texto flotante y sacudida de cámara."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass

import pygame

from game.core.math2d import Vec2
from game.render.fonts import FontCache
from game.world.camera import Camera


@dataclass(slots=True)
class Particle:
    position: Vec2
    velocity: Vec2
    life: float
    max_life: float
    size: float
    color: tuple[int, int, int]
    drag: float = 1.8
    gravity: float = 0.0
    add: bool = False


@dataclass(slots=True)
class FloatingText:
    text: str
    position: Vec2
    color: tuple[int, int, int]
    life: float = 0.9
    max_life: float = 0.9
    size: int = 20


class ScreenShake:
    def __init__(self) -> None:
        self.intensity = 0.0

    def add(self, amount: float) -> None:
        self.intensity = min(18.0, self.intensity + amount)

    def update(self, dt: float) -> None:
        self.intensity = max(0.0, self.intensity - dt * 22.0)

    def offset(self, rng: random.Random) -> Vec2:
        if self.intensity <= 0.1:
            return Vec2()
        return Vec2(
            rng.uniform(-self.intensity, self.intensity),
            rng.uniform(-self.intensity, self.intensity),
        )


class ParticleSystem:
    def __init__(self, maximum: int = 700) -> None:
        self.maximum = maximum
        self.particles: list[Particle] = []
        self._glow_cache: dict[tuple[int, tuple[int, int, int]], pygame.Surface] = {}

    def emit(
        self,
        position: Vec2,
        color: tuple[int, int, int],
        count: int,
        speed_min: float = 30.0,
        speed_max: float = 140.0,
        life_min: float = 0.22,
        life_max: float = 0.6,
        size_min: float = 1.5,
        size_max: float = 4.0,
        gravity: float = 0.0,
        drag: float = 1.8,
        add: bool = False,
        rng: random.Random | None = None,
    ) -> None:
        generator = rng or random
        available = self.maximum - len(self.particles)
        if available <= 0:
            return
        for _ in range(min(count, available)):
            angle = generator.uniform(0.0, math.tau)
            speed = generator.uniform(speed_min, speed_max)
            life = generator.uniform(life_min, life_max)
            self.particles.append(
                Particle(
                    position=position.copy(),
                    velocity=Vec2.from_angle(angle, speed),
                    life=life,
                    max_life=life,
                    size=generator.uniform(size_min, size_max),
                    color=color,
                    drag=drag,
                    gravity=gravity,
                    add=add,
                )
            )

    def update(self, dt: float) -> None:
        alive: list[Particle] = []
        damping = math.exp(-2.2 * dt)
        for particle in self.particles:
            particle.life -= dt
            if particle.life <= 0:
                continue
            particle.velocity = particle.velocity * damping
            particle.velocity.y += particle.gravity * dt
            particle.position = particle.position + particle.velocity * dt
            alive.append(particle)
        self.particles = alive

    def _glow(
        self, size: int, color: tuple[int, int, int], alpha: int
    ) -> pygame.Surface:
        key = (size, color)
        glow = self._glow_cache.get(key)
        if glow is None:
            radius = max(4, size * 3)
            glow = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(
                glow, (color[0] // 4, color[1] // 4, color[2] // 4, 90), (radius, radius), radius
            )
            pygame.draw.circle(
                glow, (color[0] // 2, color[1] // 2, color[2] // 2, 150), (radius, radius), radius // 2
            )
            self._glow_cache[key] = glow
        glow.set_alpha(alpha)
        return glow

    def draw(
        self, surface: pygame.Surface, camera: Camera, shake: Vec2, alpha_surface: pygame.Surface
    ) -> None:
        for particle in self.particles:
            screen = camera.world_to_screen(particle.position, shake)
            fade = max(0.0, particle.life / particle.max_life)
            size = max(1, int(particle.size * (0.35 + 0.65 * fade)))
            color = particle.color
            if particle.add:
                glow = self._glow(size, color, int(90 + 130 * fade))
                surface.blit(
                    glow,
                    glow.get_rect(center=(int(screen.x), int(screen.y))),
                    special_flags=pygame.BLEND_RGB_ADD,
                )
            else:
                pygame.draw.circle(
                    surface,
                    (
                        int(color[0] * (0.35 + 0.65 * fade)),
                        int(color[1] * (0.35 + 0.65 * fade)),
                        int(color[2] * (0.35 + 0.65 * fade)),
                    ),
                    (int(screen.x), int(screen.y)),
                    size,
                )


class Effects:
    def __init__(self, window_size: tuple[int, int]) -> None:
        self.particles = ParticleSystem()
        self.texts: list[FloatingText] = []
        self.shake = ScreenShake()
        self._alpha = pygame.Surface(window_size, pygame.SRCALPHA)
        self._ambience = 0.0
        self._rng = random.Random(0xF0A6E)

    def update(self, dt: float, player_position: Vec2 | None = None) -> None:
        self.particles.update(dt)
        self.shake.update(dt)
        for text in self.texts:
            text.life -= dt
            text.position.y -= 26.0 * dt
        self.texts = [text for text in self.texts if text.life > 0]
        if player_position is not None:
            self._ambience -= dt
            if self._ambience <= 0.0:
                self._ambience = self._rng.uniform(0.16, 0.42)
                offset = Vec2(
                    self._rng.uniform(-150, 150), self._rng.uniform(-90, 90)
                )
                self.particles.emit(
                    player_position + offset,
                    (255, 140, 60),
                    count=1,
                    speed_min=4,
                    speed_max=14,
                    life_min=0.8,
                    life_max=1.8,
                    size_min=1.0,
                    size_max=2.4,
                    gravity=-10.0,
                    drag=0.4,
                    add=True,
                    rng=self._rng,
                )

    def add_text(
        self,
        text: str,
        position: Vec2,
        color: tuple[int, int, int] = (255, 240, 210),
        size: int = 20,
    ) -> None:
        self.texts.append(FloatingText(text, position.copy(), color, size=size))

    def burst(
        self,
        position: Vec2,
        color: tuple[int, int, int],
        count: int = 12,
        speed: float = 150.0,
        add: bool = False,
    ) -> None:
        self.particles.emit(
            position,
            color,
            count,
            speed_min=speed * 0.35,
            speed_max=speed,
            life_min=0.18,
            life_max=0.55,
            size_min=1.2,
            size_max=3.6,
            drag=3.0,
            add=add,
            rng=self._rng,
        )

    def current_shake(self) -> Vec2:
        return self.shake.offset(self._rng)

    def draw(
        self,
        surface: pygame.Surface,
        camera: Camera,
        fonts: FontCache,
        shake: Vec2 | None = None,
    ) -> None:
        if shake is None:
            shake = self.current_shake()
        self.particles.draw(surface, camera, shake, self._alpha)
        for text in self.texts:
            screen = camera.world_to_screen(text.position, shake)
            fade = max(0.0, text.life / text.max_life)
            color = (
                int(text.color[0] * (0.4 + 0.6 * fade)),
                int(text.color[1] * (0.4 + 0.6 * fade)),
                int(text.color[2] * (0.4 + 0.6 * fade)),
            )
            image = fonts.get(text.size, True).render(text.text, True, color)
            surface.blit(image, image.get_rect(center=(int(screen.x), int(screen.y))))


class HitstopManager:
    """Gestiona micro-pausas de la simulación tras impactos pesados (Game Juice)."""

    __slots__ = ("duration_remaining",)

    def __init__(self) -> None:
        self.duration_remaining: float = 0.0

    def trigger(self, duration_s: float) -> None:
        """Activa o extiende la pausa de hitstop."""
        self.duration_remaining = max(self.duration_remaining, duration_s)

    def update(self, dt: float) -> bool:
        """Avanza el temporizador. Devuelve True si la simulación debe avanzar, False si sigue congelada."""
        if self.duration_remaining > 0.0:
            self.duration_remaining -= dt
            if self.duration_remaining <= 0.0:
                self.duration_remaining = 0.0
                return True
            return False
        return True

    @property
    def is_frozen(self) -> bool:
        return self.duration_remaining > 0.0


class TraumaScreenShake:
    """Sacudida de pantalla basada en el modelo físico de Trauma no lineal (Squirrel Eiserloh)."""

    __slots__ = (
        "trauma",
        "max_offset_px",
        "max_angle_deg",
        "decay_rate",
        "time_accumulator",
    )

    def __init__(
        self,
        max_offset_px: float = 16.0,
        max_angle_deg: float = 2.5,
        decay_rate: float = 2.0,
    ) -> None:
        self.trauma: float = 0.0
        self.max_offset_px = max_offset_px
        self.max_angle_deg = max_angle_deg
        self.decay_rate = decay_rate
        self.time_accumulator: float = 0.0

    def add_trauma(self, amount: float) -> None:
        """Añade trauma acotado en el intervalo [0.0, 1.0]."""
        self.trauma = min(1.0, self.trauma + amount)

    def update(self, dt: float) -> None:
        """Avanza la oscilación armónica y decae el trauma."""
        self.time_accumulator += dt * 32.0
        self.trauma = max(0.0, self.trauma - self.decay_rate * dt)

    def offset(self, rng: random.Random | None = None) -> Vec2:
        """Calcula el desplazamiento 2D resultante de la sacudida."""
        if self.trauma <= 0.001:
            return Vec2()

        shake = self.trauma * self.trauma
        # Composición armónica pseudo-aleatoria
        ox = self.max_offset_px * shake * (
            math.sin(self.time_accumulator) + 0.5 * math.sin(self.time_accumulator * 2.3)
        )
        oy = self.max_offset_px * shake * (
            math.cos(self.time_accumulator * 1.4) + 0.5 * math.cos(self.time_accumulator * 3.1)
        )
        return Vec2(ox, oy)

    def get_transform(self) -> tuple[Vec2, float]:
        """Devuelve la traslación y el ángulo de rotación (grados)."""
        if self.trauma <= 0.001:
            return Vec2(), 0.0

        shake = self.trauma * self.trauma
        off = self.offset()
        angle = self.max_angle_deg * shake * math.sin(self.time_accumulator * 0.9)
        return off, angle


class ParticlePool:
    """Pool preasignado de partículas continuas de memoria sin asignaciones dinámicas por frame."""

    __slots__ = (
        "capacity",
        "count",
        "x",
        "y",
        "vx",
        "vy",
        "life",
        "max_life",
        "size",
        "color_r",
        "color_g",
        "color_b",
        "drag",
        "gravity",
        "blend_add",
    )

    def __init__(self, capacity: int = 800) -> None:
        self.capacity = capacity
        self.count = 0
        self.x = [0.0] * capacity
        self.y = [0.0] * capacity
        self.vx = [0.0] * capacity
        self.vy = [0.0] * capacity
        self.life = [0.0] * capacity
        self.max_life = [1.0] * capacity
        self.size = [2.0] * capacity
        self.color_r = [255] * capacity
        self.color_g = [255] * capacity
        self.color_b = [255] * capacity
        self.drag = [1.0] * capacity
        self.gravity = [0.0] * capacity
        self.blend_add = [False] * capacity

    def spawn(
        self,
        x: float,
        y: float,
        vx: float,
        vy: float,
        life: float,
        size: float,
        color: tuple[int, int, int],
        drag: float = 1.0,
        gravity: float = 0.0,
        blend_add: bool = False,
    ) -> bool:
        """Genera una partícula en O(1). Devuelve False si el pool está saturado."""
        if self.count >= self.capacity:
            return False

        idx = self.count
        self.x[idx] = x
        self.y[idx] = y
        self.vx[idx] = vx
        self.vy[idx] = vy
        self.life[idx] = life
        self.max_life[idx] = life
        self.size[idx] = size
        self.color_r[idx], self.color_g[idx], self.color_b[idx] = color
        self.drag[idx] = drag
        self.gravity[idx] = gravity
        self.blend_add[idx] = blend_add
        self.count += 1
        return True

    def update(self, dt: float) -> None:
        """Actualización compacta con eliminación swap-and-pop en O(1)."""
        i = 0
        while i < self.count:
            self.life[i] -= dt
            if self.life[i] <= 0.0:
                self.count -= 1
                if i < self.count:
                    self._swap(i, self.count)
                continue

            drag_factor = max(0.0, 1.0 - (self.drag[i] * dt))
            self.vx[i] *= drag_factor
            self.vy[i] = (self.vy[i] + self.gravity[i] * dt) * drag_factor
            self.x[i] += self.vx[i] * dt
            self.y[i] += self.vy[i] * dt
            i += 1

    def _swap(self, a: int, b: int) -> None:
        self.x[a], self.x[b] = self.x[b], self.x[a]
        self.y[a], self.y[b] = self.y[b], self.y[a]
        self.vx[a], self.vx[b] = self.vx[b], self.vx[a]
        self.vy[a], self.vy[b] = self.vy[b], self.vy[a]
        self.life[a], self.life[b] = self.life[b], self.life[a]
        self.max_life[a], self.max_life[b] = self.max_life[b], self.max_life[a]
        self.size[a], self.size[b] = self.size[b], self.size[a]
        self.color_r[a], self.color_r[b] = self.color_r[b], self.color_r[a]
        self.color_g[a], self.color_g[b] = self.color_g[b], self.color_g[a]
        self.color_b[a], self.color_b[b] = self.color_b[b], self.color_b[a]
        self.drag[a], self.drag[b] = self.drag[b], self.drag[a]
        self.gravity[a], self.gravity[b] = self.gravity[b], self.gravity[a]
        self.blend_add[a], self.blend_add[b] = self.blend_add[b], self.blend_add[a]

    def clear(self) -> None:
        """Reinicia el contador de partículas activas en O(1)."""
        self.count = 0

