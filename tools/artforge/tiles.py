"""Generación del tileset de mazmorra: suelos, muros, líquidos y decoración.

Cada tile es una pieza de 32x32 px dibujada a mano en código, con variantes
suficientes para que la repetición no se lea como una cuadrícula.
"""

from __future__ import annotations

import random

from tools.artforge import palette as pal
from tools.artforge.pixel import Canvas, darken, lighten, mix, ramp, rgba

TILE = 32
COLUMNS = 8


# ------------------------------------------------------------------- suelos


def _grout(canvas: Canvas, x: int, y: int, w: int, h: int) -> None:
    canvas.rect(x, y, w, h, (*pal.MORTAR, 255))


def _slab(
    canvas: Canvas,
    rng: random.Random,
    x: int,
    y: int,
    w: int,
    h: int,
    tone: float,
    warm: bool = False,
) -> None:
    """Losa de piedra con bisel, manchas y desgaste."""
    colors = pal.STONE_WARM if warm else pal.STONE
    base = ramp(colors, tone)
    canvas.bevel_rect(x, y, w, h, base, lighten(base, 12), darken(base, 12))
    inner = (x + 1, y + 1, max(1, w - 2), max(1, h - 2))
    canvas.speckle(rng, inner, (lighten(base, 8), darken(base, 7), darken(base, 3)), 0.16)
    if w >= 12 and h >= 12 and rng.random() < 0.55:
        # Piquete / desconchón
        px = x + rng.randrange(2, max(3, w - 4))
        py = y + rng.randrange(2, max(3, h - 4))
        canvas.px(px, py, darken(base, 22))
        canvas.px(px + 1, py, darken(base, 16))
        canvas.px(px, py + 1, darken(base, 18))
    if w >= 16 and h >= 16 and rng.random() < 0.4:
        # Junta interior tenue
        crop = rng.randrange(6, max(7, w - 8))
        canvas.line((x + crop, y + 1), (x + crop, y + h - 2), rgba(darken(base, 20), 120))


def _crack(canvas: Canvas, rng: random.Random, x: int, y: int, length: int, vertical: bool) -> None:
    dark = (20, 20, 29, 255)
    edge = (72, 72, 92, 200)
    step = 1
    points: list[tuple[int, int]] = [(x, y)]
    for index in range(length):
        nx = x + (rng.choice((-1, 1)) if index % 2 else 0)
        ny = y + step
        if vertical:
            nx, ny = x + step, y + (rng.choice((-1, 1)) if index % 2 else 0)
        x, y = nx, ny
        points.append((x, y))
    for start, end in zip(points, points[1:]):
        canvas.line(start, end, dark, 2)
        canvas.line((start[0] + 1, start[1] + 1), (end[0] + 1, end[1] + 1), edge, 1)


def _moss(canvas: Canvas, rng: random.Random, bounds: tuple[int, int, int, int]) -> None:
    x, y, w, h = bounds
    for _ in range(rng.randrange(18, 34)):
        px = x + rng.randrange(w)
        py = y + rng.randrange(h)
        color = rng.choice(pal.STONE_MOSS)
        canvas.px(px, py, (*color, 255))
        if rng.random() < 0.45:
            canvas.px(px + 1, py, (*darken(color, 10), 255))
        if rng.random() < 0.25:
            canvas.px(px, py + 1, (*darken(color, 6), 255))


def floor_tile(rng: random.Random, variant: int) -> Canvas:
    canvas = Canvas(TILE, TILE, (20, 20, 29, 255))
    if variant == 0:
        _slab(canvas, rng, 0, 0, 31, 31, rng.uniform(0.34, 0.46))
    elif variant == 1:
        _slab(canvas, rng, 0, 0, 31, 15, rng.uniform(0.3, 0.4))
        _slab(canvas, rng, 0, 16, 31, 16, rng.uniform(0.36, 0.48))
    elif variant == 2:
        _slab(canvas, rng, 0, 0, 15, 31, rng.uniform(0.34, 0.44))
        _slab(canvas, rng, 16, 0, 16, 31, rng.uniform(0.3, 0.42))
    elif variant == 3:
        _slab(canvas, rng, 0, 0, 15, 15, rng.uniform(0.34, 0.44))
        _slab(canvas, rng, 16, 0, 16, 15, rng.uniform(0.3, 0.4))
        _slab(canvas, rng, 0, 16, 15, 16, rng.uniform(0.32, 0.44))
        _slab(canvas, rng, 16, 16, 16, 16, rng.uniform(0.36, 0.48))
    else:  # losa partida
        _slab(canvas, rng, 0, 0, 31, 31, rng.uniform(0.32, 0.44))
        canvas.line((3, 21), (13, 25), (20, 20, 29, 255), 2)
        canvas.line((13, 25), (21, 31), (20, 20, 29, 255), 2)
        canvas.line((3, 22), (13, 26), (78, 80, 100, 160), 1)
        _slab(canvas, rng, 2, 23, 9, 8, rng.uniform(0.4, 0.5))
    return canvas


