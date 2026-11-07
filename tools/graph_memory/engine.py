"""Motor principal de orquestación de Graphify para GameForge.

Coordina la extracción AST, extracción Markdown, extracción de decisiones,
fusión incremental, generación de grafos, consultas y auditoría.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from tools.graph_memory.audit import AuditLogger
from tools.graph_memory.decision_extractor import extract_decision_memory
from tools.graph_memory.freshness import ManifestTracker
from tools.graph_memory.isolated_env import run_graphify_script


class GraphEngine:
    def __init__(self, root: Path | None = None, out_dir: Path | None = None) -> None:
        self.root = (root or Path.cwd()).resolve()
        self.out_dir = (out_dir or (self.root / "graphify-out")).resolve()
        self.audit = AuditLogger(self.out_dir / "audit.log")
        self.manifest = ManifestTracker(self.root, self.out_dir / ".manifest.json")

    def build_initial_graph(self, agent_id: str = "DIRECTOR") -> dict[str, Any]:
        """Genera el grafo inicial del proyecto GameForge de forma determinista y local."""
        t0 = time.perf_counter()
        self.out_dir.mkdir(parents=True, exist_ok=True)

        # 1. Extraer memoria de decisiones
        decision_extract = extract_decision_memory(self.root)

        # 2. Script para ejecutar en el entorno aislado de Graphify
        root_posix = self.root.as_posix()
        out_posix = self.out_dir.as_posix()
        decisions_temp_posix = (self.out_dir / ".decisions_temp.json").as_posix()

        worker_script = f"""# -*- coding: utf-8 -*-
import sys, json, time
from pathlib import Path
from graphify.extract import collect_files, extract
from graphify.extractors.markdown import extract_markdown
from graphify.build import build_from_json
from graphify.cluster import cluster, score_all
from graphify.analyze import god_nodes, surprising_connections, suggest_questions
from graphify.report import generate
from graphify.export import to_json

root = Path(r"{root_posix}")
out = Path(r"{out_posix}")
out.mkdir(parents=True, exist_ok=True)

# Colectar archivos de codigo
code_files = []
for p in root.rglob("*.py"):
    if not p.is_file(): continue
    parts = p.parts
    if any(x in parts for x in [".venv", ".git", "__pycache__", "archive", "build", "dist"]):
        continue
    code_files.append(p)

# Extraer AST
ast_res = extract(code_files, cache_root=root, parallel=False)
ast_nodes = ast_res.get("nodes", [])
ast_edges = ast_res.get("edges", [])

# Extraer documentacion y directivas Markdown
md_nodes = []
md_edges = []
for md_path in root.rglob("*.md"):
    if not md_path.is_file(): continue
    parts = md_path.parts
    if any(x in parts for x in [".venv", ".git", "graphify-out", "archive"]):
        continue
    try:
        res = extract_markdown(md_path)
        md_nodes.extend(res.get("nodes", []))
        md_edges.extend(res.get("edges", []))
    except Exception:
        pass

# Cargar nodos de decisiones
decisions = json.loads(Path(r"{decisions_temp_posix}").read_text(encoding="utf-8"))

# Fusion
seen_nodes = set()
all_nodes = []
for n in ast_nodes + md_nodes + decisions.get("nodes", []):
    nid = n.get("id")
    if nid and nid not in seen_nodes:
        seen_nodes.add(nid)
        all_nodes.append(n)

all_edges = ast_edges + md_edges + decisions.get("edges", [])

# Construir grafo NetworkX
extraction = {{"nodes": all_nodes, "edges": all_edges}}
G = build_from_json(extraction, root=str(root), directed=True)

# Clustering y metricas
communities = cluster(G)
cohesion = score_all(G, communities)
gods = god_nodes(G)
surprises = surprising_connections(G, communities)
labels = {{cid: f"Community {{cid}}" for cid in communities}}
questions = suggest_questions(G, communities, labels)

# Exportar graph.json
wrote = to_json(G, communities, str(out / "graph.json"))

# Exportar reporte
detection = {{"total_files": len(code_files) + len(md_nodes), "total_words": 150000}}
tokens = {{"input": 0, "output": 0}}
report = generate(G, communities, cohesion, labels, gods, surprises, detection, tokens, str(root), suggested_questions=questions)
(out / "GRAPH_REPORT.md").write_text(report, encoding="utf-8")

