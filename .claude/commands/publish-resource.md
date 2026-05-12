---
name: publish-resource
type: command
version: 1.2.0
status: stable

description: Normaliza e publica um recurso do projeto no hub para reutilização em outros projetos.
tags: [publish, resource, hub]

scope: global
auto_load: false

source: hub/commands/publish-resource@1.2.0
project: Claude
dependencies: []
checksum: ""

author: ""
created: 2026-05-10
updated: 2026-05-12
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
