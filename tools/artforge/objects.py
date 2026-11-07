"""Objetos del mundo: cofre, hoguera, altar de la forja y ascuas."""

from __future__ import annotations

import math
import random

from tools.artforge import palette as pal
from tools.artforge.pixel import Canvas, darken, lighten, ramp, rgba


def _pack(
    pieces: list[tuple[str, Canvas]], width: int = 256, padding: int = 2
) -> tuple[Canvas, dict[str, dict[str, object]]]:
    """Empaqueta piezas por filas con relleno, devolviendo atlas y manifiesto."""
    rows: list[list[tuple[str, Canvas]]] = []
    current: list[tuple[str, Canvas]] = []
    used = padding
    for piece in pieces:
        if used + piece[1].width + padding > width:
            rows.append(current)
            current = []
            used = padding
        current.append(piece)
        used += piece[1].width + padding
    if current:
        rows.append(current)

    row_heights = [max(canvas.height for _, canvas in row) for row in rows]
    atlas = Canvas(width, sum(row_heights) + padding * (len(rows) + 1))
    manifest: dict[str, dict[str, object]] = {}
    y = padding
    for row, height in zip(rows, row_heights):
        x = padding
        for name, canvas in row:
            atlas.blit(canvas, (x, y + height - canvas.height))
            manifest[name] = {"rect": [x, y + height - canvas.height, canvas.width, canvas.height]}
            x += canvas.width + padding
        y += height + padding
    return atlas, manifest


def chest(opened: bool) -> Canvas:
    canvas = Canvas(32, 32)
    # Sombra de contacto
    canvas.ellipse(2, 24, 28, 7, (10, 8, 12, 150))
    body = (3, 13, 26, 15)
    canvas.rect(*body, (*pal.WOOD[2], 255))
    canvas.rect(3, 13, 26, 2, (*pal.WOOD[4], 255))
    for x in (8, 15, 22):
        canvas.line((x, 14), (x, 27), (*pal.WOOD[1], 220))
    for y in (17, 22):
        canvas.rect(3, y, 26, 3, (*pal.IRON[1], 255))
        canvas.line((3, y), (28, y), (*pal.IRON[3], 255))
        canvas.line((3, y + 2), (28, y + 2), (*pal.IRON[0], 255))
    canvas.line((28, 14), (28, 27), (*pal.IRON[0], 220))
    if opened:
        # Tapa abierta hacia atrás
        canvas.poly([(4, 3), (28, 3), (27, 10), (5, 10)], (*pal.WOOD[1], 255))
        canvas.poly([(5, 4), (27, 4), (26, 8), (6, 8)], (*pal.WOOD[3], 255))
        canvas.rect(4, 9, 24, 3, (*pal.IRON[1], 255))
        # Interior con brasas y monedas
        canvas.rect(6, 12, 20, 4, (16, 10, 8, 255))
        canvas.ellipse(8, 12, 16, 4, (*pal.EMBER[2], 210))
        canvas.ellipse(11, 12, 10, 2, (*pal.EMBER[4], 235))
        for x in (10, 14, 18, 22):
            canvas.px(x, 12, (*pal.GOLD[3], 255))
    else:
        canvas.poly([(2, 13), (3, 7), (8, 4), (24, 4), (29, 7), (30, 13)], (*pal.WOOD[2], 255))
        canvas.poly([(4, 12), (5, 8), (9, 6), (23, 6), (27, 8), (28, 12)], (*pal.WOOD[3], 255))
        canvas.rect(3, 9, 26, 3, (*pal.IRON[1], 255))
        canvas.line((3, 9), (28, 9), (*pal.IRON[3], 255))
        canvas.rect(7, 4, 3, 25, (*pal.IRON[1], 255))
        canvas.rect(22, 4, 3, 25, (*pal.IRON[1], 255))
        canvas.line((7, 5), (9, 5), (*pal.IRON[3], 255))
        # Cerradura
        canvas.rect(14, 14, 5, 6, (*pal.GOLD[2], 255))
        canvas.rect(15, 15, 3, 3, (*pal.GOLD[4], 255))
        canvas.px(16, 17, (*pal.WOOD[0], 255))
        canvas.line((4, 12), (27, 12), (*pal.GOLD[1], 160))
    canvas.add_outline((*pal.VOID, 255))
    return canvas


