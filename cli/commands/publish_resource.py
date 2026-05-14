import difflib
import json
import shutil
import tempfile
from datetime import date
from pathlib import Path

from cli import config
from cli.utils import files, frontmatter, registry, templates


def register(sub):
    p = sub.add_parser("publish-resource", help="Publica um recurso do projeto no hub")
    p.add_argument("--type", required=True, dest="resource_type",
                   help="Tipo do recurso (skill, agent, hook, command)")
    p.add_argument("--name", required=True, help="Nome do recurso")
    p.add_argument("--src", default="", help="Diretório .claude/ fonte (padrão: .claude/ do projeto atual)")
    p.add_argument("--validate-only", action="store_true", dest="validate_only",
                   help="Apenas valida o recurso sem publicar")
    p.set_defaults(func=run)


def run(args):
    hub = config.hub_dir()
    src_dir = Path(args.src).expanduser().resolve() if args.src else Path.cwd() / ".claude"
    resource_type = args.resource_type
    name = args.name

    # T1: validar presença de CLAUDE.md no diretório .claude/ do projeto
    if not (src_dir / "CLAUDE.md").exists():
        raise FileNotFoundError(
            f"CLAUDE.md não encontrado em: {src_dir}\n"
            f"  Verifique se --src aponta para o diretório .claude/ correto"
        )

    if resource_type == "plugin":
        raise ValueError(
            f"Publicação de plugin não suportada. Edite hub/plugins/{name}/plugin.json diretamente."
        )

    if resource_type == "hook":
        # T2: modo validação apenas para hook
        if args.validate_only:
            _validate_hook(src_dir, name)
            print("  [ok] Validação concluída sem erros")
            return
        _publish_hook(hub, src_dir, name)
        return

    valid_types = ("skill", "agent", "command")
    if resource_type not in valid_types:
        raise ValueError(f"Tipo inválido: {resource_type}. Válidos para publish-resource: {', '.join(valid_types)}")

    type_dir = config.dest_dir_for_type(src_dir, resource_type)
    src = type_dir / f"{name}.md"

    if not src.exists():
        raise FileNotFoundError(f"Recurso não encontrado: {src}")

    # L3: rejeitar arquivos proxy (commands instalados via skill/agent)
    if src.read_text().startswith("<!-- proxy:"):
        raise ValueError(
            f"'{name}' é um proxy de skill/agent e não pode ser publicado diretamente.\n"
            f"  Use --type skill ou --type agent para publicar o recurso original."
        )

    _validate(src)

    # T2: modo validação apenas
    if args.validate_only:
        print("  [ok] Validação concluída sem erros")
        return

    fields = frontmatter.read(src)
    version = fields.get("version", "1.0.0")
    description = fields.get("description", "")
    tags_raw = fields.get("tags", "[]")
    project_name = fields.get("project", "")

    hub_resource_dir = hub / "hub" / f"{resource_type}s" / name
    hub_file = hub_resource_dir / f"{resource_type}.md"

    is_new = not hub_file.exists()
    if not is_new:
        bumped = files.bump_version(version)
        print(f"  -> Recurso já existe no hub — bump de versão: {version} -> {bumped}")
        version = bumped

    today = str(date.today())
    resource_id = None
    if is_new:
        existing = registry.find(hub, resource_type, name)
        if existing and existing.get("id"):
            resource_id = existing["id"]
        else:
            resource_id = registry.next_id(hub, resource_type)
            print(f"  -> ID atribuído: {resource_id}")

    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as tf:
        tmp = Path(tf.name)
    try:
        shutil.copy2(src, tmp)
        frontmatter.write(tmp, {"version": version, "updated": today})
        frontmatter.strip(tmp, ["project", "source"])
        frontmatter.write(tmp, {"scope": "global"}, section="system")
        if resource_id:
            frontmatter.write(tmp, {"id": resource_id}, section="about")
        tmp.write_text(templates.normalize_body(tmp.read_text(), project_name))

        _show_diff(hub_file, tmp)

        hub_resource_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(tmp, hub_file)
        print(f"  [ok] Publicado: {hub_file}")
    finally:
        tmp.unlink(missing_ok=True)

    # T4: atualizar version e source no arquivo local após publicação
    # version é atualizada na seção history; source na seção system (evita append fora do bloco)
    frontmatter.write(src, {"version": version}, section="history")
    frontmatter.write(src, {"source": f"hub/{resource_type}s/{name}@{version}"}, section="system")
    if resource_id:
        frontmatter.write(src, {"id": resource_id}, section="about")

    tags = _parse_tags(tags_raw)
    entry = {
        "version": version,
        "description": description,
        "tags": tags,
        "updated": today,
    }
    if resource_id:
        entry["id"] = resource_id
    registry.upsert(hub, resource_type, name, entry)

    _append_changelog(hub, resource_type, name, version)
    print(f"  [ok] {name}@{version} disponível no hub")


