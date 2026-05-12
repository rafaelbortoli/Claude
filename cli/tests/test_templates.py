from cli.utils import templates


SAMPLE_WITH_HEADER = """\
---
name: recurso
type: skill
---

Instalado em /Users/bortoli/Code/MeuProjeto pelo time MeuProjeto.
"""

SAMPLE_WITHOUT_HEADER = "Arquivo em /home/user/projetos sem frontmatter.\n"


class TestFill:
    def test_replaces_placeholder(self):
        result = templates.fill("Olá, {{nome}}!", {'nome': 'Mundo'})
        assert result == "Olá, Mundo!"

    def test_replaces_multiple_placeholders(self):
        result = templates.fill(
            "{{tipo}} chamado {{nome}}",
            {'tipo': 'Skill', 'nome': 'code-review'}
        )
        assert result == "Skill chamado code-review"

    def test_leaves_unknown_placeholder(self):
        result = templates.fill("Valor: {{desconhecido}}", {'outro': 'x'})
        assert result == "Valor: {{desconhecido}}"

    def test_empty_context(self):
        original = "Sem {{substituicao}}"
        assert templates.fill(original, {}) == original

    def test_empty_template(self):
        assert templates.fill("", {'chave': 'valor'}) == ""


class TestNormalizeBody:
    def test_replaces_users_path(self):
        result = templates.normalize_body(SAMPLE_WITHOUT_HEADER, '')
        assert '/home/user/projetos' not in result
        assert '<path>' in result

    def test_replaces_home_path(self):
        content = "Arquivo em /Users/bortoli/Code/Projeto.\n"
        result = templates.normalize_body(content, '')
        assert '/Users/bortoli' not in result
        assert '<path>' in result

    def test_replaces_project_name(self):
        result = templates.normalize_body(SAMPLE_WITH_HEADER, 'MeuProjeto')
        assert 'MeuProjeto' not in result
        assert '<project-name>' in result

    def test_preserves_header(self):
        result = templates.normalize_body(SAMPLE_WITH_HEADER, 'MeuProjeto')
        assert result.startswith('---\n')
        assert 'name: recurso' in result

    def test_does_not_replace_in_header(self):
        content = "---\nname: MeuProjeto\n---\n\nCorpo.\n"
        result = templates.normalize_body(content, 'MeuProjeto')
        assert 'name: MeuProjeto' in result

    def test_empty_project_name_skips_replacement(self):
        content = "Texto com NomeProjeto.\n"
        result = templates.normalize_body(content, '')
        assert 'NomeProjeto' in result