def campfire_base() -> Canvas:
    canvas = Canvas(48, 36)
    canvas.ellipse(2, 24, 44, 10, (10, 9, 13, 160))
    # Anillo de piedras
    stones = ((3, 24), (11, 27), (20, 29), (30, 28), (38, 25), (6, 20), (41, 20))
    for index, (x, y) in enumerate(stones):
        tone = 0.26 + (index % 3) * 0.08
        base = ramp(pal.STONE, tone)
        canvas.ellipse(x, y, 9, 7, (*darken(base, 20), 255))
        canvas.ellipse(x, y - 1, 8, 5, (*base, 255))
        canvas.line((x + 1, y - 1), (x + 6, y - 1), (*lighten(base, 20), 230))
    # Ceniza
    canvas.ellipse(11, 23, 26, 9, (34, 30, 30, 255))
    canvas.ellipse(13, 24, 22, 7, (*pal.EMBER[1], 150))
    canvas.ellipse(17, 25, 12, 4, (*pal.EMBER[2], 190))
    # Troncos cruzados
    canvas.line((8, 28), (38, 20), (*pal.WOOD[1], 255), 5)
    canvas.line((8, 28), (38, 20), (*pal.WOOD[3], 255), 3)
    canvas.line((10, 20), (37, 28), (*pal.WOOD[0], 255), 5)
    canvas.line((10, 20), (37, 28), (*pal.WOOD[2], 255), 3)
    canvas.add_outline((*pal.VOID, 200))
    return canvas


def campfire_flame(phase: int) -> Canvas:
    canvas = Canvas(26, 34)
    sway = (0.0, 1.2, 0.4, -1.1)[phase % 4]
    height = (23.0, 26.0, 24.0, 21.0)[phase % 4]
    base_y = 30.0
    outer = [
        (13 - 9, base_y),
        (13 - 8 + sway, base_y - height * 0.45),
        (13 - 3 + sway * 1.6, base_y - height),
        (13 + 2, base_y - height * 0.62),
        (13 + 5 + sway, base_y - height * 0.95),
        (13 + 9, base_y - height * 0.35),
        (13 + 8, base_y),
    ]
    canvas.poly(outer, (*pal.EMBER[2], 235))
    mid = [
        (13 - 6, base_y),
        (13 - 5 + sway * 0.7, base_y - height * 0.4),
        (13 - 1 + sway, base_y - height * 0.78),
        (13 + 3, base_y - height * 0.5),
        (13 + 5, base_y - height * 0.7),
        (13 + 6, base_y - height * 0.3),
        (13 + 5, base_y),
    ]
    canvas.poly(mid, (*pal.EMBER[3], 240))
    inner = [
        (13 - 3, base_y),
        (13 - 2 + sway * 0.4, base_y - height * 0.35),
        (13 + 1, base_y - height * 0.55),
        (13 + 3, base_y - height * 0.3),
        (13 + 3, base_y),
    ]
    canvas.poly(inner, (*pal.EMBER[4], 245))
    canvas.poly(
        [(12, base_y - 2), (13, base_y - height * 0.3), (14.5, base_y - 2)], (*pal.EMBER[5], 240)
    )
    for index in range(3):
        x = 8 + index * 5 + phase * 0.6
        y = base_y - height * (0.5 + index * 0.15)
        canvas.px(x, y - (phase % 2), (*pal.EMBER[5], 180))
    return canvas


