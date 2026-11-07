"""Interfaz de fantasía oscura: paneles 9-slice, marcos, iconos y cursor."""

from __future__ import annotations

import math
import random

from tools.artforge import palette as pal
from tools.artforge.pixel import Canvas, darken, lighten, rgba


def _stone_fill(canvas: Canvas, rect: tuple[int, int, int, int], rng: random.Random) -> None:
    x, y, w, h = rect
    canvas.rect(x, y, w, h, (*pal.UI_FILL, 246))
    # Degradado vertical sutil con dithering
    for row in range(h):
        t = row / max(1, h - 1)
        alpha = int(14 * (1.0 - t))
        if alpha > 0:
            canvas.rect(x, y + row, w, 1, rgba((60, 54, 78), alpha))
    canvas.speckle(rng, rect, ((30, 28, 42), (20, 19, 30)), 0.05)


def _gold_border(canvas: Canvas, x: int, y: int, w: int, h: int) -> None:
    canvas.rect(x, y, w, h, (*pal.GOLD[1], 255))
    canvas.rect(x + 1, y + 1, w - 2, h - 2, (*pal.GOLD[2], 255))
    canvas.rect(x + 2, y + 2, w - 4, h - 4, (14, 13, 21, 255))
    canvas.line((x + 1, y + 1), (x + w - 2, y + 1), (*pal.GOLD[4], 220))
    canvas.line((x + 1, y + 1), (x + 1, y + h - 2), (*pal.GOLD[3], 180))


def _corner(canvas: Canvas, x: int, y: int, sx: int, sy: int) -> None:
    """Escuadra ornamentada: sx/sy indican la dirección del vértice."""
    canvas.rect(min(x, x + sx * 7), min(y, y + sy * 7), 7, 2, (*pal.GOLD[2], 255))
    canvas.rect(min(x, x + sx * 7), min(y, y + sy * 7), 2, 7, (*pal.GOLD[2], 255))
    canvas.rect(min(x, x + sx * 5), min(y, y + sy * 5), 5, 1, (*pal.GOLD[4], 200))
    canvas.rect(min(x, x + sx * 5), min(y, y + sy * 5), 1, 5, (*pal.GOLD[4], 200))
    gem_x = x + sx * 3
    gem_y = y + sy * 3
    canvas.px(gem_x, gem_y, (*pal.EMBER[3], 255))
    canvas.px(gem_x, gem_y - sy, (*pal.EMBER[2], 220))


def panel(size: int = 64, rng: random.Random | None = None) -> Canvas:
    generator = rng or random.Random(11)
    canvas = Canvas(size, size)
    canvas.rect(0, 0, size, size, (7, 7, 12, 235))
    canvas.rect(1, 1, size - 2, size - 2, (*pal.UI_FILL, 248))
    _stone_fill(canvas, (4, 4, size - 8, size - 8), generator)
    _gold_border(canvas, 2, 2, size - 4, size - 4)
    canvas.line((5, 5), (size - 6, 5), (74, 66, 92, 150))
    canvas.line((5, 5), (5, size - 6), (74, 66, 92, 130))
    _corner(canvas, 1, 1, 1, 1)
    _corner(canvas, size - 2, 1, -1, 1)
    _corner(canvas, 1, size - 2, 1, -1)
    _corner(canvas, size - 2, size - 2, -1, -1)
    return canvas


def bar_frame(width: int = 32, height: int = 18) -> Canvas:
    canvas = Canvas(width, height)
    canvas.rect(0, 0, width, height, (*pal.GOLD[0], 255))
    canvas.rect(1, 1, width - 2, height - 2, (*pal.GOLD[2], 255))
    canvas.rect(2, 2, width - 4, height - 4, (8, 8, 14, 255))
    canvas.rect(4, 4, width - 8, height - 8, (0, 0, 0, 0))
    canvas.line((1, 1), (width - 2, 1), (*pal.GOLD[4], 220))
    return canvas


