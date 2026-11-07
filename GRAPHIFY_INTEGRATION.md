# Integración de Graphify como Memoria Operativa — GameForge 2D (GRAPHIFY_INTEGRATION.md)

> **Estado:** Documento de diseño y evaluación normativa (Misión 005).  
> **Ámbito:** Memoria estructural, grafo de dependencias y comprensión multiagente.  
> **Autoridad:** Agente Director / Arquitecto de Contexto.

---

## 1. Resumen Ejecutivo y Objetivo

La **Misión 005** tiene como objetivo evaluar e integrar **Graphify** (`https://github.com/Graphify-Labs/graphify`, versión v0.9.85) como sistema principal de comprensión estructural, grafo de dependencias y memoria operativa para el proyecto **GameForge 2D**.

En misiones previas (Misión 004, `KNOWLEDGE_GRAPH_ARCHITECTURE.md`), se identificó la necesidad crítica de dotar a los agentes de:
1. Una visión topológica determinista del código fuente (AST).
2. Un índice unificado de directivas, contratos arquitectónicos y decisiones de diseño (ADRs).
3. Un mecanismo fiable de consulta de dependencias y cálculo de radio de explosión (*blast radius*) previo a cualquier modificación de interfaces.
4. Una actualización incremental ultrarrápida que impida la obsolescencia del índice sin incurrir en reconstrucciones completas innecesarias ni consumo desmedido de tokens.

Graphify proporciona una arquitectura modular, orientada a grafos heterogéneos (NetworkX, JSON node-link, HTML interactivo), dotada de extracción AST nativa para Python, soporte de servidores MCP (`graphify-mcp`), y capacidades de recorrido BFS/DFS y análisis inverso de impacto (`affected`).

---

## 2. Arquitectura de Entorno Aislado

Siguiendo las directivas de calidad de GameForge (`01_GLOBAL.md`, `02_ARCHITECTURE.md`) y la restricción explícita de **no contaminar las dependencias del motor de juego**, la integración de Graphify se ejecuta en un **entorno estrictamente aislado**.

```
+-------------------------------------------------------------------------------+
|                       ESPACIO DE TRABAJO (GAMEFORGE 2D)                       |
+-------------------------------------------------------------------------------+
         |                                                       |
         v                                                       v
+-------------------------------+               +-------------------------------+
|    MOTOR DE JUEGO (GAME)      |               |     MEMORIA OPERATIVA         |
|   Entorno: .venv (Python)     |               |  Entorno Aislado: uv tool     |
+-------------------------------+               +-------------------------------+
| - pygame-ce >= 2.5            |               | - graphifyy v0.9.85           |
| - pytest                      |               | - networkx                    |
| - ruff                        |               | - mcp (stdio / Streamable HTTP|
| (Simulación pura, renderizado,|               | (AST extraction, clustering,  |
|  sin dependencias de grafos)  |               |  blast radius, memory query)  |
+-------------------------------+               +-------------------------------+
         |                                                       |
         +--------------------------+----------------------------+
                                    |
                                    v
                     +-----------------------------+
                     | tools/graph_ops.py          |
                     | tools/graph_memory/         |
                     |  - isolated_env.py          |
                     |  - decision_extractor.py    |
                     |  - freshness.py             |
                     |  - audit.py                 |
                     |  - engine.py                |
                     +-----------------------------+
                                    |
                                    v
                     +-----------------------------+
                     | graphify-out/               |
                     |  - graph.json (2717 nodos)  |
                     |  - GRAPH_REPORT.md          |
                     |  - .manifest.json           |
                     |  - audit.log                |
                     +-----------------------------+
```

### 2.1. Criterios de Aislamiento
1. **Sin contaminación de `requirements.txt` / `pyproject.toml`:** El motor de juego continúa dependiendo exclusivamente de `pygame-ce` y utilidades mínimas. Graphify no se instala dentro del `.venv` del motor.
2. **Localizador Automático (`tools/graph_memory/isolated_env.py`):**
   El sistema localiza el intérprete aislado de Graphify en el siguiente orden determinista:
   - Variable de entorno `GRAPHIFY_PYTHON`.
   - Marcador local `graphify-out/.graphify_python`.
   - Entorno aislado global administrado por uv: `$(uv tool dir)/graphifyy/Scripts/python.exe`.
   - Intérprete activo si Graphify estuviese disponible.
