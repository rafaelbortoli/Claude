import json
from pathlib import Path


def register(sub):
    p = sub.add_parser("setup-claude", help="Prepara contexto para configurar o CLAUDE.md de um projeto")
    p.add_argument("--prepare", action="store_true",
                   help="Retorna JSON com caminho atual e projetos irmãos detectados")
    p.add_argument("--path", default="", help="Diretório base (padrão: cwd)")
    p.set_defaults(func=run)


def run(args):
    if args.prepare:
        try:
            base = Path(args.path).expanduser().resolve() if args.path else Path.cwd()
            result = _prepare(base)
            print(json.dumps(result, ensure_ascii=False))
        except Exception as e:
            print(json.dumps({"error": str(e)}, ensure_ascii=False))
        return


def _prepare(base: Path) -> dict:
    """Detecta caminho atual e projetos irmãos com .claude/CLAUDE.md."""
    candidates = _find_candidate_paths(base)
    return {
        "context": {
            "current_path": str(base),
        },
        "suggestions": {
            "project_paths": candidates,
        },
    }


def _find_candidate_paths(base: Path) -> list:
    """Retorna base + até 2 pastas irmãs que contêm .claude/CLAUDE.md."""
    candidates = [str(base)]
    parent = base.parent
    for sibling in sorted(parent.iterdir()):
        if sibling == base or not sibling.is_dir():
            continue
        if (sibling / ".claude" / "CLAUDE.md").exists():
            candidates.append(str(sibling))
        if len(candidates) == 3:
            break
    return candidates
