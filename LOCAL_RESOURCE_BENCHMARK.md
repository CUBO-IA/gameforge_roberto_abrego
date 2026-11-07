# LOCAL_RESOURCE_BENCHMARK.md — GAMEFORGE 2D
## Benchmark de Recursos Locales del Sistema de Grafos

**Estado:** ESPECIFICACIÓN TÉCNICA NORMATIVA  
**Misión:** MISIÓN 004 — Sistema de Grafos, Memoria y Contexto Operativo  
**Fecha:** 2026-11-07  
**Autor:** Director / Arquitecto de Sistemas  
**Proyecto:** GameForge 2D (RPG Modular en Python / Pygame CE)  

---

## 1. Objetivo

Demostrar que GF-Graph opera dentro de presupuestos aceptables de tiempo, memoria, disco y tokens para un proyecto de la escala de GameForge 2D (~65 archivos Python, ~15,000 LOC) sin degradar la experiencia del desarrollador, sin requerir servicios de pago y sin interferir con el rendimiento del juego (presupuesto de 16.67 ms/frame a 60 FPS).

---

## 2. Perfil del Repositorio Actual

| Métrica | Valor |
|:---|:---|
| Archivos `.py` en `game/` | ~65 |
| Archivos de test en `tests/` | ~44 |
| Líneas totales de código (estimado) | ~15,000 |
| Tamaño promedio de archivo | ~230 LOC |
| Archivo más grande | `game/scenes/play.py` (~600 LOC) |
| Módulos con `__init__.py` | 11 |
| Archivos de datos JSON | 5 (`config.json`, `enemies.json`, `quests.json`, `recipes.json`, mapas) |
| Tests verdes actuales | 278 |
| Benchmark p95 actual | 1.29 ms/frame |

---

## 3. Métricas a Medir

### 3.1. Rendimiento temporal

| Métrica | Unidad | Umbral Aceptable | Umbral Óptimo | Justificación |
|:---|:---|:---|:---|:---|
| Indexación completa (cold start) | ms | <5,000 | <2,000 | `ast.parse` es ~1 ms/archivo para <500 LOC |
| Indexación incremental (1 archivo) | ms | <500 | <100 | Un solo parse + transacción SQLite |
| Indexación incremental (5 archivos) | ms | <1,000 | <300 | 5 parses + transacción batch |
| Consulta de subgrafo k=1 | ms | <50 | <10 | SELECT con índice compuesto |
| Consulta de subgrafo k=2 | ms | <100 | <20 | BFS de 2 niveles sobre índices |
| Generación de skeleton (1 archivo) | ms | <50 | <10 | Formateo de texto en memoria |
| Generación de skeleton (10 archivos) | ms | <200 | <50 | 10 formateos secuenciales |
| Análisis blast radius (BFS 3 niveles) | ms | <300 | <50 | BFS inverso con índice de target |
| Recálculo de PageRank | ms | <2,000 | <500 | NetworkX sobre ~65 nodos |
| Generación de recibo pre-flight | ms | <100 | <20 | Hash + INSERT |
| Verificación de recibo en verify.py | ms | <50 | <10 | SELECT por task_id |

### 3.2. Consumo de recursos

| Métrica | Unidad | Umbral Aceptable | Umbral Óptimo | Justificación |
|:---|:---|:---|:---|:---|
| Tamaño de `.gameforge/graph.db` | KB | <5,000 | <1,000 | ~65 archivos, ~2,000 nodos, ~5,000 aristas |
| Memoria RSS del proceso de indexación | MB | <200 | <50 | AST en memoria es compacto |
| Memoria RSS de consulta | MB | <50 | <20 | Solo subgrafo en memoria |
| CPU durante indexación completa | % (1 core) | <100% | <50% | Single-threaded, CPU-bound |
| Overhead en `verify.py` | ms | <1,000 | <200 | No debe degradar el benchmark existente |

### 3.3. Eficiencia de tokens

| Métrica | Unidad | Umbral Aceptable | Umbral Óptimo | Justificación |
|:---|:---|:---|:---|:---|
| Tokens del skeleton vs código fuente | ratio | <0.15 | <0.08 | Skeleton sin cuerpos de función |
| Tokens del subgrafo k=2 vs lectura completa | ratio | <0.30 | <0.10 | Solo firmas + relaciones |
| Tokens ahorrados por consulta típica | % | >50% | >80% | Comparado con leer archivos directamente |

---

## 4. Metodología de Medición

### 4.1. Herramientas

