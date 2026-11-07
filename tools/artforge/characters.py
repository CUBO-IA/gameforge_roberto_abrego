"""Sprites animados de personajes y enemigos.

Los sprites se dibujan a 1x con un rig mínimo: posiciones de articulación por
fotograma, miembros rasterizados como segmentos y un contorno oscuro único al
final. El volumen se consigue con bandas de valor (luz / base / sombra) y una
luz de borde superior izquierda coherente en todo el elenco.
"""

from __future__ import annotations

import math
import random

from tools.artforge import palette as pal
from tools.artforge.pixel import Canvas, darken, lighten, mix, rgba


def _limb(
    canvas: Canvas,
    start: tuple[float, float],
    end: tuple[float, float],
    width: int,
    base: tuple[int, int, int],
    light: tuple[int, int, int],
) -> None:
    canvas.line(start, end, (*darken(base, 14), 255), width)
    canvas.line(start, end, (*base, 255), max(1, width - 1))
    canvas.line(
        (start[0] - 0.5, start[1] - width / 3),
        (end[0] - 0.5, end[1] - width / 3),
        (*light, 220),
        1,
    )


def _sword(
    canvas: Canvas,
    hand: tuple[float, float],
    angle: float,
    length: float,
    grip_color: tuple[int, int, int] = pal.GOLD[2],
    smear: bool = False,
) -> None:
    """Hoja de un solo filo, con filo claro y arco de estela opcional."""
    dx, dy = math.cos(angle), math.sin(angle)
    px, py = -dy, dx
    tip = (hand[0] + dx * length, hand[1] + dy * length)
    base = (hand[0] + dx * 4, hand[1] + dy * 4)
    blade = [
        (base[0] + px * 2, base[1] + py * 2),
        (tip[0] + px * 0.6, tip[1] + py * 0.6),
        (tip[0] - px * 0.6, tip[1] - py * 0.6),
        (base[0] - px * 2, base[1] - py * 2),
    ]
    if smear:
        # Media luna rellena: estela de golpe limpia, no un trazo grueso.
        outer: list[tuple[float, float]] = []
        inner: list[tuple[float, float]] = []
        for step in range(12):
            t = step / 11
            a = angle - 1.5 + 2.6 * t
            tension = 0.86 + 0.22 * math.sin(math.pi * t)
            outer.append((hand[0] + math.cos(a) * length * 1.06 * tension, hand[1] + math.sin(a) * length * 1.06 * tension))
            inner.append((hand[0] + math.cos(a) * length * 0.54, hand[1] + math.sin(a) * length * 0.54))
        canvas.poly(outer + inner[::-1], (255, 240, 196, 42))
        for a, b in zip(outer, outer[1:]):
            canvas.line(a, b, (255, 250, 224, 120), 2)
    canvas.poly(blade, (*pal.IRON[2], 255))
    canvas.line(base, tip, (*pal.IRON[4], 255), 2)
    canvas.line(
        (base[0] + px * 1.2, base[1] + py * 1.2),
        (tip[0], tip[1]),
        (*pal.IRON[5], 255),
        1,
    )
    canvas.line(
        (base[0] - px * 1.2, base[1] - py * 1.2),
        (tip[0] - dx, tip[1] - dy),
        (*pal.IRON[4], 200),
        1,
    )
    canvas.line(
        (base[0] - px * 1.4, base[1] - py * 1.4),
        (tip[0] - dx * 2, tip[1] - dy * 2),
        (*pal.IRON[1], 255),
        1,
    )
    guard_a = (base[0] + px * 4, base[1] + py * 4)
    guard_b = (base[0] - px * 4, base[1] - py * 4)
    canvas.line(guard_a, guard_b, (*grip_color, 255), 2)
    grip_end = (hand[0] - dx * 3, hand[1] - dy * 3)
    canvas.line(base, grip_end, (*pal.LEATHER[2], 255), 3)
    canvas.circle(grip_end[0], grip_end[1], 1.8, (*grip_color, 255))


# --------------------------------------------------------------------- héroe

HERO_W, HERO_H = 52, 50
HERO_PIVOT = (20, 48)


