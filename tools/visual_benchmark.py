"""Benchmark visual y de rendimiento del escenario jugable.

Arranca ``PlayScene`` en modo headless con una semilla fija, dibuja un número
determinista de frames y escribe capturas reales del renderizado del juego,
además de métricas de tiempo de carga, frame time y memoria pico.

Uso:
    python tools/visual_benchmark.py --label before --frames 120
"""

from __future__ import annotations

import argparse
import json
import os
import statistics
import time
import tracemalloc
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import sys  # noqa: E402
from pathlib import Path as _Path  # noqa: E402

ROOT = _Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pygame  # noqa: E402

from game.app import Application  # noqa: E402
from game.core.math2d import Vec2  # noqa: E402
from game.scenes.play import PlayScene  # noqa: E402
from tools.test_runner.capture import save_png  # noqa: E402

FIXED_DT = 1.0 / 60.0
SEED = 20261107


def _nearest_enemy(scene: PlayScene) -> Vec2 | None:
    if not scene.enemies:
        return None
    return min(
        scene.enemies,
        key=lambda enemy: enemy.position.distance_to(scene.player.position),
    ).position


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--label", default="current", help="Nombre del conjunto de capturas.")
    parser.add_argument("--frames", type=int, default=180)
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--output", default="artifacts/visual")
    parser.add_argument("--no-art", action="store_true", help="Desactiva ArtLibrary para medir línea base procedural.")
    args = parser.parse_args()

    output_dir = Path(args.output) / args.label
    output_dir.mkdir(parents=True, exist_ok=True)

    pygame.init()
    tracemalloc.start()
    load_started = time.perf_counter()
    app = Application(headless=True, data_dir=output_dir / "data")
    if args.no_art:
        app.art = None
    scene = PlayScene(app, seed=args.seed)
    if args.no_art:
        from game.render.tile_renderer import TileRenderer
        scene.tile_renderer = TileRenderer(scene.tilemap, art=None)
        scene.hud.art = None
    app.replace_scene(scene)
    load_ms = (time.perf_counter() - load_started) * 1000.0

    # Encuadre de combate: jugador cerca del primer enemigo y apuntando a él.
    hunt_target = _nearest_enemy(scene)
    if hunt_target is not None:
        scene.player.position = hunt_target + Vec2(46, 26)
        scene.camera.snap_to(
            scene.player.position, scene.tilemap.pixel_width, scene.tilemap.pixel_height
        )

    frame_times: list[float] = []
    captures: list[str] = []
    capture_at = {1, args.frames // 2, args.frames}
    try:
        for frame in range(1, args.frames + 1):
            app.input.begin_frame()
            for event in pygame.event.get():
                app.input.handle_event(event)
                scene.handle_event(event)
            started = time.perf_counter()
            scene.update(FIXED_DT)
            scene.draw(app.canvas.surface)
            frame_times.append((time.perf_counter() - started) * 1000.0)
            if frame in capture_at:
                name = f"frame_{frame:04d}.png"
                captures.append(str(save_png(app.canvas.surface.copy(), output_dir / name)))
            if frame == args.frames // 2:
                # Provoca un ataque real para capturar el golpe y sus efectos.
                scene.player.pending_attack = scene.player.build_attack()
                from game.sim.combat import resolve_player_attack

                resolve_player_attack(scene.player.pending_attack, scene.enemies)
                scene.effects.shake.add(4.0)
    finally:
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        app.shutdown()

    ordered = sorted(frame_times)
    report = {
        "label": args.label,
        "seed": args.seed,
        "frames": len(frame_times),
        "load_time_ms": round(load_ms, 2),
        "frame_ms_p50": round(statistics.median(ordered), 3),
        "frame_ms_p95": round(ordered[int(len(ordered) * 0.95) - 1], 3),
        "frame_ms_max": round(max(ordered), 3),
        "fps_equivalent": round(1000.0 / statistics.median(ordered), 1),
        "peak_memory_kb": round(peak / 1024.0, 1),
        "retained_memory_kb": round(current / 1024.0, 1),
        "tilemap": [scene.tilemap.width, scene.tilemap.height, scene.tilemap.tile_size],
        "enemies": len(scene.enemies),
        "captures": captures,
    }
    report_path = output_dir / "benchmark.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
