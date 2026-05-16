import json
import shutil
from datetime import date
from pathlib import Path

from cli import config
from cli.utils import files, frontmatter
from cli.utils.files import git_author


_TEMPLATE_MAP = {
    "skill":   ("build/01-skills/_template", "skill.md"),
    "agent":   ("build/03-agents/_template", "agent.md"),
    "command": ("build/04-plugins/_template/commands", "command-name.md"),
    "plugin":  ("build/04-plugins/_template", "plugin.json"),
    "hook":    ("build/02-hooks/_template", None),
}

_PLACEHOLDERS = ["skill-name", "agent-name", "command-name"]


def register(sub):
    p = sub.add_parser("build-resource", help="Cria um novo recurso a partir do template")
    p.add_argument("--type", required=True, dest="resource_type",
                   help="Tipo do recurso (skill, agent, hook, command, plugin)")
    p.add_argument("--name", default="", help="Nome do recurso (obrigatório fora do modo --prepare)")
    p.add_argument("--dest", default="", help="Diretório .claude/ destino (padrão: .claude/ do projeto atual)")
    p.add_argument("--prepare", action="store_true",
                   help="Retorna JSON com contexto para popular opções no command.md")
    p.set_defaults(func=run)


def run(args):
    dest_dir = Path(args.dest).expanduser().resolve() if args.dest else Path.cwd() / ".claude"
    resource_type = args.resource_type

    if args.prepare:
        try:
            result = _prepare(dest_dir, resource_type)
            print(json.dumps(result, ensure_ascii=False))
        except Exception as e:
            print(json.dumps({"error": str(e)}, ensure_ascii=False))
        return

    if not args.name:
        raise ValueError("--name é obrigatório fora do modo --prepare")

    hub = config.hub_dir()
    name = args.name

    # validar presença de CLAUDE.md no diretório .claude/ do projeto
    if not (dest_dir / "CLAUDE.md").exists():
        raise FileNotFoundError(
            f"Projeto não encontrado em: {dest_dir}\n"
            f"  Use --dest <caminho/.claude> para especificar o diretório .claude/ do projeto"
        )

    if resource_type not in _TEMPLATE_MAP:
        raise ValueError(f"Tipo inválido: {resource_type}. Tipos válidos para build-resource: {', '.join(_TEMPLATE_MAP)}")

    project_name = _get_project_name(dest_dir)
    today = str(date.today())
    author = git_author()

    if resource_type == "hook":
        _build_hook(hub, dest_dir, name, project_name, today, author)
    elif resource_type == "plugin":
        _build_plugin(hub, dest_dir, name, project_name, today, author)
    else:
        _build_md_resource(hub, dest_dir, resource_type, name, project_name, today, author)


def _prepare(dest_dir: Path, resource_type: str) -> dict:
    """Computa contexto para o command.md popular AskUserQuestion sem inferência."""
    if not (dest_dir / "CLAUDE.md").exists():
        raise FileNotFoundError(f"Projeto não encontrado em: {dest_dir}")

    project_name = _get_project_name(dest_dir)
    current_path = str(dest_dir.parent)

    type_folder = dest_dir / f"{resource_type}s"
    existing_names = sorted(
        f.stem for f in type_folder.glob("*.md")
        if type_folder.exists()
    ) if type_folder.exists() else []

    return {
        "context": {
            "current_path": current_path,
            "project_name": project_name,
        },
        "meta": {
            "has_existing_resources": bool(existing_names),
            "naming_pattern":         _infer_naming_pattern(existing_names),
            "existing_names":         existing_names,
        },
        "suggestions": {
            "tags": _extract_tag_suggestions(dest_dir),
        },
    }


def _infer_naming_pattern(names: list) -> str:
    """Detecta padrão de nomenclatura a partir dos nomes existentes."""
    if not names:
        return "<nome>"
    part_counts = [len(n.split('-')) for n in names]
    most_common = max(set(part_counts), key=part_counts.count)
    return '-'.join([f'<parte-{i + 1}>' for i in range(most_common)])


