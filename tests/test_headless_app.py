"""Integración headless: aplicación, escenas, guardado y final de partida."""

from __future__ import annotations

from pathlib import Path

import pytest

from game.__main__ import main
from game.app import Application
from game.core.math2d import Vec2
from game.persistence.savegame import load_run
from game.render import palette
from game.scenes.play import PlayScene
from game.scenes.results import ResultsScene


@pytest.fixture
def app(default_config, tmp_path: Path):
    application = Application(
        default_config,
        data_dir=tmp_path / "data",
        headless=True,
    )
    yield application
    application.shutdown()


def test_application_runs_menu_frames(app: Application) -> None:
    frames = app.run(3)
    assert frames == 3
    assert app.scene is not None
    assert app.scene.__class__.__name__ == "MenuScene"


def test_play_scene_update_and_draw(app: Application) -> None:
    scene = PlayScene(app, seed=123)
    app.replace_scene(scene)
    for _ in range(20):
        scene.update(1 / 60)
    scene.draw(app.screen)
    scene.show_inventory = True
    scene.draw(app.screen)
    scene.show_inventory = False
    scene.paused = True
    scene.draw(app.screen)
    assert scene.player.alive
    assert scene.dungeon.seed == 123


def test_walk_animation_emits_dust_with_palette_color(
    app: Application, monkeypatch: pytest.MonkeyPatch
) -> None:
    scene = PlayScene(app, seed=13)
    app.replace_scene(scene)
    monkeypatch.setattr(app.input, "move_vector", lambda: Vec2(1.0, 0.0))

    for _ in range(20):
        scene.update(1 / 60)

    assert any(particle.color == palette.TEXT_DIM for particle in scene.effects.particles.particles)


def test_save_and_restore_through_scene(app: Application) -> None:
    scene = PlayScene(app, seed=77)
    app.replace_scene(scene)
    scene.inventory.add("potion", 2)
    scene.player.health = 55.0
    scene.player.position = scene.player.position + Vec2(4, 0)
    error = scene._save()
    assert error is None
    assert app.has_save()

    data = load_run(app.save_path)
    restored = PlayScene(app, snapshot=data.run)
    assert restored.dungeon.seed == scene.dungeon.seed
    assert restored.inventory.count("potion") == 2
    assert restored.player.health == pytest.approx(55.0)
    assert restored.player.position.distance_to(scene.player.position) < 1.0


def test_chest_interaction_and_potion(app: Application) -> None:
    scene = PlayScene(app, seed=5)
    app.replace_scene(scene)
    chest = scene.chests[0]
    scene.player.position = chest.position.copy()
    scene.nearby = (chest, "Abrir cofre")
    scene._interact()
    assert chest.opened
    assert chest.id in scene.chests_opened
    assert scene.inventory.count(chest.item_id) >= 1

    scene.player.health = 40.0
    scene.inventory.add("potion", 1)
    before = scene.player.health
    scene._use_potion()
    assert scene.player.health > before
    assert scene.inventory.count("potion") == 0


def test_victory_records_score_and_removes_save(app: Application) -> None:
    scene = PlayScene(app, seed=9)
    scene.floor = 3  # Planta final (Fase 2)
    scene.quest.shards_required = 3
    app.replace_scene(scene)
    scene.inventory.add("shard", 3)
    scene.player.position = scene.altar.position.copy()
    scene.nearby = (scene.altar, "Activar la Fragua")
    scene._activate_altar()
    assert scene.victory_timer > 0
    scene.update(2.3)
    assert isinstance(app.scene, ResultsScene)
    assert app.scene.summary.victory
    assert app.scores is not None
    assert app.scores.count() == 1
    assert not app.has_save()


def test_death_records_run(app: Application) -> None:
    scene = PlayScene(app, seed=11)
    app.replace_scene(scene)
    scene.player.health = 0.0
    scene.update(1 / 60)
    assert isinstance(app.scene, ResultsScene)
    assert not app.scene.summary.victory
    assert app.scores is not None
    assert app.scores.count() == 1


def test_cli_headless_smoke(tmp_path: Path) -> None:
    exit_code = main(
        [
            "--headless",
            "--frames",
            "2",
            "--new-game",
            "--seed",
            "3",
            "--data-dir",
            str(tmp_path / "cli-data"),
        ]
    )
    assert exit_code == 0