def _publish_hook(hub: Path, src_dir: Path, name: str) -> None:
    hook_src_dir = src_dir / "hooks" / name
    hook_json_src = hook_src_dir / "hook.json"
    hook_sh_src = hook_src_dir / "hook.sh"

    if not hook_src_dir.is_dir():
        raise FileNotFoundError(f"Hook não encontrado: {hook_src_dir}")
    if not hook_json_src.exists():
        raise FileNotFoundError(f"hook.json ausente: {hook_json_src}")
    if not hook_sh_src.exists():
        raise FileNotFoundError(f"hook.sh ausente: {hook_sh_src}")

    with open(hook_json_src) as f:
        data = json.load(f)

    description = data.get("description", "")
    if not description or description in ('""', "(preencher)"):
        raise ValueError("Campo obrigatório ausente: description — preencha hook.json antes de publicar")

    version = data.get("version", "1.0.0")
    tags_raw = data.get("tags", [])

    hub_hook_dir = hub / "hub" / "hooks" / name
    hub_json = hub_hook_dir / "hook.json"

    is_new = not hub_hook_dir.exists()
    if not is_new:
        bumped = files.bump_version(version)
        print(f"  -> Hook já existe no hub — bump de versão: {version} -> {bumped}")
        version = bumped

    today = str(date.today())
    resource_id = None
    if is_new:
        existing = registry.find(hub, "hook", name)
        if existing and existing.get("id"):
            resource_id = existing["id"]
        else:
            resource_id = registry.next_id(hub, "hook")
            print(f"  -> ID atribuído: {resource_id}")

    pub_data = {k: v for k, v in data.items() if k not in ("project", "source")}
    pub_data["version"] = version
    pub_data["updated"] = today
    pub_data["scope"] = "global"
    if resource_id:
        pub_data["id"] = resource_id

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
        tmp_json = Path(tf.name)
    try:
        tmp_json.write_text(json.dumps(pub_data, indent=2, ensure_ascii=False) + "\n")

        _show_diff(hub_json, tmp_json)

        hub_hook_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(tmp_json, hub_json)
        shutil.copy2(hook_sh_src, hub_hook_dir / "hook.sh")
        print(f"  [ok] Publicado: {hub_hook_dir}/")
    finally:
        tmp_json.unlink(missing_ok=True)

    # T4: atualizar version e source no arquivo local após publicação do hook
    data["version"] = version
    data["source"] = f"hub/hooks/{name}@{version}"
    if resource_id:
        data["id"] = resource_id
    hook_json_src.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")

    tags = tags_raw if isinstance(tags_raw, list) else _parse_tags(str(tags_raw))
    entry = {
        "version": version,
        "description": description,
        "tags": tags,
        "updated": today,
    }
    if resource_id:
        entry["id"] = resource_id
    registry.upsert(hub, "hook", name, entry)

    _append_changelog(hub, "hook", name, version)
    print(f"  [ok] {name}@{version} disponível no hub")


def _validate_hook(src_dir: Path, name: str) -> None:
    """Valida campos obrigatórios de um hook antes de publicar."""
    hook_json = src_dir / "hooks" / name / "hook.json"
    if not (src_dir / "hooks" / name).is_dir():
        raise FileNotFoundError(f"Hook não encontrado: {src_dir / 'hooks' / name}")
    if not hook_json.exists():
        raise FileNotFoundError(f"hook.json ausente: {hook_json}")

    data = json.loads(hook_json.read_text())
    description = data.get("description", "")
    if not description or description in ('""', "(preencher)"):
        raise ValueError("Campo obrigatório ausente: description — preencha hook.json antes de publicar")


def _validate(file: Path) -> None:
    fields = frontmatter.read(file)
    errors = 0
    for field in ("name", "type", "version", "description"):
        val = fields.get(field, "")
        if not val or val in ('""', "(preencher)"):
            print(f"  [erro] Campo obrigatório ausente ou vazio: {field}", flush=True)
            errors += 1
    for field in ("author", "tags"):
        val = fields.get(field, "")
        if not val or val in ("[]", '""'):
            print(f"  [aviso] Campo recomendado vazio: {field}")
    if errors:
        raise ValueError(f"{errors} erro(s) — preencha os campos obrigatórios antes de publicar")


def _show_diff(existing: Path, new: Path) -> None:
    print("\nDiff do que será publicado:")
    if existing.exists():
        old_lines = existing.read_text().splitlines(keepends=True)
        new_lines = new.read_text().splitlines(keepends=True)
        diff = list(difflib.unified_diff(old_lines, new_lines, fromfile=str(existing), tofile="(novo)"))
        print("".join(diff) if diff else "  (sem diferenças no conteúdo)")
    else:
        print(new.read_text())
    print()


def _parse_tags(tags_raw: str) -> list:
    if not tags_raw or tags_raw == "[]":
        return []
    return [t.strip() for t in tags_raw.strip("[]").split(",") if t.strip()]


def _append_changelog(hub: Path, resource_type: str, name: str, version: str) -> None:
    changelog = hub / "CHANGELOG.md"
    if not changelog.exists():
        return
    today = str(date.today())
    content = changelog.read_text()
    entry = f"- [{today}] [{resource_type}] {name} v{version} — publicado no hub\n"
    marker = "<!-- Recursos em desenvolvimento ou aguardando publicação no hub. -->"
    if marker in content:
        changelog.write_text(content.replace(marker, marker + "\n" + entry))
        print(f"  [ok] CHANGELOG.md atualizado")
