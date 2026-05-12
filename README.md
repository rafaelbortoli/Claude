---
# identity
name: claude-resources-readme
type: readme
version: 1.0.0
status: stable

# context
description: Visão geral do repositório de recursos Claude — hub, build e ciclo de vida.
tags: [overview]

# loading
scope: global
auto_load: false

# traceability
source: ""
project: ""
dependencies: []
checksum: ""

# metadata
author: ""
created: 2026-05-10
updated: ""
---

# Claude

Repositório de recursos para Claude Code — hub de recursos reutilizáveis, templates de build e CLI Python.

## Estrutura

```
.
├── cli/                ← módulo Python — backend de todos os comandos
│   ├── commands/       ← implementação de cada comando
│   ├── utils/          ← frontmatter, registry, files, templates
│   └── tests/          ← testes unitários (pytest)
├── install.sh          ← DEPRECATED — substituído por python -m cli
├── registry.json       ← índice dos recursos publicados no hub
├── CHANGELOG.md        ← histórico de publicações
│
├── hub/                ← recursos prontos para instalação
│   ├── commands/       ← slash commands (/claude-start, /setup-claude, ...)
│   ├── skills/         ← skills reutilizáveis
│   ├── agents/         ← agentes especializados
│   ├── hooks/          ← hooks de ciclo de vida
│   ├── plugins/        ← plugins (conjuntos de recursos)
│   └── instructions/   ← fragmentos de instrução
│
├── build/              ← templates e fragmentos para criação de recursos
│   ├── 00-claude-md/   ← templates de CLAUDE.md e fragmentos de instrução
│   ├── 01-skills/      ← template de skill
│   ├── 02-hooks/       ← template de hook
│   ├── 03-agents/      ← template de agente
│   ├── 04-plugins/     ← template de plugin e command
│   └── stacks/         ← definições de stack (nextjs-supabase, generic)
│
├── global/             ← arquivos globais (~/.claude/)
│   ├── CLAUDE.md       ← instruções globais
│   └── settings.json   ← permissões base
│
└── docs/               ← documentação e propostas
```

## Como usar

### Primeira vez em uma máquina nova

```
/claude-start
```

Instala `global/CLAUDE.md` e `global/settings.json` em `~/.claude/`.

### Novo projeto

```
/setup-claude
```

Inicializa `.claude/` no diretório atual com estrutura mínima e identidade do projeto.

### Instalar recurso do hub

```
/install-resource <tipo> <nome>
```

Tipos: `skill`, `agent`, `hook`, `command`, `plugin`.

### Criar novo recurso

```
/build-resource <tipo> <nome>
```

Cria o recurso a partir do template, com frontmatter pré-preenchido.

### Publicar recurso no hub

```
/publish-resource <tipo> <nome>
```

Normaliza e copia o recurso do projeto para o hub.

---

Os comandos `/...` são slash commands do Claude Code instalados via `/install-resource command <nome>`. O backend é `python -m cli` — o usuário não o executa diretamente.

## CLI (uso direto)

```bash
python -m cli --help
python -m cli claude-start
python -m cli setup-claude --path ~/Code/MeuProjeto --name "Meu Projeto"
python -m cli build-resource --type skill --name code-review
python -m cli install-resource --type skill --name code-review
python -m cli publish-resource --type skill --name code-review
```

Requer Python 3.10+ e deve ser executado a partir da raiz do repositório. Para criar o ambiente:

```bash
python -m venv .venv
.venv/bin/pip install pytest
```