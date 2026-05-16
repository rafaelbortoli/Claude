import pytest
from pathlib import Path

from cli.commands.setup_claude import _prepare, _find_candidate_paths


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def siblings_dir(tmp_path):
    """Cria 3 pastas irmãs, duas com .claude/CLAUDE.md."""
    base = tmp_path / "project-a"
    base.mkdir()

    proj_b = tmp_path / "project-b"
    proj_b.mkdir()
    (proj_b / ".claude").mkdir()
    (proj_b / ".claude" / "CLAUDE.md").write_text("---\nname: project-b\n---\n")

    proj_c = tmp_path / "project-c"
    proj_c.mkdir()
    (proj_c / ".claude").mkdir()
    (proj_c / ".claude" / "CLAUDE.md").write_text("---\nname: project-c\n---\n")

    proj_d = tmp_path / "project-d"  # sem CLAUDE.md
    proj_d.mkdir()

    return base


# ---------------------------------------------------------------------------
# _find_candidate_paths
# ---------------------------------------------------------------------------

class TestFindCandidatePaths:
    def test_always_includes_base(self, tmp_path):
        base = tmp_path / "my-project"
        base.mkdir()
        result = _find_candidate_paths(base)
        assert str(base) in result

    def test_includes_siblings_with_claude_md(self, siblings_dir):
        result = _find_candidate_paths(siblings_dir)
        assert any("project-b" in p for p in result)
        assert any("project-c" in p for p in result)

    def test_excludes_sibling_without_claude_md(self, siblings_dir):
        result = _find_candidate_paths(siblings_dir)
        assert not any("project-d" in p for p in result)

    def test_max_3_candidates(self, tmp_path):
        base = tmp_path / "base"
        base.mkdir()
        # cria 5 irmãs com CLAUDE.md
        for i in range(5):
            d = tmp_path / f"proj-{i}"
            d.mkdir()
            (d / ".claude").mkdir()
            (d / ".claude" / "CLAUDE.md").write_text("---\nname: x\n---\n")
        result = _find_candidate_paths(base)
        assert len(result) <= 3

    def test_base_is_first(self, siblings_dir):
        result = _find_candidate_paths(siblings_dir)
        assert result[0] == str(siblings_dir)


# ---------------------------------------------------------------------------
# _prepare
# ---------------------------------------------------------------------------

class TestPrepare:
    def test_returns_context_keys(self, tmp_path):
        base = tmp_path / "my-project"
        base.mkdir()
        result = _prepare(base)
        assert "context" in result
        assert "current_path" in result["context"]

    def test_current_path_matches_base(self, tmp_path):
        base = tmp_path / "my-project"
        base.mkdir()
        result = _prepare(base)
        assert result["context"]["current_path"] == str(base)

    def test_suggestions_project_paths_present(self, tmp_path):
        base = tmp_path / "my-project"
        base.mkdir()
        result = _prepare(base)
        assert "suggestions" in result
        assert "project_paths" in result["suggestions"]

    def test_project_paths_includes_base(self, tmp_path):
        base = tmp_path / "my-project"
        base.mkdir()
        result = _prepare(base)
        assert str(base) in result["suggestions"]["project_paths"]

    def test_project_paths_includes_siblings_with_claude_md(self, siblings_dir):
        result = _prepare(siblings_dir)
        paths = result["suggestions"]["project_paths"]
        assert any("project-b" in p for p in paths)
        assert any("project-c" in p for p in paths)
