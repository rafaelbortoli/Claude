import json
import shutil
from pathlib import Path

from cli.utils import files
from cli.utils.logger import log
from cli.commands.remove_resource import purge_expired
from cli.commands.install_resource import _update_settings, _create_proxy


def register(sub):
    p = sub.add_parser("restore-resource", help="Restaura um recurso da lixeira")
    p.add_argument("--type", required=True, dest="resource_type",
                   help="Tipo do recurso (skill, agent, command, hook, plugin, instruction)")
    p.add_argument("--name", required=True, help="Nome do recurso")
    p.add_argument("--dest", default="", help="Diretório .claude/ do projeto (padrão: .claude/ do cwd)")
    p.set_defaults(func=run)


def run(args):
    dest_dir = Path(args.dest).expanduser().resolve() if args.dest else Path.cwd() / ".claude"
    resource_type = args.resource_type
    name = args.name

    purge_expired(dest_dir)

    if resource_type in ("skill", "agent"):
        _restore_md_resource(dest_dir, resource_type, name)
    elif resource_type == "command":
        _restore_command(dest_dir, name)
    elif resource_type == "hook":
        _restore_hook(dest_dir, name)
    elif resource_type == "plugin":
        _restore_plugin(dest_dir, name)
    elif resource_type == "instruction":
        _restore_instruction(dest_dir, name)
    else:
        raise ValueError(f"Tipo inválido: {resource_type}")

    log(dest_dir, "resource.restored", {"type": resource_type, "name": name})
    print(f"  [ok] '{name}' restaurado com sucesso")


def _restore_md_resource(dest_dir: Path, resource_type: str, name: str) -> None:
    trash_item_dir = dest_dir / "trash" / resource_type / name
    trash_file = trash_item_dir / f"{name}.md"
    if not trash_file.exists():
        raise FileNotFoundError(f"Recurso não encontrado na lixeira: {trash_item_dir}")

    dest = dest_dir / f"{resource_type}s" / f"{name}.md"
    files.ensure_dir(dest.parent)
    shutil.move(str(trash_file), dest)

    _create_proxy(dest_dir, resource_type, name)
    _cleanup_trash_dir(trash_item_dir)
    print(f"  [ok] {resource_type.capitalize()} '{name}' restaurado")


def _restore_command(dest_dir: Path, name: str) -> None:
    trash_item_dir = dest_dir / "trash" / "command" / name
    trash_file = trash_item_dir / f"{name}.md"
    if not trash_file.exists():
        raise FileNotFoundError(f"Command não encontrado na lixeira")

    dest = dest_dir / "commands" / f"{name}.md"
    files.ensure_dir(dest.parent)
    shutil.move(str(trash_file), dest)
    _cleanup_trash_dir(trash_item_dir)
    print(f"  [ok] Command '{name}' restaurado")


def _restore_hook(dest_dir: Path, name: str) -> None:
    trash_item_dir = dest_dir / "trash" / "hook" / name
    if not trash_item_dir.exists():
        raise FileNotFoundError(f"Hook não encontrado na lixeira")

    hook_dest_dir = dest_dir / "hooks" / name
    hook_dest_dir.mkdir(parents=True, exist_ok=True)

    for f in trash_item_dir.iterdir():
        if f.name == "_trash.json":
            continue
        shutil.move(str(f), hook_dest_dir / f.name)

    hook_json = hook_dest_dir / "hook.json"
    if hook_json.exists():
        _update_settings(dest_dir / "settings.json", name, hook_json)

    _cleanup_trash_dir(trash_item_dir)
    print(f"  [ok] Hook '{name}' restaurado")


def _restore_plugin(dest_dir: Path, name: str) -> None:
    trash_item_dir = dest_dir / "trash" / "plugin" / name
    trash_json_file = trash_item_dir / "_trash.json"
    plugin_file = trash_item_dir / f"{name}.json"

    if not plugin_file.exists():
        raise FileNotFoundError(f"Plugin não encontrado na lixeira")

    with open(trash_json_file) as f:
        meta = json.load(f)

    for sub in meta.get("sub_resources", []):
        sub_type = sub["type"]
        sub_name = sub["name"]
        sub_trash = dest_dir / "trash" / sub_type / sub_name
        if not sub_trash.exists():
            print(f"  [aviso] Sub-recurso não encontrado na lixeira: {sub_type}/{sub_name} — ignorado")
            continue
        try:
            if sub_type in ("skill", "agent"):
                _restore_md_resource(dest_dir, sub_type, sub_name)
            elif sub_type == "hook":
                _restore_hook(dest_dir, sub_name)
            elif sub_type == "command":
                _restore_command(dest_dir, sub_name)
        except Exception as e:
            print(f"  [aviso] Erro ao restaurar {sub_type}/{sub_name}: {e}")

    plugins_dir = dest_dir / "plugins"
    plugins_dir.mkdir(exist_ok=True)
    shutil.move(str(plugin_file), plugins_dir / f"{name}.json")
    _cleanup_trash_dir(trash_item_dir)
    print(f"  [ok] Plugin '{name}' e sub-recursos restaurados")


def _restore_instruction(dest_dir: Path, name: str) -> None:
    trash_item_dir = dest_dir / "trash" / "instruction" / name
    content_file = trash_item_dir / "content.md"
    if not content_file.exists():
        raise FileNotFoundError(f"Instruction não encontrada na lixeira")

    claude_md = dest_dir / "CLAUDE.md"
    if not claude_md.exists():
        raise FileNotFoundError(f"CLAUDE.md não encontrado")

    content = content_file.read_text()
    with claude_md.open("a") as f:
        f.write(f"\n{content}\n")

    _cleanup_trash_dir(trash_item_dir)
    print(f"  [ok] Instruction '{name}' restaurada no CLAUDE.md")


def _cleanup_trash_dir(trash_item_dir: Path) -> None:
    trash_json = trash_item_dir / "_trash.json"
    if trash_json.exists():
        trash_json.unlink()
    try:
        trash_item_dir.rmdir()
    except OSError:
        pass
