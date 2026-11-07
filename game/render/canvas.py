"""Lienzo virtual escalable (Virtual Canvas).

Desacopla la resolución lógica interna de diseño (fija en 1280x720) de la
resolución física de la ventana del sistema operativo. Gestiona el escalado
con preservación de relación de aspecto (letterbox/pillarbox) y el mapeo
inverso de coordenadas del ratón.
"""

from __future__ import annotations

import pygame


def calculate_letterbox(
    window_width: int,
    window_height: int,
    logical_width: int,
    logical_height: int,
) -> tuple[int, int, int, int, float]:
    """Calcula el viewport escalado y centrado (offset_x, offset_y, width, height, scale)."""
    if window_width <= 0 or window_height <= 0:
        raise ValueError("Las dimensiones de ventana deben ser positivas.")
    if logical_width <= 0 or logical_height <= 0:
        raise ValueError("Las dimensiones lógicas deben ser positivas.")

    scale = min(window_width / logical_width, window_height / logical_height)
    scaled_w = max(1, int(round(logical_width * scale)))
    scaled_h = max(1, int(round(logical_height * scale)))
    offset_x = (window_width - scaled_w) // 2
    offset_y = (window_height - scaled_h) // 2

    return offset_x, offset_y, scaled_w, scaled_h, scale


def screen_to_logical(
    physical_x: float,
    physical_y: float,
    offset_x: int,
    offset_y: int,
    scale: float,
    logical_width: int,
    logical_height: int,
) -> tuple[int, int] | None:
    """Transforma coordenadas físicas de la ventana a coordenadas lógicas del canvas."""
    if scale <= 1e-9:
        return None

    rel_x = physical_x - offset_x
    rel_y = physical_y - offset_y

    log_x = int(rel_x / scale)
    log_y = int(rel_y / scale)

    # Clamping dentro de los límites del canvas lógico
    clamped_x = max(0, min(logical_width - 1, log_x))
    clamped_y = max(0, min(logical_height - 1, log_y))

    return clamped_x, clamped_y


class VirtualCanvas:
    """Manejador de renderizado sobre superficie lógica con escalado."""

    def __init__(
        self,
        logical_width: int = 1280,
        logical_height: int = 720,
        initial_window_size: tuple[int, int] | None = None,
    ) -> None:
        self.logical_width = logical_width
        self.logical_height = logical_height
        self.surface = pygame.Surface((logical_width, logical_height))

        win_w = initial_window_size[0] if initial_window_size else logical_width
        win_h = initial_window_size[1] if initial_window_size else logical_height
        self.offset_x, self.offset_y, self.scaled_w, self.scaled_h, self.scale = (
            calculate_letterbox(win_w, win_h, logical_width, logical_height)
        )

    def resize_window(self, width: int, height: int) -> None:
        """Actualiza las dimensiones físicas de la ventana."""
        self.offset_x, self.offset_y, self.scaled_w, self.scaled_h, self.scale = (
            calculate_letterbox(width, height, self.logical_width, self.logical_height)
        )

    def map_mouse(self, physical_x: float, physical_y: float) -> tuple[int, int] | None:
        """Traduce la posición del ratón de la ventana a la resolución lógica."""
        return screen_to_logical(
            physical_x,
            physical_y,
            self.offset_x,
            self.offset_y,
            self.scale,
            self.logical_width,
            self.logical_height,
        )

    def render_to_display(self, display_surface: pygame.Surface) -> None:
        """Escala la superficie lógica y la presenta con letterboxing en la pantalla."""
        display_surface.fill((0, 0, 0))
        if self.scaled_w == self.logical_width and self.scaled_h == self.logical_height:
            display_surface.blit(self.surface, (self.offset_x, self.offset_y))
        else:
            scaled = pygame.transform.scale(self.surface, (self.scaled_w, self.scaled_h))
            display_surface.blit(scaled, (self.offset_x, self.offset_y))
