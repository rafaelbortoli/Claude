import json
import re
import shutil
from datetime import date, timedelta
from pathlib import Path

from cli import config
from cli.utils import files, frontmatter
from cli.utils.files import git_author
from cli.utils.logger import log

_EXPIRY_DAYS = 30


def register(sub):
    p = sub.add_parser("remove-resource", help="Move um recurso do projeto para a lixeira")
    p.add_argument("--type", required=True, dest="resource_type",
                   help="Tipo do recurso (skill, agent, command, hook, plugin, instruction)")
    p.add_argument("--name", required=True, help="Nome do recurso")
    p.add_argument("--dest", default="", help="Diretório .claude/ do projeto (padrão: .claude/ do cwd)")
    p.set_defaults(func=run)


def run(args):
    dest_dir = Path(args.dest).expanduser().resolve() if args.dest else Path.cwd() / ".claude"
    hub = config.hub_dir()
    resource_type = args.resource_type
    name = args.name

    purge_expired(dest_dir)

    valid = ("skill", "agent", "command", "hook", "plugin", "instruction")
    if resource_type not in valid:
        raise ValueError(f"Tipo inválido: {resource_type}. Válidos: {', '.join(valid)}")

    if resource_type in ("skill", "agent"):
        _remove_md_resource(dest_dir, resource_type, name)
    elif resource_type == "command":
        _remove_command(dest_dir, name)
    elif resource_type == "hook":
        _remove_hook(dest_dir, name)
    elif resource_type == "plugin":
        _remove_plugin(hub, dest_dir, name)
    elif resource_type == "instruction":
        _remove_instruction(dest_dir, name)

    expires = date.today() + timedelta(days=_EXPIRY_DAYS)
    log(dest_dir, "resource.removed", {
        "type":       resource_type,
        "name":       name,
        "expires_at": str(expires),
    })
    print(f"  [ok] '{name}' movido para a lixeira — remoção permanente em {_EXPIRY_DAYS} dias ({expires})")


def purge_expired(dest_dir: Path) -> None:
    trash_dir = dest_dir / "trash"
    if not trash_dir.exists():
        return
    today = date.today()
    for trash_json in list(trash_dir.glob("*/*/_trash.json")):
        try:
            with open(trash_json) as f:
                meta = json.load(f)
            expires = date.fromisoformat(meta.get("expires_at", "9999-12-31"))
            if expires <= today:
                item_dir = trash_json.parent
                shutil.rmtree(item_dir)
                log(dest_dir, "resource.purged", {
                    "type": meta.get("type"),
                    "name": meta.get("name"),
                })
                print(f"  [ok] Removido permanentemente: {meta.get('name')} ({meta.get('type')})")
        except Exception:
            pass


def _write_trash_meta(trash_item_dir: Path, resource_type: str, name: str, extra: dict = None) -> None:
    meta = {
        "type":       resource_type,
        "name":       name,
        "removed_at": str(date.today()),
        "expires_at": str(date.today() + timedelta(days=_EXPIRY_DAYS)),
        "removed_by": git_author(),
    }
    if extra:
        meta.update(extra)
    (trash_item_dir / "_trash.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False) + "\n"
    )


def _remove_md_resource(dest_dir: Path, resource_type: str, name: str) -> None:
    src = dest_dir / f"{resource_type}s" / f"{name}.md"
    if not src.exists():
        raise FileNotFoundError(f"Recurso não encontrado: {src}")

    fm = frontmatter.read(src)
    locked = fm.get("locked", "").lower() == "true"

    trash_item_dir = dest_dir / "trash" / resource_type / name
    trash_item_dir.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), trash_item_dir / f"{name}.md")

    proxy = dest_dir / "commands" / f"{name}.md"
    proxy_removed = False
    if proxy.exists():
        proxy.unlink()
        proxy_removed = True

    _write_trash_meta(trash_item_dir, resource_type, name, {
        "locked":        locked,
        "proxy_removed": proxy_removed,
    })
    print(f"  [ok] {resource_type.capitalize()} '{name}' movido para a lixeira")
    if proxy_removed:
        print(f"  [ok] Proxy /{name} removido")


def _remove_command(dest_dir: Path, name: str) -> None:
    src = dest_dir / "commands" / f"{name}.md"
    if not src.exists():
        raise FileNotFoundError(f"Command não encontrado: {src}")

    trash_item_dir = dest_dir / "trash" / "command" / name
    trash_item_dir.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), trash_item_dir / f"{name}.md")
    _write_trash_meta(trash_item_dir, "command", name)
    print(f"  [ok] Command '{name}' movido para a lixeira")


