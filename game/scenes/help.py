"""Pantalla de ayuda y controles."""

from __future__ import annotations

import pygame

from game.render import palette
from game.render.background import vertical_gradient
from game.render.ui import MenuEntry, MenuList, draw_panel, draw_text
from game.scenes.base import Scene


class HelpScene(Scene):
    def __init__(self, app) -> None:
        super().__init__(app)
        width, height = app.config.window.width, app.config.window.height
        self.background = vertical_gradient((width, height), (10, 9, 18), (20, 16, 30))
        self.menu = MenuList([MenuEntry("Volver", "back")])
        self.lines = [
            ("WASD / flechas", "Moverse"),
            ("Ratón", "Apuntar"),
            ("Clic izquierdo / J / Espacio", "Atacar con la espada"),
            ("Shift / K", "Dash con invulnerabilidad breve"),
            ("E", "Interactuar con cofres, hoguera y altar"),
            ("Q", "Beber un frasco de brasa"),
            ("I", "Abrir el inventario"),
            ("F5", "Guardar la partida"),
            ("ESC", "Pausa / volver"),
        ]

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
            "CÓMO JUGAR",
            (width // 2, 56),
            48,
            color=palette.ACCENT,
            center=True,
            bold=True,
        )

        panel = pygame.Rect(0, 0, 900, 430)
        panel.center = (width // 2, height // 2 - 10)
        draw_panel(surface, panel, fill=(16, 15, 26, 240))
        draw_text(
            surface,
            self.app.fonts,
            "Recupera 3 fragmentos de ascua de los cofres y activa la Fragua del fondo de la mazmorra.",
            (panel.centerx, panel.y + 34),
            23,
            color=palette.TEXT,
            center=True,
        )
        draw_text(
            surface,
            self.app.fonts,
            "Los enemigos dañan al tocarte. La lava quema. El agua frena. Descansa en la hoguera para curarte y guardar.",
            (panel.centerx, panel.y + 62),
            19,
            color=palette.TEXT_DIM,
            center=True,
        )

        y = panel.y + 100
        for key, action in self.lines:
            draw_text(surface, self.app.fonts, key, (panel.x + 80, y), 22, color=palette.ACCENT)
            draw_text(surface, self.app.fonts, action, (panel.x + 390, y), 22)
            y += 33

        draw_text(
            surface,
            self.app.fonts,
            "Consejo: el dash atraviesa el peligro sin recibir daño. Los proyectiles de los fuegos fatuos se esquivan.",
            (width // 2, panel.bottom + 34),
            19,
            color=palette.TEXT_DIM,
            center=True,
        )
        self.menu.draw(surface, self.app.fonts, width // 2, height - 84, spacing=44, width=220)