def hero_frame(
    *,
    bob: float = 0.0,
    lean: float = 0.0,
    step: float = 0.0,
    arm_swing: float = 0.0,
    cape_sway: float = 0.0,
    cape_lift: float = 0.0,
    sword_angle: float = 1.35,
    head_drop: float = 0.0,
    crouch: float = 0.0,
    fallen: float = 0.0,
    smear: bool = False,
) -> Canvas:
    canvas = Canvas(HERO_W, HERO_H)
    cx = 20.0 + lean
    ground = 48.0
    shift = -bob + crouch
    shoulder_y = 20.0 + shift
    hip_y = 33.0 + shift + crouch * 0.3

    # ------------------------------------------------------------- capa
    top = shoulder_y + 1
    bottom = 45.0 + shift * 0.25 - cape_lift
    cape = [
        (cx - 10, top),
        (cx + 8, top),
        (cx + 13 + cape_sway, bottom - 2),
        (cx + 8 + cape_sway, bottom + 1),
        (cx + 3 + cape_sway * 0.8, bottom - 3),
        (cx - 1 + cape_sway * 0.6, bottom + 1),
        (cx - 6 + cape_sway * 0.4, bottom - 2),
        (cx - 12 + cape_sway * 0.5, bottom + 1),
    ]
    canvas.poly(cape, (*pal.CAPE[1], 255))
    inner_cape = [
        (cx - 8, top + 2),
        (cx + 6, top + 2),
        (cx + 10 + cape_sway, bottom - 4),
        (cx + 4 + cape_sway * 0.8, bottom - 1),
        (cx - 2 + cape_sway * 0.6, bottom - 4),
        (cx - 9 + cape_sway * 0.5, bottom - 1),
    ]
    canvas.poly(inner_cape, (*pal.CAPE[2], 255))
    canvas.line(
        (cx - 9, top + 1), (cx - 11 + cape_sway * 0.4, bottom), (*pal.CAPE[3], 230)
    )
    canvas.line(
        (cx + 7, top + 2), (cx + 11 + cape_sway, bottom - 3), (*pal.CAPE[0], 220)
    )

    # ------------------------------------------------- pierna y brazo lejanos
    far = -step * 4.0
    _limb(
        canvas,
        (cx - 4, hip_y),
        (cx - 6 + far, hip_y + 6),
        6,
        darken(pal.IRON[1], 8),
        pal.IRON[2],
    )
    _limb(
        canvas,
        (cx - 6 + far, hip_y + 6),
        (cx - 7 + far * 1.5, ground - 4),
        5,
        darken(pal.IRON[1], 16),
        pal.IRON[2],
    )
    canvas.circle(cx - 6 + far, hip_y + 6, 2.2, (*pal.IRON[2], 255))
    canvas.rect(int(cx - 11 + far * 1.5), int(ground - 6), 9, 5, (*pal.IRON[1], 255))
    canvas.line(
        (cx - 11 + far * 1.5, ground - 6),
        (cx - 2 + far * 1.5, ground - 6),
        (*pal.IRON[3], 200),
    )
    canvas.line(
        (cx - 11 + far * 1.5, ground - 2),
        (cx - 2 + far * 1.5, ground - 2),
        (*pal.LEATHER[1], 235),
    )
    _limb(
        canvas,
        (cx - 7, shoulder_y + 3),
        (cx - 10 - arm_swing * 2, shoulder_y + 9),
        5,
        darken(pal.IRON[1], 6),
        pal.IRON[2],
    )

    # ------------------------------------------------------------- torso
    torso = [
        (cx - 9, shoulder_y),
        (cx + 9, shoulder_y),
        (cx + 7, hip_y),
        (cx - 7, hip_y),
    ]
    canvas.poly(torso, (*pal.IRON[1], 255))
    canvas.poly(
        [(cx - 9, shoulder_y), (cx - 3, shoulder_y), (cx - 2, hip_y), (cx - 7, hip_y)],
        (*pal.IRON[2], 255),
    )
    canvas.poly(
        [(cx + 4, shoulder_y), (cx + 9, shoulder_y), (cx + 7, hip_y), (cx + 3, hip_y)],
        (*pal.IRON[0], 255),
    )
    # Peto con bisel
    chest = [(cx - 5, shoulder_y + 2), (cx + 4, shoulder_y + 2), (cx + 3, hip_y - 2), (cx - 4, hip_y - 2)]
    canvas.poly(chest, (*pal.IRON[2], 255))
    canvas.line(chest[0], chest[1], (*pal.IRON[4], 255))
    canvas.line(chest[0], chest[3], (*pal.IRON[3], 220))
    canvas.line(chest[1], chest[2], (*pal.IRON[0], 255))
    for index in range(2):
        canvas.px(cx - 6 + index * 11, shoulder_y + 3, (*pal.IRON[4], 255))

    # Tabardo
    tabard = [
        (cx - 3, shoulder_y + 3),
        (cx + 3, shoulder_y + 3),
        (cx + 4, hip_y + 3),
        (cx, hip_y + 6),
        (cx - 4, hip_y + 3),
    ]
    canvas.poly(tabard, (*pal.TEAL[1], 255))
    canvas.line((cx - 2, shoulder_y + 4), (cx - 2, hip_y + 2), (*pal.TEAL[3], 220))
    canvas.line((cx + 2, shoulder_y + 4), (cx + 3, hip_y + 2), (*pal.TEAL[0], 230))
    # Emblema de yunque
    canvas.rect(int(cx - 2), int(shoulder_y + 8), 4, 2, (*pal.GOLD[2], 255))
    canvas.rect(int(cx - 1), int(shoulder_y + 10), 2, 2, (*pal.GOLD[2], 255))

    # Cinturón
    canvas.rect(int(cx - 7), int(hip_y - 3), 14, 4, (*pal.LEATHER[2], 255))
    canvas.line((cx - 7, hip_y - 3), (cx + 6, hip_y - 3), (*pal.LEATHER[4], 200))
    canvas.rect(int(cx - 1), int(hip_y - 3), 3, 4, (*pal.GOLD[2], 255))
    canvas.px(cx, hip_y - 2, (*pal.GOLD[4], 255))

    # ------------------------------------------------------- pierna cercana
    near = step * 4.6
    _limb(
        canvas,
        (cx + 4, hip_y),
        (cx + 6 + near, hip_y + 6),
        6,
        pal.IRON[2],
        pal.IRON[4],
    )
    _limb(
        canvas,
        (cx + 6 + near, hip_y + 6),
        (cx + 7 + near * 1.5, ground - 4),
        5,
        pal.IRON[2],
        pal.IRON[4],
    )
    canvas.circle(cx + 6 + near, hip_y + 6, 2.4, (*pal.IRON[3], 255))
    canvas.px(cx + 6 + near, hip_y + 5, (*pal.IRON[5], 255))
    canvas.rect(int(cx + 3 + near * 1.5), int(ground - 6), 10, 5, (*pal.IRON[2], 255))
    canvas.line(
        (cx + 3 + near * 1.5, ground - 6),
        (cx + 12 + near * 1.5, ground - 6),
        (*pal.IRON[5], 230),
    )
    canvas.line(
        (cx + 3 + near * 1.5, ground - 2),
        (cx + 12 + near * 1.5, ground - 2),
        (*pal.LEATHER[2], 235),
    )
    canvas.line(
        (cx + 3 + near * 1.5, ground - 4),
        (cx + 12 + near * 1.5, ground - 4),
        (*pal.IRON[1], 220),
    )

    # -------------------------------------------------------- tassets / faldón
    plates = (
        (cx - 9, 6, -1.0),
        (cx - 3, 7, 0.0),
        (cx + 3, 6, 0.8),
    )
    for index, (plate_x, plate_w, tilt) in enumerate(plates):
        top_y = hip_y - 2
        bottom_y = hip_y + 7 - index * 0.6
        canvas.poly(
            [
                (plate_x, top_y),
                (plate_x + plate_w, top_y),
                (plate_x + plate_w - 1 + tilt, bottom_y),
                (plate_x + 1 + tilt, bottom_y + 1),
            ],
            (*pal.IRON[1], 255),
        )
        canvas.line(
            (plate_x + 1, top_y + 1),
            (plate_x + plate_w - 1, top_y + 1),
            (*pal.IRON[3], 235),
        )
        canvas.line(
            (plate_x + 1 + tilt, bottom_y),
            (plate_x + plate_w - 2 + tilt, bottom_y),
            (*pal.IRON[0], 235),
        )
        canvas.px(plate_x + plate_w / 2, top_y + 2, (*pal.IRON[3], 255))

    # --------------------------------------------------------- hombreras
    canvas.ellipse(int(cx - 15), int(shoulder_y - 3), 11, 10, (*pal.IRON[0], 255))
    canvas.ellipse(int(cx - 14), int(shoulder_y - 3), 9, 7, (*pal.IRON[1], 255))
    canvas.ellipse(int(cx - 13), int(shoulder_y - 2), 5, 3, (*pal.IRON[2], 255))
    canvas.ellipse(int(cx + 4), int(shoulder_y - 4), 12, 11, (*pal.IRON[1], 255))
    canvas.ellipse(int(cx + 5), int(shoulder_y - 4), 10, 8, (*pal.IRON[2], 255))
    canvas.ellipse(int(cx + 6), int(shoulder_y - 3), 6, 3, (*pal.IRON[3], 255))
    canvas.line(
        (cx + 5, shoulder_y - 3), (cx + 12, shoulder_y + 1), (*pal.IRON[4], 220)
    )
    canvas.line(
        (cx + 13, shoulder_y - 1), (cx + 13, shoulder_y + 4), (*pal.EMBER[2], 110)
    )
    canvas.line(
        (cx + 5, shoulder_y + 2), (cx + 13, shoulder_y + 4), (*pal.IRON[0], 220)
    )
    canvas.px(cx + 9, shoulder_y + 1, (*pal.GOLD[2], 255))
    canvas.px(cx - 9, shoulder_y + 1, (*pal.GOLD[2], 255))

    # ------------------------------------------------------------- cabeza
    head_y = shoulder_y - 16 + head_drop
    canvas.rect(int(cx - 3), int(head_y + 13), 6, 5, (*pal.IRON[0], 255))
    canvas.rect(int(cx - 2), int(head_y + 14), 4, 3, (*pal.IRON[1], 255))
    # Yelmo: cúpula, ala y guardajaw
    canvas.ellipse(int(cx - 7), int(head_y), 14, 16, (*pal.IRON[1], 255))
    canvas.ellipse(int(cx - 6), int(head_y), 12, 13, (*pal.IRON[2], 255))
    canvas.ellipse(int(cx - 5), int(head_y + 1), 9, 9, (*pal.IRON[3], 255))
    canvas.rect(int(cx - 8), int(head_y + 6), 16, 2, (*pal.IRON[2], 255))
    canvas.line((cx - 8, head_y + 6), (cx + 7, head_y + 6), (*pal.IRON[4], 235))
    canvas.poly(
        [
            (cx - 7, head_y + 8),
            (cx + 7, head_y + 8),
            (cx + 5, head_y + 16),
            (cx - 5, head_y + 16),
        ],
        (*pal.IRON[1], 255),
    )
    canvas.poly(
        [(cx - 7, head_y + 8), (cx - 4, head_y + 8), (cx - 3, head_y + 16), (cx - 5, head_y + 16)],
        (*pal.IRON[2], 255),
    )
    # Visor
    canvas.rect(int(cx - 6), int(head_y + 8), 12, 3, (*pal.VOID, 255))
    canvas.rect(int(cx - 5), int(head_y + 9), 10, 1, (*pal.CYAN[2], 255))
    canvas.rect(int(cx - 4), int(head_y + 9), 6, 1, (*pal.CYAN[4], 255))
    canvas.px(cx + 4, head_y + 9, (*pal.CYAN[5], 255))
    canvas.px(cx - 5, head_y + 9, (*pal.CYAN[3], 255))
    # Luz de borde izquierda del yelmo (fuente: arriba-izquierda)
    canvas.line((cx - 6, head_y + 2), (cx - 6, head_y + 12), (*pal.IRON[5], 220))
    canvas.px(cx - 5, head_y + 1, (*pal.IRON[5], 255))
    canvas.px(cx - 8, head_y + 7, (*pal.IRON[4], 230))
    # Rebote cálido de la forja en el lado derecho
    canvas.line((cx + 6, head_y + 4), (cx + 6, head_y + 10), (*pal.EMBER[2], 120))
    # Cresta teal
    canvas.poly(
        [
            (cx - 2, head_y + 1),
            (cx + 1, head_y - 5),
            (cx + 5 + cape_sway * 0.4, head_y - 1),
            (cx + 2, head_y + 2),
        ],
        (*pal.TEAL[2], 255),
    )
    canvas.line(
        (cx, head_y - 3), (cx + 4 + cape_sway * 0.4, head_y - 1), (*pal.TEAL[4], 230)
    )
    canvas.px(cx + 4, head_y + 3, (*pal.IRON[5], 255))
    canvas.px(cx + 5, head_y + 4, (*pal.IRON[4], 220))
    # Cuello
    canvas.rect(int(cx - 3), int(head_y + 15), 6, 3, (*pal.IRON[0], 255))

    # ------------------------------------------------ brazo cercano + espada
    elbow = (cx + 9, shoulder_y + 7)
    hand = (cx + 11 + arm_swing * 1.5, shoulder_y + 12)
    _limb(canvas, (cx + 6, shoulder_y + 3), elbow, 6, pal.IRON[2], pal.IRON[4])
    _limb(canvas, elbow, hand, 5, pal.IRON[3], pal.IRON[5])
    canvas.circle(hand[0], hand[1], 2.6, (*pal.IRON[3], 255))
    canvas.px(hand[0] - 1, hand[1] - 1, (*pal.IRON[5], 255))
    _sword(canvas, hand, sword_angle, 19.0, smear=smear)

    if fallen > 0:
        canvas = _fallen(canvas, fallen)

    canvas.add_outline((*pal.VOID, 255))
    return canvas


