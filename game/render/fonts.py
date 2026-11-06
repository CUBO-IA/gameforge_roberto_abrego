"""Caché de fuentes. La fuente por defecto de pygame evita assets externos."""

from __future__ import annotations

import pygame


class FontCache:
    def __init__(self) -> None:
        self._cache: dict[tuple[int, bool], pygame.font.Font] = {}

    def get(self, size: int, bold: bool = False) -> pygame.font.Font:
        key = (int(size), bold)
        font = self._cache.get(key)
        if font is None:
            font = pygame.font.Font(None, key[0])
            font.set_bold(bold)
            self._cache[key] = font
        return font

    def clear(self) -> None:
        self._cache.clear()