def altar(active: bool) -> Canvas:
    canvas = Canvas(64, 60)
    canvas.ellipse(4, 46, 56, 12, (8, 7, 11, 170))
    # Escalinata
    canvas.rect(6, 44, 52, 8, (*pal.STONE[2], 255))
    canvas.line((6, 44), (57, 44), (*pal.STONE[4], 255))
    canvas.rect(10, 38, 44, 7, (*pal.STONE[1], 255))
    canvas.line((10, 38), (53, 38), (*pal.STONE[3], 255))
    # Bloque central
    canvas.rect(14, 24, 36, 15, (*pal.STONE[1], 255))
    canvas.line((14, 24), (49, 24), (*pal.STONE[4], 255))
    canvas.line((14, 24), (14, 38), (*pal.STONE[3], 220))
    canvas.rect(17, 27, 30, 10, (*pal.STONE[0], 255))
    # Runas doradas
    for x in (20, 27, 34, 41):
        canvas.px(x, 29, (*pal.GOLD[2], 230))
        canvas.px(x, 31, (*pal.GOLD[1], 180))
    # Yunque
    canvas.poly([(20, 24), (44, 24), (42, 19), (34, 19), (34, 11), (28, 11), (28, 19), (22, 19)], (*pal.IRON[0], 255))
    canvas.rect(21, 18, 21, 6, (*pal.IRON[1], 255))
    canvas.poly([(21, 18), (42, 18), (40, 14), (29, 14), (29, 10), (25, 10)], (*pal.IRON[2], 255))
    canvas.line((25, 10), (29, 10), (*pal.IRON[4], 240))
    canvas.line((23, 20), (39, 20), (*pal.IRON[3], 220))
    canvas.poly([(21, 18), (16, 20), (21, 21)], (*pal.IRON[1], 255))
    # Engarces de ascuas
    for index in range(3):
        sx = 22 + index * 10
        sy = 34
        canvas.circle(sx, sy, 4, (*pal.STONE[0], 255))
        canvas.circle(sx, sy, 3, (*pal.EMBER[1], 255))
        if active or index == 0:
            canvas.circle(sx, sy, 2, (*pal.EMBER[3], 255))
            canvas.px(sx, sy, (*pal.EMBER[5], 255))
    if active:
        # Fuego de forja y resplandor
        for radius, alpha in ((26, 40), (18, 60), (11, 90)):
            canvas.circle(32, 16, radius, rgba(pal.EMBER[3], alpha))
        canvas.poly([(20, 22), (26, 4), (32, 14), (38, 2), (44, 22)], (*pal.EMBER[2], 235))
        canvas.poly([(24, 21), (29, 8), (33, 15), (37, 7), (40, 21)], (*pal.EMBER[3], 240))
        canvas.poly([(28, 20), (31, 11), (34, 19)], (*pal.EMBER[5], 245))
        for x, y in ((18, 10), (46, 13), (30, 6), (40, 18)):
            canvas.px(x, y, (*pal.EMBER[5], 200))
    else:
        canvas.circle(32, 16, 14, rgba(pal.EMBER[2], 22))
    canvas.add_outline((*pal.VOID, 235))
    return canvas


def shard(phase: int) -> Canvas:
    canvas = Canvas(14, 20)
    pulsar = (0, 1, 0, -1)[phase % 4]
    for radius, alpha in ((7, 30), (5, 55)):
        canvas.circle(7, 10, radius + pulsar, rgba(pal.EMBER[3], alpha))
    canvas.poly([(7, 1), (12, 10), (9, 18), (4, 18), (2, 10)], (*pal.EMBER[2], 255))
    canvas.poly([(7, 2), (10, 10), (8, 17), (5, 17), (4, 10)], (*pal.EMBER[3], 255))
    canvas.poly([(7, 4), (9, 10), (7, 16), (6, 10)], (*pal.EMBER[5], 245))
    canvas.line((4, 10), (7, 3), (*pal.EMBER[4], 220))
    canvas.add_outline((*pal.VOID, 220))
    return canvas


def brazier() -> Canvas:
    canvas = Canvas(28, 36)
    canvas.ellipse(2, 28, 24, 7, (9, 8, 12, 160))
    canvas.poly([(8, 28), (20, 28), (18, 20), (10, 20)], (*pal.IRON[1], 255))
    canvas.rect(12, 20, 4, 8, (*pal.IRON[2], 255))
    canvas.ellipse(4, 14, 20, 10, (*pal.IRON[1], 255))
    canvas.ellipse(5, 15, 18, 7, (*pal.IRON[2], 255))
    canvas.ellipse(7, 16, 14, 5, (*pal.EMBER[2], 235))
    canvas.ellipse(9, 16, 10, 3, (*pal.EMBER[4], 240))
    canvas.add_outline((*pal.VOID, 230))
    return canvas


def build_objects() -> tuple[Canvas, dict[str, object]]:
    rng = random.Random(4242)
    pieces: list[tuple[str, Canvas]] = [
        ("chest_closed", chest(False)),
        ("chest_open", chest(True)),
        ("campfire_base", campfire_base()),
        ("altar_idle", altar(False)),
        ("altar_active", altar(True)),
        ("brazier", brazier()),
    ]
    for index in range(4):
        pieces.append((f"campfire_flame_{index}", campfire_flame(index)))
    for index in range(4):
        pieces.append((f"shard_{index}", shard(index)))

    atlas, rects = _pack(pieces)
    manifest: dict[str, object] = {
        "version": "gf-objects-v1",
        "image_path": "objects.png",
        "objects": {
            name: {
                "rect": data["rect"],
                "anchor": "bottom_center",
                "category": "prop",
            }
            for name, data in rects.items()
        },
    }
    return atlas, manifest
