---
name: setup-claude
type: command
version: 1.4.0
status: stable

description: Configura a estrutura .claude/ em um novo projeto — cria diretórios, CLAUDE.md e estrutura de pastas do projeto.
tags: [setup, project, init]

scope: global
auto_load: false

source: ""
project: ""
dependencies: []
checksum: ""

author: ""
created: 2026-05-10
updated: 2026-05-12
---

# /setup-claude

Inicializa a estrutura `.claude/` e cria as pastas do projeto.

## Argumentos

| Argumento | Como coletar |
|---|---|
| `--path` | Pergunte: "Qual é a pasta do projeto? (ex: ~/Code/MeuProjeto)" |
| `--name` | Pergunte: "Qual o nome do projeto?" |
| `--vision` | Pergunte: "Descreva o projeto em uma frase." (opcional) |
| `--stack` | Pergunte: "Qual a stack do projeto?" somente se diferente do padrão `nextjs-supabase-vercel-claude`. Omitir se padrão. |

## Execução

```bash
HUB_DIR="$(cat ~/.claude/hub-path)"
"$HUB_DIR/.venv/bin/python" -m cli setup-claude --path "<pasta>" --name "<nome>" --vision "<visão>"
```

## Pós-execução

Mostre o output ao usuário. Se solicitado, abra `<pasta>/.claude/CLAUDE.md` para revisão e preenchimento das seções restantes.
