# Matriz de propiedad de archivos — GAMEFORGE 2D

Cada ruta tiene un único agente responsable (definido en §9.2 de
`GAMEFORGE_2D_ARCHITECTURE_REVIEW.md`). Los archivos compartidos solo cambian
vía propuesta aprobada por el director. Regla vigente: quien implementa no se
autoaprueba.

| Ruta | Responsable | Notas |
|---|---|---|
| `architecture/`, `directives/`, `tasks/`, `prompts/` | DIRECTOR/ARQUITECTO | cambios de contrato requieren su aprobación |
| `GAMEFORGE_2D_ARCHITECTURE_REVIEW.md` | DIRECTOR/ARQUITECTO | documento de referencia aprobado |
| `game/core/`, `game/persistence/` | DIRECTOR/ARQUITECTO | contratos congelados salvo propuesta |
| `game/entities/`, `game/systems/`, `game/sim/` (F1+) | GAMEPLAY | incluye física tile-based existente |
| `game/render/`, `game/scenes/`, `game/input/` | PRESENTACIÓN | lienzo virtual en F4 |
| `game/world/generation.py`, `benchmark/bench_generation.py` | PROCEDURAL | multiplanta/biomas en F2-F3 |
| `game/ai/` (F2), `game/data/enemies.json` (comportamientos) | IA/NPC | A* presupuestado, FSM data-driven |
| `game/world/` (resto: tilemap, collision, camera, spatial) | GAMEPLAY | spatial.py en F3, coordinado con IA/NPC |
| `game/data/config.json` | COMPARTIDO | cambios con aprobación del director |
| `benchmark/bench_simulation.py`, `benchmark/METRICS.md`, `benchmark/agent_tasks/` | QA/INTEGRADOR | umbrales y suite de tareas estándar |
| `tools/verify.py` | QA/INTEGRADOR | único punto de verificación estándar |
| `tests/` | QA/INTEGRADOR (añade) | especialistas pueden añadir tests de su módulo vía tarea |
| `assets/` | PRESENTACIÓN | registro de licencias obligatorio |
| `documentation/` | DIRECTOR/ARQUITECTO | ADRs y plan de fases |

## Procedimiento de cambio

1. Tarea en `tasks/BOARD.md` con archivos permitidos declarados.
2. El responsable implementa solo dentro de su ámbito.
3. `python tools/verify.py` verde antes de entregar.
4. QA/INTEGRADOR ejecuta regresión y fusiona; el director cierra.
