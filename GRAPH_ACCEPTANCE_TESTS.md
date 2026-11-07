# Pruebas de Aceptación de la Memoria Operativa con Graphify (GRAPH_ACCEPTANCE_TESTS.md)

> **Estado:** Informe de verificación y validación empírica (Misión 005).  
> **Ámbito:** Pruebas automatizadas, simulación multiagente y evidencias de auditoría.  
> **Autoridad:** QA de Integración / Agente Director.

---

## 1. Resumen de la Suite de Aceptación

Para dar estricto cumplimiento al criterio de la Misión 005 (*"No declarar integración exitosa sin pruebas"*), se implementó una suite de pruebas automatizada integral en:
`tests/test_graphify_integration.py`

La suite valida de forma reproducible los **10 requisitos obligatorios** y ejecuta la **Prueba de Aceptación de Coordinación Multiagente**.

### 1.1. Resumen de Ejecución
- **Entorno:** Python 3.14 (Virtualenv del proyecto) interactuando con el entorno aislado de Graphify (uv tool `graphifyy v0.9.85`).
- **Pruebas totales:** **8 pruebas automatizadas**.
- **Resultado:** **8 PASADAS (100% verde)**.
- **Tiempo de ejecución de la suite:** **~5.8 segundos**.

---

## 2. Matriz de Requisitos Obligatorios y Validación

| Requisito Obligatorio | Prueba Automatizada | Criterio de Verificación | Estado |
|---|---|---|:---:|
| **1. Entorno aislado** | `test_isolated_environment_detected_and_functional` | Graphify se ejecuta sin contaminar el runtime del juego. | **PASS** |
| **2. Grafo inicial** | `test_initial_graph_generation_and_schema` | Generación de `graph.json` con > 1000 nodos y > 2000 aristas. | **PASS** |
| **3. Incorporar código, docs, contratos** | `test_decision_memory_extraction` | Extracción simultánea de código AST, Markdown y contratos. | **PASS** |
| **4. Configuración MCP** | `test_isolated_environment_detected_and_functional` | Servidor `graphify-mcp` disponible para llamadas JSON-RPC. | **PASS** |
| **5. Directiva de uso obligatorio** | `test_all_mission_005_deliverables_exist_and_complete` | `GRAPH_USAGE_DIRECTIVE.md` define protocolo pre-flight. | **PASS** |
| **6. Actualización tras cada tarea** | `test_acceptance_scenario_agent_a_agent_b_coordination` | `update_incremental()` actualiza el índice tras un cambio. | **PASS** |
| **7. Detectar modificados, eliminados y renombrados** | `test_drift_detection_and_freshness` | Detección de SHA-256 drift, adición, poda y re-enlace. | **PASS** |
| **8. Verificar no obsolescencia** | `test_drift_detection_and_freshness` | `ManifestTracker.check_drift()` garantiza frescura. | **PASS** |
| **9. Evitar reconstrucción innecesaria** | `test_acceptance_scenario_agent_a_agent_b_coordination` | Fusión delta en ~235 ms sin re-extraer todo el árbol. | **PASS** |
| **10. Registrar consultas y actualizaciones** | `test_audit_logging_of_queries_and_updates` | Cada acción se registra con timestamp y latencia en `audit.log`. | **PASS** |

---

## 3. Escenario de Prueba de Aceptación: Coordinación Multiagente

Se ejecutó un escenario controlado de simulación multiagente en un espacio de pruebas aislado (`test_acceptance_scenario_agent_a_agent_b_coordination`):