def _fallen(canvas: Canvas, progress: float) -> Canvas:
    """Cuerpo derribado: el guerrero cae hacia la izquierda y la espada queda suelta."""
    if progress < 0.4:
        return canvas
    fallen = Canvas(HERO_W, HERO_H)
    y = 43.0
    fallen.blit(canvas, (0, 0))
    fallen.ellipse(4, int(y + 1), 30, 7, (10, 9, 15, 190))
    # Capa extendida
    fallen.poly([(4, y + 2), (30, y - 1), (34, y + 2), (8, y + 5)], (*pal.CAPE[1], 255))
    fallen.poly([(6, y + 2), (26, y), (29, y + 2), (9, y + 4)], (*pal.CAPE[2], 255))
    # Torso y piernas
    fallen.poly([(12, y), (25, y - 4), (30, y), (15, y + 3)], (*pal.IRON[1], 255))
    fallen.poly([(13, y - 1), (24, y - 4), (27, y - 1), (14, y + 1)], (*pal.IRON[2], 255))
    fallen.rect(27, int(y - 2), 9, 3, (*pal.IRON[1], 255))
    fallen.rect(34, int(y - 1), 7, 3, (*pal.LEATHER[1], 255))
    # Yelmo caído
    fallen.ellipse(8, int(y - 7), 10, 9, (*pal.IRON[2], 255))
    fallen.ellipse(9, int(y - 6), 8, 6, (*pal.IRON[3], 255))
    fallen.rect(9, int(y - 4), 7, 2, (*pal.VOID, 255))
    fallen.rect(10, int(y - 4), 4, 1, (*pal.CYAN[2], 220))
    fallen.poly([(10, y - 7), (12, y - 10), (15, y - 7)], (*pal.TEAL[2], 255))
    # Espada suelta
    fallen.line((31, y - 4), (45, y - 12), (*pal.IRON[2], 255), 3)
    fallen.line((31, y - 5), (44, y - 12), (*pal.IRON[4], 220), 1)
    fallen.line((29, y - 2), (33, y - 5), (*pal.GOLD[2], 255), 2)
    fallen.add_outline((*pal.VOID, 255))
    return fallen


