import json
import re
import shutil
import tempfile
from datetime import date
from pathlib import Path

from cli import config
from cli.utils import files, frontmatter


def register(sub):
    p = sub.add_parser("install-resource", help="Instala um recurso do hub no projeto atual")
    p.add_argument("--type", required=True, dest="resource_type",
                   help="Tipo do recurso (skill, agent, hook, command, plugin, instruction)")
    p.add_argument("--name", required=True, help="Nome do recurso")
    p.add_argument("--dest", default="", help="Diretório .claude/ destino (padrão: .claude/ do projeto atual)")
    p.set_defaults(func=run)


def run(args):
    hub = config.hub_dir()
    dest_dir = Path(args.dest).expanduser().resolve() if args.dest else Path.cwd() / ".claude"
    resource_type = args.resource_type
    name = args.name

    project_name = _get_project_name(dest_dir)

    dispatch = {
        "skill":       _install_md_resource,
        "agent":       _install_md_resource,
        "command":     _install_md_resource,
        "hook":        _install_hook,
        "plugin":      _install_plugin,
        "instruction": _install_instruction,
    }
    if resource_type not in dispatch:
        raise ValueError(f"Tipo desconhecido: {resource_type}. Use: skill, agent, hook, command, plugin, instruction")

    if resource_type in ("skill", "agent", "command"):
        dispatch[resource_type](hub, dest_dir, resource_type, name, project_name)
    else:
        dispatch[resource_type](hub, dest_dir, name, project_name)


def _get_project_name(dest_dir: Path) -> str:
    claude_md = dest_dir / "CLAUDE.md"
    if claude_md.exists():
        return frontmatter.read(claude_md).get("name", "")
    return ""


def _hub_resources_dir(hub: Path) -> Path:
    return hub / "hub"


def _install_md_resource(hub: Path, dest_dir: Path, resource_type: str, name: str, project_name: str) -> None:
    hub_res = _hub_resources_dir(hub)
    src = hub_res / f"{resource_type}s" / name / f"{resource_type}.md"

    if not src.exists():
        raise FileNotFoundError(f"Recurso não encontrado no hub: {src}")

    version = frontmatter.read(src).get("version", "0.0.0")
    type_dir = config.dest_dir_for_type(dest_dir, resource_type)
    dest = type_dir / f"{name}.md"

    tmp = Path(tempfile.mktemp(suffix=".md"))
    try:
        shutil.copy2(src, tmp)
        frontmatter.inject(tmp, project_name, f"hub/{resource_type}s/{name}@{version}")
        files.ensure_dir(type_dir)
        if dest.exists():
            v_dest = frontmatter.read(dest).get("version", "?")
            shutil.copy2(tmp, dest)
            print(f"  [ok] Atualizado: {dest} ({v_dest} -> {version})")
        else:
            shutil.copy2(tmp, dest)
            print(f"  [ok] Instalado: {dest}")
    finally:
        tmp.unlink(missing_ok=True)


def _install_hook(hub: Path, dest_dir: Path, name: str, project_name: str) -> None:
    hook_src_dir = _hub_resources_dir(hub) / "hooks" / name
    hook_json_src = hook_src_dir / "hook.json"
    hook_sh_src = hook_src_dir / "hook.sh"

    if not hook_src_dir.is_dir():
        raise FileNotFoundError(f"Hook não encontrado: {hook_src_dir}")
    if not hook_json_src.exists():
        raise FileNotFoundError(f"hook.json ausente: {hook_json_src}")
    if not hook_sh_src.exists():
        raise FileNotFoundError(f"hook.sh ausente: {hook_sh_src}")

    with open(hook_json_src) as f:
        hook_meta = json.load(f)
    version = hook_meta.get("version", "0.0.0")

    dest_hook_dir = dest_dir / "hooks" / name
    if dest_hook_dir.exists():
        with open(dest_hook_dir / "hook.json") as f:
            v_dest = json.load(f).get("version", "?")
        print(f"  -> Hook {name} já instalado ({v_dest} -> {version}) — sobrescrevendo")

    dest_hook_dir.mkdir(parents=True, exist_ok=True)

    hook_meta["project"] = project_name
    hook_meta["source"] = f"hub/hooks/{name}@{version}"
    hook_meta["created"] = str(date.today())
    (dest_hook_dir / "hook.json").write_text(json.dumps(hook_meta, indent=2, ensure_ascii=False) + "\n")

    shutil.copy2(hook_sh_src, dest_hook_dir / "hook.sh")
    (dest_hook_dir / "hook.sh").chmod(0o755)
    print(f"  [ok] Hook instalado: {dest_hook_dir}/")

    settings_file = dest_dir / "settings.json"
    _update_settings(settings_file, name, dest_hook_dir / "hook.json")


