"""Sistema de diálogos y comercio basado en Nemotron-Personas-El-Salvador.

ATRIBUCIÓN Y FUENTE OBLIGATORIA:
Este módulo consume datos de personas sintéticas del dataset abierto oficial de NVIDIA:
    Dataset: nvidia/Nemotron-Personas-El-Salvador
    Hugging Face: https://huggingface.co/datasets/nvidia/Nemotron-Personas-El-Salvador
    Licencia: Creative Commons Attribution 4.0 International (CC BY 4.0)
    Autores: NVIDIA Sovereign AI Initiative & WideLabs / Datos demográficos de El Salvador

Personajes integrados con UUIDs oficiales del dataset:
1. Doña Rosa (UUID: 108fefeb-c9f6-4429-8ce1-a67eaad444ef) - 39 años, La Libertad Centro.
   Comerciante del puesto de víveres, provisiones y frascos de brasa.
2. Maestro José (UUID: 2e2bca1d-f265-4214-beb3-858d676f2907) - 51 años, Santa Ana Oeste.
   Constructor y herrero estructural de edificios y herramientas de la Fragua.
3. Don Antonio (UUID: 0b125a4d-c467-4cc5-8789-968ae1ba7f01) - 88 años, Santa Ana Centro.
   Custodio sabio y archivista de insumos, guía de los Fragmentos Solares.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from game.systems.inventory import Inventory

PERSONAS_PATH = Path(__file__).resolve().parent.parent / "data" / "personas_el_salvador.json"

DATASET_NAME: str = "nvidia/Nemotron-Personas-El-Salvador"
DATASET_URL: str = "https://huggingface.co/datasets/nvidia/Nemotron-Personas-El-Salvador"
DATASET_LICENSE: str = "CC-BY-4.0"


@dataclass(frozen=True, slots=True)
class PersonaInfo:
    """Información completa de una persona del dataset Nemotron El Salvador."""

    uuid: str
    name: str
    role: str
    department: str
    municipality: str
    age: int
    occupation: str
    background: str
    greeting: str


@dataclass(frozen=True, slots=True)
class TradeResult:
    """Resultado de una operación comercial con un NPC."""

    success: bool
    item_id: str
    cost: int
    message: str


class DialogManager:
    """Gestiona los diálogos culturales y el comercio de los NPCs en el Hub."""

    def __init__(self, personas_file: Path | str | None = None) -> None:
        self.personas: dict[str, PersonaInfo] = {}
        self._load_dataset(personas_file or PERSONAS_PATH)

    def _load_dataset(self, path: Path | str) -> None:
        p = Path(path)
        if not p.is_file():
            return
        with open(p, encoding="utf-8") as f:
            data = json.load(f)

        personas_dict = data.get("personas", {})
        for role, raw in personas_dict.items():
            uuid = raw.get("uuid", "")
            dept = raw.get("department", "")
            muni = raw.get("municipality", "")
            age = int(raw.get("age", 0))
            occ = raw.get("occupation", "")
            prof = raw.get("professional_persona", "")
            name = prof.split(",")[0].strip() if prof else role.capitalize()

            if role == "merchant":
                greeting = (
                    f"¡Buenas! Pase adelante al puesto de Doña Rosa. Con 15 años de comerciar "
                    f"en {dept}, le aseguro que mis frascos de brasa le devolverán el aliento."
                )
            elif role == "blacksmith":
                greeting = (
                    f"Buenas tardes. Soy el Maestro José; 30 años levantando estructuras en "
                    f"{dept} me enseñaron que un acero firme y un buen cimiento salvan vidas."
                )
            elif role in ("elder", "quest_giver"):
                greeting = (
                    f"Saludos, viajero. Soy Don Antonio. A mis {age} años en {dept}, "
                    f"he aprendido que el rigor y la paciencia son indispensables: cuida tus fragmentos solares."
                )
            else:
                greeting = f"Saludos desde {dept}."

            self.personas[role] = PersonaInfo(
                uuid=uuid,
                name=name,
                role=role,
                department=dept,
                municipality=muni,
                age=age,
                occupation=occ,
                background=prof,
                greeting=greeting,
            )

    def get_persona(self, role: str) -> PersonaInfo | None:
        return self.personas.get(role)

    def get_dialog(self, role: str, shard_count: int = 0, shards_required: int = 3) -> str:
        """Devuelve el diálogo contextual del personaje."""
        persona = self.get_persona(role)
        if persona is None:
            return "El habitante te saluda con respeto."

        if role in ("elder", "quest_giver"):
            if shard_count >= shards_required:
                return (
                    f"¡Asombroso trabajo, muchacho! Don Antonio ({persona.age} años, {persona.department}) "
                    f"asiente con satisfacción: 'Tienes los {shard_count} fragmentos solares completos. "
                    f"El Altar de la Fragua aguarda tu encendido.'"
                )
            remaining = shards_required - shard_count
            return (
                f"Don Antonio te aconseja con paciencia: 'Te faltan {remaining} fragmento(s). "
                f"En mis años de archivo hospitalario en {persona.municipality} aprendí que ningún detalle "
                f"puede dejarse al azar. Desciende con cautela.'"
            )

        if role == "merchant":
            return (
                f"Doña Rosa sonríe desde su puesto de {persona.department}: "
                f"'¿Desea llevar un Frasco de Brasa por 15 monedas? En la Fragua el calor no perdona.'"
            )

        if role == "blacksmith":
            return (
                f"Maestro José examina tu equipo con mirada de constructor de {persona.municipality}: "
                f"'El temple de tu espada resistirá las criaturas inferiores. Para las profundidades, "
                f"mantén tu salto y esquiva los pozos de lava.'"
            )

        return persona.greeting

    def buy_potion(self, inventory: Inventory, cost: int = 15) -> TradeResult:
        """Compra un frasco de brasa en la tienda de Doña Rosa a cambio de monedas."""
        coins = inventory.count("coin")
        if coins < cost:
            return TradeResult(
                success=False,
                item_id="potion",
                cost=cost,
                message=f"No te alcanzan las monedas. Doña Rosa pide {cost} monedas (tienes {coins}).",
            )
        # Verificar espacio
        removed = inventory.remove("coin", cost)
        if removed < cost:
            return TradeResult(
                success=False,
                item_id="potion",
                cost=cost,
                message="Error en la transacción de monedas.",
            )
        added = inventory.add("potion", 1)
        if added <= 0:
            # Reembolsar
            inventory.add("coin", cost)
            return TradeResult(
                success=False,
                item_id="potion",
                cost=cost,
                message="Inventario lleno. Haz espacio antes de comprar.",
            )
        return TradeResult(
            success=True,
            item_id="potion",
            cost=cost,
            message="¡Compraste 1 Frasco de Brasa a Doña Rosa por 15 monedas!",
        )
