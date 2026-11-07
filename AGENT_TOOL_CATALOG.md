# AGENT_TOOL_CATALOG.md — GAMEFORGE 2D
## Catálogo Central de Herramientas, Contratos de Ejecución y Skills para Agentes

**Estado:** ESPECIFICACIÓN TÉCNICA NORMATIVA  
**Misión:** MISIÓN 006 — Investigación e Integración de Herramientas para Desarrollo 2D  
**Fecha:** 2026-11-07  
**Autor:** Director de Tecnología / Agente de Arquitectura e Integración  
**Proyecto:** GameForge 2D (RPG Modular en Python / Pygame CE)  

---

## 1. Propósito y Filosofía del Catálogo Central

Para que los agentes de programación (Claude Code, Antigravity, agentes de background) operen con máxima autonomía, calidad y consistencia sin depender de instrucciones manuales reiterativas ni inventar comandos inexistentes, este documento establece el **Catálogo Central Canónico de Herramientas de GameForge 2D**.

### Principios Fundamentales:
1. **Descubrimiento antes de la acción (*Pre-Flight Protocol*):** Todo agente debe consultar este catálogo antes de ejecutar comandos o intentar instalar paquetes.
2. **Prohibición de instalación autónoma no supervisada:** Ningún agente instalará librerías o dependencias de forma permanente en `pyproject.toml` o en el entorno global sin autorización explícita del Director de Arquitectura.
3. **Contratos Estrictos de Entrada y Salida:** Cada herramienta debe ejecutarse con parámetros deterministas y entregar salidas estructuradas (JSON o códigos de salida estándar) para que el agente valide el resultado sin ambigüedad.
4. **Eficiencia de Tokens:** Se priorizan comandos con formatos de salida concisos (`--json`, `--output-format=json`, `--quiet`) para proteger la ventana de contexto de los modelos LLM, de acuerdo con `directives/TOKEN_EFFICIENCY.md`.

---

## 2. Directorio Canónico de Herramientas por Categoría

| Categoría | Herramienta | Comando Canónico | Formato de Salida | Propósito Principal |
|:---|:---|:---|:---|:---|
| **Calidad de Código** | **Ruff** | `ruff check . --output-format=json` | JSON estructurado | Detección estática de errores de sintaxis, imports rotos y malas prácticas. |
| **Formateo de Código** | **Ruff Format** | `ruff format --check .` | Texto conciso / exit code | Verificación de consistencia de estilo y formato PEP 8. |
| **Tipado Estático** | **Pyright** | `python tools/typecheck.py` | Texto / JSON (`--json`) | Verificación de tipos con línea base y módulos obligados a cero. |
| **Testing del Motor** | **pytest** | `pytest -ra -q --tb=short` | Texto estructurado | Ejecución de suites unitarias y de integración del juego. |
| **Arnés de Jugabilidad**| **GF-TR** | `python -m tools.test_runner --scenario <path> --json` | JSON estructurado | Ejecución de escenarios headless con inyección de inputs y asserts. |
| **Inspección de Grafo**| **Graphify Ops** | `python tools/graph_ops.py query "<término>"` | JSON estructurado | Consulta de componentes existentes y radio de explosión (*blast radius*). |
| **Validación de Personaje**| **Validate Character**| `python tools/validate_character.py <manifest>` | Texto / exit code | Validación de esquemas de animación conforme a `gf-anim-v1`. |
| **Procesamiento Gráfico**| **Asset Hub CLI** | `python -m tools.asset_hub export --id <id>` | JSON / Archivos | Exportación y empaquetado de assets verificados. |
| **Conversión Multimedia**| **FFmpeg CLI** | `ffmpeg -i <in> -c:a libvorbis -q:a 4 <out>` | CLI / exit code | Transcodificación y normalización de audio a OGG Vorbis / WAV. |
| **Verificación Global** | **Verify** | `python tools/verify.py` | Salida estándar | Puerta de calidad obligatoria (Ruff + pytest + Bench + Grafo). |

### 2.1. Disponibilidad real de cada entrada (verificada 2026-11-07)

Antes de invocar cualquier comando, el agente debe distinguir entre herramienta **disponible** y
herramienta **planificada**. Invocar una entrada planificada es un error de ejecución, no una tarea.

