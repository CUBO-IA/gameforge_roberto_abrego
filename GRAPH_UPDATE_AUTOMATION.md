# Automatización de Actualización del Grafo — GameForge 2D (GRAPH_UPDATE_AUTOMATION.md)

> **Estado:** Documento de diseño y especificación operativa (Misión 005).  
> **Ámbito:** Ciclo de vida, sincronización incremental y prevención de obsolescencia.  
> **Autoridad:** Agente Director / QA de Integración.

---

## 1. Ciclo de Vida Operativo de la Memoria

Para garantizar que el grafo de conocimiento nunca quede obsoleto y sirva como una memoria operativa viva, todo agente en GameForge debe seguir un ciclo de vida bifásico estricto:

```
               [ INICIO DE TAREA DEL AGENTE ]
                             |
                             v
           +-----------------------------------+
           |    FASE 1: PRE-FLIGHT CHECK       |
           | 1. tools/graph_ops.py verify      |
           | 2. tools/graph_ops.py query       |
           | 3. tools/graph_ops.py affected    |
           +-----------------------------------+
                             |
                             v
             [ PLANIFICACIÓN E IMPLEMENTACIÓN ]
             (Modificaciones puras y desacopladas)
                             |
                             v
           +-----------------------------------+
           |   FASE 2: POST-FLIGHT UPDATE      |
           | 1. tools/graph_ops.py update      |
           | 2. tools/graph_ops.py verify      |
           | 3. Registro en audit.log          |
           +-----------------------------------+
                             |
                             v
                [ TAREA FINALIZADA Y LISTA ]
```

---

## 2. Detección Automática de Cambios (Drift Detection)

El sistema implementa un motor de detección de discrepancias (`ManifestTracker` en `tools/graph_memory/freshness.py`) que compara el estado físico del sistema de archivos contra el manifiesto persistido en `graphify-out/.manifest.json`.

El tracking se ejecuta en **menos de 20 milisegundos** calculando hashes criptográficos SHA-256 sobre archivos `.py`, `.md` y `.json`, ignorando directorios efímeros (`.venv`, `__pycache__`, `graphify-out`).

### 2.1. Clasificación de Eventos de Drift

```
                                [ ESCANEO SHA-256 ]
                                         |
            +----------------------------+----------------------------+
            |                            |                            |
            v                            v                            v
   [ MODIFICACIONES ]            [ ELIMINACIONES ]             [ RENOMBRADOS ]
   Hash diferente entre          Ruta en manifiesto pero       Hash coincide entre ruta
   manifiesto y disco            inexistente en disco          eliminada y nueva ruta
            |                            |                            |
            v                            v                            v
  Re-extracción AST delta        Poda de nodos con dicho       Actualización de ruta en
  y reemplazo in-place           source_file (sin fantasmas)   nodos y re-enlace de IDs
```

1. **Archivos Modificados:**
   - Detecta colisiones de ruta donde `hash_actual != hash_almacenado`.
   - Se programa únicamente la re-extracción de este archivo.
2. **Archivos Eliminados:**
   - Detecta rutas presentes en el manifiesto que ya no existen en disco.
   - Pasa la lista a la rutina de poda (`prune_sources`) de Graphify, eliminando sus nodos y aristas sin dejar "nodos fantasma" huérfanos.
3. **Archivos Renombrados:**
   - Algoritmo heurístico por coincidencia de hash SHA-256: si un archivo eliminado comparte el mismo hash que un archivo nuevo, se clasifica como `RENAMED (old_path -> new_path)`.
   - Se migra la atribución de `source_file` y se actualizan los IDs relacionados sin duplicar el coste de extracción.

---

## 3. Motor de Actualización Incremental (`build_merge`)

Un defecto habitual en los sistemas de grafos es recurrir a reconstrucciones completas (*full rebuild*) ante cualquier cambio menor, lo cual satura tokens y ralentiza los flujos de trabajo.

GameForge utiliza la tecnología `build_merge` de Graphify:

### 3.1. Flujo Incremental para Código (Delta AST)
1. **Detección selectiva:** Solo los archivos en el subconjunto `to_update` son analizados por el parser AST.
2. **Conservación de nodos intactos:** Los nodos y aristas de archivos no modificados se preservan íntegros desde `graph.json`.
3. **Sustitución in-place:** Los nodos antiguos cuyo `source_file` coincida con los archivos modificados son reemplazados por las nuevas definiciones AST.
4. **Poda garantizada:** Cualquier nodo perteneciente a `to_delete` es extirpado del grafo.
5. **Re-clustering local:** Se re-calculan las comunidades sobre la topología actualizada sin necesidad de llamadas a LLMs.

### 3.2. Comparativa de Rendimiento
- **Reconstrucción completa inicial:** **3,638 ms** (3.64 s)
- **Actualización incremental delta:** **235 ms**
- **Aceleración:** **~15.5x más rápido**

---

## 4. Prevención de Obsolescencia y Puntos de Integración

Para asegurar que ningún cambio llegue a las ramas principales o sea consumido por otros agentes sin que el grafo esté al día:

### 4.1. Verificación en Línea de Comandos
```powershell
# Modo informativo:
python tools/graph_ops.py verify

# Modo estricto para CI y pre-commit (código de salida 1 si hay drift):
python tools/graph_ops.py verify --strict
```

### 4.2. Hooks de Git
Graphify provee soporte nativo para instalar githooks automáticos:
```powershell
# Instalación del hook post-commit y post-checkout
graphify hook install
```
El hook post-commit:
1. Inspecciona `git diff HEAD~1` para obtener los archivos modificados.
2. Lanza en segundo plano la re-extracción AST de los archivos modificados.
3. Actualiza `graphify-out/graph.json` y `GRAPH_REPORT.md` en menos de 1 segundo.

### 4.3. Integración en `tools/verify.py`
El script central de verificación del proyecto (`tools/verify.py`) ejecuta la verificación de frescura del grafo como parte de su suite de control de calidad:
- Si un agente olvida actualizar el grafo tras implementar una tarea, `verify.py` reportará la discrepancia impidiendo la entrega de la tarea en `tasks/BOARD.md`.

---

## 5. Control de Concurrencia y Bloqueos

Cuando múltiples agentes colaboran simultáneamente en el mismo repositorio:
- Graphify utiliza bloqueos de archivo por repositorio (`.flock` o `msvcrt.locking` en Windows).
- Si un agente o hook está ejecutando una actualización incremental, cualquier otra llamada concurrente de actualización se encola ordenadamente sin corromper el archivo `graph.json`.
- La lectura del grafo a través del servidor MCP o CLI es segura y no bloqueante.

---

## 6. Registro de Auditoría Operativa (`audit.log`)

Todas las operaciones sobre la memoria operativa quedan registradas en formato JSON Lines en `graphify-out/audit.log`.

### 6.1. Esquema del Evento de Auditoría
```json
{
  "timestamp": "2026-11-07T07:58:51.962689+00:00",
  "operation": "UPDATE",
  "agent_id": "AGENTE_GAMEPLAY",
  "target": "1 updated, 0 deleted",
  "result": {
    "node_count": 2720,
    "edge_count": 5708,
    "updated_files": 1,
    "deleted_files": 0
  },
  "latency_ms": 242.15,
  "status": "SUCCESS"
}
```

Este registro provee una pista de auditoría inmutable que permite verificar qué agente consultó o actualizó qué subsistema y en qué momento exacto de la sesión.
