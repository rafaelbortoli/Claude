def register(sub):
    p = sub.add_parser("install-resource", help="Instala um recurso do hub no projeto atual")
    p.add_argument("--type", required=True, help="Tipo do recurso (skill, agent, hook, command, plugin)")
    p.add_argument("--name", required=True, help="Nome do recurso")
    p.add_argument("--dest", default="", help="Diretório destino (padrão: .claude/ do projeto atual)")
    p.set_defaults(func=run)


def run(args):
    raise NotImplementedError("install-resource: implementação pendente (Fase 2)")
