"""Benchmark de simulación sin ventana (jugador + enemigos + colisión).

Uso:
    python benchmark/bench_simulation.py --frames 3000 --enemies 24
"""

from __future__ import annotations

import argparse
import random
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from game.core.config import EnemyStats, GameConfig  # noqa: E402
from game.core.math2d import Vec2  # noqa: E402
from game.entities.enemies import Enemy, separate_enemies  # noqa: E402
from game.entities.player import Player  # noqa: E402
from game.systems.combat import resolve_player_attack  # noqa: E402
from game.world.generation import generate_dungeon  # noqa: E402


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, int(round(fraction * (len(ordered) - 1)))))
    return ordered[index]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--frames", type=int, default=3000)
    parser.add_argument("--enemies", type=int, default=24)
    parser.add_argument("--seed", type=int, default=7)
    args = parser.parse_args()
    if args.frames < 1 or args.enemies < 1:
        parser.error("--frames y --enemies deben ser >= 1")

    config = GameConfig()
    dungeon = generate_dungeon(args.seed, 1, config.dungeon)
    player = Player(dungeon.spawn, config.player)
    rng = random.Random(args.seed)
    kinds = ["slime", "wisp", "brute"]
    enemies: list[Enemy] = []
    for index in range(args.enemies):
        kind = kinds[index % len(kinds)]
        stats: EnemyStats = config.enemies[kind]
        position = dungeon.altar + Vec2(
            rng.uniform(-180, 180), rng.uniform(-180, 180)
        )
        enemies.append(Enemy(f"bench{index}", kind, position, stats))

    dt = 1.0 / 60.0
    samples: list[float] = []
    attack_timer = 0.0
    for frame in range(args.frames):
        start = time.perf_counter()
        angle = frame * 0.013
        move = Vec2.from_angle(angle)
        aim = Vec2.from_angle(angle + 0.8)
        attack = attack_timer <= 0.0
        if attack:
            attack_timer = 0.38
        attack_timer -= dt
        player.update(dt, move, aim, frame % 90 == 0, attack, dungeon.tilemap)
        if player.pending_attack is not None:
            resolve_player_attack(player.pending_attack, enemies)
        for enemy in enemies:
            if enemy.alive:
                enemy.update(dt, player.position, player.radius, dungeon.tilemap, rng)
        separate_enemies(enemies, dungeon.tilemap)
        enemies = [enemy for enemy in enemies if enemy.alive]
        samples.append((time.perf_counter() - start) * 1000.0)
        if not enemies:
            break

    print("GAMEFORGE 2D — benchmark de simulación (sin ventana)")
    print(
        f"frames: {len(samples)}, enemigos iniciales: {args.enemies}, "
        f"enemigos finales: {len(enemies)}"
    )
    print(f"p50: {statistics.median(samples):.3f} ms/frame")
    print(f"media: {statistics.fmean(samples):.3f} ms/frame")
    print(f"p95: {percentile(samples, 0.95):.3f} ms/frame")
    print(f"máximo: {max(samples):.3f} ms/frame")
    print(f"presupuesto 60 FPS: {1000 / 60:.2f} ms/frame")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
