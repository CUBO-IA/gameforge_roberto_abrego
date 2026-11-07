"""Vista del mundo de juego: ordena y dibuja entidades, efectos e iluminación.

Solo lee el estado de la escena; no contiene reglas de simulación.
Extraído de ``game.scenes.play`` en la Fase 1 para mantener la escena
centrada en orquestar input y sistemas.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

import pygame

from game.core.math2d import Vec2
from game.render import entity_renderer, palette
from game.render.effects import Effects
from game.render.entity_renderer import draw_attack_arc
from game.render.lighting import Lighting
from game.world.camera import Camera

if TYPE_CHECKING:
    from game.render.assets import ArtLibrary


def draw_play_world(
    surface: pygame.Surface,
    *,
    tile_renderer,
    camera: Camera,
    effects: Effects,
    lighting: Lighting,
    time: float,
    player,
    enemies: list,
    projectiles: list,
    chests: list,
    campfire,
    altar,
    nearby: tuple[object, str] | None,
    shard_count: int,
    shards_required: int,
    art: ArtLibrary | None = None,
) -> None:
    """Dibuja el mundo completo sobre la superficie de la escena."""
    surface.fill(palette.BACKGROUND_DEEP)
    shake = effects.current_shake()
    top_left = camera.top_left + shake
    surface.blit(tile_renderer.surface, (-int(top_left.x), -int(top_left.y)))
    tile_renderer.draw_animated(surface, camera, time, shake)

    margin = 80.0
    view_min_x = top_left.x - margin
    view_max_x = top_left.x + camera.viewport_width + margin
    view_min_y = top_left.y - margin
    view_max_y = top_left.y + camera.viewport_height + margin

    def in_view(pos: Vec2, radius: float = 32.0) -> bool:
        return (
            view_min_x - radius <= pos.x <= view_max_x + radius
            and view_min_y - radius <= pos.y <= view_max_y + radius
        )

    drawables: list[tuple[float, str, object]] = []
    for chest in chests:
        if in_view(chest.position, 32.0):
            drawables.append((chest.position.y, "chest", chest))
    if in_view(campfire.position, 48.0):
        drawables.append((campfire.position.y, "campfire", campfire))
    if in_view(altar.position, 48.0):
        drawables.append((altar.position.y, "altar", altar))
    for enemy in enemies:
        if enemy.alive and in_view(enemy.position, enemy.radius + 16.0):
            drawables.append((enemy.position.y, "enemy", enemy))
    for projectile in projectiles:
        if in_view(projectile.position, projectile.radius):
            drawables.append((projectile.position.y, "projectile", projectile))
    drawables.append((player.position.y, "player", player))
    drawables.sort(key=lambda item: item[0])

    def is_highlighted(obj: object) -> bool:
        return nearby is not None and nearby[0] is obj

    for _, kind, obj in drawables:
        if kind == "chest":
            entity_renderer.draw_chest(
                surface, obj, camera, shake, time, is_highlighted(obj), art=art
            )
        elif kind == "campfire":
            entity_renderer.draw_campfire(
                surface, obj, camera, shake, time, is_highlighted(obj), art=art
            )
        elif kind == "altar":
            entity_renderer.draw_altar(
                surface,
                obj,
                camera,
                shake,
                time,
                shard_count,
                shards_required,
                is_highlighted(obj),
                art=art,
            )
        elif kind == "enemy":
            entity_renderer.draw_enemy(surface, obj, player.position, camera, shake, time)
        elif kind == "projectile":
            entity_renderer.draw_projectile(surface, obj, camera, shake)
        else:
            entity_renderer.draw_player(surface, obj, camera, shake, time)

    draw_attack_arc(
        surface,
        player,
        camera,
        shake,
        (surface.get_width(), surface.get_height()),
    )


def draw_lighting(
    surface: pygame.Surface,
    lighting: Lighting,
    camera: Camera,
    shake: Vec2,
    time: float,
    player,
    campfire,
    altar,
    projectiles: list,
) -> None:
    """Oscuridad + luces radiales (jugador, hoguera con parpadeo, altar, proyectiles)."""
    flicker = 1.0 + 0.08 * math.sin(time * 9.0)
    lights = [
        (player.position, 270, 1.0),
        (campfire.position, int(175 * flicker), 1.0),
        (altar.position, 190, 1.0),
    ]
    for projectile in projectiles:
        lights.append((projectile.position, 70, 0.8))
    lighting.render(surface, lights, camera, shake)


def draw_play_overlay(
    surface: pygame.Surface,
    *,
    effects: Effects,
    hud,
    fonts,
    camera: Camera,
    shake: Vec2,
    player,
    inventory,
    altar,
    campfire,
    floor: int,
    elapsed: float,
    score: int,
    nearby: tuple[object, str] | None,
    toast: str,
    toast_timer: float,
    mouse_position: tuple[int, int],
    fps: float,
    show_inventory: bool,
    paused: bool,
    save_hint: str,
    victory_timer: float,
    hurt_overlay: pygame.Surface,
    fade: pygame.Surface,
) -> None:
    """HUD, overlays de daño/pausa/inventario y fundido de victoria."""
    if player.damage_flash > 0:
        alpha = int(110 * min(1.0, player.damage_flash * 5))
        hurt_overlay.fill((160, 20, 30, alpha))
        surface.blit(hurt_overlay, (0, 0))

    effects.draw(surface, camera, fonts, shake=shake)

    hud.draw(
        surface,
        player,
        inventory,
        altar.position,
        campfire.position,
        floor,
        elapsed,
        score,
        nearby[1] if nearby else None,
        toast,
        toast_timer,
        mouse_position,
        fps,
    )

    if show_inventory:
        hud.draw_inventory(surface, inventory)
    elif paused:
        hud.draw_pause(surface, save_hint)

    if victory_timer >= 0:
        progress = 1.0 - max(0.0, victory_timer) / 2.2
        fade.fill((255, 200, 130, int(200 * min(1.0, progress))))
        surface.blit(fade, (0, 0))
