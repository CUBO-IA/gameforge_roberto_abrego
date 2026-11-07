# Configuración del Servidor MCP para Graphify — GameForge 2D (GRAPH_MCP_CONFIGURATION.md)

> **Estado:** Documento normativo de integración MCP (Misión 005).  
> **Ámbito:** Protocolo MCP (Model Context Protocol) para Claude Code y agentes autónomos.  
> **Autoridad:** Agente Director / Arquitecto de Herramientas.

---

## 1. Visión General del Servidor MCP de Graphify

Graphify incorpora nativamente un servidor **MCP (Model Context Protocol)** de alto rendimiento (`graphify-mcp` o `python -m graphify.serve`). Este servidor expone la memoria operativa, la topología de código y el grafo de dependencias de GameForge directamente como herramientas invocables por agentes de IA como **Claude Code**, **Claude Desktop** y **Google Antigravity**.

```
+-------------------------------------------------------------------------------+
|                             CLIENTES AGÉNTICOS                                |
|  - Claude Code (CLI)                                                          |
|  - Google Antigravity / Cursor / Claude Desktop                               |
+-------------------------------------------------------------------------------+
                                    |
                          Protocolo MCP (JSON-RPC)
                                    |
                                    v
+-------------------------------------------------------------------------------+
|                         GRAPHIFY MCP SERVER (stdio)                           |
|  Comando: $(GRAPHIFY_PYTHON) -m graphify.serve graphify-out/graph.json        |
+-------------------------------------------------------------------------------+
                                    |
          +-------------------------+-------------------------+
          |                                                   |
          v                                                   v
+-----------------------------+             +-----------------------------------+
|  HERRAMIENTAS EXPUESTAS     |             |  RECURSOS EN TIEMPO REAL          |
|  - query_graph              |             |  - graph.json (Hot-Reloading)     |
|  - get_node                 |             |  - GRAPH_REPORT.md                |
|  - get_neighbors            |             |  - audit.log                      |
|  - god_nodes                |             +-----------------------------------+
|  - graph_stats              |
|  - shortest_path            |
|  - get_community            |
+-----------------------------+
```

### 1.1. Características Clave
- **Hot-Reload Automático:** El servidor MCP detecta cambios de timestamp en `graphify-out/graph.json` y recarga el grafo en memoria bajo demanda sin necesidad de reiniciar el proceso.
- **Transporte Dual:** Soporta tanto `stdio` (estándar recomendado para agentes locales) como `Streamable HTTP` (para orquestadores distribuidos o multi-proceso).
- **Consumo Mínimo de Tokens:** Los agentes consultan nodos, vecinos y rutas específicas en lugar de volcar archivos enteros de código en la ventana de contexto.

---

## 2. Herramientas MCP Expuestas (Tool Specifications)

El servidor registra las siguientes herramientas bajo la especificación oficial de MCP:

### 2.1. `query_graph`
- **Descripción:** Realiza un recorrido semántico (BFS o DFS) sobre el grafo para responder preguntas técnicas sobre la arquitectura o el funcionamiento del código.
- **Argumentos:**
  - `query` (*string, requerido*): Pregunta o concepto a explorar (ej. `"sistema de inventario y almacenamiento de items"`).
  - `context` (*string, opcional*): Filtro contextual de relación.
  - `budget` (*integer, opcional, por defecto 2000*): Límite presupuestario en tokens para la respuesta estructurada.

### 2.2. `get_node`
- **Descripción:** Obtiene los metadatos completos, etiquetas, tipo de nodo, ubicación de archivo y líneas de definición de un símbolo o concepto.
- **Argumentos:**
  - `node_id` (*string, requerido*): Identificador exacto del nodo (ej. `"game_world_collision_move_circle"`, `"adr:ADR-002"`).

### 2.3. `get_neighbors`
- **Descripción:** Devuelve los vecinos entrantes (quién depende de este nodo) y salientes (de quién depende este nodo) junto con el tipo de relación.
- **Argumentos:**
  - `node_id` (*string, requerido*): Identificador del nodo raíz.
  - `direction` (*string, opcional, enum: `["both", "incoming", "outgoing"]`, por defecto `"both"`*).

### 2.4. `god_nodes`
- **Descripción:** Devuelve los nodos con mayor centralidad de grado (los centros neurálgicos y clases maestras de la arquitectura).
- **Argumentos:**
  - `limit` (*integer, opcional, por defecto 10*).