# Exportar resultado de ejecucion a stdout
result = {{
    "node_count": G.number_of_nodes(),
    "edge_count": G.number_of_edges(),
    "community_count": len(communities),
    "god_nodes": gods[:5]
}}
print(json.dumps(result))
"""

        # Escribir temporal de decisiones
        decisions_temp = self.out_dir / ".decisions_temp.json"
        decisions_temp.write_text(json.dumps(decision_extract, indent=2), encoding="utf-8")

        try:
            proc = run_graphify_script(worker_script, root=self.root, timeout=60.0)
            lines = proc.stdout.strip().splitlines()
            result_json = {}
            for line in reversed(lines):
                if line.startswith("{") and line.endswith("}"):
                    try:
                        result_json = json.loads(line)
                        break
                    except json.JSONDecodeError:
                        pass
        finally:
            decisions_temp.unlink(missing_ok=True)

        latency = (time.perf_counter() - t0) * 1000
        self.manifest.save_manifest()

        self.audit.log_event(
            operation="BUILD",
            agent_id=agent_id,
            target="project_root",
            result=result_json,
            latency_ms=latency,
            status="SUCCESS",
        )
        return {
            "status": "SUCCESS",
            "latency_ms": latency,
            "metrics": result_json,
        }

    def update_incremental(
        self,
        changed_paths: list[str] | None = None,
        deleted_paths: list[str] | None = None,
        agent_id: str = "DIRECTOR",
    ) -> dict[str, Any]:
        """Ejecuta una actualización incremental detectando archivos modificados y eliminados."""
        t0 = time.perf_counter()

        drift = self.manifest.check_drift()
        to_update = changed_paths or (drift.modified + drift.added)
        to_delete = deleted_paths or drift.deleted

        if not to_update and not to_delete and not drift.renamed:
            latency = (time.perf_counter() - t0) * 1000
            self.audit.log_event(
                operation="UPDATE",
                agent_id=agent_id,
                target="none",
                result={"updated_files": 0, "message": "No drift detected"},
                latency_ms=latency,
                status="UP_TO_DATE",
            )
            return {"status": "UP_TO_DATE", "latency_ms": latency, "updated": 0}

        # Para archivos renombrados, añadir el viejo a delete y el nuevo a update
        for old_p, new_p in drift.renamed:
            if old_p not in to_delete:
                to_delete.append(old_p)
            if new_p not in to_update:
                to_update.append(new_p)

        root_posix = self.root.as_posix()
        out_posix = self.out_dir.as_posix()

        worker_script = f"""# -*- coding: utf-8 -*-
import sys, json
from pathlib import Path
from graphify.extract import extract
from graphify.extractors.markdown import extract_markdown
from graphify.build import build_merge
from graphify.cluster import cluster, score_all
from graphify.analyze import god_nodes, surprising_connections, suggest_questions
from graphify.report import generate
from graphify.export import to_json

root = Path(r"{root_posix}")
out = Path(r"{out_posix}")
graph_file = out / "graph.json"

to_update = {json.dumps(to_update)}
to_delete = {json.dumps(to_delete)}

code_updates = [root / p for p in to_update if p.endswith(".py") and (root / p).is_file()]
md_updates = [root / p for p in to_update if p.endswith(".md") and (root / p).is_file()]

new_nodes = []
new_edges = []

if code_updates:
    ast_res = extract(code_updates, cache_root=root, parallel=False)
    new_nodes.extend(ast_res.get("nodes", []))
    new_edges.extend(ast_res.get("edges", []))

for md_path in md_updates:
    try:
        md_res = extract_markdown(md_path)
        new_nodes.extend(md_res.get("nodes", []))
        new_edges.extend(md_res.get("edges", []))
    except Exception:
        pass

new_extraction = {{"nodes": new_nodes, "edges": new_edges}}

G = build_merge(
    [new_extraction],
    graph_path=str(graph_file),
    prune_sources=to_delete,
    root=str(root),
    directed=True
)

communities = cluster(G)
wrote = to_json(G, communities, str(graph_file), force=True)

