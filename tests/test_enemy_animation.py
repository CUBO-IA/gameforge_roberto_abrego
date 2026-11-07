"""Pruebas del sistema de animación integrado para enemigos (gf-anim-v1)."""

from __future__ import annotations

from pathlib import Path

import pygame
import pytest

from game.core.config import EnemyStats
from game.core.math2d import Vec2
from game.entities.enemies import Enemy
from game.render.animation import AnimationPlayer, load_animation_manifest
from game.render.entity_renderer import draw_enemy
from game.world.camera import Camera


@pytest.fixture(scope="module")
def pygame_display():
    pygame.init()
    if not pygame.display.get_surface():
        pygame.display.set_mode((1, 1), pygame.NOFRAME)
    yield
    pygame.quit()


def test_enemy_manifests_load(pygame_display):
    for kind in ("slime", "wisp", "brute"):
        manifest_path = Path(f"assets/sprites/enemies/{kind}/{kind}.anim.json")
        assert manifest_path.is_file(), f"Falta el manifiesto para {kind}"
        clips, metadata = load_animation_manifest(manifest_path)
        assert len(clips) >= 4, f"{kind} debe tener al menos 4 clips básicos"
        for mandatory in ("idle", "walk", "hurt", "die"):
            assert mandatory in clips, f"{kind} debe tener el clip {mandatory}"
        assert metadata.get("id") == kind


def test_enemy_animation_player_playback(pygame_display):
    manifest_path = Path("assets/sprites/enemies/slime/slime.anim.json")
    clips, _ = load_animation_manifest(manifest_path)
    player = AnimationPlayer(clips)

    assert player.play("idle")
    assert player.current_clip.name == "idle"
    assert player.current_surface is not None
    assert player.current_pivot == (16, 32)

    # Avanzar tiempo
    events = player.update(0.2)
    assert isinstance(events, list)

    # Interrupción por prioridad
    assert player.interrupt_with("hurt")
    assert player.current_clip.name == "hurt"


def test_draw_enemy_with_animation_player(pygame_display):
    stats = EnemyStats(health=50.0, speed=40.0, touch_damage=10.0, radius=14.0, score=50)
    enemy = Enemy(id="slime_1", kind="slime", position=Vec2(100, 100), stats=stats)

    manifest_path = Path("assets/sprites/enemies/slime/slime.anim.json")
    clips, _ = load_animation_manifest(manifest_path)
    enemy.anim_player = AnimationPlayer(clips)
    enemy.anim_player.play("idle")

    surface = pygame.Surface((320, 240), pygame.SRCALPHA)
    camera = Camera(320, 240)
    shake = Vec2()

    # Debe dibujar sin lanzar excepción y usar la superficie del sprite
    draw_enemy(surface, enemy, Vec2(120, 100), camera, shake, 0.0)

    # Girado hacia la izquierda (to_player.x < 0)
    draw_enemy(surface, enemy, Vec2(80, 100), camera, shake, 0.0)
