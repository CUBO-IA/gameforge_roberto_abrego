"""Paleta maestra de GameForge: fantasía oscura, piedra fría y forja cálida.

Rampas cortas de 4-6 pasos, pensadas para leerse sobre fondo casi negro.
Los nombres son estables: la guía de arte y el código comparten estas claves.
"""

from __future__ import annotations

from tools.artforge.pixel import Color

# Profundidad ambiental
VOID: Color = (7, 7, 13)
DEEP: Color = (11, 12, 20)
NIGHT: Color = (18, 19, 30)

# Piedra fría (muros y suelos de mazmorra)
MORTAR: Color = (16, 16, 25)
STONE: tuple[Color, ...] = (
    (24, 25, 36),
    (34, 35, 49),
    (46, 48, 64),
    (60, 62, 80),
    (80, 82, 102),
    (104, 106, 128),
)
STONE_WARM: tuple[Color, ...] = (
    (28, 24, 27),
    (42, 35, 37),
    (58, 48, 47),
    (78, 64, 58),
    (102, 84, 72),
)
STONE_MOSS: tuple[Color, ...] = (
    (28, 38, 32),
    (40, 56, 42),
    (54, 76, 52),
    (74, 100, 64),
)

# Metal y oro viejo (armaduras, UI, cofres)
IRON: tuple[Color, ...] = (
    (30, 34, 46),
    (48, 54, 70),
    (70, 78, 100),
    (96, 106, 132),
    (132, 144, 170),
    (178, 192, 216),
)
GOLD: tuple[Color, ...] = (
    (92, 64, 24),
    (140, 100, 36),
    (190, 146, 58),
    (232, 192, 92),
    (252, 234, 158),
)
WOOD: tuple[Color, ...] = (
    (44, 30, 22),
    (64, 44, 30),
    (88, 62, 40),
    (116, 84, 54),
    (146, 110, 70),
)
LEATHER: tuple[Color, ...] = (
    (48, 32, 26),
    (70, 48, 36),
    (96, 68, 48),
    (124, 92, 64),
    (158, 126, 92),
)

# Telas y acentos
TEAL: tuple[Color, ...] = (
    (16, 40, 48),
    (24, 66, 76),
    (34, 96, 104),
    (52, 132, 138),
    (86, 176, 176),
)
CAPE: tuple[Color, ...] = (
    (20, 16, 34),
    (30, 24, 50),
    (44, 34, 68),
    (62, 48, 90),
)
BONE: tuple[Color, ...] = (
    (108, 102, 88),
    (142, 134, 114),
    (176, 168, 146),
    (208, 202, 182),
    (236, 232, 216),
)
BLOOD: tuple[Color, ...] = (
    (56, 16, 20),
    (92, 26, 30),
    (136, 44, 44),
    (184, 72, 60),
    (226, 118, 96),
)
SLIME: tuple[Color, ...] = (
    (20, 44, 32),
    (32, 74, 48),
    (48, 112, 62),
    (72, 156, 80),
    (112, 202, 106),
    (170, 236, 150),
)
ARCANE: tuple[Color, ...] = (
    (26, 18, 48),
    (44, 30, 76),
    (68, 46, 112),
    (98, 70, 156),
    (140, 106, 202),
    (192, 164, 240),
)
CYAN: tuple[Color, ...] = (
    (12, 42, 54),
    (20, 70, 86),
    (32, 108, 122),
    (56, 154, 162),
    (100, 204, 202),
    (176, 244, 234),
)
EMBER: tuple[Color, ...] = (
    (92, 24, 14),
    (140, 44, 18),
    (196, 74, 24),
    (238, 122, 42),
    (252, 180, 78),
    (255, 234, 160),
)
LAVA: tuple[Color, ...] = (
    (60, 16, 12),
    (104, 30, 16),
    (156, 54, 22),
    (212, 92, 30),
    (248, 148, 52),
    (255, 214, 120),
)
WATER: tuple[Color, ...] = (
    (10, 26, 44),
    (16, 42, 66),
    (24, 62, 92),
    (38, 90, 120),
    (62, 126, 150),
    (110, 176, 186),
)
FLESH: tuple[Color, ...] = (
    (52, 30, 26),
    (78, 46, 38),
    (108, 66, 52),
    (142, 92, 70),
    (178, 124, 96),
)

# Interfaz
UI_FILL: Color = (18, 17, 27)
UI_FILL_SOFT: Color = (26, 24, 38)
UI_EDGE: Color = (86, 74, 104)
UI_TEXT: Color = (238, 230, 214)
UI_TEXT_DIM: Color = (152, 146, 168)
UI_ACCENT: Color = (255, 164, 72)
UI_HEALTH: Color = (198, 58, 66)
UI_MANA: Color = (86, 158, 214)
UI_SHADOW: Color = (6, 6, 12)
