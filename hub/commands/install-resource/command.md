---
name: install-resource
type: command
version: 1.2.0
status: stable

description: Instala um recurso do hub no projeto atual — skill, agent, hook, command ou plugin.
tags: [install, resource, hub]

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

# /install-resource

Instala um recurso do hub no projeto atual.

## Argumentos

| Argumento | Como coletar |
|---|---|
| `--type` | Pergunte: "Qual o tipo? Opções: `skill`, `agent`, `hook`, `command`, `plugin`, `instruction`" |
| `--name` | Pergunte: "Qual o nome do recurso?" |

## Execução

```bash
HUB_DIR="$(cat ~/.claude/hub-path)"
"$HUB_DIR/.venv/bin/python" -m cli install-resource --type "<tipo>" --name "<nome>"
```

## Pós-execução

Mostre o output ao usuário confirmando o que foi instalado ou atualizado.
