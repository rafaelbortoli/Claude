import json
import re
import shutil
from datetime import date
from pathlib import Path

from cli import config
from cli.utils import files, frontmatter
from cli.utils.files import git_author
from cli.utils.logger import log
from cli.commands.install_resource import _install_plugin, _install_instruction

_FRAGMENT_ORDER = [
    "language.md",
    "communication.md",
    "execution.md",
    "anti-hallucination.md",
    "tools.md",
    "frontmatter.md",
]

_DESIGN_DIRS = [
    ("design/01-branding/01-research", "Pesquisa de marca",
     "Resultados de pesquisa e discovery de marca: benchmarking, moodboard e insights."),
    ("design/01-branding/02-plan", "Estratégia de marca",
     "Estratégia da marca: posicionamento, voz, tom e diretrizes."),
    ("design/01-branding/03-create", "Assets de marca",
     "Todos os assets produzidos: tokens de design, expressão visual, expressão verbal e direção criativa."),
    ("design/02-interface/01-research", "Pesquisa de interface",
     "Pesquisa com usuários, benchmarking de interfaces e insights de usabilidade."),
    ("design/02-interface/02-uxui", "UX/UI",
     "Wireframes, protótipos e interfaces finais do produto."),
    ("design/02-interface/03-resources", "Recursos de interface",
     "Design system, componentes, tokens e assets de interface."),
    ("design/03-product-design/01-discovery", "Discovery",
     "Pesquisa exploratória, oportunidades e definição do problema."),
    ("design/03-product-design/02-ux-research", "UX Research",
     "Pesquisa com usuários, personas, jornadas e testes de usabilidade."),
    ("design/03-product-design/03-ideation", "Ideação",
     "Exploração de soluções, conceitos e alternativas de design."),
    ("design/03-product-design/04-prototype", "Prototipação",
     "Protótipos de baixa e alta fidelidade para validação."),
    ("design/03-product-design/05-development", "Desenvolvimento",
     "Especificações, handoff e acompanhamento da implementação."),
    ("design/03-product-design/06-release", "Release",
     "Entrega final, documentação e métricas pós-lançamento."),
]

_DESIGN_PARENT_READMES = [
    ("design",                  "Design",
     "Assets de marca, interface e design do produto."),
    ("design/01-branding",      "Identidade visual da marca",
     "Pesquisa, planejamento e produção dos assets de marca."),
    ("design/02-interface",     "Design de interface",
     "Pesquisa, UX/UI e recursos de interface do produto."),
    ("design/03-product-design", "Design de produto",
     "Processo completo de design estratégico do produto digital."),
]

_DEV_DIRS = [
    ("dev/00-vision",             "Visão do Produto",
     "Briefing, escopo, requisitos e decisões estratégicas do produto."),
    ("dev/01-architecture",       "Arquitetura",
     "Diagramas, decisões técnicas (ADRs) e estrutura do sistema."),
    ("dev/02-supabase",           "Supabase",
     "Migrations, schemas, Edge Functions e políticas RLS."),
    ("dev/03-app",                "App",
     "Rotas e páginas da aplicação (Next.js App Router). Componentes específicos de rota em `_components/` dentro de cada rota."),
    ("dev/04-lib",                "Lib",
     "Funções utilitárias, helpers e código compartilhado entre módulos."),
    ("dev/05-hooks",              "Hooks",
     "React hooks customizados reutilizáveis."),
    ("dev/06-components/ui",      "UI",
     "Componentes primitivos de UI: botões, inputs, modais, badges e similares."),
    ("dev/06-components/layout",  "Layout",
     "Componentes de estrutura e layout: header, sidebar, grid e wrappers."),
    ("dev/07-types",              "Types",
     "Definições de tipos TypeScript compartilhados entre módulos."),
    ("dev/08-public",             "Public",
     "Assets estáticos públicos: imagens, fontes e ícones."),
]

_DEV_PARENT_READMES = [
    ("dev",             "Dev",
     "Código-fonte e documentação técnica do produto."),
    ("dev/06-components", "Components",
     "Componentes reutilizáveis da interface, organizados por tipo."),
]


def register(sub):
    p = sub.add_parser("new-project", help="Inicializa estrutura .claude/ e pastas em um novo projeto")
    p.add_argument("--path", required=True, help="Caminho da pasta do projeto")
    p.add_argument("--name", required=True, help="Nome do projeto")
    p.add_argument("--description", default="", help="Descrição do projeto em uma frase")
    p.add_argument("--tags", default="", help="Tags do projeto separadas por vírgula (ex: saas, fintech)")
    p.add_argument("--stack", default="nextjs-supabase", help="Stack a instalar (padrão: nextjs-supabase)")
    p.set_defaults(func=run)


def run(args):
    hub = config.hub_dir()
    dest = Path(args.path).expanduser().resolve()
    claude_dir = dest / ".claude"
    today = str(date.today())

    author = git_author()

    _create_claude_dirs(claude_dir)
    _setup_claude_md(hub, claude_dir, args.name, args.description, args.tags, today, author)
    _copy_settings(hub, claude_dir)
    _create_project_folders(dest, args.name, today, author)
    _create_project_details(hub, dest, args.name, args.description, today, author)
    _apply_stack(hub, claude_dir, args.stack, args.name)

    log(claude_dir, "project.created", {
        "name":        args.name,
        "description": args.description,
        "tags":        args.tags,
        "stack":       args.stack,
        "path":        str(dest),
    })

    print(f"  [ok] Projeto '{args.name}' configurado em {dest}")