def build_hero_frames() -> list[tuple[str, Canvas]]:
    frames: list[tuple[str, Canvas]] = []

    for index, (bob, sway) in enumerate(((0, 0), (1, 0.8), (1, 1.6), (0, 0.8))):
        frames.append(
            (
                f"idle_{index}",
                hero_frame(bob=bob, cape_sway=sway, sword_angle=1.34 + index * 0.02),
            )
        )

    for index in range(6):
        phase = math.tau * index / 6.0
        step = math.sin(phase)
        frames.append(
            (
                f"walk_{index}",
                hero_frame(
                    bob=0.5 + 0.5 * abs(math.sin(phase)),
                    step=step,
                    arm_swing=-step * 0.7,
                    cape_sway=step * 1.8,
                    sword_angle=1.36 + step * 0.05,
                ),
            )
        )

    for index in range(6):
        phase = math.tau * index / 6.0
        step = math.sin(phase)
        frames.append(
            (
                f"run_{index}",
                hero_frame(
                    bob=1.0 + 0.7 * abs(math.sin(phase)),
                    lean=2,
                    step=step * 1.4,
                    arm_swing=-step * 1.2,
                    cape_sway=step * 2.6,
                    cape_lift=3,
                    sword_angle=1.42 + step * 0.1,
                ),
            )
        )

    frames.append(
        ("attack_0", hero_frame(bob=1, lean=-3, arm_swing=-1.6, cape_sway=-2, sword_angle=-2.25))
    )
    frames.append(
        (
            "attack_1",
            hero_frame(bob=0, lean=3, arm_swing=1.0, cape_sway=3, sword_angle=-0.15, smear=True),
        )
    )
    frames.append(
        ("attack_2", hero_frame(bob=1, lean=1, arm_swing=0.3, cape_sway=1, sword_angle=0.65))
    )

    frames.append(
        ("hurt_0", hero_frame(bob=1, lean=-4, head_drop=2, cape_sway=-3, sword_angle=1.6))
    )
    frames.append(
        ("hurt_1", hero_frame(bob=2, lean=-2, head_drop=1, cape_sway=-1, sword_angle=1.45))
    )

    frames.append(
        ("die_0", hero_frame(bob=2, lean=-3, head_drop=3, cape_sway=-2, sword_angle=1.75))
    )
    frames.append(
        ("die_1", hero_frame(bob=7, lean=-1, head_drop=5, crouch=4, cape_sway=-3, sword_angle=1.95))
    )
    frames.append(
        ("die_2", hero_frame(bob=12, lean=3, head_drop=6, crouch=9, cape_sway=2, sword_angle=2.15))
    )
    frames.append(
        ("die_3", hero_frame(bob=14, lean=6, head_drop=7, crouch=12, cape_sway=3, fallen=0.6))
    )
    frames.append(
        ("die_4", hero_frame(bob=14, lean=6, head_drop=7, crouch=12, cape_sway=3, fallen=0.85))
    )
    frames.append(
        ("die_5", hero_frame(bob=14, lean=6, head_drop=7, crouch=12, cape_sway=3, fallen=1.0))
    )

    return frames