| Entrada | Estado | Evidencia |
|:---|:---|:---|
| Ruff | **DISPONIBLE** | `.venv/Scripts/ruff.exe` 0.17.4 |
| Ruff Format | **DISPONIBLE** | incluido en el binario anterior |
| Pyright | **DISPONIBLE (vía npx)** | `pyrightconfig.json` + `tools/typecheck.py`; 46 errores base, `game/core` y `game/world` en 0 |
| pytest | **DISPONIBLE** | 9.1.1, 314 tests verdes |
| GF-TR | **DISPONIBLE (MVP)** | `tools/test_runner/`; 2 escenarios en `tests/scenarios/`; `python -m tools.test_runner` |
| Graphify Ops | **DISPONIBLE** | `tools/graph_ops.py` |
| Validate Character | **DISPONIBLE** | `tools/validate_character.py` |
| Asset Hub CLI | **DISPONIBLE** | `tools/asset_hub/` |
| FFmpeg CLI | **DISPONIBLE** | 8.1.1 en PATH |
| Verify | **DISPONIBLE** | `tools/verify.py` |
| `tools/record_tool_usage.py` | **PLANIFICADO** | no existe; el registro descrito en §6 es un esquema, no una implementación |
| `.gameforge/tool_registry.json` | **PLANIFICADO** | no existe en el repositorio |

### 2.2. Precondición de intérprete

Todo comando Python debe ejecutarse con el intérprete del entorno virtual del proyecto
(`.venv/Scripts/python.exe` en Windows). El Python del sistema no tiene `pygame` y hace fallar la
colección de 11 módulos de prueba. Los agentes no deben instalar dependencias para "arreglar" esto:
la dependencia correcta ya está en `.venv`.

---

## 3. Contratos de Entrada y Salida (I/O Contracts)

### 3.1. Contrato: Análisis Estático con Ruff
- **Invocación:**
  ```bash
  ruff check . --output-format=json
  ```
- **Contrato de Salida (JSON Schema):**
  ```json
  [
    {
      "code": "F401",
      "message": "'game.core.math2d.Vec2' imported but unused",
      "location": { "row": 12, "column": 5 },
      "end_location": { "row": 12, "column": 23 },
      "filename": "game/scenes/play.py",
      "fix": { "applicability": "safe" }
    }
  ]
  ```
- **Interpretación del Agente:**
  - `exit code == 0`: Base de código limpia. Proceder.
  - `exit code == 1`: Existen violaciones. Parsear archivo y línea; aplicar corrección manual o `ruff check --fix` solo si la corrección es segura.

### 3.2. Contrato: Verificación de Tipos con Pyright
- **Invocación:**
  ```bash
  npx --yes pyright --outputjson
  ```
- **Contrato de Salida (JSON Schema):**
  ```json
  {
    "version": "1.1.414",
    "time": "0.45s",
    "generalDiagnostics": [
      {
        "file": "c:/GIT HUB/GAMEFORGE/game/entities/player.py",
        "severity": "error",
        "message": "Argument of type 'None' cannot be assigned to parameter 'target' of type 'Vec2'",
        "range": {
          "start": { "line": 45, "character": 12 },
          "end": { "line": 45, "character": 16 }
        },
        "rule": "reportArgumentType"
      }
    ],
    "summary": { "filesAnalyzed": 68, "errorCount": 1, "warningCount": 0 }
  }
  ```
- **Interpretación del Agente:**
  - Si `errorCount > 0`, localizar las líneas afectadas y alinear la firma con el contrato definido en `architecture/CONTRACTS.md`.

### 3.3. Contrato: Escenario de Prueba en Game Test Runner (GF-TR)
- **Salida:** con `--json` se emite **siempre un array** con un resultado por escenario. Códigos de
  salida: `0` todos pasan, `1` algún escenario falla, `2` escenario inválido. Ejecutar desde la raíz
  del repositorio y con el intérprete de `.venv`.
- **Invocación:**
  ```bash
  python -m tools.test_runner --scenario tests/scenarios/chest_loot.json --json
  ```
