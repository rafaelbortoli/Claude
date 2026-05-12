import re
import shutil
from datetime import date
from pathlib import Path

from cli import config
from cli.utils import files, frontmatter

_FRAGMENT_ORDER = [
    "language.md",
    "communication.md",
    "execution.md",
    "anti-hallucination.md",
    "tools.md",
    "frontmatter.md",
]

_DEFAULT_STACK = "nextjs-supabase-vercel-claude"

_DESIGN_DIRS = [
    ("design/01-branding/research", "Pesquisa de marca",
     "Resultados de pesquisa e discovery de marca: benchmarking, moodboard e insights."),
    ("design/01-branding/plan", "Estratégia de marca",
     "Estratégia da marca: posicionamento, voz, tom e diretrizes."),
    ("design/01-branding/create", "Assets de marca",
     "Todos os assets produzidos: tokens de design, expressão visual, expressão verbal e direção criativa."),
    ("design/02-product/discovery", "Discovery de produto",
     "Pesquisa com usuários, personas, jornadas e definição de requisitos."),
    ("design/02-product/ux-ui", "UX/UI",
     "Wireframes, protótipos e interfaces finais do produto."),
]

_DESIGN_PARENT_READMES = [
    ("design",             "Design",
     "Assets de marca e design do produto."),
    ("design/01-branding", "Identidade visual da marca",
     "Pesquisa, planejamento e produção dos assets de marca."),
    ("design/02-product",  "Design do produto digital",
     "Discovery com usuários e design de interface do produto."),
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
    p = sub.add_parser("setup-claude", help="Inicializa estrutura .claude/ em um novo projeto")
    p.add_argument("--path", required=True, help="Caminho da pasta do projeto")
    p.add_argument("--name", required=True, help="Nome do projeto")
    p.add_argument("--vision", default="", help="Visão geral do projeto (uma frase)")
    p.add_argument("--stack", default=_DEFAULT_STACK, help="Stack do projeto")
    p.set_defaults(func=run)


def run(args):
    hub = config.hub_dir()
    dest = Path(args.path).expanduser().resolve()
    claude_dir = dest / ".claude"
    today = str(date.today())

    _create_claude_dirs(claude_dir)
    _setup_claude_md(hub, claude_dir, args.name, args.vision, args.stack, today)
    _copy_settings(hub, claude_dir)
    _create_project_folders(dest, today)

    print(f"  [ok] Projeto '{args.name}' configurado em {dest}")


def _create_claude_dirs(claude_dir: Path) -> None:
    for subdir in ["skills", "agents", "hooks", "commands", "plugins"]:
        files.ensure_dir(claude_dir / subdir)


def _setup_claude_md(hub: Path, claude_dir: Path, name: str, vision: str, stack: str, today: str) -> None:
    claude_md = claude_dir / "CLAUDE.md"

    if claude_md.exists():
        print(f"  -> CLAUDE.md já existe — mantido (projeto já configurado)")
        return

    shutil.copy2(hub / "build/00-claude-md/project.md", claude_md)

    content = claude_md.read_text()
    content = content.replace("[NOME DO PROJETO]", name)
    if vision:
        content = content.replace("(preencher)", vision, 1)
    content = content.replace("(preencher)", '""')
    claude_md.write_text(content)

    frontmatter.write(claude_md, {
        "name":    name,
        "status":  "stable",
        "project": name,
        "created": today,
        "updated": today,
        "tags":    f"[{stack}]",
        "stack":   stack,
    })

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


def _create_project_folders(dest: Path, today: str) -> None:
    for subpath, title, description in _DESIGN_PARENT_READMES:
        path = dest / subpath
        files.ensure_dir(path)
        _write_readme(path, title, description, today)

    for subpath, title, description in _DESIGN_DIRS:
        path = dest / subpath
        files.ensure_dir(path)
        _write_readme(path, title, description, today)

    print(f"  [ok] design/ criado")

    for subpath, title, description in _DEV_PARENT_READMES:
        path = dest / subpath
        files.ensure_dir(path)
        _write_readme(path, title, description, today)

    for subpath, title, description in _DEV_DIRS:
        path = dest / subpath
        files.ensure_dir(path)
        _write_readme(path, title, description, today)

    print(f"  [ok] dev/ criado (nextjs-supabase)")


def _write_readme(dir_path: Path, title: str, description: str, today: str) -> None:
    readme = dir_path / "README.md"
    if readme.exists():
        return
    name = dir_path.name
    readme.write_text(
        f"---\n"
        f"# about\n"
        f"name: {name}\n"
        f"type: readme\n"
        f"project: \"\"\n"
        f"description: {description}\n"
        f"tags: []\n"
        f"\n"
        f"# history\n"
        f"author: \"\"\n"
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