def floor_cracked(rng: random.Random) -> Canvas:
    canvas = floor_tile(rng, 3)
    _crack(canvas, rng, rng.randrange(4, 12), 2, 9, vertical=False)
    _crack(canvas, rng, rng.randrange(16, 24), 18, 7, vertical=True)
    return canvas


def floor_mossy(rng: random.Random) -> Canvas:
    canvas = floor_tile(rng, 0)
    _moss(canvas, rng, (2, 20, 18, 10))
    _moss(canvas, rng, (20, 3, 10, 8))
    return canvas


def floor_puddle(rng: random.Random) -> Canvas:
    canvas = floor_tile(rng, 1)
    canvas.ellipse(5, 14, 22, 12, (*pal.WATER[0], 235))
    canvas.ellipse(6, 15, 20, 9, (*pal.WATER[1], 235))
    canvas.ellipse(8, 17, 12, 4, (*pal.WATER[2], 210))
    canvas.line((10, 17), (16, 17), (*pal.WATER[4], 220))
    canvas.px(13, 16, (*pal.WATER[5], 255))
    return canvas


def floor_grate(rng: random.Random) -> Canvas:
    canvas = Canvas(TILE, TILE, (*pal.MORTAR, 255))
    canvas.bevel_rect(1, 1, 30, 30, pal.IRON[1], pal.IRON[3], pal.IRON[0])
    for index in range(4):
        x = 5 + index * 7
        canvas.rect(x, 4, 3, 24, pal.IRON[2])
        canvas.line((x, 4), (x, 27), pal.IRON[4])
        canvas.line((x + 2, 4), (x + 2, 27), pal.IRON[0])
    canvas.line((2, 15), (29, 15), pal.IRON[3])
    canvas.rect(3, 3, 26, 1, pal.IRON[4])
    return canvas


# -------------------------------------------------------------------- muros


def wall_face(rng: random.Random, variant: int) -> Canvas:
    canvas = Canvas(TILE, TILE, (*pal.MORTAR, 255))
    rows = 4
    brick_h = 8
    for row in range(rows):
        offset = 0 if row % 2 == 0 else 8
        y = row * brick_h
        for col in range(2):
            x = col * 16 + offset
            width = 16
            if x + width > TILE:
                width = TILE - x
            tone = rng.uniform(0.2, 0.38) + (0.05 if variant == 1 else 0.0)
            base = ramp(pal.STONE_WARM if variant == 2 else pal.STONE, tone)
            canvas.rect(x, y, width, brick_h, base)
            canvas.line((x, y), (x + width - 1, y), lighten(base, 20))
            canvas.line((x, y), (x, y + brick_h - 1), lighten(base, 12))
            canvas.line((x, y + brick_h - 1), (x + width - 1, y + brick_h - 1), darken(base, 16))
            canvas.speckle(rng, (x, y, width, brick_h), (darken(base, 8), lighten(base, 6)), 0.12)
            if rng.random() < 0.22:
                cx = x + rng.randrange(3, max(4, width - 4))
                cy = y + rng.randrange(2, brick_h - 2)
                canvas.line((cx, cy), (cx + 2, cy + 2), darken(base, 24))
    # Humedad descendente y detrito en la base
    for index in range(rng.randrange(2, 5)):
        x = rng.randrange(2, TILE - 3)
        height = rng.randrange(8, 22)
        canvas.line((x, 0), (x, height), rgba((16, 24, 26), 80))
    canvas.rect(0, TILE - 3, TILE, 3, rgba((12, 15, 18), 130))
    canvas.speckle(rng, (0, TILE - 3, TILE, 3), ((52, 58, 50), (38, 42, 40)), 0.22)
    return canvas


