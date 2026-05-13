---
# about
name: claude-start
type: command
project: Claude
description: Setup global do Claude Code na máquina — copia CLAUDE.md e settings.json para ~/.claude/.
tags: [setup, global, machine]

# history
author: ""
created: 2026-05-10
status: stable
version: 1.2.0
updated: 2026-05-12

# system
scope: global
source: hub/commands/claude-start@1.2.0
auto_load: false
checksum: ""
dependencies: []
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
