# Directiva de Uso Obligatorio del Grafo como Memoria Operativa (GRAPH_USAGE_DIRECTIVE.md)

> **Directiva Formal:** `06_GRAPH_USAGE.md`  
> **Ámbito de Aplicación:** Todos los agentes (Director, Arquitectos, Programadores Gameplay/Engine, Diseñadores de Datos, QA).  
> **Autoridad:** Vinculante bajo `01_GLOBAL.md` y `TOKEN_EFFICIENCY.md`.

---

## 1. Principio Fundamental y Mandato de Uso Real

**No basta con que la herramienta Graphify esté instalada en el repositorio.**

Todo agente que intervenga en el proyecto **GameForge 2D** está obligado a consultar la memoria operativa en grafo antes de formular planes, inspeccionar código o realizar modificaciones, y a actualizarla inmediatamente después de concluir cualquier tarea relevante.

El objetivo de esta directiva es erradicar la duplicación accidental de código, prevenir regresiones en interfaces compartidas, y mantener una memoria viva y compartida de todas las decisiones de diseño.

---

## 2. Protocolo Obligatorio de 5 Pasos (Pre-Flight & Post-Flight)

Antes de editar cualquier archivo, y al terminar cada modificación, todo agente debe cumplir rigurosamente el siguiente protocolo:

```
[ PASO 1: Consulta Previa ]
  └─ Consultar si los componentes, entidades o algoritmos requeridos ya existen.
     Comando: python tools/graph_ops.py query "<concepto>"  (o MCP query_graph)

[ PASO 2: Análisis de Impacto (Blast Radius) ]
  └─ Si se prevé modificar una función, clase o módulo existente, calcular quién depende de él.
     Comando: python tools/graph_ops.py affected "<símbolo>" --depth 2

[ PASO 3: Verificación de Contratos y Decisiones ]
  └─ Comprobar si la modificación entra en conflicto con un ADR o contrato arquitectónico.
     Comando: python tools/graph_ops.py query "contract:<modulo>" / "adr:<numero>"

[ PASO 4: Implementación y Pruebas Puras ]
  └─ Realizar el cambio mínimo, sin tocar el motor si la tarea no lo autoriza.
     Comando: uv run pytest <pruebas_relevantes>

[ PASO 5: Sincronización y Auditoría Post-Flight ]
  └─ Actualizar el grafo incrementalmente y comprobar que queda en estado FRESCO.
     Comando: python tools/graph_ops.py update
     Comando: python tools/graph_ops.py verify --strict
```

---

## 3. Reglas Estrictas de Prevención de Duplicación

1. **Prohibición de Reinvención:**
   - Está terminantemente prohibido crear nuevas clases vectoriales si `game.core.math2d.Vec2` ya está disponible.
   - Está prohibido implementar rutinas de colisión ad-hoc si `game.world.collision` contiene `move_circle()` o `circle_hits_solid()`.
   - Está prohibido crear nuevos cargadores de animación si `game.render.animation` ya soporta `gf-anim-v1`.
2. **Consulta de Catálogo y Assets:**
   - Antes de generar un nuevo sprite o recurso, se debe consultar el grafo y el Asset Hub (`tools/asset_hub/`).
3. **Reutilización Guiada por Grafo:**
   - Si la consulta de Graphify arroja una similitud semántica superior al 70%, el agente debe reutilizar o extender el componente existente mediante composición, nunca duplicarlo.

---

## 4. Consulta Obligatoria de Dependencias antes de Modificar Interfaces

Cualquier cambio que afecte:
- Firmas de funciones públicas (`def foo(a, b) -> c`).
- Estructura de contratos en `architecture/CONTRACTS.md`.
- Campos de clases inmutables de configuración (`GameConfig`, `PlayerConfig`).
- Protocolos de comunicación entre capas (`sim/`, `render/`, `entities/`).

**Exige obligatoriamente la ejecución de:**
```powershell
python tools/graph_ops.py affected "<nombre_del_simbolo>"
```
El agente debe documentar en su informe de tarea (`tasks/reports/T-XXX.md`) la lista de nodos impactados y adjuntar la evidencia de que todas las pruebas de los módulos dependientes han sido ejecutadas y resultaron verdes.

---

## 5. Integración con la Directiva de Eficiencia de Tokens (`TOKEN_EFFICIENCY.md`)

1. **Lectura Selectiva:** El agente no debe utilizar comandos que impriman archivos de más de 200 líneas sin antes ubicar el rango de líneas o el símbolo específico mediante `get_node` de Graphify.
2. **Contexto Quirúrgico:** La consulta semántica al grafo extrae únicamente los nodos y relaciones relevantes, reduciendo el consumo de tokens por prompt en un **99.6%** comparado con la lectura masiva de archivos fuente.

---

## 6. Verificación de Consultabilidad y Control de Calidad

Una tarea **NO** se considerará terminada (DoD) si:
1. El comando `python tools/graph_ops.py verify --strict` devuelve código de error o detecta *drift*.
2. No existe al menos una entrada de actualización en `graphify-out/audit.log` asociada al identificador del agente (`agent_id`).
3. El nuevo componente, función o contrato no es consultable de forma inmediata por otro agente mediante `tools/graph_ops.py query`.

Cualquier PR o entrega que viole esta directiva será automáticamente rechazada por el Agente Director o por el script de verificación `tools/verify.py`.
