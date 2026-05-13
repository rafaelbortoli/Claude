---
# about
name: new-project
type: command
project: Claude
description: Inicializa a estrutura .claude/ e as pastas de um novo projeto.
tags: [setup, project, init]

# history
author: ""
created: 2026-05-13
status: stable
version: 1.0.0
updated: 2026-05-13

# system
scope: global
source: hub/commands/new-project@1.0.0
auto_load: false
checksum: ""
dependencies: []
---

# /new-project

Inicializa a estrutura `.claude/` e cria as pastas do projeto.

## Fluxo obrigatório — execute cada etapa em ordem, aguarde a resposta antes de avançar

**Etapa 1 — Pasta do projeto**
Pergunte: "Qual é a pasta do projeto? (ex: ~/Code/MeuProjeto)"
Aguarde a resposta do usuário.

**Etapa 2 — Nome do projeto**
Pergunte: "Qual o nome do projeto?"
Aguarde a resposta do usuário.

**Etapa 3 — Descrição**
Pergunte: "Descreva o projeto em uma frase."
Aguarde a resposta do usuário.

**Etapa 4 — Tags**
Pergunte: "Quais tags identificam este projeto? (ex: saas, fintech, b2b)"
Aguarde a resposta do usuário.

**Etapa 5 — Execução**

```bash
HUB_DIR="$(cat ~/.claude/hub-path)"
"$HUB_DIR/.venv/bin/python" -m cli new-project \
  --path "<pasta>" \
  --name "<nome>" \
  --description "<descrição>" \
  --tags "<tags>"
```

## Pós-execução

Mostre o output ao usuário.
