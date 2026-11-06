"""Compatibilidad: el combate vive ahora en ``game.sim.combat``.

Contrato público mantenido: ``resolve_player_attack`` conserva firma y
semántica. La importación real desde aquí está en desuso para código nuevo.
"""

from __future__ import annotations

from game.sim.combat import attack_hits_enemy, resolve_player_attack  # noqa: F401

__all__ = ["attack_hits_enemy", "resolve_player_attack"]
