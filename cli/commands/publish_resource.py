def register(sub):
    p = sub.add_parser("publish-resource", help="Publica um recurso do projeto no hub")
    p.add_argument("--type", required=True, help="Tipo do recurso (skill, agent, hook, command, plugin)")
    p.add_argument("--name", required=True, help="Nome do recurso")
    p.add_argument("--src", default="", help="Diretório fonte (padrão: .claude/ do projeto atual)")
    p.set_defaults(func=run)


def run(args):
    raise NotImplementedError("publish-resource: implementação pendente (Fase 2)")