HERO_CLIPS: dict[str, dict[str, object]] = {
    "idle": {
        "frames": ["idle_0", "idle_1", "idle_2", "idle_3"],
        "loop": True,
        "duration_ms": 170,
        "interrupt_priority": 0,
    },
    "walk": {
        "frames": [f"walk_{i}" for i in range(6)],
        "loop": True,
        "duration_ms": 95,
        "interrupt_priority": 1,
        "events": {0: "dust_step", 3: "dust_step"},
    },
    "run": {
        "frames": [f"run_{i}" for i in range(6)],
        "loop": True,
        "duration_ms": 75,
        "interrupt_priority": 1,
        "events": {0: "dust_step", 3: "dust_step"},
    },
    "attack": {
        "frames": ["attack_0", "attack_1", "attack_2"],
        "loop": False,
        "duration_ms": 105,
        "interrupt_priority": 3,
        "events": {1: "slash_spark"},
        "hitbox": (1, (6, -24, 28, 28), 15.0),
    },
    "hurt": {
        "frames": ["hurt_0", "hurt_1"],
        "loop": False,
        "duration_ms": 90,
        "interrupt_priority": 5,
    },
    "die": {
        "frames": [f"die_{i}" for i in range(6)],
        "loop": False,
        "duration_ms": 130,
        "interrupt_priority": 9,
    },
}


# -------------------------------------------------------------------- enemigos

SLIME_W, SLIME_H = 32, 32


def slime_frame(
    squash: float = 0.0,
    look: float = 0.0,
    inflate: float = 0.0,
    death: float = 0.0,
) -> Canvas:
    canvas = Canvas(SLIME_W, SLIME_H)
    if death > 0.75:
        canvas.ellipse(3, 25, 26, 6, (*pal.SLIME[0], 240))
        canvas.ellipse(5, 25, 22, 5, (*pal.SLIME[1], 210))
        canvas.ellipse(9, 26, 12, 3, (*pal.SLIME[2], 200))
        canvas.px(16, 26, (*pal.SLIME[4], 220))
        return canvas

    center_y = 25.5 - 4.0 * squash - death * 5
    rx = 12.5 + squash * 1.8 + inflate
    ry = 9.0 - squash * 1.4 - death * 3
    points: list[tuple[float, float]] = []
    steps = 24
    for index in range(steps):
        angle = math.tau * index / steps
        wobble = 1.0 + 0.055 * math.sin(angle * 3 + squash * 6)
        points.append(
            (16 + math.cos(angle) * rx * wobble, center_y + math.sin(angle) * ry * wobble)
        )
    canvas.poly(points, (*pal.SLIME[0], 255))
    body = [(16 + (x - 16) * 0.94, center_y + (y - center_y) * 0.9 - 0.4) for x, y in points]
    canvas.poly(body, (*pal.SLIME[1], 255))
    # Volumen: banda superior iluminada y núcleo interno
    upper = [(16 + (x - 16) * 0.72, center_y - 1 + (y - center_y) * 0.6) for x, y in points]
    canvas.poly(upper, (*pal.SLIME[2], 255))
    core = [(16 + (x - 16) * 0.4, center_y + 1.5 + (y - center_y) * 0.34) for x, y in points]
    canvas.poly(core, (*pal.SLIME[1], 235))
    canvas.ellipse(8, int(center_y - ry * 0.85), 8, 4, (*pal.SLIME[4], 200))
    canvas.ellipse(9, int(center_y - ry * 0.8), 4, 2, (*pal.SLIME[5], 235))
    # Ojos con cuenca
    eye_y = int(center_y - 2)
    for base_x, side in ((11, -1), (19, 1)):
        ex = int(base_x + look * 2)
        canvas.ellipse(ex - 1, eye_y - 1, 6, 7, (*pal.SLIME[0], 200))
        canvas.ellipse(ex, eye_y, 4, 5, (14, 40, 26, 255))
        canvas.circle(ex + 2, eye_y + 2, 1.5, (240, 255, 235, 255))
        canvas.px(ex + 2 + int(look), eye_y + 2, (12, 24, 18, 255))
        canvas.px(ex + 1, eye_y + 1, (255, 255, 250, 220))
    # Boca entreabierta
    canvas.line((13, eye_y + 7), (19, eye_y + 7), (*pal.SLIME[0], 230), 1)
    canvas.px(13, eye_y + 8, (*pal.SLIME[0], 160))
    canvas.px(19, eye_y + 8, (*pal.SLIME[0], 160))
    if death == 0:
        rng = random.Random(int((squash + 1) * 57))
        for _ in range(2):
            dx = rng.randrange(6, 26)
            canvas.rect(dx, int(center_y + ry - 1), 1, 2, (*pal.SLIME[2], 190))
    canvas.add_outline((*pal.VOID, 235))
    return canvas


WISP_W, WISP_H = 32, 32