| Qué medir | Herramienta | Notas |
|:---|:---|:---|
| Tiempo de ejecución | `time.perf_counter_ns()` | Resolución de nanosegundos, sin overhead de GC |
| Memoria Python | `tracemalloc` | Picos de asignación de Python |
| Memoria RSS del proceso | `os.getpid()` + lectura de `/proc/PID/status` o `psutil` | Memoria total del proceso |
| Tamaño de BD | `os.path.getsize()` | Bytes en disco |
| Conteo de tokens | `len(text) // 4` | Estimación estándar 4 chars/token; alternativa: `tiktoken` si disponible |
| CPU time | `time.process_time_ns()` | Tiempo de CPU (no wall clock) |

### 4.2. Protocolo de medición

1. **Repeticiones**: 10 repeticiones por escenario.
2. **Warm-up**: 2 ejecuciones de descarte antes de medir.
3. **Reportar**: p50, p95, máximo y desviación estándar.
4. **Aislamiento**: Ejecutar sin otros procesos intensivos en CPU.
5. **BD limpia**: Cada repetición comienza con una BD vacía (cold) o pre-indexada (warm) según el escenario.

---

## 5. Escenarios de Benchmark

### Escenario A: Indexación Completa (Cold Start)

- **Precondición**: `.gameforge/graph.db` no existe o está vacío.
- **Acción**: `python tools/gf_graph.py index --full`
- **Medir**: Tiempo total, memoria RSS pico, tamaño final de BD, conteo de nodos y aristas.
- **Expectativa**: <2,000 ms para ~65 archivos.

### Escenario B: Indexación Incremental (1 archivo modificado)

- **Precondición**: BD completa y actualizada.
- **Acción**: Modificar `game/sim/combat.py` (añadir una línea de comentario), ejecutar `gf-graph index`.
- **Medir**: Tiempo de detección + parsing + actualización.
- **Expectativa**: <100 ms.

### Escenario C: Indexación Incremental (5 archivos modificados)

- **Precondición**: BD completa y actualizada.
- **Acción**: Modificar 5 archivos en `game/sim/` y `game/entities/`, ejecutar `gf-graph index`.
- **Medir**: Tiempo total batch.
- **Expectativa**: <300 ms.

### Escenario D: Consulta de Subgrafo para Tarea Típica

- **Precondición**: BD indexada.
- **Acción**: `gf-graph query --task T-802 --depth 2` (tarea que toca `game/sim/combat.py`).
- **Medir**: Tiempo de consulta, número de nodos/aristas retornados, tamaño en tokens del resultado.
- **Expectativa**: <20 ms, <50 nodos, <500 tokens de resultado.

### Escenario E: Generación de Skeletons (Top 10)

- **Precondición**: BD indexada con PageRank calculado.
- **Acción**: `gf-graph skeleton --top 10 --task T-802`
- **Medir**: Tiempo de generación, tokens generados vs tokens del código fuente completo.
- **Expectativa**: <50 ms, ratio <0.10.

### Escenario F: Blast Radius de Archivo Central

- **Precondición**: BD indexada.
- **Acción**: `gf-graph blast game/core/config.py --depth 3`
- **Medir**: Tiempo de BFS, número de nodos afectados por nivel.
- **Expectativa**: <50 ms. `config.py` es importado por muchos módulos → radio de explosión amplio.

### Escenario G: Comparación de Tokens

- **Precondición**: BD indexada.
- **Acción**: Para los 10 archivos más relevantes de una tarea típica, comparar:
  - Tokens del skeleton generado por GF-Graph.
  - Tokens del código fuente completo.
  - Tokens de leer solo las primeras 50 líneas (heurística ingenua).
- **Medir**: Ratios y porcentajes de ahorro.
- **Expectativa**: Skeleton < 15% del código completo.

---

## 6. Comparación con Alternativas Descartadas

### 6.1. Tabla comparativa de dependencias

| Característica | GF-Graph (elegido) | ctx (descartado) | CodeGraph (descartado) | Graphiti (descartado) |
|:---|:---|:---|:---|:---|
| **Lenguaje** | Python puro | Rust (binario) | TypeScript / Node.js | Python + Neo4j |
| **Instalación** | 0 dependencias nuevas (stdlib) + networkx opcional | `cargo install` o `winget` | `npm install` + compilación nativa | `pip install` + Neo4j server |
| **Tamaño de instalación** | ~0 MB (ya incluido en Python) | ~15 MB binario | ~100 MB (node_modules) | ~200 MB (Neo4j) |
| **Tiempo de setup** | 0 s (import ast) | 30-120 s (compilación/descarga) | 60-180 s | 120-300 s (Neo4j startup) |
| **Backend de datos** | SQLite (stdlib) | SQLite | RocksDB | Neo4j / FalkorDB |
| **Costo por operación** | 0 | 0 | 0 | LLM calls para extracción |
| **Compatibilidad Python 3.11** | ✅ Nativa | ❌ Binario externo | ❌ Node.js | ⚠️ Neo4j como servicio |
| **Lenguajes soportados** | Python (suficiente para GameForge) | 38+ lenguajes | 38+ lenguajes | Agnóstico (LLM) |
| **Sobreingeniería para GameForge** | Mínima | Moderada | Alta | Muy alta |

