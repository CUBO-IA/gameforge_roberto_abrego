"""Dibujo procedural de entidades. Sin assets externos."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

import pygame

from game.core.math2d import Vec2, lerp
from game.entities.enemies import Enemy
from game.entities.interactables import Campfire, Chest, ForgeAltar
from game.entities.player import Player
from game.entities.projectiles import Projectile
from game.render import palette
from game.world.camera import Camera

if TYPE_CHECKING:
    from game.render.assets import ArtLibrary


def _screen(position: Vec2, camera: Camera, shake: Vec2) -> tuple[int, int]:
    point = camera.world_to_screen(position, shake)
    return int(point.x), int(point.y)


def draw_shadow(
    surface: pygame.Surface, position: Vec2, camera: Camera, shake: Vec2, width: int, height: int
) -> None:
    x, y = _screen(position, camera, shake)
    pygame.draw.ellipse(
        surface,
        (8, 8, 14),
        pygame.Rect(x - width // 2, y + height // 3, width, height // 2),
    )


def draw_player(
    surface: pygame.Surface,
    player: Player,
    camera: Camera,
    shake: Vec2,
    time: float,
) -> None:
    z = getattr(player, "z", 0.0)
    scale = max(0.35, 1.0 - z / 90.0)
    shadow_w = max(10, int(30 * scale))
    shadow_h = max(6, int(18 * scale))
    draw_shadow(surface, player.position, camera, shake, shadow_w, shadow_h)

    x, y_ground = _screen(player.position, camera, shake)
    y = y_ground - int(z)

    if player.invulnerability > 0.1 and not player.is_dashing:
        if int(time * 24) % 2 == 0:
            return

    anim_player = getattr(player, "anim_player", None)
    if anim_player is not None and getattr(anim_player, "current_surface", None) is not None:
        frame_surf = anim_player.current_surface
        px, py = getattr(anim_player, "current_pivot", (frame_surf.get_width() // 2, frame_surf.get_height()))
        if player.facing.x < 0:
            frame_surf = pygame.transform.flip(frame_surf, True, False)
            px = frame_surf.get_width() - px
        surface.blit(frame_surf, (x - px, y - py))
        return

    angle = player.facing.angle()
    facing = player.facing
    perpendicular = Vec2(-facing.y, facing.x)
    bob = math.sin(time * 7.0) * 1.2

    # Capa detrás del cuerpo.
    cape_center = Vec2(x, y) - facing * 4 + perpendicular * 1
    pygame.draw.polygon(
        surface,
        (42, 44, 66),
        [
            (int(cape_center.x), int(cape_center.y - 12)),
            (int(cape_center.x - 12), int(cape_center.y + 9)),
            (int(cape_center.x + 12), int(cape_center.y + 9)),
        ],
    )

    body_center = (x, int(y + bob))
    pygame.draw.circle(surface, (16, 16, 24), body_center, 14)
    pygame.draw.circle(surface, (62, 70, 104), body_center, 12)
    pygame.draw.circle(surface, (82, 94, 132), (x - 2, int(y + bob) - 2), 8)
    pygame.draw.circle(
        surface,
        (24, 26, 40),
        (x + int(facing.x * 3), int(y + bob + facing.y * 3)),
        7,
    )
    # Ojos orientados al frente.
    eye_offset = perpendicular * 2.6 + facing * 3.0
    for side in (-1, 1):
        eye = Vec2(x, y + bob) + eye_offset + perpendicular * (side * 2.0)
        pygame.draw.circle(surface, palette.ACCENT, (int(eye.x), int(eye.y)), 1)

    # Espada y arco de golpe.
    swing = 0.0
    if player.attack_anim > 0:
        progress = 1.0 - player.attack_anim / 0.22
        swing = lerp(-1.25, 1.35, progress)
    sword_angle = angle + swing
    direction = Vec2.from_angle(sword_angle)
    start = Vec2(x, y + bob) + direction * 9
    end = Vec2(x, y + bob) + direction * 30
    pygame.draw.line(
        surface, (34, 34, 46), (int(start.x), int(start.y)), (int(end.x), int(end.y)), 5
    )
    pygame.draw.line(
        surface,
        (210, 218, 235),
        (int(start.x), int(start.y)),
        (int(end.x), int(end.y)),
        2,
    )
    guard = Vec2(x, y + bob) + direction * 10 + perpendicular * 3
    pygame.draw.line(
        surface,
        palette.GOLD,
        (int(guard.x), int(guard.y)),
        (int(guard.x - perpendicular.x * 6), int(guard.y - perpendicular.y * 6)),
        2,
    )

    if player.is_dashing:
        pygame.draw.circle(surface, palette.ACCENT, (x, int(y + bob)), 15, 1)
    if player.damage_flash > 0:
        pygame.draw.circle(surface, (255, 120, 110), (x, int(y + bob)), 16, 2)


def draw_attack_arc(
    surface: pygame.Surface,
    player: Player,
    camera: Camera,
    shake: Vec2,
    window_size: tuple[int, int],
) -> None:
    if player.attack_anim <= 0:
        return
    progress = 1.0 - player.attack_anim / 0.22
    alpha = int(150 * (1.0 - progress * 0.65))
    radius = 52
    half = math.radians(player.config.attack_arc / 2)
    angle = player.facing.angle()
    center = camera.world_to_screen(player.position, shake)
    overlay = pygame.Surface(window_size, pygame.SRCALPHA)
    points = [(int(center.x), int(center.y))]
    for index in range(13):
        t = index / 12
        point_angle = angle - half + half * 2 * t
        points.append(
            (
                int(center.x + math.cos(point_angle) * radius * (0.7 + 0.3 * t)),
                int(center.y + math.sin(point_angle) * radius * (0.7 + 0.3 * t)),
            )
        )
    pygame.draw.polygon(overlay, (255, 196, 120, alpha), points)
    pygame.draw.lines(overlay, (255, 236, 200, alpha + 50), False, points[1:], 2)
    surface.blit(overlay, (0, 0))


def draw_enemy(
    surface: pygame.Surface,
    enemy: Enemy,
    player_position: Vec2,
    camera: Camera,
    shake: Vec2,
    time: float,
) -> None:
    x, y = _screen(enemy.position, camera, shake)
    draw_shadow(surface, enemy.position, camera, shake, int(enemy.radius * 2.2), 18)
    color = palette.ENEMY_COLORS.get(enemy.kind, (160, 160, 160))
    to_player = (player_position - enemy.position).normalized()

    anim_player = getattr(enemy, "anim_player", None)
    if anim_player is not None and getattr(anim_player, "current_surface", None) is not None:
        frame_surf = anim_player.current_surface
        px, py = getattr(anim_player, "current_pivot", (frame_surf.get_width() // 2, frame_surf.get_height()))
        if to_player.x < 0:
            frame_surf = pygame.transform.flip(frame_surf, True, False)
            px = frame_surf.get_width() - px
        surface.blit(frame_surf, (x - px, y - py))
    elif enemy.kind == "slime":
        wobble = math.sin(enemy.anim_time * 6.0) * 0.16
        width = int(enemy.radius * 2 * (1 + wobble))
        height = int(enemy.radius * 2 * (1 - wobble * 0.7))
        rect = pygame.Rect(0, 0, width, height)
        rect.center = (x, y + 3)
        pygame.draw.ellipse(surface, (18, 30, 24), rect.inflate(4, 4))
        pygame.draw.ellipse(surface, color, rect)
        highlight = pygame.Rect(0, 0, width // 2, height // 3)
        highlight.topleft = (rect.x + 5, rect.y + 4)
        pygame.draw.ellipse(surface, (140, 216, 160), highlight)
        eye_y = y + 1
        for side in (-1, 1):
            eye_x = x + side * 5 + int(to_player.x * 2)
            pygame.draw.circle(surface, (240, 255, 240), (eye_x, eye_y), 3)
            pygame.draw.circle(
                surface,
                (18, 24, 20),
                (eye_x + int(to_player.x * 1.4), eye_y + int(to_player.y * 1.4)),
                1,
            )
    elif enemy.kind == "wisp":
        flicker = 0.8 + 0.2 * math.sin(time * 9.0 + enemy.anim_time)
        pygame.draw.circle(
            surface, (54, 44, 104), (x, y), int(enemy.radius * 2.1 * flicker)
        )
        pygame.draw.circle(
            surface, (90, 76, 160), (x, y), int(enemy.radius * 1.4 * flicker)
        )
        pygame.draw.circle(surface, color, (x, y), int(enemy.radius * 0.9))
        pygame.draw.circle(
            surface, (230, 220, 255), (x - 2, y - 3), int(enemy.radius * 0.35)
        )
        for index in range(3):
            orbit = time * 2.4 + index * math.tau / 3 + enemy.anim_time
            spark = (
                x + int(math.cos(orbit) * (enemy.radius + 7)),
                y + int(math.sin(orbit) * (enemy.radius + 7)),
            )
            pygame.draw.circle(surface, (190, 166, 255), spark, 2)
    else:  # brute
        radius = enemy.radius
        charge = enemy.state in ("windup", "charge")
        body_color = (220, 130, 100) if enemy.state == "windup" else color
        points = []
        for index in range(8):
            angle = math.tau * index / 8 + math.pi / 8
            wobble = 1.0 + 0.06 * math.sin(enemy.anim_time * 3 + index)
            points.append(
                (x + math.cos(angle) * radius * wobble, y + math.sin(angle) * radius * wobble)
            )
        pygame.draw.polygon(surface, (28, 18, 18), points)
        inner = [(px * 0.86 + x * 0.14, py * 0.86 + y * 0.14) for px, py in points]
        pygame.draw.polygon(surface, body_color, inner)
        pygame.draw.circle(surface, (94, 44, 38), (x, y + 2), radius // 2)
        eye_offset = to_player * 4
        for side in (-1, 1):
            eye = (x + int(eye_offset.x) + side * 7, y + int(eye_offset.y) - 3)
            pygame.draw.circle(surface, (255, 220, 120), eye, 3)
        if charge:
            end = (
                x + int(enemy._charge_direction.x * 110),
                y + int(enemy._charge_direction.y * 110),
            )
            pygame.draw.line(surface, (255, 120, 80), (x, y), end, 2)
            pygame.draw.circle(surface, (255, 190, 110), (x, y), radius + 5, 2)

    if enemy.hit_flash > 0:
        pygame.draw.circle(surface, (255, 255, 255), (x, y), int(enemy.radius) + 2, 2)

    if enemy.health < enemy.stats.health:
        width = int(enemy.radius * 2)
        bar = pygame.Rect(x - width // 2, y - int(enemy.radius) - 12, width, 4)
        pygame.draw.rect(surface, (34, 16, 20), bar.inflate(2, 2), border_radius=2)
        fill = bar.copy()
        fill.width = max(1, int(width * max(0.0, enemy.health / enemy.stats.health)))
        pygame.draw.rect(surface, (222, 86, 84), fill, border_radius=2)


def draw_chest(
    surface: pygame.Surface,
    chest: Chest,
    camera: Camera,
    shake: Vec2,
    time: float,
    highlighted: bool,
    art: ArtLibrary | None = None,
) -> None:
    x, y = _screen(chest.position, camera, shake)
    draw_shadow(surface, chest.position, camera, shake, 30, 14)
    if highlighted and not chest.opened:
        pulse = 2 + int(math.sin(time * 5) * 2)
        pygame.draw.circle(surface, palette.ACCENT, (x, y), 22 + pulse, 2)

    if art and art.objects:
        sprite_name = "chest_open" if chest.opened else "chest_closed"
        sprite = art.object_sprite(sprite_name)
        if sprite:
            rect = sprite.get_rect(midbottom=(x, y + 14))
            surface.blit(sprite, rect)
            return

    body = pygame.Rect(0, 0, 30, 20)
    body.center = (x, y + 3)
    pygame.draw.rect(surface, (28, 20, 16), body.inflate(4, 4), border_radius=3)
    pygame.draw.rect(surface, (92, 64, 40), body, border_radius=3)
    pygame.draw.rect(surface, (52, 36, 26), body, width=2, border_radius=3)
    if chest.opened:
        pygame.draw.rect(surface, (22, 18, 16), body.inflate(-6, -6), border_radius=2)
        pygame.draw.line(
            surface, (120, 94, 56), (body.left + 3, body.top - 1), (body.right - 3, body.top - 1), 2
        )
    else:
        lid = pygame.Rect(0, 0, 32, 9)
        lid.midbottom = (x, body.top + 3)
        pygame.draw.rect(surface, (122, 86, 52), lid, border_radius=4)
        pygame.draw.rect(surface, palette.GOLD, (x - 3, y - 1, 6, 7), border_radius=2)
        pygame.draw.line(
            surface, (156, 114, 66), (body.left + 2, body.centery), (body.right - 2, body.centery), 2
        )


def draw_campfire(
    surface: pygame.Surface,
    campfire: Campfire,
    camera: Camera,
    shake: Vec2,
    time: float,
    highlighted: bool,
    art: ArtLibrary | None = None,
) -> None:
    x, y = _screen(campfire.position, camera, shake)
    draw_shadow(surface, campfire.position, camera, shake, 46, 22)
    if art and art.objects:
        base_sprite = art.object_sprite("campfire_base")
        if base_sprite:
            rect = base_sprite.get_rect(midbottom=(x, y + 16))
            surface.blit(base_sprite, rect)
            frame_idx = int(time * 8.0) % 4
            flame_sprite = art.object_sprite(f"campfire_flame_{frame_idx}")
            if flame_sprite:
                flame_rect = flame_sprite.get_rect(midbottom=(x, y + 6))
                surface.blit(flame_sprite, flame_rect)
            if highlighted:
                pygame.draw.circle(surface, palette.ACCENT, (x, y), 32, 1)
            return

    pygame.draw.ellipse(surface, (54, 50, 60), pygame.Rect(x - 25, y + 2, 50, 20))
    for index in range(5):
        angle = math.tau * index / 5 + 0.3
        pygame.draw.circle(
            surface,
            (92, 88, 100),
            (x + int(math.cos(angle) * 20), y + 4 + int(math.sin(angle) * 7)),
            4,
        )
    pygame.draw.line(surface, (72, 48, 30), (x - 12, y + 10), (x + 12, y + 2), 5)
    pygame.draw.line(surface, (78, 52, 32), (x - 10, y + 2), (x + 13, y + 10), 5)
    flicker = math.sin(time * 11.0) * 2
    flame_height = 22 + flicker
    pygame.draw.polygon(
        surface,
        (214, 82, 38),
        [(x - 8, y + 2), (x, int(y - flame_height)), (x + 8, y + 2)],
    )
    pygame.draw.polygon(
        surface,
        (248, 162, 62),
        [(x - 4, y + 2), (x + 1, int(y - flame_height * 0.7)), (x + 5, y + 2)],
    )
    pygame.draw.circle(surface, (255, 230, 150), (x + 1, y - 4), 3)
    if highlighted:
        pygame.draw.circle(surface, palette.ACCENT, (x, y), 32, 1)


def draw_altar(
    surface: pygame.Surface,
    altar: ForgeAltar,
    camera: Camera,
    shake: Vec2,
    time: float,
    shards: int,
    shards_required: int,
    highlighted: bool,
    art: ArtLibrary | None = None,
) -> None:
    x, y = _screen(altar.position, camera, shake)
    draw_shadow(surface, altar.position, camera, shake, 72, 30)
    if art and art.objects:
        sprite_name = "altar_active" if altar.activated else "altar_idle"
        sprite = art.object_sprite(sprite_name)
        if sprite:
            rect = sprite.get_rect(midbottom=(x, y + 18))
            surface.blit(sprite, rect)
            if altar.activated:
                pulse = 1.0 + 0.25 * math.sin(time * 6)
                pygame.draw.polygon(
                    surface,
                    (255, 140, 52),
                    [
                        (x - 12, y - 22),
                        (x, y - int(60 * pulse)),
                        (x + 12, y - 22),
                    ],
                )
                pygame.draw.polygon(
                    surface,
                    (255, 226, 150),
                    [(x - 5, y - 22), (x, y - int(42 * pulse)), (x + 5, y - 22)],
                )
            else:
                for index in range(3):
                    lit = index < shards
                    socket_x = x - 15 + index * 15
                    socket_y = y - 11
                    if lit:
                        pygame.draw.circle(surface, palette.ACCENT, (socket_x, socket_y), 4)
                        pygame.draw.circle(surface, (255, 230, 160), (socket_x, socket_y), 2)
                if shards >= shards_required:
                    pygame.draw.circle(surface, palette.ACCENT, (x, y - 16), 20, 2)
            if highlighted:
                pygame.draw.circle(surface, palette.ACCENT, (x, y - 10), 42, 1)
            return

    pygame.draw.ellipse(surface, (52, 46, 62), pygame.Rect(x - 36, y - 8, 72, 30))
    pygame.draw.ellipse(surface, (82, 72, 96), pygame.Rect(x - 30, y - 12, 60, 24))
    pygame.draw.rect(surface, (66, 60, 78), pygame.Rect(x - 22, y - 24, 44, 22), border_radius=4)
    pygame.draw.rect(surface, (94, 82, 108), pygame.Rect(x - 22, y - 24, 44, 7), border_radius=4)
    for index in range(3):
        lit = index < shards
        socket_x = x - 15 + index * 15
        socket_y = y - 11
        pygame.draw.circle(surface, (28, 24, 34), (socket_x, socket_y), 6)
        if lit:
            pygame.draw.circle(surface, palette.ACCENT, (socket_x, socket_y), 4)
            pygame.draw.circle(surface, (255, 230, 160), (socket_x, socket_y), 2)
    if altar.activated:
        pulse = 1.0 + 0.25 * math.sin(time * 6)
        pygame.draw.polygon(
            surface,
            (255, 140, 52),
            [
                (x - 12, y - 22),
                (x, y - int(60 * pulse)),
                (x + 12, y - 22),
            ],
        )
        pygame.draw.polygon(
            surface,
            (255, 226, 150),
            [(x - 5, y - 22), (x, y - int(42 * pulse)), (x + 5, y - 22)],
        )
    else:
        remaining = max(0, shards_required - shards)
        if remaining == 0:
            pygame.draw.circle(surface, palette.ACCENT, (x, y - 16), 20, 2)
    if highlighted:
        pygame.draw.circle(surface, palette.ACCENT, (x, y - 10), 42, 1)
    pygame.draw.circle(surface, (30, 26, 38), (x, y - 2), 26, 1)


def draw_projectile(
    surface: pygame.Surface, projectile: Projectile, camera: Camera, shake: Vec2
) -> None:
    x, y = _screen(projectile.position, camera, shake)
    trail = projectile.velocity.normalized() * -14
    pygame.draw.line(
        surface,
        (90, 74, 160),
        (int(x + trail.x), int(y + trail.y)),
        (x, y),
        3,
    )
    pygame.draw.circle(surface, (60, 48, 120), (x, y), int(projectile.radius) + 3)
    pygame.draw.circle(surface, projectile.color, (x, y), int(projectile.radius))
    pygame.draw.circle(surface, (235, 226, 255), (x, y), max(1, int(projectile.radius * 0.45)))