### 2.5. `graph_stats`
- **Descripción:** Muestra estadísticas en tiempo real del grafo: cantidad de nodos, aristas, densidad de conexiones y cantidad de comunidades detectadas.

### 2.6. `shortest_path`
- **Descripción:** Encuentra la ruta más corta de dependencias o llamadas entre dos nodos conceptuales o de código.
- **Argumentos:**
  - `source` (*string, requerido*): Nodo de origen.
  - `target` (*string, requerido*): Nodo de destino.
  - `directed` (*boolean, opcional, por defecto `true`*).

---

## 3. Configuración para Clientes de Agentes

### 3.1. Configuración para Claude Code (`.mcp.json`)

Para que **Claude Code** cargue automáticamente el servidor MCP de Graphify al abrir el repositorio, se configura el archivo `.mcp.json` en la raíz de `GAMEFORGE`:

```json
{
  "mcpServers": {
    "graphify": {
      "command": "C:\\Users\\PC\\AppData\\Roaming\\uv\\tools\\graphifyy\\Scripts\\python.exe",
      "args": [
        "-m",
        "graphify.serve",
        "C:\\GIT HUB\\GAMEFORGE\\graphify-out\\graph.json"
      ],
      "env": {
        "PYTHONIOENCODING": "utf-8"
      }
    }
  }
}
```

> **Nota:** La ruta del comando debe apuntar siempre al intérprete aislado reportado por `tools/graph_ops.py` (o `tools/graph_memory/isolated_env.py`).

### 3.2. Configuración en `CLAUDE.md` (Integración Nativa)
Para indicar a Claude Code las directivas de consulta obligatoria, se ejecuta:
```powershell
graphify claude install
```
Esto registra la siguiente instrucción de uso permanente en `CLAUDE.md`:
```markdown
## Memoria Operativa con Graphify
- Antes de responder dudas sobre arquitectura o flujo de datos, consulta la memoria del grafo con MCP (`query_graph` o `get_node`).
- Antes de modificar interfaces compartidas, verifica el impacto con `get_neighbors` o `graphify affected`.
- Tras completar tareas con cambios de código o contratos, ejecuta `python tools/graph_ops.py update` para mantener el grafo sincronizado.
```

### 3.3. Configuración para Claude Desktop (`claude_desktop_config.json`)

Ubicación en Windows: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "gameforge-graph": {
      "command": "C:\\Users\\PC\\AppData\\Roaming\\uv\\tools\\graphifyy\\Scripts\\python.exe",
      "args": [
        "-m",
        "graphify.serve",
        "C:\\GIT HUB\\GAMEFORGE\\graphify-out\\graph.json"
      ]
    }
  }
}
```

---

## 4. Modo Estricto y Gancho PreToolUse (*Strict Mode*)

Graphify soporta una política de contención de tokens denominada **Strict Mode**.

Cuando se activa `strict=True` en la instalación de Claude Code (`graphify claude install --strict`):
1. El hook `PreToolUse` intercepta cualquier intento del agente de leer archivos completos a ciegas (usando herramientas como `read_file` o `cat`).
2. Si el agente no ha ejecutado al menos una consulta inicial (`query_graph` o `graphify query`) en la sesión para acotar el problema, la lectura es pausada informando al agente:
   > *"Consulta el grafo de Graphify primero para ubicar exactamente los símbolos relevantes antes de leer archivos completos."*
3. Esto ahorra hasta un **90% del contexto**, forzando al modelo a trabajar con precisión quirúrgica.

---

## 5. Seguridad, Permisos y Sandbox

1. **Solo Lectura a través de MCP:** El servidor MCP opera estrictamente como un visor indexado. Ningún comando de MCP puede modificar archivos del código fuente o la arquitectura directamente. Las actualizaciones se efectúan mediante los scripts supervisados (`tools/graph_ops.py update`).
2. **Sin Exposición a Red Externa:** Por defecto, el transporte `stdio` no abre puertos de red. Si se utiliza transporte HTTP, este se vincula exclusivamente a la interfaz local de loopback (`127.0.0.1:8080`), protegido por clave de API opcional si se comparte entre procesos (`GRAPHIFY_API_KEY`).
3. **Determinismo Cero-Fugas:** No se transmiten claves de API ni código a proveedores externos de LLM durante el servicio de MCP.
