"""Menú principal."""

from __future__ import annotations

import random

import pygame

from game import __version__
from game.core.math2d import Vec2
from game.persistence.savegame import SaveGameError, load_run
from game.render import palette
from game.render.background import draw_anvil, forge_glow, vertical_gradient
from game.render.effects import Effects
from game.render.ui import MenuEntry, MenuList, draw_text
from game.scenes.base import Scene
from game.world.camera import Camera


class MenuScene(Scene):
    def __init__(self, app) -> None:
        super().__init__(app)
        self.time = 0.0
        self.error = ""
        width, height = app.config.window.width, app.config.window.height
        self.background = vertical_gradient(
            (width, height), (10, 9, 18), (30, 15, 18)
        )
        self.glow = forge_glow((width, height), (width // 2, height - 80), 340, (255, 120, 48))
        self.effects = Effects((width, height))
        self.camera = Camera(width, height)
        self.camera.position = Vec2(width / 2, height / 2)
        self._ember_timer = 0.0
        self._rng = random.Random(0x51ACE)
        self.menu = self._build_menu()

    def _build_menu(self) -> MenuList:
        entries = [
            MenuEntry("Nueva partida", "new"),
            MenuEntry("Continuar", "continue", enabled=self.app.has_save()),
            MenuEntry("Clasificación", "scores"),
            MenuEntry("Cómo jugar", "help"),
            MenuEntry("Salir", "quit"),
        ]
        return MenuList(entries)

    def on_enter(self) -> None:
        self.menu = self._build_menu()
        self.error = ""
        self.app.input.reset()

    def handle_event(self, event: pygame.event.Event) -> None:
        action = self.menu.handle_event(event)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.app.request_quit()
            return
        if action:
            self._activate(action)

    def _activate(self, action: str) -> None:
        self.app.audio.play("ui")
        if action == "new":
            from game.scenes.play import PlayScene

            self.app.replace_scene(PlayScene(self.app))
        elif action == "continue":
            self._continue()
        elif action == "scores":
            from game.scenes.leaderboard import LeaderboardScene

            self.app.replace_scene(LeaderboardScene(self.app))
        elif action == "help":
            from game.scenes.help import HelpScene

            self.app.replace_scene(HelpScene(self.app))
        elif action == "quit":
            self.app.request_quit()

    def _continue(self) -> None:
        try:
            data = load_run(self.app.save_path)
        except SaveGameError as exc:
            self.error = str(exc)
            self.app.audio.play("denied")
            self.menu = self._build_menu()
            return
        from game.scenes.play import PlayScene

        self.app.replace_scene(PlayScene(self.app, snapshot=data.run))

    def update(self, dt: float) -> None:
        self.time += dt
        self.effects.update(dt)
        self._ember_timer -= dt
        if self._ember_timer <= 0:
            self._ember_timer = self._rng.uniform(0.05, 0.16)
            width, height = self.app.config.window.width, self.app.config.window.height
            self.effects.particles.emit(
                Vec2(self._rng.uniform(0, width), height + 8),
                (255, self._rng.randint(120, 190), 60),
                count=1,
                speed_min=18,
                speed_max=40,
                life_min=2.0,
                life_max=4.5,
                size_min=1.0,
                size_max=2.6,
                gravity=-12.0,
                drag=0.25,
                rng=self._rng,
            )

    def draw(self, surface: pygame.Surface) -> None:
        width, height = surface.get_size()
        surface.blit(self.background, (0, 0))
        surface.blit(self.glow, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        draw_anvil(surface, width // 2, height - 155, 1.15)

        title_y = 112
        draw_text(
            surface,
            self.app.fonts,
            "GAMEFORGE",
            (width // 2, title_y),
            82,
            color=palette.ACCENT,
            center=True,
            bold=True,
        )
        draw_text(
            surface,
            self.app.fonts,
            "LA FRAGUA OLVIDADA",
            (width // 2, title_y + 52),
            28,
            color=palette.TEXT,
            center=True,
        )
        draw_text(
            surface,
            self.app.fonts,
            "Un descenso, tres ascuas, una fragua.",
            (width // 2, title_y + 84),
            20,
            color=palette.TEXT_DIM,
            center=True,
        )

        self.menu.draw(surface, self.app.fonts, width // 2, 300, spacing=50)

        if self.error:
            draw_text(
                surface,
                self.app.fonts,
                self.error,
                (width // 2, 585),
                20,
                color=(255, 130, 120),
                center=True,
            )

        self.effects.draw(surface, self.camera, self.app.fonts)
        draw_text(
            surface,
            self.app.fonts,
            f"v{__version__} · Python + Pygame CE",
            (20, height - 28),
            17,
            color=palette.TEXT_DIM,
        )
        hint = "W/S o ratón para elegir · Enter para confirmar"
        hint_width = self.app.fonts.get(17).size(hint)[0]
        draw_text(
            surface,
            self.app.fonts,
            hint,
            (width - 20 - hint_width, height - 28),
            17,
            color=palette.TEXT_DIM,
        )