def wall_top(rng: random.Random) -> Canvas:
    """Superficie superior del muro vista en escorzo: sillares oscuros y polvo."""
    canvas = Canvas(TILE, TILE, (*pal.MORTAR, 255))
    _slab(canvas, rng, 0, 0, 15, 15, rng.uniform(0.14, 0.22))
    _slab(canvas, rng, 16, 0, 16, 15, rng.uniform(0.16, 0.24))
    _slab(canvas, rng, 0, 16, 15, 16, rng.uniform(0.16, 0.26))
    _slab(canvas, rng, 16, 16, 16, 16, rng.uniform(0.14, 0.22))
    canvas.speckle(rng, (0, 0, TILE, TILE), ((52, 54, 70), (20, 20, 28), (40, 42, 56)), 0.09)
    for _ in range(2):
        x = rng.randrange(4, TILE - 6)
        y = rng.randrange(4, TILE - 6)
        canvas.line((x, y), (x + 4, y + 3), (18, 18, 26, 200), 1)
    return canvas


def wall_cap(rng: random.Random) -> Canvas:
    """Banda superior iluminada del muro (se dibuja sobre la cara)."""
    canvas = Canvas(TILE, 14)
    base = ramp(pal.STONE, 0.46)
    canvas.rect(0, 0, TILE, 14, base)
    canvas.speckle(rng, (0, 0, TILE, 14), (lighten(base, 10), darken(base, 8)), 0.22)
    canvas.line((0, 0), (TILE - 1, 0), lighten(base, 26))
    canvas.line((0, 1), (TILE - 1, 1), lighten(base, 14))
    canvas.line((0, 11), (TILE - 1, 11), darken(base, 12))
    canvas.line((0, 12), (TILE - 1, 12), darken(base, 22))
    canvas.rect(0, 13, TILE, 1, (*pal.MORTAR, 255))
    for _ in range(3):
        x = rng.randrange(3, TILE - 4)
        canvas.line((x, 3), (x + 3, 6), rgba(darken(base, 18), 180))
    return canvas


def wall_top_shadow(rng: random.Random) -> Canvas:
    """Cara superior vista en escorzo cuando el muro queda sobre suelo."""
    canvas = Canvas(TILE, 14)
    base = ramp(pal.STONE, 0.24)
    canvas.rect(0, 0, TILE, 14, base)
    canvas.speckle(rng, (0, 0, TILE, 14), (darken(base, 6), darken(base, 12)), 0.2)
    canvas.rect(0, 0, TILE, 3, (*pal.MORTAR, 255))
    return canvas


# ------------------------------------------------------------------ líquidos


def water_tile(rng: random.Random, variant: int) -> Canvas:
    canvas = Canvas(TILE, TILE, (*pal.WATER[1], 255))
    canvas.rect(0, 0, TILE, TILE, (*pal.WATER[1], 255))
    for index in range(4):
        y = 4 + index * 7 + variant
        amplitude = rng.choice((0, 1, 2))
        color = pal.WATER[3] if index % 2 == 0 else pal.WATER[2]
        canvas.line((0, y), (8, y - amplitude), (*color, 230))
        canvas.line((8, y - amplitude), (16, y), (*color, 230))
        canvas.line((16, y), (24, y + amplitude), (*color, 230))
        canvas.line((24, y + amplitude), (31, y), (*color, 230))
    canvas.speckle(rng, (0, 0, TILE, TILE), (pal.WATER[4], pal.WATER[2]), 0.06)
    canvas.rect(0, 0, TILE, 2, rgba(pal.WATER[0], 120))
    canvas.rect(0, TILE - 2, TILE, 2, rgba(pal.WATER[0], 120))
    return canvas


