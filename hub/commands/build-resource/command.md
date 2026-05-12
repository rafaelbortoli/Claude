---
name: build-resource
type: command
version: 1.2.0
status: stable

description: Cria um novo recurso no projeto atual a partir do template correspondente.
tags: [build, resource, template]

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

# /build-resource

Cria um novo recurso no projeto atual a partir do template correspondente.

## Argumentos

| Argumento | Como coletar |
|---|---|
| `--type` | Pergunte: "Qual o tipo? Opções: `skill`, `agent`, `hook`, `command`, `plugin`" |
| `--name` | Pergunte: "Qual o nome do recurso?" |

## Execução

```bash
HUB_DIR="$(cat ~/.claude/hub-path)"
"$HUB_DIR/.venv/bin/python" -m cli build-resource --type "<tipo>" --name "<nome>"
```

## Pós-execução

Mostre o arquivo criado ao usuário e oriente a preencher os placeholders antes de usar `/publish-resource`.
