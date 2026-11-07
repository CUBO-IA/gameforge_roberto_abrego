"""HUD, minimapa y paneles superpuestos."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

import pygame

from game.core.math2d import Vec2
from game.entities.items import ITEMS
from game.entities.player import Player
from game.render import palette
from game.render.fonts import FontCache
from game.render.ui import draw_bar, draw_key_hint, draw_panel, draw_text
from game.systems.inventory import Inventory
from game.systems.quest import QuestState
from game.world.tilemap import TileMap
from game.world.tiles import TileType

if TYPE_CHECKING:
    from game.render.assets import ArtLibrary

MINIMAP_SCALE = 3


class Hud:
    def __init__(
        self,
        fonts: FontCache,
        tilemap: TileMap,
        quest: QuestState,
        window_size: tuple[int, int],
        art: ArtLibrary | None = None,
    ) -> None:
        self.fonts = fonts
        self.quest = quest
        self.window_width, self.window_height = window_size
        self.tile_size = tilemap.tile_size
        self.art = art
        self.minimap = self._build_minimap(tilemap)

    def _build_minimap(self, tilemap: TileMap) -> pygame.Surface:
        scale = MINIMAP_SCALE
        surface = pygame.Surface((tilemap.width * scale, tilemap.height * scale), pygame.SRCALPHA)
        colors = {
            TileType.FLOOR: (66, 62, 88),
            TileType.WALL: (18, 18, 28),
            TileType.WATER: (34, 78, 120),
            TileType.LAVA: (140, 52, 34),
        }
        for col, row, tile in tilemap.iter_tiles():
            pygame.draw.rect(
                surface,
                colors[tile],
                pygame.Rect(col * scale, row * scale, scale, scale),
            )
        return surface

    def draw(
        self,
        surface: pygame.Surface,
        player: Player,
        inventory: Inventory,
        altar_position: Vec2,
        campfire_position: Vec2,
        floor: int,
        elapsed: float,
        score: int,
        prompt: str | None,
        toast: str,
        toast_timer: float,
        mouse_position: tuple[int, int],
        fps: float,
    ) -> None:
        panel = pygame.Rect(20, 20, 360, 104)
        draw_panel(surface, panel, art=self.art)
        draw_text(surface, self.fonts, "VIDA", (panel.x + 16, panel.y + 10), 18, palette.TEXT_DIM)
        draw_bar(
            surface,
            pygame.Rect(panel.x + 16, panel.y + 30, 220, 15),
            player.health / player.max_health,
            palette.HEALTH,
            palette.HEALTH_BACK,
            art=self.art,
        )
        draw_text(
            surface,
            self.fonts,
            f"{int(math.ceil(player.health))}/{int(player.max_health)}",
            (panel.x + 248, panel.y + 28),
            20,
            color=palette.TEXT,
        )
        shards = inventory.count("shard")
        draw_text(
            surface,
            self.fonts,
            f"Ascuas {shards}/{self.quest.shards_required}",
            (panel.x + 16, panel.y + 64),
            20,
            color=palette.ACCENT,
        )
        draw_text(
            surface,
            self.fonts,
            f"Frascos {inventory.count('potion')}",
            (panel.x + 140, panel.y + 64),
            20,
            color=(220, 140, 150),
        )
        draw_text(
            surface,
            self.fonts,
            f"Monedas {inventory.count('coin')}",
            (panel.x + 242, panel.y + 64),
            20,
            color=palette.GOLD,
        )

        # Objetivo
        objective = pygame.Rect(self.window_width - 370, 20, 350, 74)
        draw_panel(surface, objective)
        if self.quest.altar_activated:
            text = "La Fragua despierta"
            color = palette.ACCENT
        elif shards >= self.quest.shards_required:
            text = "Activa la Fragua (E)"
            color = palette.ACCENT
        else:
            text = f"Recupera fragmentos ({shards}/{self.quest.shards_required})"
            color = palette.TEXT
        draw_text(
            surface,
            self.fonts,
            text,
            (objective.centerx, objective.y + 24),
            24,
            color=color,
            center=True,
        )
        draw_text(
            surface,
            self.fonts,
            "La Fragua Olvidada",
            (objective.centerx, objective.y + 50),
            18,
            color=palette.TEXT_DIM,
            center=True,
        )

        # Piso, tiempo y FPS discretos
        minutes = int(elapsed) // 60
        seconds = int(elapsed) % 60
        draw_text(
            surface,
            self.fonts,
            (
                f"Piso {floor}   ·   {minutes:02d}:{seconds:02d}"
                f"   ·   {score} pts   ·   {fps:.0f} FPS"
            ),
            (self.window_width // 2, 24),
            19,
            color=palette.TEXT_DIM,
            center=True,
        )

        self._draw_minimap(surface, player, altar_position, campfire_position)
        self._draw_controls(surface)

        if toast and toast_timer > 0:
            alpha = min(1.0, toast_timer * 2.0)
            width = min(self.window_width - 80, 640)
            message = pygame.Surface((width, 40), pygame.SRCALPHA)
            message.fill((12, 12, 20, int(220 * alpha)))
            pygame.draw.rect(
                message,
                (*palette.ACCENT, int(180 * alpha)),
                message.get_rect(),
                width=1,
                border_radius=8,
            )
            text_color = (
                int(palette.TEXT[0] * alpha),
                int(palette.TEXT[1] * alpha),
                int(palette.TEXT[2] * alpha),
            )
            rendered = self.fonts.get(22, True).render(toast, True, text_color)
            message.blit(rendered, rendered.get_rect(center=message.get_rect().center))
            surface.blit(message, message.get_rect(midtop=(self.window_width // 2, 110)))

        if prompt:
            self._draw_prompt(surface, prompt)

        self._draw_crosshair(surface, mouse_position)

    def _draw_minimap(
        self,
        surface: pygame.Surface,
        player: Player,
        altar_position: Vec2,
        campfire_position: Vec2,
    ) -> None:
        rect = pygame.Rect(
            self.window_width - self.minimap.get_width() - 22,
            self.window_height - self.minimap.get_height() - 22,
            self.minimap.get_width(),
            self.minimap.get_height(),
        )
        draw_panel(surface, rect.inflate(12, 12), fill=(10, 10, 18, 210), radius=6)
        surface.blit(self.minimap, (rect.x, rect.y))
        pygame.draw.rect(surface, (86, 78, 110), rect, 1)
        factor = MINIMAP_SCALE / self.tile_size

        def to_minimap(world: Vec2) -> tuple[int, int]:
            return rect.x + int(world.x * factor), rect.y + int(world.y * factor)

        pygame.draw.circle(surface, palette.ACCENT, to_minimap(player.position), 3)
        for marker, color in (
            (altar_position, palette.GOLD),
            (campfire_position, palette.GREEN),
        ):
            pygame.draw.circle(surface, color, to_minimap(marker), 3, 1)

    def _draw_controls(self, surface: pygame.Surface) -> None:
        lines = [
            "WASD mover · Ratón atacar · Shift dash",
            "E interactuar · Q frasco · I inventario",
            "ESC pausa · F5 guardar",
        ]
        y = self.window_height - 78
        for index, line in enumerate(lines):
            draw_text(
                surface,
                self.fonts,
                line,
                (20, y + index * 18),
                17,
                color=palette.TEXT_DIM,
            )

    def _draw_prompt(self, surface: pygame.Surface, prompt: str) -> None:
        width = min(self.window_width - 80, 470)
        rect = pygame.Rect(0, 0, width, 52)
        rect.midbottom = (self.window_width // 2, self.window_height - 38)
        draw_panel(surface, rect, fill=(14, 12, 22, 225), art=self.art)
        draw_key_hint(surface, self.fonts, "E", prompt, (rect.x + 18, rect.y + 12))

    def _draw_crosshair(self, surface: pygame.Surface, position: tuple[int, int]) -> None:
        if self.art and self.art.ui_atlas:
            crosshair_surf = self.art.ui_atlas.surface_of("crosshair")
            if crosshair_surf:
                surface.blit(crosshair_surf, crosshair_surf.get_rect(center=position))
                return
        x, y = position
        pygame.draw.circle(surface, palette.ACCENT, (x, y), 7, 1)
        pygame.draw.line(surface, palette.ACCENT, (x - 11, y), (x - 5, y), 1)
        pygame.draw.line(surface, palette.ACCENT, (x + 5, y), (x + 11, y), 1)
        pygame.draw.line(surface, palette.ACCENT, (x, y - 11), (x, y - 5), 1)
        pygame.draw.line(surface, palette.ACCENT, (x, y + 5), (x, y + 11), 1)

    def draw_inventory(self, surface: pygame.Surface, inventory: Inventory) -> None:
        self._dim(surface)
        panel = pygame.Rect(0, 0, 620, 400)
        panel.center = (self.window_width // 2, self.window_height // 2)
        draw_panel(surface, panel, fill=(16, 15, 26, 246), art=self.art)
        draw_text(
            surface,
            self.fonts,
            "INVENTARIO",
            (panel.centerx, panel.y + 32),
            34,
            color=palette.ACCENT,
            center=True,
            bold=True,
        )
        draw_text(
            surface,
            self.fonts,
            f"{inventory.used_slots}/{inventory.capacity} ranuras",
            (panel.right - 24, panel.y + 20),
            19,
            color=palette.TEXT_DIM,
        )
        if not inventory.items():
            draw_text(
                surface,
                self.fonts,
                "Vacío. Explora los cofres.",
                (panel.centerx, panel.centery),
                26,
                color=palette.TEXT_DIM,
                center=True,
            )
        else:
            y = panel.y + 72
            for item_id, quantity in inventory.items():
                item = ITEMS[item_id]
                pygame.draw.rect(surface, item.color, pygame.Rect(panel.x + 30, y, 18, 18), border_radius=4)
                pygame.draw.rect(
                    surface, (12, 12, 20), pygame.Rect(panel.x + 30, y, 18, 18), 1, border_radius=4
                )
                draw_text(surface, self.fonts, item.name, (panel.x + 60, y - 2), 24)
                draw_text(
                    surface,
                    self.fonts,
                    f"x{quantity}",
                    (panel.right - 40, y - 2),
                    24,
                    color=palette.GOLD,
                )
                draw_text(
                    surface,
                    self.fonts,
                    item.description,
                    (panel.x + 60, y + 22),
                    17,
                    color=palette.TEXT_DIM,
                )
                y += 54
                if y > panel.bottom - 70:
                    break
        draw_text(
            surface,
            self.fonts,
            "Q usar frasco   ·   I / ESC cerrar",
            (panel.centerx, panel.bottom - 30),
            20,
            color=palette.TEXT_DIM,
            center=True,
        )

    def draw_pause(self, surface: pygame.Surface, save_hint: str) -> None:
        self._dim(surface)
        panel = pygame.Rect(0, 0, 520, 330)
        panel.center = (self.window_width // 2, self.window_height // 2)
        draw_panel(surface, panel, fill=(16, 15, 26, 246))
        draw_text(
            surface,
            self.fonts,
            "PAUSA",
            (panel.centerx, panel.y + 40),
            42,
            color=palette.ACCENT,
            center=True,
            bold=True,
        )
        lines = [
            ("ESC", "Continuar"),
            ("F5", "Guardar partida"),
            ("M", "Salir al menú (sin guardar)"),
        ]
        y = panel.y + 100
        for key, label in lines:
            draw_key_hint(surface, self.fonts, key, label, (panel.x + 90, y))
            y += 48
        if save_hint:
            draw_text(
                surface,
                self.fonts,
                save_hint,
                (panel.centerx, panel.bottom - 28),
                18,
                color=palette.GREEN,
                center=True,
            )

    def _dim(self, surface: pygame.Surface) -> None:
        overlay = pygame.Surface((self.window_width, self.window_height), pygame.SRCALPHA)
        overlay.fill((4, 4, 10, 170))
        surface.blit(overlay, (0, 0))
