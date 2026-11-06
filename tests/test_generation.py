import pytest

from game.core.config import DungeonConfig
from game.core.math2d import Vec2
from game.world.generation import (
    GenerationError,
    generate_dungeon,
    is_reachable,
    reachable_cells,
)
from game.world.tiles import TileType

SMALL = DungeonConfig(
    width=40,
    height=32,
    tile_size=24,
    rooms=7,
    min_room=5,
    max_room=8,
    chests=4,
    shards_required=3,
    enemies_per_room=2,
    placement_attempts=60,
)


def tile_signature(dungeon) -> list[int]:
    return [int(tile) for _, _, tile in dungeon.tilemap.iter_tiles()]


def cell_of(position: Vec2, dungeon) -> tuple[int, int]:
    size = dungeon.tilemap.tile_size
    return int(position.x // size), int(position.y // size)


def test_same_seed_is_deterministic() -> None:
    first = generate_dungeon(1234, 1, SMALL)
    second = generate_dungeon(1234, 1, SMALL)
    assert tile_signature(first) == tile_signature(second)
    assert first.spawn.as_tuple() == second.spawn.as_tuple()
    assert first.altar.as_tuple() == second.altar.as_tuple()
    assert [(chest.id, chest.position.as_tuple(), chest.item_id) for chest in first.chests] == [
        (chest.id, chest.position.as_tuple(), chest.item_id) for chest in second.chests
    ]
    assert [enemy.id for enemy in first.enemies] == [enemy.id for enemy in second.enemies]


def test_different_seed_changes_map() -> None:
    first = generate_dungeon(10, 1, SMALL)
    second = generate_dungeon(11, 1, SMALL)
    assert tile_signature(first) != tile_signature(second)


def test_spawn_altar_and_chests_are_reachable() -> None:
    for seed in range(8):
        dungeon = generate_dungeon(seed, 1, SMALL)
        start = cell_of(dungeon.spawn, dungeon)
        assert dungeon.tilemap.tile_at(*start) != TileType.WALL
        targets = [cell_of(dungeon.altar, dungeon)]
        targets += [cell_of(chest.position, dungeon) for chest in dungeon.chests]
        targets.append(cell_of(dungeon.campfire, dungeon))
        reachable = reachable_cells(dungeon.tilemap, start)
        for target in targets:
            assert target in reachable
            assert is_reachable(dungeon.tilemap, start, target)


def test_chest_contract() -> None:
    dungeon = generate_dungeon(99, 1, SMALL)
    assert len(dungeon.chests) == SMALL.chests
    assert sum(1 for chest in dungeon.chests if chest.item_id == "shard") == 3
    assert len({chest.id for chest in dungeon.chests}) == len(dungeon.chests)
    for chest in dungeon.chests:
        assert chest.quantity >= 1
        assert dungeon.tilemap.tile_at(*cell_of(chest.position, dungeon)) != TileType.WALL


def test_enemies_are_placed_away_from_spawn() -> None:
    dungeon = generate_dungeon(7, 1, SMALL)
    assert dungeon.enemies
    assert len({enemy.id for enemy in dungeon.enemies}) == len(dungeon.enemies)
    for enemy in dungeon.enemies:
        cell = cell_of(enemy.position, dungeon)
        assert dungeon.tilemap.tile_at(*cell) == TileType.FLOOR
        assert (cell[0] - cell_of(dungeon.spawn, dungeon)[0]) ** 2 + (
            cell[1] - cell_of(dungeon.spawn, dungeon)[1]
        ) ** 2 >= 49


def test_deeper_floor_is_generated() -> None:
    dungeon = generate_dungeon(5, 3, SMALL)
    assert dungeon.floor == 3
    assert dungeon.rooms
    assert dungeon.altar != dungeon.spawn


def test_invalid_arguments_raise() -> None:
    with pytest.raises(ValueError):
        generate_dungeon(1, 0, SMALL)
    with pytest.raises(ValueError):
        generate_dungeon(1, 1, SMALL, attempts=0)


def test_impossible_map_raises_generation_error() -> None:
    impossible = DungeonConfig(
        width=16,
        height=16,
        rooms=20,
        min_room=10,
        max_room=10,
        chests=20,
        shards_required=20,
    )
    with pytest.raises(GenerationError):
        generate_dungeon(3, 1, impossible, attempts=2)
