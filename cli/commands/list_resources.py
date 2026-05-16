import json
import re
from datetime import date
from pathlib import Path

from cli import config
from cli.utils import frontmatter

_TYPE_PREFIX = {
    "skill":       "sk",
    "agent":       "ag",
    "hook":        "hk",
    "command":     "cmd",
    "plugin":      "pl",
    "instruction": "ins",
}


def register(sub):
    p = sub.add_parser("list-resources", help="Lista recursos do hub, do projeto ou da lixeira")
    p.add_argument("--type", default="", dest="resource_type",
                   help="Tipo do recurso (skill, agent, hook, command, plugin, instruction)")
    p.add_argument("--installed", action="store_true",
                   help="Lista recursos instalados no projeto em vez do hub")
    p.add_argument("--trash", action="store_true",
                   help="Lista recursos na lixeira do projeto")
    p.add_argument("--dest", default="",
                   help="Diretório .claude/ do projeto (padrão: .claude/ do cwd)")
    p.set_defaults(func=run)


def run(args):
    hub = config.hub_dir()
    dest_dir = Path(args.dest).expanduser().resolve() if args.dest else Path.cwd() / ".claude"
    resource_type = args.resource_type

    if args.trash:
        rows = _collect_trash(dest_dir)
        if not rows:
            print("Lixeira vazia.")
            return
        _print_trash_table(rows)
        return

    if resource_type and resource_type not in _TYPE_PREFIX:
        raise ValueError(f"Tipo inválido: {resource_type}. Válidos: {', '.join(_TYPE_PREFIX)}")

    if args.installed:
        types = [resource_type] if resource_type else list(_TYPE_PREFIX)
        found_any = False
        for t in types:
            rows = _collect_installed(dest_dir, t)
            if rows:
                found_any = True
                if not resource_type:
                    print(f"\n{t.upper()}S")
                _print_table(rows, _TYPE_PREFIX[t])
        if not found_any:
            msg = f"do tipo '{resource_type}'" if resource_type else "instalados"
            print(f"Nenhum recurso {msg} no projeto.")
        return

    if not resource_type:
        raise ValueError("--type é obrigatório ao listar recursos do hub.")

    rows = _collect_hub(hub, resource_type)
    if not rows:
        print(f"Nenhum recurso do tipo '{resource_type}' disponível no hub.")
        return
    _print_table(rows, _TYPE_PREFIX[resource_type])


def _collect_hub(hub: Path, resource_type: str) -> list[dict]:
    hub_dir = hub / "hub"
    rows = []

    if resource_type == "instruction":
        for f in sorted((hub_dir / "instructions").glob("*.md")):
            if f.name == "README.md":
                continue
            fm = frontmatter.read(f)
            rows.append({"id": fm.get("id", ""), "name": f.stem, "description": fm.get("description", "")})

    elif resource_type == "hook":
        for d in sorted((hub_dir / "hooks").iterdir()):
            if not d.is_dir():
                continue
            hook_json = d / "hook.json"
            if not hook_json.exists():
                continue
            with open(hook_json) as f:
                data = json.load(f)
            rows.append({"id": data.get("id", ""), "name": d.name, "description": data.get("description", "")})

    elif resource_type == "plugin":
        for d in sorted((hub_dir / "plugins").iterdir()):
            if not d.is_dir():
                continue
            plugin_json = d / "plugin.json"
            if not plugin_json.exists():
                continue
            with open(plugin_json) as f:
                data = json.load(f)
            rows.append({"id": data.get("id", ""), "name": d.name, "description": data.get("description", "")})

    else:
        for d in sorted((hub_dir / f"{resource_type}s").iterdir()):
            if not d.is_dir():
                continue
            md = d / f"{resource_type}.md"
            if not md.exists():
                continue
            fm = frontmatter.read(md)
            rows.append({
                "id":          fm.get("id", ""),
                "name":        d.name,
                "version":     fm.get("version", ""),
                "description": fm.get("description", ""),
            })

    return rows


