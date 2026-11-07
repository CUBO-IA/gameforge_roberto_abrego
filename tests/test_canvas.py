"""Pruebas del Lienzo Virtual y escalado de interfaz (game.render.canvas)."""

from __future__ import annotations

import pytest

from game.render.canvas import (
    VirtualCanvas,
    calculate_letterbox,
    screen_to_logical,
)


def test_calculate_letterbox_exact_aspect() -> None:
    # Misma resolución 16:9
    ox, oy, sw, sh, scale = calculate_letterbox(1280, 720, 1280, 720)
    assert ox == 0
    assert oy == 0
    assert sw == 1280
    assert sh == 720
    assert scale == 1.0


def test_calculate_letterbox_full_hd_scale() -> None:
    # 1920x1080 es exactamente 1.5x de 1280x720
    ox, oy, sw, sh, scale = calculate_letterbox(1920, 1080, 1280, 720)
    assert ox == 0
    assert oy == 0
    assert sw == 1920
    assert sh == 1080
    assert scale == 1.5


def test_calculate_letterbox_ultrawide_pillarbox() -> None:
    # Pantalla 21:9 ultrawide (2560x1080): debe tener barras negras laterales (pillarbox)
    ox, oy, sw, sh, scale = calculate_letterbox(2560, 1080, 1280, 720)
    assert scale == 1.5
    assert sw == 1920
    assert sh == 1080
    assert oy == 0
    # 2560 - 1920 = 640px excedente -> 320px a cada lado
    assert ox == 320


def test_calculate_letterbox_narrow_letterbox() -> None:
    # Pantalla 4:3 (800x600): escala limitada por ancho (800 / 1280 = 0.625)
    ox, oy, sw, sh, scale = calculate_letterbox(800, 600, 1280, 720)
    assert scale == 0.625
    assert sw == 800
    assert sh == 450
    assert ox == 0
    # 600 - 450 = 150px excedente -> 75px arriba y abajo
    assert oy == 75


def test_calculate_letterbox_invalid() -> None:
    with pytest.raises(ValueError):
        calculate_letterbox(0, 100, 1280, 720)
    with pytest.raises(ValueError):
        calculate_letterbox(100, 100, -10, 720)


def test_screen_to_logical_mapping() -> None:
    # Escala 2.0x con offset (100, 50)
    ox, oy = 100, 50
    scale = 2.0
    # Un clic en (100, 50) debe mapear al origen lógico (0, 0)
    assert screen_to_logical(100, 50, ox, oy, scale, 1280, 720) == (0, 0)

    # Un clic en (300, 250) -> rel (200, 200) / 2 = (100, 100)
    assert screen_to_logical(300, 250, ox, oy, scale, 1280, 720) == (100, 100)


def test_screen_to_logical_clamping() -> None:
    # Clic en barras negras (fuera del canvas) debe ser clamped
    ox, oy = 100, 50
    scale = 1.0
    # A la izquierda del offset
    assert screen_to_logical(10, 60, ox, oy, scale, 1280, 720) == (0, 10)
    # Por debajo de los límites lógicos
    assert screen_to_logical(100, 1000, ox, oy, scale, 1280, 720) == (0, 719)


def test_virtual_canvas_instance_and_resize() -> None:
    canvas = VirtualCanvas(1280, 720, (1920, 1080))
    assert canvas.logical_width == 1280
    assert canvas.logical_height == 720
    assert canvas.scale == 1.5

    canvas.resize_window(800, 600)
    assert canvas.scale == 0.625
    assert canvas.scaled_w == 800
    assert canvas.scaled_h == 450
