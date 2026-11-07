# Directiva de uso del grafo como memoria operativa (06_GRAPH_USAGE.md)

## Propósito
Garantizar la comprensión topológica, trazabilidad y prevención de duplicación en GameForge 2D mediante el uso obligatorio de Graphify como memoria operativa compartida.

## Principios
1. **Memoria operativa compartida:** El grafo en `graphify-out/graph.json` es la fuente canónica de verdad estructural del proyecto. Ningún agente debe basar sus decisiones en suposiciones si el grafo puede responderlas.
2. **Protocolo Pre-Flight obligatorio:** Antes de formular planes o escribir código, todo agente debe:
   - Consultar si los componentes, entidades o algoritmos requeridos ya existen (`python tools/graph_ops.py query "<concepto>"` o herramienta MCP `query_graph`).
   - Consultar el radio de explosión (*blast radius*) de dependencias antes de cambiar interfaces (`python tools/graph_ops.py affected "<símbolo>"`).
   - Verificar si la modificación entra en conflicto con algún ADR o contrato arquitectónico (`contract:*` o `adr:*`).
3. **Prohibición estricta de reinvención:** Si una clase (ej. `Vec2`), algoritmo (ej. `move_circle`, A* cuotado, Dijkstra) o recurso ya está presente en el grafo, es obligatorio reutilizarlo o componer sobre él. No duplicar código.
4. **Protocolo Post-Flight obligatorio:** Al concluir cualquier tarea con cambios en código o documentación, el agente debe:
   - Actualizar el grafo de forma incremental (`python tools/graph_ops.py update`).
   - Verificar que el grafo queda en estado fresco (`python tools/graph_ops.py verify --strict`).
5. **Registro de auditoría permanente:** Toda consulta, análisis de impacto y sincronización debe registrarse con identificador de agente en `graphify-out/audit.log`.
6. **Definición de Terminado (DoD):** Ninguna tarea se considerará aprobada ni verificada si `tools/verify.py` reporta drift de grafo o si los nuevos componentes no son consultables por otros agentes.
