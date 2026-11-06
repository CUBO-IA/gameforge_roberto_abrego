"""Clasificación local en SQLite.

Se registra una fila por partida terminada. La base de datos es local y se
inicializa de forma idempotente al abrir el repositorio.
"""

from __future__ import annotations

import math
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


class ScoreError(ValueError):
    """Resultado inválido para la clasificación."""


@dataclass(frozen=True, slots=True)
class RunResult:
    seed: int
    floor: int
    score: int
    kills: int
    duration: float
    victory: bool


@dataclass(frozen=True, slots=True)
class ScoreEntry:
    id: int
    created_at: str
    seed: int
    floor: int
    score: int
    kills: int
    duration: float
    victory: bool


SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    seed INTEGER NOT NULL,
    floor INTEGER NOT NULL,
    score INTEGER NOT NULL,
    kills INTEGER NOT NULL,
    duration REAL NOT NULL,
    victory INTEGER NOT NULL
)
"""


class ScoreRepository:
    def __init__(self, database_path: str | Path) -> None:
        self.path = Path(database_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(str(self.path))
        self._connection.row_factory = sqlite3.Row
        with self._connection:
            self._connection.execute(SCHEMA)

    def record(self, result: RunResult) -> int:
        _validate_result(result)
        created_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        with self._connection:
            cursor = self._connection.execute(
                """
                INSERT INTO runs (created_at, seed, floor, score, kills, duration, victory)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    created_at,
                    result.seed,
                    result.floor,
                    result.score,
                    result.kills,
                    round(result.duration, 3),
                    1 if result.victory else 0,
                ),
            )
        return int(cursor.lastrowid)

    def top(self, limit: int = 10, victories_only: bool = False) -> list[ScoreEntry]:
        if not 1 <= limit <= 100:
            raise ScoreError("limit debe estar entre 1 y 100.")
        query = "SELECT * FROM runs"
        if victories_only:
            query += " WHERE victory = 1"
        query += " ORDER BY score DESC, duration ASC, id ASC LIMIT ?"
        rows = self._connection.execute(query, (limit,)).fetchall()
        return [
            ScoreEntry(
                id=row["id"],
                created_at=row["created_at"],
                seed=row["seed"],
                floor=row["floor"],
                score=row["score"],
                kills=row["kills"],
                duration=row["duration"],
                victory=bool(row["victory"]),
            )
            for row in rows
        ]

    def count(self) -> int:
        row = self._connection.execute("SELECT COUNT(*) AS total FROM runs").fetchone()
        return int(row["total"])

    def close(self) -> None:
        self._connection.close()

    def __enter__(self) -> "ScoreRepository":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()


def _validate_result(result: RunResult) -> None:
    if isinstance(result.seed, bool) or not isinstance(result.seed, int):
        raise ScoreError("seed inválida.")
    if not 0 <= result.seed <= (1 << 63) - 1:
        raise ScoreError("seed fuera de rango.")
    if not 1 <= result.floor <= 99:
        raise ScoreError("floor fuera de rango.")
    if not 0 <= result.score <= 1_000_000_000:
        raise ScoreError("score fuera de rango.")
    if not 0 <= result.kills <= 10_000_000:
        raise ScoreError("kills fuera de rango.")
    if (
        isinstance(result.duration, bool)
        or not isinstance(result.duration, (int, float))
        or not math.isfinite(float(result.duration))
        or not 0 <= float(result.duration) <= 10_000_000
    ):
        raise ScoreError("duration fuera de rango.")
    if not isinstance(result.victory, bool):
        raise ScoreError("victory debe ser booleano.")