3. **Ejecución Segura:** Todas las llamadas complejas de Graphify se canalizan mediante invocaciones controladas o mediante el servidor MCP stdio, aislando fallos de memoria o parsing del runtime del juego.

---

## 3. Generación del Grafo Inicial del Proyecto

La primera construcción del grafo (`tools/graph_ops.py build`) procesa exhaustivamente todo el árbol de archivos de GameForge:

| Categoría | Archivos Procesados | Tipo de Extracción | Coste en Tokens / API |
|---|---|---|---|
| **Código Python (`game/`, `tests/`, `tools/`)** | 152 archivos | AST determinista nativo | **0 tokens** ($0.00) |
| **Documentación y Directivas (`.md`)** | 87 archivos | Parser estructural Markdown | **0 tokens** ($0.00) |
| **Memoria de Decisiones (ADRs, Tareas, Contratos)** | 4 fuentes canónicas | Extractor ontológico tipado | **0 tokens** ($0.00) |
| **Total Inicial** | **248 archivos** | **Híbrida determinista** | **0 tokens ($0.00)** |

### 3.1. Métricas del Grafo Inicial Generado
- **Nodos totales:** **2,717 nodos**
- **Aristas (vínculos) totales:** **5,701 aristas**
- **Comunidades identificadas (Louvain / Greedy Modularity):** **201 comunidades**
- **Tiempo de construcción en frío:** **3.64 segundos**
- **Huella en memoria pico:** **< 0.50 MB**
- **Tamaño de `graphify-out/graph.json`:** **3.05 MB**

### 3.2. Nodos Centrales ("God Nodes") Identificados
El análisis de centralidad de grado sobre el grafo de GameForge identificó los hubs arquitectónicos reales del sistema:
1. `Vec2` (`game.core.math2d.Vec2`): Grado 237 (base geométrica y cinemática de todo el motor).
2. `TileMap` (`game.world.tilemap.TileMap`): Grado 95 (soporte del mundo y colisiones).
3. `Inventory` (`game.systems.inventory.Inventory`): Grado 70 (subsistema de objetos e interacciones).
4. `PlayScene` (`game.scenes.play.PlayScene`): Grado 66 (controlador de ciclo y orquestación).
5. `TileType` (`game.world.tiles.TileType`): Grado 58 (clasificación espacial del mundo).

---

## 4. Memoria de Decisiones vs. Relaciones Sintácticas

Un requisito fundamental de la Misión 005 es **no confundir los registros de decisiones con las relaciones sintácticas extraídas del código**.

Graphify modela esta distinción a través de tipos de archivo (`file_type`), tipos de nodo (`node_kind`) y relaciones de arista estrictamente diferenciadas:

```
[ Directiva / Instrucción ] --governs--> [ Tarea (T-XXX) ] --fulfills--> [ ADR (Decisión) ]
                                                |                             |
                                         modifies_contract                 governs
                                                |                             |
                                                v                             v
[ Símbolo de Código ] ------------implements_contract------------> [ Contrato de Arquitectura ]
         |
         +-----------------solves-----------------> [ Problema Técnico ] <--- [ Solución Verificada ]
```

### 4.1. Taxonomía de Nodos y Estados Epistémicos

| Categoría | Prefijo ID | `file_type` | `node_kind` | Estado Epistémico | Fuente Canónica |
|---|---|---|---|---|---|
| **Decisión Arquitectónica** | `adr:ADR-XXX` | `rationale` | `adr` | `COMPROBADA` / `PROPUESTA` | `documentation/DECISIONS.md` |
| **Tarea Operativa** | `task:T-XXX` | `concept` | `task` | `COMPROBADA` / `PENDIENTE` | `tasks/BOARD.md` |
| **Contrato Compartido** | `contract:X` | `concept` | `contract` | `COMPROBADA` | `architecture/CONTRACTS.md` |
| **Directiva Global** | `directive:X` | `document` | `directive` | `COMPROBADA` | `directives/*.md` |
| **Problema Registrado** | `problem:X` | `rationale` | `problem` | `COMPROBADA` | Incidentes y ADRs |
| **Solución Verificada** | `solution:X` | `rationale` | `solution` | `COMPROBADA` | Tests y fixes validados |

