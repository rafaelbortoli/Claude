---
name: claude-start
type: command
version: 1.2.0
status: stable

description: Setup global do Claude Code na máquina — copia CLAUDE.md e settings.json para ~/.claude/.
tags: [setup, global, machine]

scope: global
auto_load: false

source: hub/commands/claude-start@1.2.0
project: Claude
dependencies: []
checksum: ""

author: ""
created: 2026-05-10
updated: 2026-05-12
---

# /claude-start

Setup global do Claude Code na máquina.

## Execução

```bash
HUB_DIR="$(cat ~/.claude/hub-path)"
"$HUB_DIR/.venv/bin/python" -m cli claude-start
```

Se `~/.claude/hub-path` não existir ainda, o usuário deve informar o caminho do repositório e executar:

```bash
"<caminho-do-hub>/.venv/bin/python" -m cli claude-start
```

## Pós-execução

Mostre o output ao usuário confirmando o que foi instalado ou mantido.
