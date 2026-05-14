---
# about
id: cmd-004
name: build-resource
type: command
project: ""
description: Cria um novo recurso no projeto atual a partir do template correspondente.
tags: [build, resource, template]

# history
author: ""
created: 2026-05-10
status: stable
version: 1.3.0
updated: 2026-05-14

# system
scope: global
source: ""
auto_load: false
checksum: ""
dependencies: []
---

# /build-resource

Cria um novo recurso no projeto a partir do template correspondente.

Compatível com: `skill`, `agent`, `hook`, `command`, `plugin`.

---

## Passo 1 — Caminho do projeto

Execute:

```bash
pwd
```

Use `AskUserQuestion`:
- **"Sim, usar `<caminho retornado>`"** — confirma o diretório atual como projeto
- **"Não, informar outro caminho"** — solicita o caminho correto em texto livre

Se o usuário escolher "Não", peça o caminho e guarde como `<projeto>`. Caso contrário, use o caminho retornado pelo `pwd`.

## Passo 2 — Tipo do recurso

São 5 opções — exiba como lista e peça ao usuário que informe o tipo:

- `skill` — skill instalada em `.claude/skills/`
- `agent` — agente instalado em `.claude/agents/`
- `hook` — hook de evento instalado em `.claude/hooks/`
- `command` — comando instalado em `.claude/commands/`
- `plugin` — plugin com múltiplos recursos

## Passo 3 — Nome do recurso

Pergunte em texto livre: _"Qual o nome do recurso? (ex: ux-writing-review)"_

## Execução

```bash
HUB_DIR="$(cat ~/.claude/hub-path)"
"$HUB_DIR/.venv/bin/python" -m cli build-resource --type "<tipo>" --name "<nome>" --dest "<projeto>/.claude"
```

## Pós-execução

Mostre o arquivo criado ao usuário. Oriente a preencher os campos do frontmatter (`description`, `tags`, `author`) e os placeholders do corpo antes de usar `/publish-resource`.
