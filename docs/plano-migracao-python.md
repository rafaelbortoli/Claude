---
title: Plano de Migração — Markdown para Python
type: doc
status: draft
created: 2026-05-12
---

# Plano de Migração: Markdown → Python

## 1. Motivação

O sistema atual delega lógica operacional a instruções em Markdown que Claude interpreta em tempo de execução. Isso cria um ponto de falha não determinístico: a mesma instrução pode ser seguida de forma diferente dependendo do contexto, do histórico de conversa e do estado interno do modelo.

**O problema não é o Claude — é o tipo de tarefa.**

Claude é excelente para raciocínio, geração e decisão. É ruim como executor confiável de sequências exatas de passos. Python é o oposto: executa exatamente o que foi escrito, sem variação.

| Dimensão | Instrução em Markdown | Código Python |
|---|---|---|
| Confiabilidade | Probabilística | Determinística |
| Testabilidade | Não testável | Testável com `pytest` |
| Rastreabilidade | Nenhuma | Stack trace, logs |
| Manutenção | Editar texto | Editar código |
| Reutilização | Copiar texto | Importar módulo |
| Validação de input | Depende de Claude | Validação em runtime |

---

## 2. Princípio de Separação

A migração não é "substituir tudo por Python". É separar responsabilidades:

```
┌─────────────────────────────────────────────────────────────┐
│                    RESPONSABILIDADE DE CLAUDE                │
│                                                             │
│  • Entender a intenção do usuário                           │
│  • Fazer perguntas e coletar respostas                      │
│  • Decidir qual comando chamar                              │
│  • Apresentar resultados ao usuário                         │
│  • Instruções comportamentais (CLAUDE.md, skills, agents)   │
└─────────────────────────────────────────────────────────────┘
                              │
                    Chama com argumentos
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    RESPONSABILIDADE DO PYTHON               │
│                                                             │
│  • Criar/copiar/mover arquivos                              │
│  • Preencher templates                                      │
│  • Ler/escrever frontmatter YAML                            │
│  • Atualizar registry.json                                  │
│  • Validar inputs e paths                                   │
│  • Calcular checksums e versões                             │
│  • Aplicar transformações em texto                          │
└─────────────────────────────────────────────────────────────┘
```

### O que permanece em Markdown

| Arquivo | Motivo |
|---|---|
| `CLAUDE.md` (global e projeto) | É instrução ao modelo, não lógica |
| `.claude/skills/*.md` | Define conhecimento/comportamento de Claude |
| `.claude/agents/*.md` | Define escopo/ferramentas de subagente |
| Templates de conteúdo | Gerados como texto, não como código |

### O que migra para Python

| Atual | Novo |
|---|---|
| `install.sh` (1294 linhas shell) | `cli/` — módulo Python estruturado |
| `.claude/commands/*.md` (instruções longas) | `.claude/commands/*.md` (thin wrapper: 5-10 linhas) |
| Python embutido em here-docs no shell | Módulos Python próprios |
| Manipulação de frontmatter via regex no shell | `cli/utils/frontmatter.py` |
| Operações de registry via shell | `cli/utils/registry.py` |

---

## 3. Arquitetura Proposta

### Estrutura de Pastas

```
Claude/
├── cli/                          ← NOVO — substitui install.sh
│   ├── __init__.py
│   ├── main.py                   ← Entrada: python -m cli <comando> [args]
│   ├── config.py                 ← Constantes e paths derivados do hub-path
│   ├── commands/
│   │   ├── __init__.py
│   │   ├── claude_start.py
│   │   ├── setup_claude.py
│   │   ├── build_resource.py
│   │   ├── install_resource.py
│   │   └── publish_resource.py
│   └── utils/
│       ├── __init__.py
│       ├── frontmatter.py        ← Leitura/escrita de YAML frontmatter
│       ├── registry.py           ← Operações no registry.json
│       ├── files.py              ← Cópia, criação e validação de arquivos
│       └── templates.py          ← Preenchimento de templates
├── install.sh                    ← MANTIDO temporariamente (deprecated)
├── hub/
├── build/
└── docs/
```

### Contrato da CLI

```bash
# Padrão de chamada
python -m cli <comando> [argumentos nomeados]

# Exemplos
python -m cli claude-start
python -m cli setup-claude --path ~/Code/MeuProjeto --name "Meu Projeto"
python -m cli build-resource --type skill --name code-review
python -m cli install-resource --type skill --name code-review
python -m cli publish-resource --type skill --name code-review
```

**Saída padronizada:**
- Exit code `0` = sucesso
- Exit code `1` = erro com mensagem em stderr
- Stdout = resultado para Claude apresentar ao usuário

---

## 4. Contrato entre Claude e Python

O novo papel dos commands `.md` é mínimo:

