"""Registro de auditoría operativa para Graphify en GameForge.

Registra cronológicamente cada consulta, impacto, actualización y verificación
efectuada por cualquier agente del ecosistema.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


class AuditLogger:
    def __init__(self, log_path: Path | None = None) -> None:
        self.log_path = log_path or (Path("graphify-out") / "audit.log")

    def log_event(
        self,
        operation: str,
        agent_id: str,
        target: str,
        result: dict[str, Any] | str,
        latency_ms: float = 0.0,
        status: str = "SUCCESS",
    ) -> dict[str, Any]:
        """Escribe una entrada estructurada en formato JSON Lines al archivo de auditoría."""
        event = {
            "timestamp": datetime.now(UTC).isoformat(),
            "operation": operation,
            "agent_id": agent_id,
            "target": target,
            "result": result,
            "latency_ms": round(latency_ms, 2),
            "status": status,
        }

        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")

        return event

    def read_events(self, limit: int = 50) -> list[dict[str, Any]]:
        """Lee los últimos eventos registrados."""
        if not self.log_path.is_file():
            return []
        lines = self.log_path.read_text(encoding="utf-8").strip().splitlines()
        events = []
        for line in lines[-limit:]:
            if line.strip():
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
        return events
