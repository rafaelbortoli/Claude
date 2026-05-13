---
id: cmd-008
name: restore-resource
type: command
description: Restaura um recurso da lixeira do projeto para sua localização original.
tags: [restore, resource, trash]
version: 1.1.0
status: stable
scope: global
---

# /restore-resource

Restaura um recurso da lixeira para sua localização original no projeto.

## Passo 1 — Projeto destino

Informe o caminho do projeto:

```bash
pwd
```

Se o diretório atual for o projeto correto, use-o. Caso contrário, pergunte: "Qual o caminho do projeto? (ex: ~/Code/MeuProjeto)"

Guarde o caminho como `<projeto>` para usar nos próximos passos.

## Passo 2 — Listar lixeira

Execute obrigatoriamente o comando abaixo e exiba o resultado completo ao usuário antes de fazer qualquer pergunta:

```bash
HUB_DIR="$(cat ~/.claude/hub-path)"
"$HUB_DIR/.venv/bin/python" -m cli list-resources --trash --dest "<projeto>/.claude"
```

Se a lixeira estiver vazia, informe o usuário e encerre.

## Passo 3 — Seleção

Pergunte: "Qual o ID do recurso que deseja restaurar?"

Resolva o ID para `type` e `name` a partir da tabela exibida no passo anterior.

## Execução

```bash
HUB_DIR="$(cat ~/.claude/hub-path)"
"$HUB_DIR/.venv/bin/python" -m cli restore-resource --type "<tipo>" --name "<nome>" --dest "<projeto>/.claude"
```

## Pós-execução

Mostre o output ao usuário confirmando o que foi restaurado.
