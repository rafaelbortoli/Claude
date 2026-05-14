---
# about
id: cmd-002
name: new-project
type: command
project: ""
description: Inicializa a estrutura .claude/ e as pastas de um novo projeto.
tags: [setup, project, init]

# history
author: ""
created: 2026-05-13
status: stable
version: 1.1.0
updated: 2026-05-14

# system
scope: global
source: ""
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

**Etapa 3 — Tipo de projeto**

Use `AskUserQuestion`:
- **"Branding"** — identidade visual e marca
- **"UX and UI"** — research, interfaces e design system
- **"Product Design"** — design estratégico de produto

Aguarde a resposta do usuário. Guarde como `<tipo>`.

**Etapa 3A — Sub-tipo (condicional)**

Se `<tipo>` for **Branding**: use `AskUserQuestion`:
- **"Plus"** — pacote essencial de marca
- **"Pro"** — pacote completo de marca
- **"Ultra"** — pacote abrangente de marca

Se `<tipo>` for **UX and UI**: use `AskUserQuestion` com `multiSelect: true`:
- **"UX Research"** — discovery e pesquisa com usuários
- **"Interface digital"** — app, web, site, loja, landing page
- **"Design System"** — biblioteca de componentes e tokens
- **"Outro (digitar)"** — escopo personalizado

Se `<tipo>` for **Product Design**: use `AskUserQuestion`:
- **"New product"** — produto sendo criado do zero
- **"Feature"** — nova funcionalidade em produto existente
- **"Redesign"** — revisão e melhoria de produto existente

Aguarde a resposta do usuário. Guarde como `<subtipo>`.

**Etapa 4 — Descrição**

**[smart-suggestions: on]** Sugestões baseadas no Tipo e Sub-tipo informados.

Gere 3 variações de descrição em uma frase usando `<tipo>` e `<subtipo>` como contexto. Use `AskUserQuestion` com as 3 variações e **"Outro (digitar)"** como quarta opção.

Se o usuário escolher "Outro (digitar)": pergunte em texto livre e aguarde a resposta.

Guarde como `<descricao>`.

**Etapa 5 — Tags**

**[smart-suggestions: on]** Sugestões baseadas no Tipo, Sub-tipo e Descrição.

Monte até 3 conjuntos de tags relevantes usando `<tipo>`, `<subtipo>` e `<descricao>` como contexto. Use `AskUserQuestion` com `multiSelect: true`, exibindo cada conjunto como opção (ex: `branding, identidade, b2b`), e **"Outro (digitar)"** como quarta opção.

Se o usuário escolher "Outro (digitar)": pergunte em texto livre e aguarde a resposta.

Guarde como `<tags>`.

**Etapa 6 — Execução**

```bash
HUB_DIR="$(cat ~/.claude/hub-path)"
"$HUB_DIR/.venv/bin/python" -m cli new-project \
  --path "<pasta>" \
  --name "<nome>" \
  --description "<descricao>" \
  --tags "<tags>"
```

## Pós-execução

Mostre o output ao usuário.

Edite `<pasta>/project/project-details.md` preenchendo a tabela de identidade com os valores coletados:

| Campo | Valor |
|---|---|
| Tipo de projeto | `<tipo>` |
| Sub-tipo | `<subtipo>` |
| Domínio | *(a preencher via /setup-claude)* |
| Público-alvo | *(a preencher via /setup-claude)* |
| Estágio | *(a preencher via /setup-claude)* |
| Palavras-chave | `<tags>` |