- **Contrato de Salida (JSON Schema):**
  ```json
  {
    "scenario": "player_open_chest",
    "status": "PASSED",
    "frames_executed": 120,
    "elapsed_wall_ms": 24.5,
    "fps_achieved": 4897.9,
    "peak_memory_kb": 312.4,
    "assertions": [
      { "step": 30, "check": "player_reach_position", "passed": true },
      { "step": 60, "check": "input_interact_pressed", "passed": true },
      { "step": 90, "check": "chest_opened_state", "passed": true },
      { "step": 120, "check": "inventory_item_received", "passed": true }
    ],
    "visual_regression": {
      "golden_diff_percent": 0.00,
      "diff_image_path": null
    },
    "errors": []
  }
  ```

---

## 4. Especificación de Skills Especializadas para Agentes

Para que los agentes ejecuten tareas complejas con un flujo estandarizado, se definen cinco (5) skills operativas en GameForge:

```
┌────────────────────────────────────────────────────────────────────────┐
│               SKILLS ESPECIALIZADAS PARA AGENTES GAMEFORGE             │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
    ┌───────────────────────────────┼───────────────────────────────┐
    ▼                               ▼                               ▼
┌───────────────────────┐ ┌───────────────────────┐ ┌───────────────────────┐
│  agent-code-quality   │ │    agent-game-test    │ │  agent-asset-pipeline │
│ (Ruff + Pyright)      │ │  (Headless Scenarios) │ │ (Pillow + Validation) │
└───────────────────────┘ └───────────────────────┘ └───────────────────────┘
                │                               │
                ▼                               ▼
    ┌───────────────────────┐       ┌───────────────────────┐
    │   agent-map-editor    │       │  agent-audio-process  │
    │  (Tiled JSON Verify)  │       │ (FFmpeg Normalization)│
    └───────────────────────┘       └───────────────────────┘
```

### Skill 1: `agent-code-quality`
- **Gatillo de activación:** Antes de dar por terminado cualquier cambio en archivos de código Python (`.py`).
- **Flujo de ejecución:**
  1. Ejecutar `ruff check <archivos_modificados> --output-format=json`.
  2. Si hay errores de import o sintaxis, resolverlos inmediatamente.
  3. Ejecutar `ruff format --check <archivos_modificados>`.
  4. Ejecutar `npx pyright <archivos_modificados> --outputjson`.
  5. Asegurar 0 errores antes de pasar a la fase de pruebas.

### Skill 2: `agent-game-test`
- **Gatillo de activación:** Creación de mecánicas de gameplay, enemigos, balance de combate o interacciones.
- **Flujo de ejecución:**
  1. Crear o actualizar el archivo de escenario `.json` en `tests/scenarios/`.
  2. Ejecutar `python -m tools.test_runner --scenario <path> --json`.
  3. Verificar que todas las aserciones lógicas y colisiones retornen `passed: true`.
  4. Si hay regresión visual (>0.05% de variación), inspeccionar el diff generado en `artifacts/diff/`.

### Skill 3: `agent-asset-pipeline`
- **Gatillo de activación:** Incorporación o modificación de sprites, spritesheets o atlas de personajes.
- **Flujo de ejecución:**
  1. Procesar la imagen con `tools/asset_hub` o scripts con Pillow para empaquetado y recorte.
  2. Generar el manifiesto `metadata.json` conforme al formato `gf-anim-v1`.
  3. Ejecutar `python tools/validate_character.py <manifiesto>`.
  4. Comprobar que no existan fotogramas fuera de los límites de la textura (`tex_w`, `tex_h`).

### Skill 4: `agent-map-editor`
- **Gatillo de activación:** Creación o modificación de mapas autorales (pueblos, interiores, mazmorras).
- **Flujo de ejecución:**
  1. Diseñar o ajustar la cuadrícula y capas en Tiled o directamente en JSON.
  2. Validar que la capa de colisiones use GIDs válidos (`DEFAULT_GID_MAP`).
  3. Validar la existencia obligatoria de los puntos clave: `spawn` y `target`/`altar`.
  4. Ejecutar test unitario con `game.world.tiled_loader.load_tiled_json()`.

