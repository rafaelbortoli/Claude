import json
import pytest
from pathlib import Path
from unittest.mock import patch

from cli.commands.install_resource import _prepare


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def hub_dir(tmp_path):
    """Hub mínimo com skills e agents."""
    hub = tmp_path / "hub"
    hub_res = hub / "hub"

    skills_dir = hub_res / "skills"
    for name, desc, version in [
        ("code-review", "Revisa código", "1.2.0"),
        ("ux-audit",    "Audita UX",     "1.0.0"),
    ]:
        d = skills_dir / name
        d.mkdir(parents=True)
        (d / "skill.md").write_text(
            f"---\nname: {name}\nversion: {version}\ndescription: {desc}\n---\n\n# Body\n"
        )

    agents_dir = hub_res / "agents"
    (agents_dir / "planner").mkdir(parents=True)
    (agents_dir / "planner" / "agent.md").write_text(
        "---\nname: planner\nversion: 1.0.0\ndescription: Planeja tarefas\n---\n\n# Body\n"
    )

    return hub


@pytest.fixture
def project_dir(tmp_path):
    """Projeto com .claude/CLAUDE.md e uma skill já instalada."""
    claude_dir = tmp_path / "my-project" / ".claude"
    claude_dir.mkdir(parents=True)
    (claude_dir / "CLAUDE.md").write_text(
        "---\nname: meu-projeto\ntype: doc\n---\n\n# Projeto\n"
    )
    skills_dir = claude_dir / "skills"
    skills_dir.mkdir()
    (skills_dir / "code-review.md").write_text(
        "---\nname: code-review\nversion: 1.2.0\ndescription: Revisa código\n---\n\n# Body\n"
    )
    return claude_dir


# ---------------------------------------------------------------------------
# _prepare
# ---------------------------------------------------------------------------

class TestPrepare:
    def test_raises_when_no_claude_md(self, hub_dir, tmp_path):
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        with pytest.raises(FileNotFoundError):
            _prepare(hub_dir, claude_dir, "skill")

    def test_returns_context_keys(self, hub_dir, project_dir):
        result = _prepare(hub_dir, project_dir, "skill")
        assert "context" in result
        assert "current_path" in result["context"]
        assert "project_name" in result["context"]

    def test_project_name_from_frontmatter(self, hub_dir, project_dir):
        result = _prepare(hub_dir, project_dir, "skill")
        assert result["context"]["project_name"] == "meu-projeto"

    def test_available_lists_hub_resources(self, hub_dir, project_dir):
        result = _prepare(hub_dir, project_dir, "skill")
        names = [r["name"] for r in result["available"]]
        assert "code-review" in names
        assert "ux-audit" in names

    def test_installed_lists_project_resources(self, hub_dir, project_dir):
        result = _prepare(hub_dir, project_dir, "skill")
        names = [r["name"] for r in result["installed"]]
        assert "code-review" in names

    def test_installed_names_in_meta(self, hub_dir, project_dir):
        result = _prepare(hub_dir, project_dir, "skill")
        assert "installed_names" in result["meta"]
        assert "code-review" in result["meta"]["installed_names"]

    def test_has_available_true(self, hub_dir, project_dir):
        result = _prepare(hub_dir, project_dir, "skill")
        assert result["meta"]["has_available"] is True

    def test_has_installed_true(self, hub_dir, project_dir):
        result = _prepare(hub_dir, project_dir, "skill")
        assert result["meta"]["has_installed"] is True

    def test_has_installed_false_when_empty(self, hub_dir, project_dir):
        result = _prepare(hub_dir, project_dir, "agent")
        assert result["meta"]["has_installed"] is False

    def test_current_path_is_parent_of_claude_dir(self, hub_dir, project_dir):
        result = _prepare(hub_dir, project_dir, "skill")
        assert result["context"]["current_path"] == str(project_dir.parent)
