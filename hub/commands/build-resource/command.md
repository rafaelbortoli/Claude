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

Mostre o caminho retornado e pergunte: _"Este é o diretório do projeto? Se não, informe o caminho correto."_

Guarde o caminho como `<projeto>`.

## Passo 2 — Tipo do recurso

Pergunte: _"Qual o tipo de recurso? Opções: `skill`, `agent`, `hook`, `command`, `plugin`"_

## Passo 3 — Nome do recurso

Pergunte: _"Qual o nome do recurso? (ex: ux-writing-review)"_

## Execução

```bash
HUB_DIR="$(cat ~/.claude/hub-path)"
"$HUB_DIR/.venv/bin/python" -m cli build-resource --type "<tipo>" --name "<nome>" --dest "<projeto>/.claude"
```

## Pós-execução

Mostre o arquivo criado ao usuário. Oriente a preencher os campos do frontmatter (`description`, `tags`, `author`) e os placeholders do corpo antes de usar `/publish-resource`.
