import shutil
from pathlib import Path

from cli.utils import frontmatter


def register(sub):
    p = sub.add_parser("claude-start", help="Setup global do Claude Code na máquina")
    p.set_defaults(func=run)


def run(args):
    hub = Path(__file__).parent.parent.parent
    dest = Path.home() / ".claude"

    _check_sources(hub)
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "commands").mkdir(exist_ok=True)

    _set_hub_path(hub, dest)
    _copy_global_files(hub, dest)
    _install_commands(hub, dest)


def _check_sources(hub: Path) -> None:
    for f in ["global/CLAUDE.md", "global/settings.json"]:
        if not (hub / f).exists():
            raise FileNotFoundError(f"Não encontrado: {hub / f}")


def _set_hub_path(hub: Path, dest: Path) -> None:
    hub_path_file = dest / "hub-path"
    if hub_path_file.exists():
        existing = hub_path_file.read_text().strip()
        if existing != str(hub):
            hub_path_file.write_text(str(hub))
            print(f"  [ok] hub-path atualizado: {existing} -> {hub}")
        else:
            print(f"  -> hub-path já correto — mantido")
    else:
        hub_path_file.write_text(str(hub))
        print(f"  [ok] hub-path salvo: {hub_path_file}")


def _copy_global_files(hub: Path, dest: Path) -> None:
    for f in ["CLAUDE.md", "settings.json"]:
        src = hub / "global" / f
        target = dest / f
        if target.exists():
            if f == "CLAUDE.md":
                v_hub = frontmatter.read(src).get("version", "")
                v_local = frontmatter.read(target).get("version", "")
                if v_hub and v_local and v_hub != v_local:
                    print(f"  [aviso] CLAUDE.md desatualizado — local: {v_local}, hub: {v_hub} (edite manualmente se necessário)")
                else:
                    print(f"  -> CLAUDE.md já existe — mantido")
            else:
                print(f"  -> {f} já existe — mantido")
        else:
            shutil.copy2(src, target)
            print(f"  [ok] {f} instalado: {target}")


def _install_commands(hub: Path, dest: Path) -> None:
    commands_dir = hub / "hub" / "commands"
    if not commands_dir.exists():
        return
    for cmd_dir in sorted(commands_dir.iterdir()):
        if not cmd_dir.is_dir():
            continue
        cmd_src = cmd_dir / "command.md"
        if not cmd_src.exists():
            continue
        cmd_name = cmd_dir.name
        cmd_dest = dest / "commands" / f"{cmd_name}.md"
        if cmd_dest.exists():
            v_hub = frontmatter.read(cmd_src).get("version", "?")
            v_local = frontmatter.read(cmd_dest).get("version", "?")
            content_changed = cmd_src.read_text() != cmd_dest.read_text()
            if v_hub != v_local or content_changed:
                shutil.copy2(cmd_src, cmd_dest)
                print(f"  [ok] Comando atualizado: {cmd_name} ({v_local} -> {v_hub})")
            else:
                print(f"  -> Comando já atualizado: {cmd_name} ({v_local})")
        else:
            shutil.copy2(cmd_src, cmd_dest)
            print(f"  [ok] Comando instalado: {cmd_name}")
