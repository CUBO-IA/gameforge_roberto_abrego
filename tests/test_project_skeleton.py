from pathlib import Path

from game import __version__


def test_project_has_agent_directives() -> None:
    root = Path(__file__).resolve().parents[1]
    assert (root / "AGENTS.md").is_file()
    assert (root / "directives" / "01_GLOBAL.md").is_file()
    assert (root / "architecture" / "CONTRACTS.md").is_file()


def test_package_version_is_declared() -> None:
    assert __version__
    root = Path(__file__).resolve().parents[1]
    assert f'version = "{__version__}"' in (root / "pyproject.toml").read_text(encoding="utf-8")
