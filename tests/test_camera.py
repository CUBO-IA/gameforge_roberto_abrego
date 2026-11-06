import pytest

from game.core.math2d import Vec2
from game.world.camera import Camera


def test_camera_clamps_to_map_edges() -> None:
    camera = Camera(800, 600)
    camera.snap_to(Vec2(0, 0), 2000, 1500)
    assert camera.position.as_tuple() == (400, 300)
    camera.snap_to(Vec2(2000, 1500), 2000, 1500)
    assert camera.position.as_tuple() == (1600, 1200)


def test_camera_centers_small_map() -> None:
    camera = Camera(800, 600)
    camera.snap_to(Vec2(10, 10), 400, 300)
    assert camera.position.as_tuple() == (200, 150)


def test_camera_follow_smoothing() -> None:
    camera = Camera(800, 600)
    camera.snap_to(Vec2(800, 600), 3000, 2000)
    camera.update(Vec2(1200, 900), 0.1, 3000, 2000, smoothing=8)
    assert 800 < camera.position.x < 1200
    assert 600 < camera.position.y < 900


def test_world_screen_roundtrip() -> None:
    camera = Camera(800, 600)
    camera.snap_to(Vec2(900, 700), 3000, 2000)
    point = Vec2(123, 456)
    screen = camera.world_to_screen(point)
    assert camera.screen_to_world(screen).as_tuple() == pytest.approx(point.as_tuple())
    shake = Vec2(4, -5)
    assert camera.screen_to_world(
        camera.world_to_screen(point, shake), shake
    ).as_tuple() == pytest.approx(point.as_tuple())


def test_invalid_viewport() -> None:
    with pytest.raises(ValueError):
        Camera(0, 600)
