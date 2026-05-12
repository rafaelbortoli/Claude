def register(sub):
    p = sub.add_parser("build-resource", help="Cria um novo recurso a partir do template")
    p.add_argument("--type", required=True, help="Tipo do recurso (skill, agent, hook, command, plugin)")
    p.add_argument("--name", required=True, help="Nome do recurso")
    p.add_argument("--dest", default="", help="Diretório destino (padrão: .claude/ do projeto atual)")
    p.set_defaults(func=run)


def run(args):
    raise NotImplementedError("build-resource: implementação pendente (Fase 2)")