def _extract_tag_suggestions(dest_dir: Path) -> list:
    """Extrai conjuntos de tags dos resources instalados, agrupados por frequência."""
    counter: dict = {}
    for folder in ["skills", "agents"]:
        folder_path = dest_dir / folder
        if not folder_path.exists():
            continue
        for f in folder_path.glob("*.md"):
            tags = frontmatter.read(f).get("tags", [])
            if isinstance(tags, list):
                for tag in tags:
                    counter[tag] = counter.get(tag, 0) + 1
    sorted_tags = sorted(counter, key=lambda t: counter[t], reverse=True)
    return [sorted_tags[i:i + 3] for i in range(0, min(len(sorted_tags), 9), 3)][:3]


def _get_project_name(dest_dir: Path) -> str:
    claude_md = dest_dir / "CLAUDE.md"
    if claude_md.exists():
        return frontmatter.read(claude_md).get("name", "")
    return ""


def _build_md_resource(hub: Path, dest_dir: Path, resource_type: str, name: str, project_name: str, today: str, author: str = "") -> None:
    tmpl_subdir, tmpl_filename = _TEMPLATE_MAP[resource_type]
    tmpl_file = hub / tmpl_subdir / tmpl_filename

    if not tmpl_file.exists():
        raise FileNotFoundError(f"Template não encontrado: {tmpl_file}")

    type_dir = config.dest_dir_for_type(dest_dir, resource_type)
    dest = type_dir / f"{name}.md"

    if dest.exists():
        raise FileExistsError(
            f"Recurso já existe: {dest} — edite-o diretamente ou use /publish-resource para publicá-lo"
        )

    files.ensure_dir(type_dir)
    content = tmpl_file.read_text()
    for placeholder in _PLACEHOLDERS:
        content = content.replace(placeholder, name)
    dest.write_text(content)

    fields = {"name": name, "created": today, "project": project_name, "source": "local"}
    if author:
        fields["author"] = author
    frontmatter.write(dest, fields)

    print(f"  [ok] Criado: {dest}")
    print(f"  -> Preencha os placeholders e use /publish-resource quando estiver pronto")


def _build_plugin(hub: Path, dest_dir: Path, name: str, project_name: str, today: str, author: str = "") -> None:
    tmpl_file = hub / "build/04-plugins/_template/plugin.json"
    if not tmpl_file.exists():
        raise FileNotFoundError(f"Template não encontrado: {tmpl_file}")

    type_dir = config.dest_dir_for_type(dest_dir, "plugin")
    dest = type_dir / f"{name}.json"

    if dest.exists():
        raise FileExistsError(f"Recurso já existe: {dest}")

    files.ensure_dir(type_dir)
    data = json.loads(tmpl_file.read_text())
    if data.get("name") == "plugin-name":
        data["name"] = name
    data["project"] = project_name
    data["created"] = today
    data["source"] = "local"
    if author:
        data["author"] = author

    dest.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print(f"  [ok] Criado: {dest}")


def _build_hook(hub: Path, dest_dir: Path, name: str, project_name: str, today: str, author: str = "") -> None:
    tmpl_dir = hub / "build/02-hooks/_template"
    hook_dest_dir = dest_dir / "hooks" / name

    if hook_dest_dir.exists():
        raise FileExistsError(
            f"Hook já existe: {hook_dest_dir} — edite-o diretamente ou use /publish-resource para publicá-lo"
        )

    hook_dest_dir.mkdir(parents=True)

    data = json.loads((tmpl_dir / "hook.json").read_text())
    data["name"] = name
    data["project"] = project_name
    data["created"] = today
    data["source"] = "local"
    if author:
        data["author"] = author
    (hook_dest_dir / "hook.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")

    shutil.copy2(tmpl_dir / "events" / "pre-tool-use.sh", hook_dest_dir / "hook.sh")
    (hook_dest_dir / "hook.sh").chmod(0o755)

    print(f"  [ok] Criado: {hook_dest_dir}/")
    print(f"  -> Edite hook.json (evento, matcher) e hook.sh (lógica).")
    print(f"  -> Use /publish-resource hook {name} quando estiver pronto.")
