"""Sprites de partículas y efectos. Se dibujan en claro para teñirlos en runtime."""

from __future__ import annotations

import math

from tools.artforge.pixel import Canvas, rgba

CELL = 16
COLUMNS = 6


def _spark() -> Canvas:
    canvas = Canvas(CELL, CELL)
    canvas.line((7, 3), (7, 11), (255, 250, 230, 230), 1)
    canvas.line((3, 7), (11, 7), (255, 240, 210, 200), 1)
    canvas.px(7, 7, (255, 255, 250, 255))
    for offset in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
        canvas.px(7 + offset[0] * 2, 7 + offset[1] * 2, (255, 236, 200, 120))
    return canvas


def _ember() -> Canvas:
    canvas = Canvas(CELL, CELL)
    for radius, alpha in ((5, 40), (3, 110), (2, 200)):
        canvas.circle(8, 8, radius, (255, 240, 210, alpha))
    canvas.circle(8, 8, 1, (255, 255, 250, 255))
    return canvas


def _smoke() -> Canvas:
    canvas = Canvas(CELL, CELL)
    for cx, cy, radius, alpha in ((6, 9, 4, 60), (10, 7, 4, 55), (8, 5, 3, 45), (10, 10, 3, 40)):
        canvas.circle(cx, cy, radius, (228, 224, 232, alpha))
    return canvas


def _blood() -> Canvas:
    canvas = Canvas(CELL, CELL)
    for x, y, radius in ((6, 9, 2), (10, 7, 2), (8, 12, 1)):
        canvas.circle(x, y, radius, (255, 235, 235, 220))
    canvas.px(6, 8, (255, 255, 255, 240))
    return canvas


def _mote() -> Canvas:
    canvas = Canvas(CELL, CELL)
    canvas.circle(8, 8, 4, (220, 250, 255, 30))
    canvas.circle(8, 8, 2, (230, 250, 255, 120))
    canvas.circle(8, 8, 1, (255, 255, 255, 235))
    return canvas


def _ring() -> Canvas:
    canvas = Canvas(CELL, CELL)
    canvas.circle(8, 8, 7, (255, 245, 225, 120), 1)
    canvas.circle(8, 8, 5, (255, 240, 210, 70), 1)
    return canvas


def _dust() -> Canvas:
    canvas = Canvas(CELL, CELL)
    for cx, cy, radius, alpha in ((7, 10, 3, 55), (10, 9, 2, 45), (5, 9, 2, 40)):
        canvas.circle(cx, cy, radius, (226, 220, 200, alpha))
    return canvas


def _glint() -> Canvas:
    canvas = Canvas(CELL, CELL)
    canvas.line((8, 1), (8, 15), (255, 255, 240, 150), 1)
    canvas.line((1, 8), (15, 8), (255, 255, 240, 150), 1)
    canvas.line((4, 4), (12, 12), (255, 250, 220, 70), 1)
    canvas.line((12, 4), (4, 12), (255, 250, 220, 70), 1)
    canvas.circle(8, 8, 2, (255, 255, 255, 240))
    return canvas


def _slash() -> Canvas:
    canvas = Canvas(CELL, CELL)
    points = []
    for step in range(9):
        t = step / 8
        angle = -1.2 + 2.4 * t
        points.append((8 + math.cos(angle) * 7, 8 + math.sin(angle) * 7))
    for a, b in zip(points, points[1:]):
        canvas.line(a, b, (255, 250, 230, 210), 2)
    return canvas


def _star() -> Canvas:
    canvas = Canvas(CELL, CELL)
    for angle in range(0, 360, 45):
        rad = math.radians(angle)
        length = 7 if angle % 90 == 0 else 4
        canvas.line(
            (8, 8),
            (8 + math.cos(rad) * length, 8 + math.sin(rad) * length),
            (255, 248, 220, 200),
            1,
        )
    canvas.circle(8, 8, 2, (255, 255, 255, 250))
    return canvas


def _rune() -> Canvas:
    canvas = Canvas(CELL, CELL)
    canvas.circle(8, 8, 6, (230, 240, 255, 90), 1)
    canvas.line((8, 3), (8, 13), (240, 248, 255, 150))
    canvas.line((4, 8), (12, 8), (240, 248, 255, 110))
    canvas.px(8, 8, (255, 255, 255, 230))
    return canvas


def _shard_glint() -> Canvas:
    canvas = Canvas(CELL, CELL)
    canvas.poly([(8, 2), (11, 8), (8, 14), (5, 8)], (255, 245, 220, 180))
    canvas.line((8, 3), (8, 12), (255, 255, 255, 240))
    canvas.px(8, 8, (255, 255, 255, 255))
    return canvas


SPRITES = (
    ("spark", _spark),
    ("ember", _ember),
    ("smoke", _smoke),
    ("blood", _blood),
    ("mote", _mote),
    ("ring", _ring),
    ("dust", _dust),
    ("glint", _glint),
    ("slash", _slash),
    ("star", _star),
    ("rune", _rune),
    ("shard_glint", _shard_glint),
)


def build_particles() -> tuple[Canvas, dict[str, object]]:
    rows = (len(SPRITES) + COLUMNS - 1) // COLUMNS
    atlas = Canvas(COLUMNS * CELL, rows * CELL)
    manifest: dict[str, object] = {
        "version": "gf-vfx-v1",
        "image_path": "particles.png",
        "cell": CELL,
        "sprites": {},
    }
    sprites: dict[str, object] = {}
    for index, (name, factory) in enumerate(SPRITES):
        col = index % COLUMNS
        row = index // COLUMNS
        atlas.blit(factory(), (col * CELL, row * CELL))
        sprites[name] = {"rect": [col * CELL, row * CELL, CELL, CELL], "tintable": True}
    manifest["sprites"] = sprites
    return atlas, manifest
