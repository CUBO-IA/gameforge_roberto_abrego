"""Pruebas de verificación de los entregables de la Misión 004 (Grafos, Memoria y Contexto)."""

from __future__ import annotations

from pathlib import Path

REQUIRED_DELIVERABLES = [
    "KNOWLEDGE_GRAPH_ARCHITECTURE.md",
    "CODE_GRAPH_INTEGRATION.md",
    "AGENT_MEMORY_SYSTEM.md",
    "GRAPH_UPDATE_LIFECYCLE.md",
    "MANDATORY_GRAPH_USAGE.md",
    "GRAPH_VALIDATION_TESTS.md",
    "LOCAL_RESOURCE_BENCHMARK.md",
]

INVESTIGATED_REPOS = [
    "gitnexus",
    "codegraph",
    "ctx",
    "graphiti",
    "cognee",
    "aider",
    "langgraph",
]

REQUIRED_CONCEPTS = [
    "sqlite",
    "pagerank",
    "ast",
    "skeleton",
    "blast radius",
    "epistemic",
    "pre-flight",
    "incremental",
]


def test_all_mission_004_deliverables_exist() -> None:
    root = Path(__file__).resolve().parents[1]
    for filename in REQUIRED_DELIVERABLES:
        filepath = root / filename
        assert filepath.is_file(), f"Falta el entregable obligatorio: {filename}"
        assert filepath.stat().st_size > 5000, f"El entregable {filename} es demasiado corto o incompleto"


def test_investigated_repos_covered_in_architecture() -> None:
    root = Path(__file__).resolve().parents[1]
    arch_content = (root / "KNOWLEDGE_GRAPH_ARCHITECTURE.md").read_text(encoding="utf-8").lower()
    for repo in INVESTIGATED_REPOS:
        assert repo in arch_content, (
            f"El repositorio requerido '{repo}' no está analizado en KNOWLEDGE_GRAPH_ARCHITECTURE.md"
        )


def test_required_concepts_present_across_deliverables() -> None:
    root = Path(__file__).resolve().parents[1]
    combined = ""
    for filename in REQUIRED_DELIVERABLES:
        combined += (root / filename).read_text(encoding="utf-8").lower() + "\n"
    for concept in REQUIRED_CONCEPTS:
        assert concept in combined, (
            f"El concepto requerido '{concept}' no aparece en ningún entregable"
        )


def test_code_graph_defines_node_types() -> None:
    root = Path(__file__).resolve().parents[1]
    content = (root / "CODE_GRAPH_INTEGRATION.md").read_text(encoding="utf-8").lower()
    for node_type in ["file", "module", "class", "function", "contract", "test"]:
        assert node_type in content, (
            f"El tipo de nodo '{node_type}' no está definido en CODE_GRAPH_INTEGRATION.md"
        )


def test_code_graph_defines_edge_types() -> None:
    root = Path(__file__).resolve().parents[1]
    content = (root / "CODE_GRAPH_INTEGRATION.md").read_text(encoding="utf-8").lower()
    for edge_type in ["imports", "calls", "defines", "implements_contract", "tested_by"]:
        assert edge_type in content, (
            f"El tipo de arista '{edge_type}' no está definido en CODE_GRAPH_INTEGRATION.md"
        )


def test_agent_memory_defines_epistemic_states() -> None:
    root = Path(__file__).resolve().parents[1]
    content = (root / "AGENT_MEMORY_SYSTEM.md").read_text(encoding="utf-8")
    for state in ["COMPROBADA", "PROPUESTA", "PENDIENTE", "OBSOLETA", "RECHAZADA"]:
        assert state in content, (
            f"El estado epistémico '{state}' no está definido en AGENT_MEMORY_SYSTEM.md"
        )


def test_agent_memory_defines_knowledge_categories() -> None:
    root = Path(__file__).resolve().parents[1]
    content = (root / "AGENT_MEMORY_SYSTEM.md").read_text(encoding="utf-8").lower()
    for category in ["task", "adr", "instruction", "problem", "solution", "agent"]:
        assert category in content, (
            f"La categoría de conocimiento '{category}' no está definida en AGENT_MEMORY_SYSTEM.md"
        )


def test_mandatory_usage_defines_7_steps() -> None:
    root = Path(__file__).resolve().parents[1]
    content = (root / "MANDATORY_GRAPH_USAGE.md").read_text(encoding="utf-8")
    for step_num in range(1, 8):
        pattern = f"PASO {step_num}"
        assert pattern in content, (
            f"El {pattern} no está definido en MANDATORY_GRAPH_USAGE.md"
        )


