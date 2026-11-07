"""Carga y caché de arte (tilesets, props, VFX y UI).

El juego solo consume PNG y manifiestos JSON generados por ``tools/artforge``.
Este módulo es tolerante a la ausencia de arte: devuelve ``None`` y los
renderizadores usan su camino procedural, de modo que el modo headless y las
pruebas sigan funcionando sin assets.

No es un singleton: ``Application`` crea una instancia y la comparte.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import pygame

Color = tuple[int, int, int]


@dataclass(frozen=True, slots=True)
class AtlasEntry:
    rect: pygame.Rect
    meta: dict[str, object]


class ArtAtlas:
    """Atlas RGBA con entradas nombradas y subsurface cacheada."""

    def __init__(self, image_path: Path, manifest: dict[str, object], key: str) -> None:
        raw = pygame.image.load(str(image_path))
        self.surface = raw.convert_alpha() if pygame.display.get_surface() else raw
        self.entries: dict[str, AtlasEntry] = {}
        self._sub: dict[str, pygame.Surface] = {}
        table = manifest.get(key, {})
        if not isinstance(table, dict):
            raise ValueError(f"Sección '{key}' inválida en {image_path}")
        for name, data in table.items():
            if not isinstance(data, dict) or "rect" not in data:
                continue
            rect = pygame.Rect(*(int(value) for value in data["rect"]))
            self.entries[name] = AtlasEntry(rect=rect, meta=data)

    def surface_of(self, name: str) -> pygame.Surface | None:
        cached = self._sub.get(name)
        if cached is not None:
            return cached
        entry = self.entries.get(name)
        if entry is None or not self.surface.get_rect().contains(entry.rect):
            return None
        sub = self.surface.subsurface(entry.rect).copy()
        self._sub[name] = sub
        return sub


class ArtLibrary:
    """Acceso centralizado al arte generado, con caches de tinte y 9-slice."""

    def __init__(self, root: str | Path = "assets") -> None:
        self.root = Path(root)
        self.tiles = self._load(
            "art/tiles/dungeon_tileset.json", "art/tiles/dungeon_tileset.png", "tiles"
        )
        self.objects = self._load("art/objects/objects.json", "art/objects/objects.png", "objects")
        self.particles = self._load("art/vfx/particles.json", "art/vfx/particles.png", "sprites")
        self.ui_atlas = self._load("art/ui/ui.json", "art/ui/ui.png", "elements")
        self.tile_size = int(
            self.tiles.entries and self._tileset_tile_size()
        ) if self.tiles else 0
        self._tinted: dict[tuple[str, Color], pygame.Surface] = {}
        self._nine: dict[tuple[str, int, int], pygame.Surface] = {}
        self._scaled: dict[tuple[str, int, int], pygame.Surface] = {}

    # ------------------------------------------------------------------ carga

    def _load(self, manifest_rel: str, image_rel: str, key: str) -> ArtAtlas | None:
        manifest_path = self.root / manifest_rel
        if not manifest_path.is_file():
            return None
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None
        image_path = manifest_path.parent / str(manifest.get("image_path", Path(image_rel).name))
        if not image_path.is_file():
            return None
        try:
            return ArtAtlas(image_path, manifest, key)
        except (pygame.error, ValueError):
            return None

    def _tileset_tile_size(self) -> int:
        if self.tiles is None:
            return 0
        entry = next(iter(self.tiles.entries.values()), None)
        return entry.rect.width if entry else 32

    @property
    def available(self) -> bool:
        return self.tiles is not None

    # ---------------------------------------------------------------- tiles

    def tile(self, name: str) -> pygame.Surface | None:
        return self.tiles.surface_of(name) if self.tiles else None

    def object_sprite(self, name: str) -> pygame.Surface | None:
        return self.objects.surface_of(name) if self.objects else None

    def particle_sprite(self, name: str, color: Color | None = None) -> pygame.Surface | None:
        if self.particles is None:
            return None
        base = self.particles.surface_of(name)
        if base is None:
            return None
        if color is None:
            return base
        key = (name, color)
        cached = self._tinted.get(key)
        if cached is not None:
            return cached
        tinted = base.copy()
        tinted.fill((*color, 255), special_flags=pygame.BLEND_RGBA_MULT)
        self._tinted[key] = tinted
        return tinted

    # ------------------------------------------------------------------- ui

    def ui(self, name: str) -> tuple[pygame.Surface, list[int] | None] | None:
        if self.ui_atlas is None:
            return None
        surface = self.ui_atlas.surface_of(name)
        entry = self.ui_atlas.entries.get(name)
        if surface is None or entry is None:
            return None
        margins = entry.meta.get("nine_slice")
        return surface, list(margins) if isinstance(margins, list) else None  # type: ignore[arg-type]

    def nine_slice(self, name: str, size: tuple[int, int]) -> pygame.Surface | None:
        """Escala un 9-slice al tamaño pedido, cacheando el resultado."""
        width, height = int(size[0]), int(size[1])
        if width <= 0 or height <= 0:
            return None
        key = (name, width, height)
        cached = self._nine.get(key)
        if cached is not None:
            return cached
        entry = self.ui(name)
        if entry is None:
            return None
        source, margins = entry
        if not margins:
            out = pygame.transform.scale(source, (width, height))
            self._nine[key] = out
            return out
        left, top, right, bottom = margins
        left = min(left, width // 2)
        right = min(right, width - left)
        top = min(top, height // 2)
        bottom = min(bottom, height - top)
        source_w, source_h = source.get_size()
        middle_w = max(0, width - left - right)
        middle_h = max(0, height - top - bottom)
        source_middle_w = max(0, source_w - margins[0] - margins[2])
        source_middle_h = max(0, source_h - margins[1] - margins[3])

        out = pygame.Surface((width, height), pygame.SRCALPHA)

        def piece(
            source_rect: pygame.Rect, dest_rect: pygame.Rect
        ) -> None:
            if dest_rect.width <= 0 or dest_rect.height <= 0:
                return
            if source_rect.width <= 0 or source_rect.height <= 0:
                return
            if source_rect.size == dest_rect.size:
                out.blit(source, dest_rect.topleft, source_rect)
            else:
                out.blit(
                    pygame.transform.scale(source.subsurface(source_rect), dest_rect.size),
                    dest_rect.topleft,
                )

        sw, sh = source_w, source_h
        # Esquinas
        piece(pygame.Rect(0, 0, margins[0], margins[1]), pygame.Rect(0, 0, left, top))
        piece(pygame.Rect(sw - margins[2], 0, margins[2], margins[1]), pygame.Rect(width - right, 0, right, top))
        piece(pygame.Rect(0, sh - margins[3], margins[0], margins[3]), pygame.Rect(0, height - bottom, left, bottom))
        piece(
            pygame.Rect(sw - margins[2], sh - margins[3], margins[2], margins[3]),
            pygame.Rect(width - right, height - bottom, right, bottom),
        )
        # Bordes
        piece(
            pygame.Rect(margins[0], 0, source_middle_w, margins[1]),
            pygame.Rect(left, 0, middle_w, top),
        )
        piece(
            pygame.Rect(margins[0], sh - margins[3], source_middle_w, margins[3]),
            pygame.Rect(left, height - bottom, middle_w, bottom),
        )
        piece(
            pygame.Rect(0, margins[1], margins[0], source_middle_h),
            pygame.Rect(0, top, left, middle_h),
        )
        piece(
            pygame.Rect(sw - margins[2], margins[1], margins[2], source_middle_h),
            pygame.Rect(width - right, top, right, middle_h),
        )
        # Centro
        piece(
            pygame.Rect(margins[0], margins[1], source_middle_w, source_middle_h),
            pygame.Rect(left, top, middle_w, middle_h),
        )
        self._nine[key] = out
        return out

    def scaled(self, surface: pygame.Surface, name: str, size: tuple[int, int]) -> pygame.Surface:
        key = (name, int(size[0]), int(size[1]))
        cached = self._scaled.get(key)
        if cached is None:
            cached = pygame.transform.scale(surface, (max(1, int(size[0])), max(1, int(size[1]))))
            self._scaled[key] = cached
        return cached
