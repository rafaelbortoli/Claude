def register(sub):
    p = sub.add_parser("claude-start", help="Setup global do Claude Code na máquina")
    p.set_defaults(func=run)


def run(args):
    raise NotImplementedError("claude-start: implementação pendente (Fase 2)")