def test_mandatory_usage_defines_receipt_format() -> None:
    root = Path(__file__).resolve().parents[1]
    content = (root / "MANDATORY_GRAPH_USAGE.md").read_text(encoding="utf-8").lower()
    for field in ["receipt_id", "task_id", "queried_subgraph_hash", "contracts_consulted"]:
        assert field in content, (
            f"El campo de recibo '{field}' no está definido en MANDATORY_GRAPH_USAGE.md"
        )


def test_lifecycle_defines_hooks() -> None:
    root = Path(__file__).resolve().parents[1]
    content = (root / "GRAPH_UPDATE_LIFECYCLE.md").read_text(encoding="utf-8").lower()
    for hook in ["pre-commit", "post-commit", "verify.py"]:
        assert hook in content, (
            f"El hook '{hook}' no está definido en GRAPH_UPDATE_LIFECYCLE.md"
        )


def test_validation_tests_defines_test_suite() -> None:
    root = Path(__file__).resolve().parents[1]
    content = (root / "GRAPH_VALIDATION_TESTS.md").read_text(encoding="utf-8").lower()
    for test_name in [
        "test_initial_index",
        "test_incremental_index",
        "test_import_edges",
        "test_blast_radius",
        "test_valid_epistemic_transitions",
        "test_preflight_receipt",
        "test_full_workflow_scenario",
    ]:
        assert test_name in content, (
            f"El test '{test_name}' no está definido en GRAPH_VALIDATION_TESTS.md"
        )


def test_validation_tests_defines_requisito_7_scenario() -> None:
    root = Path(__file__).resolve().parents[1]
    content = (root / "GRAPH_VALIDATION_TESTS.md").read_text(encoding="utf-8").lower()
    assert "requisito 7" in content or "prueba de uso real" in content, (
        "El escenario de prueba de uso real (Requisito 7) no está definido en GRAPH_VALIDATION_TESTS.md"
    )


def test_benchmark_defines_metrics_and_thresholds() -> None:
    root = Path(__file__).resolve().parents[1]
    content = (root / "LOCAL_RESOURCE_BENCHMARK.md").read_text(encoding="utf-8").lower()
    for metric in ["indexación completa", "indexación incremental", "blast radius", "skeleton", "pagerank"]:
        assert metric in content, (
            f"La métrica '{metric}' no está definida en LOCAL_RESOURCE_BENCHMARK.md"
        )


def test_benchmark_compares_alternatives() -> None:
    root = Path(__file__).resolve().parents[1]
    content = (root / "LOCAL_RESOURCE_BENCHMARK.md").read_text(encoding="utf-8").lower()
    for alt in ["ctx", "codegraph", "graphiti"]:
        assert alt in content, (
            f"La alternativa '{alt}' no está comparada en LOCAL_RESOURCE_BENCHMARK.md"
        )


def test_architecture_identifies_redundancies() -> None:
    root = Path(__file__).resolve().parents[1]
    content = (root / "KNOWLEDGE_GRAPH_ARCHITECTURE.md").read_text(encoding="utf-8").lower()
    assert "redundancia" in content, (
        "KNOWLEDGE_GRAPH_ARCHITECTURE.md no identifica redundancias entre tecnologías"
    )


def test_architecture_defines_ddl_schema() -> None:
    root = Path(__file__).resolve().parents[1]
    content = (root / "KNOWLEDGE_GRAPH_ARCHITECTURE.md").read_text(encoding="utf-8")
    for table in ["code_nodes", "code_edges", "file_hashes", "knowledge_nodes", "knowledge_edges", "task_receipts"]:
        assert table in content, (
            f"La tabla '{table}' no está definida en el esquema DDL de KNOWLEDGE_GRAPH_ARCHITECTURE.md"
        )


def test_no_paid_services_required() -> None:
    root = Path(__file__).resolve().parents[1]
    combined = ""
    for filename in REQUIRED_DELIVERABLES:
        combined += (root / filename).read_text(encoding="utf-8").lower() + "\n"
    assert "sin servicios de pago" in combined or "cero servicios" in combined or "cero dependencias" in combined, (
        "Los entregables no declaran explícitamente la ausencia de servicios de pago"
    )
