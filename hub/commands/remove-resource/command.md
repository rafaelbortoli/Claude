---
# about
id: cmd-007
name: remove-resource
type: command
project: ""
description: Move um recurso instalado no projeto para a lixeira, com remoção permanente após 30 dias.
tags: [remove, resource, trash]

# history
author: ""
created: 2026-05-13
status: stable
version: 1.1.0
updated: 2026-05-13

# system
scope: global
source: ""
auto_load: false
checksum: ""
dependencies: []
---

# /remove-resource

Move um recurso instalado no projeto para a lixeira. O recurso pode ser restaurado com `/restore-resource` até a data de expiração (30 dias).

## Passo 1 — Projeto destino

Informe o caminho do projeto:

```bash
pwd
```

Se o diretório atual for o projeto correto, use-o. Caso contrário, pergunte: "Qual o caminho do projeto? (ex: ~/Code/MeuProjeto)"

Guarde o caminho como `<projeto>` para usar nos próximos passos.

## Passo 2 — Listar recursos instalados

Execute obrigatoriamente o comando abaixo e exiba o resultado completo ao usuário antes de fazer qualquer pergunta:

```bash
HUB_DIR="$(cat ~/.claude/hub-path)"
"$HUB_DIR/.venv/bin/python" -m cli list-resources --installed --dest "<projeto>/.claude"
```

Se não houver recursos instalados, informe o usuário e encerre.

## Passo 3 — Tipo

Pergunte: "Qual o tipo do recurso que deseja remover?"

Aguarde a resposta antes de continuar.

## Passo 4 — Listar recursos do tipo

Execute obrigatoriamente o comando abaixo e exiba o resultado completo ao usuário antes de fazer qualquer pergunta:

```bash
HUB_DIR="$(cat ~/.claude/hub-path)"
"$HUB_DIR/.venv/bin/python" -m cli list-resources --installed --type "<tipo>" --dest "<projeto>/.claude"
```

## Passo 5 — Seleção

Pergunte: "Qual o ID do recurso que deseja remover?"

Se o usuário informar um ID, resolva o nome correspondente a partir da tabela exibida no passo anterior.

## Passo 6 — Confirmação

Antes de remover, verifique:
- Se o tipo for `skill` ou `agent` e a descrição iniciar com `[personalizado]` — avise que o recurso possui personalizações locais que serão perdidas se não restaurado antes da expiração
- Se o tipo for `plugin` — avise que todos os sub-recursos instalados por ele também serão removidos

Solicite confirmação explícita: "Confirma a remoção de '<nome>'? (s/n)"

Só prossiga se o usuário responder com "s" ou "sim".

## Execução

```bash
HUB_DIR="$(cat ~/.claude/hub-path)"
"$HUB_DIR/.venv/bin/python" -m cli remove-resource --type "<tipo>" --name "<nome>" --dest "<projeto>/.claude"
```

## Pós-execução

Mostre o output ao usuário e informe a data exata de expiração.