### Skill 5: `agent-audio-process`
- **Gatillo de activación:** Incorporación de efectos de sonido (SFX) o música ambiental.
- **Flujo de ejecución:**
  1. Verificar que el archivo de entrada cuente con licencia permisiva registrada en `assets/README.md`.
  2. Ejecutar comando FFmpeg de normalización y transcodificación:
     ```bash
     ffmpeg -i input_raw.wav -af "loudnorm=I=-14:LRA=7:tp=-1.5" -c:a libvorbis -q:a 4 assets/audio/sfx_output.ogg
     ```
  3. Comprobar que el archivo se reproduce limpiamente con el subsistema de audio de Pygame CE.

---

## 5. Integración con Hooks de Claude Code

Para garantizar que ningún agente pueda cometer errores o violar contratos de forma inadvertida, se especifica la configuración formal de ganchos (*hooks*) para el entorno de trabajo:

```json
{
  "hooks": {
    "pre-commit": [
      {
        "name": "Ruff Linter Guard",
        "command": "ruff check .",
        "description": "Impide commits si existen violaciones de linter",
        "blocking": true
      },
      {
        "name": "Graphify Drift Guard",
        "command": "python tools/graph_ops.py verify --strict",
        "description": "Impide commits si el grafo de conocimiento presenta desincronización",
        "blocking": true
      }
    ],
    "post-edit": [
      {
        "name": "Incremental File Quality",
        "command": "ruff check $EDITED_FILE",
        "description": "Valida la calidad inmediata del archivo recién modificado",
        "blocking": false
      }
    ],
    "post-test": [
      {
        "name": "Audit Logging",
        "command": "python tools/record_tool_usage.py --tool pytest --status $EXIT_CODE",
        "description": "Registra el resultado de la prueba en el log central",
        "blocking": false
      }
    ]
  }
}
```

---

## 6. Registro Central de Herramientas y Auditoría (`tool_registry.json`)

Para evitar duplicaciones y auditar el uso efectivo de las herramientas por parte de los distintos agentes, se define el esquema canónico del archivo `.gameforge/tool_registry.json`:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "GameForgeToolRegistry",
  "type": "object",
  "properties": {
    "version": { "type": "string", "enum": ["1.0.0"] },
    "last_updated": { "type": "string", "format": "date-time" },
    "registered_tools": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": { "type": "string" },
          "name": { "type": "string" },
          "binary": { "type": "string" },
          "canonical_args": { "type": "array", "items": { "type": "string" } },
          "category": { "type": "string" },
          "status": { "type": "string", "enum": ["ADOPTED", "EXPERIMENTAL", "DEPRECATED"] },
          "agent_skill": { "type": "string" }
        },
        "required": ["id", "name", "binary", "category", "status"]
      }
    },
    "execution_log": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "timestamp": { "type": "string" },
          "agent_id": { "type": "string" },
          "tool_id": { "type": "string" },
          "command": { "type": "string" },
          "exit_code": { "type": "integer" },
          "duration_ms": { "type": "number" }
        },
        "required": ["timestamp", "agent_id", "tool_id", "exit_code"]
      }
    }
  },
  "required": ["version", "registered_tools"]
}
```

---

## 7. Protocolos de Validación de Resultados y Manejo de Errores

Cuando una herramienta reporta un fallo durante la ejecución de una tarea por un agente:

1. **Protocolo ante Violación de Linter (Ruff):**
   - El agente no debe ocultar el error con `# noqa` ni desactivar reglas de forma indiscriminada.
   - Debe resolver la causa raíz: eliminar el import huérfano, declarar la variable o tipar el retorno.
2. **Protocolo ante Fallo de Tipado (Pyright):**
   - Verificar si el error se debe a discrepancia entre la implementación y los contratos de `architecture/CONTRACTS.md`.
   - Si el contrato cambió legalmente, actualizar primero la documentación y el grafo (`graph_ops.py update`).
3. **Protocolo ante Regresión Visual (Game Test Runner):**
   - Si la prueba visual falla, el agente debe comparar la imagen golden con la imagen actual generada.
   - Si el cambio visual era intencionado (e.g. nueva animación o cambio de color de armadura), se debe someter la nueva imagen golden a revisión y aprobación del Director antes de sobreescribirla.
4. **Protocolo ante Fallo de Tests de Regresión (pytest):**
   - No avanzar bajo ninguna circunstancia si `pytest` falla.
   - Aislar el test unitario fallido, analizar el traceback reducido y reparar la lógica del dominio.
