"""
Testes de contrato de integração para o padrão --prepare.

Chama o CLI via subprocess e verifica:
- stdout é JSON válido
- exit code é sempre 0
- chaves obrigatórias estão presentes
- erros retornam {"error": "..."} com exit 0 (nunca traceback)
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _run(args: list, env_hub: Path = None) -> subprocess.CompletedProcess:
    """Executa o CLI via subprocess com env opcional para hub."""
    env = os.environ.copy()
    if env_hub is not None:
        env["CLI_HUB_PATH"] = str(env_hub)
    return subprocess.run(
        [sys.executable, "-m", "cli"] + args,
        capture_output=True, text=True, env=env,
    )


def _project(tmp_path: Path, name: str = "test-project") -> Path:
    """Cria estrutura mínima de projeto com .claude/CLAUDE.md."""
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir(parents=True)
    (claude_dir / "CLAUDE.md").write_text(
        f"---\nname: {name}\ntype: doc\n---\n\n# Projeto\n"
    )
    return claude_dir


def _hub(tmp_path: Path) -> Path:
    """Cria hub mínimo com uma skill."""
    hub_res = tmp_path / "hub"
    skill_dir = hub_res / "skills" / "sample-skill"
    skill_dir.mkdir(parents=True)
    (skill_dir / "skill.md").write_text(
        "---\nname: sample-skill\nversion: 1.0.0\ndescription: Skill de exemplo\n---\n\n# Body\n"
    )
    return tmp_path


# ---------------------------------------------------------------------------
# setup-claude --prepare
# (não depende de hub — testado sem CLI_HUB_PATH)
# ---------------------------------------------------------------------------

class TestSetupClaudePrepare:
    def test_exit_code_0(self, tmp_path):
        result = _run(["setup-claude", "--prepare", "--path", str(tmp_path)])
        assert result.returncode == 0

    def test_stdout_is_valid_json(self, tmp_path):
        result = _run(["setup-claude", "--prepare", "--path", str(tmp_path)])
        data = json.loads(result.stdout)
        assert isinstance(data, dict)

    def test_stderr_is_empty(self, tmp_path):
        result = _run(["setup-claude", "--prepare", "--path", str(tmp_path)])
        assert result.stderr == ""

    def test_required_keys_present(self, tmp_path):
        result = _run(["setup-claude", "--prepare", "--path", str(tmp_path)])
        data = json.loads(result.stdout)
        assert "context" in data
        assert "suggestions" in data
        assert "current_path" in data["context"]
        assert "project_paths" in data["suggestions"]

    def test_current_path_matches_argument(self, tmp_path):
        result = _run(["setup-claude", "--prepare", "--path", str(tmp_path)])
        data = json.loads(result.stdout)
        assert data["context"]["current_path"] == str(tmp_path)

    def test_without_prepare_exits_1(self, tmp_path):
        result = _run(["setup-claude"])
        assert result.returncode == 1

    def test_without_prepare_prints_usage_to_stderr(self, tmp_path):
        result = _run(["setup-claude"])
        assert "setup-claude" in result.stderr


# ---------------------------------------------------------------------------
# build-resource --prepare
# (não depende de hub — hub_dir() nunca é chamado em modo --prepare)
# ---------------------------------------------------------------------------

class TestBuildResourcePrepare:
    def test_exit_code_0(self, tmp_path):
        claude_dir = _project(tmp_path)
        result = _run(["build-resource", "--type", "skill", "--prepare", "--dest", str(claude_dir)])
        assert result.returncode == 0

    def test_stdout_is_valid_json(self, tmp_path):
        claude_dir = _project(tmp_path)
        result = _run(["build-resource", "--type", "skill", "--prepare", "--dest", str(claude_dir)])
        data = json.loads(result.stdout)
        assert isinstance(data, dict)

    def test_stderr_is_empty(self, tmp_path):
        claude_dir = _project(tmp_path)
        result = _run(["build-resource", "--type", "skill", "--prepare", "--dest", str(claude_dir)])
        assert result.stderr == ""

    def test_required_keys_present(self, tmp_path):
        claude_dir = _project(tmp_path)
        result = _run(["build-resource", "--type", "skill", "--prepare", "--dest", str(claude_dir)])
        data = json.loads(result.stdout)
        assert "context" in data
        assert "meta" in data
        assert "suggestions" in data

    def test_context_keys(self, tmp_path):
        claude_dir = _project(tmp_path)
        result = _run(["build-resource", "--type", "skill", "--prepare", "--dest", str(claude_dir)])
        data = json.loads(result.stdout)
        assert "current_path" in data["context"]
        assert "project_name" in data["context"]

    def test_meta_keys(self, tmp_path):
        claude_dir = _project(tmp_path)
        result = _run(["build-resource", "--type", "skill", "--prepare", "--dest", str(claude_dir)])
        data = json.loads(result.stdout)
        assert "has_existing_resources" in data["meta"]
        assert "naming_pattern" in data["meta"]
        assert "existing_names" in data["meta"]

    def test_project_name_from_claude_md(self, tmp_path):
        claude_dir = _project(tmp_path, name="meu-projeto")
        result = _run(["build-resource", "--type", "skill", "--prepare", "--dest", str(claude_dir)])
        data = json.loads(result.stdout)
        assert data["context"]["project_name"] == "meu-projeto"

    # --- contrato de erro ---

    def test_error_when_no_claude_md_exit_0(self, tmp_path):
        (tmp_path / ".claude").mkdir()
        result = _run(["build-resource", "--type", "skill", "--prepare", "--dest", str(tmp_path / ".claude")])
        assert result.returncode == 0

    def test_error_when_no_claude_md_returns_json(self, tmp_path):
        (tmp_path / ".claude").mkdir()
        result = _run(["build-resource", "--type", "skill", "--prepare", "--dest", str(tmp_path / ".claude")])
        data = json.loads(result.stdout)
        assert "error" in data

    def test_error_stderr_empty_on_failure(self, tmp_path):
        (tmp_path / ".claude").mkdir()
        result = _run(["build-resource", "--type", "skill", "--prepare", "--dest", str(tmp_path / ".claude")])
        assert result.stderr == ""


# ---------------------------------------------------------------------------
# install-resource --prepare
# (depende de hub — usa CLI_HUB_PATH via tmp hub)
# ---------------------------------------------------------------------------

class TestInstallResourcePrepare:
    def test_exit_code_0(self, tmp_path):
        claude_dir = _project(tmp_path / "project")
        hub = _hub(tmp_path / "hub")
        result = _run(
            ["install-resource", "--type", "skill", "--prepare", "--dest", str(claude_dir)],
            env_hub=hub,
        )
        assert result.returncode == 0

    def test_stdout_is_valid_json(self, tmp_path):
        claude_dir = _project(tmp_path / "project")
        hub = _hub(tmp_path / "hub")
        result = _run(
            ["install-resource", "--type", "skill", "--prepare", "--dest", str(claude_dir)],
            env_hub=hub,
        )
        data = json.loads(result.stdout)
        assert isinstance(data, dict)

    def test_stderr_is_empty(self, tmp_path):
        claude_dir = _project(tmp_path / "project")
        hub = _hub(tmp_path / "hub")
        result = _run(
            ["install-resource", "--type", "skill", "--prepare", "--dest", str(claude_dir)],
            env_hub=hub,
        )
        assert result.stderr == ""

    def test_required_keys_present(self, tmp_path):
        claude_dir = _project(tmp_path / "project")
        hub = _hub(tmp_path / "hub")
        result = _run(
            ["install-resource", "--type", "skill", "--prepare", "--dest", str(claude_dir)],
            env_hub=hub,
        )
        data = json.loads(result.stdout)
        assert "context" in data
        assert "available" in data
        assert "installed" in data
        assert "meta" in data

    def test_available_lists_hub_skills(self, tmp_path):
        claude_dir = _project(tmp_path / "project")
        hub = _hub(tmp_path / "hub")
        result = _run(
            ["install-resource", "--type", "skill", "--prepare", "--dest", str(claude_dir)],
            env_hub=hub,
        )
        data = json.loads(result.stdout)
        names = [r["name"] for r in data["available"]]
        assert "sample-skill" in names

    def test_installed_empty_when_no_skills(self, tmp_path):
        claude_dir = _project(tmp_path / "project")
        hub = _hub(tmp_path / "hub")
        result = _run(
            ["install-resource", "--type", "skill", "--prepare", "--dest", str(claude_dir)],
            env_hub=hub,
        )
        data = json.loads(result.stdout)
        assert data["installed"] == []
        assert data["meta"]["has_installed"] is False

    # --- contrato de erro ---

    def test_error_when_no_claude_md_exit_0(self, tmp_path):
        (tmp_path / ".claude").mkdir()
        hub = _hub(tmp_path / "hub")
        result = _run(
            ["install-resource", "--type", "skill", "--prepare", "--dest", str(tmp_path / ".claude")],
            env_hub=hub,
        )
        assert result.returncode == 0

    def test_error_when_no_claude_md_returns_json(self, tmp_path):
        (tmp_path / ".claude").mkdir()
        hub = _hub(tmp_path / "hub")
        result = _run(
            ["install-resource", "--type", "skill", "--prepare", "--dest", str(tmp_path / ".claude")],
            env_hub=hub,
        )
        data = json.loads(result.stdout)
        assert "error" in data

    def test_error_when_hub_not_configured_exit_0(self, tmp_path):
        """hub_dir() falha → contrato de erro deve ser respeitado (exit 0, JSON)."""
        claude_dir = _project(tmp_path)
        env = os.environ.copy()
        env.pop("CLI_HUB_PATH", None)
        # aponta hub-path para arquivo inexistente isolando do hub real
        env["HOME"] = str(tmp_path)
        result = subprocess.run(
            [sys.executable, "-m", "cli", "install-resource", "--type", "skill",
             "--prepare", "--dest", str(claude_dir)],
            capture_output=True, text=True, env=env,
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "error" in data

    def test_error_stderr_empty_on_failure(self, tmp_path):
        (tmp_path / ".claude").mkdir()
        hub = _hub(tmp_path / "hub")
        result = _run(
            ["install-resource", "--type", "skill", "--prepare", "--dest", str(tmp_path / ".claude")],
            env_hub=hub,
        )
        assert result.stderr == ""


# ---------------------------------------------------------------------------
# Contrato de erro — cobertura transversal aos 3 comandos
# ---------------------------------------------------------------------------

class TestErrorContract:
    """
    Verifica que --prepare nunca vaza exceções:
    - stdout sempre é JSON válido
    - exit code sempre é 0
    - stderr sempre é vazio
    - campo "error" presente com mensagem não vazia
    """

    # --- tipo inválido ---

    def test_build_resource_invalid_type_exit_0(self, tmp_path):
        claude_dir = _project(tmp_path)
        result = _run(["build-resource", "--type", "invalido", "--prepare", "--dest", str(claude_dir)])
        assert result.returncode == 0

    def test_build_resource_invalid_type_returns_json_error(self, tmp_path):
        claude_dir = _project(tmp_path)
        result = _run(["build-resource", "--type", "invalido", "--prepare", "--dest", str(claude_dir)])
        data = json.loads(result.stdout)
        assert "error" in data
        assert data["error"] != ""

    def test_build_resource_invalid_type_stderr_empty(self, tmp_path):
        claude_dir = _project(tmp_path)
        result = _run(["build-resource", "--type", "invalido", "--prepare", "--dest", str(claude_dir)])
        assert result.stderr == ""

    def test_install_resource_invalid_type_exit_0(self, tmp_path):
        claude_dir = _project(tmp_path / "project")
        hub = _hub(tmp_path / "hub")
        result = _run(
            ["install-resource", "--type", "invalido", "--prepare", "--dest", str(claude_dir)],
            env_hub=hub,
        )
        assert result.returncode == 0

    def test_install_resource_invalid_type_returns_json_error(self, tmp_path):
        claude_dir = _project(tmp_path / "project")
        hub = _hub(tmp_path / "hub")
        result = _run(
            ["install-resource", "--type", "invalido", "--prepare", "--dest", str(claude_dir)],
            env_hub=hub,
        )
        data = json.loads(result.stdout)
        assert "error" in data
        assert data["error"] != ""

    def test_install_resource_invalid_type_stderr_empty(self, tmp_path):
        claude_dir = _project(tmp_path / "project")
        hub = _hub(tmp_path / "hub")
        result = _run(
            ["install-resource", "--type", "invalido", "--prepare", "--dest", str(claude_dir)],
            env_hub=hub,
        )
        assert result.stderr == ""

    # --- mensagem de erro não vazia ---

    def test_build_resource_error_message_not_empty_on_missing_claude_md(self, tmp_path):
        (tmp_path / ".claude").mkdir()
        result = _run(["build-resource", "--type", "skill", "--prepare", "--dest", str(tmp_path / ".claude")])
        data = json.loads(result.stdout)
        assert data["error"] != ""

    def test_install_resource_error_message_not_empty_on_missing_claude_md(self, tmp_path):
        (tmp_path / ".claude").mkdir()
        hub = _hub(tmp_path / "hub")
        result = _run(
            ["install-resource", "--type", "skill", "--prepare", "--dest", str(tmp_path / ".claude")],
            env_hub=hub,
        )
        data = json.loads(result.stdout)
        assert data["error"] != ""

    def test_install_resource_error_message_not_empty_on_missing_hub(self, tmp_path):
        claude_dir = _project(tmp_path)
        env = os.environ.copy()
        env.pop("CLI_HUB_PATH", None)
        env["HOME"] = str(tmp_path)
        result = subprocess.run(
            [sys.executable, "-m", "cli", "install-resource", "--type", "skill",
             "--prepare", "--dest", str(claude_dir)],
            capture_output=True, text=True, env=env,
        )
        data = json.loads(result.stdout)
        assert data["error"] != ""

    # --- setup-claude: --path inexistente não é erro (retorna como candidato) ---

    def test_setup_claude_nonexistent_path_exit_0(self, tmp_path):
        nonexistent = tmp_path / "nao-existe"
        result = _run(["setup-claude", "--prepare", "--path", str(nonexistent)])
        assert result.returncode == 0

    def test_setup_claude_nonexistent_path_returns_json_not_error(self, tmp_path):
        """--path inexistente é válido — setup-claude não valida existência do dir."""
        nonexistent = tmp_path / "nao-existe"
        result = _run(["setup-claude", "--prepare", "--path", str(nonexistent)])
        data = json.loads(result.stdout)
        assert "error" not in data
        assert "context" in data


# ---------------------------------------------------------------------------
# Comportamento sem --prepare
# Documenta o contrato DIFERENTE do modo normal:
#   - exit code 1 em erro (não 0)
#   - erro em stderr (não stdout JSON)
#   - stdout vazio
# ---------------------------------------------------------------------------

class TestWithoutPrepare:
    """
    Verifica o contrato do modo normal (sem --prepare).
    O objetivo não é testar o fluxo completo de instalação/criação,
    mas documentar explicitamente que o contrato de saída é diferente
    do modo --prepare — importante para quem lê ou escreve command.md.
    """

    # --- build-resource ---

    def test_build_resource_without_name_exits_1(self, tmp_path):
        claude_dir = _project(tmp_path)
        result = _run(["build-resource", "--type", "skill", "--dest", str(claude_dir)])
        assert result.returncode == 1

    def test_build_resource_without_name_error_in_stderr(self, tmp_path):
        claude_dir = _project(tmp_path)
        result = _run(["build-resource", "--type", "skill", "--dest", str(claude_dir)])
        assert result.stderr != ""

    def test_build_resource_without_name_stdout_empty(self, tmp_path):
        claude_dir = _project(tmp_path)
        result = _run(["build-resource", "--type", "skill", "--dest", str(claude_dir)])
        assert result.stdout == ""

    # --- install-resource ---
    # hub_dir() é chamado antes da validação de --name no modo normal,
    # por isso o teste usa CLI_HUB_PATH com hub mínimo.

    def test_install_resource_without_name_exits_1(self, tmp_path):
        claude_dir = _project(tmp_path / "project")
        hub = _hub(tmp_path / "hub")
        result = _run(
            ["install-resource", "--type", "skill", "--dest", str(claude_dir)],
            env_hub=hub,
        )
        assert result.returncode == 1

    def test_install_resource_without_name_error_in_stderr(self, tmp_path):
        claude_dir = _project(tmp_path / "project")
        hub = _hub(tmp_path / "hub")
        result = _run(
            ["install-resource", "--type", "skill", "--dest", str(claude_dir)],
            env_hub=hub,
        )
        assert result.stderr != ""

    def test_install_resource_without_name_stdout_empty(self, tmp_path):
        claude_dir = _project(tmp_path / "project")
        hub = _hub(tmp_path / "hub")
        result = _run(
            ["install-resource", "--type", "skill", "--dest", str(claude_dir)],
            env_hub=hub,
        )
        assert result.stdout == ""

    # --- setup-claude (já coberto em TestSetupClaudePrepare, referência explícita) ---

    def test_setup_claude_without_prepare_exits_1(self, tmp_path):
        """Duplica TestSetupClaudePrepare.test_without_prepare_exits_1 intencionalmente
        para manter a classe TestWithoutPrepare como referência completa do contrato."""
        result = _run(["setup-claude"])
        assert result.returncode == 1

    def test_setup_claude_without_prepare_error_in_stderr(self, tmp_path):
        result = _run(["setup-claude"])
        assert result.stderr != ""

    def test_setup_claude_without_prepare_stdout_empty(self, tmp_path):
        result = _run(["setup-claude"])
        assert result.stdout == ""


# ---------------------------------------------------------------------------
# Encoding — caracteres UTF-8 preservados no JSON de saída
# ---------------------------------------------------------------------------

class TestJsonEncoding:
    """
    Verifica que json.dumps(..., ensure_ascii=False) produz JSON com
    caracteres UTF-8 literais — não sequências unicode escapadas.
    Relevante para nomes de projeto em pt-BR com acentuação.
    """

    def test_build_resource_project_name_with_accents_is_decodable(self, tmp_path):
        claude_dir = _project(tmp_path, name="revisão-ux")
        result = _run(["build-resource", "--type", "skill", "--prepare", "--dest", str(claude_dir)])
        data = json.loads(result.stdout)
        assert isinstance(data, dict)

    def test_build_resource_project_name_with_accents_preserved(self, tmp_path):
        claude_dir = _project(tmp_path, name="revisão-ux")
        result = _run(["build-resource", "--type", "skill", "--prepare", "--dest", str(claude_dir)])
        data = json.loads(result.stdout)
        assert data["context"]["project_name"] == "revisão-ux"

    def test_install_resource_project_name_with_accents_is_decodable(self, tmp_path):
        claude_dir = _project(tmp_path / "project", name="gestão-conteúdo")
        hub = _hub(tmp_path / "hub")
        result = _run(
            ["install-resource", "--type", "skill", "--prepare", "--dest", str(claude_dir)],
            env_hub=hub,
        )
        data = json.loads(result.stdout)
        assert isinstance(data, dict)

    def test_install_resource_project_name_with_accents_preserved(self, tmp_path):
        claude_dir = _project(tmp_path / "project", name="gestão-conteúdo")
        hub = _hub(tmp_path / "hub")
        result = _run(
            ["install-resource", "--type", "skill", "--prepare", "--dest", str(claude_dir)],
            env_hub=hub,
        )
        data = json.loads(result.stdout)
        assert data["context"]["project_name"] == "gestão-conteúdo"


# ---------------------------------------------------------------------------
# Hub sem recursos do tipo pedido
# ---------------------------------------------------------------------------

class TestHubWithoutResourceType:
    """
    Verifica que hub sem diretório do tipo pedido retorna available: []
    e has_available: false — não {"error": ...}.

    O _hub() helper cria apenas skills. Usar --type agent exercita o
    caminho onde hub/agents/ não existe.
    """

    def test_available_empty_when_type_absent_from_hub(self, tmp_path):
        claude_dir = _project(tmp_path / "project")
        hub = _hub(tmp_path / "hub")
        result = _run(
            ["install-resource", "--type", "agent", "--prepare", "--dest", str(claude_dir)],
            env_hub=hub,
        )
        data = json.loads(result.stdout)
        assert data["available"] == []

    def test_has_available_false_when_type_absent_from_hub(self, tmp_path):
        claude_dir = _project(tmp_path / "project")
        hub = _hub(tmp_path / "hub")
        result = _run(
            ["install-resource", "--type", "agent", "--prepare", "--dest", str(claude_dir)],
            env_hub=hub,
        )
        data = json.loads(result.stdout)
        assert data["meta"]["has_available"] is False

    def test_no_error_key_when_type_absent_from_hub(self, tmp_path):
        """Diretório ausente não é erro — é hub vazio para esse tipo."""
        claude_dir = _project(tmp_path / "project")
        hub = _hub(tmp_path / "hub")
        result = _run(
            ["install-resource", "--type", "agent", "--prepare", "--dest", str(claude_dir)],
            env_hub=hub,
        )
        data = json.loads(result.stdout)
        assert "error" not in data

    def test_exit_0_when_type_absent_from_hub(self, tmp_path):
        claude_dir = _project(tmp_path / "project")
        hub = _hub(tmp_path / "hub")
        result = _run(
            ["install-resource", "--type", "agent", "--prepare", "--dest", str(claude_dir)],
            env_hub=hub,
        )
        assert result.returncode == 0