def wisp_frame(flicker: float = 0.0, open_eyes: bool = True, dim: float = 0.0) -> Canvas:
    canvas = Canvas(WISP_W, WISP_H)
    cx, cy = 16.0, 17.0
    scale = 1.0 - dim * 0.55
    for radius, alpha in ((12, 34), (9, 52), (6, 70)):
        canvas.circle(cx, cy - 1, radius * scale, rgba(pal.ARCANE[2], alpha))
    # Llama exterior con tres lenguas
    flame = [
        (cx - 7 * scale, cy + 7),
        (cx - 8 * scale, cy - 1),
        (cx - 5 * scale + flicker * 0.6, cy - 7 - flicker),
        (cx - 2, cy - 3),
        (cx + flicker * 0.8, cy - 12 + flicker * 0.4),
        (cx + 3, cy - 4),
        (cx + 6 * scale - flicker * 0.4, cy - 8 + flicker),
        (cx + 8 * scale, cy + 1),
        (cx + 6 * scale, cy + 8),
        (cx, cy + 10),
    ]
    canvas.poly(flame, (*pal.ARCANE[2], 255))
    canvas.poly(
        [
            (cx - 5 * scale, cy + 6),
            (cx - 5 * scale + flicker * 0.4, cy - 1),
            (cx - 1, cy - 7 + flicker * 0.3),
            (cx + 3, cy - 1),
            (cx + 5 * scale, cy - 6 + flicker * 0.5),
            (cx + 5.5 * scale, cy + 5),
            (cx, cy + 8),
        ],
        (*pal.ARCANE[4], 255),
    )
    inner = [
        (cx - 3 * scale, cy + 5),
        (cx - 3 * scale + flicker * 0.3, cy),
        (cx - 1, cy - 5),
        (cx + 2, cy - 1),
        (cx + 3 * scale, cy + 1),
        (cx + 3 * scale, cy + 5),
        (cx, cy + 7),
    ]
    canvas.poly(inner, (*pal.CYAN[2], 255))
    canvas.poly(
        [(cx - 1.5, cy + 4), (cx - 1 + flicker * 0.2, cy - 1), (cx + 1, cy - 4), (cx + 1.5, cy + 4)],
        (*pal.CYAN[4], 255),
    )
    canvas.circle(cx, cy - 0.5, 2.0, (*pal.CYAN[5], 255))
    if open_eyes:
        for side, ex in ((-1, 12), (1, 18)):
            canvas.ellipse(ex, 14, 3, 4, (12, 10, 22, 245))
            canvas.rect(ex + 1, 15, 2, 2, (*pal.CYAN[5], 255))
        canvas.line((15, 19), (18, 20), (12, 10, 22, 190))
    for index in range(3):
        angle = flicker * 2.0 + index * math.tau / 3
        sx = cx + math.cos(angle) * (9 + index * 0.6)
        sy = cy - 2 + math.sin(angle) * (6.5 + index * 0.4)
        canvas.px(sx, sy, (*pal.ARCANE[5], 230))
        if index == 0:
            canvas.px(sx - 1, sy + 1, (*pal.ARCANE[4], 160))
    canvas.add_outline((*pal.VOID, 210))
    return canvas


BRUTE_W, BRUTE_H = 48, 48
BRUTE_PIVOT = (24, 46)


