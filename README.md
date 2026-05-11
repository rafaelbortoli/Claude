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

# traceability — preenchidos pelo install.sh
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

Repositório de recursos para Claude Code — hub de recursos reutilizáveis, templates de build e script de instalação.

## Estrutura

```
.
├── install.sh          ← script de instalação (backend de todos os comandos)
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

Os comandos `/...` são slash commands do Claude Code instalados via `/install-resource command <nome>`. O `install.sh` é o backend — o usuário não o executa diretamente.