from pathlib import Path

import pytest

from game.persistence.scores import RunResult, ScoreError, ScoreRepository


def result(score: int, victory: bool = False, duration: float = 10.0, seed: int = 1) -> RunResult:
    return RunResult(
        seed=seed,
        floor=1,
        score=score,
        kills=3,
        duration=duration,
        victory=victory,
    )


def test_record_and_ranking(tmp_path: Path) -> None:
    path = tmp_path / "scores.sqlite3"
    with ScoreRepository(path) as repository:
        low = repository.record(result(100))
        high = repository.record(result(900, victory=True, duration=20))
        middle = repository.record(result(500))
        assert repository.count() == 3
        top = repository.top()
        assert [entry.score for entry in top] == [900, 500, 100]
        assert top[0].victory is True
        assert top[0].id == high
        assert {low, middle, high}.issubset({entry.id for entry in top})
        assert repository.top(2) == top[:2]
        assert [entry.score for entry in repository.top(victories_only=True)] == [900]


def test_ranking_tie_breaks_by_duration(tmp_path: Path) -> None:
    path = tmp_path / "scores.sqlite3"
    with ScoreRepository(path) as repository:
        slow = repository.record(result(500, duration=30))
        fast = repository.record(result(500, duration=10))
        assert [entry.id for entry in repository.top(2)] == [fast, slow]


def test_persistence_across_connections(tmp_path: Path) -> None:
    path = tmp_path / "scores.sqlite3"
    with ScoreRepository(path) as repository:
        repository.record(result(42))
    reopened = ScoreRepository(path)
    try:
        assert reopened.count() == 1
        assert reopened.top()[0].score == 42
    finally:
        reopened.close()


@pytest.mark.parametrize(
    "bad",
    [
        RunResult(seed=-1, floor=1, score=1, kills=0, duration=1, victory=False),
        RunResult(seed=1, floor=0, score=1, kills=0, duration=1, victory=False),
        RunResult(seed=1, floor=1, score=-1, kills=0, duration=1, victory=False),
        RunResult(seed=1, floor=1, score=1, kills=-1, duration=1, victory=False),
        RunResult(seed=1, floor=1, score=1, kills=0, duration=-1, victory=False),
        RunResult(seed=1, floor=1, score=1, kills=0, duration=1, victory=1),  # type: ignore[arg-type]
    ],
)
def test_invalid_results(tmp_path: Path, bad: RunResult) -> None:
    with ScoreRepository(tmp_path / "scores.sqlite3") as repository:
        with pytest.raises(ScoreError):
            repository.record(bad)


def test_invalid_limit(tmp_path: Path) -> None:
    with ScoreRepository(tmp_path / "scores.sqlite3") as repository:
        with pytest.raises(ScoreError):
            repository.top(0)
        with pytest.raises(ScoreError):
            repository.top(101)
