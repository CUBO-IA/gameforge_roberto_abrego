# Referencias de código abierto — GAMEFORGE 2D

Verificar estado, versión, licencia y documentación actual antes de adoptar.
Para una investigación técnica y legal exhaustiva de cada repositorio, consultar [`REPOSITORY_RESEARCH.md`](../REPOSITORY_RESEARCH.md) y [`DEPENDENCY_AUDIT.md`](../DEPENDENCY_AUDIT.md).

| Proyecto | URL Oficial | Licencia | Estado en GameForge 2D | Veredicto Técnico |
|---|---|---|---|---|
| **Pygame CE** | https://github.com/pygame-community/pygame-ce | LGPL-2.1+ | **Adoptado** | Motor multimedia y display principal |
| **Pygame** | https://github.com/pygame/pygame | LGPL-2.1+ | Referencia | Referencia histórica/ecosistema |
| **Pymunk** | https://github.com/viblo/pymunk | MIT | Opcional | Física 2D reservada bajo condición ADR-002 |
| **esper** | https://github.com/benmoran56/esper | MIT | Opcional | Patrón ECS para futuros buffs/debuffs |
| **Tiled** | https://github.com/mapeditor/tiled | GPLv2 / BSD | **Adoptado** | Herramienta de autoría para mapas fijos JSON |
| **PyTMX** | https://github.com/bitcraft/pytmx | LGPLv3 | **Descartado** | Sustituido por cargador JSON nativo sin dependencias |
| **tilemap-generator** | https://github.com/damian-pastorini/tile-map-generator | MIT | **Descartado** | Ecosistema JS incompatible con runtime Python |
| **python-tcod** | https://github.com/libtcod/python-tcod | BSD-2-Clause | Algoritmos | Adoptados algoritmos (FOV, Dijkstra); librerías descartadas |
| **py_trees** | https://github.com/splintered-reality/py_trees | BSD-3-Clause | Conceptual | Estudiar para bosses; FSM en JSON para mobs |
| **SolarWolf** | https://github.com/pygame/solarwolf | LGPL-2.1+ | Referencia | Patrón de degradación segura de audio (ADR-008) |
| **pygame-topdownengine** | https://github.com/shaurya-sharma-dev/pygame-topdownengine | MIT / CC0 | **Patrones** | Adoptados patrones de Z-axis, sombras y Y-sorting |
| **Procedural-Maps** | https://github.com/strwdr/Procedural-Maps | **SIN LICENCIA** | **Prohibido** | Código prohibido por copyright; concepto Whittaker limpio |
| **opensimplex-island** | https://github.com/lmas/opensimplex | MIT / CC0 | **Algoritmo** | Adoptada máscara de decaimiento radial para cavernas |
| **Nemotron Personas El Salvador** | https://huggingface.co/datasets/nvidia/Nemotron-Personas-El-Salvador | CC-BY-4.0 | **Adoptado** | Perfiles demográficos, narrativa y diálogos de NPCs del Hub |

## Política de Licencias y Dependencias
- No copiar código sin verificar licencia (estrictamente prohibido copiar repositorios sin licencia explícita).
- No copiar sprites, música, fuentes ni mapas de terceros sin registrar procedencia y licencia en `assets/README.md`.
- Toda nueva dependencia requiere benchmark previo que justifique la imposibilidad técnica de desarrollarla en código nativo.
- Revalidar dependencias y congelar hashes en `uv.lock`.