### 6.2. Justificación de la decisión

1. **ctx** ofrece rendimiento superior (~10x más rápido) por ser Rust nativo, pero introduce un binario externo que debe mantenerse actualizado y no se integra nativamente con el ecosistema Python de GameForge.

2. **CodeGraph** soporta 38 lenguajes (cuando GameForge es 100% Python) y requiere Node.js + RocksDB, añadiendo ~100 MB de dependencias para resolver un problema que `ast.parse` resuelve en <2 segundos.

3. **Graphiti** requiere un servidor Neo4j corriendo en segundo plano y realiza llamadas a LLMs para extraer tripletas semánticas, violando tanto la directiva de eficiencia de tokens como el requisito de cero servicios de pago.

Para un repositorio de ~65 archivos Python, la solución basada en `ast` + SQLite es la opción óptima en la intersección de **suficiencia funcional**, **cero dependencias externas** y **mantenibilidad a largo plazo**.

---

## 7. Integración con Benchmarks Existentes

### 7.1. No interferencia con el game loop

GF-Graph **nunca** se ejecuta durante el game loop. Opera exclusivamente como herramienta de desarrollo (pre-commit, pre-tarea, verify.py). Por tanto, no tiene impacto en el presupuesto de 16.67 ms/frame.

### 7.2. Integración con `tools/verify.py`

El paso de verificación de grafo se añade **después** del benchmark de simulación existente:

```
== lint (ruff) ==
== pruebas (pytest) ==
== benchmark de simulación ==
  [OK] p95=1.29 ms dentro del umbral informativo.
== verificación de grafo (gf-graph) ==         ← NUEVO
  Índice: 65 archivos, 0 obsoletos.
  Recibo: T-802 válido (emitido hace 3 min).
  Contratos: 25/25 vinculados.
  [OK] Grafo coherente.
```

### 7.3. Overhead aceptable en verify.py

El overhead del paso de grafo en verify.py debe ser <1,000 ms (idealmente <200 ms), manteniéndose como una fracción menor del tiempo total de verificación (~3 segundos actualmente).

---

## 8. Script de Benchmark Propuesto

### 8.1. Ubicación y nombre

```
benchmark/bench_gf_graph.py
```

### 8.2. Argumentos

| Argumento | Descripción | Default |
|:---|:---|:---|
| `--scenario` | Escenario a ejecutar (A-G o `all`) | `all` |
| `--repetitions` | Número de repeticiones | `10` |
| `--warmup` | Ejecuciones de descarte | `2` |
| `--output` | Formato de salida (`text`, `json`, `csv`) | `text` |
| `--db-path` | Ruta a la BD (usa temporal si se omite) | `None` (temp) |

### 8.3. Formato de salida

```
GAMEFORGE 2D — Benchmark GF-Graph
══════════════════════════════════
Escenario A: Indexación completa (cold start)
  archivos: 65, nodos: 2134, aristas: 5412
  p50:    1,245 ms
  media:  1,389 ms
  p95:    1,823 ms
  máximo: 2,104 ms
  BD: 487 KB, RSS pico: 34 MB

Escenario B: Indexación incremental (1 archivo)
  p50:     42 ms
  media:   51 ms
  p95:     78 ms
  máximo:  95 ms

...

Escenario G: Comparación de tokens
  Código fuente (10 archivos): 4,230 tokens
  Skeleton (10 archivos):        412 tokens
  Ratio: 0.097 (90.3% de ahorro)

═══════════════════════════════════
Todos los umbrales dentro del rango aceptable ✅
```

---

## 9. Requisitos de Eficiencia Cumplidos (Requisito 6)

| Requisito | Cumplimiento | Evidencia |
|:---|:---|:---|
| Consultas selectivas por tarea | ✅ | Subgrafo k-hop limitado por presupuesto de tokens |
| Contexto limitado a relaciones relevantes | ✅ | PageRank personalizado filtra por relevancia |
| Indexación incremental | ✅ | SHA-256 + mtime evita reparseo innecesario |
| Persistencia local | ✅ | SQLite WAL en `.gameforge/graph.db` |
| Sin servicios de pago obligatorios | ✅ | Cero dependencias de red, LLM o nube |
| Evitar modelos grandes si existen alternativas deterministas | ✅ | `ast.parse` es 100% determinista |
| Integración compatible con Python | ✅ | Usa solo stdlib + networkx (opcional) |
| Medir consumo de memoria, CPU, disco y tokens | ✅ | Benchmark con 7 escenarios y métricas completas |
