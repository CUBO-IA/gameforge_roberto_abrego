"""Paleta visual centralizada."""

from __future__ import annotations

Color = tuple[int, int, int]
RGBA = tuple[int, int, int, int]

BACKGROUND: Color = (9, 10, 18)
BACKGROUND_DEEP: Color = (5, 6, 12)
FLOOR: Color = (34, 36, 52)
FLOOR_ALT: Color = (40, 42, 60)
WALL_TOP: Color = (68, 62, 88)
WALL_FACE: Color = (35, 32, 49)
WALL_EDGE: Color = (96, 84, 120)
WATER: Color = (28, 68, 102)
WATER_LIGHT: Color = (58, 118, 150)
LAVA: Color = (128, 44, 28)
LAVA_LIGHT: Color = (246, 132, 54)
TEXT: Color = (238, 230, 218)
TEXT_DIM: Color = (154, 148, 168)
ACCENT: Color = (255, 154, 64)
ACCENT_DARK: Color = (156, 72, 34)
HEALTH: Color = (214, 62, 74)
HEALTH_BACK: Color = (58, 22, 30)
MANA: Color = (86, 168, 220)
GOLD: Color = (226, 196, 92)
VIOLET: Color = (150, 120, 255)
GREEN: Color = (112, 196, 134)
WHITE: Color = (255, 255, 255)
BLACK: Color = (0, 0, 0)

ENEMY_COLORS: dict[str, Color] = {
    "slime": (86, 178, 120),
    "wisp": (142, 118, 255),
    "brute": (196, 92, 70),
}
