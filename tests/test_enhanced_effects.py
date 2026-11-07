"""Pruebas unitarias para los efectos visuales mejorados (Hitstop, TraumaShake, ParticlePool)."""

from __future__ import annotations

from game.render.effects import HitstopManager, ParticlePool, TraumaScreenShake


def test_hitstop_manager_lifecycle() -> None:
    hitstop = HitstopManager()
    assert hitstop.is_frozen is False

    # Activar hitstop de 0.06s (aprox 3-4 frames)
    hitstop.trigger(0.06)
    assert hitstop.is_frozen is True

    # Durante la pausa, update(0.02) devuelve False (congelado)
    can_advance = hitstop.update(0.02)
    assert can_advance is False
    assert hitstop.is_frozen is True

    # Avanzar 0.05s más: debe superar la duración y volver a permitir simulación
    can_advance = hitstop.update(0.05)
    assert can_advance is True
    assert hitstop.is_frozen is False


def test_trauma_screen_shake_physics() -> None:
    shake = TraumaScreenShake(max_offset_px=10.0, max_angle_deg=2.0, decay_rate=2.0)
    assert shake.trauma == 0.0

    off, angle = shake.get_transform()
    assert off.x == 0.0 and off.y == 0.0
    assert angle == 0.0

    # Añadir trauma moderado
    shake.add_trauma(0.5)
    assert shake.trauma == 0.5

    shake.update(0.016)
    off, angle = shake.get_transform()
    # Con trauma=0.5, shake cuadrático = 0.25, produce desplazamiento no nulo
    assert abs(off.x) > 0.0 or abs(off.y) > 0.0

    # Decaimiento continuo: tras 0.3s con decay_rate=2.0, trauma debe reducirse
    shake.update(0.3)
    assert shake.trauma < 0.5


def test_particle_pool_zero_allocation_lifecycle() -> None:
    pool = ParticlePool(capacity=10)
    assert pool.count == 0

    # Generar 5 partículas
    for i in range(5):
        spawned = pool.spawn(
            x=float(i * 10),
            y=0.0,
            vx=10.0,
            vy=0.0,
            life=0.1 if i == 0 else 1.0,  # La partícula 0 morirá primero
            size=2.0,
            color=(255, 100, 100),
        )
        assert spawned is True

    assert pool.count == 5

    # Llenar hasta la capacidad (10)
    for _ in range(5):
        assert pool.spawn(0, 0, 0, 0, 1.0, 1.0, (255, 255, 255)) is True
    assert pool.count == 10

    # El pool está saturado: el siguiente spawn devuelve False
    assert pool.spawn(0, 0, 0, 0, 1.0, 1.0, (255, 255, 255)) is False

    # Actualizar 0.15s: la partícula con vida 0.1 debe eliminarse mediante swap-and-pop en O(1)
    pool.update(0.15)
    assert pool.count == 9

    # Limpiar pool
    pool.clear()
    assert pool.count == 0