1. Claude coleta os argumentos via perguntas ao usuário
2. Claude chama o script Python com os argumentos
3. Claude apresenta o output ao usuário

```
ANTES (setup-claude.md — 200 linhas):
  Claude lê instruções → interpreta → decide o que fazer →
  tenta executar → às vezes erra etapas → às vezes esqueçe detalhes

DEPOIS (setup-claude.md — ~15 linhas):
  Claude coleta 2 respostas → executa 1 comando Python →
  Python faz tudo → Claude mostra output
```

---

## 5. Fases da Migração

### Fase 0 — Infraestrutura Python

**Objetivo:** Criar a estrutura base do módulo CLI sem quebrar nada existente.

**Passos:**

1. Criar `cli/__init__.py` vazio
2. Criar `cli/config.py` com constantes derivadas de caminhos
3. Criar `cli/main.py` com dispatcher de subcomandos via `argparse`
4. Criar esqueleto vazio de cada módulo em `cli/commands/` e `cli/utils/`
5. Validar: `python -m cli --help` funciona e lista os comandos

**Critério de conclusão:** `python -m cli --help` executa sem erro.

---

### Fase 1 — Utilitários (substituir Python embutido no shell)

**Objetivo:** Extrair toda lógica Python dos here-docs em `install.sh` para módulos próprios.

**Passos:**

1. **`cli/utils/frontmatter.py`**
   - `read(file: Path) -> dict` — lê campos do frontmatter YAML
   - `write(file: Path, fields: dict)` — atualiza campos no frontmatter
   - `strip(file: Path, fields: list[str])` — remove campos específicos
   - `inject(file: Path, project: str, source: str, today: str)` — atalho para install

2. **`cli/utils/registry.py`**
   - `load(hub_dir: Path) -> dict` — lê registry.json
   - `save(hub_dir: Path, data: dict)` — salva registry.json
   - `find(hub_dir: Path, type: str, name: str) -> dict | None`
   - `upsert(hub_dir: Path, type: str, name: str, metadata: dict)`

3. **`cli/utils/files.py`**
   - `copy_template(src: Path, dest: Path, overwrite: bool = False)`
   - `ensure_dir(path: Path)`
   - `checksum(file: Path) -> str`
   - `bump_version(version: str) -> str`

4. **`cli/utils/templates.py`**
   - `fill(template: str, context: dict) -> str` — substitui `{{key}}` por valores
   - `normalize_body(content: str, project_name: str) -> str` — remove paths absolutos

**Critério de conclusão:** Todos os testes unitários passam. A lógica pode ser importada independentemente do shell.

---

### Fase 2 — Comandos (substituir install.sh por módulos)

**Objetivo:** Cada comando do `install.sh` vira um módulo Python autônomo.

**Ordem de implementação** (do mais simples ao mais complexo):

1. **`cli/commands/claude_start.py`**
   - Copia `global/CLAUDE.md` → `~/.claude/CLAUDE.md`
   - Copia `global/settings.json` → `~/.claude/settings.json`
   - Salva `~/.claude/hub-path`
   - Arg: nenhum

2. **`cli/commands/build_resource.py`**
   - Copia template do tipo escolhido para `.claude/<tipo>s/<nome>`
   - Injeta frontmatter com `created`, `project`, `source: local`
   - Args: `--type`, `--name`, `--dest` (opcional, default: `.claude/`)

3. **`cli/commands/install_resource.py`**
   - Copia de `hub/<tipo>/<nome>/` → `.claude/<tipo>s/<nome>`
   - Injeta frontmatter com `source: hub/<tipo>/<nome>@<versão>`, `project`
   - Atualiza seção "Recursos Instalados" no CLAUDE.md
   - Para hooks: atualiza settings.json e exibe diff
   - Args: `--type`, `--name`, `--dest` (opcional)

4. **`cli/commands/setup_claude.py`**
   - Cria estrutura `.claude/` no destino
   - Copia `CLAUDE.md` template e `settings.json`
   - Cria estrutura de pastas `design/` e `dev/`
   - Preenche CLAUDE.md com os valores fornecidos
   - Args: `--path`, `--name`, `--vision` (opcional), `--stack` (opcional)

5. **`cli/commands/publish_resource.py`**
   - Valida que o recurso existe em `.claude/<tipo>s/<nome>`
   - Copia para `hub/<tipo>/<nome>/`
   - Strip de campos locais do frontmatter
   - Normaliza body (remove paths absolutos, substitui project name)
   - Bump de versão se já existe no hub
   - Atualiza registry.json
   - Args: `--type`, `--name`, `--src` (opcional)

**Critério de conclusão:** Cada comando Python produz resultado idêntico ao `install.sh` correspondente, verificado por diff.

---

### Fase 3 — Commands (simplificar .md)