def lava_tile(rng: random.Random, variant: int) -> Canvas:
    """Corteza de escoria flotante sobre lava: placas oscuras y grietas vivas."""
    canvas = Canvas(TILE, TILE, (*pal.LAVA[2], 255))
    # Lecho incandescente con vetas
    canvas.speckle(rng, (0, 0, TILE, TILE), (pal.LAVA[3], pal.LAVA[4], pal.LAVA[1]), 0.35)
    # Placas de corteza
    plates = [
        (1, 2, 13, 11), (16, 1, 15, 9), (2, 16, 10, 14),
        (14, 13, 9, 8), (25, 12, 6, 12), (14, 23, 12, 8),
    ]
    for index, (x, y, w, h) in enumerate(plates):
        if index % 3 == variant % 3:
            continue
        ink = (30, 16, 16, 255)
        top = (58, 26, 22, 255)
        canvas.ellipse(x, y, w, h, ink)
        canvas.ellipse(x, y + 1, w, max(2, h - 1), top)
        canvas.ellipse(x + 1, y + 2, max(2, w - 3), max(2, h - 4), (40, 21, 19, 255))
        canvas.speckle(rng, (x + 1, y + 1, max(1, w - 2), max(1, h - 2)), ((24, 14, 15), (52, 24, 20)), 0.18)
        canvas.line((x + 2, y + 1), (x + w - 3, y + 1), (74, 34, 26, 220))
    # Burbujas brillantes en las grietas
    for _ in range(4):
        x = rng.randrange(3, TILE - 4)
        y = rng.randrange(3, TILE - 4)
        canvas.circle(x, y, 2, (*pal.LAVA[4], 210))
        canvas.px(x, y, (*pal.LAVA[5], 255))
    return canvas


# ------------------------------------------------------------------ decorado


def decor_rubble(rng: random.Random) -> Canvas:
    canvas = Canvas(TILE, TILE)
    for _ in range(rng.randrange(5, 8)):
        x = rng.randrange(3, TILE - 8)
        y = rng.randrange(8, TILE - 6)
        w = rng.randrange(4, 8)
        h = rng.randrange(3, 6)
        base = ramp(pal.STONE, rng.uniform(0.3, 0.52))
        canvas.ellipse(x, y + 1, w, h, (*darken(base, 26), 255))
        canvas.ellipse(x, y, w, h - 1, (*base, 255))
        canvas.line((x + 1, y), (x + w - 2, y), (*lighten(base, 24), 255))
        canvas.line((x + 1, y + 1), (x + 1, y + h - 2), (*lighten(base, 10), 200))
    canvas.add_outline((*pal.MORTAR, 200))
    return canvas


def decor_bones(rng: random.Random) -> Canvas:
    canvas = Canvas(TILE, TILE)
    for index in range(3):
        y = 14 + index * 4
        x = 5 + index
        canvas.line((x, y), (x + 7, y - 2), (*pal.BONE[1], 255), 2)
        canvas.line((x + 7, y - 2), (x + 14, y + 1), (*pal.BONE[2], 255), 2)
        canvas.px(x, y, (*pal.BONE[3], 255))
    # Fémur
    canvas.line((17, 24), (27, 20), (*pal.BONE[2], 255), 3)
    canvas.circle(17, 24, 2, (*pal.BONE[3], 255))
    canvas.circle(27, 20, 2, (*pal.BONE[3], 255))
    canvas.add_outline((*pal.MORTAR, 200))
    return canvas


def decor_skull(rng: random.Random) -> Canvas:
    canvas = Canvas(16, 14)
    canvas.ellipse(1, 1, 13, 11, (*pal.BONE[2], 255))
    canvas.rect(4, 9, 8, 4, (*pal.BONE[1], 255))
    canvas.ellipse(3, 4, 4, 4, (*pal.MORTAR, 255))
    canvas.ellipse(9, 4, 4, 4, (*pal.MORTAR, 255))
    canvas.px(5, 5, (200, 240, 240, 255))
    canvas.px(11, 5, (200, 240, 240, 255))
    canvas.rect(7, 7, 2, 2, (*pal.MORTAR, 255))
    for x in (5, 7, 9):
        canvas.line((x, 10), (x, 12), (*pal.BONE[0], 255))
    canvas.line((2, 3), (3, 4), (*pal.BONE[3], 255))
    canvas.add_outline((*pal.MORTAR, 220))
    return canvas


