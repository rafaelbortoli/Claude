import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from cli import config
from cli.utils import frontmatter, registry


# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

HUB_PATH_FILE = Path.home() / ".claude" / "hub-path"
REQUIRED_FM_FIELDS = ("name", "type", "version", "description")
RESOURCE_TYPES = ("skills", "agents", "commands")
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")


# ---------------------------------------------------------------------------
# Fixtures de integração
# ---------------------------------------------------------------------------

@pytest.fixture
def hub_tmp(tmp_path, monkeypatch):
    """Hub isolado em tmp_path com templates do hub real. Nenhum side effect no hub real."""
    real_hub = config.hub_dir()
    shutil.copytree(real_hub / "build", tmp_path / "build")

    for d in ("skills", "agents", "commands", "hooks", "plugins", "instructions"):
        (tmp_path / "hub" / d).mkdir(parents=True)

    (tmp_path / "registry.json").write_text(
        json.dumps({
            "version": "1.0.0",
            "updated": "2026-01-01",
            "skills": [], "agents": [], "hooks": [],
            "commands": [], "plugins": [],
            "id_counters": {},
        }, indent=2) + "\n"
    )
    (tmp_path / "CHANGELOG.md").write_text(
        "<!-- Recursos em desenvolvimento ou aguardando publicação no hub. -->\n"
    )

    monkeypatch.setattr("cli.config.hub_dir", lambda: tmp_path)
    return tmp_path


@pytest.fixture
def hub_tmp_with_skill(hub_tmp):
    """hub_tmp com uma skill pré-publicada para testes de install."""
    skill_dir = hub_tmp / "hub" / "skills" / "skill-teste"
    skill_dir.mkdir(parents=True)
    (skill_dir / "skill.md").write_text(
        "---\n"
        "name: skill-teste\n"
        "type: skill\n"
        "version: 1.2.0\n"
        "description: Skill de teste para integração\n"
        "project: \"\"\n"
        "source: hub/skills/skill-teste@1.2.0\n"
        "author: Teste\n"
        "tags: [teste]\n"
        "scope: global\n"
        "auto_load: false\n"
        "---\n\n"
        "# Skill Teste\n\nConteúdo da skill de teste.\n"
    )
    return hub_tmp


@pytest.fixture
def project(tmp_path):
    """Projeto mínimo com .claude/CLAUDE.md."""
    dot_claude = tmp_path / "projeto" / ".claude"
    dot_claude.mkdir(parents=True)
    (dot_claude / "CLAUDE.md").write_text(
        "---\nname: Projeto Teste\ntype: product\n---\n\n# Projeto Teste\n"
    )
    return dot_claude


# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------

def _make_build_args(resource_type, name, dest):
    class Args:
        pass
    a = Args()
    a.resource_type = resource_type
    a.name = name
    a.dest = str(dest)
    a.prepare = False
    return a


def _make_install_args(resource_type, name, dest):
    return _make_build_args(resource_type, name, dest)


def _make_publish_args(resource_type, name, src, validate_only=False):
    class Args:
        pass
    a = Args()
    a.resource_type = resource_type
    a.name = name
    a.src = str(src)
    a.validate_only = validate_only
    return a


def _make_remove_args(resource_type, name, dest):
    return _make_build_args(resource_type, name, dest)


def _make_restore_args(resource_type, name, dest):
    return _make_build_args(resource_type, name, dest)


def _build_and_fill_skill(hub_tmp, project, name="minha-skill"):
    from cli.commands import build_resource
    build_resource.run(_make_build_args("skill", name, project))
    skill_file = project / "skills" / f"{name}.md"
    frontmatter.write(skill_file, {
        "description": "Descrição de teste",
        "author": "Teste",
        "tags": "[teste]",
    })
    return skill_file


# ===========================================================================
# SMOKE TESTS — leitura do sistema real, sem side effects
# ===========================================================================

class TestSmokeHubPath:
    def test_hub_path_file_exists(self):
        assert HUB_PATH_FILE.exists(), "~/.claude/hub-path não encontrado"

    def test_hub_path_points_to_real_directory(self):
        hub = Path(HUB_PATH_FILE.read_text().strip())
        assert hub.is_dir(), f"hub-path aponta para diretório inexistente: {hub}"

    def test_hub_path_contains_registry(self):
        hub = config.hub_dir()
        assert (hub / "registry.json").exists(), "registry.json não encontrado no hub"

    def test_hub_path_contains_build_templates(self):
        hub = config.hub_dir()
        assert (hub / "build").is_dir(), "Diretório build/ não encontrado no hub"