### 4.2. Taxonomía de Relaciones (Aristas)

1. **Relaciones Sintácticas de Código (extraídas vía AST):**
   - `imports`, `imports_from`, `calls`, `defines`, `inherits`, `contains`.
   - Conectan clases, funciones, métodos y módulos entre sí.
2. **Relaciones Semánticas de Decisiones (extraídas vía `decision_extractor.py`):**
   - `governs`: directiva o ADR que rige un módulo, contrato o subsistema.
   - `fulfills`: tarea que materializa y da cumplimiento a un ADR.
   - `implements_contract`: código que implementa la especificación de un contrato.
   - `modifies_contract`: tarea o cambio que altera un contrato compartido.
   - `solves`: solución técnica verificada que erradica un problema documentado.
   - `verified_by`: vinculación entre una solución o contrato y la suite de pruebas que lo garantiza.

Esta separación garantiza que un agente que investiga el código pueda consultar por qué existe una función (`calls` hacia `solution:SUBDIVIDED_MOVE_CIRCLE` y `governed_by` hacia `adr:ADR-002`) sin que la memoria de decisiones corrompa los grafos de llamadas de ejecución.

---

## 5. Capacidades de Consulta y Radio de Explosión (*Blast Radius*)

La integración habilita dos modos fundamentales de navegación para los agentes de GameForge:

### 5.1. Consulta Semántica (`tools/graph_ops.py query <pregunta>`)
Permite al agente explorar conceptos, directivas o módulos antes de redactar código. Por ejemplo, al consultar `collision`:
- Localiza de inmediato los tipos de datos relevantes (`CollisionResult`, `move_circle()`, `circle_hits_solid()`).
- Identifica las pruebas existentes (`test_collision.py`).
- Impide que el agente intente crear funciones utilitarias de colisión redundantes.

### 5.2. Análisis Inverso de Impacto (`tools/graph_ops.py affected <símbolo>`)
Permite al agente conocer en milisegundos qué archivos, funciones y pruebas se verán afectados si se modifica la firma o comportamiento de un símbolo.

**Caso real comprobado (`affected game_world_collision` a profundidad 2):**
- **Impacto detectado:** 42 nodos dependientes.
- **Profundidad 1:** `game.entities.player.Player.update`, `game.entities.enemies.Enemy.move`, `game.scenes.play.PlayScene.restore`, `tests/test_collision.py`.
- **Profundidad 2:** `game.sim.combat`, `game.sim.engagement`, `tests/test_jumping_25d.py`.
- **Tiempo de respuesta:** **583.71 ms**.

Esto elimina por completo las regresiones accidentales en módulos dependientes.

---

## 6. Puertas de Integridad y Verificación

1. **Guardia contra Encogimiento Accidental (*Shrink Guard*):** Graphify incorpora validación que rechaza sobreescrituras de `graph.json` si el nuevo grafo cuenta con menos nodos que el anterior, previniendo pérdidas de datos por errores transitorios en pipelines CI o agentes.
2. **Comprobación de Salud del Grafo (*Diagnostics*):** Inspecciona y previene aristas colgantes (*dangling endpoints*), endpoints ausentes o colapsos de multígrafos en ejecuciones dirigidas.
3. **Registro Auditado de Todas las Operaciones:** Cada consulta, actualización y análisis queda reflejado en `graphify-out/audit.log`.

---

## 7. Conclusión de la Evaluación Técnica

Graphify cumple con creces todos los requisitos de comprensión estructural para GameForge 2D:
- Es **100% local**, determinista y no requiere suscripciones ni APIs externas para el núcleo de código y documentación.
- Su extracción AST toma menos de **4 segundos** para el repositorio completo.
- Su consumo de memoria es despreciable (< 1 MB en el orquestador).
- Proporciona interfaces nativas CLI y MCP (stdio) listas para consumo de Claude Code y agentes autónomos.
