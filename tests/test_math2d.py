import math

import pytest

from game.core.math2d import (
    Vec2,
    angle_difference,
    circles_overlap,
    clamp,
    lerp,
    normalize_angle,
)


def test_vector_arithmetic_and_length() -> None:
    a = Vec2(3, 4)
    assert a.length() == pytest.approx(5.0)
    assert (a + Vec2(1, 1)).as_tuple() == (4, 5)
    assert (a - Vec2(1, 1)).as_tuple() == (2, 3)
    assert (a * 2).as_tuple() == (6, 8)
    assert (2 * a).as_tuple() == (6, 8)
    assert (a / 2).as_tuple() == (1.5, 2.0)
    assert (-a).as_tuple() == (-3, -4)


def test_normalized_and_zero_vector() -> None:
    normalized = Vec2(0, 10).normalized()
    assert normalized.as_tuple() == pytest.approx((0.0, 1.0))
    assert Vec2().normalized().as_tuple() == (0.0, 0.0)


def test_clamped_limits_length() -> None:
    assert Vec2(10, 0).clamped(4).length() == pytest.approx(4.0)
    assert Vec2(3, 0).clamped(4).as_tuple() == (3, 0)


def test_angles_are_normalized() -> None:
    assert normalize_angle(3 * math.pi) == pytest.approx(-math.pi)
    assert normalize_angle(-4 * math.pi) == pytest.approx(0.0)
    assert angle_difference(0.1, -0.1) == pytest.approx(0.2)


def test_from_angle_and_overlap() -> None:
    vector = Vec2.from_angle(math.pi / 2, 5)
    assert vector.x == pytest.approx(0.0, abs=1e-9)
    assert vector.y == pytest.approx(5.0)
    assert circles_overlap(Vec2(0, 0), 2, Vec2(3, 0), 2)
    assert not circles_overlap(Vec2(0, 0), 1, Vec2(3, 0), 1)


def test_scalar_helpers() -> None:
    assert clamp(5, 0, 3) == 3
    assert clamp(-1, 0, 3) == 0
    assert lerp(0, 10, 0.5) == 5
    assert lerp(0, 10, 2) == 10
    with pytest.raises(ZeroDivisionError):
        _ = Vec2(1, 1) / 0
