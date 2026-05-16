import pytest
from pathlib import Path
from cli.utils import frontmatter


SAMPLE = """\
---
name: meu-recurso
type: skill
version: 1.0.0
description: Descrição do recurso
project: ""
source: ""

# system
scope: project
auto_load: false
---

# Conteúdo do recurso

Texto do body.
"""


@pytest.fixture
def tmp_file(tmp_path):
    f = tmp_path / "resource.md"
    f.write_text(SAMPLE)
    return f


class TestRead:
    def test_reads_simple_field(self, tmp_file):
        result = frontmatter.read(tmp_file)
        assert result['name'] == 'meu-recurso'
        assert result['type'] == 'skill'
        assert result['version'] == '1.0.0'

    def test_parses_inline_list(self, tmp_path):
        f = tmp_path / "tagged.md"
        f.write_text("---\nname: x\ntags: [review, ux, interface]\n---\n\nBody.\n")
        result = frontmatter.read(f)
        assert result['tags'] == ['review', 'ux', 'interface']

    def test_parses_empty_list(self, tmp_path):
        f = tmp_path / "empty.md"
        f.write_text("---\nname: x\ntags: []\n---\n\nBody.\n")
        result = frontmatter.read(f)
        assert result['tags'] == []

    def test_parses_single_item_list(self, tmp_path):
        f = tmp_path / "single.md"
        f.write_text("---\nname: x\ntags: [review]\n---\n\nBody.\n")
        result = frontmatter.read(f)
        assert result['tags'] == ['review']

    def test_string_field_unchanged(self, tmp_path):
        f = tmp_path / "str.md"
        f.write_text("---\nname: x\ndescription: Faz algo útil\n---\n\nBody.\n")
        result = frontmatter.read(f)
        assert result['description'] == 'Faz algo útil'

    def test_ignores_comment_lines(self, tmp_file):
        result = frontmatter.read(tmp_file)
        assert '# system' not in result

    def test_returns_empty_dict_when_no_frontmatter(self, tmp_path):
        f = tmp_path / "no_fm.md"
        f.write_text("# Só conteúdo\n\nSem frontmatter.\n")
        assert frontmatter.read(f) == {}

    def test_preserves_body_unchanged(self, tmp_file):
        frontmatter.read(tmp_file)
        assert "# Conteúdo do recurso" in tmp_file.read_text()


class TestWrite:
    def test_updates_existing_field(self, tmp_file):
        frontmatter.write(tmp_file, {'version': '2.0.0'})
        result = frontmatter.read(tmp_file)
        assert result['version'] == '2.0.0'

    def test_updates_multiple_fields(self, tmp_file):
        frontmatter.write(tmp_file, {'version': '2.0.0', 'name': 'novo-nome'})
        result = frontmatter.read(tmp_file)
        assert result['version'] == '2.0.0'
        assert result['name'] == 'novo-nome'

    def test_appends_new_field(self, tmp_file):
        frontmatter.write(tmp_file, {'author': 'Bortoli'})
        result = frontmatter.read(tmp_file)
        assert result['author'] == 'Bortoli'

    def test_preserves_body(self, tmp_file):
        frontmatter.write(tmp_file, {'version': '2.0.0'})
        assert "# Conteúdo do recurso" in tmp_file.read_text()
        assert "Texto do body." in tmp_file.read_text()

    def test_no_op_when_no_frontmatter(self, tmp_path):
        f = tmp_path / "no_fm.md"
        original = "# Só conteúdo\n"
        f.write_text(original)
        frontmatter.write(f, {'version': '1.0.0'})
        assert f.read_text() == original


class TestStrip:
    def test_removes_specified_fields(self, tmp_file):
        frontmatter.strip(tmp_file, ['project', 'source'])
        result = frontmatter.read(tmp_file)
        assert 'project' not in result
        assert 'source' not in result

    def test_keeps_other_fields(self, tmp_file):
        frontmatter.strip(tmp_file, ['project'])
        result = frontmatter.read(tmp_file)
        assert result['name'] == 'meu-recurso'
        assert result['version'] == '1.0.0'

    def test_no_triple_blank_lines(self, tmp_file):
        frontmatter.strip(tmp_file, ['project', 'source'])
        assert '\n\n\n' not in tmp_file.read_text()

    def test_preserves_body(self, tmp_file):
        frontmatter.strip(tmp_file, ['project'])
        assert "# Conteúdo do recurso" in tmp_file.read_text()

    def test_does_not_change_scope(self, tmp_file):
        # strip é genérico — publish_resource chama write({'scope': 'global'}) separadamente
        frontmatter.strip(tmp_file, ['project', 'source'])
        result = frontmatter.read(tmp_file)
        assert result.get('scope') == 'project'


class TestInject:
    def test_sets_project(self, tmp_file):
        frontmatter.inject(tmp_file, 'MeuProjeto', 'hub/skills/meu-recurso@1.0.0')
        result = frontmatter.read(tmp_file)
        assert result['project'] == 'MeuProjeto'

    def test_sets_source(self, tmp_file):
        frontmatter.inject(tmp_file, 'MeuProjeto', 'hub/skills/meu-recurso@1.0.0')
        result = frontmatter.read(tmp_file)
        assert result['source'] == 'hub/skills/meu-recurso@1.0.0'

    def test_sets_created(self, tmp_file):
        from datetime import date
        frontmatter.inject(tmp_file, 'MeuProjeto', 'hub/skills/meu-recurso@1.0.0')
        result = frontmatter.read(tmp_file)
        assert result['created'] == str(date.today())

    def test_inserts_under_system_comment(self, tmp_path):
        f = tmp_path / "resource.md"
        f.write_text(
            "---\nname: teste\n\n# system\nscope: project\n---\n\nBody.\n"
        )
        frontmatter.inject(f, 'Proj', 'local')
        content = f.read_text()
        # project e source devem aparecer após # system (dentro do bloco system)
        assert content.index('# system') < content.index('project:')
        assert content.index('# system') < content.index('source:')

    def test_preserves_body(self, tmp_file):
        frontmatter.inject(tmp_file, 'MeuProjeto', 'local')
        assert "# Conteúdo do recurso" in tmp_file.read_text()
