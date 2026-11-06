"""Contrato de escena."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from game.app import Application


class Scene:
    def __init__(self, app: "Application") -> None:
        self.app = app

    def on_enter(self) -> None:
        """Se llama al pasar a ser la escena activa."""

    def on_exit(self) -> None:
        """Se llama al abandonar la escena."""

    def handle_event(self, event: pygame.event.Event) -> None:
        """Procesa un evento de pygame."""

    def update(self, dt: float) -> None:
        """Avanza la simulación. dt ya está limitado por la aplicación."""

    def draw(self, surface: pygame.Surface) -> None:
        """Dibuja el estado actual."""
