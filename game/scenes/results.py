"""Pantalla de fin de partida: derrota o victoria."""

from __future__ import annotations

import random
from dataclasses import dataclass

import pygame

from game.core.math2d import Vec2
from game.render import palette
from game.render.background import vertical_gradient
from game.render.effects import Effects
from game.render.ui import MenuEntry, MenuList, draw_panel, draw_text
from game.scenes.base import Scene
from game.world.camera import Camera


@dataclass(frozen=True, slots=True)
class RunSummary:
    victory: bool
    score: int
    kills: int
    duration: float
    floor: int
    shards: int
    seed: int
    record_error: str | None = None


class ResultsScene(Scene):
    def __init__(self, app, summary: RunSummary) -> None:
        super().__init__(app)
        self.summary = summary
        width, height = app.config.window.width, app.config.window.height
        self.background = vertical_gradient(
            (width, height),
            (8, 9, 16) if not summary.victory else (20, 12, 10),
            (24, 10, 16) if not summary.victory else (52, 24, 12),
        )
        self.menu = MenuList(
            [
                MenuEntry("Volver a intentarlo", "retry"),
                MenuEntry("Clasificación", "scores"),
                MenuEntry("Menú principal", "menu"),
            ]
        )
        self.camera = Camera(width, height)
        self.camera.position = Vec2(width / 2, height / 2)
        self.effects = Effects((width, height))
        self.time = 0.0
        self._rng = random.Random(0xDEAD if not summary.victory else 0xF1A6E)
        self._timer = 0.0

    def on_enter(self) -> None:
        self.app.input.reset()
        self.app.audio.play("victory" if self.summary.victory else "death")

    def handle_event(self, event: pygame.event.Event) -> None:
        action = self.menu.handle_event(event)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self._go("menu")
            return
        if action:
            self._go(action)

    def _go(self, action: str) -> None:
        self.app.audio.play("ui")
        if action == "retry":
            from game.scenes.play import PlayScene

            self.app.replace_scene(PlayScene(self.app))
        elif action == "scores":
            from game.scenes.leaderboard import LeaderboardScene

            self.app.replace_scene(LeaderboardScene(self.app))
        elif action == "menu":
            from game.scenes.menu import MenuScene

            self.app.replace_scene(MenuScene(self.app))

    def update(self, dt: float) -> None:
        self.time += dt
        self.effects.update(dt)
        self._timer -= dt
        if self._timer <= 0:
            self._timer = 0.18
            width, height = self.app.config.window.width, self.app.config.window.height
            color = (255, 150, 60) if self.summary.victory else (150, 90, 130)
            self.effects.particles.emit(
                Vec2(self._rng.uniform(0, width), height + 6),
                color,
                count=1,
                speed_min=20,
                speed_max=50,
                life_min=2.0,
                life_max=4.0,
                size_min=1.0,
                size_max=2.5,
                gravity=-14,
                drag=0.2,
                rng=self._rng,
            )

    def draw(self, surface: pygame.Surface) -> None:
        width, height = surface.get_size()
        surface.blit(self.background, (0, 0))
        title = "LA FRAGUA DESPIERTA" if self.summary.victory else "HAS CAÍDO"
        subtitle = (
            "La ascua vuelve a arder. La mazmorra te recuerda."
            if self.summary.victory
            else "La oscuridad te reclama. Pero la Fragua sigue esperando."
        )
        color = palette.ACCENT if self.summary.victory else (220, 110, 110)
        draw_text(
            surface,
            self.app.fonts,
            title,
            (width // 2, 84),
            58,
            color=color,
            center=True,
            bold=True,
        )
        draw_text(
            surface,
            self.app.fonts,
            subtitle,
            (width // 2, 134),
            21,
            color=palette.TEXT_DIM,
            center=True,
        )

        panel = pygame.Rect(0, 0, 640, 310)
        panel.center = (width // 2, height // 2 - 6)
        draw_panel(surface, panel, fill=(16, 15, 26, 242))
        minutes, seconds = divmod(int(self.summary.duration), 60)
        rows = [
            ("Puntuación", f"{self.summary.score:,}"),
            ("Enemigos derrotados", str(self.summary.kills)),
            ("Tiempo", f"{minutes:02d}:{seconds:02d}"),
            ("Profundidad", f"Piso {self.summary.floor}"),
            ("Fragmentos", f"{self.summary.shards}/3"),
            ("Semilla", str(self.summary.seed)),
        ]
        y = panel.y + 34
        for label, value in rows:
            draw_text(surface, self.app.fonts, label, (panel.x + 48, y), 24, color=palette.TEXT_DIM)
            draw_text(
                surface,
                self.app.fonts,
                value,
                (panel.right - 48, y),
                24,
                color=palette.GOLD if label == "Puntuación" else palette.TEXT,
            )
            y += 42

        if self.summary.record_error:
            draw_text(
                surface,
                self.app.fonts,
                self.summary.record_error,
                (width // 2, panel.bottom + 26),
                19,
                color=(255, 130, 120),
                center=True,
            )

        self.menu.draw(surface, self.app.fonts, width // 2, height - 160, spacing=46, width=330)
        self.effects.draw(surface, self.camera, self.app.fonts)
