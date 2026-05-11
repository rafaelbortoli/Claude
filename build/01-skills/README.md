---
# identity
name: build-skills-readme
type: readme
version: 1.0.0
status: stable

# context
description: Documentação do layer 01 — templates para criação de skills.
tags: [skills, build]

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

# 01 — Skills

Templates para criação de skills. Skills concluídas vão para `hub/skills/`.

## O que é uma skill

Conhecimento especializado carregado on-demand. O Claude lê a `description` e o conteúdo do `skill.md` para decidir quando a skill é relevante — não há lista de triggers processada automaticamente.

Skills são invocadas de duas formas:
- **Explícita**: o usuário digita `/skill-name`
- **Por contexto**: o Claude infere que a skill é relevante com base na descrição e na seção "Quando usar"

## Estrutura de uma skill

```
<skill-name>/
├── skill.json       # Metadados para o registry e install.sh (fonte autoritativa)
├── skill.md         # Conteúdo que o Claude lê e executa
├── scripts/         # Scripts shell invocados pelas instruções da skill
├── templates/       # Arquivos boilerplate que a skill copia para o projeto
└── assets/          # Arquivos de suporte: configs, schemas, exemplos
```

## Responsabilidade de cada arquivo

| Arquivo | Lido por | Contém |
|---|---|---|
| `skill.json` | `registry.json`, `install.sh` | Metadados completos: versão, tags, scope, author |
| `skill.md` | Claude | Instruções de execução: o que faz, quando usar, passos, output |

`skill.json` é a fonte autoritativa de metadados. `skill.md` contém apenas `name` e `description` no frontmatter — o mínimo que o Claude precisa para correspondência.

## Subpastas

| Pasta | Uso |
|---|---|
| `scripts/` | Scripts shell que a skill invoca durante a execução (`bash scripts/lint.sh`) |
| `templates/` | Boilerplate que a skill copia para o projeto (`cp templates/config.json .`) |
| `assets/` | Arquivos de suporte referenciados nas instruções (schemas, exemplos, configs) |

Subpastas vazias são válidas — manter o `.gitkeep` para preservar a estrutura no git.

## Campos de skill.json

| Campo | Descrição |
|---|---|
| `name` | Identificador em kebab-case |
| `version` | Semântico: `1.0.0` |
| `description` | O que a skill faz — mesma string do frontmatter do skill.md |
| `triggers` | Palavras-chave para documentação e busca no hub (não processadas pelo Claude) |
| `tags` | Categorias para organização no hub |
| `scope` | `global` ou `project` |

## Scope

| Valor | Destino de instalação | Disponibilidade |
|---|---|---|
| `global` | `~/.claude/skills/` | Todos os projetos |
| `project` | `.claude/skills/` | Apenas este repositório |

## Como criar uma nova skill

1. Copiar `_template/` para uma nova pasta com o nome em kebab-case
2. Preencher `skill.json` com os metadados
3. Preencher `skill.md` — description precisa ser idêntica ao `skill.json`
4. Adicionar scripts, templates e assets conforme necessário
5. Testar: instalar a skill localmente e invocar no Claude Code com `/skill-name`
6. Mover a pasta concluída para `hub/skills/<skill-name>/`
7. Atualizar `registry.json` na raiz do repositório
