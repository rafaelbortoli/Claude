---
# identity
name: build-hooks-readme
type: readme
version: 1.0.0
status: stable

# context
description: Documentação do layer 02 — templates para criação de hooks.
tags: [hooks, build]

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

# 02 — Hooks

Templates para criação de hooks. Hooks concluídos vão para `hub/hooks/`.

## O que são hooks

Scripts shell determinísticos que disparam em eventos do Claude Code. Sem AI — lógica pura de shell. O matcher no `settings.json` filtra quais eventos chegam ao script; o script decide o que fazer com eles.

## Estrutura de um hook

```
<hook-name>/
├── hook.json     # Metadados: evento, matcher, descrição
└── hook.sh       # Script executável
```

## Eventos disponíveis

| Evento | Quando dispara | Pode bloquear |
|---|---|---|
| `PreToolUse` | Antes de qualquer ferramenta executar | Sim (exit 2) |
| `PostToolUse` | Após qualquer ferramenta executar | Não |
| `SessionStart` | Quando uma sessão é iniciada | Não |
| `Stop` | Quando Claude termina um turno | Não |
| `SubagentStop` | Quando um subagente retorna | Não |

## Como um hook funciona

```
Evento dispara → Matcher filtra (settings.json) → Script recebe JSON via stdin → Executa lógica
```

- **Stdin**: JSON com contexto do evento — lido uma vez com `INPUT=$(cat)`
- **Stdout**: texto injetado no contexto do Claude (PreToolUse e SessionStart)
- **Stderr**: exibido como erro no terminal, não afeta o Claude
- **Exit 2**: bloqueia a execução — exclusivo do `PreToolUse`
- **Exit 0**: execução continua normalmente

## Campos de hook.json

| Campo | Descrição |
|---|---|
| `name` | Identificador em kebab-case |
| `event` | Um dos 5 eventos disponíveis |
| `matcher.tool` | Nome da ferramenta (`*` para todas) |
| `matcher.command_pattern` | Regex sobre o comando — `null` para sem filtro |
| `script` | Nome do arquivo `.sh` do hook finalizado |

## Como configurar no settings.json

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "bash /caminho/absoluto/para/hook.sh"
          }
        ]
      }
    ]
  }
}
```

## Como criar um novo hook

1. Copiar `_template/hook.json` → `<hook-name>/hook.json`
2. Copiar o script do evento em `_template/events/` → `<hook-name>/hook.sh`
3. Preencher `hook.json` com metadados e matcher
4. Implementar a lógica no `hook.sh` — descomentando e adaptando os blocos
5. Tornar o script executável: `chmod +x hook.sh`
6. Configurar no `settings.json` e testar no Claude Code
7. Mover a pasta concluída para `hub/hooks/<hook-name>/`
8. Atualizar `registry.json` na raiz do repositório

## Templates de evento disponíveis

| Arquivo | Evento | Campos extraídos |
|---|---|---|
| `events/pre-tool-use.sh` | `PreToolUse` | `TOOL`, `COMMAND` |
| `events/post-tool-use.sh` | `PostToolUse` | `TOOL`, `COMMAND`, `FILE_PATH`, `EXIT_CODE` |
| `events/session-start.sh` | `SessionStart` | `SESSION_ID`, `PROJECT_DIR` |
| `events/stop.sh` | `Stop` | `SESSION_ID` |
| `events/subagent-stop.sh` | `SubagentStop` | `AGENT_NAME`, `SESSION_ID`, `OUTPUT` |