def brute_frame(
    *,
    bob: float = 0.0,
    step: float = 0.0,
    cleaver_angle: float = 1.9,
    lean: float = 0.0,
    glow: float = 0.0,
    death: float = 0.0,
) -> Canvas:
    canvas = Canvas(BRUTE_W, BRUTE_H)
    cx = 24.0 + lean
    ground = 46.0
    shift = -bob
    if death > 0.5:
        canvas.ellipse(6, 37, 36, 9, (10, 8, 11, 210))
        canvas.poly([(8, 41), (34, 35), (42, 41), (14, 45)], (*pal.FLESH[0], 255))
        canvas.poly([(10, 40), (33, 35), (38, 39), (16, 43)], (*pal.FLESH[1], 255))
        canvas.ellipse(33, 33, 13, 10, (*pal.FLESH[1], 255))
        canvas.ellipse(34, 34, 10, 7, (*pal.FLESH[2], 255))
        canvas.circle(39, 36, 2.2, (*pal.EMBER[4], 240))
        canvas.circle(35, 37, 1.6, (*pal.EMBER[3], 200))
        canvas.line((30, 40), (12, 44), (*pal.BONE[2], 220), 2)
        canvas.add_outline((*pal.VOID, 255))
        return canvas

    # Piernas
    for side, base_color in ((-1, pal.FLESH[0]), (1, pal.FLESH[1])):
        swing = step * 2.6 * side
        hip = (cx + side * 5, 32 + shift)
        knee = (cx + side * 6 + swing, 38 + shift)
        foot = (cx + side * 7 + swing * 1.4, ground - 3)
        _limb(canvas, hip, knee, 9, base_color, lighten(base_color, 12))
        _limb(canvas, knee, foot, 8, base_color, lighten(base_color, 10))
        canvas.rect(int(foot[0] - 5), int(ground - 5), 10, 5, (*pal.LEATHER[1], 255))
        canvas.line((foot[0] - 5, ground - 5), (foot[0] + 4, ground - 5), (*pal.LEATHER[3], 190))
        canvas.px(foot[0] + 3, ground - 4, (*pal.IRON[2], 220))

    # Torso en bandas de volumen
    torso = [
        (cx - 13, 19 + shift),
        (cx + 10, 17 + shift),
        (cx + 13, 33 + shift),
        (cx - 11, 35 + shift),
    ]
    canvas.poly(torso, (*pal.FLESH[1], 255))
    canvas.poly(
        [(cx - 13, 19 + shift), (cx - 4, 18 + shift), (cx - 3, 34 + shift), (cx - 11, 35 + shift)],
        (*pal.FLESH[2], 255),
    )
    canvas.poly(
        [(cx + 4, 18 + shift), (cx + 10, 17 + shift), (cx + 13, 33 + shift), (cx + 4, 34 + shift)],
        (*pal.FLESH[0], 255),
    )
    # Placa de hierro en el pecho
    plate = [(cx - 11, 21 + shift), (cx + 1, 20 + shift), (cx + 1, 31 + shift), (cx - 10, 32 + shift)]
    canvas.poly(plate, (*pal.IRON[1], 255))
    canvas.line(plate[0], plate[1], (*pal.IRON[3], 255))
    canvas.line(plate[0], plate[3], (*pal.IRON[2], 220))
    for offset in (3, 7):
        canvas.px(cx - 8 + offset, 24 + shift, (*pal.IRON[4], 255))
    # Grietas de escoria
    crack = [(cx + 3, 21), (cx + 5, 25), (cx + 2, 28), (cx + 4, 32)]
    lifted = [(x, y + shift) for x, y in crack]
    for a, b in zip(lifted, lifted[1:]):
        canvas.line(a, b, (*pal.EMBER[1], 255), 2)
        canvas.line(a, b, (*pal.EMBER[3], int(140 + 100 * glow)), 1)
    canvas.line((cx + 8, 26 + shift), (cx + 9, 29 + shift), (*pal.EMBER[2], 200))

    # Cabeza hundida
    head_y = 10 + shift
    canvas.ellipse(int(cx - 7), int(head_y), 15, 13, (*pal.FLESH[0], 255))
    canvas.ellipse(int(cx - 6), int(head_y + 1), 13, 11, (*pal.FLESH[2], 255))
    canvas.ellipse(int(cx - 5), int(head_y + 1), 9, 7, (*pal.FLESH[3], 255))
    canvas.rect(int(cx - 2), int(head_y + 8), 7, 4, (*pal.FLESH[1], 255))
    # Cuernos
    canvas.poly(
        [(cx - 7, head_y + 2), (cx - 12, head_y - 6), (cx - 4, head_y + 1)], (*pal.BONE[1], 255)
    )
    canvas.poly(
        [(cx + 6, head_y + 2), (cx + 11, head_y - 7), (cx + 3, head_y)], (*pal.BONE[2], 255)
    )
    canvas.line((cx - 11, head_y - 5), (cx - 6, head_y + 1), (*pal.BONE[3], 200))
    # Ojos de brasa
    for ex in (cx - 2, cx + 3):
        canvas.circle(ex, head_y + 5, 2.0, (*pal.EMBER[2], 255))
        canvas.circle(ex, head_y + 5, 1.2, (*pal.EMBER[5], 255))
    canvas.line((cx - 1, head_y + 9), (cx + 4, head_y + 9), (*pal.FLESH[0], 255))

    # Brazo izquierdo enorme
    shoulder = (cx + 10, 22 + shift)
    elbow = (cx + 15, 25 + shift)
    hand = (cx + 18, 30 + shift)
    canvas.ellipse(int(cx + 5), int(17 + shift), 14, 12, (*pal.BONE[1], 255))
    canvas.ellipse(int(cx + 6), int(18 + shift), 11, 9, (*pal.BONE[2], 255))
    _limb(canvas, shoulder, elbow, 11, pal.FLESH[1], pal.FLESH[3])
    _limb(canvas, elbow, hand, 9, pal.FLESH[2], pal.FLESH[3])
    canvas.circle(hand[0], hand[1], 3.6, (*pal.FLESH[1], 255))
    canvas.px(hand[0] - 1, hand[1] - 1, (*pal.FLESH[3], 255))

    # Mandoble de escoria
    dx, dy = math.cos(cleaver_angle), math.sin(cleaver_angle)
    px, py = -dy, dx
    tip = (hand[0] + dx * 20, hand[1] + dy * 20)
    blade = [
        (hand[0] + px * 3, hand[1] + py * 3),
        (tip[0] + px * 2.5, tip[1] + py * 2.5),
        (tip[0] - px * 3.5, tip[1] - py * 3.5),
        (hand[0] - px * 4, hand[1] - py * 4),
    ]
    canvas.poly(blade, (*pal.IRON[1], 255))
    canvas.poly(
        [
            (hand[0] + px * 1, hand[1] + py * 1),
            (tip[0] + px * 1.5, tip[1] + py * 1.5),
            (tip[0] - px * 1.5, tip[1] - py * 1.5),
            (hand[0] - px * 2, hand[1] - py * 2),
        ],
        (*pal.IRON[2], 255),
    )
    canvas.line(
        (hand[0] + px * 3, hand[1] + py * 3),
        (tip[0] + px * 2.5, tip[1] + py * 2.5),
        (*pal.IRON[4], 240),
        1,
    )
    canvas.line(
        (hand[0] - dx * 2, hand[1] - dy * 2),
        (hand[0] + dx * 9, hand[1] + dy * 9),
        (*pal.BLOOD[2], 220),
        2,
    )
    canvas.line(
        (hand[0] + px * 5, hand[1] + py * 5),
        (hand[0] - px * 5, hand[1] - py * 5),
        (*pal.IRON[2], 255),
        3,
    )
    canvas.circle(hand[0] - dx * 4, hand[1] - dy * 4, 2, (*pal.LEATHER[2], 255))

    # Brazo derecho corto con pincho
    _limb(canvas, (cx - 11, 23 + shift), (cx - 15, 29 + shift), 8, pal.FLESH[0], pal.FLESH[1])
    canvas.circle(cx - 15, 30 + shift, 3.2, (*pal.FLESH[1], 255))
    canvas.poly(
        [(cx - 17, 30 + shift), (cx - 20, 34 + shift), (cx - 14, 32 + shift)], (*pal.BONE[2], 255)
    )

    canvas.add_outline((*pal.VOID, 255))
    return canvas


def build_slime_frames() -> list[tuple[str, Canvas]]:
    frames: list[tuple[str, Canvas]] = []
    for index, squash in enumerate((0.0, 0.3, 0.45, 0.3)):
        frames.append((f"idle_{index}", slime_frame(squash=squash)))
    for index in range(4):
        phase = math.tau * index / 4
        frames.append(
            (
                f"walk_{index}",
                slime_frame(squash=0.45 + 0.45 * math.sin(phase), look=math.sin(phase) * 0.6),
            )
        )
    frames.append(("attack_0", slime_frame(squash=-0.35, inflate=1.5)))
    frames.append(("attack_1", slime_frame(squash=0.75, inflate=1.0)))
    frames.append(("hurt_0", slime_frame(squash=0.85)))
    frames.append(("hurt_1", slime_frame(squash=0.15)))
    for index, death in enumerate((0.2, 0.45, 0.7, 1.0)):
        frames.append((f"die_{index}", slime_frame(squash=0.9 - death * 0.5, death=death)))
    return frames


