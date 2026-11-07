"""Pruebas de verificación de la integración de Graphify como memoria operativa (Misión 005)."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from tools.graph_memory.audit import AuditLogger
from tools.graph_memory.decision_extractor import extract_decision_memory
from tools.graph_memory.engine import GraphEngine
from tools.graph_memory.freshness import ManifestTracker
from tools.graph_memory.isolated_env import find_graphify_python, run_graphify_script

REQUIRED_DELIVERABLES = [
    "GRAPHIFY_INTEGRATION.md",
    "GRAPH_UPDATE_AUTOMATION.md",
    "GRAPH_MCP_CONFIGURATION.md",
    "GRAPH_USAGE_DIRECTIVE.md",
    "GRAPH_ACCEPTANCE_TESTS.md",
    "RESOURCE_BENCHMARK.md",
]


def test_isolated_environment_detected_and_functional() -> None:
    """Requisito 1: Instalar y configurar Graphify en un entorno aislado."""
    py_path = find_graphify_python()
    assert py_path.is_file(), f"No se encontró el ejecutable: {py_path}"

    # Verificar que el entorno aislado posee graphify instalado
    proc = run_graphify_script("import graphify; print(graphify.__file__)")
    assert proc.returncode == 0
    assert "graphify" in proc.stdout.lower()


def test_decision_memory_extraction() -> None:
    """Memoria de decisiones: incorporar ADRs, tareas, contratos, problemas y soluciones."""
    root = Path(__file__).resolve().parents[1]
    memory = extract_decision_memory(root)
    nodes = memory["nodes"]
    edges = memory["edges"]

    assert len(nodes) >= 30, f"Demasiado pocos nodos de decisiones: {len(nodes)}"

    kinds = {n.get("node_kind") for n in nodes}
    assert "adr" in kinds, "Falta node_kind 'adr'"
    assert "task" in kinds, "Falta node_kind 'task'"
    assert "contract" in kinds, "Falta node_kind 'contract'"
    assert "problem" in kinds, "Falta node_kind 'problem'"
    assert "solution" in kinds, "Falta node_kind 'solution'"

    # Verificar separación entre código y relaciones de decisión
    relations = {e.get("relation") for e in edges}
    assert "references" in relations or "fulfills" in relations or "solves" in relations


def test_initial_graph_generation_and_schema() -> None:
    """Requisitos 2 y 3: Generar grafo inicial incorporando código, docs y contratos."""
    root = Path(__file__).resolve().parents[1]
    engine = GraphEngine(root)
    graph_json = engine.out_dir / "graph.json"
    assert graph_json.is_file(), "No se encontró graphify-out/graph.json"

    data = json.loads(graph_json.read_text(encoding="utf-8"))
    nodes = data.get("nodes", [])
    edges = data.get("links", []) or data.get("edges", [])

    assert len(nodes) > 1000, f"Grafo incompleto: {len(nodes)} nodos"
    assert len(edges) > 2000, f"Grafo incompleto: {len(edges)} aristas"

    # Verificar reporte generado
    report_file = engine.out_dir / "GRAPH_REPORT.md"
    assert report_file.is_file(), "No se encontró GRAPH_REPORT.md"
    assert report_file.stat().st_size > 1000


def test_audit_logging_of_queries_and_updates() -> None:
    """Requisito 10: Registrar las consultas y actualizaciones efectuadas."""
    root = Path(__file__).resolve().parents[1]
    audit_file = root / "graphify-out" / "audit.log"
    assert audit_file.is_file(), "No existe graphify-out/audit.log"

    logger = AuditLogger(audit_file)
    event = logger.log_event(
        operation="TEST_VERIFY",
        agent_id="QA_TESTER",
        target="tests/test_graphify_integration.py",
        result={"status": "ok"},
        latency_ms=12.5,
    )
    assert event["operation"] == "TEST_VERIFY"

    events = logger.read_events(limit=10)
    assert any(e["operation"] == "TEST_VERIFY" for e in events)


def test_drift_detection_and_freshness() -> None:
    """Requisitos 7 y 8: Detectar modificados, eliminados y renombrados sin obsolescencia."""
    with tempfile.TemporaryDirectory() as td:
        sandbox = Path(td)
        file_a = sandbox / "module_a.py"
        file_a.write_text("def foo(): return 1\n", encoding="utf-8")

        tracker = ManifestTracker(sandbox)
        tracker.save_manifest()

        report_init = tracker.check_drift()
        assert report_init.is_fresh is True

        # Modificación
        file_a.write_text("def foo(): return 2\n", encoding="utf-8")
        report_mod = tracker.check_drift()
        assert report_mod.is_fresh is False
        assert "module_a.py" in report_mod.modified

        # Renombrado (mismo contenido en nueva ruta)
        tracker.save_manifest()
        file_b = sandbox / "module_b.py"
        file_a.rename(file_b)

        report_ren = tracker.check_drift()
        assert report_ren.is_fresh is False
        assert len(report_ren.renamed) == 1
        assert report_ren.renamed[0] == ("module_a.py", "module_b.py")

        # Eliminación
        tracker.save_manifest()
        file_b.unlink()
        report_del = tracker.check_drift()
        assert report_del.is_fresh is False
        assert "module_b.py" in report_del.deleted


def test_affected_dependencies_blast_radius() -> None:
    """Requisito de uso real: Consultar dependencias antes de cambiar interfaces."""
    root = Path(__file__).resolve().parents[1]
    engine = GraphEngine(root)
    res = engine.affected("game_world_collision", depth=2, agent_id="AGENT_TEST")

    assert res["status"] == "SUCCESS"
    affected_hits = res["result"]["affected"]
    assert len(affected_hits) > 0, "No se encontraron nodos afectados para collision"

    # Verificar que player o enemies aparecen entre los afectados
    affected_ids = [h["node_id"] for h in affected_hits]
    assert any("player" in nid or "enemies" in nid for nid in affected_ids)


def test_acceptance_scenario_agent_a_agent_b_coordination() -> None:
    """Prueba de aceptación completa:

    1. Agente A modifica un módulo.
    2. Graphify actualiza el índice incrementalmente.
    3. Agente B recibe una tarea relacionada.
    4. Agente B consulta Graphify y encuentra los cambios del Agente A.
    5. Agente B identifica dependencias y trabaja sin duplicar componentes.
    6. El sistema registra evidencias de todo el proceso en audit.log.
    """
    with tempfile.TemporaryDirectory() as td:
        sandbox = Path(td)
        out_dir = sandbox / "graphify-out"

        # Crear módulo inicial
        game_dir = sandbox / "game" / "skills"
        game_dir.mkdir(parents=True, exist_ok=True)
        dash_module = game_dir / "dash.py"
        dash_module.write_text(
            "class DashSystem:\n"
            "    def perform_dash(self, speed: float) -> bool:\n"
            "        return speed > 0\n",
            encoding="utf-8",
        )

        engine = GraphEngine(sandbox, out_dir=out_dir)
        engine.build_initial_graph(agent_id="DIRECTOR")

        # Paso 1: Agente A modifica el módulo agregando 'cooldown_dash'
        dash_module.write_text(
            "class DashSystem:\n"
            "    def perform_dash(self, speed: float) -> bool:\n"
            "        return speed > 0\n\n"
            "    def cooldown_dash(self) -> float:\n"
            "        return 1.5\n",
            encoding="utf-8",
        )

        # Paso 2: Graphify actualiza el índice incrementalmente
        up_res = engine.update_incremental(agent_id="AGENTE_A")
        assert up_res["status"] == "SUCCESS"
        assert up_res["metrics"]["updated_files"] >= 1

        # Paso 3: Agente B recibe tarea ("Verificar dash cooldown")
        # Paso 4: Agente B consulta Graphify
        q_res = engine.query("cooldown dash", agent_id="AGENTE_B")
        assert q_res["status"] == "SUCCESS"
        matching_labels = [n["label"] for n in q_res["result"]["sample_nodes"]]
        assert any("cooldown_dash" in str(lbl) or "DashSystem" in str(lbl) for lbl in matching_labels)

        # Paso 5: Agente B analiza dependencias del DashSystem
        aff_res = engine.affected("DashSystem", depth=1, agent_id="AGENTE_B")
        assert aff_res["status"] == "SUCCESS"

        # Paso 6: Verificar evidencias en audit.log
        audit_events = engine.audit.read_events(limit=10)
        agent_names = {e["agent_id"] for e in audit_events}
        assert "AGENTE_A" in agent_names, "Falta registro de Agente A en auditoría"
        assert "AGENTE_B" in agent_names, "Falta registro de Agente B en auditoría"


def test_all_mission_005_deliverables_exist_and_complete() -> None:
    """Verifica la existencia y contenido sustancial de los 6 entregables de la Misión 005."""
    root = Path(__file__).resolve().parents[1]
    for filename in REQUIRED_DELIVERABLES:
        filepath = root / filename
        assert filepath.is_file(), f"Falta el entregable obligatorio: {filename}"
        assert filepath.stat().st_size > 4000, f"El entregable {filename} está incompleto"
