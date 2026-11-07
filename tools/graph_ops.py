#!/usr/bin/env python
"""tools/graph_ops.py — Herramienta operativa CLI para la memoria de grafos de GameForge."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

# Añadir raíz al sys.path para permitir importaciones
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tools.graph_memory.engine import GraphEngine  # noqa: E402
from tools.graph_memory.freshness import ManifestTracker  # noqa: E402
from tools.graph_memory.isolated_env import find_graphify_python  # noqa: E402


def cmd_build(args: argparse.Namespace) -> None:
    engine = GraphEngine(PROJECT_ROOT)
    print(f"Generando grafo inicial en {engine.out_dir}...")
    res = engine.build_initial_graph(agent_id=args.agent)
    print(f"Construcción finalizada en {res['latency_ms']:.2f} ms")
    print(json.dumps(res["metrics"], indent=2))


def cmd_update(args: argparse.Namespace) -> None:
    engine = GraphEngine(PROJECT_ROOT)
    print("Ejecutando actualización incremental...")
    res = engine.update_incremental(
        changed_paths=args.files if args.files else None,
        agent_id=args.agent,
    )
    print(f"Actualización completada en {res['latency_ms']:.2f} ms")
    if "metrics" in res:
        print(json.dumps(res["metrics"], indent=2))


def cmd_query(args: argparse.Namespace) -> None:
    engine = GraphEngine(PROJECT_ROOT)
    question = " ".join(args.question)
    print(f"Consultando grafo: '{question}'...")
    res = engine.query(question, agent_id=args.agent)
    print(f"Consulta completada en {res['latency_ms']:.2f} ms")
    print(json.dumps(res["result"], indent=2))


def cmd_affected(args: argparse.Namespace) -> None:
    engine = GraphEngine(PROJECT_ROOT)
    print(f"Analizando impacto y dependencias para: '{args.node}' (profundidad {args.depth})...")
    res = engine.affected(args.node, depth=args.depth, agent_id=args.agent)
    print(f"Análisis completado en {res['latency_ms']:.2f} ms")
    print(json.dumps(res["result"], indent=2))


def cmd_verify(args: argparse.Namespace) -> None:
    tracker = ManifestTracker(PROJECT_ROOT)
    report = tracker.check_drift()
    print(f"Estado del grafo: {'FRESCO (Al día)' if report.is_fresh else 'DESACTUALIZADO'}")
    if not report.is_fresh:
        print(f"  Modificados: {len(report.modified)}")
        for m in report.modified[:5]:
            print(f"    - {m}")
        print(f"  Añadidos:    {len(report.added)}")
        for a in report.added[:5]:
            print(f"    - {a}")
        print(f"  Eliminados:  {len(report.deleted)}")
        for d in report.deleted[:5]:
            print(f"    - {d}")
        print(f"  Renombrados: {len(report.renamed)}")
        for r in report.renamed[:5]:
            print(f"    - {r[0]} -> {r[1]}")
        sys.exit(1 if args.strict else 0)


def cmd_mcp(args: argparse.Namespace) -> None:
    py_path = find_graphify_python(PROJECT_ROOT)
    graph_path = PROJECT_ROOT / "graphify-out" / "graph.json"
    if not graph_path.is_file():
        print(f"Error: No existe {graph_path}. Ejecute build primero.", file=sys.stderr)
        sys.exit(1)

    cmd = [str(py_path), "-m", "graphify.serve", str(graph_path)]
    if args.transport == "http":
        cmd.extend(["--transport", "http", "--host", args.host, "--port", str(args.port)])

    print(f"Iniciando MCP Server Graphify ({args.transport}) con {py_path}...")
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\nServidor MCP detenido.")


def cmd_benchmark(args: argparse.Namespace) -> None:
    import time
    import tracemalloc

    print("=== BENCHMARK DE RENDIMIENTO: GRAPHIFY GAMEFORGE ===")
    tracemalloc.start()
    t0 = time.perf_counter()

    engine = GraphEngine(PROJECT_ROOT)
    res_build = engine.build_initial_graph(agent_id="BENCHMARK")

    current_mem, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    build_time = time.perf_counter() - t0

    print("1. Cold Build:")
    print(f"   - Tiempo total: {build_time:.3f} s")
    print(f"   - Memoria pico: {peak_mem / (1024 * 1024):.2f} MB")
    print(f"   - Nodos: {res_build['metrics'].get('node_count', 0)}")
    print(f"   - Aristas: {res_build['metrics'].get('edge_count', 0)}")

    # Incremental update benchmark
    t1 = time.perf_counter()
    engine.update_incremental(agent_id="BENCHMARK")
    update_time = time.perf_counter() - t1
    print("2. Incremental Check/Update (sin cambios):")
    print(f"   - Tiempo: {update_time * 1000:.2f} ms")

    # Query benchmark
    t2 = time.perf_counter()
    engine.query("collision movement player", agent_id="BENCHMARK")
    query_time = time.perf_counter() - t2
    print("3. Query Latency:")
    print(f"   - Tiempo: {query_time * 1000:.2f} ms")

    # Blast radius affected benchmark
    t3 = time.perf_counter()
    engine.affected("game.world.collision", depth=2, agent_id="BENCHMARK")
    affected_time = time.perf_counter() - t3
    print("4. Affected Blast Radius:")
    print(f"   - Tiempo: {affected_time * 1000:.2f} ms")

    # Tamaño en disco
    graph_size = (engine.out_dir / "graph.json").stat().st_size / 1024
    report_size = (engine.out_dir / "GRAPH_REPORT.md").stat().st_size / 1024
    print("5. Huella en disco:")
    print(f"   - graph.json: {graph_size:.2f} KB")
    print(f"   - GRAPH_REPORT.md: {report_size:.2f} KB")


def main() -> None:
    parser = argparse.ArgumentParser(description="GameForge Graphify Operations CLI")
    parser.add_argument("--agent", default="DIRECTOR", help="Identificador del agente invocador")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("build", help="Construir grafo completo inicial")

    up_p = subparsers.add_parser("update", help="Actualización incremental")
    up_p.add_argument("files", nargs="*", help="Archivos específicos modificados")

    q_p = subparsers.add_parser("query", help="Consultar grafo")
    q_p.add_argument("question", nargs="+", help="Pregunta o consulta semántica")

    aff_p = subparsers.add_parser("affected", help="Calcular dependencias y radio de explosión")
    aff_p.add_argument("node", help="Nodo o símbolo semilla")
    aff_p.add_argument("--depth", type=int, default=2, help="Profundidad de búsqueda")

    v_p = subparsers.add_parser("verify", help="Verificar frescura del grafo contra manifiesto")
    v_p.add_argument("--strict", action="store_true", help="Retornar código de error 1 si hay drift")

    mcp_p = subparsers.add_parser("mcp", help="Lanzar servidor MCP")
    mcp_p.add_argument("--transport", choices=["stdio", "http"], default="stdio")
    mcp_p.add_argument("--host", default="127.0.0.1")
    mcp_p.add_argument("--port", type=int, default=8080)

    subparsers.add_parser("benchmark", help="Ejecutar benchmark de recursos")

    args = parser.parse_args()
    cmds = {
        "build": cmd_build,
        "update": cmd_update,
        "query": cmd_query,
        "affected": cmd_affected,
        "verify": cmd_verify,
        "mcp": cmd_mcp,
        "benchmark": cmd_benchmark,
    }
    cmds[args.command](args)


if __name__ == "__main__":
    main()