def decor_mushroom(rng: random.Random) -> Canvas:
    canvas = Canvas(TILE, TILE)
    for _ in range(rng.randrange(2, 4)):
        x = rng.randrange(6, 24)
        y = rng.randrange(12, 24)
        height = rng.randrange(3, 6)
        cap = rng.randrange(4, 7)
        canvas.rect(x, y, 2, height, (*pal.BONE[1], 255))
        canvas.ellipse(x - cap // 2, y - 3, cap, cap - 2, (*pal.CYAN[2], 255))
        canvas.ellipse(x - cap // 2, y - 3, cap, cap - 3, (*pal.CYAN[3], 255))
        canvas.px(x, y - 2, (*pal.CYAN[5], 255))
        canvas.px(x + 1, y - 1, (*pal.CYAN[4], 220))
    return canvas


def decor_crystal(rng: random.Random) -> Canvas:
    canvas = Canvas(TILE, TILE)
    shards = [
        (13, 26, 5, 14, 0.0),
        (18, 27, 4, 10, 0.2),
        (9, 27, 3, 7, 0.35),
    ]
    for x, base_y, width, height, tone in shards:
        color = ramp(pal.CYAN, 0.45 + tone)
        canvas.poly(
            [(x, base_y), (x + width // 2, base_y - height), (x + width, base_y)],
            (*color, 255),
        )
        canvas.line((x + width // 2, base_y - height + 2), (x + width // 2, base_y - 2), (*pal.CYAN[5], 220))
        canvas.line((x + 1, base_y - 1), (x + width // 2, base_y - height + 1), (*pal.CYAN[4], 180))
    canvas.ellipse(7, 25, 20, 5, (*pal.CYAN[0], 150))
    canvas.add_outline((*pal.MORTAR, 210))
    return canvas


def decor_roots(rng: random.Random) -> Canvas:
    canvas = Canvas(TILE, TILE)
    color = pal.WOOD[1]
    points = [(0, 2)]
    x, y = 0, 2
    for _ in range(9):
        x += rng.randrange(3, 6)
        y += rng.randrange(1, 4)
        points.append((min(30, x), min(30, y)))
    for start, end in zip(points, points[1:]):
        canvas.line(start, end, (*color, 255), 2)
        canvas.line((start[0], start[1] + 1), (end[0], end[1] + 1), (*darken(color, 12), 200))
    canvas.line((14, 8), (16, 18), (*color, 255), 2)
    canvas.line((22, 12), (20, 22), (*color, 255), 2)
    return canvas


def decor_pebbles(rng: random.Random) -> Canvas:
    canvas = Canvas(TILE, TILE)
    for _ in range(rng.randrange(7, 12)):
        x = rng.randrange(2, TILE - 5)
        y = rng.randrange(2, TILE - 4)
        tone = rng.uniform(0.3, 0.55)
        color = ramp(pal.STONE, tone)
        canvas.rect(x, y + 1, 3, 2, (*darken(color, 24), 255))
        canvas.rect(x, y, 3, 1, (*lighten(color, 16), 255))
        canvas.px(x, y + 2, (*pal.MORTAR, 180))
    return canvas


def decor_web(rng: random.Random) -> Canvas:
    canvas = Canvas(TILE, TILE)
    web = (150, 154, 168, 70)
    for index in range(4):
        canvas.line((0, 0), (10 + index * 5, 10 + index * 5), web)
    for radius in (5, 9, 13):
        canvas.circle(0, 0, radius, web, 1)
    return canvas


def decor_chain(rng: random.Random) -> Canvas:
    canvas = Canvas(10, 22)
    for index in range(7):
        y = index * 3
        canvas.ellipse(1 if index % 2 else 3, y, 5, 4, (*pal.IRON[2], 255), 1)
        canvas.px(3 if index % 2 else 5, y + 1, (*pal.IRON[4], 255))
    canvas.add_outline((*pal.MORTAR, 220))
    return canvas


def tool_torch_bracket(rng: random.Random) -> Canvas:
    canvas = Canvas(TILE, TILE)
    canvas.rect(14, 12, 4, 12, (*pal.IRON[1], 255))
    canvas.line((15, 12), (15, 23), (*pal.IRON[3], 255))
    canvas.rect(11, 22, 10, 3, (*pal.IRON[2], 255))
    canvas.line((11, 22), (20, 22), (*pal.IRON[4], 255))
    canvas.rect(13, 8, 6, 6, (*pal.WOOD[1], 255))
    canvas.rect(14, 9, 4, 4, (*pal.WOOD[3], 255))
    canvas.rect(13, 6, 6, 3, (*pal.EMBER[3], 255))
    canvas.px(15, 5, (*pal.EMBER[4], 255))
    canvas.add_outline((*pal.MORTAR, 220))
    return canvas


def tool_banner(rng: random.Random) -> Canvas:
    canvas = Canvas(22, 32)
    canvas.rect(0, 0, 22, 2, (*pal.WOOD[1], 255))
    canvas.poly([(2, 2), (20, 2), (19, 28), (16, 25), (13, 29), (10, 25), (7, 29), (3, 26)], (*pal.TEAL[0], 255))
    canvas.poly([(4, 4), (18, 4), (17, 26), (15, 24), (12, 27), (9, 24), (6, 27), (5, 25)], (*pal.TEAL[1], 255))
    canvas.line((4, 4), (4, 24), (*pal.TEAL[3], 200))
    # Sigilo de la forja
    canvas.circle(11, 13, 4, (*pal.GOLD[2], 235), 1)
    canvas.line((11, 9), (11, 17), (*pal.GOLD[2], 235))
    canvas.line((8, 12), (14, 12), (*pal.GOLD[2], 235))
    canvas.line((16, 6), (17, 20), rgba((0, 0, 0), 60))
    canvas.add_outline((*pal.MORTAR, 210))
    return canvas


def tool_pillar_base(rng: random.Random) -> Canvas:
    """Base de columna rota: plinto, fuste truncado y escombros alrededor."""
    canvas = Canvas(TILE, TILE)
    canvas.ellipse(1, 21, 30, 11, (10, 10, 17, 200))
    canvas.rect(2, 18, 28, 7, (*pal.STONE[1], 255))
    canvas.line((2, 18), (29, 18), (*pal.STONE[4], 255))
    canvas.line((2, 18), (2, 24), (*pal.STONE[3], 200))
    canvas.ellipse(2, 22, 28, 8, (*pal.STONE[2], 255))
    canvas.rect(8, 9, 16, 10, (*pal.STONE[2], 255))
    canvas.line((8, 9), (23, 9), (*pal.STONE[4], 255))
    canvas.line((9, 9), (9, 18), (*pal.STONE[3], 255))
    canvas.line((23, 9), (23, 18), (*pal.STONE[1], 255))
    for y in (10, 13, 16):
        canvas.line((9, y), (21, y), (52, 54, 70, 160))
    canvas.rect(6, 6, 20, 4, (*pal.STONE[3], 255))
    canvas.line((6, 6), (25, 6), (*pal.STONE[5], 255))
    canvas.line((6, 9), (25, 9), (*pal.STONE[1], 255))
    canvas.poly([(6, 6), (8, 2), (11, 6)], (*pal.STONE[3], 255))
    for _ in range(4):
        x = rng.randrange(2, 28)
        y = rng.randrange(24, 30)
        canvas.rect(x, y, 3, 2, (*pal.STONE[2], 220))
    canvas.add_outline((*pal.MORTAR, 230))
    return canvas


def prop_barrel(rng: random.Random) -> Canvas:
    canvas = Canvas(24, 26)
    canvas.ellipse(1, 1, 22, 8, (*pal.WOOD[2], 255))
    canvas.ellipse(2, 2, 20, 5, (*pal.WOOD[4], 255))
    canvas.rect(1, 4, 22, 19, (*pal.WOOD[2], 255))
    canvas.ellipse(1, 20, 22, 6, (*pal.WOOD[1], 255))
    for x in (5, 10, 15, 20):
        canvas.line((x, 5), (x, 22), (*pal.WOOD[3], 200))
    for y in (8, 16):
        canvas.rect(0, y, 24, 2, (*pal.IRON[2], 255))
        canvas.line((0, y), (23, y), (*pal.IRON[3], 255))
        canvas.line((0, y + 1), (23, y + 1), (*pal.IRON[0], 255))
    canvas.line((4, 6), (4, 20), (*pal.WOOD[4], 180))
    canvas.add_outline((*pal.MORTAR, 220))
    return canvas


def prop_crate(rng: random.Random) -> Canvas:
    canvas = Canvas(24, 24)
    canvas.rect(1, 4, 22, 19, (*pal.WOOD[1], 255))
    canvas.rect(2, 5, 20, 17, (*pal.WOOD[2], 255))
    for y in (6, 11, 16):
        canvas.line((2, y), (21, y), (*pal.WOOD[3], 220))
    canvas.line((2, 5), (21, 21), (*pal.WOOD[3], 200))
    canvas.line((21, 5), (2, 21), (*pal.WOOD[3], 200))
    canvas.rect(1, 2, 22, 3, (*pal.WOOD[3], 255))
    canvas.line((1, 2), (22, 2), (*pal.WOOD[4], 255))
    canvas.add_outline((*pal.MORTAR, 220))
    return canvas


def prop_urn(rng: random.Random) -> Canvas:
    canvas = Canvas(20, 24)
    canvas.ellipse(4, 1, 12, 5, (*pal.STONE[2], 255))
    canvas.rect(6, 3, 8, 4, (*pal.STONE[2], 255))
    canvas.ellipse(1, 6, 18, 16, (*pal.STONE_WARM[2], 255))
    canvas.ellipse(3, 8, 14, 11, (*pal.STONE_WARM[3], 255))
    canvas.ellipse(5, 9, 6, 6, (*pal.STONE_WARM[4], 220))
    canvas.rect(4, 18, 12, 5, (*pal.STONE_WARM[1], 255))
    canvas.ellipse(3, 20, 14, 4, (*pal.STONE_WARM[0], 255))
    canvas.add_outline((*pal.MORTAR, 220))
    return canvas


# ------------------------------------------------------------------- ensamblado


def build_tileset(seed: int = 20261107) -> tuple[Canvas, dict[str, object]]:
    """Construye el atlas de tiles y su manifiesto de nombres."""
    rng = random.Random(seed)
    tiles: list[tuple[str, Canvas]] = []

    tiles.append(("floor_a", floor_tile(rng, 0)))
    tiles.append(("floor_b", floor_tile(rng, 1)))
    tiles.append(("floor_c", floor_tile(rng, 2)))
    tiles.append(("floor_d", floor_tile(rng, 3)))
    tiles.append(("floor_broken", floor_tile(rng, 4)))
    tiles.append(("floor_cracked", floor_cracked(rng)))
    tiles.append(("floor_mossy", floor_mossy(rng)))
    tiles.append(("floor_puddle", floor_puddle(rng)))
    tiles.append(("floor_grate", floor_grate(rng)))
    for index in range(3):
        tiles.append((f"wall_face_{index}", wall_face(rng, index)))
    tiles.append(("wall_top", wall_top(rng)))
    tiles.append(("wall_cap", wall_cap(rng)))
    tiles.append(("wall_shadow", wall_top_shadow(rng)))
    for index in range(2):
        tiles.append((f"water_{index}", water_tile(rng, index)))
    for index in range(2):
        tiles.append((f"lava_{index}", lava_tile(rng, index)))

    decor = [
        ("decor_rubble", decor_rubble(rng)),
        ("decor_bones", decor_bones(rng)),
        ("decor_skull", decor_skull(rng)),
        ("decor_mushroom", decor_mushroom(rng)),
        ("decor_crystal", decor_crystal(rng)),
        ("decor_roots", decor_roots(rng)),
        ("decor_pebbles", decor_pebbles(rng)),
        ("decor_web", decor_web(rng)),
        ("decor_chain", decor_chain(rng)),
        ("tool_torch", tool_torch_bracket(rng)),
        ("tool_banner", tool_banner(rng)),
        ("tool_pillar", tool_pillar_base(rng)),
        ("prop_barrel", prop_barrel(rng)),
        ("prop_crate", prop_crate(rng)),
        ("prop_urn", prop_urn(rng)),
    ]

    entries = tiles + decor
    rows = (len(entries) + COLUMNS - 1) // COLUMNS
    atlas = Canvas(COLUMNS * TILE, rows * TILE)
    manifest_tiles: dict[str, dict[str, object]] = {}
    for index, (name, canvas) in enumerate(entries):
        col = index % COLUMNS
        row = index // COLUMNS
        atlas.blit(canvas, (col * TILE, row * TILE))
        manifest_tiles[name] = {
            "index": index,
            "rect": [col * TILE, row * TILE, canvas.width, canvas.height],
            "layer": "decor" if name.startswith(("decor_", "tool_", "prop_")) else "terrain",
        }

    manifest: dict[str, object] = {
        "version": "gf-tiles-v1",
        "image_path": "dungeon_tileset.png",
        "tile_size": TILE,
        "columns": COLUMNS,
        "rows": rows,
        "tiles": manifest_tiles,
    }
    return atlas, manifest
