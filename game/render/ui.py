"""Primitivas de UI compartidas por escenas."""

from __future__ import annotations

from dataclasses import dataclass

import pygame

from game.render import palette
from game.render.fonts import FontCache


def draw_text(
    surface: pygame.Surface,
    fonts: FontCache,
    text: str,
    position: tuple[int, int],
    size: int = 24,
    color: palette.Color = palette.TEXT,
    bold: bool = False,
    center: bool = False,
    shadow: bool = True,
) -> pygame.Rect:
    font = fonts.get(size, bold)
    image = font.render(text, True, color)
    rect = image.get_rect()
    if center:
        rect.center = position
    else:
        rect.topleft = position
    if shadow:
        shadow_image = font.render(text, True, (0, 0, 0))
        surface.blit(shadow_image, rect.move(2, 2))
    surface.blit(image, rect)
    return rect


def draw_panel(
    surface: pygame.Surface,
    rect: pygame.Rect,
    fill: palette.RGBA = (18, 18, 30, 235),
    border: palette.Color = (92, 82, 118),
    radius: int = 10,
) -> None:
    panel = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(panel, fill, panel.get_rect(), border_radius=radius)
    pygame.draw.rect(panel, border, panel.get_rect(), width=2, border_radius=radius)
    surface.blit(panel, rect.topleft)


def draw_bar(
    surface: pygame.Surface,
    rect: pygame.Rect,
    fraction: float,
    color: palette.Color,
    background: palette.Color,
    border: palette.Color = (12, 12, 20),
) -> None:
    fraction = max(0.0, min(1.0, fraction))
    pygame.draw.rect(surface, border, rect.inflate(4, 4), border_radius=5)
    pygame.draw.rect(surface, background, rect, border_radius=4)
    if fraction > 0:
        fill = rect.copy()
        fill.width = max(1, int(rect.width * fraction))
        pygame.draw.rect(surface, color, fill, border_radius=4)
        highlight = fill.inflate(-2, -2)
        if highlight.width > 0 and highlight.height > 0:
            pygame.draw.rect(
                surface, _lighten(color, 35), highlight, width=1, border_radius=3
            )


def draw_key_hint(
    surface: pygame.Surface,
    fonts: FontCache,
    key: str,
    label: str,
    position: tuple[int, int],
) -> None:
    x, y = position
    font = fonts.get(20)
    key_width = max(30, font.size(key)[0] + 14)
    key_rect = pygame.Rect(x, y, key_width, 28)
    pygame.draw.rect(surface, (32, 32, 48), key_rect, border_radius=5)
    pygame.draw.rect(surface, (104, 94, 132), key_rect, width=1, border_radius=5)
    draw_text(
        surface,
        fonts,
        key,
        (key_rect.centerx, key_rect.centery),
        20,
        center=True,
        shadow=False,
    )
    draw_text(surface, fonts, label, (key_rect.right + 10, y + 4), 21, color=palette.TEXT_DIM)


def _lighten(color: palette.Color, amount: int) -> palette.Color:
    return (
        min(255, color[0] + amount),
        min(255, color[1] + amount),
        min(255, color[2] + amount),
    )


@dataclass(slots=True)
class MenuEntry:
    label: str
    action: str
    enabled: bool = True
    rect: pygame.Rect | None = None


class MenuList:
    """Lista de opciones con teclado y ratón.

    Los rects se calculan al dibujar; el manejo de eventos usa el último layout,
    que existe desde el primer frame visible.
    """

    def __init__(self, entries: list[MenuEntry]) -> None:
        self.entries = entries
        self.selected = next(
            (index for index, entry in enumerate(entries) if entry.enabled), 0
        )

    def move(self, direction: int) -> None:
        if not self.entries:
            return
        for _ in range(len(self.entries)):
            self.selected = (self.selected + direction) % len(self.entries)
            if self.entries[self.selected].enabled:
                break

    def activate(self) -> str | None:
        if not self.entries:
            return None
        entry = self.entries[self.selected]
        return entry.action if entry.enabled else None

    def handle_event(self, event: pygame.event.Event) -> str | None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.move(-1)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.move(1)
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                return self.activate()
        elif event.type == pygame.MOUSEMOTION:
            for index, entry in enumerate(self.entries):
                if entry.rect is not None and entry.rect.collidepoint(event.pos):
                    if entry.enabled:
                        self.selected = index
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for index, entry in enumerate(self.entries):
                if entry.rect is not None and entry.rect.collidepoint(event.pos):
                    if entry.enabled:
                        self.selected = index
                        return entry.action
        return None

    def draw(
        self,
        surface: pygame.Surface,
        fonts: FontCache,
        center_x: int,
        top_y: int,
        spacing: int = 52,
        width: int = 360,
    ) -> None:
        for index, entry in enumerate(self.entries):
            rect = pygame.Rect(0, 0, width, 42)
            rect.centerx = center_x
            rect.top = top_y + index * spacing
            entry.rect = rect
            selected = index == self.selected and entry.enabled
            if selected:
                pygame.draw.rect(surface, (42, 34, 52), rect, border_radius=8)
                pygame.draw.rect(surface, palette.ACCENT, rect, width=2, border_radius=8)
            color = palette.TEXT if entry.enabled else palette.TEXT_DIM
            prefix = "> " if selected else "  "
            draw_text(
                surface,
                fonts,
                prefix + entry.label,
                (rect.centerx, rect.centery),
                28,
                color=color,
                center=True,
            )
