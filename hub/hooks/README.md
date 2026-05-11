---
# identity
name: hub-hooks-readme
type: readme
version: 1.0.0
status: stable

# context
description: Catálogo de hooks — scripts shell determinísticos que disparam em eventos do Claude Code.
tags: [hub, hooks]

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

# Hub — Hooks

Scripts shell determinísticos que disparam em eventos do Claude Code. Sem AI — lógica pura de shell.

## Estrutura de cada hook

```
<hook-name>/
├── hook.json        # Metadados: evento, matcher, descrição
└── hook.sh          # Script executável
```

## Como configurar

Adicionar ao `settings.json` do projeto ou global (`~/.claude/settings.json`):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "bash /caminho/para/hook.sh"
          }
        ]
      }
    ]
  }
}
```

## Hooks disponíveis

<!-- Esta seção é atualizada a cada novo recurso publicado no hub. -->

| Nome | Evento | Matcher | Descrição | Tags |
|---|---|---|---|---|
| — | — | — | — | — |