class TestSmokeCli:
    def test_cli_boots(self):
        result = subprocess.run(
            [sys.executable, "-m", "cli", "--help"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0, f"CLI falhou no boot:\n{result.stderr}"

    def test_all_subcommands_registered(self):
        result = subprocess.run(
            [sys.executable, "-m", "cli", "--help"],
            capture_output=True, text=True,
        )
        expected = (
            "build-resource", "install-resource", "publish-resource",
            "remove-resource", "restore-resource", "list-resources",
            "setup-claude",
        )
        for cmd in expected:
            assert cmd in result.stdout, f"Subcomando '{cmd}' ausente no --help"


class TestSmokeRegistry:
    def test_registry_is_valid_json(self):
        hub = config.hub_dir()
        data = json.loads((hub / "registry.json").read_text())
        assert isinstance(data, dict)

    def test_registry_has_required_collection_keys(self):
        hub = config.hub_dir()
        data = json.loads((hub / "registry.json").read_text())
        for key in ("skills", "agents", "commands", "hooks"):
            assert key in data, f"Chave '{key}' ausente no registry.json"

    def test_registry_ids_are_unique(self):
        hub = config.hub_dir()
        data = json.loads((hub / "registry.json").read_text())
        ids = [
            entry["id"]
            for key in ("skills", "agents", "commands", "hooks", "plugins")
            for entry in data.get(key, [])
            if "id" in entry
        ]
        assert len(ids) == len(set(ids)), "IDs duplicados no registry.json"

    def test_registry_versions_are_semver(self):
        hub = config.hub_dir()
        data = json.loads((hub / "registry.json").read_text())
        for key in ("skills", "agents", "commands", "hooks"):
            for entry in data.get(key, []):
                v = entry.get("version", "")
                assert SEMVER_RE.match(v), (
                    f"{entry.get('name')}: versão inválida '{v}' em {key}"
                )


class TestSmokeHubResources:
    def test_hub_resource_files_have_valid_frontmatter(self):
        hub = config.hub_dir()
        errors = []
        for resource_type in RESOURCE_TYPES:
            type_dir = hub / "hub" / resource_type
            if not type_dir.exists():
                continue
            singular = resource_type.rstrip("s")
            for resource_dir in type_dir.iterdir():
                if not resource_dir.is_dir():
                    continue
                md_file = resource_dir / f"{singular}.md"
                if not md_file.exists():
                    errors.append(f"{md_file}: arquivo principal ausente")
                    continue
                fields = frontmatter.read(md_file)
                for field in REQUIRED_FM_FIELDS:
                    val = fields.get(field, "")
                    if not val or val in ('""', "(preencher)"):
                        errors.append(f"{md_file}: campo '{field}' vazio ou placeholder")
        assert not errors, "Recursos com frontmatter inválido:\n" + "\n".join(errors)

    def test_hub_resource_versions_match_registry(self):
        hub = config.hub_dir()
        reg = json.loads((hub / "registry.json").read_text())
        errors = []
        for resource_type in RESOURCE_TYPES:
            singular = resource_type.rstrip("s")
            for entry in reg.get(resource_type, []):
                name = entry.get("name", "")
                reg_version = entry.get("version", "")
                md_file = hub / "hub" / resource_type / name / f"{singular}.md"
                if not md_file.exists():
                    errors.append(f"{resource_type}/{name}: no registry mas sem arquivo no hub")
                    continue
                file_version = frontmatter.read(md_file).get("version", "")
                if reg_version != file_version:
                    errors.append(
                        f"{resource_type}/{name}: registry={reg_version}, arquivo={file_version}"
                    )
        assert not errors, "Versões divergentes entre registry e arquivos:\n" + "\n".join(errors)

    def test_hub_resources_have_no_hardcoded_absolute_paths(self):
        hub = config.hub_dir()
        errors = [
            str(f)
            for f in (hub / "hub").rglob("*.md")
            if "/Users/" in f.read_text()
        ]
        assert not errors, (
            "Arquivos com paths absolutos hardcodados:\n" + "\n".join(errors)
        )

    def test_hub_resources_project_field_is_empty(self):
        hub = config.hub_dir()
        errors = []
        for resource_type in RESOURCE_TYPES:
            singular = resource_type.rstrip("s")
            type_dir = hub / "hub" / resource_type
            if not type_dir.exists():
                continue
            for resource_dir in type_dir.iterdir():
                md_file = resource_dir / f"{singular}.md"
                if not md_file.exists():
                    continue
                project = frontmatter.read(md_file).get("project", "")
                if project and project != '""':
                    errors.append(f"{md_file}: project='{project}' (deve ser vazio no hub)")
        assert not errors, "Recursos do hub com 'project' preenchido:\n" + "\n".join(errors)


# ===========================================================================
# INTEGRATION TESTS — workflows com hub e projeto isolados em tmp_path
# ===========================================================================

class TestBuildResource:
    def test_creates_skill_file(self, hub_tmp, project):
        from cli.commands import build_resource
        build_resource.run(_make_build_args("skill", "minha-skill", project))
        assert (project / "skills" / "minha-skill.md").exists()

    def test_skill_frontmatter_has_name_and_source(self, hub_tmp, project):
        from cli.commands import build_resource
        build_resource.run(_make_build_args("skill", "minha-skill", project))
        fields = frontmatter.read(project / "skills" / "minha-skill.md")
        assert fields["name"] == "minha-skill"
        assert fields["source"] == "local"
        assert fields["project"] == "Projeto Teste"

    def test_creates_agent_file(self, hub_tmp, project):
        from cli.commands import build_resource
        build_resource.run(_make_build_args("agent", "meu-agent", project))
        assert (project / "agents" / "meu-agent.md").exists()

    def test_raises_for_invalid_type(self, hub_tmp, project):
        from cli.commands import build_resource
        with pytest.raises(ValueError, match="Tipo inválido"):
            build_resource.run(_make_build_args("invalido", "test", project))

    def test_raises_if_no_claude_md(self, hub_tmp, tmp_path):
        from cli.commands import build_resource
        empty = tmp_path / "empty" / ".claude"
        empty.mkdir(parents=True)
        with pytest.raises(FileNotFoundError):
            build_resource.run(_make_build_args("skill", "test", empty))

    def test_raises_on_duplicate(self, hub_tmp, project):
        from cli.commands import build_resource
        build_resource.run(_make_build_args("skill", "minha-skill", project))
        with pytest.raises(FileExistsError):
            build_resource.run(_make_build_args("skill", "minha-skill", project))


class TestInstallResource:
    def test_installs_skill_file(self, hub_tmp_with_skill, project):
        from cli.commands import install_resource
        install_resource.run(_make_install_args("skill", "skill-teste", project))
        assert (project / "skills" / "skill-teste.md").exists()

    def test_creates_proxy_command(self, hub_tmp_with_skill, project):
        from cli.commands import install_resource
        install_resource.run(_make_install_args("skill", "skill-teste", project))
        proxy = project / "commands" / "skill-teste.md"
        assert proxy.exists()
        assert "proxy:skill:skill-teste" in proxy.read_text()

    def test_installed_skill_has_injected_metadata(self, hub_tmp_with_skill, project):
        from cli.commands import install_resource
        install_resource.run(_make_install_args("skill", "skill-teste", project))
        fields = frontmatter.read(project / "skills" / "skill-teste.md")
        assert fields["source"] == "hub/skills/skill-teste@1.2.0"
        assert fields["project"] == "Projeto Teste"

    def test_raises_if_not_in_hub(self, hub_tmp, project):
        from cli.commands import install_resource
        with pytest.raises(FileNotFoundError):
            install_resource.run(_make_install_args("skill", "nao-existe", project))


class TestPublishResource:
    def test_creates_hub_file(self, hub_tmp, project):
        from cli.commands import publish_resource
        skill_file = _build_and_fill_skill(hub_tmp, project)
        publish_resource.run(_make_publish_args("skill", "minha-skill", project))
        assert (hub_tmp / "hub" / "skills" / "minha-skill" / "skill.md").exists()

    def test_updates_registry_after_publish(self, hub_tmp, project):
        from cli.commands import publish_resource
        _build_and_fill_skill(hub_tmp, project)
        publish_resource.run(_make_publish_args("skill", "minha-skill", project))
        entry = registry.find(hub_tmp, "skill", "minha-skill")
        assert entry is not None
        assert entry["description"] == "Descrição de teste"

    def test_hub_file_has_no_project_field(self, hub_tmp, project):
        from cli.commands import publish_resource
        _build_and_fill_skill(hub_tmp, project)
        publish_resource.run(_make_publish_args("skill", "minha-skill", project))
        hub_file = hub_tmp / "hub" / "skills" / "minha-skill" / "skill.md"
        project_val = frontmatter.read(hub_file).get("project", "")
        assert project_val in ("", '""')

    def test_second_publish_bumps_version(self, hub_tmp, project):
        from cli.commands import publish_resource
        skill_file = _build_and_fill_skill(hub_tmp, project)
        frontmatter.write(skill_file, {"version": "1.0.5"})
        args = _make_publish_args("skill", "minha-skill", project)
        publish_resource.run(args)
        publish_resource.run(args)
        hub_file = hub_tmp / "hub" / "skills" / "minha-skill" / "skill.md"
        assert frontmatter.read(hub_file)["version"] == "1.0.6"

    def test_validate_only_does_not_write(self, hub_tmp, project):
        from cli.commands import publish_resource
        _build_and_fill_skill(hub_tmp, project)
        publish_resource.run(_make_publish_args("skill", "minha-skill", project, validate_only=True))
        assert not (hub_tmp / "hub" / "skills" / "minha-skill").exists()

    def test_raises_if_required_field_missing(self, hub_tmp, project):
        from cli.commands import build_resource, publish_resource
        build_resource.run(_make_build_args("skill", "incompleta", project))
        with pytest.raises(ValueError, match="erro"):
            publish_resource.run(_make_publish_args("skill", "incompleta", project))


class TestRemoveRestoreCycle:
    def test_remove_moves_skill_to_trash(self, hub_tmp, project):
        from cli.commands import build_resource, remove_resource
        build_resource.run(_make_build_args("skill", "minha-skill", project))
        remove_resource.run(_make_remove_args("skill", "minha-skill", project))
        assert not (project / "skills" / "minha-skill.md").exists()
        assert (project / "trash" / "skill" / "minha-skill" / "minha-skill.md").exists()

    def test_remove_deletes_proxy(self, hub_tmp_with_skill, project):
        from cli.commands import install_resource, remove_resource
        install_resource.run(_make_install_args("skill", "skill-teste", project))
        assert (project / "commands" / "skill-teste.md").exists()
        remove_resource.run(_make_remove_args("skill", "skill-teste", project))
        assert not (project / "commands" / "skill-teste.md").exists()

    def test_restore_recovers_skill_file(self, hub_tmp, project):
        from cli.commands import build_resource, remove_resource, restore_resource
        build_resource.run(_make_build_args("skill", "minha-skill", project))
        remove_resource.run(_make_remove_args("skill", "minha-skill", project))
        restore_resource.run(_make_restore_args("skill", "minha-skill", project))
        assert (project / "skills" / "minha-skill.md").exists()

    def test_restore_recreates_proxy(self, hub_tmp, project):
        from cli.commands import build_resource, remove_resource, restore_resource
        build_resource.run(_make_build_args("skill", "minha-skill", project))
        remove_resource.run(_make_remove_args("skill", "minha-skill", project))
        restore_resource.run(_make_restore_args("skill", "minha-skill", project))
        proxy = project / "commands" / "minha-skill.md"
        assert proxy.exists()
        assert "proxy:skill:minha-skill" in proxy.read_text()

    def test_restore_cleans_trash_entry(self, hub_tmp, project):
        from cli.commands import build_resource, remove_resource, restore_resource
        build_resource.run(_make_build_args("skill", "minha-skill", project))
        remove_resource.run(_make_remove_args("skill", "minha-skill", project))
        restore_resource.run(_make_restore_args("skill", "minha-skill", project))
        assert not (project / "trash" / "skill" / "minha-skill").exists()

    def test_remove_raises_if_not_found(self, hub_tmp, project):
        from cli.commands import remove_resource
        with pytest.raises(FileNotFoundError):
            remove_resource.run(_make_remove_args("skill", "nao-existe", project))

    def test_restore_raises_if_not_in_trash(self, hub_tmp, project):
        from cli.commands import restore_resource
        with pytest.raises(FileNotFoundError):
            restore_resource.run(_make_restore_args("skill", "nao-existe", project))
