---
# identity
name: Claude System
type: doc
version: 1.0.0
status: stable

# context
description: Instruções específicas do projeto — estende ~/.claude/CLAUDE.md.
tags: []

# loading
scope: project
auto_load: true

# traceability — preenchidos pelo /new-project
source: build/00-claude-md/project.md
project: Claude System
dependencies: []
checksum: ""

# metadata
author: ""
created: 2026-05-10
updated: 2026-05-10
---

# Claude — Instruções do Projeto

> Estende `~/.claude/CLAUDE.md`.

---

## Visão Geral

ClaudeSystem é o **engine** — infraestrutura que é instalada em projetos para habilitar resources, definir regras e estabelecer mecanismos para acelerar planejamento e execução. Não é um projeto em si.

---

## Arquitetura

- `hub/` — fonte canônica de todos os resources (commands, skills, agents, hooks, plugins). Nunca copiado para projetos.
- `build/` — templates usados pelo CLI para criar novos resources
- `cli/` — CLI Python que executa operações do engine (install, build, publish, etc.)
- `global/` — arquivos instalados globalmente em `~/.claude/` pelo `claude-start`
- `plan/` — planos de arquitetura e feature em andamento
- `.claude/` — configuração do engine (sem commands instalados — ver Regras abaixo)

---

## Stack do Projeto

| Camada | Stack |
|---|---|
| CLI | Python |
| Resources | Markdown + JSON |
| Orquestração | Claude Code |

---

## Mapa do Repositório

| Caminho | O que vive aqui |
|---|---|
| `hub/commands/` | Comandos canônicos — instalados globalmente via `claude-start` |
| `hub/skills/` | Skills canônicas — instaladas em projetos via `install-resource` |
| `hub/agents/` | Agentes canônicos |
| `hub/hooks/` | Hooks canônicos |
| `hub/plugins/` | Plugins canônicos |
| `build/0X-*/` | Templates por tipo de resource |
| `cli/commands/` | Implementação Python de cada comando do CLI |

---

## Regras

- **ClaudeSystem não tem `.claude/commands/`** — commands são ferramentas de projeto, não do engine
- **Fonte canônica é o hub** — nunca editar resources instalados em `~/.claude/commands/` diretamente
- **Workflow de desenvolvimento:** editar em `hub/` → rodar `claude-start` → propaga para `~/.claude/commands/`
- **Não usar commands de projeto aqui** — `/build-resource`, `/install-resource` e similares são para projetos externos

---

## Bootstrap

Para configurar uma nova máquina:

```bash
<caminho-do-ClaudeSystem>/.venv/bin/python -m cli claude-start
```

Isso registra `hub-path` e instala todos os commands do hub em `~/.claude/commands/`.