def build_wisp_frames() -> list[tuple[str, Canvas]]:
    frames: list[tuple[str, Canvas]] = []
    for index, flicker in enumerate((0.0, 0.6, 1.2, 0.6, 0.0, -0.6)):
        frames.append((f"idle_{index}", wisp_frame(flicker=flicker, open_eyes=index % 3 != 2)))
    for index, flicker in enumerate((0.8, -0.4, 0.5, -0.8)):
        frames.append((f"walk_{index}", wisp_frame(flicker=flicker)))
    frames.append(("shoot_0", wisp_frame(flicker=1.4, open_eyes=False)))
    frames.append(("shoot_1", wisp_frame(flicker=2.0, open_eyes=False)))
    frames.append(("hurt_0", wisp_frame(flicker=-1.2, open_eyes=False)))
    frames.append(("hurt_1", wisp_frame(flicker=0.4, open_eyes=True)))
    for index, dim in enumerate((0.3, 0.6, 0.85, 1.0)):
        frames.append((f"die_{index}", wisp_frame(flicker=index * 0.4, open_eyes=False, dim=dim)))
    return frames


def build_brute_frames() -> list[tuple[str, Canvas]]:
    frames: list[tuple[str, Canvas]] = []
    for index, bob in enumerate((0.0, 0.8, 1.2, 0.8)):
        frames.append((f"idle_{index}", brute_frame(bob=bob, glow=0.2 + index * 0.1)))
    for index in range(6):
        phase = math.tau * index / 6
        frames.append(
            (
                f"walk_{index}",
                brute_frame(
                    bob=0.6 + 0.6 * abs(math.sin(phase)),
                    step=math.sin(phase),
                    cleaver_angle=1.75 + math.sin(phase) * 0.18,
                    glow=0.3 + 0.3 * abs(math.sin(phase)),
                ),
            )
        )
    frames.append(("windup_0", brute_frame(bob=1, lean=-2, cleaver_angle=-2.1, glow=1.0)))
    frames.append(("windup_1", brute_frame(bob=2, lean=-3, cleaver_angle=-2.5, glow=1.0)))
    frames.append(("charge_0", brute_frame(bob=1, lean=3, step=0.6, cleaver_angle=0.2, glow=0.7)))
    frames.append(("charge_1", brute_frame(bob=0, lean=4, step=1.0, cleaver_angle=0.1, glow=0.9)))
    frames.append(("charge_2", brute_frame(bob=1, lean=3, step=0.2, cleaver_angle=0.3, glow=0.6)))
    frames.append(("attack_0", brute_frame(bob=0, lean=2, cleaver_angle=0.9, glow=0.8)))
    frames.append(("attack_1", brute_frame(bob=1, lean=1, cleaver_angle=1.3, glow=0.4)))
    frames.append(("hurt_0", brute_frame(bob=2, lean=-4, cleaver_angle=2.2, glow=0.9)))
    frames.append(("hurt_1", brute_frame(bob=1, lean=-2, cleaver_angle=2.0, glow=0.5)))
    for index, death in enumerate((0.2, 0.4, 0.6, 0.8, 1.0)):
        frames.append((f"die_{index}", brute_frame(glow=1.0 - death, death=death)))
    return frames


SLIME_CLIPS: dict[str, dict[str, object]] = {
    "idle": {
        "frames": [f"idle_{i}" for i in range(4)],
        "loop": True,
        "duration_ms": 150,
        "interrupt_priority": 0,
    },
    "walk": {
        "frames": [f"walk_{i}" for i in range(4)],
        "loop": True,
        "duration_ms": 130,
        "interrupt_priority": 1,
    },
    "attack": {
        "frames": ["attack_0", "attack_1"],
        "loop": False,
        "duration_ms": 110,
        "interrupt_priority": 3,
    },
    "hurt": {
        "frames": ["hurt_0", "hurt_1"],
        "loop": False,
        "duration_ms": 90,
        "interrupt_priority": 5,
    },
    "die": {
        "frames": [f"die_{i}" for i in range(4)],
        "loop": False,
        "duration_ms": 130,
        "interrupt_priority": 9,
    },
}

WISP_CLIPS: dict[str, dict[str, object]] = {
    "idle": {
        "frames": [f"idle_{i}" for i in range(6)],
        "loop": True,
        "duration_ms": 120,
        "interrupt_priority": 0,
    },
    "walk": {
        "frames": [f"walk_{i}" for i in range(4)],
        "loop": True,
        "duration_ms": 110,
        "interrupt_priority": 1,
    },
    "shoot": {
        "frames": ["shoot_0", "shoot_1"],
        "loop": False,
        "duration_ms": 110,
        "interrupt_priority": 3,
    },
    "hurt": {
        "frames": ["hurt_0", "hurt_1"],
        "loop": False,
        "duration_ms": 90,
        "interrupt_priority": 5,
    },
    "die": {
        "frames": [f"die_{i}" for i in range(4)],
        "loop": False,
        "duration_ms": 120,
        "interrupt_priority": 9,
    },
}

BRUTE_CLIPS: dict[str, dict[str, object]] = {
    "idle": {
        "frames": [f"idle_{i}" for i in range(4)],
        "loop": True,
        "duration_ms": 170,
        "interrupt_priority": 0,
    },
    "walk": {
        "frames": [f"walk_{i}" for i in range(6)],
        "loop": True,
        "duration_ms": 120,
        "interrupt_priority": 1,
    },
    "windup": {
        "frames": ["windup_0", "windup_1"],
        "loop": True,
        "duration_ms": 130,
        "interrupt_priority": 3,
    },
    "charge": {
        "frames": [f"charge_{i}" for i in range(3)],
        "loop": True,
        "duration_ms": 100,
        "interrupt_priority": 3,
    },
    "attack": {
        "frames": ["attack_0", "attack_1"],
        "loop": False,
        "duration_ms": 110,
        "interrupt_priority": 4,
    },
    "hurt": {
        "frames": ["hurt_0", "hurt_1"],
        "loop": False,
        "duration_ms": 90,
        "interrupt_priority": 5,
    },
    "die": {
        "frames": [f"die_{i}" for i in range(5)],
        "loop": False,
        "duration_ms": 140,
        "interrupt_priority": 9,
    },
}