def bar_fill(width: int = 32, height: int = 18) -> Canvas:
    canvas = Canvas(width, height)
    canvas.rect(0, 0, width, height, (120, 20, 26, 255))
    canvas.rect(0, 1, width, max(1, height // 2 - 2), (214, 66, 72, 255))
    canvas.rect(0, height // 2, width, max(1, height // 2 - 2), (168, 40, 46, 255))
    canvas.rect(0, height - 2, width, 2, (90, 16, 22, 255))
    for x in range(2, width - 2, 6):
        canvas.line((x, 2), (x, height - 3), (150, 34, 40, 120))
    return canvas


def slot(size: int = 24) -> Canvas:
    canvas = Canvas(size, size)
    canvas.rect(0, 0, size, size, (*pal.GOLD[0], 220))
    canvas.rect(1, 1, size - 2, size - 2, (16, 15, 24, 255))
    canvas.rect(3, 3, size - 6, size - 6, (24, 22, 34, 255))
    canvas.line((1, 1), (size - 2, 1), (*pal.GOLD[2], 230))
    canvas.line((1, 1), (1, size - 2), (*pal.GOLD[1], 200))
    canvas.line((3, size - 4), (size - 4, size - 4), (10, 10, 16, 220))
    return canvas


def button(hover: bool) -> Canvas:
    canvas = Canvas(48, 24)
    fill = (40, 34, 52) if hover else (26, 24, 36)
    canvas.rect(1, 2, 46, 20, (*lighten(fill, 10), 255))
    canvas.rect(2, 3, 44, 15, (*fill, 255))
    canvas.rect(2, 18, 44, 3, (*darken(fill, 10), 255))
    canvas.rect(1, 1, 46, 20, (*pal.GOLD[1], 255))
    canvas.rect(2, 2, 44, 18, (0, 0, 0, 0))
    canvas.line((3, 2), (44, 2), (*pal.GOLD[4], 220))
    canvas.rect(0, 21, 48, 3, (*pal.GOLD[0], 200))
    return canvas


def _icon_heart() -> Canvas:
    canvas = Canvas(16, 16)
    canvas.rect(3, 4, 4, 3, (*pal.BLOOD[3], 255))
    canvas.rect(9, 4, 4, 3, (*pal.BLOOD[3], 255))
    canvas.rect(2, 5, 12, 4, (*pal.BLOOD[3], 255))
    canvas.rect(3, 9, 10, 3, (*pal.BLOOD[2], 255))
    canvas.rect(5, 12, 6, 2, (*pal.BLOOD[2], 255))
    canvas.rect(7, 13, 2, 1, (*pal.BLOOD[1], 255))
    canvas.px(5, 5, (*pal.BLOOD[4], 255))
    canvas.px(6, 6, (*pal.BLOOD[4], 220))
    canvas.add_outline((*pal.VOID, 230))
    return canvas


def _icon_shard() -> Canvas:
    canvas = Canvas(16, 16)
    canvas.poly([(8, 1), (12, 7), (10, 14), (6, 14), (4, 7)], (*pal.EMBER[2], 255))
    canvas.poly([(8, 2), (10, 7), (8, 13), (6, 7)], (*pal.EMBER[3], 255))
    canvas.line((8, 3), (8, 12), (*pal.EMBER[5], 230))
    canvas.px(7, 8, (*pal.EMBER[5], 255))
    canvas.add_outline((*pal.VOID, 230))
    return canvas


def _icon_potion() -> Canvas:
    canvas = Canvas(16, 16)
    canvas.rect(6, 1, 4, 3, (*pal.LEATHER[2], 255))
    canvas.rect(6, 4, 4, 3, (*pal.BONE[2], 255))
    canvas.poly([(6, 6), (10, 6), (13, 12), (3, 12)], (*pal.BONE[2], 255))
    canvas.poly([(5, 8), (11, 8), (12, 12), (4, 12)], (*pal.BLOOD[3], 255))
    canvas.poly([(6, 10), (10, 10), (11, 12), (5, 12)], (*pal.BLOOD[4], 235))
    canvas.px(6, 9, (*pal.BLOOD[4], 255))
    canvas.add_outline((*pal.VOID, 230))
    return canvas


def _icon_coin() -> Canvas:
    canvas = Canvas(16, 16)
    canvas.circle(8, 8, 6, (*pal.GOLD[1], 255))
    canvas.circle(8, 8, 5, (*pal.GOLD[2], 255))
    canvas.circle(8, 8, 3, (*pal.GOLD[3], 255), 1)
    canvas.line((8, 5), (8, 11), (*pal.GOLD[4], 220))
    canvas.px(7, 6, (*pal.GOLD[4], 235))
    canvas.add_outline((*pal.VOID, 230))
    return canvas


def _icon_sword() -> Canvas:
    canvas = Canvas(16, 16)
    canvas.line((4, 12), (12, 3), (*pal.IRON[4], 255), 2)
    canvas.line((5, 12), (12, 4), (*pal.IRON[5], 220), 1)
    canvas.line((3, 11), (6, 13), (*pal.GOLD[2], 255), 1)
    canvas.line((2, 9), (5, 12), (*pal.LEATHER[2], 255), 2)
    canvas.add_outline((*pal.VOID, 220))
    return canvas


def _icon_shield() -> Canvas:
    canvas = Canvas(16, 16)
    canvas.poly([(3, 2), (13, 2), (13, 8), (8, 14), (3, 8)], (*pal.IRON[1], 255))
    canvas.poly([(4, 3), (12, 3), (12, 8), (8, 12), (4, 8)], (*pal.IRON[2], 255))
    canvas.line((8, 3), (8, 11), (*pal.IRON[4], 220))
    canvas.line((5, 6), (11, 6), (*pal.IRON[4], 200))
    canvas.add_outline((*pal.VOID, 230))
    return canvas


def _icon_skull() -> Canvas:
    canvas = Canvas(16, 16)
    canvas.ellipse(3, 2, 10, 10, (*pal.BONE[2], 255))
    canvas.rect(5, 10, 6, 3, (*pal.BONE[1], 255))
    canvas.rect(5, 5, 2, 3, (*pal.VOID, 255))
    canvas.rect(9, 5, 2, 3, (*pal.VOID, 255))
    canvas.line((7, 8), (9, 8), (*pal.BONE[0], 255))
    canvas.add_outline((*pal.VOID, 230))
    return canvas


def _icon_key() -> Canvas:
    canvas = Canvas(16, 16)
    canvas.circle(5, 5, 3, (*pal.GOLD[2], 255), 1)
    canvas.line((7, 7), (13, 13), (*pal.GOLD[2], 255), 2)
    canvas.line((11, 11), (13, 9), (*pal.GOLD[2], 255), 2)
    canvas.px(4, 4, (*pal.GOLD[4], 255))
    canvas.add_outline((*pal.VOID, 220))
    return canvas


def crosshair() -> Canvas:
    canvas = Canvas(24, 24)
    center = 12
    canvas.circle(center, center, 8, (*pal.EMBER[3], 150), 1)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        canvas.line(
            (center + dx * 4, center + dy * 4),
            (center + dx * 9, center + dy * 9),
            (*pal.EMBER[4], 220),
            1,
        )
    canvas.px(center, center, (*pal.EMBER[5], 255))
    return canvas


def divider(width: int = 64) -> Canvas:
    canvas = Canvas(width, 6)
    canvas.line((0, 2), (width - 1, 2), (*pal.GOLD[1], 200))
    canvas.line((0, 3), (width - 1, 3), (*pal.GOLD[2], 150))
    canvas.poly([(width // 2, 0), (width // 2 + 4, 3), (width // 2, 6), (width // 2 - 4, 3)], (*pal.GOLD[2], 235))
    return canvas


def build_ui() -> tuple[Canvas, dict[str, object]]:
    rng = random.Random(777)
    pieces: list[tuple[str, Canvas, list[int] | None]] = [
        ("panel", panel(64, rng), [14, 14, 14, 14]),
        ("bar_frame", bar_frame(), [6, 5, 6, 5]),
        ("bar_fill", bar_fill(), [2, 2, 2, 2]),
        ("slot", slot(), [5, 5, 5, 5]),
        ("button", button(False), [8, 8, 8, 8]),
        ("button_hover", button(True), [8, 8, 8, 8]),
        ("crosshair", crosshair(), None),
        ("divider", divider(), [6, 2, 6, 2]),
    ]
    icons = (
        ("icon_heart", _icon_heart),
        ("icon_shard", _icon_shard),
        ("icon_potion", _icon_potion),
        ("icon_coin", _icon_coin),
        ("icon_sword", _icon_sword),
        ("icon_shield", _icon_shield),
        ("icon_skull", _icon_skull),
        ("icon_key", _icon_key),
    )
    for name, factory in icons:
        pieces.append((name, factory(), None))

    # Empaquetado en rejilla de celdas de 64x64 para conservar los 9-slice.
    cell = 64
    columns = 4
    rows = (len(pieces) + columns - 1) // columns
    atlas = Canvas(columns * cell, rows * cell)
    elements: dict[str, object] = {}
    for index, (name, canvas, margins) in enumerate(pieces):
        col = index % columns
        row = index // columns
        x = col * cell + (cell - canvas.width) // 2
        y = row * cell
        atlas.blit(canvas, (x, y))
        entry: dict[str, object] = {"rect": [x, y, canvas.width, canvas.height]}
        if margins:
            entry["nine_slice"] = margins
        elements[name] = entry

    manifest: dict[str, object] = {
        "version": "gf-ui-v1",
        "image_path": "ui.png",
        "elements": elements,
    }
    return atlas, manifest
