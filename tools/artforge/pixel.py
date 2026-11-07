"""Rasterizado pixel-art 1x para el pipeline de arte de GameForge.

Todo el arte de GameForge se produce aquí, en tiempo de desarrollo, con
operaciones de píxel deterministas. El juego solo carga PNG ya generados:
no importa nada de este paquete en tiempo de ejecución.

El objetivo es arte nítido de 1x (sin antialiasing) con contorno oscuro
unificado, rampas de color cortas y variación controlada, que es lo que hace
legible un sprite de 32-48 px sobre un fondo oscuro.
"""

from __future__ import annotations

import math
import random

import pygame

Color = tuple[int, int, int]
RGBA = tuple[int, int, int, int]


# --------------------------------------------------------------------- color


def _c(value: float) -> int:
    return max(0, min(255, int(round(value))))


def mix(a: Color, b: Color, t: float) -> Color:
    """Interpola linealmente entre dos colores RGB."""
    t = max(0.0, min(1.0, t))
    return (_c(a[0] + (b[0] - a[0]) * t), _c(a[1] + (b[1] - a[1]) * t), _c(a[2] + (b[2] - a[2]) * t))


def lighten(color: Color, amount: float) -> Color:
    return (_c(color[0] + amount), _c(color[1] + amount), _c(color[2] + amount))


def darken(color: Color, amount: float) -> Color:
    return (_c(color[0] - amount), _c(color[1] - amount), _c(color[2] - amount))


def scale(color: Color, factor: float) -> Color:
    return (_c(color[0] * factor), _c(color[1] * factor), _c(color[2] * factor))


def rgba(color: Color, alpha: int) -> RGBA:
    return (color[0], color[1], color[2], max(0, min(255, int(alpha))))


def ramp(colors: tuple[Color, ...], t: float) -> Color:
    """Muestrea una rampa de color con t en [0, 1]."""
    if len(colors) == 1:
        return colors[0]
    t = max(0.0, min(1.0, t)) * (len(colors) - 1)
    index = int(t)
    if index >= len(colors) - 1:
        return colors[-1]
    return mix(colors[index], colors[index + 1], t - index)


# -------------------------------------------------------------------- canvas


