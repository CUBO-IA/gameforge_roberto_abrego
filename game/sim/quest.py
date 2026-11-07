"""Sistema de misiones dirigido por datos (Data-Driven Quest System).

Procesa objetivos de cacería, exploración y activación sin dependencias de Pygame.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from game.systems.inventory import Inventory


class QuestError(Exception):
    """Excepción para errores de esquema o validación de misiones."""


@dataclass(frozen=True, slots=True)
class QuestDefinition:
    id: str
    title: str
    description: str
    floor: int
    type: str  # "kill", "chest", "altar"
    target: str
    count: int
    reward_score: int
    reward_item: str
    reward_count: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> QuestDefinition:
        if not isinstance(data, dict):
            raise QuestError("La definición de misión debe ser un objeto JSON.")
        quest_id = data.get("id")
        if not isinstance(quest_id, str) or not quest_id.strip():
            raise QuestError("El campo 'id' de la misión debe ser un string no vacío.")
        count = int(data.get("count", 1))
        if count < 1:
            raise QuestError(f"La misión '{quest_id}' exige un count >= 1.")
        floor = int(data.get("floor", 1))
        if floor < 1:
            raise QuestError(f"La misión '{quest_id}' exige floor >= 1.")
        return cls(
            id=quest_id,
            title=str(data.get("title", quest_id)),
            description=str(data.get("description", "")),
            floor=floor,
            type=str(data.get("type", "kill")),
            target=str(data.get("target", "")),
            count=count,
            reward_score=int(data.get("reward_score", 0)),
            reward_item=str(data.get("reward_item", "")),
            reward_count=int(data.get("reward_count", 0)),
        )


@dataclass(slots=True)
class QuestProgress:
    quest_id: str
    current_count: int = 0
    completed: bool = False
    claimed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "quest_id": self.quest_id,
            "current_count": self.current_count,
            "completed": self.completed,
            "claimed": self.claimed,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> QuestProgress:
        return cls(
            quest_id=str(data["quest_id"]),
            current_count=int(data.get("current_count", 0)),
            completed=bool(data.get("completed", False)),
            claimed=bool(data.get("claimed", False)),
        )


@dataclass(frozen=True, slots=True)
class QuestReward:
    quest_id: str
    title: str
    score: int
    item_id: str
    item_count: int


def load_quest_catalog(path: Path | str | None = None) -> dict[str, QuestDefinition]:
    if path is None:
        path = Path(__file__).resolve().parents[1] / "data" / "quests.json"
    p = Path(path)
    if not p.is_file():
        raise QuestError(f"Archivo de catálogo de misiones no encontrado: {p}")
    try:
        with open(p, encoding="utf-8") as f:
            raw = json.load(f)
    except Exception as exc:
        raise QuestError(f"Error al parsear {p}: {exc}") from exc

    if not isinstance(raw, dict) or "quests" not in raw:
        raise QuestError("El JSON de misiones debe contener un array 'quests'.")

    catalog: dict[str, QuestDefinition] = {}
    for entry in raw["quests"]:
        quest = QuestDefinition.from_dict(entry)
        if quest.id in catalog:
            raise QuestError(f"ID de misión duplicado en catálogo: '{quest.id}'")
        catalog[quest.id] = quest
    return catalog


class QuestManager:
    """Gestiona el ciclo de vida y eventos de las misiones."""

    def __init__(self, catalog: dict[str, QuestDefinition] | None = None) -> None:
        self.catalog = catalog if catalog is not None else load_quest_catalog()
        self.progress: dict[str, QuestProgress] = {}

    def start_floor(self, floor: int) -> None:
        """Activa las misiones asignadas a la planta especificada."""
        for quest in self.catalog.values():
            if quest.floor == floor and quest.id not in self.progress:
                self.progress[quest.id] = QuestProgress(quest_id=quest.id)

    def on_kill(self, enemy_kind: str, inventory: Inventory | None = None) -> list[QuestReward]:
        """Avanza las misiones de tipo 'kill' que coincidan con enemy_kind."""
        rewards: list[QuestReward] = []
        for qid, prog in self.progress.items():
            if prog.completed:
                continue
            definition = self.catalog.get(qid)
            if definition and definition.type == "kill":
                if not definition.target or definition.target == enemy_kind:
                    prog.current_count += 1
                    if prog.current_count >= definition.count:
                        prog.completed = True
                        reward = self._claim(definition, prog, inventory)
                        if reward:
                            rewards.append(reward)
        return rewards

    def on_chest_opened(self, inventory: Inventory | None = None) -> list[QuestReward]:
        """Avanza las misiones de tipo 'chest'."""
        rewards: list[QuestReward] = []
        for qid, prog in self.progress.items():
            if prog.completed:
                continue
            definition = self.catalog.get(qid)
            if definition and definition.type == "chest":
                prog.current_count += 1
                if prog.current_count >= definition.count:
                    prog.completed = True
                    reward = self._claim(definition, prog, inventory)
                    if reward:
                        rewards.append(reward)
        return rewards

    def on_altar_activated(self, inventory: Inventory | None = None) -> list[QuestReward]:
        """Avanza las misiones de tipo 'altar'."""
        rewards: list[QuestReward] = []
        for qid, prog in self.progress.items():
            if prog.completed:
                continue
            definition = self.catalog.get(qid)
            if definition and definition.type == "altar":
                prog.current_count = definition.count
                prog.completed = True
                reward = self._claim(definition, prog, inventory)
                if reward:
                    rewards.append(reward)
        return rewards

    def _claim(
        self,
        quest: QuestDefinition,
        prog: QuestProgress,
        inventory: Inventory | None,
    ) -> QuestReward | None:
        if prog.claimed:
            return None
        prog.claimed = True
        if inventory is not None and quest.reward_item and quest.reward_count > 0:
            inventory.add(quest.reward_item, quest.reward_count)
        return QuestReward(
            quest_id=quest.id,
            title=quest.title,
            score=quest.reward_score,
            item_id=quest.reward_item,
            item_count=quest.reward_count,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "progress": [p.to_dict() for p in self.progress.values()]
        }

    @classmethod
    def from_dict(
        cls,
        raw: dict[str, Any],
        catalog: dict[str, QuestDefinition] | None = None,
    ) -> QuestManager:
        manager = cls(catalog=catalog)
        for item in raw.get("progress", []):
            prog = QuestProgress.from_dict(item)
            manager.progress[prog.quest_id] = prog
        return manager
