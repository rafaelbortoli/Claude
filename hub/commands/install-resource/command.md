---
id: cmd-003
name: install-resource
type: command
description: Instala um recurso do hub no projeto atual — skill, agent, hook, command ou plugin.
tags: [install, resource, hub]
version: 1.4.0
status: stable
scope: global
---

# /install-resource

Instala um recurso do hub em um projeto.

## Passo 1 — Projeto destino

Informe o caminho do projeto onde o recurso será instalado:

```bash
pwd
```

Se o diretório atual for o projeto correto, use-o. Caso contrário, pergunte: "Qual o caminho do projeto? (ex: ~/Code/MeuProjeto)"

Guarde o caminho como `<projeto>` para usar nos próximos passos.

## Passo 2 — Tipo

Pergunte: "Qual o tipo de recurso? (`skill`, `agent`, `hook`, `command`, `plugin`, `instruction`)"

Aguarde a resposta antes de continuar.

## Passo 3 — Listar recursos disponíveis

Execute obrigatoriamente o comando abaixo e exiba o resultado completo ao usuário antes de fazer qualquer pergunta:

```bash
HUB_DIR="$(cat ~/.claude/hub-path)"
"$HUB_DIR/.venv/bin/python" -m cli list-resources --type "<tipo>"
```

Se não houver recursos disponíveis, informe o usuário e encerre.

## Passo 4 — Seleção

Pergunte: "Qual o ID do recurso que deseja instalar?"

Se o usuário informar um ID (ex: `sk-001`), resolva o nome correspondente a partir da tabela exibida no passo anterior.

## Execução

```bash
HUB_DIR="$(cat ~/.claude/hub-path)"
"$HUB_DIR/.venv/bin/python" -m cli install-resource --type "<tipo>" --name "<nome>" --dest "<projeto>/.claude"
```

## Pós-execução

Mostre o output ao usuário confirmando o que foi instalado ou atualizado.