class Canvas:
    """Superficie de dibujo con utilidades de pixel art."""

    __slots__ = ("surface", "width", "height")

    def __init__(self, width: int, height: int, fill: RGBA = (0, 0, 0, 0)) -> None:
        self.width = int(width)
        self.height = int(height)
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        if fill[3] > 0:
            self.surface.fill(fill)

    # -- píxeles

    def px(self, x: float, y: float, color: RGBA | Color) -> None:
        xi, yi = int(x), int(y)
        if 0 <= xi < self.width and 0 <= yi < self.height:
            self.surface.set_at((xi, yi), color)

    def get(self, x: int, y: int) -> RGBA:
        return self.surface.get_at((x, y))

    def alpha(self, x: int, y: int) -> int:
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.surface.get_at((x, y))[3]
        return 0

    # -- formas

    def fill(self, color: RGBA | Color) -> None:
        self.surface.fill(color)

    def rect(self, x: int, y: int, w: int, h: int, color: RGBA | Color) -> None:
        if w <= 0 or h <= 0:
            return
        self.surface.fill(color, pygame.Rect(x, y, w, h))

    def poly(self, points: list[tuple[float, float]], color: RGBA | Color) -> None:
        if len(points) < 3:
            return
        pygame.draw.polygon(self.surface, color, [(int(x), int(y)) for x, y in points])

    def line(
        self,
        start: tuple[float, float],
        end: tuple[float, float],
        color: RGBA | Color,
        width: int = 1,
    ) -> None:
        pygame.draw.line(
            self.surface,
            color,
            (int(start[0]), int(start[1])),
            (int(end[0]), int(end[1])),
            max(1, width),
        )

    def circle(self, x: float, y: float, radius: float, color: RGBA | Color, width: int = 0) -> None:
        if radius <= 0:
            return
        pygame.draw.circle(self.surface, color, (int(x), int(y)), int(radius), width)

    def ellipse(
        self, x: int, y: int, w: int, h: int, color: RGBA | Color, width: int = 0
    ) -> None:
        if w <= 0 or h <= 0:
            return
        pygame.draw.ellipse(self.surface, color, pygame.Rect(x, y, w, h), width)

    # -- patrones

    def speckle(
        self,
        rng: random.Random,
        bounds: tuple[int, int, int, int],
        colors: tuple[Color, ...],
        density: float,
    ) -> None:
        """Ruido de píxeles sueltos, sin alfa: útil para piedra y tela."""
        x, y, w, h = bounds
        total = max(0, int(w * h * density))
        for _ in range(total):
            px = x + rng.randrange(w)
            py = y + rng.randrange(h)
            self.px(px, py, rng.choice(colors))

    def dither(
        self,
        bounds: tuple[int, int, int, int],
        color: Color,
        alpha_low: int,
        alpha_high: int,
        direction: str = "vertical",
    ) -> None:
        """Bayer 2x2 con alfa, para degradados suaves sin bandas."""
        x, y, w, h = bounds
        pattern = ((0, 2), (3, 1))
        for py in range(h):
            for px in range(w):
                t = (py / max(1, h - 1)) if direction == "vertical" else (px / max(1, w - 1))
                threshold = pattern[(y + py) % 2][(x + px) % 2] / 4.0
                alpha = alpha_low + (alpha_high - alpha_low) * t
                if threshold <= (alpha / 255.0):
                    self.px(x + px, y + py, rgba(color, 255))

    def bevel_rect(
        self,
        x: int,
        y: int,
        w: int,
        h: int,
        base: Color,
        light: Color,
        dark: Color,
        inset: int = 0,
    ) -> None:
        """Rectángulo con bisel de 1 px: luz arriba/izquierda, sombra abajo/derecha."""
        self.rect(x, y, w, h, base)
        if w > 2 and h > 2:
            self.line((x, y), (x + w - 1, y), light)
            self.line((x, y), (x, y + h - 1), light)
            self.line((x, y + h - 1), (x + w - 1, y + h - 1), dark)
            self.line((x + w - 1, y), (x + w - 1, y + h - 1), dark)
        if inset:
            self.line((x + 1, y + 1), (x + w - 2, y + 1), mix(light, base, 0.5))
            self.line((x + 1, y + 1), (x + 1, y + h - 2), mix(light, base, 0.5))

    # -- contorno y composición

    def add_outline(self, color: RGBA = (9, 9, 15, 255)) -> None:
        """Añade un contorno de 1 px por fuera de la silueta actual."""
        mask = pygame.mask.from_surface(self.surface, 12)
        solid = mask.to_surface(setcolor=color, unsetcolor=(0, 0, 0, 0))
        ring = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ring.blit(solid, (dx, dy))
        inside = mask.to_surface(setcolor=(255, 255, 255, 255), unsetcolor=(0, 0, 0, 0))
        ring.blit(inside, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
        self.surface.blit(ring)

    def blit(self, other: Canvas | pygame.Surface, position: tuple[int, int]) -> None:
        source = other.surface if isinstance(other, Canvas) else other
        self.surface.blit(source, position)

    def blit_alpha(self, other: Canvas | pygame.Surface, position: tuple[int, int], alpha: int) -> None:
        source = other.surface if isinstance(other, Canvas) else other
        layer = source.copy()
        layer.set_alpha(alpha)
        self.surface.blit(layer, position)

    def copy(self) -> Canvas:
        clone = Canvas(self.width, self.height)
        clone.surface.blit(self.surface, (0, 0))
        return clone

    def flip(self, horizontal: bool = True, vertical: bool = False) -> Canvas:
        clone = Canvas(self.width, self.height)
        clone.surface = pygame.transform.flip(self.surface, horizontal, vertical)
        return clone

    def tinted(self, color: Color) -> Canvas:
        """Copia teñida conservando el canal alfa (para flashes de daño)."""
        clone = Canvas(self.width, self.height)
        clone.surface = self.surface.copy()
        mask = pygame.mask.from_surface(self.surface, 12)
        layer = mask.to_surface(setcolor=(*color, 255), unsetcolor=(0, 0, 0, 0))
        clone.surface.blit(layer, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        return clone

    def save(self, path: str) -> None:
        pygame.image.save(self.surface, path)


# ------------------------------------------------------------------ utilidades


def ellipse_points(cx: float, cy: float, rx: float, ry: float, steps: int = 18) -> list[tuple[float, float]]:
    return [
        (cx + math.cos(math.tau * i / steps) * rx, cy + math.sin(math.tau * i / steps) * ry)
        for i in range(steps)
    ]


def blob_points(
    cx: float,
    cy: float,
    rx: float,
    ry: float,
    rng: random.Random,
    jitter: float = 0.08,
    steps: int = 20,
) -> list[tuple[float, float]]:
    """Silueta orgánica: elipse con jitter radial estable."""
    points = []
    for i in range(steps):
        angle = math.tau * i / steps
        wobble = 1.0 + rng.uniform(-jitter, jitter)
        points.append((cx + math.cos(angle) * rx * wobble, cy + math.sin(angle) * ry * wobble))
    return points


def contact_sheet(
    frames: list[tuple[str, Canvas]],
    path: str,
    scale: int = 4,
    columns: int = 8,
    background: Color = (26, 24, 34),
) -> None:
    """Monta una hoja de contacto ampliada para inspección visual del arte."""
    if not frames:
        return
    font = pygame.font.Font(None, 14)
    cell_w = max(canvas.width for _, canvas in frames) * scale + 12
    cell_h = max(canvas.height for _, canvas in frames) * scale + 24
    rows = (len(frames) + columns - 1) // columns
    sheet = Canvas(cell_w * columns, cell_h * rows, (*background, 255))
    for index, (label, canvas) in enumerate(frames):
        col = index % columns
        row = index // columns
        scaled = pygame.transform.scale(
            canvas.surface, (canvas.width * scale, canvas.height * scale)
        )
        x = col * cell_w + (cell_w - scaled.get_width()) // 2
        y = row * cell_h + 4
        sheet.surface.blit(scaled, (x, y))
        text = font.render(label, True, (206, 198, 214))
        sheet.surface.blit(
            text, (col * cell_w + (cell_w - text.get_width()) // 2, y + scaled.get_height() + 3)
        )
    sheet.save(path)