def _collect_installed(dest_dir: Path, resource_type: str) -> list[dict]:
    rows = []

    if resource_type == "instruction":
        claude_md = dest_dir / "CLAUDE.md"
        if not claude_md.exists():
            return rows
        for m in re.finditer(r'<!-- instruction: (.+?) -->', claude_md.read_text()):
            rows.append({"name": m.group(1), "version": "", "description": "instrução no CLAUDE.md"})

    elif resource_type == "hook":
        folder = dest_dir / "hooks"
        if not folder.exists():
            return rows
        for d in sorted(folder.iterdir()):
            if not d.is_dir():
                continue
            hook_json = d / "hook.json"
            if not hook_json.exists():
                continue
            with open(hook_json) as f:
                data = json.load(f)
            rows.append({"name": d.name, "version": data.get("version", ""), "description": data.get("description", "")})

    elif resource_type == "plugin":
        folder = dest_dir / "plugins"
        if not folder.exists():
            return rows
        for f in sorted(folder.glob("*.json")):
            with open(f) as fp:
                data = json.load(fp)
            rows.append({"name": data.get("name", f.stem), "version": data.get("version", ""), "description": f"v{data.get('version', '?')} — instalado em {data.get('installed', '?')}"})

    elif resource_type == "command":
        folder = dest_dir / "commands"
        if not folder.exists():
            return rows
        for f in sorted(folder.glob("*.md")):
            content = f.read_text()
            # skip proxies — commands only
            if content.startswith("<!-- proxy:"):
                continue
            fm = frontmatter.read(f)
            rows.append({"name": f.stem, "version": fm.get("version", ""), "description": fm.get("description", "")})

    else:
        folder = dest_dir / f"{resource_type}s"
        if not folder.exists():
            return rows
        for f in sorted(folder.glob("*.md")):
            fm = frontmatter.read(f)
            locked = fm.get("locked", "").lower() == "true"
            desc = fm.get("description", "")
            if locked:
                desc = f"[personalizado] {desc}"
            rows.append({
                "name":        f.stem,
                "version":     fm.get("version", ""),
                "description": desc,
            })

    return rows


def _collect_trash(dest_dir: Path) -> list[dict]:
    trash_dir = dest_dir / "trash"
    if not trash_dir.exists():
        return []
    rows = []
    today = date.today()
    for trash_json in sorted(trash_dir.glob("*/*/_trash.json")):
        try:
            with open(trash_json) as f:
                meta = json.load(f)
            expires = date.fromisoformat(meta.get("expires_at", "9999-12-31"))
            days_left = (expires - today).days
            rows.append({
                "type":      meta.get("type", "?"),
                "name":      meta.get("name", "?"),
                "removed_at": meta.get("removed_at", "?"),
                "days_left": days_left,
            })
        except Exception:
            pass
    return rows


def _print_table(rows: list[dict], prefix: str) -> None:
    def _row_id(row: dict, idx: int) -> str:
        stored = row.get("id", "")
        return stored if stored else f"{prefix}-{idx+1:03d}"

    ids    = [_row_id(r, i) for i, r in enumerate(rows)]
    id_w   = max(len(rid) for rid in ids)
    name_w = max(len(r["name"]) for r in rows)
    desc_w = max((len(r["description"]) for r in rows), default=0)

    header = f"{'ID':<{id_w}}  {'Nome':<{name_w}}  Descrição"
    sep    = "-" * id_w + "  " + "-" * name_w + "  " + "-" * max(desc_w, 9)
    print(header)
    print(sep)
    for rid, row in zip(ids, rows):
        print(f"{rid:<{id_w}}  {row['name']:<{name_w}}  {row['description']}")


def _print_trash_table(rows: list[dict]) -> None:
    counter = {}
    tagged = []
    for row in rows:
        t = row["type"]
        prefix = _TYPE_PREFIX.get(t, t[:3])
        counter[prefix] = counter.get(prefix, 0) + 1
        rid = f"{prefix}-{counter[prefix]:03d}"
        tagged.append({**row, "id": rid})

    id_w      = max(len(r["id"]) for r in tagged)
    type_w    = max(len(r["type"]) for r in tagged)
    name_w    = max(len(r["name"]) for r in tagged)
    date_w    = 10
    days_w    = len("Dias restantes")

    header = f"{'ID':<{id_w}}  {'Tipo':<{type_w}}  {'Nome':<{name_w}}  {'Removido em':<{date_w}}  Dias restantes"
    sep    = "-"*id_w + "  " + "-"*type_w + "  " + "-"*name_w + "  " + "-"*date_w + "  " + "-"*days_w
    print(header)
    print(sep)
    for r in tagged:
        print(f"{r['id']:<{id_w}}  {r['type']:<{type_w}}  {r['name']:<{name_w}}  {r['removed_at']:<{date_w}}  {r['days_left']}")