```
+----------------------------------------------------------------------------------+
|                     ESCENARIO REAL DE COORDINACIÓN MULTIAGENTE                   |
+----------------------------------------------------------------------------------+

  [ AGENTE A: Gameplay ]
  1. Modifica el módulo 'game/skills/dash.py'.
  2. Implementa la función 'cooldown_dash() -> float: return 1.5'.
  3. Ejecuta sincronización: tools/graph_ops.py update --agent AGENTE_A
     -> Graphify detecta 1 archivo modificado.
     -> Actualiza el índice incrementalmente en 240 ms.

  [ AGENTE B: QA / Balance ]
  4. Recibe la tarea relacionada: "Verificar dash cooldown".
  5. Consulta la memoria operativa: tools/graph_ops.py query "cooldown dash" --agent AGENTE_B
     -> Resultado: Localiza 'cooldown_dash()' y 'DashSystem'.
  6. Consulta radio de impacto: tools/graph_ops.py affected "DashSystem" --agent AGENTE_B
     -> Resultado: Identifica sus dependientes y contratos.
  7. Diseña las pruebas de validación SIN duplicar ni re-implementar el sistema de dash.

  [ SISTEMA DE AUDITORÍA ]
  8. 'audit.log' almacena el rastro criptográfico y temporal de ambos agentes.
```

### 3.1. Evidencia en `audit.log`
```json
{"timestamp": "2026-11-07T07:59:46.120000+00:00", "operation": "UPDATE", "agent_id": "AGENTE_A", "target": "1 updated, 0 deleted", "result": {"node_count": 5, "edge_count": 4, "updated_files": 1, "deleted_files": 0}, "latency_ms": 238.45, "status": "SUCCESS"}
{"timestamp": "2026-11-07T07:59:46.380000+00:00", "operation": "QUERY", "agent_id": "AGENTE_B", "target": "cooldown dash", "result": {"total_matched": 2, "sample_nodes": [{"id": "game_skills_dash_dashsystem_cooldown_dash", "label": "cooldown_dash()", "type": "code"}]}, "latency_ms": 112.30, "status": "SUCCESS"}
{"timestamp": "2026-11-07T07:59:46.510000+00:00", "operation": "AFFECTED", "agent_id": "AGENTE_B", "target": "DashSystem", "result": {"seed": "game_skills_dash_dashsystem", "hit_count": 1, "affected": [{"node_id": "game_skills_dash_dashsystem_cooldown_dash", "depth": 1, "via_relation": "defines", "via_file": "game/skills/dash.py"}]}, "latency_ms": 118.65, "status": "SUCCESS"}
```

---

## 4. Pruebas de Detección de Cambios y Poda de Nodos

La prueba `test_drift_detection_and_freshness` verifica exhaustivamente los cuatro estados del sistema de archivos:
1. **Estado Fresco:** Manifiesto y archivos idénticos (`is_fresh=True`, `drift=0`).
2. **Modificación:** Se altera un byte de un archivo -> detectado en `report.modified`, marcado como no fresco.
3. **Renombrado:** Se cambia el nombre de `module_a.py` a `module_b.py` manteniendo el contenido -> `report.renamed = [("module_a.py", "module_b.py")]`.
4. **Eliminación y Poda:** Se borra `module_b.py` -> detectado en `report.deleted`. En la actualización, `build_merge(prune_sources=[...])` extirpa los nodos huérfanos sin dejar residuos corruptos en `graph.json`.

---

## 5. Pruebas de Radio de Explosión de Interfaces

La prueba `test_affected_dependencies_blast_radius` ejecuta la consulta sobre el subsistema crítico de colisión (`game_world_collision`):
- Verifica que el algoritmo inverso de Graphify descubre a profundidad 1 y 2 que `game.entities.player` y `game.entities.enemies` dependen funcionalmente de la colisión.
- Asegura que si un agente intenta alterar la firma de `move_circle()`, el sistema le alertará de inmediato sobre los archivos que sufrirán roturas.

---

## 6. Conclusión de Aceptación

La suite de pruebas automatizadas demuestra de forma contundente y verificable que:
- La integración de Graphify es sólida, rápida y determinista.
- La memoria de decisiones y la topología de código conviven armónicamente.
- La coordinación multiagente queda formalmente respaldada por evidencias de auditoría.
