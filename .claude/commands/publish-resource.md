---
# about
name: publish-resource
type: command
project: Claude System
description: Normaliza e publica um recurso do projeto no hub para reutilização em outros projetos.
tags: [publish, resource, hub]

# history
author: ""
created: 2026-05-10
status: stable
version: 1.2.0
updated: 2026-05-12

# system
scope: global
source: hub/commands/publish-resource@1.2.0
auto_load: false
checksum: ""
dependencies: []
---

# /publish-resource

Normaliza e publica um recurso do projeto no hub.

## Argumentos

| Argumento | Como coletar |
|---|---|
| `--type` | Pergunte: "Qual o tipo? Opções: `skill`, `agent`, `hook`, `command`" |
| `--name` | Pergunte: "Qual o nome do recurso?" |

## Execução

```bash
HUB_DIR="$(cat ~/.claude/hub-path)"
"$HUB_DIR/.venv/bin/python" -m cli publish-resource --type "<tipo>" --name "<nome>"
```

## Pós-execução

Mostre o diff e o output ao usuário.
