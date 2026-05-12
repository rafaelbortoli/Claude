def register(sub):
    p = sub.add_parser("setup-claude", help="Inicializa estrutura .claude/ em um novo projeto")
    p.add_argument("--path", required=True, help="Caminho da pasta do projeto")
    p.add_argument("--name", required=True, help="Nome do projeto")
    p.add_argument("--vision", default="", help="Visão geral do projeto (uma frase)")
    p.set_defaults(func=run)


def run(args):
    raise NotImplementedError("setup-claude: implementação pendente (Fase 2)")