result = {{
    "node_count": G.number_of_nodes(),
    "edge_count": G.number_of_edges(),
    "updated_files": len(to_update),
    "deleted_files": len(to_delete)
}}
print(json.dumps(result))
"""
        proc = run_graphify_script(worker_script, root=self.root, timeout=45.0)
        lines = proc.stdout.strip().splitlines()
        result_json = {}
        for line in reversed(lines):
            if line.startswith("{") and line.endswith("}"):
                try:
                    result_json = json.loads(line)
                    break
                except json.JSONDecodeError:
                    pass

        self.manifest.save_manifest()
        latency = (time.perf_counter() - t0) * 1000

        self.audit.log_event(
            operation="UPDATE",
            agent_id=agent_id,
            target=f"{len(to_update)} updated, {len(to_delete)} deleted",
            result=result_json,
            latency_ms=latency,
            status="SUCCESS",
        )

        return {
            "status": "SUCCESS",
            "latency_ms": latency,
            "metrics": result_json,
        }

    def query(self, question: str, agent_id: str = "DIRECTOR") -> dict[str, Any]:
        """Consulta el grafo mediante búsqueda semántica/estructural."""
        t0 = time.perf_counter()
        graph_file = self.out_dir / "graph.json"
        if not graph_file.is_file():
            raise FileNotFoundError("graph.json no existe. Ejecute build_initial_graph() primero.")

        graph_file_posix = graph_file.as_posix()
        worker_script = f"""# -*- coding: utf-8 -*-
import sys, json
from pathlib import Path
from graphify.affected import load_graph

graph_file = Path(r"{graph_file_posix}")
G = load_graph(graph_file)

question = {json.dumps(question)}.lower()
matching_nodes = []
for n, data in G.nodes(data=True):
    label = str(data.get("label", "")).lower()
    nid = str(n).lower()
    if any(word in label or word in nid for word in question.split() if len(word) > 3):
        matching_nodes.append({{"id": n, "label": data.get("label", n), "type": data.get("file_type", "")}})

result = {{
    "total_matched": len(matching_nodes),
    "sample_nodes": matching_nodes[:10]
}}
print(json.dumps(result))
"""
        proc = run_graphify_script(worker_script, root=self.root, timeout=30.0)
        lines = proc.stdout.strip().splitlines()
        result_json = {}
        for line in reversed(lines):
            if line.startswith("{") and line.endswith("}"):
                try:
                    result_json = json.loads(line)
                    break
                except json.JSONDecodeError:
                    pass

        latency = (time.perf_counter() - t0) * 1000
        self.audit.log_event(
            operation="QUERY",
            agent_id=agent_id,
            target=question,
            result=result_json,
            latency_ms=latency,
            status="SUCCESS",
        )
        return {
            "status": "SUCCESS",
            "latency_ms": latency,
            "result": result_json,
        }

    def affected(self, node_id: str, depth: int = 2, agent_id: str = "DIRECTOR") -> dict[str, Any]:
        """Calcula el radio de explosión (blast radius) de dependientes sobre un nodo dado."""
        t0 = time.perf_counter()
        graph_file = self.out_dir / "graph.json"
        if not graph_file.is_file():
            raise FileNotFoundError("graph.json no existe.")

        graph_file_posix = graph_file.as_posix()
        worker_script = f"""# -*- coding: utf-8 -*-
import sys, json
from pathlib import Path
from graphify.affected import load_graph, affected_nodes

graph_file = Path(r"{graph_file_posix}")
G = load_graph(graph_file)
seed = {json.dumps(node_id)}

# Resolver nodo exacto o buscar candidatos
target_node = seed
if seed not in G:
    candidates = [n for n in G.nodes() if seed in str(n)]
    if candidates:
        target_node = candidates[0]

hits = []
if target_node in G:
    raw_hits = affected_nodes(G, target_node, depth={depth})
    for h in raw_hits:
        hits.append({{
            "node_id": h.node_id,
            "depth": h.depth,
            "via_relation": h.via_relation,
            "via_file": h.via_file
        }})

result = {{
    "seed": target_node,
    "hit_count": len(hits),
    "affected": hits
}}
print(json.dumps(result))
"""
        proc = run_graphify_script(worker_script, root=self.root, timeout=30.0)
        lines = proc.stdout.strip().splitlines()
        result_json = {}
        for line in reversed(lines):
            if line.startswith("{") and line.endswith("}"):
                try:
                    result_json = json.loads(line)
                    break
                except json.JSONDecodeError:
                    pass

        latency = (time.perf_counter() - t0) * 1000
        self.audit.log_event(
            operation="AFFECTED",
            agent_id=agent_id,
            target=node_id,
            result=result_json,
            latency_ms=latency,
            status="SUCCESS",
        )
        return {
            "status": "SUCCESS",
            "latency_ms": latency,
            "result": result_json,
        }