def _update_settings(settings_file: Path, hook_name: str, hook_json_file: Path) -> None:
    try:
        with open(settings_file) as f:
            settings = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        settings = {}

    with open(hook_json_file) as f:
        hook_meta = json.load(f)

    event = hook_meta.get("event", "PostToolUse")
    matcher = hook_meta.get("matcher", {}).get("tool", "*")
    new_hook = {"type": "command", "command": f"bash .claude/hooks/{hook_name}/hook.sh"}
    new_block = {"matcher": matcher, "hooks": [new_hook]}

    hooks = settings.setdefault("hooks", {})
    event_list = hooks.setdefault(event, [])

    for block in event_list:
        for h in block.get("hooks", []):
            if h.get("command") == new_hook["command"]:
                print(f"  -> Hook já presente em settings.json — mantido")
                return

    event_list.append(new_block)
    settings_file.write_text(json.dumps(settings, indent=2, ensure_ascii=False) + "\n")
    print(f"  [ok] settings.json atualizado")


def _install_plugin(hub: Path, dest_dir: Path, name: str, project_name: str) -> None:
    plugin_json = _hub_resources_dir(hub) / "plugins" / name / "plugin.json"
    if not plugin_json.exists():
        raise FileNotFoundError(f"Plugin não encontrado: {plugin_json}")

    with open(plugin_json) as f:
        manifest = json.load(f)

    print(f"  -> Lendo manifesto: {plugin_json}")

    for resource_name in manifest.get("skills", []):
        _install_md_resource(hub, dest_dir, "skill", resource_name, project_name)
    for resource_name in manifest.get("agents", []):
        _install_md_resource(hub, dest_dir, "agent", resource_name, project_name)
    for resource_name in manifest.get("hooks", []):
        _install_hook(hub, dest_dir, resource_name, project_name)
    for resource_name in manifest.get("commands", []):
        _install_md_resource(hub, dest_dir, "command", resource_name, project_name)

    version = manifest.get("version", "0.0.0")
    plugin_record = {"name": name, "version": version, "installed": str(date.today())}
    plugins_dir = dest_dir / "plugins"
    plugins_dir.mkdir(exist_ok=True)
    (plugins_dir / f"{name}.json").write_text(json.dumps(plugin_record, indent=2) + "\n")
    print(f"  [ok] Plugin registrado: .claude/plugins/{name}.json")


def _install_instruction(hub: Path, dest_dir: Path, name: str, project_name: str) -> None:
    src = _hub_resources_dir(hub) / "instructions" / f"{name}.md"
    claude_md = dest_dir / "CLAUDE.md"

    if not src.exists():
        raise FileNotFoundError(f"Instruction não encontrada: {src}")
    if not claude_md.exists():
        raise FileNotFoundError(f"CLAUDE.md não encontrado — execute /setup-claude primeiro")

    marker = f"<!-- instruction: {name} -->"
    if marker in claude_md.read_text():
        print(f"  -> Instruction '{name}' já presente em CLAUDE.md — mantida")
        return

    content = src.read_text()
    m = re.match(r'^---\n.*?\n---\n', content, re.DOTALL)
    fragment = content[m.end():] if m else content

    with claude_md.open("a") as f:
        f.write(f"\n{marker}\n" + fragment.strip() + "\n")

    print(f"  [ok] Instruction '{name}' adicionada ao CLAUDE.md")