def _remove_hook(dest_dir: Path, name: str) -> None:
    hook_dir = dest_dir / "hooks" / name
    if not hook_dir.exists():
        raise FileNotFoundError(f"Hook não encontrado: {hook_dir}")

    trash_item_dir = dest_dir / "trash" / "hook" / name
    trash_item_dir.mkdir(parents=True, exist_ok=True)

    for f in hook_dir.iterdir():
        shutil.move(str(f), trash_item_dir / f.name)
    hook_dir.rmdir()

    _write_trash_meta(trash_item_dir, "hook", name)
    _remove_from_settings(dest_dir / "settings.json", name)
    print(f"  [ok] Hook '{name}' movido para a lixeira")


def _remove_from_settings(settings_file: Path, hook_name: str) -> None:
    if not settings_file.exists():
        return
    try:
        with open(settings_file) as f:
            settings = json.load(f)
    except (json.JSONDecodeError, OSError):
        return

    command_str = f"bash .claude/hooks/{hook_name}/hook.sh"
    changed = False
    for event, blocks in settings.get("hooks", {}).items():
        new_blocks = []
        for block in blocks:
            new_hooks = [h for h in block.get("hooks", []) if h.get("command") != command_str]
            if len(new_hooks) != len(block.get("hooks", [])):
                changed = True
            if new_hooks:
                new_blocks.append({**block, "hooks": new_hooks})
            else:
                changed = True
        settings["hooks"][event] = new_blocks

    if changed:
        settings_file.write_text(json.dumps(settings, indent=2, ensure_ascii=False) + "\n")
        print(f"  [ok] settings.json atualizado")


def _remove_plugin(hub: Path, dest_dir: Path, name: str) -> None:
    plugin_record = dest_dir / "plugins" / f"{name}.json"
    if not plugin_record.exists():
        raise FileNotFoundError(f"Plugin não encontrado: {plugin_record}")

    hub_manifest = hub / "hub" / "plugins" / name / "plugin.json"
    removed_sub = []

    if hub_manifest.exists():
        with open(hub_manifest) as f:
            manifest = json.load(f)

        for res_name in manifest.get("skills", []):
            if (dest_dir / "skills" / f"{res_name}.md").exists():
                _remove_md_resource(dest_dir, "skill", res_name)
                removed_sub.append({"type": "skill", "name": res_name})

        for res_name in manifest.get("agents", []):
            if (dest_dir / "agents" / f"{res_name}.md").exists():
                _remove_md_resource(dest_dir, "agent", res_name)
                removed_sub.append({"type": "agent", "name": res_name})

        for res_name in manifest.get("hooks", []):
            if (dest_dir / "hooks" / res_name).exists():
                _remove_hook(dest_dir, res_name)
                removed_sub.append({"type": "hook", "name": res_name})

        for res_name in manifest.get("commands", []):
            if (dest_dir / "commands" / f"{res_name}.md").exists():
                _remove_command(dest_dir, res_name)
                removed_sub.append({"type": "command", "name": res_name})

    trash_item_dir = dest_dir / "trash" / "plugin" / name
    trash_item_dir.mkdir(parents=True, exist_ok=True)
    shutil.move(str(plugin_record), trash_item_dir / f"{name}.json")
    _write_trash_meta(trash_item_dir, "plugin", name, {"sub_resources": removed_sub})
    print(f"  [ok] Plugin '{name}' e {len(removed_sub)} sub-recurso(s) movidos para a lixeira")


def _remove_instruction(dest_dir: Path, name: str) -> None:
    claude_md = dest_dir / "CLAUDE.md"
    if not claude_md.exists():
        raise FileNotFoundError(f"CLAUDE.md não encontrado: {claude_md}")

    marker = f"<!-- instruction: {name} -->"
    content = claude_md.read_text()
    if marker not in content:
        raise ValueError(f"Instruction '{name}' não encontrada em CLAUDE.md")

    pattern = re.compile(
        rf'(\n?{re.escape(marker)}\n)(.*?)(?=\n<!-- instruction:|\Z)',
        re.DOTALL,
    )
    m = pattern.search(content)
    block_content = (m.group(1) + m.group(2)) if m else f"\n{marker}\n"

    trash_item_dir = dest_dir / "trash" / "instruction" / name
    trash_item_dir.mkdir(parents=True, exist_ok=True)
    (trash_item_dir / "content.md").write_text(block_content)
    _write_trash_meta(trash_item_dir, "instruction", name)

    new_content = pattern.sub("", content)
    claude_md.write_text(new_content)
    print(f"  [ok] Instruction '{name}' removida do CLAUDE.md")
