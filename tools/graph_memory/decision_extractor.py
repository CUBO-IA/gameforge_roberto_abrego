"""Extractor semántico de memoria de decisiones para GameForge.

Extrae entidades no-código (instrucciones, ADRs, tareas, contratos, problemas y soluciones)
y genera grafos enriquecidos sin confundir la memoria operativa con relaciones sintácticas del código.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any


def extract_decision_memory(root: Path) -> dict[str, list[dict[str, Any]]]:
    """Extrae la memoria de decisiones desde la documentación oficial del repositorio."""
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []

    # 1. ADRs desde documentation/DECISIONS.md
    decisions_file = root / "documentation" / "DECISIONS.md"
    if decisions_file.is_file():
        content = decisions_file.read_text(encoding="utf-8")
        blocks = re.split(r"(?=## ADR-)", content)
        for block in blocks:
            match = re.search(r"## (ADR-\d+)\s*—\s*([^\n]+)", block)
            if not match:
                continue
            adr_id = match.group(1).strip()
            title = match.group(2).strip()
            node_id = f"adr:{adr_id}"

            status_match = re.search(r"\*\*Estado:\*\*\s*([^\n]+)", block, re.IGNORECASE)
            status_str = status_match.group(1).strip() if status_match else "aceptada"
            epistemic = "COMPROBADA" if "aceptada" in status_str.lower() else "PROPUESTA"

            nodes.append({
                "id": node_id,
                "label": f"{adr_id}: {title}",
                "file_type": "rationale",
                "node_kind": "adr",
                "source_file": "documentation/DECISIONS.md",
                "status": status_str,
                "epistemic_state": epistemic,
            })

            # Detectar vinculaciones tecnológicas/conceptuales
            if "pygame" in block.lower():
                edges.append({
                    "source": node_id,
                    "target": "concept:pygame-ce",
                    "relation": "references",
                    "confidence": "EXTRACTED",
                    "source_file": "documentation/DECISIONS.md",
                })
            if "sqlite" in block.lower():
                edges.append({
                    "source": node_id,
                    "target": "concept:sqlite",
                    "relation": "references",
                    "confidence": "EXTRACTED",
                    "source_file": "documentation/DECISIONS.md",
                })
            if "graph" in block.lower():
                edges.append({
                    "source": node_id,
                    "target": "concept:knowledge_graph",
                    "relation": "references",
                    "confidence": "EXTRACTED",
                    "source_file": "documentation/DECISIONS.md",
                })

    # 2. Tareas desde tasks/BOARD.md
    board_file = root / "tasks" / "BOARD.md"
    if board_file.is_file():
        b_content = board_file.read_text(encoding="utf-8")
        blocks = re.split(r"(?=### T-)", b_content)
        for block in blocks:
            match = re.search(r"### (T-\d+)\s*—\s*([^\n]+)", block)
            if not match:
                continue
            tid = match.group(1).strip()
            title = match.group(2).strip()
            node_id = f"task:{tid}"

            resp_match = re.search(r"- Responsable:\s*([^\n]+)", block)
            responsible = resp_match.group(1).strip() if resp_match else "DIRECTOR"

            nodes.append({
                "id": node_id,
                "label": f"{tid}: {title}",
                "file_type": "concept",
                "node_kind": "task",
                "source_file": "tasks/BOARD.md",
                "responsible": responsible,
                "epistemic_state": "COMPROBADA",
            })

            # Vincular tareas con ADRs relacionados si se mencionan
            for adr_num in re.findall(r"ADR-(\d+)", block):
                edges.append({
                    "source": node_id,
                    "target": f"adr:ADR-{adr_num}",
                    "relation": "fulfills",
                    "confidence": "EXTRACTED",
                    "source_file": "tasks/BOARD.md",
                })

    # 3. Contratos desde architecture/CONTRACTS.md
    contracts_file = root / "architecture" / "CONTRACTS.md"
    if contracts_file.is_file():
        c_content = contracts_file.read_text(encoding="utf-8")
        contract_sections = re.findall(r"##\s+`?([a-zA-Z0-9_\.]+)`?", c_content)
        for c in set(contract_sections):
            if c in ("Game loop", "Input", "Entity", "World", "Inventory", "Persistence", "Events", "Regla"):
                node_id = f"contract:arch.{c.lower().replace(' ', '_')}"
            else:
                node_id = f"contract:{c}"

            nodes.append({
                "id": node_id,
                "label": f"Contract: {c}",
                "file_type": "concept",
                "node_kind": "contract",
                "source_file": "architecture/CONTRACTS.md",
                "epistemic_state": "COMPROBADA",
            })

            # Vincular contrato a símbolo de código coincidente
            if "." in c:
                edges.append({
                    "source": c,
                    "target": node_id,
                    "relation": "implements_contract",
                    "confidence": "EXTRACTED",
                    "source_file": "architecture/CONTRACTS.md",
                })

    # 4. Directivas desde directives/
    directives_dir = root / "directives"
    if directives_dir.is_dir():
        for dfile in directives_dir.glob("*.md"):
            d_id = f"directive:{dfile.stem}"
            nodes.append({
                "id": d_id,
                "label": f"Directive: {dfile.name}",
                "file_type": "document",
                "node_kind": "directive",
                "source_file": str(dfile.relative_to(root)).replace("\\", "/"),
                "epistemic_state": "COMPROBADA",
            })
            # La directiva gobierna las tareas
            edges.append({
                "source": d_id,
                "target": "task:T-901",
                "relation": "governs",
                "confidence": "EXTRACTED",
                "source_file": str(dfile.relative_to(root)).replace("\\", "/"),
            })

    # 5. Problemas conocidos y soluciones verificadas
    # Problema canónico: tunneling de colisión circular
    nodes.append({
        "id": "problem:CIRCULAR_COLLISION_TUNNELING",
        "label": "Problem: Tunneling en colisión círculo-tile a alta velocidad",
        "file_type": "rationale",
        "node_kind": "problem",
        "source_file": "architecture/CONTRACTS.md",
        "epistemic_state": "COMPROBADA",
    })
    nodes.append({
        "id": "solution:SUBDIVIDED_MOVE_CIRCLE",
        "label": "Solution: Subdivisión de desplazamiento en max_step=4.0px",
        "file_type": "rationale",
        "node_kind": "solution",
        "source_file": "game/world/collision.py",
        "epistemic_state": "COMPROBADA",
    })
    edges.append({
        "source": "solution:SUBDIVIDED_MOVE_CIRCLE",
        "target": "problem:CIRCULAR_COLLISION_TUNNELING",
        "relation": "solves",
        "confidence": "EXTRACTED",
        "source_file": "architecture/CONTRACTS.md",
    })
    edges.append({
        "source": "game.world.collision.move_circle",
        "target": "solution:SUBDIVIDED_MOVE_CIRCLE",
        "relation": "implements",
        "confidence": "EXTRACTED",
        "source_file": "game/world/collision.py",
    })
    edges.append({
        "source": "solution:SUBDIVIDED_MOVE_CIRCLE",
        "target": "tests.test_collision",
        "relation": "verified_by",
        "confidence": "EXTRACTED",
        "source_file": "tests/test_collision.py",
    })

    return {"nodes": nodes, "edges": edges}
