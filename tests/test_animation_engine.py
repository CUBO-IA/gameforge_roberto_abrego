"""Pruebas unitarias para el motor de animación gf-anim-v1 (AnimationPlayer y loader)."""

from __future__ import annotations

import json
from pathlib import Path

import pygame
import pytest

from game.render.animation import (
    AnimationClip,
    AnimationFormatError,
    AnimationPlayer,
    FrameData,
    FrameEvent,
    HitboxData,
    load_animation_manifest,
)


@pytest.fixture(autouse=True)
def init_pygame() -> None:
    pygame.init()


def test_animation_player_playback_and_loop() -> None:
    dummy_surf = pygame.Surface((32, 32))
    frame1 = FrameData(
        id="f1",
        rect=(0, 0, 32, 32),
        pivot=(16, 32),
        duration=0.1,
        surface=dummy_surf,
        sockets={"hand": (20, 20)},
        hurtboxes=((-10, -30, 20, 30),),
        hitboxes=(),
        events=(FrameEvent(name="step", payload={"side": "left"}),),
    )
    frame2 = FrameData(
        id="f2",
        rect=(32, 0, 32, 32),
        pivot=(16, 32),
        duration=0.1,
        surface=dummy_surf,
        sockets={"hand": (22, 22)},
        hurtboxes=((-10, -30, 20, 30),),
        hitboxes=(HitboxData(rect=(0, -20, 20, 20), damage=15.0),),
        events=(FrameEvent(name="swing", payload={}),),
    )

    clip = AnimationClip(name="walk", frames=(frame1, frame2), loop=True)
    player = AnimationPlayer(clips={"walk": clip})

    assert player.current_clip is None
    started = player.play("walk")
    assert started is True
    assert player.current_clip.name == "walk"
    assert player.frame_index == 0
    assert player.current_frame.id == "f1"
    assert player.get_socket("hand") == (20, 20)
    assert len(player.active_hitboxes) == 0
    assert len(player.active_hurtboxes) == 1

    # Avanzar medio frame (0.05s): sigue en f1
    events = player.update(0.05)
    assert player.frame_index == 0
    assert len(events) == 0

    # Avanzar otro medio frame (0.05s): pasa a f2 y emite evento "swing"
    events = player.update(0.06)
    assert player.frame_index == 1
    assert player.current_frame.id == "f2"
    assert len(player.active_hitboxes) == 1
    assert player.active_hitboxes[0].damage == 15.0
    assert any(ev.name == "swing" for ev in events)

    # Avanzar un frame completo (0.10s): al ser loop=True, vuelve a f1
    player.update(0.10)
    assert player.frame_index == 0
    assert player.is_finished is False


def test_animation_player_non_loop_finishes() -> None:
    dummy_surf = pygame.Surface((32, 32))
    frame = FrameData(
        id="die",
        rect=(0, 0, 32, 32),
        pivot=(16, 32),
        duration=0.1,
        surface=dummy_surf,
        sockets={},
        hurtboxes=(),
        hitboxes=(),
        events=(),
    )
    clip = AnimationClip(name="die", frames=(frame,), loop=False)
    player = AnimationPlayer(clips={"die": clip})

    player.play("die")
    assert player.is_finished is False
    player.update(0.15)
    assert player.is_finished is True
    assert player.frame_index == 0


def test_animation_player_priority_interruption() -> None:
    dummy_surf = pygame.Surface((32, 32))
    f_idle = FrameData("id1", (0, 0, 32, 32), (16, 32), 0.2, dummy_surf, {}, (), (), ())
    f_attack = FrameData("atk1", (0, 0, 32, 32), (16, 32), 0.3, dummy_surf, {}, (), (), ())
    f_hurt = FrameData("hrt1", (0, 0, 32, 32), (16, 32), 0.1, dummy_surf, {}, (), (), ())

    clip_idle = AnimationClip("idle", (f_idle,), loop=True, interrupt_priority=0)
    clip_attack = AnimationClip("attack", (f_attack,), loop=False, interrupt_priority=3)
    clip_hurt = AnimationClip("hurt", (f_hurt,), loop=False, interrupt_priority=5)

    player = AnimationPlayer({"idle": clip_idle, "attack": clip_attack, "hurt": clip_hurt})

    player.play("attack")
    assert player.current_clip.name == "attack"

    # Idle (prioridad 0) no puede interrumpir attack (prioridad 3)
    interrupted = player.interrupt_with("idle")
    assert interrupted is False
    assert player.current_clip.name == "attack"

    # Hurt (prioridad 5) sí puede interrumpir attack (prioridad 3)
    interrupted = player.interrupt_with("hurt")
    assert interrupted is True
    assert player.current_clip.name == "hurt"


def test_load_canonical_knight_hero_manifest() -> None:
    manifest_path = Path("assets/sprites/characters/player/knight_hero.anim.json")
    assert manifest_path.is_file()

    clips, metadata = load_animation_manifest(manifest_path)
    assert metadata["id"] == "knight_hero"
    assert "idle" in clips
    assert "walk" in clips
    assert "attack" in clips
    assert "hurt" in clips
    assert "die" in clips

    attack_clip = clips["attack"]
    assert len(attack_clip.frames) == 3
    # El segundo fotograma de ataque tiene hitbox
    assert len(attack_clip.frames[1].hitboxes) == 1
    assert attack_clip.frames[1].hitboxes[0].damage == 15.0


def test_load_invalid_manifest_raises_format_error(tmp_path: Path) -> None:
    bad_manifest = tmp_path / "bad.anim.json"

    # 1. Archivo inexistente
    with pytest.raises(AnimationFormatError):
        load_animation_manifest(tmp_path / "non_existent.json")

    # 2. JSON inválido
    bad_manifest.write_text("{bad_json: true", encoding="utf-8")
    with pytest.raises(AnimationFormatError):
        load_animation_manifest(bad_manifest)

    # 3. Falta versión
    bad_manifest.write_text(json.dumps({"metadata": {}}), encoding="utf-8")
    with pytest.raises(AnimationFormatError):
        load_animation_manifest(bad_manifest)


def test_player_animation_integration_with_scene(default_config, tmp_path: Path) -> None:
    from game.app import Application
    from game.scenes.play import PlayScene

    app = Application(default_config, data_dir=tmp_path / "data", headless=True)
    scene = PlayScene(app, seed=42)
    assert scene.player_anim is not None
    assert scene.player.anim_player is scene.player_anim
    assert scene.player_anim.current_clip.name == "idle"

    # Simular un frame de actualización en reposo
    scene.update(1 / 60)
    assert scene.player_anim.current_clip.name == "idle"

    # Simular ataque
    scene.player.attack_anim = 0.2
    scene.update(1 / 60)
    assert scene.player_anim.current_clip.name == "attack"

    app.shutdown()

