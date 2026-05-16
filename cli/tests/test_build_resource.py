import json
import pytest
from pathlib import Path

from cli.commands.build_resource import _prepare, _infer_naming_pattern, _extract_tag_suggestions


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def project_dir(tmp_path):
    """Estrutura mínima de projeto com .claude/CLAUDE.md."""
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir()
    (claude_dir / "CLAUDE.md").write_text(
        "---\nname: meu-projeto\ntype: doc\n---\n\n# Projeto\n"
    )
    return claude_dir


@pytest.fixture
def project_with_skills(project_dir):
    """Projeto com 3 skills instaladas."""
    skills_dir = project_dir / "skills"
    skills_dir.mkdir()
    for name, tags in [
        ("code-review", "[review, quality]"),
        ("code-format", "[review, style]"),
        ("ux-audit",    "[ux, review]"),
    ]:
        (skills_dir / f"{name}.md").write_text(
            f"---\nname: {name}\ntags: {tags}\n---\n\n# Body\n"
        )
    return project_dir


# ---------------------------------------------------------------------------
# _infer_naming_pattern
# ---------------------------------------------------------------------------

class TestInferNamingPattern:
    def test_empty_list_returns_placeholder(self):
        assert _infer_naming_pattern([]) == "<nome>"

    def test_single_part_names(self):
        assert _infer_naming_pattern(["review", "format"]) == "<parte-1>"

    def test_two_part_names(self):
        result = _infer_naming_pattern(["code-review", "code-format"])
        assert result == "<parte-1>-<parte-2>"

    def test_three_part_names(self):
        result = _infer_naming_pattern(["ux-audit-light", "ux-audit-deep"])
        assert result == "<parte-1>-<parte-2>-<parte-3>"

    def test_most_common_wins(self):
        # 3 x dois-partes, 1 x três-partes → padrão de dois
        names = ["code-review", "code-format", "ux-audit", "very-long-name"]
        result = _infer_naming_pattern(names)
        assert result == "<parte-1>-<parte-2>"


# ---------------------------------------------------------------------------
# _extract_tag_suggestions
# ---------------------------------------------------------------------------

class TestExtractTagSuggestions:
    def test_empty_project_returns_empty(self, project_dir):
        result = _extract_tag_suggestions(project_dir)
        assert result == []

    def test_returns_groups_of_3(self, project_with_skills):
        result = _extract_tag_suggestions(project_with_skills)
        for group in result:
            assert len(group) <= 3

    def test_most_frequent_tag_in_first_group(self, project_with_skills):
        result = _extract_tag_suggestions(project_with_skills)
        assert len(result) > 0
        # "review" aparece 3x — deve ser o primeiro
        assert "review" in result[0]

    def test_max_3_groups(self, project_with_skills):
        result = _extract_tag_suggestions(project_with_skills)
        assert len(result) <= 3


# ---------------------------------------------------------------------------
# _prepare
# ---------------------------------------------------------------------------

class TestPrepare:
    def test_raises_when_no_claude_md(self, tmp_path):
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        with pytest.raises(FileNotFoundError):
            _prepare(claude_dir, "skill")

    def test_returns_context_keys(self, project_dir):
        result = _prepare(project_dir, "skill")
        assert "context" in result
        assert "current_path" in result["context"]
        assert "project_name" in result["context"]

    def test_project_name_from_frontmatter(self, project_dir):
        result = _prepare(project_dir, "skill")
        assert result["context"]["project_name"] == "meu-projeto"

    def test_current_path_is_parent_of_claude_dir(self, project_dir):
        result = _prepare(project_dir, "skill")
        assert result["context"]["current_path"] == str(project_dir.parent)

    def test_meta_keys_present(self, project_dir):
        result = _prepare(project_dir, "skill")
        assert "meta" in result
        assert "naming_pattern" in result["meta"]
        assert "existing_names" in result["meta"]
        assert "has_existing_resources" in result["meta"]

    def test_meta_no_existing_resources(self, project_dir):
        result = _prepare(project_dir, "skill")
        assert result["meta"]["has_existing_resources"] is False
        assert result["meta"]["existing_names"] == []

    def test_meta_with_existing_resources(self, project_with_skills):
        result = _prepare(project_with_skills, "skill")
        assert result["meta"]["has_existing_resources"] is True
        assert len(result["meta"]["existing_names"]) == 3

    def test_suggestions_tags_present(self, project_dir):
        result = _prepare(project_dir, "skill")
        assert "suggestions" in result
        assert "tags" in result["suggestions"]