def _create_project_details(hub: Path, dest: Path, name: str, description: str, today: str, author: str = "") -> None:
    project_dir = dest / "project"
    files.ensure_dir(project_dir)

    details = project_dir / "project-details.md"
    if details.exists():
        print(f"  -> project-details.md já existe — mantido")
        return

    template = hub / "build/project/project-details.md"
    content = template.read_text()
    content = content.replace("(nome-do-projeto)", name)
    content = content.replace("(Nome do Projeto)", name)
    content = content.replace("(visao-geral)", description if description else "")
    details.write_text(content)

    fm_fields = {
        "project": name,
        "created": today,
        "updated": today,
    }
    if description:
        fm_fields["description"] = description
    if author:
        fm_fields["author"] = author
    frontmatter.write(details, fm_fields)

    print(f"  [ok] project/project-details.md criado")


def _apply_stack(hub: Path, claude_dir: Path, stack_name: str, project_name: str) -> None:
    stack_file = hub / "build" / "stacks" / stack_name / "stack.json"
    if not stack_file.exists():
        print(f"  [aviso] Stack '{stack_name}' não encontrada em {stack_file} — ignorada")
        return

    with open(stack_file) as f:
        stack = json.load(f)

    plugins = stack.get("plugins", [])
    instructions = stack.get("instructions", [])

    if not plugins and not instructions:
        print(f"  -> Stack '{stack_name}' sem recursos para instalar")
        return

    print(f"  -> Aplicando stack '{stack_name}'...")
    for name in plugins:
        _install_plugin(hub, claude_dir, name, project_name)
    for name in instructions:
        _install_instruction(hub, claude_dir, name, project_name)
    print(f"  [ok] Stack '{stack_name}' aplicada")


def _parse_tags(raw: str) -> str:
    if not raw.strip():
        return "[]"
    items = [t.strip() for t in raw.split(",") if t.strip()]
    return "[" + ", ".join(items) + "]"


def _create_claude_dirs(claude_dir: Path) -> None:
    for subdir in ["skills", "agents", "hooks", "commands", "plugins"]:
        files.ensure_dir(claude_dir / subdir)


def _setup_claude_md(hub: Path, claude_dir: Path, name: str, description: str, tags: str, today: str, author: str = "") -> None:
    claude_md = claude_dir / "CLAUDE.md"

    if claude_md.exists():
        print(f"  -> CLAUDE.md já existe — mantido (projeto já configurado)")
        return

    shutil.copy2(hub / "build/00-claude-md/project.md", claude_md)

    content = claude_md.read_text()
    content = content.replace("[NOME DO PROJETO]", name)
    content = content.replace("(descricao)", description if description else '""')
    content = content.replace("(visao-geral)", description)
    claude_md.write_text(content)

    fm_fields = {
        "name":    name,
        "status":  "stable",
        "project": name,
        "created": today,
        "updated": today,
        "tags":    _parse_tags(tags),
    }
    if description:
        fm_fields["description"] = description
    if author:
        fm_fields["author"] = author
    frontmatter.write(claude_md, fm_fields)

    _append_fragments(hub, claude_md)
    print(f"  [ok] CLAUDE.md gerado")


def _append_fragments(hub: Path, claude_md: Path) -> None:
    fragments_dir = hub / "build/00-claude-md/fragments"
    if not fragments_dir.exists():
        return
    for frag_name in _FRAGMENT_ORDER:
        frag_path = fragments_dir / frag_name
        if not frag_path.exists():
            continue
        content = frag_path.read_text()
        body = re.sub(r'^---\n.*?\n---\n', '', content, flags=re.DOTALL).strip()
        with claude_md.open("a") as f:
            f.write(f"\n---\n\n{body}\n")
    print(f"  [ok] Fragmentos incluídos")


def _copy_settings(hub: Path, claude_dir: Path) -> None:
    settings = claude_dir / "settings.json"
    if not settings.exists():
        shutil.copy2(hub / "global/settings.json", settings)
        print(f"  [ok] settings.json copiado")
    else:
        print(f"  -> settings.json já existe — mantido")


def _create_project_folders(dest: Path, project_name: str, today: str, author: str = "") -> None:
    for subpath, title, description in _DESIGN_PARENT_READMES:
        path = dest / subpath
        files.ensure_dir(path)
        _write_readme(path, title, description, project_name, today, author)

    for subpath, title, description in _DESIGN_DIRS:
        path = dest / subpath
        files.ensure_dir(path)
        _write_readme(path, title, description, project_name, today, author)

    print(f"  [ok] design/ criado")

    for subpath, title, description in _DEV_PARENT_READMES:
        path = dest / subpath
        files.ensure_dir(path)
        _write_readme(path, title, description, project_name, today, author)

    for subpath, title, description in _DEV_DIRS:
        path = dest / subpath
        files.ensure_dir(path)
        _write_readme(path, title, description, project_name, today, author)

    print(f"  [ok] dev/ criado (nextjs-supabase)")


def _write_readme(dir_path: Path, title: str, description: str, project_name: str, today: str, author: str = "") -> None:
    readme = dir_path / "README.md"
    if readme.exists():
        return
    name = dir_path.name
    readme.write_text(
        f"---\n"
        f"# about\n"
        f"name: {name}\n"
        f"type: readme\n"
        f"project: \"{project_name}\"\n"
        f"description: \"{description}\"\n"
        f"tags: []\n"
        f"\n"
        f"# history\n"
        f"author: \"{author}\"\n"
        f"created: {today}\n"
        f"status: stable\n"
        f"version: 1.0.0\n"
        f"updated: \"\"\n"
        f"\n"
        f"# system\n"
        f"scope: project\n"
        f"source: local\n"
        f"auto_load: false\n"
        f"checksum: \"\"\n"
        f"dependencies: []\n"
        f"---\n"
        f"\n"
        f"# {title}\n"
        f"\n"
        f"{description}\n"
    )