**Objetivo:** Reduzir os commands de instruções longas para thin wrappers.

**Estrutura nova de cada command.md:**

```markdown
---
[frontmatter sem alteração]
---

# /nome-do-comando

[Uma linha descrevendo o que faz]

## Argumentos

| Argumento | Como coletar |
|---|---|
| `--path` | Pergunte: "Qual a pasta do projeto?" |
| `--name` | Pergunte: "Qual o nome do projeto?" |

## Execução

Após coletar os argumentos, execute:

\`\`\`bash
HUB_DIR="$(cat ~/.claude/hub-path)"
python -m cli <comando> --arg1 "<valor1>" --arg2 "<valor2>"
\`\`\`

## Pós-execução

[O que Claude deve fazer com o output — ex: mostrar resultado, abrir arquivo]
```

**Critério de conclusão:** Nenhum command.md contém lógica de execução (criação de pastas, manipulação de arquivos, etc). Toda lógica está no Python.

---

### Fase 4 — Deprecação do install.sh

**Objetivo:** Remover dependência do `install.sh`.

**Passos:**

1. Verificar que todos os comandos Python cobrem 100% dos casos do shell
2. Adicionar aviso de deprecação no topo do `install.sh`
3. Atualizar `README.md` com novo padrão de uso
4. Após período de validação (2 semanas de uso), remover `install.sh`

---

## 6. Exemplos de Código

### `cli/main.py`

```python
import argparse
import sys
from cli.commands import claude_start, setup_claude, build_resource, install_resource, publish_resource

def main():
    parser = argparse.ArgumentParser(prog="cli", description="Claude Hub CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    claude_start.register(sub)
    setup_claude.register(sub)
    build_resource.register(sub)
    install_resource.register(sub)
    publish_resource.register(sub)

    args = parser.parse_args()
    try:
        args.func(args)
    except Exception as e:
        print(f"[erro] {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### `cli/config.py`

```python
from pathlib import Path

HUB_PATH_FILE = Path.home() / ".claude" / "hub-path"

def hub_dir() -> Path:
    if not HUB_PATH_FILE.exists():
        raise RuntimeError("~/.claude/hub-path não encontrado. Execute /claude-start primeiro.")
    return Path(HUB_PATH_FILE.read_text().strip())

def dest_dir_for_type(base: Path, type: str) -> Path:
    mapping = {
        "skill": base / "skills",
        "agent": base / "agents",
        "hook": base / "hooks",
        "command": base / "commands",
        "plugin": base / "plugins",
    }
    if type not in mapping:
        raise ValueError(f"Tipo inválido: {type}. Válidos: {', '.join(mapping)}")
    return mapping[type]
```

### `cli/utils/frontmatter.py`

```python
import re
from pathlib import Path
from datetime import date

_FENCE = re.compile(r'^---\n(.*?)\n---', re.DOTALL)
_FIELD = lambda key: re.compile(rf'^{re.escape(key)}:\s*(.+)$', re.MULTILINE)

def read(file: Path) -> dict:
    m = _FENCE.match(file.read_text())
    if not m:
        return {}
    result = {}
    for line in m.group(1).splitlines():
        if ':' in line and not line.startswith('#'):
            k, _, v = line.partition(':')
            result[k.strip()] = v.strip()
    return result

def write(file: Path, fields: dict) -> None:
    content = file.read_text()
    m = _FENCE.match(content)
    if not m:
        return
    fm = m.group(2) if len(m.groups()) > 1 else m.group(1)
    for key, value in fields.items():
        pattern = rf'^{re.escape(key)}:.*$'
        replacement = f'{key}: {value}'
        if re.search(pattern, fm, re.MULTILINE):
            fm = re.sub(pattern, replacement, fm, flags=re.MULTILINE)
        else:
            fm += f'\n{key}: {value}'
    file.write_text(f'---\n{fm}\n---' + content[m.end():])

def strip(file: Path, fields: list) -> None:
    content = file.read_text()
    m = _FENCE.match(content)
    if not m:
        return
    fm = m.group(1)
    for field in fields:
        fm = re.sub(rf'^{re.escape(field)}:.*\n?', '', fm, flags=re.MULTILINE)
    fm = re.sub(r'\n{3,}', '\n\n', fm).strip()
    file.write_text(f'---\n{fm}\n---' + content[m.end():])

def inject(file: Path, project: str, source: str) -> None:
    write(file, {"project": project, "source": source, "created": str(date.today())})
```

### `cli/commands/setup_claude.py`

```python
import argparse
import shutil
from pathlib import Path
from cli import config
from cli.utils import files, frontmatter

def register(sub):
    p = sub.add_parser("setup-claude", help="Inicializa estrutura .claude/ em um novo projeto")
    p.add_argument("--path", required=True, help="Caminho da pasta do projeto")
    p.add_argument("--name", required=True, help="Nome do projeto")
    p.add_argument("--vision", default="", help="Visão geral do projeto (uma frase)")
    p.set_defaults(func=run)

