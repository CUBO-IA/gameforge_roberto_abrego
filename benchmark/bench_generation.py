"""Benchmark de generación de mazmorras.

Uso:
    python benchmark/bench_generation.py --count 50 --seed 1000
"""

from __future__ import annotations

import argparse
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from game.core.config import DungeonConfig  # noqa: E402
from game.world.generation import generate_dungeon  # noqa: E402


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, int(round(fraction * (len(ordered) - 1)))))
    return ordered[index]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=50)
    parser.add_argument("--seed", type=int, default=1000)
    parser.add_argument("--floor", type=int, default=1)
    args = parser.parse_args()
    if args.count < 1:
        parser.error("--count debe ser >= 1")

    config = DungeonConfig()
    times: list[float] = []
    rooms = 0
    enemies = 0
    for index in range(args.count):
        start = time.perf_counter()
        dungeon = generate_dungeon(args.seed + index, args.floor, config)
        times.append((time.perf_counter() - start) * 1000.0)
        rooms += len(dungeon.rooms)
        enemies += len(dungeon.enemies)

    print("GAMEFORGE 2D — benchmark de generación")
    print(f"mapa: {config.width}x{config.height}, salas objetivo: {config.rooms}")
    print(f"muestras: {len(times)}, semilla inicial: {args.seed}, piso: {args.floor}")
    print(f"p50: {statistics.median(times):.2f} ms")
    print(f"media: {statistics.fmean(times):.2f} ms")
    print(f"p95: {percentile(times, 0.95):.2f} ms")
    print(f"máximo: {max(times):.2f} ms")
    print(f"salas medias: {rooms / len(times):.1f}")
    print(f"enemigos medios: {enemies / len(times):.1f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
