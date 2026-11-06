"""Clasificación local leída de SQLite."""

from __future__ import annotations

import pygame

from game.render import palette
from game.render.background import vertical_gradient
from game.render.ui import MenuEntry, MenuList, draw_panel, draw_text
from game.scenes.base import Scene


class LeaderboardScene(Scene):
    def __init__(self, app) -> None:
        super().__init__(app)
        width, height = app.config.window.width, app.config.window.height
        self.background = vertical_gradient((width, height), (10, 9, 18), (16, 18, 32))
        self.menu = MenuList([MenuEntry("Volver al menú", "back")])
        self.entries = []
        self.error = ""
        self._load()

    def _load(self) -> None:
        entries, error = self.app.top_scores(10)
        self.entries = entries or []
        self.error = error or ""

    def handle_event(self, event: pygame.event.Event) -> None:
        action = self.menu.handle_event(event)
        if action == "back" or (
            event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE)
        ):
            self._back()

    def _back(self) -> None:
        from game.scenes.menu import MenuScene

        self.app.audio.play("ui")
        self.app.replace_scene(MenuScene(self.app))

    def draw(self, surface: pygame.Surface) -> None:
        width, height = surface.get_size()
        surface.blit(self.background, (0, 0))
        draw_text(
            surface,
            self.app.fonts,
            "CLASIFICACIÓN",
            (width // 2, 54),
            48,
            color=palette.ACCENT,
            center=True,
            bold=True,
        )
        draw_text(
            surface,
            self.app.fonts,
            "Las mejores incursiones en la Fragua",
            (width // 2, 92),
            20,
            color=palette.TEXT_DIM,
            center=True,
        )

        panel = pygame.Rect(0, 0, 980, 470)
        panel.center = (width // 2, height // 2 + 10)
        draw_panel(surface, panel, fill=(16, 15, 26, 240))

        headers = [
            ("#", panel.x + 32),
            ("PUNTOS", panel.x + 92),
            ("RESULTADO", panel.x + 240),
            ("PISO", panel.x + 400),
            ("BAJAS", panel.x + 490),
            ("TIEMPO", panel.x + 610),
            ("FECHA", panel.x + 730),
        ]
        for label, x in headers:
            draw_text(surface, self.app.fonts, label, (x, panel.y + 24), 18, color=palette.TEXT_DIM)

        if self.error:
            draw_text(
                surface,
                self.app.fonts,
                self.error,
                (panel.centerx, panel.centery),
                22,
                color=(255, 130, 120),
                center=True,
            )
        elif not self.entries:
            draw_text(
                surface,
                self.app.fonts,
                "Todavía no hay partidas registradas. La Fragua espera.",
                (panel.centerx, panel.centery),
                24,
                color=palette.TEXT_DIM,
                center=True,
            )
        else:
            y = panel.y + 62
            for index, entry in enumerate(self.entries, start=1):
                if index % 2 == 0:
                    pygame.draw.rect(
                        surface,
                        (24, 22, 36),
                        pygame.Rect(panel.x + 16, y - 6, panel.width - 32, 36),
                        border_radius=4,
                    )
                minutes, seconds = divmod(int(entry.duration), 60)
                values = [
                    (f"{index:02d}", panel.x + 32, palette.TEXT_DIM),
                    (f"{entry.score:,}", panel.x + 92, palette.GOLD),
                    ("Victoria" if entry.victory else "Derrota", panel.x + 240, palette.GREEN if entry.victory else (200, 110, 110)),
                    (str(entry.floor), panel.x + 400, palette.TEXT),
                    (str(entry.kills), panel.x + 490, palette.TEXT),
                    (f"{minutes:02d}:{seconds:02d}", panel.x + 610, palette.TEXT),
                    (entry.created_at[:10], panel.x + 730, palette.TEXT_DIM),
                ]
                for value, x, color in values:
                    draw_text(surface, self.app.fonts, value, (x, y), 21, color=color)
                y += 40

        self.menu.draw(surface, self.app.fonts, width // 2, height - 72, spacing=44, width=260)