def run(args):
    dest = Path(args.path).expanduser().resolve()
    hub = config.hub_dir()
    claude_dir = dest / ".claude"

    _create_directories(dest, claude_dir)
    _copy_base_files(hub, claude_dir)
    _fill_claude_md(claude_dir / "CLAUDE.md", args.name, args.vision)

    print(f"[ok] Projeto '{args.name}' configurado em {dest}")
    print(f"[ok] .claude/ criado com CLAUDE.md, settings.json e subdiretórios")

def _create_directories(dest: Path, claude_dir: Path):
    for sub in ["skills", "agents", "hooks", "commands", "plugins"]:
        files.ensure_dir(claude_dir / sub)

    for folder in [
        "design/01-branding/research", "design/01-branding/plan", "design/01-branding/create",
        "design/02-product/discovery", "design/02-product/ux-ui",
        "dev/00-vision", "dev/01-architecture", "dev/02-supabase", "dev/03-app",
        "dev/04-lib", "dev/05-hooks", "dev/06-components/ui", "dev/06-components/layout",
        "dev/07-types", "dev/08-public",
    ]:
        files.ensure_dir(dest / folder)

def _copy_base_files(hub: Path, claude_dir: Path):
    template_dir = hub / "build" / "00-claude-md"
    shutil.copy2(template_dir / "project.md", claude_dir / "CLAUDE.md")
    shutil.copy2(hub / "global" / "settings.json", claude_dir / "settings.json")

def _fill_claude_md(file: Path, name: str, vision: str):
    content = file.read_text()

    replacements = {
        "<!-- nome do projeto -->": name,
        "<!-- visão geral -->": vision or "<!-- preencher: visão geral do projeto -->",
    }
    for placeholder, value in replacements.items():
        content = content.replace(placeholder, value)

    frontmatter.write(file, {"name": name})
    file.write_text(content)
```

### Command `.md` — Antes e Depois

**ANTES** (`setup-claude.md` — 200 linhas):
```markdown
# /setup-claude

> 1. Verifique se ~/.claude/hub-path existe...
> 2. Pergunte o nome da pasta...
> 3. Pergunte o nome do projeto...
> 4. Confirme com o usuário...
> 5. Execute bash "$HUB_DIR/install.sh" setup-claude <nome>
> 6. Fluxo guiado de preenchimento do CLAUDE.md — percorra cada seção...
>    Seção: Visão Geral — pergunta aberta...
>    Seção: Arquitetura — preencher automaticamente com...
>    Seção: Stack do Projeto — preencher automaticamente...
>    [... 150 linhas de instruções de preenchimento ...]
> 7. Após preencher todas as seções, faça a limpeza final do CLAUDE.md...
> 8. Confirme ao usuário...
```

**DEPOIS** (`setup-claude.md` — 20 linhas):
```markdown
# /setup-claude

Inicializa a estrutura `.claude/` e cria a estrutura de pastas do projeto.

## Argumentos

| Argumento | Como coletar |
|---|---|
| `--path` | Pergunte: "Qual a pasta do projeto? (ex: ~/Code/MeuProjeto)" |
| `--name` | Pergunte: "Qual o nome do projeto?" |
| `--vision` | Pergunte: "Descreva o projeto em uma frase." |

## Execução

\`\`\`bash
HUB_DIR="$(cat ~/.claude/hub-path)"
python -m cli setup-claude --path "<pasta>" --name "<nome>" --vision "<visão>"
\`\`\`

## Pós-execução

Mostre o output ao usuário. Se solicitado, abra `<pasta>/.claude/CLAUDE.md` para revisão.
```

---

## 7. Critérios de Sucesso da Migração

| Critério | Como verificar |
|---|---|
| Paridade funcional | Output de cada comando Python = output do install.sh correspondente |
| Commands simplificados | Nenhum .md de comando > 30 linhas |
| Sem lógica no shell | `install.sh` sem funções operacionais (apenas shim de compatibilidade) |
| Testável | `pytest cli/` passa sem erros |
| Sem regressão | Todos os recursos existentes no hub continuam válidos |

---

## 8. Riscos e Mitigações

| Risco | Mitigação |
|---|---|
| `install.sh` tem casos não mapeados | Manter install.sh ativo durante Fases 0-3; só remover na Fase 4 |
| Python não disponível no ambiente | Verificar `python3 --version` no claude-start; já é pré-requisito atual |
| Mudança de interface quebra commands | Fase 3 só ocorre depois que Fase 2 está completa e validada |
| Templates .md com placeholders frágeis | Usar delimitadores únicos (`{{NOME}}`) em vez de comentários HTML |
